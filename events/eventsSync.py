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
import pisiprogress

def syncEvents(verbose,  modulesToLoad,  source):
    allEventsLeft = source[0].allEvents()
    allEventsRight = source[1].allEvents()
    pisiprogress.getCallback().verbose("")
    pisiprogress.getCallback().verbose("Module %s has %d events in total" %(modulesToLoad[0],  len(allEventsLeft)))
    pisiprogress.getCallback().verbose("Module %s has %d events in total" %(modulesToLoad[1],  len(allEventsRight)))
    pisiprogress.getCallback().verbose("")
    for id in allEventsLeft.keys():
        event = allEventsLeft[id]
        if not id in allEventsRight.keys():    
            # This event is new to the right side
            source[1].addEvent(event)
        else:
            sameEvent = allEventsRight[id]
            if not event.compare(sameEvent):    # only update if something really changed; update time is not an indicator - this was updated when we wrote the last entry
                if event.updated < sameEvent.updated:
                    source[0].replaceEvent( event.id, sameEvent )
                elif event.updated > sameEvent.updated:
                    source[1].replaceEvent( sameEvent.id, event )
                else:
                    pass    # same update time should mean both sides are untouched!

    for id in allEventsRight.keys():
        event = allEventsRight[id]
        if not id in allEventsLeft.keys():
            # This event is new to the left side
            source[0].addEvent( event )
