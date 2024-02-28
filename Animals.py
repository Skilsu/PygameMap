import random

import pygame


class Cow:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.action = "random"
        self.direction_x = 0
        self.direction_y = 0
        self.time = 0
        self.food = random.randint(25, 200)
        self.size = 0
        self.age = 0  # TODO rethink!

    def do(self, terrain):
        self.food -= 0.01
        self.age += 0.002
        if self.food > 250 and self.size < 2:
            self.food = 100
            self.size += 1
        if self.food < 0:
            return {"death": True}
        rnd_death = random.random()
        if self.food < 25:
            if rnd_death < 0.0005:
                return {"death": True}
        elif self.food < 100:
            if rnd_death < 0.00002:
                return {"death": True}
        elif self.age > 70:
            if rnd_death < 0.0005:
                return {"death": True}
        if self.food < 100 or self.size < 2:
            if self.action == "random":
                if terrain[1][1][2][0] == 1 or terrain[1][1][2][1] == 1:
                    self.time = 100
                    self.action = "eat"
                else:
                    self.time = 50
                    self.action = "move"
                    flattened_terrain = []
                    for x, row in enumerate(terrain):
                        for y, col in enumerate(row):
                            flattened_terrain.append((x, y, col[1], col[2]))

                    sorted_terrain = sorted(flattened_terrain, key=lambda elem: elem[2], reverse=True)
                    self.direction_x = sorted_terrain[0][0] - 1
                    self.direction_y = sorted_terrain[0][1] - 1
                    # Check conditions
                    possible_dirs = []
                    for x, y, _, type in sorted_terrain:
                        if type[0] == 1 or type[1] == 1:
                            possible_dirs.append([x, y])
                    if possible_dirs:
                        direction = random.choice(possible_dirs)
                        self.direction_x = direction[0] - 1
                        self.direction_y = direction[1] - 1

        if self.action == "random":
            action = random.random()
            self.time = random.randint(0, 100)
            if action < 0.3:
                self.action = "move"
                self.direction_x = random.randint(-1, 1)
                self.direction_y = random.randint(-1, 1)
            elif action < 0.95:
                self.action = "pause"
            else:
                self.action = "eat"
        elif self.action == "move":
            if self.time <= 0:
                self.action = "random"
            else:
                self.time -= 1
                self.x = max(min(self.x + self.direction_x * 0.02, 2999), 0)
                self.y = max(min(self.y + self.direction_y * 0.02, 2999), 0)
        elif self.action == "pause":
            if self.time <= 0:
                self.action = "random"
            else:
                self.time -= 1
        elif self.action == "eat":
            if self.time <= 0:
                self.action = "random"
                if terrain[1][1][2][0] == 1:  # grass
                    self.food += terrain[1][1][1] * 25
                    terrain[1][1][1] = terrain[1][1][1] / 2
                    terrain[1][1][2][0] = 0
                elif terrain[1][1][2][1] == 1:  # wood
                    self.food += terrain[1][1][1] * 5
                    terrain[1][1][1] -= terrain[1][1][1] / 5
                    if terrain[1][1][1] < 0.3:
                        terrain[1][1][2][1] = 0
                return {"terrain": [terrain[1][1][0], terrain[1][1][1], terrain[1][1][2]]}
            else:
                self.time -= 4
        return
