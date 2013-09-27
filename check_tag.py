#  This file is used by nfc-eventd and i2c-nfc-eventd.py apps
#  to interface cylonalarm.py (main program)

import sys
# import dbus

# bus = dbus.SessionBus()
# synservice = bus.get_object('org.kapcom.synagermos', '/org/kapcom/synagermos')
# nfc_call = synservice.get_dbus_method('nfc_call', 'org.kapcom.synagermos')
# nfc_call(sys.argv[1],sys.argv[2]) # nfc_call(tag_id,domain_id)

import socket
import pickle

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(('127.0.0.1',5000))

d={
	"nfc_call" : {
		"tag_id" : sys.argv[1],
		"domain_id" : sys.argv[2]
	}
}

s.send(pickle.dumps(d))
s.close()