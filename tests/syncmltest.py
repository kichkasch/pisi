import gtk.gdk
gtk.gdk.threads_init()
import syncml
 
#locServer = syncml.Location("http://www.mobical.net/sync/server", "")
#locClient = syncml.Location("om_micha", "")
#s = syncml.Session(syncml.SML_SESSION_TYPE_CLIENT, syncml.SML_MIMETYPE_XML, syncml.SML_VERSION_12, syncml.SML_PROTOCOL_SYNCML, locServer, locClient, "1", 0)

def manager_cb(eventType, session):
    print "CALLBACK ", eventType
    global cm
    cm.Stop()

c = syncml.Transport(syncml.SML_TRANSPORT_HTTP_CLIENT)
cm = syncml.Manager(c)
cm.SetEventCallback(manager_cb)
cm.Start()
c.SetConfigOption("URL", "http://www.mobical.net/sync/server")
c.Initialize()
cm.Start()
datastr = "<SyncML><SyncHdr><VerProto>SyncML/1.1</VerProto><VerDTD>1.1</VerDTD><MsgID>1</MsgID><SessionID>1</SessionID><Target><LocURI>http://www.mobical.net/sync/server</LocURI></Target><Source><LocURI>om_micha</LocURI></Source></SyncHdr><SyncBody><Alert><CmdID>1</CmdID><Item><Target><LocURI>http://www.mobical.net/sync/server</LocURI></Target><Source><LocURI>om_micha</LocURI></Source><Meta><Anchor xmlns=\"syncml:metinf\"><Next>Next</Next><Last>last</Last></Anchor></Meta></Item><Data>200</Data></Alert><Final></Final></SyncBody></SyncML>"
data = syncml.TransportData(datastr, len(datastr), syncml.SML_MIMETYPE_XML, False)
print c.Send(None, data)


cred = syncml.smlCredNew(syncml.SML_AUTH_TYPE_BASIC, syncml.SML_FORMAT_TYPE_BASE64,  "hd5hainer",  "kichkasch")
a = syncml.Authenticator()

syncml.smlAuthRegister(a,  cm)

raw_input()
    
print "FINISHED"
