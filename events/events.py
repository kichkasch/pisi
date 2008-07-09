#!/usr/bin/env python

"""
    Copyright Esben Damgaard

    My own calendar-event-object.



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

import datetime

class Event:
	def __init__( self, id, updated, datetimeStart, datetimeEnd, title="Test event", description="", location="", alarm=False, alarmmin=0 ):
		self.id = id # Must be a unique id
		self.updated = updated
		"""self.start = datetimeStart # Start-time
		self.end = datetimeEnd # End-time
		self.title = title # Title or subject
		self.description = description # Description or comment
		self.location = location # Location of event
		self.alarm = alarm # Is there an alarm? True/False
		self.alarmmin = alarmmin # How many minutes before start"""
		#TODO: Recurrence, attendees
		self.attributtes=\
			{'start':datetimeStart, 'end':datetimeEnd, 'title':title,\
			 'description':description, 'location':location, 'alarm':alarm,\
			 'alarmmin':alarmmin \
			}
	
	def merge( self, e ):
		"""Merges the event (e) with itself. If two sections are different, use
		the section from the newest updated."""
		# Find which is newer
		selfNew=False
		if e.updated < self.updated:
			# self is newer
			selfNew=True
		for key,value in self.attributtes.iteritems():
			if value != e.attributtes[key]:
				# The events differ in this field
				if not selfNew:
					self.attributtes[key] = e.attributtes[key]
			del e.attributtes[key]
		for key,value in e.attributtes.iteritems():
			if value != self.attributtes[key]:
				# The events differ in this field
				if not selfNew:
					self.attributtes[key] = e.attributtes[key]
		return self
	
	def prettyPrint ( self ):
		"""Prints all attributtes 'nicely'.."""
		print "\t_PrettyPrint of id:",self.id
		for key,value in self.attributtes.iteritems():
			print "\t\t",key," = ",value
	

class Events:
	def __init__( self ):
		self._events = dict()
	
	def insertEvent( self, eventInstance ):
		"""Saves a new event. Expects an event instance."""
		self._events[eventInstance.id] = eventInstance

	def getEvent( self, id ):
		try:
			return self._events[id]
		except:
			return False
	
	def getAllEvents( self ):
		return self._events
	
	def removeEvent( self, id ):
		try:
			del self._events[id]
		except:
			print "Couldn't remove event with id",id,". Wastn't found!"

if __name__=="__main__":
	print "Testing events module"
	all = Events()
	testevent = Event( "testid1", datetime.datetime(2008,7,8), datetime.datetime(2008,7,8), "Test title" )
	all.insertEvent( testevent )
	print all.getEvent( "testid1" ).title
	
	
	
	
	
	
