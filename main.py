from sqlite3 import Time
from pico2d import *
import math
from dataclasses import dataclass
from mj_values import *
import numpy as np
from check_col import collision_check
'''  '''

class RECT:
    left: int
    bottom: int
    right: int
    top: int

class BLOCK:
    left: int
    bottom: int
    right: int
    top: int
    type: int


# BLOCK 구조체 배열(리스트) 만들 예정. 
BLOCKS = []

PLAYER_RECT = RECT()



min_jump_height = 0
is_falling = 0
grid_data = []

def load_block():
    global BLOCKS, BLOCK_CNT, grid_data
    
    with open("grid_data.txt", "r") as file:
        data = file.readlines()
    file.close()

    BLOCK_CNT = len(data)

    for i in data:
        tmp_str = i.replace('\n', '\n')
        grid_data.append(tmp_str)
    for i in range(BLOCK_CNT):
        BLOCKS.append(BLOCK())
        BLOCKS[i].left = int(grid_data[i][0:6]) # 중간에 | 들어감.
        BLOCKS[i].bottom = int(grid_data[i][7:13])
        BLOCKS[i].right = BLOCKS[i].left + int(grid_data[i][14:18])
        BLOCKS[i].top = BLOCKS[i].bottom + int(grid_data[i][19:23])
        BLOCKS[i].type = int(grid_data[i][24])

def blocks_init():
    global BLOCKS, block_x, block_y, MoveDistance, JumpHeight, BLOCK_CNT
    global X_MOVE_POWER, Y_MOVE_POWER

    for i in range(BLOCK_CNT):
        BLOCKS[i].left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + int(grid_data[i][0:6])
        BLOCKS[i].right = BLOCKS[i].left + int(grid_data[i][14:18])
        BLOCKS[i].bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + int(grid_data[i][7:13])
        BLOCKS[i].top = BLOCKS[i].bottom + int(grid_data[i][19:23])

def player_init():
    global PLAYER_RECT, PlayerMoveDistance, player_x, X_MOVE_POWER
    PLAYER_RECT.left = 640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) - 50
    PLAYER_RECT.bottom = 200 - 50
    PLAYER_RECT.right = PLAYER_RECT.left + 100
    PLAYER_RECT.top = 200 + 50

def Jump():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime
    global JumpAgain
    global y, block_y
    global min_jump_height, is_falling
    global player_on_block_num

    blocks_init()

    # space를 누르지 않으면, 종료
    if JumpKeyPressed == 0 and is_falling == 0:
        return
    

    min_jump_height = JumpHeight
    JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0
    JumpTime += 0.2

    # 변곡점 --> JumpHeight = -312.5
    if JumpHeight <= -312:
        is_falling = True


    # 점프 끝내는 조건문
    ## 끝내야 할 때?
    ##  1. 땅에 도착했을 때
    ##      -> 2번이랑 같은 조건
    ##  2. 블럭 위에 도착했을 때
    ##      -> is_falling 상태일 때만 활성화하기.
    ##  3. 블럭 아래에 부딪혔을 때

    # print(JumpTime, JumpPower, "///",  y - JumpHeight)

    if JumpTime > JumpPower and y - JumpHeight <= 99: # 
        JumpTime = 0
        y = y - JumpHeight
        block_y = block_y + JumpHeight
        JumpHeight = 0
        JumpKeyPressed = False
        JumpAgain = False

        is_falling = False
        min_jump_height = 0
    
    for i in range(BLOCK_CNT):
        # 충돌 검사. BLOCK_CNT만큼
        # 충돌했을 때, 위에 충돌했는지, 아래에 충돌했는지 판별 필요.
        temp_rect = BLOCK()
        temp_rect.left, temp_rect.right = BLOCKS[i].left, BLOCKS[i].right 
        temp_rect.top, temp_rect.bottom = BLOCKS[i].top + 8, BLOCKS[i].top + 8
        # top 원소 먼저 check, + 5 해주는 이유? -> 계속 충돌해있으면 안되기 때문, 원천 차단
        
        if collision_check(temp_rect, PLAYER_RECT) and is_falling == True:
            JumpTime = 0
            y = y - JumpHeight
            block_y = block_y + JumpHeight

            JumpHeight = 0
            JumpKeyPressed = False
           

            is_falling = False
            min_jump_height = 0
            player_on_block_num = i
            
            collision_repair(i)

            JumpAgain = False
            return

        temp_rect.top, temp_rect.bottom = BLOCKS[i].bottom - 8, BLOCKS[i].bottom - 8
        if collision_check(temp_rect, PLAYER_RECT) and is_falling == False:
            # 위와 같이 통통 튀어오르는게 아니라.... 
            # 올라갈 때 남은 JumpTime 만큼 멈췄다가
            # 다시 내려와야 함.
            # 일단 거의 50이라고 가정.
            # 내려오고 93까지 내려가기도 하니까..

            # 총 50번 수행.
            # 남은 JumpTime 증가 횟수 to 25번
            # 다른 변수에 저장.
            # 그 변수만큼 main에서 y값 block_y값 내려주기..? -> 가만 있어야 함.

            # 아래 식으로 했을 때 더블 점프했을 때 너무 격하게 내려옴.
            #   JumpTime = 50 - JumpTime
            # 더블 점프 시에는 안정적이게 해줘야 할듯.

            # 더블 점프 시 블럭을 통과함.
            #  -> 첫 점프 후 바닥 충돌, 이후 떨어지면서 다시 점프 시 블럭 통과.
            #      sol) is_falling을 더블 점프 시에 false로 바꾸지 않음.
            
            # 다시.. count를 써본다면?
            # 원작 게임과 같이 점프를 구현?
            # JumpPower를 case마다 바꿔줘야 함.
            # 변곡점이 매번 달라지는 점프?
            # 노가다로 최저점, 최고점 점프 세분화해서 만들면 가능.


            print("Before:", JumpTime)
            if JumpAgain:
                JumpTime = 50 - JumpTime
            else:
                JumpTime = 50 - JumpTime

            collision_repair_bottom(i)

            print("After:", JumpTime)

            JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0

            draw_rectangle(temp_rect.left, temp_rect.bottom - 1, temp_rect.right, temp_rect.top + 1)
            update_canvas()
            print("bottom col")

            is_falling = True

        pass

def Move():
    global LeftKeyPressed, RightKeyPressed, MoveDistance, PlayerMoveDistance, MovePower, MoveTime, MoveCount, x, y
    global block_x, X_MOVE_POWER, now_move_player_left, now_move_player_right, player_x, ex_block, block_y
    global JumpTime, JumpKeyPressed, player_on_block_num, is_falling, JumpHeight, JumpPower
    global can_climb_left, can_climb_right
    # Distance에 상한을 정하고, 최대 속력을 맞추기

    # 둘 다 누른 상태가 아니거나, 둘 다 눌렀다가 뗸 상태도 아니면, 바로 종료하기
    if LeftKeyPressed == 0 and RightKeyPressed == 0 and MoveCount == 0:
        return

    # 충돌체크
    for i in range(BLOCK_CNT):
        temp_rect = BLOCK()
        temp_rect.top, temp_rect.bottom = BLOCKS[i].top, BLOCKS[i].bottom
        temp_rect.left, temp_rect.right = BLOCKS[i].left - 5, BLOCKS[i].left - 5 # 왼쪽

        if collision_check(temp_rect, PLAYER_RECT):
            MoveCount = 0
            MoveTime = 0
            can_climb_left = True
            # 약간 생각을 해보아야 할듯
            # 블럭의 top, bottom 차이에 따라서 (블럭의 세로 크기) 너무 얇아서 타지 못하는 벽일수도 있고
            # PLAYER_RECT에 비해 블럭이 너무 아래나 위에 있을 때.
            #   -> BLOCK과 PLAYER의 차이가 적을 때 일단 벽을 탈 수 있게.
            collision_repair_left(i)
            return

        temp_rect.left, temp_rect.right = BLOCKS[i].right + 5, BLOCKS[i].right + 5 # 오른쪽

        if collision_check(temp_rect, PLAYER_RECT):
            MoveCount = 0
            MoveTime = 0
            can_climb_right = True
            collision_repair_right(i)
            return

        # player_on_block_num이 현재 i랑 같을 때,
        # i번째 block 좌우로 player_rect가 나간다면?
        # => 떨어져야 함

        
        if i == player_on_block_num and JumpKeyPressed == 0:
            if PLAYER_RECT.right > BLOCKS[i].left - 5 and PLAYER_RECT.left > BLOCKS[i].right + 5 or \
            PLAYER_RECT.right < BLOCKS[i].left - 5 and PLAYER_RECT.left < BLOCKS[i].right + 5:
                # 떨어지기!
                JumpTime = 25.2
                JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0
                # JumpKeyPressed = False
                player_on_block_num = -1
                is_falling = True
                y = y - 312.48
                block_y = block_y + 312.48
                print("falling")
                pass


    if now_move_player_left:
        # 플레이어를 움직일 차례. -> 맵 끝으로 갔기 때문
        PlayerMoveDistance = (MoveTime * MoveTime - MovePower * MoveTime) / 600.0
        if LeftKeyPressed == 1:
            if player_x - PlayerMoveDistance < 920:
                player_x = player_x - PlayerMoveDistance
        if RightKeyPressed == 1:
            player_x = player_x + PlayerMoveDistance

        
            # 맵 끝으로 갔을 때, 못움직이게

        # 관성 -> Movecount
        if LeftKeyPressed == 1 or RightKeyPressed == 1:
            if MoveCount < 100:
                MoveTime += 0.1
                MoveCount += 1

        # 키를 뗐을 때, MoveCount만큼 관성 이동
        else:
            if MoveCount > 0:
                MoveTime -= 0.1
                MoveCount -= 1
                if LeftKeyPressed == -1:
                    if player_x - PlayerMoveDistance < 920:
                        player_x = player_x - PlayerMoveDistance
                elif RightKeyPressed == -1:
                    player_x = player_x + PlayerMoveDistance

        if int(player_x - PlayerMoveDistance) < 0:
            now_move_player_left = False

    elif now_move_player_right:
        # 플레이어를 움직일 차례. -> 맵 끝으로 갔기 때문
        PlayerMoveDistance = (MoveTime * MoveTime - MovePower * MoveTime) / 600.0
        if LeftKeyPressed == 1:
            player_x = player_x - PlayerMoveDistance
        if RightKeyPressed == 1:
            if player_x + PlayerMoveDistance > -920:
                player_x = player_x + PlayerMoveDistance

        
            # 맵 끝으로 갔을 때, 못움직이게

        # 관성 -> Movecount
        if LeftKeyPressed == 1 or RightKeyPressed == 1:
            if MoveCount < 100:
                MoveTime += 0.1
                MoveCount += 1

        # 키를 뗐을 때, MoveCount만큼 관성 이동
        else:
            if MoveCount > 0:
                MoveTime -= 0.1
                MoveCount -= 1
                if LeftKeyPressed == -1:
                    player_x = player_x - PlayerMoveDistance
                elif RightKeyPressed == -1:
                    if player_x + PlayerMoveDistance > -920:
                        player_x = player_x + PlayerMoveDistance

        if int(player_x - PlayerMoveDistance) > 4:
            now_move_player_right = False

    else:

        MoveDistance = (MoveTime * MoveTime - MovePower * MoveTime) / 600.0

        if (int(x - MoveDistance) // X_MOVE_POWER) <= 5:
        # 맵 왼쪽 끝으로 갔다면?
            now_move_player_left = True
            player_x = 0

        elif int(x - MoveDistance) >= 11605:
            now_move_player_right = True
            player_x = 0

        # xpos 최신화
        if LeftKeyPressed == 1:
            x = x + MoveDistance
            block_x = block_x - MoveDistance
        if RightKeyPressed == 1:
            x = x - MoveDistance
            block_x = block_x + MoveDistance

        # 관성 -> Movecount
        if LeftKeyPressed == 1 or RightKeyPressed == 1:
            if MoveCount < 100:
                MoveTime += 0.1
                MoveCount += 1

        # 키를 뗐을 때, MoveCount만큼 관성 이동
        else:
            if MoveCount > 0:
                MoveTime -= 0.1
                MoveCount -= 1
                if LeftKeyPressed == -1:
                    x = x + MoveDistance
                    block_x = block_x - MoveDistance
                elif RightKeyPressed == -1:
                    x = x - MoveDistance
                    block_x = block_x + MoveDistance

    if MoveCount == 0:
        LeftKeyPressed = 0
        RightKeyPressed = 0

def handle_events():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime, player_on_block_num, is_falling
    global running
    global JumpAgain
    global y, block_y
    global LeftKeyPressed, RightKeyPressed, MoveCount, MoveTime

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                if (JumpKeyPressed == False):
                    JumpKeyPressed = True
                    player_on_block_num = -1
                elif (JumpKeyPressed == True and JumpAgain == False):
                    JumpAgain = True
                    is_falling = False
                    y = y - JumpHeight
                    block_y = block_y + JumpHeight
                    JumpHeight = 0
                    JumpTime = 0.0
                    player_on_block_num = -1
                    blocks_init()
                    # 여기서 block_y값이 갑자기 확 낮아짐.

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
                if LeftKeyPressed == 1:
                    LeftKeyPressed = -1
            elif event.key == SDLK_RIGHT:
                if RightKeyPressed == 1:
                    RightKeyPressed = -1

running = 1
x_frame = 0
y_frame = 15
count = 0

def animation_count():
    global count, x_frame, y_frame
    count += 1
    if count == 30:
        x_frame = (x_frame + 1) % 16
        count = 0

def collision_repair(i):
    global y, block_y, BLOCKS, PLAYER_RECT

    blocks_init()
    if collision_check(BLOCKS[i], PLAYER_RECT):
        y += 5
        block_y -= 5
        collision_repair(i)
        print("did")
    else:
        return

def collision_repair_bottom(i):
    global y, block_y, BLOCKS, PLAYER_RECT

    blocks_init()
    if collision_check(BLOCKS[i], PLAYER_RECT):
        y -= 5
        block_y += 5
        collision_repair_bottom(i)
        print("did_bottom")
    else:
        return

def collision_repair_left(i):
    global x, player_x, BLOCKS, PLAYER_RECT, now_move_player_left, now_move_player_right, block_x

    blocks_init()
    player_init()
    temp_rect = BLOCK()
    temp_rect.top, temp_rect.bottom = BLOCKS[i].top, BLOCKS[i].bottom
    temp_rect.left, temp_rect.right = BLOCKS[i].left - 5, BLOCKS[i].left - 5 # 왼쪽

    if collision_check(temp_rect, PLAYER_RECT):
        if now_move_player_left:
            player_x += 1
        elif now_move_player_right:
            player_x += 1
            pass
        else:
            x -= 1
            block_x += 1
        print("did left")
        collision_repair_left(i)
    else:
        return

def collision_repair_right(i):
    global x, player_x, BLOCKS, PLAYER_RECT, now_move_player_left, now_move_player_right, block_x

    blocks_init()
    player_init()
    temp_rect = BLOCK()
    temp_rect.top, temp_rect.bottom = BLOCKS[i].top, BLOCKS[i].bottom
    temp_rect.left, temp_rect.right = BLOCKS[i].right + 5, BLOCKS[i].right + 5 # 오른쪽

    if collision_check(temp_rect, PLAYER_RECT):
        if now_move_player_left:
            player_x -= 1
        elif now_move_player_right:
            player_x -= 1
        else:
            x += 1
            block_x -= 1
        print("did right")
        collision_repair_right(i)
    else:
        return

open_canvas(1280, 720)

black_rect = load_image('resources/black_rect.png')
white_rect = load_image('resources/white_rect.png')
hero = load_image('resources/knight_hero.png')
ex_map = load_image('resources/map_ex.png')
ex_block = load_image('resources/first_map.png')



if __name__ == '__main__':
    load_block()
    blocks_init()
    player_init()

    while running:
        clear_canvas()
        blocks_init()
        player_init()

        # draw(Xpos for start, Ypos for start, WIDTH /none, HEIGHT /none)
        

        ex_block.clip_draw(int(x - MoveDistance) // X_MOVE_POWER, int(y - JumpHeight) // Y_MOVE_POWER, 640, 360, 640, 360, 1280, 720)

        # block draw 할때 y는 x처럼 Move에서 최신화가 되지 않기 때문에 더해주어야 함.
        white_rect.draw(int(block_x - MoveDistance) // (X_MOVE_POWER / 2), int(block_y + JumpHeight) // (Y_MOVE_POWER / 2))

        print(int(block_x - MoveDistance) // (X_MOVE_POWER / 2), int(block_y + JumpHeight) // (Y_MOVE_POWER / 2))

        # hero? 128x128
        # 캐릭터 크기 100이 딱 맞는듯
        hero.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200, 100, 100)

        

        

        draw_rectangle(PLAYER_RECT.left, PLAYER_RECT.top, PLAYER_RECT.right, PLAYER_RECT.bottom)

        for i in range(BLOCK_CNT):
            draw_rectangle(BLOCKS[i].left, BLOCKS[i].bottom, BLOCKS[i].right, BLOCKS[i].top)


        animation_count()
        
        handle_events() 

        Move()
        Jump()
        update_canvas()
        

close_canvas()