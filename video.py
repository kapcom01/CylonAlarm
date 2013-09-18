import sys
import os
import pygame
from pygame.locals import*

lib_path = os.path.abspath('lib/')
sys.path.append(lib_path)

from adafruit.pyscope import pyscope

class CylonVideo():
	def __init__(self):
		self.nfc = [pygame.image.load('images/nfc-up.jpg'),pygame.image.load('images/nfc-down.jpg')]
		self.door = [pygame.image.load('images/door-opened.jpg'),pygame.image.load('images/door-closed.jpg')]
		self.welcome = pygame.image.load('images/welcome.jpg')
		white = (255, 255, 255)
		w = 656
		h = 416

		self.scope = pyscope()

		pygame.mouse.set_visible(False)

		self.scope.screen = pygame.display.set_mode((w, h))
		self.scope.screen.fill((white))

		self.clock = pygame.time.Clock()

	def show_welcome(self):
		self.scope.screen.blit(self.welcome,(0,0))
		pygame.display.update()

	def animate_door(self):
		for image in self.door:
			self.clock.tick(2)
			self.scope.screen.blit(image,(0,0))
			pygame.display.update()

	def animate_nfc(self):
		for image in self.nfc:
			self.clock.tick(2)
			self.scope.screen.blit(image,(0,0))
			pygame.display.update()
