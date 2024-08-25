import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import pyttsx3


class CropInterface:
    """
    CropInterface is a class that provides a GUI to manually crop an image at two stages:
    1. Cropping the external borders (including the frame).
    2. Cropping the internal borders (excluding the frame).

    Attributes:
    - root: The Tkinter root window.
    - image_path: Path to the image to be cropped.
    - external_path: Path where the cropped external image will be saved.
    - internal_path: Path where the cropped internal image will be saved.
    - image: The image loaded using OpenCV.
    - pil_image: The image converted to PIL format.
    - tk_image: The image converted to Tkinter format.
    - stage: Indicates whether the current stage is external or internal cropping.
    - instructions: List of instructions for the current stage.
    - canvas: The canvas where the image and cropping rectangle will be displayed.
    - rect: Rectangle representing the selected cropping area.
    - start_x, start_y, end_x, end_y: Coordinates for the cropping area.
    - crop_button: Button to confirm the cropping area.
    - crop_button_window: The window for the crop button on the canvas.

    Methods:
    - __init__: Initializes the interface, loads the image, and sets up the canvas.
    - speak: Uses text-to-speech to vocalize the instructions.
    - show_instructions: Displays and vocalizes the instructions for the current stage.
    - on_button_press: Handles the event when the mouse button is pressed to start selecting the cropping area.
    - on_mouse_drag: Handles the event when the mouse is dragged to adjust the cropping area.
    - on_button_release: Handles the event when the mouse button is released to finalize the cropping area.
    - on_done: Handles the event when the "Done" button is pressed to save the cropped area and proceed to the next stage.
    - run_next_stage: Initiates the next stage of cropping.
    """

    def __init__(self, root, image_path, external_path, internal_path, stage):
        self.root = root
        self.root.title("Manual Crop Interface")
        self.image_path = image_path
        self.external_path = external_path
        self.internal_path = internal_path
        self.image = cv2.imread(image_path)
        self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.pil_image = Image.fromarray(self.image)
        self.tk_image = ImageTk.PhotoImage(self.pil_image)

        self.stage = stage
        self.instructions = [
            "Mark the outer borders of the image, including the frame, and then press DONE.",
            "Mark the internal borders of the image, not including the image frame, and then press DONE."
        ]

        self.canvas = tk.Canvas(root, width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None

        self.crop_button = tk.Button(root, text="Done", command=self.on_done)
        self.crop_button_window = self.canvas.create_window(50, 40, anchor=tk.SE, window=self.crop_button)

        self.show_instructions()

    def speak(self, text):
        """
        Uses the pyttsx3 library to vocalize the provided text.
        Args:
        - text: The text to vocalize.
        """
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def show_instructions(self):
        """
        Displays and vocalizes the instructions for the current cropping stage.
        """
        self.speak(self.instructions[self.stage])
        instruction_label = tk.Label(self.root, text=self.instructions[self.stage], font=("Helvetica", 12))
        instruction_label.pack(anchor=tk.N)

    def on_button_press(self, event):
        """
        Starts the cropping area selection when the mouse button is pressed.
        Args:
        - event: The event object containing the mouse position.
        """
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')
        print(f"Button Pressed: start_x={self.start_x}, start_y={self.start_y}")

    def on_mouse_drag(self, event):
        """
        Adjusts the cropping area as the mouse is dragged.
        Args:
        - event: The event object containing the current mouse position.
        """
        cur_x, cur_y = event.x, event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)
        print(f"Dragging: cur_x={cur_x}, cur_y={cur_y}")

    def on_button_release(self, event):
        """
        Finalizes the cropping area when the mouse button is released.
        Args:
        - event: The event object containing the mouse position at release.
        """
        self.end_x = event.x
        self.end_y = event.y
        print(f"Button Released: end_x={self.end_x}, end_y={self.end_y}")

    def on_done(self):
        """
        Saves the cropped area based on the selected coordinates and either advances to the next stage
        or finishes the process depending on the current stage.
        """
        if self.start_x is not None and self.start_y is not None and self.end_x is not None and self.end_y is not None:
            x1, y1 = min(self.start_x, self.end_x), min(self.start_y, self.end_y)
            x2, y2 = max(self.start_x, self.end_x), max(self.start_y, self.end_y)

            # Ensure the crop coordinates are within the image bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(self.image.shape[1], x2), min(self.image.shape[0], y2)

            if x1 == x2 or y1 == y2:
                messagebox.showwarning("Warning", "Invalid crop area. Please select a valid crop area.")
                print("Invalid crop area. Crop area has zero width or height.")
                return

            print(f"Cropping coordinates: ({x1}, {y1}), ({x2}, {y2})")

            cropped_image = self.image[y1:y2, x1:x2]

            if cropped_image.size == 0:
                messagebox.showwarning("Warning", "Invalid crop area. Please select a valid crop area.")
                print("Invalid crop area. Cropped image is empty.")
                return

            if self.stage == 0:
                cv2.imwrite(self.external_path, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Information", "External crop saved. Now select the internal crop area.")
                self.root.destroy()
                self.run_next_stage()
            elif self.stage == 1:
                cv2.imwrite(self.internal_path, cv2.cvtColor(cropped_image, cv2.COLOR_RGB2BGR))
                messagebox.showinfo("Information", "Internal crop saved successfully.")
                print(f"Cropped image saved: {self.internal_path}")
                self.root.destroy()
        else:
            messagebox.showwarning("Warning", "No crop area selected. Please select a crop area.")
            print("No crop area selected.")

    def run_next_stage(self):
        """
        Initiates the next stage of the cropping process.
        """
        next_stage = self.stage + 1
        if next_stage < 2:
            root = tk.Tk()
            CropInterface(root, self.image_path, self.external_path, self.internal_path, next_stage)
            root.mainloop()


def run_crop_interface(image_path):
    """
    Starts the cropping interface and returns the paths for the external and internal crops.
    Args:
    - image_path: Path to the image to be cropped.
    Returns:
    - external_crop_path: Path to the saved external crop image.
    - internal_crop_path: Path to the saved internal crop image.
    """
    external_crop_path = image_path.replace(".jpg", "_external.jpg")
    internal_crop_path = image_path.replace(".jpg", "_internal.jpg")
    root = tk.Tk()
    app = CropInterface(root, image_path, external_crop_path, internal_crop_path, stage=0)
    root.mainloop()
    return external_crop_path, internal_crop_path


if __name__ == "__main__":
    external_crop_path, internal_crop_path = run_crop_interface(
        "C:\\Users\\Adir Ashash\\PycharmProjects\\MY_PROJECT\\assets\\captured_frame.jpg")
    print(f"External Crop Path: {external_crop_path}")
    print(f"Internal Crop Path: {internal_crop_path}")
