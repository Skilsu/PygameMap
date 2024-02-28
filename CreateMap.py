import os
import pickle
import random
import sys
import threading

import pygame
import noise
from Animals import Cow

SHAPE = [300, 300]
SCALE = 100.0
PERSISTENCE = 0.8
LACUNARITY = 2.0


class GenerateMap:
    def __init__(self):
        # Set up Pygame
        self.generated_terrain = []
        self.generated_height = []
        self.generated_plants = []
        self.thresholds_terrain = []
        self.thresholds_height = []
        self.main_map = []
        pygame.init()
        self.width, self.height = 1550, 700
        self.init_pos = [1500, 1500]
        self.old_pos = self.init_pos
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.loading_progress = 0
        self.loading_finished = False
        self.stop_thread = False
        self.main_map_generated = False
        self.main_map_drawed = False
        self.running = True
        self.scale = 60
        self.divider = 5
        self.animals = []

    def load_map(self):
        self.loading_progress += 1500
        self.generated_terrain = load_list_from_file("temp/generated_terrain")
        self.loading_progress += 1500
        self.generated_height = load_list_from_file("temp/generated_height")
        self.loading_progress += 1500
        self.generated_plants = load_list_from_file("temp/generated_plants")
        self.loading_progress += 1500
        self.thresholds_terrain = load_list_from_file("temp/thresholds_terrain")
        self.loading_progress += 1500
        self.thresholds_height = load_list_from_file("temp/thresholds_height")
        self.loading_progress += 1500
        self.loading_finished = True
        self.draw_main_map()
        self.draw_zoomed_field()

    def load_main_map(self):
        self.loading_progress += 1
        self.main_map = load_list_from_file("temp/main_map")
        self.loading_progress += 1
        self.main_map_generated = True

    def generate_new_map(self):
        self.generated_terrain = []
        self.generated_height = []
        terrain_base = random.randint(0, 100)
        height_base = random.randint(0, 100)
        for i in range(3000):
            self.loading_progress += 1
            if self.stop_thread:  # Check if the thread should stop
                return
            generated_row = []
            for j in range(3000):
                generated_row.append(noise.pnoise2(i / SCALE / 10,
                                                   j / SCALE / 10,
                                                   octaves=3,
                                                   persistence=PERSISTENCE,
                                                   lacunarity=LACUNARITY,
                                                   repeatx=1000,
                                                   repeaty=1000,
                                                   base=terrain_base) + 0.5)
            self.generated_terrain.append(generated_row)
        for i in range(3000):
            self.loading_progress += 2
            if self.stop_thread:  # Check if the thread should stop
                return
            generated_row = []
            for j in range(3000):
                generated_row.append((noise.pnoise2(i / SCALE / 10,
                                                    j / SCALE / 10,
                                                    octaves=1,
                                                    persistence=PERSISTENCE,
                                                    lacunarity=LACUNARITY,
                                                    repeatx=1000,
                                                    repeaty=1000,
                                                    base=height_base) + 0.5) * 0.6 +
                                     (noise.pnoise2(i / SCALE / 10,
                                                    j / SCALE / 10,
                                                    octaves=4,
                                                    persistence=PERSISTENCE,
                                                    lacunarity=LACUNARITY,
                                                    repeatx=1000,
                                                    repeaty=1000,
                                                    base=height_base) + 0.5) * 0.4
                                     )
            self.generated_height.append(generated_row)
        self.thresholds()
        self.generate_plants()
        self.loading_finished = True
        self.draw_main_map()
        self.draw_zoomed_field()

    def thresholds(self):
        self.thresholds_terrain = []
        self.thresholds_height = []

        # Step 1: Sort the list
        raw_terrain = []
        raw_height = []
        for i in self.generated_terrain:
            raw_terrain.extend(i)
        for i in self.generated_height:
            raw_height.extend(i)
        sorted_terrain = sorted(raw_terrain)
        sorted_height = sorted(raw_height)
        self.loading_progress += 3000
        # Step 2: Calculate the index for the 80th percentile
        self.thresholds_height.append(sorted_height[int(len(sorted_height) * 0.06)])
        self.thresholds_height.append(sorted_height[int(len(sorted_height) * 0.17)])
        self.thresholds_height.append(sorted_height[int(len(sorted_height) * 0.2)])
        self.thresholds_height.append(sorted_height[int(len(sorted_height) * 0.5)])
        self.thresholds_height.append(sorted_height[int(len(sorted_height) * 0.8)])
        self.thresholds_height.append(sorted_height[int(len(sorted_height) * 0.98)])
        self.thresholds_height.append(sorted_height[int(len(sorted_height) * 0.999)])
        self.thresholds_height.append(max(sorted_height))

        self.thresholds_terrain.append(sorted_terrain[int(len(sorted_terrain) * 0.08)])
        self.thresholds_terrain.append(sorted_terrain[int(len(sorted_terrain) * 0.75)])

    def generate_plants(self):
        for i in range(3000):
            self.loading_progress += 1
            if self.stop_thread:  # Check if the thread should stop
                return
            generated_row = []
            for j in range(3000):
                likelihood = random.random()
                if self.generated_height[i][j] < self.thresholds_height[1]:  # water
                    generated_row.append([0, 0, 0, 0, 0])
                elif self.generated_height[i][j] < self.thresholds_height[2]:  # near water
                    generated_row.append([0, 0, 0, 0, 1])  # sand
                elif self.generated_height[i][j] < self.thresholds_height[4]:  # land
                    wood_height = self.generated_height[i][j] - self.thresholds_height[2]  # pos - coastline
                    wood_threshold = self.thresholds_height[4] - self.thresholds_height[2]  # woodline - coastline
                    wood_likelihood = (wood_height / wood_threshold)  # pos / woodline -> %
                    wood_terrain = self.generated_terrain[i][j] - self.thresholds_terrain[1]  # pos - threshold
                    wood_threshold = 1 - self.thresholds_terrain[1]  # max - threshold
                    wood_likelihood *= (wood_terrain / wood_threshold)
                    if self.generated_terrain[i][j] > self.thresholds_terrain[1]:
                        wood_likelihood *= 2

                    dirt_height = self.generated_height[i][j] - self.thresholds_height[2]  # pos - coastline
                    dirt_threshold = self.thresholds_height[3] - self.thresholds_height[2]  # upperboarder - coastline
                    dirt_likelihood = min(dirt_height, dirt_threshold) / dirt_threshold * 4
                    dirt_likelihood = min(dirt_likelihood, (self.generated_terrain[i][j] / self.thresholds_terrain[0]))
                    if self.generated_terrain[i][j] < self.thresholds_terrain[0]:
                        dirt_likelihood *= dirt_likelihood

                    if min(dirt_likelihood, 0.999) < likelihood:  # dirt
                        generated_row.append([0, 0, 0, 0, 0])
                    elif max(wood_likelihood, 0.001) > likelihood:  # wood
                        generated_row.append([0, 1, 0, 0, 0])
                    else:  # grass
                        generated_row.append([1, 0, 0, 0, 0])
                elif self.generated_height[i][j] < self.thresholds_height[5]:  # land
                    wood_height = self.generated_height[i][j] - self.thresholds_height[4]  # pos - woodline
                    wood_threshold = self.thresholds_height[5] - self.thresholds_height[4]  # rockline - woodline
                    wood_likelihood = 1 - ((wood_height / wood_threshold) * 0.75)  # pos / woodline -> %
                    wood_terrain = self.generated_terrain[i][j] - self.thresholds_terrain[1]  # pos - threshold
                    wood_threshold = 1 - self.thresholds_terrain[1]  # max - threshold
                    wood_likelihood *= (wood_terrain / wood_threshold)
                    if self.generated_terrain[i][j] > self.thresholds_terrain[1]:
                        wood_likelihood *= 2

                    dirt_likelihood = self.generated_terrain[i][j] / self.thresholds_terrain[0]
                    if self.generated_terrain[i][j] < self.thresholds_terrain[0]:
                        dirt_likelihood *= dirt_likelihood

                    if min(dirt_likelihood, 0.999) < likelihood:  # dirt
                        generated_row.append([0, 0, 0, 0, 0])
                    elif max(wood_likelihood, 0.001) > likelihood:  # wood
                        generated_row.append([0, 1, 0, 0, 0])
                    else:  # grass
                        generated_row.append([1, 0, 0, 0, 0])
                elif self.generated_height[i][j] < self.thresholds_height[6]:  # lower highland
                    wood_height = self.generated_height[i][j] - self.thresholds_height[5]  # pos - rockline
                    wood_threshold = self.thresholds_height[6] - self.thresholds_height[5]  # snowline - rockline
                    wood_likelihood = 1 - ((wood_height / wood_threshold) * 0.75)  # pos / rockline -> %
                    wood_terrain = self.generated_terrain[i][j] - self.thresholds_terrain[1]  # pos - threshold
                    wood_threshold = self.thresholds_height[7] - self.thresholds_terrain[1]  # max - threshold
                    wood_likelihood *= (wood_terrain / wood_threshold)
                    if wood_likelihood > likelihood:  # rocky moss ?
                        generated_row.append([1, 0, 0, 0, 0])
                    else:  # rock
                        generated_row.append([0, 0, 0, 1, 0])
                else:
                    if self.generated_terrain[i][j] < self.thresholds_terrain[0]:  # snow
                        generated_row.append([0, 0, 0, 0, 0])
                    else:  # rock
                        generated_row.append([0, 0, 0, 1, 0])
            self.generated_plants.append(generated_row)

    def get_color(self, i, j):
        i = int(i)
        j = int(j)
        if self.generated_height[i][j] < self.thresholds_height[1]:  # water
            hight_multiplier = int(self.generated_height[i][j] / self.thresholds_height[1] * 5) / 5
            color = (0, 150 * max(0, hight_multiplier - 3), 100 + (154 * hight_multiplier))
        elif self.generated_height[i][j] < self.thresholds_height[5]:  # land
            hight_multiplier = int((self.generated_height[i][j] - self.thresholds_height[1]) /
                                   (self.thresholds_height[5] - self.thresholds_height[1]) * 10) / 10
            if self.generated_plants[i][j][0]:  # grass
                green = 125 * hight_multiplier
                color = (0, 255 - green, 0)
            elif self.generated_plants[i][j][1]:  # wood
                green = 50 * hight_multiplier
                color = (0, 100 - green, 0)
            elif self.generated_plants[i][j][4]:  # sand
                color = (255, 255, 153)
            else:  # dirt
                red = 60 * hight_multiplier
                green = 45 * hight_multiplier
                blue = 15 * hight_multiplier
                color = (220 - red, 180 - green, 90 - blue)  # return 120, 50, 10 wet dirt
        else:  # highland
            hight_multiplier = int(((self.generated_height[i][j] - self.thresholds_height[5]) /
                                    (self.thresholds_height[7] - self.thresholds_height[5])) * 5) * 20
            if self.generated_plants[i][j][0]:  # moss
                color = (50 + hight_multiplier, 100 + hight_multiplier, 50 + hight_multiplier)
            elif self.generated_plants[i][j][3]:  # rock
                color = (150 - hight_multiplier, 150 - hight_multiplier, 150 - hight_multiplier)
            else:
                """if self.generated_terrain[i][j] < self.thresholds_terrain[0]:  # glacier
                    return 102, 204, 255
                else:  """  # snow
                color = (255, 255, 255)
        return min(255, max(0, color[0])), min(255, max(0, color[1])), min(255, max(0, color[2]))

    def generate_main_map_pos(self, x, y):
        land_flag = True
        if self.generated_height[x * 10][y * 10] < self.thresholds_height[1]:
            land_flag = False
        lower_bound_x = max(0, x * 10 - 20)
        upper_bound_x = min(2999, x * 10 + 20)
        lower_bound_y = max(0, y * 10 - 20)
        upper_bound_y = min(2999, y * 10 + 20)
        land_amount, tree_amount, sand_amount, rock_amount, dirt_amount = 0, 0, 0, 0, 0
        # pixel_amount = (upper_bound_x - lower_bound_x) / (upper_bound_y - lower_bound_y)
        if land_flag:
            for i in range(lower_bound_x, upper_bound_x):
                for j in range(lower_bound_y, upper_bound_y):
                    if self.generated_height[i][j] > self.thresholds_height[1]:
                        land_amount += 1
                    if self.generated_plants[i][j][1]:
                        tree_amount += 1
                    elif self.generated_plants[i][j][4]:
                        sand_amount += 1
                    elif self.generated_plants[i][j][3]:
                        rock_amount += 1
                    elif all(element == 0 for element in self.generated_plants[i][j]):
                        dirt_amount += 1
        return [land_amount, tree_amount, sand_amount, rock_amount, dirt_amount]

    def generate_main_map(self):
        self.main_map = []
        for x in range(int(SHAPE[0])):
            row = []
            for y in range(int(SHAPE[1])):
                self.loading_progress += 1
                row.append(self.generate_main_map_pos(x, y))
            self.main_map.append(row)
        self.main_map_generated = True

    def get_color_main_map(self, x, y):  # TODO implement correct
        if not self.main_map_generated:
            return self.get_color(x, y)
        land_amount, tree_amount, sand_amount, rock_amount, dirt_amount = self.main_map[int(x / 10)][int(y / 10)]
        color = self.get_color(x, y)
        if self.thresholds_height[1] <= self.generated_height[x][y] < self.thresholds_height[5]:  # land
            hight_multiplier = int((self.generated_height[x][y] - self.thresholds_height[1]) /
                                   (self.thresholds_height[5] - self.thresholds_height[1]) * 10) / 10
            green = 255 - 125 * hight_multiplier
            if tree_amount > 30:
                tree_percentage = min(1, 0.3 + (int((tree_amount / land_amount) * 6) / 5))
                tree_green = (100 - (50 * hight_multiplier)) * tree_percentage
            else:
                tree_percentage, tree_green = 0, 0
            if sand_amount > 30:
                sand_percentage = min(1, 0.2 + (int((sand_amount / land_amount) * 6) / 4))
                sand_red = 255 * sand_percentage
                sand_green = 255 * sand_percentage
                sand_blue = 153 * sand_percentage
            else:
                sand_percentage, sand_red, sand_green, sand_blue = 0, 0, 0, 0
            if rock_amount > 30:
                rock_percentage = min(1, 0.2 + (int((rock_amount / land_amount) * 6) / 4))
                rock_red = 125 * rock_percentage
                rock_green = 125 * rock_percentage
                rock_blue = 125 * rock_percentage
            else:
                rock_percentage, rock_red, rock_green, rock_blue = 0, 0, 0, 0
            if dirt_amount > 30:
                dirt_percentage = min(1, max(0, int((dirt_amount / land_amount) * 4) / 4))
                dirt_red = (220 - (60 * hight_multiplier)) * dirt_percentage
                dirt_green = (180 - (45 * hight_multiplier)) * dirt_percentage
                dirt_blue = (90 - (15 * hight_multiplier)) * dirt_percentage
            else:
                dirt_percentage, dirt_red, dirt_green, dirt_blue = 0, 0, 0, 0
            green = ((green * (1 - (tree_percentage + sand_percentage + rock_percentage + dirt_percentage))) +
                     tree_green + sand_green + rock_green + dirt_green)
            color = (sand_red + rock_red + dirt_red, green, sand_blue + rock_blue + dirt_blue)
        elif self.thresholds_height[5] <= self.generated_height[x][y]:  # highland
            hight_multiplier = int(((self.generated_height[x][y] - self.thresholds_height[5]) /
                                    (self.thresholds_height[7] - self.thresholds_height[5])) * 5) * 20
        return min(255, max(0, color[0])), min(255, max(0, color[1])), min(255, max(0, color[2]))

    def draw_main_map(self):
        self.screen.fill((0, 0, 0))
        for i in range(int(SHAPE[0])):
            for j in range(int(SHAPE[1])):
                pygame.draw.circle(self.screen, self.get_color_main_map(i * 10, j * 10),
                                   (i * 2 + 50, j * 2 + 50), 1)

    def draw_zoomed_field(self):
        scale = 60
        divider = 5
        # fill old edge
        x_start = int(self.old_pos[0] / divider) + 50
        y_start = int(self.old_pos[1] / divider) + 50
        for i in range(scale):
            pygame.draw.circle(self.screen,
                               self.get_color_main_map(self.old_pos[0] + i * divider, self.old_pos[1]),
                               (x_start + i, y_start), 1)
            pygame.draw.circle(self.screen,
                               self.get_color_main_map(self.old_pos[0] + i * divider,
                                                       self.old_pos[1] + scale * divider),
                               (x_start + i, y_start + scale), 1)
            pygame.draw.circle(self.screen,
                               self.get_color_main_map(self.old_pos[0], self.old_pos[1] + i * divider),
                               (x_start, y_start + i), 1)
            pygame.draw.circle(self.screen,
                               self.get_color_main_map(self.old_pos[0] + scale * divider,
                                                       self.old_pos[1] + i * divider),
                               (x_start + scale, y_start + i), 1)
        # create new edge
        x_start = int(self.init_pos[0] / 5) + 50
        y_start = int(self.init_pos[1] / 5) + 50
        for i in range(x_start, x_start + scale):
            pygame.draw.circle(self.screen, (255, 255, 255),
                               (i, y_start), 1)
            pygame.draw.circle(self.screen, (255, 255, 255),
                               (i, y_start + scale), 1)

        for i in range(y_start, y_start + scale):
            pygame.draw.circle(self.screen, (255, 255, 255),
                               (x_start, i), 1)
            pygame.draw.circle(self.screen, (255, 255, 255),
                               (x_start + scale, i), 1)
        # draw new map
        for i in range(self.init_pos[0], self.init_pos[0] + int(SHAPE[0])):
            for j in range(self.init_pos[1], self.init_pos[1] + int(SHAPE[1])):
                pygame.draw.circle(self.screen, self.get_color(i, j),
                                   (700 + (i - self.init_pos[0]) * 2, (j - self.init_pos[1]) * 2 + 50), 1)
        pygame.display.flip()

    def draw_animals(self):
        for a in self.animals:
            if (self.init_pos[0] + 2 <= a.x <= self.init_pos[0] + self.scale * self.divider - 3 and
                    self.init_pos[1] + 2 <= a.y <= self.init_pos[1] + self.scale * self.divider - 3):
                self.redraw_position(a.x, a.y)
            else:
                self.redraw_main_map_pos(a.x, a.y)

        for a in self.animals:
            if (self.init_pos[0] + 1 <= a.x <= self.init_pos[0] + self.scale * self.divider - 2 and
                    self.init_pos[1] + 1 <= a.y <= self.init_pos[1] + self.scale * self.divider - 2):
                pygame.draw.circle(self.screen, (120, 50, 10),
                                   (700 + (int(a.x) - self.init_pos[0]) * 2,
                                    (int(a.y) - self.init_pos[1]) * 2 + 50), a.size + 1)
        if len(self.animals) > 0:
            action_text = f"Action: {self.animals[0].action}"
            food_text = f"Food: {self.animals[0].food:.2f}"
            size_text = f"Size: {self.animals[0].size}"
            age_text = f"Age: {self.animals[0].age:.2f}"
            cows_text = f"Cows: {len(self.animals)}"
            font = pygame.font.Font(None, 36)
            background = pygame.Rect(1350, 50, 200, 300)
            pygame.draw.rect(self.screen, (0, 0, 0), background)
            action_text_surface = font.render(action_text, True, (255, 255, 255))
            self.screen.blit(action_text_surface, (1350, 50))
            food_text_surface = font.render(food_text, True, (255, 255, 255))
            self.screen.blit(food_text_surface, (1350, 100))
            size_text_surface = font.render(size_text, True, (255, 255, 255))
            self.screen.blit(size_text_surface, (1350, 150))
            age_text_surface = font.render(age_text, True, (255, 255, 255))
            self.screen.blit(age_text_surface, (1350, 200))
            cows_text_surface = font.render(cows_text, True, (255, 255, 255))
            self.screen.blit(cows_text_surface, (1350, 250))
        pygame.display.flip()

    def redraw_position(self, x, y):
        for i in range(5):
            for j in range(5):
                pygame.draw.circle(self.screen,
                                   self.get_color(int(x) - 2 + i,
                                                  int(y) - 2 + j),
                                   (700 + ((int(x) - 2 + i) - self.init_pos[0]) * 2,
                                    ((int(y) - 2 + j) - self.init_pos[1]) * 2 + 50), 1)
        self.redraw_main_map_pos(x, y)

    def redraw_main_map_pos(self, x, y):
        for i in range(max(0, int(x) - 20), min(2999, int(x) + 20)):
            for j in range(max(0, int(y) - 20), min(2999, int(y) + 20)):
                if int(i) % 10 == 0 and int(j) % 10 == 0:
                    self.main_map[int(i/10)][int(j/10)] = self.generate_main_map_pos(int(i/10), int(j/10))
                    pygame.draw.circle(self.screen, self.get_color_main_map(int(i), int(j)),
                                       (int(i) / 5 + 50, int(j) / 5 + 50), 1)

    def draw_loading_bar(self, x, y, progress):
        loading_bar = pygame.Rect(x - 200, y - 20, 1, 40)
        pygame.draw.rect(self.screen, (50, 255, 50), pygame.Rect(x - 205, y - 25, 410, 50))
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(x - 200, y - 20, 400, 40))
        loading_bar.width = int(400 * progress)
        pygame.draw.rect(self.screen, (0, 100, 0), loading_bar)
        if self.loading_progress == 9000:
            action_text = f"Continues but not visible!"
        else:
            action_text = f"{100 * progress:.2f} %"
        font = pygame.font.Font(None, 36)
        action_text_surface = font.render(action_text, True, (255, 255, 255))
        text_width, text_height = action_text_surface.get_size()
        self.screen.blit(action_text_surface, (x - text_width / 2,
                                               y - text_height / 2))
        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stop_thread = True
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and self.loading_finished:
                # Get the position of the mouse click
                mouse_x, mouse_y = event.pos
                # Check if the click is within the specified range
                if 50 <= mouse_x <= 650 and 50 <= mouse_y <= 650:
                    # Handle the click position here
                    self.old_pos = self.init_pos
                    self.init_pos = [max(min((mouse_x - 50) * 5 - 150, 2699), 0),
                                     max(min((mouse_y - 50) * 5 - 150, 2699), 0)]
                    self.draw_zoomed_field()
                # Check if the click is within the specified range
                if 700 <= mouse_x <= 1300 and 50 <= mouse_y <= 650:
                    x = self.init_pos[0] + ((mouse_x - 700) / 2)
                    y = self.init_pos[1] + ((mouse_y - 50) / 2)
                    self.animals.append(Cow(x, y))

    def execute_loading_bar(self):
        self.draw_loading_bar(self.width / 2, self.height / 2, self.loading_progress / 15000)
        self.handle_events()
        pygame.time.delay(1)

    def run(self):
        animals_to_remove = []
        for a in self.animals:
            terrain = []
            for i in range(3):
                row = []
                for j in range(3):
                    row.append([self.generated_height[int(a.x + i - 1)][int(a.y + j - 1)],
                                self.generated_terrain[int(a.x + i - 1)][int(a.y + j - 1)],
                                self.generated_plants[int(a.x + i - 1)][int(a.y + j - 1)]])
                terrain.append(row)
            action = a.do(terrain)
            if action:
                if "terrain" in action:
                    self.generated_height[int(a.x)][int(a.y)] = action["terrain"][0]
                    self.generated_terrain[int(a.x)][int(a.y)] = action["terrain"][1]
                    self.generated_plants[int(a.x)][int(a.y)] = action["terrain"][2]
                if "death" in action:
                    animals_to_remove.append(a)
                    if (self.init_pos[0] + 2 <= a.x <= self.init_pos[0] + self.scale * self.divider - 3 and
                            self.init_pos[1] + 2 <= a.y <= self.init_pos[1] + self.scale * self.divider - 3):
                        self.redraw_position(a.x, a.y)
                    else:
                        self.redraw_main_map_pos(a.x, a.y)
        for a in animals_to_remove:
            self.animals.remove(a)
        self.draw_animals()
        self.handle_events()
        pygame.time.delay(1)


def save_list_to_file(lst, filename):
    """Save a list to a file using pickle."""
    with open(filename, 'wb') as f:
        pickle.dump(lst, f)


def load_list_from_file(filename):
    """Load a list from a file using pickle."""
    with open(filename, 'rb') as f:
        lst = pickle.load(f)
    return lst


if __name__ == '__main__':
    newmap = GenerateMap()

    if not os.path.exists("temp/generated_terrain"):
        threading.Thread(target=newmap.generate_new_map).start()
    else:
        threading.Thread(target=newmap.load_map).start()

    while not newmap.loading_finished and newmap.running:
        newmap.execute_loading_bar()

    newmap.loading_progress = 0

    if not os.path.exists("temp/main_map"):
        threading.Thread(target=newmap.generate_main_map).start()
        amount = SHAPE[0] * SHAPE[1]
    else:
        threading.Thread(target=newmap.load_main_map).start()
        amount = 2

    while not newmap.main_map_generated and newmap.running:
        newmap.run()
        newmap.draw_loading_bar(350, 675, newmap.loading_progress / amount)

    newmap.draw_main_map()
    newmap.draw_zoomed_field()

    while newmap.running:
        newmap.run()

    pygame.quit()
    if newmap.loading_finished:
        save_list_to_file(newmap.generated_terrain, "temp/generated_terrain")
        save_list_to_file(newmap.generated_height, "temp/generated_height")
        save_list_to_file(newmap.generated_plants, "temp/generated_plants")
        save_list_to_file(newmap.thresholds_terrain, "temp/thresholds_terrain")
        save_list_to_file(newmap.thresholds_height, "temp/thresholds_height")
    if newmap.main_map_generated:
        save_list_to_file(newmap.main_map, "temp/main_map")
    sys.exit()
