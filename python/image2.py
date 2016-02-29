from Pylargraph import polargraph, constrainDrawingRectangle
from PIL import Image
import math


def circleBlip(centre, point, length):
    m = (point[1] - centre[1]) / (point[0] - centre[0])
    b = point[1] - m * point[0]

    diff = math.sqrt(length * length / (1 + m * m))
    x1 = point[0] - diff
    x2 = point[0] + diff

    y1 = m * x1 + b
    y2 = m * x2 + b
    return (x1, y1), (x2, y2)


def spiral_points(arc=1, separation=1):
    """generate points on an Archimedes' spiral
    with `arc` giving the length of arc between two points
    and `separation` giving the distance between consecutive
    turnings
    - approximate arc length with circle arc at given distance
    - use a spiral equation r = b * phi
    :param separation:
    :param arc:
    """

    def p2c(r, phi):
        """polar to cartesian
        :param phi:
        :param r:
        """
        return r * math.cos(phi), r * math.sin(phi)

    # yield a point at origin
    yield (0, 0)

    # initialize the next point in the required distance
    r = arc
    b = separation / (2 * math.pi)
    # find the first phi to satisfy distance of `arc` to the second point
    phi = float(r) / b
    count = 0
    while True:
        count += 1
        yield p2c(r, phi)
        # advance the variables
        # calculate phi that will give desired arc length at current radius
        # (approximating with circle)
        phi += float(arc) / r
        r = b * phi


im = Image.open("Vulcan.jpg")
#im = Image.open("Angel.jpg")
# im = Image.open("queen.jpg")
im = im.convert('L')
# im.show()
pixels = im.load()
imgWidth, imgHeight = im.size

# polargraph scaling
Polargraph = polargraph.Polargraph

with Polargraph() as p:
    width = p.config.pixels
    height = imgHeight * width / imgWidth

    if height > p.config.heightPixels:
        height = p.config.heightPixels
        width = imgWidth * height / imgHeight
    drawingConstraint = constrainDrawingRectangle.ConstrainDrawingRectangle(0, 0, width, height, p)

    separation = 20
    centre = (width / 2, height / 2)

    points = spiral_points(2, separation)
    pixmin = 30
    pixmax = 220


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
        point = (i[0] + centre[0], i[1] + centre[1])
        if count == 0:
            drawingConstraint.moveTo(point[0], point[1])
        else:
            imgPixel = scaleDownCoords(point)
            cpixel = pixels[imgPixel[0], imgPixel[1]]
            if cpixel < pixmin:
                cpixel = pixmin
            if cpixel > pixmax:
                cpixel = pixmax
            cpixelLOG = (math.log10(cpixel) - math.log10(pixmin)) / (math.log10(pixmax) - math.log10(pixmin))
            density = (separation / 2) - cpixelLOG * separation / 2
            if density > 0.02:
                blip = circleBlip(centre, point, density)
                drawingConstraint.drawTo(blip[0][0], blip[0][1])
                drawingConstraint.drawTo(blip[1][0], blip[1][1])
            else:
                drawingConstraint.moveTo(point[0], point[1])
        count += 1
        if point[0] < (0 - height) and point[1] < (0 - height):
            break
