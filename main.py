import os
import random
import sqlite3
import sys

import pygame

pygame.init()

WIDTH = 400
HEIGHT = 600
FPS = 100
GRAVITY = 0.1
JUMP_HEIGHT = 150

pygame.display.set_caption('Once upon a castle')
pygame.display.set_icon(pygame.image.load('data/player.png'))
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
static_block = pygame.sprite.Group()
dynamic_block = pygame.sprite.Group()
start_sprites = pygame.sprite.Group()
end_player = pygame.sprite.Group()
end_sprites = pygame.sprite.Group()
crashed_block = pygame.sprite.Group()
wall = pygame.sprite.Group()
start_player = pygame.sprite.Group()
player = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()


def load_image(name, color_key=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print('Файл с изображением ' + '"' + fullname + '"' + ' не найден')
        sys.exit()
    image = pygame.image.load(fullname)
    if color_key is not None:
        image = image.convert()
        if color_key == -1:
            color_key = image.get_at((0, 0))
        image.set_colorkey(color_key)
    else:
        image = image.convert_alpha()
    return image


def game():
    # camera = Camera()
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    for sprite in static_block:
        sprite.kill()
    for sprite in dynamic_block:
        sprite.kill()
    for sprite in crashed_block:
        sprite.kill()
    running = True
    for i in range(WIDTH // 18):
        WallLeft((-(35 // 2), 35 * i))
    for i in range(WIDTH // 18):
        WallRight((WIDTH - (35 // 2), 35 * i))
    for i in range(0, HEIGHT - JUMP_HEIGHT // 2, JUMP_HEIGHT // 2):
        if i // (JUMP_HEIGHT // 2) == random.randint(1, HEIGHT // (JUMP_HEIGHT // 2)):
            DynamicBlock(random.randint(25, WIDTH - 85), i)
        elif i // (JUMP_HEIGHT // 2) == random.randint(1, HEIGHT // (JUMP_HEIGHT // 2)):
            CrashedBlock(random.randint(25, WIDTH - 85), i)
        else:
            StaticBlock(random.randint(25, WIDTH - 85), i)
    first_block_pos_x = random.randint(25, WIDTH - 85)
    StaticBlock(first_block_pos_x, HEIGHT - JUMP_HEIGHT // 2)
    hero = Player((first_block_pos_x, (HEIGHT - JUMP_HEIGHT // 2) - 55))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RIGHT]:
            hero.right(5)
        elif pressed[pygame.K_LEFT]:
            hero.left(5)
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
        # camera.update(hero)
        # for sprite in all_sprites:
        # camera.apply(sprite)
    terminate()


def score_screen():
    pass


def save_score(name, score):
    name = name.lower().strip()
    exists = False
    con = sqlite3.connect('data/score_base.db')
    cur = con.cursor()
    existed = []
    for tpl in cur.execute("""SELECT name FROM score_table""").fetchall():
        existed.append(*tpl)
    if name in existed:
        exists = True
    if exists:
        if score > cur.execute(
                f"""SELECT best_score FROM score_table WHERE name='{name}'""").fetchall()[0][0]:
            que = f"""UPDATE score_table
SET last_score={score}, best_score={score}\nWHERE name='{name}'"""
        else:
            que = f"""UPDATE score_table\nSET last_score={score}\nWHERE name='{name}'"""
    else:
        string = 'score_table(name, last_score, best_score)'
        que = f"""INSERT INTO {string} VALUES('{name}', {score}, {score})"""
    cur.execute(que)
    con.commit()
    con.close()


class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('black')
        self.color_active = pygame.Color((150, 32, 40))
        self.text = text
        self.font = pygame.font.Font('data/font.ttf', 16)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            if self.active:
                self.color = self.color_active
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, pygame.Color((20, 20, 20)))

    def draw(self, scr):
        scr.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(scr, self.color, self.rect, 3)

    def text(self):
        return self.txt_surface


class StartScreenPlayer(pygame.sprite.Sprite):
    def __init__(self, player_pos, sort='start'):
        if sort == 'end':
            super().__init__(end_player)
        else:
            super().__init__(start_player)
        self.image = pygame.transform.scale(load_image('player.png'), (55, 55))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = player_pos
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


StartScreenPlayer((255, 300))


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
    # кнопки
    start_image = pygame.transform.scale(load_image('start.png'), (140, 60))
    btn_rect = start_image.get_rect()
    btn_rect.x, btn_rect.y = 50, 380
    exit_image = pygame.transform.scale(load_image('exit.png'), (140, 50))
    exit_image_rect = exit_image.get_rect()
    exit_image_rect.x, exit_image_rect.y = btn_rect.x, btn_rect.y + btn_rect.h + 10
    score_tab_image = pygame.transform.scale(load_image('score_tab.png'), (140, 50))
    score_tab_image_rect = score_tab_image.get_rect()
    score_tab_image_rect.x, score_tab_image_rect.y = \
        btn_rect.x, btn_rect.y + btn_rect.h + 10 + score_tab_image_rect.h + 5
    # основной цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 50 <= event.pos[0] <= 190 and 380 <= event.pos[1] <= 440:
                    game()
                if 50 <= event.pos[0] <= 190 and btn_rect.y + btn_rect.h + 10 <= \
                        event.pos[
                            1] <= btn_rect.y + btn_rect.h + 60:
                    exit()
                if event.pos[0] >= 50 and event.pos[
                    0] <= 190 and btn_rect.y + btn_rect.h + 15 + score_tab_image_rect.h <= \
                        event.pos[
                            1] <= btn_rect.y + btn_rect.h + 15 + score_tab_image_rect.h + 50:
                    score_screen()
        screen.blit(background, (0, 0))
        screen.blit(text, text_rect)
        screen.blit(start_image, btn_rect)
        screen.blit(exit_image, exit_image_rect)
        screen.blit(score_tab_image, score_tab_image_rect)
        start_sprites.draw(screen)
        start_player.draw(screen)
        start_player.update()
        pygame.display.flip()
        clock.tick(FPS)


def name_tab(score):
    input_box = InputBox(60, 275, 280, 30)
    back_rect = pygame.Rect(50, 200, 300, 150)
    border_rect = pygame.Rect(48, 198, 304, 154)
    font = pygame.font.Font('data/font.ttf', 16)
    text = font.render("Enter name", True, pygame.Color((20, 20, 20)))
    text_rect = text.get_rect()
    text_rect.x = back_rect.x + 70
    text_rect.y = back_rect.y + 20
    close_image = pygame.transform.scale(load_image('close.png'), (20, 20))
    close_image_rect = close_image.get_rect()
    close_image_rect.x, close_image_rect.y = 325, text_rect.y - 15
    ok_image = pygame.transform.scale(load_image('ok.png'), (80, 30))
    ok_image_rect = ok_image.get_rect()
    ok_image_rect.x, ok_image_rect.y = 160, 313
    input_box.draw(screen)
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if close_image_rect.collidepoint(event.pos):
                    return
                if ok_image_rect.collidepoint(event.pos):
                    if input_box.text != '':
                        save_score(input_box.text, score)
                        return
            input_box.handle_event(event)
        pygame.draw.rect(screen, pygame.Color((20, 20, 20)), border_rect, 0)
        pygame.draw.rect(screen, pygame.Color((220, 220, 115)), back_rect, 0)
        screen.blit(text, text_rect)
        screen.blit(close_image, close_image_rect)
        screen.blit(ok_image, ok_image_rect)
        input_box.draw(screen)
        pygame.display.flip()


StartScreenPlayer((295, 300), 'end')


def game_over_screen(score):
    # очки
    font = pygame.font.Font('data/font.ttf', 16)
    text_score = font.render('Score: ' + str(score) + ' points', True, pygame.Color((20, 20, 20)))
    text_rect = text_score.get_rect()
    text_rect.x, text_rect.y = 30, 100
    # фон
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    # кнопки и картинки
    save_image = pygame.transform.scale(load_image('save_score.png'),
                                        (text_rect.h + 10, text_rect.h + 10))
    save_image_rect = save_image.get_rect()
    save_image_rect.x, save_image_rect.y = text_rect.x + text_rect.w + 15, text_rect.y - 5
    game_over_image = pygame.transform.scale(load_image('game_over.png'), (240, 120))
    image_rect = game_over_image.get_rect()
    image_rect.x, image_rect.y = WIDTH // 2 - image_rect.w // 2, HEIGHT // 2 - image_rect.h
    restart_image = pygame.transform.scale(load_image('restart.png'), (140, 60))
    restart_image_rect = restart_image.get_rect()
    restart_image_rect.x, restart_image_rect.y = \
        WIDTH // 2 - restart_image_rect.w // 2 - 15, HEIGHT // 2 - restart_image_rect.h // 2 + 125
    exit_image = pygame.transform.scale(load_image('exit.png'), (110, 42))
    exit_image_rect = exit_image.get_rect()
    exit_image_rect.x, exit_image_rect.y = \
        WIDTH // 2 - exit_image_rect.w // 2, HEIGHT // 2 - exit_image_rect.h // \
        2 + 125 + restart_image_rect.h + 5
    score_tab_image = pygame.transform.scale(load_image('score_tab.png'), (110, 42))
    score_tab_image_rect = score_tab_image.get_rect()
    score_tab_image_rect.x, score_tab_image_rect.y = \
        WIDTH // 2 - exit_image_rect.w // 2, HEIGHT // 2 - exit_image_rect.h // \
        2 + 125 + restart_image_rect.h + exit_image_rect.h + 15
    # блок
    block = pygame.sprite.Sprite(end_sprites)
    block.image = pygame.transform.scale(load_image('static_block.png'), (75, 25))
    block.rect = block.image.get_rect()
    block.rect.x, block.rect.y = 290, 450
    # основной цикл
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if restart_image_rect.collidepoint(event.pos):
                    screen.fill((0, 0, 0))
                    start_screen()
                if save_image_rect.collidepoint(event.pos):
                    name_tab(score)
                if exit_image_rect.collidepoint(event.pos):
                    exit()
                if score_tab_image_rect.collidepoint(event.pos):
                    score_screen()
        end_sprites.draw(screen)
        end_player.draw(screen)
        end_player.update()
        screen.blit(background, (0, 0))
        screen.blit(save_image, save_image_rect)
        screen.blit(text_score, text_rect)
        screen.blit(exit_image, exit_image_rect)
        screen.blit(restart_image, restart_image_rect)
        screen.blit(game_over_image, image_rect)
        screen.blit(score_tab_image, score_tab_image_rect)
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


class StaticBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(static_block, all_sprites)
        self.image = pygame.transform.scale(load_image('static_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.rect.h = 6


class DynamicBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(dynamic_block, all_sprites)
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
        super().__init__(crashed_block, all_sprites)
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
        self.dy = 0

    def apply(self, obj):
        obj.rect.y += self.dy

    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


class Player(pygame.sprite.Sprite):
    def __init__(self, block_pos):
        super().__init__(player, all_sprites)
        self.image = pygame.transform.scale(load_image('player.png'), (55, 55))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = block_pos
        self.block_pos = block_pos
        self.velocity = [0, 0]
        self.gravity = GRAVITY
        self.up = True
        self.height = 0
        self.score = 0

    def update(self):
        if self.rect.y > HEIGHT - self.rect.h + 1:
            self.kill()
            game_over_screen(int(self.score / 100))
        else:
            if self.up:
                if self.height < JUMP_HEIGHT:
                    self.height += 1
                    self.rect.y -= 1
                else:
                    self.up = False
            else:
                self.height -= 1
                self.rect.y += 1
            if pygame.sprite.spritecollideany(self, static_block):
                self.moving_up()
                self.score += 100
            if pygame.sprite.spritecollideany(self, dynamic_block):
                self.moving_up()
                self.score += 150
            if pygame.sprite.spritecollideany(self, wall):
                if self.rect.x < 300:
                    self.rect.x += 5
                else:
                    self.rect.x -= 5

    def moving_up(self):
        if self.up is False:
            self.height = 0
            self.up = True

    def left(self, x):
        self.rect.x -= x

    def right(self, x):
        self.rect.x += x


start_screen()
