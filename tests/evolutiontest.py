

def tryLibWay():
    from evolution import ebook, ecal

    print ebook.list_addressbooks()

    personal = ebook.open_addressbook('default')

    for c in personal.get_all_contacts():
        print ("*** %s" %(c.get_name()))
        print ("\t%s, %s" %(c.props.family_name, c.props.given_name))
        print ("\t%s" %(c.props.email_1))


# this program helped

def tryDodgyWay():
    import bsddb
    import vobject  
    file = bsddb.hashopen("/home/michael/.evolution/addressbook/local/system/addressbook.db")
    rem = None
    print len(file.keys())
    for key in file.keys():
        data = file[key]
        if not data.startswith('BEGIN:VCARD'):
            continue
        
        comps = vobject.readComponents(data[:len(data)-1])
        for x in comps:
            print x.n.value.given
#            if x.n.value.given == "Michael":
#                rem = [key, data, x]
#                x.n.value.given = "KichKasch"
#
#        
#        file[rem[0]] = rem[2].serialize()
#        file.sync()
        
tryDodgyWay()
