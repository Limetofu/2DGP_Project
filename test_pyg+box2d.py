import pygame
from pygame.locals import *
from Box2D import *
from Box2D.b2 import *

SCREEN_WD = 400
SCREEN_HT = 400
TARGET_FPS = 60
PPM = 20.0

screen = pygame.display.set_mode((SCREEN_WD, SCREEN_HT), 0, 32)
pygame.display.set_caption("Pygame_Example")
clock = pygame.time.Clock()

world = b2World(gravity = (0, -10), doSleep = True)

ground1BodyDef = b2BodyDef()
ground1BodyDef.position.Set(0, 1)
ground1Body = world.CreateBody(ground1BodyDef)
ground1Shape = b2PolygonShape()
ground1Shape.SetAsBox(50, 5)
ground1Body.CreateFixture(shape = ground1Shape)

box1BodyDef = b2BodyDef()
box1BodyDef.type = b2_dynamicBody
box1BodyDef.position.Set(10, 15)
box1Body = world.CreateBody(box1BodyDef)
box1Shape = b2PolygonShape()
box1Shape.SetAsBox(2, 1)
box1FixtureDef = b2FixtureDef()
box1FixtureDef.shape = box1Shape
box1FixtureDef.density = 1
box1FixtureDef.friction = 0.3
box1Body.CreateFixture(box1FixtureDef)

timeStep = 1.0 / 60
velocity = 10
positers = 10

colors = {
    dynamicBody : (127, 127, 127, 255),
    staticBody : (255, 255, 255, 255)
}

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

    for body in (ground1Body, box1Body):
        for fixture in body.fixtures:
            shape = fixture.shape
            vertices = [(body.transform * v) * PPM for v in shape.vertices]
            vertices = [(v[0], (SCREEN_HT - v[1])) for v in vertices]
            pygame.draw.polygon(screen, colors[body.type], vertices)
    
    world.Step(timeStep, velocity, positers)
    pygame.display.flip()
    clock.tick(TARGET_FPS)

pygame.quit()
print("done")