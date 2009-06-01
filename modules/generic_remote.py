"""
Abstract class for providing remote features (download, upload) for file based modules

This file is part of Pisi.

Only HTTP (Webdav) is supported.

Urllib2 (read, D{http://www.python.org/doc/2.5/lib/module-urllib2.html}) and Pythonwebdavlib (write, D{http://sourceforge.net/projects/pythonwebdavlib} are used for implementation. 

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

import socket
import urllib2
import webdav.WebdavClient
import os
from pisiconstants import *

class RemoteRessourceHandler:
    """
    Generic class for handling remote resources.
    
    Your specific class (a handler for a certain PIM type) should inherit from this class and just use upload and download methods.
    """
    
    def __init__(self, url, remoteFilename, localFilename = FILEDOWNLOAD_TMPFILE, username = None,  password = None):
        """
        Constructor
        
        Initializes instance variables.
        """
        self._url = url
        self._remoteFilename = remoteFilename
        self._localFile = localFilename
        self._user = username
        self._password = password
        
        self._completeUrl = self._url + self._remoteFilename
        socket.setdefaulttimeout(FILEDOWNLOAD_TIMEOUT)
        
    def download(self):
        """
        Downloads remote file and overwrites local file
        """
        if self._user and self._password:
            passman = urllib2.HTTPPasswordMgrWithDefaultRealm()
            passman.add_password(None, self._url, self._user, self._password)
            authhandler = urllib2.HTTPBasicAuthHandler(passman)
            opener = urllib2.build_opener(authhandler)
            response = opener.open(self._completeUrl)
        else:
            response = urllib2.urlopen(self._completeUrl)
        data = response.read()
        file = open(self._localFile,  'w')
        file.write(data)
        file.close()
        
    def upload(self):
        """
        Uploads local file and overwrites remote file
        """
        c = webdav.WebdavClient.CollectionStorer(self._url, None)
        c.connection.addBasicAuthorization(self._user, self._password) 
        child= c.addResource(self._remoteFilename)
        f = open(self._localFile, "r") 
        child.uploadFile(f) 
        f.close() 
        
    def cleanup(self):
        """
        Remove traces
        """
        try:
            os.remove(self._localFile)
        except BaseException:
            pass
            
