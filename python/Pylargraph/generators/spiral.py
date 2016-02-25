import math


def drawSpiral(self, centreX, centreY, radius, density, maxDensity):
    def spiral_points(centreX, centreY, radius, density, maxDensity):
        def p2c(r, phi):
            return r * math.cos(phi) + centreX, r * math.sin(phi) + centreY

        arc = 2.0
        phi = 0.0

        if maxDensity > radius:
            md = float(maxDensity)
            d = float(density)
        else:
            md = float(radius)
            d = float(radius) * density / maxDensity

        if density > 0:
            yield (centreX, centreY)
            separation = float(maxDensity - density) * 15 / maxDensity + 1
            r = float(arc)
            b = float(separation) / (2 * math.pi)
            phi = float(r) / b
            count = 0
            while r <= radius:
                count += 1
                yield p2c(r, phi)
                phi += float(arc) / r
                r = b * phi
        circB = phi + (2 * math.pi)
        arc = 2
        while phi <= circB:
            yield p2c(radius, phi)
            phi += float(arc) / radius
        return

    points = spiral_points(centreX, centreY, radius, density, maxDensity)
    count = 0
    for i in points:
        point = (i[0], i[1])
        if count == 0:
            self.moveTo(i[0], i[1])
        else:
            self.drawTo(point[0], point[1])
        count += 1
