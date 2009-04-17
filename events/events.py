#!/usr/bin/env python

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
import pisiprogress
import pisiinterfaces

# Recurrence constants
YEARLY, MONTHLY, WEEKLY, DAILY = range(4)
MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY = range(7)

class Event:
    def __init__( self, id, commonid, updated, attributes ):
        """
        Initialize event.
        @param id: is the id the module uses to id the event
        @param commonid: This is the id for this event and the two modules. If it hasn't been synchronized (with the other module), it should be False.
        @param updated: datetime instance
        @param attributes: a dictionary with attributes. See U{http://projects.openmoko.org/plugins/wiki/index.php?Developer&id=156&type=g} for more help.
        """
        self.id        = id
        self.commonid  = commonid
        self.updated   = updated
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
        print "\t\t- Updated = ",self.updated
        for key,value in self.attributes.iteritems():
            print "\t\t- ",key," = ",value


class Events:
    def __init__( self ):
        self._events = dict()

    def insertEvent( self, eventInstance ):
        """Saves a new event. Expects an event instance."""
        _id = eventInstance.commonid
        if _id==False:
            _id = eventInstance.id
        self._events[_id] = eventInstance

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
            pisiprogress.getCallback().error( "Couldn't remove event with id %s. Wasn't found!" %(id))


class Recurrence:
    def __init__( self ):
        # We don't have any information yet
        self.icsTextReady = False
        self.recurrenceElementsReady = False
    
    def setRecurrenceElements( self, startDate, endDate, frequency, count, untilDate, byMonth, byDay ):
        """Arguments according to iCalendar standard (RFC 2445)"""
        self.recurrenceElementsReady = True
        # Look for inspiration in: http://codespeak.net/icalendar/
##        self.startDate = startDate
##        self.endDate   = endDate
##        self.frequency = frequency
##        self.count     = count
##        self.untilDate = untilDate
##        self.byMonth   = byMonth
##        self.byDay     = byDay

    def setIcsText( self, icsText ):
        """Recurrence according to iCalendar standard (RFC 2445)"""
        self.icsTextReady = True
        self.icsText = icsText
    
    def getIcsText( self ):
        if not self.icsTextReady:
            self._compileIcsText
        return self.icsText
    
    def getRecurrenceElements( self ):
        # TODO
        return False

    def _compileIcsText( self ):
        """Creates iCalendar recurrence text from 'recurrenceElements'"""
        # TODO
    
    def _compileRecurrenceElements( self ):
        """Creates 'recurrenceElements' from iCalendar recurrence text"""
        # TODO




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
#        self._allContacts = self._allEntries
#        self._history = []
#                
#    def allContacts( self ):
#        """
#        Getter.
#        
#        @return: The link to the instance variable L{_allContacts}.
#        """
#        return self.allEntries()
#        
#    def getContact(self,  id):
#        """
#        GETTER
#        
#        @return: The link with the given ID.
#        """
#        return self.getEntry(id)

#    def flush(self):
#        """
#        Remove all entries in repository
#        
#        An entry in the history list (L{_history}) is appended for each entry in the contact list with action id for 'delete'.
#        Afterwards, the dictionary for all contacts (L{_allContacts}) is flushed.
#        """
#        for id in self._allEntries.keys():
#            self._history.append([ACTIONID_DELETE,  id])
#        pisiinterfaces.AbstractSynchronizationModule.flush(self)
#        self._allContacts = self._allEntries
#
#    def addContact( self, contactInstance ):
#        """
#        Saves a contact for later writing
#        
#        One entry is added to the history list (L{_history}) with action id for 'add' and the new instance is stored in the contacts dictionary (L{_allContacts}).
#        """
#        self.addEntry(contactInstance)
#        self._history.append([ACTIONID_ADD,  contactInstance.getID()])
#
#    def replaceContact( self, id, updatedContact):
#        """
#        Replaces an existing contact entry with a new one.
#
#        One entry is added to the history list (L{_history}) with action id for 'replace' and the old instance is replaced by the new one in the contacts dictionary (L{_allContacts}).
#        """
#        pisiprogress.getCallback().verbose("We will replace contact %s" %(id))
#        self.replaceEntry(id, updatedContact)
#        self._history.append([ACTIONID_MODIFY,  id])
#
#    def removeContact( self, id ):
#        """
#        Removes a contact entry
#        
#        One entry is added to the history list (L{_history}) with action id for 'delete' and the instance is as well removed from the contacts dictionary (L{_allContacts}).
#        """
#        pisiprogress.getCallback().verbose("We will delete contact %s" %(id))
#        self.removeEntry(id)
#        self._history.append([ACTIONID_DELETE,  id])
