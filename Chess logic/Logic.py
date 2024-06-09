class Piece:
    def __init__(self, color):
        self.color = color

    def get_legal_moves(self, board, position):
        raise NotImplementedError("This method should be overridden.")

class Pawn(Piece):
    def get_legal_moves(self, board, position):
        legal_moves = []
        direction = 1 if self.color == 'white' else -1
        start_row = 1 if self.color == 'white' else 6

        # Normal move
        forward_pos = (position[0] + direction, position[1])
        if board.is_empty(forward_pos):
            legal_moves.append(forward_pos)

            # Double move if in start position
            if position[0] == start_row:
                double_forward_pos = (position[0] + 2 * direction, position[1])
                if board.is_empty(double_forward_pos):
                    legal_moves.append(double_forward_pos)

        # Capture moves
        for capture_offset in [-1, 1]:
            capture_pos = (position[0] + direction, position[1] + capture_offset)
            if board.is_enemy(capture_pos, self.color):
                legal_moves.append(capture_pos)

        # En passant
        en_passant_pos = board.get_en_passant_target()
        if en_passant_pos and en_passant_pos[0] == position[0] + direction:
            legal_moves.append(en_passant_pos)

        return legal_moves

class Rook(Piece):
    def get_legal_moves(self, board, position):
        return self.get_linear_moves(board, position, [(1, 0), (-1, 0), (0, 1), (0, -1)])

    def get_linear_moves(self, board, position, directions):
        legal_moves = []
        for direction in directions:
            for i in range(1, 8):
                new_pos = (position[0] + direction[0] * i, position[1] + direction[1] * i)
                if not board.is_within_bounds(new_pos):
                    break
                if board.is_empty(new_pos):
                    legal_moves.append(new_pos)
                elif board.is_enemy(new_pos, self.color):
                    legal_moves.append(new_pos)
                    break
                else:
                    break
        return legal_moves

class Knight(Piece):
    def get_legal_moves(self, board, position):
        legal_moves = []
        knight_moves = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        for move in knight_moves:
            new_pos = (position[0] + move[0], position[1] + move[1])
            if board.is_within_bounds(new_pos) and (board.is_empty(new_pos) or board.is_enemy(new_pos, self.color)):
                legal_moves.append(new_pos)
        return legal_moves

class Bishop(Piece):
    def get_legal_moves(self, board, position):
        return self.get_linear_moves(board, position, [(1, 1), (1, -1), (-1, 1), (-1, -1)])

class Queen(Piece):
    def get_legal_moves(self, board, position):
        return self.get_linear_moves(board, position, [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ])

class King(Piece):
    def get_legal_moves(self, board, position):
        legal_moves = []
        king_moves = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1)
        ]
        for move in king_moves:
            new_pos = (position[0] + move[0], position[1] + move[1])
            if board.is_within_bounds(new_pos) and (board.is_empty(new_pos) or board.is_enemy(new_pos, self.color)):
                legal_moves.append(new_pos)

        # Castling moves
        if not self.has_moved and not board.is_in_check(self.color):
            for rook_col in [0, 7]:
                if not board.has_moved((position[0], rook_col)):
                    direction = 1 if rook_col == 7 else -1
                    path_clear = all(
                        board.is_empty((position[0], position[1] + i * direction))
                        for i in range(1, 4 if direction == -1 else 3)
                    )
                    if path_clear:
                        new_pos = (position[0], position[1] + 2 * direction)
                        legal_moves.append(new_pos)
        return legal_moves

class ChessBoard:
    def __init__(self):
        self.board = self.setup_board()
        self.en_passant_target = None

    def setup_board(self):
        # Initialize the board with pieces in starting positions
        board = [[None for _ in range(8)] for _ in range(8)]
        # Place pawns
        for i in range(8):
            board[1][i] = Pawn('white')
            board[6][i] = Pawn('black')
        # Place other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, piece in enumerate(piece_order):
            board[0][i] = piece('white')
            board[7][i] = piece('black')
        return board

    def is_within_bounds(self, position):
        return 0 <= position[0] < 8 and 0 <= position[1] < 8

    def is_empty(self, position):
        return self.is_within_bounds(position) and self.board[position[0]][position[1]] is None

    def is_enemy(self, position, color):
        if not self.is_within_bounds(position):
            return False
        piece = self.board[position[0]][position[1]]
        return piece is not None and piece.color != color

    def get_en_passant_target(self):
        return self.en_passant_target

    def move_piece(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]
        if piece:
            self.board[end_pos[0]][end_pos[1]] = piece
            self.board[start_pos[0]][start_pos[1]] = None
            # Handle special moves like en passant, castling, and pawn promotion
            self.en_passant_target = None
            if isinstance(piece, Pawn):
                if abs(start_pos[0] - end_pos[0]) == 2:
                    self.en_passant_target = (start_pos[0] + (end_pos[0] - start_pos[0]) // 2, start_pos[1])
                if end_pos[0] == 0 or end_pos[0] == 7:
                    self.board[end_pos[0]][end_pos[1]] = Queen(piece.color)
            if isinstance(piece, King) and abs(start_pos[1] - end_pos[1]) == 2:
                rook_start = (start_pos[0], 0 if end_pos[1] < start_pos[1] else 7)
                rook_end = (start_pos[0], (start_pos[1] + end_pos[1]) // 2)
                self.board[rook_end[0]][rook_end[1]] = self.board[rook_start[0]][rook_start[1]]
                self.board[rook_start[0]][rook_start[1]] = None

    def is_in_check(self, color):
        king_position = self.find_king(color)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if king_position in piece.get_legal_moves(self, (row, col)):
                        return True
        return False

    def find_king(self, color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and isinstance(piece, King) and piece.color == color:
                    return (row, col)
        return None

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in piece.get_legal_moves(self, (row, col)):
                        temp_board = self.copy()
                        temp_board.move_piece((row, col), move)
                        if not temp_board.is_in_check(color):
                            return False
        return True

    def copy(self):
        new_board = ChessBoard()
        new_board.board = [row[:] for row in self.board]
        new_board.en_passant_target = self.en_passant_target
        return new_board

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for move in piece.get_legal_moves(self, (row, col)):
                        temp_board = self.copy()
                        temp_board.move_piece((row, col), move)
                        if not temp_board.is_in_check(color):
                            return False
        return True

class ChessGame:
    def __init__(self):
        self.board = ChessBoard()
        self.current_turn = 'white'
        self.history = []

    def play_turn(self, start_pos, end_pos):
        piece = self.board.board[start_pos[0]][start_pos[1]]
        if piece and piece.color == self.current_turn:
            legal_moves = piece.get_legal_moves(self.board, start_pos)
            if end_pos in legal_moves:
                self.board.move_piece(start_pos, end_pos)
                self.history.append((start_pos, end_pos))
                self.switch_turn()
                return True
        return False

    def switch_turn(self):
        self.current_turn = 'black' if self.current_turn == 'white' else 'white'

    def is_game_over(self):
        return self.board.is_checkmate(self.current_turn) or self.board.is_stalemate(self.current_turn)

# Example of creating a game and making moves
game = ChessGame()
game.play_turn((6, 4), (4, 4))  # Move pawn from e2 to e4
