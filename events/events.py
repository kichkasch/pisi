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

# Recurrence constants
YEARLY, MONTHLY, WEEKLY, DAILY = range(4)
MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)

class Event(pisiinterfaces.Syncable):
    def __init__( self, id, updated, attributes ):
        """
        Initialize event.
        @param id: is the id the module uses to id the event
        @param commonid: This is the id for this event and the two modules. If it hasn't been synchronized (with the other module), it should be False.
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

#class Recurrence:
#    def __init__( self ):
#        # We don't have any information yet
#        self.icsTextReady = False
#        self.recurrenceElementsReady = False
#    
#    def setRecurrenceElements( self, startDate, endDate, frequency, count, untilDate, byMonth, byDay ):
#        """Arguments according to iCalendar standard (RFC 2445)"""
#        self.recurrenceElementsReady = True
#        # Look for inspiration in: http://codespeak.net/icalendar/
###        self.startDate = startDate
###        self.endDate   = endDate
###        self.frequency = frequency
###        self.count     = count
###        self.untilDate = untilDate
###        self.byMonth   = byMonth
###        self.byDay     = byDay
#
#    def setIcsText( self, icsText ):
#        """Recurrence according to iCalendar standard (RFC 2445)"""
#        self.icsTextReady = True
#        self.icsText = icsText
#    
#    def getIcsText( self ):
#        if not self.icsTextReady:
#            self._compileIcsText
#        return self.icsText
#    
#    def getRecurrenceElements( self ):
#        # TODO
#        return False
#
#    def _compileIcsText( self ):
#        """Creates iCalendar recurrence text from 'recurrenceElements'"""
#        # TODO
#    
#    def _compileRecurrenceElements( self ):
#        """Creates 'recurrenceElements' from iCalendar recurrence text"""
#        # TODO




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

    def removeContact( self, id ):
        """
        Removes an event entry
        
        One entry is added to the history list (L{_history}) with action id for 'delete' and the delete command is passed on to the super class method L{removeEntry}.
        """
        self.removeEntry(id)
        self._history.append([ACTIONID_DELETE,  id])
        
def assembleID():
    return str(random.randint(0,  100000000000000000000000))
