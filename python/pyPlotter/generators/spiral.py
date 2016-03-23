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
import math


def generateSpiral(centreX, centreY, radius, density, maxDensity, resolution):
    def p2c(r, phi):
        return r * math.cos(phi) + centreX, r * math.sin(phi) + centreY

    arc = resolution
    phi = 0.0
    try:
        md = float(radius)
        d = float(radius) * density / maxDensity

        if density > 0:
            yield (centreX, centreY)
            separation = max((md - d + 1) * radius / md / 2, 2)

            r = float(arc)
            b = float(separation) / (2 * math.pi)
            phi = float(r) / b
            count = 0
            while r <= radius:
                count += 1
                yield p2c(r, phi)
                phi += float(arc) / r
                r = b * phi
        # draw boundary circle
        circB = phi + (2 * math.pi)
        arc = resolution
        while phi <= circB:
            yield p2c(radius, phi)
            phi += float(arc) / radius
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
    return
