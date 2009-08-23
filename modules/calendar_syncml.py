""" 
Syncronize with SyncML (Calendar)

This file is part of Pisi. This implementation is based on the Conduit branch of John Carr (http://git.gnome.org/cgit/conduit/log/?h=syncml),
which was one of the very first Python Syncml implementation - based on a ctime binding to the libsyncml library (https://libsyncml.opensync.org/).
The bindings were kept as found there - but I changed a lot the SyncModule file - in order to keep it as simple as possible.
Go and check L{thirdparty.conduit.SyncmlModule} for some more details.

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
import vobject

# Allows us to import contact
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from events import events
from pisiconstants import *
import vobjecttools
import pisiprogress
import thirdparty.conduit.SyncmlModule as SyncmlModule

SYNCMLSERVER_IDENTIFIER = "pisi"
"""What app name to use when connecting to Syncml server"""

class SynchronizationModule(events.AbstractCalendarSynchronizationModule):
    """
    The implementation of the interface L{events.AbstractCalendarSynchronizationModule} for the Syncml Calendar backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{events.AbstractCalendarSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded. 
        The connection to the Google Gdata backend is established.
        """
        events.AbstractCalendarSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "Syncml Calendar")
        pisiprogress.getCallback().verbose('calendar syncml module loaded')
        self._url = config.get(configsection,'url')
        self._username = config.get(configsection,'username')
        self._password = config.get(configsection,'password')
        self._database = config.get(configsection,'database')
        self._mapping = {}

    def load(self):
        """
        Load all data from backend
        
        For data parsing (VCF) the tools layer in L{vobjecttools} is used.
        """
        pisiprogress.getCallback().progress.push(0, 100)
        pisiprogress.getCallback().verbose("SyncML: Loading")
        if_calendar = SyncmlModule.SyncmlCalendarInterface(self._url, self._username, self._password, self._database, SYNCMLSERVER_IDENTIFIER)
        events_raw = if_calendar.downloadItems()   # load
        if_calendar.finish()
        pisiprogress.getCallback().progress.setProgress(20) 
        pisiprogress.getCallback().update("Loading")

        i = 0
        for x in events_raw.keys():
            content = vobject.readOne(events_raw[x])

            if content.contents.has_key('vevent'):     # maybe it's an empty file - you new know ;)
                for y in content.contents['vevent']:
                    atts, globalId, updated = vobjecttools.extractICSEntry(y)
                    if not globalId or globalId == "":
                        globalId = events.assembleID()
                        tmpEvent = events.Event( globalId, updated, atts)
                        tmpEvent.attributes['globalid'] = globalId
                        self.replaceEvent(globalId,  tmpEvent)
                    else:
                        tmpEvent = events.Event(globalId, updated, atts)
                        tmpEvent.attributes['globalid'] = globalId

                    self._allEvents[globalId] = tmpEvent
                    self._mapping[globalId] = x
                    
            i += 1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / len(events_raw)))
            pisiprogress.getCallback().update('Loading')
            
        pisiprogress.getCallback().progress.drop()

    def saveModifications(self):
        """
        Save whatever changes have come by
        
        The history of actions for this data source is iterated. For each item in there the corresponding action is carried out on the item in question.
        For data assembling (ICS) the tools layer in L{vobjecttools} is used.
        """
        pisiprogress.getCallback().verbose("SyncML module: I apply %d changes now" %(len(self._history)))
        if_events = SyncmlModule.SyncmlCalendarInterface(self._url, self._username, self._password, self._database, SYNCMLSERVER_IDENTIFIER)
        
        mods = {}
        dels = {}
        adds = {}
        
        i=0
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose( "\t\t<syncml> adding %s" %(id))
                c = self.getEvent(id)
                ics = vobjecttools.createRawEventEntry(c)
                print ics.serialize()
                adds[str(i)] = ics.serialize()
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<syncml> deleting %s" %(id))
                syncml_id = self._mapping[id]
                dels[syncml_id] = ""
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<syncml> replacing %s" %(id))
                c = self.getEvent(id)
                syncml_id = self._mapping[id]
                ics = vobjecttools.createRawEventEntry(c)
#                mods[syncml_id] = vcard.serialize()    # causing problems - no proper replacement
                dels[syncml_id] = ""
                adds[str(i)] = ics.serialize()
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 90 / len(self._history))
            pisiprogress.getCallback().update('Storing')
        
        if_events.applyChanges(mods = mods, dels = dels,  adds = adds)
        if_events.finish()
        pisiprogress.getCallback().progress.setProgress(100)
        pisiprogress.getCallback().update('Storing')
