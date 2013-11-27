from threading import Thread, Event, Timer
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
import socket
import json
import logging
import pdb

def print_time():
	now = datetime.now()
	now = now.strftime("%d/%m/%y %H:%M.%S")
	return now

def log(text):
	logging.info(text)
	with open("logs/cylonalarm.log","a") as f:
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

class CylonSocket(BaseThread):
	def __init__(self,ca,config):
		BaseThread.__init__(self)
		self.ca = ca
		self.config = config
		self.sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		self.sock.bind(('127.0.0.1',5000))
		self.sock.listen(5)

	def setup_thread(self):
		self.thread = Thread(target=self.thread_action, args=(self.event,))

	def thread_action(self,stop_event):
		while not stop_event.is_set():
			client, address = self.sock.accept() 
			data = client.recv(1024)
			data = json.loads(data)
			# AJAX
			if "nfc_call" in data:
				self.nfc_call(data["nfc_call"]["tag_id"],data["nfc_call"]["domain_id"])
			elif "actdeact" in data:
				client.send(self.ca[int(data["actdeact"]["domain_id"])].actdeact())
			elif "status" in data:
				res = {
				"status": []
				}
				for domain in self.config["domains"]:
					state = self.ca[domain["id"]].state
					res["status"].append({
						"domain_id": str(domain["id"]),
						"domain_name": str(domain["name"]),
						"state": state
						})
				client.send(json.dumps(res))
			client.close()

	def nfc_call(self,tag_id,domain_id):
		for tag in self.config["tags"]:
			if tag["id"] == tag_id:
				for domain in tag["domain_id"]:
					if domain==int(domain_id):
						self.ca[int(domain_id)].actdeact()

	def thread_stop(self):
		self.event.set()
		# REALLY UGLY BUG HERE ##########
		print("Ugly workaround:")
		from subprocess import call
		call(["python", "lib/jsonsockclient.py", "webapp@@gskjw734", "1"])
		###########################################
		self.sock.close()
		BaseThread.thread_stop(self)
		print("ok, sockets closed")

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
	def __init__(self,action,on_state_actions,hardware,video):
		BaseThread.__init__(self)
		self.on_state_actions = on_state_actions
		self.action = action
		self.thread_pool=[]
		self.hardware=hardware
		self.video=video

	def setup_thread(self):
		self.thread = Thread(target=self.thread_action, args=(self.event,))

	def new_state_set(self,state):
		actions = self.on_state_actions[state]
		for a in actions :
			new_action_thread=Action(a,None,self.hardware,self.video)
			self.thread_pool.append(new_action_thread)
			logging.debug("added new action thread:")
			logging.debug(a)
		for action_thread in self.thread_pool :
			action_thread.thread_start()

	def thread_action(self, stop_event):
		if self.action["loop"]=="no":
			logging.debug("run thread: %s"%self.thread.ident)
			if self.action["type"]=="free_gpios":
				self.action["hardcoded_method"](self.action["pin"])
			elif self.action["type"]=="video":
				self.action["hardcoded_method"](self.action["images"])
		while not stop_event.is_set():
			if self.action["loop"]=="yes":
				logging.debug("loop thread: %s"%self.thread.ident)
				if self.action["type"]=="free_gpios":
					self.action["hardcoded_method"](self.action["pin"])
					self.event.wait(1)
				elif self.action["type"]=="video":
					self.action["hardcoded_method"](self.action["images"])

	def thread_stop(self):
		if self.action==None:
			logging.debug("killing action thread pool:")
			for action_thread in self.thread_pool:
				action_thread.thread_stop()
			self.thread_pool=[]
			logging.debug("killed all.")
			self.hardware.reset_to_default_states()
		else:
			logging.debug("killing action thread (%s)"%self.thread.ident)
			logging.debug(self.action)
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
		self.action_thread=Action(None,on_state_actions,self.hardware,self.video)
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
			return self.sactivate()
		else:
			return self.deactivate()

	def sactivate(self):
		self.action_thread.thread_stop()
		log(print_time()+" ["+self.domain_name+"] Activating in "+str(self.config["settings"]["activation_wait"])+" seconds...")
		self.state = "activating"				
		self.activation_timer = Timer(self.config["settings"]["activation_wait"],self.start_sensing)
		self.activation_timer.start()
		self.action_thread.new_state_set(self.state)
		return self.state

	def deactivate(self):
		self.action_thread.thread_stop()
		self.activation_timer.cancel()
		self.alarm_delay_timer.cancel()
		self.alarm_duration_timer.cancel()
		self.stop_sensing()
		self.state = "deactivated"
		log(print_time()+" ["+self.domain_name+"] \033[93mDeactivated\033[0m")
		self.action_thread.new_state_set(self.state)
		return self.state

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
		pass_check = self.hardware.getSensorInAfterDelay(channel) and self.state=="activated" and not self.alarm_delay_timer.isAlive()
		if pass_check:
			self.action_thread.thread_stop()
			self.stop_sensing()
			self.state = "movement"
			for zone in self.config["connections"]["zones"]:
				if zone["pin"] == channel:
					zone_name=zone["name"]
					if zone["level"] == 1:
						self.sendsms.set_text(print_time()+" ["+self.domain_name+"] Movement detected at Zone <"+zone_name+">.")
						log(print_time()+" ["+self.domain_name+"]\033[1;97m Movement detected at Zone <"+zone_name+">, you have "+str(self.config["settings"]["alarm_delay"])+" seconds...\033[0m")

						self.alarm_delay_timer = Timer(self.config["settings"]["alarm_delay"],self.sound_the_alarm)
						self.alarm_delay_timer.start()
						self.action_thread.new_state_set(self.state)
					elif zone["level"] == 2:
						self.sendsms.set_text(print_time()+" ["+self.domain_name+"] Movement detected at Zone <"+zone_name+">. (Level=2)")
						log(print_time()+" ["+self.domain_name+"]\033[1;97m Movement detected at Zone <"+zone_name+">. (Level=2)")

						self.sound_the_alarm()
					break

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
		self.action_thread.thread_stop()
		for siren in self.config["connections"]["sirens"]:
			for domain in siren["domain"]:
				if domain == self.domain_id:
					self.hardware.low(siren["pin"])
		log(print_time()+" ["+self.domain_name+"]\033[1;97m Alarm stopped\033[0m")
		self.action_thread.new_state_set("activated")

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
