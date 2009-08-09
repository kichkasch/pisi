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
            self._extractValue(atts, 'email', contactObject, 'Email')
            self._extractValue(atts, 'mobile', contactObject, 'Phone')
            if not atts['mobile']:
                self._extractValue(atts, 'mobile', contactObject, 'Cellphone')
            self._extractValue(atts, 'phone', contactObject, 'HomePhone')
            self._extractValue(atts, 'officePhone', contactObject, 'WorkPhone')
            self._extractValue(atts, 'fax', contactObject, 'FaxPhone')
            
            self._extractValue(atts, 'title', contactObject, 'Title')
            self._extractValue(atts, 'businessOrganisation', contactObject, 'Organisation')
            self._extractValue(atts, 'businessDepartment', contactObject, 'Departement')
            
            self._extractValue(atts, 'businessStreet', contactObject, 'BusinessStreet')
            self._extractValue(atts, 'businessPocalCode', contactObject, 'BusinessPocalCode')
            self._extractValue(atts, 'businessCity', contactObject, 'BusinessCity')
            self._extractValue(atts, 'businessCountry', contactObject, 'BusinessCountry')
            self._extractValue(atts, 'businessState', contactObject, 'BusinessState')
            
            self._extractValue(atts, 'homeStreet', contactObject, 'HomeStreet')
            self._extractValue(atts, 'homePocalCode', contactObject, 'HomePocalCode')
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

    def _saveOperationAdd(self, id):
        """
        Making changes permanent: Add a single contact instance to backend
        """
        contact = self.getContact(id)

        bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
        dbusObject = bus.get_object(BUSNAME, PATH_CONTACTS)
        contacts = dbus.Interface(dbusObject, dbus_interface=INTERFACE_CONTACTS)

        fields = {}
        fields['Name'] = contact.attributes['firstname']
        fields['Surname'] = contact.attributes['lastname']
        fields['Middlename'] = contact.attributes['middlename']
        fields['Email'] = contact.attributes['email']
        fields['Cellphone'] = contact.attributes['mobile']
        fields['WorkPhone'] = contact.attributes['officePhone']
        fields['HomePhone'] = contact.attributes['phone']
        fields['FaxPhone'] = contact.attributes['fax']

        fields['Title'] = contact.attributes['title']
        fields['Organisation'] = contact.attributes['businessOrganisation']
        fields['Departement'] = contact.attributes['businessDepartment']

        fields['BusinessStreet'] = contact.attributes['businessStreet']
        fields['BusinessPostalCode'] = contact.attributes['businessPostalCode']
        fields['BusinessCity'] = contact.attributes['businessCity']
        fields['BusinessCountry'] = contact.attributes['businessCountry']
        fields['BusinessState'] = contact.attributes['businessState']
        
        fields['HomeStreet'] = contact.attributes['homeStreet']
        fields['HomePostalCode'] = contact.attributes['homePostalCode']
        fields['HomeCity'] = contact.attributes['homeCity']
        fields['HomeCountry'] = contact.attributes['homeCountry']
        fields['HomeState'] = contact.attributes['homeState']
        
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
