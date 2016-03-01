import sys
import traceback
from Pylargraph import *
from Pylargraph.renderers.norwegianSpiral import renderNorwegianSpiral
Polargraph = polargraph.Polargraph

filename = "Vulcan.jpg"
with Polargraph() as p:
    try:
        renderNorwegianSpiral(filename, 300, 200, 600, 9.6, 10, 3, p)
        renderNorwegianSpiral(filename, 200, 1000, 800, 9.7, 10, 3, p)
        renderNorwegianSpiral(filename, 0, 1950, 1200, 9.8, 10, 3, p)
        renderNorwegianSpiral(filename, 1200, 0, 3800, 9.9, 10, 3, p)
        p.goHome()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("test1 main thread exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)