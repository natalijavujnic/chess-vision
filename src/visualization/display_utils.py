import cv2
from motion.motion_utils import calculate_motion_mask
from board.board_utils import get_square_position


def show_frame(frame, window_name="Frame", destroy=True):
    cv2.imshow(window_name, frame)
    cv2.waitKey(0)
    if destroy:
        cv2.destroyAllWindows()


def draw_centered_text(frame, text):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    thickness = 2

    # text dimensions
    (text_width, text_height), _ = cv2.getTextSize(
        text,
        font,
        font_scale,
        thickness
    )

    # frame center
    frame_height, frame_width = frame.shape[:2]
    x = (frame_width - text_width) // 2
    y = (frame_height - text_height) // 2

    cv2.putText(
        frame,
        text,
        (x, y),
        font,
        font_scale,
        (0, 255, 0),
        thickness
    )


def draw_board_grid(board):
    board_with_grid = board.copy()
    board_size = board.shape[0]
    square_size = board_size // 8

    for i in range(9):
        position = i * square_size

        cv2.line(
            board_with_grid,
            (position, 0),
            (position, board_size),
            (0, 0, 255),
            2
        )

        cv2.line(
            board_with_grid,
            (0, position),
            (board_size, position),
            (0, 0, 255),
            2
        )

    return board_with_grid


def draw_detected_corners(frame, corners):
    result = frame.copy()
    for corner in corners:
        cv2.circle(result, corner, 8, (0, 0, 255), -1)
    return result


def draw_detected_lines(frame, horizontal_lines, vertical_lines):
    result = frame.copy()

    for line in horizontal_lines:
        cv2.line(
            result,
            (line["x1"], line["y1"]),
            (line["x2"], line["y2"]),
            (0, 0, 255),
            2
        )

    for line in vertical_lines:
        cv2.line(
            result,
            (line["x1"], line["y1"]),
            (line["x2"], line["y2"]),
            (255, 0, 0),
            2
        )

    return result


def draw_line_positions(frame, horizontal_positions, vertical_positions):
    result = frame.copy()
    height, width = frame.shape[:2]

    for y in horizontal_positions:
        cv2.line(
            result,
            (0, int(y)),
            (width, int(y)),
            (0, 0, 255),
            2
        )

    for x in vertical_positions:
        cv2.line(
            result,
            (int(x), 0),
            (int(x), height),
            (255, 0, 0),
            2
        )

    return result


def draw_board_grid_positions(frame, horizontal_grid, vertical_grid):
    result = frame.copy()
    height, width = frame.shape[:2]

    if horizontal_grid is not None:
        for y in horizontal_grid:
            cv2.line(
                result,
                (0, int(y)),
                (width, int(y)),
                (0, 0, 255),
                3
            )
    if vertical_grid is not None:
        for x in vertical_grid:
            cv2.line(
                result,
                (int(x), 0),
                (int(x), height),
                (255, 0, 0),
                3
            )

    return result


def show_motion_mask(previous_frame, current_frame):
    motion_mask = calculate_motion_mask(previous_frame, current_frame)
    show_frame(motion_mask, "Motion mask")


def draw_changed_squares(board, changes, white_at_top, top_squares=5):
    result = board.copy()
    square_size = board.shape[0] // 8

    changed_squares = sorted(
        changes.items(),
        key=lambda x: x[1]["motion_ratio"],
        reverse=True
    )[:top_squares]
    for square_name, analysis in changed_squares:
        row, col = get_square_position(square_name, white_at_top)
        x1 = col * square_size
        y1 = row * square_size
        x2 = x1 + square_size
        y2 = y1 + square_size

        cv2.rectangle(result, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(
            result,
            f"{square_name} {analysis['motion_ratio']:.3f}",
            (x1 + 5, y1 + 18),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.45,
            (0, 0, 255),
            1
        )

    return result


def print_move_candidates(candidates, limit=10):
    for source, destination, score, move_type in candidates[:limit]:
        print(f"{source} -> {destination} | {move_type} | {score:.4f}")


def draw_move_squares(board, source, destination, white_at_top, blue=False):
    marked_board = board.copy()
    square_size = board.shape[0] // 8
    for square_name, label in [(source, "FROM"), (destination, "TO")]:
        row, col = get_square_position(square_name, white_at_top)
        x1 = col * square_size
        y1 = row * square_size
        x2 = x1 + square_size
        y2 = y1 + square_size

        cv2.rectangle(marked_board, (x1, y1), (x2, y2), (0, 0, 255) if not blue else (255, 0, 0), 4)
        cv2.putText(
            marked_board,
            label,
            (x1 + 5, y1 + 25),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255) if not blue else (255, 0, 0),
            2
        )
    return marked_board


def draw_single_square(board, square_name, label, white_at_top):
    marked_board = board.copy()
    square_size = board.shape[0] // 8
    row, col = get_square_position(square_name, white_at_top)
    x1 = col * square_size
    y1 = row * square_size
    x2 = x1 + square_size
    y2 = y1 + square_size

    cv2.rectangle(marked_board, (x1, y1), (x2, y2), (255, 0, 0), 4)
    cv2.putText(
        marked_board,
        label,
        (x1 + 5, y1 + 25),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        (255, 0, 0),
        2
    )

    return marked_board


def draw_square_names(board, white_at_top):
    result = board.copy()
    height, width = result.shape[:2]

    square_height = height // 8
    square_width = width // 8

    for letter in "ABCDEFGH":
        for number in range(1, 9):
            square_name = f"{letter}{number}"

            row, col = get_square_position(
                square_name,
                white_at_top
            )

            x = col * square_width + 8
            y = row * square_height + 22

            cv2.putText(
                result,
                square_name,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 255),
                1,
                cv2.LINE_AA
            )

    return result
