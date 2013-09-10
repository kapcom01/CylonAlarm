#! /usr/bin/env python
import sys
import gobject
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop

import json
with open("cylonalarm/config.json") as f:
	config = json.load(f)

from cylonalarm.threads import CylonAlarm
from cylonalarm.hardware import CylonHardware
hw = CylonHardware(config)
ca = []

print("CylonAlarm version: 0.2.8")

hardcoded_methods = {
	"high" : hw.high,
	"low" : hw.low,
	"high_edge" : hw.high_edge,
	"low_edge" : hw.low_edge,
	"double_high_edge" : hw.double_high_edge,
	"double_low_edge" : hw.double_low_edge,
}

states = ["activated", "alarming", "movement", "activating", "deactivated"]

on_state_actions = {
	"activated" : [
		#{				# template
		#	"pin" : 0,
		#	"hardcoded_method" : hw.high
		#}
	],
	"alarming" : [],
	"movement" : [],
	"activating" : [],
	"deactivated" : []
	}

for state in states:
	actions = config["states"][state]["actions"]
	for action in actions:
		hardcoded_method = hardcoded_methods[config["actions"][action]["hardcoded_method"]]
		free_gpio_id = config["actions"][action]["free_gpio_id"]
		loop = config["actions"][action]["loop"]
		for free_gpio in config["connections"]["free_gpios"]:
			if free_gpio_id == free_gpio["id"]: # loop se ola.. den maresei poly..
				pin = free_gpio["pin"]
				# add in on_state_action dictionary
				on_state_actions[state].append({
					"pin" : pin,
					"hardcoded_method" : hardcoded_method,
					"loop" : loop
					})

for domain in config["domains"]:
	ca.append(CylonAlarm(domain["id"],config,on_state_actions,hw))	# initiate

class MyDBUSService(dbus.service.Object):
	def __init__(self):
		bus_name = dbus.service.BusName('org.kapcom.synagermos', bus=dbus.SessionBus())
		dbus.service.Object.__init__(self, bus_name, '/org/kapcom/synagermos')

	@dbus.service.method('org.kapcom.synagermos')
	def nfc_call(self,tag_id,domain_id):
		for tag in config["tags"]:
			if tag["id"] == tag_id:
				for domain in tag["domain_id"]:
					if domain==int(domain_id):
						ca[int(domain_id)].actdeact()
 
DBusGMainLoop(set_as_default=True)
myservice = MyDBUSService()
gobject.threads_init() #http://www.jejik.com/articles/2007/01/python-gstreamer_threading_and_the_main_loop/
try:
	gobject.MainLoop().run()
except:
	print("\nCleaning up...")
	for cylonalarm in ca:
		cylonalarm.__exit__()
	hw.reset_to_default_states()
	hw.cleanup()
	gobject.MainLoop().quit()
	print("Bye")
	sys.exit(0)

