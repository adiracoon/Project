import numpy as np

# Constants
ANGLE_THRESHOLD = np.deg2rad(30)  # Tolerance for considering lines parallel
POSITION_THRESHOLD = 0.4  # 40% from the sides for identifying relevant lines
MIN_LINE_LENGTH_RATIO = 0.3  # Minimum line length as a ratio of the image dimension

def extend_line(line, img_shape):
    """
    Extends a line to the borders of the image.

    Args:
        line (array-like): Line coordinates in the format [x1, y1, x2, y2].
        img_shape (tuple): Shape of the image (height, width).

    Returns:
        list: Extended line coordinates to the image borders.
    """
    if line is None or len(line) == 0:
        return None
    x1, y1, x2, y2 = line[0]
    if x1 == x2:  # Vertical line
        return [[x1, 0, x2, img_shape[0] - 1]]
    elif y1 == y2:  # Horizontal line
        return [[0, y1, img_shape[1] - 1, y2]]
    else:
        # Calculate slope and intercept
        slope = (y2 - y1) / (x2 - x1) if x2 != x1 else float('inf')
        if slope == float('inf'):  # Handle vertical lines
            return [[x1, 0, x2, img_shape[0] - 1]]
        intercept = y1 - slope * x1
        # Extend to the image borders
        y_at_x0 = intercept
        y_at_xmax = slope * (img_shape[1] - 1) + intercept
        x_at_y0 = (0 - intercept) / slope if slope != 0 else 0
        x_at_ymax = ((img_shape[0] - 1) - intercept) / slope if slope != 0 else img_shape[1] - 1
        return [[int(x_at_y0), 0, int(x_at_ymax), img_shape[0] - 1]]

def average_angle(lines):
    """
    Calculates the average angle of a list of lines.

    Args:
        lines (list): List of lines, each represented by its coordinates.

    Returns:
        float: The average angle in radians.
    """
    angles = [np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]) for line in lines]
    return np.mean(angles)

def filter_lines_by_angle(lines, avg_angle):
    """
    Filters lines by their angle proximity to a given average angle.

    Args:
        lines (list): List of lines to filter.
        avg_angle (float): The average angle to compare against.

    Returns:
        list: Filtered list of lines close to the average angle.
    """
    angle_threshold = np.pi / 36  # 5-degree threshold for angle proximity
    return [line for line in lines if np.isclose(np.arctan2(line[0][3] - line[0][1], line[0][2] - line[0][0]), avg_angle, atol=angle_threshold)]

def line_length(line):
    """
    Calculates the length of a line segment.

    Args:
        line (array-like): Line coordinates in the format [x1, y1, x2, y2].

    Returns:
        float: Length of the line segment.
    """
    x1, y1, x2, y2 = line[0]
    return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def classify_lines(lines, img_shape):
    """
    Classifies lines into top, bottom, left, and right categories based on their position.

    Args:
        lines (list): List of lines to classify.
        img_shape (tuple): Shape of the image (height, width).

    Returns:
        tuple: Lists of top, bottom, left, and right lines.
    """
    center_x, center_y = img_shape[1] // 2, img_shape[0] // 2
    top, bottom, left, right = [], [], [], []

    upper_limit = img_shape[0] * 0.2  # Top 20% of the image
    lower_limit = img_shape[0] * 0.8  # Bottom 20% of the image
    left_limit = img_shape[1] * 0.2  # Left 20% of the image
    right_limit = img_shape[1] * 0.8  # Right 20% of the image

    for line in lines:
        x1, y1, x2, y2 = line[0]

        if abs(x2 - x1) > abs(y2 - y1):  # Horizontal lines
            if (y1 + y2) / 2 < center_y and (y1 + y2) / 2 <= upper_limit:
                top.append(line)
            elif (y1 + y2) / 2 >= lower_limit:
                bottom.append(line)
        else:  # Vertical lines
            if (x1 + x2) / 2 < center_x and (x1 + x2) / 2 <= left_limit:
                left.append(line)
            elif (x1 + x2) / 2 >= right_limit:
                right.append(line)

    if len([top, bottom, left, right]) == 3:
        print("Only three lines found. Attempting to infer the missing line.")

    return top, bottom, left, right

def line_angle(line):
    """
    Calculates the angle of a line in radians.

    Args:
        line (array-like): Line coordinates in the format [x1, y1, x2, y2].

    Returns:
        float: Angle of the line in radians.
    """
    x1, y1, x2, y2 = line[0]
    return np.arctan2(y2 - y1, x2 - x1)

def are_lines_parallel(line1, line2):
    """
    Checks if two lines are parallel based on their angles.

    Args:
        line1, line2 (array-like): Lines to compare.

    Returns:
        bool: True if lines are parallel within the threshold, False otherwise.
    """
    return abs(line_angle(line1) - line_angle(line2)) <= ANGLE_THRESHOLD

def select_most_representative_line(lines_group, img_shape):
    """
    Selects the most representative line from a group by considering parallelism and average angle.

    Args:
        lines_group (list): Group of lines to select from.
        img_shape (tuple): Shape of the image (height, width).

    Returns:
        list: Selected and extended line.
    """
    selected_lines = []
    for lines in lines_group:
        if not lines:
            selected_lines.append(None)
            continue

        parallel_pairs = []
        for i in range(len(lines)):
            for j in range(i + 1, len(lines)):
                if are_lines_parallel(lines[i], lines[j]):
                    parallel_pairs.append((lines[i], lines[j]))
                    break
            if parallel_pairs:
                break

        if parallel_pairs:
            avg_angle = average_angle(lines)
            representative_line = min(parallel_pairs[0], key=lambda line: abs(line_angle(line) - avg_angle))
        else:
            avg_angle = average_angle(lines)
            lines_close_to_avg_angle = filter_lines_by_angle(lines, avg_angle)
            if not lines_close_to_avg_angle:
                lines_close_to_avg_angle = lines
            representative_line = lines_close_to_avg_angle[0]

        extended_line = extend_line(representative_line, img_shape)
        selected_lines.append(extended_line)

    return selected_lines
