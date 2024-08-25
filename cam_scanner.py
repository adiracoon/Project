"""
cam_scanner.py

This module provides the CamScanner class, which facilitates the definition of wall boundaries
through a graphical user interface (GUI) using Tkinter. Users can interactively select points
on an image to define the corners of a wall, and the application will draw the corresponding
lines and shapes based on these selections.

Functions:
----------
- run_camscanner_realtime(picture, points=None):
    Runs the CamScanner in real-time mode with optional initial points.

- run_camscanner(picture, points=None):
    Runs the CamScanner with optional initial points.

Classes:
--------
- CamScanner:
    Manages the GUI for selecting wall boundaries on an image.
"""

import tkinter
from PIL import ImageTk, Image
from tkinter.messagebox import askyesno
from vertex import Vertex  # Assumes 'vertex.py' is in the same directory


class CamScanner:
    """
    CamScanner provides a graphical interface for users to define wall boundaries by selecting
    points on an image. It allows for interactive point selection, resizing, and visualization
    of the defined boundaries.

    Attributes:
    -----------
    file_name : str
        Path to the image file used for defining wall boundaries.
    points : list of tuples
        Optional initial points to pre-populate the vertex list.

    Methods:
    --------
    __init__(self, file_name, points):
        Initializes the CamScanner instance with the specified image and points.

    start(self):
        Starts the Tkinter main event loop to display the GUI.

    resize_handle(self, event):
        Handles the resizing of the canvas and adjusts the image and drawn elements accordingly.

    create_shape_after_resize(self):
        Recreates shapes (vertices and lines) after the canvas has been resized.

    click_handle(self, event):
        Handles mouse click events for adding or moving vertices.

    draw_vertex(self):
        Draws all vertices on the canvas.

    draw_square(self):
        Draws lines between vertices to form a square or rectangle.

    draw_single_line(self, p1, p2):
        Draws a single line between two specified points.

    finish_handle(self):
        Handles the completion of wall boundary definition and prompts for confirmation.
    """

    def __init__(self, file_name, points):
        """
        Initializes the CamScanner with the specified image and optional initial points.

        Parameters:
        -----------
        file_name : str
            Path to the image file to be displayed on the canvas.
        points : list of tuples
            Optional list of (x, y) tuples to initialize vertices on the canvas.
        """
        self.click_count = 0  # Initialize the click counter
        self.exit_app = True  # Flag to determine if the app should exit after completion

        # Set up the main Tkinter window
        self.root = tkinter.Tk()
        self.root.title("CamScanner - Define Wall Boundaries")

        # Load and display the image
        self.file = Image.open(file_name)
        self.img = ImageTk.PhotoImage(self.file)
        self.root.img = self.img  # Keep a reference to avoid garbage collection

        # Create and pack the "Finish" button
        self.button_finish = tkinter.Button(
            self.root,
            text="Finish",
            command=self.finish_handle,
            bg="skyblue",
            font='Caliberi'
        )
        self.button_finish.pack()

        # Create and pack the canvas
        self.canvas = tkinter.Canvas(
            self.root,
            width=self.img.width(),
            height=self.img.height()
        )
        self.image_id = self.canvas.create_image(
            self.img.width() / 2,
            self.img.height() / 2,
            image=self.img
        )
        self.canvas.pack(fill="both", expand=True)

        # Bind events to the canvas
        self.canvas.bind("<Button-1>", self.click_handle)
        self.canvas.bind("<Configure>", self.resize_handle)

        # Initialize lists to store vertices and lines
        self.vertex_list = []
        self.lines_list = []

        # Store the initial width and height of the canvas
        self.width = self.img.width()
        self.height = self.img.height()

        # Add a tag to all items on the canvas for easier manipulation
        self.canvas.addtag_all("all")

        # If initial points are provided, add them to the vertex list and draw them
        if points is not None:
            start = len(points) - 4
            for point in points[start:]:
                self.vertex_list.append(Vertex(point[0], point[1], -1))
            self.draw_vertex()

    def start(self):
        """
        Starts the Tkinter main event loop to display the GUI.
        """
        self.root.mainloop()

    def resize_handle(self, event):
        """
        Handles the resizing of the canvas. Adjusts the image size, scales all drawn elements,
        and updates vertex positions accordingly.

        Parameters:
        -----------
        event : tkinter.Event
            The event object containing information about the resize event.
        """
        # Calculate the scale factors based on the new size
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height

        # Update the stored width and height
        self.width = event.width
        self.height = event.height

        # Resize the image and update the PhotoImage
        self.file = self.file.resize((int(self.file.width * wscale), int(self.file.height * hscale)))
        self.img = ImageTk.PhotoImage(self.file)
        self.root.img = self.img  # Keep a reference to avoid garbage collection

        # Scale all items on the canvas
        self.canvas.scale("all", 0, 0, wscale, hscale)
        self.canvas.itemconfigure(self.image_id, image=self.img)  # Update the image displayed

        # Update the positions of all vertices based on the scale factors
        for node in self.vertex_list:
            node.x = node.x * wscale
            node.y = node.y * hscale

        # Recreate shapes after resizing
        self.create_shape_after_resize()

    def create_shape_after_resize(self):
        """
        Recreates shapes (vertices and lines) on the canvas after it has been resized.
        Deletes existing vertex representations and redraws them at updated positions.
        """
        # Delete existing vertex representations
        for node in self.vertex_list:
            self.canvas.delete(node.id)

        # Redraw vertices as ovals on the canvas
        for node in self.vertex_list:
            node.id = self.canvas.create_oval(
                node.x,
                node.y,
                node.x + 10,
                node.y + 10,
                fill='red'
            )

        # If four vertices are present, redraw the connecting lines
        if len(self.vertex_list) == 4:
            self.draw_square()

    def click_handle(self, event):
        """
        Handles mouse click events on the canvas. Adds new vertices or updates existing ones
        based on the number of clicks and existing vertices.

        Parameters:
        -----------
        event : tkinter.Event
            The event object containing information about the mouse click.
        """
        self.click_count += 1  # Increment the click counter

        x = event.x
        y = event.y

        if len(self.vertex_list) < 4:
            # If fewer than 4 vertices, create a new vertex
            vertex_id = self.canvas.create_oval(x, y, x + 10, y + 10, fill='red')
            self.vertex_list.append(Vertex(x, y, vertex_id))
        else:
            # If 4 vertices already exist, find the closest vertex to move
            closest_vertex = self.vertex_list[0]
            current_vertex = Vertex(x, y, id=None)

            # Determine the closest existing vertex to the click
            for vertex in self.vertex_list:
                if current_vertex.distance_between_two_nodes(vertex) < current_vertex.distance_between_two_nodes(closest_vertex):
                    closest_vertex = vertex

            # Update the position of the closest vertex
            self.canvas.delete(closest_vertex.id)
            closest_vertex.id = self.canvas.create_oval(x, y, x + 10, y + 10, fill='red')
            closest_vertex.x = x
            closest_vertex.y = y

        # If four vertices are present, draw connecting lines
        if len(self.vertex_list) == 4:
            self.draw_square()

    def draw_vertex(self):
        """
        Draws all vertices in the vertex list as ovals on the canvas and connects them
        with lines to form a square or rectangle.
        """
        for vertex in self.vertex_list:
            vertex.id = self.canvas.create_oval(
                vertex.x,
                vertex.y,
                vertex.x + 10,
                vertex.y + 10,
                fill='red'
            )
        self.draw_square()

    def draw_square(self):
        """
        Sorts the vertices and draws lines between them to form a square or rectangle.
        Ensures that lines are drawn in a consistent order based on vertex positions.
        """
        # Remove existing lines from the canvas
        for line in self.lines_list:
            self.canvas.delete(line)
        self.lines_list.clear()

        # Sort the vertex list based on their positions to determine drawing order
        self.vertex_list.sort()

        # Assign sorted vertices to variables for clarity
        p1, p2, p3, p4 = self.vertex_list

        # Ensure consistent ordering based on x-coordinates
        if p2.x < p1.x:
            p1, p2 = p2, p1
        if p4.x < p3.x:
            p3, p4 = p4, p3

        # Draw lines between the sorted vertices
        self.draw_single_line(p1, p2)
        self.draw_single_line(p2, p4)
        self.draw_single_line(p4, p3)
        self.draw_single_line(p3, p1)

        print(self.vertex_list)  # Debugging: Print the sorted list of vertices

    def draw_single_line(self, p1, p2):
        """
        Draws a single line between two specified points on the canvas.

        Parameters:
        -----------
        p1 : Vertex
            The starting vertex of the line.
        p2 : Vertex
            The ending vertex of the line.
        """
        line_id = self.canvas.create_line(
            p1.x + 5,
            p1.y + 5,
            p2.x + 5,
            p2.y + 5,
            smooth=True,
            fill='red'
        )
        self.lines_list.append(line_id)

    def finish_handle(self):
        """
        Handles the "Finish" button click event. Prompts the user for confirmation to
        finalize the wall boundary definition. If confirmed, closes the application
        and outputs the total number of clicks made during the session.
        """
        if len(self.vertex_list) < 4:
            # If fewer than 4 vertices, do nothing
            return

        # Prompt the user for confirmation
        answer = askyesno("Confirmation", "Are you sure you want to define the wall like this?")

        if answer:
            self.exit_app = False  # Update the exit flag
            self.root.destroy()     # Close the Tkinter window
            print(f"Total clicks CAM_SCANNER: {self.click_count}")  # Output the total number of clicks


def run_camscanner_realtime(picture, points=None):
    """
    Runs the CamScanner in real-time mode. Initializes the CamScanner with the provided
    image and optional initial points, starts the GUI, and returns the list of selected
    points upon completion.

    Parameters:
    -----------
    picture : str
        Path to the image file to be used for defining wall boundaries.
    points : list of tuples, optional
        Optional list of (x, y) tuples to pre-populate the vertex list.

    Returns:
    --------
    list of tuples
        A list of (x, y) coordinates representing the selected vertices.
    """
    scanner = CamScanner(file_name=picture, points=points)
    scanner.start()

    # Collect the coordinates of all vertices
    tuple_list = [(int(vertex.x), int(vertex.y)) for vertex in scanner.vertex_list]
    print("tuple_list", tuple_list)

    if scanner.exit_app:
        quit()  # Exit the application if the user did not confirm

    return tuple_list  # Return the list of selected points


def run_camscanner(picture, points=None):
    """
    Runs the CamScanner. Initializes the CamScanner with the provided image and optional
    initial points, starts the GUI, and returns the list of selected points upon completion.

    Parameters:
    -----------
    picture : str
        Path to the image file to be used for defining wall boundaries.
    points : list of tuples, optional
        Optional list of (x, y) tuples to pre-populate the vertex list.

    Returns:
    --------
    list of tuples
        A list of (x, y) coordinates representing the selected vertices.
    """
    scanner = CamScanner(file_name=picture, points=points)
    scanner.start()

    # Collect the coordinates of all vertices
    tuple_list = [(int(vertex.x), int(vertex.y)) for vertex in scanner.vertex_list]
    print("tuple_list", tuple_list)

    if scanner.exit_app:
        quit()  # Exit the application if the user did not confirm

    return tuple_list  # Return the list of selected points


if __name__ == "__main__":
    """
    If this script is run as the main program, execute the CamScanner on a default image.
    """
    run_camscanner("./assets/wall.jpg")
