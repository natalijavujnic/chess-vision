import cv2
import numpy as np

from image.image_utils import grayscale, canny
from motion.motion_utils import calculate_motion_ratio


class SquareAnalyzer:
    def analyze(self, previous_square, current_square):
        previous_square = crop_center(previous_square)
        current_square = crop_center(current_square)

        motion_ratio = calculate_motion_ratio(previous_square, current_square)

        previous_gray = grayscale(previous_square)
        current_gray = grayscale(current_square)
        brightness_change = np.mean(current_gray) - np.mean(previous_gray)

        previous_edges = canny(previous_gray)
        current_edges = canny(current_gray)
        edge_change = cv2.countNonZero(current_edges) - cv2.countNonZero(previous_edges)

        return {
            "motion_ratio": motion_ratio,  # percentage of changed pixels
            "brightness_change": brightness_change,  # difference in average brightness
            "edge_change": edge_change  # difference in detected edges
        }


def crop_center(square, margin=0.2):
    height, width = square.shape[:2]

    x1 = int(width * margin)
    x2 = int(width * (1 - margin))
    y1 = int(height * margin)
    y2 = int(height * (1 - margin))

    return square[y1:y2, x1:x2]
