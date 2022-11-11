from sqlite3 import Time
from pico2d import *
import math
from dataclasses import dataclass
from mj_values import *
import numpy as np
from check_col import collision_check
from time import time

'''  '''

open_canvas(1280, 720, sync=False)

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

class MONSTER:
    left: int
    bottom: int
    right: int
    top: int
    type: str
    state: str
        # idle / alert / attacking / hit by player / dying / dead



# BLOCK 구조체 배열(리스트) 만들 예정. 
BLOCKS = []

PLAYER_RECT = RECT()

first = MONSTER()

# def move_all(xdir, ydir):
#     global x, y
#     # xdir, ydir만큼 전부 옮기기.
#     #  --> 화면 흔들리는 이펙트
#     # BLOCKS는 옮길 필요가 없지 않은지?
   
#     x += xdir
#     y += ydir    
    
#     pass



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
    PLAYER_RECT.left = 640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) -25
    PLAYER_RECT.bottom = 200 - 50
    PLAYER_RECT.right = PLAYER_RECT.left + 50
    PLAYER_RECT.top = 200 + 50

# player JUMP
# 

def Jump():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime
    global JumpAgain
    global y, block_y
    global is_falling
    global player_on_block_num

    blocks_init()

    # space를 누르지 않으면, 종료
    if JumpKeyPressed == 0 and is_falling == 0:
        return

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

    # if JumpTime > JumpPower and y - JumpHeight <= 99: # 
    #     JumpTime = 0
    #     y = y - JumpHeight
    #     block_y = block_y + JumpHeight
    #     JumpHeight = 0
    #     JumpKeyPressed = False
    #     JumpAgain = False

    #     is_falling = False
    
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

            # 남은 JumpTime 증가 갯수만큼 remainJumpCount 저장
            # 해당 위치에 JumpHeight 고정, remainJumpCount--;
            # remainJumpCount 모두 감소되면, 다시 떨어지게 만들어줌.
            #   -> 여기서 JumpTime = 50 - JumpTime!
            # remainJumpCount 조건문에 추가, 충돌이 유지돼서 무한 반복하는걸 막아줘야 함.
            # bool 변수 하나 더 추가?  
            

            print("Before:", JumpTime)
            if JumpAgain:
                JumpTime = 50 - JumpTime
            else:
                JumpTime = 50 - JumpTime

            collision_repair_bottom(i)

            print("After:", JumpTime)

            JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0

            # draw_rectangle(temp_rect.left, temp_rect.bottom - 1, temp_rect.right, temp_rect.top + 1)
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

    MoveValue = 600.0
    MoveCountLimit = 100
    MoveTimeChange = 0.1


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
        PlayerMoveDistance = (MoveTime * MoveTime - MovePower * MoveTime) / MoveValue
        if LeftKeyPressed == 1:
            if player_x - PlayerMoveDistance < 920:
                player_x -= PlayerMoveDistance
        if RightKeyPressed == 1:
            player_x += PlayerMoveDistance

        
            # 맵 끝으로 갔을 때, 못움직이게

        # 관성 -> Movecount
        if LeftKeyPressed == 1 or RightKeyPressed == 1:
            if MoveCount < MoveCountLimit:
                MoveTime += MoveTimeChange
                MoveCount += 1

        # 키를 뗐을 때, MoveCount만큼 관성 이동
        else:
            if MoveCount > 0:
                MoveTime -= MoveTimeChange
                MoveCount -= 1
                if LeftKeyPressed == -1:
                    if player_x - PlayerMoveDistance < 920:
                        player_x -= PlayerMoveDistance
                elif RightKeyPressed == -1:
                    player_x += PlayerMoveDistance

        if int(player_x - PlayerMoveDistance) < 0:
            now_move_player_left = False

    elif now_move_player_right:
        # 플레이어를 움직일 차례. -> 맵 끝으로 갔기 때문
        PlayerMoveDistance = (MoveTime * MoveTime - MovePower * MoveTime) / MoveValue
        if LeftKeyPressed == 1:
            player_x -= PlayerMoveDistance
        if RightKeyPressed == 1:
            if player_x + PlayerMoveDistance > -920:
                player_x += PlayerMoveDistance

        
            # 맵 끝으로 갔을 때, 못움직이게

        # 관성 -> Movecount
        if LeftKeyPressed == 1 or RightKeyPressed == 1:
            if MoveCount < MoveCountLimit:
                MoveTime += MoveTimeChange
                MoveCount += 1

        # 키를 뗐을 때, MoveCount만큼 관성 이동
        else:
            if MoveCount > 0:
                MoveTime -= MoveTimeChange
                MoveCount -= 1
                if LeftKeyPressed == -1:
                    player_x -= PlayerMoveDistance
                elif RightKeyPressed == -1:
                    if player_x + PlayerMoveDistance > -920:
                        player_x += PlayerMoveDistance

        if int(player_x - PlayerMoveDistance) > 4:
            now_move_player_right = False

    else:

        MoveDistance = (MoveTime * MoveTime - MovePower * MoveTime) / MoveValue

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
                MoveTime += MoveTimeChange
                MoveCount += 1

        # 키를 뗐을 때, MoveCount만큼 관성 이동
        else:
            if MoveCount > 0:
                MoveTime -= MoveTimeChange
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

def Attack():
    # 플레이어가 공격
    #  handle_events에 player_state 바꾸기
    #  player_state == attack이면, 
    #  해당 

    global count # idle anime count
    global player_state
    global DownKeyPressed, UpKeyPressed, hero_heading_left, hero_heading_right
    global attack_anime_count, attack_dir, attack_anime_frame, x_frame

    if player_state != 1:
        return

    #   ---  경우  ---

    # 1. 아무 버튼도 누르지 않음
    #    => 플레이어가 향하는 방향에 베기
    # 2. 좌우 방향키
    #    => 누른 방향키 따라 베기
    #       근데? heading값만 따라가도 판단 가능.
    # 3. 위아래 방향키
    #    => 누른 방향키 따라 베기.
    #       최우선으로 적용해야 함

    # attack 애니메이션 count는 여기 함수에서 관리
    # animation_count 함수에서는 출력만 해주고
    # 여기서 count에 따라 player_state 바꿔주기 등 연산

    # 좌우를 나눌 필요가 있을까?
    # attack_anime_count만 바꿀것.
    
    # attack_dir == 0? -> 공격중이 아님!
    # attack_dir != 0  -> 공격중

    if attack_dir == 0:
        attack_anime_count = 0 # count 초기화. 새 공격이기 때문
        if DownKeyPressed:
            attack_dir = -2
            x_frame = 7
        elif UpKeyPressed:
            if hero_heading_left:
                attack_dir = 3
                x_frame = 15
            else:
                attack_dir = 2
                x_frame = 0
        elif hero_heading_left:
            attack_dir = -1
            x_frame = 15
        else:
            attack_dir = 1
            x_frame = 0
    
    else: # 0이 아님! -> 공격중. count 올려주자
        if attack_anime_count > attack_anime_frame:
            # attack anime이 끝. 초기화 시켜주기.
            attack_anime_count = 0
            attack_dir = 0
            count = 0
            player_state = 0 # idle 상태로

        else:
            attack_anime_count += 1

# what monster need?
#   1. position
#   2. type <-- type에 따라서 Monster에서 
#   3. state <-- str

def Monster():
    pass



def handle_events():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime, player_on_block_num, is_falling
    global running
    global JumpAgain
    global y, block_y, show_blocks
    global LeftKeyPressed, RightKeyPressed, MoveCount, MoveTime
    global hero_heading_right, hero_heading_left, x_frame
    global UpKeyPressed, DownKeyPressed, player_state

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

            elif event.key == SDLK_LEFT:
                LeftKeyPressed, hero_heading_left = 1, True
                #if RightKeyPressed == 1: 
                RightKeyPressed, MoveCount, MoveTime, hero_heading_right = 0, 0, 0, False
                if player_state == 0: x_frame = 15

            elif event.key == SDLK_RIGHT:
                RightKeyPressed, hero_heading_right = 1, True
                #if LeftKeyPressed == 1: 
                LeftKeyPressed, MoveCount, MoveTime, hero_heading_left = 0, 0, 0, False
                if player_state == 0: x_frame = 0

            elif event.key == SDLK_UP:
                UpKeyPressed, DownKeyPressed = True, False

            elif event.key == SDLK_DOWN:
                DownKeyPressed, UpKeyPressed = True, False
            elif event.key == SDLK_z:
                if player_state == 0:
                    player_state = 1
            elif event.key == SDLK_ESCAPE:
                running = False
            elif event.key == SDLK_u:
                if show_blocks == False:
                    show_blocks = True
                else:
                    show_blocks = False

            # elif event.key == SDLK_j:
            #     move_all(10, 10)
            # elif event.key == SDLK_l:
            #     move_all(-10, -10)

        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LEFT:
                if LeftKeyPressed == 1:
                    LeftKeyPressed = -1

            elif event.key == SDLK_RIGHT:
                if RightKeyPressed == 1:
                    RightKeyPressed = -1

            elif event.key == SDLK_DOWN:
                DownKeyPressed = False
            elif event.key == SDLK_UP:
                UpKeyPressed = False

        # elif event.type == SDL_MOUSEBUTTONDOWN:
        #     if event.button == SDL_BUTTON_LEFT:
                
        

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



black_rect = load_image('resources/black_rect.png')
white_rect = load_image('resources/white_rect.png')
hero_right = load_image('resources/knight_hero_right.png')
hero_left = load_image('resources/knight_hero_left.png')
ex_map = load_image('resources/map_ex.png')
ex_block = load_image('resources/first_map.png')



running = 1
x_frame = 0
y_frame = 15
count = 0

def animation_count(): # 16 x 16
    global count, x_frame, y_frame, player_state, hero_heading_left, hero_heading_right
    global LeftKeyPressed, RightKeyPressed, is_falling
    global attack_anime_count, attack_dir

    count += 1

    if player_state == 1:
        if attack_dir == -1: # 유일한 left
            y_frame = 12
            if attack_anime_count % 15 == 0:
                x_frame -= 1
        elif attack_dir == 3:
            y_frame = 7
            if attack_anime_count % 15 == 0:
                x_frame -= 1

        elif attack_dir == 1:
            y_frame = 12
            if attack_anime_count % 15 == 0:
                x_frame += 1
        elif attack_dir == -2 or attack_dir == 2:
            y_frame = 7
            if attack_anime_count % 15 == 0:
                x_frame += 1
            

    elif count == 30:
        if JumpKeyPressed or JumpAgain or is_falling:
            y_frame = 6
                        # <- 0 ~ 25 상승, 25.2 ~ 50까지 착지.
                        # 점프 애니메이션 12개. 50까지 12개로 쪼개기.
                        
            if hero_heading_right:

                if JumpTime < 34:
                    for i in range(0, 34, 4):
                        if i <= JumpTime <= i + 4:
                            x_frame = i // 4
                            break
                elif 34 <= JumpTime < 38:
                    x_frame = 11
                elif 38 <= JumpTime < 42:
                    x_frame = 10
                elif 42 <= JumpTime < 46:
                    x_frame = 9
                elif 46 <= JumpTime:
                    x_frame = 8

            elif hero_heading_left:
                if JumpTime < 34:
                    for i in range(0, 34, 4):
                        if i <= JumpTime <= i + 4:
                            x_frame = 15 - (i // 4)
                            break
                            # 0 1 2 3 4 5 6 7
                            # 15 14 13 12 11 10 9 8
                elif 34 <= JumpTime < 38:
                    x_frame = 4
                elif 38 <= JumpTime < 42:
                    x_frame = 5
                elif 42 <= JumpTime < 46:
                    x_frame = 6
                elif 46 <= JumpTime:                                  
                    x_frame = 7
        
        elif hero_heading_right: # 0 1 2 3 4 5 6 7 8
            y_frame = 15
            if RightKeyPressed != 0: # moving, right
                x_frame = (x_frame + 1) % 9
            else: # idle, right
                x_frame = 0
            
        elif hero_heading_left: # 14 13 12 11 10 9 8 7 6
                                # x_frame은 왼쪽으로 전환할 때 초기화
            y_frame = 15
            if LeftKeyPressed != 0: # moving, left
                x_frame -= 1
                if (7 <= x_frame and x_frame <= 15) == False:
                    x_frame = 15
                if x_frame == 6:
                    x_frame = 15
            else: # idle, left
                x_frame = 15

        count = 0


if __name__ == '__main__':

    load_block()
    blocks_init()
    player_init()
    animation_count()
    

    while running:
        clear_canvas()
        blocks_init()
        player_init()

        pico2d.opacify(ex_block, 255)
        
        # draw(Xpos for start, Ypos for start, WIDTH /none, HEIGHT /none)
        ex_block.clip_draw(int(x - MoveDistance) // X_MOVE_POWER, int(y - JumpHeight) // Y_MOVE_POWER, 640, 360, 640, 360, 1280, 720)

        # block draw 할때 y는 x처럼 Move에서 최신화가 되지 않기 때문에 더해주어야 함.
        # white_rect.draw(int(block_x - MoveDistance) // (X_MOVE_POWER / 2), int(block_y + JumpHeight) // (Y_MOVE_POWER / 2))

        # print(int(block_x - MoveDistance) // (X_MOVE_POWER / 2), int(block_y + JumpHeight) // (Y_MOVE_POWER / 2))

        # hero? 128x128
        # 캐릭터 크기 100이 딱 맞는듯

        if player_state == 1:
            if attack_dir == 2 or attack_dir == -2 or attack_dir == 1: # up
                hero_right.clip_draw(128 * x_frame, 128 * y_frame, 128, 128,   # right로 통일.
                640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200, 100, 100)
            elif attack_dir == -1 or attack_dir == 3:
                hero_left.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
                640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200, 100, 100)


        elif player_state == 0: # idle 상태라면, 
            if hero_heading_right == 1:
                hero_right.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
                640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200, 100, 100)
            elif hero_heading_left == 1:
                hero_left.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
                640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200, 100, 100)

        hero_right.clip_draw(128 * 13, 128 * 3, 128, 128,
                             500, 300, 100, 100)        

        

        
        if show_blocks:
            draw_rectangle(PLAYER_RECT.left, PLAYER_RECT.top, PLAYER_RECT.right, PLAYER_RECT.bottom)
            for i in range(BLOCK_CNT):
                draw_rectangle(BLOCKS[i].left, BLOCKS[i].bottom, BLOCKS[i].right, BLOCKS[i].top)
        
        
        handle_events() 

        Move()
        Jump()
        Attack()

        animation_count()
        update_canvas()

close_canvas()