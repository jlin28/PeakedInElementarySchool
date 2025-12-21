# Joyce Lin, Evan Khosh, Sean Zheng, Zixi Qiao
# PIES
# SoftDev
# P01 -- ArRESTed Development
# 12/22/2025

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

castling_state = {"white_kingside": True,
                  "white_queenside": True,
                  "black_kingside": True,
                  "black_queenside": True}

def reset_board():
    global current_pos, en_passant, castling_state
    current_pos = copy.deepcopy(init_pos)
    en_passant = None
    castling_state = {
        "white_kingside": True,
        "white_queenside": True,
        "black_kingside": True,
        "black_queenside": True
    }

# perspective = white or black
def get_display_board(board, perspective="white"):
    # display board can be flipped but internal logic stays from POV
    # with white at the bottom for legal_squares
    if perspective == "white":
        return board

    # black's perspective: rotate 180°
    flipped = []
    for r in range(7, -1, -1):
        row = []
        for c in range(7, -1, -1):
            row.append(board[r][c])
        flipped.append(row)
    return flipped

def display_to_internal(r, c, perspective):
    if perspective == "white":
        return r, c
    return 7 - r, 7 - c

def internal_to_display(r, c, perspective):
    if perspective == "white":
        return r, c
    return 7 - r, 7 - c

def set_board(board):
    global current_pos
    current_pos = board

def remove_piece(r,c):
    global current_pos
    current_pos[r][c] = 0;
    print("internal:")
    print(current_pos)

def get_internal_board():
    global current_pos
    return current_pos

# must capture king to win game (no checkmates), stalemates still possible and draw if king vs king (+ knight/bishop)
# color to move is used to check stalemate, white or black
def game_over(board, color_to_move = None):
    global en_passant

    king_count = 0
    winner_color = None
    non_rook_queen_pieces = 0

    # Count non-rook/queen pieces and also kings specifically
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if abs(piece) == 5:
                king_count += 1
                winner_color = get_color(piece)
            if piece != 0 and abs(piece) != 1 and abs(piece) != 4:
                non_rook_queen_pieces += 1

    # If a king was captured, the remaining king's side wins
    if king_count == 1:
        return (True, winner_color)

    # Draw from insufficient material
    if king_count == 2 and non_rook_queen_pieces <= 3:
        return (True, "gray") # winner color is gray for draws

    # Stalemate if side to move has no legal moves
    has_legal_move = False
    for r in range(8):
        for c in range(8):
            if color_to_move is None:
                return (False, None)
            if get_color(board[r][c]) == color_to_move:
                if legal_squares(board, r, c, en_passant): # if moves exist
                    has_legal_move = True
                    break
        if has_legal_move:
            break
    if not has_legal_move:
        return (True, "gray") # draw

    # Game is not over
    return (False, None)

# Not game over, but checks if a king is in check and they have no legal moves
def in_checkmate(board, color_to_move):
    global en_passant
    if not in_check(board, color_to_move):
        return False, color_to_move
    for r in range(len(board)):
        for c in range(len(board[0])):
            if get_color(board[r][c]) == color_to_move:
                if legal_squares(board, r, c, en_passant):
                    return False, color_to_move
    return True, color_to_move

def legal_squares(board, r, c, en_passant_state):
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
        moves = king_moves(board, r, c, color, castling_state)
    elif piece_type == 6:
        moves = pawn_moves(board, r, c, color, en_passant_state)

    # filter based on checks/pins
    legal = []
    for nr, nc in moves:
        new_board = simulate_move(board, r, c, nr, nc, en_passant_state, castling_state)[0]
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

def simulate_move(board, r1, c1, r2, c2, en_passant_state, castling_state):
    piece = board[r1][c1]
    new_board = copy.deepcopy(board)
    new_en_passant = None  # gets reset every move unless replaced
    new_castling = copy.deepcopy(castling_state)

    # En passant capture
    if en_passant_state is not None:
        target_r, target_c, pawn_r, pawn_c = en_passant_state
        if (r2, c2) == (target_r, target_c) and abs(piece) == 6:
            new_board[pawn_r][pawn_c] = 0  # remove captured pawn

    # King castling in simulate_move
    if abs(piece) == 5:
        if c2 - c1 == 2:  # kingside
            new_board[r1][7] = 0
            new_board[r1][c1 + 1] = 1 if piece > 0 else -1  # rook moves next to king
        elif c2 - c1 == -2:  # queenside
            new_board[r1][0] = 0
            new_board[r1][c1 - 1] = 1 if piece > 0 else -1

    # Move piece normally
    potential_captured_piece = new_board[r2][c2]
    new_board[r2][c2] = piece
    new_board[r1][c1] = 0

    # Update castling rights
    if abs(piece) == 5:  # king moved
        if piece > 0:
            new_castling["white_kingside"] = False
            new_castling["white_queenside"] = False
        else:
            new_castling["black_kingside"] = False
            new_castling["black_queenside"] = False

    elif abs(piece) == 1:  # rook moved
        if r1 == 7 and c1 == 0:
            new_castling["white_queenside"] = False
        elif r1 == 7 and c1 == 7:
            new_castling["white_kingside"] = False
        elif r1 == 0 and c1 == 0:
            new_castling["black_queenside"] = False
        elif r1 == 0 and c1 == 7:
            new_castling["black_kingside"] = False

    elif abs(potential_captured_piece) == 1:   # rook captured
        if r2 == 7 and c2 == 0:
            new_castling["white_queenside"] = False
        elif r2 == 7 and c2 == 7:
            new_castling["white_kingside"] = False
        elif r2 == 0 and c2 == 0:
            new_castling["black_queenside"] = False
        elif r2 == 0 and c2 == 7:
            new_castling["black_kingside"] = False

    # Check if new en passant state should be created
    if abs(piece) == 6 and abs(r2 - r1) == 2:
        passed_square = ((r1 + r2) // 2, c1)
        new_en_passant = (passed_square[0], passed_square[1], r2, c1)

    return new_board, new_en_passant, new_castling

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

def king_moves(board, r, c, color, castling_state = None):
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

    # Castling
    if castling_state is not None:
        if color == "white":
            row = 7
            if castling_state.get("white_kingside", False):
                if board[row][5] == 0 and board[row][6] == 0:
                    if not is_square_attacked(board, row, 4, enemy) and not is_square_attacked(board, row, 5, enemy) and not is_square_attacked(board, row, 6, enemy):
                        moves.append((row, 6))  # kingside castling
            if castling_state.get("white_queenside", False):
                if board[row][1] == 0 and board[row][2] == 0 and board[row][3] == 0:
                    if not is_square_attacked(board, row, 4, enemy) and not is_square_attacked(board, row, 3, enemy) and not is_square_attacked(board, row, 2, enemy):
                        moves.append((row, 2))  # queenside castling
        else:
            row = 0
            if castling_state.get("black_kingside", False):
                if board[row][5] == 0 and board[row][6] == 0:
                    if not is_square_attacked(board, row, 4, enemy) and not is_square_attacked(board, row, 5, enemy) and not is_square_attacked(board, row, 6, enemy):
                        moves.append((row, 6))
            if castling_state.get("black_queenside", False):
                if board[row][1] == 0 and board[row][2] == 0 and board[row][3] == 0:
                    if not is_square_attacked(board, row, 4, enemy) and not is_square_attacked(board, row, 3, enemy) and not is_square_attacked(board, row, 2, enemy):
                        moves.append((row, 2))
    return moves

def pawn_moves(board, r, c, color, en_passant_state):
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
    if en_passant_state is not None:
        target_r, target_c, pawn_r, pawn_c = en_passant_state

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

def apply_promotion(board, promotion_choice=None):
    promos = promotions(board)
    
    if not promos:
        return board

    piece_map = {
        "q": 4,
        "r": 1,
        "b": 3,
        "n": 2
    }

    for r, c, options in promos:
        if promotion_choice is None:
            board[r][c] = options[0]   # auto-queen
        else:
            base = piece_map.get(promotion_choice.lower(), 4)
            if options[0] > 0:
                board[r][c] = base
            else:
                board[r][c] = -base

    return board

# Convert board position to FEN for chess engine api
def board_to_fen(board, color_to_move, castling_state, en_passant):
    piece_map = {
        1: "r", 2: "n", 3: "b", 4: "q", 5: "k", 6: "p"
    }

    rows = []
    for r in range(8):
        empty = 0
        fen_row = ""
        for c in range(8):
            piece = board[r][c]
            if piece == 0:
                empty += 1
            else:
                if empty > 0:
                    fen_row += str(empty)
                    empty = 0
                p = piece_map[abs(piece)]
                fen_row += p.upper() if piece > 0 else p
        if empty > 0:
            fen_row += str(empty)
        rows.append(fen_row)

    board_part = "/".join(rows)
    turn_part = "w" if color_to_move == "white" else "b"

    castling = ""
    if castling_state["white_kingside"]: castling += "K"
    if castling_state["white_queenside"]: castling += "Q"
    if castling_state["black_kingside"]: castling += "k"
    if castling_state["black_queenside"]: castling += "q"
    if castling == "":
        castling = "-"

    if en_passant is None:
        ep = "-"
    else:
        r, c, _, _ = en_passant
        ep = chr(ord("a") + c) + str(8 - r) # convert to a square like e4 for en passant

    return f"{board_part} {turn_part} {castling} {ep} 0 1"