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
    # Get all events
    allEvents = [ source[0].allEvents(), source[1].allEvents() ]
    pisiprogress.getCallback().verbose("")
    pisiprogress.getCallback().verbose("Module %s has %d events in total" %(modulesToLoad[0],  len(allEvents[0].getAllEvents())))
    pisiprogress.getCallback().verbose("Module %s has %d events in total" %(modulesToLoad[1],  len(allEvents[1].getAllEvents())))
    pisiprogress.getCallback().verbose("")
    # Loop through all events from source[0]
    for id,event in allEvents[0].getAllEvents().iteritems():
        pisiprogress.getCallback().verbose("Checking eventid %s from module %s" %(id, modulesToLoad[0]))
        # Does it exist in the other module? Did it ever?
        if not event.commonid:
            # This event has never been synchronized
            pisiprogress.getCallback().verbose("\tThis event has never been synchronized")
            pisiprogress.getCallback().verbose("\tAdd %s to module %s" %(event.id,  modulesToLoad[1]))
            event.commonid = event.id # 'Steal' the id as the common id
            # Update commonid
            source[0].addCommonid( event.id, event.commonid )
            # Add event
            source[1].addEvent( event )
        else:
            sameEvent = allEvents[1].getEvent(event.commonid)
            if not sameEvent==False:
                # They have the same event
                pisiprogress.getCallback().verbose("\tThey both have this event")
                # See if they have different updatetimes

                if event.updated < sameEvent.updated:
                    source[0].replaceEvent( event.id, sameEvent )
                elif event.updated > sameEvent.updated:
                    event.id = sameEvent.id
                    source[1].replaceEvent( sameEvent.id, event )

                # Remove event from our temporary list from source[1]
                allEvents[1].removeEvent( sameEvent.commonid )
            else:
                # Event has been deleted from source[1]
                # so delete it from source[0]
                source[0].removeEvent( event.id )
        pisiprogress.getCallback().verbose("")

    # Loop through all remaning events from source[1]
    for id,event in allEvents[1].getAllEvents().iteritems():
        pisiprogress.getCallback().verbose("Checking eventid %s from module %s" %(id,  modulesToLoad[0]))
        # Does it exist in the other module? Did it ever?
        if not event.commonid:
            # This event has never been synchronized
            pisiprogress.getCallback().verbose("\tThis event has never been synchronized")
            pisiprogress.getCallback().verbose("\tAdd %s to module %s" %(event.id,  modulesToLoad[1]))
            event.commonid = event.id # 'Steal' the id as the common id
            # Update commonid
            source[1].addCommonid( event.id, event.commonid )
            # Add event
            source[0].addEvent( event )
        else:
            # Event has been deleted from source[0]
            # so delete it from source[1]
            source[1].removeEvent( event.id )
