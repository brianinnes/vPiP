from config import PolarConfig
from coordinates import Coordinate
from serialHandler import SerialHandler
from math import floor


class Polargraph:
    def __enter__(self):
        return self

    def __init__(self):
        print("Polargraph __init__")
        self.config = PolarConfig()
        self.maxSegment = 200
        self.outOfBounds = False
        self.outOfBoundsDrawingCoord = None
        self.outstandingMove = False
        self.moveSystemCoordinates = None
        print(self.config)

        if self.config.pixels > 0:
            self.mmpp = (float(self.config.width) - (2 * self.config.margin)) / self.config.pixels
            self.maxPy = (float(self.config.height * self.config.pixels) /
                          self.config.width)
        else:
            self.mmpp = 1
            self.maxPy = self.config.height = 2 * self.config.margin
        self.serial = SerialHandler(self.config)
        self.serial.connect()
        self.currPosSysCoords = Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)

    def __exit__(self, *err):
        print("Polargraph __exit__")
        self.goHome()
        self.serial.disconnect()

    def isOutsideDrawingArea(self, coord):
        if coord.x < 0 or coord.x > self.config.pixels or coord.y < 0 or coord.y > self.maxPy:
            return True
        else:
            return False

    def crossBoundary(self, coord):
        m = (coord.y - self.outOfBoundsDrawingCoord.y) / (coord.x - self.outOfBoundsDrawingCoord.x)
        b = coode.y - m * coord.x
        ret = None
        if coord.x < 0:
            ret = Coordinate.fromCoords(0, b)
            if self.isOutsideDrawingArea(ret):
                ret = None
        if ret == None and coord.x > self.config.pixels:
            ret = Coordinate.fromCoords(self.config.pixels, m * self.config.pixels + b)
            if self.isOutsideDrawingArea(ret):
                ret = None
        if coord.y < 0:
            ret = Coordinate.fromCoords(-b/m, 0)
            if self.isOutsideDrawingArea(ret):
                ret = None
        if ret == None and coord.y > self.maxPy:
            ret = Coordinate.fromCoords((self.maxPy-b)/m, self.maxPy)
            if self.isOutsideDrawingArea(ret):
                ret = None
        return ret

    #def sendCommand(self, coord):
    #    if self.outOfBounds:
    #        if self.isOutsideDrawingArea(coord):
    #            self.outOfBoundsDrawingCoord = coord
    #        else:
                


    #   High level drawing functions
    def moveTo(self, x, y):
        point = Coordinate.fromCoords(x, y, True)
        self.moveSystemCoordinates = self.config.drawing2systemCoords(point)
        self.outstandingMove = True

    def drawTo(self, x, y):
        if self.outstandingMove:
            self.serial.sendCommand(self.moveSystemCoordinates)
            self.CurrPosSysCoords = Coordinate.fromCoords(self.moveSystemCoordinates.x, self.moveSystemCoordinates.y, self.moveSystemCoordinates.penup)
            self.outstandingMove = False
        point = Coordinate.fromCoords(x, y, False)
        coordsSystem = self.config.drawing2systemCoords(point)
        self.serial.sendCommand(coordsSystem)
        self.currPosSysCoords = Coordinate.fromCoords(coordsSystem.x, coordsSystem.y, coordsSystem.penup)

    def goHome(self):
        self.outstandingMove = False
        self.moveSystemCoordinates = None
        self.currPosSysCoords = Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)
        self.serial.sendCommand(self.currPosSysCoords)
        self.serial.sendCommand(self.currPosSysCoords)

    def penUp(self):
        self.currPosSysCoords = Coordinate.fromCoords(self.currPosSysCoords.x, self.currPosSysCoords.y, True)
        self.serial.sendCommand(self.currPosSysCoords)
