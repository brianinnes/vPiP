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
