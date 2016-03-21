# Copyright 2016 Mark Benson, portions Copyright 2016 Brian Innes
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
import math

# How do we generate concentric circles?
# We generate n circles of varying size.
# The higher the density, the more circles
# So we can take the density and create a big circle of size = density and iterate down to zero
# How do we ensure the circles are spaced far enough apart?
# That could be based on the pen size/density/max pixel size or we could take the density value and divide it by some
# number - say 2 or 3 to space the circles out. Or it could be dynamically calculated.

# For a first pass, Lets do it manually with a fixed spacing.

def generateConcentricCircle(positionX,positionY,maxSize,density):

    radius = int(density) # How big is our biggest circle
    points = [] # List of genereated co-ordinates (Could probably be replaced with a tuple to store the last value)
    spacing = 3 # How far apart (in pixels) are our concentric circles
    numberOfCircles = int(radius / spacing) # How many concentric circles 

    try:
        # Iterate over the number of circles
        for circleNumber in range(numberOfCircles,0,-1):
            # Start with the biggest circle and work down
            radius = circleNumber * spacing

            # Work out the x & y coordinates of the circle using the Angle and the radius.
            # Well do this for every whole degree in a circle which might cause a lumpy
            # circle when the circle is big... but we can look at that case if it happens.
            # Also we have to work out when a result is a step change
            # (i.e. the value we get isn't in the same pixel as the last one.
            for angle in range(0,360):
                
                y = int((math.sin(math.radians(angle)) * radius)) + positionY
                x = int((math.cos(math.radians(angle)) * radius)) + positionX

                # Step change. How do we tell if the values have changed much?
                # Compare our newly genereated x,y values against the last stored set of values
                # If they are the same, don't bother storing them, it they are new, store them
                # Does this make a clean circle or are their odd pixels?

                # See note above about replacing the list as we probably don't need to list anymore

                if len(points): #If the list has anything in it check new points against old
                    if points[len(points)-1][0] != x or points[len(points)-1][1] != y:
                        points.append((x,y))
                        yield((x,y))
                else:
                    points.append((x,y))
                    yield((x,y))
                    
            #for each in points:
            #    yield(each[0],each[1])
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("exception : %s" % exc_type)
        traceback.print_tb(exc_traceback, limit=2, file=sys.stdout)
    
    return
