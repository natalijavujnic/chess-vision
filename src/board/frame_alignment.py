import cv2
import numpy as np

from image.image_utils import grayscale


def align_frame(reference_frame, current_frame):
    reference_gray = grayscale(reference_frame)
    current_gray = grayscale(current_frame)
    warp_matrix = np.eye(2, 3, dtype=np.float32)

    criteria = (
        cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,
        50,
        1e-5
    )

    _, warp_matrix = cv2.findTransformECC(
        reference_gray,
        current_gray,
        warp_matrix,
        cv2.MOTION_EUCLIDEAN,
        criteria
    )

    aligned_frame = cv2.warpAffine(
        current_frame,
        warp_matrix,
        (reference_frame.shape[1], reference_frame.shape[0]),
        flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP
    )

    return aligned_frame

