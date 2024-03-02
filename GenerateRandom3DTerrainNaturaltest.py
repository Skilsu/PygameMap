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
        width, height = 1400, 800
        self.screen = pygame.display.set_mode((width, height))
        self.generate_new_map()
        self.running = True
        self.thresholds()

    def generate_new_map(self):
        self.generated_map = []
        base = random.randint(0, 100)
        for i in range(400):
            generated_row = []
            for j in range(3000):
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
        self.screen.fill((0, 0, 0))
        x = len(self.generated_map)
        y = len(self.generated_map[0])
        for idx, i in enumerate(self.generated_map):
            for jdx, j in enumerate(i):
                if x - 2 > idx and y - 2 > jdx:
                    multiplier = 2
                    height_multiplier = 500
                    d_x = idx * multiplier
                    d_y = jdx * multiplier
                    if j[0] < self.thresholds_height[1]:
                        height_1 = d_y - (self.thresholds_height[1] * height_multiplier)
                        height_2 = height_1
                        height_3 = height_1 + multiplier
                        height_4 = height_3
                    else:
                        height_1 = d_y - (self.generated_map[idx][jdx][0] * height_multiplier)
                        height_2 = d_y - (self.generated_map[idx + 1][jdx][0] * height_multiplier)
                        height_3 = d_y + multiplier - (self.generated_map[idx][jdx + 1][0] * height_multiplier)
                        height_4 = d_y + multiplier - (self.generated_map[idx + 1][jdx + 1][0] * height_multiplier)

                    width_1 = d_x * 2
                    width_2 = (d_x + multiplier) * 2
                    width_3 = width_1
                    width_4 = width_2

                    color_1 = self.get_color(idx, jdx)
                    color_2 = self.get_color(idx + 1, jdx)
                    color_3 = self.get_color(idx, jdx + 1)
                    color_4 = self.get_color(idx + 1, jdx + 1)

                    color_p1 = (int((color_1[0] + color_2[0] + color_3[0]) / 3),
                                int((color_1[1] + color_2[1] + color_3[1]) / 3),
                                int((color_1[2] + color_2[2] + color_3[2]) / 3))
                    color_p2 = (int((color_4[0] + color_2[0] + color_3[0]) / 3),
                                int((color_4[1] + color_2[1] + color_3[1]) / 3),
                                int((color_4[2] + color_2[2] + color_3[2]) / 3))
                    pygame.draw.polygon(self.screen, color_p1,
                                        ((width_1, height_1),
                                         (width_2, height_2),
                                         (width_3, height_3)))
                    pygame.draw.polygon(self.screen, color_p2,
                                        ((width_4, height_4),
                                         (width_2, height_2),
                                         (width_3, height_3)))
        pygame.display.flip()

    def run(self):
        self.draw()
        while self.running:
            self.handle_events()
            pygame.time.delay(1)


newmap = GenerateMap()
newmap.run()
