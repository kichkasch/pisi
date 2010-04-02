"""
Collection of tools for PISI

This file is part of Pisi.

Pisi is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Pisi is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Pisi.  If not, see <http://www.gnu.org/licenses/>.
"""
import pisiprogress

import atom
import gdata.contacts
import gdata.contacts.service
import gdata.service

def parseFullName(fullName):
    retTitle = retLastname = retFirstname = retMiddlename = ''
    fullName = fullName.strip()
    list = fullName.split(" ")
    try:
        title = ''
        moreTitles = True
        while moreTitles:
            moreTitles = False
            if list[0].upper().startswith("PROF"):
                title += 'Prof. '
                del list[0]
                moreTitles = True
            if list[0].upper().startswith("DR"):
                title += 'Dr. '
                del list[0]
                moreTitles = True
        retTitle = title.strip()
        retFirstname = list[0]
        del list[0]
        retLastname = list[len(list)-1]
        del list[len(list)-1]
        if len(list) > 0:
            middlename = ''
            for item in list:
                middlename += item + ' '
            retMiddlename = middlename.strip() # remove trailing white space
    except IndexError:
        pass    # that's fine - we cannot have everything
    return retTitle, retFirstname, retLastname, retMiddlename

def assembleFullName(contactEntry):
        """
        Assembles all information from a contact entry for the packed version of a one line full name
        """
        ret = ""
        if contactEntry.attributes.has_key('title'):
            title = contactEntry.attributes['title']
            if title and title != '':
                ret += title + " "
        if contactEntry.attributes.has_key('firstname'):
            firstname = contactEntry.attributes['firstname']
            if firstname and firstname != '':
                ret += firstname + " "
        if contactEntry.attributes.has_key('middlename'):
            middlename = contactEntry.attributes['middlename']
            if middlename and middlename != '':
                ret += middlename  + " "
        if contactEntry.attributes.has_key('lastname'):
            lastname = contactEntry.attributes['lastname']
            if lastname and lastname != '':
                ret += lastname
        return ret.strip()    

class GDataSyncer():
    """
    Super class for all gdata sync modules (for now contacts and calendar)
    """
    
    def __init__(self, user, password):
        """
        Constructor
        """
        self._user = user
        self._password = password 

    def _doGoogleLogin(self, APPNAME):
        """
        Perform login
        
        Especially take care of Google Captcha mechanism, which kicks in from time to time.
        """
        self._google_client.email = self._user
        self._google_client.password = self._password
        self._google_client.source = APPNAME
        pisiprogress.getCallback().verbose("Google gdata: Logging in with user %s" %(self._user))
        try:
            self._google_client.ProgrammaticLogin()
            pisiprogress.getCallback().verbose("-- Google gdata - sucessfully passed authentication (no capture)")
        except gdata.service.CaptchaRequired:
            pisiprogress.getCallback().verbose("-- Google gdata - this time authentication requires capture")
            captcha_token = self._google_client._GetCaptchaToken()
            url = self._google_client._GetCaptchaURL()
            pisiprogress.getCallback().verbose("-- Google gdata capture URL is <%s>" %(url))
            captcha_response = pisiprogress.getCallback().promptGeneric("Google account requests captcha. Please visit page <%s> and provide capture solution here" %(url))
            pisiprogress.getCallback().verbose("-- Google gdata capture response is <%s>" %(captcha_response))
            self._google_client.ProgrammaticLogin(captcha_token, captcha_response)
