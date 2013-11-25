import logging
from time import sleep

class CylonVideo():
	def __init__(self,config):
		logging.debug("[video] init")

	def show_image(self,filename):
		logging.debug("[video] show_image()")

	def animate_images(self,filenames):
		logging.debug("[video] animate_images()")
		sleep(0.5)