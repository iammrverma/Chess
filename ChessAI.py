import random

piece_score = {"K": 0, "Q": 10, "R": 5, "B": 5, "N": 4, "P": 2}

knight_scores = [
    [1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 3, 3, 3, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1]
]

bishop_scores = [
    [4, 3, 2, 1, 1, 2, 3, 4],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 4, 3, 3, 4, 3, 2],
    [3, 4, 3, 2, 2, 3, 4, 3],
    [4, 3, 2, 1, 1, 2, 3, 4]
]

queen_scores = [
    [1, 1, 1, 3, 1, 1, 1, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 2, 3, 3, 3, 2, 2, 1],
    [1, 4, 3, 3, 3, 4, 2, 1],
    [1, 2, 3, 3, 3, 1, 1, 1],
    [1, 1, 1, 3, 1, 1, 1, 1]
]

rook_scores = [
    [4, 3, 4, 4, 4, 4, 3, 4],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [4, 4, 4, 4, 4, 4, 4, 4],
    [4, 3, 4, 4, 4, 4, 3, 4]
]

white_pawn_scores = [
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [2, 3, 3, 4, 4, 3, 3, 2],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 0]
]

black_pawn_scores = [
    [0, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 1, 1, 1],
    [1, 1, 2, 3, 3, 2, 1, 1],
    [1, 2, 3, 4, 4, 3, 2, 1],
    [2, 3, 3, 4, 4, 3, 3, 2],
    [5, 6, 6, 7, 7, 6, 6, 5],
    [8, 8, 8, 8, 8, 8, 8, 8],
    [8, 8, 8, 8, 8, 8, 8, 8]
]

piece_position_scores = {
    "N": knight_scores,
    "Q": queen_scores,
    "B": bishop_scores,
    "R": rook_scores,
    "bP": black_pawn_scores,
    "wP": white_pawn_scores
}

CHECKMATE = 1000
STALEMATE = 0
DEPTH = int(3)

global next_move
global num_moves


def random_move(valid_moves):
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_move_nega_max_alpha_beta(gs, valid_moves):
    global next_move
    global num_moves
    num_moves = 0
    next_move = None
    nega_max_alpha_beta(gs, valid_moves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_turn else -1)
    return next_move


def nega_max_alpha_beta(gs, valid_moves, depth, alpha, beta, turn_multiplier):
    global next_move, num_moves
    num_moves += 1
    if depth == 0:
        return turn_multiplier * score_board(gs)

    max_score = -CHECKMATE
    for move in valid_moves:
        piece = gs.board[move.end_col][move.end_col]
        score = move_order(move)  # move ordering
        if piece != "--":
            score += piece_score[piece[1]]
            if gs.square_under_attack(move.end_row, move.end_col):
                score -= piece_score[piece[1]]
        gs.make_move(move)
        nm = gs.get_valid_moves
        score += - nega_max_alpha_beta(gs, nm, depth - 1, -beta, -alpha, -turn_multiplier)
        if score > max_score:
            max_score = score
            if depth == DEPTH:
                next_move = move
        gs.undo()
        alpha = max(alpha, max_score)
        if alpha >= beta:
            break
    return max_score


def score_board(gs):
    if gs.check_mate:
        if gs.white_turn:
            return -CHECKMATE
        else:
            return CHECKMATE
    elif gs.stale_mate:
        return STALEMATE

    score = 0
    for row in range(len(gs.board)):
        for col in range(len((gs.board[row]))):
            box = gs.board[row][col]
            if box != "--":
                piece_position_score = 0
                if box[1] != "K":
                    if box[1] == "P":
                        piece_position_score = piece_position_scores[box][row][col]
                    else:
                        piece_position_score = piece_position_scores[box[1]][row][col]

                if box[0] == "w":
                    score += piece_score[box[1]] + piece_position_score * 10

                elif box[0] == "b":
                    score -= piece_score[box[1]] + piece_position_score * 10

    return score


def score_material(board):
    score = 0
    for row in board:
        for box in row:
            if box[0] == "w":
                score += piece_score[box[1]]
            elif box[0] == "b":
                score -= piece_score[box[1]]

    return score


def move_order(move):
    score = 0
    if move.piece_capture != '--':
        score += piece_score[move.piece_capture[1]]
        if move.is_pawn_promotion:
            score += piece_score['Q']
    elif move.is_castle_move:
        score += piece_score['K'] + piece_score['R']

    return score
