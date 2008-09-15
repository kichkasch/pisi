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

import sys,os
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
		self.file = config.get(configsection,'file')
		if self.verbose:
			print 'ics-module using file %s' % (self.file)
	
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
		
		return allEvents
	
	def addEvent( self, eventInstance ):
		"""Saves an event for later writing"""
	
	def addCommonid( self, id, commonid ):
		"""Add commonid"""
		# - localfile
		print "Adding commonid to id",id
		self.localFile[id]['commonid'] = commonid
	
	def replaceEvent( self, id, updatedevent ):
		"""Replace event"""
		if self.verbose:
			print "We will replace event",id
		# - localfile
		self.localFile[id] = \
			{'commonid':updatedevent.commonid , 'updated':updatedevent.updated }
	
	def removeEvent( self, id ):
		"""Removes an event"""
		if self.verbose:
			print "We will delete event",id
		# - localfile
		del self.localFile[id]

	def saveModifications( self ):
		"""Save whatever changes have come by"""
		if not self.soft:
			# Save updatetime and commonid in a local file
			f = open( self.folder+'local', 'w' )
			# Save
			f.close()
