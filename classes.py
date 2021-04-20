import pygame
import math
from spritesheet import SpriteSheet

class Display():
	def __init__(self, rect, length = 4):
		self.rect = rect
		self.length = length
		self.numberSS = SpriteSheet('spritesheets/number-sprites.png')
		self.negative = (130,0,13,23)
		self.numberSprites = [
			(0,0,13,23),
			(13,0,13,23),
			(26,0,13,23),
			(39,0,13,23),
			(52,0,13,23),
			(65,0,13,23),
			(78,0,13,23),
			(91,0,13,23),
			(104,0,13,23),
			(117,0,13,23),
		]

		self.digits = [None] * self.length
		self.displaySurface = pygame.Surface((13 * self.length,23))

	def setDisplay(self, number):
		paddedNumber = str(math.trunc(number)).zfill(self.length)

		for index in range(self.length):
			if number < 0 and index == 0:
				self.displaySurface.blit(self.numberSS.image_at(self.negative), (13 * index, 0))
				self.digits[index] = self.numberSS.image_at(self.negative)
			else:
				spriteIndex = int(paddedNumber[index])
				self.displaySurface.blit(self.numberSS.image_at(self.numberSprites[spriteIndex]), (13 * index, 0))

class Face(pygame.sprite.Sprite):
	def __init__(self, SCREEN_WIDTH):
		super(Face, self).__init__()

		self.isPressed = False

		self.faceSS = SpriteSheet('spritesheets/face-sprites.png')

		self.smile = (0,0,24,24)
		self.clicked = (24,0,24,24)
		self.cellPushed = (48,0,24,24)
		self.win = (72,0,24,24)
		self.dead = (96,0,24,24)

		self.surf = self.faceSS.image_at(self.smile)
		self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)

		self.rect = self.surf.get_rect(
			center=(
				(SCREEN_WIDTH-self.surf.get_width())/2,
				30
			)
		)

	def applySprite(self, sprite):
		self.surf = self.faceSS.image_at(sprite)



class Cell(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Cell, self).__init__()

		# Cell state
		self.isActive = True
		self.isPressed = False
		self.isBomb = False
		# 0 = unlocked, 1 = flagged, 2 = question
		self.lockedState = 0

		self.cellSS = SpriteSheet('spritesheets/cell-sprites-2.png')

		# cell sprites
		self.normal = (0,0,16,16)
		self.clicked = (16,0,16,16)
		self.flag = (32,0,16,16)
		self.question = (48,0,16,16)
		self.bomb = (80,0,16,16)
		self.bombClicked = (96,0,16,16)
		self.bombIncorrect = (112,0,16,16)
		self.numberSprites = [
			(0,16,16,16),
			(16,16,16,16),
			(32,16,16,16),
			(48,16,16,16),
			(64,16,16,16),
			(80,16,16,16),
			(96,16,16,16),
			(112,16,16,16),
			(128,16,16,16)
		]

		self.surf = self.cellSS.image_at((0,0,16,16))
		self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)

		self.rect = self.surf.get_rect(center=(x+8, y+8))

	def applySprite(self, sprite):
		self.surf = self.cellSS.image_at(sprite)