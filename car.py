# GUI and Physics depiction of a car(ball) in a mountain valley
# Author: Matthew Atteberry

import pygame
from pygame.locals import * # grant easy access to pygame constants
from pygame.color import * # grant easy access to pygame colors
import pymunk
from pymunk.vec2d import Vec2d as vec
import math

from pymunk.vec2d import Vec2d as v2

X,Y = 0,1
SCENE_WIDTH = 600
SCENE_HEIGHT = 600
PYMUNK_GRAVITY = -981.0
B_DEGREE = 2
B_SMOOTHNESS = 10
DT = 1.0/60.0 # define physics time step
DT_MS = DT * 1000 # time step in milliseconds

def bSplineCurve(cPoints, degree, smoothness):
    """
    Uses De Boore's algorithm to output an array of points depicting a smooth curve based on control points
    :param cPoints: an array of pymunk.Vec2d control points to define shape of curve
    :param degree: the degree of each b-spline polynomial (2=quadratic, 3=cubic, etc)
    :param smoothness: how many points to fit between control points (e.g. 3=3 points between each cPoint)
    :return: an array of pymunk.Vec2d points that form a smooth curve
    """

    numPoints = len(cPoints)
    points = [cPoints[0]]*degree + cPoints + [cPoints[numPoints-1]]*(degree) #To make interface more inutive, pad first and last points
    numPoints = len(points)
    #list of equidistant knots for open uniform bSpline Curve
    knots = [float(degree)]*degree + [float(i+degree) for i in range(numPoints)] #Padding for knots

    outPoints = [] #declare output array


    def subControlP(curveT, curPoint, curDegree):
        """
        recursive portion of the De Boore algorithm. Essentially we
        interpolate additional control points between the orginal
        according to the specified degree
        """
        # this is basis control point for interpolated points
        if curDegree is 0:
            return points[curPoint]

        aCoef = (curveT - knots[curPoint])/(knots[curPoint + 1 + degree - curDegree] - knots[curPoint])
        return (1-aCoef)*subControlP(curveT, curPoint-1, curDegree-1) + aCoef*subControlP(curveT, curPoint, curDegree-1)

    curveInterval = 1.0/smoothness
    x = float(degree) #start at first "real" point
    while x < numPoints:
        outPoints.append(subControlP(x,int(math.floor(x)),degree))
        x += curveInterval
    return outPoints

def munkFlipY(y):
    """pymunk and pygame use different orgins for the y axis,
    this translates from pygame to pymunk coordinates"""
    return -y + SCENE_HEIGHT

def main():

    ### Initialize pygame instance

    pygame.init()
    running = True #flag to signal end of scene

    ### setup pygame scene

    scene = pygame.display.set_mode((SCENE_WIDTH, SCENE_HEIGHT))
    clock = pygame.time.Clock()

    ### PyMunk Physics

    physSpace = pymunk.Space() # this is pymunk physics simulation container
    physSpace.gravity = 0.0, PYMUNK_GRAVITY

    ### Core scene loop


    ### Curved Line
    controlPoints = []

    while running:
        # handle pygame events
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False
            elif event.type == MOUSEBUTTONDOWN and event.button == 1: #left mouse click
                newPoint = vec(event.pos[X], munkFlipY(event.pos[Y])) #pymunk Vec2d
                controlPoints.append(newPoint)
        #create smoothed points if there are enough control points
        smoothPoints = None
        if len(controlPoints) >= 2:
            smoothPoints = bSplineCurve(controlPoints,B_DEGREE,B_SMOOTHNESS)

        ### physics upkeep
        physSpace.step(DT)

        ### draw upkeep

        # Draw background
        scene.fill(THECOLORS["blue"])

        # draw control points:
        for i in range(len(controlPoints)):
            pos = (controlPoints[i].x, munkFlipY(controlPoints[i].y))
            pygame.draw.circle(scene,THECOLORS["red"],pos,3)

        # draw smoothed curve
        if smoothPoints:
            drawPoints = []
            for i in range(len(smoothPoints)):
                drawPoints.append((smoothPoints[i].x,munkFlipY(smoothPoints[i].y)))
            pygame.draw.lines(scene, THECOLORS["white"],False, drawPoints)


        # scene update
        pygame.display.flip()
        clock.tick(DT_MS)

    print("End of Scene")

if __name__ == '__main__':
    main()