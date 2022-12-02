from pico2d import *
from mj_values import * 

open_canvas(1280, 720)

# 데이터? 
# left, bottom, width, height
# 키보드로 이동 후
# left, bottom 위치에 가서  번호 키 (Type)
# 좌우상하로 이동, 이동하는 만큼 width, height 추가.
# 엔터 누르면 블럭 생성.

# 생성중인 블럭은 파란색 출력
# 생성된 블럭은 흰색 출력
# txt 파일에서

class BLOCK:
    left: int
    bottom: int
    width: int
    height: int
    type: int
    
blocks = []
grid_data = []


map_x, map_y = 0, 0



with open("grid_data.txt", "r") as file:
    data = file.readlines()

BLOCK_CNT, ORIGINAL_BLOCK_CNT = len(data), len(data)

file.close()


def change_type(i, a):
    my_list = list(data[i])
    my_list[24] = '%d' % a
    new_data = ''.join(my_list)
    data[i] = new_data

# 개행 문자 제거
for i in data:
    tmp_str = i.replace('\n', '\n')
    grid_data.append(tmp_str)

# BLOCK 구조체 생성, 붙여넣기.
for i in range(BLOCK_CNT):
    blocks.append(BLOCK())
    blocks[i].left = int(grid_data[i][0:6]) # 중간에 | 들어감.
    blocks[i].bottom = int(grid_data[i][7:13])
    blocks[i].width = int(grid_data[i][14:18])
    blocks[i].height = int(grid_data[i][19:23])
    blocks[i].type = int(grid_data[i][24])

running = True
left, bottom = 20, 20
pxdir, pydir = 0, 0
mdir = 0
draw_blue = 0
blue_left = 0
blue_bottom = 0
blue_right = 0
blue_top = 0
blue_type = 0
shift_pressed = False

def handle_events():
    global running, shift_pressed
    global left, bottom
    global pxdir, pydir, mdir
    global draw_blue, blue_left, blue_bottom, blue_right, blue_top, blue_type
    global BLOCK_CNT, blocks

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_DELETE:
                running = False
            elif event.key == SDLK_LSHIFT:
                shift_pressed = True

            # 포인터 옮기기
            elif event.key == SDLK_UP:
                pydir = 1
            elif event.key == SDLK_DOWN:
                pydir = 2
            elif event.key == SDLK_LEFT:
                pxdir = 1
            elif event.key == SDLK_RIGHT:
                pxdir = 2
            

            # 맵 옮기기
            elif event.key == SDLK_w:
                mdir = 1
            elif event.key == SDLK_a:
                mdir = 3
            elif event.key == SDLK_s:
                mdir = 2
            elif event.key == SDLK_d:
                mdir = 4
            
            # draw_blue를 켜고, 
            # 현재의 left, bottom 값을 다른 변수에 임시 저장.

            elif event.key == SDLK_1: # 기본 블럭
                if draw_blue == True:
                    draw_blue = False
                    return
                draw_blue = True
                blue_left = left
                blue_bottom = bottom
                blue_type = 1
            elif event.key == SDLK_2: # 함정
                if draw_blue == True:
                    draw_blue = False
                    return
                draw_blue = True
                blue_left = left
                blue_bottom = bottom
                blue_type = 2
            elif event.key == SDLK_3:
                if draw_blue == True:
                    draw_blue = False
                    return
                draw_blue = True
                blue_left = left
                blue_bottom = bottom
                blue_type = 3
            elif event.key == SDLK_4:
                if draw_blue == True:
                    draw_blue = False
                    return
                draw_blue = True
                blue_left = left
                blue_bottom = bottom
                blue_type = 4


        elif event.type == SDL_KEYUP:
            if event.key == SDLK_LSHIFT:
                shift_pressed = False
            elif event.key == SDLK_LEFT or event.key == SDLK_RIGHT:
                pxdir = 0
            elif event.key == SDLK_UP or event.key == SDLK_DOWN:
                pydir = 0
            elif event.key == SDLK_w or event.key == SDLK_s or event.key == SDLK_a or event.key == SDLK_d:
                mdir = 0
            elif event.key == SDLK_RETURN:
                if draw_blue == True:
                    draw_blue = 0
                    blue_right = left + 40 - blue_left
                    blue_top = bottom + 40 - blue_bottom
                    blocks.append(BLOCK())
                    blocks[BLOCK_CNT].left = blue_left
                    blocks[BLOCK_CNT].bottom = blue_bottom
                    blocks[BLOCK_CNT].width = blue_right
                    blocks[BLOCK_CNT].height = blue_top
                    blocks[BLOCK_CNT].type = blue_type

                    BLOCK_CNT += 1
                # 데이터 추가해주기
                # 블럭에만 추가해주면 됨

                # 맵을 옮긴 만큼,
                # 값을 추가해주어야 함


def move_pointer():
    global pxdir, pydir, left, bottom

    move_value = 2
    if shift_pressed == True:
        move_value = 2
    else:
        move_value = 1

    if pydir == 1:
        bottom += move_value
    elif pydir == 2:
        bottom -= move_value
    
    if pxdir == 1:
        left -= move_value
    elif pxdir == 2:
        left += move_value

def move_map():
    global mdir, map_x, map_y, map_image
    global blue_left, blue_bottom
    global shift_pressed

    move_value = 2
    if shift_pressed == True:
        move_value = 2
    else:
        move_value = 1

    if mdir == 1: # 상
        if (map_image.h - 360 <= map_y) == 0:
            map_y += move_value
            move_block(mdir)
            blue_bottom -= move_value * 2
    elif mdir == 2: # 하
        if (0 >= map_y) == 0:
            map_y -= move_value
            move_block(mdir)
            blue_bottom += move_value * 2
    elif mdir == 3: # 좌
        if (0 >= map_x) == 0:
            map_x -= move_value
            move_block(mdir)
            blue_left += move_value * 2
    elif mdir == 4: # 우
        if (map_image.w - 640 <= map_x) == 0:
            map_x += move_value
            move_block(mdir)
            blue_left -= move_value * 2

def move_block(dir):
    global blocks
    global BLOCK_CNT
    global shift_pressed

    move_value = 2
    if shift_pressed == True:
        move_value = 2
    else:
        move_value = 1

    for i in range(BLOCK_CNT):
        if dir == 1:
            blocks[i].bottom -= move_value * 2
            
        elif dir == 2:
            blocks[i].bottom += move_value * 2
            
        elif dir == 3:
            blocks[i].left += move_value * 2
            
        elif dir == 4:
            blocks[i].left -= move_value * 2
           

block_black = load_image('resources/black_rect.png')
block_white = load_image('resources/white_rect.png')
block_blue = load_image('resources/blue_rect.png')

map_image = load_image('resources/first_map.png')


while running:
    clear_canvas()

    map_image.clip_draw(map_x, map_y, 640, 360, 640, 360, 1280, 720)

    # block_white.draw(left, bottom, 40, 40)


    # 불러온 데이터만큼
    # 이미지 그리기
    for i in range(BLOCK_CNT):
        if blocks[i].type == 1:
            block_blue.draw(blocks[i].left + (blocks[i].width // 2), blocks[i].bottom + (blocks[i].height // 2), blocks[i].width, blocks[i].height)
        elif blocks[i].type == 2:
            block_white.draw(blocks[i].left + (blocks[i].width // 2), blocks[i].bottom + (blocks[i].height // 2), blocks[i].width, blocks[i].height)
        elif blocks[i].type == 3:
            block_black.draw(blocks[i].left + (blocks[i].width // 2), blocks[i].bottom + (blocks[i].height // 2), blocks[i].width, blocks[i].height)
        
        draw_rectangle(blocks[i].left, blocks[i].bottom, blocks[i].left + blocks[i].width, blocks[i].bottom + blocks[i].height)
    
    if draw_blue:
        draw_rectangle(blue_left, blue_bottom, left + 40, bottom + 40)
    
    # draw cursor
    draw_rectangle(left, bottom, left + 40, bottom + 40)
    
    update_canvas()
    handle_events()
    move_pointer()
    move_map()



# 파일에다 다시 붙여넣기.
# grid_data에다가 다시 넣어줘야 함.
# for i in range(0, ORIGINAL_BLOCK_CNT):
#     grid_data.

# grid_data.append("\n")
for i in range(ORIGINAL_BLOCK_CNT, BLOCK_CNT):
    grid_data.append("%6d|%6d|%4d|%4d|%d\n" % (blocks[i].left + (map_x * 2), blocks[i].bottom + (map_y * 2), blocks[i].width, blocks[i].height, blocks[i].type))

with open('grid_data.txt', 'w') as file:
    file.writelines(grid_data)




close_canvas()