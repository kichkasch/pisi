"""
Command Line Interface to PISI - one implementation of user interaction

This file is part of Pisi.

This module provides the CLI interface to PISI:
    - controlling the entire CLI application
    - Checking of Arguments
    
A callback is defined as well, which handles all the output coming from the application core.

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
from pisiconstants import *
import pisiprogress
import pisi
import sys
import os
import ConfigParser
from thirdparty.epydocutil import TerminalController 

class CLICallback(pisiprogress.AbstractCallback):
    """
    Command Line Interface to PISI
    """
    
    def __init__(self,  verbose):
        """
        Constructor
        
        Remember whether we are in verbose mode.
        """
        pisiprogress.AbstractCallback.__init__(self)
        self.isVerbose = verbose
        if not verbose:
            self.term = TerminalController()
    
    def message(self,  st):
        """
        Output the string to console
        """
        if not self.isVerbose:
            sys.stdout.write(self.term.CLEAR_LINE)
        print st

    def error(self,  st):
        """
        Redirect to L{message}
        """
        self.message(st)

    def verbose(self,  st):
        """
        Only redirect to L{message} if we are in verbose mode
        """
        if self.isVerbose:
            self.message(st)
        
    def promptGeneric(self,  prompt,  default):
        """
        Prepare a prompt and return the user input
        
        If user input is empty, the provided default is returned.
        """
        if default:
            prompt += "[" + default + "]"
        st = raw_input(prompt + ": ")
        if default:
            if st == '':
                return default
        return st
        
    def update(self,  status):
        """
        If we are not in verbose mode, we display the progress here
        """
        if not self.isVerbose:
            percent = self.progress.calculateOverallProgress() / 100.0
            message = status 
            background = "." * CONSOLE_PROGRESSBAR_WIDTH
            dots = int(len(background)  * percent)
            sys.stdout.write(self.term.CLEAR_LINE + '%3d%% '%(100*percent) + self.term.GREEN + '[' + self.term.BOLD + '='*dots + background[dots:] + self.term.NORMAL + self.term.GREEN + '] ' + self.term.NORMAL + message + self.term.BOL) 
            sys.stdout.flush()            
            if status == 'Finished':
                print
#            print ("Progress: %d %% (%s)" %(self.progress.calculateOverallProgress(),  status))
            
    def _strFixedLen(self, str,  width,  spaces = " "):
        """
        Supporting function to print a string with a fixed length (good for tables)
        
        Cuts the string when too long and fills up with characters when too short.
        """
        return (str + (spaces * width))[:width]

    def _getDetailValue(self,  dict,  key,  default = '<n.a.>'):
        """
        Gets around the problem if an attribute in one data source is not set in the other one at all
        
        Returns default value if the attribute is not available in the given dictionery (key error).
        """
        try:
            return dict[key]
        except KeyError:
            return default


    def _printConflictDetails(self,  entry1,  entry2,  nameSource1,  nameSource2):
        """
        Supporting function to show differences for two contact entries
        
        Prints a table with all attributes being different in the two sources for comparing two contact entries.
        """
        diffList = pisi.determineConflictDetails(entry1,  entry2)        
        
        print "\n " + "=" * 25 + " DETAILS " + "=" * 25
        print "* %s, %s" %(entry1.attributes['lastname'],entry1.attributes['firstname'])
        print self._strFixedLen('Attribute',  15) + " | " + self._strFixedLen(nameSource1,  20) + " | " + self._strFixedLen(nameSource2,  20)
        print "-" * 60
        for key in diffList.keys():
            print self._strFixedLen(key,  15) + " | " + self._strFixedLen(self._getDetailValue(entry1.attributes, key),  20) + " | " + self._strFixedLen(self._getDetailValue(entry2.attributes, key),  20)
        print "-" * 60

    def askConfirmation(self, source,  idList):
        """
        Use interaction for choosing which contact entry to keep in case of a conflict
        
        Iterates through the given list of contact IDs and requests the user for choosing an action for every single entry.
        
        @return: A dictionary which contains the action for each conflict entry; the key is the id of the contact entry, 
        the value one out of a - keep entry from first source, b - keep value from second source and s - skip this entry (no change on either side)
        """
        if len(idList) > 0:
            print
            print "Please resolve the following conflicts manually"
        ret = {}
        for entryID in idList:
            entry1 = source[0].getContact(entryID)
            entry2 = source[1].getContact(entryID)
            myinput = ''
            while myinput != 'a' and myinput != 'b' and myinput != 's':
                if myinput != 'd':
                    print "* %s, %s" %(entry1.attributes['lastname'],entry1.attributes['firstname'])
                else:
                    self._printConflictDetails(entry1,  entry2, source[0].getName(),  source[1].getName() )
                print "  [a]-Keep <%s> [b]-Keep <%s> [d]etails [s]kip [a|b|d|s]: " %(source[0].getName(),  source[1].getName()), 
                myinput = raw_input()
            ret[entryID] = myinput
        return ret
     
def testConfiguration():
    """
    Checks, whether configuration can be loaded from PISI core.
    
    If not possible, an error message is printed and False will be returned.
    @return: False, if an Error occurs when loading the configration from core; otherwise True
    """
    try:
        pisi.getConfiguration()
        return True
    except ValueError:
        print ("PISI configuration not found")
        print ("For running PISI you must have a configuration file located in '/home/root/.pisi/conf'.\n\nWith the package a well-documented sample was placed at '/home/root/.pisi/conf_default'. You may rename this for a starting point - then edit this file in order to configure your PIM synchronization data sources.")
        return False
     
        
def startCLI():
    """
    Controls the major flow for PISI (CLI)
    
    Calls one after another the supporting functions in this module.
    """
    if not testConfiguration():
        sys.exit(0)
    
    verbose, modulesToLoad, modulesNamesCombined, soft, mergeMode = parseArguments()
    cb = CLICallback(verbose)
    pisiprogress.registerCallback(cb)
    
    cb.progress.push(0, 10)
    cb.update('Starting Configuration')
    cb.verbose('')
    cb.verbose("*" * 55)
    cb.verbose( "*" * 22 + "   PISI    " + "*" * 22)
    cb.verbose( "*" * 55)
    cb.verbose( "** PISI is synchronizing information " + "*" * 18)
    cb.verbose( "** http://projects.openmoko.org/projects/pisi/ " + "*" * 8)
    cb.verbose( "*" * 55)
    
    cb.verbose( ("\n" + "*" * 15 + " PHASE 0 - Configuration " + "*" * 15))
    cb.verbose( "Verbose mode on")
    cb.verbose( ("In case of conflicts I use the following strategy: %s" %(MERGEMODE_STRINGS[mergeMode])))

    config,  configfolder = pisi.readConfiguration()
    source = pisi.importModules(configfolder,  config,  modulesToLoad,  modulesNamesCombined, soft)
    mode = pisi.determineMode(config,  modulesToLoad)
    cb.progress.drop()

    cb.progress.push(10, 40)
    cb.update('Loading from sources')
    cb.verbose("\n" + "*" * 18 + " PHASE 1 - Loading " + "*" * 18)
    cb.progress.push(0, 50)
    source[0].load()
    cb.progress.drop()
    cb.progress.push(50,  100)
    cb.update('Loading')
    source[1].load()
    cb.progress.drop()
    cb.progress.drop()

    cb.progress.push(40, 70)
    cb.update('Comparing sources')
    cb.verbose("\n" + "*" * 17 + " PHASE 2 - Comparing " + "*" * 17)
    if mode == MODE_CALENDAR:  # events mode
        pisi.eventsSync.syncEvents(verbose,  modulesToLoad,  source)
    elif mode == MODE_CONTACTS:  # contacts mode
        pisi.contactsSync.syncContacts(verbose,  modulesToLoad,  source,  mergeMode)    
    cb.progress.drop()

    cb.progress.push(70, 100)
    cb.update('Making changes permanent')
    cb.verbose ("\n" + "*" * 18 + " PHASE 3 - Saving  " + "*" * 18)
    if soft:
        print "You chose soft mode for PISI - changes are not applied to data sources."
    else:
        pisi.applyChanges(source)
    cb.verbose( "*" * 24 + " DONE  " + "*" * 24)
    cb.progress.drop()
    cb.update('Finished')


def parseArguments ():
    """
    Parses command line arguments
    
    All information from the command line arguments are returned by this function.
    If the number of arguments given is not valid, a help text is printed on the console by calling function L{usage}.
    """
    mergeMode = MERGEMODE_SKIP 
    modulesToLoad = []
    modulesNamesCombined = ""
    soft = False
    verbose = False
    for arg in sys.argv[1:]:
        if arg[:1]!='-':
            modulesToLoad.append( arg )
            modulesNamesCombined += arg
        elif arg=='-v' or arg=='--verbose':
            verbose=True
        elif arg=='-s' or arg=='--soft':
            soft = True
        elif arg=='-l' or arg=='--list-configurations':
            list_configurations()
        elif arg.startswith('-m'):
            mergeMode = int(arg[2:])
    if len(modulesToLoad)!=2:
        usage()
    return verbose, modulesToLoad, modulesNamesCombined, soft, mergeMode

def usage ():
    """
    Prints a help text to the console
    
    The application is shut down afterwards.
    """
    usage = """You start the program by specifying 2 sources to synchronize.
Like this:
  ./pisi [options] $SOURCE1 $SOURCE2
Flags:
  -v --verbose
      Make program verbose
  -s --soft
      Don't actually make any changes on the servers/in the files
  -l --list-configurations
      List which configurations there are in the config-file (this don't need
      the two modules)
  -mX
      Define the mode to deal with conflicts:
      -m0 SKIP entry (default)
      -m1 FLUSH source 1 in the beginning
      -m2 FLUSH source 2 in the beginning
      -m3 Overwrite source 1 entry wise
      -m4 Overwrite source 2 entry wise
      -m5 Manually confirm each entry

Configuration:
Read https://projects.openmoko.org/plugins/wiki/index.php?configure&id=156&type=g for help.
"""
    sys.exit(usage)
    
def list_configurations():
    """
    Prints available configurations for data sources
    
    Parses the configuration file for PISI and prints all available data sources to the console.
    """
    config = pisi.getConfiguration()
    print 'You have these configurations:'
    for con in config.sections():
        print ('\t-%s which uses module <%s>: %s'  %(con, config.get(con,'module'),  config.get(con,'description')))
    sys.exit(0)
