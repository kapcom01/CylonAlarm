import logging
from time import sleep

class CylonHardware():
	def __init__(self,config):
		logging.debug("[hardware] init")

	def cleanup(self):
		logging.debug("[hardware] cleanup()")

	def high(self,pin):
		logging.debug("[hardware] high("+str(pin)+")")

	def low(self,pin):
		logging.debug("[hardware] low("+str(pin)+")")

	def high_edge(self,pin):
		logging.debug("[hardware] high_edge("+str(pin)+")")
		sleep(0.3)

	def double_high_edge(self,pin):
		self.high_edge(pin)
		self.high_edge(pin)

	def low_edge(self,pin):
		logging.debug("[hardware] low_edge("+str(pin)+")")
		sleep(0.3)

	def double_low_edge(self,pin):
		self.low_edge(pin)
		self.low_edge(pin)

	def getSensorInAfterDelay(self,pin):
		sleep(0.3)
		return 1

	def addSensorEvent(self,pin,my_callback):
		logging.debug("[hardware] addSensorEvent("+str(pin)+", my_callback)")

	def removeSensorEvent(self,pin):
		logging.debug("[hardware] removeSensorEvent("+str(pin)+")")

	def reset_to_default_states(self):
		logging.debug("[hardware] reset_to_default_states)")
