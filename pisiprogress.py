"""
Abstract way of user interaction

This file is part of Pisi.

In order to make it possible, to use core functionality code with any kind of User Interface, the user interaction is
being abstracted to an interface, which has to be overwritten for a UI implementation.

The UI implementation is simply registered in the beginning, the core functionality modules access it by using the
Singleton implementation. This way, there is no need for passing around a reference to the UI all the time.

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

global instance
instance = None

def getCallback():
    """
    Singleton
    
    This function may be called from anywhere within the program in order to carry out user interaction.
    """
    global instance
    if instance == None:
        raise ValueError("No callback yet implemented - progress cannot be reported!")
    return instance
    
def registerCallback(callback):
    """
    Register a callback instance
    
    @param callback: Implementation of interface L{AbstractCallback}
    """
    global instance
    instance = callback
    
    
class AbstractCallback():
    """
    Each callback implementation (CLI or GUI) should overwrite this interface
    """
    def __init__(self):
        """
        Constructor
        
        Initializes a L{Progress} instance.
        """
        self.progress = Progress()
    
    def message(self,  st):
        """
        Output a message to the user
        """
        pass
        
    def verbose(self,  st):
        """
        Output a message (of lower interest) to the user
        """
        pass
        
    def error(self,  st):
        """
        Pass on an error message to the user
        """
        pass
        
    def promptGeneric(self,  prompt,  default=None):
        """
        Prompt the user for a single entry to type in
        """
        return None
        
    def promptGenericConfirmation(self,  prompt):
        """
        Ask user for a single confirmation (OK / Cancel)
        """
        return False

    def promptFilename(self, prompt,  default):
        """
        Prompt the user for providing a file name
        """
        return self.promptGeneric(prompt, default)
                
    def askConfirmation(self, source,  idList):
        """
        Use interaction for choosing which contact entry to keep in case of a conflict
        
        @return: A dictionary which contains the action for each conflict entry; the key is the id of the contact entry, 
        the value one out of a - keep entry from first source, b - keep value from second source and s - skip this entry (no change on either side)
        """
        return {}
        
    def update(self,  status):
        """
        This function should be called whenever new information has been made available and the UI should be updates somehow.
        """
        pass

class Progress:
    """
    Handling of progress in terms of percentage
    
    You may have a linear progress 'bar' or create several layers of progresses.
    There is a need to put some more documentation here soon.
    """
    def __init__(self):
        """
        Initialize progress with one single layer
        """
        self.reset()
        
    def setProgress(self,  x):
        """
        Set progress in top layer
        """
        self._progress[len(self._progress)-1][0] = x
        
    def push(self,  x1,  x2):
        """
        Add another layer of progress
        """
        self.setProgress(x1)
        self._progress.append([0,  (x1, x2)])
        
    def drop(self):
        """
        Remove the top layer in progress
        """
        current = self._progress[len(self._progress)-1]
        self._progress[len(self._progress)-1:] = []
        x1,  x2 = current[1]
        self.setProgress(x2)
        
    def reset(self):
        """
        Drop all layers and reset to 0
        """
        self._progress = []
        self._progress.append([0,  (0, 100)])
        
    def calculateOverallProgress(self):
        """
        Iterate through layers to calculate the current overall progress
        """
        total = 0.0
        for i in reversed (range(0,  len(self._progress))):
            current = self._progress[i]
            x1,  x2 = current[1]
            total = (total + current[0]) / 100 * (x2 - x1)
        return total
