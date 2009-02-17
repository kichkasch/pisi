#!/usr/bin/env python

"""
    A dummy to make a new module from (if one so pleases)



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

import sys,os,datetime
# Allows us to import event
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from events import events



class SynchronizationModule:
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
          * moduleString is a small string to help you make a unique id. It is the two modules configuration-names concatinated.
          * config/configsection is the configuration from ~/.pisi/conf. Use like config.get(configsection,'user')
          * folder is a string with the location for where your module can save its own files if necessary
          * verbose should make your module "talk" more
          * soft should tell you if you should make changes (ie. save)
        """
        self.vebose = verbose
        if self.vebose:
            print "Dummy module loaded"

    def allEvents( self ):
        """Returns an Events instance with all events"""
        if self.vebose:
            print "Dummy module makes some dummy events and returns them..\n \
        Dummy likes to talk about itself in third person."
        allEvents = events.Events( )
        attributes=\
            {'start':datetime.datetime(2008,7,8,14,15,0), \
             'end':datetime.datetime(2008,7,8,16,0,0), 'title':"Dummy title",\
             'description':"None", 'location':"Somewhere", 'alarm':False,\
             'alarmmin':0 \
            }
        dummyevent = events.Event( "dummyid1",False, datetime.datetime(2008,7,7,14,16,0), attributes )
        allEvents.insertEvent( dummyevent )
        attributes['start'] = datetime.datetime(2008,7,8,14,20,0)
        dummyevent = events.Event( "dummyid2","dummyid2", datetime.datetime(2008,7,8,14,15,0), attributes )
        allEvents.insertEvent( dummyevent )
        return allEvents

    def addEvent( self, eventInstance ):
        """Saves an event for later writing"""

    def replaceEvent( self, id, updatedevent ):
        """Replace event (for later writing)"""

    def removeEvent( self, id ):
        """Removes an event"""

    def saveModifications( self ):
        """Save whatever changes have come by"""

    def addCommonid( self, id, commonid ):
        """Add commonid"""

#----------------------------------------------------------------------------#

if __name__ == "__main__":
    print "Testing the dummy module"
