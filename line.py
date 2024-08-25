from vertex import Vertex

class Line:
    HORIZONTAL = 1
    VERTICAL = 2

    def __init__(self, start, end, line_id, direction):
        """
        Initialize a Line object.

        Args:
            start (Vertex): The starting point of the line.
            end (Vertex): The ending point of the line.
            line_id (int): The ID of the line (for use in GUI elements).
            direction (int): The direction of the line, either Line.HORIZONTAL or Line.VERTICAL.
        """
        self.start = start
        self.end = end
        self.id = line_id
        self.direct = direction  # horizontal or vertical

    def __repr__(self):
        """
        Provide a string representation of the line showing its start and end points.

        Returns:
            str: A string representation of the line.
        """
        return f"{self.start} - {self.end}"

    def __eq__(self, other):
        """
        Check if two lines are equivalent, meaning they have the same start and end points,
        regardless of the order of the points.

        Args:
            other (Line): The line to compare with.

        Returns:
            bool: True if the lines are equivalent, False otherwise.
        """
        return (self.start == other.start and self.end == other.end) or \
               (self.start == other.end and self.end == other.start)

    def is_meeting(self, other):
        """
        Check if this line intersects with another line and return the intersection point.

        Args:
            other (Line): The other line to check for intersection.

        Returns:
            Vertex or None: The point of intersection as a Vertex object if the lines intersect;
                            otherwise, None.
        """
        if self.direct != other.direct:
            if self.direct == Line.HORIZONTAL:
                return Vertex(other.start.x, self.start.y)
            else:
                return Vertex(self.start.x, other.start.y)
        else:
            return None
