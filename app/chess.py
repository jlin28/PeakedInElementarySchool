# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# TBD

import copy

# 1 = rook, 2 = knight, 3 = bishop, 4 = queen, 5 = king, 6 = pawn, 0 = empty, negative = black pieces
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

# prerequisite: r, c on board
def is_legal_square(board, r, c, color):
    target = board[r][c]
    if target == 0:  # empty
        return True
    elif get_color(target) != color:  # capture square
        return True
    return False

# returns True if the square is attacked by any piece, tracking color
def is_square_attacked(board, r, c, by_color):
    # Loop through all enemy pieces
    for rr in range(8):
        for cc in range(8):
            piece = board[rr][cc]
            if piece == 0:
                continue
            if get_color(piece) != by_color:
                continue  # skip non-enemy pieces

            ptype = abs(piece)

            # Knights
            if ptype == 2:
                for dr, dc in [(2,1),(1,2),(-2,1),(-1,2),(2,-1),(1,-2),(-2,-1),(-1,-2)]:
                    if rr+dr == r and cc+dc == c:
                        return True

            # Pawns
            if ptype == 6:
                direction = -1 if by_color == "white" else 1
                for dc in (-1, 1):
                    if rr + direction == r and cc + dc == c:
                        return True

            # King
            if ptype == 5:
                for dr in (-1,0,1):
                    for dc in (-1,0,1):
                        if dr == 0 and dc == 0:
                            continue
                        if rr+dr == r and cc+dc == c:
                            return True

            # Sliding pieces: rook, bishop, queen
            if ptype in (1, 3, 4):
                if attacks_by_slider(board, rr, cc, r, c, ptype):
                    return True
    return False


# if rook/bishop/queen at (rr,cc) attacks target (tr,tc)
def attacks_by_slider(board, rr, cc, tr, tc, ptype):
    directions = []
    if ptype in (1,4):  # rook or queen
        directions += [(1,0),(-1,0),(0,1),(0,-1)]
    if ptype in (3,4):  # bishop or queen
        directions += [(1,1),(1,-1),(-1,1),(-1,-1)]

    for dr, dc in directions:
        r, c = rr + dr, cc + dc
        while on_board(r, c):
            if r == tr and c == tc:
                return True
            if board[r][c] != 0:
                break
            r += dr
            c += dc
    return False

def rook_moves(board, r, c, color):
    moves = []
    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            if is_legal_square(board, nr, nc, color):
                moves.append((nr, nc))
            if board[nr, nc] != 0:
                break  # stop sliding when hitting any piece
            nr += dr
            nc += dc
    return moves

def knight_moves(board, r, c, color):
    moves = []
    directions = [(2, 1), (1, 2), (-2,1), (-1, 2), (-2, -1), (-1, -2), (2, -1), (1, -2)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if on_board(nr, nc):
            if is_legal_square(board, nr, nc, color):
                moves.append((nr, nc))
    return moves

def bishop_moves(board, r, c, color):
    moves = []
    directions = [(1,1), (-1, 1), (-1,-1), (1,-1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            if is_legal_square(board, nr, nc, color):
                moves.append((nr, nc))
            if board[nr, nc] != 0:
                break  # stop sliding when hitting any piece
            nr += dr
            nc += dc
    return moves

def queen_moves(board, r, c, color):
    moves = []
    directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1, 1), (-1,-1), (1,-1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            if is_legal_square(board, nr, nc, color):
                moves.append((nr, nc))
            if board[nr, nc] != 0:
                break  # stop sliding when hitting any piece
            nr += dr
            nc += dc
    return moves

def king_moves(board, r, c, color):
    moves = []
    if color == "white":
        enemy = "black"
    else:
        enemy = "white"

    directions = [(1,0), (-1,0), (0,1), (0,-1),
                  (1,1), (-1,1), (-1,-1), (1,-1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if not on_board(nr, nc):
            continue

        if not is_legal_square(board, nr, nc, color):
            continue

        # do not move into an attacked square
        if is_square_attacked(board, nr, nc, enemy):
            continue

        moves.append((nr, nc))
    return moves

def pawn_moves(board, r, c, color):
    moves = []

    direction = -1 if color == "white" else 1   # white moves upward (r decreases)

    start_row = 6 if color == "white" else 1
    enemy_color = "black" if color == "white" else "white"

    # 1. Forward move (one square)
    nr = r + direction
    if on_board(nr, c) and board[nr][c] == 0:
        moves.append((nr, c))

        # 2. Two squares from starting position
        nr2 = r + 2*direction
        if r == start_row and board[nr2][c] == 0:
            moves.append((nr2, c))

    # 3. Captures (diagonals)
    for dc in (-1, 1):
        nc = c + dc
        nr = r + direction
        if on_board(nr, nc):
            target = board[nr][nc]
            if target != 0 and get_color(target) == enemy_color:
                moves.append((nr, nc))

    return moves
