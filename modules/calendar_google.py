"""
Syncronize with Google Calendar

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

import gdata.calendar.service
import gdata.service
import atom
import sys,os
import datetime,time

import pisiprogress
from pisiconstants import *
from events import events

class SynchronizationModule(events.AbstractCalendarSynchronizationModule):
    """
    The implementation of the interface L{events.AbstractCalendarSynchronizationModule} for the Google Calendar backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded. 
        The connection to the Google Gdata backend is established.
        """
        events.AbstractCalendarSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "Google Calendar")
        self.folder = folder
        self.newEvents = {}
        self._googleevents = {}
        self.batchOperations = gdata.calendar.CalendarEventFeed()
        user = config.get(configsection,'user')
        password = config.get(configsection, 'password')
        self.calendarid = config.get(configsection,'calendarid')
        self._login( user, password )
        
    def load(self):
        """
        Load all data from backend
        
        A single query is performed and the result set is parsed afterwards.
        """
        feed = self.cal_client.GetCalendarEventFeed('/calendar/feeds/'+self.calendarid+'/private/full?max-results=%d' %(GOOGLE_CALENDAR_MAXRESULTS))
        for i, an_event in enumerate(feed.entry):
            globalId,  updated, attributes = self._geventToPisiEvent(an_event)
            if globalId == None:
                globalId = events.assembleID()
                tmpEvent = events.Event( globalId, updated, attributes )
                tmpEvent.attributes['globalid'] = globalId
                self.replaceEvent(globalId,  tmpEvent)
            else:
                tmpEvent = events.Event( globalId, updated, attributes )
            self._allEvents[globalId] = tmpEvent
            self._googleevents[globalId] = an_event

    def _saveAddEvent(self, id ):
        """
        Saves an event as part of saving modifications
        """
        eventInstance = self.getEvent(id)
        gevent = self._convertPisiEventToGoogle(eventInstance)
        gevent.batch_id = gdata.BatchId(text=eventInstance.id)
        self.batchOperations.AddInsert(entry=gevent)

    def _saveReplaceEvent(self, id):
        """
        Replace event as part of saving modifications
        """
        updatedevent = self.getEvent(id)
        gevent = self._convertPisiEventToGoogle(updatedevent)
        gevent.batch_id = gdata.BatchId(text=id)
        gevent.id = atom.Id( id )
        editUri = self._googleevents[id].GetEditLink().href
        gevent.link.append( atom.Link(editUri, 'edit', 'application/atom+xml') )
        self.batchOperations.AddUpdate(gevent)

    def _saveRemoveEvent( self, id ):
        """
        Removes an event as part of saving modifications
        """
        self.googleevents[id].batch_id = gdata.BatchId(text=id)
        self.batchOperations.AddDelete(entry=self.googleevents[id])

    def _commitModifications(self):
        """
        Makes changes permanent
        """
        pisiprogress.getCallback().verbose("Commiting Google-calendar modifications")
        response_feed = self.cal_client.ExecuteBatch(self.batchOperations, '/calendar/feeds/'+self.calendarid+'/private/full/batch')

    def saveModifications(self ):
        """
        Save whatever changes have come by
        
        Iterates the history of actions and calls the corresponding supporting functions.
        In the end, the commit supporting function L{_commitModifications} is called for writing through changes.
        """
        pisiprogress.getCallback().verbose("\t\tSaving google calendar <%s> (%d)" %(self.getDescription(),  len(self._history)))
        i=0
        for listItem in self._history:
            action = listItem[0]
            id = listItem[1]
            if action == ACTIONID_ADD:
                pisiprogress.getCallback().verbose("\t\t<google calendar> adding %s" %(id))
                self._saveAddEvent(id)
            elif action == ACTIONID_DELETE:
                pisiprogress.getCallback().verbose("\t\t<google calendar> deleting %s" %(id))
                self._saveRemoveEvent(id)
            elif action == ACTIONID_MODIFY:
                pisiprogress.getCallback().verbose("\t\t<google calendar> replacing %s" %(id))
                self._saveReplaceEvent(id)
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 80 / len(self._history))
            pisiprogress.getCallback().update('Storing')
        
        self._commitModifications()
        pisiprogress.getCallback().progress.setProgress(100)
        pisiprogress.getCallback().update('Storing')
        

    def _convertToGoogle(self, dateTimeObject, allday ):
        """
        Supporting function to assemble a date-time-object depending on the type of event (all day or special times)
        """
        if allday:
            return dateTimeObject.strftime('%Y-%m-%d')
        else:
            return dateTimeObject.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def _convertPisiEventToGoogle( self, event ):
        """
        Supporting function to convert a PISI event (internal format) into a Google Gdata Calendar event
        """
        gevent = gdata.calendar.CalendarEventEntry()
        gevent.title = atom.Title(text=event.attributes['title'])
        gevent.where.append(gdata.calendar.Where(value_string=event.attributes['location']))
        gevent.when.append(gdata.calendar.When(\
                                start_time=self._convertToGoogle(event.attributes['start'],event.attributes['allday']), \
                                end_time=self._convertToGoogle(event.attributes['end'],event.attributes['allday'])))
        gevent.content = atom.Content(text=event.attributes['description'])
        gevent.extended_property.append(gdata.calendar.ExtendedProperty(name='pisiid',  value=event.attributes['globalid'] ))
        return gevent

    def _geventToPisiEvent( self, event ):
        """
        Converts a Google event to Pisi event (internal format)
        """
        if event.recurrence:
            # When there is a recurrence, the 'start' and 'end' is inside the recurrence text
            recurrence = events.Recurrence()
            recurrence.setIcsText( event.recurrence.text )
            start = None
            end = None
            allday = None
        else:
            recurrence = None
            (allday, start) = self._gtimeToDatetime(event.when[0].start_time )
            (allday, end) = self._gtimeToDatetime(event.when[0].end_time )
        attributes=\
            {'start':start, \
             'end':end, \
             'recurrence':recurrence, \
             'allday':allday, \
             'title':event.title.text, \
             'description':event.content.text, \
             'location':event.where[0].value_string,\
             'alarm':False, 'alarmmin':0 \
            }
        (tmp, updated) = self._gtimeToDatetime(event.updated.text )
        pisiID = None
        try:
            for prop in event.extended_property:
                if prop.name == 'pisiid':
                    pisiID = prop.value
                    attributes['globalid'] = pisiID
        except BaseException:
            pass    # fair enough; this event hasn't been synchronized before
        return pisiID,  updated, attributes

    def _gtimeToDatetime( self, gtime ):
        """
        Converts Google normal way (RFC3339) to write date and time to a datetime instance
        """
        allday = False
        if len(gtime)==10:
            allday = True
            date = datetime.datetime.strptime(gtime[:19], '%Y-%m-%d')
            return (allday, date)
        onlyDandT = datetime.datetime.strptime(gtime[:19], '%Y-%m-%dT%H:%M:%S')
        timezone = gtime[23:24]
        if timezone=='Z':
            timezonehour = 0
            timezonemin  = 0
        else:
            timezonehour = int(gtime[24:26])
            timezonemin  = int(gtime[27:29])
        if timezonehour>0 or timezonemin>0:
            # Convert time to timestamp, the add or subtract timezone,
            # and convert back
            onlyDandT = time.mktime(onlyDandT.timetuple())
            if timezone=='+':
                onlyDandT -= (timezonehour*60 + timezonemin)*60
            else:
                onlyDandT += (timezonehour*60 + timezonemin)*60
            onlyDandT = datetime.datetime.fromtimestamp(onlyDandT)
        return (allday, onlyDandT)

    def _login( self, user, password ):
        """
        Supporting function to perform login at Google's Calendar Web-Service API
        """
        pisiprogress.getCallback().verbose("Google Calendar: Logging in with user %s" %(user))
        self.cal_client = gdata.calendar.service.CalendarService()
        self.cal_client.email = user
        self.cal_client.password = password
        self.cal_client.source = GOOGLE_CALENDAR_APPNAME
        self.cal_client.ProgrammaticLogin()
