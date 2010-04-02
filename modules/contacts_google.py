"""
Syncronize with Google Contacts

This file is part of Pisi.

Google provides a really straight forward API for accessing their contact information (gdata). 
U{http://code.google.com/p/gdata-python-client/}. It is used for this implementation - the site package 
has to be installed.

Pisi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pisi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pisi.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys,os,datetime
# Allows us to import event
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from contacts import contacts
from pisiconstants import *
import pisiprogress
import pisitools

import atom
import gdata.contacts
import gdata.contacts.service
import gdata.service

class SynchronizationModule(contacts.AbstractContactSynchronizationModule, pisitools.GDataSyncer):
    """
    The implementation of the interface L{contacts.AbstractContactSynchronizationModule} for the Google Contacts backend
    """
    
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded. 
        The connection to the Google Gdata backend is established.

        @param modulesString: is a small string to help you make a unique id. It is the two modules configuration-names concatinated.
        @param config: is the configuration from ~/.pisi/conf. Use like config.get(configsection,'user')
        @param configsection: is the configuration from ~/.pisi/conf. Use like config.get(configsection,'user')
        @param folder: is a string with the location for where your module can save its own files if necessary
        @param verbose: should make your module "talk" more
        @param soft: should tell you if you should make changes (ie. save)
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "Google contacts")
        pisitools.GDataSyncer.__init__(self, config.get(configsection,'user'), config.get(configsection,'password'))
        self.verbose = verbose
        pisiprogress.getCallback().verbose("Google contacts module loaded")

        self._idMappingInternalGlobal = {}
        self._idMappingGlobalInternal = {}

        self._gd_client = gdata.contacts.service.ContactsService()
        self._google_client = self._gd_client
        self._doGoogleLogin(GOOGLE_CONTACTS_APPNAME)

    def _unpackGoogleTitle(self, atts, gtitle):
        """
        Takes the components of a Google Title apart (all names)
        
        The whole thing is about guessing - check code for details.
        """
        pisiprogress.getCallback().verbose("Google Contacts: Loading")
        title,  first,  last,  middle = pisitools.parseFullName(gtitle)
        atts['title'] = title
        atts['firstname'] = first
        atts['lastname'] = last
        atts['middlename'] = middle

    def _unpackPostalCity(self,  line):
        """
        Takes one address line apart and identifies postal code and locality
        
        This is really tricky - you never know how many parts belong to which side - and it's all in one line.
        We do it this way: 
         - only one item indicates city only
         - two items one each
         - more than two - depending on the length of the first item, another item is applied to the postal code; all the remaining stuff is city
        """
        items = line.strip().split(' ')
        if len(items) == 1: # only city - no postal code given
            city = items[0]
            postalCode = ''
        elif len(items) == 2:
            postalCode = items[0]
            city = items[1]
        else:
            if len(items[0]) > 4:
                postalCode = items[0]
            else:
                postalCode = items[0] + " " + items[1]
            city = line[len(postalCode):].strip()   # all stuff behind postal code (cities might have several components)
#        print ('%s \t> %s : %s' %(line, postalCode, city))
        return city,  postalCode

    def _unpackGooglePostalAddress(self,  atts,  addressText,  type):
        """
        Takes the components of a Google address apart
        
        The whole thing is about guessing - check code for details.
        """
        text = addressText.strip()
        lines = text.split("\n")
        try:
            street = lines[0].strip()
            if type == 'home':
                atts['homeStreet'] = street
            elif type == 'work':
                atts['businessStreet'] = street
            del lines[0]
            city,  postalCode = self._unpackPostalCity(lines[0])
            if type == 'home':
                atts['homeCity'] = city
                if postalCode:
                    atts['homePostalCode'] = postalCode
            elif type == 'work':
                atts['businessCity'] = city
                if postalCode:
                    atts['businessPostalCode'] = postalCode
            del lines[0]
            if len(lines)>1:    # we assume, if there is another two lines, one will be the state; the other one the country - one line left indicates that we only have country information
                state = lines[0].strip()
                if type == 'home':
                    atts['homeState'] = state
                elif type == 'work':
                    atts['businessState'] = state
                del lines[0]
            country = lines[0].strip()
            if type == 'home':
                atts['homeCountry'] = country
            elif type == 'work':
                atts['businessCountry'] = country
            
        except IndexError:
            pass     # that's fine - we cannot have everything

    def load(self):
        """
        Load all data from backend
        
        A single query is performed and the result set is parsed afterwards.
        """
        query = gdata.contacts.service.ContactsQuery()
        query.max_results = GOOGLE_CONTACTS_MAXRESULTS
        feed = self._gd_client.GetContactsFeed(query.ToUri())
        for i, entry in enumerate(feed.entry):
            atts = {}
            if not entry.title or not entry.title.text:
                pisiprogress.getCallback().verbose('** In Googlecontacts account is an entry with no title - I cannot process this account and will skip it.')
                continue    # an entry without a title cannot be processed by PISI as the name is the 'primary key'
            self._unpackGoogleTitle(atts,  entry.title.text.decode("utf-8"))
            
            if len(entry.email) > 0:
                email = entry.email[0]
#            for email in entry.email:
                if email.primary and email.primary == 'true':   # for now we only support one email address
                    if email.address:
                        atts['email'] = email.address.decode("utf-8")
            
            for phone in entry.phone_number:
                if phone.rel == gdata.contacts.PHONE_HOME:
                    atts['phone'] = phone.text
                if phone.rel == gdata.contacts.PHONE_MOBILE:
                    atts['mobile'] = phone.text
                if phone.rel == gdata.contacts.PHONE_WORK:
                    atts['officePhone'] = phone.text
                if phone.rel == gdata.contacts.PHONE_WORK_FAX:
                    atts['fax'] = phone.text
            
            for address in entry.postal_address:
                if address.text:
                    value = address.text.decode("utf-8")
                    type = None
                    if address.rel == gdata.contacts.REL_HOME:
                        type = 'home'
                    elif address.rel == gdata.contacts.REL_WORK:
                        type = 'work'
                    if type:
                        self._unpackGooglePostalAddress(atts, value, type)
            
            if entry.organization:
                if entry.organization.org_name and entry.organization.org_name.text:
                    atts['businessOrganisation'] = entry.organization.org_name.text.decode("utf-8")
                if entry.organization.org_title and entry.organization.org_title.text:
                    atts['businessDepartment'] = entry.organization.org_title.text.decode("utf-8")      # well - that doesn't map fully - but better than nothing :)
            
            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c

            self._idMappingGlobalInternal[id] = entry.GetEditLink().href
            self._idMappingInternalGlobal[entry.GetEditLink().href] = id

    def _assembleTitle(self,  contactEntry):
        """
        Assembles all information from a contact entry for the packed version of a title in google contacts
        """
        return pisitools.assembleFullName(contactEntry)

    def _savePhones(self,  contact,  new_contact):
        """
        Integrates all saving tranformations for phone attributes
        """
        if contact.attributes.has_key('phone'):
            phone = contact.attributes['phone']
            if phone and phone != '':
                new_contact.phone_number.append(gdata.contacts.PhoneNumber(text=phone,  rel=gdata.contacts.PHONE_HOME))
        if contact.attributes.has_key('mobile'):
            mobile = contact.attributes['mobile']
            if mobile and mobile != '':
                new_contact.phone_number.append(gdata.contacts.PhoneNumber(text=mobile,  rel=gdata.contacts.PHONE_MOBILE))
        if contact.attributes.has_key('officePhone'):
            phone = contact.attributes['officePhone']
            if phone and phone != '':
                new_contact.phone_number.append(gdata.contacts.PhoneNumber(text=phone,  rel=gdata.contacts.PHONE_WORK))
        if contact.attributes.has_key('fax'):
            fax = contact.attributes['fax']
            if fax and fax != '':
                new_contact.phone_number.append(gdata.contacts.PhoneNumber(text=fax,  rel=gdata.contacts.PHONE_WORK_FAX))

    def _saveAddresses(self,  contact,  new_contact):
        """
        Integrates all saving tranformations for address attributes
        """
        # we assume, if somebody supplies information about an address, first the city (locality) name would be provided
        if contact.attributes.has_key('homeCity'):
            homeCity = contact.attributes['homeCity']
            if  homeCity and homeCity != None:
                text = ''
                if contact.attributes.has_key('homeStreet'):
                    homeStreet = contact.attributes['homeStreet']
                    if homeStreet and homeStreet != '':
                        text += homeStreet + "\n"
                if contact.attributes.has_key('homePostalCode'):
                    homePostalCode = contact.attributes['homePostalCode']
                    if homePostalCode and homePostalCode != '':
                        text += homePostalCode + " "
                text += homeCity +"\n"
                if contact.attributes.has_key('homeState'):
                    homeState = contact.attributes['homeState']
                    if homeState and homeState != '':
                        text += homeState + "\n"
                if contact.attributes.has_key('homeCountry'):
                    homeCountry = contact.attributes['homeCountry']
                    if homeCountry and homeCountry != '':
                        text += homeCountry + "\n"
                new_contact.postal_address.append(gdata.contacts.PostalAddress(text=text,  rel=gdata.contacts.REL_HOME))
                
        if contact.attributes.has_key('businessCity'):
            businessCity = contact.attributes['businessCity']
            if  businessCity and businessCity != None:
                text = ''
                if contact.attributes.has_key('businessStreet'):
                    businessStreet = contact.attributes['businessStreet']
                    if businessStreet and businessStreet != '':
                        text += businessStreet + "\n"
                if contact.attributes.has_key('businessPostalCode'):
                    businessPostalCode = contact.attributes['businessPostalCode']
                    if businessPostalCode and businessPostalCode != '':
                        text += businessPostalCode + " "
                text += businessCity +"\n"
                if contact.attributes.has_key('businessState'):
                    businessState = contact.attributes['businessState']
                    if businessState and businessState != '':
                        text += businessState + "\n"
                if contact.attributes.has_key('businessCountry'):
                    businessCountry = contact.attributes['businessCountry']
                    if businessCountry and businessCountry != '':
                        text += businessCountry + "\n"
                new_contact.postal_address.append(gdata.contacts.PostalAddress(text=text,  rel=gdata.contacts.REL_WORK))

    def _saveBusinessDetails(self,  c,  new_contact):
        """
        Creates an entry for business organzation und unit.
        """
        if c.attributes.has_key('businessOrganisation'):
            o = c.attributes['businessOrganisation']
            if o and o != '':
                ou = None
                if c.attributes.has_key('businessDepartment'):
                    ou = c.attributes['businessDepartment']
                
                new_contact.organization = gdata.contacts.Organization(org_name = gdata.contacts.OrgName(o),  org_title = gdata.contacts.OrgTitle(ou))

    def _saveOperationAdd(self,  id):
        """
        Save all changes to Google contacts that have come by
        """
        contact = self.getContact(id)
        new_contact = gdata.contacts.ContactEntry(title=atom.Title(text=self._assembleTitle(contact)))
        if contact.attributes.has_key('email'):
            email = contact.attributes['email']
            if email and email != '':
                new_contact.email.append(gdata.contacts.Email(address=email,primary='true', rel=gdata.contacts.REL_HOME))
        self._savePhones(contact,  new_contact)
        self._saveAddresses(contact,  new_contact)
        self._saveBusinessDetails(contact,  new_contact)
        
        contact_entry = self._gd_client.CreateContact(new_contact)

    def _saveOperationDelete(self,  id):
        """
        Finally deletes the contact entry identified by its ID in the google contact backend
        """
        link = self._idMappingGlobalInternal[id]
        self._gd_client.DeleteContact(link)

    def _saveOperationModify(self,  id):
        """
        Applies changes for an entry to the Google contacts backend
        
        In order to keep things simple the old value is simply erased using the method L{_saveOperationDelete} and a new one is inserted (L{_saveOperationAdd}).
        """
        self._saveOperationDelete(id)
        self._saveOperationAdd(id)

    def saveModifications(self ):
        """
        Save whatever changes have come by
        
        The L{_history} variable is iterated. The corresponding function is called for each action.
        """
        i=0
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose("\t\t<google contacts> adding %s" %(id))
                self._saveOperationAdd(id)
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<google contacts> deleting %s" %(id))
                self._saveOperationDelete(id)
            elif action == ACTIONID_MODIFY:
                self._saveOperationModify(id)
                pisiprogress.getCallback().verbose("\t\t<google contacts> replacing %s" %(id))
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 100 / len(self._history))
            pisiprogress.getCallback().update('Storing')
