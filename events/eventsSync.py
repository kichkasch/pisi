""" 
Module for synchronization of two sources of type calendar "event".

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
import pickle, os
import pisiprogress

def syncEvents(verbose,  modulesToLoad,  source):
    modulesToLoad.sort() 
    modulesNamesCombined = modulesToLoad[0] + modulesToLoad[1]
    knownEvents = _readModulesPreviousEvents( modulesNamesCombined )
    
    allEventsLeft = source[0].allEvents()
    allEventsRight = source[1].allEvents()
    pisiprogress.getCallback().verbose("")
    pisiprogress.getCallback().verbose("Module %s has %d events in total" %(modulesToLoad[0],  len(allEventsLeft)))
    pisiprogress.getCallback().verbose("Module %s has %d events in total" %(modulesToLoad[1],  len(allEventsRight)))
    pisiprogress.getCallback().verbose("")
    for id in allEventsLeft.keys():
        event = allEventsLeft[id]
        if not id in allEventsRight.keys():    
            # This event is not in the right side
            if id in knownEvents:
                # It is deleted from the right side
                source[0].removeEvent(id)
            else:
                # It's new
                source[1].addEvent(event)
                knownEvents.append(id)
        else:
            sameEvent = allEventsRight[id]
            if not event.compare(sameEvent):    # only update if something really changed; update time is not an indicator - this was updated when we wrote the last entry
                if event.updated == "":     # this event has never been updated
                    source[0].replaceEvent( event.id, sameEvent )
                elif sameEvent.updated == "":     # the other event has never been updated
                    source[1].replaceEvent( event.id, event )
                elif event.updated < sameEvent.updated:
                    source[0].replaceEvent( event.id, sameEvent )
                elif event.updated > sameEvent.updated:
                    source[1].replaceEvent( sameEvent.id, event )
                else:
                    pass    # same update time should mean both sides are untouched!

    for id in allEventsRight.keys():
        event = allEventsRight[id]
        if not id in allEventsLeft.keys():
            # This event is not in the left side
            if id in knownEvents:
                # It is deleted from the left side
                source[1].removeEvent(id)
            else:
                source[0].addEvent( event )
                knownEvents.append(id)
    
    _saveModulesNewEvent(modulesNamesCombined, knownEvents)

def _readModulesPreviousEvents( moduleNames ):
    """
    Load, which events were existent already in past, when these two sources were synchronised
    """
    homedir = os.environ.get('HOME')
    configfolder = homedir + '/.pisi/modules/'
    if not os.path.exists(configfolder):
        os.mkdir( configfolder )
    modulesFile = configfolder + moduleNames
    if not os.path.exists(modulesFile):
        tmplist = []
        file = open(modulesFile, 'w')
        pickle.dump(tmplist, file)
        file.close()
        return []
    file = open(modulesFile, 'r')
    ret = pickle.load(file)
    file.close()
    return ret

def _saveModulesNewEvent( moduleNames, list ):
    """
    Save the list of events ids, which have ever been synchronised for these two sources
    """
    homedir = os.environ.get('HOME')
    modulesFile = homedir + '/.pisi/modules/' + moduleNames
    file = open(modulesFile, 'w')
    pickle.dump(list, file)
    file.close()
