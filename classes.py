import pygame
import math
from settings import Settings
from spritesheet import SpriteSheet
from helpers import readOrCreatePickle

class ModalWindow():
	def __init__(self, onClick):
		self.onClick = onClick
		self.settings = readOrCreatePickle('save', Settings())
		cellSize = 16 * self.settings.scale

		self.surf = pygame.Surface((self.settings.boardWidth * cellSize, (self.settings.boardHeight * cellSize) + 60 * self.settings.scale))
		self.surf.set_colorkey((255,255,255), pygame.SRCALPHA)
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect(topleft=(0,0))

		# self.surf = pygame.Surface((self.settings.boardWidth * cellSize - cellSize * 2, (self.settings.boardHeight * cellSize + (60 * self.settings.scale)) - cellSize * 2))
		# self.surf = pygame.Surface((self.settings.boardWidth * 16 - 32, (self.settings.boardHeight * 16 + 60) - 32))
		# self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)

		self.surf2 = pygame.Surface((self.settings.boardWidth * cellSize - cellSize * 2, (self.settings.boardHeight * cellSize + (60 * self.settings.scale)) - cellSize * 2))
		self.surf2.fill((0,0,255))
		self.surf.blit(self.surf2, self.surf.get_rect(topleft=(cellSize,cellSize)))

		buttonSize = int(24 * self.settings.scale)
		buttonPosition = (cellSize + buttonSize / 2) + cellSize
		newRect = self.surf.get_rect(topleft=(buttonPosition,buttonPosition))
		self.closeButton = Button((newRect.x, newRect.y), self._onButtonClick)

	def _onButtonClick(self, event):
		self.onClick(event)

	def updateModalUi(self):
		self.surf.blit(self.closeButton.surf, self.closeButton.rect)

	def handleEvents(self, event):
		if event.type == pygame.MOUSEBUTTONDOWN:
			self.closeButton.handleMouseDown(event)
		if event.type == pygame.MOUSEBUTTONUP:
			self.closeButton.handleMouseUp(event)

class Display():
	def __init__(self, rect, length):
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
		
		self.scale = readOrCreatePickle('save', Settings()).scale
		self.spriteSize = (int(13 * self.scale), int(23 * self.scale))

		self.digits = [None] * self.length
		self.displaySurface = pygame.Surface(((13 * self.scale) * self.length, 23 * self.scale))

	def setDisplay(self, number):
		paddedNumber = str(math.trunc(number)).zfill(self.length)

		for index in range(self.length):
			if number < 0 and index == 0:
				self.displaySurface.blit(self.numberSS.image_at(self.negative), (13 * index, 0))
				self.digits[index] = self.numberSS.image_at(self.negative)
			else:
				spriteIndex = int(paddedNumber[index])
				self.displaySurface.blit(pygame.transform.scale(self.numberSS.image_at(self.numberSprites[spriteIndex]), self.spriteSize), ((13 * self.scale) * index, 0))

class Button():
	def __init__(self, pos, onMouseUp):
		self.onMouseUp = onMouseUp
		
		self.scale = readOrCreatePickle('save', Settings()).scale
		self.spriteSize = (int(24 * self.scale), int(24 * self.scale))

		self.buttonSS = SpriteSheet('spritesheets/button-sprites.png')
		self.blank = (0,0,24,24)
		self.blankPressed = (24,0,24,24)
		self.disabled = (48,0,24,24)

		self.surf = pygame.transform.scale(self.buttonSS.image_at(self.blank), self.spriteSize)
		self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
		self.rect = self.surf.get_rect(center=(pos))

		self.isPressed = False

	def applySprite(self, sprite):
		self.surf = pygame.transform.scale(self.buttonSS.image_at(sprite), self.spriteSize)
	
	def handleMouseDown(self, event):
		if event.button == 1 and self.rect.collidepoint(pygame.mouse.get_pos()):
			self.isPressed = True
			self.surf = pygame.transform.scale(self.buttonSS.image_at(self.blankPressed), self.spriteSize)

	def handleMouseUp(self, event):
		if self.isPressed:
			self.isPressed = False
			self.surf = pygame.transform.scale(self.buttonSS.image_at(self.blank), self.spriteSize)

			if self.rect.collidepoint(pygame.mouse.get_pos()):
				self.onMouseUp(event)


class Face():
	def __init__(self, pos):
		self.scale = readOrCreatePickle('save', Settings()).scale
		self.spriteSize = (int(24 * self.scale), int(24 * self.scale))

		self.faceSS = SpriteSheet('spritesheets/face-sprites.png')
		self.smile = (0,0,24,24)
		self.clicked = (24,0,24,24)
		self.cellPushed = (48,0,24,24)
		self.win = (72,0,24,24)
		self.dead = (96,0,24,24)

		self.isPressed = False

		self.surf = pygame.transform.scale(self.faceSS.image_at(self.smile), self.spriteSize)
		self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)
		self.rect = self.surf.get_rect(center=(pos))
		
		# x, y = pos
		# self.rect = self.surf.get_rect(center=(x, y * self.scale))

	def applySprite(self, sprite):
		self.surf = pygame.transform.scale(self.faceSS.image_at(sprite), self.spriteSize)

class Cell():
	def __init__(self, x, y):
		self.scale = readOrCreatePickle('save', Settings()).scale
		self.spriteSize = (int(16 * self.scale), int(16 * self.scale))
		# Cell state
		self.isActive = True
		self.isPressed = False
		self.isBomb = False
		# 0 = unlocked, 1 = flagged, 2 = question
		self.lockedState = 0
		self.neighbouringBombs = 0

		self.cellSS = SpriteSheet('spritesheets/cell-sprites.png')

		# cell sprites
		self.normal = (0,0,16,16)
		self.clicked = (16,0,16,16)
		self.flag = (32,0,16,16)
		self.question = (48,0,16,16)
		self.questionClicked = (64,0,16,16)
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

		self.cellStates = [
			self.normal,
			self.flag,
			self.question
		]

		self.surf = pygame.transform.scale(self.cellSS.image_at(self.normal), self.spriteSize)
		self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
	
		self.rect = self.surf.get_rect(topleft=(x, y))

	def applySprite(self, sprite):
		scale = readOrCreatePickle('save', Settings()).scale
		spriteSize = (int(16 * scale), int(16 * scale))
		self.surf = pygame.transform.scale(self.cellSS.image_at(sprite), spriteSize)