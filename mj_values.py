from dataclasses import dataclass

X_MOVE_POWER = 3
Y_MOVE_POWER = 3

BLOCK_CNT = 3

x = 600.0
y = 100.0
diameter = 20.0

now_move_player_left = False
now_move_player_right = False

player_on_block_num = -1

block_x = 0.0
block_y = 0.0

player_x = 0

JumpTime = 0.0
JumpHeight = 0
JumpPower = 50.0

JumpKeyPressed = 0

JumpAgain = 0

MoveTime = 0.0
MoveDistance = 0
PlayerMoveDistance = 0
MovePower = 200.0
LeftKeyPressed = 0
RightKeyPressed = 0
MoveCount = 0

can_climb_left = False
can_climb_right = False