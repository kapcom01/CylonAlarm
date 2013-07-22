import RPi.GPIO as GPIO
from time import sleep

class SynHardware():
	def __init__(self):
		GPIO.setmode(GPIO.BOARD)
		self.pin = {
			"seirhna" : 18,
			"pagides" : 22,
			"led" : 24,
			"buzzer" : 26
		}
		GPIO.setup(self.pin["buzzer"], GPIO.OUT, initial=0)
		GPIO.setup(self.pin["led"], GPIO.OUT, initial=0)
		GPIO.setup(self.pin["seirhna"], GPIO.OUT, initial=0)
		GPIO.setup(self.pin["pagides"], GPIO.IN)

		self.alarming = False
		
		print("GPIO.RPI_REVISION: " + str(GPIO.RPI_REVISION))
		print("GPIO.VERSION: " + str(GPIO.VERSION))

	def self_test(self):
		print("Running self test...")
		for test in range(1,7):
			GPIO.output(self.pin["led"],test%2)
			GPIO.output(self.pin["buzzer"],test%2)
			sleep(0.1)
		sleep(0.5)
		GPIO.output(self.pin["seirhna"],1)
		sleep(0.3)
		GPIO.output(self.pin["seirhna"],0)
		print("Self test completed.\n")

	def cleanup(self):
		GPIO.cleanup()

	def led_on(self):
		GPIO.output(self.pin["led"], 1)

	def led_off(self):
		GPIO.output(self.pin["led"], 0)

	def buzzer_on(self):
		GPIO.output(self.pin["buzzer"], 1)

	def buzzer_off(self):
		GPIO.output(self.pin["buzzer"], 0)

	def led_set_state(self, state):
		GPIO.output(self.pin["led"], state)

	def buzzer_set_state(self, state):
		GPIO.output(self.pin["buzzer"], state)

	def bleep(self):
		for bleep in range(0,3):
			self.led_set_state(bleep%2)
			self.buzzer_set_state(bleep%2)
			sleep(0.1)

	def double_bleep(self):
		self.bleep()
		self.bleep()

	def alarm_on(self):
		self.alarming = True
		GPIO.output(self.pin["seirhna"],1)

	def alarm_off(self):
		self.alarming = False
		GPIO.output(self.pin["seirhna"],0)

	def getSensorIn(self):
		if GPIO.input(self.pin["pagides"]):
			sleep(0.3)
			if GPIO.input(self.pin["pagides"]):
				return 1
		return 0

	def isAlarming(self):
		return self.alarming
