#!/usr/bin/python

"""
Third party module for access to SIM card

The original has been taken from http://wiki.openmoko.org/wiki/Import_Sim_Contacts - all non-required stuff has been deleted
"""

import sys, os
import tempfile
import re
import subprocess


#RSTR=`+CPBR: (1-250),44,18'
contactSizeRE = re.compile('^RSTR=[^:]*:\s*\(?1-([0-9]+).*$')

#RSTR=`+CPBR: 61,"18005551212",129,"Debbie"'
contactRE = re.compile('^RSTR=[^,]*,\s*"?([^",]*)"?\s*,[^,]*,"?(.*?)"?\'?\s*$')
def getAllContactsFromSim():
    maxSize = 0

    #find out size of contact list

    
    contactSize = subprocess.Popen('echo "AT+CPBR=?" | libgsmd-tool -m atcmd').stdout
    #with os.popen('echo "AT+CPBR=?" | libgsmd-tool -m atcmd') as contactSize:
        
    for contactSizeLine in contactSize.readlines():
        m = contactSizeRE.match(contactSizeLine)
        if m:
            maxSize = int(m.group(1))

    if maxSize == 0: raise "Couldn't figure out total number of contacts in SIM"

    #build file with the AT cmds for getting all contacts out of the SIM
    (ftmp, ftmpname) = tempfile.mkstemp()
    for i in range(1,maxSize + 1):
        os.write(ftmp, "AT+CPBR=%d\n" % i)
    os.close(ftmp)

    #read all contacts from sim
    retval = {}

    contactSize = subprocess.Popen('libgsmd-tool -m atcmd < %s | grep "RSTR=..CPBR"' % ftmpname).stdout
#    with os.popen('libgsmd-tool -m atcmd < %s | grep "RSTR=..CPBR"' % ftmpname) as contacts:
    for contact in contacts.readlines():
        m = contactRE.match(contact)
        if m:
            (phone, name) = (m.group(1), m.group(2))
            if retval.has_key(name):
                retval[name].append(phone)
            else:
                retval[name] = [phone]
        else:
            print "Didn't understand contact " + contact

    os.remove(ftmpname)
    return retval
    

