# Chess Vision

**Computer vision system for automatic chessboard analysis and chess move recognition from video.**

Chess Vision processes video recordings of a physical chess game and automatically reconstructs the sequence of played moves. Instead of visually classifying every chess piece in every frame, the system tracks changes between stable board positions and combines computer vision with the current game state and chess rules to determine the most likely move.

The project was developed as part of a Bachelor's thesis at the University of Belgrade, School of Electrical Engineering.

---

## Overview

The system takes a video of a physical chessboard recorded from above and processes it through several stages:

1. Detect the first stable board position.
2. Locate the chessboard in the video frame.
3. Apply a perspective transformation to obtain a normalized top-down board view.
4. Determine the orientation of the board.
5. Monitor the video for movement and detect stable board positions.
6. Align frames to reduce the effect of small camera movements.
7. Compare consecutive stable board states.
8. Identify the squares that changed.
9. Generate candidate chess moves.
10. Validate candidates using the current game state and chess rules.
11. Update the internal board state and continue processing the game.

This approach avoids the need for direct chess-piece classification. The system assumes a standard initial chess position and reconstructs the game by tracking valid moves over time.

---

## Features

- Automatic chessboard detection from video
- Perspective correction and board extraction
- Automatic board orientation detection
- Division of the board into individual chess squares
- Motion detection and stable-position detection
- Frame alignment for small camera shifts
- Square-level board change analysis
- Chess move candidate generation
- Legal move validation using the current game state
- Internal reconstruction of the chess position
- Temporal confirmation of detected board states
- Handling of temporarily detected illegal positions

The move detection pipeline supports:

- Normal moves
- Captures
- Castling
- En passant
- Pawn promotion

---

## How It Works

### 1. Chessboard Detection

The first stable frame is used to locate the chessboard.

The image is converted to grayscale, blurred and processed using Canny edge detection. A Hough transform is then used to detect horizontal and vertical lines.

Detected lines are grouped and filtered to identify the regular 9 × 9 line structure of a chessboard. The four outer lines are fitted and intersected to determine the board corners.

Once the corners are known, a perspective transformation converts the board into a normalized square image.

---

### 2. Board Orientation

After extracting the board, the system determines its orientation so that image coordinates can be mapped correctly to chess-square names such as `E2`, `E4` or `G8`.

The normalized board can then be divided into 64 individual square images.

---

### 3. Motion and Stable Position Detection

Move recognition is not performed on every video frame.

The system first detects movement on the board. After movement stops, it waits for the board to remain stable before considering the position as a candidate new chess state.

A candidate stable position is additionally confirmed using subsequent frames. This helps prevent a hand, moving piece or other temporary visual change from being interpreted as a completed move.

---

### 4. Frame Alignment

Even with a stationary camera, small shifts can occur between frames.

Before comparing board positions, the current frame is aligned with the reference frame using OpenCV's Enhanced Correlation Coefficient (ECC) image alignment.

This reduces false differences caused by camera movement rather than chess-piece movement.

---

### 5. Board Change Analysis

The current stable board is compared with the previous stable board.

For every square, the system analyzes visual changes and ranks the squares according to how strongly they changed.

The most significant changed squares are then used as input for move detection.

---

### 6. Move Detection

Move candidates are generated from the most significantly changed squares.

Candidate scoring combines visual information from the source and destination squares. Additional analysis of empty-square references helps determine whether pieces have left or entered particular squares.

Rather than relying only on image differences, candidate moves are evaluated together with the current internal chess position.

---

### 7. Chess Rule Validation

The system maintains an internal representation of the game using `python-chess`.

Each detected candidate is checked against the legal moves available in the current position.

If the move is legal, the internal board state is updated and processing continues from the new position.

This combination of computer vision and chess rules helps resolve ambiguous visual changes and prevents many invalid detections from being accepted as real moves.

---

### 8. Illegal Position Confirmation

A visually detected move that is not legal is not immediately accepted as a new board state.

Instead, the system waits for additional frames to determine whether the position persists.

If the board changes again, the candidate is rejected as a temporary position. If the same illegal position remains stable long enough, it is confirmed as the new physical board state so that processing can continue.

This mechanism is useful when players temporarily move pieces, correct a position or create visual states that do not correspond to a completed legal move.

---

## Architecture

The project is divided into modules according to the individual stages of the computer vision pipeline:

```text
src/
├── board/
│   ├── board_comparison.py
│   ├── board_detection.py
│   ├── board_utils.py
│   ├── frame_alignment.py
│   └── square_analyzer.py
│
├── game/
│   ├── board_state.py
│   ├── game_analyzer.py
│   └── move_detection.py
│
├── image/
│   └── image_utils.py
│
├── motion/
│   ├── motion_utils.py
│   └── move_detector.py
│
├── tests/
│   ├── chess_vision_pipeline_test.py
│   └── expected_output.py
│
├── video/
│   └── video_utils.py
│
├── visualization/
│   ├── board_selection.py
│   └── display_utils.py
│
└── main.py
```

### `board`

Responsible for chessboard detection and board-level image processing.

It includes board extraction, perspective transformation, square mapping, frame alignment and comparison of individual squares between stable positions.

### `motion`

Determines when activity occurs on the board and when a new stable position has been reached.

It also performs additional temporal confirmation before a candidate position is passed to the game-analysis stage.

### `game`

Contains the main chess-move reconstruction logic.

`GameAnalyzer` connects motion detection, frame alignment, board comparison and move detection.

`BoardState` maintains the current chess position and validates moves using chess rules.

### `image`

Contains reusable low-level image-processing utilities used by the board-detection pipeline.

### `video`

Handles reading and iterating through video frames.

### `visualization`

Contains utilities used to visualize intermediate processing results, detected board geometry and recognized moves during development and testing.

### `tests`

Contains end-to-end pipeline tests using recorded chess games with known expected move sequences.

---

## Technologies

The project is implemented in **Python** and primarily uses:

- **OpenCV** — image processing, line detection, perspective transformation and frame alignment
- **NumPy** — numerical and image-array operations
- **python-chess** — chess position representation and legal move validation

---

## Installation

Clone the repository:

```bash
git clone https://github.com/natalijavujnic/chess-vision.git
cd chess-vision
```

Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Project

The current entry point is:

```bash
python src/main.py
```

The project includes predefined test scenarios that process recorded chess games and compare the detected move sequence with the expected results.

Test videos are stored locally in the `videos/` directory and are not included in the repository.

---

## Testing

The end-to-end test pipeline is implemented in:

```text
src/tests/chess_vision_pipeline_test.py
```

Expected move sequences used for testing are defined in:

```text
src/tests/expected_output.py
```

The test pipeline processes a recorded chess game through the main stages of the system:

```text
Video
  ↓
First stable frame
  ↓
Chessboard detection
  ↓
Board extraction and orientation
  ↓
Motion / stable-position detection
  ↓
Frame alignment
  ↓
Board comparison
  ↓
Move detection
  ↓
Chess-rule validation
  ↓
Detected move sequence
```

The detected moves are then compared with the expected move sequence for the selected test scenario.

Individual parts of the pipeline can also be visualized during development, including board detection, stable positions, frame alignment and before/after states of detected moves.


---

## Design Approach

A central design decision of Chess Vision is to **avoid direct chess-piece classification**.

Recognizing every piece independently would require the system to handle different chess sets, viewing conditions, piece shapes and visual appearances.

Instead, Chess Vision starts from the known standard chess position and maintains an internal game state. Computer vision determines **where the physical board changed**, while chess rules determine **which move can explain that change**.

This creates a hybrid approach:

```text
Computer Vision
      +
Temporal Analysis
      +
Chess Rules
      ↓
Move Recognition
```

---

## Current Assumptions and Limitations

The current implementation is designed around several assumptions:

- The game starts from the standard chess starting position.
- The complete chessboard is visible in the video.
- The camera observes the board primarily from above.
- The board can be detected from its grid structure.
- Moves are reconstructed sequentially, so the internal board state depends on previously detected moves.
- Large visual or camera changes may affect board comparison.
- The current implementation focuses on move reconstruction rather than visual classification of individual chess pieces.

---

## Bachelor Thesis

This project was developed as part of the Bachelor's thesis:

**Recognition of Chess Moves from Video Using Computer Vision**

University of Belgrade  
School of Electrical Engineering  
Belgrade, Serbia — 2026

The thesis explores the design and implementation of the complete computer-vision pipeline used to detect a physical chessboard, analyze changes over time and reconstruct chess moves from video.

---

## Author

**Natalija Vujnić**

University of Belgrade  
School of Electrical Engineering