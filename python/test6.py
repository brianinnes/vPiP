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

# Example test script for the concentric circle arc renderer

# Will attempt to open an image viewer to display the simulated plot.
# Comment out p.setShowDrawing(True) & p.setPlotting(False) to physically plot this
# Use p.setSaveDrawing(True) with p.setPlotting(False) to save the simulated plot.

import sys
import traceback
from Pylargraph import *
from Pylargraph.renderers.spiralArcRenderer import renderSpiralArc
from Pylargraph.renderers.conCircleArcRenderer import renderConcentricCircleArc
Polargraph = polargraph.Polargraph

filename = "../testImages/Vulcan.jpg"
# filename = "../testImages/TyneBridge.jpg"
# filename = "../testImages/SydneyOpera.jpg"
# filename = "../testImages/SydneyOperaNight.jpg"
# filename = "../testImages/HamptonCourt.jpg"
with Polargraph() as p:
    p.setShowDrawing(True)
    #p.setSaveDrawing(True)
    p.setPlotting(False)
    try:
        renderConcentricCircleArc(filename, 300, 200, 600, 10, p)
        renderConcentricCircleArc(filename, 200, 1000, 800, 15, p)
        renderConcentricCircleArc(filename, 0, 1950, 1200, 20, p)
        renderConcentricCircleArc(filename, 1250, 50, 3700, 25, p)
        p.goHome()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("test1 main thread exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
