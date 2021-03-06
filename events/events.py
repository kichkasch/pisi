"""
Our own calendar-event-object.

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
import random
import vobject

import pisiprogress
import pisiinterfaces
from pisiconstants import *

KNOWN_ATTRIBUTES = ['start', 'end', 'recurrence', 'allday', 'title', 'description', 'location', 'alarm', 'alarmmin']
"""List of attribute names, which have to be set for Event instances"""

UTC_STRING = """BEGIN:VTIMEZONE
TZID:UTC
BEGIN:STANDARD
DTSTART:20000101T000000
RRULE:FREQ=YEARLY;BYMONTH=1
TZNAME:UTC
TZOFFSETFROM:+0000
TZOFFSETTO:+0000
END:STANDARD
END:VTIMEZONE"""

class Event(pisiinterfaces.Syncable):
    """
    Holds information for a single event (Calendar entry) instance
    """
    
    def __init__( self, id, updated, attributes,  attributesToUTF = True):
        """
        Initialize event.
        @param id: is the id the module uses to id the event
        @param updated: datetime instance
        @param attributes: a dictionary with attributes. See U{http://projects.openmoko.org/plugins/wiki/index.php?Developer&id=156&type=g} for more help.
        """
        pisiinterfaces.Syncable.__init__(self, id,  attributes)
        self.updated = updated
        if attributesToUTF:
            for key in attributes.keys():
                if type(attributes[key]) == str:
                    attributes[key] = attributes[key].decode("utf-8")

    def compare(self,  e):
        """
        Compares this event with another one
        
        @return: True, if all attributes (L{KNOWN_ATTRIBUTES}) match, otherwise False
        """
        for key,value in self.attributes.iteritems():
            if key not in KNOWN_ATTRIBUTES:
                continue
            if (value == "" or value == None) and (e.attributes[key] == "" or e.attributes[key] == None):
                continue
#            print key,  value,  e.attributes[key]
            if value != e.attributes[key]:
                return False
        return True

    def merge( self, e ):
        """
        Merges the event (e) with itself. If two sections are different, use the section from the newest updated.
        """
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
        """
        Prints all attributes 'nicely'..
        """
        print "\t_PrettyPrint of id: %s" %self.id
        print "\t\t- Updated = ",self.updated
        for key,value in self.attributes.iteritems():
            print "\t\t- ",key," = ",value


ZERO = datetime.timedelta(0)
"""Pre-set timedelta of 0 for L{UTC}"""
HOUR = datetime.timedelta(hours=1)
"""Pre-set timedelta of 1 for L{UTC}"""

class UTC(datetime.tzinfo):
    """
    Timezone-Info for UTC
    
    See U{http://iorich.caltech.edu/~t/transfer/python-trunk-doc/library/datetime.html} for details.
    """
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

class CustomOffset(datetime.tzinfo):
    """
    Custom Timezone-Info
    
    Takes a String containing Timezone Information (e.g. +04:00) and creates the corresponding Timezone Info Object.
    
    See U{http://iorich.caltech.edu/~t/transfer/python-trunk-doc/library/datetime.html} for more information.
    """
    def __init__(self, name, st):
        """
        Constructor
        
        Parses the string and saves the details in local variables.
        """
        self._name = name
        self._hour = int(st[1:3])
        self._min = int(st[4:5])
        self._isPositive = st[0] == "+"
        
    def utcoffset(self, dt):
        """
        Calculates timedelta
        """
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
    
    The entire ICS information is provided as one String in ICalendar format. This string is stored and returned on request; it is
    as well parsed, so you can request single information chunks (DTStart, DTEnd, RROLE) from it.
    
    The other way around is working as well; provide the information chunks and the ICalendar formatted string is computed.
    """
    def __init__(self):
        """
        Empty Constructor
        
        Call L{initFromData} or L{initFromAttributes} to initialize.
        """
        pass

    def initFromData(self,  data):
        """
        Initialize a recurrence from ICalendar formatted String
        """
        self._data = data
        
        try:
            v = vobject.readComponents(data).next()
        except:
            # some stupid Google Calendar recurrence entries do come without time zone information
            # this cause ParseError in vobject lib; therefore we do another attempt with manually attached
            # UTC information (stupid, but seems to work)
            v = vobject.readComponents(data + "\n" + UTC_STRING).next()
            
        self._allDay = False
        try:
            self._dtstart = vobject.icalendar.DateOrDateTimeBehavior.transformToNative(v.dtstart).value
            if type(self._dtstart) == datetime.date:
                self._allDay = True
            elif self._dtstart.tzinfo == None:
                self._dtstart = self._dtstart.replace(tzinfo = UTC())
        except BaseException:
            self._dtstart = None
        try:
            self._dtend = vobject.icalendar.DateOrDateTimeBehavior.transformToNative(v.dtend).value
            if type(self._dtend) == datetime.datetime and self._dtend.tzinfo == None:
                self._dtend = self._dtend.replace(tzinfo = UTC())
        except BaseException:
            self._dtend = None
        try:
            self._rrule = v.rrule
        except BaseException:
            self._rrule = None

    def initFromAttributes(self,  rrule,  dtstart,  dtend = None,  isAllDay = False):   
        """
        Initialize a recurrence from the information chunks
        """
        self._rrule = rrule
        self._dtstart = dtstart
        self._dtend = dtend
        self._allDay = isAllDay
                                
        data = self._rrule.serialize() + self._dtstart.serialize()
        if self._dtend:
            data += dtend.serialize()
            
        if type(self._dtstart.value) == datetime.date or self._dtstart.serialize().strip().endswith("Z"):  # special handling for all day recurrences and UTCs
            frame = vobject.iCalendar()
            frame.add("standard")
            frame.standard = vobject.icalendar.TimezoneComponent(UTC())
            data += frame.standard.serialize()

#        file = open("/tmp/pisi-ics.data", "w")
#        file.write("from attributes")
#        file.write(data)
#        file.close()
#        import os
#        os.system("gedit /tmp/pisi-ics.data")
        self._data = data

    def getData(self):
        """
        GETTER
        """
        return self._data
        
    def getDTStart(self):
        """
        GETTER
        """
        return self._dtstart
        
    def getDTEnd(self):
        """
        GETTER
        """
        return self._dtend
        
    def getRRule(self):
        """
        GETTER
        """
        return self._rrule
        
    def isAllDay(self):
        """
        GETTER
        """
        return self._allDay
        
    def __eq__(self,  other):
        """
        Operator overload
        
        Checks whether all items in the recurrences (rrule, dtstart, dtend) match.
        """
        if other == None:
            return False
        if type(other) == str:
            return False
        return self._rrule == other._rrule and self._dtstart != other._dtstart and self._dtend != other._dtend
        
    def __ne__(self,  other):
        """
        Operator overload
        
        @return: NOT L{__eq__}
        """
        return not self.__eq__(other)

    def prettyPrint ( self ):
        """
        Prints all attributes 'nicely'..
        """
        print "\t_PrettyPrint of Recurrence"
        print "\t\tStart:\t%s" %(self._dtstart)
        print "\t\tEnd:\t%s" %(self._dtend)
        print "\t\tRRule:\t%s" %(self._rrule)


class AbstractCalendarSynchronizationModule(pisiinterfaces.AbstractSynchronizationModule):
    """
    Super class for all synchronization modules, which aim to synchronize contacts information.
    
    Each Synchronization class implementing contact synchronization should inherit from this class.
    @ivar _allEvents: Dictionary to hold all Calendar instances for the implementation.
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
        
        @return: The link to the instance variable L{_allEvents}.
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
    """
    Assembles a unique ID for PISI events
    
    A random number is generated.
    """
    return str(random.randint(0,  100000000000000000000000))
