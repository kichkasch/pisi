""" 
Import from SIM card

This file is part of Pisi.

SIM import is pretty much based on the idea from this side:
U{http://wiki.openmoko.org/wiki/Import_Sim_Contacts}

It is not functional yet - implementation was only started and is not really continued as the priorities are different right now.

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

import sys,os,datetime
# Allows us to import event
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
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
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "SIM")
        self.verbose = verbose
        pisiprogress.getCallback().verbose("SIM module loaded")
            
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
        pisiprogress.getCallback().verbose("SIM module: I would apply %d changes now" %(len(self._history)))
        if len(self._history) == 0:
            return      # don't touch anything if there haven't been any changes

        raise ValueError("SIM module not (yet) writable!")
        
