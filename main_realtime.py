import time
import numpy as np
import cv2
from grid_class import draw_grid_on_slice
from take_a_picture import run_take_a_picture
from cam_scanner import run_camscanner_realtime, run_camscanner
from choose_image_to_hang import choose_image_to_hang
from perspective_transform import compute_perspective_transform, apply_inverse_perspective_transform
from image_preprocessing import preprocess_image, detect_edges
from detect_img_center_online import detect_template
from slicing_and_overlay import detect_vertical_lines, find_approximately_vertical_lines, apply_colored_slices
from line_detection import detect_lines
from line_processing import classify_lines, select_most_representative_line
from user_crop_interface import run_crop_interface
from frame_capture import run_initial_capture
from lines_intersection_points import draw_intersection_points, find_intersection_points
from voice_guidance import provide_voice_instruction


def capture_frame(vid):
    """
    Capture a single frame from the video source.

    Args:
        vid: The video capture object.

    Returns:
        The captured frame or None if capturing failed.
    """
    ret, frame = vid.read()
    if ret:
        return frame
    return None


def order_points(pts):
    """
    Order points in top-left, top-right, bottom-right, bottom-left order.

    Args:
        pts: A numpy array of points.

    Returns:
        A numpy array of ordered points.
    """
    pts = np.array(pts, dtype="float32")
    xSorted = pts[np.argsort(pts[:, 0]), :]
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost
    rightMost = rightMost[np.argsort(rightMost[:, 1]), :]
    (tr, br) = rightMost
    return np.array([tl, tr, br, bl], dtype="float32")


def detect_and_classify_lines(image):
    """
    Detect and classify lines in the image.

    Args:
        image: The input image.

    Returns:
        Top, bottom, left, and right classified lines.
    """
    edges = detect_edges(image)
    lines = detect_lines(edges)
    margin = 5

    width = image.shape[1]
    height = image.shape[0]
    global image_lines
    image_lines.append(((margin, margin, width - margin, margin),))
    image_lines.append(((margin, height - margin, width - margin, height - margin),))
    image_lines.append(((margin, margin, margin, height - margin),))
    image_lines.append(((width - margin, margin, width - margin, height - margin),))
    if lines is None:
        width = image.shape[1]
        height = image.shape[0]
        lines = []
        lines.append(((margin, margin, width - margin, margin),))
        lines.append(((margin, height - margin, width - margin, height - margin),))
        lines.append(((margin, margin, margin, height - margin),))
        lines.append(((width - margin, margin, width - margin, height - margin),))
    top, bottom, left, right = classify_lines(lines, image.shape)
    return top, bottom, left, right


image_lines = []


def save_result(image, result_path):
    """
    Save the processed image to the specified path.

    Args:
        image: The image to be saved.
        result_path: The path where the image will be saved.
    """
    cv2.imwrite(result_path, image)


def draw_result_with_intersection_points(image, intersection_points):
    """
    Draw intersection points on the image.

    Args:
        image: The input image.
        intersection_points: The points to be drawn.

    Returns:
        The image with intersection points drawn.
    """
    draw_intersection_points(image, intersection_points)
    return image


def rectify_image(image, ordered_points):
    """
    Rectify the image using the perspective transform.

    Args:
        image: The input image.
        ordered_points: Points used for the transformation.

    Returns:
        The transformation matrix and the rectified image.
    """
    rectified_img, M = compute_perspective_transform(image, np.array(ordered_points, dtype=np.float32))
    cv2.imwrite("./assets/rectified_image.jpg", rectified_img)
    return M, rectified_img


def rectify_image2(image, ordered_points):
    """
    Rectify the image using the perspective transform without saving it.

    Args:
        image: The input image.
        ordered_points: Points used for the transformation.

    Returns:
        The transformation matrix and the rectified image.
    """
    rectified_img, M = compute_perspective_transform(image, np.array(ordered_points, dtype=np.float32))
    return M, rectified_img


def slice_image_and_apply_colored_slices(rectified_img, image_path):
    """
    Slice the image and apply colored slices to it.

    Args:
        rectified_img: The rectified image.
        image_path: Path to the image.

    Returns:
        The sliced image with colored slices applied.
    """
    rectified_img = cv2.imread("assets/rectified_image.jpg")
    img_width = rectified_img.shape[1]
    gray = cv2.cvtColor(rectified_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = detect_vertical_lines(edges)
    vertical_lines = find_approximately_vertical_lines(lines, img_width)
    return apply_colored_slices(rectified_img, vertical_lines)


def draw_lines(image, lines, color=(0, 255, 0), thickness=2):
    """
    Draw lines on the image.

    Args:
        image: The image on which to draw.
        lines: List of lines to draw.
        color: Color of the lines.
        thickness: Thickness of the lines.

    Returns:
        The image with lines drawn.
    """
    for line in lines:
        if line is not None:
            x1, y1, x2, y2 = line[0]
            cv2.line(image, (x1, y1), (x2, y2), color, thickness)
    return image


def validate_and_get_points(ordered_points, frame_shape):
    """
    Validate the ordered points to form a logical rectangle, return default if invalid.

    Args:
        ordered_points: List of points.
        frame_shape: Shape of the frame (height, width).

    Returns:
        Validated points or default points.
    """
    frame_height, frame_width = frame_shape
    default_points = [(10, 10), (frame_width - 10, 10), (frame_width - 10, frame_height - 10), (10, frame_height - 10)]

    if len(ordered_points) != 4:
        return default_points

    def is_connected_shape(points):
        def cross_product(o, a, b):
            return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

        cp1 = cross_product(ordered_points[0], ordered_points[1], ordered_points[2])
        cp2 = cross_product(ordered_points[1], ordered_points[2], ordered_points[3])
        cp3 = cross_product(ordered_points[2], ordered_points[3], ordered_points[0])
        cp4 = cross_product(ordered_points[3], ordered_points[0], ordered_points[1])

        return (cp1 * cp3 <= 0) and (cp2 * cp4 <= 0)

    def is_point_in_quadrant(point, quadrant):
        x, y = point
        if quadrant == 0:  # Top-left
            return 0 <= x < frame_width // 2 and 0 <= y < frame_height // 2
        elif quadrant == 1:  # Top-right
            return frame_width // 2 <= x < frame_width and 0 <= y < frame_height // 2
        elif quadrant == 2:  # Bottom-right
            return frame_width // 2 <= x < frame_width and frame_height // 2 <= y < frame_height
        elif quadrant == 3:  # Bottom-left
            return 0 <= x < frame_width // 2 and frame_height // 2 <= y < frame_height

    quadrants = [0, 1, 2, 3]
    for point, quadrant in zip(ordered_points, quadrants):
        if not is_point_in_quadrant(point, quadrant):
            return default_points

    if not is_connected_shape(ordered_points):
        return default_points

    return ordered_points


def draw_green_frame(image, center, crop_dims):
    """
    Draw a green rectangle frame on the image around the center point.

    Args:
        image: The image on which to draw.
        center: The center point of the rectangle (tuple of x, y coordinates).
        crop_dims: The dimensions of the rectangle (width, height).

    Returns:
        Image with the green rectangle frame drawn.
    """
    w, h = crop_dims
    x, y = int(center[0]), int(center[1])
    top_left = (x - w // 2, y - h // 2)
    bottom_right = (x + w // 2, y + h // 2)

    # Draw a rectangle with a fluorescent green color
    cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)
    return image


def main():
    """
    Main function to run the real-time picture hanging assistant.

    Steps include:
    - Capturing an image of the wall.
    - Preprocessing the image and detecting lines.
    - Rectifying the image and slicing it for grid overlay.
    - Selecting a point on the grid for hanging the picture.
    - Running real-time feedback using the camera to guide the user to the correct hanging position.
    """
    # Step 1: Take a picture of the wall
    image_path = run_take_a_picture()

    # Step 2: Load and preprocess the image
    original_image = np.copy(cv2.imread(image_path))
    copy_image = np.copy(original_image)
    preprocessed_image, original_image = preprocess_image(image_path)

    # Step 3: Detect and classify lines in the image
    top, bottom, left, right = detect_and_classify_lines(preprocessed_image)

    # Step 4: Select the most representative lines
    lines_groups = [top, bottom, left, right]
    representative_lines = select_most_representative_line(lines_groups, preprocessed_image.shape)
    for i in range(len(representative_lines)):
        if representative_lines[i] is None:
            representative_lines[i] = image_lines[i]

    # Step 5: Find intersection points of the representative lines
    intersection_points = find_intersection_points(representative_lines)

    # Step 6: Verify borders using CamScanner and rectify the image
    intersection_points = run_camscanner_realtime(image_path, intersection_points)
    ordered_points = order_points(intersection_points)
    M, rectified_img = rectify_image(copy_image, ordered_points)

    # Step 7: Save the rectified image
    result_path = "./assets/BIG_RECT.jpg"
    save_result(rectified_img, result_path)

    # Step 8: Slice the rectified image and apply colored slices
    sliced_pic, lines, slices_data = slice_image_and_apply_colored_slices(rectified_img, image_path)

    # Step 9: Select a point on the grid
    selected_point, _ = draw_grid_on_slice(sliced_pic, lines)

    # Step 10: Run the initial capture interface to get a new image with the user holding the picture
    new_capture_path = run_initial_capture()

    # Step 11: Rectify the new capture using the ordered points
    new_capture_image = cv2.imread(new_capture_path)
    _, rectified_new_capture = rectify_image(new_capture_image, ordered_points)

    # Step 12: Save the rectified capture
    rectified_capture_path = "./assets/rectified_capture.jpg"
    save_result(rectified_new_capture, rectified_capture_path)

    # Step 13: Run the cropping interface for the user to crop the rectified capture
    external_crop_path, internal_crop_path = run_crop_interface(rectified_capture_path)

    # Step 14: Get crop dimensions for visual rendering
    crop_dims = get_image_dimensions(external_crop_path)

    # Step 15: Open the video capture for real-time alignment guidance
    video_source = 0  # Default camera
    vid = cv2.VideoCapture(video_source)
    if not vid.isOpened():
        raise ValueError("Unable to open video source", video_source)

    while True:
        current_frame = capture_frame(vid)  # Capture a frame
        if current_frame is None:
            continue

        _, rectified_frame = rectify_image2(current_frame, ordered_points)
        detected_center = detect_template(rectified_frame, internal_crop_path)

        if detected_center:
            dx = detected_center[0] - selected_point.x
            dy = detected_center[1] - selected_point.y

            if abs(dx) < 1 and abs(dy) < 1:  # Threshold for alignment
                provide_voice_instruction("You've come to the right location!")
                break
            elif dx > 0:
                provide_voice_instruction("Move left")
            else:
                provide_voice_instruction("Move right")

            if dy > 0:
                provide_voice_instruction("Move up")
            else:
                provide_voice_instruction("Move down")
        else:
            print("No template detected. Retrying...")

        # Draw green frame around the selected center point
        rectified_frame = draw_green_frame(rectified_frame, (selected_point.x, selected_point.y), crop_dims)

        # Display the frame
        cv2.imshow("Streaming with Green Frame", rectified_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
