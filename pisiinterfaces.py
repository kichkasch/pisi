"""
Provides interfaces (abstract super classes) for generic functionality.

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
import os

class Syncable:
    """
    Common interface (Super-class) for a syncable items (calendar event, contact entry)
    """
    def __init__(self, id, attributes):
        """
        Constructor
        """
        self.id         = id
        self.attributes = attributes
        
    def compare(self,  contactEntry):
        """
        Compares this entry with another one and checks, whether all attributes from this one have the same values in the other one and vice verse
        
        @return: 0 if there is at least a single difference in attributes; 1 if all attributes are the same
        """
        raise ValueError("!!!Implementation missing!!!")        # this has to be implemented individually for each syncable type
        
    def getID(self):
        """
        GETTER
        """
        return self.id

    def prettyPrint (self ):
        """
        Beautyful output for one Syncable entry
        
        Prints a headline containing the ID of the entry and iterates through all attributes available for the entry and displays each in a single line.
        """
        print "\t_PrettyPrint of id:",self.id
        for key,value in self.attributes.iteritems():
            print ("\t\t- %s = %s" %(key,value)) #.encode("utf8",  "replace")



class AbstractSynchronizationModule:
    """
    Super class for all synchronization modules, which aim to synchronize any kind of information.
    
    Each Synchronization class should inherit from this class.
    
    @ivar _allEntries: Dictionary for storing all information entries
    """
    def __init__(self, verbose, soft, modulesString, config, configsection, name = "unkown source"):
        """
        Constructor
        
        Instance variables are initialized.
        """
        self.verbose = verbose
        self.soft = soft
        self.modulesString = modulesString
        self._name = name
        self._description = config.get(configsection,'description')
        
        try:
            self._preProcess = config.get(configsection,'preprocess')
        except:
            self._preProcess = None
        try:
            self._postProcess = config.get(configsection,'postprocess')
        except:
            self._postProcess = None
        self._allEntries = {}
        
    def getName(self):
        """
        GETTER
        """
        return self._name

    def getDescription(self):
        """
        GETTER
        """
        return self._description

    def prettyPrint (self ):
        """
        Beautyful output for the entries in the repository
        
        Prints a small headline and calls the function L{Syncable.prettyPrint} for each contact Entry in turn.
        """
        print "Pretty print of %s content:" %(self._name)
        for entry in self.allEntires().values():
            entry.prettyPrint()

    def allEntries( self ):
        """
        Getter.
        
        @return: The link to the instance variable L{_allEntries}.
        """
        return self._allEntries
        
    def getEntry(self,  id):
        """
        GETTER
        
        @return: The link with the given ID.
        """
        return self._allEntries[id]

    def flush(self):
        """
        Remove all entries in repository
        
        The dictionary for all entries (L{_allEntries}) is flushed.
        """
        self._allEntries = {}

    def addEntry( self, entry):
        """
        Saves an entry for later writing
        
        The new instance is stored in the dictionary (L{_allEntries}).
        """
        self._allEntries[entry.getID()] = entry

    def replaceEntry( self, id, updatedEntry):
        """
        Replaces an existing entry with a new one.

        The old instance is replaced by the new one in the  dictionary (L{_allEntries}).
        """
        self._allEntries[id] = updatedEntry

    def removeEntry( self, id ):
        """
        Removes an entry
        
        The instance is removed from the dictionary (L{_allEntries}).
        """
        del self._allEntries[id]

    def preProcess(self):
        """
        Executes the shell command that has been configured for this source under 'preprocess'
        """
        if self._preProcess:
            ret = os.system(self._preProcess)
            
    def postProcess(self):
        """
        Executes the shell command that has been configured for this source under 'postprocess'
        """
        if self._postProcess:
            ret = os.system(self._postProcess)
