
def get_move_candidates(changes, board_state, top_squares=5):
    changed_squares = sorted(
        changes.items(),
        key=lambda x: x[1]["motion_ratio"],
        reverse=True
    )[:top_squares]

    candidates = []

    for source_name, source_analysis in changed_squares:
        if not board_state.is_occupied(source_name):
            continue

        for destination_name, destination_analysis in changed_squares:
            if destination_name == source_name:
                continue

            score = (
                source_analysis["motion_ratio"]
                + destination_analysis["motion_ratio"]
                + 0.001 * abs(destination_analysis["edge_change"])
            )
            if board_state.is_occupied(destination_name):
                move_type = "capture"
            else:
                move_type = "normal"

            candidate = (
                source_name,
                destination_name,
                score,
                move_type)
            candidates.append(candidate)

    candidates.sort(
        key=lambda x: x[2],
        reverse=True
    )  # sort by score in descending order
    return candidates


def resolve_capture_direction(square1, square2, current_board, get_empty_difference, board_state):
    legal1 = board_state.is_move_legal(square1, square2)
    legal2 = board_state.is_move_legal(square2, square1)
    if legal1 and not legal2:
        return square1, square2
    elif not legal1 and legal2:
        return square2, square1

    diff1 = get_empty_difference(square1, current_board)
    diff2 = get_empty_difference(square2, current_board)

    if diff1 is not None and diff2 is not None:
        if abs(diff1 - diff2) > 0.05:
            if diff1 < diff2:
                return square1, square2
            else:
                return square2, square1
    return None, None


def detect_move(changes, board_state, current_board, get_empty_difference):
    #  check for castling
    source, destination, move_type = detect_castling(changes, board_state)
    if source is not None:
        return source, destination, move_type

    #  check for en passant
    source, destination, move_type = detect_en_passant(changes, board_state)
    if source is not None:
        return source, destination, move_type

    #  check for normal move and capture
    candidates = get_move_candidates(changes, board_state)
    if not candidates:
        return None, None, None

    for source, destination, _, move_type in candidates:
        if move_type == "normal":
            return source, destination, move_type

        if move_type == "capture":
            resolved_source, resolved_destination = resolve_capture_direction(source, destination, current_board, get_empty_difference, board_state)
            if resolved_source is not None:
                return resolved_source, resolved_destination, move_type
    return None, None, None


def detect_castling(changes, board_state):
    castling_moves = [
        ("E1", "G1", ["E1", "F1", "G1", "H1"]),
        ("E1", "C1", ["A1", "C1", "D1", "E1"]),
        ("E8", "G8", ["E8", "F8", "G8", "H8"]),
        ("E8", "C8", ["A8", "C8", "D8", "E8"]),
    ]
    for source, destination, squares in castling_moves:
        if not board_state.is_move_legal(source, destination):
            continue
        changed_count = 0
        for square in squares:
            if changes[square]["motion_ratio"] >= 0.10:
                changed_count += 1
        if changed_count >= 3:
            return source, destination, "castling"
    return None, None, None


def detect_en_passant(changes, board_state):
    for move in board_state.chess_board.legal_moves:
        if not board_state.chess_board.is_en_passant(move):
            continue
        source = move.uci()[:2].upper()
        destination = move.uci()[2:4].upper()
        source_motion = changes[source]["motion_ratio"]
        destination_motion = changes[destination]["motion_ratio"]
        if source_motion > 0.10 and destination_motion > 0.10:
            return source, destination, "en passant"
    return None, None, None
