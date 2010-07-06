"""Additional layer to vobject site-package"""

from pisiconstants import *
import vobject
import datetime
from events import events

"""Indentifies a phone entry as home phone"""
VCF_PHONETYPE_HOME = [['HOME', 'VOICE'], ['VOICE', 'HOME'], ['HOME']]
"""Indentifies a phone entry as work phone"""
VCF_PHONETYPE_WORK = [['WORK', 'VOICE'], ['VOICE', 'WORK'], ['WORK']]
"""Indentifies a phone entry as mobile phone"""
VCF_PHONETYPE_MOBILE = [['CELL', 'VOICE'], ['VOICE', 'CELL'], ['CELL'], ['VOICE']]
"""Indentifies a phone entry as fax"""
VCF_PHONETYPE_FAX = [['FAX']]
"""Entries to remove before comparing"""
VCF_PHONETYPE_IGNORELIST = ['OTHER', 'PREF']
"""Indentifies a phone entry as home phone (older VCF versions; no attribute values)"""
VCF_PHONETYPE_HOME_SINGLETON = 'HOME'
"""Indentifies a phone entry as home phone (older VCF versions; no attribute values)"""
VCF_PHONETYPE_MOBILE_SINGLETON = 'CELL'
"""Indentifies a phone entry as home phone (older VCF versions; no attribute values)"""
VCF_PHONETYPE_WORK_SINGLETON = 'WORK'
"""Indentifies a phone entry as fax (older VCF versions; no attribute values)"""
VCF_PHONETYPE_FAX_SINGLETON = 'FAX'

"""Indentifies an address entry as home address"""
VCF_ADDRESSTYPE_HOME = [['HOME', 'POSTAL'], ['POSTAL', 'HOME'], ['HOME']]
"""Indentifies an address entry as work address"""
VCF_ADDRESSTYPE_WORK = [['WORK', 'POSTAL'], ['POSTAL', 'WORK'], ['WORK']]
"""Identifies an address entry as home address (older VCF versions; no attribute values)"""
VCF_ADDRESSTYPE_HOME_SINGLETON = 'HOME'
"""Identifies an address entry as work address (older VCF versions; no attribute values)"""
VCF_ADDRESSTYPE_WORK_SINGLETON = 'WORK'

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

def extractVcfEntry(x, defaultPhonetype = None):
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
            isHome = False
            isWork = False
            isMobile = False
            isFax = False
            if tel.params.has_key('TYPE'):         
                for i in range(len(tel.params['TYPE'])):
                    tel.params['TYPE'][i] = tel.params['TYPE'][i].upper()
                for ign in VCF_PHONETYPE_IGNORELIST:
                    try:
                        del tel.params['TYPE'][tel.params['TYPE'].index(ign)]
                    except ValueError:
                        pass    # fine - this ignore value is not in the list
                if tel.params['TYPE'] in VCF_PHONETYPE_HOME:
                    isHome = True
                elif tel.params['TYPE'] in VCF_PHONETYPE_MOBILE:
                    isMobile = True
                elif tel.params['TYPE'] in VCF_PHONETYPE_WORK:
                    isWork = True
                elif tel.params['TYPE'] in VCF_PHONETYPE_FAX:
                    isFax = True
            elif VCF_PHONETYPE_MOBILE_SINGLETON in tel.singletonparams:
                isMobile = True
            elif VCF_PHONETYPE_HOME_SINGLETON in tel.singletonparams:
                isHome = True
            elif VCF_PHONETYPE_WORK_SINGLETON in tel.singletonparams:
                isWork = True
            elif VCF_PHONETYPE_FAX_SINGLETON in tel.singletonparams:
                isFax = True
            elif defaultPhonetype:
                atts[defaultPhonetype] = tel.value

            if isHome:
                atts['phone'] = tel.value
            elif isMobile:
                atts['mobile'] = tel.value
            elif isWork:
                atts['officePhone'] = tel.value
            elif isFax:
                atts['fax'] = tel.value
    except KeyError:
        pass    # no phone number; that's alright

    # addresses
    try:
        for addr in x.contents['adr']:
            isHome = False
            isWork = False
            if addr.params.has_key('TYPE'):
                for i in range(len(addr.params['TYPE'])):
                    addr.params['TYPE'][i] = addr.params['TYPE'][i].upper()
                if addr.params['TYPE'] in VCF_ADDRESSTYPE_HOME:
                    isHome = True
                elif addr.params['TYPE'] in VCF_ADDRESSTYPE_WORK:
                    isWork = True
            elif VCF_ADDRESSTYPE_HOME_SINGLETON in addr.singletonparams:
                isHome = True
            elif VCF_ADDRESSTYPE_WORK_SINGLETON in addr.singletonparams:
                isWork = True
            if isHome:
                atts['homeStreet'] = addr.value.street
                atts['homeCity'] = addr.value.city
                atts['homeState'] = addr.value.region
                atts['homePostalCode'] = addr.value.code
                atts['homeCountry'] = addr.value.country
            elif isWork:
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
        if type in VCF_PHONETYPE_HOME:
            value = c.attributes['phone']
        elif type in VCF_PHONETYPE_WORK:
            value = c.attributes['officePhone']
        elif type in VCF_PHONETYPE_MOBILE:
            value = c.attributes['mobile']
        elif type in VCF_PHONETYPE_FAX:
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
    if type in VCF_ADDRESSTYPE_HOME:
        street = _attFromDict(c.attributes,  'homeStreet')
        postalCode = _attFromDict(c.attributes,  'homePostalCode')
        city = _attFromDict(c.attributes,  'homeCity')
        country = _attFromDict(c.attributes,  'homeCountry')
        state = _attFromDict(c.attributes,  'homeState')
    elif type in VCF_ADDRESSTYPE_WORK:
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
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_HOME[0])
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_WORK[0])
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_MOBILE[0])
    _createPhoneAttribute(c, j,  VCF_PHONETYPE_FAX[0])
    
    _createAddressAttribute(c,  j, VCF_ADDRESSTYPE_HOME[0])
    _createAddressAttribute(c,  j, VCF_ADDRESSTYPE_WORK[0])
    _createBusinessDetails(c,  j)
    return j

def checkForMandatoryFields(entries):
    """
    Checks each entry, whether all mandatory fields are available.
    
    Current implementation only chechs for Full Name - if not available it will try to assemble something from first and last name.
    """
    for x in entries.keys():
        v = entries[x]

        try:
            v.fn
        except AttributeError:
            firstname = _extractAtt(v, 'x.n.value.given')
            lastname = _extractAtt(v, 'x.n.value.family')

            if firstname:
                if lastname:
                    fn =firstname + ' ' +  lastname
                else:
                    fn = firstname
            else:
                fn = lastname
            _createRawAttribute(None,  v,  'fn',  "'''" + fn + "'''")
            
            
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
    atts = {}
    atts['start'] = _extractAtt(x, 'x.dtstart.value')
    atts['end'] = _extractAtt(x, 'x.dtend.value')
    if type(x.dtstart.value) ==datetime.date:
        atts['allday'] = True
    else:
        atts['allday'] = False
        # For all stupid ICS files coming without timezone information

        # start even more stupid
        # some funny date entries within ics files cannot be parsed by vobject
        # I realized that with Mobical Syncml for instance
        if type (atts['start']) == unicode:
            if atts['start'].endswith('Z'):
                atts['start'] = datetime.datetime.strptime(atts['start'], "%Y%m%dT%H%M%SZ")
            else:
                atts['start'] = datetime.datetime.strptime(atts['start'], "%Y%m%dT%H%M%S")
        if type (atts['end']) == unicode:
            if atts['end'].endswith('Z'):
                atts['end'] = datetime.datetime.strptime(atts['end'], "%Y%m%dT%H%M%SZ")
            else:
                atts['end'] = datetime.datetime.strptime(atts['end'], "%Y%m%dT%H%M%S")
        # end even more stupid

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

def _createRecurrencePart(c,  cal):
    """
    Transforms PISI internal recurrence information (L{events.Recurrence}) into vobject representation
    """
    if c.attributes['recurrence']:
        rec = c.attributes['recurrence']
        cal.add('rrule')
        cal.rrule = rec.getRRule()
        
def _createAlarmPart(c, cal):
    """
    Transforms PISI internal alarm information (1 single integer for minutes) into vobject representation
    """
    if c.attributes['alarm']:
        mins = c.attributes['alarmmin']
        days = mins / (24 * 60)
        seconds = (mins - days*(24*60)) * 60
        cal.add("valarm")
        cal.valarm.add("trigger")
        cal.valarm.trigger.value=datetime.timedelta(days,seconds)

def createRawEventEntry(c, stupidMode = False):
    """
    Transforms PISI internal Calendar event information (L{events.Event}) into vobject representation
    """
    frame = vobject.iCalendar()
    frame.add('vevent')
    cal = frame.vevent
    cal.add('dtstart')
    if c.attributes['allday']:
        if type(c.attributes['start']) == datetime.datetime:
            c.attributes['start'] = c.attributes['start'].date()
        if type(c.attributes['end']) == datetime.datetime:
            c.attributes['end'] = c.attributes['end'].date()
    cal.dtstart.value = c.attributes['start']   # all day is applied automatically due to datetime.datetime or datetime.date class
    cal.add('dtend')
    cal.dtend.value = c.attributes['end']
    if c.attributes['title']:
        cal.add('summary')
        cal.summary.value = c.attributes['title']
    if c.attributes['description']:
        cal.add('description')
        cal.description.value = c.attributes['description']
    if c.attributes['location']:
        cal.add('location')
        cal.location.value = c.attributes['location']
    cal.add('x-pisi-id')
    cal.contents['x-pisi-id'][0].value = c.attributes['globalid']
    _createRecurrencePart(c,  cal)
    _createAlarmPart(c, cal)
    cal.add('last-modified')
    cal.last_modified.value = datetime.datetime.now(events.UTC())
    return cal
