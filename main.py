import pygame
import math
import hex
import os
from random import shuffle

class Game(object):
	
	def __init__(self):
		pygame.init()
		
		self.resl = pygame.display.Info()
		background_colour = (255,255,255)
		self.screen = pygame.display.set_mode((self.resl.current_w, self.resl.current_h))
		pygame.display.set_caption("Board Game")
		self.screen.fill(background_colour)
		
		self.initGraphics()		
		self.drawBoard()
		
		self.take_deck = Deck(10)
		self.discard_deck = Deck(0)
		
		self.players = [Player() for i in range(4)]

		self.players[0].takeCard(self.take_deck)
		self.players[1].takeCard(self.take_deck)
		self.players[2].takeCard(self.take_deck)
		self.players[3].takeCard(self.take_deck)
		
	def initGraphics(self):
		self.board = pygame.image.load("BGHackathon/BOARD.jpg")
		self.cardIms = []
		for i in os.listdir("BGHackathon"):
			if i.startswith("CARD"):
				self.cardIms.append(pygame.image.load("BGHackathon/"+i))
				
	def drawBoard(self):
		self.screen.blit(pygame.transform.scale(self.board, (self.resl.current_w-400, self.resl.current_h-200)), [200,100])
		
	def drawPlayerCards(self):
		for i in range(len(self.players)):
			for j in range(len(self.players[i].hand)):
				self.screen.blit(pygame.transform.scale(self.cardIms[self.players[i].hand[j]], (150,200)),(5+j*10,5))
		
		
	def update(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
				
		xpos, ypos = pygame.mouse.get_pos()
		if xpos < 200:
			self.screen.blit(self.cardIms[self.players[0].hand[0]],[200,100])	
			
		self.drawPlayerCards()		
				
		pygame.display.flip()
		
class Deck(object):

	def __init__(self,number_cards):
		self.deck = [i for i in range(1,number_cards) for _ in range(3)]
		self.shuffleDeck()
		
	def shuffleDeck(self):
		shuffle(self.deck)
		
class Player(object):

	def __init__(self):
		self.hand_limit = 1
		self.hand = []
		self.card_pickup_number = 3
		self.turn = False
		
	def increaseHandLimit(self,x):
		self.hand_limit = self.hand_limit + x
		
	def decreaseHandLimit(self,x):
		self.hand_limit = self.hand_limit - x
		
	def takeCard(self,card_deck):
		self.hand.append(card_deck.deck.pop())
	
	def endTurn(self):
		self.turn = False
		
	def startTurn(self):
		self.turn = True
				
g = Game()
while 1:
	g.update()
				
				
		