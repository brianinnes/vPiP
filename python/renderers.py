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
from pyPlotter import *
from pyPlotter.renderers.spiralArcRenderer import renderSpiralArc
from pyPlotter.renderers.norwegianSpiral import renderNorwegianSpiral
PyPlotter = pyPlotter.PyPlotter

filename = "../testImages/Vulcan.jpg"
# filename = "../testImages/TyneBridge.jpg"
# filename = "../testImages/SydneyOpera.jpg"
# filename = "../testImages/SydneyOperaNight.jpg"
# filename = "../testImages/HamptonCourt.jpg"
with PyPlotter() as p:
#    p.setShowDrawing(True)
#    p.setPlotting(False)
    try:
        renderSpiralArc(filename, 10, 10, 2200, 10, p)
        renderNorwegianSpiral(filename, 2510, 10, 2200, 9.9, 10, 3, p)
        renderSpiralArc(filename, 10, p.height/2 +10, 2200, 30, p)
        renderNorwegianSpiral(filename, 2510, p.height/2 + 10, 2200, 9.6, 10, 5, p)
        p.goHome()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("test1 main thread exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)