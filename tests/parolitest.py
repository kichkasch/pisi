#from tichy.service import Service
#contacts_service = Service('Contacts',  "ContactsService")
#contacts_service.init()

def testWrite():
    contact = contacts_service.create(name=str("Michael Pilgermann"),tel=str(12345))
    contacts_service.add(contact)
    
def testLoad():
    pass
    
#testWrite()


import pickle
f = open('phone-parolicontacts.dat','r')
d = pickle.load(f)
print d
