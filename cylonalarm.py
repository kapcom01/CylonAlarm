from cylonalarm.threads import SynControl

import sys
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

def killme():
	print("\nCleaning up...")
	synagermos.cleanup()
	#print("synagermos.cleanup()... ok")
	gobject.MainLoop().quit()
	#print("object.MainLoop().quit()... ok")
	print("Bye")
	sys.exit(0)

print("Synagermos version: 0.2")
synagermos = SynControl()	# initiate
synagermos.deactivate()		# set state: deactivated

class MyDBUSService(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('org.kapcom.synagermos', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/org/kapcom/synagermos')

    @dbus.service.method('org.kapcom.synagermos')
    def actdeact(self):
	if synagermos.state == "ACTIVATED" or synagermos.state == "ACTIVATING":
		synagermos.deactivate()
	else:
		synagermos.sactivate()
 
DBusGMainLoop(set_as_default=True)
myservice = MyDBUSService()
gobject.threads_init() #http://www.jejik.com/articles/2007/01/python-gstreamer_threading_and_the_main_loop/
try:
	gobject.MainLoop().run()
except:
	killme()
	pass #debug interrupt

