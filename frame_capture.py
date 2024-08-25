import tkinter as tk
import cv2
import PIL.Image, PIL.ImageTk
import time

class InitialCaptureApp:
    """
    A class representing the initial capture application that uses Tkinter and OpenCV
    to capture a video frame and save it as an image file.

    Attributes:
        window (tk.Tk): The main window of the Tkinter application.
        window_title (str): The title of the application window.
        video_source (int or str): The video source, typically the camera index or file path.
        vid (MyVideoCapture): Instance of the MyVideoCapture class for video capture.
        width (int): The width of the video frame.
        height (int): The height of the video frame.
        label (tk.Label): Label displaying instructions to the user.
        canvas (tk.Canvas): Canvas widget for displaying the video frame.
        ok_button (tk.Button): Button widget to capture the frame.
        exit_app (bool): Flag to determine if the application should exit.

    Methods:
        snapshot(): Captures the current video frame and saves it as an image file.
        update(): Updates the video frame on the canvas at a set interval.
    """

    SECOND = 1000  # Constant for 1 second in milliseconds
    DELAY = 15  # Delay for camera refresh in milliseconds

    def __init__(self, window, window_title, video_source=0):
        """
        Initializes the InitialCaptureApp class with the provided parameters.

        Args:
            window (tk.Tk): The main window of the Tkinter application.
            window_title (str): The title of the application window.
            video_source (int or str): The video source, typically the camera index or file path.
        """
        self.exit_app = True
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)
        self.width = self.vid.width
        self.height = self.vid.height

        # Wrap the text to fit the window
        self.label = tk.Label(window, text="Stand in the requested area, hold the photo on the wall, and click 'OK' when you are ready to take a photo", font=("Helvetica", 12), wraplength=self.width)
        self.label.pack(anchor=tk.CENTER, expand=True)

        self.canvas = tk.Canvas(window, width=self.width, height=self.height)
        self.canvas.pack()

        # Add an OK button
        self.ok_button = tk.Button(window, text="OK", command=self.snapshot)
        self.ok_button.place(x=20, y=50)

        self.update()
        self.window.mainloop()

    def snapshot(self):
        """
        Captures the current video frame and saves it as an image file in the assets directory.
        """
        self.exit_app = False
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite("./assets/captured_frame.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            print("Frame saved at ./assets/captured_frame.jpg")
        self.window.destroy()

    def update(self):
        """
        Updates the video frame on the canvas at a set interval defined by DELAY.
        """
        ret, frame = self.vid.get_frame()
        if ret:
            self.raw_image = PIL.Image.fromarray(frame)
            self.photo = PIL.ImageTk.PhotoImage(image=self.raw_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.canvas.update_idletasks()  # Update the canvas
        if self.exit_app:
            self.window.after(self.DELAY, self.update)

class MyVideoCapture:
    """
    A class to capture video frames from a camera or video file.

    Attributes:
        vid (cv2.VideoCapture): OpenCV VideoCapture object for capturing video frames.
        width (int): The width of the video frame.
        height (int): The height of the video frame.

    Methods:
        get_frame(): Retrieves the current frame from the video source.
        __del__(): Releases the video capture object when the instance is destroyed.
    """

    def __init__(self, video_source=0):
        """
        Initializes the MyVideoCapture class with the provided video source.

        Args:
            video_source (int or str): The video source, typically the camera index or file path.
        """
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        """
        Retrieves the current frame from the video source and converts it to RGB format.

        Returns:
            tuple: A tuple containing a boolean indicating success, and the frame in RGB format.
        """
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            else:
                return (ret, None)
        else:
            return (None, None)

    def __del__(self):
        """
        Releases the video capture object when the instance is destroyed.
        """
        if self.vid.isOpened():
            self.vid.release()

def run_initial_capture():
    """
    Runs the initial capture application and returns the path to the saved image.

    Returns:
        str: The path to the captured frame image.
    """
    app = InitialCaptureApp(tk.Tk(), "Tkinter and OpenCV")
    if app.exit_app:
        quit()
    return "./assets/captured_frame.jpg"

if __name__ == "__main__":
    run_initial_capture()
