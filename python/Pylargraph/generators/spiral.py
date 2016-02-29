import math


def generateSpiral(centreX, centreY, radius, density, maxDensity, resolution):
    def p2c(r, phi):
        return r * math.cos(phi) + centreX, r * math.sin(phi) + centreY

    arc = resolution
    phi = 0.0

    md = float(radius)
    d = float(radius) * density / maxDensity

    if density > 0:
        yield (centreX, centreY)
        separation = max((md - d + 1) * radius / md / 2, 2)

        r = float(arc)
        b = float(separation) / (2 * math.pi)
        phi = float(r) / b
        count = 0
        while r <= radius:
            count += 1
            yield p2c(r, phi)
            phi += float(arc) / r
            r = b * phi
    # draw boundary circle
    circB = phi + (2 * math.pi)
    arc = resolution
    while phi <= circB:
        yield p2c(radius, phi)
        phi += float(arc) / radius
    return
