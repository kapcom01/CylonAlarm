import sys
import dbus

import cylonalarm.config as config # temporary configuration file

tag = config.tag

try:
	temp = tag[sys.argv[1]]
	bus = dbus.SessionBus()
	synservice = bus.get_object('org.kapcom.synagermos', '/org/kapcom/synagermos')
	actdeact = synservice.get_dbus_method('actdeact', 'org.kapcom.synagermos')
	actdeact()
except KeyError:
	pass	# wrong tag id

