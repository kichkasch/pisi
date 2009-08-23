"""
Syncronize with an iCalendar file

This file is part of Pisi.

ICalendar support is based on the VOBJECT library by skyhouseconsulting (U{http://vobject.skyhouseconsulting.com/}).
Consequently, the vobject site-package has to be installed for utilizing ICS support in PISI.

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
import datetime
import os.path
import os
from pisiconstants import *
#import vobject
from vobjecttools import *

FIELD_PISI = "X-PISI-ID"
"""Name of additional field in ICS file for PISI ID (must start with X-)"""

class SynchronizationModule(events.AbstractCalendarSynchronizationModule):
    """
    The implementation of the interface L{events.AbstractCalendarSynchronizationModule} for the ICalendar file backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{events.AbstractCalendarSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded.
        """
        events.AbstractCalendarSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "ICalendar file")
        self._folder = folder
        self._path = config.get(configsection,'path')
        pisiprogress.getCallback().verbose('ics-module using file %s' % (self._path))
        self._rawData = {}

            
    def _guessAmount(self):
        """
        Try to determine roughly how many entries are in this file (we can't know prior to parsing; but we have a guess using the file size)
        """
        info = os.stat(self._path)
        return info.st_size / ICS_BYTES_PER_ENTRY
        
    def load(self):
        """
        Load all data from local ICS file
        
        File is opened and the entries are parsed. For each entry an L{events.events.Event} instance is created and stored in the instance dictionary.
        """
        pisiprogress.getCallback().verbose("ICalendar: Loading")
        file = None
        try:
            file = open(self._path,  "r")
        except IOError,  e:
            pisiprogress.getCallback().error("--> Error: Could not load ICS file - we still carry on with processing:\n\t%s" %(e))
            return
        pisiprogress.getCallback().progress.push(0, 100)
        vcal = vobject.readOne(file)
        pisiprogress.getCallback().progress.setProgress(20) 
        pisiprogress.getCallback().update("Loading")
        amount = self._guessAmount()
        i = 0        
        if vcal.contents.has_key('vevent'):     # maybe it's an empty file - you new know ;)
            for x in vcal.contents['vevent']:
                atts, globalId, updated = extractICSEntry(x)
                if not globalId or globalId == "":
                    globalId = events.assembleID()
                    tmpEvent = events.Event( globalId, updated, atts)
                    tmpEvent.attributes['globalid'] = globalId
                    self.replaceEvent(globalId,  tmpEvent)
                else:
                    tmpEvent = events.Event(globalId, updated, atts)
                    tmpEvent.attributes['globalid'] = globalId

                self._allEvents[globalId] = tmpEvent
                self._rawData[globalId] = x
                
                if i < amount:
                    i += 1
                pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / amount))
                pisiprogress.getCallback().update('Loading')
                
        file.close()
        pisiprogress.getCallback().progress.drop()

        
    def saveModifications(self):
        """
        Save whatever changes have come by
        
        Iterates the history of actions and replaces the corresponding items with new vobject instances.
        In the end, the vobject representation is written to the ICS file.
        """
        pisiprogress.getCallback().verbose("ICalendar module: I apply %d changes now" %(len(self._history)))
        if len(self._history) == 0:
            return      # don't touch anything if there haven't been any changes
            
        # rename old file         
        try:
            bakFilename = os.path.join(self._folder,  os.path.basename(self._path))
            os.rename(self._path,  bakFilename)
        except OSError,  e:
            pisiprogress.getCallback().verbose("\tError when backing up old ICS file - we still carry on with processing:\n\t%s" %(e))
        
        file = open(self._path,  "w")
        
        i = 0
        for actionItem in self._history:
            action = actionItem[0]
            globalId = actionItem[1]
            if action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<ics> deleting %s" %(globalId))
                del self._rawData[globalId]
            elif action == ACTIONID_ADD or action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<ics> adding or replacing %s" %(globalId))                
                e = self.getEvent(globalId)
                self._rawData[globalId] = createRawEventEntry(e)
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 70 / len(self._history))
            pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().progress.setProgress(70)
        pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().verbose("\tICS: Writing through file")
        calendar = vobject.iCalendar()
        calendar.add('vevent')
        del calendar.contents['vevent'][0]
        for x in self._rawData.values():
            calendar.contents['vevent'].append(x)
        file.write(calendar.serialize())
        pisiprogress.getCallback().verbose("\tNew ICS file saved to %s; \n\tbackup file is located in %s." %(self._path,  bakFilename))
        file.close()
