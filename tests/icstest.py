import vobject
import datetime

file = open("/home/michael/test.ics",  "r")
    
cal = vobject.readOne(file)
for event in cal.contents['vevent']:
    print event.dtstart.value
    print type(event.dtstart.value)
    print type(event.dtstart.value) == datetime.datetime
    print event.last_modified.value

#    print event.valarm.trigger.value.days * 24 * 60 + event.valarm.trigger.value.seconds / 60,  "minutes"
#    print event.valarm.trigger.value.days ,  event.valarm.trigger.value.seconds,  event.valarm.trigger.value.microseconds
    
    print event.rrule.serialize() + event.dtstart.serialize() + event.dtend.serialize()

file.close()
