"""
Syncronize with an iCalendar file

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

from events import events
import datetime,time
import pisiprogress

class SynchronizationModule(events.AbstractCalendarSynchronizationModule):
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        events.AbstractCalendarSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "ICalendar file")
        self.folder = folder
        self._path = config.get(configsection,'path')
        pisiprogress.getCallback().verbose('ics-module using file %s' % (self._path))

    def load(self):
        pisiprogress.getCallback().verbose("ICalendar: Loading")
        pass        # implementation goes here
        
        
    def saveModifications(self):
        pisiprogress.getCallback().verbose("ICalendar module: I apply %d changes now" %(len(self._history)))
        pass        # implementation goes here
