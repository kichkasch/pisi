"""
Synchronize with local VCF file

This file is part of Pisi.

VCF support is based on the VOBJECT library by skyhouseconsulting (U{http://vobject.skyhouseconsulting.com/}).
Consequently, the vobject site-package has to be installed for utilizing vcard support in PISI.

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

import sys,os,datetime
# Allows us to import event
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from contacts import contacts
import vobject
import os.path
import os
from pisiconstants import *
import pisiprogress
from vobjecttools import *

PATH_INTERACTIVE = "@interactive"
"""Option in configuration file for supplying filename and path of VCF file interactively"""


class SynchronizationModule(contacts.AbstractContactSynchronizationModule):
    """
    The implementation of the interface L{contacts.AbstractContactSynchronizationModule} for VCF file persistence backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded.
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "VCF")
        self._vcfpath = config.get(configsection,'vcfpath')
        self._folder = folder
        pisiprogress.getCallback().verbose("contact VCF module loaded using file %s" %(self._vcfpath))
        self._rawData = {}

    def _promptFilename(self,  prompt, default = None,  description = None):
        """
        Asks for user input on console
        """
        if description:
            pisiprogress.getCallback().message(description)
        return pisiprogress.getCallback().promptFilename(prompt,  default)

    def _guessAmount(self):
        """
        Try to determine roughly how many entries are in this file (we can't know prior to parsing; but we have a guess using the file size)
        """
        info = os.stat(self._vcfpath)
        return info.st_size / VCF_BYTES_PER_ENTRY

    def load(self):
        """
        Load all data from local VCF file
        
        File opened and the entries are parsed. For each entry a L{contacts.contacts.Contact} instance is created and stored in the instance dictionary
        L{contacts.AbstractContactSynchronizationModule._allContacts}.
        """
        pisiprogress.getCallback().verbose ("VCF: Loading")
        if self._vcfpath == PATH_INTERACTIVE:
            self._vcfpath = self._promptFilename("\tPath to VCF file ", "pisi_export.vcf", "You configured PISI VCF support to ask for VCF file name when running.")
        
        file = None
        try:
            file = open(self._vcfpath,  "r")
        except IOError,  e:
            pisiprogress.getCallback().error("--> Error: Could not load VCF file - we still carry on with processing:\n\t%s" %(e))
            return
        
        pisiprogress.getCallback().progress.push(0, 100)
        comps = vobject.readComponents(file)
        pisiprogress.getCallback().progress.setProgress(20) 
        pisiprogress.getCallback().update("Loading")
        amount = self._guessAmount()
        i = 0
        for x in comps:
            atts = extractVcfEntry(x)

            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c
            self._rawData[id] = x
            if i < amount:
                i += 1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / amount))
            pisiprogress.getCallback().update('Loading')
            
        file.close()
        pisiprogress.getCallback().progress.drop()

    
    def saveModifications( self ):
        """
        Save whatever changes have come by
        
        We first make a backup of the old file. Then, the entire set of information is dumped into a new file. (I hope, you don't mind the order of your entries).
        Thereby, we shouldn't create entries from the scratch when they were not changed in the meantime (in the likely case of PISI not supporting all fields
        within the VCF format and file).
        """
        pisiprogress.getCallback().verbose("VCF module: I apply %d changes now" %(len(self._history)))

        if len(self._history) == 0:
            return      # don't touch anything if there haven't been any changes
            
        # rename old file         
        try:
            bakFilename = os.path.join(self._folder,  os.path.basename(self._vcfpath))
            os.rename(self._vcfpath,  bakFilename)
        except OSError,  e:
            pisiprogress.getCallback().verbose("\tError when backing up old VCF file - we still carry on with processing:\n\t%s" %(e))
        
        # there is no unique key for contacts at all in VCF files; we have to use our global keys (name + given name)

        file = open(self._vcfpath,  "w")
        
        i = 0
        for actionItem in self._history:
            action = actionItem[0]
            contactID = actionItem[1]
            if action == ACTIONID_DELETE:
                del self._rawData[contactID]
                pisiprogress.getCallback().verbose("\t\t<vcf> deleting %s" %(contactID))
            elif action == ACTIONID_ADD or action == ACTIONID_MODIFY:
                c = self.getContact(contactID)
                self._rawData[contactID] = createRawVcard(c)
                pisiprogress.getCallback().verbose("\t\t<vcf> adding or replacing %s" %(contactID))                
            i+=1
            pisiprogress.getCallback().progress.setProgress(i * 70 / len(self._history))
            pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().progress.setProgress(70)
        pisiprogress.getCallback().update('Storing')

        pisiprogress.getCallback().verbose("\tVCF: Writing through file")
        for x in self._rawData.values():
            file.write(x.serialize())
            file.write("\n")
        pisiprogress.getCallback().verbose("\tNew VCF file saved to %s; \n\tbackup file is located in %s." %(self._vcfpath,  bakFilename))
        file.close()
