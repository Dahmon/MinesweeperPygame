# Minesweeper
# Author: Dahmon Bicheno

# import the pygame library
import random
import pygame
import sys
# import pygame.locals for easier access to key coordinates
from pygame.locals import (
	K_UP,
	K_DOWN,
	K_LEFT,
	K_RIGHT,
	K_ESCAPE,
	KEYDOWN,
	QUIT,
	MOUSEBUTTONUP,
	MOUSEBUTTONDOWN
)

# Import classes
from classes import Face, Cell, Board #, Settings


class Minesweeper:
	def __init__(self):
		# init game and assets 
		pygame.init()

		self.isRunning = True

		# set up variables
		self.boardWidth = 30
		self.boardHeight = 20
		self.bombRatio = 0.2 # 20%
		faceButtonRowHeight = 60

		SCREEN_WIDTH = self.boardWidth * 16
		SCREEN_HEIGHT = self.boardHeight * 16 + faceButtonRowHeight

		# set up the drawing window
		self.screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
		self.screen.fill((255, 255, 255))

		pygame.display.set_caption('Minesweeper')
		self.clock = pygame.time.Clock()

		# set up face and sprites
		self.face = Face(SCREEN_WIDTH)
		self.sprites = pygame.sprite.Group()
		self.sprites.add(self.face)

		self.cells = []
		# self.board = Board(boardWidth, boardHeight)
		for y in range(self.boardHeight):
			for x in range(self.boardWidth):
				cell = Cell(x * 16, (y * 16) + faceButtonRowHeight)
				self.sprites.add(cell)
				self.cells.append(cell)
		
		self._generateBombs()


	def runGame(self):
		# start main game loop
		while True:
			self._checkEvents()
			self._updateScreen()


	def _generateBombs(self):
		bombs = 0
		bombCount = (self.boardWidth * self.boardHeight) * self.bombRatio

		while bombs < bombCount:
			cell = self.cells[random.randint(0, len(self.cells) - 1)]
			if not cell.isBomb:
				cell.isBomb = True
				bombs += 1
				cell.surf = cell.cellSS.image_at(cell.bomb)

	def _resetGame(self):
		for cell in self.cells:
			cell.surf = cell.cellSS.image_at(cell.normal)
			cell.isActive = True
			cell.isBomb = False
			cell.isPressed = False
			cell.lockedState = 0

		self.face.surf = self.face.faceSS.image_at(self.face.smile)
		self.isRunning = True
		self._generateBombs()

	def _checkEvents(self):
		# loop through all events in queue
		for event in pygame.event.get():
			# did the user click the window close button?
			if event.type == QUIT:
				# quit pygame and exit
				pygame.quit()
				sys.exit()

			# Holding both mouse buttons should clear area

			if event.type == MOUSEBUTTONDOWN:
				if event.button == 1 and self.face.rect.collidepoint(pygame.mouse.get_pos()):
					self.face.isPressed = True
					self.face.surf = self.face.faceSS.image_at(self.face.clicked)
				elif self.isRunning:
					self.face.surf = self.face.faceSS.image_at(self.face.cell_pushed)

				self._handleCellMouseDown(event)

			if event.type == MOUSEBUTTONUP:
				if self.isRunning:
					self.face.surf = self.face.faceSS.image_at(self.face.smile)
				if self.face.isPressed and self.face.rect.collidepoint(pygame.mouse.get_pos()):
					self._resetGame()

				# handle cell click after face, so can apply correct sprite
				self._handleCellMouseUp(event)

	def _updateScreen(self):
		# fill the background with white
		# self.screen.fill((255, 255, 255))

		# draw all sprites
		for entity in self.sprites:
			self.screen.blit(entity.surf, entity.rect)

		# update the display
		pygame.display.flip()

		# Ensure program maintains a rate of 30 frames per second
		self.clock.tick(30)


	def _handleCellMouseDown(self, event):
		for cell in self.cells:
			if cell.isActive and cell.rect.collidepoint(pygame.mouse.get_pos()):
				# if left clicking, handle cell opening
				if event.button == 1 and not cell.lockedState:
					cell.isPressed = True
					cell.surf = cell.cellSS.image_at(cell.clicked)

				# if right clicking, handle cell flagging and question marking
				if event.button == 3 and cell.isActive:
					if cell.lockedState < 2:
						cell.lockedState += 1
						cell.surf = cell.cellSS.image_at(cell.flag if cell.lockedState == 1 else cell.question)
					else:
						cell.lockedState = 0
						cell.surf = cell.cellSS.image_at(cell.normal)


	def _handleCellMouseUp(self, event):
		for cell in self.cells:
			if cell.isPressed and cell.rect.collidepoint(pygame.mouse.get_pos()):
				cell.isActive = False
				if cell.isBomb:
					self._handleBombClick()
				else:
					self._checkCellNeighbours(self.cells.index(cell))

			elif cell.isPressed:
				cell.surf = cell.cellSS.image_at(cell.normal)

			cell.isPressed = False


	def _checkCellNeighbours(self, cellIndex):
		neighbouringCellIndexes = [
			(cellIndex - self.boardWidth) - 1, (cellIndex - self.boardWidth), (cellIndex - self.boardWidth) + 1,
			cellIndex - 1, cellIndex + 1,
			(cellIndex + self.boardWidth) - 1, (cellIndex + self.boardWidth), (cellIndex + self.boardWidth) + 1,
		]
		neighbouringBombs = 0

		# get neighbouringBombs count
		# replace with list reduce?
		for neighbourIndex in neighbouringCellIndexes:
			cell = self.cells[neighbourIndex]
			if cell.isBomb:
				neighbouringBombs += 1

		cell = self.cells[cellIndex]

		# I THINK BREAKING BECAUSE NEIGHBOR INDEX WRAPS WHEN NEGATIVE OR MORE THAN CELL LIST LENGTH
		# change sprite and call function on neightbours if required
		if neighbouringBombs == 0:
			print('no neighbor bombs')
			cell.surf = cell.cellSS.image_at(cell.clicked)
			for neighbourIndex in neighbouringCellIndexes:
				neighbourCell = self.cells[neighbourIndex]
				if neighbourCell.isActive: 
					print('recursion hell!')
					# self._checkCellNeighbours(neighbourIndex)
		else:
			print('!neighbor bombs!')
			# Apply number sprite
			cell.surf = cell.cellSS.image_at(cell.numberSprites[neighbouringBombs - 1])


	def _handleBombClick(self):
		self.face.surf = self.face.faceSS.image_at(self.face.dead)
		self.isRunning = False

		for cell in self.cells:
			cell.isActive = False
			if cell.isBomb:
				if not cell.lockedState == 1:
					if cell.rect.collidepoint(pygame.mouse.get_pos()):
						cell.surf = cell.cellSS.image_at(cell.bombClicked)
					else:
						cell.surf = cell.cellSS.image_at(cell.bomb)
			elif cell.lockedState:
				cell.surf = cell.cellSS.image_at(cell.bombIncorrect)


if __name__ == '__main__':
	minesweeper = Minesweeper()
	minesweeper.runGame()