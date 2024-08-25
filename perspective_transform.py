import cv2
import numpy as np

def rectify_quadrilateral_area(src_img, src_points, output_width=800):
    """
    Extracts and rectifies the quadrilateral area defined by src_points from the source image.

    Parameters:
    - src_img: The source image from which to extract the quadrilateral.
    - src_points: A list of four (x, y) tuples representing the corners of the quadrilateral.
                  The points should be in the order [top-left, top-right, bottom-right, bottom-left].
    - output_width: Desired width of the output rectified image. The height will be calculated based on the quadrilateral's aspect ratio.

    Returns:
    - rectified_img: The rectified image where the quadrilateral has been transformed to a rectangle.
    """

    # Calculate the height of the quadrilateral to maintain aspect ratio
    width_top = np.linalg.norm(src_points[0] - src_points[1])
    width_bottom = np.linalg.norm(src_points[2] - src_points[3])
    height_left = np.linalg.norm(src_points[0] - src_points[3])
    height_right = np.linalg.norm(src_points[1] - src_points[2])

    # Calculate the aspect ratio of the quadrilateral
    quad_width = (width_top + width_bottom) / 2
    quad_height = (height_left + height_right) / 2
    aspect_ratio = quad_height / quad_width

    # Calculate output height to maintain the aspect ratio
    output_height = int(output_width * aspect_ratio)

    # Destination points for the perspective transformation
    dst_points = np.array([[0, 0], [output_width - 1, 0],
                           [output_width - 1, output_height - 1], [0, output_height - 1]], dtype=np.float32)

    # Compute the perspective transform matrix
    M = cv2.getPerspectiveTransform(src_points.astype(np.float32), dst_points)

    # Apply the perspective transformation to rectify the image
    rectified_img = cv2.warpPerspective(src_img, M, (output_width, output_height))

    return rectified_img

def compute_perspective_transform(src_img, src_points, output_width=800):
    """
    Compute the perspective transform matrix and apply it to the source image to rectify it.

    Parameters:
    - src_img: The source image to be rectified.
    - src_points: A list of four (x, y) tuples representing the corners of the area to rectify.
    - output_width: The desired width of the output rectified image.

    Returns:
    - rectified_img: The rectified image where the area has been transformed to a rectangle.
    - M: The perspective transform matrix.
    """
    # Calculate the width and height of the quadrilateral
    width_top = np.sqrt(((src_points[1][0] - src_points[0][0]) ** 2) + ((src_points[1][1] - src_points[0][1]) ** 2))
    width_bottom = np.sqrt(((src_points[2][0] - src_points[3][0]) ** 2) + ((src_points[2][1] - src_points[3][1]) ** 2))
    width_avg = (width_top + width_bottom) / 2

    height_left = np.sqrt(((src_points[3][0] - src_points[0][0]) ** 2) + ((src_points[3][1] - src_points[0][1]) ** 2))
    height_right = np.sqrt(((src_points[2][0] - src_points[1][0]) ** 2) + ((src_points[2][1] - src_points[1][1]) ** 2))
    height_avg = (height_left + height_right) / 2

    # Maintain aspect ratio
    aspect_ratio = width_avg / height_avg
    output_height = int(output_width / aspect_ratio)

    dst_points = np.float32([[0, 0], [output_width, 0], [output_width, output_height], [0, output_height]])
    M = cv2.getPerspectiveTransform(np.float32(src_points), dst_points)
    rectified_img = cv2.warpPerspective(src_img, M, (output_width, output_height))

    return rectified_img, M

def apply_inverse_perspective_transform(processed_img, M, original_img, src_points):
    """
    Applies the inverse perspective transformation to return the rectified image to its original shape.

    Parameters:
    - processed_img: The processed (rectified) image after applying the perspective transformation.
    - M: The perspective transformation matrix obtained from the rectification process.
    - original_img: The original image before rectification.
    - src_points: The source points used for the original perspective transformation.

    Returns:
    - result: The image after applying the inverse perspective transformation to return to the original shape.
    """
    # Calculate the inverse of the perspective transformation matrix
    inv_M = np.linalg.inv(M)

    # Apply the inverse perspective transformation to return to the original shape
    result = cv2.warpPerspective(processed_img, inv_M, (original_img.shape[1], original_img.shape[0]))

    # Overlay the original image on top of the result to preserve non-rectified areas
    mask = np.zeros_like(original_img)
    cv2.fillConvexPoly(mask, src_points.astype(int), (255, 255, 255))
    result = cv2.bitwise_and(result, mask)
    result += original_img

    return result

def process_rectified_image(rectified_img):
    """
    Perform desired operations on the rectified image.

    Parameters:
    - rectified_img: The rectified image to process.

    Returns:
    - processed_img: The processed image.
    """
    # Placeholder function for processing the rectified image
    processed_img = rectified_img.copy()

    return processed_img

from tkinter import filedialog, Tk, Label, Button
from PIL import Image, ImageTk

def select_image():
    """
    Opens a file dialog for the user to select an image file.

    Returns:
    - img: The selected image object.
    """
    file_path = filedialog.askopenfilename(title="Select Image File", filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp")])
    if file_path:
        img = Image.open(file_path)
        img = img.resize((400, 300), Image.ANTIALIAS)  # Resize image with antialiasing
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk
        return img
    return None

def main():
    """
    The main function that sets up the Tkinter interface for selecting and displaying an image.
    """
    global label  # Define label as a global variable
    root = Tk()
    root.title("Image Rectification")
    root.geometry("400x350")

    label = Label(root, text="Step 1: Upload an image", padx=10, pady=10)
    label.pack()

    def upload_image():
        """
        Handles the image upload process, updating the interface with the selected image.
        """
        global original_img
        original_img = select_image()
        if original_img is None:
            label.config(text="Error: No image selected.")
        else:
            label.config(text="Image uploaded successfully.")

    upload_button = Button(root, text="Upload Image", command=upload_image)
    upload_button.pack()

    root.mainloop()

if __name__ == "__main__":
    main()
