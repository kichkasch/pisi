"""Additional layer to vobject site-package"""

from pisiconstants import *
import vobject
import datetime
from events import events

VCF_PHONETYPE_HOME = ['HOME', 'VOICE']
"""Indentifies a phone entry as home phone"""
VCF_PHONETYPE_WORK = ['WORK', 'VOICE']
"""Indentifies a phone entry as work phone"""
VCF_PHONETYPE_MOBILE = ['CELL', 'VOICE']
"""Indentifies a phone entry as mobile phone"""
VCF_PHONETYPE_FAX = ['FAX']
"""Indentifies a phone entry as fax"""
VCF_ADDRESSTYPE_HOME = ['HOME', 'POSTAL']
"""Indentifies an address entry as home address"""
VCF_ADDRESSTYPE_WORK = ['WORK', 'POSTAL']
"""Indentifies an address entry as work address"""


def _extractAtt(x,  st):
    """
    Supporting function for pulling information out of a attribute
    
    Gets around problems with non available attributes without the need for checking this beforehand for each attribute.
    """
    try:
        ret = None
        exec "ret = " + st
        return ret
    except AttributeError:
        return ''

#
# PART 1: LOADING (Contacts)
#

def extractVcfEntry(x):
    """
    Walks an entire vobject vcard entity and stores all information in a dictionary, which is returned in the end
    
    For mapping the PISI rules are applied.
    """
    atts = {}
    atts['firstname'] = _extractAtt(x, 'x.n.value.given')
    atts['middlename'] = _extractAtt(x, 'x.n.value.additional')
    atts['lastname'] = _extractAtt(x, 'x.n.value.family')
    
    atts['email'] = _extractAtt(x, 'x.email.value')
    atts['title'] = _extractAtt(x, 'x.title.value')

    # phone numbers
    try:
        for tel in x.contents['tel']:
            if not tel.params.has_key('TYPE'):
                atts['mobile'] = tel.value
            elif tel.params['TYPE'] == VCF_PHONETYPE_HOME:
                atts['phone'] = tel.value
            elif tel.params['TYPE'] == VCF_PHONETYPE_MOBILE:
                atts['mobile'] = tel.value
            elif tel.params['TYPE'] == VCF_PHONETYPE_WORK:
                atts['officePhone'] = tel.value
            elif tel.params['TYPE'] == VCF_PHONETYPE_FAX:
                atts['fax'] = tel.value
    except KeyError:
        pass    # no phone number; that's alright

    # addresses
    try:
        for addr in x.contents['adr']:
            if addr.params['TYPE'] == VCF_ADDRESSTYPE_HOME:
                atts['homeStreet'] = addr.value.street
                atts['homeCity'] = addr.value.city
                atts['homeState'] = addr.value.region
                atts['homePostalCode'] = addr.value.code
                atts['homeCountry'] = addr.value.country
            elif addr.params['TYPE'] == VCF_ADDRESSTYPE_WORK:
                atts['businessStreet'] = addr.value.street
                atts['businessCity'] = addr.value.city
                atts['businessState'] = addr.value.region
                atts['businessPostalCode'] = addr.value.code
                atts['businessCountry'] = addr.value.country
    except KeyError:
        pass    # no addresses here; that's fine
    
    try:
        atts['businessOrganisation'] = x.org.value[0]
        atts['businessDepartment'] = x.org.value[1]
    except:
        pass
    return atts

    
    
#
# PART 2: SAVING (Contacts)
#

def _createRawAttribute(c,  j, att,   value,  params = []):
    """
    Supporting function for adding a single attribute to vcard raw object
    """
    try:
        v = None
        if value != None:
            exec ("v =" + value)
            if v != None and v != '':
                j.add(att)
                exec ("j." + att + ".value = " + value)
                for param in params:
                    exec("j." + att + "." + param[0] + "=" + param[1] )
    except KeyError:
        pass    # this attribute is not available; that's not a problem for us
        
def _createNameAttribute(c,  j):
    family = c.attributes['lastname']
    if family == None:
        family = ''
    given = c.attributes['firstname']
    if given == None:
        given = ''
    additional = c.attributes['middlename']
    if additional == None:
        additional = ''
    if family == '' and given == '' and additional == '':
        c.prettyPrint()
    nameEntry = vobject.vcard.Name(family = family,  given = given,  additional = additional)
    n = j.add('n')
    n.value = nameEntry

def _createPhoneAttribute(c,  j,  type):
    """
    Create and append phone entry
    
    Phone entries are a bit tricky - you cannot access each of them directly as they all have the same attribute key (tel). Consequently, we have to access the dictionary for phones directly.
    """
    try:
        if type == VCF_PHONETYPE_HOME:
            value = c.attributes['phone']
        elif type == VCF_PHONETYPE_WORK:
            value = c.attributes['officePhone']
        elif type == VCF_PHONETYPE_MOBILE:
            value = c.attributes['mobile']
        elif type == VCF_PHONETYPE_FAX:
            value = c.attributes['fax']
        if value == '' or value == None:
            return
        tel = j.add('tel')
        tel.value = value
        tel.type_param = type
    except KeyError:
        pass    # that's fine - this phone type is not available
        
def _attFromDict(dict,  att):
    try:
        return dict[att]
    except KeyError:
        return  ''

def _createAddressAttribute(c,  j,  type):
    """
    Create and append address entry
    
    Entry is only created if city is set.
    """        
    if type == VCF_ADDRESSTYPE_HOME:
        street = _attFromDict(c.attributes,  'homeStreet')
        postalCode = _attFromDict(c.attributes,  'homePostalCode')
        city = _attFromDict(c.attributes,  'homeCity')
        country = _attFromDict(c.attributes,  'homeCountry')
        state = _attFromDict(c.attributes,  'homeState')
    elif type == VCF_ADDRESSTYPE_WORK:
        street = _attFromDict(c.attributes,  'businessStreet')
        postalCode = _attFromDict(c.attributes,  'businessPostalCode')
        city = _attFromDict(c.attributes,  'businessCity')
        country = _attFromDict(c.attributes,  'businessCountry')
        state = _attFromDict(c.attributes,  'businessState')
    if city == None or city == '':
        return
    addr = j.add('adr')
    addr.value = vobject.vcard.Address(street = street,  code = postalCode,  city = city,  country = country,  region = state)
    addr.type_param = type

def _createBusinessDetails(c,  j):
    """
    Creates an entry for business organzation und unit.
    """
    if c.attributes.has_key('businessOrganisation'):
        o = c.attributes['businessOrganisation']
        if o == None or o == '':
            return
        list = []
        list.append(o)
        if c.attributes.has_key('businessDepartment'):
            ou = c.attributes['businessDepartment']
            if ou != None and ou != '':
                list.append(ou)
        j.add('org')
        j.org.value = list

def createRawVcard(c):
    """
    Converts internal contact entry to VObject format
    """
    j = vobject.vCard()
    _createNameAttribute(c, j)
    
    if c.attributes['firstname']:
        if c.attributes['lastname']:
            fn = c.attributes['firstname'] + ' ' +  c.attributes['lastname']
        else:
            fn = c.attributes['firstname']
    else:
        fn = c.attributes['lastname']
    _createRawAttribute(c,  j,  'fn',  "'''" + fn + "'''")
    _createRawAttribute(c,  j,  'title',  "c.attributes['title']")

    _createRawAttribute(c,  j,  'email',  "c.attributes['email']",  [['type_param',  "'INTERNET'"]])
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_HOME)
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_WORK)
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_MOBILE)
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_FAX)
    
    _createAddressAttribute(c,  j, VCF_ADDRESSTYPE_HOME)
    _createAddressAttribute(c,  j, VCF_ADDRESSTYPE_WORK)
    _createBusinessDetails(c,  j)
    return j





#
# PART 3: LOADING (Calendar)
#
def _extractRecurrence(x,  allDay):
    """
    Transforms VObject recurrence information into PISI internal object L{events.Recurrence}
    """
    if _extractAtt(x, 'x.dtend.value'):
        end = x.dtend
    else:
        end = None
    rec = events.Recurrence()
    rec.initFromAttributes(x.rrule,  x.dtstart,  end,  allDay)
    return rec

def extractICSEntry(x):
    print x, "\n"
    atts = {}
    atts['start'] = _extractAtt(x, 'x.dtstart.value')
    atts['end'] = _extractAtt(x, 'x.dtend.value')
    if type(x.dtstart.value) ==datetime.date:
        atts['allday'] = True
    else:
        atts['allday'] = False
        # For all stupid ICS files coming without timezone information
#        print atts['start'].tzinfo()
        if type (atts['start']) == unicode:
            print type(vobject.icalendar.DateOrDateTimeBehavior.transformToNative(atts['start']).value)
        
        if atts['start'].tzinfo == None:
            atts['start'] = atts['start'].replace(tzinfo = events.UTC())
        if atts['end'].tzinfo == None:
            atts['end'] = atts['end'].replace(tzinfo = events.UTC())
    atts['title'] = _extractAtt(x, 'x.summary.value')
    atts['description'] = _extractAtt(x, 'x.description.value')
    atts['location'] = _extractAtt(x, 'x.location.value')
    try:
        atts['alarmmin'] = x.valarm.trigger.value.days * 24 * 60 + x.valarm.trigger.value.seconds / 60
        atts['alarm'] = True
    except AttributeError:
        atts['alarm'] = False
        atts['alarmmin'] = 0
        
    try:
        atts['recurrence'] = _extractRecurrence(x, atts['allday'] )
    except AttributeError:
        atts['recurrence'] = None
    updated = _extractAtt(x, 'x.last_modified.value')
    
    if x.contents.has_key('x-pisi-id'):
        globalId = x.contents['x-pisi-id'][0].value
    else:
        globalId = None
        
    return atts,  globalId, updated


#
# PART 4: SAVING (Calendar)
#

