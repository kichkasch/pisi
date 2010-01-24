#!/usr/bin/env python

"""
Graphical User Interface to PISI based on GTK - one implementation of user interaction

This file is part of Pisi.

It is a very basic GUI, which only allows for selection of two data sources and after initiation
of sync shows a progress bar. What else do we need?

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

import pygtk
pygtk.require('2.0')
import gtk

from pisiconstants import *
import pisiprogress
import pisi


class Base(pisiprogress.AbstractCallback):
    """
    The one and only Main frame
    
    Made up mainly by a notebook; one side for each type of PIM data, and by a progress bar and some buttons.
    """
    def __init__(self):
        """
        Constructor - the whole assembling of the window is performed in here
        """
        pisiprogress.AbstractCallback.__init__(self)
        config = pisi.getConfiguration()
        self.sources = {}
        self.sourcesContacts = []
        self.sourcesCalendar = []
        for con in config.sections():
            self.sources[config.get(con,'description')] = [con, config.get(con,'module') ]
            if config.get(con,'module').startswith('calendar'):
                self.sourcesCalendar.append(config.get(con,'description'))
            elif config.get(con,'module').startswith('contacts'):
                self.sourcesContacts.append(config.get(con,'description'))
        
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete_event", self.delete_event)
        self.window.connect("destroy", self.destroy)
        self.window.set_border_width(10)

        box = gtk.VBox(False, 5)
        
        labelTitle= gtk.Label("PISI Synchronization")
        box.pack_start(labelTitle, False, False, 0)
        labelTitle.show()

        contactsPanel = self._createContactsPanel(self.sourcesContacts)
        paddingBox1 = gtk.HBox(False, 5)
        paddingBox1.pack_start(contactsPanel, False, True, 5)
        paddingBox1.show()
        calendarPanel = self._createCalendarPanel(self.sourcesCalendar)
        paddingBox2 = gtk.HBox(False, 5)
        paddingBox2.pack_start(calendarPanel, False, True, 5)
        paddingBox2.show()
        self.notebook = gtk.Notebook()
        self.notebook.append_page(paddingBox1, gtk.Label('Contacts'))
        self.notebook.append_page(paddingBox2, gtk.Label('Calendar'))
        self.notebook.show()

        box.pack_start(self.notebook, False, True, 5)

        separator = gtk.HSeparator()
        box.pack_start(separator, False, True, 5)
        separator.show()
        
        labelProgress = gtk.Label("Progress")
        labelProgress.set_alignment(0, 0)
        box.pack_start(labelProgress, False, False, 0)
        labelProgress.show()
        self.progressbar = gtk.ProgressBar(adjustment=None)
        self.progressbar.set_text("idle")
        self.progressbar.set_fraction(0)
        box.pack_start(self.progressbar, False, False, 0)
        self.progressbar.show()

        separator = gtk.HSeparator()
        box.pack_start(separator, False, True, 5)
        separator.show()

        boxButtons = gtk.HBox(False, 5)
        bAbout = gtk.Button('About')
        bAbout.connect('clicked', self.showAbout)
        boxButtons.pack_start(bAbout,  True,  False,  0)
        bAbout.show()

        bStart = gtk.Button('Start')
        bStart.connect('clicked', self.startSync)
        boxButtons.pack_start(bStart,  True,  False,  0)
        bStart.show()

        bQuit = gtk.Button('Quit')
        bQuit.connect_object("clicked", gtk.Widget.destroy, self.window)
        boxButtons.pack_start(bQuit,  True,  False,  0)
        bQuit.show()

        boxButtons.show()
        box.pack_start(boxButtons,  False,  False, 0)

        box.show()
        self.window.add(box)
        self.window.show()

    def _createContactsPanel(self,  sources):
        """
        Creates one side in the notebook - the one for setting up contacts synchronization
        """
        box = gtk.VBox(False, 5)
        label = gtk.Label("Source A")
        label.set_alignment(0, 0)
        box.pack_start(label, False, False, 0)
        label.show()
        self.contacts_combobox1 = gtk.combo_box_new_text()
        for sourceDesc in sources:
            self.contacts_combobox1.append_text(sourceDesc)
        self.contacts_combobox1.set_active(0)
        box.pack_start(self.contacts_combobox1, False, False, 0)
        self.contacts_combobox1.show()

        label = gtk.Label("Source B")
        label.set_alignment(0, 0)
        box.pack_start(label, False, False, 0)
        label.show()
        self.contacts_combobox2 = gtk.combo_box_new_text()
        for sourceDesc in sources:
            self.contacts_combobox2.append_text(sourceDesc)
        self.contacts_combobox2.set_active(1)
        box.pack_start(self.contacts_combobox2, False, False, 0)
        self.contacts_combobox2.show()

        separator = gtk.HSeparator()
        box.pack_start(separator, False, True, 5)
        separator.show()

        label = gtk.Label("Conflict Mode")
        label.set_alignment(0, 0)
        box.pack_start(label, False, False, 0)
        label.show()
        self.contacts_combobox3 = gtk.combo_box_new_text()
        for mode in MERGEMODE_STRINGS:
            self.contacts_combobox3.append_text(mode)
        self.contacts_combobox3.set_active(0)
        box.pack_start(self.contacts_combobox3, False, False, 0)
        self.contacts_combobox3.show()
        
        box.show()
        return box

    def _createCalendarPanel(self,  sources):
        """
        Creates one side in the notebook - the one for setting up calendar synchronization
        """
        box = gtk.VBox(False, 5)
        label = gtk.Label("Source A")
        label.set_alignment(0, 0)
        box.pack_start(label, False, False, 0)
        label.show()
        self.calendar_combobox1 = gtk.combo_box_new_text()
        for sourceDesc in sources:
            self.calendar_combobox1.append_text(sourceDesc)
        self.calendar_combobox1.set_active(0)
        box.pack_start(self.calendar_combobox1, False, False, 0)
        self.calendar_combobox1.show()

        label = gtk.Label("Source B")
        label.set_alignment(0, 0)
        box.pack_start(label, False, False, 0)
        label.show()
        self.calendar_combobox2 = gtk.combo_box_new_text()
        for sourceDesc in sources:
            self.calendar_combobox2.append_text(sourceDesc)
        self.calendar_combobox2.set_active(1)
        box.pack_start(self.calendar_combobox2, False, False, 0)
        self.calendar_combobox2.show()
        
        box.show()
        return box

    def main(self):
        """
        Starts up the application ('Main-Loop')
        """
        gtk.main()

    def destroy(self, widget, data=None):
        """
        Shuts down the application
        """
        gtk.main_quit()

    def delete_event(self, widget, event, data=None):
        """
        Event handler
        """
        return False


    def showAbout(self,  target):
        """
        Pops up an 'About'-dialog, which displays all the application meta information from module pisiconstants.
        """
        d = gtk.AboutDialog()
        d.set_name(PISI_NAME)
        d.set_version(PISI_VERSION)
        f = open(FILEPATH_COPYING,  "r")
        content = f.read()
        f.close()
        d.set_license(content)
        d.set_authors(PISI_AUTHORS)
        d.set_comments(PISI_COMMENTS)
        d.set_website(PISI_HOMEPAGE)
        if PISI_TRANSLATOR_CREDITS:
            d.set_translator_credits(PISI_TRANSLATOR_CREDITS)
        if PISI_DOCUMENTERS:
            d.set_documenters(PISI_DOCUMENTERS)
        ret = d.run()
        d.destroy()

    def startSync(self, target):
        """
        Passes control on to PISI core and starts up synchronization process
        
        Updates on the GUI are from now on only performed on request of the core by calling the callback functions.
        """
        self.verbose('Configuring')
        self.progress.reset()
        self.progress.setProgress(0)
        self.update('Configuring')
        self.verbose('Starting synchronization')
        self.verbose('My configuration is:')
        page = self.notebook.get_current_page()
        modulesToLoad = []
        modulesNamesCombined = ""
        mergeMode = 0
        if page == 0:   # sync contacts
            mode = 1
            if len(self.sourcesContacts) < 2:
                self.progress.setProgress(0)
                self.update('Error')
                self.message("You cannot synchronize this type of PIM information as you do not have enough data sources available / configured.")
                return
            source1 = self.contacts_combobox1.get_active()
            source1 = self.sourcesContacts[source1]
            source1 = self.sources[source1][0]
            source2 = self.contacts_combobox2.get_active()
            source2 = self.sourcesContacts[source2]
            source2 = self.sources[source2][0]
            mergeMode = self.contacts_combobox3.get_active()
        elif page == 1: # sync calendar
            mode = 0
            if len(self.sourcesCalendar) < 2:
                self.progress.setProgress(0)
                self.update('Error')
                self.message("You cannot synchronize this type of PIM information as you do not have enough data sources available / configured.")
                return
            source1 = self.calendar_combobox1.get_active()
            source1 = self.sourcesCalendar[source1]
            source1 = self.sources[source1][0]
            source2 = self.calendar_combobox2.get_active()
            source2 = self.sourcesCalendar[source2]
            source2 = self.sources[source2][0]
            
        if source1 == source2:
            self.progress.setProgress(0)
            self.update('Error')
            self.error("You cannot choose one source for synchronization twice. Please make sure that two different sources are chosen for synchronization.")
            return
            
        self.verbose('\tMode is %d - %s' %(mode,  MODE_STRINGS[mode]))
        self.verbose( ('\tIn case of conflicts I use the following strategy: %s' %(MERGEMODE_STRINGS[mergeMode])))
        modulesToLoad.append(source1)
        modulesToLoad.append(source2)
        modulesNamesCombined += source1
        modulesNamesCombined += source2

        config,  configfolder = pisi.readConfiguration()
        source = pisi.importModules(configfolder,  config,  modulesToLoad,  modulesNamesCombined, False)

        self.progress.push(8, 10)
        self.update('Pre-Processing sources')
        self.verbose('Pre-Processing sources')
        self.verbose("\tSource 1")
        source[0].preProcess()
        self.verbose("\tSource 2")
        source[1].preProcess()
        self.verbose("  Pre-Processing Done")
        self.progress.drop()

        self.progress.push(10, 40)
        self.update('Loading')
        self.verbose("\n PHASE 1 - Loading ")
        try:
            self.progress.push(0, 50)
            source[0].load()
            self.progress.drop()
        except BaseException,  m:
            if not self.promptGenericConfirmation("The following error occured when loading:\n%s\nContinue processing?" %(m.message)):
                self.progress.reset()
                self.update("Error")
                return
            self.progress.drop()
        try:
            self.progress.push(50,  100)
            self.update('Loading')
            source[1].load()
            self.progress.drop()
        except BaseException,  m:
            if not self.promptGenericConfirmation("The following error occured when loading:\n%s\nContinue processing?" %(m.message)):
                self.progress.reset()
                self.update("Error")
                return
            self.progress.drop()
        self.progress.drop()
        
        self.progress.push(40, 70)
        self.update('Comparing')
        self.verbose("\n PHASE 2 - Comparing ")
        if mode == MODE_CALENDAR:  # events mode
            pisi.eventsSync.syncEvents(True,  modulesToLoad,  source)
        elif mode == MODE_CONTACTS:  # contacts mode
            pisi.contactsSync.syncContacts(True,  modulesToLoad,  source,  mergeMode)    
        self.progress.drop()
        
        self.progress.push(70, 95)
        self.update('Storing')
        self.verbose ("\n PHASE 3 - Saving  ")
        try:
            pisi.applyChanges(source)
            self.verbose( " DONE  ")
            self.progress.drop()
            
            self.progress.push(95, 100)
            self.update('Post-Processing sources')
            self.verbose('Post-Processing sources')
            self.verbose("\tSource 1")
            source[0].postProcess()
            self.verbose("\tSource 2")
            source[1].postProcess()
            self.verbose("  Post-Processing Done")
            self.progress.drop()
            
            self.progress.setProgress(100)
            self.update('Finished')
        except BaseException,  m:
            self.error(str(m.message))
            self.progress.reset()
            self.update("Error")
            return
        
##
##
## Callbacks for PISI interaction
##
##

    def message(self,  st,  messageType = gtk.MESSAGE_INFO):
        """
        Output a message to the user - a message dialog is popped up
        """
        dialog = gtk.MessageDialog(self.window, buttons=gtk.BUTTONS_OK,  message_format = st,  flags = gtk.DIALOG_MODAL,  type = messageType)
        ret = dialog.run()
        dialog.destroy()
        
    def verbose(self,  st):
        """
        Output a message (of lower interest) to the user - output is directed to text based console.
        """
        print st
        
    def error(self,  st):
        """
        Redirect to L{message} with special dialog type
        """
        print "** Error: %s" %(str(st))
        self.message(str(st),  gtk.MESSAGE_ERROR)

    def promptGenericConfirmation(self,  prompt):
        """
        Ask user for a single confirmation (OK / Cancel)
        """
        d = gtk.MessageDialog(self.window, type = gtk.MESSAGE_QUESTION, buttons = gtk.BUTTONS_YES_NO, message_format = prompt)
        ret = d.run()
        d.destroy()
        return ret == gtk.RESPONSE_YES

    def promptGeneric(self,  prompt,  default):
        """
        Prompt the user for a single entry to type in - not implemented in GUI
        """
        raise ValueError("Prompt Generic not implemented for this GUI.")

    def promptFilename(self, prompt,  default):
        """
        Prompt the user for providing a file name - the standard file selection dialog of GTK is used for this
        """
        d = gtk.FileChooserDialog(prompt,  self.window,  buttons =(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK) )
        d.set_select_multiple(False)
        ret = d.run()
        filename = d.get_filename()
        d.destroy()
        if ret == gtk.RESPONSE_CANCEL or ret == -4:
            raise ValueError("File selection dialog - no file was chosen (%s)." %(prompt))
        return filename
                
    def askConfirmation(self, source,  idList):
        """
        Use interaction for choosing which contact entry to keep in case of a conflict
        
        An instance of L{ConflictsDialog} is started up with the information in question.
        
        @return: A dictionary which contains the action for each conflict entry; the key is the id of the contact entry, 
        the value one out of a - keep entry from first source, b - keep value from second source and s - skip this entry (no change on either side)
        """
        if len(idList) == 0:
            return {}
        d = ConflictsDialog(self.window,  source,  idList)
        ret = d.run()
        reactions = d.getReactions()
        d.destroy()
        return reactions
        
    def update(self,  status):
        """
        This function should be called whenever new information has been made available and the UI should be updates somehow.
        
        The progress bar is updated and the messages is put insight the progress bar. Finally, the GUI is forced to update all components.
        """
        prog = self.progress.calculateOverallProgress()
        self.progressbar.set_text("%s (%d %%)" %(status,  prog ))
        self.progressbar.set_fraction(prog / 100.0)
        while gtk.events_pending():     # see http://faq.pygtk.org/index.py?req=show&file=faq03.007.htp
           gtk.main_iteration(False)

class ConflictsDialog(gtk.Dialog):
    """
    GTK-Dialog to visualize a list of conflicting contact entries in a table view with options to select actions for each entry
    """
    
    def __init__(self,  parent,  source,  idList):
        """
        Contructor - all components are assembled in here
        """
        gtk.Dialog.__init__(self, "Please resolve conflicts",  parent,  gtk.DIALOG_MODAL ,  (gtk.STOCK_OK,gtk.RESPONSE_OK))
        self._idList = idList
        self._source= source
                
        self.set_size_request(500, 300)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.vbox.pack_start(scrolled_window, True, True, 0)
        scrolled_window.show()
        
        table = gtk.Table(3, len(idList), True)
        table.set_row_spacings(10)
        table.set_col_spacings(10)

        scrolled_window.add_with_viewport(table)

        y = 0
        self.combos = []
        self.entries = []
        self.entriesForButton = {}
        for entryID in idList:
            entry1 = source[0].getContact(entryID)
            entry2 = source[1].getContact(entryID)
            self.entries.append([entry1,  entry2])

            l = gtk.Label("%s, %s" %(entry1.attributes['lastname'],entry1.attributes['firstname']))
            l.show()
            table.attach(l, 0, 1, y, y+1)
            
            box = gtk.HBox(False,  5)

            b = gtk.Button("Details")
            b.connect('clicked', self.actionDetails)
            b.show()
            box.pack_start(b, False, False, 0)
            self.entriesForButton[b] = [entry1,  entry2]
 
            self.combos.append(gtk.combo_box_new_text())
            self.combos[y].append_text("SKIP")
            self.combos[y].append_text("Keep <%s>" %(source[0].getDescription()))
            self.combos[y].append_text("Keep <%s>" %(source[1].getDescription()))
            
            self.combos[y].set_active(0)
            self.combos[y].show()
            box.pack_start(self.combos[y], False, False, 0)
            
            box.show()
            table.attach(box, 1, 3, y, y+1)

            y+=1
        
        table.show()
        self.vbox.pack_start(table, True, True, 0)

    def getReactions(self):
        """
        Checks all drop down boxes for their selections and assembles a nice dictionary containing all the user selections
        """
        y = 0
        ret = {}
        for entryID in self._idList:
            ret[entryID] = ['s',  'a',  'b'][self.combos[y].get_active()]
            y+=1
        return ret
        
    def actionDetails(self,  target):
        """
        Pops up an instance of L{ConflictDetailsDialog}
        """
        entry1 = self.entriesForButton[target][0]
        entry2 = self.entriesForButton[target][1]
        d = ConflictDetailsDialog(self, entry1,  entry2, self._source[0].getDescription(),  self._source[1].getDescription() )
        ret = d.run()
        d.destroy()
        

class ConflictDetailsDialog(gtk.Dialog):
    """
    GTK-Dialog for visualizing the differences between two particular contact entries from two data sources (which are concerned as belonging to the same person)
    
    All attributes, in which the two entries differ, are visualized in a table for the two sources.
    """
    
    def __init__(self,  parent,  entry1,  entry2,  nameSource1,  nameSource2):
        """
        Constructor - all components are assembled in here
        """
        gtk.Dialog.__init__(self, "Details for conflict",  parent,  gtk.DIALOG_MODAL ,  ("Close",gtk.RESPONSE_OK))

        self.set_size_request(600, 300)
        box = gtk.VBox(False,  5)

        l = gtk.Label("Details for <%s, %s>" %(entry1.attributes['lastname'],entry1.attributes['firstname']))
        l.show()
        box.pack_start(l, False, False, 0)

        separator = gtk.HSeparator()
        box.pack_start(separator, False, True, 5)
        separator.show()

        diffList = pisi.determineConflictDetails(entry1,  entry2) 

#        boxH = gtk.HBox(False,  20)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(10)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        box.pack_start(scrolled_window, True, True, 0)
        scrolled_window.show()

        table = gtk.Table(3, len(diffList.keys())+1, True)
        table.set_row_spacings(10)
        table.set_col_spacings(10)
        
        l = gtk.Label('Attribute')
        l.set_pattern('_' * len('Attribute'))
        l.set_use_underline(True)
        l.show()
        table.attach(l, 0, 1, 0, 1)
        l = gtk.Label(nameSource1)
        l.set_pattern('_' * len(nameSource1))
        l.set_use_underline(True)
        l.show()
        table.attach(l, 1, 2, 0, 1)
        l = gtk.Label(nameSource2)
        l.set_pattern('_' * len(nameSource2))
        l.set_use_underline(True)
        l.show()
        table.attach(l, 2, 3, 0, 1)

        y = 1
        for key in diffList.keys():
            l = gtk.Label(key)
            l.show()
            table.attach(l, 0, 1, y, y+1)
            l = gtk.Label(self._getDetailValue(entry1.attributes, key))
            l.show()
            table.attach(l, 1, 2, y, y+1)
            l = gtk.Label(self._getDetailValue(entry2.attributes, key))
            l.show()
            table.attach(l, 2, 3, y, y+1)
            y+=1            
            
        table.show()
        scrolled_window.add_with_viewport(table)
#        boxH.pack_start(table, False, True, 20)
#        boxH.show()
#        box.pack_start(boxH, False, True, 5)
        box.show()
        self.vbox.pack_start(box, True, True, 0)
        
    def _getDetailValue(self,  dict,  key,  default = '<n.a.>'):
        """
        Gets around the problem if an attribute in one data source is not set in the other one at all
        """
        try:
            return dict[key]
        except KeyError:
            return default
        
def testConfiguration():
    """
    Checks, whether configuration can be loaded from PISI core.
    
    If not possible, an error message is visualized in a GTK dialog.
    @return: False, if an Error occurs when loading the configration from core; otherwise True
    """
    try:
        pisi.getConfiguration()
        return True
    except ValueError:
        dialog = gtk.MessageDialog(None, buttons=gtk.BUTTONS_OK,  message_format = "PISI configuration not found",  type = gtk.MESSAGE_ERROR)
        dialog.format_secondary_markup("For running PISI you must have a configuration file located in '/home/root/.pisi/conf'.\n\nWith the package a well-documented sample was placed at '/usr/share/doc/pisi/conf.example'. You may rename this for a starting point - then edit this file in order to configure your PIM synchronization data sources.")
        ret = dialog.run()
        dialog.destroy()
        return False
        
"""
This starts the GUI version of PISI
"""
if __name__ == "__main__":
    if testConfiguration():
        base = Base()
        pisiprogress.registerCallback(base)
        base.main()

