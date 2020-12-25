import os
import sys

import pygame

pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 999

pygame.display.set_caption('Once upon a castle')  # или что-то другое :)
pygame.display.set_icon(pygame.image.load('data/player.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
all_sprites = pygame.sprite.Group()
static_block = pygame.sprite.Group()
start_sprites = pygame.sprite.Group()


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


class StaticBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static_block, all_sprites)
        self.image = pygame.transform.scale(load_image('static_block.png'), (75, 25))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


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
    wall = pygame.transform.scale(load_image('wall.png'), (35, 35))
    for i in range(WIDTH // 18):
        screen.blit(wall, (-(wall.get_width() // 2), wall.get_height() * i))
    wall = pygame.transform.rotate(wall, 180)
    for i in range(WIDTH // 18):
        screen.blit(wall, (WIDTH - (wall.get_width() // 2), wall.get_height() * i))
    # основной цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        start_sprites.draw(screen)


def terminate():
    pygame.quit()
    sys.exit()


start_screen()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    pygame.display.flip()
    clock.tick(FPS)
terminate()
