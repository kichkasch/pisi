"""
Synchronize with simple dump file (used by Paroli)

This file is part of Pisi.

Logic is taken from U{http://www.mail-archive.com/support@lists.openmoko.org/msg04770.html}.

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

from tichy.service import Service

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
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "Contacts Paroli")
        self.verbose = verbose
        pisiprogress.getCallback().verbose("Paroli module loaded")
        self._path = config.get(configsection,'path')

    def load(self):
        """
        Load all data from backend
        """
        pass

    def _saveOperationAdd(self, id):
        """
        Writing through: Adds a single value to the Paroli backend
        """
        c = self.getContact(id)
        fullName = pisitools.assembleFullName(c)
        number = c.attributes['mobile']
        pass

    def _saveOperationDelete(self, sim, id):
        """
        Writing through: Removes a single value from the Paroli backend
        """
        pass

    def saveModifications( self ):
        """
        Save whatever changes have come by
        """
        pisiprogress.getCallback().verbose("Paroli module: I apply %d changes now" %(len(self._history)))

        i = 0
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose("\t\t<Paroli> adding %s" %(id))
                self._saveOperationAdd(sim, id)
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<Paroli> deleting %s" %(id))
                self._saveOperationDelete(sim, id)
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<Paroli> replacing %s" %(id))
                self._saveOperationDelete(sim, id)
                self._saveOperationAdd(sim, id)
            i += 1
            pisiprogress.getCallback().progress.setProgress(i * 100 / len(self._history))
            pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().progress.setProgress(100)
        pisiprogress.getCallback().update('Storing')
