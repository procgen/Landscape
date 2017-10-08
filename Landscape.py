import sys, pygame, Perlin, math
pygame.init()

size = width, height = 800, 800

screen = pygame.display.set_mode(size)


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

screen.fill((0, 0, 0))
screenX = 0
screenY = 0

perlin = Perlin.Perlin(350)
y = 0

CHUNK_SIZE = 100

surfaces = {}

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()

	inKeys = pygame.key.get_pressed()

	if inKeys[pygame.K_RIGHT]:
		screenX += 1
	if inKeys[pygame.K_LEFT]:
		screenX -= 1
	if inKeys[pygame.K_UP]:
		screenY += 1
	if inKeys[pygame.K_DOWN]:
		screenY -= 1

	chunkGenerated = False
	screen.fill((0, 0, 0))
	for x in range(width // CHUNK_SIZE):
		for y in range(height // CHUNK_SIZE):
			if (x, y) in surfaces:
				screen.blit(surfaces[x,y], (CHUNK_SIZE * x - screenX, CHUNK_SIZE * y + screenY))
			else:
				chunkGenerated = True
				surface = pygame.Surface((CHUNK_SIZE, CHUNK_SIZE))
				for i in range(CHUNK_SIZE):
					for j in range(CHUNK_SIZE):
						surface.set_at((i, j), getColor(perlin.octave(i + x * CHUNK_SIZE, j + y * CHUNK_SIZE, 3, 0.5)))
				surfaces[x, y] = surface
				break
		if chunkGenerated:
			break

	pygame.display.flip()