#  This file is used by nfc-eventd and i2c-nfc-eventd.py apps
#  to interface cylonalarm.py dbus actdeact() function
#  when the tag_id exists on the config.tag dictionary.

import sys
import dbus

import cylonalarm.config as config # temporary configuration file

tag = config.tag

try:
	temp = tag[sys.argv[1]] # first arg is the tag_id
	bus = dbus.SessionBus()
	synservice = bus.get_object('org.kapcom.synagermos', '/org/kapcom/synagermos')
	actdeact = synservice.get_dbus_method('actdeact', 'org.kapcom.synagermos')
	actdeact(sys.argv[2]) # second arg is the nfc_reader_id
except KeyError:
	pass	# wrong tag id

