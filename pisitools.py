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
