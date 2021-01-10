import os
import random
import sqlite3
import sys

import pygame

pygame.init()
button = pygame.mixer.Sound('data/button.wav')
jump = pygame.mixer.Sound('data/jump.wav')
jump_menu = pygame.mixer.Sound('data/jump.wav')
crash = pygame.mixer.Sound('data/crash.mp3')
game_over = pygame.mixer.Sound('data/game_over.wav')
menu_music = pygame.mixer.Sound('data/menu_music.mp3')
game_over.set_volume(0.5)
crash.set_volume(0.02)
jump.set_volume(0.1)
jump_menu.set_volume(0.005)
menu_music.set_volume(0.025)
button.set_volume(0.05)
WIDTH = 400
HEIGHT = 600
PIXELS = 300
FPS = 80
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
all_platforms = pygame.sprite.Group()
player_group = pygame.sprite.Group()
block_types = ['static', 'dynamic', 'crashed']


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
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    for sprite in static_block:
        sprite.kill()
    for sprite in dynamic_block:
        sprite.kill()
    for sprite in crashed_block:
        sprite.kill()
    running = True
    for i in range(WIDTH // 18):
        WallLeft((-11, 35 * i))
    for i in range(WIDTH // 18):
        WallRight((WIDTH - 15, 35 * i))
    first_block_pos_x = random.randint(25, WIDTH - 85)
    StaticBlock(first_block_pos_x, HEIGHT - JUMP_HEIGHT // 3)
    hero = Player(first_block_pos_x)
    player_group.add(hero)
    pos_y = 600
    generated_blocks_count = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_RIGHT]:
            hero.right()
        elif pressed[pygame.K_LEFT]:
            hero.left()
        pos_x = random.randint(25, WIDTH - 85)
        pos_y -= random.randint(JUMP_HEIGHT - 80, JUMP_HEIGHT)
        if generated_blocks_count % 2 == 0:
            block_type = block_types[random.randint(0, 2)]
            if block_type == 'dynamic':
                DynamicBlock(pos_x, pos_y)
            elif block_type == 'crashed':
                CrashedBlock(pos_x, pos_y)
            else:
                StaticBlock(pos_x, pos_y)
        else:
            block_type = block_types[random.randint(0, 2)]
            if block_type == 'crashed':
                DynamicBlock(pos_x, pos_y)
            else:
                StaticBlock(pos_x, pos_y)
        generated_blocks_count += 1
        screen.blit(background, (0, 0))
        wall.draw(screen)
        static_block.draw(screen)
        dynamic_block.draw(screen)
        dynamic_block.update()
        crashed_block.draw(screen)
        crashed_block.update()
        all_platforms.update()
        player_group.update()
        all_platforms.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    terminate()


def score_screen():
    menu_music.play()
    # задний фон
    screen.fill((0, 0, 0))
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    # кнопки и текст
    back_rect = pygame.Rect(36, 120, 328, 443)
    home_image = pygame.transform.scale(load_image('home.png'), (90, 30))
    home_image_rect = home_image.get_rect()
    home_image_rect.x, home_image_rect.y = back_rect.x + 120, 565
    font = pygame.font.Font('data/font.ttf', 18)
    title = font.render("Score Tab", True, pygame.Color((20, 20, 20)))
    title_rect = title.get_rect()
    title_rect.x = back_rect.x + 75
    title_rect.y = 80
    font = pygame.font.Font('data/font.ttf', 15)
    table_text = font.render("Name       Best score", True, pygame.Color(20, 20, 20))
    table_text_rect = table_text.get_rect()
    table_text_rect.x = 45
    table_text_rect.y = 135
    border_rect = pygame.Rect(33, 117, 334, 449)
    # отрисовка очков
    con = sqlite3.connect('data/score_base.db')
    cur = con.cursor()
    table_info = cur.execute("""SELECT name, best_score FROM score_table""").fetchall()
    font = pygame.font.Font('data/font.ttf', 14)
    empty = True
    table_texts = []
    table_rect = []
    text = ''
    for i in range(len(table_info)):
        name = table_info[i][0]
        score = table_info[i][1]
        if len(name) > 9:
            name = name[:8] + '...'
            if len(str(score)) > 10:
                score = str(score)[:9] + '.'
                text = font.render(f"{name} {score}", True, pygame.Color(20, 20, 20))
        else:
            text = font.render(f"{name} " + ' ' * (11 - len(name)) + f"{score}", True,
                               pygame.Color(20, 20, 20))
        text_rect = text.get_rect()
        text_rect.x = table_text_rect.x
        text_rect.y = table_text_rect.y + 40 * (i + 1)
        table_rect.append(text_rect)
        table_texts.append(text)
    if table_rect:
        empty = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if home_image_rect.collidepoint(event.pos):
                    button.play()
                    screen.fill((0, 0, 0))
                    menu_music.stop()
                    start_screen()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 4:
                if not empty:
                    if table_rect[0].y == 175 or len(table_rect) <= 10:
                        continue
                    for elem in table_rect:
                        elem.y += 40
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 5:
                if not empty:
                    if table_rect[-1].y == 535 or len(table_rect) <= 10:
                        continue
                    for elem in table_rect:
                        elem.y -= 40
        pygame.draw.rect(screen, pygame.Color((20, 20, 20)), border_rect, 0)
        pygame.draw.rect(screen, pygame.Color((220, 220, 115)), back_rect, 0)
        for i in range(0, 10, 2):
            pygame.draw.rect(screen, pygame.Color(230, 230, 150),
                             pygame.Rect(36, 160 + 40 * i, 164, 40))
        for i in range(0, 10, 2):
            pygame.draw.rect(screen, pygame.Color(230, 230, 150),
                             pygame.Rect(200, 200 + 40 * i, 164, 40))
        pygame.draw.line(screen, pygame.Color(0, 0, 0), (36, 160), (364, 160), 2)
        pygame.draw.line(screen, pygame.Color(0, 0, 0), (200, 120), (200, 563), 2)
        for i in range(len(table_info)):
            screen.blit(table_texts[i], table_rect[i])
        pygame.draw.rect(screen, pygame.Color(220, 220, 115), pygame.Rect(36, 120, 162, 40))
        pygame.draw.rect(screen, pygame.Color(220, 220, 115), pygame.Rect(202, 120, 162, 40))
        screen.blit(table_text, table_text_rect)
        screen.blit(title, title_rect)
        screen.blit(home_image, home_image_rect)
        if empty:
            back_rect = pygame.Rect(50, 200, 300, 150)
            border_rect = pygame.Rect(48, 198, 304, 154)
            font = pygame.font.Font('data/font.ttf', 16)
            text = font.render("Nothing here yet", True, pygame.Color((20, 20, 20)))
            text_rect = text.get_rect()
            text_rect.x = back_rect.x + 25
            text_rect.y = back_rect.y + 60
            pygame.draw.rect(screen, pygame.Color((20, 20, 20)), border_rect, 0)
            pygame.draw.rect(screen, pygame.Color((220, 220, 115)), back_rect, 0)
            screen.blit(text, text_rect)
        pygame.display.flip()
        clock.tick(FPS)


def save_score(name, score):
    name = name.strip()
    lower_name = name.lower()
    exists = False
    con = sqlite3.connect('data/score_base.db')
    cur = con.cursor()
    existed = []
    for tpl in cur.execute("""SELECT name FROM score_table""").fetchall():
        existed.append(*tpl)
    if name in existed or lower_name in existed:
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


def start_screen():
    hero = StartScreenPlayer((255, 300))
    menu_music.play()
    # задний фон
    background = pygame.transform.scale(load_image('background.png'), (WIDTH, HEIGHT))
    screen.blit(background, (0, 0))
    # текст
    font = pygame.font.Font('data/font.ttf', 17)
    text = font.render("Once upon a castle...", True, pygame.Color((20, 20, 20)))
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
                if btn_rect.collidepoint(event.pos):
                    button.play()
                    hero.kill()
                    menu_music.stop()
                    game()
                if exit_image_rect.collidepoint(event.pos):
                    button.play()
                    pygame.time.delay(300)
                    exit()
                if score_tab_image_rect.collidepoint(event.pos):
                    button.play()
                    hero.kill()
                    menu_music.stop()
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
                    button.play()
                    return
                if ok_image_rect.collidepoint(event.pos):
                    button.play()
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


def game_over_screen(score):
    menu_music.play()
    hero = StartScreenPlayer((295, 300), 'end')
    # очки
    font = pygame.font.Font('data/font.ttf', 16)
    fl = False
    if len(str(score)) > 6:
        score = str(score)[:6] + '.'
        fl = True
    text_score = font.render(f'Score: {score} points', True, pygame.Color((20, 20, 20)))
    text_rect = text_score.get_rect()
    text_rect.x, text_rect.y = 40, 100
    if fl:
        text_rect.x, text_rect.y = 20, 100
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
                    button.play()
                    screen.fill((0, 0, 0))
                    hero.kill()
                    menu_music.stop()
                    start_screen()
                if save_image_rect.collidepoint(event.pos):
                    button.play()
                    name_tab(score)
                if exit_image_rect.collidepoint(event.pos):
                    button.play()
                    hero.kill()
                    pygame.time.delay(300)
                    exit()
                if score_tab_image_rect.collidepoint(event.pos):
                    button.play()
                    hero.kill()
                    menu_music.stop()
                    score_screen()
        screen.blit(background, (0, 0))
        screen.blit(save_image, save_image_rect)
        screen.blit(text_score, text_rect)
        screen.blit(exit_image, exit_image_rect)
        screen.blit(restart_image, restart_image_rect)
        screen.blit(game_over_image, image_rect)
        screen.blit(score_tab_image, score_tab_image_rect)
        end_sprites.draw(screen)
        end_player.draw(screen)
        end_player.update()
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


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
                jump_menu.play()
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
        super().__init__(static_block, all_sprites, all_platforms)
        self.image = pygame.transform.scale(load_image('static_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.rect.h = 6


class DynamicBlock(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(dynamic_block, all_sprites, all_platforms)
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
        super().__init__(crashed_block, all_sprites, all_platforms)
        self.image = pygame.transform.scale(load_image('crashed_block.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.rect.h = 6

    def update(self):
        if pygame.sprite.spritecollideany(self, player):
            self.kill()
            crash.play()
            CrashedBlockRight((self.rect.x, self.rect.y))
            CrashedBlockLeft((self.rect.x, self.rect.y))


class CrashedBlockRight(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(crashed_block, all_platforms)
        self.image = pygame.transform.scale(load_image('crashed_block_right.png'), (60, 20))
        self.rect = self.image.get_rect()
        self.screen = (0, 0, WIDTH, HEIGHT)
        self.velocity = [1, -1]
        self.rect.x, self.rect.y = pos
        self.gravity = 0.5

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
        self.gravity = 0.5

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(self.screen):
            self.kill()


class WallLeft(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(wall)
        self.image = pygame.transform.scale(load_image('wall.png'), (26, 35))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


class WallRight(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(wall)
        self.image = pygame.transform.rotate(
            pygame.transform.scale(load_image('wall.png'), (26, 35)), 180)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x):
        super().__init__(player, all_sprites)
        self.image = pygame.transform.scale(load_image('player.png'), (55, 55))
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = HEIGHT - 55
        self.score = 0
        self.height = 0
        self.moving_range = 5
        self.jump = False  # прыгает ли герой
        self.flag = False  # положение по у
        self.flag_coll = False  # соприкосновение с платформой
        self.camera = 0  # положение камеры
        self.camera_move = 0  # плавность камеры

    def update(self):
        if self.rect.y > HEIGHT - self.rect.h + 1:
            self.kill()
            game_over.play()
            game_over_screen(self.score)
        if not self.flag_coll:
            self.camera_move = 0
            self.camera = 0
        if self.rect.y > HEIGHT - 200 and not self.flag:
            self.rect.y -= PIXELS / FPS
        else:
            if self.rect.y > HEIGHT - 50:
                self.flag = False
            else:
                self.flag = True
                self.rect.y += PIXELS / FPS
        if pygame.sprite.spritecollideany(self, all_platforms):
            if self.flag is True:
                self.camera_move = 700 - pygame.sprite.spritecollideany(self, all_platforms).rect.y
                self.flag_coll = True
                self.jump = True
                self.flag = False
                self.score += 10
                jump.play()
        else:
            self.jump = False
        if self.flag_coll:
            self.camera = 10
            self.camera_move -= 10
        if self.camera_move <= 0:
            self.flag_coll = False
        if self.rect.y - self.camera <= 200:
            self.camera -= 10
        for i in all_platforms:
            i.rect.y += self.camera

    def left(self):
        self.rect.x -= self.moving_range
        if pygame.sprite.spritecollideany(self, wall):
            self.rect.x += self.moving_range

    def right(self):
        self.rect.x += self.moving_range
        if pygame.sprite.spritecollideany(self, wall):
            self.rect.x -= self.moving_range


start_screen()
