import pygame
import math
import os
import hex
#from hex import Hexagon, Hexgrid
from random import shuffle
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep
class BoardGame(ConnectionListener):
	
	def __init__(self):				
		#init pygame get screen resolution set backgroud white
		pygame.init()
		self.resl = pygame.display.Info()
		background_colour = (255,255,255)	
		
		#load images
		self.initGraphics()
	
		#init clock
		self.clock=pygame.time.Clock()	
		
		#position to draw deck objects
		self.take_deck_pos = Rect(10,400,300,200)
		self.discard_deck_pos = Rect(250,400,300,200)
		
		#rectangle where enlarged cards are shown
		self.enlarge_rect = Rect(400,200,500,350)
		
		#used to define stages of player's turn
		self.stage = None

		#connect to server			
		address = raw_input("Address of Server: ")
		try:
			if not address:
				host, port="localhost", 8000
			else:
				host, port=address.split(":")
			self.Connect((host,int(port)))
		except:
			print "Error Connecting to Server"
			print "Usage:", "host:port"
			print "e.g.", "localhost:31425"
			exit()
		print "Boxes client started"
		
		#game id and player number assigned by server
		self.gameid = None
		self.num = None
		
		#listen for server communication
		self.running = False
		while not self.running:
			self.Pump()
			connection.Pump()
			sleep(0.01)
			
		#player 0 starts
		if self.num == 0:
			self.turn = True
		else:
			self.turn = False
			
		#display screen	
		self.screen = pygame.display.set_mode((self.resl.current_w, self.resl.current_h))
		pygame.display.set_caption("Board Game")
		self.screen.fill(background_colour)
		
		self.hexgrd = hex.Hexgrid(round((self.resl.current_w-400)/30),350,150,self.screen)
		self.hexgrd.setstartterr([[1,1],[5,7],[1,2],[4,6],[5,6]])
		
		#initialise players
		self.players = []
		for i in range(self.player_num):
			if i == self.num:
				self.players.append(Player(5,5))
			else:
				self.players.append(Player(self.resl.current_w-205,5+250*(((self.num-i)%self.player_num)-1)))
			
		#keep track of recent clicks and cursor hover action
		self.justclicked = 10
		self.on_image = 0

		
	def Network_setgame(self,data):
		#first person to connect to server determines player number
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
	
	def Network_endgame(self,data):
#		self.hexgrd.score()
		pass
		
	def Network_cardplay(self,data):
		#result of played card action
		self.playingcard = data["card"]
		self.stage = data["stage"]
		
	def Network_placehex(self,data):
		print "trying to place"
		#result of played card action
		self.hexgrd.change_owner(data["player"],data["position"][0],data["position"][1])
		self.stage = data["stage"]
		self.turn = 1 if data["turn"] == self.num else 0
		
	def Network_cardplacehex(self,data):
		#result of played card action
		self.hexgrd.change_owner(data["player"],data["position"][0],data["position"][1])
		self.players[data["player"]].hand.remove(data["card"])
		self.stage = data["stage"]
		self.turn = 1 if data["turn"] == self.num else 0

	def Network_cardremovehex(self,data):
		#result of played card action
		self.hexgrd.change_owner(100,data["position"][0],data["position"][1])
		self.players[data["player"]].hand.remove(data["card"])
		self.stage = data["stage"]
		self.turn = 1 if data["turn"] == self.num else 0
		
	def Network_losecard(self,data):
		#result of played card action
		self.players[data["player"]].hand.remove(data["card"])
		self.players[data["loseplayer"]].hand.remove(data["losecard"])
		self.stage = data["stage"]
		
	def Network_pracechoose(self,data):
		#result of primary race choice action
		self.turn = 1 if data["turn"] == self.num else 0
		self.players[data["player"]].setPrimerace(data["prace"])
		self.p_races.remove(data["prace"])
		self.stage = data["stage"]
		
	def Network_sracechoose(self,data):
		#result of secondary race choice action
		self.turn = 1 if data["turn"] == self.num else 0
		self.players[data["player"]].setSecrace(data["srace"])
		self.s_races.remove(data["srace"])
		self.stage = data["stage"]
		
	def Network_takecard(self,data):
		#result of drawing cards action
		self.choosecards = data["cards"]
		self.stage = data["stage"]
		
	def Network_cardgain(self,data):
		#result of choosing a card from draw action when there are more cards to be chosen
		self.choosecards = data["cards"]
		self.players[data["player"]].addToHand(data["card"])
		self.stage = data["stage"]
		
	def Network_cardgainend(self,data):
		#result of choosing a card from draw action when there are no more cards to be chosen
		self.turn = 1 if data["turn"] == self.num else 0
		self.players[data["player"]].addToHand(data["card"])
		self.stage = data["stage"]
		
	def Network_stopterrtake(self,data):
		#result of choosing a card from draw action when there are no more cards to be chosen
		self.players[data["stopplayer"]].preventterr = True
		self.stage = data["stage"]
		
#	def Network_cardblockhex(self,data):
		#result of choosing a card from draw action when there are no more cards to be chosen
#		self.players[data["player"]].hand.remove(data["card"])
#		self.blockhex = True
#		self.stage = data["stage"]
		
	def initGraphics(self):
		#load images from folder
		
		#load playable cards and races
		self.cardIms = []
		self.primary_races = []
		self.secondary_races = []
		for k in range(13):
			for i in os.listdir("BGHackathon"):
				if i.startswith("CARD") and i.endswith("%02d.jpg"%k):
					self.cardIms.append(pygame.image.load("BGHackathon/"+i))
			
		for i in range (6):
			self.primary_races.append(pygame.image.load("BGHackathon/RACEprimary%r.jpg"%i))
			self.secondary_races.append(pygame.image.load("BGHackathon/RACEsecondary%r.jpg"%i))
				
		self.card_back = pygame.image.load("BGHackathon/CARDback.jpg")
		
		#intitialise text
		self.largeText = pygame.font.Font('freesansbold.ttf',40)
		self.TextSurf, self.TextRect = self.text_objects("Skip Card Phase?", self.largeText)
		self.TextRect.center = (self.resl.current_w/2,self.resl.current_h/2)
				
	def drawBoard(self):
		#draw board at screen resolution
		self.hexgrd.draw_hexgrid()
		
	def drawPlayerCards(self,xpos,ypos):

		for i in range(self.player_num):
				
				for j in range(len(self.players[i].hand)):
					self.screen.blit(pygame.transform.scale(self.cardIms[self.players[i].hand[j]], (self.players[i].hand_rect_array.r_array[j].w,self.players[i].hand_rect_array.r_array[j].h)),(self.players[i].hand_rect_array.r_array[j].x,self.players[i].hand_rect_array.r_array[j].y))
					
					if self.players[i].hand_rect_array.r_array[j].withinRect(xpos,ypos):
						self.screen.blit(pygame.transform.scale(self.cardIms[self.players[i].hand[j]], (self.enlarge_rect.w,self.enlarge_rect.h)),(self.enlarge_rect.x,self.enlarge_rect.y))	
												
	def drawDecks(self):
		self.screen.blit(pygame.transform.scale(self.card_back, [self.take_deck_pos.w,self.take_deck_pos.h]),[self.take_deck_pos.x,self.take_deck_pos.y])
		
	def text_objects(self, text, font):
		#use for creating textboxes
		textSurface = font.render(text, True, [0,0,0])
		return textSurface, textSurface.get_rect()
		
	def update(self):
		
		#change cursor if hovering above legal move
		if self.on_image:
			pygame.mouse.set_cursor(*pygame.cursors.diamond)
		else:
			pygame.mouse.set_cursor(*pygame.cursors.arrow)
		self.on_image = False
			
		#decrement just clicked counter
		self.justclicked-=1
		
		#listen for server
		connection.Pump()
		self.Pump()
	
		#sets fps
		self.clock.tick(60)
		
		#refresh screen
		self.screen.fill([255,255,255])
		self.drawBoard()
		
		#check game exit
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
		
		#get mouse coordinates		
		xpos, ypos = pygame.mouse.get_pos()
	
		#check stages and legal moves
		if self.stage == "choose p race":
			p_race_r = RectArray(100,250,300,200,210,0,len(self.p_races))
			for i in range(len(self.p_races)):
				(self.screen.blit(pygame.transform.scale(self.primary_races[self.p_races[i]],
				[p_race_r.r_array[i].w,p_race_r.r_array[i].h]),[p_race_r.r_array[i].x,p_race_r.r_array[i].y]))
			for i in range(len(self.p_races)):
				if p_race_r.r_array[i].withinRect(xpos,ypos):
					(self.screen.blit(pygame.transform.scale(self.primary_races[self.p_races[i]],
					[self.enlarge_rect.w,self.enlarge_rect.h]),[self.enlarge_rect.x,self.enlarge_rect.y]))
					if self.turn == True:
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
				if s_race_r.r_array[i].withinRect(xpos,ypos):
					(self.screen.blit(pygame.transform.scale(self.secondary_races[self.s_races[i]],
					[self.enlarge_rect.w,self.enlarge_rect.h]),[self.enlarge_rect.x,self.enlarge_rect.y]))
					if self.turn == True:
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"choose_s_race","s race":self.s_races[i],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
							
		elif self.stage == "pick territories":
			if self.turn == True:
				if self.hexgrd.thistype(xpos,ypos) == "terr" and not self.hexgrd.occupied(xpos,ypos) and self.hexgrd.onboard(xpos,ypos):
					self.on_image = True
			        	if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
						self.Send({"action":"placehex","stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
						self.justclicked = 10
					
			self.drawDecks()
			self.drawPlayerCards(xpos,ypos)
			
			
		elif self.stage == "card phase":	
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
					
				if not len(self.players[self.num].hand) == 0:
					close_rect = self.players[self.num].hand_rect_array.whichRect(xpos,ypos)
					if close_rect == 100:
						pass
					else:
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"cardplay","card":self.players[self.num].hand[close_rect],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
			self.drawDecks()
			self.drawPlayerCards(xpos,ypos)
			
			
		#NEEDS TO BE GENERALISED
		elif self.stage == "card action phase":
			if self.turn == True:
				if self.playingcard == 3:
					otherplayers = range(self.player_num)
					otherplayers.remove(self.num)
					for i in otherplayers:
						close_rect = self.players[i].hand_rect_array.whichRect(xpos,ypos)
						if close_rect == 100:
							pass
						else:
							self.on_image = True
							if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
								self.Send({"action":"removeplayercard","card":self.playingcard,"removeplayer":i,"removecard":self.players[i].hand[close_rect],"gameid":self.gameid,"num":self.num})
								self.justclicked = 10
										
				elif self.playingcard == 0:
					otherplayers = range(self.player_num)
					otherplayers.remove(self.num)
					for i in otherplayers:
						close_rect = self.players[i].hand_rect_array.whichRect(xpos,ypos)
						if close_rect == 100:
							pass
						else:
							self.on_image = True
							if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
								self.Send({"action":"stopterrtake","card":self.playingcard,"player":i,"gameid":self.gameid,"num":self.num})
								self.justclicked = 10
								
				elif self.playingcard == 1:
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 15 and self.hexgrd.thistype(xpos,ypos) == "normal" and self.hexgrd.onboard(xpos,ypos) and not self.hexgrd.occupied(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"placehex","card":self.playingcard,"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
								
				elif self.playingcard == 2:
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and self.hexgrd.onboard(xpos,ypos) and self.hexgrd.occupied(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"placehex","card":self.playingcard,"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
								
				elif self.playingcard == 10:
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and self.hexgrd.onboard(xpos,ypos) and self.hexgrd.occupied(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"placehex","card":self.playingcard,"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
								
				elif self.playingcard == 11:
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and self.hexgrd.onboard(xpos,ypos) and self.hexgrd.occupied(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"placehex","card":self.playingcard,"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
								
				elif self.playingcard == 12:
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and self.hexgrd.onboard(xpos,ypos) and self.hexgrd.occupied(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"placehex","card":self.playingcard,"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10

#				elif self.playingcard == 9:
#					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and not self.hexgrd.occupied(xpos,ypos):
#						self.on_image = True
#							if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
#								self.Send({"action":"place2hex","stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
#								self.justclicked = 10
								
				elif self.playingcard == 8:
					print self.hexgrd.occupied(xpos,ypos)
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and self.hexgrd.numterr(xpos,ypos) <= 3 + self.players[self.num].attackbonus and self.hexgrd.onboard(xpos,ypos) and self.hexgrd.occupied(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"removehex","card":self.playingcard,"opponent":self.hexgrd.occupied_by(xpos,ypos),"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
								
				elif self.playingcard == 7:
					print self.hexgrd.occupied(xpos,ypos)
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and self.hexgrd.numterr(xpos,ypos) <= 2 + self.players[self.num].attackbonus and self.hexgrd.onboard(xpos,ypos) and self.hexgrd.occupied(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"removehex","card":self.playingcard,"opponent":self.hexgrd.occupied_by(xpos,ypos),"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
								
				elif self.playingcard == 6:
					print self.hexgrd.occupied(xpos,ypos)
					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and self.hexgrd.numterr(xpos,ypos) <= 1 + self.players[self.num].attackbonus and self.hexgrd.occupied(xpos,ypos) and self.hexgrd.onboard(xpos,ypos):
						self.on_image = True
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							self.Send({"action":"removehex","card":self.playingcard,"opponentnum":self.hexgrd.occupied_by(xpos,ypos),"stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
								
#				elif self.playingcard == 4:
#					if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= 1 and not self.hexgrd.occupied(xpos,ypos):
#						self.on_image = True
#							if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
#								self.Send({"action":"blockhex","stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
#								self.justclicked = 10
								
			self.drawDecks()
			self.drawPlayerCards(xpos,ypos)
					
			
		elif self.stage == "action phase":
			if self.turn == True:
				if self.take_deck_pos.withinRect(xpos,ypos):
					self.on_image = True
					if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
						self.Send({"action":"takecard","gameid":self.gameid,"num":self.num})
						self.players[self.num].preventterr = False
						self.justclicked = 10
				if self.hexgrd.close_neighbour(self.num,xpos,ypos) <= self.players[self.num].hexrange and not self.hexgrd.occupied(xpos,ypos) and not self.players[self.num].preventterr:
					self.on_image = True
					if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
						self.Send({"action":"placehex","stage":self.stage,"position":[xpos,ypos],"gameid":self.gameid,"num":self.num})
						self.justclicked = 10
					

			self.drawDecks()
			self.drawPlayerCards(xpos,ypos)
			
		elif self.stage == "choose card":
			if self.turn == True:
				top_deck = RectArray(300,250,300,200,210,0,len(self.choosecards))
				for i in range(len(self.choosecards)):
					(self.screen.blit(pygame.transform.scale(self.cardIms[self.choosecards[i]],
					[top_deck.r_array[i].w,top_deck.r_array[i].h]),[top_deck.r_array[i].x,top_deck.r_array[i].y]))			
				for i in range(len(self.choosecards)):
					if top_deck.r_array[i].withinRect(xpos,ypos):
						self.on_image = True
						(self.screen.blit(pygame.transform.scale(self.cardIms[self.choosecards[i]],
						[self.enlarge_rect.w,self.enlarge_rect.h]),[self.enlarge_rect.x,self.enlarge_rect.y]))	
						if pygame.mouse.get_pressed()[0] and self.justclicked<=0:
							chosencard = self.choosecards.pop(i)
							self.Send({"action":"cardchosen","discards":self.choosecards,"card":chosencard,"gameid":self.gameid,"num":self.num})
							self.justclicked = 10
			self.drawDecks()
			self.drawPlayerCards(xpos,ypos)

		pygame.display.flip()
			
class Player(object):

	def __init__(self,deck_xpos,deck_ypos):
		self.hand = []
		self.primerace = None
		self.secrace = None
		self.hand_rect_array = None
		self.deckxpos = deck_xpos
		self.deckypos = deck_ypos
		
		self.preventterr = False
		
		self.points = 0
		
		self.attackbonus = 0
		self.trapcapture = False
		self.playcardnum = 1
		self.blackpointbonus = False
		self.hexrange = 1
		self.bonuswhiteterr = False
		self.takecardnum = 1
		self.startterrnum = 2
		self.blockhex = False
		self.rearrangeterr = False
		
	def addToHand(self,card):
		self.hand.append(card)
		self.hand_rect_array = RectArray(self.deckxpos,self.deckypos,200,150,0,40,len(self.hand))

	def setPrimerace(self,prime_race):
		self.primerace = prime_race
		
		if self.primerace == 0:
			self.attackbonus += 1
		elif self.primerace == 1:
			self.trapcapture = True
		elif self.primerace == 2:
			self.playcardnum += 1
		elif self.primerace == 3:
			self.blackpointbonus = True
		elif self.primerace == 4:
			self.hexrange += 1
		elif self.primerace == 5:
			self.bonuswhiteterr = True
			
		
	def setSecrace(self,sec_race):
		self.secrace = sec_race
		
		if self.secrace == 0:
			self.points += 5
		elif self.secrace == 1:
			self.takecardnum += 1
		elif self.secrace == 2:
			self.startterrnum += 1
		elif self.secrace == 3:
			self.card_pickup_number = 5
		elif self.secrace == 4:
			self.blockhex = True
		elif self.secrace == 5:
			self.rearrangeterr = True
		
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
			
	def whichRect(self,xpos,ypos):
		which_rect = 100
		for i in range(len(self.r_array)):
			if self.r_array[i].withinRect(xpos,ypos):
				which_rect = i
		return which_rect
					
g = BoardGame()
while 1:
	g.update()
				
				
		
