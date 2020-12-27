import os
import random
import sys

import pygame

pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 100
GRAVITY = 0.1
JUMP_HEIGHT = 150  # временно, использовал для создания блоков, когда игрока будешь делать поменяй, блоки подстроятся

pygame.display.set_caption('Once upon a castle')
pygame.display.set_icon(pygame.image.load('data/player.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
static_block = pygame.sprite.Group()
dynamic_block = pygame.sprite.Group()
start_sprites = pygame.sprite.Group()
crashed_block = pygame.sprite.Group()
wall = pygame.sprite.Group()
start_player = pygame.sprite.Group()
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
    # игрок
    StartScreenPlayer((block.rect.x, block.rect.y))
    # основной цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                return
        start_sprites.draw(screen)
        start_player.draw(screen)
        start_player.update()
        pygame.display.flip()
        clock.tick(FPS)
        screen.blit(background, (0, 0))
        screen.blit(text, text_rect)


def terminate():
    pygame.quit()
    sys.exit()


class StartScreenPlayer(pygame.sprite.Sprite):
    def __init__(self, block_pos):
        super().__init__(start_player)
        self.image = pygame.transform.scale(load_image('player.png'), (55, 55))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 255, 300
        self.block_pos = block_pos
        self.velocity = [0, 0]
        self.gravity = GRAVITY
        self.fl = True

    def update(self):
        if self.fl:
            if self.rect.y >= 395:
                self.fl = False
            self.velocity[1] += self.gravity
            self.rect.x += self.velocity[0]
            self.rect.y += self.velocity[1]
        else:
            if self.rect.y <= 285:
                self.fl = True
                self.velocity = [0, 0]
            self.velocity[1] -= self.gravity
            self.rect.x -= self.velocity[0]
            self.rect.y -= self.velocity[1]


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
        self.fl = True

    def update(self):
        if self.fl:
            if self.rect.x == WIDTH - self.rect.w - 25:
                self.fl = False
            self.rect = self.rect.move(1, 0)
        else:
            if self.rect.x == 25:
                self.fl = True
            self.rect = self.rect.move(-1, 0)


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


class Player(pygame.sprite.Sprite):
    def __init__(self, block_pos):
        super().__init__(player)
        self.image = pygame.transform.scale(load_image('player.png'), (55, 55))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 175, 400
        self.block_pos = block_pos
        self.velocity = [0, 0]
        self.gravity = GRAVITY
        self.up = True
        self.height = 0

    def update(self):
        if self.up:
            if self.height < 50:
                self.height += 1
                self.velocity[1] -= self.gravity
                self.rect.x -= self.velocity[0]
                self.rect.y -= self.velocity[1]
            else:
                self.up = False
        else:
            if self.height > 0:
                self.height -= 1
                self.velocity[1] += self.gravity
                self.rect.x += self.velocity[0]
                self.rect.y += self.velocity[1]
            else:
                self.up = True


start_screen()
running = True
for i in range(WIDTH // 18):
    WallLeft((-(35 // 2), 35 * i))
for i in range(WIDTH // 18):
    WallRight((WIDTH - (35 // 2), 35 * i))
for i in range(0, HEIGHT, JUMP_HEIGHT // 2):
    if i // (JUMP_HEIGHT // 2) == random.randint(1, HEIGHT // (JUMP_HEIGHT // 2)):
        DynamicBlock(random.randint(25, WIDTH - 85), i)
    elif i // (JUMP_HEIGHT // 2) == random.randint(1, HEIGHT // (JUMP_HEIGHT // 2)):
        CrashedBlock(random.randint(25, WIDTH - 85), i)
    else:
        StaticBlock(random.randint(25, WIDTH - 85), i)
Player((0, 0))
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    wall.draw(screen)
    static_block.draw(screen)
    dynamic_block.draw(screen)
    dynamic_block.update()
    crashed_block.draw(screen)
    crashed_block.update()
    player.draw(screen)
    player.update()
    pygame.display.flip()
    clock.tick(FPS)
terminate()