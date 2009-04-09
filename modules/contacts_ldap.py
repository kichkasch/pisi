#!/usr/bin/env python

""" 
Synchronize with a LDAP

It is assumed, that you are using the "mozillaAbPersonAlpha" schema for your LDAP. Otherwise, the mapping wouldn't work as the attributes are required.

The LDAP Python site package python-ldap (http://python-ldap.sourceforge.net/) is required for this module.
Before installing the site package, the LDAP libraries (http://www.openldap.org/) must be available on the machine.
I couldn't find any pre-compiled package of either of the two - so I had to compile and install everything myself (what a mess). I found the following sources helpful:
 - http://wiki.openmoko.org/wiki/Toolchain
 - http://www.open-moko.de/die-software-anwendungen-f6/libsdl-und-crosscompiler-t25.html (in German)
Hopefully, in near future an LDAP as well as a Python-LDAP ipkg will be available.

Special characters (such as umlauts) seem to result in an error being thrown. This is due to some unicode encoding problem.
ToDo: Resolv this issue!

Please note, that currently, only read access to LDAP is implemented.

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

import os.path
import sys,os,re
import ldap

# Allows us to import contact
sys.path.insert(0,os.path.abspath(__file__+"/../.."))
from contacts import contacts
import pisiprogress

class SynchronizationModule(contacts.AbstractContactSynchronizationModule):
    """
    The implementation of the interface L{contacts.AbstractContactSynchronizationModule} for the LDAP backend
    """
    def __init__( self, modulesString, config, configsection, folder, verbose=False, soft=False):
        """
        Constructor
        
        Super class constructor (L{contacts.AbstractContactSynchronizationModule.__init__}) is called.
        Local variables are initialized.
        The settings from the configuration file are loaded. 
        """
        contacts.AbstractContactSynchronizationModule.__init__(self,  verbose,  soft,  modulesString,  config,  configsection,  "LDAP")
        self._ldapHost = config.get(configsection,'ldapHost')
        self._ldapDomain = config.get(configsection,'ldapDomain')
        self._ldapFilter = config.get(configsection,'ldapFilter')
        self._ldapUser = config.get(configsection,'ldapUser')
        self._ldapPassword = config.get(configsection,'ldapPassword')
        pisiprogress.getCallback().verbose('contact ldap module loaded using host %s' % (self._ldapHost))

    def _extractAtt(self,  contactEntry,  key):
        """
        Supporting method for loading content from the LDAP
        
        Catches possible exceptions and takes care of proper (unicode) encoding.
        """
        try:
            r = contactEntry[key][0].decode("utf-8")
            return r
        except KeyError:
            return ""

    def load(self):
        """
        Loads all attributes for all contact items from LDAP repository
        
        For each entry a new L{contacts.contacts.Contact} instance is created and stored in the instance dictionary L{contacts.AbstractContactSynchronizationModule._allContacts}.
        """
        pisiprogress.getCallback().verbose("LDAP: Loading")
        l = ldap.initialize("ldap://" + self._ldapHost)
        l.simple_bind_s(self._ldapUser,self._ldapPassword)
        res = l.search_s(self._ldapDomain, ldap.SCOPE_SUBTREE, self._ldapFilter)
        l.unbind()
        pisiprogress.getCallback().progress.setProgress(20)     # we guess that the actual query took up 20 % of the time - the remaining 80 % are taken by parsing the content ...
        pisiprogress.getCallback().update('Loading')
        i=0
        for cn,  contactEntry in res:
            atts = {}
            
            atts['firstname'] = self._extractAtt(contactEntry, "givenName")
            atts['middlename'] = self._extractAtt(contactEntry, "mozillaNickname")
            atts['lastname'] = self._extractAtt(contactEntry,"sn")
            atts['title'] = self._extractAtt(contactEntry,"title")
            
            atts['email'] = self._extractAtt(contactEntry,"mail")
            atts['mobile'] = self._extractAtt(contactEntry,"mobile")
            atts['phone'] = self._extractAtt(contactEntry,"homePhone")  
            atts['officePhone'] = self._extractAtt(contactEntry,"telephoneNumber")
            atts['fax'] = self._extractAtt(contactEntry,"facsimileTelephoneNumber")

            atts['homeStreet'] = self._extractAtt(contactEntry,  "mozillaHomeStreet")
            atts['homePostalCode'] = self._extractAtt(contactEntry,  "mozillaHomePostalCode")   
            atts['homeCity'] = self._extractAtt(contactEntry,  "mozillaHomeLocalityName") 
            atts['homeCountry'] = self._extractAtt(contactEntry,  "mozillaHomeCountryName")   
            atts['homeState'] = self._extractAtt(contactEntry,  "mozillaHomeState") 

            atts['businessOrganisation'] = self._extractAtt(contactEntry,  "o")
            atts['businessDepartment'] = self._extractAtt(contactEntry,  "ou")
            atts['businessPostalCode'] = self._extractAtt(contactEntry,  "postalCode")
            atts['businessStreet'] = self._extractAtt(contactEntry,  "street")
            atts['businessCity'] = self._extractAtt(contactEntry,  "l")
            atts['businessCountry'] = self._extractAtt(contactEntry,  "c")
            atts['businessState'] = self._extractAtt(contactEntry,  "st")

            id = contacts.assembleID(atts)
            c = contacts.Contact(id,  atts)
            self._allContacts[id] = c            
            i+=1
            pisiprogress.getCallback().progress.setProgress(20 + ((i*80) / len(res)))
            pisiprogress.getCallback().update('Loading')

    def saveModifications( self ):
        """
        Stub: To save all changes that have come by
        
        Saving for LDAP is not yet implemented. This function only raIses an exception (L{ValueError}), informing about this status of implementation.
        """
        pisiprogress.getCallback().verbose("LDAP module: I would apply %d changes now" %(len(self._history)))
        if len(self._history) == 0:
            return      # don't touch anything if there haven't been any changes

        raise ValueError("LDAP module not (yet) writable!")
        
