# Copyright 2016 Brian Innes
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import sys
import traceback
from math import pi, cos, sin, sqrt, log10
from ..generators.concircle import generateConcentricCircle
from PIL import Image
from ..constrainDrawingRectangle import ConstrainDrawingRectangle

class ConcentricCircleArc:
    def __init__(self, filename, x, y, width, drawer, pixelSize = 30, centre="NW"):
        self.fileName = filename
        self.pixelSize = float(pixelSize)
        self.phi = 0.0
        self.r = 0.0
        self.direction = 1
        self.pixelAngle = 0.0
        self.angleStep = 0.0
        self.im = Image.open(self.fileName)
        self.im = self.im.convert('L')
        self.pixels = self.im.load()
        self.imgWidth, self.imgHeight = self.im.size
        self.imageScaling = float(width) / self.imgWidth
        height = self.imgHeight * self.imageScaling
        self.offSetX = x
        self.offSetY = y
        self.drawer = ConstrainDrawingRectangle(x, y, width + x, height + y, drawer)
        self.pixmin = 30
        self.pixmax = 220
        self.logPixmin = log10(self.pixmin)
        self.logPixmax = log10(self.pixmax)
        self.centre = centre
        self.centres = {
            "NE": (width + x, y),
            "SE": (width + x, height + y),
            "SW": (x, height + y),
            "NW": (x, y)
        }
        self.angles = {
            "NE": (0.5, pi),
            "SE": (pi , 1.5 * pi),
            "SW": (1.5 * pi, 2 * pi),
            "NW": (0, 0.5 * pi)
        }
        self.coord = self.centres[self.centre]


    def scaleDownCoords(self, pt):
        x = int(float(pt[0] - self.offSetX) / self.imageScaling)
        y = int(float(pt[1] - self.offSetY) / self.imageScaling)
        if x > self.imgWidth - 1:
            x = self.imgWidth - 1
        if y > self.imgHeight - 1:
            y = self.imgHeight - 1
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        return x, y


    def calculateDensity(self, point):
                imgPixel = self.scaleDownCoords(point)
                cpixel = self.pixels[imgPixel[0], imgPixel[1]]
                if cpixel < self.pixmin:
                    cpixel = self.pixmin
                if cpixel > self.pixmax:
                    cpixel = self.pixmax
                return (log10(cpixel) - self.logPixmin) / (self.logPixmax - self.logPixmin)

    def p2c(self, r, phi):
        return (r * cos(phi) + self.centres[self.centre][0], r * sin(phi) + self.centres[self.centre][1])

    def positionDrawingCoords(self, p):
        return (p[0], p[1])

    def arcGenerator(self):
        self.direction = 1
        self.r = self.pixelSize/2
        maxR = sqrt(self.drawer.height * self.drawer.height +  self.drawer.width * self.drawer.width)
        yield self.centres[self.centre]
        while self.r < maxR:
            self.pixelAngle = self.pixelSize / self.r
            angleOK = True
            self.phi = self.angles[self.centre][self.direction]
            while angleOK:
                yield self.p2c(self.r, self.phi)
                self.phi = self.phi - self.pixelAngle if self.direction == 1 else self.phi + self.pixelAngle
                if self.direction == 1:
                    angleOK = self.phi > self.angles[self.centre][0]
                else:
                    angleOK = self.phi < self.angles[self.centre][1]
            self.phi = self.angles[self.centre][self.direction]
            self.direction = (self.direction + 1) % 2
            self.r += self.pixelSize

    def generateCoordinates(self):
        try:
            penup=True
            for c in self.arcGenerator():
                first = True
                density = (self.pixelSize / 2) - self.calculateDensity(c) * self.pixelSize / 2.2
                if density > 1.0:
                    # generateConcentricCircle(positionX,positionY,maxSize,density)
                    for p in generateConcentricCircle(c[0], c[1], self.pixelSize, density):
                        translatedP = self.positionDrawingCoords(p)
                        if first:
                            if penup:
                                self.drawer.moveTo(translatedP[0], translatedP[1])
                            else:
                                self.drawer.drawTo(translatedP[0], translatedP[1])
                            first = False
                        else:
                            self.drawer.drawTo(translatedP[0], translatedP[1])
                            penup=False
                else:
                    translatedC = self.positionDrawingCoords(c)
                    self.drawer.moveTo(translatedC[0], translatedC[1])
                    penup=True
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("test1 main thread exception : %s" % exc_type)
            traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)



def renderConcentricCircleArc(fileName, x, y, width, resolution, drawer, centre="NW"):
    generator = ConcentricCircleArc(fileName, x, y, width, drawer, resolution, centre)
    generator.generateCoordinates()
