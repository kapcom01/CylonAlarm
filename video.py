import sys
import os
import pygame
from pygame.locals import*

lib_path = os.path.abspath('lib/')
sys.path.append(lib_path)

from adafruit.pyscope import pyscope

class CylonVideo():
	def __init__(self,config):

		self.images={}
		for action in config["actions"]:
			if config["actions"][action]["type"]=="video":
				for filename in config["actions"][action]["images"]:
					self.images[filename] = pygame.image.load('images/'+filename)

		white = (255, 255, 255)
		w = 656
		h = 416

		self.scope = pyscope()

		pygame.mouse.set_visible(False)

		self.scope.screen = pygame.display.set_mode((w, h))
		self.scope.screen.fill((white))

		self.clock = pygame.time.Clock()

	def show_image(self,filename):
		self.scope.screen.blit(self.images[filename[0]],(0,0))
		pygame.display.update()

	def animate_images(self,filenames):
		for filename in filenames:
			self.clock.tick(2)
			self.scope.screen.blit(self.images[filename],(0,0))
			pygame.display.update()
