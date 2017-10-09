import sys, pygame, Perlin, math, threading
import pygame.surfarray as surfarray
import time
import numpy
pygame.init()

size = width, height = 800, 800

screen = pygame.display.set_mode(size)


#CONSTANTS
CHUNK_SIZE = 128
PIXEL_SIZE = 4
EXITING = False

surfaces = {}
chunkQueue = []
chunkCond = threading.Condition()
chunkLock = threading.Lock()

def getColor(height):
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

def genChunk(x, y):
	#surface = pygame.Surface((CHUNK_SIZE, CHUNK_SIZE))
	pixels = numpy.zeros((CHUNK_SIZE, CHUNK_SIZE))
	for i in range(CHUNK_SIZE // PIXEL_SIZE):
		for j in range(CHUNK_SIZE // PIXEL_SIZE):
			color = getColor(perlin.octave(i * PIXEL_SIZE + x * CHUNK_SIZE, j * PIXEL_SIZE + y * CHUNK_SIZE, 3, 0.5))
			colorInt = (color[0] << 16) + (color[1] << 8) + (color[2])
			for xOffset in range(PIXEL_SIZE):
				for yOffset in range(PIXEL_SIZE):
					pixels[i * PIXEL_SIZE + xOffset, j * PIXEL_SIZE + yOffset] = colorInt
					#surface.set_at((i * PIXEL_SIZE + xOffset, j * PIXEL_SIZE + yOffset), color)
	surface = pygame.Surface((128, 128))
	surfarray.blit_array(surface, pixels)
	return surface

#endless loop that handles generating chunks in the chunk queue
def chunkThread():
	while not EXITING: #don't get stuck if exiting here either
		chunkCond.acquire()
		while chunkQueue == [] and not EXITING: #don't get stuck if exiting
			chunkCond.wait()
		if EXITING: break #helps prevent errors when exiting
		chunkCoords = chunkQueue.pop(0)
		chunkCond.release()
		surface = genChunk(chunkCoords[0], chunkCoords[1])
		chunkLock.acquire()
		surfaces[chunkCoords[0], chunkCoords[1]] = surface
		chunkLock.release()

#function to help cleanup chunkThread for exiting
def cleanup():
	global EXITING
	EXITING = True #tell the thread to exit
	chunkCond.acquire() #acquire this just to notify..
	chunkCond.notify() #make sure the thread wakes up so it can end
	chunkCond.release() #just in case
	chunkThread.join() #make sure it ends before the main thread

screen.fill((0, 0, 0))
screenX = 0
screenY = 0

perlin = Perlin.Perlin(350)
y = 0

chunkThread = threading.Thread(target=chunkThread)
chunkThread.start()

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: 
			cleanup()
			sys.exit()

	inKeys = pygame.key.get_pressed()

	if inKeys[pygame.K_ESCAPE]:
		cleanup()
		break
	if inKeys[pygame.K_RIGHT]:
		screenX += 1
	if inKeys[pygame.K_LEFT]:
		screenX -= 1
	if inKeys[pygame.K_UP]:
		screenY -= 1
	if inKeys[pygame.K_DOWN]:
		screenY += 1

	chunkGenerated = False
	screen.fill((0, 0, 0))
	chunkLock.acquire()
	chunkCond.acquire()
	for x in range(screenX // CHUNK_SIZE, (width + screenX) // CHUNK_SIZE + 1):
		for y in range(screenY // CHUNK_SIZE, (height + screenY) // CHUNK_SIZE + 1):
			if (x, y) in surfaces:
				screen.blit(surfaces[x,y], (CHUNK_SIZE * x - screenX, CHUNK_SIZE * y - screenY))
			else:
				surfaces[x, y] = pygame.Surface((0, 0))
				chunkQueue.append((x, y))
				chunkCond.notify()
	chunkCond.release()
	chunkLock.release()
	pygame.display.flip()