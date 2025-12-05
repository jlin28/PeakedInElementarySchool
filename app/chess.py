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

def legal_squares(board, r, c):
    piece = board[r][c]
    if piece == 0:
        return []

    piece_type = abs(piece)
    color = get_color(piece)

    if piece_type == 1:  # rook
        return rook_moves(board, r, c, color)
    elif piece_type == 2:  # knight
        return knight_moves(board, r, c, color)
    elif piece_type == 3:  # bishop
        return bishop_moves(board, r, c, color)
    elif piece_type == 4:  # queen
        return queen_moves(board, r, c, color)
    elif piece_type == 5:  # king
        return king_moves(board, r, c, color)
    elif piece_type == 6:  # pawn
        return pawn_moves(board, r, c, color)

def get_color(piece):
    if piece > 0:
        return "white"
    elif piece < 0:
        return "black"
    return None

def on_board(r, c):
    return 0 <= r < 8 and 0 <= c < 8

def rook_moves(board, r, c, color):
    moves = []
    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            target = board[nr][nc]
            if target == 0:  # empty
                moves.append((nr, nc))
            else:
                if get_color(target) != color:  # capture square
                    moves.append((nr, nc))
                break  # stop sliding when hitting any piece
            nr += dr
            nc += dc
    return moves