from tests.chess_vision_pipeline_test import ChessVisionPipelineTest
from tests.expected_output import test1, test2, test3, test4, test5, test6

EXPECTED_MOVES = test2
VIDEO_PATH = "../videos/test2.mp4"


def main():

    test = ChessVisionPipelineTest(VIDEO_PATH, EXPECTED_MOVES)
    test.run()
    #  test.test_board_extraction(debug=True, debug_detection=False)
    #  test.test_stable_positions(show_positions=True)
    #  test.test_game_analyzer(debug=True, show_frames=False, debug_movement=False)
    #  test.show_motion_detection_example(15, 100, 135)


if __name__ == "__main__":
    main()
