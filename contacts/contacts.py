"""
    Our own contact-entry-object.
    
    This file is part of Pisi.

    You should first read the corresponding Wiki side for development of contact modules:
    U{https://projects.openmoko.org/plugins/wiki/index.php?ContactsAPI&id=156&type=g}

    Besides the two classes for a Contact instance and an abstract synchronization module for contacts
    you can find a method L{assembleID} in here, which should be used to assemble an ID for a contact
    entry when loaded from the data source. This way, it is made sure, that all implementation use exactly 
    the same algorithm. (unfortunately, there is not option to have an additional attribute for this reason, 
    which is stored in all the data sources for the entry.)

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
from pisiconstants import *
import pisiprogress
import pisiinterfaces

class Contact(pisiinterfaces.Syncable):
    """
    Holds information for a single contact instance.
    """
    def __init__(self, id, attributes):
        """
        Initialize contact.
        
        @param id: is the id the module uses to id the contact
        @param attributes: a dictionary with attributes. 
        """
        pisiinterfaces.Syncable.__init__(self, id,  attributes)

    def compare(self,  contactEntry):
        """
        Compares this entry with another one and checks, whether all attributes from this one have the same values in the other one and vice verse
        
        @return: 0 if there is at least a single difference in attributes; 1 if all attributes are the same
        """
        try:
            for key in self.attributes.keys():
                if self.attributes[key] == None or self.attributes[key] == "":
                    # if attribute is there but not set, skip
                    continue
                if not contactEntry.attributes[key] == self.attributes[key]:
                    return 0
                    
            for key in contactEntry.attributes.keys():
                if contactEntry.attributes[key] == None or contactEntry.attributes[key] == "":
                    # if attribute is there but not set, skip
                    continue
                if not self.attributes[key] == contactEntry.attributes[key] :
                    return 0
        except KeyError:
            return 0
        return 1

class AbstractContactSynchronizationModule(pisiinterfaces.AbstractSynchronizationModule):
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
        self._allContacts = self._allEntries
        self._history = []
                
    def allContacts( self ):
        """
        Getter.
        
        @return: The link to the instance variable L{_allContacts}.
        """
        return self.allEntries()
        
    def getContact(self,  id):
        """
        GETTER
        
        @return: The link with the given ID.
        """
        return self.getEntry(id)

    def flush(self):
        """
        Remove all entries in repository
        
        An entry in the history list (L{_history}) is appended for each entry in the contact list with action id for 'delete'.
        Afterwards, the dictionary for all contacts (L{_allContacts}) is flushed.
        """
        for id in self._allEntries.keys():
            self._history.append([ACTIONID_DELETE,  id])
        pisiinterfaces.AbstractSynchronizationModule.flush(self)
        self._allContacts = self._allEntries

    def addContact( self, contactInstance ):
        """
        Saves a contact for later writing
        
        One entry is added to the history list (L{_history}) with action id for 'add' and the new instance is stored in the contacts dictionary (L{_allContacts}).
        """
        self.addEntry(contactInstance)
        self._history.append([ACTIONID_ADD,  contactInstance.getID()])

    def replaceContact( self, id, updatedContact):
        """
        Replaces an existing contact entry with a new one.

        One entry is added to the history list (L{_history}) with action id for 'replace' and the old instance is replaced by the new one in the contacts dictionary (L{_allContacts}).
        """
        pisiprogress.getCallback().verbose("We will replace contact %s" %(id))
        self.replaceEntry(id, updatedContact)
        self._history.append([ACTIONID_MODIFY,  id])

    def removeContact( self, id ):
        """
        Removes a contact entry
        
        One entry is added to the history list (L{_history}) with action id for 'delete' and the instance is as well removed from the contacts dictionary (L{_allContacts}).
        """
        pisiprogress.getCallback().verbose("We will delete contact %s" %(id))
        self.removeEntry(id)
        self._history.append([ACTIONID_DELETE,  id])
        

def _safeString(st,  replacement = ""):
    """
    Supporing function which makes sure that the given value can be concatenated with other strings.
    """
    try:
        return "" + st
    except TypeError:
        return replacement

def assembleID(contactAtts):
    """
    Common way of creating a unique ID for each contact.
    
    Current implementation assembles one by using firstName and lastName.
    """
    return "@" + _safeString(contactAtts['firstname']) + "@" + _safeString(contactAtts['lastname']) + "@"
