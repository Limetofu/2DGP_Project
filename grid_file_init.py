# grid data 초기화시키는 함수.

# xpos, ypos 순, 순차적으로 증가
# type은 0으로 통일 (air => 지나갈 수 있는 블럭)

# 블럭 필요한 데이터?
# 스테이지 / 순번 / left / bottom / right / top / type

file = open("grid_data.txt", "a")

for y in range(0, 1000):
    for x in range(0, 1000):
        grid_data = "%4d|%4d|0\n" % (x, y)
        file.write(grid_data)

file.close()