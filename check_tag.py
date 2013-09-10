#  This file is used by nfc-eventd and i2c-nfc-eventd.py apps
#  to interface cylonalarm.py via dbus

import sys
import dbus

bus = dbus.SessionBus()
synservice = bus.get_object('org.kapcom.synagermos', '/org/kapcom/synagermos')
nfc_call = synservice.get_dbus_method('nfc_call', 'org.kapcom.synagermos')
nfc_call(sys.argv[1],sys.argv[2]) # nfc_call(tag_id,domain_id)
