import os
import random
import sys

import pygame

pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 100
GRAVITY = 0.25
JUMP_HEIGHT = 75  # временно, использовал для создания блоков, когда игрока будешь делать поменяй, блоки подстроятся

pygame.display.set_caption('Once upon a castle')
pygame.display.set_icon(pygame.image.load('data/player.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
static_block = pygame.sprite.Group()
dynamic_block = pygame.sprite.Group()
start_sprites = pygame.sprite.Group()
crashed_block = pygame.sprite.Group()
wall = pygame.sprite.Group()
player = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


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
    # персонаж
    player = pygame.sprite.Sprite(start_sprites)
    player.image = pygame.transform.scale(load_image('player.png'), (50, 50))
    player.rect = player.image.get_rect()
    player.rect.x, player.rect.y = 250, 400
    player.rect.h = 50
    # update

    def update():
        height = 0
        spusk = False
        if spusk is False:
            player.rect.y -= 1
            if player.rect.y == 300:
                spusk = True
        if spusk is True:
            player.rect.y += 100
            if player.rect.y == 400:
                spusk = False
    # основной цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        update()
        start_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
        screen.blit(background, (0, 0))
        screen.blit(text, text_rect)


def terminate():
    pygame.quit()
    sys.exit()


class StaticBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static_block)
        self.image = pygame.transform.scale(load_image('static_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.rect.h = 6


class DynamicBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(dynamic_block)
        self.image = pygame.transform.scale(load_image('dynamic_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.rect.h = 6

    def update(self):
        if self.rect.x >= 25 and self.rect.x + self.rect.w <= WIDTH - 25:
            self.rect = self.rect.move(1, 0)
        elif self.rect.x != 25:
            pass


class CrashedBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(crashed_block)
        self.image = pygame.transform.scale(load_image('crashed_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.rect.h = 6

    def update(self):
        if pygame.sprite.spritecollideany(self, player):
            self.kill()
            CrashedBlockRight((self.rect.x, self.rect.y))
            CrashedBlockLeft((self.rect.x, self.rect.y))


class CrashedBlockRight(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(crashed_block)
        self.image = pygame.transform.scale(load_image('crashed_block_right.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.screen = (0, 0, WIDTH, HEIGHT)
        self.velocity = [1, -1]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(self.screen):
            self.kill()


class CrashedBlockLeft(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(crashed_block)
        self.image = pygame.transform.scale(load_image('crashed_block_left.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.screen = (0, 0, WIDTH, HEIGHT)
        self.velocity = [-1, -1]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(self.screen):
            self.kill()


class WallLeft(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(wall)
        self.image = pygame.transform.scale(load_image('wall.png'), (35, 35))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


class WallRight(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(wall)
        self.image = pygame.transform.rotate(
            pygame.transform.scale(load_image('wall.png'), (35, 35)), 180)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


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
for i in range(WIDTH // 18):
    WallLeft((-(35 // 2), 35 * i))
for i in range(WIDTH // 18):
    WallRight((WIDTH - (35 // 2), 35 * i))
for i in range(0, HEIGHT, JUMP_HEIGHT):
    if i // JUMP_HEIGHT == random.randint(1, HEIGHT // JUMP_HEIGHT):
        DynamicBlock(random.randint(25, WIDTH - 85), i)
    elif i // JUMP_HEIGHT == random.randint(1, HEIGHT // JUMP_HEIGHT):
        CrashedBlock(random.randint(25, WIDTH - 85), i)
    else:
        StaticBlock(random.randint(25, WIDTH - 85), i)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            StaticBlock(event.pos[0], event.pos[1])
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    wall.draw(screen)
    static_block.draw(screen)
    dynamic_block.draw(screen)
    dynamic_block.update()
    crashed_block.draw(screen)
    crashed_block.update()
    pygame.display.flip()
    clock.tick(FPS)
terminate()
