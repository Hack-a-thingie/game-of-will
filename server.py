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
		card = data["card"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.cardPlay(card,num,self.gameid) 
		
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
		takenumber = data["takenumber"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.takeCard(takenumber,num,self.gameid)
		
	def Network_cardchosen(self,data):
		card = data["card"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.cardChosen(card,num,self.gameid)
		
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
			self.queue.players.append(channel)
			self.currentPlayers+=1
			
			if self.currentPlayers == self.queue.player_num:
				p_races = random.sample(range(6), self.queue.player_num+1)
				s_races = random.sample(range(6), self.queue.player_num+1)
			
				for i in range(self.queue.player_num):
					self.queue.players[i].Send({"action":"startgame","player_num":self.queue.player_num,"player":i,"gameid":self.queue.gameid,"stage":"choose p race","p_races":p_races,"s_races":s_races})
					
				self.games.append(self.queue)
				self.queue = None
			
		
	def setGame(self,player_num):
		self.queue = Game(self.first_channel, self.currentIndex, player_num)
		self.unset = 0
			
	def cardPlay(self, card, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].cardPlay(card,num)
			
	def pickPRace(self, p_race, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].pickPRace(p_race,num)
			
	def pickSRace(self, s_race, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].pickSRace(s_race,num)
	
	def takeCard(self, takenumber, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].takeCard(takenumber,num)
			
	def cardChosen(self, card, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].cardChosen(card,num)
		
class Game:
	def __init__(self, player0, currentIndex, player_num):
	
		self.turn = 0
		self.player_num = player_num
		self.players = []
		self.players.append(player0)
		self.stage = "card"	
		self.gameid = currentIndex
				
		self.take_deck = Deck(10)
		self.discard_deck = Deck(0)

		
	def cardPlay(self,card,num):
		if num == self.turn:
			for i in range(self.player_num):
				self.players[i].Send({"action":"cardplay","stage":"action phase"})
				
	def pickPRace(self, p_race, num):
		if num == self.turn:
			self.turn += 1
			for i in range(self.player_num):
				self.players[i].Send({"action":"pracechoose","stage":"choose p race" if self.turn<self.player_num else "choose s race","player":num,"prace":p_race,"turn":self.turn%self.player_num})
			self.turn = self.turn%self.player_num

	def pickSRace(self, s_race, num):
		if num == self.turn:
			self.turn += 1
			for i in range(self.player_num):
				self.players[i].Send({"action":"sracechoose","stage":"choose s race" if self.turn<self.player_num else "card phase","player":num,"srace":s_race,"turn":self.turn%self.player_num})
			self.turn = self.turn%self.player_num

	def takeCard(self,takenumber,num):
		if num == self.turn:
			for i in range(self.player_num):
				self.players[i].Send({"action":"takecard","cards":self.take_deck.deck[:takenumber],"stage":"choose card"})
			
	def cardChosen(self,card,num):
		if num == self.turn:
			self.turn += 1
			for i in range(self.player_num):
				self.players[i].Send({"action":"cardgain","card":card,"player":num,"stage":"card phase","turn":self.turn%self.player_num})
			self.turn = self.turn%self.player_num	

class Deck(object):

	def __init__(self,number_cards):
		self.deck = [i for i in range(1,number_cards) for _ in range(3)]
		self.shuffleDeck()
		
	def shuffleDeck(self):
		shuffle(self.deck)
					
		
print "STARTING SERVER ON LOCALHOST"
bgServe = BoardServer()
while True:
	bgServe.Pump()
	sleep(0.01)