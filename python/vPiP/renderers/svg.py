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
import re
from math import pow
from xml.dom import minidom, Node
from ..coordinates import Coordinate

class SVGElement:
    @classmethod
    def fromXMLElement(cls, node):
        obj = None
        if node.nodeType is Node.ELEMENT_NODE:
            obj = cls(node.nodeName)
            if node.hasAttributes():
                obj.parseAttributes(node.attributes)
            if node.hasChildNodes():
                obj.parseChildNodes(node.childNodes)
        return obj

    def __init__(self, nodeType):
        self.nodeType = nodeType
        self.childElements = []
        self.drawingCoords = None
        self.elementTypes = {
            "svg" : NodeSvg.fromXMLElement,
            "g" : NodeGroup.fromXMLElement,
            "path" : NodePath.fromXMLElement,
            "rect" : NodeRect.fromXMLElement,
            "circle" : NodeCircle.fromXMLElement,
            "ellipse" : NodeEllipse.fromXMLElement,
            "line" : NodeLine.fromXMLElement,
            "polyline" : NodePolyline.fromXMLElement,
            "polygon" : NodePolygon.fromXMLElement
        }

    def __str__(self):
        if isinstance(self, NodeUnsupported):
            ret = "Unsupported Node: {}\n".format(self.nodeType)
        else:
            ret = "Node: {}\nDict = {}\n:".format(self.nodeType, self.__dict__)
            if self.childElements is not None:
                for i in self.childElements:
                    ret += str(i)
        return ret

    def parseChildNodes(self, nodeList):
        for node in nodeList:
            object = self.elementTypes.get(node.nodeName, NodeUnsupported.fromXMLElement)(node)
            if object is not None:
                self.childElements.append(object)

    def parseAttributes(self, attributes):
        for j in range(0, attributes.length):
            attrib = attributes.item(j)
            # strip namespace prefix from attrib names if exist
            if attrib.name.count(':') == 1:
                attrib.name = attrib.name.split(':')[1]
            self.__dict__[attrib.name] = attrib.value

    def createDrawingCoords(self):
        # sub classes need to provide the implementation of this method
        if self.drawingCoords is None:
            self.drawingCoords = []
            for elem in self.childElements:
                coords = elem.createDrawingCoords()
                if coords is not None:
                    self.drawingCoords += coords
        if len(self.drawingCoords) > 0:
            return self.drawingCoords
        else:
            return None

    def getDrawingCoords(self):
        ret = self.createDrawingCoords()
        for child in self.childElements:
            ret += child.getDrawingCoords()
        return ret

class NodeSvg(SVGElement):
    def createDrawingCoords(self):
        return self.drawingCoords

class NodeGroup(SVGElement):
    def createDrawingCoords(self):
        coords = SVGElement.createDrawingCoords(self)
        if coords is not None:
            self.drawingCoords += coords
        return self.drawingCoords

class NodePath(SVGElement):
    def __init__(self, nodeType):
        SVGElement.__init__(self, nodeType)
        self.currentPath = None
        self.pathIterator = None
        self.currentCoord = None
        self.currentCommand = ''
        self.additionalParameter = None
        self.currentPathStartPosition = None
        self.lastCurveControlPoint = None
        self.svgPathSegmentCommands = {
            "c": self.relativeCurve,
            "C": self.curve,
            "h": self.relativeHorizontal,
            "H": self.horizontal,
            "l": self.relativeLine,
            "L": self.line,
            "m": self.relativeMove,
            "M": self.move,
            "s": self.relativeSmoothCurve,
            "S": self.smoothCurve,
            "v": self.relativeVertical,
            "V": self.vertical,
            "z": self.closePath,
            "Z": self.closePath
        }
        self.svgAdditionalCoords = {
            "c": self.relativeCurve,
            "C": self.curve,
            "h": self.relativeHorizontal,
            "H": self.horizontal,
            "l": self.relativeLine,
            "L": self.line,
            "m": self.relativeLine,
            "M": self.line,
            "s": self.relativeSmoothCurve,
            "S": self.smoothCurve,
            "v": self.relativeVertical,
            "V": self.vertical,
        }
        self.curveCommands = set('cCsS')
        # this following tokeniser is from http://codereview.stackexchange.com/questions/28502/svg-path-parsing
        self.COMMANDS = set('MmZzLlHhVvCcSsQqTtAa')
        self.COMMAND_RE = re.compile("([MmZzLlHhVvCcSsQqTtAa])")
        self.FLOAT_RE = re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")

    def _tokenize_path(self, pathdef):
        for x in self.COMMAND_RE.split(pathdef):
            if x in self.COMMANDS:
                yield x
            for token in self.FLOAT_RE.findall(x):
                yield token

    # cubic bezier curve implementation info from : http://pomax.github.io/bezierinfo/
    def _cubicCoord(self, points, t):
        if len(points) == 1:
            return points[0]
        else:
            newpoints = [None] * (len(points) - 1)
            for i in range(0, len(newpoints)):
                x = (1.0 - t) * points[i][0] + t * points[i+1][0]
                y = (1.0 - t) * points[i][1] + t * points[i+1][1]
                newpoints[i] = (x, y)
            return self._cubicCoord(newpoints, t)

    # quadratic bezier curve implementation info from : http://stackoverflow.com/questions/31757501/pixel-by-pixel-bezier-curve
    def _quadraticCoord(self, point, t):
        x = pow(1.0-t,2)*point[0][0] + 2 * (1.0-t) * t * point[1][0] + pow(t,2) * point[2][0]
        y = pow(1.0-t,2)*point[0][1] + 2 * (1.0-t) * t * point[1][1] + pow(t,2) * point[2][1]
        return (x, y)

    def curveCoords(self, points):
        minX = min(points[0][0], min(points[1][0], min(points[2][0], points[2][0])))
        maxX = max(points[0][0], max(points[1][0], max(points[2][0], points[2][0])))
        minY = min(points[0][1], min(points[1][1], min(points[2][1], points[2][1])))
        maxY = max(points[0][1], max(points[1][1], max(points[2][1], points[2][1])))
        segments = max(maxX - minX, maxY - minY)
        if not (self.currentCoord == Coordinate.fromCoords(points[0][0], points[0][1], self.currentCoord.penup)):
            self.drawingCoords.append(Coordinate.fromCoords(self.currentCoord.x, self.currentCoord.y, True))
        step = 1.0 / segments
        t = step
        while t < 1.0:
            point = self._cubicCoord(points, t)
            self.drawingCoords.append(Coordinate.fromCoords(point[0], point[1], False))
            t += step
        self.drawingCoords.append(Coordinate.fromCoords(points[3][0], points[3][1], False))
        self.currentCoord = Coordinate.fromCoords(points[3][0], points[3][1], False)
        self.lastCurveControlPoint = points[2]

    def relativeCurve(self):
        x1 = self.additionalParameter
        self.additionalParameter = None
        if x1 is None:
            x1 = float(next(self.pathIterator))
        y1 = float(next(self.pathIterator))
        x2 = float(next(self.pathIterator))
        y2 = float(next(self.pathIterator))
        x = float(next(self.pathIterator))
        y = float(next(self.pathIterator))
        points = [(self.currentCoord.x, self.currentCoord.y),
                  (self.currentCoord.x + x1, self.currentCoord.y + y1),
                  (self.currentCoord.x + x2, self.currentCoord.y + y2),
                  (self.currentCoord.x + x, self.currentCoord.y + y)]
        self.curveCoords(points)
        return None

    def curve(self):
        x1 = self.additionalParameter
        self.additionalParameter = None
        if x1 is None:
            x1 = float(next(self.pathIterator))
        y1 = float(next(self.pathIterator))
        x2 = float(next(self.pathIterator))
        y2 = float(next(self.pathIterator))
        x = float(next(self.pathIterator))
        y = float(next(self.pathIterator))
        points = [(self.currentCoord.x, self.currentCoord.y), (x1, y1), (x2, y2), (x, y)]
        self.curveCoords(points)
        return None

    def relativeHorizontal(self):
        x = self.additionalParameter
        self.additionalParameter = None
        if x is None:
            x = float(next(self.pathIterator))
        self.currentCoord = Coordinate.fromCoords(self.currentCoord.x + x, self.currentCoord.y, False);
        return self.currentCoord

    def horizontal(self):
        x = self.additionalParameter
        self.additionalParameter = None
        if x is None:
            x = float(next(self.pathIterator))
        self.currentCoord = Coordinate.fromCoords(x, self.currentCoord.y, False);
        return self.currentCoord

    def relativeLine(self):
        x = self.additionalParameter
        self.additionalParameter = None
        if x is None:
            x = float(next(self.pathIterator))
        y = float(next(self.pathIterator))
        self.currentCoord = Coordinate.fromCoords(self.currentCoord.x + x, self.currentCoord.y + y, False);
        return self.currentCoord

    def line(self):
        x = self.additionalParameter
        self.additionalParameter = None
        if x is None:
            x = float(next(self.pathIterator))
        y = float(next(self.pathIterator))
        self.currentCoord = Coordinate.fromCoords(x, y, False);
        return self.currentCoord

    def relativeMove(self):
        if self.currentCoord is None:
            return self.move()
        else:
            x = self.additionalParameter
            self.additionalParameter = None
            if x is None:
                x = float(next(self.pathIterator))
            y = float(next(self.pathIterator))
            self.currentCoord = Coordinate.fromCoords(self.currentCoord.x + x, self.currentCoord.y + y, True)
            self.currentPathStartPosition = self.currentCoord
        return self.currentCoord

    def move(self):
        x = self.additionalParameter
        self.additionalParameter = None
        if x is None:
            x = float(next(self.pathIterator))
        y = float(next(self.pathIterator))
        self.currentCoord = Coordinate.fromCoords(x, y, True)
        self.currentPathStartPosition = self.currentCoord
        return self.currentCoord

    def relativeSmoothCurve(self):
        x2 = self.additionalParameter
        self.additionalParameter = None
        if x2 is None:
            x2 = float(next(self.pathIterator))
        y2 = float(next(self.pathIterator))
        x = float(next(self.pathIterator))
        y = float(next(self.pathIterator))
        if self.currentCommand in self.curveCommands:
            x1 = self.currentCoord.x + self.currentCoord.x - self.lastCurveControlPoint[0]
            y1 = self.currentCoord.y + self.currentCoord.y - self.lastCurveControlPoint[1]
            firstControlPoint = (x1, y1)
        else:
            firstControlPoint = (self.currentCoord.x, self.currentCoord.y)
        points = [(self.currentCoord.x, self.currentCoord.y),
                  firstControlPoint,
                  (self.currentCoord.x + x2, self.currentCoord.y + y2),
                  (self.currentCoord.x + x, self.currentCoord.y + y)]
        self.curveCoords(points)
        return None

    def smoothCurve(self):
        x2 = self.additionalParameter
        self.additionalParameter = None
        if x2 is None:
            x2 = float(next(self.pathIterator))
        y2 = float(next(self.pathIterator))
        x = float(next(self.pathIterator))
        y = float(next(self.pathIterator))
        if self.currentCommand in self.curveCommands:
            x1 = self.currentCoord.x + self.currentCoord.x - self.lastCurveControlPoint[0]
            y1 = self.currentCoord.y + self.currentCoord.y - self.lastCurveControlPoint[1]
            firstControlPoint = (x1, y1)
        else:
            firstControlPoint = (self.currentCoord.x, self.currentCoord.y)
        points = [(self.currentCoord.x, self.currentCoord.y), firstControlPoint, (x2, y2), (x, y)]
        self.curveCoords(points)
        return None

    def relativeVertical(self):
        y = self.additionalParameter
        self.additionalParameter = None
        if y is None:
            y = float(next(self.pathIterator))
        self.currentCoord = Coordinate.fromCoords(self.currentCoord.x, self.currentCoord.y + y, False);
        return self.currentCoord

    def vertical(self):
        y = self.additionalParameter
        self.additionalParameter = None
        if y is None:
            y = float(next(self.pathIterator))
        self.currentCoord = Coordinate.fromCoords(self.currentCoord.x, y, False);
        return self.currentCoord

    def closePath(self):
        self.currentCoord = Coordinate.fromCoords(self.currentPathStartPosition.x, self.currentPathStartPosition.y, False)
        return self.currentCoord

    def unknownCommand(self):
        print('Unknown command : {}').format(self.currentCommand)
        return None

    def createDrawingCoords(self):
        if self.drawingCoords is None:
            self.drawingCoords = []
            self.pathIterator = self._tokenize_path(self.d)
            while True:
                try:
                    command = next(self.pathIterator)
                    if not command in self.COMMANDS:
                        self.additionalParameter = float(command)
                        coord = self.svgAdditionalCoords.get(self.currentCommand)()
                    else:
                        coord = self.svgPathSegmentCommands.get(command.strip(), self.unknownCommand)()
                        self.currentCommand = command.strip()
                    if coord is not None:
                        self.drawingCoords.append(coord)
                except StopIteration:
                    break
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print("test1 main thread exception : %s" % exc_type)
                    traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
        return self.drawingCoords

class NodeRect(SVGElement):
    def createDrawingCoords(self):
        return self.drawingCoords

class NodeCircle(SVGElement):
    def createDrawingCoords(self):
        return self.drawingCoords

class NodeEllipse(SVGElement):
    def createDrawingCoords(self):
        return self.drawingCoords

class NodeLine(SVGElement):
    def createDrawingCoords(self):
        if self.drawingCoords is None:
            self.drawingCoords = []
            self.drawingCoords.append(Coordinate.fromCoords(self.x1, self.y1, True))
            self.drawingCoords.append(Coordinate.fromCoords(self.x2, self.y2, False))
        return self.drawingCoords

class NodePolyline(SVGElement):
    def __init__(self, nodeType):
        SVGElement.__init__(self, nodeType)
        self.FLOAT_RE = re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")

    def _tokenize_path(self, pathdef):
        for token in self.FLOAT_RE.findall(pathdef):
            yield token

    def createDrawingCoords(self):
        if self.drawingCoords is None:
            self.drawingCoords = []
            tokens = self._tokenize_path(self.points)
            x = float(next(tokens))
            y = float(next(tokens))
            self.drawingCoords.append(Coordinate.fromCoords(x, y, True))
            while True:
                try:
                    self.drawingCoords.append(Coordinate.fromCoords(float(next(tokens)), float(next(tokens)), False))
                except StopIteration:
                    break
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print("test1 main thread exception : %s" % exc_type)
                    traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
        return self.drawingCoords

class NodePolygon(SVGElement):
    def __init__(self, nodeType):
        SVGElement.__init__(self, nodeType)
        self.FLOAT_RE = re.compile("[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?")

    def _tokenize_path(self, pathdef):
        for token in self.FLOAT_RE.findall(pathdef):
            yield token

    def createDrawingCoords(self):
        if self.drawingCoords is None:
            self.drawingCoords = []
            tokens = self._tokenize_path(self.points)
            x = float(next(tokens))
            y = float(next(tokens))
            startX, startY = x, y
            self.drawingCoords.append(Coordinate.fromCoords(x, y, True))
            while True:
                try:
                    self.drawingCoords.append(Coordinate.fromCoords(float(next(tokens)), float(next(tokens)), False))
                except StopIteration:
                    break
                except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print("test1 main thread exception : %s" % exc_type)
                    traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
            self.drawingCoords.append(Coordinate.fromCoords(startX, startY, False))

        return self.drawingCoords
class NodeUnsupported(SVGElement):
    pass

class SVG:
    def __init__(self, filename):
        self.filename = filename
        self.xmlDoc = minidom.parse(filename)
        self.svgElement = None
        self.children = []
        self.drawingCoords = None
        if self.xmlDoc.hasChildNodes():
            for i in self.xmlDoc.childNodes:
                n = SVGElement.fromXMLElement(i)
                if n is not None and n.nodeType == "svg":
                    self.svgElement = n
                if n is not None:
                    self.children.append(n)
        if self.svgElement is not None and "width" in self.svgElement.__dict__:
            if "viewBox" in self.svgElement.__dict__:
                parts = re.findall(r"[\w.]+",  self.svgElement.viewBox)
                self.svgElement.width = parts[2]
                self.svgElement.height = parts[3]



    def createDrawingCoords(self):
        self.drawingCoords = []
        for elem in self.children:
            coords = elem.createDrawingCoords()
            if coords is not None:
                self.drawingCoords += coords
        return self.drawingCoords

    def drawSVG(self, x, y, width, drawer, fit):
        if self.drawingCoords is None:
            try:
                self.createDrawingCoords()
            except:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    print("test1 main thread exception : %s" % exc_type)
                    traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)

        scale = float(width) / float(self.svgElement.width)
        if fit:
            scale = float(drawer.width) / float(self.svgElement.width)
            if float(self.svgElement.height) * scale > drawer.height:
                scale = float(drawer.height) / float(self.svgElement.height)
        try:
            for c in self.drawingCoords:
                if not isinstance(c, Coordinate):
                    print("Not a coord {}").format(c)
                c *= scale
                if c.penup == True:
                    drawer.moveTo(c.x + x, c.y + y)
                else:
                    drawer.drawTo(c.x + x, c.y + y)
        except:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("drawSVG exception : %s" % exc_type)
            traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)


def renderSVG(fileName, x, y, width, drawer, fit=False):
    svgImage = SVG(fileName)
    svgImage.drawSVG(x, y, width, drawer, fit)
