from evolution import ebook, ecal

print ebook.list_addressbooks()

personal = ebook.open_addressbook('couchdb://1259512302.3613.2@michael-desktop')

for c in personal.get_all_contacts():
    print ("*** %s" %(c.get_name()))
    print ("\t%s, %s" %(c.props.family_name, c.props.given_name))
    print ("\t%s" %(c.props.email_1))
