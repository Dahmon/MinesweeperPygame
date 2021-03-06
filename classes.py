import pygame
import math
import pickle
from settings import Settings
from spritesheet import SpriteSheet
from helpers import readOrCreatePickle

class ModalWindow():
	def __init__(self, toggleDialog, resetGame):
		self.toggleDialog = toggleDialog
		self.resetGame = resetGame
		self.settings = readOrCreatePickle('save', Settings())
		self.cellSize = 16 * self.settings.scale
		self.open = False

		pygame.font.init()
		self.font = pygame.font.SysFont('Comic Sans MS', math.floor(20 * self.settings.scale))

		self.surf = pygame.Surface((self.settings.boardWidth * self.cellSize, (self.settings.boardHeight * self.cellSize) + 60 * self.settings.scale))
		self.surf.set_colorkey((255,255,255), pygame.SRCALPHA)
		self.surf.fill((255,255,255))
		self.rect = self.surf.get_rect(topleft=(0,0))

		self.surf2 = pygame.Surface((self.settings.boardWidth * self.cellSize - self.cellSize * 2, (self.settings.boardHeight * self.cellSize + (60 * self.settings.scale)) - self.cellSize * 2))
		self.surf2.fill((250,250,250))
		self.surf.blit(self.surf2, self.surf.get_rect(topleft=(self.cellSize,self.cellSize)))

		buttonSize = int(24 * self.settings.scale)
		buttonPosition = (self.cellSize + buttonSize / 2) + self.cellSize
		newRect = self.surf.get_rect(topleft=(buttonPosition,buttonPosition))
		self.closeButton = Button((newRect.x, newRect.y), self.toggleDialog)
		self.resetButton = Button((newRect.x, newRect.y + (self.cellSize * 14)), self._resetSettings)

	def _resetSettings(self):
		self.settings = Settings()
		pickle.dump(self.settings, open('save', 'wb'), pickle.HIGHEST_PROTOCOL)
		self.resetGame()
		print('Settings reset')

	def toggleOpen(self):
		self.open = not self.open

	def updateModalUi(self, screen):
		if self.open:
			# Butons
			self.surf.blit(self.closeButton.surf, self.closeButton.rect)
			self.surf.blit(self.resetButton.surf, self.resetButton.rect)
			# Settings info
			self.surf.blit(self.font.render('Wins: ' + str(self.settings.wins), False, (0, 0, 0)), (self.cellSize * 2, self.cellSize * 4))
			self.surf.blit(self.font.render('Losses: ' + str(self.settings.losses), False, (0, 0, 0)), (self.cellSize * 10, self.cellSize * 4))
			self.surf.blit(self.font.render('Resets: ' + str(self.settings.resets), False, (0, 0, 0)), (self.cellSize * 20, self.cellSize * 4))
			self.surf.blit(self.font.render('Win Lengths: ' + ', '.join(str(l) for l in self.settings.winLengths), False, (0, 0, 0)), (self.cellSize * 2, self.cellSize * 6))
			self.surf.blit(self.font.render('Loss Lengths: ' + ', '.join(str(l) for l in self.settings.lossLengths), False, (0, 0, 0)), (self.cellSize * 2, self.cellSize * 8))
			self.surf.blit(self.font.render('Scale: ' + str(self.settings.scale), False, (0, 0, 0)), (self.cellSize * 2, self.cellSize * 12))

			screen.blit(self.surf, self.rect)

	def handleEvents(self, event):
		if self.open:
			if event.type == pygame.MOUSEBUTTONDOWN:
				self.closeButton.handleMouseDown(event)
				self.resetButton.handleMouseDown(event)
			if event.type == pygame.MOUSEBUTTONUP:
				self.closeButton.handleMouseUp(event)
				self.resetButton.handleMouseUp(event)

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
	def __init__(self, pos, onMouseUp, type = 'blank'):
		self.onMouseUp = onMouseUp
		self.type = type
		
		self.scale = readOrCreatePickle('save', Settings()).scale
		self.spriteSize = (int(24 * self.scale), int(24 * self.scale))

		self.buttonSS = SpriteSheet('spritesheets/button-sprites.png')
		self.buttonSprites = {
			'blank': [(0,0,24,24), (24,0,24,24)],
			'config': [(0,24,24,24), (24,24,24,24)],
		}


		self.surf = pygame.transform.scale(self.buttonSS.image_at(self.buttonSprites[self.type][0]), self.spriteSize)
		# self.surf.set_colorkey((0, 0, 0), pygame.RLEACCEL)
		self.rect = self.surf.get_rect(center=(pos))

		self.isPressed = False

	def applySprite(self, sprite):
		self.surf = pygame.transform.scale(self.buttonSS.image_at(sprite), self.spriteSize)
	
	def handleMouseDown(self, event):
		if event.button == 1 and self.rect.collidepoint(pygame.mouse.get_pos()):
			self.isPressed = True
			self.surf = pygame.transform.scale(self.buttonSS.image_at(self.buttonSprites[self.type][1]), self.spriteSize)

	def handleMouseUp(self, event):
		if self.isPressed:
			self.isPressed = False
			self.surf = pygame.transform.scale(self.buttonSS.image_at(self.buttonSprites[self.type][0]), self.spriteSize)

			if self.rect.collidepoint(pygame.mouse.get_pos()):
				self.onMouseUp()


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