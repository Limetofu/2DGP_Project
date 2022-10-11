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

JumpKeyPressed = 0

JumpAgain = 0


MoveTime = 0.0
MoveHeight = 0
MovePower = 10.0
MoveKeyPressed = 0

'''  '''


def Jump():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime
    global JumpAgain
    global y

    # space를 누르지 않으면, 종료
    if JumpKeyPressed == 0:
        return
    
    JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0
    JumpTime += 0.2

    if JumpTime > JumpPower and y - JumpHeight <= 100:
        JumpTime = 0
        y = y - JumpHeight
        JumpHeight = 0
        JumpKeyPressed = False
        JumpAgain = False

def Move():
    global MoveKeyPressed, MoveHeight, MovePower, MoveTime
    # height에 상한을 정하고, 최대 속력을 맞추기

    MoveHeight = (MoveTime * MoveTime - MovePower * MoveTime) / 5.0
    # 변곡점때, 
    MoveTime





def handle_events():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime
    global running
    global JumpAgain
    global y

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                if (JumpKeyPressed == False):
                    JumpKeyPressed = True
                elif (JumpKeyPressed == True and JumpAgain == False):
                    JumpAgain = True
                    y = y - JumpHeight
                    JumpTime = 0.0
            elif event.key == SDLK_ESCAPE:
                running = False

open_canvas(1280, 720)

black_rect = load_image('black_rect.png')
hero = load_image('knight_hero.png')

running = 1
x_frame = 0
y_frame = 15
count = 0

if __name__ == '__main__':
    while running:
        clear_canvas()
        black_rect.draw(x, y - JumpHeight, 60, 100)
        # draw(Xpos for start, Ypos for start, WIDTH /none, HEIGHT /none)
        # hero? 128x128

        # hero.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, x, y - JumpHeight)
        count += 1
        if count == 30:
            x_frame = (x_frame + 1) % 16
            count = 0
        update_canvas()

        handle_events()
        Jump()

close_canvas()