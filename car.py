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
CONTROL_RADIUS = 3
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

class gameManger:

    def __init__(self):
        ''' Initialize pygame instance'''
        pygame.init()
        self.running = True  # flag to signal end of scene
        ### setup pygame scene

        self.scene = pygame.display.set_mode((SCENE_WIDTH, SCENE_HEIGHT))
        self.clock = pygame.time.Clock()

        ### PyMunk Physics

        self.physSpace = pymunk.Space() # this is pymunk physics simulation container
        self.physSpace.gravity = 0.0, PYMUNK_GRAVITY

        ### Curved Line
        self.cPoints = controlPoints()

        self.coreLoop()

    def coreLoop(self):

        while self.running:
            # handle pygame events
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # left mouse click
                    self.cPoints.add(controlPoint(event.pos[X], event.pos[Y]))
            # create smoothed points if there are enough control points
            smoothPoints = None
            if len(self.cPoints.sprites()) >= 2:
                smoothPoints = bSplineCurve(self.cPoints.getListOfPoints(), B_DEGREE, B_SMOOTHNESS)

            ### physics upkeep
            self.physSpace.step(DT)

            ### draw upkeep

            # Draw background
            self.scene.fill(THECOLORS["blue"])

            # draw control points:
            self.cPoints.draw(self.scene)

            # draw smoothed curve
            if smoothPoints:
                drawPoints = []
                for i in range(len(smoothPoints)):
                    drawPoints.append((smoothPoints[i].x, smoothPoints[i].y))
                pygame.draw.lines(self.scene, THECOLORS["white"], False, drawPoints)

            # scene update
            pygame.display.flip()
            self.clock.tick(DT_MS)

class controlPoints(pygame.sprite.Group):

    def __init__(self,listOfSprite = None):
        #call parent class constructor
        if listOfSprite:
            pygame.sprite.Group.__init__(self,listOfSprite)
        else:
            pygame.sprite.Group.__init__(self)

    def getListOfPoints(self):

        #create a list from all control points
        return [point for point in self.sprites().pos]

class controlPoint(pygame.sprite.Sprite):

    SELECTED, MOUSED_OVER, NEUTRAL = 0,1,2
    isStatic = False
    imageSet = []
    pos = (0,0)

    def __init__(self,xPos,yPos, static = False):
        #call parent class constructor
        pygame.sprite.Sprite.__init__(self)

        self.update(xPos,yPos)
        self.isStatic = static #static controlPoints can't be moved

        self.imageSet = self.drawImages()
        self.image = self.imageSet[self.NEUTRAL]
        self.rect = self.imageSet[0].get_rect()

        self.isMousedOver = True #mouse is over point on creation

    def drawImages(self):

        imgArray = [pygame.Surface([CONTROL_RADIUS*2,CONTROL_RADIUS*2]) for i in range(3)]
        pygame.draw.circle(imgArray[self.SELECTED], THECOLORS["green"], self.pos, CONTROL_RADIUS + 1)
        pygame.draw.circle(imgArray[self.MOUSED_OVER], THECOLORS["yellow"], self.pos, CONTROL_RADIUS+1)
        pygame.draw.circle(imgArray[self.NEUTRAL], THECOLORS["orange"], self.pos, CONTROL_RADIUS+1)

        for i in range(len(imgArray)):
            pygame.draw.circle(imgArray[i], THECOLORS["red"], self.pos, CONTROL_RADIUS)

        return imgArray

    def update(self, xPos, yPos, mousedOver = False, selected = False):

        # static constrol points may not be updated
        if self.isStatic or not self.imageSet:
            return

        if selected:
            self.pos = (xPos,yPos) #used for graphics
            self.physicsPos = (self.pos[X], munkFlipY(self.pos[Y]))
            self.image = self.imageSet[self.SELECTED]
        elif mousedOver:
            self.imageSet = self.imageSet[self.MOUSED_OVER]
        else:
            self.imageSet = self.imageSet[self.NEUTRAL]

        self.isSelected = selected
        self.isMousedOver = mousedOver

        return

def main():

    #greate mountain car game instance
    GM = gameManger()
    print("End of Scene")

if __name__ == '__main__':
    main()