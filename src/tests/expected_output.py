
#  basic moves, captures and checkmate
test1 = [
    ("D2", "D4"),
    ("F7", "F5"),
    ("C1", "G5"),
    ("H7", "H6"),
    ("G5", "H4"),
    ("G7", "G5"),
    ("E2", "E4"),
    ("G5", "H4"),  # capture
    ("D1", "H5"),  # checkmate
]

#  basic moves and captures
test2 = [
    ("E2", "E4"),
    ("E7", "E5"),
    ("G1", "F3"),
    ("B8", "C6"),
    ("F1", "B5"),
    ("A7", "A6"),
    ("B5", "C6"),  # capture
    ("D7", "C6"),  # capture
    ("D2", "D4"),
    ("E5", "D4"),  # capture
    ("F3", "D4"),  # capture
    ("G8", "F6"),
    ("B1", "C3"),
    ("F8", "B4"),
    ("D1", "D3"),
    ("C8", "E6"),
    ("C1", "F4"),
    ("D8", "E7"),
    ("A2", "A3"),
    ("B4", "C3"),  # capture + check
    ("D3", "C3"),  # capture
    ("F6", "E4"),  # capture
    ("D4", "C6"),  # capture
    ("B7", "C6"),  # capture
    ("C3", "C6"),  # capture + check
    ("E8", "F8"),
]

#  special moves: castling, en passant and promotion
test3 = [
    ("E2", "E4"),
    ("C7", "C5"),
    ("G1", "F3"),
    ("D7", "D6"),
    ("F1", "E2"),
    ("C8", "G4"),
    ("E1", "G1"),  # kingside castling: rook H1 -> F1
    ("G8", "H6"),
    ("D2", "D4"),
    ("C5", "D4"),  # capture
    ("C2", "C4"),
    ("E7", "E6"),
    ("E4", "E5"),
    ("F7", "F5"),
    ("E5", "F6"),  # en passant: pawn on F5 is removed
    ("G7", "F6"),  # capture
    ("C4", "C5"),
    ("B8", "D7"),
    ("C5", "C6"),
    ("A7", "A6"),
    ("C6", "C7"),
    ("H8", "G8"),
    ("C7", "C8"),  # promotion to queen
    ("E6", "E5"),
    ("C8", "C2")
]

#  realistic game: basic moves, capture and castling
test4 = [
    ("E2", "E4"),
    ("E7", "E5"),
    ("G1", "F3"),
    ("B8", "C6"),
    ("F1", "C4"),
    ("G8", "F6"),
    ("D2", "D3"),
    ("F8", "C5"),
    ("E1", "G1"),  # kingside castling: rook H1 -> F1
    ("D7", "D6"),
    ("C2", "C3"),
    ("E8", "G8"),  # kingside castling: rook H8 -> F8
    ("B2", "B4"),
    ("C5", "B6"),
    ("A2", "A4"),
    ("A7", "A6"),
    ("B1", "D2"),
    ("C8", "E6"),
    ("C4", "E6"),  # capture
    ("F7", "E6"),  # capture
    ("D2", "B3"),
    ("D8", "E7"),
    ("A4", "A5"),
    ("B6", "A7"),
    ("B4", "B5"),
    ("A6", "B5"),  # capture
]

#  short game with check and checkmate
test5 = [
    ("E2", "E4"),
    ("E7", "E5"),
    ("G1", "F3"),
    ("D7", "D6"),
    ("F1", "C4"),
    ("C8", "G4"),
    ("B1", "C3"),
    ("B8", "C6"),
    ("F3", "E5"),  # capture
    ("G4", "D1"),  # capture
    ("C4", "F7"),  # capture + check
    ("E8", "E7"),
    ("C3", "D5"),  # checkmate
]

#  illegal game
test6 = [
    ("E2", "E4"),
    ("E7", "E5"),
    # ("G1", "G3"),  # illegal knight movement
    # ("G3", "G1"),  # return knight
    ("G1", "F3"),
    ("B8", "C6"),
    # ("E4", "E7"),  # illegal pawn movement
    # ("E7", "E4"),  # return pawn
    ("F1", "C4"),
    ("G8", "F6"),
    # ("F3", "F5"),  # illegal knight movement
    # ("F5", "F3"),  # return knight
    ("D2", "D3"),
    ("F8", "C5"),
]
