import sys, pygame, Perlin
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
perlin = Perlin.Perlin(350)
y = 0
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
	if y <= height:
		for x in range(width):
			heightValue = perlin.octave(x, y, 3, 0.5)
			screen.set_at((x, y), getColor(heightValue))
		y += 1

	pygame.display.flip()