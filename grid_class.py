import tkinter
from tkinter.messagebox import askyesno
from PIL import Image, ImageTk
from line import Line
from vertex import Vertex

class GridInterface:
    """
    A class for managing a graphical interface that allows users to select an area on an image,
    display a grid on the selected area, and choose a point on that grid.

    Attributes:
        CHOOSE_AREA (int): Constant representing the state of choosing an area.
        CHOOSE_POINT_ON_GRID (int): Constant representing the state of choosing a point on the grid.
        RADIUS (int): Radius for drawing grid points.
        select_point (Vertex): The point selected by the user on the grid.
        exit_app (bool): Flag to control the exit status of the application.
        root (tkinter.Tk): The main Tkinter window.
        file (PIL.Image): The image file loaded into the interface.
        wall (ImageTk.PhotoImage): The Tkinter-compatible photo image of the loaded file.
        width (int): The width of the image.
        height (int): The height of the image.
        topFrame (tkinter.Frame): Top frame of the interface for layout management.
        label (tkinter.Label): Label widget displaying instructions to the user.
        canvas (tkinter.Canvas): Canvas widget for displaying and interacting with the image.
        wall_image_id (int): ID of the image on the canvas.
        border_lines (list): List of border lines defining different sections on the image.
        selected_slice (int): The index of the currently selected slice.
        grid_lines (list): List of grid lines drawn on the canvas.
        state (int): Current state of the interface (choosing area or point).
        selected_point_id (int): ID of the selected point on the grid.
    """

    CHOOSE_AREA = 1
    CHOOSE_POINT_ON_GRID = 2
    RADIUS = 5

    def __init__(self, file_name, border_lines):
        """
        Initializes the GridInterface with the given image file and border lines.

        Args:
            file_name (str): The file path of the image to load.
            border_lines (list): A list of tuples representing the border lines for slicing the image.
        """
        self.select_point = None
        self.exit_app = True
        self.root = tkinter.Tk()
        self.file = Image.open(file_name)
        self.wall = ImageTk.PhotoImage(self.file)
        self.width = self.wall.width()
        self.height = self.wall.height()

        self.topFrame = tkinter.Frame(self.root)
        self.topFrame.pack(fill="both", side=tkinter.TOP)

        self.label = tkinter.Label(self.root, text="Select a slice")
        self.label.pack()

        self.canvas = tkinter.Canvas(self.root, width=self.wall.width(), height=self.wall.height())
        self.wall_image_id = self.canvas.create_image(self.wall.width() / 2, self.wall.height() / 2, image=self.wall)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.click_handle)
        self.canvas.bind("<Configure>", self.resize_handle)
        self.canvas.addtag_all("all")

        self.border_lines = border_lines
        self.selected_slice = -1
        self.grid_lines = []
        self.state = GridInterface.CHOOSE_AREA

        self.selected_point_id = None

    def start(self):
        """Starts the Tkinter main event loop."""
        self.root.mainloop()

    def draw_grid1(self):
        """Draws a grid over the selected slice area of the image."""
        if self.selected_slice > len(self.border_lines) - 1:
            print(f"Invalid selected_slice index: {self.selected_slice}")
            return

        start_x = self.border_lines[self.selected_slice - 1][0]
        end_x = self.border_lines[self.selected_slice][0]

        self.area = (start_x, 0), (end_x, 0)
        area_width = end_x - start_x
        area_height = self.canvas.winfo_height()

        y_diff = area_height / 4
        x_diff = area_width / 4

        y = 0
        for i in range(5):
            left_vertex = Vertex(start_x, y, -1)
            right_vertex = Vertex(end_x, y, -1)
            self.draw_single_line(left_vertex, right_vertex, Line.HORIZONTAL)
            y += y_diff

        x = start_x
        for i in range(5):
            up_vertex = Vertex(x, 0, -1)
            down_vertex = Vertex(x, area_height, -1)
            self.draw_single_line(up_vertex, down_vertex, Line.VERTICAL)
            x += x_diff

    def draw_single_line(self, p1, p2, direct):
        """Draws a single line between two points and stores the line information."""
        id = self.canvas.create_line(p1.x, p1.y, p2.x, p2.y, smooth=True, fill='green')
        self.grid_lines.append(Line(p1, p2, id, direct))

    def draw_point_on_grid(self):
        """Finds and draws intersection points on the grid."""
        self.point_on_grid = []
        for line1 in self.grid_lines:
            for line2 in self.grid_lines:
                if line1 != line2:
                    p = line1.is_meeting(line2)
                    if p is not None:
                        self.point_on_grid.append(p)
        self.draw_vertex()

    def draw_vertex(self):
        """Draws vertices (grid points) on the canvas."""
        for vertex in self.point_on_grid:
            id = self.canvas.create_oval(vertex.x - 5, vertex.y - 5, vertex.x + 5, vertex.y + 5, fill='red')
            vertex.id = id

    def select_point_to_hang(self):
        """Prompts the user to select a point on the grid for hanging."""
        self.label.config(text="Select a point on the grid")
        self.button_hang = tkinter.Button(self.topFrame, text="Confirm Point", command=self.confirm_hang_a_picture, bg="skyblue", font='Caliberi')
        self.button_hang.pack()

    def confirm_hang_a_picture(self):
        """Handles the confirmation of the selected point on the grid."""
        answer = askyesno("title", "Are you sure you want to hang here?")
        if answer:
            self.exit_app = False
            self.root.destroy()

    def click_handle(self, event):
        """Handles mouse clicks on the canvas, allowing the user to select areas and points."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        print(f"Clicked coordinates: x={x}, y={y}")

        if self.state == GridInterface.CHOOSE_AREA:
            print("Choosing area...")
            for i in range(len(self.border_lines)):
                start_x = self.border_lines[i][0]
                if i + 1 < len(self.border_lines):
                    end_x = self.border_lines[i + 1][0]
                else:
                    end_x = self.canvas.winfo_width()

                if start_x < x < end_x:
                    self.selected_slice = i + 1
                    self.state = GridInterface.CHOOSE_POINT_ON_GRID
                    self.draw_grid1()
                    self.draw_point_on_grid()
                    self.select_point_to_hang()
                    break

        elif self.state == GridInterface.CHOOSE_POINT_ON_GRID:
            if not self.point_on_grid:
                print("Error: No grid points available!")
                return
            closest_vertex = min(self.point_on_grid, key=lambda v: ((v.x - x) ** 2 + (v.y - y) ** 2) ** 0.5)
            x, y = closest_vertex.x, closest_vertex.y
            if self.selected_point_id:
                self.canvas.delete(self.selected_point_id)
            self.selected_point_id = self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill='yellow')
            self.select_point = closest_vertex

    def resize_handle(self, event):
        """Handles window resize events and rescales the image and grid accordingly."""
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        self.file = self.file.resize((int(self.file.width * wscale), int(self.file.height * hscale)))
        self.wall = ImageTk.PhotoImage(self.file)
        self.canvas.scale("all", 0, 0, wscale, hscale)
        self.canvas.itemconfigure(self.wall_image_id, image=self.wall)

def draw_grid_on_slice(picture, border_lines):
    """
    Runs the GridInterface application to allow the user to select a point on the grid.

    Args:
        picture (str): The file path of the image to load.
        border_lines (list): A list of tuples representing the border lines for slicing the image.

    Returns:
        tuple: The selected point on the grid and the updated border lines.
    """
    b = GridInterface(file_name=picture, border_lines=border_lines)
    b.start()
    if b.exit_app:
        quit()
    return b.select_point, border_lines
