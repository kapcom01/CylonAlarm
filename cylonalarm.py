#! /usr/bin/env python
import sys
import gobject

import json
import logging

from threads import CylonAlarm
from threads import CylonSocket

logger = logging.getLogger()
logger.setLevel("INFO")

if len(sys.argv)>1 and sys.argv[1] == "--test":
	logger.setLevel("DEBUG")
	from tests.hardware import CylonHardware
	from tests.video import CylonVideo
else:
	from hardware import CylonHardware
	from video import CylonVideo

with open("config.json") as f:
	config = json.load(f)

chw = CylonHardware(config)
cv = CylonVideo(config)
ca = []

logging.info("CylonAlarm version: 0.4.0")

hardcoded_methods = {
	"high" : chw.high,
	"low" : chw.low,
	"high_edge" : chw.high_edge,
	"low_edge" : chw.low_edge,
	"double_high_edge" : chw.double_high_edge,
	"double_low_edge" : chw.double_low_edge,
	"show_image" : cv.show_image,
	"animate_images" : cv.animate_images
}

for domain in config["domains"]:
	on_state_actions = {
	"activated" : [
		#{				# template
		#	"pin" : 0,
		#	"hardcoded_method" : chw.high
		#}
	],
	"alarming" : [],
	"movement" : [],
	"activating" : [],
	"deactivated" : []
	}
	for action in config["actions"]:
		for d in config["actions"][action]["domain"]:
			if d==domain["id"]:
				for state in config["actions"][action]["state"]:
					if config["actions"][action]["type"] == 'free_gpios':
						for free_gpio in config["connections"]["free_gpios"]:
							if free_gpio["id"] == config["actions"][action]["free_gpio_id"]:
								on_state_actions[state].append({
									"type" : "free_gpios",
									"pin" : free_gpio["pin"],
									"hardcoded_method" : hardcoded_methods[config["actions"][action]["hardcoded_method"]],
									"loop" : config["actions"][action]["loop"]
									})
								break
					elif config["actions"][action]["type"] == 'video':
						on_state_actions[state].append({
							"type" : "video",
							"images" : config["actions"][action]["images"],
							"hardcoded_method" : hardcoded_methods[config["actions"][action]["hardcoded_method"]],
							"loop" : config["actions"][action]["loop"]
							})
				break
	ca.append(CylonAlarm(domain["id"],config,on_state_actions,chw,cv))	# initiate domain instances

cs = CylonSocket(ca,config)
cs.thread_start()

# TESTS
from time import sleep
for instance in ca:
	instance.actdeact()
	sleep(3)
	instance.actdeact()
	sleep(1)

# gobject.threads_init() #http://www.jejik.com/articles/2007/01/python-gstreamer_threading_and_the_main_loop/
# try:
# 	gobject.MainLoop().run()
# except:
logging.info("\nCleaning up...")
cs.thread_stop()
for cylonalarm in ca:
	cylonalarm.__exit__()
chw.reset_to_default_states()
chw.cleanup()
gobject.MainLoop().quit()
logging.info("Bye")
sys.exit(0)

