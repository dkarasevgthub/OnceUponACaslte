import os
import random
import sys

import pygame

pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 60
GRAVITY = 0.25

pygame.display.set_caption('Once upon a castle')
pygame.display.set_icon(pygame.image.load('data/player.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
static_block = pygame.sprite.Group()
dynamic_block = pygame.sprite.Group()
start_sprites = pygame.sprite.Group()
crashed_block = pygame.sprite.Group()
player = pygame.sprite.Group()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print('Файл с изображением ' + '"' + fullname + '"' + ' не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def start_screen():
    # задний фон
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    # текст
    font = pygame.font.Font('data/font.ttf', 20)
    text = font.render("Have fun!", True, pygame.Color((20, 20, 20)))
    text_rect = text.get_rect()
    text_rect.x = 30
    text_rect.y = 90
    screen.blit(text, text_rect)
    # блок
    block = pygame.sprite.Sprite(start_sprites)
    block.image = pygame.transform.scale(load_image('static_block.png'), (75, 25))
    block.rect = block.image.get_rect()
    block.rect.x, block.rect.y = 250, 450
    # основной цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        start_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


class StaticBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static_block)
        self.image = pygame.transform.scale(load_image('static_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class DynamicBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(dynamic_block)
        self.image = pygame.transform.scale(load_image('dynamic_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self):
        if self.rect.x >= 25 and self.rect.x + self.rect.w <= WIDTH - 25:
            self.rect = self.rect.move(1, 0)
        else:
            pass


class CrashedBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(crashed_block)
        self.image = pygame.transform.scale(load_image('crashed_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.velocity = [random.choice(range(-5, 5)), random.choice(range(-5, 5))]
        self.gravity = GRAVITY
        self.screen_rect = (0, 0, WIDTH, HEIGHT)

    def update(self):
        # BlocksDropping()
        pass


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


start_screen()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            DynamicBlock(event.pos[0], event.pos[1])
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    wall = pygame.transform.scale(load_image('wall.png'), (35, 35))
    for i in range(WIDTH // 18):
        screen.blit(wall, (-(wall.get_width() // 2), wall.get_height() * i))
    wall = pygame.transform.rotate(wall, 180)
    for i in range(WIDTH // 18):
        screen.blit(wall, (WIDTH - (wall.get_width() // 2), wall.get_height() * i))
    dynamic_block.draw(screen)
    dynamic_block.update()
    pygame.display.flip()
    clock.tick(FPS)
terminate()
