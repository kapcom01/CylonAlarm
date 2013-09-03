#! /usr/bin/env python

from cylonalarm.threads import CylonAlarm

import sys
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

print("Synagermos version: 0.2.2")
ca = CylonAlarm()	# initiate

class MyDBUSService(dbus.service.Object):
	def __init__(self):
		bus_name = dbus.service.BusName('org.kapcom.synagermos', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/org/kapcom/synagermos')

	@dbus.service.method('org.kapcom.synagermos')
	def actdeact(self,nfc_reader_id):
		ca.actdeact(nfc_reader_id)
 
DBusGMainLoop(set_as_default=True)
myservice = MyDBUSService()
gobject.threads_init() #http://www.jejik.com/articles/2007/01/python-gstreamer_threading_and_the_main_loop/
try:
	gobject.MainLoop().run()
except:
	print("\nCleaning up...")
	ca.__exit__()
	gobject.MainLoop().quit()
	print("Bye")
	sys.exit(0)

