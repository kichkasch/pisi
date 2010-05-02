#!/usr/bin/env python

"""
Main module for PISI

This file is part of Pisi.

This file is the python module to be started for running PISI.
Initialization is performed in here:
 - Loading and parsing of configuration from file
 - Importing of modules (for data sources)

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

import ConfigParser
import os
import os.path
import sys

from events import events,  eventsSync
from contacts import contactsSync
from pisiconstants import *
import pisiprogress

def getConfigLocation():
    return os.path.join(os.environ.get('HOME'), '.pisi', 'conf')

def getConfiguration():
    """
    Returns the entire content of the configuration file
    """
    # Read configuration
    configfile = getConfigLocation()
    if not os.path.isfile(configfile):
        raise ValueError("Couldn't find the configuration file: "+configfile)
    config = ConfigParser.ConfigParser()
    config.readfp(open(configfile))
    return config

def readConfiguration():
    """
    Loads configuration from the configuration file and returns the container with all the information as well as the config folder
    """
    configfolder = os.path.join(os.environ.get('HOME'), '.pisi')
    pisiprogress.getCallback().verbose("Reading configfile: %s" %(configfile) )
    config = getConfiguration()
    return config, configfolder

def importModules(configfolder,  config,  modulesToLoad,  modulesNamesCombined, soft):
    """
    Imports the required modules for handling the specific data sources
    
    The required modules had been determined by examining the chosen data sources. 
    The required modules are now imported.
    """
    # Create folders for the modules to use to save stuff
    modulesFolder = configfolder+modulesToLoad[0]+modulesToLoad[1]+'/'
    if not os.path.exists(modulesFolder):
        os.mkdir( modulesFolder )

    source = []
    for i in range(0,2):
        modulename = config.get(  modulesToLoad[i], 'module' )
        if not os.path.exists(modulesFolder + modulesToLoad[i]):
            os.mkdir( modulesFolder + modulesToLoad[i] )
        exec "from modules import " + modulename + " as module"+i.__str__()
        exec "source.append( module"+i.__str__()+".SynchronizationModule(modulesNamesCombined, config, modulesToLoad[i], modulesFolder+modulesToLoad[i]+'/', True, soft) )"
    # Now we have source[0] and source[1] as our 2 synchronization modules
    return source

def determineMode(config,  modulesToLoad):
    """
    Check, what type of information we have to synchronize
    
    Checks, whether the two modules (for the given data sources) are equal in type for data they can sync (contacts - contacts or calendar - calendar). 
    This is done by simply comparing the starting part of the module names (all stuff left from '_'); this is a naming convention.
    E.g. contacts_ldap and contacts_sqlite3 would return 'CONTACTS' mode, whereby contacts_ldap and calendar_google would raise an error.
    An error is thrown whenever the two sources do not match in type, or if a type is not known or unvalid..
    """
    modes = [None,  None]
    for j in range(0, 2):
        modulename = config.get(  modulesToLoad[j], 'module' )
        modeString = modulename[:modulename.index("_")]
        for i in range (0, len(MODE_STRINGS)):
            if MODE_STRINGS[i] == modeString:
                modes[j] = i
        if modes[j] == None:
            raise ValueError ("Mode check: mode <%s> not known." %(modulesToLoad[j]))
    if modes[0] != modes[1]:
        raise ValueError("Mode check: Source 1 and 2 are not compatible.")
    pisiprogress.getCallback().verbose("Running in mode <%s>." %(MODE_STRINGS[modes[0]]))
    return modes[0]

def applyChanges(source):
    """
    Write changes through to data source backends
    
    All changes in syncing are only performed in memory. This function finally requests the data sources to make their changes permanent by calling
    the corresponding function in there.
    """
    pisiprogress.getCallback().verbose("Making changes permanent")
    pisiprogress.getCallback().progress.push(0, 50)
    try:
        source[0].saveModifications()
    except ValueError,  ex:
        pisiprogress.getCallback().error("Changes to source 1 (%s) could not be applied due to the following reason: %s" %(source[0].getName(),  ex))
    pisiprogress.getCallback().progress.drop()
    pisiprogress.getCallback().progress.push(50, 100)
    try:
        source[1].saveModifications()
    except ValueError,  ex:
        pisiprogress.getCallback().error ("Changes to source 2 (%s) could not be applied due to the following reason: %s" %(source[1].getName(),  ex))
    pisiprogress.getCallback().progress.drop()
        

def determineConflictDetails(entry1,  entry2):
    diffList = {}
    for key,  value in entry1.attributes.iteritems():
        try:
            if value == None or value == '':
                continue
            if entry2.attributes[key] != value:
                diffList[key] = 1
        except KeyError:
            diffList[key] = 1
    for key,  value in entry2.attributes.iteritems():
        try:
            if value == None or value == '':
                continue
            if entry1.attributes[key] != value:
                diffList[key] = 1
        except KeyError:
            diffList[key] = 1
    return diffList

"""
This starts the CLI version of PISI
"""
if __name__ == "__main__":
    import pisicli
    pisicli.startCLI()
