import cv2
from image.image_utils import grayscale, binary_threshold
from video.video_utils import iterate_frames


def calculate_motion_mask(previous_frame, current_frame, threshold_value=25):
    difference = cv2.absdiff(previous_frame, current_frame)
    gray_difference = grayscale(difference)
    motion_mask = binary_threshold(gray_difference, threshold_value)
    return motion_mask


def calculate_motion_ratio(previous_frame, current_frame, threshold_value=25):
    motion_mask = calculate_motion_mask(previous_frame, current_frame, threshold_value)
    changed_pixels = cv2.countNonZero(motion_mask)
    total_pixels = motion_mask.size
    return changed_pixels / total_pixels


def is_board_stable(motion_ratio, threshold=0.001):
    return motion_ratio < threshold


def is_move_finished(stable_counter, required_frames=15):
    return stable_counter == required_frames


def find_first_stable_frame(video_path):
    previous_frame = None
    stable_counter = 0

    for frame_number, frame in iterate_frames(video_path):
        if previous_frame is None:
            previous_frame = frame
            continue

        motion_ratio = calculate_motion_ratio(previous_frame, frame)
        if is_board_stable(motion_ratio):
            stable_counter += 1
        else:
            stable_counter = 0
        if is_move_finished(stable_counter):
            return frame.copy(), frame_number
        previous_frame = frame.copy()

    print("No stable frame detected.")
    return None, None

