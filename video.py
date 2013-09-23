import sys
import os
import pygame
from pygame.locals import*

lib_path = os.path.abspath('lib/')
sys.path.append(lib_path)

from adafruit.pyscope import pyscope

class CylonVideo():
	def __init__(self):
		# TODO : na fortoso oles tis eikones apo tin arxi
		white = (255, 255, 255)
		w = 656
		h = 416

		self.scope = pyscope()

		pygame.mouse.set_visible(False)

		self.scope.screen = pygame.display.set_mode((w, h))
		self.scope.screen.fill((white))

		self.clock = pygame.time.Clock()

	def show_welcome(self):
		image = pygame.image.load('images/welcome.jpg')
		self.scope.screen.blit(image,(0,0))
		pygame.display.update()

	def show_image(self,filename):
		image = pygame.image.load('images/'+filename[0])
		self.scope.screen.blit(image,(0,0))
		pygame.display.update()

	def animate_images(self,filenames):
		images=[]
		for filename in filenames:
			images.append(pygame.image.load('images/'+filename))
		for image in images:
			self.clock.tick(2)
			self.scope.screen.blit(image,(0,0))
			pygame.display.update()
