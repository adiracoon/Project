import math


class Vertex:
    """
    Represents a vertex or point in 2D space with x and y coordinates.

    Attributes:
    - x (float): The x-coordinate of the vertex.
    - y (float): The y-coordinate of the vertex.
    - id (int): An optional identifier for the vertex (default is -1).
    """

    def __init__(self, x, y, id=-1):
        """
        Initializes a Vertex object with x, y coordinates and an optional id.

        Args:
        - x (float): The x-coordinate of the vertex.
        - y (float): The y-coordinate of the vertex.
        - id (int): The identifier for the vertex, default is -1.
        """
        self.x = x
        self.y = y
        self.id = id

    def distance_between_two_nodes(self, other):
        """
        Calculates the Euclidean distance between this vertex and another vertex.

        Args:
        - other (Vertex): The other vertex to calculate the distance to.

        Returns:
        - float: The distance between the two vertices.
        """
        return math.sqrt(math.pow(self.x - other.x, 2) + math.pow(self.y - other.y, 2))

    def __eq__(self, other):
        """
        Checks if this vertex is equal to another vertex, based on their coordinates.

        Args:
        - other (Vertex): The other vertex to compare with.

        Returns:
        - bool: True if the vertices have the same coordinates, False otherwise.
        """
        if other is None:
            return False
        return self.x == other.x and self.y == other.y

    def __lt__(self, other):
        """
        Compares this vertex with another vertex based on their y-coordinates.
        This method is used for sorting vertices vertically.

        Args:
        - other (Vertex): The other vertex to compare with.

        Returns:
        - bool: True if this vertex is above (has a smaller y-coordinate) the other vertex, False otherwise.
        """
        return self.y < other.y

    def __repr__(self):
        """
        Provides a string representation of the vertex for debugging and logging.

        Returns:
        - str: A string representing the vertex in the format "(x, y)".
        """
        return f"({self.x}, {self.y})"
