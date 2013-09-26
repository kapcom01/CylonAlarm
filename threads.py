from threading import Thread, Event, Timer
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

def print_time():
	now = datetime.now()
	now = now.strftime("%d/%m/%y %H:%M.%S")
	return now

def log(text):
	print(text)
	with open("cylonalarm.log","a") as f:
		f.write(text+"\n")

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
	def __init__(self,domain_name,config):
		BaseThread.__init__(self)
		self.domain_name = domain_name
		self.config = config
		self.text=""

	def setup_thread(self):
		self.thread = Thread(target=self.thread_action, args=(self.event,))

	def send_mail(self):
		sender = self.config["settings"]["mail_sender"]
		recipients = self.config["settings"]["mail_receipents"]
		msg = MIMEText(self.text)
		msg['Subject'] = "ALARM! <" + self.domain_name + ">"
		msg['From'] = sender
		msg['To'] = ", ".join(recipients)

		 
		# Credentials (if needed)
		username = self.config["settings"]["mail_username"]
		password = self.config["settings"]["mail_password"]
		 
		# The actual mail send
		server = smtplib.SMTP('smtp.gmail.com:587')
		server.starttls()
		server.login(username,password)
		server.sendmail(sender, recipients, msg.as_string())
		server.quit()

	def thread_action(self,stop_event):
		log(print_time()+" ["+self.domain_name+"] Sending SMS...")
		self.send_mail()

	def set_text(self,text):
		self.text=text

class Action(BaseThread):
	def __init__(self,on_state_actions,hardware,video):
		BaseThread.__init__(self)
		self.on_state_actions = on_state_actions
		self.actions = []
		self.hardware=hardware
		self.video=video

	def setup_thread(self):
		self.thread = Thread(target=self.thread_action, args=(self.event,))

	def new_state_set(self,state):
		self.actions = self.on_state_actions[state]
		self.thread_start()

	def thread_action(self, stop_event):
		a=[]
		for a in self.actions:
			if a["loop"]=="no":
				if a["type"]=="free_gpios":
					a["hardcoded_method"](a["pin"])
				elif a["type"]=="video":
					a["hardcoded_method"](a["images"])
		while not stop_event.is_set():
			for a in self.actions:
				if a["loop"]=="yes":
					if a["type"]=="free_gpios":
						a["hardcoded_method"](a["pin"])
						self.event.wait(1)
					elif a["type"]=="video":
						a["hardcoded_method"](a["images"])

	def thread_stop(self):
		self.hardware.reset_to_default_states()
		BaseThread.thread_stop(self)

class CylonAlarm():
	def __init__(self,domain_id,config,on_state_actions,hardware,video):
		self.domain_id = domain_id
		self.config = config
		self.hardware=hardware
		self.video=video

		self.state = ""

		for domain in self.config["domains"]:
			if domain["id"]==self.domain_id:
				self.domain_name=domain["name"]

		for zone in config["connections"]["zones"]:
			for domain in zone["domain"]:
				if domain == self.domain_id:
					self.hardware.addSensorEvent(zone["pin"],self.movement)

		self.activation_timer = Timer(0, self.dummy)
		self.alarm_delay_timer = Timer(0, self.dummy)
		self.alarm_duration_timer = Timer(0, self.dummy)
		self.action_thread=Action(on_state_actions,self.hardware,self.video)
		self.sendsms = SendSMS(self.domain_name,self.config)
		log("\n"+print_time()+" ["+self.domain_name+"] \033[92mRunning...\033[0m Press Ctrl+C to exit")
		self.deactivate() # todo

	# just a workaround to be able to call activation_timer.cancel() without being really started
	def dummy(self):
		pass

	def is_deactivated(self):
		if self.state == "deactivated":
			return True
		else:
			return False

	def actdeact(self):
		if self.is_deactivated():
			self.sactivate()
		else:
			self.deactivate()

	def sactivate(self):
		self.action_thread.thread_stop()
		log(print_time()+" ["+self.domain_name+"] Activating in "+str(self.config["settings"]["activation_wait"])+" seconds...")
		self.state = "activating"				
		self.activation_timer = Timer(self.config["settings"]["activation_wait"],self.start_sensing)
		self.activation_timer.start()
		self.action_thread.new_state_set(self.state)

	def deactivate(self):
		self.action_thread.thread_stop()
		self.activation_timer.cancel()
		self.alarm_delay_timer.cancel()
		self.alarm_duration_timer.cancel()
		self.stop_sensing()
		self.state = "deactivated"
		log(print_time()+" ["+self.domain_name+"] \033[93mDeactivated\033[0m")
		self.action_thread.new_state_set(self.state)

	def check_all_zones_state(self):
		for zone in self.config["connections"]["zones"]:
			for domain in zone["domain"]:
				if domain == self.domain_id and self.hardware.getSensorInAfterDelay(zone["pin"]):
					return zone["pin"]
		return 0

	def start_sensing(self):
		self.action_thread.thread_stop()
		self.state = "activated"
		log(print_time()+" ["+self.domain_name+"] \033[93mActivated\033[0m")
		self.action_thread.new_state_set(self.state)
		# if a zone is already opened (workaround)
		active_zone = self.check_all_zones_state()
		if active_zone:
			self.movement(active_zone)

	def stop_sensing(self):
		self.action_thread.thread_stop()

	def movement(self,channel):
		pass_check = self.hardware.getSensorInAfterDelay(channel) and self.state=="activated" and not self.state=="alarming" and not self.alarm_delay_timer.isAlive()
		if pass_check:
			self.action_thread.thread_stop()
			self.stop_sensing()
			self.state = "movement"
			for zone in self.config["connections"]["zones"]:
				if zone["pin"] == channel:
					if zone["level"] == 1:
						self.alarm_delay_timer = Timer(self.config["settings"]["alarm_delay"],self.sound_the_alarm)
						self.alarm_delay_timer.start()
						self.action_thread.new_state_set(self.state)
					elif zone["level"] == 2:
						self.sound_the_alarm()
					break
			for zone in self.config["connections"]["zones"]:
				if channel==zone["pin"]:
					zone_name=zone["name"]
					break
			self.sendsms.set_text(print_time()+" ["+self.domain_name+"] Movement detected at Zone <"+zone_name+">.")
			log(print_time()+" ["+self.domain_name+"]\033[1;97m Movement detected at Zone <"+zone_name+">, you have "+str(self.config["settings"]["alarm_delay"])+" seconds...\033[0m")

	def sound_the_alarm(self):
		self.action_thread.thread_stop()
		for siren in self.config["connections"]["sirens"]:
			for domain in siren["domain"]:
				if domain == self.domain_id:
					self.hardware.high(siren["pin"])
		self.state = "alarming"
		log("\033[91m"+print_time()+" ["+self.domain_name+"] <<<  ALERT  >>>\033[0m")
		self.sendsms.thread_start()
		self.alarm_duration_timer = Timer(self.config["settings"]["alarm_duration"],self.stop_the_alarm)
		self.alarm_duration_timer.start()
		self.action_thread.new_state_set("alarming")

	def stop_the_alarm(self):
		for siren in self.config["connections"]["sirens"]:
			for domain in siren["domain"]:
				if domain == self.domain_id:
					self.hardware.low(siren["pin"])
		log(print_time()+" ["+self.domain_name+"]\033[1;97m Alarm stopped\033[0m")

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
		self.action_thread.thread_stop()
		self.sendsms.thread_stop()
