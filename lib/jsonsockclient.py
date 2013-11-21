#  This file is used by nfc-eventd
#  to interface cylonalarm.py (main program)

import sys

import socket
import json

class JsonSocketClient():
	def __init__(self,address,port):
		self.address=address
		self.port=port
		self.c=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.c.settimeout(3)

	def sendJSON(self,data):
		self.c.connect((self.address,self.port))
		self.c.send(json.dumps(data))
		data_recv=self.c.recv(1024)
		self.c.close()
		return data_recv

if __name__ == "__main__":
    # This is for nfc-eventd program
	d={
		"nfc_call" : {
			"tag_id" : sys.argv[1],
			"domain_id" : sys.argv[2]
		}
	}
	sock=JsonSocketClient('127.0.0.1',5000)
	sock.sendJSON(d)