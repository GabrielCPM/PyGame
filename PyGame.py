import pygame
import sys
import random
import math

class Spark:
    """Partícula de faísca que se move para trás do player ao contato com o chão ou blocos."""
    def __init__(self, x, y):
        self.x = x + random.uniform(-5, 5)
        self.y = y
        self.vx = random.uniform(-100, -200)
        self.vy = random.uniform(-50, 50)
        self.life = random.uniform(0.3, 0.6)
        self.color = (255, 200, 50)

    def update(self, dt):
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 200 * dt  # leve gravidade vertical

    def draw(self, surf):
        if self.life > 0:
            alpha = max(0, min(255, int(255 * (self.life / 0.6))))
            col = (*self.color, alpha)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, col, (2,2), 2)
            surf.blit(s, (self.x, self.y))


def run_phase(screen, clock, phase):
    WIDTH, HEIGHT = screen.get_size()
    FPS = 60

    # Carrega e redimensiona background da fase
    bg_img = pygame.image.load("assets/img/background.png").convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))

    # Função de explosão de morte
    def death_explosion(cx, cy):
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
        TOTAL_TIME       = 90.0
        spawn_interval   = 1350
        block_chance     = 0.0
        vertical_chance  = 0.0
        min_platform_gap = 0.0
    else:
        TOTAL_TIME       = 120.0
        spawn_interval   = 1350
        block_chance     = 0.8
        vertical_chance  = 0.2
        min_platform_gap = 0.02 * TOTAL_TIME

    # Gap de 6 blocos para spikes solo (fase 2)
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

        # Atualiza partículas
        for sp in sparks[:]:
            sp.update(dt)
            if sp.life <= 0:
                sparks.remove(sp)

        # Eventos
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == SPAWN_OBSTACLE:
                base_x = WIDTH

                if phase == 1:
                    # Fase 1: spikes únicos/duplos/triplos por terço
                    if percent < 33:
                        count = 1
                    elif percent < 66:
                        count = random.choice([1, 2])
                    else:
                        count = random.choice([1, 2, 3])
                    for i in range(count):
                        h = random.choice([player_size, player_size//2])
                        sx = base_x + i * player_size
                        spikes.append(pygame.Rect(sx, ground_y-h, player_size, h))
                else:
                    # Fase 2: blocos ou spikes solo
                    spawn_block = (
                        random.random() < block_chance and
                        (elapsed_time - last_platform) >= min_platform_gap
                    )
                    if spawn_block:
                        last_platform = elapsed_time
                        # paredes verticais: sempre no último terço, antes por chance
                        if percent >= 66 or random.random() < vertical_chance:
                            # Paredão de 2 blocos
                            blocks.append(pygame.Rect(base_x,
                                                      ground_y-player_size,
                                                      player_size, player_size))
                            blocks.append(pygame.Rect(base_x,
                                                      ground_y-2*player_size,
                                                      player_size, player_size))
                            # Spike no topo apenas no último terço
                            if percent >= 66:
                                h = random.choice([player_size, player_size//2])
                                spikes.append(pygame.Rect(base_x,
                                                          ground_y-2*player_size-h,
                                                          player_size, h))
                        else:
                            # Plataforma horizontal (máximo 1 grupo)
                            length = random.randint(1, 10)
                            for i in range(length):
                                blocks.append(pygame.Rect(base_x + i*player_size,
                                                          ground_y-player_size,
                                                          player_size, player_size))
                            if percent >= 33:
                                pos = random.choice([0, length-1])
                                group_size = 1 if length <= 4 else random.choice([1, 2])
                                for g in range(group_size):
                                    idx = pos + (g if pos == 0 else -g)
                                    h = random.choice([player_size, player_size//2])
                                    spikes.append(pygame.Rect(base_x + idx*player_size,
                                                              ground_y-player_size-h,
                                                              player_size, h))
                    else:
                        # Spikes solo após gap_time
                        if (elapsed_time - last_platform) >= gap_time:
                            count = random.randint(1, 3)
                            for i in range(count):
                                h = random.choice([player_size, player_size//2])
                                sx = base_x + i*player_size
                                spikes.append(pygame.Rect(sx, ground_y-h, player_size, h))

        # Desenha background
        screen.blit(bg_img, (0, 0))

        # Salto contínuo
        keys = pygame.key.get_pressed()
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

        # Colisões com blocos
        for b in blocks:
            if player_rect.colliderect(b):
                if vel_y > 0 and player_rect.bottom - vel_y <= b.top:
                    player_rect.bottom, vel_y, on_ground, rotating = b.top, 0, True, False
                    angle = 0
                    for _ in range(5):
                        sparks.append(Spark(player_rect.left, b.top - 4))
                else:
                    death_explosion(*player_rect.center)
                    return

        # Colisões com spikes
        for s in spikes:
            if player_rect.colliderect(s):
                death_explosion(*player_rect.center)
                return

        # Rotação no ar
        if rotating:
            angle = min(angle + ROTATION_SPEED, 180)

        # Move e limpa obstáculos
        for s in spikes: s.x -= scroll_speed
        for b in blocks: b.x -= scroll_speed
        spikes = [s for s in spikes if s.right > 0]
        blocks = [b for b in blocks if b.right > 0]

        # Desenha partículas
        for sp in sparks:
            sp.draw(screen)

        # Desenha chão e limites
        pygame.draw.rect(screen, GROUND_COLOR,
                         (0, ground_y, WIDTH, GROUND_HEIGHT))
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

        # Desenha player rotacionado
        rotated = pygame.transform.rotate(player_surf, -angle)
        r_rect  = rotated.get_rect(center=player_rect.center)
        screen.blit(rotated, r_rect)

        # % de progresso
        pct_surf = font.render(f"{int(percent)}%", True, LINE_COLOR)
        screen.blit(pct_surf, (WIDTH - 120, 10))

        pygame.display.flip()

        if percent >= TOTAL_TIME:
            break


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Geometry Dash Clone")
    clock = pygame.time.Clock()

    # Carrega e redimensiona o mesmo background usado nos níveis
    bg_menu = pygame.image.load("assets/img/background.png").convert()
    bg_menu = pygame.transform.scale(bg_menu, screen.get_size())
    font = pygame.font.SysFont(None, 48)

    while True:
        dt = clock.tick(60) / 1000.0
        screen.blit(bg_menu, (0, 0))

        title = font.render("Selecione a fase", True, (255,255,255))
        opt1  = font.render("1 - Fase 1",       True, (255,255,255))
        opt2  = font.render("2 - Fase 2",       True, (255,255,255))
        opt3  = font.render("3 - Fase 3",       True, (255,255,255))
        screen.blit(title, ((800-title.get_width())//2, 200))
        screen.blit(opt1,  ((800-opt1.get_width())//2, 300))
        screen.blit(opt2,  ((800-opt2.get_width())//2, 360))
        screen.blit(opt3,  ((800-opt3.get_width())//2, 420))

        pygame.display.flip()
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_1:
                    run_phase(screen, clock, 1)
                elif ev.key == pygame.K_2:
                    run_phase(screen, clock, 2)
                elif ev.key == pygame.K_3:
                    run_phase(screen, clock, 3)  # inicia fase 3 vazia

if __name__ == '__main__':
    main()