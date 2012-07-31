""" 
Syncronize with a SQLite database

General information about the database specs of Qtopia PIM is provided on this site: http://doc.trolltech.com/qtopia4.3/database-specification.html
Details may be obtained from a source code release (ftp://ftp.trolltech.com/qtopia/source/) in folder "src/libraries/qtopiapim/resources".

This file is part of Pisi.

Pisi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pisi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pisi.  If not, see <http://www.gnu.org/licenses/>

"""

import os.path
import sqlite3 
import sys,os,re
from types import *

# Allows us to import contact
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from contacts import contacts
from pisiconstants import *
import pisiprogress

QTOPIADB_PHONETYPE_HOME = 1
"""Constant value for phone type used in QTOPIA database - value for type home phone."""
QTOPIADB_PHONETYPE_MOBILE = 256
"""Constant value for phone type used in QTOPIA database - value for type mobile phone."""
QTOPIADB_PHONETYPE_MOBILE_PRIVATE = 257
"""Constant value for phone type used in QTOPIA database - value for type mobile phone private."""
QTOPIADB_PHONETYPE_MOBILE_WORK = 258
"""Constant value for phone type used in QTOPIA database - value for type mobile phone work."""
QTOPIADB_PHONETYPE_OFFICE = 2
"""Constant value for phone type used in QTOPIA database - value for type office phone."""
QTOPIADB_PHONETYPE_FAX = 514
"""Constant value for phone type used in QTOPIA database - value for type fax."""
QTOPIADB_ADDRESSTYPE_PRIVATE = 1
"""Constant value for address type used in QTOPIA database - value for type home address."""
QTOPIADB_ADDRESSTYPE_BUSINESS = 2
"""Constant value for address type used in QTOPIA database - value for type business address."""

class SynchronizationModule(contacts.AbstractContactSynchronizationModule):
    """
    The implementation of the interface L{contacts.AbstractContactSynchronizationModule} for SQLite persistence backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded. 
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "SQLite")
        self._dbpath = config.get(configsection,'database')
        pisiprogress.getCallback().verbose('contact sqlite module loaded using file %s' % (self._dbpath))
        self._idMappingInternalGlobal = {}
        self._idMappingGlobalInternal = {}

    def load(self):
        """
        Loads all attributes for all contact entries from the SQLite database
        
        For each entry a new L{contacts.contacts.Contact} instance is created and stored in the instance dictionary L{contacts.AbstractContactSynchronizationModule._allContacts}.
        Several requests to the database are executed in order to get all the detailled information about phone numbers and addresses, etc. as well.
        """
        pisiprogress.getCallback().verbose("SQLite: Loading")
        database = sqlite3.connect(self._dbpath, isolation_level=None)
        db_call = "select recid, firstname, middlename, lastname, company, title, department from contacts"
        contactEntries = database.execute(db_call).fetchall()

        pisiprogress.getCallback().progress.setProgress(20) # we guess that the actual query took up 20 % of the time - the remaining 80 % are taken by parsing the content ...
        pisiprogress.getCallback().update('Loading')
        i=0
        for contactEntry in contactEntries:
            atts = {}
            recid = contactEntry[0]
            atts['firstname'] = contactEntry[1]
            atts['middlename'] = contactEntry[2]
            atts['lastname'] = contactEntry[3]
            atts['businessOrganisation'] = contactEntry[4]
            atts['title'] = contactEntry[5]
            atts['businessDepartment'] = contactEntry[6]
            
            # fetch detail information as well
            db_call = "select phone_number, phone_type from contactphonenumbers where recid = %s" %(recid)
            phoneEntries = database.execute(db_call).fetchall()
            for phoneEntry in phoneEntries:
                type = int(phoneEntry[1])
                if type == QTOPIADB_PHONETYPE_MOBILE or type == QTOPIADB_PHONETYPE_MOBILE_PRIVATE or type == QTOPIADB_PHONETYPE_MOBILE_WORK:     
                    atts['mobile'] = phoneEntry[0]
                elif type == QTOPIADB_PHONETYPE_HOME:     
                    atts['phone'] = phoneEntry[0]
                elif type == QTOPIADB_PHONETYPE_OFFICE:     
                    atts['officePhone'] = phoneEntry[0]
                elif type == QTOPIADB_PHONETYPE_FAX:     
                    atts['fax'] = phoneEntry[0]
            
            db_call = "select addr from emailaddresses where recid = %s" %(recid)
            emailEntries = database.execute(db_call).fetchall()
            for emailEntry in emailEntries:
                atts['email'] = emailEntry[0]
            
            db_call = "select street, city, state, zip, country, addresstype from contactaddresses where recid = %s" %(recid)
            addressEntries = database.execute(db_call).fetchall()
            for addressEntry in addressEntries:
                type = int(addressEntry[5])
                if type == QTOPIADB_ADDRESSTYPE_PRIVATE:       
                    atts['homeStreet'] = addressEntry[0]
                    atts['homeCity'] = addressEntry[1]
                    atts['homeState'] = addressEntry[2]
                    atts['homePostalCode'] = addressEntry[3]
                    atts['homeCountry'] = addressEntry[4]
                if type == QTOPIADB_ADDRESSTYPE_BUSINESS:       
                    atts['businessStreet'] = addressEntry[0]
                    atts['businessCity'] = addressEntry[1]
                    atts['businessState'] = addressEntry[2]
                    atts['businessPostalCode'] = addressEntry[3]
                    atts['businessCountry'] = addressEntry[4]
            
            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c
            
            self._idMappingGlobalInternal[id] = recid
            self._idMappingInternalGlobal[recid] = id
            i+=1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / len(contactEntries)))
            pisiprogress.getCallback().update('Loading')
        database.close() 

    def _quoteString(self,  contact, st):
        """
        Supporting function to get around problems with integrating 'None' values and KeyErrors if an attribute is not available
        """
        try:
            if type(contact.attributes[st]) == NoneType:
                return "''"
            else:
                val = contact.attributes[st].replace("'",  "''")    # this is SQL standard; one apostrophe has to be quoted by another one
                return "'" +val + "'"
        except TypeError:
            return "''"
        except KeyError:
            return "''"

    def _saveOperationAdd(self,  id,  database):
        """
        Save all new entries to SQLite database
        
        The information from all the attributes in the Contact entry are stored 1st in the major table and afterwards in all the related tables (addresses, phone numbers, etc.). Thereby the foreign keys are taken care of.
        """
        contact = self.getContact(id)
        # todo: What is this context thing about? We just put 1 here for now - all entries manually inserted in the phone have 1 as well.
        st = "insert into contacts (firstname, middlename, lastname, default_email, default_phone, context, company, title, department) values (%s, %s, %s, %s, %s, 1, %s, %s, %s)" %(
                                                                                                                                self._quoteString(contact, 'firstname'), 
                                                                                                                                self._quoteString(contact, 'middlename'), 
                                                                                                                                self._quoteString(contact, 'lastname'), 
                                                                                                                                self._quoteString(contact, 'email'), 
                                                                                                                                self._quoteString(contact, 'mobile'), 
                                                                                                                                self._quoteString(contact, 'businessOrganisation'), 
                                                                                                                                self._quoteString(contact, 'title'), 
                                                                                                                                self._quoteString(contact, 'businessDepartment'))
        database.execute(st)
        db_call = "select recid from contacts where firstname=%s and lastname=%s" %(
                                                                                    self._quoteString(contact, 'firstname'), 
                                                                                    self._quoteString(contact, 'lastname') )
        recidEntry = database.execute(db_call).fetchall()[0]    # here must only be a single entry (assuming that we have each combination of firstname and surname only once
        recid = recidEntry[0]
        
        try:
            if contact.attributes['mobile'] != '' and contact.attributes['mobile'] != None:
                st = "insert into contactphonenumbers (phone_number, recid, phone_type) values (%s, %d, %d)" %(
                                                                                                                                        self._quoteString(contact, 'mobile'), 
                                                                                                                                        recid, 
                                                                                                                                        QTOPIADB_PHONETYPE_MOBILE)
                database.execute(st)
        except KeyError:
            pass    # that's fine - we haven't got this phone number here

        try:
            if contact.attributes['email'] != '' and contact.attributes['email'] != None:
                st = "insert into emailaddresses (recid, addr) values (%d,  %s)" %(
                                                                                    recid, 
                                                                                    self._quoteString(contact, 'email'))
                database.execute(st)
        except KeyError:
            pass    # that's fine - we haven't got this phone number here
            
        try:
            if contact.attributes['phone'] != '' and contact.attributes['phone'] != None:
                st = "insert into contactphonenumbers (phone_number, recid, phone_type) values (%s, %d, %d)" %(
                                                                                                                                        self._quoteString(contact, 'phone'), 
                                                                                                                                        recid, 
                                                                                                                                        QTOPIADB_PHONETYPE_HOME)
                database.execute(st)
        except KeyError:
            pass    # that's fine - we haven't got this phone number here

        try:
            if contact.attributes['officePhone'] != '' and contact.attributes['officePhone'] != None:
                st = "insert into contactphonenumbers (phone_number, recid, phone_type) values (%s, %d, %d)" %(
                                                                                                                                        self._quoteString(contact, 'officePhone'), 
                                                                                                                                        recid, 
                                                                                                                                        QTOPIADB_PHONETYPE_OFFICE)
                database.execute(st)
        except KeyError:
            pass    # that's fine - we haven't got this phone number here
        
        try:
            if contact.attributes['fax'] != '' and contact.attributes['fax'] != None:
                st = "insert into contactphonenumbers (phone_number, recid, phone_type) values (%s, %d, %d)" %(
                                                                                                                                        self._quoteString(contact, 'fax'), 
                                                                                                                                        recid, 
                                                                                                                                        QTOPIADB_PHONETYPE_FAX)
                database.execute(st)
        except KeyError:
            pass    # that's fine - we haven't got this phone number here
            
        # we assume, if somebody supplies information about an address, first the city (locality) name would be provided
        # addresstype is set to 1 - the type for private addresses
        try:
            if contact.attributes['homeCity'] != '' and contact.attributes['homeCity'] != None:
                st = "insert into contactaddresses (street, city, state, zip, country, addresstype,  recid) values (%s, %s, %s, %s, %s, %d, %d)" %(
                                                                                                                                        self._quoteString(contact, 'homeStreet'),
                                                                                                                                        self._quoteString(contact, 'homeCity'),
                                                                                                                                        self._quoteString(contact, 'homeState'),
                                                                                                                                        self._quoteString(contact, 'homePostalCode'),
                                                                                                                                        self._quoteString(contact, 'homeCountry'),
                                                                                                                                        QTOPIADB_ADDRESSTYPE_PRIVATE, 
                                                                                                                                        recid)
                database.execute(st)
        except KeyError:
            pass    # that's fine - we haven't got this address here
                
        # addresstype is set to 2 - the type for business addresses
        try:
            if contact.attributes['businessCity'] != '' and contact.attributes['businessCity'] != None:
                st = "insert into contactaddresses (street, city, state, zip, country, addresstype,  recid) values (%s, %s, %s, %s, %s, %d, %d)" %(
                                                                                                                                        self._quoteString(contact, 'businessStreet'),
                                                                                                                                        self._quoteString(contact, 'businessCity'),
                                                                                                                                        self._quoteString(contact, 'businessState'),
                                                                                                                                        self._quoteString(contact, 'businessPostalCode'),
                                                                                                                                        self._quoteString(contact, 'businessCountry'),
                                                                                                                                        QTOPIADB_ADDRESSTYPE_BUSINESS, 
                                                                                                                                        recid)
                database.execute(st)
        except KeyError:
            pass    # that's fine - we haven't got this address here
        
    def _saveOperationDelete(self,  id,  database):
        """
        Finally deletes the contact entry identified by its ID in the database
        
        Besides the deletion in the major table all traces in related tables (addresses phone numbers, etc.) are erased as well.
        """
        recid = self._idMappingGlobalInternal[id]
        st = "delete from contacts where recid=%s" %(recid)
        database.execute(st)
        st = "delete from emailaddresses where recid=%s" %(recid)
        database.execute(st)
        st = "delete from contactphonenumbers where recid=%s" %(recid)
        database.execute(st)
        st = "delete from contactaddresses where recid=%s" %(recid)
        database.execute(st)

    def _saveOperationModify(self,  id,  database):
        """
        Applies changes from an entry to the SQLite database
        
        In order to keep things simple the old value is simply erased using the method L{_saveOperationDelete} and a new one is inserted (L{_saveOperationAdd}).
        """
        self._saveOperationDelete(id,  database)
        self._saveOperationAdd(id,  database)

    def saveModifications(self):
        """
        Save whatever changes have come by
        
        The history of actions for this data source is iterated. For each item in there the corresponding action is carried out on the item in question.
        This function is just a dispatcher to one of the three functions L{_saveOperationAdd}, L{_saveOperationDelete} or L{_saveOperationModify}.
        """
        pisiprogress.getCallback().verbose("SQLite module: I apply %d changes now" %(len(self._history)))
        database = sqlite3.connect(self._dbpath, isolation_level=None)
        #c = database.cursor()
        i=0
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose( "\t\t<sqlite> adding %s" %(id))
                self._saveOperationAdd(id, database)
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<sqlite> deleting %s" %(id))
                self._saveOperationDelete(id,  database)
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<sqlite> replacing %s" %(id))
                self._saveOperationModify(id,  database)
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 90 / len(self._history))
            pisiprogress.getCallback().update('Storing')
        database.commit()
        database.close()
        pisiprogress.getCallback().progress.setProgress(100)
        pisiprogress.getCallback().update('Storing')
