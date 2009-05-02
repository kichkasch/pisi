"""
Our own calendar-event-object.

This file is part of Pisi.

Calendar-Events part does currently not make use of the inheritance infrastructure (Syncable and AbstractSyncronizationModule).

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
import random

import pisiprogress
import pisiinterfaces
from pisiconstants import *

import vobject
#import tzinfo, timedelta
KNOWN_ATTRIBUTES = ['start', 'end', 'recurrence', 'allday', 'title', 'description', 'location', 'alarm', 'alarmmin']

class Event(pisiinterfaces.Syncable):
    def __init__( self, id, updated, attributes ):
        """
        Initialize event.
        @param id: is the id the module uses to id the event
        @param updated: datetime instance
        @param attributes: a dictionary with attributes. See U{http://projects.openmoko.org/plugins/wiki/index.php?Developer&id=156&type=g} for more help.
        """
        pisiinterfaces.Syncable.__init__(self, id,  attributes)
        self.updated   = updated

    def compare(self,  e):
        """
        Compares two events against each other
        
        @return: True, if all attributes match, otherwise False
        """
        for key,value in self.attributes.iteritems():
            if key not in KNOWN_ATTRIBUTES:
                continue
            if (str(value) == "" or value == None) and (str(e.attributes[key] )== "" or e.attributes[key] == None):
                continue
            if value != e.attributes[key]:
                return False
        return True

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
        print "\t_PrettyPrint of id: %s" %self.id
        print "\t\t- Updated = ",self.updated
        for key,value in self.attributes.iteritems():
            print "\t\t- ",key," = ",value


ZERO = datetime.timedelta(0)
HOUR = datetime.timedelta(hours=1)

class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

class CustomOffset(datetime.tzinfo):
    def __init__(self, name, st):
        self._name = name
        self._hour = int(st[1:3])
        self._min = int(st[4:5])
        self._isPositive = st[0] == "+"
#        print st,  "->", self._hour,  self._min,  "Pos: ", self._isPositive
        
    def utcoffset(self, dt):
        if self._isPositive:
            return datetime.timedelta(hours = self._hour,  minutes = self._min)
        else:
            return datetime.timedelta(hours = - self._hour,  minutes = - self._min)

    def tzname(self, dt):
        return self._name

    def dst(self, dt):
        return ZERO

class Recurrence:
    """
    Recurrence infomation for an event; this is attached as an attribute to a "normal" event
    
    For now, we only support Google Calendar and (hopefully soon) ICS files; both use the ICalendar standard for Recurences:
    The entire ICS information is provided as one String in ICalendar format. This string is stored and returned on request; it is
    as well parsed, so you can request single information chunks (DTStart, DTEnd, RROLE) from it.
    
    At some point we will also need a constructor for converting the other way around; giving the single data chunks as input
    and create the overall ICS string from it. Well; as I say - at some point.
    """
    def __init__(self):
        pass

    def initFromData(self,  data):
#        print data
        self._data = data
        v = vobject.readComponents(data).next()
            
        self._allDay = False
        try:
            self._dtstart = vobject.icalendar.DateOrDateTimeBehavior.transformToNative(v.dtstart).value
            if type(self._dtstart) == datetime.date:
                self._allDay = True
        except KeyError: #BaseException:
            self._dtstart = None
        try:
            self._dtend = vobject.icalendar.DateOrDateTimeBehavior.transformToNative(v.dtend).value
        except BaseException:
            self._dtend = None
        try:
            self._rrule = v.rrule
        except KeyError: #BaseException:
            self._rrule = None

    def initFromAttributes(self,  rrule,  dtstart,  dtend = None,  isAllDay = False):   # just learned; there is no Constructor overwriting allowed in Python :(
        self._rrule = rrule
        self._dtstart = dtstart
        self._dtend = dtend
        self._allDay = isAllDay
                                
        data = self._rrule.serialize() + self._dtstart.serialize()
        if self._dtend:
            data += dtend.serialize()
            
        if type(self._dtstart.value) == datetime.date:  # special handling for all day recurrences
            frame = vobject.iCalendar()
            frame.add("standard")
            frame.standard = vobject.icalendar.TimezoneComponent(UTC())
            data += frame.standard.serialize()

        self._data = data

    def getData(self):
        return self._data
        
    def getDTStart(self):
        return self._dtstart
        
    def getDTEnd(self):
        return self._dtend
        
    def getRRule(self):
        return self._rrule
        
    def isAllDay(self):
        return self._allDay
        
    def __eq__(self,  other):
        if other == None:
            return False
        return self._rrule == other._rrule and self._dtstart != other._dtstart and self._dtend != other._dtend
        
    def __ne__(self,  other):
        return not self.__eq__(other)

    def prettyPrint ( self ):
        """Prints all attributes 'nicely'.."""
        print "\t_PrettyPrint of Recurrence"
        print "\t\tStart:\t%s" %(self._dtstart)
        print "\t\tEnd:\t%s" %(self._dtend)
        print "\t\tRRule:\t%s" %(self._rrule)

class AbstractCalendarSynchronizationModule(pisiinterfaces.AbstractSynchronizationModule):
    """
    Super class for all synchronization modules, which aim to synchronize contacts information.
    
    Each Synchronization class implementing contact synchronization should inherit from this class.
    @ivar _allContacts: Dictionary to hold all contact instance for the implementation.
    @ivar _history: Keeps track of all changes applied to the container for this data source (for later write through)
    """
    
    def __init__(self,  verbose,  soft,  modulesString,  config,  configsection,  name = "unkown contact source"):
        """
        Constructor
        
        Instance variables are initialized.
        """
        pisiinterfaces.AbstractSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  name)
        self._allEvents = self._allEntries
        self._history = []
                
    def allEvents( self ):
        """
        Getter.
        
        @return: The link to the instance variable L{_allContacts}.
        """
        return self.allEntries()

    def getEvent(self,  id):
        """
        GETTER
        
        @return: The link with the given ID.
        """
        return self.getEntry(id)

    def addEvent( self, eventInstance ):
        """
        Saves an event for later writing
        
        One entry is added to the history list (L{_history}) with action id for 'add' and the new instance is passed on to the super class method L{addEntry}.
        """
        self.addEntry(eventInstance)
        self._history.append([ACTIONID_ADD,  eventInstance.getID()])

    def replaceEvent( self, id, updatedEvent):
        """
        Replaces an existing calendar entry with a new one.

        One entry is added to the history list (L{_history}) with action id for 'replace' and the old instance is replaced by the new one by passing it on to the super class method L{replaceEntry}.
        """
        self.replaceEntry(id, updatedEvent)
        self._history.append([ACTIONID_MODIFY,  id])

    def removeEvent( self, id ):
        """
        Removes an event entry
        
        One entry is added to the history list (L{_history}) with action id for 'delete' and the delete command is passed on to the super class method L{removeEntry}.
        """
        self.removeEntry(id)
        self._history.append([ACTIONID_DELETE,  id])
        
def assembleID():
    return str(random.randint(0,  100000000000000000000000))
