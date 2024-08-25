import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time


class App:
    """
    App class that creates a Tkinter window to capture an image from the webcam with a countdown timer.
    Attributes:
        SECOND (int): Milliseconds in one second (used for timing).
        TIMER_INITIAL (int): Initial countdown value (in seconds).
        DELAY (int): Delay before starting the snapshot, calculated in milliseconds.
    Methods:
        __init__(self, window, window_title, video_source=0): Initializes the window, video capture, and UI elements.
        shoot_handle(self): Handles the countdown and triggers the snapshot when the timer reaches zero.
        snapshot(self): Captures the current frame from the video and saves it as an image file.
        update(self): Continuously updates the canvas with the current frame from the video source.
        resize_handle(self, event): Resizes the canvas and image when the window size changes.
    """

    SECOND = 1000  # second = 1000ms
    TIMER_INITIAL = 0  # Countdown timer in seconds
    DELAY = TIMER_INITIAL * SECOND  # Delay in milliseconds before taking the snapshot

    def __init__(self, window, window_title, video_source=0):
        """
        Initializes the App class.
        Args:
            window (Tk): The Tkinter window instance.
            window_title (str): The title of the window.
            video_source (int or str): The video source, typically the default webcam (0).
        """
        self.exit_app = True  # Flag to check if the app should exit
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        # Initialize video capture
        self.vid = MyVideoCapture(self.video_source)
        self.width = self.vid.width
        self.height = self.vid.height

        # Add a button to start the capture process
        self.button_shoot = tkinter.Button(window, text="Shoot!", command=self.shoot_handle, bg="skyblue",
                                           font='Caliberi')
        self.button_shoot.pack(anchor=tkinter.CENTER, expand=True)

        # Label to display the timer countdown
        self.timer_label = tkinter.Label(self.window, text="Timer: ")
        self.timer_label.pack()
        self.timer = self.TIMER_INITIAL + 1  # Initialize the countdown timer

        # Create a canvas to display the video feed
        self.canvas = tkinter.Canvas(window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()
        self.canvas.bind("<Configure>", self.resize_handle)

        self.wscale = 1  # Width scaling factor
        self.hscale = 1  # Height scaling factor
        self.delay = 15  # Delay in milliseconds between frames

        self.update()  # Start the video feed
        self.window.mainloop()  # Start the Tkinter main loop

    def shoot_handle(self):
        """
        Handles the countdown timer and takes a snapshot when the timer reaches zero.
        """
        self.timer_label.config(text=str(self.timer))
        if self.timer > 0:
            self.timer -= 1
            self.timer_label.config(text=str(self.timer))
            self.window.update()
            time.sleep(1)
            self.shoot_handle()  # Recursive call until timer reaches zero
        else:
            self.snapshot()  # Capture the image

    def snapshot(self):
        """
        Captures the current frame from the video source and saves it as an image file.
        """
        self.should_exit = False
        ret, frame = self.vid.get_frame()
        if ret:
            cv2.imwrite("./assets/Wall.jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))  # Save the captured image
            self.taken_picture = "./assets/Wall.jpg"  # Save the path of the captured image
            self.exit_app = False  # Set the exit flag to false
            self.window.destroy()  # Close the window

    def update(self):
        """
        Continuously updates the canvas with the current frame from the video source.
        """
        ret, frame = self.vid.get_frame()
        if ret:
            self.raw_image = PIL.Image.fromarray(frame)
            self.raw_image = self.raw_image.resize(
                (int(self.raw_image.width * self.wscale), int(self.raw_image.height * self.hscale)))
            self.photo = PIL.ImageTk.PhotoImage(image=self.raw_image)
            self.image_id = self.canvas.create_image(0, 0, image=self.photo, anchor=tkinter.NW)
        self.window.after(self.delay, self.update)

    def resize_handle(self, event):
        """
        Handles the resizing of the canvas and adjusts the displayed image accordingly.
        Args:
            event: The event that triggered the resize.
        """
        self.wscale = float(event.width) / self.width
        self.hscale = float(event.height) / self.height
        self.canvas.scale("all", 0, 0, self.wscale, self.hscale)
        self.canvas.itemconfigure(self.image_id, image=self.photo)  # Update the image size


class MyVideoCapture:
    """
    MyVideoCapture class to handle video capture using OpenCV.
    Attributes:
        vid: The video capture object.
        width: The width of the video frame.
        height: The height of the video frame.
    Methods:
        get_frame(self): Captures and returns the current frame from the video source.
        __del__(self): Releases the video capture object when the instance is destroyed.
    """

    def __init__(self, video_source=0):
        """
        Initializes the MyVideoCapture class.
        Args:
            video_source (int or str): The video source, typically the default webcam (0).
        """
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        """
        Captures and returns the current frame from the video source.
        Returns:
            ret: Boolean indicating if the frame was successfully captured.
            frame: The captured frame in RGB format.
        """
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None
        else:
            return None, None

    def __del__(self):
        """
        Releases the video capture object when the instance is destroyed.
        """
        if self.vid.isOpened():
            self.vid.release()


def run_take_a_picture():
    """
    Runs the application to take a picture using the webcam.
    Returns:
        str: The path to the captured image.
    """
    b = App(tkinter.Tk(), "Tkinter and OpenCV")
    if b.exit_app:
        quit()
    return b.taken_picture


if __name__ == "__main__":
    run_take_a_picture()  # Start the application and take a picture
