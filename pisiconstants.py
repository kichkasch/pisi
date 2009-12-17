""" 
Module for definition of shared constants between the modules.

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

PISI_NAME = 'PISI'
"""'About'-information for user - program name"""
PISI_COMMENTS = "PISI is synchronizing information"
"""'About'-information for user - comments / explainations"""
PISI_VERSION = '0.4.7' #'-svn-' # 
"""'About'-information for user - current version"""
FILEPATH_COPYING = "/opt/pisi/COPYING"
"""'About'-information for user - where to find the 'licence' file"""
PISI_AUTHORS = ["Esben Damgaard","Michael Pilgermann"]
"""'About'-information for user - list of programmers"""
PISI_HOMEPAGE = "https://projects.openmoko.org/projects/pisi/"
"""'About'-information for user - program home page"""
PISI_TRANSLATOR_CREDITS = None
"""'About'-information for user - list of translators"""
PISI_DOCUMENTERS = ['Michael Pilgermann']
"""'About'-information for user - list of documenters"""

CONSOLE_PROGRESSBAR_WIDTH = 80
"""Length of progress bar in CLI mode"""

MODE_CALENDAR = 0
"""Type of sources to deal with are calendars"""
MODE_CONTACTS = 1
"""Type of sources to deal with are contacts"""
MODE_STRINGS = ['calendar',  'contacts']
"""Names for the types of sources in order"""

MERGEMODE_SKIP = 0
"""Resolve conflicts between two entries from two sources by skipping the entry"""
MERGEMODE_FLUSH_A = 1
"""Resolve conflicts between two entries from two sources by flushing the entire data repository for the first data source"""
MERGEMODE_FLUSH_B = 2
"""Resolve conflicts between two entries from two sources by flushing the entire data repository for the second data source"""
MERGEMODE_OVERWRITE_A = 3
"""Resolve conflicts between two entries from two sources by overwriting the single entry on the first data source"""
MERGEMODE_OVERWRITE_B = 4
"""Resolve conflicts between two entries from two sources by overwriting the single entry on the second data source"""
MERGEMODE_MANUALCONFIRM = 5
"""Resolve conflicts between two entries from two sources by asking the user for decision for every single entry"""
MERGEMODE_STRINGS = ["Skip",  "Flush source 1",  "Flush source 2",  "Overwrite entry in source 1",  "Overwrite entry in source 2",  "Manual confirmation"]
"""Names of merge modes in order"""

ACTIONID_ADD = 0
"""Entry in the history of activities for synchronization modules - here for ADD"""
ACTIONID_DELETE = 1
"""Entry in the history of activities for synchronization modules - here for DELETE"""
ACTIONID_MODIFY = 2
"""Entry in the history of activities for synchronization modules - here for MODIFY"""

GOOGLE_CONTACTS_APPNAME = "pisi" + PISI_VERSION
"""application name to use for connecting against google contacts services"""
GOOGLE_CONTACTS_MAXRESULTS = 1000
"""upper limit of result set when querying google contacts api"""
GOOGLE_CALENDAR_APPNAME = "pisi" + PISI_VERSION
"""application name to use for connecting against google calendar services"""
GOOGLE_CALENDAR_MAXRESULTS = GOOGLE_CONTACTS_MAXRESULTS
"""upper limit of result set when querying google calendar api"""

FILEDOWNLOAD_TIMEOUT = 10
"""Timeout for socket opeations (e.g. http download) in seconds - None for disable"""
FILEDOWNLOAD_TMPFILE = "/tmp/pisi-remotebuffer.data"
"""Temporary file for buffering information from remote file sources"""

VCF_BYTES_PER_ENTRY = 200
"""For guessing the number of entries inside a VCF file by evaluating its size we need an estimation of the size for a single entry - for the purpose of showing some progress"""
ICS_BYTES_PER_ENTRY = 200
"""For guessing the number of entries inside an ICS file by evaluating its size we need an estimation of the size for a single entry - for the purpose of showing some progress"""
