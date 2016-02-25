import sys
import traceback
from Pylargraph import *

Polargraph = polargraph.Polargraph

with Polargraph() as p:
    try:
        p.moveTo(0, 0)
        p.drawTo(p.config.pixels, 0)
        p.drawTo(p.config.pixels, p.config.HeightPixels)
        p.drawTo(0, p.config.HeightPixels)
        p.drawTo(0,0)

        gridX = (p.config.pixels-20) / 10
        gridY = (p.config.HeightPixels-20) / 10

        x = 10
        y = 10

        while x+gridX < p.config.pixels:
            while y+gridY < p.config.HeightPixels:
                p.moveTo(x, y)
                p.drawTo(x+gridX, y)
                p.drawTo(x+gridX, y+gridY)
                p.drawTo(x, y+gridY)
                p.drawTo(x, y)
                y += gridY
                x += gridX
        p.goHome()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("test1 main thread exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
