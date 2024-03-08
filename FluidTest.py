import pygame


class GenerateMap:
    def __init__(self):
        # Set up Pygame
        self.generated_map = []
        pygame.init()
        width, height = 500, 500
        self.screen = pygame.display.set_mode((width, height))
        self.generate_new_map()
        self.running = True

    def generate_new_map(self):
        self.generated_map = [[0 for _ in range(20)] for _ in range(20)]

    def act(self):
        for idx, row in enumerate(self.generated_map):
            for jdx, position in enumerate(row):
                min_x = max(0, idx - 1)
                max_x = min(idx + 1, 200)
                min_y = max(0, jdx - 1)
                max_y = min(jdx + 1, 200)
                pos = []
                for i in range(min_x, max_x):
                    for j in range(min_y, max_y):
                        pos.append(self.generated_map[i][j])
                diff = 0
                lowest = min(pos)
                pos.remove(lowest)
                for i in pos:
                    diff += i - lowest
                goal = lowest + (diff / 9)
                self.generated_map[idx][jdx] += (goal - self.generated_map[idx][jdx]) / 10

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 51 < mouse_x < 449 and 51 < mouse_y < 449:
                    mouse_x -= 50
                    mouse_y -= 50
                    mouse_x /= 20
                    mouse_y /= 20
                    self.generated_map[int(mouse_x)][int(mouse_y)] += 1
                self.draw()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for idx, i in enumerate(self.generated_map):
            for jdx, j in enumerate(i):
                pygame.draw.circle(self.screen, (100, min(255, 255 * j), 100),
                                   (idx * 20 + 50, jdx * 20 + 50), 5)
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
