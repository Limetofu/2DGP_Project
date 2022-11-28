from dataclasses import dataclass

map_y_change = 3100
map_left_change = 500
map_left_change = 900

running = False

X_MOVE_POWER = 3
Y_MOVE_POWER = 3

stop_count = 0
if_stop_screen = False
stop_count_limit = 0

BLOCK_CNT = 0

x = 0.0
y = 3000.0 # 시작점

block_x = 0.0
block_y = -3000.0 # 시작점의 역수로 잡아야 블럭의 위치가 잡힘

diameter = 20.0

now_move_player_left = False
now_move_player_right = False

player_on_block_num = -1

entire_move_count = 0

player_x = 0
player_y = 0 # <--- y 변화량만. (아래 바라보거나 / 화면 흔들리는 이펙트)

player_full_hp = 5
player_hp = 5

JumpHeight = 0
JumpPower = 50.0
JumpTime = JumpPower // 2 + 1.0

RemainJumpTimeCount = 0

JumpKeyPressed = True
is_falling = True
JumpAgain = True


black_rect, white_rect, hero_right, hero_left, ex_map, ex_block = None, None, None, None, None, None
fly_idle, fly_chase, fly_die, fly_turn_left, fly_shock = None, None, None, None, None
hp_o, hp_x, hp_breaking = None, None, None
hp_x_frame = 0
hp_to_break = -1

hit_effect_image = None
hero_right_hit, hero_left_hit = None, None

shake_countY = 0
shake_countX = 0
shake_hit_count = 0
hit_effect = []
hit_count = 0

grid_data = []

MoveTime = 0.0
MoveDistance = 0
PlayerMoveDistance = 0
MovePower = 200.0
LeftKeyPressed = 0
RightKeyPressed = 0
UpKeyPressed, DownKeyPressed = 0, 0
MoveCount = 0

can_climb_left = False
can_climb_right = False

hero_heading_right = True
hero_heading_left = True

show_blocks = False

player_state = 0 
# 0 : idle, jump, move
# 1 : attack
# 2 : getting hit
# 3 : dying
# 4 : dead

attack_anime_frame = 55
attack_dir = 0

StageNum = 1

phun = []

penable_dark = True
pdark_anime_count = 0
pdark_count = 9
pdark_dir = -1


# ---------------------- menu --------------------------

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

# ---------------------- key guide --------------------------

key_running = False

key_image = None
esc_pressed = False

khun = []

kenable_dark = True
kdark_anime_count = 0
kdark_count = 9
kdark_dir = -1