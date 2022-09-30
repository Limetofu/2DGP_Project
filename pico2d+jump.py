from sqlite3 import Time
from pico2d import *
import math

'''  Value about Jump '''

x = 600.0
y = 100.0
diameter = 20.0

JumpTime = 0.0
JumpHeight = 0
JumpPower = 50.0

JumpKeyPressed = False

'''  '''


def Jump():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime

    if JumpKeyPressed == 0:
        return
    
    JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0
    JumpTime += 0.11

    if JumpTime > JumpPower:
        JumpTime = 0
        JumpHeight = 0
        JumpKeyPressed = False

def handle_events():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime
    global running

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                JumpKeyPressed = True
            elif event.key == SDLK_ESCAPE:
                running = False

open_canvas(1280, 720)

black_rect = load_image('black_rect.png')

running = 1

if __name__ == '__main__':
    while running:
        clear_canvas()
        black_rect.draw(x, y - JumpHeight)
        update_canvas()

        handle_events()
        Jump()

close_canvas()