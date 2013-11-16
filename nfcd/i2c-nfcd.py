#! /usr/bin/env python3
import os
import sys
from subprocess import call
from binascii import hexlify
import time

lib_path = os.path.abspath('lib/py532lib/')
sys.path.append(lib_path)

from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *

print("loading pn532 library...")
pn532 = Pn532_i2c()
pn532.SAMconfigure()
print("i2c NFC Eventd is running. Hit CTRL+C to exit.")

tag_data = None
prev_time = int(time.time())

while True:
	new_tag_data = pn532.read_mifare().get_data()
	new_time = int(time.time())
	if not new_tag_data == tag_data or new_time>prev_time+2:
		tag_data=new_tag_data
		tag_data_str=str(hexlify(tag_data).decode("utf-8"))[-8:]
		# print("TAG (id="+tag_data_str+") inserted")
		print("Executing: python lib/jsonsockclient.py "+tag_data_str+" 1")
		call(["python", "lib/jsonsockclient.py", tag_data_str, "1"])
	prev_time=int(time.time())