from sqlite3 import Time
from pico2d import *
import math
from dataclasses import dataclass
from mj_values import *
import numpy as np
from check_col import collision_check
import time
from random import randint

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
    right: int
    top: int

    bleft: int
    bbottom: int
    bright: int
    btop: int
    
    width: int
    height: int
    type: str
    state: str
    count: int
    xframe: int
    dir: int
        # idle / alert / attacking / hit by player / dying / dead

class HIT_EFFECT:
    x: int
    y: int
    left: int
    right: int
    bottom: int
    top: int
    show: bool
    count: int
    x_frame: int
    dir: str

class BOSS:
    x: int
    y: int

    hp: int

    left: int
    bottom: int
    right: int
    top: int

    bleft: int
    bbottom: int
    bright: int
    btop: int
    
    width: int
    height: int

    type: str
    state: str

    count: int
    xframe: int
    dir: int

class PATTERN:
    x: int
    y: int

    left: int
    bottom: int
    right: int
    top: int

    bleft: int
    bbottom: int
    bright: int
    btop: int

    width: int
    height: int

    count: int
    xframe: int

    type: str
    state: str

# BLOCK 구조체 배열(리스트) 만들 예정. 
BLOCKS = []

PLAYER_RECT = RECT()

MONSTERS = []
MONSTERS_ORIGINAL_POS = []

warp_effect = HIT_EFFECT()

def init_warp_effect():
    global warp_effect
    warp_effect.show = False
    warp_effect.x = 0
    warp_effect.y = 0
    warp_effect.left = 0
    warp_effect.bottom = 0
    warp_effect.count = 0
    warp_effect.dir = ''
    warp_effect.x_frame = 0

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

def load_monster():
    global MONSTERS, MONSTER_CNT, monster_data

    with open("monster_data.txt", "r") as file:
        data = file.readlines()
    file.close()

    MONSTER_CNT = len(data)

    for i in data:
        tmp_str = i.replace('\n', '\n')
        monster_data.append(tmp_str)

    for M in (MONSTERS, MONSTERS_ORIGINAL_POS):
        for i in range(MONSTER_CNT):
            mtype = int(monster_data[i][24])
            if mtype == 4: # Elder Hu
                pass

            M.append(MONSTER())
            M[i].x = int(monster_data[i][0:6])
            M[i].y = int(monster_data[i][7:13])
            
            if mtype == 1: # fly
                M[i].width = 150
                M[i].height = 150
                M[i].type = 'fly'
                M[i].state = 'idle'
                M[i].hp = 3

            elif mtype == 2: # tik
                M[i].width = 93
                M[i].height = 80
                M[i].type = 'tiktik'
                M[i].state = 'idle'
                M[i].hp = 3

            elif mtype == 3: # thorn block
                M[i].width = int(monster_data[i][14:18])
                M[i].height = int(monster_data[i][19:23])
                M[i].type = 'thorn'
                M[i].state = 'thorn'
                M[i].hp = 999

            elif mtype == 4: # teleport block
                M[i].width = int(monster_data[i][14:18])
                M[i].height = int(monster_data[i][19:23])
                M[i].type = 'teleport'
                M[i].state = 'teleport'
                M[i].hp = 999
            
            elif mtype == 5: # heart item
                M[i].width = 50
                M[i].height = 50
                M[i].type = 'item'
                M[i].state = 'on'
                M[i].hp = 999

            M[i].count = 0
            M[i].x_frame = 0
            if randint(0, 1):
                M[i].dir = -1
            else:
                M[i].dir = 1
            if M[i].dir != -1 and M[i].dir != 1: # -1도 아니고 1도 아니면
                print(f'{i}th monster dir error')

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
    global player_y, player_move_y, boss_stage_jump_value

    PLAYER_RECT.left = 640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) -25
    PLAYER_RECT.bottom = 200 + int(boss_stage_jump_value) - 50
    PLAYER_RECT.right = PLAYER_RECT.left + 50
    PLAYER_RECT.top = 200 + int(boss_stage_jump_value) + 50

def monster_init():
    global MONSTERS, block_x, block_y, MoveDistance, JumpHeight
    global X_MOVE_POWER, Y_MOVE_POWER

    for m in MONSTERS:
        m.left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + m.x
        m.right = m.left + m.width
        m.bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + m.y
        m.top = m.bottom + m.height
        if m.type == 'fly':
            m.bleft = m.left + 30
            m.bright = m.right - 30
            m.bbottom = m.bottom + 30
            m.btop = m.top - 30
        else:
            m.bleft = m.left
            m.bright = m.right
            m.bbottom = m.bottom
            m.btop = m.top

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

    global play_font
    play_font = load_font('resources/fonts/HeirofLightRegular.ttf', 30)

def pdark_animation():
    global penable_dark, pdark_count, pdark_dir, pdark_anime_count, pdc
    global player_state, teleport_type

    if penable_dark:
        pdark_anime_count += 1
        pdc += 1

        if pdark_anime_count % 15 == 14:
            if pdark_dir == 1:
                if pdark_count == 9:
                    pdark_dir *= -1
                    pdark_anime_count = 9
                    pdc = 0
                    if player_state == 3:
                        player_resurrection(teleport_type)
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

def player_resurrection(dest = 'start'):
    global player_state, x, y, block_x, block_y
    global diameter, now_move_player_left, now_move_player_right, player_on_block_num, entire_move_count
    global player_x, player_y, player_move_y, x_frame, y_frame, count
    global JumpHeight, JumpTime, RemainJumpTimeCount, JumpKeyPressed, is_falling, JumpAgain
    global PLAYER_START_X, PLAYER_START_Y, START_BLOCK_X, START_BLOCK_Y
    global player_full_hp, player_hp
    global MONSTERS, MONSTERS_ORIGINAL_POS

    player_state = 0

    if dest == 'start':
        player_hp = player_full_hp
        x = PLAYER_START_X
        y = PLAYER_START_Y # 시작점

        block_x = START_BLOCK_X
        block_y = START_BLOCK_Y # 시작점의 역수로 잡아야 블럭의 위치가 잡힘

    elif dest == 'boss':
        x = 9350.0
        y = 5950.0 # 시작점

        block_x = -x
        block_y = -y # 시작점의 역수로 잡아야 블럭의 위치가 잡힘


    diameter = 20.0

    now_move_player_left = False
    now_move_player_right = False

    player_on_block_num = -1

    entire_move_count = 0

    player_x = 0
    player_y = 0 # <--- y 변화량만. (아래 바라보거나 / 화면 흔들리는 이펙트)
    player_move_y = 0 # 보스 스테이지에서 수정하는 값

    x_frame = 0
    y_frame = 15
    count = 0

    JumpHeight = 0
    JumpTime = JumpPower // 2 + 1.0

    RemainJumpTimeCount = 0

    JumpKeyPressed = True
    is_falling = True
    JumpAgain = True

    for i in range(MONSTER_CNT):
        if MONSTERS[i].type != 'item':
            MONSTERS[i].x = MONSTERS_ORIGINAL_POS[i].x
            MONSTERS[i].y = MONSTERS_ORIGINAL_POS[i].y
            MONSTERS[i].width = MONSTERS_ORIGINAL_POS[i].width
            MONSTERS[i].height = MONSTERS_ORIGINAL_POS[i].height
            MONSTERS[i].type = MONSTERS_ORIGINAL_POS[i].type
            MONSTERS[i].state = MONSTERS_ORIGINAL_POS[i].state
            MONSTERS[i].hp = MONSTERS_ORIGINAL_POS[i].hp

            MONSTERS[i].count = 0
            MONSTERS[i].x_frame = 0

            if randint(0, 1):
                MONSTERS[i].dir = -1
            else:
                MONSTERS[i].dir = 1

def Jump():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime
    global JumpAgain, RemainJumpTimeCount
    global y, block_y, player_move_y
    global is_falling
    global player_on_block_num, StageNum, boss_stage_jump_value

    blocks_init()

    # space를 누르지 않으면, 종료
    if JumpKeyPressed == 0 and is_falling == 0:
        return
    
    if StageNum == 1:
        JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0
        
        if RemainJumpTimeCount > 0:
            RemainJumpTimeCount -= 4
            if RemainJumpTimeCount <= 0:
                JumpTime = 50 - JumpTime
                RemainJumpTimeCount = 0
        else:
            JumpTime += 0.2

        # 변곡점 --> JumpHeight = -312.5
        if JumpHeight <= -312:
            is_falling = True


        # 점프 끝내는 조건문
        ## 끝내야 할 때?
        ##  1. 블럭 위에 도착했을 때
        ##      -> is_falling 상태일 때만 활성화하기.
        ##  2. 블럭 아래에 부딪혔을 때
        
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
                # 바닥 충돌

                collision_repair_bottom(i)

                
                # if JumpAgain:
                #     JumpTime = 50 - JumpTime
                # else:
                #     JumpTime = 50 - JumpTime

                RemainJumpTimeCount = (25 - JumpTime) / 0.2 + 0.1

                JumpHeight = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0

                # draw_rectangle(temp_rect.left, temp_rect.bottom - 1, temp_rect.right, temp_rect.top + 1)
                update_canvas()

                is_falling = True

    elif StageNum == 2: # boss
        boss_stage_jump_value = (JumpTime * JumpTime - JumpPower * JumpTime) / 2.0
        JumpTime += 0.2

        # 변곡점 --> JumpHeight = -312.5
        if boss_stage_jump_value <= -312:
            is_falling = True
        
        for i in range(BLOCK_CNT): # 위쪽 충돌
            temp_rect = BLOCK()
            temp_rect.left, temp_rect.right = BLOCKS[i].left, BLOCKS[i].right 
            temp_rect.top, temp_rect.bottom = BLOCKS[i].top + 8, BLOCKS[i].top + 8

            if collision_check(temp_rect, PLAYER_RECT) and is_falling == True:
                JumpTime = 0
                player_move_y -= boss_stage_jump_value

                JumpKeyPressed = False
                boss_stage_jump_value = 0
                is_falling = False
                player_on_block_num = i
                
                collision_repair(i)

                JumpAgain = False
                return

def Move():
    global LeftKeyPressed, RightKeyPressed, MoveDistance, PlayerMoveDistance, MovePower, MoveTime, MoveCount, x, y
    global block_x, X_MOVE_POWER, now_move_player_left, now_move_player_right, player_x, ex_block, block_y
    global JumpTime, JumpKeyPressed, player_on_block_num, is_falling, JumpHeight, JumpPower
    global can_climb_left, can_climb_right
    global entire_move_count
    global DashCount, DashCoolTime
    # Distance에 상한을 정하고, 최대 속력을 맞추기

    MoveValue = 600.0
    MoveCountLimit = 100
    MoveTimeChange = 0.1

    if DashCount > 0:
        MovePower = 1000.0
        DashCount -= 1
        if DashCount <= 0: 
            DashCoolTime = 150
    else:
        MovePower = 200.0

    if DashCoolTime >= 1:
        DashCoolTime -= 1

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
                    PLAYER_RECT.left - 80 < m.bleft + (m.width // 2) < PLAYER_RECT.right + 80 and \
                    PLAYER_RECT.bottom - 150 < m.btop < PLAYER_RECT.bottom:
                    m.state = 'hit'
                    m.count = 0
                    m.x_frame = 0
                    m.hp -= 1
                    shake_hit_count = 6
                    attack_effect(m.x, m.y, 'down')

        elif UpKeyPressed:
            if hero_heading_left:
                attack_dir = 3
                x_frame = 15
            else:
                attack_dir = 2
                x_frame = 0
            for m in MONSTERS:
                if (m.state == 'idle' or m.state == 'turn' or m.state == 'alert' or m.state == 'alert_turn') and \
                    PLAYER_RECT.left - 80 < m.bleft + (m.width // 2) < PLAYER_RECT.left + 80 and \
                    PLAYER_RECT.top < m.bbottom < PLAYER_RECT.top + 150:
                    m.state = 'hit'
                    m.count = 0
                    m.x_frame = 0
                    m.hp -= 1
                    shake_hit_count = 6
                    attack_effect(m.x, m.y, 'up')
            

        elif hero_heading_left:
            attack_dir = -1
            x_frame = 15
            for m in MONSTERS:
                if (m.state == 'idle' or m.state == 'turn' or m.state == 'alert' or m.state == 'alert_turn') and \
                    PLAYER_RECT.left - 150 < m.bright < PLAYER_RECT.left and \
                    PLAYER_RECT.bottom - 50 < m.bbottom < PLAYER_RECT.top + 50:
                    m.state = 'hit'
                    m.count = 0
                    m.x_frame = 0
                    m.hp -= 1
                    shake_hit_count = 6
                    attack_effect(m.x, m.y, 'right')
        
        else:
            attack_dir = 1
            x_frame = 0
            for m in MONSTERS:
                if (m.state == 'idle' or m.state == 'turn' or m.state == 'alert' or m.state == 'alert_turn') and \
                    PLAYER_RECT.right < m.bleft < PLAYER_RECT.right + 150 and \
                    PLAYER_RECT.bottom - 50 < m.bbottom < PLAYER_RECT.top + 50:
                    m.state = 'hit'
                    m.count = 0
                    m.x_frame = 0
                    m.hp -= 1
                    shake_hit_count = 6
                    attack_effect(m.x, m.y, 'left')
    
    else: # 0이 아님! -> 공격중. count 올려주자
        if attack_anime_count > attack_anime_frame:
            # attack anime이 끝. 초기화 시켜주기.
            attack_anime_count = 0
            attack_dir = 0
            count = 0
            player_state = 0 # idle 상태로

        else:
            attack_anime_count += 1

def attack_effect(x, y, dir):
    global hit_effect, player_hp_gage
    l = len(hit_effect)
    hit_effect.append(HIT_EFFECT())

    player_hp_gage += 1

    if player_hp_gage >= 11:
        player_hp_gage = 10

    hit_effect[l].x = x
    hit_effect[l].y = y
    hit_effect[l].left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + x
    hit_effect[l].bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + y
    # print(f'effect x :{hit_effect[l].x} | effect y :{hit_effect[l].y}')
    hit_effect[l].show = True
    hit_effect[l].x_frame = 0
    hit_effect[l].count = 0
    hit_effect[l].dir = dir

def boss_warp_effect(x, y):
    global warp_effect
    warp_effect.x = x
    warp_effect.y = y
    warp_effect.left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + x
    warp_effect.bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + y

    warp_effect.show = True
    warp_effect.count = 0
    warp_effect.dir = ''
    
def update_effect():
    global hit_effect, warp_effect
    for l in range(len(hit_effect)):
        hit_effect[l].left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + hit_effect[l].x
        hit_effect[l].bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + hit_effect[l].y
    warp_effect.left = int(block_x - MoveDistance) // (X_MOVE_POWER / 2) + warp_effect.x
    warp_effect.bottom = int(block_y + JumpHeight) // (Y_MOVE_POWER / 2) + warp_effect.y

def attack_effect_count():
    global hit_effect, hit_effect_image, warp_effect

    del_cnt_list = []

    cnt = -1
    for a in hit_effect:
        cnt += 1
        if a.show:
            if a.count % 15 == 14:
                if a.x_frame == 2:
                    del_cnt_list.append(cnt)
                else: a.x_frame += 1
            a.count += 1
    del_attack_effect(del_cnt_list)

def warp_effect_count():
    global warp_effect

    if warp_effect.show:
        if warp_effect.count == 15:
            if warp_effect.x_frame + 1 == 4:
                warp_effect.x_frame = 0
                warp_effect.count = 0
                warp_effect.show = False
            else:
                warp_effect.x_frame = (warp_effect.x_frame + 1) % 4
                warp_effect.count = 0
        else: 
            warp_effect.count += 1

def del_attack_effect(del_cnt_list):
    global hit_effect

    for i in del_cnt_list:
        try:
            del hit_effect[0]
        except:
            print('hit_effect error occured, ', i, len(hit_effect))

def draw_attack_effect():
    global hit_effect_image, hit_effect
    for a in hit_effect:
        if a.show:
            if a.dir == 'left':
                hit_effect_image.clip_draw_to_origin(hit_effect_image.w // 3 * a.x_frame, 0,
                                                 hit_effect_image.w // 3, hit_effect_image.h,
                                                 a.left, a.bottom, hit_effect_image.w // 3, hit_effect_image.h)
            if a.dir == 'right':
                hit_effect_image.clip_composite_draw(hit_effect_image.w // 3 * a.x_frame, 0, 
                                                 hit_effect_image.w // 3, hit_effect_image.h,
                                                 0, 'h',
                                                 a.left, a.bottom + (hit_effect_image.h // 2), hit_effect_image.w // 3, hit_effect_image.h)
            if a.dir == 'up':
                hit_effect_image.clip_composite_draw(hit_effect_image.w // 3 * a.x_frame, 0, 
                                                 hit_effect_image.w // 3, hit_effect_image.h,
                                                 0, 'v',
                                                 a.left + (hit_effect_image.w // 6), a.bottom + (hit_effect_image.h // 2), hit_effect_image.w // 3, hit_effect_image.h)
            if a.dir == 'down':
                hit_effect_image.clip_composite_draw(hit_effect_image.w // 3 * a.x_frame, 0, 
                                                 hit_effect_image.w // 3, hit_effect_image.h,
                                                 0, 'hv',
                                                 a.left, a.bottom + (hit_effect_image.h // 2), hit_effect_image.w // 3, hit_effect_image.h)

def draw_warp_effect():
    global warp_effect, warp_image
    if warp_effect.show:
        draw_rectangle(int(warp_effect.left) - 10, int(warp_effect.bottom) - 10, int(warp_effect.left) + 10, int(warp_effect.bottom) + 10)
        warp_image.clip_draw(0, warp_effect.x_frame * (warp_image.h // 4), 1843, 614, int(warp_effect.left), int(warp_effect.bottom), 402, 134)

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
                        if m.bbottom + 10 > PLAYER_RECT.top:
                            m.y -= 0.5
                        elif m.bbottom + (m.height - 60) - 10 < PLAYER_RECT.bottom:
                            m.y += 0.5

                    if PLAYER_RECT.right > m.left + m.width:
                        m.count = 0
                        m.x_frame = 0
                        m.state = 'alert_turn'
                        m.dir *= -1

                elif m.dir == 1:
                    if m.count > 250:
                        m.x += 1
                        if m.bbottom + 10 > PLAYER_RECT.top:
                            m.y -= 0.5
                        elif m.bbottom + (m.height - 60) - 10 < PLAYER_RECT.bottom:
                            m.y += 0.5

                    if PLAYER_RECT.right < m.left:
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

            
        elif m.type == 'tiktik':
            if m.state == 'idle': # 블럭 따라 이동
                if m.dir == 1:
                    if m.count >= 600:
                        m.count = 0
                        m.dir *= -1
                    else:
                        m.x += 0.1
                elif m.dir == -1:
                    if m.count >= 600:
                        m.count = 0
                        m.dir *= -1
                    else:
                        m.x -= 0.1

            elif m.state == 'hit':
                if m.hp <= 0: 
                    m.count = 0
                    m.x_frame = 0
                    m.state = 'dying'

                if m.count >= 120:
                    m.count = 0
                    m.x_frame = 0
                    m.state = 'idle'
                else: 
                    m.count += 1

            elif m.state == 'dying':
                if m.count >= 30 * 5:
                    m.state = 'dead'
                else: 
                    m.count += 1
            elif m.state == 'dead':
                pass
        elif m.type == 'elder_hu':
            if m.state == 'sleep':
                pass
            elif m.state == 'boss_idle':
                pass
            elif m.state == 'warp':
                pass
            elif m.state == 'attack':
                pass
            elif m.state == 'dying':
                pass
            elif m.state == 'die':
                pass

        m.count += 1
            
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

        elif m.type == 'tiktik':
            if m.count % 30 == 29:
                if m.state == 'idle':
                    m.x_frame = (m.x_frame + 1) % 4
                elif m.state == 'hit':
                    if not m.x_frame:
                        m.x_frame = (m.x_frame + 1) % 2
                elif m.state == 'dying':
                    m.x_frame = (m.x_frame + 1) % 5

    monster_init()

def intersect_hit_by_monster():
    global MONSTERS, PLAYER_RECT
    global player_state, x_frame, shake_countX, DashCount, FPressed, canPressF, teleport_type
    global player_full_hp, player_hp

    on = False

    for m in MONSTERS:
        if m.btop > PLAYER_RECT.bottom and PLAYER_RECT.top > m.bbottom and m.bleft < PLAYER_RECT.right and PLAYER_RECT.left < m.bright \
          and player_state != 2 \
          and not (10 <= DashCount <= 30): # 맞고 더블로 맞지 않게
          if (m.state == 'alert' or m.state == 'alert_turn' or m.state == 'idle' or m.state == 'turn' or m.state == 'thorn'):
            stop_screen(200)
            player_state = 2
            break_hp(player_hp)
            if shake_countX == 0: shake_countX = 6
          elif (m.state == 'teleport') or (m.state == 'on'):
            canPressF = True
            on = True
            if (m.state == 'teleport'):
                if FPressed:
                    teleport_type = 'boss'
                    player_state = 3
                    stop_screen(300)
            elif (m.state == 'on'):
                if FPressed:
                    m.state = 'off'
                    player_full_hp += 1
                    player_hp += 1
    
    if not on:
        canPressF = False
            
def intersect_hit_by_boss():
    pass

def hit_god_count():
    global player_state, hit_count
    if player_state == 2:
        hit_count += 1
        if hit_count == 240:
            player_state = 0
            hit_count = 0

def stop_screen(t):
    global stop_count, if_stop_screen, stop_count_limit
    if_stop_screen = True
    stop_count_limit = t

def stop_screen_count():
    global stop_count, if_stop_screen, stop_count_limit
    global player_state, penable_dark

    if stop_count_limit > 0:
        stop_count += 1
        if stop_count == stop_count_limit:
            stop_count = 0
            if_stop_screen = False
            stop_count_limit = 0
            if player_state == 3:
                penable_dark = True

def handle_events():
    global JumpKeyPressed, JumpHeight, JumpPower, JumpTime, player_on_block_num, is_falling
    global running
    global JumpAgain
    global y, block_y, show_blocks
    global LeftKeyPressed, RightKeyPressed, MoveCount, MoveTime
    global hero_heading_right, hero_heading_left, x_frame
    global UpKeyPressed, DownKeyPressed, player_state
    global shake_countY, shake_countX
    global StageNum, player_move_y, boss_stage_jump_value
    global DashCount, PlayDashAnime, DashCoolTime, FPressed, warp_effect

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False
            exit(0)

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_SPACE:
                if StageNum == 1:
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

                elif StageNum == 2:
                    if (JumpKeyPressed == False):
                        JumpKeyPressed = True
                        player_on_block_num = -1

                    elif (JumpKeyPressed == True and JumpAgain == False):
                        JumpAgain = True
                        is_falling = False
                        player_move_y -= boss_stage_jump_value
                        JumpTime = 0
                        boss_stage_jump_value = 0
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

            elif event.key == SDLK_LSHIFT:
                if DashCoolTime <= 0:
                    DashCount = 33
                    if MoveCount > 60:
                        PlayDashAnime = True

            elif event.key == SDLK_f:
                FPressed = True
            elif event.key == SDLK_a:
                use_hp_gage()
            elif event.key == SDLK_8:
                if not warp_effect.show:
                    boss_warp_effect(int(PLAYER_START_X), int(PLAYER_START_X))

# ----------------------- shake test ---------------------------

            # elif event.key == SDLK_h:
            #     if shake_countY == 0: shake_countY = 6

            # elif event.key == SDLK_y:
            #     if shake_countY == 0: shake_countY = -6

            # elif event.key == SDLK_k:
            #     if shake_countX == 0: shake_countX = 6

            # elif event.key == SDLK_i:
            #     if shake_countX == 0: shake_countX = -6
            

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
            elif event.key == SDLK_f:
                FPressed = False

def collision_repair(i):
    global y, block_y, BLOCKS, PLAYER_RECT

    blocks_init()
    if collision_check(BLOCKS[i], PLAYER_RECT):
        y += 5
        block_y -= 5
        collision_repair(i)
    else:
        return

def collision_repair_bottom(i):
    global y, block_y, BLOCKS, PLAYER_RECT

    blocks_init()
    if collision_check(BLOCKS[i], PLAYER_RECT):
        y -= 5
        block_y += 5
        collision_repair_bottom(i)
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

def animation_count():
    global count, x_frame, y_frame, player_state, hero_heading_left, hero_heading_right
    global LeftKeyPressed, RightKeyPressed, is_falling
    global attack_anime_count, attack_dir
    global hp_x_frame, hp_to_break, DashCount

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
        if hp_x_frame == 2:
            hp_x_frame = 3
            hp_to_break = -1
        elif hp_x_frame == 3:
            hp_x_frame = 0
        else:
            hp_x_frame += 1

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
                
            if RightKeyPressed != 0: # moving, right
                y_frame = 15
                x_frame = (x_frame + 1) % 9
            else: # idle, right
                y_frame = 15
                x_frame = 0
            
        elif hero_heading_left: # 14 13 12 11 10 9 8 7 6
                                # x_frame은 왼쪽으로 전환할 때 초기화
            
            if LeftKeyPressed != 0: # moving, left
                y_frame = 15
                x_frame -= 1
                if (7 <= x_frame and x_frame <= 15) == False:
                    x_frame = 15
                if x_frame == 6:
                    x_frame = 15
            else: # idle, left
                y_frame = 15
                x_frame = 15

        count = 0

def init_image():
    global white_rect, hero_right, hero_left, ex_map, ex_block
    global fly_idle, fly_chase, fly_die, fly_turn_left, fly_shock
    global tiktik_idle, tiktik_dying, tiktik_stun
    global hp_o, hp_x, hit_effect_image, hp_breaking
    global hero_right_hit, hero_left_hit
    global hero_left_40, hero_left_70, hero_right_40, hero_right_70
    global item, hp_gage, hp_gage_frame, warp_image

    white_rect = load_image('resources/white_rect.png')
    hero_right = load_image('resources/knight_hero_right.png')
    hero_left = load_image('resources/knight_hero_left.png')

    hero_right_hit = load_image('resources/knight_hero_right_hit.png')
    hero_left_hit = load_image('resources/knight_hero_left_hit.png')

    hero_left_40 = load_image('resources/knight_hero_left_40.png')
    hero_left_70 = load_image('resources/knight_hero_left_70.png')

    hero_right_40 = load_image('resources/knight_hero_right_40.png')
    hero_right_70 = load_image('resources/knight_hero_right_70.png')

    ex_map = load_image('resources/map_ex.png')
    ex_block = load_image('resources/first_map.png')

    fly_idle = load_image('resources/monsters/fly_idle.png')
    fly_shock = load_image('resources/monsters/fly_shock.png')
    fly_chase = load_image('resources/monsters/fly_chase.png')
    fly_die = load_image('resources/monsters/fly_die.png')
    fly_turn_left = load_image('resources/monsters/fly_turn_left.png')

    tiktik_idle = load_image('resources/monsters/tiktik_walk_right.png')
    tiktik_stun = load_image('resources/monsters/tiktik_stun_right.png')
    tiktik_dying = load_image('resources/monsters/tiktik_dying_right.png')

    hp_o = load_image('resources/hp_o.png')
    hp_x = load_image('resources/hp_x.png')
    hp_breaking = load_image('resources/hp_breaking.png')
    hit_effect_image = load_image('resources/hit_effect_left.png')

    item = load_image('resources/heart.png')
    hp_gage = load_image('resources/hp_gage.png')
    hp_gage_frame = load_image('resources/hp_gage_frame.png')

    warp_image = load_image('resources/monsters/boss_warp.png')

def draw_player():
    # hero? 128x128
        # 캐릭터 크기 100
    global player_state, attack_dir, x_frame, y_frame, player_x, PlayerMoveDistance, player_y
    global X_MOVE_POWER, hero_right, hero_left, hero_heading_right, hero_heading_left
    global boss_stage_jump_value, PlayDashAnime, DashCount
    global hero_left_40, hero_left_70, hero_right_40, hero_right_70

    if player_state == 1: # Attack
        
        # 플레이어
        if attack_dir == 2 or attack_dir == -2 or attack_dir == 1: # up
            hero_right.clip_draw(128 * x_frame, 128 * y_frame, 128, 128,   # right로 통일.
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)
        elif attack_dir == -1 or attack_dir == 3:
            hero_left.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)

        # x_frame 6개. # 3, 13
        # 검기
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

    elif PlayDashAnime:
        y_frame = 11
        if hero_heading_right == 1:
            if DashCount <= 0:
                PlayDashAnime = False
            elif 0 < DashCount < 3:
                x_frame = 0
            elif 3 <= DashCount < 6:
                x_frame = 1
            elif 6 <= DashCount < 9:
                x_frame = 2
            elif 9 <= DashCount < 12:
                x_frame = 3
            elif 12 <= DashCount < 15:
                x_frame = 4
            elif 15 <= DashCount < 18:
                x_frame = 5
            elif 18 <= DashCount < 21:
                x_frame = 4
            elif 21 <= DashCount < 24:
                x_frame = 3
            elif 24 <= DashCount < 27:
                x_frame = 2
            elif 27 <= DashCount < 30:
                x_frame = 1
            elif 30 <= DashCount < 33:
                x_frame = 0


            hero_right_40.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) - 16, 200 + player_y, 100, 100)

            hero_right_70.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) - 8, 200 + player_y, 100, 100)

            hero_right.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)

        elif hero_heading_left == 1:
            if DashCount <= 0:
                PlayDashAnime = False
            elif 0 < DashCount < 3:
                x_frame = 15
            elif 3 <= DashCount < 6:
                x_frame = 14
            elif 6 <= DashCount < 9:
                x_frame = 13
            elif 9 <= DashCount < 12:
                x_frame = 12
            elif 12 <= DashCount < 15:
                x_frame = 11
            elif 15 <= DashCount < 18:
                x_frame = 10
            elif 18 <= DashCount < 21:
                x_frame = 11
            elif 21 <= DashCount < 24:
                x_frame = 12
            elif 24 <= DashCount < 27:
                x_frame = 13
            elif 27 <= DashCount < 30:
                x_frame = 14
            elif 30 <= DashCount < 33:
                x_frame = 15

            hero_left_40.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) + 16, 200 + player_y, 100, 100)

            hero_left_70.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)) + 8, 200 + player_y, 100, 100)

            hero_left.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)

    elif player_state == 0: # idle 상태라면, 
        if hero_heading_right == 1:
            hero_right.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 - boss_stage_jump_value + player_y, 100, 100)
        elif hero_heading_left == 1:
            hero_left.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 - boss_stage_jump_value + player_y, 100, 100)

    elif player_state == 2: # hit by monsters
        if hero_heading_right == 1:
            hero_right_hit.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)
        elif hero_heading_left == 1:
            hero_left_hit.clip_draw(128 * x_frame, 128 * y_frame, 128, 128, 
            640 - (int(player_x - PlayerMoveDistance) // (X_MOVE_POWER / 2)), 200 + player_y, 100, 100)

def draw_monster():
    global MONSTERS
    global fly_chase, fly_die, fly_turn_left, fly_idle, fly_shock
    global tiktik_idle, tiktik_dying, tiktik_stun
    global item

    for m in MONSTERS:
        # draw_rectangle(int(m.bleft), int(m.bbottom), int(m.bright), int(m.btop))
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

        elif m.type == 'tiktik':
            if m.state == 'idle': # 4 frame
                if m.dir == 1:
                    tiktik_idle.clip_draw(tiktik_idle.w // 4 * m.x_frame, 0, tiktik_idle.w // 4, tiktik_idle.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                if m.dir == -1: 
                    tiktik_idle.clip_composite_draw(tiktik_idle.w // 4 * m.x_frame, 0, tiktik_idle.w // 4, tiktik_idle.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)

            elif m.state == 'hit': # 2 frame
                if m.dir == 1:
                    tiktik_stun.clip_draw(tiktik_stun.w // 2 * m.x_frame, 0, tiktik_stun.w // 2, tiktik_stun.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                if m.dir == -1:
                    tiktik_stun.clip_composite_draw(tiktik_stun.w // 2 * m.x_frame, 0, tiktik_stun.w // 2, tiktik_stun.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)

            elif m.state == 'dying': # 5 frame
                if m.dir == 1:
                    tiktik_dying.clip_draw(tiktik_dying.w // 5 * m.x_frame, 0, tiktik_dying.w // 5, tiktik_dying.h,
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)
                if m.dir == -1:
                    tiktik_dying.clip_composite_draw(tiktik_dying.w // 5 * m.x_frame, 0, tiktik_dying.w // 5, tiktik_dying.h, 0, 'h',
                            int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)

        elif m.type == 'item' and m.state == 'on':
            item.draw(int(m.left) + (m.width // 2), int(m.bottom) + (m.height // 2), m.width, m.height)

def draw_hp():
    global player_hp, player_full_hp
    global hp_o, hp_x

    for i in range(0, player_hp):
            hp_o.draw(35 * i + 198, 580, int(hp_o.w * 0.7), int(hp_o.h*0.7))
    for i in range(player_hp, player_full_hp):
            hp_x.draw(35 * i + 198, 580, int(hp_x.w * 0.7), int(hp_x.h*0.7))

def draw_hp_gage():
    global hp_gage, hp_gage_frame, player_hp_gage

    #hp_gage_frame.draw_to_origin(50, 530, hp_gage_frame.w, hp_gage_frame.h)
    hp_gage_frame.clip_composite_draw(0, 0, hp_gage_frame.w, hp_gage_frame.h, 0, 'h', 
                                      50 + (hp_gage_frame.w // 2) - 22, 530 + (hp_gage_frame.h // 2), hp_gage_frame.w, hp_gage_frame.h)
    hp_gage.clip_draw_to_origin(0, 0, hp_gage.w, (hp_gage.h // 10) * player_hp_gage, 50 + 2, 530 + 13, 
                                      hp_gage.w, hp_gage.h - (hp_gage.h // 10) * (10 - player_hp_gage))

def use_hp_gage():
    global player_hp_gage, player_hp, player_full_hp

    if player_hp_gage >= 5 and player_hp < player_full_hp:
        player_hp_gage -= 5
        player_hp += 1

def break_hp(hp):
    global hp_to_break, player_hp, player_state, hp_x_frame, teleport_type
    
    if player_hp - 1 <= 0:
        player_state = 3
        teleport_type = 'start'
        stop_screen(300)
        return
    
    hp_to_break = hp
    player_hp -= 1
    hp_x_frame = 3

def draw_breaking_hp():
    global player_hp, player_full_hp
    global hp_breaking, hp_x_frame
    global hp_to_break

    if hp_to_break >= 0:
        hp_breaking.clip_draw_to_origin(hp_breaking.w // 4 * hp_x_frame, 0, hp_breaking.w // 4, hp_breaking.h,
                                        35 * (hp_to_break) + 145, 580 - 30, 35, 65)

def draw_f_button():
    global canPressF, play_font, PLAYER_RECT
    if canPressF:
        play_font.draw(PLAYER_RECT.left + 40 + 1, PLAYER_RECT.top + 1, 'F', (0, 0, 0))
        play_font.draw(PLAYER_RECT.left + 40, PLAYER_RECT.top, 'F', (255, 255, 255))

def Game_State():
    init_image()

    load_block()
    load_monster()

    blocks_init()
    monster_init()
    player_init()
    init_warp_effect()
    Fly()
    animation_count()
    init_dark_images()
    global penable_dark, if_stop_screen
    penable_dark = True

    running = True

    while running:
        clear_canvas()

        current_time = time.time()
        
        global frame_for
        for i in range(0, frame_for):

            # draw(Xpos for start, Ypos for start, WIDTH /none, HEIGHT /none)
            ex_block.clip_draw(int(x - MoveDistance) // X_MOVE_POWER, int(y - JumpHeight) // Y_MOVE_POWER, 640, 360, 640, 360, 1280, 720)

            draw_player()
            draw_monster()
            draw_hp()
            draw_breaking_hp()
            draw_attack_effect()
            draw_f_button()
            draw_hp_gage()
            draw_warp_effect()

            if show_blocks:
                draw_rectangle(PLAYER_RECT.left, PLAYER_RECT.top, PLAYER_RECT.right, PLAYER_RECT.bottom)
                for i in range(BLOCK_CNT):
                    draw_rectangle(BLOCKS[i].left, BLOCKS[i].bottom, BLOCKS[i].right, BLOCKS[i].top)

            pdark_animation()
            pdraw_dark()

            if if_stop_screen == False:
                handle_events()

                Fly()
                Move()
                Jump()
                Attack()

                blocks_init()
                player_init()
                update_effect()

                attack_effect_count()
                animation_count()
                intersect_hit_by_monster()
                intersect_hit_by_boss()
                hit_god_count()
                warp_effect_count()

            else:
                stop_screen_count()


        update_canvas()

        global frame_time
        frame_time = time.time() - current_time
        frame_rate = 1.0 / frame_time
        if frame_rate > 140:
            frame_for = 2
        elif frame_rate > 110:
            frame_for = 3
        elif frame_rate > 80:
            frame_for = 4
        else: frame_for = 5
        current_time += frame_time
        # print(f'Frame Time: {frame_time}, Frame Rate: {frame_rate}')

    close_canvas()

if __name__ == '__main__':
    open_canvas(1280, 720, sync=True)
    Game_State()
