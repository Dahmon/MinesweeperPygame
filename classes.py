import pygame
from spritesheet import SpriteSheet

class Number():
	def __init__(self, number):
		self.number = number

		self.numberSS = SpriteSheet('spritesheets/number-sprites.png')
		self.numberSprites = [
				(0,16,16,16),
				(16,16,16,16),
				(32,16,16,16),
				(48,16,16,16),
				(64,16,16,16),
				(80,16,16,16),
				(96,16,16,16),
				(112,16,16,16),
			]

class Face(pygame.sprite.Sprite):
	def __init__(self, SCREEN_WIDTH):
		super(Face, self).__init__()

		self.isPressed = False

		self.faceSS = SpriteSheet('spritesheets/face-sprites.png')

		self.smile = (0,0,24,24)
		self.clicked = (24,0,24,24)
		self.cell_pushed = (48,0,24,24)
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

		self.cellSS = SpriteSheet('spritesheets/cell-sprites.png')

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
		]

		self.surf = self.cellSS.image_at((0,0,16,16))
		self.surf.set_colorkey((255, 255, 255), pygame.RLEACCEL)

		self.rect = self.surf.get_rect(center=(x+8, y+8))

	def applySprite(self, sprite):
		self.surf = self.cellSS.image_at(sprite)

class Board:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.spritesheet = SpriteSheet('spritesheets/cell-sprites.png')

		self.cells = []
	
	def _create_board(self):
		pass
	pass