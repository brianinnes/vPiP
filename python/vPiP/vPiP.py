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
from .config import PolarConfig
from .coordinates import Coordinate
from .constrainDrawingRectangle import ConstrainDrawingRectangle
from PIL import Image, ImageDraw
from time import time
from time import sleep
import paho.mqtt.client as mqtt
import ssl
import random

class outputter:
    def __init__(self, config):
        self.config = config

    def rotateCoords(self, coord):
        if self.config.rotate:
            return Coordinate.fromCoords(coord.y, self.config.pixels - coord.x, coord.penup)
        else:
            return coord

class MQTTPlotter(outputter):
    def __init__(self, config):
        outputter.__init__(self, config)
        self.currPosSysCoords = Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)
        self.mqttClient = mqtt.Client("vPiP_Client")
        self.mqttClient.username_pw_set(self.config.username, self.config.password)
        self.mqttClient.tls_insecure_set(True)
        self.mqttClient.tls_set(ca_certs="/Users/brian/.vpip/m2mqtt_ca.pem", certfile=None, keyfile=None,
                                cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        self.mqttClient.connect(self.config.broker, 8883, keepalive=60)
        self.mqttClient.loop_start()
        self.drawingID = random.randint(1, 65535)
        self.startTopic = "{}/start".format(self.config.plotterId)
        self.coordTopic = "{}/coord".format(self.config.plotterId)
        self.endTopic = "{}/end".format(self.config.plotterId)
        print("MQTT coordinate topic : %s" % self.coordTopic)
        self.topic = "{}/steps".format(self.config.plotterId)

        message = '{{\"id\": {} }}'.format(self.drawingID)
        self.mqttClient.publish(self.startTopic, message)


    def sendCommand(self, coord):
        coordsSystem = self.config.drawing2systemCoords(self.rotateCoords(coord))
        message = '{{\"id\": {}, \"x\": {}, \"y\" : {}, \"pUp\" : {} }}'.format(self.drawingID, coordsSystem.x, coordsSystem.y,
                                                                                "true" if coordsSystem.penup else "false")
        self.mqttClient.publish(self.coordTopic, message)
        self.currPosSysCoords = coordsSystem

    def finishDrawing(self):
        self.goHome()
        message = '{{\"id\": {} }}'.format(self.drawingID)
        self.mqttClient.publish(self.endTopic, message)
        sleep(2)
        self.mqttClient.disconnect()

    def penUp(self):
        self.currPosSysCoords = Coordinate.fromCoords(self.currPosSysCoords.x, self.currPosSysCoords.y, True)
        message = '{{\"id\": {}, \"x\": {}, \"y\" : {}, \"pUp\" : {} }}'.format(self.drawingID, self.currPosSysCoords.x,
                                                                                self.currPosSysCoords.y,
                                                                                "true" if self.currPosSysCoords.penup else "false")
        self.mqttClient.publish(self.coordTopic, message)

    def goHome(self):
        self.currPosSysCoords = Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)
        message = '{{\"id\": {}, \"x\": {}, \"y\" : {}, \"pUp\" : {} }}'.format(self.drawingID, self.currPosSysCoords.x,
                                                                                self.currPosSysCoords.y,
                                                                                "true" if self.currPosSysCoords.penup else "false")
        self.mqttClient.publish(self.coordTopic, message)
        self.mqttClient.publish(self.coordTopic, message)


class Drawer(outputter):
    def __init__(self, config):
        outputter.__init__(self, config)
        self.screenImage = None
        self.screenDraw = None
        if self.config.rotate:
            self.screenImage = Image.new('RGB', (self.config.heightScreen, self.config.screenX),
                                     (255, 255, 255, 255))  # create the image
        else:
            self.screenImage = Image.new('RGB', (self.config.screenX, self.config.heightScreen),
                                     (255, 255, 255, 255))  # create the image

        self.screenDraw = ImageDraw.Draw(self.screenImage)
        self.currentPosition = self.config.drawing2screenCoords(
            self.config.system2drawingCoords(Coordinate.fromCoords(self.config.homeX, self.config.homeY, True)))

    def sendCommand(self, coord):
        screenCoord = self.config.drawing2screenCoords(self.rotateCoords(coord))
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


class Vpip:
    def __enter__(self):
        return self

    def __init__(self):
        print("Vpip __init__")
        self.config = PolarConfig()
        self.plotter = None
        self.drawer = None
        self.drawing = self.config.showImage or self.config.saveImage
        self.started = False
        print(self.config)
        self.width = self.config.pixels
        self.height = self.config.heightPixels
        self.count = 0

    def __exit__(self, tpe=None, value=None, traceback=None):
        print("Vpip about to __exit__")
        sleep(2)
        print("Vpip __exit__")



    def _end(self):
        print("Vpip __end()")
        if self.drawing and not self.drawer is None:
            self.drawer.finishDrawing()
        if self.config.polarDraw and not self.plotter is None:
            self.plotter.finishDrawing()
        sleep(2)

    def _start(self):
        if not self.started:
            if self.drawing:
                self.drawer = Drawer(self.config)
                self.drawerConstraint = ConstrainDrawingRectangle(0, 0, self.config.pixels, self.config.heightPixels,
                                                                  self.drawer)
            if self.config.polarDraw:
                print("Vpip _start():self.config.polarDraw")
                if self.plotter is None:
                    self.plotter = MQTTPlotter(self.config)
                    self.plotterConstraint = ConstrainDrawingRectangle(0, 0, self.config.pixels, self.config.heightPixels,
                                                                   self.plotter)
            self.started = True

    def sendCommand(self, coord):
        """
        sendCommand Ensured the commands are to draw entirely within the degined drawing area, if not only draw what
        is inside thge drawing area.  Sends the command to the drawing engines.
        :type coord: Coordinate
        :param coord: Coordinate to draw or move to in drawing coordinate system
        :return:
        """
        self._start()
        if self.drawing:
            self.drawer.sendCommand(coord)
        if self.config.polarDraw:
            self.plotter.sendCommand(coord)

    # Override Config drawing and plotting config

    def setShowDrawing(self, setting):
        if setting:
            self.config.showImage = True
            self.drawing = True
            self.drawer = Drawer(self.config)
            self.drawerConstraint = ConstrainDrawingRectangle(0, 0, self.config.pixels, self.config.heightPixels,
                                                              self.drawer)
        else:
            self.config.showImage = False
            self.drawing = self.config.showImage or self.config.saveImage
            if not self.drawing:
                self.drawer = None
                self.drawerConstraint = None

    def setSaveDrawing(self, setting):
        if setting:
            self.config.saveImage = True
            self.drawing = True
            self.drawer = Drawer(self.config)
            self.drawerConstraint = ConstrainDrawingRectangle(0, 0, self.config.pixels, self.config.heightPixels,
                                                              self.drawer)
        else:
            self.config.saveImage = False
            self.drawing = self.config.showImage or self.config.saveImage
            if not drawing:
                self.drawer = None
                self.drawerConstraint = None

    def setPlotting(self, setting):
        print("Vpip setPlotting()")
        if setting != self.config.polarDraw:
            if setting:
                self.plotter = MQTTPlotter(self.config)
                self.plotterConstraint = ConstrainDrawingRectangle(0, 0, self.config.pixels, self.config.heightPixels,
                                                                self.plotter)
            else:
                self.plotter = None
                self.plotterConstraint = None
            self.config.polarDraw = setting

    # High level drawing functions
    def moveTo(self, x, y):
        self._start()
        if self.drawing:
            self.drawerConstraint.moveTo(x, y)
        if self.config.polarDraw:
            self.plotterConstraint.moveTo(x, y)

    def drawTo(self, x, y):
        self.count += 1
        self._start()
        if self.drawing:
            self.drawerConstraint.drawTo(x, y)
        if self.config.polarDraw:
            self.plotterConstraint.drawTo(x, y)

    def goHome(self):
        self._start()
        if self.config.polarDraw:
            self.plotter.goHome()
        home = self.config.system2drawingCoords(Coordinate.fromCoords(self.config.homeX, self.config.homeY, True))
        self.moveTo(home.x, home.y)

    def end(self):
        self._end()

    def penUp(self):
        self._start()
        if self.config.polarDraw:
            self.plotter.penUp()
