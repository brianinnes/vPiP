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
from Pylargraph import *

Polargraph = polargraph.Polargraph

with Polargraph() as p:
    try:
        p.moveTo(0, 0)
        p.drawTo(p.config.pixels, 0)
        p.drawTo(p.config.pixels, p.config.heightPixels)
        p.drawTo(0, p.config.heightPixels)
        p.drawTo(0, 0)
        p.moveTo(1, 1)
        p.drawTo(p.config.pixels - 1, 1)
        p.drawTo(p.config.pixels - 1, p.config.heightPixels - 1)
        p.drawTo(1, p.config.heightPixels - 1)
        p.drawTo(1, 1)
        p.goHome()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("test1 main thread exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
