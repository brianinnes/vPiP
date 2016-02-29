from config import PolarConfig
from coordinates import Coordinate
from constrainDrawingRectangle import ConstrainDrawingRectangle
from serialHandler import SerialHandler
from PIL import Image, ImageDraw
from time import time


class Plotter:
    def __init__(self, config):
        self.config = config
        self.serial = SerialHandler(self.config)
        self.serial.connect()
        self.currPosSysCoords = Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)

    def sendCommand(self, coord):
        coordsSystem = self.config.drawing2systemCoords(coord)
        self.serial.sendCommand(coordsSystem)
        self.currPosSysCoords = coordsSystem

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
        self.currentPosition = self.config.drawing2screenCoords(
            self.config.system2drawingCoords(Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)))

    def sendCommand(self, coord):
        screenCoord = self.config.drawing2screenCoords(coord)
        if not coord.penup:
            self.screenDraw.line([int(round(self.currentPosition.x)), int(round(self.currentPosition.y)),
                                  int(round(screenCoord.x)), int(round(screenCoord.y))], fill=(0, 0, 0))
        self.currentPosition = screenCoord

    def finishDrawing(self):
        del self.screenDraw
        if self.config.showImage:
            self.screenImage.show()
        if self.config.saveImage:
            self.screenImage.save(''.join(('{}'.format(int(round(time() * 1000))), ".jpg")), "JPEG", optimize=True)


class Polargraph:
    def __enter__(self):
        return self

    def __init__(self):
        print("Polargraph __init__")
        self.config = PolarConfig()
        self.plotter = None
        self.drawer = None
        self.drawing = self.config.showImage or self.config.saveImage
        print(self.config)

        if self.drawing:
            self.drawer = Drawer(self.config)
            self.drawerConstraint = ConstrainDrawingRectangle(0, 0, self.config.pixels, self.config.heightPixels,
                                                              self.drawer)

        if self.config.polarDraw:
            self.plotter = Plotter(self.config)
            self.plotterConstraint = ConstrainDrawingRectangle(0, 0, self.config.pixels, self.config.heightPixels,
                                                               self.plotter)

    def __exit__(self, tpe=None, value=None, traceback=None):
        print("Polargraph __exit__")
        if self.drawing:
            self.drawer.finishDrawing()
        if self.config.polarDraw:
            self.plotter.finishDrawing()

    def sendCommand(self, coord):
        """
        sendCommand Ensured the commands are to draw entirely within the degined drawing area, if not only draw what
        is inside thge drawing area.  Sends the command to the drawing engines.
        :type coord: Coordinate
        :param coord: Coordinate to draw or move to in drawing coordinate system
        :return:
        """
        if self.drawing:
            self.drawer.sendCommand(coord)
        if self.config.polarDraw:
            self.plotter.sendCommand(coord)

    # High level drawing functions
    def moveTo(self, x, y):
        if self.drawing:
            self.drawerConstraint.moveTo(x, y)
        if self.config.polarDraw:
            self.plotterConstraint.moveTo(x, y)

    def drawTo(self, x, y):
        if self.drawing:
            self.drawerConstraint.drawTo(x, y)
        if self.config.polarDraw:
            self.plotterConstraint.drawTo(x, y)

    def goHome(self):
        if self.config.polarDraw:
            self.plotter.goHome()
        home = self.config.system2drawingCoords(Coordinate.fromCoords(self.config.homeX, self.config.homeY, True))
        self.moveTo(home.x, home.y)

    def penUp(self):
        if self.config.polarDraw:
            self.plotter.penUp()
