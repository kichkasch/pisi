# tests for Fritzbox
#
#
# http://www.avm.de/de/News/artikel/schnittstellen_und_entwicklungen.php
# http://www.broadband-forum.org/technical/download/TR-064.pdf
# http://www.wehavemorefun.de/fritzbox/index.php/Fritzbox-change-port.py
# http://www.wehavemorefun.de/fritzbox/index.php/Software


from SOAPpy import SOAPProxy,  SOAPConfig, URLopener 

# URL zum Fritz-Box-Web-Interface
FRITZBOX_IP = "192.168.200.1"
## no encryption
#FRITZBOX_PORT = "49000"
#FRITZBOX_PROTOCOl = "HTTP"
## with encryption (ssl)
FRITZBOX_PORT = "49443" 
FRITZBOX_PROTOCOl = "HTTPS" 
FRITZBOX_USER = "dslf-config"
FRITZBOX_PASSWORD = "hd5hainer"


print SOAPProxy(proxy='%s://%s:%s/upnp/control/WANCommonIFC1' %(FRITZBOX_PROTOCOl, FRITZBOX_IP, FRITZBOX_PORT),
                namespace='urn:schemas-upnp-org:service:WANIPConnection:1',
                soapaction='urn:schemas-upnp-org:service:WANIPConnection:1#GetExternalIPAddress',
                noroot=True).GetExternalIPAddress()
print SOAPProxy(proxy='%s://%s:%s/upnp/control/wancommonifconfig1' %(FRITZBOX_PROTOCOl, FRITZBOX_IP, FRITZBOX_PORT),
                namespace='urn:dslforum-org:service:WANCommonInterfaceConfig:1',
                soapaction='urn:dslforum-org:service:WANCommonInterfaceConfig:1#GetCommonLinkProperties',
                noroot=True).GetCommonLinkProperties()
                
#print SOAPProxy(proxy='http://192.168.200.1:49000/upnp/control/deviceinfo',
#                namespace='urn:dslforumorg:service:DeviceInfo:1',
#                soapaction='urn:dslforum-org:service:DeviceInfo:1#GetSecurityPort',
#                noroot=True).GetSecurityPort()
   
#print SOAPProxy(proxy='%s://%s:%s@%s:%s/upnp/control/x_contact' %(FRITZBOX_PROTOCOl, FRITZBOX_USER, FRITZBOX_PASSWORD, FRITZBOX_IP, FRITZBOX_PORT),
#                namespace='urn:dslforum-org:service:X_AVM-DE_OnTel:1',
#                soapaction='urn:dslforum-org:service:X_AVM-DE_OnTel:1#GetCallList',
#                noroot=True).GetCallList()                
