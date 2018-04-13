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
import json
import paho.mqtt.client as mqtt
import ssl
import random
from array import array
from threading import Thread, Event
from multiprocessing import Process, Event, JoinableQueue
from serial import Serial
from .coordinates import Coordinate, PolarCoordinate
from .interpolator import TrapezoidInterpolater
from time import sleep

#try:
#    from Queue import Queue
#except ImportError:
#    from queue import Queue

class SerialHandler:
    def __init__(self, config):
        self.config = config
        self.coordQueue = JoinableQueue()
        self.stepQueue = JoinableQueue()
        self.connected = False
        self.stopRequestCoord = Event()
        self.stopRequestStep = Event()
        self.startedCoord = Event()
        self.startedStepWorker = Event()
        self.serialPort = None
        self.coordWorker = None
        self.stepWorker = None
        self.mqttClient = None

    def _coordHandlerThread(self, q, stopRequest, started):

        self.mqttClient.loop_start()
        totalLeftSteps = 0
        totalRightSteps = 0
        currentPenup = True
        origin = Coordinate.fromCoords(self.config.homeX,
                                       self.config.homeY,
                                       currentPenup)
        prevPolarPos = self.config.system2polarCoords(origin)
        polarHome = self.config.system2polarCoords(origin)
        scalefactor = (float(self.config.stepsSizeMM) / self.config.stepMultiplier)
        multfactor = (self.config.stepMultiplier / self.config.stepsSizeMM)

        interp = TrapezoidInterpolater()

        started.set()
        target = q.get()
        q.task_done()
        drawingID = random.randint(1,65535)
        startTopic = "{}/start".format(self.config.plotterId)
        coordTopic = "{}/coord".format(self.config.plotterId)
        endTopic = "{}/end".format(self.config.plotterId)
        print("MQTT coordinate topic : %s" % coordTopic)
        topic = "{}/steps".format(self.config.plotterId)

        message = '{{\"id\": {} }}'.format(drawingID)
        self.mqttClient.publish(startTopic, message)
#        while (not q.empty()) or (not stopRequest.is_set()):
        while (not q.empty()):
            try:
                if q.empty():
                    nextTarget = target
                else:
                    nextTarget = q.get()
                    q.task_done()

#                message = json.dumps({"x": target.x, "y": target.y, "penup": target.penup})
                message = '{{\"id\": {}, \"x\": {}, \"y\" : {}, \"pUp\" : {} }}'.format(drawingID, target.x, target.y, "true" if target.penup else "false")
                self.mqttClient.publish(coordTopic, message)

                if target.penup != currentPenup:
#                    if target.penup:
#                       sq.put(self.config.penUpCommand)
#                       sq.put(self.config.penUpCommand)
#                        message = json.dumps({"L": self.config.penUpCommand, "R": self.config.penUpCommand})
#                        message = 'p u'
#                        self.mqttClient.publish(topic, message)
#                    else:
#                        sq.put(self.config.penDownCommand)
#                        sq.put(self.config.penDownCommand)
#                        message = json.dumps({"L": self.config.penDownCommand, "R": self.config.penDownCommand})
#                        message = 'p d'
#                        self.mqttClient.publish(topic, message)
                    currentPenup = target.penup
                interp.setup(self.config, origin, target, nextTarget)
                for timeSlice in range(1, interp.slices + 1):
                    sliceTarget = interp.position(int(timeSlice))
                    polarSliceTarget = self.config.system2polarCoords(sliceTarget)
                    sliceSteps = (polarSliceTarget - prevPolarPos) * multfactor
                    sliceSteps.ceil().clamp(self.config.stepsMaxValue, -self.config.stepsMaxValue)
                    ls = int(sliceSteps.leftDist)
                    rs = int(-sliceSteps.rightDist)
                    totalLeftSteps += ls
                    totalRightSteps -= rs
#                    sq.put(ls)
#                    sq.put(rs)
#                    message = json.dumps({"L" : ls, "R" : rs})
#                    self.mqttClient.publish(topic, message)
                    prevPolarPos = polarHome + PolarCoordinate.fromCoords(totalLeftSteps * scalefactor,
                                                                          totalRightSteps * scalefactor, target.penup)
                origin = self.config.polar2systemCoords(prevPolarPos)
                target = nextTarget
                sleep(0)
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("Coord handler thread exception : %s" % exc_type)
                traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
            message = '{{\"id\": {} }}'.format(drawingID)
            self.mqttClient.publish(endTopic, message)
#        stopRequestStep.set()

    def _stepHandlerThread(self, q, stopRequest, started):
        started.set()
        writeData = array('b')
        for i in range(0, 128):
            writeData.append(0)
        while (not q.empty()) or (not stopRequest.is_set()):
            try:
                if self.serialPort.inWaiting() > 0:
                    dataRead = self.serialPort.read()
                    numBytes = ord(dataRead)
                    for i in range(0, numBytes, 2):
                        if q.empty():
                            writeData[i] = 0
                            writeData[i + 1] = 0
                        else:
                            writeData[i] = q.get()
                            q.task_done()
                            writeData[i + 1] = q.get()
                            q.task_done()
                    self.serialPort.write(writeData.tostring())
                    self.serialPort.flush()
                    sleep(0)

            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                print("Step handler thread exception : %s" % exc_type)
                traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)

    def connect(self):
        self.mqttClient = mqtt.Client("vPiP_Client")
        self.mqttClient.username_pw_set(self.config.username, self.config.password)
        self.mqttClient.tls_insecure_set(True)
        self.mqttClient.tls_set(ca_certs="/Users/brian/.vpip/m2mqtt_ca.pem", certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2, ciphers=None)
        self.mqttClient.connect(self.config.broker, 8883, keepalive=60)

#        self.serialPort = Serial(self.config.serialPort, self.config.baud, timeout=10)
#        self.coordWorker = Thread(target=self._coordHandlerThread, args=(self.coordQueue, self.stopRequest, self.startedCoord,))
#        self.coordWorker = Process(target=self._coordHandlerThread, args=(self.coordQueue, self.stepQueue, self.stopRequestCoord, self.stopRequestStep, self.startedCoord, ))
        self.coordWorker = Process(target=self._coordHandlerThread, args=(self.coordQueue, self.stopRequestCoord, self.startedCoord, ))
        self.coordWorker.start()
#        self.stepWorker = Thread(target=self._stepHandlerThread, args=(self.stepQueue, self.stopRequest, self.startedStepWorker,))
#        self.stepWorker = Process(target=self._stepHandlerThread, args=(self.stepQueue, self.stopRequestStep, self.startedStepWorker, ))
#        self.stepWorker.start()
#        while (not self.startedCoord.is_set()) or (not self.startedStepWorker.is_set()):
        while (not self.startedCoord.is_set()):
            sleep(0)
        self.connected = True
        print("Connected to Vpip")

    def disconnect(self):
        self.stopRequestCoord.set()
        self.coordQueue.join()
#        self.stepQueue.join()
        self.coordWorker.join()
#        self.stepWorker.join()
#        self.serialPort.close()
        self.mqttClient.disconnect()
        self.mqttClient.loop_stop()

    def sendCommand(self, command):
        if not self.connected:
            self.connect()
        self.coordQueue.put(command)
