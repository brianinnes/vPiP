from Pylargraph import *
from PIL import Image, ImageDraw
import math

def circleBlip(centre, point, length):
    m = (point[1] - centre[1]) / (point[0] - centre[0])
    b = point[1] - m*point[0]

    diff = math.sqrt(length*length/(1 + m*m))
    x1 = point[0] - diff
    x2 = point[0] + diff

    y1 = m*x1 + b
    y2 = m*x2 + b
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



#im = Image.open("Angel.jpg")
im = Image.open("Vulcan.jpg")
#im = Image.open("queen.jpg")
im = im.convert('L')
# im.show()
pixels = im.load()
imgWidth, imgHeight = im.size

# polargraph scaling
Polargraph = polargraph.Polargraph

with Polargraph() as p:
    width = p.config.pixels - (2 * p.config.margin)
    height = imgHeight * width / imgWidth

    im2 = Image.new('RGB', (width, height), (255,255,255,255)) # create the image
    draw = ImageDraw.Draw(im2)   # create a drawing object that is
                                # used to draw on the new image
    separation = 60
    centre = (width/2 + p.config.margin, height/2 + p.config.margin)

    points = spiral_points(6, separation)
    pixmin = 30
    pixmax = 220


    def scaleDownCoords(pt):
        polargScaling = float(width) / imgWidth
        x = int(float(pt[0])/polargScaling)
        y = int(float(pt[1])/polargScaling)
        if x >= im.size[0]:
            x = im.size[0]-1
        if y >= im.size[1]:
            y = im.size[1]-1
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        return x, y

    count = 0
    prevPoint = None
    for i in points:
        point = (i[0] + centre[0], i[1] + centre[1])
        if count == 0:
            prevPoint = point
            p.moveTo(point[0], point[1])
        else:
            if (0 <= point[0] < width
                and 0 <= point[1] < height
                and 0 <= prevPoint[0] < width
                and 0 <= prevPoint[1] < height):
                imgPixel = scaleDownCoords(point)
                cpixel = pixels[imgPixel[0], imgPixel[1]]
                if cpixel < pixmin:
                    cpixel = pixmin
                if cpixel > pixmax:
                    cpixel = pixmax
                cpixelLOG = (math.log10(cpixel) - math.log10(pixmin)) / (math.log10(pixmax) - math.log10(pixmin))
                density  =  (separation/2) - cpixelLOG * separation/2
                if density > 0.02:
                    draw.line([prevPoint[0], prevPoint[1],
                                point[0], point[1]], fill=(0,0,0))
                    #p.drawTo(point[0], point[1])
                    blip =    circleBlip(centre, point, density)
                    p.drawTo(blip[0][0], blip[0][1])
                    p.drawTo(blip[1][0], blip[1][1])
                    # p.drawTo(point[0], point[1])
                    draw.line(blip, fill=(0,0,0))
                else:
                    p.moveTo(point[0], point[1])
            prevPoint = point
        count += 1
        if point[0] < (0 - height):
                break

    #p.penUp();
    p.goHome()
    del draw # I'm done drawing so I don't need this anymore

    # now, we tell the image to save as a PNG to the
    # provided file-like object
    im2.show()
