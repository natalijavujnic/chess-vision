import cv2
from visualization.display_utils import draw_centered_text


def select_board_corners(frame):
    points = []

    corner_names = [
        "SELECT TOP LEFT CORNER",
        "SELECT TOP RIGHT CORNER",
        "SELECT BOTTOM RIGHT CORNER",
        "SELECT BOTTOM LEFT CORNER"
    ]

    def refresh_display():
        display = frame.copy()
        if len(points) < 4:
            draw_centered_text(display, corner_names[len(points)])

        for index, point in enumerate(points):
            cv2.circle(display, point, 6, (0, 0, 255), -1)
            cv2.putText(
                display,
                str(index + 1),
                (point[0] + 10, point[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 0, 255),
                2
            )
        cv2.imshow("Select board corners", display)

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(points) < 4:
            points.append((x, y))
            refresh_display()

    refresh_display()
    cv2.setMouseCallback("Select board corners", mouse_callback)

    while len(points) < 4:
        cv2.waitKey(1)

    cv2.destroyAllWindows()
    return points

