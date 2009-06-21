"""
Synchronize with local VCF file

This file is part of Pisi.

VCF support is based on the VOBJECT library by skyhouseconsulting (U{http://vobject.skyhouseconsulting.com/}).
Consequently, the vobject site-package has to be installed for utilizing vcard support in PISI.

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
import vobject
import os.path
import os
from pisiconstants import *
import pisiprogress

VCF_PHONETYPE_HOME = ['HOME', 'VOICE']
"""Indentifies a phone entry as home phone"""
VCF_PHONETYPE_WORK = ['WORK', 'VOICE']
"""Indentifies a phone entry as work phone"""
VCF_PHONETYPE_MOBILE = ['CELL', 'VOICE']
"""Indentifies a phone entry as mobile phone"""
VCF_PHONETYPE_FAX = ['FAX']
"""Indentifies a phone entry as fax"""
VCF_ADDRESSTYPE_HOME = ['HOME', 'POSTAL']
"""Indentifies an address entry as home address"""
VCF_ADDRESSTYPE_WORK = ['WORK', 'POSTAL']
"""Indentifies an address entry as work address"""
PATH_INTERACTIVE = "@interactive"
"""Option in configuration file for supplying filename and path of VCF file interactively"""

class SynchronizationModule(contacts.AbstractContactSynchronizationModule):
    """
    The implementation of the interface L{contacts.AbstractContactSynchronizationModule} for VCF file persistence backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded.
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "VCF")
        self._vcfpath = config.get(configsection,'vcfpath')
        self._folder = folder
        pisiprogress.getCallback().verbose("contact VCF module loaded using file %s" %(self._vcfpath))
        self._rawData = {}

    def _promptFilename(self,  prompt, default = None,  description = None):
        """
        Asks for user input on console
        """
        if description:
            pisiprogress.getCallback().message(description)
        return pisiprogress.getCallback().promptFilename(prompt,  default)

    def _extractAtt(self, x,  st):
        """
        Supporting function for pulling information out of a attribute
        
        Gets around problems with non available attributes without the need for checking this beforehand for each attribute.
        """
        try:
            ret = None
            exec "ret = " + st
            return ret
        except AttributeError:
            return ''

    def _guessAmount(self):
        """
        Try to determine roughly how many entries are in this file (we can't know prior to parsing; but we have a guess using the file size)
        """
        info = os.stat(self._vcfpath)
        return info.st_size / VCF_BYTES_PER_ENTRY

    def load(self):
        """
        Load all data from local VCF file
        
        File opened and the entries are parsed. For each entry a L{contacts.contacts.Contact} instance is created and stored in the instance dictionary
        L{contacts.AbstractContactSynchronizationModule._allContacts}.
        """
        pisiprogress.getCallback().verbose ("VCF: Loading")
        if self._vcfpath == PATH_INTERACTIVE:
            self._vcfpath = self._promptFilename("\tPath to VCF file ", "pisi_export.vcf", "You configured PISI VCF support to ask for VCF file name when running.")
        
        file = None
        try:
            file = open(self._vcfpath,  "r")
        except IOError,  e:
            pisiprogress.getCallback().error("--> Error: Could not load VCF file - we still carry on with processing:\n\t%s" %(e))
            return
        
        pisiprogress.getCallback().progress.push(0, 100)
        comps = vobject.readComponents(file)
        pisiprogress.getCallback().progress.setProgress(20) 
        pisiprogress.getCallback().update("Loading")
        amount = self._guessAmount()
        i = 0
        for x in comps:
            atts = {}
            atts['firstname'] = self._extractAtt(x, 'x.n.value.given')
            atts['middlename'] = self._extractAtt(x, 'x.n.value.additional')
            atts['lastname'] = self._extractAtt(x, 'x.n.value.family')
            
            atts['email'] = self._extractAtt(x, 'x.email.value')
            atts['title'] = self._extractAtt(x, 'x.title.value')

            # phone numbers
            try:
                for tel in x.contents['tel']:
                    if tel.params['TYPE'] == VCF_PHONETYPE_HOME:
                        atts['phone'] = tel.value
                    elif tel.params['TYPE'] == VCF_PHONETYPE_MOBILE:
                        atts['mobile'] = tel.value
                    elif tel.params['TYPE'] == VCF_PHONETYPE_WORK:
                        atts['officePhone'] = tel.value
                    elif tel.params['TYPE'] == VCF_PHONETYPE_FAX:
                        atts['fax'] = tel.value
            except KeyError:
                pass    # no phone number; that's alright

            # addresses
            try:
                for addr in x.contents['adr']:
                    if addr.params['TYPE'] == VCF_ADDRESSTYPE_HOME:
                        atts['homeStreet'] = addr.value.street
                        atts['homeCity'] = addr.value.city
                        atts['homeState'] = addr.value.region
                        atts['homePostalCode'] = addr.value.code
                        atts['homeCountry'] = addr.value.country
                    elif addr.params['TYPE'] == VCF_ADDRESSTYPE_WORK:
                        atts['businessStreet'] = addr.value.street
                        atts['businessCity'] = addr.value.city
                        atts['businessState'] = addr.value.region
                        atts['businessPostalCode'] = addr.value.code
                        atts['businessCountry'] = addr.value.country
            except KeyError:
                pass    # no addresses here; that's fine
            
            try:
                atts['businessOrganisation'] = x.org.value[0]
                atts['businessDepartment'] = x.org.value[1]
            except:
                pass

            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c
            self._rawData[id] = x
            if i < amount:
                i += 1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / amount))
            pisiprogress.getCallback().update('Loading')
            
        file.close()
        pisiprogress.getCallback().progress.drop()

    def _createRawAttribute(self, c,  j, att,   value,  params = []):
        """
        Supporting function for adding a single attribute to vcard raw object
        """
        try:
            v = None
            if value != None:
                exec ("v =" + value)
                if v != None and v != '':
                    j.add(att)
                    exec ("j." + att + ".value = " + value)
                    for param in params:
                        exec("j." + att + "." + param[0] + "=" + param[1] )
        except KeyError:
            pass    # this attribute is not available; that's not a problem for us
            
    def _createNameAttribute(self,  c,  j):
        family = c.attributes['lastname']
        if family == None:
            family = ''
        given = c.attributes['firstname']
        if given == None:
            given = ''
        additional = c.attributes['middlename']
        if additional == None:
            additional = ''
        if family == '' and given == '' and additional == '':
            c.prettyPrint()
        nameEntry = vobject.vcard.Name(family = family,  given = given,  additional = additional)
        n = j.add('n')
        n.value = nameEntry

    def _createPhoneAttribute(self,  c,  j,  type):
        """
        Create and append phone entry
        
        Phone entries are a bit tricky - you cannot access each of them directly as they all have the same attribute key (tel). Consequently, we have to access the dictionary for phones directly.
        """
        try:
            if type == VCF_PHONETYPE_HOME:
                value = c.attributes['phone']
            elif type == VCF_PHONETYPE_WORK:
                value = c.attributes['officePhone']
            elif type == VCF_PHONETYPE_MOBILE:
                value = c.attributes['mobile']
            elif type == VCF_PHONETYPE_FAX:
                value = c.attributes['fax']
            if value == '' or value == None:
                return
            tel = j.add('tel')
            tel.value = value
            tel.type_param = type
        except KeyError:
            pass    # that's fine - this phone type is not available
            
    def _attFromDict(self,  dict,  att):
        try:
            return dict[att]
        except KeyError:
            return  ''
    
    def _createAddressAttribute(self,  c,  j,  type):
        """
        Create and append address entry
        
        Entry is only created if city is set.
        """        
        if type == VCF_ADDRESSTYPE_HOME:
            street = self._attFromDict(c.attributes,  'homeStreet')
            postalCode = self._attFromDict(c.attributes,  'homePostalCode')
            city = self._attFromDict(c.attributes,  'homeCity')
            country = self._attFromDict(c.attributes,  'homeCountry')
            state = self._attFromDict(c.attributes,  'homeState')
        elif type == VCF_ADDRESSTYPE_WORK:
            street = self._attFromDict(c.attributes,  'businessStreet')
            postalCode = self._attFromDict(c.attributes,  'businessPostalCode')
            city = self._attFromDict(c.attributes,  'businessCity')
            country = self._attFromDict(c.attributes,  'businessCountry')
            state = self._attFromDict(c.attributes,  'businessState')
        if city == None or city == '':
            return
        addr = j.add('adr')
        addr.value = vobject.vcard.Address(street = street,  code = postalCode,  city = city,  country = country,  region = state)
        addr.type_param = type
    
    def _createBusinessDetails(self,  c,  j):
        """
        Creates an entry for business organzation und unit.
        """
        if c.attributes.has_key('businessOrganisation'):
            o = c.attributes['businessOrganisation']
            if o == None or o == '':
                return
            list = []
            list.append(o)
            if c.attributes.has_key('businessDepartment'):
                ou = c.attributes['businessDepartment']
                if ou != None and ou != '':
                    list.append(ou)
            j.add('org')
            j.org.value = list
    
    def _createRawVcard(self,  c):
        """
        Converts internal contact entry to VObject format
        """
        j = vobject.vCard()
        self._createNameAttribute(c, j)
        
        if c.attributes['firstname']:
            if c.attributes['lastname']:
                fn = c.attributes['firstname'] + ' ' +  c.attributes['lastname']
            else:
                fn = c.attributes['firstname']
        else:
            fn = c.attributes['lastname']
        self._createRawAttribute(c,  j,  'fn',  "'''" + fn + "'''")
        self._createRawAttribute(c,  j,  'title',  "c.attributes['title']")

        self._createRawAttribute(c,  j,  'email',  "c.attributes['email']",  [['type_param',  "'INTERNET'"]])
        self._createPhoneAttribute(c, j,  VCF_PHONETYPE_HOME)
        self._createPhoneAttribute(c, j,  VCF_PHONETYPE_WORK)
        self._createPhoneAttribute(c, j,  VCF_PHONETYPE_MOBILE)
        self._createPhoneAttribute(c, j,  VCF_PHONETYPE_FAX)
        
        self._createAddressAttribute(c,  j, VCF_ADDRESSTYPE_HOME)
        self._createAddressAttribute(c,  j, VCF_ADDRESSTYPE_WORK)
        self._createBusinessDetails(c,  j)
        return j
    
    def saveModifications( self ):
        """
        Save whatever changes have come by
        
        We first make a backup of the old file. Then, the entire set of information is dumped into a new file. (I hope, you don't mind the order of your entries).
        Thereby, we shouldn't create entries from the scratch when they were not changed in the meantime (in the likely case of PISI not supporting all fields
        within the VCF format and file).
        """
        pisiprogress.getCallback().verbose("VCF module: I apply %d changes now" %(len(self._history)))

        if len(self._history) == 0:
            return      # don't touch anything if there haven't been any changes
            
        # rename old file         
        try:
            bakFilename = os.path.join(self._folder,  os.path.basename(self._vcfpath))
            os.rename(self._vcfpath,  bakFilename)
        except OSError,  e:
            pisiprogress.getCallback().verbose("\tError when backing up old VCF file - we still carry on with processing:\n\t%s" %(e))
        
        # there is no unique key for contacts at all in VCF files; we have to use our global keys (name + given name)

        file = open(self._vcfpath,  "w")
        
        i = 0
        for actionItem in self._history:
            action = actionItem[0]
            contactID = actionItem[1]
            if action == ACTIONID_DELETE:
                del self._rawData[contactID]
                pisiprogress.getCallback().verbose("\t\t<vcf> deleting %s" %(contactID))
            elif action == ACTIONID_ADD or action == ACTIONID_MODIFY:
                c = self.getContact(contactID)
                self._rawData[contactID] = self._createRawVcard(c)
                pisiprogress.getCallback().verbose("\t\t<vcf> adding or replacing %s" %(contactID))                
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 70 / len(self._history))
            pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().progress.setProgress(70)
        pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().verbose("\tVCF: Writing through file")
        for x in self._rawData.values():
            file.write(x.serialize())
            file.write("\n")
        pisiprogress.getCallback().verbose("\tNew VCF file saved to %s; \n\tbackup file is located in %s." %(self._vcfpath,  bakFilename))
        file.close()
