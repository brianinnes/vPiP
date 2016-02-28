from os.path import expanduser, isfile, exists, dirname
from os import makedirs
from coordinates import Coordinate, PolarCoordinate
from math import sqrt, floor
import ConfigParser
import errno


class PolarConfig:
    def __init__(self):
        self.resetCommand = -128
        self.penUpCommand = -127
        self.penDownCommand = 127
        self.stepsMaxValue = 126.0
        self.configFile = None
        self.configured = False
        self.penSize = 0
        self.machineWidth = 0
        self.machineHeight = 0
        self.mmPerRev = 0.0
        self.stepsPerRev = 0
        self.stepMultiplier = 0
        self.serialPort = ''
        self.timeSliceUS = 0
        self.baud = 0
        self.motorAccel = 0.0
        self.motorMaxSpeed = 0.0
        self.penUp = 0
        self.penDown = 0
        self.homeX = 0
        self.homeY = 0
        self.polarDraw = False
        self.size = ''
        self.width = 0
        self.height = 0
        self.posX = 0
        self.posY = 0
        self.margin = 0
        self.pixels = 0
        self.rotate = False
        self.screenX = 0
        self.showImage = False
        self.saveImage = False
        self.stepsSizeMM = 0.0
        self.stepsPerValue = 0.0
        self.MaxSpeedMMs = 0.0
        self.AccelerationMMs2 = 0.0
        self.pixelsPerMM = 0.0
        self.heightPixels = 0.0
        self.heightScreen = 0
        self.loadConfig()

    def __str__(self):
        return '\n'.join(
            ("***** System configuration *****",
             "configured = {}".format(self.configured),
             "penSize = {}".format(self.penSize),
             "machineWidth = {}".format(self.machineWidth),
             "machineHeight = {}".format(self.machineHeight),
             "mmPerRev = {}".format(self.mmPerRev),
             "stepsPerRev = {}".format(self.stepsPerRev),
             "stepMultiplier = {}".format(self.stepMultiplier),
             "serialPort = {}".format(self.serialPort),
             "timeSliceUS = {}".format(self.timeSliceUS),
             "baud = {}".format(self.baud),
             "motorAccel = {}".format(self.motorAccel),
             "motorMaxSpeed = {}".format(self.motorMaxSpeed),
             "penUp = {}".format(self.penUp),
             "penDown = {}".format(self.penDown),
             "homeX = {}".format(self.homeX),
             "homeY = {}".format(self.homeY),
             "polarDraw = {}".format(self.polarDraw),
             "size = {}".format(self.size),
             "width = {}".format(self.width),
             "height = {}".format(self.height),
             "posX = {}".format(self.posX),
             "posY = {}".format(self.posY),
             "margin = {}".format(self.margin),
             "pixelsX = {}".format(self.pixels),
             "pixelsY = {}".format(self.heightPixels),
             "rotate = {}".format(self.rotate),
             "stepsSizeMM = {}".format(self.stepsSizeMM),
             "stepsPerValue = {}".format(self.stepsPerValue),
             "MaxSpeedMMs = {}".format(self.MaxSpeedMMs),
             "AccelerationMMs2 = {}".format(self.AccelerationMMs2),
             "screenX = {}".format(self.screenX),
             "screenY = {}".format(self.heightScreen),
             "showImage = {}".format(self.showImage),
             "saveImage = {}".format(self.saveImage)))

    def loadConfig(self):
        self.configFile = expanduser("~/.polargraph/config.cfg")
        print("Config is being read from %s\n" % self.configFile)
        if isfile(self.configFile):
            config = ConfigParser.ConfigParser()
            config.read(self.configFile)
            self.configured = True
            self.penSize = config.getfloat('Polargraph', 'penSize')
            self.machineWidth = config.getint('Polargraph', 'machineWidth')
            self.machineHeight = config.getint('Polargraph', 'machineHeight')
            self.mmPerRev = config.getfloat('Polargraph', 'mmPerRev')
            self.stepsPerRev = config.getint('Polargraph', 'stepsPerRev')
            self.stepMultiplier = config.getint('Polargraph', 'stepMultiplier')
            self.serialPort = config.get('Polargraph', 'serialPort')
            self.timeSliceUS = config.getfloat('Polargraph', 'timeSliceUS')
            self.baud = config.getint('Polargraph', 'baud')
            self.motorAccel = config.getfloat('Polargraph', 'motorAccel')
            self.motorMaxSpeed = config.getfloat('Polargraph', 'motorMaxSpeed')
            self.penUp = config.getint('Polargraph', 'penUp')
            self.penDown = config.getint('Polargraph', 'penDown')
            self.homeX = config.getint('Polargraph', 'homeX')
            self.homeY = config.getint('Polargraph', 'homeY')
            self.polarDraw = config.getboolean('Polargraph', 'polarDraw')
            self.size = config.get('Paper', 'size')
            self.width = config.getint('Paper', 'width')
            self.height = config.getint('Paper', 'height')
            self.posX = config.getint('Paper', 'posX')
            self.posY = config.getint('Paper', 'posY')
            self.margin = config.getint('Paper', 'margin')
            self.pixels = config.getint('Paper', 'pixels')
            self.rotate = config.getboolean('Paper', 'rotate')
            self.screenX = config.getint('Screen', 'screenX')
            self.showImage = config.getboolean('Screen', 'showImage')
            self.saveImage = config.getboolean('Screen', 'saveImage')
        else:
            self.configured = False
            self.createDefaultConfig()
            self.loadConfig()
        self.stepsSizeMM = (1.0 / self.stepsPerRev / self.stepMultiplier) * self.mmPerRev
        stepsPerRevolution = self.stepsPerRev * self.stepMultiplier
        self.stepsPerValue = self.stepsMaxValue / self.stepMultiplier
        self.MaxSpeedMMs = min(self.motorMaxSpeed, (
            (self.stepsPerValue / (self.timeSliceUS / 1000000.0)) / stepsPerRevolution) * self.mmPerRev)
        self.AccelerationMMs2 = self.MaxSpeedMMs / self.motorAccel
        self.pixelsPerMM = float(self.pixels) / (self.width - 2 * self.margin)
        self.heightPixels = int(floor(float((self.height) - 2 * self.margin) * self.pixelsPerMM))
        self.heightScreen = int(floor(float(self.heightPixels) * self.screenX/self.pixels))

    def createDefaultConfig(self):
        config = ConfigParser.ConfigParser()
        config.add_section('Polargraph')
        config.set('Polargraph', 'penSize', '0.0')
        config.set('Polargraph', 'machineWidth', '0')
        config.set('Polargraph', 'machineHeight', '0')
        config.set('Polargraph', 'mmPerRev', '0.0')
        config.set('Polargraph', 'stepsPerRev', '0')
        config.set('Polargraph', 'stepMultiplier', '0')
        config.set('Polargraph', 'serialPort', 'none')
        config.set('Polargraph', 'timeSliceUS', 0.0)
        config.set('Polargraph', 'baud', '0')
        config.set('Polargraph', 'motorAccel', '0.0')
        config.set('Polargraph', 'motorMaxSpeed', '0.0')
        config.set('Polargraph', 'penUp', '0')
        config.set('Polargraph', 'penDown', '0')
        config.set('Polargraph', 'homeX', '0')
        config.set('Polargraph', 'homeY', '0')
        config.set('Polargraph', 'polarDraw', True)
        config.add_section('Paper')
        config.set('Paper', 'size', 'custom')
        config.set('Paper', 'width', 0)
        config.set('Paper', 'height', 0)
        config.set('Paper', 'posX', 0)
        config.set('Paper', 'posY', 0)
        config.set('Paper', 'margin', 0)
        config.set('Paper', 'pixels', 0)
        config.set('Paper', 'rotate', False)
        config.set('Screen', 'screenX', 0)
        config.set('Screen', 'showImage', False)
        config.set('Screen', 'saveImage', False)
        if not exists(dirname(self.configFile)):
            try:
                makedirs(dirname(self.configFile))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(self.configFile, 'wb') as configfile:
            config.write(configfile)

    def writeConfig(self):
        if self.configured:
            config = ConfigParser.ConfigParser()
            config.add_section('Polargraph')
            config.set('Polargraph', 'penSize', self.penSize)
            config.set('Polargraph', 'machineWidth', self.machineWidth)
            config.set('Polargraph', 'machineHeight', self.machineHeight)
            config.set('Polargraph', 'mmPerRev', self.mmPerRev)
            config.set('Polargraph', 'stepsPerRev', self.stepsPerRev)
            config.set('Polargraph', 'stepMultiplier', self.stepMultiplier)
            config.set('Polargraph', 'serialPort', self.serialPort)
            config.set('Polargraph', 'timeSliceUS', self.timeSliceUS)
            config.set('Polargraph', 'baud', self.baud)
            config.set('Polargraph', 'motorAccel', self.motorAccel)
            config.set('Polargraph', 'motorMaxSpeed', self.motorMaxSpeed)
            config.set('Polargraph', 'penUp', self.penUp)
            config.set('Polargraph', 'penDown', self.penDown)
            config.set('Polargraph', 'homeX', self.homeX)
            config.set('Polargraph', 'homeY', self.homeY)
            config.set('Polargraph', 'polarDraw', self.polarDraw)
            config.add_section('Paper')
            config.set('Paper', 'size', self.size)
            config.set('Paper', 'width', self.width)
            config.set('Paper', 'height', self.height)
            config.set('Paper', 'posX', self.posX)
            config.set('Paper', 'posY', self.posY)
            config.set('Paper', 'margin', self.margin)
            config.set('Paper', 'pixelsX', self.pixels)
            config.set('Paper', 'rotate', self.rotate)
            config.add_section('Screen')
            config.set('Screen', 'screenX', self.screenX)
            config.set('Screen', 'showImage', self.showImage)
            config.set('Screen', 'saveImage', self.saveImage)
            if not exists(dirname(self.configFile)):
                try:
                    makedirs(dirname(self.configFile))
                except OSError as exc:  # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
            with open(self.configFile, 'wb') as configfile:
                config.write(configfile)
        else:
            print('ERROR-Trying to write configuration when unconfigured!')

        # @TODO - add rotate feature

    def system2drawingCoords(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        mmCoord = coord.translate(self.posX - self.margin, self.posY  - self.margin)
        return mmCoord * self.pixelsPerMM

    def drawing2systemCoords(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        mmCoord = coord.divide(self.pixelsPerMM)
        return mmCoord.translate(self.posX + self.margin, self.posY + self.margin)

    def drawing2screenCoords(self, coord):
        """
        :type coord: Coordinate
        :rtype: Coordinate
        """
        return coord*self.screenX/self.pixels

    def system2polarCoords(self, coord):
        """
        :param coord:
        :rtype: PolarCoordinate
        """
        xdiff = float(self.machineWidth) - coord.x
        return PolarCoordinate.fromCoords(sqrt(coord.x * coord.x + coord.y * coord.y),
                                          sqrt(xdiff * xdiff + coord.y * coord.y), coord.penup)

    def polar2systemCoords(self, coord):
        """
        :param coord:
        :rtype: Coordinate
        """
        if coord.leftDist + coord.rightDist > self.machineWidth:
            # print "polar2systemCoords-{}".format(coord)
            x = ((float(coord.leftDist * coord.leftDist) - (coord.rightDist * coord.rightDist) +
                  float(self.machineWidth * self.machineWidth)) / (2.0 * self.machineWidth))
            y = sqrt((coord.leftDist * coord.leftDist) - (x * x))
            return Coordinate.fromCoords(x, y, coord.penup)
        else:
            print "WARN: polar2systemCoords received invalid coordinate {}".format(coord)
            return Coordinate.fromCoords(0, 0, coord.penup)
