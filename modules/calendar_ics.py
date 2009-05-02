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
import vobject

FIELD_PISI = "X-PISI-ID"
"""Name of additional field in ICS file for PISI ID (must start with X-)"""

class SynchronizationModule(events.AbstractCalendarSynchronizationModule):
    """
    The implementation of the interface L{events.AbstractCalendarSynchronizationModule} for the ICalendar file backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded.
        """
        events.AbstractCalendarSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "ICalendar file")
        self._folder = folder
        self._path = config.get(configsection,'path')
        pisiprogress.getCallback().verbose('ics-module using file %s' % (self._path))
        self._rawData = {}

    def _extractAtt(self, x,  st):
        """
        Supporting function for pulling information out of a attribute
        
        Gets around problems with non available attributes without the need for checking this beforehand for each attribute.
        """
        try:
            ret = None
            exec "ret = " + st
            return ret
        except AttributeError:
            return ''
            
    def _extractRecurrence(self,  x,  allDay):
        """
        Transforms VObject recurrence information into PISI internal object L{events.Recurrence}
        """
        if self._extractAtt(x, 'x.dtend.value'):
            end = x.dtend
        else:
            end = None
        rec = events.Recurrence()
        rec.initFromAttributes(x.rrule,  x.dtstart,  end,  allDay)
        return rec
            
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
        if vcal.contents.has_key('vevent'):     # maybe it's an empty file - you new know ;)
            for x in vcal.contents['vevent']:
                atts = {}
                atts['start'] = self._extractAtt(x, 'x.dtstart.value')
                atts['end'] = self._extractAtt(x, 'x.dtend.value')
                if type(x.dtstart.value) ==datetime.date:
                    atts['allday'] = True
                else:
                    atts['allday'] = False
                atts['title'] = self._extractAtt(x, 'x.summary.value')
                atts['description'] = self._extractAtt(x, 'x.description.value')
                atts['location'] = self._extractAtt(x, 'x.location.value')
                try:
                    atts['alarmmin'] = x.valarm.trigger.value.days * 24 * 60 + x.valarm.trigger.value.seconds / 60
                    atts['alarm'] = True
                except AttributeError:
                    atts['alarm'] = False
                    atts['alarmmin'] = 0
                    
                try:
                    atts['recurrence'] = self._extractRecurrence(x, atts['allday'] )
                except AttributeError:
                    atts['recurrence'] = None
                updated = self._extractAtt(x, 'x.last_modified.value')
                
                if x.contents.has_key('x-pisi-id'):
                    globalId = x.contents['x-pisi-id'][0].value
                else:
                    globalId = None
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
                
        file.close()
        pisiprogress.getCallback().progress.drop()

    def _createRecurrencePart(self, c,  cal):
        """
        Transforms PISI internal recurrence information (L{events.Recurrence}) into vobject representation
        """
        if c.attributes['recurrence']:
            rec = c.attributes['recurrence']
            cal.add('rrule')
            cal.rrule = rec.getRRule()
            
    def _createAlarmPart(self, c, cal):
        """
        Transforms PISI internal alarm information (1 single integer for minutes) into vobject representation
        """
        if c.attributes['alarm']:
            mins = c.attributes['alarmmin']
            days = mins / (24 * 60)
            seconds = (mins * (24*60)) * 60
            cal.add("valarm")
            cal.valarm.add("trigger")
            cal.valarm.trigger.days = days
            cal.valarm.trigger.seconds = seconds

    def _createRawEventEntry(self,  c):
        """
        Transforms PISI internal Calendar event information (L{events.Event}) into vobject representation        
        """
        frame = vobject.iCalendar()
        frame.add('vevent')
        cal = frame.vevent
        cal.add('dtstart')
        if c.attributes['allday']:
            if type(c.attributes['start']) == datetime.datetime:
                c.attributes['start'] = c.attributes['start'].date()
            if type(c.attributes['end']) == datetime.datetime:
                c.attributes['end'] = c.attributes['end'].date()
        cal.dtstart.value = c.attributes['start']   # all day is applied automatically due to datetime.datetime or datetime.date class
        cal.add('dtend')
        cal.dtend.value = c.attributes['end']
        if c.attributes['title']:
            cal.add('summary')
            cal.summary.value = c.attributes['title']
        if c.attributes['description']:
            cal.add('description')
            cal.description.value = c.attributes['description']
        if c.attributes['location']:
            cal.add('location')
            cal.location.value = c.attributes['location']
        cal.add('x-pisi-id')
        cal.contents['x-pisi-id'][0].value = c.attributes['globalid']
        self._createRecurrencePart(c,  cal)
        self._createAlarmPart(c, cal)
        cal.add('last-modified')
        cal.last_modified.value = datetime.datetime.now(events.UTC())
        return cal
        
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
                self._rawData[globalId] = self._createRawEventEntry(e)
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
