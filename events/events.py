#!/usr/bin/env python

"""
    Copyright 2008 Esben Damgaard <ebbe at hvemder . dk>

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
	def __init__( self, id, commonid, updated, attributes ):
		"""Initialize event.
		Arguments:
		 * id - is the id the modules uses to id the event
		 * commonid - This is the id for this event and the two modules. If it
		              hasn't been synchronized (with the other module), it
		              should be False.
		 * updaed - datetime instance
		 * attributes - a dictionary with attributes. See 
		                http://projects.openmoko.org/plugins/wiki/index.php?Developer&id=156&type=g
		                for more help.
		"""
		self.id = id
		self.commonid = commonid 
		self.updated = updated
		self.attributes=attributes
	
	def merge( self, e ):
		"""Merges the event (e) with itself. If two sections are different, use
		the section from the newest updated."""
		# Find which is newer
		selfNew=False
		if e.updated < self.updated:
			# self is newer
			selfNew=True
		for key,value in self.attributes.iteritems():
			if value != e.attributes[key]:
				# The events differ in this field
				if not selfNew:
					self.attributes[key] = e.attributes[key]
			del e.attributes[key]
		if not selfNew:
			for key,value in e.attributes.iteritems():
				if value != self.attributes[key]:
					# The events differ in this field
					self.attributes[key] = e.attributes[key]
		return self
	
	def prettyPrint ( self ):
		"""Prints all attributes 'nicely'.."""
		print "\t_PrettyPrint of id:",self.id,"Commonid:",self.commonid
		print "\t\tUpdated = ",self.updated
		for key,value in self.attributes.iteritems():
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
			print "Couldn't remove event with id",id,". Wasn't found!"

if __name__=="__main__":
	print "Testing events module"
	all = Events()
	testevent = Event( "testid1", datetime.datetime(2008,7,8), datetime.datetime(2008,7,8), "Test title" )
	all.insertEvent( testevent )
	print all.getEvent( "testid1" ).title
	
	
	
	
	
	
