# GUI and Physics depiction of a car(ball) in a mountain valley
# Author: Matthew Atteberry

import pygame
from pygame.locals import * # grant easy access to pygame constants
import pymunk

SCENE_WIDTH = 600
SCENE_HEIGHT = 600
PYMUNK_GRAVITY = -981.0
DT = 1.0/60.0 # define physics time step
DT_MS = DT * 1000 # time step in milliseconds

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

    while running:
        # handle pygame events
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                running = False

        # physics upkeep
        physSpace.step(DT)

        # scene update
        clock.tick(DT_MS)

    print("End of Scene")

if __name__ == '__main__':
    main()