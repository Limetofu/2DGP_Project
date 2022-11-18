from sqlite3 import Time
from pico2d import *
import math
from dataclasses import dataclass
from mj_values import *
import numpy as np
from check_col import collision_check
from time import time

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

class MONSTER:
    x: int
    y: int

    hp: int

    left: int
    bottom: int
    width: int
    height: int
    type: str
    state: str
    count: int
    xframe: int
    dir: int
        # idle / alert / attacking / hit by player / dying / dead

class DIRT:
    x: int
    y: int
    show: bool
    count: int

class HIT_EFFECT:
    x: int
    y: int
    show: bool
    count: int
    x_frame: int


# BLOCK 구조체 배열(리스트) 만들 예정. 
BLOCKS = []

PLAYER_RECT = RECT()

DIRT_EFFECT = []

for i in range(0, 10):
    DIRT_EFFECT.append(DIRT())
    DIRT_EFFECT[i].x = 0
    DIRT_EFFECT[i].y = 0
    DIRT_EFFECT[i].show = 0
    DIRT_EFFECT[i].count = 0

MONSTERS = []
MONSTERS.append(MONSTER())
MONSTERS[0].x = 3000
MONSTERS[0].y = 800
MONSTERS[0].type = 'fly'
MONSTERS[0].state = 'idle'
MONSTERS[0].width = 150
MONSTERS[0].height = 150
MONSTERS[0].left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + 3385
MONSTERS[0].bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + 2500
MONSTERS[0].count = 0
MONSTERS[0].x_frame = 0
MONSTERS[0].dir = -1
MONSTERS[0].hp = 3


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

def monster_init():
    global MONSTERS, block_x, block_y, MoveDistance, JumpHeight
    global X_MOVE_POWER, Y_MOVE_POWER

    for m in MONSTERS:
        m.left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + m.x
        m.bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + m.y

def init_dark_images():
    global phun
    if len(phun) == 0:
        phun.append(load_image('resources/menu/10.png'))
        phun.append(load_image('resources/menu/20.png'))
        phun.append(load_image('resources/menu/30.png'))
        phun.append(load_image('resources/menu/40.png'))
        phun.append(load_image('resources/menu/50.png'))
        phun.append(load_image('resources/menu/60.png'))
        phun.append(load_image('resources/menu/70.png'))
        phun.append(load_image('resources/menu/80.png'))
        phun.append(load_image('resources/menu/90.png'))
        phun.append(load_image('resources/menu/100.png'))


pdc = 0

def pdark_animation():
    global penable_dark, pdark_count, pdark_dir, pdark_anime_count, pdc

    if penable_dark:
        pdark_anime_count += 1
        pdc += 1

        if pdark_anime_count % 15 == 14:
            if pdark_dir == 1:
                if pdark_count == 9:
                    pdark_dir *= -1
                    pdark_anime_count = 0
                    penable_dark = False
                    pdc = 0
                else:
                    pdark_count += 1

            elif pdark_dir == -1:
                if pdark_count == 0:
                    pdark_dir *= -1
                    pdark_anime_count = 0
                    penable_dark = False
                    pdc = 0
                else:
                    pdark_count -= 1
                
def pdraw_dark():
    global phun, pdark_count, penable_dark

    if pdark_count >= 1:
        phun[pdark_count].draw_to_origin(0, 0, 1280, 720)


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
    global entire_move_count
    # Distance에 상한을 정하고, 최대 속력을 맞추기

    MoveValue = 600.0
    MoveCountLimit = 100
    MoveTimeChange = 0.1


    # 둘 다 누른 상태가 아니거나, 둘 다 눌렀다가 뗸 상태도 아니면, 바로 종료하기
    if LeftKeyPressed == 0 and RightKeyPressed == 0 and MoveCount == 0:
        return


    entire_move_count += 1

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


    if now_move_player_left: # 플레이어를 움직일 차례. -> 맵 끝으로 갔기 때문
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

    elif now_move_player_right: # 플레이어를 움직일 차례. -> 맵 끝으로 갔기 때문

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
        entire_move_count = 0
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
    global shake_hit_count

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
            for m in MONSTERS:
                if (m.state == 'idle' or m.state == 'turn' or m.state == 'alert' or m.state == 'alert_turn') and \
                    PLAYER_RECT.left - 50 < m.left + 75 < PLAYER_RECT.left + 50 and \
                    PLAYER_RECT.bottom - 400 < m.bottom < PLAYER_RECT.bottom + 20:
                    m.state = 'hit'
                    m.hp -= 1

        elif UpKeyPressed:
            if hero_heading_left:
                attack_dir = 3
                x_frame = 15
            else:
                attack_dir = 2
                x_frame = 0
            for m in MONSTERS:
                if (m.state == 'idle' or m.state == 'turn' or m.state == 'alert' or m.state == 'alert_turn') and \
                    PLAYER_RECT.left - 50 < m.left + 75 < PLAYER_RECT.left + 50 and \
                    PLAYER_RECT.bottom + 20 < m.bottom < PLAYER_RECT.bottom + 400:
                    m.state = 'hit'
                    m.hp -= 1
            

        elif hero_heading_left:
            attack_dir = -1
            x_frame = 15
            for m in MONSTERS:
                if (m.state == 'idle' or m.state == 'turn' or m.state == 'alert' or m.state == 'alert_turn') and \
                    PLAYER_RECT.left - 150 < m.left + 150 < PLAYER_RECT.left and \
                    PLAYER_RECT.bottom - 50 < m.bottom < PLAYER_RECT.bottom + 200:
                    m.state = 'hit'
                    m.hp -= 1
                    shake_hit_count = 6
                    attack_effect(m.left, m.bottom)

        
        else:
            attack_dir = 1
            x_frame = 0
            for m in MONSTERS:
                if (m.state == 'idle' or m.state == 'turn' or m.state == 'alert' or m.state == 'alert_turn') and \
                    PLAYER_RECT.right < m.left < PLAYER_RECT.right + 150 and \
                    PLAYER_RECT.bottom - 50 < m.bottom < PLAYER_RECT.bottom + 200:
                    m.state = 'hit'
                    m.hp -= 1
                    shake_hit_count = 6
                    attack_effect(m.left, m.bottom)
    
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


def attack_effect(x, y):
    global hit_effect
    l = len(hit_effect)
    hit_effect.append(HIT_EFFECT())
    hit_effect[l].x = x
    hit_effect[l].y = y
    hit_effect[l].show = True
    hit_effect[l].x_frame = 0
    hit_effect[l].count = 0

def attack_effect_count():
    global hit_effect, hit_effect_image
    if_del = []

    cnt = -1
    for a in hit_effect:
        cnt += 1
        if a.show:
            if a.count % 15 == 14:
                if a.x_frame == 2:
                    if_del.append(cnt)
                else: a.x_frame += 1
            a.count += 1
    del_attack_effect(if_del)

def del_attack_effect(n):
    global hit_effect
    for i in n:
        del hit_effect[i]

def draw_attack_effect():
    global hit_effect_image
    for a in hit_effect:
        if a.show:
            hit_effect_image.clip_draw_to_origin(hit_effect_image.w // 3 * a.x_frame, 0, hit_effect_image.w // 3, hit_effect_image.h,
                                                 a.x, a.y, hit_effect_image.w // 3, hit_effect_image.h)



def Fly():
    global MONSTERS

    dataclass_num = -1

    # 1. idle
    #   기본 위치에서 좌우로 이동
    #   끝에 가면 잠시 멈추고, 방향 바꾸고 turn 상태 출력 후  
    #   반대 방향으로 바꾸기. (count 초기화)
    for m in MONSTERS:
        dataclass_num += 1
        if m.type == 'fly': # fly가 맞다면
            if m.state == 'idle':
                change_state_alert(dataclass_num)
                if m.count <= 2000:
                    if m.dir == -1:
                        m.x -= 0.5
                    elif m.dir == 1:
                        m.x += 0.5
                else: # change
                    if m.count > 2400:
                        m.state = 'turn'
                        m.count = 0
                        m.x_frame = 0
                        m.dir *= -1

            elif m.state == 'turn':
                change_state_alert(dataclass_num)
                if m.count >= 60:
                    m.state = 'idle'
                    m.count = 0
                    m.x_frame = 0



            elif m.state == 'alert': # chase anime
            
                if m.dir == -1: # 왼쪽 바라볼 때
                    if m.count > 250:
                        m.x -= 1
                        if m.bottom - 10 > PLAYER_RECT.top:
                            m.y -= 0.25
                        elif m.bottom + m.height + 10 < PLAYER_RECT.bottom:
                            m.y += 0.25

                    if PLAYER_RECT.left > m.left:
                        m.count = 0
                        m.x_frame = 0
                        m.state = 'alert_turn'
                        m.dir *= -1
                elif m.dir == 1:
                    if m.count > 250:
                        m.x += 1
                        if m.bottom - 10 > PLAYER_RECT.top:
                            m.y -= 0.25
                        elif m.bottom + m.height + 10 < PLAYER_RECT.bottom:
                            m.y += 0.25

                    if PLAYER_RECT.right < m.left + m.width:
                        m.count = 0
                        m.x_frame = 0
                        m.state = 'alert_turn'
                        m.dir *= -1
                
            elif m.state == 'alert_turn':
                if m.count >= 60:
                    m.state = 'alert'
                    m.count = 0
                    m.x_frame = 0
            
            elif m.state == 'hit':
                if m.hp <= 0: 
                    m.count = 0
                    m.x_frame = 0
                    m.state = 'dying'

                if m.count >= 60:
                    m.state = 'alert'
                    m.count = 150
                    m.x_frame = 0

            elif m.state == 'dying':
                if m.count >= 60:
                    m.state = 'dead'

            elif m.state == 'dead':
                pass

            m.count += 1

    #   플레이어 위치와 가까워지면, 
    monster_animation()
    
def change_state_alert(i):
    global MONSTERS, PLAYER_RECT

    if MONSTERS[i].dir == -1: # 왼쪽 보고있음
        if MONSTERS[i].left + MONSTERS[i].width - 400 < PLAYER_RECT.left < MONSTERS[i].left + MONSTERS[i].width - 10 and \
        MONSTERS[i].bottom - 150 < PLAYER_RECT.bottom + (PLAYER_RECT.top // 2) < MONSTERS[i].bottom + 150:
            MONSTERS[i].state = 'alert'
            MONSTERS[i].x_frame = 0
            MONSTERS[i].count = 0

    elif MONSTERS[i].dir == 1: # 오른쪽
        if MONSTERS[i].left + MONSTERS[i].width + 10 < PLAYER_RECT.left < MONSTERS[i].left + MONSTERS[i].width + 400 and \
        MONSTERS[i].bottom - 150 < PLAYER_RECT.bottom + (PLAYER_RECT.top // 2) < MONSTERS[i].bottom + 150:
            MONSTERS[i].state = 'alert'
            MONSTERS[i].x_frame = 0
            MONSTERS[i].count = 0



def monster_animation():
    global MONSTERS

    for m in MONSTERS:
        if m.type == 'fly':
            if m.count % 30 == 29:
                if m.state == 'idle':
                    m.x_frame = (m.x_frame + 1) % 5
                elif m.state == 'turn' or m.state == 'alert_turn':
                    m.x_frame = (m.x_frame + 1) % 2
                elif m.state == 'alert' or m.state == 'hit':
                    m.x_frame = (m.x_frame + 1) % 4
                elif m.state == 'dying':
                    m.x_frame = (m.x_frame + 1) % 3

    monster_init()




def handle_events():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime, player_on_block_num, is_falling
    global running
    global JumpAgain
    global y, block_y, show_blocks
    global LeftKeyPressed, RightKeyPressed, MoveCount, MoveTime
    global hero_heading_right, hero_heading_left, x_frame
    global UpKeyPressed, DownKeyPressed, player_state
    global shake_countY, shake_countX

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


# ----------------------- shake test ---------------------------

            elif event.key == SDLK_h:
                if shake_countY == 0: shake_countY = 6

            elif event.key == SDLK_y:
                if shake_countY == 0: shake_countY = -6

            elif event.key == SDLK_k:
                if shake_countX == 0: shake_countX = 6

            elif event.key == SDLK_i:
                if shake_countX == 0: shake_countX = -6
            

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

def shake_screen(xvalue, yvalue):
    global player_x, player_y, y, x
    global shake_countY, shake_countX, shake_hit_count

    if shake_hit_count >= 1:
        shake_hit_count -= 1
    elif shake_hit_count <= -1:
        shake_hit_count += 1

    if yvalue != 0:
        if 1 <= shake_countY: shake_countY -= 1
        elif shake_countY <= -1: shake_countY += 1
    if xvalue != 0:
        if 1 <= shake_countX: shake_countX -= 1   
        elif shake_countX <= -1: shake_countX += 1

    #player_x += xvalue
    y -= yvalue * 2
    player_y += yvalue

    x += xvalue * 2
    player_x += xvalue


def shake_anime_count():
    global shake_countY, shake_countX, shake_hit_count

    if   shake_countY == 0:  pass

    elif shake_countY == 6:  shake_screen(0, -10)
    elif shake_countY == 5:  shake_screen(0, -15)
    elif shake_countY == 4:  shake_screen(0,  20)
    elif shake_countY == 3:  shake_screen(0,  15)
    elif shake_countY == 2:  shake_screen(0,  -5)
    elif shake_countY == 1:  shake_screen(0,  -5)

    elif shake_countY == -6: shake_screen(0,  10)
    elif shake_countY == -5: shake_screen(0,  15)
    elif shake_countY == -4: shake_screen(0, -20)
    elif shake_countY == -3: shake_screen(0, -15)
    elif shake_countY == -2: shake_screen(0,   5)
    elif shake_countY == -1: shake_screen(0,   5)



    if   shake_countX == 0:  pass

    elif shake_countX == 6:  shake_screen(-10, 0)
    elif shake_countX == 5:  shake_screen(-15, 0)
    elif shake_countX == 4:  shake_screen( 20, 0)
    elif shake_countX == 3:  shake_screen( 15, 0)
    elif shake_countX == 2:  shake_screen( -5, 0)
    elif shake_countX == 1:  shake_screen( -5, 0)

    elif shake_countX == -6: shake_screen( 10, 0)
    elif shake_countX == -5: shake_screen( 15, 0)
    elif shake_countX == -4: shake_screen(-20, 0)
    elif shake_countX == -3: shake_screen(-15, 0)
    elif shake_countX == -2: shake_screen(  5, 0)
    elif shake_countX == -1: shake_screen(  5, 0)


    if   shake_hit_count == 0:  pass

    elif shake_hit_count == 6:  shake_screen( 10, 0)
    elif shake_hit_count == 5:  shake_screen( 8, 0)
    elif shake_hit_count == 4:  shake_screen( -12, 0)
    elif shake_hit_count == 3:  shake_screen( -10, 0)
    elif shake_hit_count == 2:  shake_screen( 6, 0)
    elif shake_hit_count == 1:  shake_screen( -2, 0)

    elif shake_hit_count == -6:  shake_screen( 7, 0)
    elif shake_hit_count == -5:  shake_screen( -4, 0)
    elif shake_hit_count == -4:  shake_screen( -3, 0)
    elif shake_hit_count == -3: shake_screen(- 7, 0)
    elif shake_hit_count == -2: shake_screen(  4, 0)
    elif shake_hit_count == -1: shake_screen(  3, 0)

def animation_count(): # 16 x 16
    global count, x_frame, y_frame, player_state, hero_heading_left, hero_heading_right
    global LeftKeyPressed, RightKeyPressed, is_falling
    global attack_anime_count, attack_dir

    count += 1

    if count % 7 == 0:
        shake_anime_count()

    if player_state == 1:
        if attack_dir == -1: # 유일한 left
            y_frame = 12
            if attack_anime_count % 10 == 0:
                x_frame -= 1
        elif attack_dir == 3:
            y_frame = 7
            if attack_anime_count % 10 == 0:
                x_frame -= 1

        elif attack_dir == 1:
            y_frame = 12
            if attack_anime_count % 10 == 0:
                x_frame += 1
        elif attack_dir == -2 or attack_dir == 2:
            y_frame = 7
            if attack_anime_count % 10 == 0:
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

def init_image():
    global white_rect, hero_right, hero_left, ex_map, ex_block
    global fly_idle, fly_chase, fly_die, fly_turn_left, fly_shock
    global hp_o, hp_x, hit_effect_image

    white_rect = load_image('resources/white_rect.png')
    hero_right = load_image('resources/knight_hero_right.png')
    hero_left = load_image('resources/knight_hero_left.png')
    ex_map = load_image('resources/map_ex.png')
    ex_block = load_image('resources/first_map.png')

    fly_idle = load_image('resources/monsters/fly_idle.png')
    fly_shock = load_image('resources/monsters/fly_shock.png')
    fly_chase = load_image('resources/monsters/fly_chase.png')
    fly_die = load_image('resources/monsters/fly_die.png')
    fly_turn_left = load_image('resources/monsters/fly_turn_left.png')

    hp_o = load_image('resources/hp_o.png')
    hp_x = load_image('resources/hp_x.png')
    hit_effect_image = load_image('resources/hit_effect_left.png')

# dirt_image = load_image('resources/monsters/dirt.png')

x_frame = 0
y_frame = 15
count = 0

def draw_player():
    # hero? 128x128
        # 캐릭터 크기 100이 딱 맞는듯
    global player_state, attack_dir, x_frame, y_frame, player_x, PlayerMoveDistance, player_y
    global X_MOVE_POWER, hero_right, hero_left, hero_heading_right, hero_heading_left


    if player_state == 1: # Attack
        
        if attack_dir == 2 or attack_dir == -2 or attack_dir == 1: # up
            hero_right.clip_draw(128 * x_frame, 128 * y_frame, 128, 128,   # right로 통일.
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)
        elif attack_dir == -1 or attack_dir == 3:
            hero_left.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)


        # x_frame 6개. # 3, 13
        if attack_dir == 2: # up
            hero_right.clip_composite_draw(128 * 13, 128 * 3, 128, 128, 70, '',   # right로 통일.
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) + 20, 200 + 75 + player_y, 150, 150)
        elif attack_dir == 3:
            hero_right.clip_composite_draw(128 * 13, 128 * 3, 128, 128, 90, '', 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) - 30, 200 + 75 + player_y, 150, 150)
        elif attack_dir == -1: #left
            hero_right.clip_composite_draw(128 * 13, 128 * 3, 128, 128, 210, '', 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) - 75, 200 + 20 + player_y, 150, 150)
        elif attack_dir == 1: # right
            hero_right.clip_composite_draw(128 * 13, 128 * 3, 128, 128, 100, '',
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) + 75, 200 + player_y, 150, 150)
        elif attack_dir == -2: # down
            hero_right.clip_composite_draw(128 * 13, 128 * 3, 128, 128, 325, '',
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 - 75 + player_y, 150, 150)



    elif player_state == 0: # idle 상태라면, 
        if hero_heading_right == 1:
            hero_right.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)
        elif hero_heading_left == 1:
            hero_left.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)

def draw_monster():
    global MONSTERS
    global fly_chase, fly_die, fly_turn_left, fly_idle, fly_shock

    for m in MONSTERS:
        # draw_rectangle(int(m.left), int(m.bottom), int(m.left) + m.width, int(m.bottom) + m.height)
        if m.type == 'fly':

            if m.state == 'idle':
                if m.dir == -1: fly_idle.clip_draw(fly_idle.w // 5 * m.x_frame, 0, fly_idle.w // 5, fly_idle.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                elif m.dir == 1: fly_idle.clip_composite_draw(fly_idle.w // 5 * m.x_frame, 0, fly_idle.w // 5, fly_idle.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
            elif m.state == 'turn' or m.state == 'alert_turn':
                if m.dir == -1: fly_turn_left.clip_draw(fly_turn_left.w // 2 * m.x_frame, 0, fly_turn_left.w // 2, fly_turn_left.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                elif m.dir == 1: fly_turn_left.clip_composite_draw(fly_turn_left.w // 2 * m.x_frame, 0, fly_turn_left.w // 2, fly_turn_left.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)

            elif m.state == 'alert':
                if m.dir == -1: fly_chase.clip_draw(fly_chase.w // 4 * m.x_frame, 0, fly_chase.w // 4, fly_chase.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                elif m.dir == 1: fly_chase.clip_composite_draw(fly_chase.w // 4 * m.x_frame, 0, fly_chase.w // 4, fly_chase.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)

            elif m.state == 'hit':
                if m.dir == -1: fly_shock.clip_draw(fly_shock.w // 4 * m.x_frame, 0, fly_shock.w // 4, fly_shock.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                elif m.dir == 1: fly_shock.clip_composite_draw(fly_shock.w // 4 * m.x_frame, 0, fly_shock.w // 4, fly_shock.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)

            elif m.state == 'dying':
                if m.dir == -1: fly_die.clip_draw(fly_die.w // 3 * m.x_frame, 0, fly_die.w // 3, fly_die.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                elif m.dir == 1: fly_die.clip_composite_draw(fly_die.w // 3 * m.x_frame, 0, fly_die.w // 3, fly_die.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                
def draw_hp():
    global player_hp, player_full_hp
    global hp_o, hp_x

    for i in range(0, player_hp):
            hp_o.draw(35 * i + 100, 640, int(hp_o.w * 0.7), int(hp_o.h*0.7))
    for i in range(player_hp, player_full_hp):
            hp_x.draw(35 * i + 100, 640, int(hp_x.w * 0.7), int(hp_x.h*0.7))

def Game_State():
    init_image()

    load_block()
    blocks_init()
    player_init()
    Fly()
    animation_count()
    init_dark_images()
    global penable_dark
    penable_dark = True
    running = True

    while running:
        clear_canvas()
        blocks_init()
        player_init()
        Fly()

        # draw(Xpos for start, Ypos for start, WIDTH /none, HEIGHT /none)
        ex_block.clip_draw(int(x - MoveDistance) // X_MOVE_POWER, int(y - JumpHeight) // Y_MOVE_POWER, 640, 360, 640, 360, 1280, 720)

        draw_player()
        draw_monster()
        draw_hp()

        
        attack_effect_count()
        draw_attack_effect()


        if show_blocks:
            draw_rectangle(PLAYER_RECT.left, PLAYER_RECT.top, PLAYER_RECT.right, PLAYER_RECT.bottom)
            for i in range(BLOCK_CNT):
                draw_rectangle(BLOCKS[i].left, BLOCKS[i].bottom, BLOCKS[i].right, BLOCKS[i].top)
        
        handle_events()

        Move()
        Jump()
        Attack()
        # Dirt()

        animation_count()

        pdraw_dark()
        pdark_animation()

        update_canvas()

    close_canvas()

if __name__ == '__main__':
    open_canvas(1280, 720, sync=False)
    Game_State()
