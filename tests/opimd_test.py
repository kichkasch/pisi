import dbus, e_dbus

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
        print contact.get('Name'),  contact.get('Phone')
        
def testWrite():
    pass
    
testLoad()
