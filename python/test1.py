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
from vPiP import *

Vpip = vPiP.Vpip

with Vpip() as p:
    p.setShowDrawing(True)
    p.setPlotting(False)
    try:
        p.moveTo(0, 0)
        p.drawTo(p.config.pixels, 0)
        p.drawTo(p.config.pixels, p.config.heightPixels)
        p.drawTo(0, p.config.heightPixels)
        p.drawTo(0, 0)

        gridX = (p.config.pixels - 20) / 10
        gridY = (p.config.heightPixels - 20) / 10

        x = 10
        while x + gridX < p.config.pixels:
            y = 10
            while y + gridY < p.config.heightPixels:
                p.moveTo(x, y)
                p.drawTo(x + gridX, y)
                p.drawTo(x + gridX, y + gridY)
                p.drawTo(x, y + gridY)
                p.drawTo(x, y)
                y += gridY
            x += gridX
        p.goHome()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("test1 main thread exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
