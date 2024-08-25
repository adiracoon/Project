import cv2
import numpy as np

def draw_lines(image, lines):
    """
    Draws lines on the provided image with different colors.

    Args:
        image (numpy.ndarray): The image on which to draw the lines.
        lines (list): A list of lines, each represented by its endpoints [(x1, y1, x2, y2), ...].

    Returns:
        numpy.ndarray: The image with drawn lines.
    """
    # Define a list of colors in BGR format
    colors = [
        (0, 0, 255),  # Red
        (0, 255, 0),  # Green
        (255, 0, 0),  # Blue
        (0, 255, 255),  # Yellow
    ]

    # Draw each line in the list with a different color
    for i, line in enumerate(lines):
        x1, y1, x2, y2 = line
        color = colors[i % len(colors)]  # Cycle through colors
        cv2.line(image, (x1, y1), (x2, y2), color, 2)

    return image


def draw_representative_lines(image, representative_lines):
    """
    Draw representative lines on the image.

    Args:
        image (numpy.ndarray): The image on which to draw the lines.
        representative_lines (list): List of lines represented as ((x1, y1), (x2, y2)).

    Returns:
        None
    """
    for line in representative_lines:
        (x1, y1), (x2, y2) = line
        cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 3)  # Green lines


def find_intersection_points(lines):
    """
    Finds the intersection points between pairs of lines.

    Args:
        lines (list): List of lines, each represented as [(x1, y1, x2, y2)].

    Returns:
        list: List of intersection points as (x, y) tuples.
    """
    intersection_points = []

    # Iterate through all pairs of lines to find intersection points
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            x1, y1, x2, y2 = lines[i][0]
            x3, y3, x4, y4 = lines[j][0]

            # Calculate the denominator for the intersection formula
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if denom == 0:
                continue  # Lines are parallel; no intersection

            # Calculate the intersection point
            px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
            py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

            # Check if the intersection point lies within both line segments
            if min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2) and \
                    min(x3, x4) <= px <= max(x3, x4) and min(y3, y4) <= py <= max(y3, y4):
                intersection_points.append((int(px), int(py)))

    return intersection_points


def draw_intersection_points(image, points):
    """
    Draws circles at intersection points on the given image.

    Args:
        image (numpy.ndarray): The image on which to draw the points.
        points (list): List of points represented as (x, y) tuples.

    Returns:
        None
    """
    for point in points:
        cv2.circle(image, point, radius=5, color=(0, 255, 0), thickness=-1)  # Green circles

