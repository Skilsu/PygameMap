import copy

import pygame


class GenerateMap:
    def __init__(self):
        # Set up Pygame
        self.generated_map = []
        pygame.init()
        self.screen_size = 400
        width, height = self.screen_size + 100, self.screen_size + 100
        self.grid_size = 50
        self.screen = pygame.display.set_mode((width, height))
        self.generate_new_map()
        self.running = True

    def generate_new_map(self):
        self.generated_map = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]

    def act(self):
        new_map = copy.deepcopy(self.generated_map)
        for idx, row in enumerate(self.generated_map):
            for jdx, position in enumerate(row):
                pos = []
                for i in range(max(0, idx - 1), min(idx + 2, self.grid_size)):
                    for j in range(max(0, jdx - 1), min(jdx + 2, self.grid_size)):
                        pos.append(self.generated_map[i][j])
                diff = 0
                divisor = len(pos)
                lowest = min(pos)
                pos.remove(lowest)
                for i in pos:
                    diff += i - lowest
                goal = lowest + (diff / divisor)
                new_map[idx][jdx] += (goal - self.generated_map[idx][jdx])
        self.generated_map = new_map

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 51 < mouse_x < 449 and 51 < mouse_y < 449:
                    mouse_x -= 50
                    mouse_y -= 50
                    mouse_x /= self.screen_size / self.grid_size
                    mouse_y /= self.screen_size / self.grid_size
                    self.generated_map[int(mouse_x)][int(mouse_y)] += 1
                self.draw()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for idx, i in enumerate(self.generated_map):
            for jdx, j in enumerate(i):
                pygame.draw.circle(self.screen, (100, min(255, 255 * j), 100),
                                   (idx * (self.screen_size / self.grid_size) + 50,
                                    jdx * (self.screen_size / self.grid_size) + 50), 2)
        pygame.display.flip()

    def run(self):
        self.draw()
        while self.running:
            self.handle_events()
            self.act()
            self.draw()
            pygame.time.delay(50)


newmap = GenerateMap()
newmap.run()
