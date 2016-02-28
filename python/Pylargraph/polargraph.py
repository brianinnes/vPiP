from config import PolarConfig
from coordinates import Coordinate
from serialHandler import SerialHandler
from PIL import Image, ImageDraw
import time


class Plotter:
    def __init__(self, config):
        self.config = config
        self.serial = SerialHandler(self.config)
        self.serial.connect()
        self.currPosSysCoords = Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)

    def sendCommand(self, coord):
        coordsSystem = self.config.drawing2systemCoords(coord)
        self.serial.sendCommand(coordsSystem)
        self.currPosSysCoords = Coordinate.fromCoords(coordsSystem.x, coordsSystem.y, coordsSystem.penup)

    def finishDrawing(self):
        self.goHome()
        self.serial.disconnect()

    def penUp(self):
        self.currPosSysCoords = Coordinate.fromCoords(self.currPosSysCoords.x, self.currPosSysCoords.y, True)
        self.serial.sendCommand(self.currPosSysCoords)

    def goHome(self):
        self.currPosSysCoords = Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)
        self.serial.sendCommand(self.currPosSysCoords)
        self.serial.sendCommand(self.currPosSysCoords)


class Drawer:
    def __init__(self, config):
        self.config = config
        self.screenImage = None
        self.screenDraw = None
        self.screenImage = Image.new('RGB', (self.config.screenX,
                                             self.config.heightScreen),
                                     (255, 255, 255, 255))  # create the image
        self.screenDraw = ImageDraw.Draw(self.screenImage)
        self.currentPosition = self.config.drawing2screenCoords(self.config.system2drawingCoords(Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)))

    def sendCommand(self, coord):
        screenCoord = self.config.drawing2screenCoords(coord)
        if not coord.penup:
            self.screenDraw.line([int(round(self.currentPosition.x)), int(round(self.currentPosition.y)),
                                 int(round(screenCoord.x)), int(round(screenCoord.y))] , fill=(0,0,0))
        self.currentPosition = screenCoord

    def finishDrawing(self):
        del self.screenDraw
        if self.config.showImage:
            self.screenImage.show()
        if self.config.saveImage:
            self.screenImage.save(''.join(('{}'.format(int(round(time.time() * 1000))),".jpg")), "JPEG", optimize=True)


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
        self.moveDrawingCoordinates = None
        self.currentDrawingPosition = None
        self.plotter = None
        self.drawer = None
        self.drawing = self.config.showImage or self.config.saveImage
        print(self.config)

        if self.drawing:
            self.drawer = Drawer(self.config)

        if self.config.polarDraw:
            self.plotter = Plotter(self.config)

    def __exit__(self ,type = None, value = None, traceback = None):
        print("Polargraph __exit__")
        if self.drawing:
            self.drawer.finishDrawing()
        if self.config.polarDraw:
            self.plotter.finishDrawing()

    def isOutsideDrawingArea(self, coord):
        """
        :param coord:
        :rtype: bool
        """
        if coord.x < 0 or coord.x > self.config.pixels or coord.y < 0 or coord.y > self.config.heightPixels:
            return True
        else:
            return False

    def crossBoundary(self, coord, leaving):
        ret = None
        if leaving:
            m = (self.currentDrawingPosition.y - coord.y) / (self.currentDrawingPosition.x - coord.x)
            b = self.currentDrawingPosition.y - m * self.currentDrawingPosition.x
            if coord.x < 0:
                ret = Coordinate.fromCoords(0, b, coord.penup)
                ret1 = Coordinate.fromCoords(0, b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and coord.x > self.config.pixels:
                ret = Coordinate.fromCoords(self.config.pixels, m * self.config.pixels + b, coord.penup)
                ret2 = Coordinate.fromCoords(self.config.pixels, m * self.config.pixels + b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and coord.y < 0:
                ret = Coordinate.fromCoords(-b / m, 0, coord.penup)
                ret3 = Coordinate.fromCoords(-b / m, 0, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and coord.y > self.config.heightPixels:
                ret = Coordinate.fromCoords((self.config.heightPixels - b) / m, self.config.heightPixels, coord.penup)
                ret4 = Coordinate.fromCoords((self.config.heightPixels - b) / m, self.config.heightPixels, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
        else:
            m = (coord.y - self.outOfBoundsDrawingCoord.y) / (coord.x - self.outOfBoundsDrawingCoord.x)
            b = coord.y - m * coord.x
            if self.outOfBoundsDrawingCoord.x < 0:
                ret = Coordinate.fromCoords(0, b, coord.penup)
                ret1 = Coordinate.fromCoords(0, b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and self.outOfBoundsDrawingCoord.x > self.config.pixels:
                ret = Coordinate.fromCoords(self.config.pixels, m * self.config.pixels + b, coord.penup)
                ret2 = Coordinate.fromCoords(self.config.pixels, m * self.config.pixels + b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and self.outOfBoundsDrawingCoord.y < 0:
                ret = Coordinate.fromCoords(-b / m, 0, coord.penup)
                ret3 = Coordinate.fromCoords(-b / m, 0, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and self.outOfBoundsDrawingCoord.y > self.config.heightPixels:
                ret = Coordinate.fromCoords((self.config.heightPixels - b) / m, self.config.heightPixels, coord.penup)
                ret4 = Coordinate.fromCoords((self.config.heightPixels - b) / m, self.config.heightPixels, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
        if ret is None:
            print("Oops - somethings went wrong : {} {} {} {}").format(ret1, ret2, ret3, ret4)
        return ret

    def sendCommand(self, coord):
        """
        sendCommand Ensured the commands are to draw entirely within the degined drawing area, if not only draw what
        is inside thge drawing area.  Sends the command to the drawing engines.
        :type coord: Coordinate
        :param coord: Coordinate to draw or move to in drawing coordinate system
        :return:
        """
        if self.outOfBounds:
            # last command left current draw position outside drawing area
            if self.isOutsideDrawingArea(coord):
                # current command also leaves the draw position outside the drawing area
                self.outOfBoundsDrawingCoord = coord
            else:
                # This command moves the drawing position back into drawing area
                if coord.penup:
                    # This command is a move, so simple move to the correct position
                    if self.drawing:
                        self.drawer.sendCommand(coord)
                    if self.config.polarDraw:
                        self.plotter.sendCommand(coord)
                else:
                    # This command is a draw, so calculate where the line crosses the drawing area boundary and
                    # draw a line from the crossing point to the point specified in the command
                    crossBoundryPoint = self.crossBoundary(coord, False)
                    crossBoundryPoint.penup = True
                    if self.drawing:
                        self.drawer.sendCommand(crossBoundryPoint)
                        self.drawer.sendCommand(coord)
                    if self.config.polarDraw:
                        self.plotter.sendCommand(crossBoundryPoint)
                        self.plotter.sendCommand(coord)
                self.outOfBounds = False
        else:
            # drawing position before this command was inside the drawing area
            if self.isOutsideDrawingArea(coord):
                # This command will take the drawing position outside the drawing area.  I not a move then draw a line
                # to the point where the line crosses the drawing area boundary
                if not coord.penup:
                    crossBoundryPoint = self.crossBoundary(coord, True)
                    if self.drawing:
                        self.drawer.sendCommand(crossBoundryPoint)
                    if self.config.polarDraw:
                        self.plotter.sendCommand(crossBoundryPoint)
                self.outOfBoundsDrawingCoord = coord
                self.outOfBounds = True
            else:
                # all inside drawing area
                if self.drawing:
                    self.drawer.sendCommand(coord)
                if self.config.polarDraw:
                    self.plotter.sendCommand(coord)

    # High level drawing functions
    def moveTo(self, x, y):
        self.moveDrawingCoordinates = Coordinate.fromCoords(x, y, True)
        self.outstandingMove = True

    def drawTo(self, x, y):
        if self.outstandingMove:
            self.sendCommand(self.moveDrawingCoordinates)
            self.currentDrawingPosition = Coordinate.fromCoords(self.moveDrawingCoordinates.x,
                                                                self.moveDrawingCoordinates.y,
                                                                True)
            self.outstandingMove = False
        self.sendCommand(Coordinate.fromCoords(x, y, False))
        self.currentDrawingPosition = Coordinate.fromCoords(x, y, False)

    def goHome(self):
        home = self.config.system2drawingCoords(Coordinate.fromCoords(self.config.homeX, self.config.homeY, True))
        self.moveTo(home.x, home.y)
        if self.config.polarDraw:
            self.plotter.goHome()

    def penUp(self):
        if self.config.polarDraw:
            self.plotter.penUp()

