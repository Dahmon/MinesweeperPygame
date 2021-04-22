# Minesweeper
# Author: Dahmon Bicheno

# import the pygame library
import random
import math
import pygame
import sys
import pickle
from enum import Enum
from pygame.locals import (
	K_UP,
	K_DOWN,
	K_LEFT,
	K_RIGHT,
	K_ESCAPE,
	K_LCTRL,
	K_b,
	K_MINUS,
	K_EQUALS,
	KEYDOWN,
	KEYUP,
	QUIT,
	MOUSEBUTTONUP,
	MOUSEBUTTONDOWN,
	MOUSEMOTION
)

# Import classes
from classes import Face, Cell, Display, Button, ModalWindow
from settings import Settings
from helpers import readOrCreatePickle, listToString

class GameState(Enum):
	LOST = 0
	RUNNING = 1
	WIN = 2
	IDLE  = 3

class Minesweeper:
	def __init__(self):
		# init game and assets 
		pygame.init()
		self.clock = pygame.time.Clock()
		self.startTicks = pygame.time.get_ticks()
		self.gameTime = float()
		self.gameState = GameState.IDLE.value # 0 = lost, 1 = running, 2 = win, 3 = idle

		# set up variables
		self.settings = readOrCreatePickle('save', Settings())
		self.bombCount = self.settings.getBombCount()
		self.showBombs = False
		self.clickCount = 0
		self.revealedCellCount = 0

		self.showDialog = False

		self._initUi()
		self._initGame()


	def runGame(self):
		# start main game loop
		while True:
			self._checkEvents()
			self._updateScreen()

	def _initUi(self):
		self.faceButtonRowHeight = 60 * self.settings.scale
		middleOfRow = (self.faceButtonRowHeight / 2)
		SCREEN_WIDTH = int((self.settings.boardWidth * 16) * self.settings.scale)
		SCREEN_HEIGHT = int(((self.settings.boardHeight * 16) * self.settings.scale) + self.faceButtonRowHeight) 

		# set up the drawing window
		self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
		self.screen.fill((255, 255, 255))

		pygame.display.set_caption('Minesweeper')

		self.displays = []
		self.flagDisplay = Display(0, self.settings.displayLength)
		self.flagDisplay.setDisplay(self.bombCount)
		self.displays.append(self.flagDisplay)
		self.timeDisplay = Display((SCREEN_WIDTH - (self.settings.displayLength * 13) * self.settings.scale), self.settings.displayLength)
		self.timeDisplay.setDisplay(0)
		self.displays.append(self.timeDisplay)

		self.sprites = []
		# set up face and sprites
		self.face = Face((SCREEN_WIDTH / 2, middleOfRow))
		self.sprites.append(self.face)

		distanceFromFace = 12 * self.settings.scale
		positionNextToFace = ((SCREEN_WIDTH / 2) + 24 * self.settings.scale) + distanceFromFace
		self.button1 = Button((positionNextToFace, middleOfRow), self._onButton1Click)
		self.button2 = Button((positionNextToFace + 24 * self.settings.scale, middleOfRow), self._onButton2Click)
		self.button3 = Button((positionNextToFace + 48 * self.settings.scale, middleOfRow), self._onButton3Click)
		self.button4 = Button((positionNextToFace + 72 * self.settings.scale, middleOfRow), self.toggleDialog)
		self.buttons = [self.button1, self.button2, self.button3, self.button4]

		self.modal = ModalWindow(self.toggleDialog)
		# self.sprites.append(self.modal)

	def _initGame(self):
		self.cells = []
		for row in range(self.settings.boardHeight):
			self.cells.append([])
			for col in range(self.settings.boardWidth):
				cellSize = 16 * self.settings.scale
				cell = Cell((col * cellSize), (row * cellSize) + self.faceButtonRowHeight)
				self.sprites.append(cell)
				self.cells[row].append(cell)
		
		self._generateBombs(self.bombCount)

	def _generateBombs(self, bombCount):
		bombs = 0
		while bombs < bombCount:
			randomRow = random.randint(0, self.settings.boardHeight - 1)
			randomCol = random.randint(0, self.settings.boardWidth - 1)

			cell = self.cells[randomRow][randomCol]
			if not cell.isBomb and cell.isActive:
				cell.isBomb = True
				bombs += 1
				cell.applySprite(cell.bomb if self.showBombs else cell.normal)

		self._calculateNeighbouringBombs()

	def _updateScreen(self):
		# Ensure program maintains a rate of 30 frames per second
		self.clock.tick(30)
		
		# fill the background with white
		self.screen.fill((255, 255, 255))

		if self.gameState == GameState.RUNNING.value:
			self.gameTime = (pygame.time.get_ticks() - self.startTicks) / 1000
			self.timeDisplay.setDisplay(math.floor(self.gameTime))

		# draw all sprites
		for entity in self.sprites + self.buttons:
			self.screen.blit(entity.surf, entity.rect)

		for display in self.displays:
			self.screen.blit(display.displaySurface, (display.rect, 0))

		if self.showDialog:
			self.modal.updateModalUi()
			self.screen.blit(self.modal.surf, self.modal.rect)

		# update the display
		pygame.display.flip()

	def _resetGame(self):
		# inc reset counter if reset during game
		if self.gameState == GameState.RUNNING.value:
			self.settings.resets += 1
			pickle.dump(self.settings, open('save', 'wb'), pickle.HIGHEST_PROTOCOL)

		for row in self.cells:
			for cell in row:
				cell.applySprite(cell.normal)
				cell.isActive = True
				cell.isBomb = False
				cell.isPressed = False
				cell.lockedState = 0

		self.bombCount = self.settings.getBombCount()
		self.face.applySprite(self.face.smile)
		self.flagDisplay.setDisplay(self.bombCount)
		self.gameState = GameState.IDLE.value
		self.clickCount = 0
		self.revealedCellCount = 0

		self.startTicks = pygame.time.get_ticks()

		self._initUi()
		self._initGame()

	def _checkEvents(self):
		# loop through all events in queue
		for event in pygame.event.get():
			self.modal.handleEvents(event)

			# did the user click the window close button?
			if event.type == QUIT:
				# quit pygame and exit
				pygame.quit()
				sys.exit()

			if event.type == KEYDOWN and event.key == K_b:
				self.showBombs = not self.showBombs
				for row in self.cells:
					for cell in row:
						if cell.isBomb:
							cell.applySprite(cell.bomb if self.showBombs else cell.cellStates[cell.lockedState])
			
			if event.type == KEYDOWN and event.key in (K_MINUS, K_EQUALS):
				if event.key == K_EQUALS:
					self.settings.scale += 0.25
				if event.key == K_MINUS:
					self.settings.scale -= 0.25

				pickle.dump(self.settings, open('save', 'wb'), pickle.HIGHEST_PROTOCOL)
				self._resetGame()

			if event.type == KEYDOWN and event.key in (K_UP, K_DOWN, K_LEFT, K_RIGHT):
				if event.key == K_UP:
					self.settings.boardHeight -= 1
				if event.key == K_DOWN:
					self.settings.boardHeight += 1
				if event.key == K_LEFT:
					self.settings.boardWidth -= 1
				if event.key == K_RIGHT:
					self.settings.boardWidth += 1

				pickle.dump(self.settings, open('save', 'wb'), pickle.HIGHEST_PROTOCOL)
				self._resetGame()

			if event.type == MOUSEBUTTONDOWN:
				self._handleFaceMouseDown(event)
				self._handleCellMouseDown(event)
				self._handleButtonMouseDown(event)

			if event.type == MOUSEBUTTONUP:
				self._handleFaceMouseUp()
				# handle cell click after face, so can apply correct sprite
				# TODO: What? Why?
				self._handleCellMouseUp(event)
				self._handleButtonMouseUp(event)

	def _handleFaceMouseDown(self, event):
		if event.button == 1 and self.face.rect.collidepoint(pygame.mouse.get_pos()):
			self.face.isPressed = True
			self.face.applySprite(self.face.clicked)

	def _handleCellMouseDown(self, event):
		flaggedCells = 0
		for row in self.cells:
			for cell in row:
				if cell.isActive and cell.rect.collidepoint(pygame.mouse.get_pos()):
					self.face.applySprite(self.face.cellPushed)
					# if left clicking, handle cell opening
					if event.button == 1 and not cell.lockedState == 1:
						cell.isPressed = True
						cell.applySprite(cell.questionClicked if cell.lockedState == 2 else cell.clicked)

					# if right clicking, handle cell flagging and question marking
					if event.button == 3 and cell.isActive:
						cell.lockedState = 0 if cell.lockedState == 2 else cell.lockedState + 1
						cell.applySprite(cell.cellStates[cell.lockedState])
			
				if cell.lockedState == 1:
					flaggedCells += 1

		self.flagDisplay.setDisplay(self.bombCount - flaggedCells)

	def _handleButtonMouseDown(self, event):
		for button in self.buttons:
			button.handleMouseDown(event)

	def _handleFaceMouseUp(self):
		if self.face.isPressed and self.face.rect.collidepoint(pygame.mouse.get_pos()):
			self._resetGame()

		if self.gameState == GameState.WIN.value:
			self.face.applySprite(self.face.win)
		elif self.gameState == GameState.LOST.value:
			self.face.applySprite(self.face.dead)
		else:
			self.face.applySprite(self.face.smile)

		self.face.isPressed = False

	def _handleCellMouseUp(self, event):
		for row in self.cells:
			for cell in row:
				if cell.isActive:
					if cell.isPressed and cell.rect.collidepoint(pygame.mouse.get_pos()):
						self.clickCount += 1

						if self.clickCount == 1:
							self.startTicks = pygame.time.get_ticks()
							self.gameState = GameState.RUNNING.value

						if cell.isBomb:
							if self.clickCount == 1:
								cell.isBomb = False
								cell.isActive = False
								self._generateBombs(1)
								self._checkCellNeighbours(self.cells.index(row), row.index(cell))
							else:
								self._handleBombClick()
						else:
							self._checkCellNeighbours(self.cells.index(row), row.index(cell))
					elif cell.isPressed:
						cell.applySprite(cell.cellStates[cell.lockedState])

					cell.isPressed = False

	def _handleButtonMouseUp(self, event):
		for button in self.buttons:
			button.handleMouseUp(event)

	def _calculateNeighbouringBombs(self):
		for row in self.cells:
			for cell in row:
				cell.neighbouringBombs = 0
				rowIndex = self.cells.index(row)
				cellIndex = row.index(cell)

				for neighbourRow in (rowIndex - 1, rowIndex, rowIndex + 1):
					if neighbourRow >= 0 and neighbourRow <= (self.settings.boardHeight - 1):
						for neighbourCol in (cellIndex - 1, cellIndex, cellIndex + 1):
							if neighbourCol >= 0 and neighbourCol <= (self.settings.boardWidth - 1):
								# isOwnCell = neighbourRow == rowIndex and neighbourCol == cellIndex
								if self.cells[neighbourRow][neighbourCol].isBomb:
									cell.neighbouringBombs += 1

	def _checkCellNeighbours(self, rowIndex, colIndex):
		cell = self.cells[rowIndex][colIndex]
		cell.isActive = False
		self.revealedCellCount += 1

		# Check win condition
		self._checkWinCondition()

		if cell.neighbouringBombs == 0:
			cell.applySprite(cell.clicked)
			for neighbourRow in (rowIndex - 1, rowIndex, rowIndex + 1):
				if neighbourRow >= 0 and neighbourRow <= (self.settings.boardHeight - 1):
					for neighbourCol in (colIndex - 1, colIndex, colIndex + 1):
						if neighbourCol >= 0 and neighbourCol <= (self.settings.boardWidth - 1):
							neighbourCell = self.cells[neighbourRow][neighbourCol]
							if neighbourCell.isActive and not neighbourCell.lockedState == 1:
								self._checkCellNeighbours(neighbourRow, neighbourCol)
								neighbourCell.isActive = False
		else:
			cell.applySprite(cell.numberSprites[cell.neighbouringBombs - 1])

	def _handleBombClick(self):
		# update settings
		self.settings.losses += 1
		self.settings.lossLengths.append(self.gameTime)
		pickle.dump(self.settings, open('save', 'wb'), pickle.HIGHEST_PROTOCOL)

		# update game variables
		self.face.applySprite(self.face.dead)
		self.gameState = GameState.LOST.value

		for row in self.cells:
			for cell in row:
				cell.isActive = False

				if cell.isBomb:
					if not cell.lockedState == 1:
						if cell.rect.collidepoint(pygame.mouse.get_pos()):
							cell.applySprite(cell.bombClicked)
						else:
							cell.applySprite(cell.bomb)
				elif cell.lockedState == 1:
					cell.applySprite(cell.bombIncorrect)

	def _onButton1Click(self, event):
		print('Wins: ' + str(self.settings.wins))
		print('Losses: ' + str(self.settings.losses))
		print('Resets: ' + str(self.settings.resets))
		print('Win Lengths: ' + listToString(self.settings.winLengths))
		print('Loss Lengths: ' + listToString(self.settings.lossLengths))
		print('----')
		print('Scale: ' + str(self.settings.scale))
	def _onButton2Click(self, event):
		self.settings = Settings()
		pickle.dump(self.settings, open('save', 'wb'), pickle.HIGHEST_PROTOCOL)
		self._resetGame()
		print('Settings reset')
	def _onButton3Click(self, event):
		print('Use <Arrow Keys> to change the width and height of the board')
		print('Use <Minus> and <Plus> to change the scale of the UI')
		print('Use <B> to reveal/hide bombs')
	def toggleDialog(self, event):
		self.showDialog = not self.showDialog


	def _checkWinCondition(self):
		expectedRevealedCount = math.floor((self.settings.boardWidth * self.settings.boardHeight) - self.bombCount)
		if self.revealedCellCount == expectedRevealedCount:
			# update settings
			self.settings.wins += 1
			self.settings.winLengths.append(self.gameTime)
			pickle.dump(self.settings, open('save', 'wb'), pickle.HIGHEST_PROTOCOL)

			# update game variables
			self.face.applySprite(self.face.win)
			self.gameState = GameState.WIN.value

			for row in self.cells:
				for cell in row:
					cell.isActive = False
					if cell.isBomb:
						cell.applySprite(cell.flag)

if __name__ == '__main__':
	minesweeper = Minesweeper()
	minesweeper.runGame()