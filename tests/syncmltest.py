import sys, os
sys.path.insert(0,os.path.abspath(__file__+"/../.."))


import thirdparty.conduit.SyncmlModule as SyncmlModule

def load():
    if_contacts = SyncmlModule.SyncmlContactsInterface("http://www.mobical.net/sync/server", "kichkasch", "QKUM5V8r", "con", "pisi")
    contacts_raw = if_contacts.downloadContacts()   # load
    if_contacts.finish()

    for x in contacts_raw.keys():
        print "<%s>" %x #,  contacts_raw[x]


def modify():
    if_contacts = SyncmlModule.SyncmlContactsInterface("http://www.mobical.net/sync/server", "kichkasch", "QKUM5V8r", "con", "pisi")
    st = """BEGIN:VCARD
VERSION:3.0
PRODID:-//Tactel AB//NONSGML Mobical//EN
N:Pilgermann;Christian;;;
FN:Christian Pilgermann
TEL;TYPE=:+495117809632
END:VCARD"""
    nr = "1656037892"
  
    st2 = """BEGIN:VCARD
VERSION:3.0
N:Kuschewski;Jan;;;
FN:Jan Pilgermann
TEL;TYPE=:23554646354
END:VCARD"""

    mods = {}
    mods[nr] = st
    dels = {}
#    dels['1656023293'] = ""
    adds = {}
    adds['1'] = st2
    if_contacts.applyChanges(mods = mods, dels = dels,  adds = adds)

    if_contacts.finish()
    
#load()
modify()
