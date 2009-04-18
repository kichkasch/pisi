"""
A dummy to make a new module (here for calendar)

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

from events import events
from pisiconstants import *
import pisiprogress

class SynchronizationModule(events.AbstractCalendarSynchronizationModule):
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{events.AbstractCalendarSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded. 

        @param modulesString: is a small string to help you make a unique id. It is the two modules configuration-names concatinated.
        @param config: is the configuration from ~/.pisi/conf. Use like config.get(configsection,'user')
        @param configsection: is the configuration from ~/.pisi/conf. Use like config.get(configsection,'user')
        @param folder: is a string with the location for where your module can save its own files if necessary
        @param verbose: should make your module "talk" more
        @param soft: should tell you if you should make changes (ie. save)
        """
        events.AbstractCalendarSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "Calendar DUMMY")
        self.verbose = verbose
        pisiprogress.getCallback().verbose("Dummy module loaded")
            
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
                pisiprogress.getCallback().verbose("\t\t<dummy> adding %s" %(id))
                pass    # implementation goes here
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<dummy> deleting %s" %(id))
                pass    # implementation goes here
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<dummy> replacing %s" %(id))
                pass    # implementation goes here
 
