from ..constrainDrawingRectangle import ConstrainDrawingRectangle
from ..generators.spiral import generateSpiral
from PIL import Image
from math import sqrt, log10
import sys
import traceback


def renderNorwegianSpiral(fileName, x, y, width, density, maxDensity, resolution, drawer):
    try:
        im = Image.open(fileName)
        im = im.convert('L')
        pixels = im.load()
        imgWidth, imgHeight = im.size

        height = imgHeight * width / imgWidth
        drawingConstraint = ConstrainDrawingRectangle(x, y, width + x, height + y, drawer)



        centre = (width / 2, height / 2)
        radius = sqrt((centre[0] * centre[0]) + (centre[1] * centre[1]))

        md = float(radius)
        d = float(radius) * density / maxDensity
        separation = max((md - d + 1) * radius / md / 2, 2)

        # points = spiral_points(2, separation)
        points = generateSpiral(centre[0], centre[1], radius, density, maxDensity, resolution)
        pixmin = 30
        pixmax = 220
        logPixmin = log10(pixmin)
        logPixmax = log10(pixmax)

        def circleBlip(centre, point, length):
            m = (point[1] - centre[1]) / (point[0] - centre[0])
            b = point[1] - m * point[0]

            diff = sqrt(length * length / (1 + m * m))
            x1 = point[0] - diff
            x2 = point[0] + diff

            y1 = m * x1 + b
            y2 = m * x2 + b
            return (x1, y1), (x2, y2)

        def scaleDownCoords(pt):
            polargScaling = float(width) / imgWidth
            x = int(float(pt[0]) / polargScaling)
            y = int(float(pt[1]) / polargScaling)
            if x > im.size[0] - 1:
                x = im.size[0] - 1
            if y > im.size[1] - 1:
                y = im.size[1] - 1
            if x < 0:
                x = 0
            if y < 0:
                y = 0
            return x, y


        count = 0
        for i in points:
            point = (i[0], i[1])
            if count == 0:
                drawingConstraint.moveTo(point[0] + x, point[1] + y)
            else:
                imgPixel = scaleDownCoords(point)
                cpixel = pixels[imgPixel[0], imgPixel[1]]
                if cpixel < pixmin:
                    cpixel = pixmin
                if cpixel > pixmax:
                    cpixel = pixmax
                cpixelLOG = (log10(cpixel) - logPixmin) / (logPixmax - logPixmin)
                density = (separation / 2) - cpixelLOG * separation / 2
                if density > 0.02:
                    blip = circleBlip(centre, point, density)
                    drawingConstraint.drawTo(blip[0][0] + x, blip[0][1] + y)
                    drawingConstraint.drawTo(blip[1][0] + x, blip[1][1] + y)
                else:
                    drawingConstraint.moveTo(point[0] + x, point[1] + y)
            count += 1
            if point[0] < (0 - height) and point[1] < (0 - height):
                break
        im.close()
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("test1 main thread exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
