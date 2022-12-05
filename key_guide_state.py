from mj_values import *
from pico2d import *
import menu_state

def init_image_key():
    global key_image
    key_image = load_image('resources/menu/key_guide.png')

    global khun
    if len(khun) == 0:
        khun.append(load_image('resources/menu/10.png'))
        khun.append(load_image('resources/menu/20.png'))
        khun.append(load_image('resources/menu/30.png'))
        khun.append(load_image('resources/menu/40.png'))
        khun.append(load_image('resources/menu/50.png'))
        khun.append(load_image('resources/menu/60.png'))
        khun.append(load_image('resources/menu/70.png'))
        khun.append(load_image('resources/menu/80.png'))
        khun.append(load_image('resources/menu/90.png'))
        khun.append(load_image('resources/menu/100.png'))

def draw_key_guide():
    global key_image
    key_image.draw_to_origin(0, 0, 1280, 720)


            
def kdark_animation():
    global kenable_dark, kdark_count, kdark_dir, kdark_anime_count, kdc

    if kenable_dark:
        kdark_anime_count += 1
        kdc += 1

        if kdark_anime_count % 4 == 3:
            if kdark_dir == 1:
                if kdark_count == 9:
                    kdark_dir *= -1
                    kdark_anime_count = 0
                    kenable_dark = False
                    kdc = 0
                else:
                    kdark_count += 1

            elif kdark_dir == -1:
                if kdark_count == 0:
                    kdark_dir *= -1
                    kdark_anime_count = 0
                    kenable_dark = False
                    kdc = 0
                else:
                    kdark_count -= 1
                
def kdraw_dark():
    global khun, kdark_count, kenable_dark

    if kdark_count >= 1:
        khun[kdark_count].draw_to_origin(0, 0, 1280, 720)

def handle_event():
    global esc_pressed
    global enable_dark, key_running

    Mevents = get_events()
    for event in Mevents:
        if event.type == SDL_QUIT:
            close_canvas()
            key_running = False

        elif event.type == SDL_KEYDOWN:

            if event.key == SDLK_RETURN:
                esc_pressed = True

def init_key_values():
    global key_running, key_image, esc_pressed, khun, kenable_dark
    global kdark_anime_count, kdark_count, kdark_dir
    global kdc
    kdc = 0

    key_image = None
    esc_pressed = False

    khun = []

    kenable_dark = True
    kdark_anime_count = 0
    kdark_count = 9
    kdark_dir = -1


kdc = 0

def Key_Guide_State():
    global key_running, enable_dark
    global esc_pressed
    global kdc, kenable_dark

    kenable_dark = True
    key_running = True

    init_key_values()
    init_image_key()

    while key_running:
        clear_canvas()
        draw_key_guide()

        kdark_animation()
        kdraw_dark()

        handle_event()

        update_canvas()

        if esc_pressed:
            kenable_dark = True
            if kdc >= 37:
                kdc = 0
                key_running = False
                esc_pressed = False
                menu_state.Title_Menu_State()

if __name__ == '__main__':
    open_canvas(1280, 720, sync=True)
    Key_Guide_State()