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


FLOOR_IMG = pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/floor-1.png'))

DINO_GOING_IMGS = [pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/run1.png')),
            pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/run2.png'))]

DINO_LOW_IMGS = [pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/low1_1.png'),
                pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/low2_2.png')]


KAKTUS_IMGS = [pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/k1.png')),
               pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/k2.png')),
               pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/k3.png')),
               pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/k4.png')),
               pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/k_medium.png'))]

PTER_IMGS = [pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/enemy1.png'),
             pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/enemy2.png')]

FONT = pygame.font.Font('/home/errorbe/Coding/neat_dino/imgs/font/pixelmix.ttf', 40)


class Dino:
    def __init__(self, x, y):
        self.ANIMATION_TIME = 10
        self.imgs = DINO_GOING_IMGS
        self.y = y
        self.x = x
        self.tick_count = 0
        self.vel = 0
        self.img_count = 0
        self.img = self.imgs[0]
        self.jumpin = False
        self.sneaking = False

    def jump(self):
        if not self.jumpin:
            self.jumpin = True
            self.vel = -JUMP_POWER

    def sneak(self):
        self.sneaking = True

    def move(self):
        if self.jumpin:
            self.vel += GRAVITY
            self.sneaking = False
        self.y += self.vel
        if self.y >= 300:
            self.jumpin = False
            self.vel = 0
        if self.sneaking:
            self.imgs = DINO_LOW_IMGS
        else:
            self.imgs = DINO_GOING_IMGS
        self.sneaking = False

    def draw(self, win):
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
             self.img = self.imgs[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
             self.img = self.imgs[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.imgs[0]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.imgs[1]
        elif self.img_count < self.ANIMATION_TIME * 4 + 1:
            self.img = self.imgs[0]
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


class Enemy:
    def __init__(self, x):
        if random.choice(range(6)) > 2:
            self.type_ = 1
            self.y = 290  # кактус
            self.img = random.choice(KAKTUS_IMGS)
        else:
            self.type_ = 2
            self.y = random.choice([100, 290, 240])
            self.IMGS = PTER_IMGS
            self.img = self.IMGS[0]# птеродактель
            self.img_count = 0
            self.ANIMATION_TIME = 10
        self.passed = False
        self.x = x


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
        if self.type_ == 2:
            self.img_count += 1

            if self.img_count < self.ANIMATION_TIME:
                self.img = self.IMGS[0]
            elif self.img_count < self.ANIMATION_TIME * 2:
                self.img = self.IMGS[1]
            elif self.img_count < self.ANIMATION_TIME * 3:
                self.img = self.IMGS[0]
            elif self.img_count < self.ANIMATION_TIME * 4:
                self.img = self.IMGS[1]
            elif self.img_count == self.ANIMATION_TIME * 4 + 1:
                self.img = self.IMGS[0]
                self.img_count = 0
        win.blit(self.img, (self.x, self.y))




def draw_window(win, floor, dinos, enemies, score, alive):
    win.fill((231, 231, 231))
    floor.draw(win)
    for dino in dinos:
        dino.draw(win)
    for enemy in enemies:
        enemy.draw(win)
    score = FONT.render(f'Score: {int(score)}', 1, (150, 150, 150))
    alive = FONT.render(f'Alive: {alive}', 1, (150, 150, 150))
    win.blit(score, (WIN_WIDTH - 10 - score.get_width(), 10))
    win.blit(alive, (10, 10))
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
    enemies = [Enemy(900)]
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

        enemy_ind = 0
        if len(dinos) > 0:
            if len(enemies) > 1 and dinos[0].x > enemies[0].x + enemies[0].img.get_width():
                enemy_ind = 1

        for x, dino in enumerate(dinos):
            dino.move()
            ge[x].fitness += 0.1

            output = nets[dinos.index(dino)].activate((dino.y,
                                                       abs(enemies[enemy_ind].x
                                                           - dino.x),
                                                      enemies[enemy_ind].y))
            print(dino.y,
                abs(enemies[enemy_ind].x
                - dino.x),
                enemies[enemy_ind].y)
            if output[0] > 0.5:
                dino.jump()
            if output[1] > 0.5:
                dino.sneak()

        rem = []
        add_enemy = False

        for enemy in enemies:
            for x, dino in enumerate(dinos):
                if enemy.collide(dino):
                    ge[x].fitness -= 1
                    dinos.pop(x)
                    ge.pop(x)
                    nets.pop(x)
            if not enemy.passed and dino.x > enemy.x:
                enemy.passed = True
                add_enemy = True
            if enemy.x + enemy.img.get_width() < 0:
                rem.append(enemy)

            enemy.move(int(vel))

        if add_enemy:
            for g in ge:
                g.fitness += 5
            enemies.append(Enemy(random.randrange(801, 1200)))

        for r in rem:
            enemies.remove(r)


        floor.move(int(vel))
        for dino in dinos:
            dino.move()
        score += 0.1
        draw_window(win, floor, dinos, enemies, score, len(dinos))


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
