# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# TBD

import copy

init_pos = [[1,2,3,4,5,3,2,1],
            [6,6,6,6,6,6,6,6],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [-6,-6,-6,-6,-6,-6,-6,-6],
            [-1,-2,-3,-4,-5,-3,-2,-1]]

current_pos = [[]]

def reset_board():
    global current_pos
    current_pos = copy.deepcopy(init_pos)

def flip_board():
    global current_pos
    current_pos = copy.deepcopy(current_pos[::-1])


reset_board()
print(current_pos)
flip_board()
print(current_pos)
