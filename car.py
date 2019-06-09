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
B_DEGREE = 4
B_SMOOTHNESS = 5
CONTROL_RADIUS = 8
DT = 1.0/180.0 # define physics time step
DT_MS = 100 # time step in milliseconds

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

    isMouseDown = False
    mountainCar = None

    def __init__(self):
        ''' Initialize pygame instance'''
        pygame.init()
        self.clock = pygame.time.Clock()
        self.running = True  # flag to signal end of scene
        ### setup pygame scene

        self.scene = pygame.display.set_mode((SCENE_WIDTH, SCENE_HEIGHT))

        ### PyMunk Physics

        self.physSpace = pymunk.Space() # this is pymunk physics simulation container
        self.physSpace.gravity = 0.0, PYMUNK_GRAVITY

        ### Curved Line
        self.cPoints = controlPoints(self)

        self.mousePos = (0,0)
        self.coreLoop()

    def coreLoop(self):

        while self.running:
            # handle pygame events
            for event in pygame.event.get():
                if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                    self.running = False
                elif event.type == MOUSEBUTTONDOWN and event.button == 1:  # left mouse click
                    self.mousePos = (event.pos[X], event.pos[Y])
                    self.cPoints.addItem(controlPoint(self))
                elif event.type == MOUSEBUTTONDOWN and event.button == 2: # place a 'car', 2 is middle mouse button:
                    self.mousePos = (event.pos[X], event.pos[Y])
                    self.mountainCar = mountainCar(self)
                elif event.type == MOUSEBUTTONDOWN and event.button == 3: #left mouse unclick:
                    self.isMouseDown = True
                elif event.type == MOUSEBUTTONUP and event.button == 3: #left mouse unclick:
                    self.isMouseDown = False
                elif event.type == MOUSEMOTION:
                    self.mousePos = (event.pos[X],event.pos[Y])

            ### physics upkeep
            self.physSpace.step(DT)

            ### draw upkeep

            # Draw background
            self.scene.fill(THECOLORS["blue"])

            # draw control points:
            self.cPoints.update()
            self.cPoints.draw(self.scene)
            if self.mountainCar:
                self.mountainCar.update()


            # scene update
            pygame.display.flip()
            self.clock.tick(DT_MS)

class controlPoints(pygame.sprite.Group):


    # the smooth curve created with B-splines
    smoothPoints = None
    smoothShapes = []

    # flag to denote if any of the control points have been added/moved
    isChanged = True

    def __init__(self, parentGM, listOfSprite = None):

        #set parent game manager
        self.parentGM = parentGM

        #call parent class constructor
        if listOfSprite:
            pygame.sprite.Group.__init__(self, listOfSprite)
        else:
            pygame.sprite.Group.__init__(self)

    def getListOfPoints(self):

        #create a list from all control points
        return [point.pos for point in self.sprites()]

    def draw(self, parentScene = None):

        # draw smoothed curve
        if self.smoothPoints:
            pygame.draw.lines(self.parentGM.scene, THECOLORS["white"], False, self.smoothPoints,2)

        super(controlPoints, self).draw(self.parentGM.scene)

    def addItem(self, sprite):

        self.isChanged = True
        super(controlPoints, self).add(sprite)

    def update(self, *args):

        super(controlPoints, self).update(args)

        if self.isChanged and len(self.sprites()) >= 2:
            self.smoothPoints = bSplineCurve(self.getListOfPoints(), B_DEGREE, B_SMOOTHNESS)

            #clean up old line segmenets before drawing new ones
            if self.smoothShapes:
                self.parentGM.physSpace.remove(self.smoothShapes)
            self.smoothShapes = []
            for i in range(len(self.smoothPoints) - 1):
                newBody = pymunk.Body(body_type=pymunk.Body.STATIC)
                shape = pymunk.Segment(newBody, (self.smoothPoints[i].x,munkFlipY(self.smoothPoints[i].y)), (self.smoothPoints[i+1].x,munkFlipY(self.smoothPoints[i+1].y)), 1)
                shape.friction = 0.30
                self.smoothShapes.append(shape)
                self.parentGM.physSpace.add(shape)

            self.isChanged = False

class controlPoint(pygame.sprite.Sprite):

    SELECTED, MOUSED_OVER, NEUTRAL = 0, 1, 2
    isMousedOver = True
    isSelected = False


    def __init__(self, parentSurface, static = False):

        self.parent = parentSurface

        #call parent class constructor
        pygame.sprite.Sprite.__init__(self)
        self.isStatic = static #static controlPoints can't be moved
        self.isMousedOver = True  # mouse is over point on creation

        self.pos = vec(self.parent.mousePos[X],self.parent.mousePos[Y])  # used for graphics
        self.physicsPos = (self.pos[X], munkFlipY(self.pos[Y]))

        self.drawBuffers()

        self.update()

    def drawBuffers(self):

        self.buffers = [pygame.Surface([CONTROL_RADIUS*2,CONTROL_RADIUS*2])]*3

        self.buffers[self.SELECTED] = pygame.image.load('controlPointSelected.png').convert_alpha()

        self.buffers[self.MOUSED_OVER] = pygame.image.load('controlPointMousedOver.png').convert_alpha()

        self.buffers[self.NEUTRAL] = pygame.image.load('controlPointNeautral.png').convert_alpha()

        self.image = self.buffers[0]
        self.rect = self.image.get_rect()

    def update(self, *args):

        # static control points may not be updated
        if self.isStatic:
            return

        if self.parent.isMouseDown == False:
            self.isSelected = False

        # test to see if contains mouse
        if self.rect.collidepoint((self.parent.mousePos[X],self.parent.mousePos[Y])):
            self.isMousedOver = True
            if self.parent.isMouseDown == True:
                self.isSelected = True
        else:
            self.isMousedOver = False

        #clear controlpoint buffer

        if self.isSelected:
            self.pos = vec(self.parent.mousePos[X],self.parent.mousePos[Y]) #used for graphics
            self.physicsPos = (self.pos[X], munkFlipY(self.pos[Y]))
            self.image = self.buffers[self.SELECTED]
            #only ever added to controlPoints
            self.groups()[0].isChanged = True
        elif self.isMousedOver:
            self.image = self.buffers[self.MOUSED_OVER]
        else:
            self.image = self.buffers[self.NEUTRAL]

        self.rect.center = self.pos

class mountainCar(pygame.sprite.Sprite):

    NEUTRAL = 0
    wheelRadius = 4

    def __init__(self,parent, static = False):

        self.parentGM = parent

        print("new car")
        #call parent class constructor
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec(self.parentGM.mousePos[X],self.parentGM.mousePos[Y])  # used for graphics
        self.physicsPos = (self.pos[X], munkFlipY(self.pos[Y]))

        self.body = pymunk.Body(0, 800)
        self.body.position = self.physicsPos
        self.leftWheel = pymunk.Circle(self.body,self.wheelRadius,(10,-4))
        self.leftWheel.friction = 0.002
        self.leftWheel.mass = 10
        self.rightWheel = pymunk.Circle(self.body, self.wheelRadius, (-7, -4))
        self.rightWheel.friction = 0.002
        self.rightWheel.mass = 10
        self.parentGM.physSpace.add(self.body, self.leftWheel, self.rightWheel)

        self.drawBuffers()

    def drawBuffers(self):

        self.buffers = [pygame.Surface([CONTROL_RADIUS*2, CONTROL_RADIUS*2])]*3

        self.buffers[self.NEUTRAL] = pygame.image.load('car.png').convert_alpha()

        self.image = self.buffers[0]
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def update(self):

        p = self.body.position
        self.pos = int(p.x), int(munkFlipY(p.y))
        flipImg = self.image

        if self.body.velocity.x < 0:
            flipImg = pygame.transform.flip(flipImg,True,False)
        print("Angle: " + str(self.body.angle))
        rot_img = pygame.transform.rotate(flipImg,math.degrees(self.body.angle))
        self.rect.center = self.pos
        self.parentGM.scene.blit(rot_img, self.rect)


def main():

    #greate mountain car game instance
    GM = gameManger()
    print("End of Scene")

if __name__ == '__main__':
    main()