import PodSixNet.Channel
import PodSixNet.Server
import random
from random import shuffle
from time import sleep

class ClientChannel(PodSixNet.Channel.Channel):
	
	def Network(self,data):
		print data
			
	def Network_setgame(self,data):
		player_num = data["player_num"]
		self._server.setGame(player_num)

	def Network_cardplay(self,data):
		stage = data["stage"]
		card = data["card"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.cardPlay(card,num,stage,self.gameid) 
		
	def Network_placehex(self,data):
		hex_pos = data["position"]
		num = data["num"]
		stage = data["stage"]
		self.gameid = data["gameid"]
		self._server.placeHex(hex_pos,num,stage,self.gameid) 
		
	def Network_cardplacehex(self,data):
		hex_pos = data["position"]
		num = data["num"]
		card = data["card"]
		stage = data["stage"]
		self.gameid = data["gameid"]
		self._server.cardPlaceHex(hex_pos,card,num,stage,self.gameid)
		
	def Network_cardremovehex(self,data):
		hex_pos = data["position"]
		num = data["num"]
		card = data["card"]
		opponent_num = data["opponent"]
		stage = data["stage"]
		self.gameid = data["gameid"]
		self._server.cardRemoveHex(hex_pos,card,num,opponent_num,stage,self.gameid)
		
	def Network_choose_p_race(self,data):
		p_race = data["p race"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.pickPRace(p_race,num,self.gameid)
		
	def Network_choose_s_race(self,data):
		s_race = data["s race"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.pickSRace(s_race,num,self.gameid)
		
	def Network_takecard(self,data):
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.takeCard(num,self.gameid)
		
	def Network_cardchosen(self,data):
		discards = data["discards"]
		card = data["card"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.cardChosen(discards,card,num,self.gameid)
	
	def Network_removeplayercard(self,data):
		removecard = data["removecard"]
		removeplayer = data["removeplayer"]
		card = data["card"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.removePlayerCard(removecard,removeplayer,card,num,self.gameid)
		
	def Network_stopterrtake(self,data):
		stopplayer = data["player"]
		num = data["num"]
		card = data["card"]
		self.gameid = data["gameid"]
		self._server.stopTerrTake(stopplayer,card,num,self.gameid)
		
	def Network_cardblockhex(self,data):
		blockpos = data["position"]
		num = data["num"]
		card = data["card"]
		self.gameid = data["gameid"]
		self._server.cardBlockHex(blockpos,card,num,self.gameid)
		
class BoardServer(PodSixNet.Server.Server):
	def __init__(self, *args, **kwargs):
		PodSixNet.Server.Server.__init__(self, *args, **kwargs)
		self.games = []
		self.queue = None
		self.currentIndex = 0
		self.currentPlayers = 0

	channelClass = ClientChannel

	def Connected(self,channel,addr):
		print 'new connection:', channel
		
		if self.queue == None:
			self.unset = 1
			self.currentIndex+=1
			self.currentPlayers+=1
			channel.gameid = self.currentIndex
			channel.Send({"action":"setgame"})
			self.first_channel = channel
			while self.unset:
				self.Pump()
				sleep(0.01)
		else:
			channel.gameid = self.currentIndex
			self.queue.playerchan.append(channel)
			self.currentPlayers+=1
			
			if self.currentPlayers == self.queue.player_num:
				p_races = random.sample(range(6), self.queue.player_num+1)
				s_races = random.sample(range(6), self.queue.player_num+1)
			
				for i in range(self.queue.player_num):
					self.queue.playerchan[i].Send({"action":"startgame","player_num":self.queue.player_num,"player":i,"gameid":self.queue.gameid,"stage":"choose p race","p_races":p_races,"s_races":s_races})
					
				self.games.append(self.queue)
				self.queue = None
				self.currentPlayers = 0
				
	def tick(self):
		for game in self.games:
			if game.turnsremaining == 0:
				for i in range(game.player_num):
					game.playerchan[i].Send({"action":"endgame"})	
					
	def setGame(self,player_num):
		self.queue = Game(self.first_channel, self.currentIndex, player_num)
		self.unset = 0
			
	def cardPlay(self, card, num, stage,gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].cardPlay(card,num,stage)
			
	def pickPRace(self, p_race, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].pickPRace(p_race,num)
			
	def pickSRace(self, s_race, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].pickSRace(s_race,num)
	
	def takeCard(self, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].takeCard(num)
			
	def cardChosen(self, discards, card, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].cardChosen(discards,card,num)
			
	def removePlayerCard(self, removecard,removeplayer, card, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].removePlayerCard(removecard,removeplayer,card,num)
			
	def placeHex(self, hex_pos, num, stage, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].placeHex(hex_pos,num,stage)
			
	def cardPlaceHex(self, hex_pos, card, num ,stage, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].cardPlaceHex(hex_pos,card,num,stage)
			
	def cardRemoveHex(self, hex_pos, card, num,opponent_num ,stage, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].cardRemoveHex(hex_pos,card,num,opponent_num,stage)
			
	def stopTerrTake(self, stopplayer,card, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].stopTerrTake(stopplayer,card,num)
			
	def cardBlockHex(self, blockpos, card, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].cardBlockHex(blockpos,card,num)
		
class Game:
	def __init__(self, player0, currentIndex, player_num):
	
		self.turn = 0
		self.player_num = player_num
		self.playerchan = []
		self.playerchan.append(player0)
		self.stage = "card"	
		self.gameid = currentIndex
		
		self.terrpicked = 0
				
		self.take_deck = Deck(10)
		self.discard_deck = Deck(0)
		
		self.players = [Player() for i in range(self.player_num)]
		
		self.turnsremaining = 24 - self.player_num
		
	def cardPlay(self,card,num,stage):
		if num == self.turn%self.player_num:
			if stage == "card phase":
				if card == "skip":
					print "skippping"
					for i in range(self.player_num):
						self.playerchan[i].Send({"action":"cardplay","card":card,"stage":"action phase"})	
				else:
					if self.players[num].bonusplaycard:
						for i in range(self.player_num):
							self.playerchan[i].Send({"action":"cardplay","card":card,"stage":"bonus card action phase"})
					else:
						for i in range(self.player_num):
							self.playerchan[i].Send({"action":"cardplay","card":card,"stage":"card action phase"})
							
			elif stage == "bonus card phase":
				if card == "skip":
					for i in range(self.player_num):
						self.playerchan[i].Send({"action":"cardplay","card":card,"stage":"action phase"})	
				else:
					for i in range(self.player_num):
						self.playerchan[i].Send({"action":"cardplay","card":card,"stage":"card action phase"})
				
				
	def pickPRace(self, p_race, num):
		if num == self.turn%self.player_num:
			self.turn += 1
			self.players[num].setPrimerace(p_race)
			for i in range(self.player_num):
				self.playerchan[i].Send({"action":"pracechoose","stage":"choose p race" if self.turn<self.player_num else "choose s race","player":num,"prace":p_race,"turn":self.turn if self.turn<self.player_num else (self.turn-1)})
			if not self.turn < self.player_num:
				self.turn -= 1
				
	def pickSRace(self, s_race, num):
		if num == self.turn%self.player_num:
			self.turn -= 1
			self.players[num].setSecrace(s_race)
			for i in range(self.player_num):
				self.playerchan[i].Send({"action":"sracechoose","stage":"choose s race" if self.turn >= 0 else "pick territories","player":num,"srace":s_race,"turn":self.turn if self.turn >= 0 else 0})
			if not self.turn > 0:
				self.turn = 0

	def takeCard(self,num):
		if num == self.turn%self.player_num:
			for i in range(self.player_num):
				if len(self.take_deck.deck) < self.players[num].card_pickup_number:
					self.take_deck.combineDecks(self.discard_deck.deck)
					self.discard_deck.emptyDeck()
				self.playerchan[i].Send({"action":"takecard","cards":self.take_deck.deck[:self.players[num].card_pickup_number],"stage":"choose card"})
			self.take_deck.deck[0:self.players[num].card_pickup_number] = []
			
	def cardChosen(self,discards,card,num):
		if num == self.turn%self.player_num:
			if self.players[num].takecardnum > (self.players[num].card_pickup_number - len(discards)):
				for i in range(self.player_num):
					self.playerchan[i].Send({"action":"cardgain","card":card,"player":num,"stage":"choose card","cards":discards})
			else:
				self.turn = self.turn+1
				for i in range(self.player_num):
					self.playerchan[i].Send({"action":"cardgainend","card":card,"player":num,"stage":"card phase","turn":self.turn})
				
				if self.turn%self.player_num == 0:
					self.turnsremaining -= 1				
				self.discard_deck.combineDecks(discards)
				
	def removePlayerCard(self,removecard,removeplayer,card,num):
		if num == self.turn%self.player_num:
			for i in range(self.player_num):
				self.playerchan[i].Send({"action":"losecard","card":card,"player":num,"losecard":removecard,"loseplayer":removeplayer,"stage":"action phase"})
				
	def placeHex(self,hex_pos,num,stage):
				
		if stage == "pick territories":
			if self.terrpicked < 1:
				self.turn = (self.turn+1)%self.player_num
				for i in range(self.player_num):
					self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"pick territories","turn":self.turn})
				if self.turn%self.player_num == 0:
					self.terrpicked += 1
			else:
				self.turn = (self.turn+1)%self.player_num
				if self.turn%self.player_num == 0:
					for i in range(self.player_num):
						if self.players[i].bonusstartterr:
							for j in range(self.player_num):
								self.playerchan[j].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"bonus pick territories","turn":i})
							return
					for i in range(self.player_num):
						self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"card phase","turn":self.turn})
				else:
					for i in range(self.player_num):
						self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"pick territories","turn":self.turn})
		elif stage == "bonus pick territories":
			for i in range(self.player_num):
						self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"card phase","turn":self.turn})
						
								
		elif stage == "action phase":
			if self.players[num].bonuswhiteterr:
				for i in range(self.player_num):
					self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"bonus place hex","turn":self.turn})
			else:
				self.turn = self.turn+1
				for i in range(self.player_num):
					self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"card phase","turn":self.turn})
					
		
		elif stage == "bonus place hex":
			self.turn = self.turn+1
			for i in range(self.player_num):
				self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"card phase","turn":self.turn})
				
		elif stage == "bonus place hex card":
			for i in range(self.player_num):
				self.playerchan[i].Send({"action":"placehex","position":hex_pos,"player":num,"stage":"action phase","turn":self.turn})
					
	def cardPlaceHex(self,hex_pos,card,num,stage):
		if num == self.turn%self.player_num:
			if stage == "card action phase" or stage == "bonus card action phase":
				if card == 9:
					for i in range(self.player_num):
						self.playerchan[i].Send({"action":"cardplacehex","card":card,"position":hex_pos,"player":num,"stage":"bonus place hex card","turn":self.turn})
				else:
					for i in range(self.player_num):
						self.playerchan[i].Send({"action":"cardplacehex","card":card,"position":hex_pos,"player":num,"stage":"action phase","turn":self.turn})
					
					
	def cardRemoveHex(self,hex_pos,card,num,opponent_num,stage):
		if num == self.turn%self.player_num:
			if stage == "card action phase" or stage == "bonus card action phase":
				for i in range(self.player_num):
					self.playerchan[i].Send({"action":"cardremovehex","card":card,"player":num,"position":hex_pos,"opponent":opponent_num,"stage":"action phase","turn":self.turn})
							
			elif stage == "action phase":
				self.turn = self.turn+1
				for i in range(self.player_num):
					self.playerchan[i].Send({"action":"removehex","position":hex_pos,"opponent":opponent_num,"stage":"card phase","turn":self.turn})
				
				if self.turn%self.player_num == 0:
					self.turnsremaining -= 1
					
	def stopTerrTake(self,stopplayer,card,num):
		if num == self.turn%self.player_num:
			for i in range(self.player_num):
				self.playerchan[i].Send({"action":"stopterrtake","stopplayer":stopplayer,"stage":"action phase"})
				
	def cardBlockHex(self,blockpos,card,num):
		print "here"
		if num == self.turn%self.player_num:
			for i in range(self.player_num):
				self.playerchan[i].Send({"action":"cardblockhex","card":card,"player":num,"blockpos":blockpos,"stage":"action phase"})
					
class Deck(object):

	def __init__(self,number_cards):
		self.deck = [i for i in range(1,number_cards) for _ in range(3)]
		self.shuffleDeck()
		
	def shuffleDeck(self):
		shuffle(self.deck)
		
	def combineDecks(self,decktomerge):
		self.deck = self.deck + decktomerge
		
	def emptyDeck(self):
		self.deck = []
		
class Player(object):

	def __init__(self):
	
		self.hand_limit = 1
		self.hand = []
		self.card_pickup_number = 3
		self.turn = False
		
		self.primerace = None
		self.secrace = None
		
		self.points = 0
		
		self.attackbonus = 0
		self.trapcapture = False
		self.bonusplaycard = False
		self.blackpointbonus = False
		self.hexrange = 1
		self.bonuswhiteterr = False
		self.takecardnum = 1
		self.bonusstartterr = False
		self.blockhex = False
		self.rearrangeterr = False
		
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
	
	def setPrimerace(self,prime_race):
		self.primerace = prime_race
		
		if self.primerace == 0:
			self.attackbonus += 1
		elif self.primerace == 1:
			self.trapcapture = True
		elif self.primerace == 2:
			self.bonusplaycard = True
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
			self.bonusstartterr = True
		elif self.secrace == 3:
			self.card_pickup_number = 5
		elif self.secrace == 4:
			self.blockhex = True
		elif self.secrace == 5:
			self.rearrangeterr = True
					
		
print "STARTING SERVER ON LOCALHOST"
address = raw_input("Host:Port (localhost:8000): ")
if not address:
	host, port = "localhost", 8000
else:
	host,port = address.split(":")	
bgServe = BoardServer(localaddr=(host,int(port)))
while True:
	bgServe.Pump()
	bgServe.tick()
	sleep(0.01)