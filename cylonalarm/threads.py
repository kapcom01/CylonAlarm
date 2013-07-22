from hardware import SynHardware
from threading import Timer, Thread, Event
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from subprocess import call

import config #temporary configuration file

class SynBase:
	def __init__(self):
		self.xronos_seirhnas = config.alarm_duration
		self.state = "DEACTIVATED"

class SynThreads(SynBase):
	def __init__(self):
		SynBase.__init__(self)

		self.e_activate = Event()
		self.e_alarm_seirhna = Event()
		self.e_sense_movement = Event()

		self.hw = SynHardware()

	def alarm_seirhna_start(self):
		self.alarm_seirhna_stop()
		self.e_alarm_seirhna.clear()
		self.alarm_seirhna = Thread(target=self.t_alarm_seirhna, args=(self.xronos_seirhnas, self.e_alarm_seirhna))
		self.alarm_seirhna.start()

	def alarm_seirhna_stop(self):
		self.e_alarm_seirhna.set()
		try:
			self.alarm_seirhna.join()
		except:
			pass

	def t_alarm_seirhna(self,xronos,stop_event):
		if not stop_event.is_set():
			self.hw.alarm_on()
			print("\033[91m["+self.print_time()+"] <<<  ALERT  >>>\033[0m")
			self.send_sms()
			stop_event.wait(xronos)
			print("["+self.print_time()+"]\033[1;97m Alarm stopped\033[0m")
		self.hw.alarm_off()

	def sense_movement_start(self):
		self.sense_movement_stop()
		self.e_sense_movement.clear()
		self.sense_movement = Thread(target=self.t_sense_movement, args=(self.e_sense_movement,))
		self.sense_movement.start()

	def sense_movement_stop(self):
		self.e_sense_movement.set()
		try:
			self.sense_movement.join()
		except:
			pass

	def t_sense_movement(self,stop_event):
		while(not stop_event.is_set()):
			stop_event.wait(0.1) # 98% cpu usage without it
			if self.hw.getSensorIn() and self.state == "ACTIVATED" and not self.hw.isAlarming():
				print("["+self.print_time()+"]\033[1;97m Movement detected (>500ms)\033[0m")
				for seconds_to_alarm in range(0,10):
					if self.state == "ACTIVATED":
						if seconds_to_alarm == 9: self.alarm_seirhna_start()
						else:
							self.hw.double_bleep()
							stop_event.wait(1)
					else: break

	def activate_start(self):
		self.activate_stop()
		self.e_activate.clear()
		self.activate = Thread(target=self.t_activate, args=(15, self.e_activate))
		self.activate.start()

	def activate_stop(self):
		self.e_activate.set()
		try:
			self.activate.join()
		except:
			pass

	def t_activate(self, secs, stop_event):
		if self.state == "DEACTIVATED":
			print("["+self.print_time()+"] Activating in "+str(secs)+" seconds...")
			#with open("synagermos.log", "a") as f:
			#	f.write("["+self.print_time()+"] Activating in "+str(secs)+" seconds...")

		self.state = "ACTIVATING"

		for seconds_to_activation in range(0, secs):
			if not stop_event.is_set():
				if seconds_to_activation < secs-1:
					self.hw.double_bleep()
					stop_event.wait(1)
				else:
					self.hw.led_on()
					self.sense_movement_start()
					self.state = "ACTIVATED"
					print("["+self.print_time()+"] \033[93mActivated\033[0m")
					break

	def stop_all_threads(self):
		self.activate_stop()
		self.alarm_seirhna_stop()
		self.sense_movement_stop()

	def t_deactivate(self):
		self.activate_stop()
		self.alarm_seirhna_stop()
		self.hw.bleep()
		self.state = "DEACTIVATED"
		print("["+self.print_time()+"] \033[93mDeactivated\033[0m")

	def send_mail(self):
		msg = MIMEText("""Synagermos tora!""")
		sender = config.mail_sender
		recipients = config.mail_receipents
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

	def send_sms(self):
		print("["+self.print_time()+"] Sending SMS...")
		self.send_mail()

	def print_time(self):
		now = datetime.now()
		now = now.strftime("%d/%m/%y %H:%M.%S")
		return now

class SynControl(SynThreads):
	def __init__(self):
		SynThreads.__init__(self)
		print("\n["+self.print_time()+"] \033[92mRunning...\033[0m Press Ctrl+C to exit")

	def sactivate(self):
		self.activate_start()

	def deactivate(self):
		self.t_deactivate()

	def cleanup(self):
		self.stop_all_threads()
