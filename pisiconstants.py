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
PISI_COMMENTS = "PISI is synchronizing information"
PISI_VERSION = '0.1.2'
FILEPATH_COPYING = "/opt/pisi/COPYING"
PISI_AUTHORS = ["Esben Damgaard","Michael Pilgermann"]
PISI_HOMEPAGE = "https://projects.openmoko.org/projects/pisi/"
PISI_TRANSLATOR_CREDITS = None
PISI_DOCUMENTERS = ['Michael Pilgermann']

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

GOOGLE_CONTACTS_APPNAME = "pisi0.1"
GOOGLE_CONTACTS_MAXRESULTS = 1000
