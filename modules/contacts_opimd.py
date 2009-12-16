""" 
Syncronize with OPIMD

General information about opimd is available here (L{http://wiki.openmoko.org/wiki/Opimd}).

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
import sys,os,re
import dbus, e_dbus

# Allows us to import contact
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from contacts import contacts
from pisiconstants import *
import pisiprogress

BUSNAME = "org.freesmartphone.opimd"
PATH_CONTACTS = "/org/freesmartphone/PIM/Contacts"
INTERFACE_CONTACTS = "org.freesmartphone.PIM.Contacts"
INTERFACE_QUERY = "org.freesmartphone.PIM.ContactQuery"
INTERFACE_CONTACT = "org.freesmartphone.PIM.Contact"

BACKEND_TYPE_SQLITE = "SQLite-Contacts"
#CONF_AUTOPREFIX = "phone_autoprefix"

class SynchronizationModule(contacts.AbstractContactSynchronizationModule):
    """
    The implementation of the interface L{contacts.AbstractContactSynchronizationModule} for OPIMD persistence backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "OPIMD")
        pisiprogress.getCallback().verbose('contact opimd module loaded using file')
#        try:
#            mode = config.get(configsection, CONF_AUTOPREFIX)
#            self._autoPrefix = mode and mode.lower() == "true"
#        except:
#            self._autoPrefix = False         
        self._idMappingInternalGlobal = {}
        self._idMappingGlobalInternal = {}

    def _extractValue(self, atts, attName, contactObject, opimdField):
        """
        Supporting function to extract a single attribute value
        """
        atts[attName] = contactObject.GetContent().get(opimdField)
        if not atts[attName]:
            atts[attName] = ''

    def load(self):
        """
        Loads all attributes for all contact entries from the OPIMD backend
        
        For each entry a new L{contacts.contacts.Contact} instance is created and stored in the instance dictionary L{contacts.AbstractContactSynchronizationModule._allContacts}.
        """
        pisiprogress.getCallback().verbose("OPIMD: Loading")

        bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
        dbusObject = bus.get_object(BUSNAME, PATH_CONTACTS)
        contactsInterface = dbus.Interface(dbusObject, dbus_interface= INTERFACE_CONTACTS)
        query = contactsInterface.Query({}) 

        dbusObject = bus.get_object(BUSNAME, query)
        query = dbus.Interface(dbusObject, dbus_interface=INTERFACE_QUERY)
        count = query.GetResultCount()

        pisiprogress.getCallback().progress.setProgress(20) # we guess that the actual query took up 20 % of the time - the remaining 80 % are taken by parsing the content ...
        pisiprogress.getCallback().update('Loading')
        i=0
        for contact in query.GetMultipleResults(count):
            atts = {}

            dbusObject = bus.get_object(BUSNAME, contact.get('Path'))
            contactObject = dbus.Interface(dbusObject, dbus_interface= INTERFACE_CONTACT)
            
            if contactObject.GetUsedBackends()[0]!= BACKEND_TYPE_SQLITE:
                continue    # let's only go for sqlite entries
            
            self._extractValue(atts, 'firstname', contactObject, 'Name')
            self._extractValue(atts, 'middlename', contactObject, 'Middlename')
            self._extractValue(atts, 'lastname', contactObject, 'Surname')
            self._extractValue(atts, 'email', contactObject, 'E-mail')
            self._extractValue(atts, 'mobile', contactObject, 'Phone')
            if not atts['mobile']:
                self._extractValue(atts, 'mobile', contactObject, 'Cell phone')
            self._extractValue(atts, 'phone', contactObject, 'Home phone')
            self._extractValue(atts, 'officePhone', contactObject, 'Work phone')
            self._extractValue(atts, 'fax', contactObject, 'Fax phone')
#            if self._autoPrefix:
#                self._dePrefixNumbers(atts)
            
            self._extractValue(atts, 'title', contactObject, 'Title')
            self._extractValue(atts, 'businessOrganisation', contactObject, 'Organisation')
            self._extractValue(atts, 'businessDepartment', contactObject, 'Departement')
            
            self._extractValue(atts, 'businessStreet', contactObject, 'BusinessStreet')
            self._extractValue(atts, 'businessPostalCode', contactObject, 'BusinessPostalCode')
            self._extractValue(atts, 'businessCity', contactObject, 'BusinessCity')
            self._extractValue(atts, 'businessCountry', contactObject, 'BusinessCountry')
            self._extractValue(atts, 'businessState', contactObject, 'BusinessState')
            
            self._extractValue(atts, 'homeStreet', contactObject, 'HomeStreet')
            self._extractValue(atts, 'homePostalCode', contactObject, 'HomePostalCode')
            self._extractValue(atts, 'homeCity', contactObject, 'HomeCity')
            self._extractValue(atts, 'homeCountry', contactObject, 'HomeCountry')
            self._extractValue(atts, 'homeState', contactObject, 'HomeState')

            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c
            self._idMappingGlobalInternal[id] = contact.get('Path')
            self._idMappingInternalGlobal[contact.get('Path')] = id
            
            i+=1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / count))
            pisiprogress.getCallback().update('Loading')

    def _saveOneEntry(self, fields, fieldName, contact,  attribute):
        try:
            fields[fieldName] = contact.attributes[attribute]
        except KeyError:
            fields[fieldName] = ""
        if not fields[fieldName]:
            fields[fieldName] = ""

    def _saveOperationAdd(self, id):
        """
        Making changes permanent: Add a single contact instance to backend
        """
        contact = self.getContact(id)

        bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
        dbusObject = bus.get_object(BUSNAME, PATH_CONTACTS)
        contacts = dbus.Interface(dbusObject, dbus_interface=INTERFACE_CONTACTS)
        
#        if self._autoPrefix:
#            self._prefixNumbers(contact.attributes)

        fields = {}
        self._saveOneEntry(fields, 'Name', contact,'firstname' )
        self._saveOneEntry(fields, 'Surname', contact, 'lastname')
        self._saveOneEntry(fields, 'Middlename', contact,'middlename' )
        self._saveOneEntry(fields, 'E-mail', contact, 'email')
        self._saveOneEntry(fields, 'Cell phone', contact, 'mobile')
        self._saveOneEntry(fields, 'Work phone', contact, 'officePhone')
        self._saveOneEntry(fields, 'Home phone', contact, 'phone')
        self._saveOneEntry(fields, 'Fax phone', contact,'fax' )

        self._saveOneEntry(fields, 'Title', contact, 'title')
        self._saveOneEntry(fields, 'Organisation', contact,'businessOrganisation' )
        self._saveOneEntry(fields, 'Departement', contact, 'businessDepartment')

        self._saveOneEntry(fields, 'BusinessStreet', contact, 'businessStreet')
        self._saveOneEntry(fields, 'BusinessPostalCode', contact, 'businessPostalCode')
        self._saveOneEntry(fields, 'BusinessCity', contact, 'businessCity')
        self._saveOneEntry(fields, 'BusinessCountry', contact, 'businessCountry')
        self._saveOneEntry(fields, 'BusinessState', contact, 'businessState')
        
        self._saveOneEntry(fields, 'HomeStreet', contact,'homeStreet' )
        self._saveOneEntry(fields, 'HomePostalCode', contact, 'homePostalCode')
        self._saveOneEntry(fields, 'HomeCity', contact,'homeCity' )
        self._saveOneEntry(fields, 'HomeCountry', contact, 'homeCountry')
        self._saveOneEntry(fields,'HomeState' , contact, 'homeState')
        
        contacts.Add(fields)
    
    def _saveOperationDelete(self, id):
        """
        Making changes permanent: Remove a single contact instance from backend
        """
        path = self._idMappingGlobalInternal[id]
        bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
        dbusObject = bus.get_object(BUSNAME, path)
        contactObject = dbus.Interface(dbusObject, dbus_interface= INTERFACE_CONTACT)
        contactObject.Delete()

    def _saveOperationModify(self,  id):
        """
        Making changes permanent: Update a single contact instance in backend
        """
        self._saveOperationDelete(id)
        self._saveOperationAdd(id)

    def saveModifications(self):
        """
        Save whatever changes have come by
        
        The history of actions for this data source is iterated. For each item in there the corresponding action is carried out on the item in question.
        This function is just a dispatcher to one of the three functions L{_saveOperationAdd}, L{_saveOperationDelete} or L{_saveOperationModify}.
        """
        pisiprogress.getCallback().verbose("OPIMD module: I apply %d changes now" %(len(self._history)))
        
        i=0
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose( "\t\t<opimd> adding %s" %(id))
                self._saveOperationAdd(id)
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<opimd> deleting %s" %(id))
                self._saveOperationDelete(id)
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<opimd> replacing %s" %(id))
                self._saveOperationModify(id)
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 90 / len(self._history))
            pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().progress.setProgress(100)
        pisiprogress.getCallback().update('Storing')
