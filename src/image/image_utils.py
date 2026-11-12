import cv2
import numpy as np


def grayscale(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


def gaussian_blur(frame, kernel_size=(5, 5)):
    return cv2.GaussianBlur(frame, kernel_size, 0)


def binary_threshold(gray_frame, threshold_value=127):
    _, binary_frame = cv2.threshold(
        gray_frame,
        threshold_value,
        255,
        cv2.THRESH_BINARY
    )
    return binary_frame


def canny(frame, threshold1=100, threshold2=200):
    return cv2.Canny(frame, threshold1, threshold2)


def hough_lines(edges, rho=1, theta=np.pi / 180, threshold=100, min_line_length=100, max_line_gap=20):
    return cv2.HoughLinesP(
        edges,
        rho=rho,
        theta=theta,
        threshold=threshold,
        minLineLength=min_line_length,
        maxLineGap=max_line_gap
    )
