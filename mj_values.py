from dataclasses import dataclass

running = False
frame_time = 0.0
frame_for = 2

X_MOVE_POWER = 3
Y_MOVE_POWER = 3

# 시작점 좌표. 플레이어 스폰 용
PLAYER_START_X = 100.0
PLAYER_START_Y = 6400.0
START_BLOCK_X = -PLAYER_START_X
START_BLOCK_Y = -PLAYER_START_Y

BOSS_ROOM_X = 9350.0
BOSS_ROOM_Y = 5950.0

FRONT_BOSS_ROOM_X = 11600.0
FRONT_BOSS_ROOM_Y = 800.0

# 보스방 앞 좌표 만들어야 함
teleport_type = ''

stop_count = 0
if_stop_screen = False
stop_count_limit = 0

BLOCK_CNT = 0

x = PLAYER_START_X
y = PLAYER_START_Y # 시작점
# x = FRONT_BOSS_ROOM_X
# y = FRONT_BOSS_ROOM_Y

player_in_boss_stage = False

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

player_full_hp = 5
player_hp = 5

JumpHeight = 0
JumpPower = 50.0
JumpTime = JumpPower // 2 + 1.0

RemainJumpTimeCount = 0

JumpKeyPressed = True
is_falling = True
JumpAgain = True

MONSTER_CNT, monster_data = 0, []

play_font = None
black_rect, white_rect, hero_right, hero_left, ex_map, ex_block = None, None, None, None, None, None
hero_left_70, hero_left_40, hero_right_70, hero_right_40 = None, None, None, None
fly_idle, fly_chase, fly_die, fly_turn_left, fly_shock = None, None, None, None, None
tiktik_idle, tiktik_dying, tiktik_stun = None, None, None
item = None
hp_gage, hp_gage_frame = None, None
warp_image = None
boss_idle, boss_pattern_idle, boss_attack = None, None, None
boss_pattern_attack = None

warped = False
pattern_num = 0

# 0 ~ 14번까지 있음
boss_pattern_list = \
[[],
 [0, 1, 2, 4, 6, 7, 8, 10, 12, 13, 14],
 [],
 [1, 2, 4, 5, 7, 8, 9, 11, 13, 14], 
 [1, 3, 5, 6, 7, 9, 10, 11, 12, 14], []]


sound_boss_attack = []
sound_dash, sound_jump, sound_hit, sound_attack, sound_walk, sound_land = None, None, None, None, None, None
sound_boss_die = None, None
sound_attack_hit, sound_item_eat = None, None
sound_pattern_appear = None
sound_pattern_impact = None
sound_map_change = None
sound_a = None

player_hp_gage = 7

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

DashCount = 0
PlayDashAnime = False
DashCoolTime = False

can_climb_left = False
can_climb_right = False

hero_heading_right = True
hero_heading_left = True

show_blocks = False

player_state = 0 
# 0 : idle, jump, move
# 1 : attack
# 2 : getting hit
# 3 : die

attack_anime_frame = 55
attack_dir = 0

StageNum = 1
boss_stage_jump_value = 0

phun = []

penable_dark = True
pdark_anime_count = 0
pdark_count = 9
pdark_dir = -1

pdc = 0
FPressed = False
canPressF = False
canQuitGame = False

# ---------------------- menu --------------------------
bgm_menu = None
i_change, ui_select = None, None
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