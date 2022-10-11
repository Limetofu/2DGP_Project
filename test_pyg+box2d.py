import pygame
from pygame.locals import *
from Box2D import *
from Box2D.b2 import *
from pico2d import *

SCREEN_WD = 400
SCREEN_HT = 400
TARGET_FPS = 60
PPM = 1.0

screen = pygame.display.set_mode((SCREEN_WD, SCREEN_HT), 0, 32)
pygame.display.set_caption("Pygame_Example")
clock = pygame.time.Clock()

open_canvas(SCREEN_WD, SCREEN_HT)

 # 중력 벡터 선언, sleep 여부 지정가능
 # 월드객체 생성
world = b2World(gravity = (0, -9.8), doSleep = True)

 # ground box 정의
ground1BodyDef = b2BodyDef()
 # type을 정해주지 않으면 기본 ground box로 지정됨
 # ground1BodyDef.type = b2_dynamicBody
ground1BodyDef.position.Set(0, 20)
 # body 정의 : position, damping, etc
ground1Body = world.CreateBody(ground1BodyDef)
 # 월드객체를 이용, body 생성
ground1Shape = b2PolygonShape()
ground1Shape.SetAsBox(400, 100)

ground1Body.CreateFixture(shape = ground1Shape)

box1BodyDef = b2BodyDef()
box1BodyDef.type = b2_dynamicBody
box1BodyDef.position.Set(200, 300)
box1Body = world.CreateBody(box1BodyDef)
box1Shape = b2PolygonShape()
box1Shape.SetAsBox(40, 20)

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
            print(vertices)
            vertices = [(v[0], (SCREEN_HT - v[1])) for v in vertices]
            pygame.draw.polygon(screen, colors[body.type], vertices)
    
    world.Step(timeStep, velocity, positers)
    pygame.display.flip()
    clock.tick(TARGET_FPS)



    clear_canvas()
    #draw_rectangle()
    update_canvas()

    delay(0.01)
    get_events()    


pygame.quit()
print("done")

close_canvas()