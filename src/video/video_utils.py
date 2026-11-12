import cv2


def get_video_info(video_path):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise Exception(f"Could not open video source: {video_path}.")

    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))

    duration = 0
    if fps > 0:
        duration = frame_count / fps

    video.release()

    return {
        "fps": fps,
        "frame_count": frame_count,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "duration": duration,
    }


def get_frame(video_path, frame_number=0):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise Exception(f"Could not open video source: {video_path}.")

    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    success, frame = video.read()
    video.release()
    if not success:
        raise Exception(f"Frame {frame_number} does not exist.")

    return frame


def iterate_frames(video_path):
    video = cv2.VideoCapture(video_path)
    if not video.isOpened():
        raise Exception(f"Could not open video source: {video_path}.")

    frame_number = 0
    try:
        while True:
            success, frame = video.read()
            if not success:
                break

            yield frame_number, frame
            frame_number += 1
    finally:
        video.release()

