from tichy.service import Service
contacts_service = Service('Contacts',  "ContactsService")
contacts_service.init()

def testWrite():
    contact = contacts_service.create(name=str("Michael Pilgermann"),tel=str(12345))
    contacts_service.add(contact)
    
def testLoad():
    pass
    
testWrite()
