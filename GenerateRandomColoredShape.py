import random

import pygame
import noise

SHAPE = [300, 300]
SCALE = 100.0
OCTAVES = 9
PERSISTENCE = 0.5
LACUNARITY = 2.0


class GenerateMap:
    def __init__(self):
        # Set up Pygame
        self.generated_map = []
        pygame.init()
        width, height = 700, 700
        self.screen = pygame.display.set_mode((width, height))
        self.generate_new_map()
        self.running = True

    def generate_new_map(self):
        self.generated_map = []
        base = random.randint(0, 100)
        base_2 = random.randint(0, 100)
        base_3 = random.randint(0, 100)
        for i in range(300):
            generated_row = []
            for j in range(300):
                generated_row.append([noise.pnoise2(i / SCALE,
                                                    j / SCALE,
                                                    octaves=OCTAVES,
                                                    persistence=PERSISTENCE,
                                                    lacunarity=LACUNARITY,
                                                    repeatx=1000,
                                                    repeaty=1000,
                                                    base=base) / 2 + 0.5,
                                      noise.pnoise2(i / SCALE,
                                                    j / SCALE,
                                                    octaves=OCTAVES,
                                                    persistence=PERSISTENCE,
                                                    lacunarity=LACUNARITY,
                                                    repeatx=1000,
                                                    repeaty=1000,
                                                    base=base_2) / 2 + 0.5,
                                      noise.pnoise2(i / SCALE,
                                                    j / SCALE,
                                                    octaves=OCTAVES,
                                                    persistence=PERSISTENCE,
                                                    lacunarity=LACUNARITY,
                                                    repeatx=1000,
                                                    repeaty=1000,
                                                    base=base_3) / 2 + 0.5])
            self.generated_map.append(generated_row)

    def generate_new_map_random(self):
        self.generated_map = []
        for i in range(300):
            generated_row = []
            for j in range(300):
                generated_row.append([random.random(), random.random(), random.random()])
            self.generated_map.append(generated_row)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.generate_new_map()
                self.draw()

    def draw(self):
        for idx, i in enumerate(self.generated_map):
            for jdx, j in enumerate(i):

                pygame.draw.circle(self.screen, (min(255, 255 * j[0] ** 1.5),
                                                 min(255, 255 * j[1] ** 1.5),
                                                 min(255, 255 * j[2] ** 1.5)),
                                   (idx * 2 + 50, jdx * 2 + 50), 1)
        pygame.display.flip()

    def run(self):
        self.draw()
        while self.running:
            self.handle_events()
            pygame.time.delay(1)


newmap = GenerateMap()
newmap.run()
