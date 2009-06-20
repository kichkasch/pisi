"""
Synchronize with SIM card via DBUS (currently used as default contacts storage in SHR)

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

class SynchronizationModule(contacts.AbstractContactSynchronizationModule):
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
        pisiprogress.getCallback().verbose("DBUS_SIM module loaded")

    def load(self):
        """
        Load all data from backend
        """
        pisiprogress.getCallback().verbose ("DBUS_SIM: Loading")
        pisiprogress.getCallback().progress.push(0, 100)        
        bus = dbus.SystemBus()
        gsm_device_obj = bus.get_object(DBUS_GSM_DEVICE[0], DBUS_GSM_DEVICE[1])
        sim = dbus.Interface(gsm_device_obj,DBUS_SIM)
        dbusContacts = sim.RetrievePhonebook(DBUS_CONTACTS)
        pisiprogress.getCallback().progress.setProgress(20) 
        pisiprogress.getCallback().update("Loading")
        i = 0
        for c in dbusContacts:
            id = c[0]
            name = c[1]
            number = c[2]
            atts = {}
            title,  first,  last,  middle = pisitools.parseFullName(name)
            atts['title'] = title
            atts['firstname'] = first
            atts['lastname'] = last
            atts['middlename'] = middle
            atts['mobile'] = number.strip()

            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c
            i+=1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / len(dbusContacts)))
            pisiprogress.getCallback().update('Loading')

        pisiprogress.getCallback().progress.drop()

    def saveModifications( self ):
        """
        Save whatever changes have come by
        """
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose("\t\t<dummy> adding %s" %(id))
                pass    # implementation goes here
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<dummy> deleting %s" %(id))
                pass    # implementation goes here
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<dummy> replacing %s" %(id))
                pass    # implementation goes here
 
