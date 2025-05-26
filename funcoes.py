import pygame
import sys
import random
import math
from classes import *

def run_phase(screen, clock, phase, background_music, immortal=False):
    WIDTH, HEIGHT = screen.get_size()
    FPS = 60

    # Carrega e redimensiona background da fase
    bg_img = pygame.image.load("assets/img/background.png").convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    pygame.mixer.music.load(background_music)
    pygame.mixer.music.set_volume(0.5)  # ajuste de volume entre 0.0 e 1.0
    pygame.mixer.music.play(-1)

    # Função de explosão de morte    

    # Física do jogador
    player_size      = 50
    GRAVITY          = 1.0
    desired_height   = 3.5 * player_size
    JUMP_VELOCITY    = -math.sqrt(2 * GRAVITY * desired_height)
    frames_to_apex   = abs(JUMP_VELOCITY) / GRAVITY
    total_air_frames = frames_to_apex * 2
    ROTATION_SPEED   = 180 / total_air_frames

    # Scroll para 4.5× player_size
    desired_distance = 4.5 * player_size
    air_frames       = int(round(total_air_frames))
    scroll_speed     = (desired_distance / air_frames) * 1.25

    # Configurações de fase
    if phase == 1:
        TOTAL_TIME       = 86.0
        spawn_interval   = 1350
        block_chance     = 0.0
        vertical_chance  = 0.0
        min_platform_gap = 0.0
    elif phase == 2:
        TOTAL_TIME       = 159.0
        spawn_interval   = 1150
        block_chance     = 0.7
        vertical_chance  = 0.3
        min_platform_gap = 0.02 * TOTAL_TIME
    else:  # phase == 3
        TOTAL_TIME       = 123.0
        spawn_interval   = 800
        block_chance     = 0.6
        vertical_chance  = 0.4
        min_platform_gap = 0.02 * TOTAL_TIME

    # Gap de 6 blocos para spikes solo (fases ≥2)
    px_per_sec = scroll_speed * FPS
    gap_px     = 6 * player_size
    gap_time   = gap_px / px_per_sec

    # Cores e chão
    BG_COLOR       = (30, 30, 30)
    GROUND_COLOR   = (0,   0, 139)
    LINE_COLOR     = (255,255,255)
    OBSTACLE_COLOR = (30,  30,  30)
    GROUND_HEIGHT  = 100
    ground_y       = HEIGHT - GROUND_HEIGHT

    EDGE_THICKNESS     = 1
    MAX_LINE_THICKNESS = 2

    spikes = []
    blocks = []
    sparks = []
    # portal rosa fase 3
    portal_rect = None
    portal_spawned = False
    portal_particles = []
    # novas partículas coloridas após 40% na fase 3
    phase3_particles = []

    # --- FLASH EFFECT VARIABLES ---
    FLASH_DURATION = 0.2
    flash_timer = 0.0

    SPAWN_OBSTACLE = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_OBSTACLE, spawn_interval)
    font = pygame.font.SysFont(None, 48)

    # Surface do player (quadrados concêntricos)
    player_surf = pygame.Surface((player_size, player_size), pygame.SRCALPHA)
    YELLOW, PURPLE = (255,255,0), (128,0,128)
    LINE_W = player_size // 7
    cx, cy = player_size//2, player_size//2
    pygame.draw.rect(player_surf, YELLOW,
                     pygame.Rect(cx-LINE_W//2, cy-LINE_W//2, LINE_W, LINE_W))
    for color, mult in [(PURPLE,3),(YELLOW,5),(PURPLE,7)]:
        s = LINE_W * mult
        pygame.draw.rect(player_surf, color,
                         pygame.Rect(cx-s//2, cy-s//2, s, s), LINE_W)
    pygame.draw.rect(player_surf, LINE_COLOR, player_surf.get_rect(), 2)

    # Estado do player
    player_rect      = pygame.Rect(100, ground_y-player_size, player_size, player_size)
    vel_y, on_ground = 0, True
    angle, rotating  = 0, False
    elapsed_time     = 0.0
    last_platform    = -gap_time

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        elapsed_time += dt
        percent = min(elapsed_time / TOTAL_TIME * 100, 100)

        # spawn portal rosa em 50%
        if phase == 3 and not portal_spawned and percent >= 50:
            portal_spawned = True
            h = int(3.5 * player_size)
            portal_rect = pygame.Rect(WIDTH, ground_y - h, player_size, h)

        # Atualiza partículas comuns
        for sp in sparks[:]:
            sp.update(dt)
            if sp.life <= 0:
                sparks.remove(sp)
        # Atualiza partículas do portal
        for pp in portal_particles[:]:
            pp.update(dt)
            if pp.life <= 0:
                portal_particles.remove(pp)
        # Atualiza partículas coloridas da fase 3
        for pc in phase3_particles[:]:
            pc.update(dt)
            if pc.life <= 0:
                phase3_particles.remove(pc)

        # adiciona partículas coloridas após 40% na fase 3
        if phase == 3 and percent >= 40:
            for _ in range(10):
                x = random.uniform(0, WIDTH)
                y = random.uniform(0, ground_y - 10)
                p = Spark(x, y)
                # velocidades suaves para "piscar"
                p.vx = random.uniform(-30, 30)
                p.vy = random.uniform(-30, 0)
                p.life = random.uniform(0.2, 0.4)
                # cores variadas
                p.color = random.choice([
                    (255,  0,  0), (  0,255,  0), (  0,  0,255),
                    (255,255,  0), (255,  0,255), (  0,255,255)
                ])
                phase3_particles.append(p)

        # Eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == SPAWN_OBSTACLE:
                base_x = WIDTH

                if phase == 1:
                    if percent < 33:
                        count = 1
                    elif percent < 66:
                        count = random.choice([1, 2])
                    else:
                        count = random.choice([1, 2, 3])
                    for i in range(count):
                        h2 = random.choice([player_size, player_size//2])
                        spikes.append(pygame.Rect(base_x + i*player_size,
                                                  ground_y - h2,
                                                  player_size, h2))

                elif phase == 2:
                    spawn_block = (
                        random.random() < block_chance and
                        (elapsed_time - last_platform) >= min_platform_gap
                    )
                    if spawn_block:
                        last_platform = elapsed_time
                        if random.random() < vertical_chance:
                            blocks.append(pygame.Rect(base_x,
                                                      ground_y - player_size,
                                                      player_size, player_size))
                            blocks.append(pygame.Rect(base_x,
                                                      ground_y - 2*player_size,
                                                      player_size, player_size))
                            if random.random() < 0.5:
                                h2 = random.choice([player_size, player_size//2])
                                spikes.append(pygame.Rect(base_x,
                                                          ground_y - 2*player_size - h2,
                                                          player_size, h2))
                        else:
                            length = random.randint(1, 10)
                            for i in range(length):
                                blocks.append(pygame.Rect(base_x + i*player_size,
                                                          ground_y - player_size,
                                                          player_size, player_size))
                            if random.random() < 0.5:
                                pos = random.choice([0, length-1])
                                spikes.append(pygame.Rect(base_x + pos*player_size,
                                                          ground_y - player_size - player_size,
                                                          player_size, player_size))
                    else:
                        count = random.randint(1, 3)
                        for i in range(count):
                            h2 = random.choice([player_size, player_size//2])
                            spikes.append(pygame.Rect(base_x + i*player_size,
                                                      ground_y - h2,
                                                      player_size, h2))

                else:  # phase == 3
                    if percent < 47:
                        spawn_block = random.random() < block_chance and (elapsed_time - last_platform) >= min_platform_gap
                        
                        if spawn_block:
                            last_platform = elapsed_time

                            if random.random() < vertical_chance:
                                blocks.append(pygame.Rect(base_x,
                                                          ground_y - player_size,
                                                          player_size, player_size))
                                blocks.append(pygame.Rect(base_x,
                                                          ground_y - 2*player_size,
                                                          player_size, player_size))
                                if random.random() < 0.5:
                                    h2 = random.choice([player_size, player_size//2])
                                    spikes.append(pygame.Rect(base_x,
                                                              ground_y - 2*player_size - h2,
                                                              player_size, h2))
                            else:
                                length = random.randint(1, 10)
                                for i in range(length):
                                    blocks.append(pygame.Rect(base_x + i*player_size,
                                                              ground_y - player_size,
                                                              player_size, player_size))
                                if random.random() < 0.5:
                                    pos = random.choice([0, length-1])
                                    spikes.append(pygame.Rect(base_x + pos*player_size,
                                                              ground_y - player_size - player_size,
                                                              player_size, player_size))
                                    
                    elif percent >= 53:  # FLAPPY BIRD AQUI (percent >= 53)
                        # Configurações específicas do modo Flappy
                        gap_height = 3 * player_size  # Espaço para o UFO passar
                        obstacle_width = 70  # Largura dos obstáculos
                        spike_height = 20    # Altura dos espinhos
                        
                        # Gera posição vertical aleatória do gap
                        max_gap_y = HEIGHT - gap_height - GROUND_HEIGHT - 50
                        gap_y = random.randint(50, max_gap_y)
                        
                        # Cria obstáculo superior
                        top_height = gap_y - spike_height
                        blocks.append(pygame.Rect(WIDTH, 0, obstacle_width, top_height))
                        spikes.append(pygame.Rect(WIDTH, top_height, obstacle_width, spike_height))
                        
                        # Cria obstáculo inferior
                        bottom_y = gap_y + gap_height
                        bottom_height = HEIGHT - GROUND_HEIGHT - bottom_y
                        blocks.append(pygame.Rect(WIDTH, bottom_y, obstacle_width, bottom_height))
                        spikes.append(pygame.Rect(WIDTH, bottom_y - spike_height, obstacle_width, spike_height))
    
                        # Espaçamento fixo entre obstáculos
                        last_platform = elapsed_time  # Reinicia temporizador
                            
        # Move e limpa obstáculos
        for s in spikes: s.x -= scroll_speed
        for b in blocks: b.x -= scroll_speed
        spikes[:] = [s for s in spikes if s.right>0]
        blocks[:] = [b for b in blocks if b.right>0]

        # Move portal e emite partículas rosas
        if portal_rect:
            portal_rect.x -= scroll_speed
            for _ in range(5):
                p = Spark(portal_rect.centerx, portal_rect.bottom)
                p.color = (255, 0, 255)
                portal_particles.append(p)

        # --- DETECTA PASSAGEM PELO PORTAL E TRANSFORMA EM UFO ---
        if phase == 3 and portal_rect and player_rect.colliderect(portal_rect):
            flash_timer = FLASH_DURATION
            portal_rect = None
            
            # Atualiza o retângulo de colisão para o tamanho do UFO
            original_center = player_rect.center  # Preserva o centro original
            player_rect = player_surf.get_rect(center=original_center)  # Novo tamanho
    

            # Cria skin de UFO mantendo cores originais
            ufo_skin = UFOSkin(player_size, YELLOW, PURPLE)
            player_surf = ufo_skin.surf
            
            # Efeito de transformação
            for _ in range(30):
                p = Spark(player_rect.centerx, player_rect.centery)
                p.color = (255, 0, 255)  # Rosa do portal
                p.life = random.uniform(0.3, 0.6)
                p.vx = random.uniform(-150, 150)
                p.vy = random.uniform(-150, 150)
                sparks.append(p)

        # Desenha background
        screen.blit(bg_img, (0, 0))

        # --- EFEITO DE PISCADA NA TELA ---
        if flash_timer > 0:
            flash_timer -= dt
            alpha = int(255 * (flash_timer / FLASH_DURATION))
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(alpha)
            overlay.fill((255, 255, 255))
            screen.blit(overlay, (0, 0))

        # Desenha chão e limites
        pygame.draw.rect(screen, GROUND_COLOR, (0, ground_y, WIDTH, GROUND_HEIGHT))
        pts = [
            (0, ground_y),
            (WIDTH, ground_y),
            (WIDTH, ground_y + EDGE_THICKNESS),
            (WIDTH//2, ground_y + MAX_LINE_THICKNESS),
            (0, ground_y + EDGE_THICKNESS)
        ]
        pygame.draw.polygon(screen, LINE_COLOR, pts)

        # Desenha obstáculos
        for b in blocks:
            pygame.draw.rect(screen, OBSTACLE_COLOR, b)
            pygame.draw.rect(screen, LINE_COLOR, b, 2)
        for s in spikes:
            bl = (s.x, s.bottom)
            t  = (s.x + s.width//2, s.bottom - s.height)
            br = (s.x + s.width, s.bottom)
            pygame.draw.polygon(screen, OBSTACLE_COLOR, [bl, t, br])
            pygame.draw.polygon(screen, LINE_COLOR, [bl, t, br], 2)

        # Desenha portal rosa em forma de elipse fechada
        if portal_rect and portal_rect.right > 0:
            pygame.draw.ellipse(screen, (255,0,255), portal_rect, 8)
            for pp in portal_particles:
                pp.draw(screen)

        # Desenha as partículas coloridas da fase 3
        if phase == 3:
            for pc in phase3_particles:
                pc.draw(screen)

        # Salto contínuo
        keys = pygame.key.get_pressed()
        if phase == 3 and percent > 50:
            GRAVITY          = 0.5
            desired_height   = 0.75 * player_size
            JUMP_VELOCITY    = -math.sqrt(2 * GRAVITY * desired_height)
            frames_to_apex   = abs(JUMP_VELOCITY) / GRAVITY
            total_air_frames = frames_to_apex * 2
            if keys[pygame.K_SPACE]:
                vel_y, rotating, angle, on_ground = JUMP_VELOCITY, True, 0, False
                if player_rect.top <= 0:
                    vel_y = 0
                for _ in range(12):
                    p = Spark(player_rect.centerx, player_rect.bottom)
                    p.color = (255, 165, 0)
                    p.vx = random.uniform(-100, 100)
                    p.vy = random.uniform(50, 150)
                    sparks.append(p)
        else:
            if on_ground and keys[pygame.K_SPACE]:
                vel_y, rotating, angle, on_ground = JUMP_VELOCITY, True, 0, False

        # Física do player
        vel_y += GRAVITY
        player_rect.y += vel_y
        prev_on_ground = on_ground
        on_ground = False
        if player_rect.bottom >= ground_y:
            player_rect.bottom, vel_y, on_ground = ground_y, 0, True
            if rotating:
                angle = 180
            rotating = False
            for _ in range(5):
                sparks.append(Spark(player_rect.left, ground_y - 4))
            if keys[pygame.K_SPACE]:
                vel_y, rotating, angle, on_ground = JUMP_VELOCITY, True, 0, False

        # Colisões com blocos (morto apenas se não imortal)
        for b in blocks:
            if player_rect.colliderect(b):
                if vel_y > 0 and player_rect.bottom - vel_y <= b.top:
                    player_rect.bottom, vel_y, on_ground, rotating = b.top, 0, True, False
                    angle = 0
                    for _ in range(5):
                        sparks.append(Spark(player_rect.left, b.top - 4))
                else:
                    if not immortal:
                        death_explosion(player_rect.x, player_rect.y, clock, FPS, screen, bg_img)
                        pygame.mixer.music.stop()
                        return

        # Colisões com spikes (morto apenas se não imortal)
        for s in spikes:
            if player_rect.colliderect(s):
                if not immortal:
                    death_explosion(player_rect.x, player_rect.y, clock, FPS, screen, bg_img)
                    pygame.mixer.music.stop()
                    return

        # Rotação no ar
        if rotating:
            angle = min(angle + ROTATION_SPEED, 180)

        # Desenha partículas comuns
        for sp in sparks:
            sp.draw(screen)

        # Desenha jogador (UFO ou normal)
        if phase == 3 and percent >= 50:  # UFO não rotaciona
            screen.blit(player_surf, player_rect)
        else:  # Comportamento original
            rotated = pygame.transform.rotate(player_surf, -angle)
            r_rect = rotated.get_rect(center=player_rect.center)
            screen.blit(rotated, r_rect)

        # % de progresso
        pct_surf = font.render(f"{int(percent)}%", True, LINE_COLOR)
        screen.blit(pct_surf, (WIDTH - 120, 10))

        pygame.display.flip()

        if percent >= TOTAL_TIME:
            break

def death_explosion(cx, cy, clock, FPS, screen, bg_img):
    particles = []
    for _ in range(50):
        p = Spark(cx, cy)
        p.vx = random.uniform(-300, 300)
        p.vy = random.uniform(-300, 300)
        p.life = 1.0
        particles.append(p)
    t = 0.0
    while t < 1.0:
        dt_e = clock.tick(FPS) / 1000.0
        t += dt_e
        screen.blit(bg_img, (0, 0))
        for p in particles[:]:
            p.update(dt_e)
            p.draw(screen)
        pygame.display.flip()