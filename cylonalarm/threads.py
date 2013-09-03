from threading import Thread, Event, Timer
from datetime import datetime
from cylonalarm.hardware import *
import smtplib
from email.mime.text import MIMEText

import config #temporary configuration file

def print_time():
	now = datetime.now()
	now = now.strftime("%d/%m/%y %H:%M.%S")
	return now

hw = CylonHardware()

class BaseThread:
	def __init__(self):
		self.event = Event()
		self.thread = Thread()

	def thread_start(self):
		self.event.clear()
		self.setup_thread()
		self.thread.start()

	def thread_stop(self):
		self.event.set()
		try:
			self.thread.join()
		except:
			pass

	#def setup_thread(self):
		#self.thread = Thread(target=self.thread_action, args=(self.event,))

class SendSMS(BaseThread):
	"""docstring for SendSMS"""
	def __init__(self):
		BaseThread.__init__(self)

	def setup_thread(self):
		self.thread = Thread(target=self.thread_action, args=(self.event,))

	def send_mail(self):
		sender = config.mail_sender
		recipients = config.mail_receipents
		msg = MIMEText("""Synagermos tora!""")
		msg['Subject'] = "SYNAGERMOS sto YPOGEIO!!"
		msg['From'] = sender
		msg['To'] = ", ".join(recipients)

		 
		# Credentials (if needed)
		username = config.mail_username
		password = config.mail_password
		 
		# The actual mail send
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(sender, recipients, msg.as_string())
		server.quit()

	def thread_action(self,stop_event):
		print("["+print_time()+"] Sending SMS...")
		self.send_mail()

class Beeping(BaseThread):
	def setup_thread(self):
		self.thread = Thread(target=self.thread_action, args=(self.event,))

	def thread_action(self, stop_event):
		while not stop_event.is_set():
			hw.double_beep()
			self.event.wait(1)

class CylonAlarm():
	def __init__(self):
		self.state = ""
		self.activation_timer = Timer(0, self.dummy)
		self.alarm_delay_timer = Timer(0, self.dummy)
		self.alarm_duration_timer = Timer(0, self.dummy)
		self.beeping_timer=Beeping()
		self.sendsms = SendSMS()
		print("\n["+print_time()+"] \033[92mRunning...\033[0m Press Ctrl+C to exit")
		self.deactivate()

	# just a workaround to be able to call activation_timer.cancel() without being really started
	def dummy(self):
		pass

	def is_deactivated(self):
		if self.state == "ACTIVATED" or self.state == "ACTIVATING":
			return False
		else:
			return True

	def actdeact(self,nfc_reader_id):
		print("["+print_time()+"] Call from NFC Reader ID: "+nfc_reader_id)
		if nfc_reader_id!="1":
			print("["+print_time()+"]  ignoring call...")
		else:
			if self.is_deactivated():
				self.sactivate()
			else:
				self.deactivate()

	def sactivate(self):
			print("["+print_time()+"] Activating in "+str(config.activation_wait)+" seconds...")
			self.state = "ACTIVATING"
			self.beeping_timer.thread_start()
			self.activation_timer = Timer(config.activation_wait,self.start_sensing)
			self.activation_timer.start()

	def deactivate(self):
                self.beeping_timer.thread_stop()
		self.activation_timer.cancel()
		self.alarm_delay_timer.cancel()
		self.alarm_duration_timer.cancel()
		self.stop_sensing()
		hw.alarm_off()
                hw.beep()
                hw.led_off()
		self.state = "DEACTIVATED"
		print("["+print_time()+"] \033[93mDeactivated\033[0m")

	def start_sensing(self):
		self.beeping_timer.thread_stop()
		hw.led_on()
		self.state = "ACTIVATED"
		print("["+print_time()+"] \033[93mActivated\033[0m")
		hw.addSensorEvent(self.movement)

	def stop_sensing(self):
		hw.removeSensorEvent()

	def movement(self,channel):
		if hw.getSensorIn() and not hw.isAlarming() and not self.alarm_delay_timer.isAlive():
			print("["+print_time()+"]\033[1;97m Movement detected (>500ms), you have "+str(config.alarm_delay)+" seconds...\033[0m")
                        self.beeping_timer.thread_start()
			self.alarm_delay_timer = Timer(config.alarm_delay,self.sound_the_alarm)
			self.alarm_delay_timer.start()
			self.stop_sensing()

	def sound_the_alarm(self):
		hw.alarm_on()
		print("\033[91m["+print_time()+"] <<<  ALERT  >>>\033[0m")
		self.sendsms.thread_start()
		self.alarm_duration_timer = Timer(config.alarm_duration,self.stop_the_alarm)
		self.alarm_duration_timer.start()

	def stop_the_alarm(self):
		hw.alarm_off()
		print("["+print_time()+"]\033[1;97m Alarm stopped\033[0m")

	def __exit__(self):
		self.activation_timer.cancel()
		self.alarm_delay_timer.cancel()
		self.alarm_duration_timer.cancel()
		try:
			self.activation_timer.join()
			self.alarm_delay_timer.join()
			self.alarm_duration_timer.join()
		except:
			pass
		self.beeping_timer.thread_stop()
		self.sendsms.thread_stop()
		hw.cleanup()
