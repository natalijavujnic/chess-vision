import chess

from motion.move_detector import MoveDetector
from motion.motion_utils import calculate_motion_ratio
from board.board_utils import warp_board, split_board, get_square_position, get_square_color
from board.frame_alignment import align_frame
from board.board_comparison import analyze_board_changes
from game.board_state import BoardState
from game.move_detection import detect_move


class GameAnalyzer:
    def __init__(self, reference_frame, corners, white_at_top):
        self.reference_frame = reference_frame
        self.corners = corners
        self.white_at_top = white_at_top

        self.empty_square_references = {}
        self.move_detector = MoveDetector()
        self.board_state = BoardState()

        self.previous_stable_board = None
        self.previous_frame_number = 0
        self.move_number = 1

        self.last_move_type = None
        self.last_before_board = None
        self.last_after_board = None

        self.last_illegal_before_board = None
        self.last_illegal_candidate_board = None

    def save_empty_references(self, board):
        squares = split_board(board, self.white_at_top)

        for square_name, square_image in squares.items():
            if not self.board_state.is_occupied(square_name):
                self.empty_square_references[square_name] = square_image.copy()

    def insert_empty_reference(self, square_name, board):
        if square_name not in self.empty_square_references:
            squares = split_board(board, self.white_at_top)
            self.empty_square_references[square_name] = squares[square_name].copy()

    def is_square_empty(self, square_name, board, threshold=0.05):
        reference = self.get_empty_reference(square_name)
        if reference is None:
            return None

        squares = split_board(board, self.white_at_top)
        difference = calculate_motion_ratio(
            reference,
            squares[square_name]
        )
        return difference < threshold

    def get_empty_difference(self, square_name, board):
        reference = self.get_empty_reference(square_name)
        if reference is None:
            return None

        squares = split_board(board, self.white_at_top)
        return calculate_motion_ratio(reference, squares[square_name])

    def get_empty_reference(self, square_name):
        if square_name in self.empty_square_references:
            return self.empty_square_references[square_name]

        #  if an empty reference for this square does not exist,
        #  use the empty reference of the closest square with same color
        row, col = get_square_position(square_name, self.white_at_top)
        square_color = get_square_color(square_name)

        closest_reference = None
        closest_distance = None
        for ref_name, ref_image in self.empty_square_references.items():
            ref_row, ref_col = get_square_position(ref_name, self.white_at_top)
            ref_color = get_square_color(ref_name)
            if ref_color == square_color:
                distance = abs(row - ref_row) + abs(col - ref_col)
                if closest_distance is None or distance < closest_distance:
                    closest_reference = ref_image
                    closest_distance = distance
        return closest_reference

    def process_frame(self, frame, frame_number, debug=False, debug_movement=False):
        board = warp_board(frame, self.corners)

        position_ready = self.move_detector.process_frame(board, frame_number, debug=debug_movement)
        if self.move_detector.illegal_candidate_rejected:
            self.move_detector.illegal_candidate_rejected = False
            return "ILLEGAL_REJECTED"
        if not position_ready:
            return None

        #if not self.move_detector.process_frame(board, frame_number, debug=debug_movement):
        #    return None

        aligned_frame = align_frame(self.reference_frame, frame)
        current_board = warp_board(aligned_frame, self.corners)

        if self.previous_stable_board is None:
            self.previous_stable_board = current_board.copy()
            self.save_empty_references(current_board)
            return None

        changes = analyze_board_changes(self.previous_stable_board, current_board, self.white_at_top)
        sorted_changes = sorted(
            changes.items(),
            key=lambda x: x[1]["motion_ratio"],
            reverse=True
        )
        significant_squares = [
            square_name for square_name, analysis in sorted_changes
            if analysis["motion_ratio"] > 0.10
        ]

        #  no squares changed - same board position
        if len(significant_squares) < 2:
            return None

        source, destination, move_type = detect_move(changes, self.board_state, current_board, self.get_empty_difference)
        if source is None or destination is None:
            if debug:
                print(f"Could not detect move at frame {frame_number}.")
            return None

        piece = self.board_state.get_piece(source)
        if piece is not None and piece.piece_type == chess.PAWN and destination[1] in ("1", "8"):
            move_type = "promotion"

        if not self.board_state.move_piece(source, destination):
            if not self.move_detector.illegal_position_confirmed:
                if debug:
                    print(f"Illegal candidate: {source} -> {destination}. Waiting for extra confirmation.")

                self.last_illegal_before_board = self.previous_stable_board.copy()
                self.last_illegal_candidate_board = current_board.copy()

                self.move_detector.start_illegal_confirmation(current_board, frame_number)
                return None
            #  print(f"{self.move_number}. {source} -> {destination} : ILLEGAL")

            self.move_detector.illegal_position_confirmed = False
            self.previous_stable_board = current_board.copy()
            self.previous_frame_number = frame_number
            self.move_number += 1
            return source, destination

        self.last_move_type = move_type
        self.last_before_board = self.previous_stable_board.copy()
        self.last_after_board = current_board.copy()

        self.insert_empty_reference(source, current_board)
        #  print(f"{self.move_number}. {source} -> {destination} : {move_type}")
        self.previous_stable_board = current_board.copy()
        self.previous_frame_number = frame_number
        self.move_number += 1
        return source, destination
