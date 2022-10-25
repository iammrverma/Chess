"""
This Class is responsible for:
 Storing the information about the current state of game,
 determining the valid move at current state,
 handling moveLog,
 drawing the pieces.
"""


class GameState:
    def __init__(self, win):
        """
        Board is 2d list, each element of list is
        string of two character
        1st character is color
        2nd character is piece
        B -- black
        W -- white
        -- -- empty block
        R -- rook
        N -- knight
        B -- bishop
        Q -- Queen
        K -- king
        """
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.move_functions = {"P": self.get_pawn_moves, "R": self.get_rook_moves, "N": self.get_knight_moves,
                               "B": self.get_bishop_moves, "K": self.get_king_moves, "Q": self.get_queen_moves}
        self.white_turn = True
        self.move_log = []
        self.captured_pieces = []
        self.win = win
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.check_mate = False  # when king have no valid square and is in check
        self.stale_mate = False  # when player have no valid move and king is not in check
        self.en_passant_possible = ()  # Coordinates where the en_passant possible
        self.en_passant_possible_log = [self.en_passant_possible]
        self.current_castling_rights = CastleRights(True, True, True, True)
        self.castle_right_log = [CastleRights(self.current_castling_rights.wkc, self.current_castling_rights.bkc,
                                              self.current_castling_rights.wqc, self.current_castling_rights.bqc)]

    def make_move(self, move):
        """
        takes a move(valid or invalid) and simply performs that move
        NOTE: can not for castling pawn promotion  etc
        :param move:
        :return:
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_move
        self.move_log.append(move)
        self.white_turn = not self.white_turn
        if move.piece_move == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_move == "bK":
            self.black_king_location = (move.end_row, move.end_col)

        # pawn promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_move[0] + "Q"

        # en passant
        if move.is_en_passant_move:
            self.board[move.start_row][move.end_col] = "--"

        # update en passant possible variable
        if move.piece_move[1] == "P" and abs(move.start_row - move.end_row) == 2:
            self.en_passant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.en_passant_possible = ()

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            else:
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"

        self.en_passant_possible_log.append(self.en_passant_possible)

        # updating Castling rights
        self.update_castle_right(move)
        self.castle_right_log.append(CastleRights(self.current_castling_rights.wkc, self.current_castling_rights.bkc,
                                                  self.current_castling_rights.wqc, self.current_castling_rights.bqc))

    def undo(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_move
            self.board[move.end_row][move.end_col] = move.piece_capture
            self.white_turn = not self.white_turn
            if move.piece_move == "wK":
                self.white_king_location = (move.start_row, move.start_col)
            elif move.piece_move == "bK":
                self.black_king_location = (move.start_row, move.start_col)

            # undo en passant move
            if move.is_en_passant_move:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_capture
            self.en_passant_possible_log.pop()
            self.en_passant_possible = self.en_passant_possible_log[-1]

            # undo castle rights
            self.castle_right_log.pop()  # removing the 2nd castling right
            new_rights = self.castle_right_log[-1]
            self.current_castling_rights = CastleRights(new_rights.wkc, new_rights.bkc, new_rights.wqc, new_rights.bqc)

            # undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = "--"
                else:
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = "--"

        self.check_mate = False
        self.stale_mate = False

    def update_castle_right(self, move):
        if move.piece_move == "wK":
            self.current_castling_rights.wkc = False
            self.current_castling_rights.wqc = False
        elif move.piece_move == "bK":
            self.current_castling_rights.bkc = False
            self.current_castling_rights.bqc = False
        elif move.piece_move == "wR":
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.wqc = False
                elif move.start_col == 7:
                    self.current_castling_rights.wkc = False
        elif move.piece_move == "bR":
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_rights.bqc = False
                elif move.start_col == 7:
                    self.current_castling_rights.bkc = False

        if move.piece_capture == "wR":
            if move.end_row == 7:
                if move.end_col == 0:
                    self.current_castling_rights.wqc = False
                elif move.end_col == 7:
                    self.current_castling_rights.wkc = False
        elif move.piece_capture == "bR":
            if move.end_row == 0:
                if move.end_col == 0:
                    self.current_castling_rights.bqc = False
                elif move.end_col == 7:
                    self.current_castling_rights.bkc = False

    @property
    def get_valid_moves(self):
        """
        :return: valid moves considering king's check
        """
        temp_en_passant_possible = self.en_passant_possible
        temp_castle_rights = CastleRights(self.current_castling_rights.wkc, self.current_castling_rights.bkc,
                                          self.current_castling_rights.wqc, self.current_castling_rights.bqc)
        # generating all moves
        moves = self._get_all_moves()
        if self.white_turn:
            self.get_castle_moves(self.white_king_location[0], self.white_king_location[1], moves)
        else:
            self.get_castle_moves(self.black_king_location[0], self.black_king_location[1], moves)
        # for moves make the move
        for i in range(len(moves) - 1, -1, -1):
            self.make_move(moves[i])
            # generate all opponent's move
            # for all opponent's move see if attacking king
            self.white_turn = not self.white_turn  # because the move function swap the turns so need to swap them again
            if self.in_check():
                moves.remove(moves[i])  # if they do it's not a valid move
            self.white_turn = not self.white_turn
            self.undo()
        if len(moves) == 0:  # either checkmate or stalemate
            if self.in_check():
                self.check_mate = True
            else:
                self.stale_mate = True

        self.en_passant_possible = temp_en_passant_possible
        self.current_castling_rights = temp_castle_rights

        return moves

    def in_check(self):
        """
        :return: current player is in check
        """
        if self.white_turn:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])

    def square_under_attack(self, r, c):
        """
        :param r:
        :param c:
        :return: if enemy can attack the square r, c
        """
        self.white_turn = not self.white_turn
        opp_moves = self._get_all_moves()
        self.white_turn = not self.white_turn
        for move in opp_moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def _get_all_moves(self):
        """
        :return: valid moves ignores king's check
        """
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                turn = self.board[row][col][0]
                if (turn == "w" and self.white_turn) or (turn == "b" and not self.white_turn):
                    piece = self.board[row][col][1]
                    self.move_functions[piece](row, col, moves)
        return moves

    def get_pawn_moves(self, r, c, moves):
        if self.white_turn:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board))
                if r == 6 and self.board[r - 2][c] == "--":
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r - 1][c - 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, en_passant_possible=True))

            if c + 1 <= 7:
                if self.board[r - 1][c + 1][0] == "b":
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, en_passant_possible=True))

        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == "--":
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, en_passant_possible=True))
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == "w":
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.en_passant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, en_passant_possible=True))

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.white_turn else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_knight_moves(self, r, c, moves):
        knight_move = ((-2, -1), (-2, 1), (2, 1), (2, -1), (-1, -2), (1, -2), (1, 2), (-1, 2))
        friend_color = "w" if self.white_turn else "b"
        for m in knight_move:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != friend_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemy_color = "b" if self.white_turn else "w"
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_king_moves(self, r, c, moves):
        king_moves = ((1, 0), (-1, 0), (1, 1), (1, -1), (-1, -1), (-1, 1), (0, -1), (0, 1))
        friend_color = "w" if self.white_turn else "b"
        for i in range(8):
            end_row = r + king_moves[i][0]
            end_col = c + king_moves[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != friend_color:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return  # castling is not allowed
        if (self.white_turn and self.current_castling_rights.wkc) or \
                (not self.white_turn and self.current_castling_rights.bkc):
            self.get_king_side_castle_move(r, c, moves)

        if (self.white_turn and self.current_castling_rights.wqc) or \
                (not self.white_turn and self.current_castling_rights.bqc):
            self.get_queen_side_castle_move(r, c, moves)

    def get_king_side_castle_move(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, castle_possible=True))

    def get_queen_side_castle_move(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, castle_possible=True))

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)


class CastleRights:
    """w:white, b:black, c: castle, k: king, q: queen"""

    def __init__(self, wkc, bkc, wqc, bqc):
        self.wkc = wkc
        self.bkc = bkc
        self.wqc = wqc
        self.bqc = bqc


class Move:
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board, en_passant_possible=False, castle_possible=False):
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_move = board[self.start_row][self.start_col]
        self.piece_capture = board[self.end_row][self.end_col]
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

        # pawn promotion
        self.is_pawn_promotion = (self.piece_move == "wP" and self.end_row == 0) or (
                self.piece_move == "bP" and self.end_row == 7)

        # en_passant
        self.is_en_passant_move = en_passant_possible
        self.is_castle_move = castle_possible
        if self.is_en_passant_move:
            self.piece_capture = "wP" if self.piece_move == "bP" else "bP"

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def get_chess_notations(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)

    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
