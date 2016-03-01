from coordinates import Coordinate


class ConstrainDrawingRectangle:
    def __init__(self, x1, y1, x2, y2, sendingTarget):
        self.constraint1 = Coordinate.fromCoords(min(x1, x2), min(y1, y2),
                                                 False)
        self.constraint2 = Coordinate.fromCoords(max(x1, x2), max(y1, y2),
                                                 False)
        self.sendingTarget = sendingTarget
        self.outstandingMove = False
        self.moveDrawingCoordinates = None
        self.outOfBounds = True
        self.outOfBoundsDrawingCoord = None
        self.currentDrawingPosition = None

    def isOutsideDrawingArea(self, coord):
        """
        :param coord:
        :rtype: bool
        """
        if coord.x < self.constraint1.x \
                or coord.x > self.constraint2.x \
                or coord.y < self.constraint1.y \
                or coord.y > self.constraint2.y:
            return True
        else:
            return False

    def crossBoundary(self, coord, leaving):
        ret = None
        if leaving:
            m = (self.currentDrawingPosition.y - coord.y) / (self.currentDrawingPosition.x - coord.x)
            b = self.currentDrawingPosition.y - m * self.currentDrawingPosition.x
            if coord.x < self.constraint1.x:
                ret = Coordinate.fromCoords(self.constraint1.x, m * self.constraint1.x + b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and coord.x > self.constraint2.x:
                ret = Coordinate.fromCoords(self.constraint2.x, m * self.constraint2.x + b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and coord.y < self.constraint1.y:
                ret = Coordinate.fromCoords((self.constraint1.y - b) / m, self.constraint1.y, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and coord.y > self.constraint2.y:
                ret = Coordinate.fromCoords((self.constraint2.y - b) / m, self.constraint2.y, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
        else:
            m = (coord.y - self.outOfBoundsDrawingCoord.y) / (coord.x - self.outOfBoundsDrawingCoord.x)
            b = coord.y - m * coord.x
            if self.outOfBoundsDrawingCoord.x < self.constraint1.x:
                ret = Coordinate.fromCoords(self.constraint1.x, m * self.constraint1.x + b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and self.outOfBoundsDrawingCoord.x > self.constraint2.x:
                ret = Coordinate.fromCoords(self.constraint2.x, m * self.constraint2.x + b, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and self.outOfBoundsDrawingCoord.y < self.constraint1.y:
                ret = Coordinate.fromCoords((self.constraint1.y - b) / m, self.constraint1.y, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
            if ret is None and self.outOfBoundsDrawingCoord.y > self.constraint2.y:
                ret = Coordinate.fromCoords((self.constraint2.y - b) / m, self.constraint2.y, coord.penup)
                if self.isOutsideDrawingArea(ret):
                    ret = None
        if ret is None:
            print("Oops - somethings went wrong")
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
                    self.sendingTarget.sendCommand(coord)

                else:
                    # This command is a draw, so calculate where the line crosses the drawing area boundary and
                    # draw a line from the crossing point to the point specified in the command
                    crossBoundryPoint = self.crossBoundary(coord, False)
                    crossBoundryPoint.penup = True
                    self.sendingTarget.sendCommand(crossBoundryPoint)
                    self.sendingTarget.sendCommand(coord)
                self.outOfBounds = False
        else:
            # drawing position before this command was inside the drawing area
            if self.isOutsideDrawingArea(coord):
                # This command will take the drawing position outside the drawing area.  I not a move then draw a line
                # to the point where the line crosses the drawing area boundary
                if not coord.penup:
                    crossBoundryPoint = self.crossBoundary(coord, True)
                    self.sendingTarget.sendCommand(crossBoundryPoint)
                self.outOfBoundsDrawingCoord = coord
                self.outOfBounds = True
            else:
                # all inside drawing area
                self.sendingTarget.sendCommand(coord)
            self.currentDrawingPosition = coord

    def moveTo(self, x, y):
        self.moveDrawingCoordinates = Coordinate.fromCoords(x, y, True)
        self.outstandingMove = True

    def drawTo(self, x, y):
        if self.outstandingMove:
            self.sendCommand(self.moveDrawingCoordinates)
            self.currentDrawingPosition = self.moveDrawingCoordinates
            self.outstandingMove = False
        coords = Coordinate.fromCoords(x, y, False)
        self.sendCommand(coords)
        self.currentDrawingPosition = coords
