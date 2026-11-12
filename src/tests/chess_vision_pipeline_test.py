from video.video_utils import get_frame, iterate_frames
from board.board_utils import warp_board
from board.board_detection import detect_board_corners, detect_white_at_top
from board.frame_alignment import align_frame
from visualization.display_utils import show_frame, draw_board_grid, draw_detected_corners, draw_move_squares, draw_single_square, draw_square_names
from motion.move_detector import MoveDetector
from motion.motion_utils import find_first_stable_frame, calculate_motion_mask
from game.game_analyzer import GameAnalyzer


class ChessVisionPipelineTest:
    def __init__(self, video_path, expected_moves):
        self.video_path = video_path
        self.expected_moves = expected_moves

        #  board extraction
        self.first_frame = None
        self.corners = None
        self.board = None

        # stable positions detection
        self.previous_stable_board = None
        self.current_stable_board = None
        self.stable_positions = []

        #  game analysis
        self.detected_moves = []
        self.white_at_top = True

    def run(self,
            debug_board_extraction=True,
            show_rejected_positions=True,
            show_game_frames=True
            ):
        print(f"\nCHESS VISION PIPELINE TEST {self.video_path}")

        print("\n1. Board extraction")
        if not self.test_board_extraction(debug=debug_board_extraction):
            print("Pipeline test failed.")
            return False

        # print("\n2. Stable position detection")
        # if not self.test_stable_positions(show_rejected_positions=show_rejected_positions):
        #    print("Pipeline test failed.")
        #    return False

        print("\n2. Game analyzer")
        if not self.test_game_analyzer(show_frames=show_game_frames):
            print("Pipeline test failed.")
            return False

        print("Pipeline test completed.")
        return True

    def test_board_extraction(self, debug=False, debug_detection=False):
        self.first_frame, frame_number = find_first_stable_frame(self.video_path)
        if self.first_frame is None:
            print("Board extraction: FAIL - no stable frame found")
            return False
        print(f"First stable frame detected at frame {frame_number}.")
        if debug:
            show_frame(self.first_frame, f"First stable frame - frame {frame_number}")

        self.corners = detect_board_corners(self.first_frame, debug=debug_detection)

        if self.corners is None:
            print("Board extraction: FAIL - corners not detected")
            return False
        print(f"Board corners detected.")
        if debug:
            corners_frame = draw_detected_corners(self.first_frame, self.corners)
            show_frame(corners_frame, "Detected board corners")

        self.board = warp_board(self.first_frame, self.corners)
        print(f"Board extracted.")

        self.white_at_top = detect_white_at_top(self.board)
        print("White" if self.white_at_top else "Black", "at top detected.")

        if debug:
            grid = draw_board_grid(self.board)
            grid = draw_square_names(grid, self.white_at_top)
            show_frame(grid, "Extracted board")

        print("Board extraction test: PASS")
        return True

    def initialize_board(self):
        if self.first_frame is None:
            self.first_frame, _ = find_first_stable_frame(self.video_path)
            if self.first_frame is None:
                print("Board extraction: FAIL - no stable frame found")
                return False

        if self.corners is None:
            self.corners = detect_board_corners(self.first_frame, debug=False)
            if self.corners is None:
                print("Board extraction: FAIL - corners not detected")
                return False

        if self.board is None:
            self.board = warp_board(self.first_frame, self.corners)

        self.white_at_top = detect_white_at_top(self.board)
        return True

    def test_frame_alignment(self):
        if not self.initialize_board():
            return False

        current_frame = get_frame(self.video_path, frame_number=1500)
        current_board = warp_board(current_frame, self.corners)
        aligned_frame = align_frame(self.first_frame, current_frame)
        aligned_board = warp_board(aligned_frame, self.corners)

        reference_grid = draw_board_grid(self.board.copy())
        current_grid = draw_board_grid(current_board.copy())
        aligned_grid = draw_board_grid(aligned_board.copy())

        show_frame(reference_grid, "Reference board")
        show_frame(current_grid, "Before alignment")
        show_frame(aligned_grid, "After alignment")

        print("Frame alignment test completed.")
        return True

    def test_stable_positions(self, show_positions=False, show_rejected_positions=False):
        if not self.initialize_board():
            return False

        detector = MoveDetector()
        stable_positions = 0
        self.stable_positions = []

        for frame_number, frame in iterate_frames(self.video_path):
            board = warp_board(frame, self.corners)
            if detector.process_frame(board, frame_number):
                stable_positions += 1

                aligned_frame = align_frame(self.first_frame, frame)
                aligned_board = warp_board(aligned_frame, self.corners)
                self.stable_positions.append(
                    (frame_number, aligned_board.copy())
                )

                if show_positions:
                    print(f"Stable position {stable_positions} at frame {frame_number}")
                    show_frame(board, f"Stable position {stable_positions}")

        print(f"Total of {stable_positions} stable positions detected.")
        print("Stable position detection test: PASS")
        return True

    def test_game_analyzer(self, debug=False, show_frames=False, debug_movement=False):
        if not self.initialize_board():
            return False

        self.detected_moves = []
        move_index = 0
        return_value = True

        analyzer = GameAnalyzer(self.first_frame, self.corners, self.white_at_top)

        for frame_number, frame in iterate_frames(self.video_path):
            move = analyzer.process_frame(frame, frame_number, debug=debug, debug_movement=debug_movement)

            if move == "ILLEGAL_REJECTED":
                print(f"Rejected illegal candidate at frame {frame_number}.")
                if show_frames:
                    show_frame(analyzer.last_illegal_before_board, f"Before illegal move", destroy=False)
                    show_frame(analyzer.last_illegal_candidate_board, f"After illegal move at frame {frame_number}")
                continue

            if move is not None:
                self.detected_moves.append(move)
                source, destination = move
                move_type = analyzer.last_move_type
                print(f"{move_index + 1}. {source} -> {destination} : {move_type}")

                if move_index < len(self.expected_moves):
                    expected = self.expected_moves[move_index]
                    if move != expected:
                        print(f"EXPECTED {expected[0]} -> {expected[1]}")
                        return_value = False
                else:
                    print(f"UNEXPECTED MOVE {move[0]} -> {move[1]}")
                    return_value = False

                if show_frames:
                    if move_type == "castling":
                        before = draw_move_squares(analyzer.last_before_board, source, destination, self.white_at_top)
                        after = draw_move_squares(analyzer.last_after_board, source, destination, self.white_at_top)

                        if source == "E1" and destination == "G1":
                            rook_source, rook_destination = "H1", "F1"
                        elif source == "E1" and destination == "C1":
                            rook_source, rook_destination = "A1", "D1"
                        elif source == "E8" and destination == "G8":
                            rook_source, rook_destination = "H8", "F8"
                        else:
                            rook_source, rook_destination = "A8", "D8"

                        before = draw_move_squares(before, rook_source, rook_destination, self.white_at_top, blue=True)
                        after = draw_move_squares(after, rook_source, rook_destination, self.white_at_top, blue=True)

                        show_frame(before, f"Before move {move_index + 1}", destroy=False)
                        show_frame(after, f"After move {move_index + 1}")

                    elif move_type == "en passant":
                        before = draw_move_squares(analyzer.last_before_board, source, destination, self.white_at_top)
                        after = draw_move_squares(analyzer.last_after_board, source, destination, self.white_at_top)

                        captured_square = destination[0] + source[1]
                        before = draw_single_square(before, captured_square, "CAPTURED", self.white_at_top)
                        after = draw_single_square(after, captured_square, "CAPTURED", self.white_at_top)

                        show_frame(before, f"Before move {move_index + 1}", destroy=False)
                        show_frame(after, f"After move {move_index + 1}")

                    elif move_type == "promotion":
                        before = draw_move_squares(analyzer.last_before_board, source, destination, self.white_at_top)
                        after = draw_move_squares(analyzer.last_after_board, source, destination, self.white_at_top)
                        after = draw_single_square(after, destination, "PROMOTION", self.white_at_top)

                        show_frame(before, f"Before move {move_index + 1}", destroy=False)
                        show_frame(after, f"After move {move_index + 1}")

                    else:
                        before = draw_move_squares(analyzer.last_before_board, source, destination, self.white_at_top)
                        after = draw_move_squares(analyzer.last_after_board, source, destination, self.white_at_top)
                        show_frame(before, f"Before move {move_index + 1}", destroy=False)
                        show_frame(after, f"After move {move_index + 1}")

                move_index += 1

        if len(self.detected_moves) < len(self.expected_moves):
            for i in range(len(self.detected_moves), len(self.expected_moves)):
                expected = self.expected_moves[i]
                print(f"NOT DETECTED {expected[0]} -> {expected[1]}")
            return_value = False

        if return_value:
            print("\nMove detection: PASS")
        else:
            print("\nMove detection: FAIL")
        return return_value

    def show_motion_detection_example(self, before_frame_number, motion_frame_number, after_frame_number):
        if not self.initialize_board():
            return

        before_frame = get_frame(self.video_path, before_frame_number)
        motion_frame = get_frame(self.video_path, motion_frame_number)
        after_frame = get_frame(self.video_path, after_frame_number)

        before_board = warp_board(before_frame, self.corners)
        motion_board = warp_board(motion_frame, self.corners)
        after_board = warp_board(after_frame, self.corners)

        motion_mask = calculate_motion_mask(before_board, motion_board)

        show_frame(before_board, "Stable position before move")
        show_frame(motion_board, "Movement")
        show_frame(motion_mask, "Motion mask")
        show_frame(after_board, "Stable position after move")
