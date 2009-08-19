from ctypes import *

#lib = CDLL('libsyncml.so')
lib = CDLL('/usr/lib/libsyncml.so')
libc = CDLL('libc.so.6')

def instancemethod(method):
    def _(self, *args, **kwargs):
        return method(self, *args, **kwargs)
    return _

class DataStore(c_void_p):

    new = staticmethod(lib.smlDevInfDataStoreNew)
    get_source_ref = instancemethod(lib.smlDevInfDataStoreGetSourceRef)
    set_source_ref = instancemethod(lib.smlDevInfDataStoreSetSourceRef)
    source_ref = property(fget=get_source_ref, fset=set_source_ref)
    get_display_name = instancemethod(lib.smlDevInfDataStoreGetDisplayName)
    set_display_name = instancemethod(lib.smlDevInfDataStoreSetDisplayName)
    display_name = property(fget=get_display_name, fset=set_display_name)
    get_max_guid_size = instancemethod(lib.smlDevInfGetMaxGUIDSize)
    set_max_guid_size = instancemethod(lib.smlDevInfSetMaxGUIDSize)
    max_guid_size = property(fget=get_max_guid_size, fset=set_max_guid_size)


class Info(c_void_p):

    new = staticmethod(lib.smlDevInfNew)
    add_datastore = instancemethod(lib.smlDevInfAddDataStore)
    num_datastores = instancemethod(lib.smlDevInfNumDataStores)
    get_nth_datastore = instancemethod(lib.smlDevInfGetNthDataStore)
    get_manufacturer = instancemethod(lib.smlDevInfGetManufacturer)
    set_manufacturer = instancemethod(lib.smlDevInfSetManufacturer)
    manufacturer = property(fget=get_manufacturer, fset=set_manufacturer)
    get_model = instancemethod(lib.smlDevInfGetModel)
    set_model = instancemethod(lib.smlDevInfSetModel)
    model = property(fget=get_model, fset=set_model)
    get_oem = instancemethod(lib.smlDevInfGetOEM)
    set_oem = instancemethod(lib.smlDevInfSetOEM)
    oem = property(fget=get_oem, fset=set_oem)
    get_firmware_version = instancemethod(lib.smlDevInfGetFirmwareVersion)
    set_firmware_version = instancemethod(lib.smlDevInfSetFirmwareVersion)
    firmware_version = property(fget=get_firmware_version, fset=set_firmware_version)
    get_software_version = instancemethod(lib.smlDevInfGetSoftwareVersion)
    set_software_version = instancemethod(lib.smlDevInfSetSoftwareVersion)
    software_version = property(fget=get_software_version, fset=set_software_version)
    get_hardware_version = instancemethod(lib.smlDevInfGetHardwareVersion)
    set_hardware_version = instancemethod(lib.smlDevInfSetHardwareVersion)
    hardware_version = property(fget=get_hardware_version, fset=set_hardware_version)
    get_device_id = instancemethod(lib.smlDevInfGetDeviceID)
    set_device_id = instancemethod(lib.smlDevInfSetDeviceID)
    device_id = property(fget=get_device_id, fset=set_device_id)
    get_device_type = instancemethod(lib.smlDevInfGetDeviceType)
    set_device_type = instancemethod(lib.smlDevInfSetDeviceType)
    device_type = property(fget=get_device_type, fset=set_device_type)
    get_supports_utc = instancemethod(lib.smlDevInfSupportsUTC)
    set_supports_utc = instancemethod(lib.smlDevInfSetSupportsUTC)
    supports_utc = property(fget=get_supports_utc, fset=set_supports_utc)
    get_supports_large_objs = instancemethod(lib.smlDevInfSupportsLargeObjs)
    set_supports_large_objs = instancemethod(lib.smlDevInfSetSupportsLargeObjs)
    supports_large_objs = property(fget=get_supports_large_objs, fset=set_supports_large_objs)
    get_supports_num_changes = instancemethod(lib.smlDevInfSupportsNumberOfChanges)
    set_supports_num_changes = instancemethod(lib.smlDevInfSetSupportsNumberOfChanges)
    supports_num_changes = property(fget=get_supports_num_changes, fset=set_supports_num_changes)


class SyncObject(c_void_p):

    unref = lib.smlDataSyncObjectUnref
    new = staticmethod(lib.smlDataSyncNew)
    set_option = instancemethod(lib.smlDataSyncSetOption)
    add_datastore = instancemethod(lib.smlDataSyncAddDatastore)
    init = instancemethod(lib.smlDataSyncInit)
    run = instancemethod(lib.smlDataSyncRun)
    add_change = instancemethod(lib.smlDataSyncAddChange)
    send_changes = instancemethod(lib.smlDataSyncSendChanges)
    add_mapping = instancemethod(lib.smlDataSyncAddMapping)
    get_target = instancemethod(lib.smlDataSyncGetTarget)
    
    register_event_callback = instancemethod(lib.smlDataSyncRegisterEventCallback)
    register_get_alert_type_callback = instancemethod(lib.smlDataSyncRegisterGetAlertTypeCallback)
    register_change_callback = instancemethod(lib.smlDataSyncRegisterChangeCallback)
    register_get_anchor_callback = instancemethod(lib.smlDataSyncRegisterGetAnchorCallback)
    register_set_anchor_callback = instancemethod(lib.smlDataSyncRegisterSetAnchorCallback)
    register_write_devinf_callback = instancemethod(lib.smlDataSyncRegisterWriteDevInfCallback)
    register_read_devinf_callback = instancemethod(lib.smlDataSyncRegisterReadDevInfCallback)
    register_handle_remote_devinf_callback = instancemethod(lib.smlDataSyncRegisterHandleRemoteDevInfCallback)
    register_change_status_callback = instancemethod(lib.smlDataSyncRegisterChangeStatusCallback)


class Location(c_void_p):

    new = staticmethod(lib.smlLocationNew)
    get_uri = instancemethod(lib.smlLocationGetURI)
    get_name = instancemethod(lib.smlLocationGetName)
    set_name = instancemethod(lib.smlLocationSetName)


class Error(c_void_p):

    @property
    def message(self):
        return lib.smlErrorPrint(byref(self))

    unref = lib.smlErrorDeref


g_thread_init = lib.g_thread_init
EventCallback = CFUNCTYPE(None, SyncObject, c_int, c_void_p, Error)
GetAlertTypeCallback = CFUNCTYPE(c_int, SyncObject, c_char_p, c_int, c_void_p, POINTER(Error))
ChangeCallback = CFUNCTYPE(c_int, SyncObject, c_char_p, c_int, c_char_p, c_char_p, c_uint, c_void_p, POINTER(Error))
ChangeStatusCallback = CFUNCTYPE(c_int, SyncObject, c_uint, c_char_p, c_char_p, POINTER(Error))
GetAnchorCallback = CFUNCTYPE(c_void_p, SyncObject, c_char_p, c_void_p, POINTER(Error))
SetAnchorCallback = CFUNCTYPE(c_int, SyncObject, c_char_p, c_char_p, c_void_p, POINTER(Error))
WriteDevInfCallback = CFUNCTYPE(c_int, SyncObject, Info, c_void_p, POINTER(Error))
ReadDevInfCallback = CFUNCTYPE(Info, SyncObject, c_char_p, c_void_p, POINTER(Error))
HandleRemoteDevInfCallback = CFUNCTYPE(c_int, SyncObject, Info, c_void_p, POINTER(Error))
lib.smlDevInfDataStoreNew.argtypes = [c_char_p, POINTER(Error)]
lib.smlDevInfDataStoreNew.restype = DataStore

lib.smlDevInfDataStoreGetSourceRef.argtypes = []
lib.smlDevInfDataStoreGetSourceRef.restype = c_char_p

lib.smlDevInfDataStoreGetDisplayName.argtypes = []
lib.smlDevInfDataStoreGetDisplayName.restype = c_char_p

lib.smlDevInfGetMaxGUIDSize.argtypes = []
lib.smlDevInfGetMaxGUIDSize.restype = c_char_p

lib.smlDevInfNew.argtypes = [c_char_p, c_int, POINTER(Error)]
lib.smlDevInfNew.restype = Info

lib.smlDevInfAddDataStore.argtypes = [Info, DataStore]
lib.smlDevInfAddDataStore.restype = None

lib.smlDevInfNumDataStores.argtypes = [Info]
lib.smlDevInfNumDataStores.restype = c_uint

lib.smlDevInfGetNthDataStore.argtypes = [Info, c_uint]
lib.smlDevInfGetNthDataStore.restype = DataStore

lib.smlDevInfGetManufacturer.argtypes = []
lib.smlDevInfGetManufacturer.restype = c_char_p

lib.smlDevInfGetModel.argtypes = []
lib.smlDevInfGetModel.restype = c_char_p

lib.smlDevInfGetOEM.argtypes = []
lib.smlDevInfGetOEM.restype = c_char_p

lib.smlDevInfGetFirmwareVersion.argtypes = []
lib.smlDevInfGetFirmwareVersion.restype = c_char_p

lib.smlDevInfGetSoftwareVersion.argtypes = []
lib.smlDevInfGetSoftwareVersion.restype = c_char_p

lib.smlDevInfGetHardwareVersion.argtypes = []
lib.smlDevInfGetHardwareVersion.restype = c_char_p

lib.smlDevInfGetDeviceID.argtypes = []
lib.smlDevInfGetDeviceID.restype = c_char_p

lib.smlDevInfGetDeviceType.argtypes = []
lib.smlDevInfGetDeviceType.restype = c_int

lib.smlDevInfSupportsUTC.argtypes = []
lib.smlDevInfSupportsUTC.restype = c_int

lib.smlDevInfSupportsLargeObjs.argtypes = []
lib.smlDevInfSupportsLargeObjs.restype = c_int

lib.smlDevInfSupportsNumberOfChanges.argtypes = []
lib.smlDevInfSupportsNumberOfChanges.restype = c_int

lib.smlDataSyncObjectUnref.argtypes = [POINTER(SyncObject)]
lib.smlDataSyncObjectUnref.restype = None

lib.smlDataSyncNew.argtypes = [c_int, c_int, POINTER(Error)]
lib.smlDataSyncNew.restype = SyncObject

lib.smlDataSyncSetOption.argtypes = [SyncObject, c_char_p, c_char_p, POINTER(Error)]
lib.smlDataSyncSetOption.restype = c_int

lib.smlDataSyncAddDatastore.argtypes = [SyncObject, c_char_p, c_char_p, c_char_p, POINTER(Error)]
lib.smlDataSyncAddDatastore.restype = c_int

lib.smlDataSyncInit.argtypes = [SyncObject, POINTER(Error)]
lib.smlDataSyncInit.restype = c_int

lib.smlDataSyncRun.argtypes = [SyncObject, POINTER(Error)]
lib.smlDataSyncRun.restype = c_int

lib.smlDataSyncAddChange.argtypes = [SyncObject, c_char_p, c_int, c_char_p, c_char_p, c_uint, c_void_p, POINTER(Error)]
lib.smlDataSyncAddChange.restype = c_int

lib.smlDataSyncSendChanges.argtypes = [SyncObject, POINTER(Error)]
lib.smlDataSyncSendChanges.restype = c_int

lib.smlDataSyncAddMapping.argtypes = [SyncObject, c_char_p, c_char_p, c_char_p, POINTER(Error)]
lib.smlDataSyncAddMapping.restype = c_int

lib.smlDataSyncGetTarget.argtypes = [SyncObject, POINTER(Error)]
lib.smlDataSyncGetTarget.restype = Location

lib.smlDataSyncRegisterEventCallback.argtypes = [SyncObject, EventCallback]
lib.smlDataSyncRegisterEventCallback.restype = None

lib.smlDataSyncRegisterGetAlertTypeCallback.argtypes = [SyncObject, GetAlertTypeCallback]
lib.smlDataSyncRegisterGetAlertTypeCallback.restype = None

lib.smlDataSyncRegisterChangeCallback.argtypes = [SyncObject, ChangeCallback]
lib.smlDataSyncRegisterChangeCallback.restype = None

lib.smlDataSyncRegisterGetAnchorCallback.argtypes = [SyncObject, GetAnchorCallback]
lib.smlDataSyncRegisterGetAnchorCallback.restype = None

lib.smlDataSyncRegisterSetAnchorCallback.argtypes = [SyncObject, SetAnchorCallback]
lib.smlDataSyncRegisterSetAnchorCallback.restype = None

lib.smlDataSyncRegisterWriteDevInfCallback.argtypes = [SyncObject, WriteDevInfCallback]
lib.smlDataSyncRegisterWriteDevInfCallback.restype = None

lib.smlDataSyncRegisterReadDevInfCallback.argtypes = [SyncObject, ReadDevInfCallback]
lib.smlDataSyncRegisterReadDevInfCallback.restype = None

lib.smlDataSyncRegisterHandleRemoteDevInfCallback.argtypes = [SyncObject, HandleRemoteDevInfCallback]
lib.smlDataSyncRegisterHandleRemoteDevInfCallback.restype = None

lib.smlDataSyncRegisterChangeStatusCallback.argtypes = [SyncObject, ChangeStatusCallback]
lib.smlDataSyncRegisterChangeStatusCallback.restype = None

lib.smlLocationNew.argtypes = [c_char_p, c_char_p, POINTER(Error)]
lib.smlLocationNew.restype = Location

lib.smlLocationGetURI.argtypes = [Location]
lib.smlLocationGetURI.restype = c_char_p

lib.smlLocationGetName.argtypes = [Location]
lib.smlLocationGetName.restype = c_char_p

lib.smlLocationSetName.argtypes = [Location, c_char_p]
lib.smlLocationSetName.restype = None

lib.smlErrorDeref.argtypes = [POINTER(Error)]
lib.smlErrorDeref.restype = None

lib.smlErrorPrint.argtypes = [POINTER(Error)]
lib.smlErrorPrint.restype = c_char_p

lib.g_thread_init.argtypes = [c_void_p]
lib.g_thread_init.restype = None

libc.strdup.argtypes = [c_char_p]
libc.strdup.restype = c_void_p
strdup = libc.strdup
