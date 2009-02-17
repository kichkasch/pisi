#!/usr/bin/env python

"""
    Copyright 2009 Esben Damgaard <ebbe at hvemder . dk>

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
        self._allEvents = events.Events( )
        self._currentline=''
        self._localFile = dict()
        self.timezones = dict()
        self.file = open(config.get(configsection,'file'),'r+')
        if self.verbose:
            print 'ics-module using file %s' % (config.get(configsection,'file'))
        self._readFile()

    def allEvents( self ):
        """Returns an Events instance with all events"""
        return self._allEvents

    def addEvent( self, eventInstance ):
        """Saves an event for later writing"""

    def addCommonid( self, id, commonid ):
        """Add commonid"""
        # - localfile
        if self.verbose:
            print "Adding commonid to id",id
        self._localFile[id]['commonid'] = commonid

    def replaceEvent( self, id, updatedevent ):
        """Replace event"""
        if self.verbose:
            print "We will replace event",id
        # - localfile
        self._localFile[id] = \
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
    def _convertPisiEventToIcs( self, event ):
        """"""
        _icsEvent = "BEGIN:VEVENT\n"
        _icsEvent += "UID:"+event.id+"\n"
        _icsEvent += "END:VEVENT\n"
        return _icsEvent

    def _getNextLine( self ):
        """"""
        if self._currentline=='':
            self._currentline = self.file.readline().strip('\n')
        returnString = self._currentline
        self._currentline = self.file.readline().strip('\n')
        while self._currentline[:1]==" ":
            returnString = returnString + self._currentline[1:]
            self._currentline = self.file.readline().strip('\n')

        return returnString

    def _parseEventFromFile( self ):
        """Reads the next lines of the file and parses the event. Returns
        an Event instance."""
        id = None
        commonid = False
        updated = None
        attr = dict()
        local= dict()
        while True:
            line = self._getNextLine()
            if line=="END:VEVENT":
                break
            else:
                theSplit = line.split(':')
                local[theSplit[0]] = theSplit[1]
                if theSplit[0]=="UID":
                    id = theSplit[1]
                elif theSplit[0]=="LAST-MODIFIED":
                    updated = datetime.datetime.strptime(theSplit[1], '%Y%m%dT%H%M%S')
                elif theSplit[0]=="X-PISI-COMID":
                    commonid = theSplit[1]
                elif theSplit[0][:7]=="DTSTART":
                    tz = theSplit[0].split(';')[1].split('=')[1]
                    time = theSplit[1]
                    self._parseTime( tz, time )
        self._localFile[id] = local
        # Create event and send it back

        return events.Event( id, commonid, updated, attr )

    def _parseRecurrence( self, startDate, endDate, rrule ):
        """Parses a string with recurrence rules"""
        rules = rrule.split(';')
        attr  = {'freq':None,'count':None,'until':None,'bymonth':None,'byday':None}
        for rule in rules:
            temp = rule.split('=')
            if temp[0]=="FREQ":
                if temp[1]=="YEARLY":
                    attr['freq'] = events.YEARLY
                elif temp[1]=="MONTHLY":
                    attr['freq'] = events.MONTHLY
                elif temp[1]=="WEEKLY":
                    attr['freq'] = events.WEEKLY
                elif temp[1]=="DAILY":
                    attr['freq'] = events.DAILY
            elif temp[0]=="COUNT":
                attr['count'] = int(temp[1])
            elif temp[0]=="UNTIL":
                attr['until'] = datetime.datetime.strptime(temp[1], '%Y%m%d')
            elif temp[0]=="INTERVAL":
                attr['interval'] = int(temp[1])
            elif temp[0]=="BYMONTH":
                attr['bymonth'] = temp[1]
            elif temp[0]=="BYDAY":
                attr['byday'] = temp[1]

        return events.Recurrence(
                startDate, endDate,
                attr['freq'], attr['count'],
                attr['until'], attr['bymonth'],
                attr['byday']
            )

    def _parseTime( self, timezone, time ):
        print timezone, time

    def _getTimeZoneFromFile( self ):
        """Read timezone"""
        tmp  = dict()
        rules= dict()
        ruleNr = -1
        tzid= ''
        while True:
            line = self._getNextLine()
            if line=="END:VTIMEZONE":
                break
            else:
                theSplit = line.split(':')
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
                    rules[ruleNr]['recurrence'] = self._parseRecurrence(
                        datetime.datetime.min,datetime.datetime.max,
                        theSplit[1])
        # Save timezone
        self.timezones[tzid]=tmp

    def _readFile( self ):
        """Parse the header of the file"""
        while True:
            tell = self.file.tell()
            line = self._getNextLine()
            if line=='':
                break
            elif line=="BEGIN:VTIMEZONE":
                self._getTimeZoneFromFile()
            elif line=="BEGIN:VEVENT":
                e = self._parseEventFromFile()
                e.prettyPrint()
                print self._convertPisiEventToIcs( e )
                self._allEvents.insertEvent( e )






