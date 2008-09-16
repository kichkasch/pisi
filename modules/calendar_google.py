#!/usr/bin/env python

"""
    Copyright 2008 Esben Damgaard <ebbe at hvemder . dk>

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
import pickle
# Allows us to import event
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from events import events
import datetime,time

class SynchronizationModule:
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        #TODO: Check if the configuration is in the correct format
        self.verbose = verbose
        self.soft = soft
        self.modulesString = modulesString
        self.folder = folder
        self.localFile = dict()
        self.newEvents = dict()
        self.batchOperations = gdata.calendar.CalendarEventFeed()
        self._login( config.get(configsection,'user'),
                         config.get(configsection, 'password') )
        self.calendarid = config.get(configsection,'calendarid')

    def allEvents( self ):
        """Returns an Events instance with all events"""
        # Load all commonid & updatetimes from local file
        if os.path.isfile(self.folder+'local'):
            f = open( self.folder+'local', 'r' )
            templocalFile = pickle.load(f)
            f.close()
        else:
            templocalFile = dict()
        # Retrieve all events from Google
        allEvents = events.Events( )

        feed = self.cal_client.GetCalendarEventFeed('/calendar/feeds/'+self.calendarid+'/private/full?max-results=999999')
        self.googleevents = dict()
        for i, an_event in enumerate(feed.entry):
            self.googleevents[an_event.id.text] = an_event
            """if self.verbose:
                print '\tGoogleModule: %s. %s' % (i, an_event.title.text,)
                print '\t\tId:%s' % (an_event.id.text)
                print '\t\tStart:',an_event.when[0].start_time
                print '\t\tEnd:',an_event.when[0].end_time
                print '\t\tUpdated:',an_event.updated.text,'Like new:',self._gtimeToDatetime(an_event.updated.text )"""

            # Get update-time and commonid from a local file
            commonid = False
            googleupdatedtime = self._gtimeToDatetime( an_event.updated.text )
            updated = googleupdatedtime
            if an_event.id.text in templocalFile:
                commonid = templocalFile[an_event.id.text]['commonid']
                if googleupdatedtime == templocalFile[an_event.id.text]['googleupdatedtime']:
                    updated = templocalFile[an_event.id.text]['updated']

            # Make sure event commonid and updatetime is saved in a local file
            self.localFile[an_event.id.text] = \
                 {'commonid':commonid , 'updated':updated, 'googleupdatedtime':googleupdatedtime }

            if self.verbose:
                print '\t\tCommonid:',commonid
            # Create event
            tmpevent = self._geventToPisiEvent(an_event)
            tmpevent.commonid = commonid
            tmpevent.updated = updated
            #tmpevent.prettyPrint()
            # Insert event
            allEvents.insertEvent( tmpevent )

        return allEvents

    def addEvent( self, eventInstance ):
        """Saves an event for later writing"""
        # - at Google
        gevent = self._convertPisiEventToGoogle( eventInstance )
        gevent.batch_id = gdata.BatchId(text=eventInstance.id)
        self.batchOperations.AddInsert(entry=gevent)
        # - localfile (We can't, as we don't know id)
        self.newEvents[eventInstance.id] = \
           {'commonid':eventInstance.commonid , 'updated':eventInstance.updated }
        """self.localFile[eventInstance.id] = \
            {'commonid':eventInstance.commonid , 'updated':eventInstance.updated }"""

    def addCommonid( self, id, commonid ):
        """Add commonid"""
        # - at Google
        """# Add extended property to event
        key = 'pisi'+self.modulesString+'commonid'
        self.googleevents[id].extended_property.append(gdata.calendar.ExtendedProperty(name=key, value=commonid))
        # Add event to update batch
        self.googleevents[id].batch_id = gdata.BatchId(text=id)
        self.batchOperations.AddUpdate(entry=self.googleevents[id])"""
        # - localfile
        print "Adding commonid to id",id
        self.localFile[id]['commonid'] = commonid

    def replaceEvent( self, id, updatedevent ):
        """Replace event"""
        if self.verbose:
            print "We will replace event",id
        # - at Google
        gevent = self._convertPisiEventToGoogle( updatedevent )
        gevent.batch_id = gdata.BatchId(text=id)
        gevent.id = atom.Id( id )
        # Get and insert edit link
        editUri = self.googleevents[id].GetEditLink().href
        gevent.link.append( atom.Link(editUri, 'edit', 'application/atom+xml') )
        self.batchOperations.AddUpdate(gevent)
        # - localfile
        self.localFile[id] = \
            {'commonid':updatedevent.commonid , 'updated':updatedevent.updated }

    def removeEvent( self, id ):
        """Removes an event"""
        if self.verbose:
            print "We will delete event",id
        # - at Google
        self.googleevents[id].batch_id = gdata.BatchId(text=id)
        self.batchOperations.AddDelete(entry=self.googleevents[id])
        # - localfile
        del self.localFile[id]

    def saveModifications( self ):
        """Save whatever changes have come by"""
        if not self.soft:
            # Save batchoperations
            if self.verbose:
                print "Saving Google-calendar modifications\n\n"
                print self.batchOperations
            response_feed = self.cal_client.ExecuteBatch(self.batchOperations, '/calendar/feeds/'+self.calendarid+'/private/full/batch')
            # iterate the response feed to get the operation status
            for entry in response_feed.entry:
                if self.verbose:
                    print 'batch id: %s' % (entry.batch_id.text,)
                    print 'status: %s' % (entry.batch_status.code,)
                    print 'reason: %s' % (entry.batch_status.reason,)
                    #print '\n',entry

                if entry.batch_status.reason=="Created":
                    #commonid = self.newEvents[entry.batch_id.text]['commonid']
                    if self.verbose:
                        print "\t We have just created a new event :)"
                    updated  = self.newEvents[entry.batch_id.text]['updated']
                    commonid = self.newEvents[entry.batch_id.text]['commonid']
                    self.localFile[entry.GetSelfLink().href] = { \
                        'commonid':commonid , \
                        'updated':updated, \
                        'googleupdatedtime':self._gtimeToDatetime(entry.updated.text) \
                        }
                else:
                    try:
                        # If we are deleting, this will fail
                        self.localFile[entry.batch_id.text]['googleupdatedtime'] = self._gtimeToDatetime(entry.updated.text)
                        if self.verbose:
                            print "We got a new googleupdatetime"
                    except:
                        print
                    """selfLink = entry.GetSelfLink()
                    if entry.batch_id.text!=selfLink:
                        self.localFile[selfLink] = self.localFile[entry.batch_id.text]
                        del self.localFile[entry.batch_id.text]"""
            # Save updatetime and commonid in a local file
            f = open( self.folder+'local', 'w' )
            pickle.dump(self.localFile, f)
            f.close()

    def _saveSyncronizationTime( self ):
        """
        Simply saves the current time in a file
        """
        f = open(self.folder+'lastSyncronization','w')
        f.write( datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') )
        f.close()

    def _convertToGoogle( self, dateTimeObject, allday ):
        if allday:
            return dateTimeObject.strftime('%Y-%m-%d')
        else:
            return dateTimeObject.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    def _convertPisiEventToGoogle( self, event ):
        if self.verbose:
            print "\n\nConverting this to Googleevent:"
            event.prettyPrint()
        gevent = gdata.calendar.CalendarEventEntry()
        gevent.title = atom.Title(text=event.attributes['title'])
        key = 'pisi'+self.modulesString+'commonid'
        #gevent.extended_property.append(gdata.calendar.ExtendedProperty(name=key, value=event.commonid))
        gevent.where.append(gdata.calendar.Where(value_string=event.attributes['location']))
        gevent.when.append(gdata.calendar.When(\
                                start_time=self._convertToGoogle(event.attributes['start'],event.attributes['allday']), \
                                end_time=self._convertToGoogle(event.attributes['end'],event.attributes['allday'])))
        gevent.content = atom.Content(text=event.attributes['description'])
        if self.verbose:
            print "\n\nConverting done:",gevent
        return gevent

    def _geventToPisiEvent( self, event ):
        (allday, start) = self._gtimeToDatetime(event.when[0].start_time )
        (allday, end) = self._gtimeToDatetime(event.when[0].end_time )
        attributes=\
            {'start':start, \
             'end':end, \
             'allday':allday, \
             'title':event.title.text, \
             'description':"", 'location':"",\
             'alarm':False, 'alarmmin':0 \
            }
        (tmp, updated) = self._gtimeToDatetime(event.updated.text )
        return events.Event( event.id.text, False, updated, attributes )

    def _gtimeToDatetime( self, gtime ):
        """Converts Google normal way (RFC3339) to write date and time
        to a datetime instance"""
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
        if self.verbose:
            print "Logging in with user", user
        self.cal_client = gdata.calendar.service.CalendarService()
        self.cal_client.email = user
        self.cal_client.password = password
        self.cal_client.source = 'mokoGsync-google_module'
        self.cal_client.ProgrammaticLogin()
        # We are now logged in


#----------------------------------------------------------------------------#

if __name__ == "__main__":
    print "Testing the Google module"

