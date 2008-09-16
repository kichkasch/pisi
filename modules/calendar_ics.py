#!/usr/bin/env python

"""
    Copyright 2008 Esben Damgaard <ebbe at hvemder . dk>

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

import sys,os,re
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
		self.timezones = dict()
		self.file = open(config.get(configsection,'file'),'r+')
		self._readHeader()
		if self.verbose:
			print 'ics-module using file %s' % (config.get(configsection,'file'))
	
	def allEvents( self ):
		"""Returns an Events instance with all events"""
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
		



# Private functions
	def _parseRecurrence( self,rrule ):
		"""Parses a string with recurrence rules"""
		
	
	def _getTimeZoneFromFile( self ):
		"""Read timezone"""
		tmp  = dict()
		rules= []
		ruleNr = -1
		tzid= ''
		run = True
		while run:
			line = self.file.readline()
			if line=="END:VTIMEZONE\n":
				run = False
			else:
				theSplit = line.strip('\n').split(':')
				if theSplit[0]=="TZID":
					tzid=theSplit[1]
				elif theSplit[0]=="BEGIN":
					ruleNr += 1
					rules[ruleNr] = dict()
				elif theSplit[0]=="TZOFFSETFROM":
					rules[ruleNr]['from'] = theSplit[1]
				elif theSplit[0]=="TZOFFSETTO":
					rules[ruleNr]['to'] = theSplit[1]
				elif theSplit[0]=="RRULE":
					rules[ruleNr]['recurrence'] = self._parseRecurrence(theSplit[1])
		# Save timezone
		self.timezones[tzid]=tmp

	def _readHeader( self ):
		"""Parse the header of the file"""
		header = True
		while header:
			tell = self.file.tell()
			line = self.file.readline()
			if line=='':
				header = False
			elif line=="BEGIN:VTIMEZONE\n":
				self._getTimeZoneFromFile()
			
			theSplit = line.strip('\n').split(':')
			print theSplit[1]
			
		



