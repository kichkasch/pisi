"""
Synchronize with SIM card via DBUS (currently used as default contacts storage in SHR)

This file is part of Pisi.

Check these links for background information:
- U{http://git.freesmartphone.org/?p=specs.git;a=blob_plain;f=html/org.freesmartphone.GSM.SIM.html;hb=HEAD}
- U{http://dbus.freedesktop.org/doc/dbus-python/doc/tutorial.html#data-types}
- U{http://wiki.openmoko.org/wiki/Dbus}

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

from contacts import contacts
from pisiconstants import *
import pisiprogress
import pisitools

import dbus

DBUS_GSM_DEVICE = ["org.freesmartphone.ogsmd", "/org/freesmartphone/GSM/Device"]
"""Addressing information in DBUS"""
DBUS_SIM = 'org.freesmartphone.GSM.SIM'
"""Addressing information in DBUS"""
DBUS_CONTACTS = 'contacts'
"""Addressing information in DBUS"""
DBUS_NAME_MOBILEPHONE_SUFFIX = '*'
"""String to be appended to an entry when phone number is of type 'mobile'"""
DBUS_NAME_WORKPHONE_SUFFIX = '-'
"""String to be appended to an entry when phone number is of type 'work'"""
DBUS_NAME_HOMEPHONE_SUFFIX = '+'
"""String to be appended to an entry when phone number is of type 'home'"""

PHONE_TYPE_MOBILE = 0
PHONE_TYPE_HOME = 1
PHONE_TYPE_WORK = 2

class SynchronizationModule(contacts.AbstractContactSynchronizationModule):
    """
    The implementation of the interface L{contacts.AbstractContactSynchronizationModule} for SIM Card backend accesed via DBUS
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded. 

        @param modulesString: is a small string to help you make a unique id. It is the two modules configuration-names concatinated.
        @param config: is the configuration from ~/.pisi/conf. Use like config.get(configsection,'user')
        @param configsection: is the configuration from ~/.pisi/conf. Use like config.get(configsection,'user')
        @param folder: is a string with the location for where your module can save its own files if necessary
        @param verbose: should make your module "talk" more
        @param soft: should tell you if you should make changes (ie. save)
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "Contacts DBUS SIM")
        self.verbose = verbose
        self._availableIds = {}
        for i in range (1, 101):
            self._availableIds[i] = 1
        self._idMappings = {}
        self._determineSimLimitations()        
        pisiprogress.getCallback().verbose("DBUS_SIM module loaded")

    def _determineSimLimitations(self):
        """
        Supporting function in order to auto-determine limitation of SIM card (max number of entries and max length of name)
        """
        bus = dbus.SystemBus()
        gsm_device_obj = bus.get_object(DBUS_GSM_DEVICE[0], DBUS_GSM_DEVICE[1])
        sim = dbus.Interface(gsm_device_obj,DBUS_SIM)
        infos = sim.GetPhonebookInfo(DBUS_CONTACTS)
        self._max_simentries = infos["max_index"]
        self._name_maxlength = infos["name_length"]

    def load(self):
        """
        Load all data from backend
        """
        pisiprogress.getCallback().verbose ("DBUS_SIM: Loading")
        pisiprogress.getCallback().progress.push(0, 100)        
        pisiprogress.getCallback().verbose ("  >SIM Card Limitations: %d entries maximum; no more than %d characters per name" %(self._max_simentries, self._name_maxlength))
        bus = dbus.SystemBus()
        gsm_device_obj = bus.get_object(DBUS_GSM_DEVICE[0], DBUS_GSM_DEVICE[1])
        sim = dbus.Interface(gsm_device_obj,DBUS_SIM)
        dbusContacts = sim.RetrievePhonebook(DBUS_CONTACTS)
        pisiprogress.getCallback().progress.setProgress(20) 
        pisiprogress.getCallback().update("Loading")
        i = 0
        for c in dbusContacts:
            dbus_id = c[0]
            name = c[1]
            number = c[2]
            
            del self._availableIds[dbus_id]
            
            type = PHONE_TYPE_MOBILE
            if name.endswith(DBUS_NAME_MOBILEPHONE_SUFFIX):
                name = name[:len(name) - len(DBUS_NAME_MOBILEPHONE_SUFFIX)]
            if name.endswith(DBUS_NAME_WORKPHONE_SUFFIX):
                type = PHONE_TYPE_WORK
                name = name[:len(name) - len(DBUS_NAME_WORKPHONE_SUFFIX)]
            elif name.endswith(DBUS_NAME_HOMEPHONE_SUFFIX):
                type = PHONE_TYPE_HOME
                name = name[:len(name) - len(DBUS_NAME_HOMEPHONE_SUFFIX)]
            
            atts = {}
            title,  first,  last,  middle = pisitools.parseFullName(name)
            atts['title'] = title
            atts['firstname'] = first
            atts['lastname'] = last
            atts['middlename'] = middle

            id = contacts.assembleID(atts)
            if self._allContacts.has_key(id):
                c = self._allContacts[id]
                if type == PHONE_TYPE_MOBILE:
                    c.attributes['mobile'] = number.strip()
                elif type == PHONE_TYPE_WORK:
                    c.attributes['officePhone'] = number.strip()
                elif type == PHONE_TYPE_HOME:
                    c.attributes['phone'] = number.strip()
                
            else:
                if type == PHONE_TYPE_MOBILE:
                    atts['mobile'] = number.strip()
                elif type == PHONE_TYPE_WORK:
                    atts['officePhone'] = number.strip()
                elif type == PHONE_TYPE_HOME:
                    atts['phone'] = number.strip()
                c = contacts.Contact(id,  atts)
                self._allContacts[id] = c
                self._idMappings[id] = []
            self._idMappings[id].append(dbus_id)
            i+=1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / len(dbusContacts)))
            pisiprogress.getCallback().update('Loading')
        pisiprogress.getCallback().progress.drop()

    def _saveOperationAdd(self, sim, id):
        """
        Writing through: Adds a single value to the SIM Card
        """
        c = self.getContact(id)
        fullName = pisitools.assembleFullName(c)
#        if len(fullName) > self._name_maxlength:
#            fullName = fullName[:self._name_maxlength]
        if len(fullName) > self._name_maxlength - len(DBUS_NAME_MOBILEPHONE_SUFFIX):  # let's assume, all suffixes are of same length
            fullName = fullName[:self._name_maxlength - len(DBUS_NAME_MOBILEPHONE_SUFFIX)] 
        # 1st - mobile
        if len(self._availableIds) == 0:
            return
        try:
            number = c.attributes['mobile']
            if number and number != '':
                myid = self._availableIds.keys()[0]
                sim.StoreEntry(DBUS_CONTACTS, myid, fullName + DBUS_NAME_MOBILEPHONE_SUFFIX, number)
                del self._availableIds[myid]
        except KeyError:
            pass # fine - no mobile; no entry!
        
        #2nd - home phone
        if len(self._availableIds) == 0:
            return
        try:
            number = c.attributes['phone']
            if number and number != '':
                myid = self._availableIds.keys()[0]
                sim.StoreEntry(DBUS_CONTACTS, myid, fullName + DBUS_NAME_HOMEPHONE_SUFFIX, number)
                del self._availableIds[myid]
        except KeyError:
            pass # fine - no home phone; no entry!
            
        #3rd - office phone
        if len(self._availableIds) == 0:
            return
        try:
            number = c.attributes['officePhone']
            if number and number != '':
                myid = self._availableIds.keys()[0]
                sim.StoreEntry(DBUS_CONTACTS, myid, fullName + DBUS_NAME_WORKPHONE_SUFFIX, number)
                del self._availableIds[myid]
        except KeyError:
            pass # fine - no work phone; no entry!

    def _saveOperationDelete(self, sim, id):
        """
        Writing through: Removes a single value from the SIM card
        """
        for dbus_id in self._idMappings[id]:
            sim.DeleteEntry(DBUS_CONTACTS, dbus_id)
            self._availableIds[dbus_id] = 1

    def saveModifications( self ):
        """
        Save whatever changes have come by
        """
        pisiprogress.getCallback().verbose("DBUS_SIM module: I apply %d changes now" %(len(self._history)))
        bus = dbus.SystemBus()
        gsm_device_obj = bus.get_object(DBUS_GSM_DEVICE[0], DBUS_GSM_DEVICE[1])
        sim = dbus.Interface(gsm_device_obj, DBUS_SIM)

        i = 0
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose("\t\t<DBUS_SIM> adding %s" %(id))
                self._saveOperationAdd(sim, id)
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<DBUS_SIM> deleting %s" %(id))
                self._saveOperationDelete(sim, id)
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<DBUS_SIM> replacing %s" %(id))
                self._saveOperationDelete(sim, id)
                self._saveOperationAdd(sim, id)
            i += 1
            pisiprogress.getCallback().progress.setProgress(i * 100 / len(self._history))
            pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().progress.setProgress(100)
        pisiprogress.getCallback().update('Storing')
        if len(self._availableIds.keys()) == 0:
            pisiprogress.getCallback().message("Applying changes to SIM card:\nMaximum number of entries on SIM card (%d) reached.\nSome entries were possibly dopped." %(self._max_simentries))
