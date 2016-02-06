import PodSixNet.Channel
import PodSixNet.Server
from time import sleep

class ClientChannel(PodSixNet.Channel.Channel):
	def Network(self,data):
		print data
		card = data["action"]
		num = data["num"]
		self.gameid = data["gameid"]
		self._server.skipCardPhase(card,num,self.gameid) 
		
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
			self.queue.player0.Send({"action":"startgame","player":0,"gameid":self.queue.gameid})
			self.queue.player1.Send({"action":"startgame","player":1,"gameid":self.queue.gameid})
			self.games.append(self.queue)
			self.queue = None
			
	def skipCardPhase(self, card, num, gameid):
		game = [a for a in self.games if a.gameid==gameid]
		if len(game)==1:
			game[0].skipCardPhase(card,num)
		
class Game:
	def __init__(self, player0, currentIndex):
	
		self.turn = 0
		self.player0 = player0	
		self.player1 = None	
		self.stage = "card"	
		self.gameid = currentIndex
		
	def skipCardPhase(self,card,num):
		if num == self.turn:
			self.turn = 0 if self.turn else 1
			self.player1.Send({"action":"yourturn","torf":True if self.turn == 1 else False})
			self.player0.Send({"action":"yourturn","torf":True if self.turn == 0 else False})
			
			if card == "skip":
				pass
					
		
print "STARTING SERVER ON LOCALHOST"
bgServe = BoardServer()
while True:
	bgServe.Pump()
	sleep(0.01)