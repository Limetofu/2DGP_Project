from dataclasses import dataclass

X_MOVE_POWER = 3
Y_MOVE_POWER = 3

BLOCK_CNT = 0

x = 0.0
y = 3000.0 # 시작점

block_x = 0.0
block_y = -3000.0 # 시작점의 역수로 잡아야 블럭의 위치가 잡힘

diameter = 20.0

now_move_player_left = False
now_move_player_right = False

player_on_block_num = -1



player_x = 0

JumpTime = 26.0
JumpHeight = 0
JumpPower = 50.0

JumpKeyPressed = True
is_falling = True
JumpAgain = True

grid_data = []

MoveTime = 0.0
MoveDistance = 0
PlayerMoveDistance = 0
MovePower = 200.0
LeftKeyPressed = 0
RightKeyPressed = 0
MoveCount = 0

can_climb_left = False
can_climb_right = False

hero_heading_right = True
hero_heading_left = True

show_blocks = False

player_state = 0