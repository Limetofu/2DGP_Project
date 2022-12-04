from mj_values import *
from pico2d import *
import play_state
import key_guide_state

def shake_screen(xvalue, yvalue):
    global menu_backgroundX, menu_backgroundY
    global shake_count_menuY, shake_count_menuX

    if yvalue != 0:
        if 1 <= shake_count_menuY: shake_count_menuY -= 1
        elif shake_count_menuY <= -1: shake_count_menuY += 1
    if xvalue != 0:
        if 1 <= shake_count_menuX: shake_count_menuX -= 1   
        elif shake_count_menuX <= -1: shake_count_menuX += 1

    menu_backgroundY -= yvalue * 2

def shake_anime_count():
    global shake_count_menuY, shake_count_menuX

    if   shake_count_menuY == 0:  pass

    elif shake_count_menuY == 3:  shake_screen(0,  7)
    elif shake_count_menuY == 2:  shake_screen(0,  -4)
    elif shake_count_menuY == 1:  shake_screen(0,  -3)

    elif shake_count_menuY == -3: shake_screen(0, -7)
    elif shake_count_menuY == -2: shake_screen(0,  4)
    elif shake_count_menuY == -1: shake_screen(0,  3)

def menu_animation_count():
    global menu_anime_count, menu_left_x_frame
    menu_anime_count += 1

    if menu_anime_count % 3 == 0:
        shake_anime_count()

    if menu_anime_count == 10:
        if menu_left_x_frame == 3:
            pass       
        else:
            menu_left_x_frame = (menu_left_x_frame + 1) % 4
        menu_anime_count = 0


def draw_menu():
    global menu_left, menu_num
    if menu_num == 1:
        menu_left.clip_draw(menu_left.w // 4 * menu_left_x_frame, 0, menu_left.w // 4, menu_left.h, 
                            120, 300 - 2, 29, 42)
        menu_left.clip_composite_draw(menu_left.w // 4 * menu_left_x_frame, 0, menu_left.w // 4, menu_left.h, 
                            0, 'h', 345, 300 - 2, 29, 42)

    elif menu_num == 2:
        menu_left.clip_draw(menu_left.w // 4 * menu_left_x_frame, 0, menu_left.w // 4, menu_left.h, 
                            120, 235 - 2, 29, 42)
        menu_left.clip_composite_draw(menu_left.w // 4 * menu_left_x_frame, 0, menu_left.w // 4, menu_left.h, 
                            0, 'h', 345, 235 - 2, 29, 42)

    elif menu_num == 3:
        menu_left.clip_draw(menu_left.w // 4 * menu_left_x_frame, 0, menu_left.w // 4, menu_left.h,
                            120, 170 - 2, 29, 42)
        menu_left.clip_composite_draw(menu_left.w // 4 * menu_left_x_frame, 0, menu_left.w // 4, menu_left.h, 
                            0, 'h', 345, 170 - 2, 29, 42)


def handle_event():
    global logo_running, shake_count_menuY, menu_num, menu_left_x_frame
    global enter_pressed

    global enable_dark

    Mevents = get_events()
    for event in Mevents:
        if event.type == SDL_QUIT:
            close_canvas()
            exit(0)

        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_DOWN:
                menu_left_x_frame = 0
                if shake_count_menuY == 0:
                    shake_count_menuY = 3

                if menu_num == 3:
                    menu_num = 1
                else:
                    menu_num += 1
            elif event.key == SDLK_UP:
                menu_left_x_frame = 0
                if shake_count_menuY == 0:
                    shake_count_menuY = -3

                if menu_num == 1:
                    menu_num = 3
                else:
                    menu_num -= 1

            elif event.key == SDLK_RETURN:
                enter_pressed = True
            
            elif event.key == SDLK_y:
                enable_dark = True

def dark_animation():
    global enable_dark, dark_count, dark_dir, dark_anime_count, dc

    if enable_dark:
        dark_anime_count += 1
        dc += 1

        if dark_anime_count % 4 == 3:
            if dark_dir == 1:
                if dark_count == 9:
                    dark_dir *= -1
                    dark_anime_count = 0
                    enable_dark = False
                    dc = 0
                else:
                    dark_count += 1

            elif dark_dir == -1:
                if dark_count == 0:
                    dark_dir *= -1
                    dark_anime_count = 0
                    enable_dark = False
                    dc = 0
                else:
                    dark_count -= 1
                
def draw_dark():
    global hun, dark_count, enable_dark

    if dark_count >= 1:
        hun[dark_count].draw_to_origin(0, 0, 1280, 720)

def draw_background():
    global menu_background, menu_backgroundX, menu_backgroundY
       # 16 : 9
    menu_background.clip_draw(menu_backgroundX, 20 + menu_backgroundY, 1800, 960, 640, 360, 1280, 720)

    global menu_logo
    menu_logo.draw_to_origin(50, 400, 600, 250)
    

def move_background():
    global menu_move_count, break_move_count, menu_backgroundX, menu_dir
    menu_move_count += 1

    if break_move_count != 0:
        break_move_count -= 1

    elif menu_move_count % 16 == 15:
        if menu_dir == 1: 
            if menu_backgroundX >= 50:
                break_move_count = 300
                menu_dir *= -1
            menu_backgroundX += 1
        elif menu_dir == -1: 
            if menu_backgroundX <= -50:
                break_move_count = 300
                menu_dir *= -1
            menu_backgroundX -= 1
        menu_move_count = 0


def draw_letters():
    global menu_font
    fontX = 150

    menu_font.draw(fontX + 2, 300,     'Game Start', (0, 0, 0))
    menu_font.draw(fontX + 2, 300 + 1, 'Game Start', (0, 0, 0))
    menu_font.draw(fontX,     300,     'Game Start', (255, 255, 255))

    menu_font.draw(fontX + 2 + 8, 235,     'Key Guide', (0, 0, 0))
    menu_font.draw(fontX + 2 + 8, 235 + 1, 'Key Guide', (0, 0, 0))
    menu_font.draw(fontX + 8,     235,     'Key Guide', (255, 255, 255))
    
    menu_font.draw(fontX + 2, 170,     'Quit Game', (0, 0, 0))
    menu_font.draw(fontX + 2, 170 + 1, 'Quit Game', (0, 0, 0))
    menu_font.draw(fontX,     170,     'Quit Game', (255, 255, 255))

def init_image_menu():
    global menu_font, menu_background, menu_left, menu_logo
    menu_font = load_font('resources/fonts/HeirofLightRegular.ttf', 30)
    menu_background = load_image('resources/menu/background.jpg')
    menu_left = load_image('resources/menu/menu_left.png')
    menu_logo = load_image('resources/menu/menu_title.png')

    global hun
    if len(hun) == 0:
        hun.append(load_image('resources/menu/10.png'))
        hun.append(load_image('resources/menu/20.png'))
        hun.append(load_image('resources/menu/30.png'))
        hun.append(load_image('resources/menu/40.png'))
        hun.append(load_image('resources/menu/50.png'))
        hun.append(load_image('resources/menu/60.png'))
        hun.append(load_image('resources/menu/70.png'))
        hun.append(load_image('resources/menu/80.png'))
        hun.append(load_image('resources/menu/90.png'))
        hun.append(load_image('resources/menu/100.png'))

def init_menu_values():
    global logo_running, menu_anime_count, shake_count_menuY, shake_count_menuX
    global menu_backgroundX, menu_backgroundY
    global menu_move_count, break_move_count, menu_dir
    global menu_left_x_frame, menu_num
    global enter_pressed, menu_font, menu_background, menu_left
    global hun, menu_logo, enable_dark, dark_anime_count, dark_dir, dark_count
    global dc
    dc = 0

    logo_running = True

    menu_anime_count = 0

    shake_count_menuY, shake_count_menuX = 0, 0
    menu_backgroundX, menu_backgroundY = 0, 0
    menu_move_count = 0
    break_move_count = 0
    menu_dir = 1

    menu_left_x_frame = 0

    menu_num = 1

    enter_pressed = False
    menu_font, menu_background, menu_left = None, None, None
    menu_logo = None

    hun = []

    enable_dark = True
    dark_anime_count = 0
    dark_count = 9
    dark_dir = -1

dc = 0

def Title_Menu_State():
    global logo_running, running, key_running
    global menu_font, menu_num
    global enable_dark, dc, enter_pressed

    logo_running = 1

    enable_dark = True

    init_menu_values()

    init_image_menu()
    while logo_running:

        clear_canvas()
        move_background()
        draw_background()
        draw_letters()
        draw_menu()
        dark_animation()
        draw_dark()

        handle_event()
        menu_animation_count()

        update_canvas()

        if enter_pressed:
            if (menu_num == 1):
                enable_dark = True
                if dc >= 37:
                    logo_running = False
                    dc = 0
                    enter_pressed = False
                    play_state.Game_State()

            elif (menu_num == 2):
                enable_dark = True
                if dc >= 37:
                    logo_running = False
                    dc = 0
                    enter_pressed = False
                    key_guide_state.Key_Guide_State()
                    quit()

            elif (menu_num == 3):
                close_canvas()
                exit(0)

if __name__ == '__main__':
    open_canvas(1280, 720, sync=True)
    Title_Menu_State()