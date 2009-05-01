import atom
import gdata.contacts
import gdata.contacts.service
import gdata.calendar
import gdata.calendar.service

def initContacts():
    gd_client = gdata.contacts.service.ContactsService()
    gd_client.email = "kichkasch@web.de"
    gd_client.password = "hd5hainer"
    gd_client.source = 'pisi0.1'
    gd_client.ProgrammaticLogin()


def PrintFeed(feed):
  for i, entry in enumerate(feed.entry):
    print '\n%s %s' % (i+1, entry.title.text)
    if entry.content:
      print '    %s' % (entry.content.text)
    # Display the primary email address for the contact.
    for email in entry.email:
      if email.primary and email.primary == 'true':
        print '    %s' % (email.address)
    # Show the contact groups that this contact is a member of.
    for group in entry.group_membership_info:
      print '    Member of group: %s' % (group.href)
    # Display extended properties.
    for extended_property in entry.extended_property:
      if extended_property.value:
        value = extended_property.value
      else:
        value = extended_property.GetXmlBlobString()
      print '    Extended Property - %s: %s' % (extended_property.name, value)
      
      
#feed = gd_client.GetContactsFeed()
#PrintFeed(feed)

def newContact():
    new_contact = gdata.contacts.ContactEntry(title=atom.Title(text="Christineiusaisis Pilgermann"))
    #new_contact.content = atom.Content(text=notes)
    new_contact.email.append(gdata.contacts.Email(address="christine123@web.de",
        primary='true', rel=gdata.contacts.REL_HOME))
        
    #new_contact.phone_number.append(gdata.contacts.PhoneNumber(text="34567",  rel=gdata.contacts.REL_HOME))

    new_contact.postal_address.append(gdata.contacts.PostalAddress(text="Plueschowstr. 9\n35115 Hannover",  rel=gdata.contacts.REL_HOME))

    contact_entry = gd_client.CreateContact(new_contact)
    print contact_entry.GetEditLink().href

def initCalendar():
    global gd_client
    gd_client = gdata.calendar.service.CalendarService()
    gd_client.email = "kichkasch@gmx.de"
    gd_client.password = "hd5hainer"
    gd_client.source = 'pisi0.1'
    gd_client.ProgrammaticLogin()

def googleCalendarTest():
    import random
    global gd_client
    print "testing google calendar"
    feed = gd_client.GetCalendarEventFeed('/calendar/feeds/kichkasch@gmx.de/private/full?max-results=1000')
    for event in feed.entry:
        print type(event.when[0].start_time)
        try:
            for prop in event.extended_property:
                if prop.name == 'pisiid':
                    print ("%s\n\t%s" %(event.title.text,  prop.value))
            if event.recurrence:
                print event.recurrence.text
        except AttributeError:
            print ("%s\n\t%s" %(event.title.text,  'n.a.'))
#        event.extended_property.append(gdata.calendar.ExtendedProperty(name='pisiid',  value= str(random.randint(0,  100000000000000000000000))))
#        gd_client.UpdateEvent(event.GetEditLink().href, event)
    
initCalendar()
googleCalendarTest()
