import pygame
import sys
import random
import math
from funcoes import *
from classes import *

def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Geometry Dash Clone")
    clock = pygame.time.Clock()

    # Carrega e redimensiona o mesmo background usado nos níveis
    bg_menu = pygame.image.load("assets/img/background.png").convert()
    bg_menu = pygame.transform.scale(bg_menu, screen.get_size())
    font = pygame.font.SysFont(None, 48)

    immortal_mode = False

    while True:
        dt = clock.tick(60) / 1000.0
        screen.blit(bg_menu, (0, 0))

        title = font.render("Selecione a fase", True, (255,255,255))
        opt0  = font.render(f"0 - {'Desligar' if immortal_mode else 'Ligar'} Modo Imortal", True, (255,255,255))
        opt1  = font.render("1 - Fase 1", True, (255,255,255))
        opt2  = font.render("2 - Fase 2", True, (255,255,255))
        opt3  = font.render("3 - Fase 3", True, (255,255,255))
        screen.blit(title, ((800-title.get_width())//2, 160))
        screen.blit(opt0,  ((800-opt0.get_width())//2, 240))
        screen.blit(opt1,  ((800-opt1.get_width())//2, 300))
        screen.blit(opt2,  ((800-opt2.get_width())//2, 360))
        screen.blit(opt3,  ((800-opt3.get_width())//2, 420))

        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_0:
                    immortal_mode = not immortal_mode
                elif ev.key == pygame.K_1:
                    background_music = 'assets/sounds/background_1.mp3'
                    run_phase(screen, clock, 1, background_music, immortal_mode)
                elif ev.key == pygame.K_2:
                    background_music = 'assets/sounds/background_2.mp3'
                    run_phase(screen, clock, 2, background_music, immortal_mode)
                elif ev.key == pygame.K_3:
                    background_music = 'assets/sounds/background_3.mp3'
                    run_phase(screen, clock, 3, background_music, immortal_mode)

if __name__ == '__main__':
    main()