#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import math
from sys import exit
from random import randint, choice

# INITIALIZAÇÃO DO PYGAME E CONFIGURAÇÃO DO ÍCONE
pygame.init()
icon = pygame.image.load("Assets/graphics/game_icon.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('3993463 - Alien Avoid - FRANCISCO SADI SANTOS PONTES')

# --- CARREGAMENTO DE SONS ---
bg_music = pygame.mixer.Sound('Assets/audio/music.mp3')
bg_music.play(loops=-1)
collision_sound = pygame.mixer.Sound('Assets/audio/squeaky-toy.mp3')
collision_sound.set_volume(0.7)
pop_sound = pygame.mixer.Sound('Assets/audio/pop.wav')

# --- FUNÇÃO AUXILIAR PARA INTERPOLAR SUPERFÍCIES ---
def blend_surfaces(surf1, surf2, blend):
    """RETORNA UMA SUPERFÍCIE RESULTANTE DA INTERPOLAÇÃO ENTRE surf1 E surf2.
    BLEND: 0.0 -> 100% surf1; 1.0 -> 100% surf2."""
    temp1 = surf1.copy()
    temp2 = surf2.copy()
    temp1.set_alpha(int((1 - blend) * 255))
    temp2.set_alpha(int(blend * 255))
    result = pygame.Surface(surf1.get_size()).convert()
    result.blit(temp1, (0, 0))
    result.blit(temp2, (0, 0))
    return result

# --- CLASSES ---

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # CARREGA AS IMAGENS DA ANIMAÇÃO DE CAMINHADA
        walk1 = pygame.image.load('Assets/graphics/player/player_walk_1.png').convert_alpha()
        walk2 = pygame.image.load('Assets/graphics/player/player_walk_2.png').convert_alpha()
        self.walk_frames = [walk1, walk2]
        self.walk_index = 0
        # CARREGA AS IMAGENS DE PULO
        self.jump_img = pygame.image.load('Assets/graphics/player/jump.png').convert_alpha()
        self.jump2_img = pygame.image.load('Assets/graphics/player/jump2.png').convert_alpha()
        self.jump3_img = pygame.image.load('Assets/graphics/player/jump3.png').convert_alpha()
        self.image = self.walk_frames[self.walk_index]
        self.rect = self.image.get_rect(midbottom=(250, 300))
        self.gravidade = 0.0
        self.jump_sound = pygame.mixer.Sound('Assets/audio/jump.mp3')
        self.jump_sound.set_volume(0.5)
        # VARIÁVEIS PARA DOUBLE JUMP
        self.double_jump_available = True
        self.space_pressed_last = False
        self.double_jump_timer = 0  # Controla exibição de jump3_img

        # Impulsos (ajuste conforme necessário)
        self.simple_jump_impulse = -12   # pulo simples
        self.double_jump_impulse = -16   # double jump (1.33x simples, pode ser ajustado)
        self.gravity_increment = 0.5       # aceleração suave

    def entrada(self):
        keys = pygame.key.get_pressed()
        # Detecta transição: SPACE pressionado agora e não antes
        if keys[pygame.K_SPACE] and not self.space_pressed_last:
            if self.rect.bottom >= 300:  # Se no chão: pulo simples
                self.gravidade = self.simple_jump_impulse
                self.jump_sound.play()
                self.double_jump_available = True
            elif self.double_jump_available:  # Se no ar e ainda pode double jump:
                self.gravidade = self.double_jump_impulse
                self.double_jump_timer = 20  # Exibe jump3_img por ~0.33 s
                self.double_jump_available = False
        self.space_pressed_last = keys[pygame.K_SPACE]

    def aplicar_gravidade(self):
        self.gravidade += self.gravity_increment
        self.rect.y += self.gravidade
        if self.rect.bottom >= 300:
            self.rect.bottom = 300
            self.double_jump_available = True
        if self.rect.top < 0:
            self.rect.top = 0
            self.gravidade = 0

    def animacao(self):
        if self.rect.bottom < 300:
            self.image = self.jump_img
        else:
            self.walk_index += 0.1
            if self.walk_index >= len(self.walk_frames):
                self.walk_index = 0
            self.image = self.walk_frames[int(self.walk_index)]

    def update(self):
        self.entrada()
        self.aplicar_gravidade()
        if self.double_jump_timer > 0:
            self.image = self.jump3_img
            self.double_jump_timer -= 1
        else:
            self.animacao()

class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo
        if tipo == 'flying_alien':
            # Reduz a altura dos fly para que passem logo acima do player
            fly1 = pygame.image.load('Assets/graphics/flying_alien/flying_alien1.png').convert_alpha()
            fly2 = pygame.image.load('Assets/graphics/flying_alien/flying_alien2.png').convert_alpha()
            self.frames = [fly1, fly2]
            y_pos = 170
        elif tipo == 'man_eater_flower':
            flower1 = pygame.image.load('Assets/graphics/man_eater_flower/man_eater_flower1.png').convert_alpha()
            flower2 = pygame.image.load('Assets/graphics/man_eater_flower/man_eater_flower2.png').convert_alpha()
            self.frames = [flower1, flower2]
            y_pos = 300
        else:  # ground_alien (snail)
            alien1 = pygame.image.load('Assets/graphics/ground_alien/ground_alien1.png').convert_alpha()
            alien2 = pygame.image.load('Assets/graphics/ground_alien/ground_alien2.png').convert_alpha()
            self.frames = [alien1, alien2]
            y_pos = 300
        self.anim_index = 0
        self.image = self.frames[self.anim_index]
        # Posicionamento horizontal aleatório
        self.rect = self.image.get_rect(midbottom=(randint(900, 1300), y_pos))
        self.pontuado = False

    def animacao(self):
        self.anim_index += 0.1
        if self.anim_index >= len(self.frames):
            self.anim_index = 0
        self.image = self.frames[int(self.anim_index)]

    def update(self):
        global pontuacao
        self.animacao()
        if self.tipo == 'flying_alien':
            self.rect.x -= 6
        else:
            self.rect.x -= 5
        if not self.pontuado and self.rect.right < jogador.sprite.rect.left:
            pontuacao += 1
            self.pontuado = True
        if self.rect.x <= -100:
            self.kill()

def colisao():
    collisions = pygame.sprite.spritecollide(jogador.sprite, obstaculos, False)
    for obs in collisions:
        # Define threshold: 20 px para ground_alien e man_eater_flower; 10 para flying_alien
        if obs.tipo in ['ground_alien','man_eater_flower']:
            threshold = 20
        else:
            threshold = 10
        if jogador.sprite.gravidade >= 0 and jogador.sprite.rect.bottom <= obs.rect.top + threshold:
            obs.kill()
            jogador.sprite.image = jogador.sprite.jump2_img
            jogador.sprite.gravidade = -15
            pop_sound.play()
            if not obs.pontuado:
                global pontuacao
                pontuacao += 1
                obs.pontuado = True
        else:
            return False
    return True

def mostrar_pontuacao():
    txt = fonte.render(f'Pontos: {pontuacao}', False, (64,64,64))
    rct = txt.get_rect(center=(400,50))
    screen.blit(txt, rct)

def mostrar_nivel2():
    lvl2_txt = fonte_grande.render("NÍVEL 2", True, (255,255,255))
    lvl2_rect = lvl2_txt.get_rect(center=(400,50))
    screen.blit(lvl2_txt, lvl2_rect)

def efeito_colisao():
    global bg_x_pos, ground_x_pos
    collision_sound.play()
    blink_dur = 1000  # MS
    blink_int = 100  # MS
    start_time = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_time < blink_dur:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        if ((pygame.time.get_ticks() - start_time)//blink_int) % 2 == 0:
            jogador.sprite.image.set_alpha(0)
        else:
            jogador.sprite.image.set_alpha(255)
        screen.blit(current_sky, (bg_x_pos, 0))
        screen.blit(current_sky, (bg_x_pos+current_sky.get_width(), 0))
        screen.blit(ground_surface, (ground_x_pos,300))
        screen.blit(jogador.sprite.image, jogador.sprite.rect)
        pygame.display.update()
        pygame.time.delay(30)
    jogador.sprite.image.set_alpha(255)
    fade_surf = pygame.Surface((800,400))
    fade_surf.fill((0,0,0))
    for alpha in range(0,255,5):
        fade_surf.set_alpha(alpha)
        screen.blit(current_sky, (bg_x_pos,0))
        screen.blit(current_sky, (bg_x_pos+current_sky.get_width(),0))
        screen.blit(ground_surface, (ground_x_pos,300))
        screen.blit(jogador.sprite.image, jogador.sprite.rect)
        screen.blit(fade_surf, (0,0))
        pygame.display.update()
        pygame.time.delay(30)

clock = pygame.time.Clock()
fonte = pygame.font.Font('Assets/font/Minecraft.ttf',20)
fonte_grande = pygame.font.Font('Assets/font/Minecraft.ttf',50)

game_active = False
game_started = False
pontuacao = 0

jogador = pygame.sprite.GroupSingle()
jogador.add(Jogador())
obstaculos = pygame.sprite.Group()

# LOAD BACKGROUNDS
sky_initial = pygame.image.load('Assets/graphics/sky.png').convert()
sky1_0 = pygame.image.load('Assets/graphics/sky1.0.png').convert()
sky1_1 = pygame.image.load('Assets/graphics/sky1.1.png').convert()
current_sky = sky_initial.copy()
ground_surface = pygame.image.load('Assets/graphics/ground.png').convert()

player_stand = pygame.image.load('Assets/graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand,0,2)
player_stand_rect = player_stand.get_rect(center=(400,200))

game_title = fonte.render('ALIEN VOID', False, (111,196,169))
game_title_rect = game_title.get_rect(center=(400,60))
game_info = fonte.render('RU: 3993463 - FRANCISCO SADI SANTOS PONTES', False, (111,196,169))
game_info_rect = game_info.get_rect(center=(400,110))
start_message = fonte.render('Pressione espaco para jogar', False, (111,196,169))
start_message_rect = start_message.get_rect(center=(400,330))

obstacle_timer = pygame.USEREVENT+1
pygame.time.set_timer(obstacle_timer,2000)

bg_x_pos = 0
ground_x_pos = 0
scroll_speed = 1

SECOND_PHASE_THRESHOLD = 2
THIRD_PHASE_THRESHOLD = 3
FINAL_PHASE_THRESHOLD = 5

level2_pause = False
level2_start_time = 0
level2_triggered = False

def main():
    global game_active, game_started, pontuacao, bg_x_pos, ground_x_pos, current_sky, level2_pause, level2_start_time, level2_triggered

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if game_active:
                if event.type == obstacle_timer and not level2_pause:
                    if pontuacao < 5:
                        kind = choice(['flying_alien', 'ground_alien'])
                    else:
                        kind = choice(['flying_alien', 'ground_alien', 'man_eater_flower'])
                    obstaculos.add(Obstaculo(kind))
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    pontuacao = 0
                    obstaculos.empty()
                    jogador.sprite.rect.midbottom = (250,300)
                    jogador.sprite.gravidade = 0
                    game_started = True
                    level2_pause = False
                    level2_triggered = False
                    current_sky = sky_initial.copy()
                    bg_x_pos = 0
                    ground_x_pos = 0

        if game_active:
            if pontuacao >= 15 and not level2_triggered:
                level2_pause = True
                level2_start_time = pygame.time.get_ticks()
                level2_triggered = True
                obstaculos.empty()
                current_sky = sky1_1.copy()
            if level2_pause:
                mostrar_nivel2()
                if pygame.time.get_ticks() - level2_start_time >= 5000:
                    level2_pause = False

            bg_x_pos -= scroll_speed
            if bg_x_pos <= -current_sky.get_width():
                bg_x_pos = 0
            ground_x_pos -= scroll_speed
            if ground_x_pos <= -ground_surface.get_width():
                ground_x_pos = 0

            screen.blit(current_sky, (bg_x_pos,0))
            screen.blit(current_sky, (bg_x_pos+current_sky.get_width(),0))
            screen.blit(ground_surface, (ground_x_pos,300))
            screen.blit(ground_surface, (ground_x_pos+ground_surface.get_width(),300))

            mostrar_pontuacao()
            jogador.draw(screen)
            jogador.update()
            obstaculos.draw(screen)
            obstaculos.update()

            if not colisao():
                efeito_colisao()
                game_active = False
        else:
            if not game_started:
                screen.fill((0,60,80))
                screen.blit(game_title, game_title_rect)
                screen.blit(game_info, game_info_rect)
                screen.blit(start_message, start_message_rect)
                alpha_val = 128+127*math.sin(pygame.time.get_ticks()/500)
                player_stand.set_alpha(alpha_val)
                screen.blit(player_stand, player_stand_rect)
            else:
                screen.fill((0,0,0))
                go_txt = fonte_grande.render("FIM DE JOGO", True, (255,255,255))
                go_rect = go_txt.get_rect(center=(400,150))
                screen.blit(go_txt,go_rect)
                score_msg = fonte.render(f'Sua pontuacão total foi: {pontuacao}', True, (255,255,255))
                score_rect = score_msg.get_rect(center=(400,250))
                screen.blit(score_msg,score_rect)
                re_msg = fonte.render("Pressione espaco para reiniciar", True, (255,255,255))
                re_rect = re_msg.get_rect(center=(400,350))
                screen.blit(re_msg, re_rect)
        pygame.display.update()
        clock.tick(60)

if __name__ == '__main__':
    main()
