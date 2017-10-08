import sys, pygame, Perlin
pygame.init()

size = width, height = 800, 800

screen = pygame.display.set_mode(size)

screen.fill((0, 0, 0))

perlin = Perlin.Perlin(70)

y = 0

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT: sys.exit()
	if y <= height:
		for x in range(width):
			brightness = perlin.genNoise(x, y)
			screen.set_at((x, y), (brightness * 255, brightness * 255, brightness * 255))
		y += 1

	pygame.display.flip()