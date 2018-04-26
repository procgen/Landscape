import sys, pygame, Perlin, math, threading
import pygame.surfarray as surfarray
import time
import numpy

class Generator():
	#CONSTANTS
	CHUNK_SIZE = 128
	PIXEL_SIZE = 4
	PIXELS = CHUNK_SIZE // PIXEL_SIZE
	EXITING = False
	MOVE_SPEED = 0.4
	size = width, height = 800, 800

	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode(self.size)
		self.screen.fill((0, 0, 0))
		self.screenX = 0
		self.screenY = 0

		#THREADING
		self.surfaces = {}
		self.chunkQueue = []
		self.chunkCond = threading.Condition()
		self.chunkLock = threading.Lock()

		self.chunkThread = threading.Thread(target=self.chunkThread)
		self.chunkThread.start()

		self.clock = pygame.time.Clock()

	def colorToInt(this, color):
		colorInt = (int(color[0]) << 16) + (int(color[1]) << 8) + (int(color[2]))
		return colorInt

	def getPixel(self, x, y, i, j):
		color = (125, 255, 125)
		return self.colorToInt(color)

	def genChunk(self, x, y):
		pixels = numpy.zeros((self.CHUNK_SIZE, self.CHUNK_SIZE), numpy.int32)
		for i in range(self.PIXELS):
			for j in range(self.PIXELS):
				colorInt = self.getPixel(x, y, i, j)
				for xOffset in range(self.PIXEL_SIZE):
					for yOffset in range(self.PIXEL_SIZE):
						pixels[i * self.PIXEL_SIZE + xOffset, j * self.PIXEL_SIZE + yOffset] = int(colorInt)
		surface = pygame.Surface((128, 128))
		surfarray.blit_array(surface, pixels)
		return surface

	#endless loop that handles generating chunks in the chunk queue
	def chunkThread(self):
		while not self.EXITING: #don't get stuck if exiting here either
			self.chunkCond.acquire()
			while self.chunkQueue == [] and not self.EXITING: #don't get stuck if exiting
				self.chunkCond.wait()
			if self.EXITING: break #helps prevent errors when exiting
			chunkCoords = self.chunkQueue.pop(0)
			self.chunkCond.release()
			surface = self.genChunk(chunkCoords[0], chunkCoords[1])
			self.chunkLock.acquire()
			self.surfaces[chunkCoords[0], chunkCoords[1]] = surface
			self.chunkLock.release()

	#function to help cleanup chunkThread for exiting
	def cleanup(self):
		self.EXITING = True #tell the thread to exit
		self.chunkCond.acquire() #acquire this just to notify..
		self.chunkCond.notify() #make sure the thread wakes up so it can end
		self.chunkCond.release() #just in case
		self.chunkThread.join() #make sure it ends before the main thread

	def update(self):
		dt = self.clock.tick(60)

		for event in pygame.event.get():
			if event.type == pygame.QUIT: 
				self.cleanup()
				sys.exit()

		inKeys = pygame.key.get_pressed()

		if inKeys[pygame.K_ESCAPE]:
			self.cleanup()
			return False
		if inKeys[pygame.K_RIGHT]:
			self.screenX += math.floor(self.MOVE_SPEED * dt)
		if inKeys[pygame.K_LEFT]:
			self.screenX -= math.floor(self.MOVE_SPEED * dt)
		if inKeys[pygame.K_UP]:
			self.screenY -= math.floor(self.MOVE_SPEED * dt)
		if inKeys[pygame.K_DOWN]:
			self.screenY += math.floor(self.MOVE_SPEED * dt)

		chunkGenerated = False
		self.screen.fill((0, 0, 0))
		self.chunkLock.acquire()
		self.chunkCond.acquire()
		for x in range(self.screenX // self.CHUNK_SIZE, (self.width + self.screenX) // self.CHUNK_SIZE + 1):
			for y in range(self.screenY // self.CHUNK_SIZE, (self.height + self.screenY) // self.CHUNK_SIZE + 1):
				if (x, y) in self.surfaces:
					self.screen.blit(self.surfaces[x,y], (self.CHUNK_SIZE * x - self.screenX, self.CHUNK_SIZE * y - self.screenY))
				else:
					self.surfaces[x, y] = pygame.Surface((0, 0))
					self.chunkQueue.append((x, y))
					self.chunkCond.notify()
		self.chunkCond.release()
		self.chunkLock.release()
		pygame.display.flip()

class PerlinGenerator(Generator):

	def __init__(self):
		Generator.__init__(self)
		self.perlin = Perlin.Perlin(350)

	def getColor(self, height):
		return (int(255 * height), int(255 * height), int(255 * height))

	def getPixel(self, x, y, i, j):
		color = self.getColor(self.perlin.octave(i * self.PIXEL_SIZE + x * self.CHUNK_SIZE, j * self.PIXEL_SIZE + y * self.CHUNK_SIZE, 3, 0.5))
		return self.colorToInt(color)

class LandscapeGenerator(PerlinGenerator):

	def getColor(self, height):
		if height <= 0.20:
			return (105,210,231)
		if height <= 0.34:
			return (167,219,216)
		if height <= 0.37:
			return (224,228,204)
		if height <= 0.4:
			return (186,219,129)
		if height <= 0.6:
			return (124,197,130)
		if height <= 0.68:
			return (62,175,131)
		if height <= 0.75:
			return (143,154,156)
		if height <= 0.8:
			return (190,195,188)
		if height <= 0.85:
			return (215,218,207)
		else:
			return (230,232,227)

gen = LandscapeGenerator()

while True:
	if gen.update() == False:
		break
