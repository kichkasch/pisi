"""
background information - database schema

root@om-gta02 ~/programming $ sqlite3  /etc/freesmartphone/opim/sqlite-contacts.db 
SQLite version 3.6.5
Enter ".help" for instructions
Enter SQL statements terminated with a ";"
sqlite> .schema
CREATE TABLE contact_values (id INTEGER PRIMARY KEY, contactId INTEGER, Field TEXT, Value TEXT);
CREATE TABLE contacts (
                id INTEGER PRIMARY KEY,
                Name TEXT,
                Surname TEXT,
                Nickname TEXT,
                Birthdate TEXT,
                MarrDate TEXT,
                Partner TEXT,
                Spouse TEXT,
                MetAt TEXT,
                HomeLoc TEXT,
                Department TEXT,
                refid TEXT,
                deleted INTEGER DEFAULT 0);
CREATE INDEX contact_values_contactId_idx ON contact_values (contactId);
CREATE INDEX contacts_Name_idx ON contacts (Name);
CREATE INDEX contacts_Nickname_idx ON contacts (Nickname);
CREATE INDEX contacts_Surname_idx ON contacts (Surname);
CREATE INDEX contacts_id_idx ON contacts (id);
sqlite> root@om-gta02 ~/programming $ 
"""


import dbus, e_dbus
import warnings
warnings.filterwarnings('ignore', '.*')


def testLoad():
    bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
    dbusObject = bus.get_object("org.freesmartphone.opimd", "/org/freesmartphone/PIM/Contacts")
    contacts = dbus.Interface(dbusObject, dbus_interface="org.freesmartphone.PIM.Contacts")

    dict = {'_sortby':'Name'}
    query = contacts.Query(dict) 

    dbusObject = bus.get_object("org.freesmartphone.opimd", query)
    query = dbus.Interface(dbusObject, dbus_interface="org.freesmartphone.PIM.ContactQuery")
    count = query.GetResultCount()
    print count,  " entries in total."
    
    for contact in query.GetMultipleResults(count):
        dbusObject = bus.get_object("org.freesmartphone.opimd", contact.get('Path'))
        contactObject = dbus.Interface(dbusObject, dbus_interface="org.freesmartphone.PIM.Contact")
        
        if contactObject.GetUsedBackends()[0]!= "SQLite-Contacts":
            continue    # let's only go for sqlite entries
        print contactObject.GetContent()
#        print contact.get('Name'),  contact.get('Phone')


        
def testWrite():
    bus = dbus.SystemBus(mainloop = e_dbus.DBusEcoreMainLoop()) 
    dbusObject = bus.get_object("org.freesmartphone.opimd", "/org/freesmartphone/PIM/Contacts")
    contacts = dbus.Interface(dbusObject, dbus_interface="org.freesmartphone.PIM.Contacts")

    contact = {}
    contact['Phone'] = "12345"
    contact['Name'] = "Michael"
    contact['Surname'] = 'Pilgermann'
    contact['Email'] = 'michael.pilgermann@gmx.de'
    path = contacts.Add(contact)

#testWrite()
testLoad()
