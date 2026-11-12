import cv2
import numpy as np
from itertools import combinations
from image.image_utils import grayscale, gaussian_blur, canny, hough_lines
from visualization.display_utils import (
    show_frame, draw_detected_lines, draw_line_positions,
    draw_board_grid_positions, draw_detected_corners)
from board.square_analyzer import crop_center


def detect_board_corners(frame, debug=False):
    horizontal_lines, vertical_lines = detect_board_lines(frame, debug=debug)

    if debug:
        detected_lines = draw_detected_lines(frame, horizontal_lines, vertical_lines)
        show_frame(detected_lines, "1. Hough lines")

    horizontal_groups = merge_lines(horizontal_lines, "y")
    vertical_groups = merge_lines(vertical_lines, "x")
    height, width = frame.shape[:2]

    horizontal_positions = filter_line_groups(horizontal_groups, "y", width, min_coverage_ratio=0.2)
    vertical_positions = filter_line_groups(vertical_groups, "x", height, min_coverage_ratio=0.3)

    horizontal_positions = insert_missing_lines(horizontal_positions)
    vertical_positions = insert_missing_lines(vertical_positions)

    if debug:
        print("Horizontal positions: ", horizontal_positions)
        print("Vertical positions: ", vertical_positions)
        merged_lines = draw_line_positions(frame, horizontal_positions, vertical_positions)
        show_frame(merged_lines, "2. Merged lines")

    horizontal_grid = find_board_grid(horizontal_positions)
    vertical_grid = find_board_grid(vertical_positions)

    if debug:
        print("Horizontal grid: ", horizontal_grid)
        print("Vertical grid: ", vertical_grid)
        grid_frame = draw_board_grid_positions(frame, horizontal_grid, vertical_grid)
        show_frame(grid_frame, "3. Detected grid")

    if horizontal_grid is None or vertical_grid is None:
        print("Board detection failed: grid not found.")
        return None

    top_line = fit_grid_line(horizontal_lines, "y", horizontal_grid[0])
    bottom_line = fit_grid_line(horizontal_lines, "y", horizontal_grid[-1])
    left_line = fit_grid_line(vertical_lines, "x", vertical_grid[0])
    right_line = fit_grid_line(vertical_lines, "x", vertical_grid[-1])

    if top_line is None or bottom_line is None or left_line is None or right_line is None:
        print("Board detection failed: outer lines could not be fitted.")
        return None

    corners = [
        intersect_lines(top_line, left_line),
        intersect_lines(top_line, right_line),
        intersect_lines(bottom_line, right_line),
        intersect_lines(bottom_line, left_line)
    ]

    if debug:
        corners_frame = draw_detected_corners(frame, corners)
        show_frame(corners_frame, "4. Detected corners")

    return corners


def detect_board_lines(frame, debug=False):
    gray = grayscale(frame)
    blur = gaussian_blur(gray)
    edges = canny(blur, threshold1=50, threshold2=150)

    if debug:
        show_frame(edges, "0. Canny edges")

    lines = hough_lines(edges)

    horizontal = []
    vertical = []
    if lines is None:
        print("Board detection failed: no Hough lines detected.")
        return horizontal, vertical

    for x1, y1, x2, y2 in lines.reshape(-1, 4):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        angle = abs(np.degrees(np.arctan2(dy, dx)))
        if angle <= 10 or angle >= 170:
            horizontal.append(normalize_horizontal(x1, y1, x2, y2))
        elif 80 <= angle <= 100:
            vertical.append(normalize_vertical(x1, y1, x2, y2))
    return horizontal, vertical


def normalize_horizontal(x1, y1, x2, y2):
    return {
        "y": (y1 + y2) / 2,
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2
    }


def normalize_vertical(x1, y1, x2, y2):
    return {
        "x": (x1 + x2) / 2,
        "x1": x1,
        "y1": y1,
        "x2": x2,
        "y2": y2
    }


def merge_lines(lines, axis, threshold=10):
    if not lines:
        return []
    lines = sorted(
        lines,
        key=lambda current_line: current_line[axis]
    )

    groups = [[lines[0]]]
    for line in lines[1:]:
        current = groups[-1]
        group_position = sum(group[axis] for group in current) / len(current)

        if abs(line[axis] - group_position) <= threshold:
            current.append(line)
        else:
            groups.append([line])

    return groups


def insert_missing_lines(positions, min_spacing=50, tolerance_ratio=0.15):
    positions = sorted(positions)
    if len(positions) < 2:
        return positions

    distances = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]

    valid_distances = [d for d in distances if d >= min_spacing]
    if not valid_distances:
        return positions

    typical_distance = np.median(valid_distances)
    result = [positions[0]]
    for i, distance in enumerate(distances):
        if abs(distance - 2 * typical_distance) <= typical_distance * tolerance_ratio:
            missing_position = (positions[i] + positions[i + 1]) / 2
            result.append(missing_position)
        result.append(positions[i + 1])
    return result


def find_board_grid(positions, grid_size=9, tolerance_ratio=0.15, min_spacing=50):
    positions = sorted(positions)
    best_grid = None
    best_error = None

    for candidate in combinations(positions, grid_size):
        distances = [candidate[i + 1] - candidate[i] for i in range(grid_size - 1)]

        #  ignore very small gaps
        if any(d < min_spacing for d in distances):
            continue

        typical_distance = np.median(distances)
        tolerance = typical_distance * tolerance_ratio

        if not all(abs(d - typical_distance) <= tolerance for d in distances):
            continue

        error = sum(abs(d - typical_distance) for d in distances)
        if best_error is None or error < best_error:
            best_grid = list(candidate)
            best_error = error

    '''
    for start in range(len(positions) - grid_size + 1):
        candidate = positions[start:start + grid_size]
        distances = [candidate[i + 1] - candidate[i] for i in range(grid_size - 1)]
        avg = sum(distances) / len(distances)
        tolerance = avg * tolerance_ratio
        error = sum(abs(d - avg) for d in distances)
        if all(abs(d - avg) <= tolerance for d in distances):
            if best_error is None or error < best_error:
                best_grid = candidate
                best_error = error
    '''
    return best_grid


def fit_grid_line(lines, axis, position, threshold=10):
    points = []
    for line in lines:
        if abs(line[axis] - position) <= threshold:
            points.append([line["x1"], line["y1"]])
            points.append([line["x2"], line["y2"]])
    if len(points) < 2:
        return None

    points = np.array(points, dtype=np.float32)
    vx, vy, x, y = cv2.fitLine(points, cv2.DIST_L2, 0, 0.01, 0.01).flatten()
    return vx, vy, x, y


def intersect_lines(line1, line2):
    vx1, vy1, x1, y1 = line1
    vx2, vy2, x2, y2 = line2

    matrix = np.array([[vx1, -vx2], [vy1, -vy2]])
    vector = np.array([x2 - x1, y2 - y1])
    t, _ = np.linalg.solve(matrix, vector)

    x = x1 + t * vx1
    y = y1 + t * vy1
    return int(round(x)), int(round(y))


def calculate_line_coverage(group, axis):
    intervals = []

    for line in group:
        if axis == "y":
            #  horizontal line
            start = min(line["x1"], line["x2"])
            end = max(line["x1"], line["x2"])
        else:
            #  vertical line
            start = min(line["y1"], line["y2"])
            end = max(line["y1"], line["y2"])

        intervals.append((start, end))

    intervals.sort()
    start, end = intervals[0]
    coverage = 0
    for s, e in intervals[1:]:
        if s <= end:
            end = max(end, e)
        else:
            coverage += end - start
            start = s
            end = e
    coverage += end - start
    return coverage


def filter_line_groups(groups, axis, frame_size, min_coverage_ratio=0.3):
    positions = []
    minimum_coverage = frame_size * min_coverage_ratio

    for group in groups:
        coverage = calculate_line_coverage(group, axis)
        if coverage < minimum_coverage:
            continue
        position = sum(g[axis] for g in group) / len(group)
        positions.append(position)

    return positions


def detect_white_at_top(board):
    height, width = board.shape[:2]
    square_height = height // 8
    square_width = width // 8
    top_brightness = []
    bottom_brightness = []

    for col in range(8):
        #  top pieces
        for row in [0, 1]:
            square = board[
                row * square_height:(row + 1) * square_height,
                col * square_width:(col + 1) * square_width
            ]
            center = crop_center(square)
            gray = grayscale(center)
            top_brightness.append(np.mean(gray))

        #  bottom pieces
        for row in [6, 7]:
            square = board[
                     row * square_height:(row + 1) * square_height,
                     col * square_width:(col + 1) * square_width
                     ]
            center = crop_center(square)
            gray = grayscale(center)
            bottom_brightness.append(np.mean(gray))

    top = np.mean(top_brightness)
    bottom = np.mean(bottom_brightness)
    return top > bottom
