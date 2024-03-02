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
        self.thresholds_height = []
        pygame.init()
        width, height = 700, 500
        self.screen = pygame.display.set_mode((width, height))
        self.generate_new_map()
        self.running = True
        self.thresholds()

    def generate_new_map(self):
        self.generated_map = []
        base = random.randint(0, 100)
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
                                                    base=base) / 2 + 0.5])
            self.generated_map.append(generated_row)

    def thresholds(self):
        self.thresholds_height = []

        # Step 1: Sort the list
        raw_height = []
        for i in self.generated_map:
            raw_height.extend(i)
        sorted_height = sorted(raw_height)
        # Step 2: Calculate the index for the 80th percentile
        self.thresholds_height.extend(sorted_height[int(len(sorted_height) * 0.06)])
        self.thresholds_height.extend(sorted_height[int(len(sorted_height) * 0.17)])
        self.thresholds_height.extend(sorted_height[int(len(sorted_height) * 0.2)])
        self.thresholds_height.extend(sorted_height[int(len(sorted_height) * 0.5)])
        self.thresholds_height.extend(sorted_height[int(len(sorted_height) * 0.8)])
        self.thresholds_height.extend(sorted_height[int(len(sorted_height) * 0.98)])
        self.thresholds_height.extend(sorted_height[int(len(sorted_height) * 0.999)])
        self.thresholds_height.extend(max(sorted_height))

    def get_color(self, i, j):
        i = int(i)
        j = int(j)
        if self.generated_map[i][j][0] < self.thresholds_height[1]:  # water
            hight_multiplier = int(self.generated_map[i][j][0] / self.thresholds_height[1] * 5) / 5
            color = (0, 150 * max(0, hight_multiplier - 3), 100 + (154 * hight_multiplier))
        elif self.generated_map[i][j][0] < self.thresholds_height[5]:  # land
            hight_multiplier = int((self.generated_map[i][j][0] - self.thresholds_height[1]) /
                                   (self.thresholds_height[5] - self.thresholds_height[1]) * 10) / 10
            green = 125 * hight_multiplier
            color = (0, 255 - green, 0)

        else:  # highland
            hight_multiplier = int(((self.generated_map[i][j][0] - self.thresholds_height[5]) /
                                    (self.thresholds_height[7] - self.thresholds_height[5])) * 5) * 20
            color = (150 - hight_multiplier, 150 - hight_multiplier, 150 - hight_multiplier)

        return min(255, max(0, color[0])), min(255, max(0, color[1])), min(255, max(0, color[2]))

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
        self.screen.fill((255, 255, 255))
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(40, 40, 620, 420))
        for idx, i in enumerate(self.generated_map):
            for jdx, j in enumerate(i):
                if j[0] < self.thresholds_height[1]:
                    height = jdx + 225 - self.thresholds_height[1] * 250
                else:
                    height = jdx + 225 - j[0] * 250
                pygame.draw.circle(self.screen, self.get_color(idx, jdx),
                                   (idx * 2 + 50, height), 2)
        pygame.display.flip()

    def run(self):
        self.draw()
        while self.running:
            self.handle_events()
            pygame.time.delay(1)


newmap = GenerateMap()
newmap.run()
