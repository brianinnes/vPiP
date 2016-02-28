from math import hypot, ceil


class Coordinate:
    @classmethod
    def fromCoords(cls, x, y, penup):
        """

        :param penup: bool
        :param y: float
        :param x: float
        :rtype: Coordinate
        """
        obj = cls()
        obj.x = float(x)
        obj.y = float(y)
        obj.penup = penup
        return obj

    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.penup = True

    def __eq__(self, coord):
        return (isinstance(coord, self.__class__) and
                self.minus(coord).length() < 0.000000001 and
                coord.penup == self.penup)

    def __add__(self, coord):
        return self.add(coord)

    def __sub__(self, coord):
        return self.minus(coord)

    def __mul__(self, factor):
        return self.scaled(factor)

    def __div__(self, factor):
        return self.divide(factor)

    def __str__(self):
        return "({}, {} with penup={})".format(self.x, self.y, self.penup)

    def length(self):
        """
        :rtype: float
        """
        return hypot(self.x, self.y)

    def add(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        return Coordinate.fromCoords(self.x + coord.x, self.y + coord.y, self.penup or coord.penup)

    def minus(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        return Coordinate.fromCoords(self.x - coord.x, self.y - coord.y, self.penup or coord.penup)

    def scaled(self, factor):
        """
        :param factor:
        :rtype: Coordinate
        """
        return Coordinate.fromCoords(self.x * factor, self.y * factor, self.penup)

    def divide(self, factor):
        """
        :param factor:
        :rtype: Coordinate
        """
        return Coordinate.fromCoords(self.x / factor, self.y / factor, self.penup)

    def translate(self, factorX, factorY):
        """
        :param factorX:
        :param factorY:
        :rtype: Coordinate
        """
        return Coordinate.fromCoords(self.x + factorX,  self.y + factorY, self.penup)

    def normalised(self):
        """
        :rtype: Coordinate
        """
        length = self.length()
        return Coordinate.fromCoords(self.x / length, self.y / length, self.penup)

    def dotProduct(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        return self.x * coord.x + self.y * coord.y

    def update(self, x, y):
        self.x = x
        self.y = y


class PolarCoordinate:
    def __init__(self):
        self.leftDist = 0.0
        self.rightDist = 0.0
        self.penup = True

    @classmethod
    def fromCoords(cls, lDist, rDist, penup):
        """

        :param penup:
        :param rDist:
        :param lDist:
        :rtype: PolarCoordinate
        """
        obj = cls()
        obj.leftDist = float(lDist)
        obj.rightDist = float(rDist)
        obj.penup = penup
        return obj

    def __str__(self):
        return "(L: {}, R: {}, penup: {})".format(self.leftDist, self.rightDist, self.penup)

    def __add__(self, pCoord):
        return self.add(pCoord)

    def __sub__(self, pCoord):
        return self.minus(pCoord)

    def __mul__(self, factor):
        return self.scale(factor)

    def __div__(self, factor):
        return self.divide(factor)

    def add(self, pCoord):
        return PolarCoordinate.fromCoords(self.leftDist + pCoord.leftDist, self.rightDist + pCoord.rightDist,
                                          self.penup or pCoord.penup)

    def minus(self, pCoord):
        return PolarCoordinate.fromCoords(self.leftDist - pCoord.leftDist, self.rightDist - pCoord.rightDist,
                                          self.penup or pCoord.penup)

    def scale(self, factor):
        return PolarCoordinate.fromCoords(self.leftDist * factor, self.rightDist * factor, self.penup)

    def divide(self, factor):
        return PolarCoordinate.fromCoords(self.leftDist * factor, self.rightDist * factor, self.penup)

    def ceil(self):
        return PolarCoordinate.fromCoords(ceil(self.leftDist), ceil(self.rightDist), self.penup)

    def clamp(self, mx, mn):
        if self.leftDist > mx or self.leftDist < mn or self.rightDist > mx or self.rightDist < mn:
            print('Clampling coord {} between {} and {}').format(self, mn, mx)
        return PolarCoordinate.fromCoords(min(mx, max(self.leftDist, mn)), min(mx, max(self.rightDist, mn)), self.penup)
