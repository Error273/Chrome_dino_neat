import pygame
import random
import neat

WIN_WIDTH = 800
WIN_HEIGHT = 400

GRAVITY = 0.4
JUMP_POWER = 10

pygame.init()


pygame.display.set_caption('damn.')
clock = pygame.time.Clock()


FLOOR_IMG = pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/floor-1.png'))
DINO_IMGS = [pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/run1.png')),
            pygame.transform.scale2x(pygame.image.load('/home/errorbe/Coding/neat_dino/imgs/run2.png'))]


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



def draw_window(win, floor, dino):
    win.fill((231, 231, 231))
    floor.draw(win)
    dino.draw(win)
    pygame.display.update()




def main():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    floor = Floor(350)
    dino = Dino(200, 300)


    runnin = True
    while runnin:
        pygame.draw.line(win, (255, 0, 0), (0, 0), (500, 500), 5)
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                runnin = False
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                dino.jump()

        floor.move(5)
        dino.move()

        draw_window(win, floor, dino)

main()
