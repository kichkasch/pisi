#!/usr/bin/env python

"""
    Copyright by Esben Damgaard

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
# Allows us to import event
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from events import events
import datetime

class SynchronizationModule:
	def __init__( self, modulesString, config, configsection, folder, verbose=False):
		#TODO: Check if the configuration is in the correct format
		self.verbose = verbose
		self.modulesString = modulesString
		self.folder = folder
		if not os.path.exists(self.folder):
			os.mkdir(self.folder)
		self._login( config.get(configsection,'user'),
						 config.get(configsection, 'password') )
		self.calendarid = config.get(configsection,'calendarid')
	
	def allEvents( self ):
		"""Returns an Events instance with all events"""
		# Retrieve all events from Google
		# Remember: Id should be recognizable with the other module->use self.modulesString
		
		# Temporary return an empty events.events.Events
		allEvents = events.Events( )
		attributes=\
			{'start':datetime.datetime(2008,7,8,14,15,0), \
			 'end':datetime.datetime(2008,7,8,16,0,0), 'title':"Google title",\
			 'description':"", 'location':"", 'alarm':False,\
			 'alarmmin':0 \
			}
		dummyevent = events.Event( "dummyid2", datetime.datetime(2008,7,8,15,18,0), attributes )
		allEvents.insertEvent( dummyevent )
		return allEvents
	
	def addEvent( self, eventInstance ):
		"""Saves and event for later writing"""
	
	def replaceEvent( self, id, updatedevent ):
		"""Replace event"""

	def initChangesSince( self, datet ):
		"""Initialize changes since datet. datet is a datetime object
		"""
		if self.verbose:
			print "Find changes since",\
					datet.strftime('%Y-%m-%d %H:%M:%S')
		""" Find changes
				* Save a copy of the old backup
				* Find deleted events
				* Find updated & new events
		"""
	
	def saveModifications( self ):
		"""Save whatever changes have come by"""

	def _saveSyncronizationTime( self ):
		"""
		Simply saves the current time in a file
		"""
		f = open(self.folder+'lastSyncronization','w')
		f.write( datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') )
		f.close()

	def _convertToGoogle( self, dateTimeObject ):
		if dateTimeObject:
			#FIXME: Timezone
			time = dateTimeObject.strftime('%Y-%m-%dT%H:%M:%SZ')
			if self.verbose:
				print 'Last syncronization was:',time
			return time
		else:
			if self.verbose:
				print 'No lastSyncronization-file'
			return "1970-01-01T01:00:00Z"

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
	import ConfigParser
	config = ConfigParser.ConfigParser()
	config.readfp(open(os.environ.get('HOME') + '/.mokogsync/conf'))
	google = SynchronizationModule(config, os.environ.get('HOME') + '/.mokogsync/', True)

	"""    
	feed = google.cal_client.GetAllCalendarsFeed()
	print 'Printing allcalendars: %s' % feed.title.text
	for i, a_calendar in zip(xrange(len(feed.entry)), feed.entry):
	print '\t%s. %s' % (i, a_calendar.title.text,)
	"""

	feed = google.cal_client.GetCalendarEventFeed('/calendar/feeds/'+config.get('google','calendarid')+'/private/full?max-results=999999')
	print 'Events on Primary Calendar: %s' % (feed.title.text,)
	for i, an_event in enumerate(feed.entry):
		print '\t%s. %s' % (i, an_event.title.text,)
		print '\t\tId:%s' % (an_event.id.text)
		print '\t\tStart:',an_event.when[0].start_time
		print '\t\tEnd:',an_event.when[0].end_time
		print '\t\tUpdated:',an_event.updated.text

	""" Get entire feed in a file:
	f = open('feed','w')
	f.write(feed.__str__())
	f.close()
	"""
