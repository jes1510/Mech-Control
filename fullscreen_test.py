import pygame
from pygame.locals import *

def Game():
    pygame.init()
    clock = pygame.time.Clock()
    pygame.display.set_caption('Pygame Loop')
    screen = pygame.display.set_mode(((640,480)) ,FULLSCREEN)
    exit = False
    red = 0
    increment = 1
    while not exit:
        for event in pygame.event.get():
            if event.type == QUIT:
                exit = True
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    exit = True
        screen.fill((red,0,0))
        pygame.display.update()
        red += increment
        if (red >= 255 and increment > 0):
            increment = -1
        elif (red <= 0 and increment < 0):
            increment = 1
        clock.tick(100)
    pygame.quit()

# Start the game loop.
Game()

