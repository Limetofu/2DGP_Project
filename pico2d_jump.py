from sqlite3 import Time
from urllib.request import AbstractDigestAuthHandler
from pico2d import *
import math
from dataclasses import dataclass
from mj_values import *

'''  '''

class BLOCK:
    x: int = None
    y: int = None
    type: int = None

blocks = BLOCK()

blocks.type = 1
blocks.x = 1
blocks.y = 1



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
    global LeftKeyPressed, RightKeyPressed, MoveDistance, MovePower, MoveTime, MoveCount, x
    # Distance에 상한을 정하고, 최대 속력을 맞추기

    # 둘 다 누른 상태가 아니거나, 둘 다 눌렀다가 뗸 상태도 아니면, 바로 종료하기
    if LeftKeyPressed == 0 and RightKeyPressed == 0:
        return

    MoveDistance = (MoveTime * MoveTime - MovePower * MoveTime) / 1000.0
    if LeftKeyPressed == 1:
        x = x + MoveDistance
    if RightKeyPressed == 1:
        x = x - MoveDistance

    if LeftKeyPressed == 1 or RightKeyPressed == 1:
        if MoveCount < 100:
            MoveTime += 0.1
            MoveCount += 1
    else:
        if MoveCount > 0:
            MoveTime -= 0.1
            MoveCount -= 1
            if LeftKeyPressed == -1:
                x = x + MoveDistance
            elif RightKeyPressed == -1:
                x = x - MoveDistance

    if MoveCount == 0:
        LeftKeyPressed = 0
        RightKeyPressed = 0

def handle_events():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime
    global running
    global JumpAgain
    global y
    global LeftKeyPressed, RightKeyPressed, MoveCount, MoveTime

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

            elif event.key == SDLK_LEFT:
                LeftKeyPressed = 1
                #if RightKeyPressed == 1: 
                RightKeyPressed, MoveCount, MoveTime = 0, 0, 0

            elif event.key == SDLK_RIGHT:
                RightKeyPressed = 1
                #if LeftKeyPressed == 1: 
                LeftKeyPressed, MoveCount, MoveTime = 0, 0, 0


            elif event.key == SDLK_ESCAPE:
                running = False


        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                LeftKeyPressed = -1
            elif event.key == SDLK_RIGHT:
                RightKeyPressed = -1



open_canvas(1280, 720)

black_rect = load_image('resources/black_rect.png')
hero = load_image('resources/knight_hero.png')

running = 1
x_frame = 0
y_frame = 15
count = 0

if __name__ == '__main__':
    file = open("grid_data.txt", "r")
        # 파일 열기. 뒤의 인자는 C와 동일
    before_strings = file.readlines()
        # 개행 문자 포함, 리스트 형식 return
    print(before_strings)
    file.close()
    grid_data = []

    for i in before_strings:
        tmp_str = i.replace('\n', '')
        grid_data.append(tmp_str)
    
    print(grid_data)

    while running:
        clear_canvas()
        black_rect.draw(x - MoveDistance, y - JumpHeight, 100, 100)
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
        Move()

close_canvas()