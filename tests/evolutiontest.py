

def tryLibWay():
    from evolution import ebook, ecal

    print ebook.list_addressbooks()

    personal = ebook.open_addressbook('default')

    for c in personal.get_all_contacts():
        print ("*** %s" %(c.get_name()))
        print ("\t%s, %s" %(c.props.family_name, c.props.given_name))
        print ("\t%s" %(c.props.email_1))

import random
def _generateEDS_ID():
    """
    IDs from EDS look like being a 16 digit Hex String
    """
    st = ""
    for i in range (16):
        k = random.randint(0, 15)
        if k > 9:
            st += chr(k + 55)
        else:
            st += str(k)
    return 'pas-id-' + st



def tryDodgyWay():
    import bsddb
    import vobject  
    file = bsddb.hashopen("/home/michael/.evolution/addressbook/local/system/addressbook.db")
    rem = None
    print len(file.keys())
    for key in file.keys():
        data = file[key]
        print "\n\n", data
        if not data.startswith('BEGIN:VCARD'):
            continue
        
        comps = vobject.readComponents(data[:len(data)-1])
        for x in comps:
#            print x.n.value.given, key, ":"
            print x
            if x.n.value.given == "Juliane":
                rem = [key, data, x]
            
#            # test modify
#                x.n.value.given = "KichKasch"
#        
#        file[rem[0]] = rem[2].serialize()

#    # test delete
#    if rem:
#        print "Deleting ", rem[0]
#        del file[rem[0]]
            
            
#    #test add
#    import vobject
#    j = vobject.vCard()
#    nameEntry = vobject.vcard.Name(family = "Gust",  given = "Juliane",  additional = "")
#    n = j.add('n')
#    n.value = nameEntry
#    fn = j.add('fn')
#    fn.value = "Juliane Gust"
#    email = j.add('email')
#    email.value="juliane.gust@gmx.de"
#    email.type_param = "HOME"  
#    
#    id = _generateEDS_ID()
#    jid = j.add('uid')
#    jid.value = id
#    
#    print "adding ", id, "\n", j.serialize()
#    file[id] = j.serialize()
            
#    # del all
#    for x in file.keys():
#        del file[x]
            
            
    print "Committing ..."
    file.sync() # commit
        
tryDodgyWay()
