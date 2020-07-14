import pygame
import random
import neat
import os


WIN_WIDTH = 800
WIN_HEIGHT = 400

GRAVITY = 0.4
JUMP_POWER = 10

pygame.init()


pygame.display.set_caption('damn.')
clock = pygame.time.Clock()


FLOOR_IMG = pygame.transform.scale2x(pygame.image.load('imgs/floor-1.png'))
DINO_IMGS = [pygame.transform.scale2x(pygame.image.load('imgs/run1.png')),
            pygame.transform.scale2x(pygame.image.load('imgs/run2.png'))]
KAKTUS_IMGS = [pygame.transform.scale2x(pygame.image.load('imgs/k1.png')),
               pygame.transform.scale2x(pygame.image.load('imgs/k2.png')),
               pygame.transform.scale2x(pygame.image.load('imgs/k3.png')),
               pygame.transform.scale2x(pygame.image.load('imgs/k4.png')),
               pygame.transform.scale2x(pygame.image.load('imgs/k_medium.png'))]
FONT = pygame.font.Font('imgs/font/pixelmix.ttf', 40)

class Dino:
    def __init__(self, x, y):
        self.ANIMATION_TIME = 10
        self.IMGS = DINO_IMGS
        self.y = y
        self.x = x
        self.tick_count = 0
        self.vel = 0
        self.img_count = 0
        self.img = self.IMGS[0]
        self.jumpin = False

    def jump(self):
        if not self.jumpin:
            self.jumpin = True
            self.vel = -JUMP_POWER

    def move(self):
        if self.jumpin:
            self.vel += GRAVITY
        self.y += self.vel
        if self.y >= 300:
            self.jumpin = False
            self.vel = 0

    def draw(self, win):
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
             self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
             self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        win.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


class Floor():
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = FLOOR_IMG.get_width()
        self.img = FLOOR_IMG
        self.width = self.img.get_width()

    def move(self, vel):
        self.x1 -= vel
        self.x2 -= vel
        if self.x1 + self.width < 0:
           self.x1 = self.width + self.x2
        if self.x2 + self.width < 0:
            self.x2 = self.width + self.x1

    def draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))


class Kaktus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.img = random.choice(KAKTUS_IMGS)
        if str(self.img) == '<Surface(102x100x32 SW)>':
            self.type_ = 2
        else:
            self.type_ = 1
        self.passed = False


    def move(self, vel):
        self.x -= vel

    def collide(self, dino):
        dino_mask = dino.get_mask()
        mask =  pygame.mask.from_surface(self.img)
        top_offset = (self.x - dino.x, self.y - round(dino.y))
        t_point = dino_mask.overlap(mask, top_offset)
        if t_point:
            return True
        return False

    def draw(self, win):
        win.blit(self.img, (self.x, self.y))



def draw_window(win, floor, dinos, kaktuts, score):
    win.fill((231, 231, 231))
    floor.draw(win)
    for dino in dinos:
        dino.draw(win)
    for kaktus in kaktuts:
        kaktus.draw(win)
    text = FONT.render(f'Score: {int(score)}', 1, (150, 150, 150))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    pygame.display.update()




def main(genomes, config):
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    nets = []
    ge = []
    dinos = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        dinos.append(Dino(200, 300))
        ge.append(g)


    floor = Floor(350)
    kaktuts = [Kaktus(900, 290)]
    score = 0
    vel = 10
    clock = pygame.time.Clock()

    runnin = True
    while runnin and len(dinos):
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runnin = False
                pygame.quit()

        kaktus_ind = 0
        if len(dinos) > 0:
            if len(kaktuts) > 1 and dinos[0].x > kaktuts[0].x + kaktuts[0].img.get_width():
                kaktus_ind = 1

        for x, dino in enumerate(dinos):
            dino.move()
            ge[x].fitness += 0.1

            output = nets[dinos.index(dino)].activate((dino.y,
                                                       abs(kaktuts[kaktus_ind].x - dino.x),
                                                       kaktuts[kaktus_ind].type_,
                                                       vel))

            if output[0] > 0.5:
                dino.jump()

        rem = []
        add_kaktus = False

        for kaktus in kaktuts:
            for x, dino in enumerate(dinos):
                if kaktus.collide(dino):
                    ge[x].fitness -= 1
                    dinos.pop(x)
                    ge.pop(x)
                    nets.pop(x)
            if not kaktus.passed and dino.x > kaktus.x:
                kaktus.passed = True
                add_kaktus = True
            if kaktus.x + kaktus.img.get_width() < 0:
                rem.append(kaktus)

            kaktus.move(int(vel))

        if add_kaktus:
            for g in ge:
                g.fitness += 5
            kaktuts.append(Kaktus(random.randrange(801, 1200), 290))
            vel += 0.3

        for r in rem:
            kaktuts.remove(r)

        floor.move(int(vel))

        for dino in dinos:
            dino.move()
        score += 0.1
        draw_window(win, floor, dinos, kaktuts, score)


def run(confug_path):
    config = neat.config.Config(neat.DefaultGenome,
                               neat.DefaultReproduction,
                               neat.DefaultSpeciesSet,
                               neat.DefaultStagnation,
                               config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)

