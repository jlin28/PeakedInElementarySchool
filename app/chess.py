# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# TBD

import copy

# 1 = rook, 2 = knight, 3 = bishop, 4 = queen, 5 = king, 6 = pawn, 0 = empty, negative = black pieces
init_pos = [[-1,-2,-3,-4,-5,-3,-2,-1],
            [-6,-6,-6,-6,-6,-6,-6,-6],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [6,6,6,6,6,6,6,6],
            [1,2,3,4,5,3,2,1]]

current_pos = [[]]

en_passant = None

def reset_board():
    global current_pos
    current_pos = copy.deepcopy(init_pos)

def flip_board():
    global current_pos
    new_board = []
    for r in range(7, -1, -1):
        new_row = []
        for c in range(7, -1, -1):
            new_row.append(current_pos[r][c])
        new_board.append(new_row)
    current_pos = new_board


def legal_squares(board, r, c):
    piece = board[r][c]
    if piece == 0:
        return []

    piece_type = abs(piece)
    color = get_color(piece)

    if piece_type == 1:
        moves = rook_moves(board, r, c, color)
    elif piece_type == 2:
        moves = knight_moves(board, r, c, color)
    elif piece_type == 3:
        moves = bishop_moves(board, r, c, color)
    elif piece_type == 4:
        moves = queen_moves(board, r, c, color)
    elif piece_type == 5:
        moves = king_moves(board, r, c, color)
    elif piece_type == 6:
        moves = pawn_moves(board, r, c, color)

    # filter based on checks/pins
    legal = []
    for nr, nc in moves:
        new_board, en_passant = simulate_move(board, r, c, nr, nc, en_passant)
        if not in_check(new_board, color):
            legal.append((nr, nc))

    return legal

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

            # Pawnsand en passant
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

def simulate_move(board, r1, c1, r2, c2, en_passant_state):
    piece = board[r1][c1]
    new_board = copy.deepcopy(board)
    new_en_passant = None  # gets reset every move unless replaced

    # En passant capture
    if en_passant_state is not None:
        target_r, target_c, pawn_r, pawn_c = en_passant_state
        if (r2, c2) == (target_r, target_c) and abs(piece) == 6:
            new_board[pawn_r][pawn_c] = 0  # remove captured pawn

    # Move piece normally
    new_board[r2][c2] = piece
    new_board[r1][c1] = 0

    # Check if new en passant state should be created
    if abs(piece) == 6 and abs(r2 - r1) == 2:
        passed_square = ((r1 + r2) // 2, c1)
        new_en_passant = (passed_square[0], passed_square[1], r2, c1)

    return new_board, new_en_passant

def in_check(board, color):
    if color == "white":
        enemy_color ="black"
    else:
        enemy_color = "white"
    king_r, king_c = 0, 0
    for i in range (len(board)):
        for j in range (len(board[0])):
            if abs(board[i][j]) == 5 and get_color(board[i][j]) == color:
                king_r, king_c = i, j
    if is_square_attacked(board, king_r, king_c, enemy_color):
        return True
    return False

def rook_moves(board, r, c, color):
    moves = []
    directions = [(1,0), (-1,0), (0,1), (0,-1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while on_board(nr, nc):
            if not is_legal_square(board, nr, nc, color):
                break

            moves.append((nr, nc))

            # Stop sliding if we hit a piece
            if board[nr][nc] != 0:
                break

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
            if board[nr][nc] != 0:
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
            if board[nr][nc] != 0:
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
    global en_passant
    moves = []

    direction = -1 if color == "white" else 1
    enemy_color = "black" if color == "white" else "white"
    start_row = 6 if color == "white" else 1

    # Forward move (one square)
    nr = r + direction
    if on_board(nr, c) and board[nr][c] == 0:
        moves.append((nr, c))

        # Two-square move
        nr2 = r + 2*direction
        if r == start_row and board[nr2][c] == 0:
            moves.append((nr2, c))

    # Normal captures
    for dc in (-1, 1):
        nc = c + dc
        nr = r + direction
        if on_board(nr, nc):
            target = board[nr][nc]
            if target != 0 and get_color(target) == enemy_color:
                moves.append((nr, nc))

    # En passant
    if en_passant is not None:
        target_r, target_c, pawn_r, pawn_c = en_passant

        # must be next to en-passantable pawn
        if pawn_r == r and abs(pawn_c - c) == 1:
            if target_r == r + direction and target_c == pawn_c:
                moves.append((target_r, target_c))


    return moves

def promotions(board):
    all_promotions = []
    for i in range(8):
        if board[0][i] == 6:
            all_promotions.append((0, i, (-4, -1, -3, -2))) # in order: queen, rook, bishop, knight
        if board[7][i] == -6:
            all_promotions.append((7, i, (4, 1, 3, 2)))
    return all_promotions

# Testing

current_pos = [[-1,-2,-3,-4,-5,-3,-2,-1],
            [-6,-6,-6,-6,-6,-6,-6,-6],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [0,0,0,0,0,0,0,0],
            [6,6,6,6,6,6,6,6],
            [1,2,3,4,5,3,2,1]]