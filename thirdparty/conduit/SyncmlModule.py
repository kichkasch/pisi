"""
The original of this file was taken from a Conduit branch of John Carr (http://git.gnome.org/cgit/conduit/log/?h=syncml),
It was modified significantly for PISI use by Michael Pilgermann.

Major keys are:
 - there is a bit of a problem as Syncml is actually the server (making all the comparing) - but PISI has its engine itself
 - consequently, we are always using slow sync (all items have to be transmitted) and tell the Syncml server our changes afterwards
 
The entire implementation (of libsyncml) is asynchronous. We just tell the server, we want to sync - then the server comes back at some
point to ask for further information. So it's all based on handlers, which have to be registered in the beginning - all the work has
to be done in there.
"""

import pysyncml
import enums
import threading
import uuid

SYNCML_LOGFILE = '/tmp/pisi-syncml.log'
"""Log file for Syncml module debug output"""

class Log:
    """
    There was this nice logging facility in the original
    
    I only redirected to a file - there might always be some problems with this complex protocol.
    """
    def __init__(self):
        self._file = open(SYNCML_LOGFILE, 'w')
    
    def error(self, arg):
        self._file.write("Error: " + arg + "\n")
        
    def info(self, arg):
        self._file.write("Info: " + arg + "\n")

    def debug(self, arg):
        self._file.write("Debug: " + arg + "\n")

log = Log()

class SyncmlDataProvider():
    """
    This class is doing all the work
    
    Don't instantiate it - there is a datastore and a connection missing; go for SyncmlContactsInterface instead.
    """

    _syncml_version_ = "1.1"

    def handle_event(self, sync_object, event, userdata, err):
        """ handle_event is called by libsyncml at different stages of a sync
            This includes when this connect and disconnect and when errors occur.

            It WILL happen in a different thread to whatever thread called syncobject.run()
        """
        if event == enums.SML_DATA_SYNC_EVENT_ERROR:
            log.error("CB: An error has occurred: %s" % err.message)
            return

        if event == enums.SML_DATA_SYNC_EVENT_CONNECT:
            log.info("CB: Connect")
            return

        if event == enums.SML_DATA_SYNC_EVENT_DISCONNECT:
            log.info("CB: Disconnect")
            return

        if event == enums.SML_DATA_SYNC_EVENT_FINISHED:
            log.info("CB: Session complete")
            self._refresh_lock.set()
            return

        if event == enums.SML_DATA_SYNC_EVENT_GOT_ALL_ALERTS:
            log.info("CB: Got all alerts" )
            self._syncml_sendall()
            return

        if event == enums.SML_DATA_SYNC_EVENT_GOT_ALL_CHANGES:
            log.info("CB: Got All Changes")
            return

        if event == enums.SML_DATA_SYNC_EVENT_GOT_ALL_MAPPINGS:
            log.info("CB: Got All Mappings")
            return

        log.error("An error has occurred (Unexpected event)")


    def handle_change(self, sync_object, source, type, uid, data, size, userdata, err):
        """ handle_change is called by libsyncml to tells us about changes on the server or device
            we are synchronising to.

            This WILL happen in a different thread to where sync is happening.
        """
        log.debug("got change (%s)" %(['UNKNOWN','ADD',  'REPLACE','DELETE'][type]))
        self._rawContacts[uid] = data
        err = pysyncml.Error()
        self.syncobj.add_mapping(source, uid, uid, pysyncml.byref(err))
        return 1

    def handle_devinf(self, sync_object, info, userdata, err):
        """ handle_devinf is called by libsyncml to tells us information such as device mfr and firmware
            version of whatever we are syncing against.

            This WILL happen in a different thread to where sync is happening.
            There is a known bug with SE C902 where this is called twice - ignore the 2nd one or crashes
            occur
        """
        return 1

    def handle_change_status(self, sync_object, code, newuid, userdata, err):
        """
        200 is good ...
        201 seems to indicate OK (sometimes not :()
        211 - I think not
        """
        log.info("CB: Handle Change Status (ret: %s)" %code)
        if code < 200 or 299 < code:
            return 0
        return 1

    def handle_get_anchor(self, sync_object, name, userdata, err):
        anchor = self.anchor[name] if name in self.anchor else None
        log.debug("get_anchor('%s') returns %s" % (name, anchor or "None"))
        return pysyncml.strdup(anchor) if anchor else None

    def handle_set_anchor(self, sync_object, name, value, userdata, err):
        log.info("CB: Set Anchor")
        self.anchor[name] = value
        return 1

    def handle_get_alert_type(self, sync_object, source, alert_type, userdata, err):
        log.info("CB: Get Alert Type")
        return enums.SML_ALERT_SLOW_SYNC

    def _syncml_sendall(self):
        err = pysyncml.Error()
        for key in self._actions[0].keys():
            LUID = str(uuid.uuid4())
            self.syncobj.add_change(self._store_, enums.SML_CHANGE_ADD, LUID, self._actions[0][key], len(self._actions[0][key]), "", pysyncml.byref(err))
        for key in self._actions[1].keys():
            self.syncobj.add_change(self._store_, enums.SML_CHANGE_DELETE, key, "", 0, key, pysyncml.byref(err))
        for key in self._actions[2].keys():
            self.syncobj.add_change(self._store_, enums.SML_CHANGE_REPLACE, key, self._actions[2][key], len(self._actions[2][key]), key, pysyncml.byref(err))
        self.syncobj.send_changes(pysyncml.byref(err))

    def _syncml_run(self):
        err = pysyncml.Error()

        self._setup_connection(err)
        self._setup_datastore(err)

        self.syncobj.set_option(enums.SML_DATA_SYNC_CONFIG_VERSION, self._syncml_version_, pysyncml.byref(err))
        self.syncobj.set_option(enums.SML_DATA_SYNC_CONFIG_IDENTIFIER, self._syncml_identifier_, pysyncml.byref(err))
        self.syncobj.set_option(enums.SML_DATA_SYNC_CONFIG_USE_WBXML, "1", pysyncml.byref(err))

        self.syncobj.register_event_callback(self._handle_event, None)
        self.syncobj.register_change_callback(self._handle_change, None)
        self.syncobj.register_handle_remote_devinf_callback(self._handle_devinf, None)
        self.syncobj.register_change_status_callback(self._handle_change_status)
        self.syncobj.register_set_anchor_callback(self._handle_set_anchor, None)
        self.syncobj.register_get_anchor_callback(self._handle_get_anchor, None)
        self.syncobj.register_get_alert_type_callback(self._handle_get_alert_type, None)

        if not self.syncobj.init(pysyncml.byref(err)):
            log.error("Unable to prepare synchronisation")
            return

        if not self.syncobj.run(pysyncml.byref(err)):
            log.error("Unable to synchronise")
            log.error (err.message)
            return

        log.info("running sync..")
        return err

    def __init__(self, address):
        """
        Initializes all parameters
        """
        self.address = address
        self.anchor = {}
        self._rawContacts = {}
        self._actions = [{}, {}, {}]
        
        self._handle_event = pysyncml.EventCallback(self.handle_event)
        self._handle_change = pysyncml.ChangeCallback(self.handle_change)
        self._handle_devinf = pysyncml.HandleRemoteDevInfCallback(self.handle_devinf)
        self._handle_change_status = pysyncml.ChangeStatusCallback(self.handle_change_status)
        self._handle_get_anchor = pysyncml.GetAnchorCallback(self.handle_get_anchor)
        self._handle_set_anchor = pysyncml.SetAnchorCallback(self.handle_set_anchor)
        self._handle_get_alert_type = pysyncml.GetAlertTypeCallback(self.handle_get_alert_type)
        
        self._refresh_lock = threading.Event()
#        self._put_lock = threading.Event()

    def downloadItems(self):
        """
        Public Interface: download all contacts from server
        """
        self._syncml_run()
        self._refresh_lock.wait(60)
        self._refresh_lock.clear()
        return self._rawContacts

    def applyChanges(self, adds = {}, dels = {}, mods = {}):
        """
        Public Interface: apply changes on server
        """
        self._syncml_run()
        self._refresh_lock.wait(60)
        self._refresh_lock.clear()

        self._actions = [adds, dels, mods]
        self._syncml_run()
        self._refresh_lock.wait(60)
        self._refresh_lock.clear()

    def finish(self):
        self.syncobj.unref(pysyncml.byref(self.syncobj))



class HttpClient(SyncmlDataProvider):
    """
    Encapsulates the connection establishment via HTTP
    """

    def __init__(self, username, password):
        SyncmlDataProvider.__init__(self, self._address_)
        self.username = username
        self.password = password

    def _setup_connection(self, err = pysyncml.Error()):
        self.syncobj = pysyncml.SyncObject.new(enums.SML_SESSION_TYPE_CLIENT, enums.SML_TRANSPORT_HTTP_CLIENT, pysyncml.byref(err))
        self.syncobj.set_option(enums.SML_TRANSPORT_CONFIG_URL, self._address_, pysyncml.byref(err))

        if self.username != None and len(self.username) > 0:
            self.syncobj.set_option(enums.SML_DATA_SYNC_CONFIG_AUTH_USERNAME, self.username, pysyncml.byref(err))
            self.syncobj.set_option(enums.SML_DATA_SYNC_CONFIG_AUTH_PASSWORD, self.password, pysyncml.byref(err))

        self._session_type = enums.SML_SESSION_TYPE_CLIENT


class ContactsProvider(SyncmlDataProvider):
    """
    Encapsulated the data handling (VCF)
    """

    _name_ = "Contacts"
    _description_ = "Contacts"
    _module_type_ = "twoway"
    _in_type_ = "contact"
    _out_type_ = "contact"
    _icon_ = "contact-new"
    _configurable_ = False

    _mime_ = "text/x-vcard"

    def _setup_datastore(self, err = pysyncml.Error()):
        self.syncobj.add_datastore(self._mime_, None, self._store_, pysyncml.byref(err))


class CalendarProvider(SyncmlDataProvider):
    """
    Encapsulated the data handling (ICS)
    """
    _name_ = "Calendar"
    _description_ = "Calendar"
    _module_type_ = "twoway"
    _in_type_ = "event"
    _out_type_ = "event"
    _icon_ = "x-office-calendar"
    _configurable_ = False

    _mime_ = "text/x-calendar"

    def _setup_datastore(self):
        err = pysyncml.Error()
        self.syncobj.add_datastore(self._mime_, None, self._store_, pysyncml.byref(err))


class SyncmlContactsInterface(HttpClient, ContactsProvider):
    """
    Public Interface that should be used  from outside
    """
    _mime_ = "text/vcard"
    _syncml_version_ = "1.2"

    def __init__(self, url, username, password, store, syncml_identifier):
        self._address_ = url
        self._store_ = store
        self._syncml_identifier_ = syncml_identifier
        HttpClient.__init__(self, username, password)

class SyncmlCalendarInterface(HttpClient, CalendarProvider):
    """
    Public Interface that should be used  from outside
    """
    _mime_ = "text/x-calendar"
    _syncml_version_ = "1.2"

    def __init__(self, url, username, password, store, syncml_identifier):
        self._address_ = url
        self._store_ = store
        self._syncml_identifier_ = syncml_identifier
        HttpClient.__init__(self, username, password)
