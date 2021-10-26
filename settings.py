import math

class Settings():
	def __init__(self):
		self.boardWidth = 30
		self.boardHeight = 20
		self.bombRatio = 0.15
		self.wins = 0
		self.losses = 0
		self.resets = 0

		self.scale = 2
		self.displayLength = 4

		self.winLengths = []
		self.lossLengths = []
	
	def getBombCount(self):
		cellCount = self.boardWidth * self.boardHeight
		return min(math.floor((self.boardWidth * self.boardHeight) * self.bombRatio), cellCount - 1)