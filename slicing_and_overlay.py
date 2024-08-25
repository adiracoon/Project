import math
import cv2
import numpy as np
from Hang_a_Picture_on_slice import run_slices

# Define a minimum width percentage for slices
SLICE_MIN_WIDTH_PERCENT = 0.15

def detect_vertical_lines(edges):
    """
    Detect vertical lines in the image using the probabilistic Hough Line Transform.

    Parameters:
    - edges: The edge-detected image (usually obtained via Canny edge detection).

    Returns:
    - lines: A list of lines detected in the image, where each line is represented by its endpoints (x1, y1, x2, y2).
    """
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=50, minLineLength=30, maxLineGap=10)
    return lines

def find_approximately_vertical_lines(lines, img_width, angle_threshold_rad=np.deg2rad(5)):
    """
    Filter and identify lines that are approximately vertical from the detected lines.

    Parameters:
    - lines: The list of lines detected in the image.
    - img_width: The width of the image.
    - angle_threshold_rad: The angle threshold in radians for classifying a line as vertical.

    Returns:
    - start_end_points: A list of start and end points of vertical lines.
    """
    if len(lines) == 0:
        return None

    vertical_lines = []
    for line in lines:
        for x1, y1, x2, y2 in line:
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1))
            if np.pi / 2 - angle_threshold_rad < angle < np.pi / 2 + angle_threshold_rad:
                avg_x = (x1 + x2) / 2
                vertical_lines.append(avg_x)

    vertical_lines_sorted = sorted(vertical_lines)

    filtered_lines = []
    min_spacing = img_width * SLICE_MIN_WIDTH_PERCENT
    last_x = 0

    for x in vertical_lines_sorted:
        if not filtered_lines or (x - last_x) >= min_spacing:
            filtered_lines.append(x)
            last_x = x
        if len(filtered_lines) >= 7:
            break

    # Convert filtered lines to start and end points
    start_end_points = []
    for x in filtered_lines:
        start_end_points.append(((int(x), 0), (int(x), img_width)))

    return start_end_points

def apply_colored_slices(image, lines, alpha=0.3):
    """
    Apply colored slices on the image based on the provided vertical lines.

    Parameters:
    - image: The original image on which slices will be applied.
    - lines: The vertical lines that define the slices.
    - alpha: The transparency level for the colored overlay.

    Returns:
    - "./assets/numbered_slices.jpg": The path to the saved image with numbered slices.
    - valid_slices: A list of valid slices defined by their start and end x-coordinates.
    - slice_info: Information about each slice including its number and coordinates.
    """
    SLICE_MIN_WIDTH_PERCENT = 0.15
    img_width = image.shape[1]
    min_slice_width = img_width * SLICE_MIN_WIDTH_PERCENT

    # Debugging: Print initial state
    print("Initial Image Width:", img_width)
    print("Minimum Slice Width:", min_slice_width)
    print("Lines for slicing:", lines)

    if not lines or len(lines) == 1:
        print("No vertical lines detected or only one line. Treating the entire image as a single slice.")
        cv2.rectangle(image, (0, 0), (img_width, image.shape[0]), (180, 130, 70), -1)
        cv2.addWeighted(image, alpha, image, 1 - alpha, 0, image)
        cv2.putText(image, '1', (img_width // 2 - 10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 100), 3)
        cv2.imwrite("./assets/numbered_slices.jpg", image)
        return "./assets/numbered_slices.jpg", [((0, 0), (img_width, 0))], [(1, (0, 0), (img_width, image.shape[0]))]

    print("Debug lines structure:", lines)
    ending_x = image.shape[1]

    colors = [(180, 130, 70), (130, 180, 70), (70, 130, 180), (180, 180, 70)]  # Adjusted colors
    color_index = 0

    last_x = 0
    slice_info = []  # Store slice information
    valid_lines = []

    # First, filter valid lines
    for line in lines:
        start_x = last_x
        end_x = line[0][0]
        slice_width = end_x - start_x

        # Enforce minimum slice width
        if slice_width >= min_slice_width:
            valid_lines.append(line)
            last_x = end_x

    # Debugging: Print valid lines
    print("Valid lines after filtering:", valid_lines)

    # Now handle merging and rendering slices
    last_x = 0
    valid_slices = []
    for i, line in enumerate(valid_lines):
        start_x = last_x
        end_x = line[0][0]
        slice_width = end_x - start_x

        print(f"Slice {i + 1}: StartX = {start_x}, EndX = {end_x}, Width = {slice_width}")  # Test line

        overlay = image.copy()
        cv2.rectangle(overlay, (start_x, 0), (end_x, image.shape[0]), colors[color_index], -1)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        # Place number in the middle of the slice
        mid_point_x = (start_x + end_x) // 2
        cv2.putText(image, str(len(slice_info) + 1), (mid_point_x - 10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 100), 3)

        # Debugging: Print number position
        print(f"Number {len(slice_info) + 1} placed at X = {mid_point_x - 10}")

        # Store slice information
        slice_info.append((len(slice_info) + 1, (start_x, 0), (end_x, image.shape[0])))
        valid_slices.append((start_x, end_x))
        last_x = end_x
        color_index = (color_index + 1) % len(colors)

    # Handle the last slice if necessary
    if last_x < ending_x:
        print(f"Handling the last slice from {last_x} to {ending_x}")
        overlay = image.copy()
        cv2.rectangle(overlay, (last_x, 0), (ending_x, image.shape[0]), colors[color_index], -1)
        cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0, image)

        # Place number in the middle of the last slice
        mid_point_x = (last_x + ending_x) // 2
        cv2.putText(image, str(len(slice_info) + 1), (mid_point_x - 10, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (100, 100, 100), 3)

        # Debugging: Print number position for last slice
        print(f"Number {len(slice_info) + 1} placed at X = {mid_point_x - 10} (last slice)")

        # Store slice information
        slice_info.append((len(slice_info) + 1, (last_x, 0), (ending_x, image.shape[0])))
        valid_slices.append((last_x, ending_x))

    # Save the image with numbered slices
    cv2.imwrite("./assets/numbered_slices.jpg", image)
    print("Slices numbered and saved as 'numbered_slices.jpg'.")
    print("Final slice information:", slice_info)
    print("Final valid slices:", valid_slices)

    return "./assets/numbered_slices.jpg", valid_slices, slice_info  # Return slice information
