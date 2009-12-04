"""
Sync contact information with Evolution on a Desktop.

This file is part of Pisi.

Implementation is based on *evolution-python* (L{http://live.gnome.org/Conduit/evolution-python}, 
L{http://www.johnstowers.co.nz/blog/index.php/2007/05/30/python-bindings-for-evolution/}).

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
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "Contacts Evolution")
        self.verbose = verbose
        pisiprogress.getCallback().verbose("Evolution contacts module loaded")
            
        # pull configuration data and whatever initialization might be required

    def load(self):
        """
        Load all data from backend
        """
        pass    # implementation goes here

    def saveModifications( self ):
        """
        Save whatever changes have come by
        """
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose("\t\t<evolution contacts> adding %s" %(id))
                pass    # implementation goes here
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<evolution contacts> deleting %s" %(id))
                pass    # implementation goes here
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<evolution contacts> replacing %s" %(id))
                pass    # implementation goes here
 
