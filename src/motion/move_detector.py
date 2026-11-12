from motion.motion_utils import calculate_motion_ratio, is_board_stable, is_move_finished


class MoveDetector:
    def __init__(self):
        self.motion_detected = False
        self.stable_counter = 0

        self.previous_frame = None
        self.initial_board_saved = False

        self.pending_board = None
        self.pending_frame_number = None
        self.confirmation_counter = 0
        self.confirmation_frames = 2

        self.illegal_candidate_board = None
        self.illegal_candidate_frame = None
        self.illegal_confirmation_counter = 0
        self.illegal_confirmation_frames = 10
        self.illegal_position_confirmed = False

        self.illegal_candidate_rejected = False
        self.waiting_after_rejected_illegal = False

    def process_frame(self, board, frame_number, debug=False):
        #  initialization
        if self.previous_frame is None:
            self.previous_frame = board.copy()
            return False

        #  check if illegal position was detected
        if self.illegal_candidate_board is not None:
            return self.process_illegal_candidate(board, frame_number, debug)

        motion_ratio = calculate_motion_ratio(self.previous_frame, board)

        #  wait for motion after rejecting illegal position
        if self.waiting_after_rejected_illegal:
            return self.wait_for_motion(board, frame_number, motion_ratio, debug)

        #  check pending stable position
        if self.pending_board is not None:
            return self.process_pending_position(board, frame_number, debug)

        #  normal motion detection
        return self.process_normal_frame(board, frame_number, motion_ratio, debug)

    def process_illegal_candidate(self, board, frame_number, debug):
        illegal_motion = calculate_motion_ratio(self.illegal_candidate_board, board)

        if is_board_stable(illegal_motion):
            self.illegal_confirmation_counter += 1

            if self.illegal_confirmation_counter >= self.illegal_confirmation_frames:
                if debug:
                    print(f"Illegal position from frame {self.illegal_candidate_frame} confirmed at frame {frame_number}")
                self.clear_illegal_candidate()
                self.illegal_position_confirmed = True
                self.motion_detected = False
                self.stable_counter = 0
                self.previous_frame = board.copy()
                return True
        else:
            if debug:
                print(f"Illegal position from frame {self.illegal_candidate_frame} rejected")
            self.clear_illegal_candidate()
            self.illegal_candidate_rejected = True
            self.waiting_after_rejected_illegal = True
            self.motion_detected = False
            self.stable_counter = 0

        self.previous_frame = board.copy()
        return False

    def clear_illegal_candidate(self):
        self.illegal_candidate_board = None
        self.illegal_candidate_frame = None
        self.illegal_confirmation_counter = 0

    def wait_for_motion(self, board, frame_number, motion_ratio, debug):
        if not is_board_stable(motion_ratio):
            self.waiting_after_rejected_illegal = False
            self.motion_detected = True
            self.stable_counter = 0

            if debug:
                print(f"Motion detected after rejected illegal position at frame {frame_number}")

        self.previous_frame = board.copy()
        return False

    def process_pending_position(self, board, frame_number, debug):
        self.confirmation_counter += 1

        if self.confirmation_counter < self.confirmation_frames:
            self.previous_frame = board.copy()
            return False

        pending_motion = calculate_motion_ratio(self.pending_board, board)
        if is_board_stable(pending_motion):
            if debug:
                print(f"Stable position confirmed at frame {frame_number}")

            self.clear_pending_position()

            self.motion_detected = False
            self.stable_counter = 0
            self.previous_frame = board.copy()
            return True

        if debug:
            print(f"Pending position from frame {self.pending_frame_number} rejected")

        self.clear_pending_position()
        self.motion_detected = True
        self.stable_counter = 0
        self.previous_frame = board.copy()
        return False

    def clear_pending_position(self):
        self.pending_board = None
        self.pending_frame_number = None
        self.confirmation_counter = 0

    def process_normal_frame(self, board, frame_number, motion_ratio, debug):
        if is_board_stable(motion_ratio):
            self.stable_counter += 1
        else:
            self.motion_detected = True
            self.stable_counter = 0

        #  initial board
        if not self.initial_board_saved and is_move_finished(self.stable_counter):
            self.initial_board_saved = True
            if debug:
                print(f"Initial board saved at frame {frame_number}")
            self.previous_frame = board.copy()
            return True

        #  possibly finished movement
        if self.motion_detected and is_move_finished(self.stable_counter):
            self.pending_board = board.copy()
            self.pending_frame_number = frame_number
            self.confirmation_counter = 0

            if debug:
                print(f"Pending stable position at frame {frame_number}")

        self.previous_frame = board.copy()
        return False

    def start_illegal_confirmation(self, board, frame_number):
        self.illegal_candidate_board = board.copy()
        self.illegal_candidate_frame = frame_number
        self.illegal_confirmation_counter = 0
        self.illegal_position_confirmed = False
        self.illegal_candidate_rejected = False
