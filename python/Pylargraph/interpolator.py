from math import sqrt, pow, ceil

from coordinates import Coordinate


class TrapezoidInterpolater:
    def __init__(self):
        self.destination = None
        self.direction = None
        self.distance = 0.0
        self.entrySpeed = 0.0
        self.exitSpeed = 0.0
        self.cruiseSpeed = 0.0
        self.accelDist = 0.0
        self.accelTime = 0.0
        self.decelDist = 0.0
        self.decelTime = 0.0
        self.cruiseDist = 0.0
        self.cruiseTime = 0.0
        self.acceleration = 0.0
        self.time = 0.0
        self.slices = 0
        self.origin = None
        self.config = None

    def setup(self, config, origin, dest, nextDest):
        self.entrySpeed = self.exitSpeed
        self.origin = origin
        self.destination = dest
        self.config = config

        if origin == dest:
            self.direction = Coordinate.fromCoords(0, 1, origin.penup)
            self.distance = 0.0
            self.exitSpeed = self.entrySpeed
            self.cruiseSpeed = self.entrySpeed
            self.accelDist = 0.0
            self.accelTime = 0.0
            self.cruiseDist = 0.0
            self.cruiseTime = 0.0
            self.decelDist = 0.0
            self.decelTime = 0.0
            self.acceleration = config.AccelerationMMs2
            self.time = 0.0
            self.slices = 0
        else:
            self.direction = dest - origin
            self.distance = self.direction.length()
            self.direction = self.direction.normalised()

            nextDirection = nextDest - dest
            if nextDirection.length() == 0 or nextDest.penup != dest.penup:
                self.exitSpeed = 0
            else:
                nextDirection = nextDirection.normalised()
                cosAngle = self.direction.dotProduct(nextDirection)
                cosAngle = pow(cosAngle, 3)
                self.exitSpeed = config.MaxSpeedMMs * max(cosAngle, 0.0)
            self.cruiseSpeed = config.MaxSpeedMMs

            self.accelTime = (self.cruiseSpeed - self.entrySpeed) / config.AccelerationMMs2
            self.accelDist = (0.5 *
                              config.AccelerationMMs2 * self.accelTime * self.accelTime +
                              self.entrySpeed * self.accelTime)

            self.decelTime = (self.cruiseSpeed - self.exitSpeed) / config.AccelerationMMs2
            self.decelDist = (0.5 *
                              -config.AccelerationMMs2 * self.decelTime * self.decelTime +
                              self.cruiseSpeed * self.decelTime)

            self.cruiseDist = self.distance - (self.accelDist + self.decelDist)
            self.cruiseTime = self.cruiseDist / self.cruiseSpeed

            self.acceleration = config.AccelerationMMs2

            if self.distance < self.accelDist + self.decelDist:
                self.decelTime = (sqrt(2) * sqrt(
                    self.exitSpeed * self.exitSpeed + self.entrySpeed * self.entrySpeed +
                    2 * config.AccelerationMMs2 * self.distance) - 2 * self.exitSpeed) / \
                                 (2 * config.AccelerationMMs2)
                self.cruiseTime = 0
                self.cruiseSpeed = self.exitSpeed + config.AccelerationMMs2 * self.decelTime
                self.accelTime = (self.cruiseSpeed - self.entrySpeed) / config.AccelerationMMs2

                if self.decelTime < 0 or self.accelTime < 0:
                    if self.exitSpeed > self.entrySpeed:
                        self.decelDist = 0.0
                        self.decelTime = 0.0
                        self.cruiseDist = 0.0
                        self.cruiseTime = 0.0

                        self.accelTime = (sqrt(self.entrySpeed * self.entrySpeed +
                                               2 * config.AccelerationMMs2 * self.distance) -
                                          self.entrySpeed) / config.AccelerationMMs2
                        self.exitSpeed = self.entrySpeed + config.AccelerationMMs2 * self.accelTime
                        self.cruiseSpeed = self.exitSpeed
                        self.accelDist = self.distance
                    else:
                        self.accelDist = 0.0
                        self.accelTime = 0.0
                        self.cruiseDist = 0.0
                        self.cruiseTime = 0.0

                        self.decelTime = 2.0 * self.distance / (self.exitSpeed + self.entrySpeed)
                        self.acceleration = (self.entrySpeed - self.exitSpeed) / self.decelTime
                        self.cruiseSpeed = self.entrySpeed
                        self.decelDist = self.distance
                else:
                    self.accelDist = (0.5 * config.AccelerationMMs2 * self.accelTime *
                                      self.accelTime + self.entrySpeed * self.accelTime)
                    self.cruiseDist = 0.0
                    self.decelDist = (0.5 * -config.AccelerationMMs2 * self.decelTime *
                                      self.decelTime + self.cruiseSpeed * self.decelTime)
            self.time = self.accelTime + self.cruiseTime + self.decelTime
            self.slices = int(ceil(self.time / (config.timeSliceUS / 1000000)))

    def slices(self):
        return self.slices

    def position(self, slce):
        if slce == self.slices:
            return self.destination
        else:
            time = (float(slce) / self.slices) * self.time

            if time < self.accelTime:
                distanceAlongMovement = 0.5 * self.config.AccelerationMMs2 * time * time + self.entrySpeed * time
            elif time < self.accelTime + self.cruiseTime:
                time -= self.accelTime
                distanceAlongMovement = self.accelDist + time * self.cruiseSpeed
            else:
                time -= self.accelTime + self.cruiseTime
                distanceAlongMovement = (self.accelDist + self.cruiseDist + 0.5 * -self.acceleration
                                         * time * time + self.cruiseSpeed * time)
            return self.origin + (self.direction * distanceAlongMovement)

    def writeData(self):
        print "Origin: {}, Dest: {}".format(self.origin, self.destination)
        print 'Dir: {}, Slices: {}'.format(self.direction, self.slices)
        print "Entry: {}, Cruise: {}, Exit: {}".format(self.entrySpeed, self.cruiseSpeed, self.exitSpeed)
        print "Taccel: {}, Tcruise: {}, Tdecel: {}".format(self.accelTime, self.cruiseTime, self.decelTime)
        print "Daccel: {}, Dcruise: {}. Ddecel: {}".format(self.accelDist, self.cruiseDist, self.decelDist)
        print "Total distance: {}".format(self.distance)
