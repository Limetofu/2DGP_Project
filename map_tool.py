from pico2d import *

open_canvas(1280, 720)

# x, y = 0

with open("grid_data.txt", "r") as file:
    data = file.readlines()

def change_type(i, a):
    my_list = list(data[i])
    my_list[10] = '%d' % a
    new_data = ''.join(my_list)
    data[i] = new_data

file = open("grid_data.txt", "r")
    # 파일 열기. 뒤의 인자는 C와 동일
before_strings = file.readlines()
    # 개행 문자 포함, 리스트 형식 return
file.close()

class BLOCK:
    x: int
    y: int
    type: int

blocks = []
grid_data = []

# 개행 문자 제거
for i in before_strings:
    tmp_str = i.replace('\n', '')
    grid_data.append(tmp_str)

# BLOCK 구조체 생성, 붙여넣기.
for i in range(0, 1000000):
    blocks.append(BLOCK())
    blocks[i].x = grid_data[i][0:4]
    blocks[i].y = grid_data[i][5:9]
    blocks[i].type = grid_data[i][10]

running = 1
left, top, right, bottom = 20, 20, 60, 60

def handle_events():
    global running
    global left, top
    global y

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            running = False

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_LEFT:
                left -= 40
            elif event.key == SDLK_RIGHT:
                left += 40
            elif event.key == SDLK_UP:
                top += 40
            elif event.key == SDLK_DOWN:
                top -= 40
            
            elif event.key == SDLK_0:
                pass
            elif event.key == SDLK_1:
                pass
            elif event.key == SDLK_2:
                pass
            elif event.key == SDLK_3:
                pass
                

block_0 = load_image('resources/black_rect.png')
block_1 = load_image('resources/white_rect.png')

for i in range(0, 1000000):
    xpos = int(blocks[i].x) * 40 + 20
    ypos = int(blocks[i].y) * 40 + 20
    block_1.draw(xpos, ypos, 40, 40)


while running:
    clear_canvas()

    block_0.draw(left, top, 40, 40)
    update_canvas()
    handle_events()

with open('grid_data.txt', 'w') as file:
    file.writelines(data)

close_canvas()


'''
    class BLOCK:
        x: int
        y: int
        type: int

    blocks = []
    grid_data = []

    file = open("grid_data.txt", "r")
        # 파일 열기. 뒤의 인자는 C와 동일
    before_strings = file.readlines()
        # 개행 문자 포함, 리스트 형식 return
    file.close()

    # 개행 문자 제거
    for i in before_strings:
        tmp_str = i.replace('\n', '')
        grid_data.append(tmp_str)

    # BLOCK 구조체 생성, 붙여넣기.
    for i in range(0, 1000000):
        blocks.append(BLOCK())
        blocks[i].x = grid_data[i][0:4]
        blocks[i].y = grid_data[i][5:9]
        blocks[i].type = grid_data[i][10]
'''