import pygame
import math
import os
from random import shuffle
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

class BoardGame(ConnectionListener):
	
	def __init__(self):	
	
		self.on_image = 0
		
		pygame.init()
		self.resl = pygame.display.Info()
		background_colour = (255,255,255)	
		
		#load images
		self.initGraphics()	
	
		#init clock
		self.clock=pygame.time.Clock()	
		
		self.take_deck_pos = Rect(10,400,300,200)
		self.discard_deck_pos = Rect(250,400,300,200)
		
		#define stages
		self.stage = None

		#connect to network		
		self.Connect()
		self.gameid = None
		self.num = None
		
		#search for server
		self.running = False
		while not self.running:
			self.Pump()
			connection.Pump()
			sleep(0.01)
			
		#player[0] starts
		if self.num == 0:
			self.turn = True
		else:
			self.turn = False
			
		#init pygame, find screen resolution, define scree
		self.screen = pygame.display.set_mode((self.resl.current_w, self.resl.current_h))
		pygame.display.set_caption("Board Game")
		self.screen.fill(background_colour)
		
		self.players = [Player() for i in range(self.player_num)]
			
		#delay to prevent multiple actions before server responds
		self.justclicked = 10
		
	def Network_setgame(self,data):
		player_num = input("How many players?:")
		self.Send({"action":"setgame","player_num":player_num})
		print "searching for other players..."
		
	def Network_startgame(self,data):
		#recieve server data on game commencement
		self.running = True
		self.num = data["player"]
		self.gameid = data["gameid"]
		self.stage = data["stage"]
		self.p_races = data["p_races"]
		self.s_races = data["s_races"]
		self.player_num = data["player_num"]
		
		#self.take_deck = data["takedeck"]
		#self.discard_deck = data["discarddeck"]
		
	def Network_cardplay(self,data):
		#recieve server data on turn
		self.stage = data["stage"]
		
	def Network_pracechoose(self,data):
		self.turn = 1 if data["turn"] == self.num else 0
		self.players[data["player"]].primerace = data["prace"]
		self.p_races.remove(data["prace"])
		self.stage = data["stage"]
		
	def Network_sracechoose(self,data):
		self.turn = 1 if data["turn"] == self.num else 0
		self.players[data["player"]].secrace = data["srace"]
		self.s_races.remove(data["srace"])
		self.stage = data["stage"]
		
	def Network_takecard(self,data):
		self.choosecards = data["cards"]
		self.stage = data["stage"]
		
	def Network_cardgain(self,data):
		self.turn = 1 if data["turn"] == self.num else 0
		self.players[data["player"]].hand.append(data["card"])
		self.stage = data["stage"]
		
	def initGraphics(self):
		#load board image
		self.board = pygame.image.load("BGHackathon/BOARD.jpg")
		
		#load card images
		self.cardIms = []
		self.primary_races = []
		self.secondary_races = []
		for i in os.listdir("BGHackathon"):
			if i.startswith("CARD"):
				self.cardIms.append(pygame.image.load("BGHackathon/"+i))
			elif i.startswith("RACEprimary"):
				self.primary_races.append(pygame.image.load("BGHackathon/"+i))
			elif i.startswith("RACEsecondary"):
				self.secondary_races.append(pygame.image.load("BGHackathon/"+i))
				
		#initialize text
		self.largeText = pygame.font.Font('freesansbold.ttf',40)
		self.TextSurf, self.TextRect = self.text_objects("Skip Card Phase?", self.largeText)
		self.TextRect.center = (self.resl.current_w/2,self.resl.current_h/2)
				
	def drawBoard(self):
		#draw board at screen resolution
		self.screen.blit(pygame.transform.scale(self.board, (self.resl.current_w-400, self.resl.current_h-200)), [200,100])
		
	def drawPlayerCards(self):
		#draw players cards
		my_hand = RectArray(5,5,200,150,0,100,len(self.players[self.num].hand))
		for j in range(len(self.players[self.num].hand)):
			self.screen.blit(pygame.transform.scale(self.cardIms[self.players[self.num].hand[j]], (my_hand.r_array[j].w,my_hand.r_array[j].h)),(my_hand.r_array[j].x,my_hand.r_array[j].y))
		for i in range(self.num+1,self.num+self.player_num):
				their_hand = RectArray(self.resl.current_w-205,5+300*(i-1-self.num),200,150,0,40,len(self.players[i%self.player_num].hand))
				for j in range(len(self.players[i%self.player_num].hand)):
					self.screen.blit(pygame.transform.scale(self.cardIms[self.players[i%self.player_num].hand[j]], (their_hand.r_array[j].w,their_hand.r_array[j].h)),(their_hand.r_array[j].x,their_hand.r_array[j].y))
		
	def drawDecks(self):
		self.screen.blit(pygame.transform.scale(self.secondary_races[1], [self.take_deck_pos.w,self.take_deck_pos.h]),[self.take_deck_pos.x,self.take_deck_pos.y])
		#if self.discard_deck.deck:
			#self.screen.blit(pygame.transform.scale(self.cardIms[self.discard_deck.deck[-1]], [self.discard_deck_pos.w,self.discard_deck_pos.h]),[self.discard_deck_pos.x,self.discard_deck_pos.y])
		
	def text_objects(self, text, font):
		#use for creating textboxes
		textSurface = font.render(text, True, [0,0,0])
		return textSurface, textSurface.get_rect()
		
	def update(self):
		#main loop
		
		if self.on_image:
			pygame.mouse.set_cursor(*pygame.cursors.diamond)
		else:
			pygame.mouse.set_cursor(*pygame.cursors.arrow)
			
		self.on_image = False
			
		#decrement just clicked
		self.justclicked-=1
		
		#recieve server data
		connection.Pump()
		self.Pump()
	
		#60 fps
		self.clock.tick(60)
		
		#refresh screen
		self.screen.fill([255,255,255])
		self.drawBoard()
		
		#check for exit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
				
		xpos, ypos = pygame.mouse.get_pos()
	
		if self.stage == "choose p race":
			p_race_r = RectArray(100,250,300,200,210,0,len(self.p_races))
			for i in range(len(self.p_races)):
				(self.screen.blit(pygame.transform.scale(self.primary_races[self.p_races[i]],
				[p_race_r.r_array[i].w,p_race_r.r_array[i].h]),[p_race_r.r_array[i].x,p_race_r.r_array[i].y]))
			for i in range(len(self.p_races)):
				if p_race_r.r_array[i].withinRect(xpos,ypos) and self.turn == True:
					self.on_image = True
					if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
						self.Send({"action":"choose_p_race","p race":self.p_races[i],"gameid":self.gameid,"num":self.num})
						self.justclicked = 10
					
		elif self.stage == "choose s race":
			s_race_r = RectArray(100,250,300,200,210,0,len(self.s_races))
			for i in range(len(self.s_races)):
				(self.screen.blit(pygame.transform.scale(self.secondary_races[self.s_races[i]],
				[s_race_r.r_array[i].w,s_race_r.r_array[i].h]),[s_race_r.r_array[i].x,s_race_r.r_array[i].y]))
			for i in range(len(self.s_races)):
				if s_race_r.r_array[i].withinRect(xpos,ypos) and self.turn == True:
					self.on_image = True
					if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
						self.Send({"action":"choose_s_race","s race":self.s_races[i],"gameid":self.gameid,"num":self.num})
						self.justclicked = 10
			
		#if in card phase check action and send data to server
		elif self.stage == "card phase":
			self.drawPlayerCards()
			self.drawDecks()	
			if self.turn == True:
				if self.TextRect[0] < xpos < self.TextRect[0]+ self.TextRect[2] and self.TextRect[1] < ypos < self.TextRect[1]+ self.TextRect[3]:
					self.on_image = True
					if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
						self.Send({"action":"cardplay","card":"skip", "gameid":self.gameid,"num":self.num})
						self.justclicked = 10
					else:
						pygame.draw.rect(self.screen,[0,200,0],	self.TextRect)							
						self.screen.blit(self.TextSurf, self.TextRect)
				else:
					pygame.draw.rect(self.screen,[255,255,255],	self.TextRect)
					self.screen.blit(self.TextSurf, self.TextRect)

		elif self.stage == "action phase":
			self.drawPlayerCards()
			self.drawDecks()
			if self.turn == True:
				if self.take_deck_pos.withinRect(xpos,ypos):
					self.on_image = True
					if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
						self.Send({"action":"takecard","takenumber":self.players[self.num].card_pickup_number,"gameid":self.gameid,"num":self.num})
						self.justclicked = 10
					
	
		elif self.stage == "choose card":
			self.drawPlayerCards()
			self.drawDecks()	
			if self.turn == True:
				top_deck = RectArray(300,250,300,200,210,0,len(self.choosecards))
				for i in range(len(self.choosecards)):
					(self.screen.blit(pygame.transform.scale(self.cardIms[self.choosecards[i]],
					[top_deck.r_array[i].w,top_deck.r_array[i].h]),[top_deck.r_array[i].x,top_deck.r_array[i].y]))			
				for i in range(len(self.choosecards)):
					if top_deck.r_array[i].withinRect(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"cardchosen","card":self.choosecards[i],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
				
		pygame.display.flip()
				
class Player(object):

	def __init__(self):
		self.hand_limit = 1
		self.hand = []
		self.card_pickup_number = 3
		self.turn = False
		self.primerace = None
		self.secrace = None
		
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
		
class Rect(object):
	def __init__(self,x,y,h,w):
		self.x = x
		self.y = y
		self.h = h
		self.w = w
		
	def withinRect(self,xpos,ypos):
		if self.x < xpos < self.x + self.w and self.y < ypos < self.y + self.h:
			return True
		else:
			return False
			
		
		
class RectArray(object):
	def __init__(self,x,y,h,w,x_trans,y_trans,number_rectangles):
		self.r_array = []
		for i in range(number_rectangles):
			self.r_array.append(Rect(x+i*x_trans,y+i*y_trans,h,w))
					
g = BoardGame()
while 1:
	g.update()
				
				
		