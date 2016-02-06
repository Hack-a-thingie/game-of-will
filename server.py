import PodSixNet.Channel
import PodSixNet.Server
import random
from random import shuffle
from time import sleep

class ClientChannel(PodSixNet.Channel.Channel):
	def Network(self,data):
		print data

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

	channelClass = ClientChannel
	
	def Connected(self,channel,addr):
		print 'new connection:', channel
		
		if self.queue == None:
			self.currentIndex+=1
			channel.gameid = self.currentIndex
			self.queue = Game(channel, self.currentIndex)
		else:
			channel.gameid = self.currentIndex
			self.queue.player1 = channel
			
			p_races = random.sample(range(6), 5)
			s_races = random.sample(range(6), 5)
			
			self.queue.player0.Send({"action":"startgame","player":0,"gameid":self.queue.gameid,"stage":"choose p race","p_races":p_races,"s_races":s_races})
			self.queue.player1.Send({"action":"startgame","player":1,"gameid":self.queue.gameid,"stage":"choose p race","p_races":p_races,"s_races":s_races})
			#self.queue.player0.Send({"action":"startgame","player":0,"gameid":self.queue.gameid,"stage":"choose p race","p_races":p_races,"s_races":s_races,"takedeck":self.queue.take_deck,"discarddeck":self.queue.discard_deck})
			#self.queue.player1.Send({"action":"startgame","player":1,"gameid":self.queue.gameid,"stage":"choose p race","p_races":p_races,"s_races":s_races,"takedeck":self.queue.take_deck,"discarddeck":self.queue.discard_deck})
			self.games.append(self.queue)
			self.queue = None
			
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
	def __init__(self, player0, currentIndex):
	
		self.turn = 0
		self.player0 = player0	
		self.player1 = None	
		self.stage = "card"	
		self.gameid = currentIndex
		
		self.take_deck = Deck(10)
		self.discard_deck = Deck(0)
		print "done init"
		
	def cardPlay(self,card,num):
		if num == self.turn:
			self.player1.Send({"action":"cardplay","stage":"action phase"})
			self.player0.Send({"action":"cardplay","stage":"action phase"})
				
	def pickPRace(self, p_race, num):
		if num == self.turn:
			self.turn = 0 if self.turn else 1
			self.player1.Send({"action":"pracechoose","stage":"choose s race" if num else "choose p race","player":num,"prace":p_race,"torf":True if self.turn == 1 else False})
			self.player0.Send({"action":"pracechoose","stage":"choose s race" if num else "choose p race","player":num,"prace":p_race,"torf":True if self.turn == 0 else False})

	def pickSRace(self, s_race, num):
		if num == self.turn:
			self.turn = 0 if self.turn else 1
			self.player1.Send({"action":"sracechoose","stage":"card phase" if num else "choose s race","player":num,"srace":s_race,"torf":True if self.turn == 1 else False})
			self.player0.Send({"action":"sracechoose","stage":"card phase" if num else "choose s race","player":num,"srace":s_race,"torf":True if self.turn == 0 else False})

	def takeCard(self,takenumber,num):
		if num == self.turn:
			self.player1.Send({"action":"takecard","cards":self.take_deck.deck[:takenumber],"stage":"choose card"})
			self.player0.Send({"action":"takecard","cards":self.take_deck.deck[:takenumber],"stage":"choose card"})
		
	def cardChosen(self,card,num):
		if num == self.turn:
			self.turn = 0 if self.turn else 1
			self.player1.Send({"action":"cardgain","card":card,"player":num,"stage":"card phase","torf":True if self.turn == 1 else False})
			self.player0.Send({"action":"cardgain","card":card,"player":num,"stage":"card phase","torf":True if self.turn == 0 else False})	

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