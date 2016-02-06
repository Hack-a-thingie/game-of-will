import pygame
import math

class Game(object):
	
	def __init__(self):
		pygame.init()
		
		self.resl = pygame.display.Info()
		backgroundColour = (255,255,255)
		self.screen = pygame.display.set_mode((self.resl.current_w, self.resl.current_h))
		pygame.display.set_caption("Board Game")
		self.screen.fill(backgroundColour)
		
		self.initGraphics()
		
		self.drawBoard()

		
	def initGraphics(self):
		self.board = pygame.image.load("BGHackathon/BOARD.jpg")
		
	def drawBoard(self):
		self.screen.blit(pygame.transform.scale(self.board, (self.resl.current_w-400, self.resl.current_h-200)), [200,100])
		
	def update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
				
		pygame.display.flip()
				
g = Game()
while 1:
	g.update()
				
				
		