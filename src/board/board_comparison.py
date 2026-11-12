from board.board_utils import split_board
from board.square_analyzer import SquareAnalyzer


def analyze_board_changes(previous_board, current_board, white_at_top):
    previous_squares = split_board(previous_board, white_at_top)
    current_squares = split_board(current_board, white_at_top)

    analyzer = SquareAnalyzer()
    changes = {}

    for square_name in previous_squares:
        changes[square_name] = analyzer.analyze(
            previous_squares[square_name],
            current_squares[square_name]
        )

    return changes
