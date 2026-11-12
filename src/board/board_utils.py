import cv2
import numpy as np


def warp_board(frame, corners, board_size=800):
    source_points = np.float32(corners)
    destination_points = np.float32([
        [0, 0],
        [board_size - 1, 0],
        [board_size - 1, board_size - 1],
        [0, board_size - 1]
    ])

    transformation_matrix = cv2.getPerspectiveTransform(
        source_points,
        destination_points
    )

    warped_board = cv2.warpPerspective(
        frame,
        transformation_matrix,
        (board_size, board_size)
    )

    return warped_board


def split_board(board, white_at_top):
    """
    white at top
    H1 G1 ... A1
    H2 G2 ... A2
    ...
    H8 G8 ... A8

    black at top
    A8 B8 ... H8
    A7 B7 ... H7
    ...
    A1 B1 ... H1
    """
    squares = {}
    square_size = board.shape[0] // 8

    if white_at_top:
        letters = "HGFEDCBA"
    else:
        letters = "ABCDEFGH"

    for row in range(8):
        for col in range(8):
            x1 = col * square_size
            x2 = x1 + square_size
            y1 = row * square_size
            y2 = y1 + square_size

            square = board[y1:y2, x1:x2]
            if white_at_top:
                rank = row + 1
            else:
                rank = 8 - row
            square_name = f"{letters[col]}{rank}"
            squares[square_name] = square

    return squares


def get_square_position(square_name, white_at_top):
    if white_at_top:
        letters = "HGFEDCBA"
        col = letters.index(square_name[0])
        row = int(square_name[1]) - 1
    else:
        letters = "ABCDEFGH"
        col = letters.index(square_name[0])
        row = 8 - int(square_name[1])
    return row, col


def get_square_color(square_name):
    row, col = get_square_position(square_name, True)
    return (row + col) % 2


def are_squares_adjacent(square1, square2):
    file1 = ord(square1[0]) - ord("A")
    rank1 = int(square1[1])
    file2 = ord(square2[0]) - ord("A")
    rank2 = int(square2[1])
    return abs(file1 - file2) <= 1 and abs(rank1 - rank2) <= 1
