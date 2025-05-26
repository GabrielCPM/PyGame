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
            alpha = max(0, min(255, int(255 * (self.life / 0.6))))  # Linha 57 corrigida
            col = (*self.color, alpha)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, col, (2,2), 2)
            surf.blit(s, (self.x, self.y))

class UFOSkin:
    def __init__(self, size, yellow, purple):
        self.size = size
        self.yellow = yellow
        self.purple = purple
        self.surf = pygame.Surface((size, size), pygame.SRCALPHA)
        self._draw_ufo()
    
    def _draw_ufo(self):
        center = (self.size//2, self.size//2)
        radius = self.size//2
        
        # Corpo principal (roxa)
        pygame.draw.circle(self.surf, self.purple, center, radius)
        
        # Centro amarelo
        pygame.draw.circle(self.surf, self.yellow, center, radius-8)
        
        # Detalhes do UFO
        pygame.draw.arc(self.surf, self.purple, 
                       [center[0]-radius+5, center[1]-radius//3, 
                        (radius-5)*2, radius//1.5], 
                       0, math.pi, 3)
        
        # Luzes amarelas
        for i in range(6):
            angle = math.radians(i * 60)
            light_pos = (
                int(center[0] + (radius-12) * math.cos(angle)),
                int(center[1] + (radius-12) * math.sin(angle)))
            pygame.draw.circle(self.surf, self.yellow, light_pos, 3)