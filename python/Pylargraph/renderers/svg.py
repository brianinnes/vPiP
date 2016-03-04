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
            "polygone" : NodePolygon.fromXMLElement
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
            self.drawingCoords.append(coords)
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
        self.svgPathSegmentCommands = {
            "l": self.relativeLine,
            "L": self.line,
            "m": self.relativeMove,
            "M": self.move,
            "z": self.closePath,
            "Z": self.closePath
        }
        self.svgAdditionalCoords = {
            "l": self.relativeLine,
            "L": self.line,
            "m": self.relativeLine,
            "M": self.line,
        }

    def splitCoordinates(self, coords):
        if ',' in coords:
            xy = coords.split(',')
            return float(xy[0]), float(xy[1])
        else:
            return coords


    def relativeLine(self):
        coords = self.additionalParameter
        self.additionalParameter = None
        if coords is None:
            coords = self.pathIterator.next()
        x, y = self.splitCoordinates(coords)
        self.currentCoord = Coordinate.fromCoords(self.currentCoord.x + x, self.currentCoord.y + y, False);
        return self.currentCoord

    def line(self):
        coords = self.additionalParameter
        self.additionalParameter = None
        if coords is None:
            coords = self.pathIterator.next()
        x, y = self.splitCoordinates(coords)
        self.currentCoord = Coordinate.fromCoords(self.currentCoord.x, self.currentCoord, False);
        return self.currentCoord

    def relativeMove(self):
        if self.currentPathStartPosition is None:
            self.move()
        else:
            coords = self.additionalParameter
            self.additionalParameter = None
            if coords is None:
                coords = self.pathIterator.next()
            x, y = self.splitCoordinates(coords)
            self.currentCoord = Coordinate.fromCoords(self.currentCoord.x + x, self.currentCoord + y, True);
        return self.currentCoord

    def move(self):
        coords = self.additionalParameter
        self.additionalParameter = None
        if coords is None:
            coords = self.pathIterator.next()
        x, y = self.splitCoordinates(coords)
        self.currentCoord = Coordinate.fromCoords(x, y, True)
        self.currentPathStartPosition = self.currentCoord
        return self.currentCoord

    def closePath(self):
        self.currentCoord = Coordinate.fromCoords(self.currentPathStartPosition.x, self.currentPathStartPosition.y, False)
        self.currentPathStartPosition = None
        return self.currentCoord

    def unknownCommand(self):
        print('Unknown command : {}').format(self.currentCommand)
        return None

    def createDrawingCoords(self):
        if self.drawingCoords is None:
            self.drawingCoords = []
            self.pathIterator = iter(self.d.split())
            while True:
                try:
                    command = self.pathIterator.next()
                    coord = None
                    if ',' in command:
                        self.additionalParameter = command
                        coord = self.svgAdditionalCoords.get(self.currentCommand)()
                    else:
                        self.currentCommand = command
                        coord = self.svgPathSegmentCommands.get(self.currentCommand.strip(), self.unknownCommand)()
                    if coord is not None:
                        self.drawingCoords.append(coord)
                except StopIteration:
                    break
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
        return self.drawingCoords

class NodePolyline(SVGElement):
    def createDrawingCoords(self):
        return self.drawingCoords

class NodePolygon(SVGElement):
    def createDrawingCoords(self):
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


    def createDrawingCoords(self):
        self.drawingCoords = []
        for elem in self.children:
            coords = elem.createDrawingCoords()
            if coords is not None:
                self.drawingCoords += coords
        return self.drawingCoords

    def drawSVG(self, x, y, width, drawer):
        if self.drawingCoords is None:
            self.createDrawingCoords()

        scale = float(width) / float(self.svgElement.width)
        for c in self.drawingCoords:
            c *= scale
            if c.penup == True:
                drawer.moveTo(c.x + x, c.y + y)
            else:
                drawer.drawTo(c.x + x, c.y + y)


def renderSVG(fileName, x, y, width, drawer):
    svgImage = SVG(fileName)
    svgImage.drawSVG(x, y, width, drawer)