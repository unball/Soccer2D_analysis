import math 


#======================================
# geometric abstractions

class Point:
    '''
    A class to create a point somewhere in the field.
    ...
    Attributes
    ----------
    x: float
        x coordinates of the point in the field
    y: float
        y coordinates of the point in the field
    '''

    def __init__(self, x=0.0, y=0.0):
        '''
        Constructs all the necessary attributes for the point object.
        Parameters
        ----------
        x: float
            x coordinates of the point in the field
        y: float
            y coordinates of the point in the field
        '''
        self.x = x
        self.y = y

    def __str__(self):
        return "x: {} - y: {}".format(self.x, self.y)
    
class Circle:
    """
    The circle class

    Circle(radius: float, center: socceranalyzer.common.geometric.point.Point)

    Attributes
    ----------
            private:
                radius : float
                    the circle radius
                center: socceranalyzer.common.geometric.point.Point
                    the circle center point

    Methods
    -------
            public:
                is_inside(point : socceranalyzer.common.geometric.point.Point) -> bool
                    checks if point is inside the circle
                distance_to_center(point : socceranalyzer.common.geometric.point.Point) -> float
                    computes distance from 'point' to center of the circle
    """
    def __init__(self, radius: float, center: Point):
        self.__radius = radius
        self.__center = center

    @property
    def radius(self):
        return self.__radius

    @radius.setter
    def radius(self, r: float):
        self.__radius = r

    @property
    def center(self):
        return self.__center

    @center.setter
    def center(self, point: Point):
        self.__center = point

    def is_inside(self, point: Point):
        """
        Returns a boolean indicating if point is inside the circle.

                Parameters:
                        point (Point): Point of interest

                Returns:
                        is_inside (bool): Indicates if point is inside the circle.
        """

        dist = distance(self.__center, point)

        if dist <= self.__radius:
            return True
        else:
            return False

    def distance_to_center(self, point: Point) -> float:
        """
        Returns a float indicating the distance between the point coordinates and the circle.

                Parameters:
                        point (Point): Point of interest

                Returns:
                        dist (float): Distance value.
        """
        return distance(self.__center, point)

class Triangle:
    """
    Represents a triangle

    Attributes
    ----------
            private:
                vertices : list[Point]
                    the triangle vertices

    Methods
    -------
            public:
                is_inside(point : socceranalyzer.common.geometric.point.Point) -> bool
                    checks if point is inside the triangle
    """

    def __init__(self, a: Point, b: Point, c: Point):
        self.__vertices = [a, b, c]
    
    def is_inside(self, point: Point) -> bool:
        """
        Returns a boolean indicating if point is inside triangle.

                Parameters:
                        point (list[float]): Point of interest

                Returns:
                        is_inside (bool): Indicates if point is inside triangle defined by vertices
        """
        v0 = [self.__vertices[2].x - self.__vertices[0].x, self.__vertices[2].y - self.__vertices[0].y]
        v1 = [self.__vertices[1].x - self.__vertices[0].x, self.__vertices[1].y - self.__vertices[0].y]
        v2 = [point.x - self.__vertices[0].x, point.y - self.__vertices[0].y]

        # Compute dot products
        dot00 = dot(v0, v0)
        dot01 = dot(v0, v1)
        dot02 = dot(v0, v2)
        dot11 = dot(v1, v1)
        dot12 = dot(v1, v2)

        # Compute barycentric coordinates
        invDenom = 1.0 / (dot00 * dot11 - dot01 * dot01)
        u = (dot11 * dot02 - dot01 * dot12) * invDenom
        v = (dot00 * dot12 - dot01 * dot02) * invDenom

        # Check if point is in triangle
        return (u >= 0.) and (v >= 0.) and(u + v < 1.)
    

# ================================================================
# geometric functions

def distance(point: Point, position: Point) -> float:
    """
    Returns the distance between a point and the position of the object.

            Parameters:
                    point (Point): A Point object
                    position (Point): Another Point object

            Returns:
                    dist (float): value of the distance
    """
    dist = math.sqrt(pow(position.x - point.x, 2) + pow(position.y - point.y, 2))

    return dist

def dot(v1: list[float], v2: list[float]) -> float:
    """
    Returns the dot product between v1 and v2.

        Parameters:
                    v1 (list[float]): Vector 1
                    v2 (list[float]): Vector 2

            Returns:
                    result (float): The dot product between vector 1 and vector 2
    """
    result = 0.0
    for m, n in zip(v1,v2):
        result += m*n
    return result

def distance_sqrd(p1: Point, p2: Point) -> float:
    """
    Returns the distance squared between two points.

            Parameters:
                    p1 (Point): First point
                    p2 (Point): Second point

            Returns:
                    dist^2 (float): integer value of the distance squared
    """

    return (p1.x - p2.x)**2 + (p1.y - p2.y)**2

def line_intersection(line1: tuple[tuple[float, float]], line2: tuple[tuple[float, float]]) -> tuple[float, float]:
    """
    Returns a tuple where lines intersect.

            Parameters:
                    line1 (tuple[tuple[float, float]]): First line
                    line2 (tuple[tuple[float, float]]): Second line

            Returns:
                    (x, y) (tuple[float, float]): Point where lines intersect

            Raises:
                    Exception('lines do not intersect!')
    """
    def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
    div = det(xdiff, ydiff)
    if div == 0:
            raise Exception('lines do not intersect!')
    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y