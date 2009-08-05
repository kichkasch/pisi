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
        The settings from the configuration file are loaded. 
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "OPIMD")
        pisiprogress.getCallback().verbose('contact opimd module loaded using file')
        self._idMappingInternalGlobal = {}
        self._idMappingGlobalInternal = {}

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
                
            atts['firstname'] = contactObject.GetContent().get('Name')
            if not atts['firstname']:
                atts['firstname'] = ''
            atts['middlename'] = contactObject.GetContent().get('Middlename')
            if not atts['middlename']:
                atts['middlename'] = ''
            atts['lastname'] =  contactObject.GetContent().get('Surname')
            if not atts['lastname']:
                atts['lastname'] = ''
            atts['title'] = contactObject.GetContent().get('Title')
            if not atts['title']:
                atts['title'] = ''
            atts['email'] = contactObject.GetContent().get('Email')
            if not atts['email']:
                atts['email'] = ''
            atts['mobile'] = contactObject.GetContent().get('Phone')
            if not atts['mobile']:
                atts['mobile'] = contactObject.GetContent().get('Cellphone')
                if not atts['mobile']:
                    atts['mobile'] = ''
            atts['phone'] = contactObject.GetContent().get('HomePhone')
            if not atts['phone']:
                atts['phone'] = ''
            atts['officePhone'] = contactObject.GetContent().get('WorkPhone')
            if not atts['officePhone']:
                atts['officePhone'] = ''

            #
            # that's it for now - not clear, which attributes will finally be supported :(
            # todo: Finish off!

            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c
            self._idMappingGlobalInternal[id] = contact.get('Path')
            self._idMappingInternalGlobal[contact.get('Path')] = id
            
            i+=1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / count))
            pisiprogress.getCallback().update('Loading')

    def _saveOperationAdd(self, id):
        contact = self.getContact(id)

        bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
        dbusObject = bus.get_object(BUSNAME, PATH_CONTACTS)
        contacts = dbus.Interface(dbusObject, dbus_interface=INTERFACE_CONTACTS)

        fields = {}
        fields['Name'] = contact.attributes['firstname']
        fields['Surname'] = contact.attributes['lastname']
        fields['Middlename'] = contact.attributes['middlename']
        fields['Title'] = contact.attributes['title']
        fields['Email'] = contact.attributes['email']
        fields['Cellphone'] = contact.attributes['mobile']
        fields['WorkPhone'] = contact.attributes['officePhone']
        fields['HomePhone'] = contact.attributes['phone']
        contacts.Add(fields)
    
    def _saveOperationDelete(self, id):
        path = self._idMappingGlobalInternal[id]
        bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
        dbusObject = bus.get_object(BUSNAME, path)
        contactObject = dbus.Interface(dbusObject, dbus_interface= INTERFACE_CONTACT)
        contactObject.Delete()

    def _saveOperationModify(self,  id):
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
