"""
Syncronize with a remote VCF file

This file is part of Pisi.

This module is based on contacts_vcf and generic_remote and is only pulling functionality from these two modules together.

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

import sys,  os
# Allows us to import other modules
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from modules import generic_remote,  contacts_vcf
from pisiconstants import *
import pisiprogress
import urllib2

class SynchronizationModule(contacts_vcf.SynchronizationModule, generic_remote.RemoteRessourceHandler):
    """
    The implementation of the interface L{events.AbstractCalendarSynchronizationModule} for the VCF remote backend
    """
    
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Local variables are initialized.
        The settings from the configuration file are loaded.
        Super class constructors are called.
        """
        self._url = config.get(configsection,'url')
        self._file = config.get(configsection,'file')
        self._username = config.get(configsection,'username')
        self._password = config.get(configsection,'password')
        config.set(configsection, 'vcfpath', FILEDOWNLOAD_TMPFILE) # for constructor of superclass
        pisiprogress.getCallback().verbose('remote vcf-module using server %s' % (self._url))
        contacts_vcf.SynchronizationModule.__init__(self,  modulesString,  config,  configsection,  folder, verbose,  soft)
        generic_remote.RemoteRessourceHandler.__init__(self, self._url, self._file, FILEDOWNLOAD_TMPFILE, self._username, self._password)

    def load(self):
        """
        The file is downloaded from the webserver and then passed on to the (local) vcf module for parsing
        """
        try:
            self.download()
        except urllib2.HTTPError,  e:
            raise IOError("Problems when downloading remote VCF file.\nFor ressource <%s> error code %d was returned." %(e.url, e.code))
        contacts_vcf.SynchronizationModule.load(self)
        self.cleanup()
        
    def saveModifications(self):
        """
        Modifications are applied by local VCF module - the new file is uploaded to the original location.
        """
        pisiprogress.getCallback().verbose("Remote VCF module: I apply %d changes now" %(len(self._history)))
        if len(self._history) == 0:
            return      # don't touch anything if there haven't been any changes
            
        contacts_vcf.SynchronizationModule.saveModifications(self)
        self.upload()
        self.cleanup()
