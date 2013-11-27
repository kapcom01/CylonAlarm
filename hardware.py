import RPi.GPIO as GPIO
from time import sleep
import logging

GPIO.setwarnings(False)

class CylonHardware():
	def __init__(self,config):
		logging.debug("[hardware] init")
		self.config = config
		GPIO.setmode(GPIO.BOARD)

		for zone in self.config["connections"]["zones"]:
			GPIO.setup(zone["pin"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
			GPIO.add_event_detect(zone["pin"], GPIO.RISING, bouncetime=500)

		for siren in self.config["connections"]["sirens"]:
			GPIO.setup(siren["pin"], GPIO.OUT, initial=0)

		for free_gpio in self.config["connections"]["free_gpios"]:
			GPIO.setup(free_gpio["pin"], GPIO.OUT if free_gpio["direction"]=="OUT" else GPIO.IN, initial=free_gpio["default_value"])

		self.alarming = False
		
		print("GPIO.RPI_REVISION: " + str(GPIO.RPI_REVISION))
		print("GPIO.VERSION: " + str(GPIO.VERSION))

	def cleanup(self):
		logging.debug("[hardware] cleanup()")
		GPIO.cleanup()

	def high(self,pin):
		logging.debug("[hardware] high("+str(pin)+")")
		GPIO.output(pin, 1)

	def low(self,pin):
		logging.debug("[hardware] low("+str(pin)+")")
		GPIO.output(pin, 0)

	def high_edge(self,pin):
		logging.debug("[hardware] high_edge("+str(pin)+")")
		for value in range(0,3):
			GPIO.output(pin,value%2)
			sleep(0.1)

	def double_high_edge(self,pin):
		self.high_edge(pin)
		self.high_edge(pin)

	def low_edge(self,pin):
		logging.debug("[hardware] low_edge("+str(pin)+")")
		for value in range(1,4):
			GPIO.output(pin,value%2)
			sleep(0.1)

	def double_low_edge(self,pin):
		self.low_edge(pin)
		self.low_edge(pin)

	def getSensorInAfterDelay(self,pin):
		if GPIO.input(pin):
			sleep(0.3)
			if GPIO.input(pin):
				return 1
		return 0

	def addSensorEvent(self,pin,my_callback):
		logging.debug("[hardware] addSensorEvent("+str(pin)+", my_callback)")
		GPIO.add_event_callback(pin, my_callback)

	def removeSensorEvent(self,pin):
		logging.debug("[hardware] removeSensorEvent("+str(pin)+")")
		GPIO.remove_event_detect(pin)

	def reset_to_default_states(self):
		logging.debug("[hardware] reset_to_default_states")
		for free_gpio in self.config["connections"]["free_gpios"]:
			GPIO.output(free_gpio["pin"],free_gpio["default_value"])

		for siren in self.config["connections"]["sirens"]:
			GPIO.output(siren["pin"], 0)
