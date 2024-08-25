import cv2
import numpy as np
from tkinter import filedialog, Tk
import matplotlib.pyplot as plt

def detect_template(main_image, template_image_path):
    """
    Detect the template in the main image and return the center of the detected template.

    Args:
        main_image (numpy.ndarray): The image in which the template is to be detected.
        template_image_path (str): Path to the template image.

    Returns:
        tuple: Coordinates of the center of the detected template in the form (center_x, center_y).

    Example:
        center = detect_template(main_image, template_image_path)
        print(f"Center of the detected template: {center}")
    """
    template_image = cv2.imread(template_image_path)

    if main_image is None or template_image is None:
        print("Error: Unable to read one of the images.")
        return None

    # Perform template matching
    result = cv2.matchTemplate(main_image, template_image, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Extract the location and size of the detected template
    top_left = max_loc
    h, w = template_image.shape[:2]

    # Define the four corners of the detected template
    points = [
        (top_left[0], top_left[1]),
        (top_left[0] + w, top_left[1]),
        (top_left[0] + w, top_left[1] + h),
        (top_left[0], top_left[1] + h)
    ]

    # Find the center by calculating the average of the coordinates
    center = find_center(points)
    return center

def find_center(points):
    """
    Calculate the center of a rectangle defined by four points.

    Args:
        points (list): A list of four tuples representing the coordinates of the corners.

    Returns:
        tuple: Coordinates of the center (center_x, center_y).
    """
    if len(points) != 4:
        raise ValueError("Exactly four points are required to define a rectangle.")

    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = points

    center_x = (x1 + x2 + x3 + x4) / 4
    center_y = (y1 + y2 + y3 + y4) / 4

    return (center_x, center_y)

# Example usage:
if __name__ == "__main__":
    # Select main image and template image
    main_image_path = "path_to_main_image.jpg"
    template_image_path = "path_to_template_image.jpg"

    main_image = cv2.imread(main_image_path)
    center = detect_template(main_image, template_image_path)
    print(f"Center of the detected template: {center}")
