import pygame
import random
import sys

pygame.init()
screen = pygame.display.set_mode((256,256))
pygame.display.set_caption('Application')
screen.fill((159, 182, 205))

# Search for Verdana and create a Font object
verdana = pygame.font.match_font('Verdana')
verdanaFont = pygame.font.Font(verdana, 13)

# Search for a font that does not exist and create a Font object
doesNotExist = pygame.font.match_font('doesNotExist')
dNEFont = pygame.font.Font(doesNotExist, 13)

# Search for a font that does not exist, followed by Arial, and create a Font object
arial = pygame.font.match_font('doesNotExist,Arial')
arialFont = pygame.font.Font(arial, 13)
print arial, arialFont

# Get a list of fonts
fonts = pygame.font.get_fonts()

# Create some random fonts
# get_fonts() merely returns a list of names, so we'll have to match them
font1 = pygame.font.Font(pygame.font.match_font(random.choice(fonts)), 13)
font2 = pygame.font.Font(pygame.font.match_font(random.choice(fonts)), 13)
font3 = pygame.font.Font(pygame.font.match_font(random.choice(fonts)), 13)

# Render text in verdana, doesNotExist, arial and the randomfonts
text1 = verdanaFont.render(str(verdana), 1, (255, 255, 255),(159, 182, 205))
text2 = dNEFont.render(str(doesNotExist), 1, (255, 255, 255),(159, 182, 205))
text3 = arialFont.render(str(arial), 1, (255, 255, 255), (159,182, 205))
text4 = font1.render('Random', 1, (255, 255, 255), (159, 182,205))
text5 = font2.render('Random', 1, (255, 255, 255), (159, 182,205))
text6 = font3.render('Random', 1, (255, 255, 255), (159, 182,205))

# Make some rectangles
rect1 = text1.get_rect()
rect2 = text2.get_rect()
rect3 = text3.get_rect()
rect4 = text4.get_rect()
rect5 = text5.get_rect()
rect6 = text6.get_rect()

# Position the rectangles
rect1.y, rect1.centerx = 0, screen.get_rect().centerx
rect2.y, rect2.centerx = 20, screen.get_rect().centerx
rect3.y, rect3.centerx = 40, screen.get_rect().centerx
rect4.y, rect4.centerx = 60, screen.get_rect().centerx
rect5.y, rect5.centerx = 80, screen.get_rect().centerx
rect6.y, rect6.centerx = 100, screen.get_rect().centerx

# Blit everything
screen.blit(text1, rect1)
screen.blit(text2, rect2)
screen.blit(text3, rect3)
screen.blit(text4, rect4)
screen.blit(text5, rect5)
screen.blit(text6, rect6)

pygame.display.update()

while True:
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         sys.exit()
