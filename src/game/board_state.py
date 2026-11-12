import chess


class BoardState:
    def __init__(self):
        self.chess_board = chess.Board()

    def get_piece(self, square):
        square = chess.parse_square(square.lower())
        return self.chess_board.piece_at(square)

    def is_occupied(self, square):
        return self.get_piece(square) is not None

    def is_move_legal(self, source, destination):
        move = self.promotion(source, destination)
        return move in self.chess_board.legal_moves

    def move_piece(self, source, destination):
        move = self.promotion(source, destination)
        if move not in self.chess_board.legal_moves:
            return False
        self.chess_board.push(move)
        return True

    def promotion(self, source, destination):
        move_uci = source.lower() + destination.lower()
        piece = self.get_piece(source)

        if piece is not None and piece.piece_type == chess.PAWN:
            destination_rank = int(destination[1])
            if destination_rank == 1 or destination_rank == 8:
                move_uci += "q"
        move = chess.Move.from_uci(move_uci)
        return move
