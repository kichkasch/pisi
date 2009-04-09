""" 
    Module for synchronization of two sources of type "contacts".

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
from pisiconstants import *
import pisiprogress

def _askConfirmation(source,  idList):
    """
    Use interaction for choosing which contact entry to keep in case of a conflict
    
    @return: A dictionary which contains the action for each conflict entry; the key is the id of the contact entry, 
    the value one out of a - keep entry from first source, b - keep value from second source and s - skip this entry (no change on either side)
    
    The call is passed on to L{pisiprogress.AbstractCallback.askConfirmation}
    """
    return pisiprogress.getCallback().askConfirmation(source,  idList)

def syncContacts(verbose,  modulesToLoad,  source,  mergeMode):
    """
    Synchronizes two data sources of type 'CONTACT'
    
    This method is taking the mergeMode into account when deciding about overwriting values (in case of conflicts).
    
    All contacts entries of one data source are compared against the ones of the other data source.
    First of all, the ID of the entries is taken into accout for checking, which entries relate to each other. The delta (regarding the IDs) is
    appended to the other data source. Whenever the IDs are the same for two entries, a deep compare is carried out; all attributes are
    compared against each other. If there is any difference, the overwrite of a value (or a skip) is performed depending on the merge mode.
    """
    pisiprogress.getCallback().verbose("")
    pisiprogress.getCallback().verbose("Module %s has %d contacts in total" %(modulesToLoad[0],len(source[0].allContacts())))
    pisiprogress.getCallback().verbose("Module %s has %d contacts in total" %(modulesToLoad[1],len(source[1].allContacts())))

    if mergeMode == MERGEMODE_FLUSH_A:
        pisiprogress.getCallback().verbose("I am in conflict mode FLUSH source 1 - deleting all (%d) entries on this side now." %(len(source[0].allContacts())))
        source[0].flush()
    if mergeMode == MERGEMODE_FLUSH_B:
        pisiprogress.getCallback().verbose("I am in conflict mode FLUSH source 2 - deleting all (%d) entries on this side now." %(len(source[1].allContacts())))
        source[1].flush()

    commonIDs = {}
    delta1 = []
    delta2 = []
    for id1 in source[0].allContacts().keys():
        if source[1].allContacts().has_key(id1):
            commonIDs[id1] = 1
        else:
            delta1.append(id1)
    for id2 in source[1].allContacts().keys():
        if not commonIDs.has_key(id2):
            delta2.append(id2)
            
    # new, we take the entries where there are common ids and compare them deeply
    conflicts = []
    for key in commonIDs.keys():
        if not source[0].getContact(key).compare(source[1].getContact(key)):
            del commonIDs[key]
            conflicts.append(key)

    pisiprogress.getCallback().verbose("")
    pisiprogress.getCallback().verbose("%d entries in common" %(len(commonIDs)))
    pisiprogress.getCallback().verbose("%d entries with conflicts" %(len(conflicts)))
    pisiprogress.getCallback().verbose("%d entires in source 1 - but not in 2" %(len(delta1)))
    pisiprogress.getCallback().verbose("%d entires in source 2 - but not in 1" %(len(delta2)))

    # simple stuff first - add the deltas always to the opposite side
    for addID in delta1:
        source[1].addContact(source[0].getContact(addID))
    for addID in delta2:
        source[0].addContact(source[1].getContact(addID))
    
    confDict = {}
    if mergeMode == MERGEMODE_SKIP:
        pass        # leave each side as it is
    elif mergeMode == MERGEMODE_FLUSH_A or mergeMode == MERGEMODE_FLUSH_B:
        pass        # there shouldn't be anything to do here as there can't be any common instances with a flushed repository
    else:
        if mergeMode == MERGEMODE_MANUALCONFIRM:
            confirmDict = _askConfirmation(source,  conflicts)
        for id in conflicts:
            if mergeMode == MERGEMODE_OVERWRITE_A:
                source[0].replaceContact(id,  source[1].getContact(id))
            if mergeMode == MERGEMODE_OVERWRITE_B:
                source[1].replaceContact(id,  source[0].getContact(id))
            if mergeMode == MERGEMODE_MANUALCONFIRM:
                if confirmDict[id] == 'a':
                    source[1].replaceContact(id,  source[0].getContact(id))
                elif confirmDict[id] == 'b':
                    source[0].replaceContact(id,  source[1].getContact(id))
                elif confirmDict[id] == 's':    # skip
                    pass
