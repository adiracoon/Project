import cv2
import numpy as np

def preprocess_image(image_path):
    """
    Convert the image to grayscale and apply Gaussian blur to reduce noise and detail.

    Args:
        image_path (str): The path to the image file.

    Returns:
        tuple: A tuple containing the blurred grayscale image and the original image.
    """
    image = np.copy(cv2.imread(image_path))  # Load the image and make a copy
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)  # Apply Gaussian blur
    return blurred, image

def detect_edges(image):
    """
    Detect the edges in a given image using the Canny edge detection algorithm.

    Args:
        image (numpy.ndarray): The preprocessed grayscale image.

    Returns:
        numpy.ndarray: The edges detected in the image.
    """
    return cv2.Canny(image, 50, 150)  # Apply Canny edge detection with specified thresholds
