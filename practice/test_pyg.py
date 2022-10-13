import pygame
from pygame.locals import *

SCREEN_WD = 400
SCREEN_HT = 400
TARGET_FPS = 60

screen = pygame.display.set_mode((SCREEN_WD, SCREEN_HT), 0, 32)
pygame.display.set_caption("Pygame_Example")
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            continue
        if event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
            continue

    screen.fill((0, 0, 0, 0))
    vertices = [(10, 10), (20, 10), (20, 20), (10, 20)]
    pygame.draw.polygon(screen, (0, 255, 0, 0), vertices)
    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
print("done")
