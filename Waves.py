import random

import pygame
import noise

SHAPE = [300, 300]
SCALE = 100.0
OCTAVES = 9
PERSISTENCE = 0.5
LACUNARITY = 2.0


class Wave:
    """
    wave class to simulate moving waves
    """
    def __init__(self, wave_size=10):
        """
        wave_size can be adjusted and refers to coordinate size of get_wave() function.
        :param wave_size:
        """
        self.wave_size = wave_size
        self.factor = 0

    def next(self, increment=0.5):
        """
        Updates factor incrementally to simulate wave moving. Should be called in the game loop.
        higher increment implies faster moving.
        :param increment:
        :return:
        """
        self.factor += increment
        if self.factor == self.wave_size * 2:
            self.factor = 0

    def get_water(self, x, y):
        """
        returns height of the wave (float between 0 and 1) for given coordinates x and y.
        directions and orientations can't be changed via param.
        (TODO: add this functionality to __init__ [or maybe separate method])
        :param x:
        :param y:
        :return:
        """
        x_height = (x + y - self.factor) % self.wave_size
        if x_height > self.wave_size / 2:
            x_height = self.wave_size - x_height
        x_height /= self.wave_size

        y_height = (x - (self.factor / 2)) % self.wave_size
        if y_height > self.wave_size / 2:
            y_height = self.wave_size - y_height
        y_height /= self.wave_size
        pos = (x_height + y_height)
        return pos


class GenerateMap:
    def __init__(self):
        # Set up Pygame
        self.generated_map = []
        pygame.init()
        self.screen_size = 400
        self.noise = []
        width, height = self.screen_size + 100, self.screen_size + 100
        self.grid_size = 50
        self.screen = pygame.display.set_mode((width, height))
        self.running = True
        self.wave = Wave(10)
        self.generate_noise()
        self.generate_new_map()

    def generate_noise(self):
        self.noise = []
        base = random.randint(0, 100)
        for x in range(self.grid_size):
            row = []
            for y in range(self.grid_size):
                row.append(noise.pnoise2(x / SHAPE[0],
                                         y / SHAPE[1],
                                         octaves=OCTAVES,
                                         persistence=PERSISTENCE,
                                         lacunarity=LACUNARITY,
                                         repeatx=1000,
                                         repeaty=1000,
                                         base=base) / 2 + 0.5)
            self.noise.append(row)

    def generate_new_map(self):
        self.generated_map = []
        for x in range(self.grid_size):
            row = []
            for y in range(self.grid_size):
                row.append(self.wave.get_water(x, y))
            self.generated_map.append(row)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.draw()

    def draw(self):
        self.screen.fill((0, 0, 0))
        for idx, i in enumerate(self.generated_map):
            for jdx, j in enumerate(i):
                """pygame.draw.circle(self.screen, (100, min(255, 255 * j), 100),
                                   (idx * (self.screen_size / self.grid_size) + 50,
                                    jdx * (self.screen_size / self.grid_size) + 50), 2)"""
                pygame.draw.circle(self.screen, (0, 0, min(255, 100 + 155 * j)),
                                   (idx * 2 + 50, jdx * 2 + 50 - j * 5), 1)
        pygame.display.flip()

    def run(self):
        self.draw()
        while self.running:
            self.handle_events()
            self.generate_new_map()
            self.wave.next()
            self.draw()
            pygame.time.delay(30)


if __name__ == '__main__':
    newmap = GenerateMap()
    newmap.run()
