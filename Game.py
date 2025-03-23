#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
import math
from sys import exit
from random import randint, choice

# Inicialização do Pygame e configuração do ícone
pygame.init()
icon = pygame.image.load("Assets/graphics/game_icon.png")
pygame.display.set_icon(icon)
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('3993463 - Alien Avoid - Francisco Sadi Santos Pontes')

# --- Carregamento de Sons ---
bg_music = pygame.mixer.Sound('Assets/audio/music.mp3')
bg_music.play(loops=-1)
collision_sound = pygame.mixer.Sound('Assets/audio/squeaky-toy.mp3')
collision_sound.set_volume(0.7)

# --- Classes ---

class Jogador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Carrega as imagens da animação de caminhada
        caminhar1 = pygame.image.load('Assets/graphics/player/player_walk_1.png').convert_alpha()
        caminhar2 = pygame.image.load('Assets/graphics/player/player_walk_2.png').convert_alpha()
        self.caminhada = [caminhar1, caminhar2]
        self.indice_caminhada = 0
        # Carrega a imagem de pulo
        self.pulo_img = pygame.image.load('Assets/graphics/player/jump.png').convert_alpha()

        # Posiciona o jogador centralizado
        self.image = self.caminhada[self.indice_caminhada]
        self.rect = self.image.get_rect(midbottom=(250, 300))
        self.gravidade = 0

        self.som_pulo = pygame.mixer.Sound('Assets/audio/jump.mp3')
        self.som_pulo.set_volume(0.5)

    def entrada(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravidade = -20
            self.som_pulo.play()

    def aplicar_gravidade(self):
        self.gravidade += 1
        self.rect.y += self.gravidade
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animacao(self):
        if self.rect.bottom < 300:
            self.image = self.pulo_img
        else:
            self.indice_caminhada += 0.1
            if self.indice_caminhada >= len(self.caminhada):
                self.indice_caminhada = 0
            self.image = self.caminhada[int(self.indice_caminhada)]

    def update(self):
        self.entrada()
        self.aplicar_gravidade()
        self.animacao()


class Obstaculo(pygame.sprite.Sprite):
    def __init__(self, tipo):
        super().__init__()
        self.tipo = tipo
        if tipo == 'flying_alien':
            fly1 = pygame.image.load('Assets/graphics/flying_alien/flying_alien1.png').convert_alpha()
            fly2 = pygame.image.load('Assets/graphics/flying_alien/flying_alien2.png').convert_alpha()
            self.frames = [fly1, fly2]
            y_pos = 190  # Alien voador em posição elevada
        else:  # ground_alien
            alien1 = pygame.image.load('Assets/graphics/ground_alien/ground_alien1.png').convert_alpha()
            alien2 = pygame.image.load('Assets/graphics/ground_alien/ground_alien2.png').convert_alpha()
            self.frames = [alien1, alien2]
            y_pos = 300

        self.indice_animacao = 0
        self.image = self.frames[self.indice_animacao]
        self.rect = self.image.get_rect(midbottom=(randint(900, 1100), y_pos))
        self.pontuado = False  # Evita pontuação múltipla

    def animacao(self):
        self.indice_animacao += 0.1
        if self.indice_animacao >= len(self.frames):
            self.indice_animacao = 0
        self.image = self.frames[int(self.indice_animacao)]

    def update(self):
        global pontuacao
        self.animacao()
        if self.tipo == 'ground_alien':
            self.rect.x -= 5
        else:
            self.rect.x -= 6

        if not self.pontuado and self.rect.right < jogador.sprite.rect.left:
            if self.tipo == 'ground_alien' and jogador.sprite.rect.bottom < 300:
                pontuacao += 1
                self.pontuado = True
            elif self.tipo == 'flying_alien' and self.rect.centery < jogador.sprite.rect.top:
                pontuacao += 1
                self.pontuado = True

        if self.rect.x <= -100:
            self.kill()


def mostrar_pontuacao():
    texto = fonte.render(f'Pontos: {pontuacao}', False, (64, 64, 64))
    texto_rect = texto.get_rect(center=(400, 50))
    screen.blit(texto, texto_rect)


def colisao():
    if pygame.sprite.spritecollide(jogador.sprite, obstaculos, False):
        obstaculos.empty()
        return False
    return True


def efeito_colisao():
    """Efeito visual e sonoro ao colidir:
       - O jogador pisca (blink effect) por um curto período.
       - Em seguida, a tela realiza um fade out.
    """
    global bg_x_pos, ground_x_pos
    collision_sound.play()

    # Blink effect: faz o jogador piscar por 1 segundo.
    duracao_blink = 1000  # duração em milissegundos
    intervalo_blink = 100  # intervalo de piscar (ms)
    tempo_inicial_blink = pygame.time.get_ticks()
    while pygame.time.get_ticks() - tempo_inicial_blink < duracao_blink:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        # Alterna visibilidade
        if ((pygame.time.get_ticks() - tempo_inicial_blink) // intervalo_blink) % 2 == 0:
            jogador.sprite.image.set_alpha(0)
        else:
            jogador.sprite.image.set_alpha(255)
        # Redesenha o fundo para evitar rastro
        screen.blit(sky_surface, (bg_x_pos, 0))
        screen.blit(sky_surface, (bg_x_pos + sky_surface.get_width(), 0))
        screen.blit(ground_surface, (ground_x_pos, 300))
        screen.blit(jogador.sprite.image, jogador.sprite.rect)
        pygame.display.update()
        clock.tick(60)

    # Restaura a imagem original
    jogador.sprite.image.set_alpha(255)

    # Fade out: aumenta progressivamente uma camada preta sobre a tela.
    fade_surface = pygame.Surface((800, 400))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade_surface.set_alpha(alpha)
        screen.blit(sky_surface, (bg_x_pos, 0))
        screen.blit(sky_surface, (bg_x_pos + sky_surface.get_width(), 0))
        screen.blit(ground_surface, (ground_x_pos, 300))
        screen.blit(jogador.sprite.image, jogador.sprite.rect)
        screen.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(30)


# --- Configuração inicial do jogo ---
clock = pygame.time.Clock()
fonte = pygame.font.Font('Assets/font/Minecraft.ttf', 20)
fonte_grande = pygame.font.Font('Assets/font/Minecraft.ttf', 50)

game_active = False
game_started = False
pontuacao = 0

jogador = pygame.sprite.GroupSingle()
jogador.add(Jogador())
obstaculos = pygame.sprite.Group()

sky_surface = pygame.image.load('Assets/graphics/Sky.png').convert()
ground_surface = pygame.image.load('Assets/graphics/ground.png').convert()

player_stand = pygame.image.load('Assets/graphics/player/player_stand.png').convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center=(400, 200))

game_name = fonte.render('Alien Avoid - 3993463', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center=(400, 80))
start_message = fonte.render('Pressione espaco para jogar', False, (111, 196, 169))
start_message_rect = start_message.get_rect(center=(400, 330))

obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

bg_x_pos = 0
ground_x_pos = 0
scroll_speed = 1


def main():
    global game_active, game_started, pontuacao, bg_x_pos, ground_x_pos

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if game_active:
                if event.type == obstacle_timer:
                    obstaculos.add(Obstaculo(choice(['flying_alien', 'ground_alien', 'ground_alien', 'ground_alien'])))
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    pontuacao = 0
                    obstaculos.empty()
                    jogador.sprite.rect.midbottom = (250, 300)
                    jogador.sprite.gravidade = 0
                    game_started = True

        if game_active:
            # Atualiza o scroll do fundo
            bg_x_pos -= scroll_speed
            if bg_x_pos <= -sky_surface.get_width():
                bg_x_pos = 0
            ground_x_pos -= scroll_speed
            if ground_x_pos <= -ground_surface.get_width():
                ground_x_pos = 0

            screen.blit(sky_surface, (bg_x_pos, 0))
            screen.blit(sky_surface, (bg_x_pos + sky_surface.get_width(), 0))
            screen.blit(ground_surface, (ground_x_pos, 300))
            screen.blit(ground_surface, (ground_x_pos + ground_surface.get_width(), 300))

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
                # Tela de início: fundo azul petróleo escuro
                screen.fill((0, 60, 80))
                screen.blit(game_name, game_name_rect)
                screen.blit(start_message, start_message_rect)

                alpha_value = 128 + 127 * math.sin(pygame.time.get_ticks() / 500)
                player_stand.set_alpha(alpha_value)
                screen.blit(player_stand, player_stand_rect)
            else:
                # Tela de Game Over: fundo preto, texto branco
                screen.fill((0, 0, 0))
                game_over_text = fonte_grande.render("FIM DE JOGO", True, (255, 255, 255))
                game_over_rect = game_over_text.get_rect(center=(400, 150))
                screen.blit(game_over_text, game_over_rect)
                score_message = fonte.render(f'Sua pontuacão total foi: {pontuacao}', True, (255, 255, 255))
                score_message_rect = score_message.get_rect(center=(400, 250))
                screen.blit(score_message, score_message_rect)
                restart_message = fonte.render("Pressione espaco para reiniciar", True, (255, 255, 255))
                restart_message_rect = restart_message.get_rect(center=(400, 350))
                screen.blit(restart_message, restart_message_rect)

        pygame.display.update()
        clock.tick(60)


if __name__ == '__main__':
    main()