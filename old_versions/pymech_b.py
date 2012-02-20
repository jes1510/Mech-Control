
#!/usr/bin/env python

"""
trendnet.py: A python/pygame interface to the Trendnet TV-IP110W.

  Copyright (c) 2009-2010 Michael E. Ferguson.  All right reserved.
  Copyright (c) 2010 Jesse Merritt. All rights reserved.

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software Foundation,
  Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

http://www.blunderingbotics.com/

usage: trendnet.py <ip_of_cam>


Serial protocol:
BYTE0 = 255 
BYTE1 = F B L R G1 G2 FREE FREE
BYTE2 = PAN
BYTE3 = TILT
BYTE4 = FREE
BYTE5 = FREE
BYTE6 = FREE
BYTE8 = CHECKSUM = (~(B0+B1+B2+B3+B4+B5+B6+B7+B8))+1

"""


import sys, time, pygame, httplib
from pygame.locals import *
import base64
import StringIO
from threading import Thread 
import os
from pgu import gui
import serial



#ser = serial.Serial('/dev/ttyUSB0', 38400)
    
exit = 0                # Variable that allows exiting from outside of main thread

ip = sys.argv[1]        # IP of cam

lastMouseTime = 0       #  Init a tracker for polling the mouse
fireMode = 3            # Default firing mode

mouseFramerate = 1/60   # 1/n = Hz
cursor_visible = 0      # Display cursor.  

#  Crosshair options
crossX = 512            #  X location
crossY = 384            #  Y location
crossSize = 10          #  Size in pixels
crossMode = 1           #  default crosshair mode
crossOffset = 100       #  How far between each crosshair in pixels

H = 768                 #  Screen size X
W = 1024                #  Screen size Y

# defines for serial protocol
controlByte = 0
header = 255
forward = 0
backward = 0
left = 0
right = 0
gun1 = 0
gun2 = 0
controlBit1 = 0
controlBit0 = 0
pan = 0
tilt = 0
byte4 = 0
byte5 = 0
byte6 = 0
checksum = 0




#  Reads the trendnet camera and updates the background of the window 
class Trendnet(Thread):
    def __init__(self, surface, ip):

        Thread.__init__(self)
        self.setDaemon(True)
        """ Configures the class with the IP of the camera, and the surface to paint to. """
        username = "admin"
        password = "admin"
        # default log in information
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
       
        self.surface = surface
        self.ip = ip
        self.size = (1024,768)
        self.offset = (16,16)
       
        h=httplib.HTTP(ip)
        h.putrequest('GET','/cgi/mjpg/mjpeg.cgi')
        h.putheader('Authorization', 'Basic %s' % base64string)
        h.endheaders()
        errcode,errmsg,headers=h.getreply()
        #print errcode, errmsg, headers
        self.file=h.getfile()
        self.filecount = 0
        #<if errcode is 200 go on the the next part>
        global overlaySync


    def run(self) :
        while True :          
           
            self.update()
            
        
 
    def update(self):
        """ This will paint an image to the surface already given in init. """
        data=self.file.readline()
        if data[0:15]=='Content-Length:':
            count=int(data[16:])
            s = self.file.read(count)
            # there is some funky stuff going on... lets make this a real jpeg    
            while s[0] != chr(0xff):
                s = s[1:]
            p=StringIO.StringIO(s)            
            try:
                background = pygame.image.load(p).convert()            
                background = pygame.transform.scale(background, self.size)#, DestSurface = tempSurface)
                self.surface.blit(background, self.offset)
                self.filecount = self.filecount + 1
            except:
                print "file error" 
                         
            p.close()

#  Creates an overlay with text.  Also has aiming recticles
class Overlay(Thread):
    def __init__(self, surface):
        Thread.__init__(self)
        self.setDaemon(True)
        self.surface = surface   
        self.lastMode = 0   
        self.lastState = []         
        global crossMode   
        global fireMode   
        global lastMouseTime
  
    def run(self) :
      #  self.drawCrosshairs(crossSize, 412, 384)  # 512, 384 is exact center
      #  self.drawCrosshairs(crossSize, 612, 384) 
     #   self.circleCrosshairs(412,384)
     #   self.circleCrosshairs(612,384)
        while True :
            self.states = [crossMode, fireMode]            
            if set(self.states) != set(self.lastState) :                  
                self.drawBoxes()
                self.drawText()
                self.drawCrosshairs()
                self.lastState = self.states
                

    def drawCrosshairs(self) :        
        if crossMode == 1:            
            self.crosshairs(crossSize, (W/2)-crossOffset, H/2)            
            self.crosshairs(crossSize, (W/2)+crossOffset, H/2)
        if crossMode == 2 :
           
            self.circleCrosshairs((W/2)-crossOffset, H/2)
            self.circleCrosshairs((W/2)+crossOffset, H/2)

    def crosshairs(self, size, x, y):
        if fireMode == 1 or fireMode == 3 :
            pygame.draw.line(self.surface, (255, 255, 255), (x, y-size/2), (x, y+size/2))
        if fireMode == 2 or fireMode == 3 :
            pygame.draw.line(self.surface, (255, 255, 255), (x-size/2, y), (x+size/2, y))

    def circleCrosshairs(self, x, y):
        if fireMode == 1 or fireMode == 3 :
            pygame.draw.circle(screen, (255,255,255), (x,y), 30, 2 )
        if fireMode == 2 or fireMode == 3 :
            pygame.draw.circle(screen, (255,255,255), (x,y), 2)

    def drawBoxes(self):
        pygame.draw.rect(screen, (139, 26, 26), (0, 0, 1024, 50)) # color followed by x,y,width,height        

    def drawText(self):
        font = pygame.font.Font(None, 25)        
        fmtext = font.render('Fire Mode: ', True, (255,255, 255), (139, 26, 26))        
        if fireMode == 1 :
            fireText = font.render('LEFT', True, (255,255, 255), (139, 26, 26))
        if fireMode == 2 :
            fireText = font.render('RIGHT', True, (255,255, 255), (139, 26, 26))
        if fireMode == 3 :
            fireText = font.render('BOTH', True, (255,255, 255), (139, 26, 26))
        self.surface.blit(fireText, (100,0))
        self.surface.blit(fmtext, (0,0))           

#   Reads the pygame event engine and does stuff with keyboard and mouse events 
class eventHandler(Thread) :    
    def __init__(self, screen):
        Thread.__init__(self)
        self.setDaemon(True)    
        global exit  
        global crossMode   
        global forward
        global backward
        global left
        global right
        global gun1
        global gun2
        global pan
        global tilt
        global fireMode
        global lastMouseTime           
        global controlByte   
        


        
    def run(self):  
        
    
        while True:                       
            for event in pygame.event.get():                
                if event.type == QUIT:  
                    self.exit = 1
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3: # right mouse button
                        print "Cycle Guns"
                        fireMode = fireMode + 1
                        if fireMode > 3:
                            fireMode = 1

                    if event.button == 1: # right mouse button
                        print "Fire!"
                        if fireMode == 1 :
                            print "Left only"
                            gun1 = 8
                            gun0 = 0
                        if fireMode == 2 :
                            print "right only"
                            gun1 = 0
                            gun2 = 4

                        if fireMode == 3 :
                            print "Both"
                            gun1 = 8
                            gun2 = 4
                        
                    
                if event.type == KEYDOWN:
            
                    if event.key == K_ESCAPE:                        
                        exit = 1

                    if event.key ==  K_PERIOD:
                       # crossMode = crossMode + 1
                       # print crossMode
                       # if crossMode == 2 :
                       #     crossMode = 0

                       # Overlay(screen).drawCrosshairs()
                        Overlay(screen).drawCrosshairs()

                    if event.key ==  K_w:
                        print "Forward"
                        forward = 128
                        backward = 0

                    if event.key ==  K_s:
                        print "Backward"
                        forward = 0
                        backward = 64

                    if event.key ==  K_a:
                        print "Left"
                        left = 32
                        right = 0
                        
                    if event.key ==  K_d:
                        print "right"
                        left = 0
                        right = 16

                    if event.key ==  K_c:
                        print "Center_Turret"
        
                 #   Com().send()
            if event.type == KEYUP:
                controlByte = controlByte & 15
                

            if event.type == pygame.MOUSEBUTTONUP:
                controlByte = controlByte & 240
                print "UP"   
            
            

            #  Only do this every so often
            if time.time() - lastMouseTime > mouseFramerate :
                pos= pygame.mouse.get_pos()
                w,h = pos
                moved = pygame.mouse.get_rel()
                moved_x, moved_y = moved    
            
                if moved_x != 0 or moved_y !=0 :
                    print "M_x: " + str(moved_x)
                    print "M_y: " + str(moved_y)
                   # ser.write(str(Com.buildPacket))               
                    
                lastMouseTime = time.time()
            controlByte = forward | backward | left | right | gun1 | gun2 | controlBit1 | controlBit0
            Com().send()
                

class Com (Thread) :
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)    

    def send(self) :
      #  ser.write(str(chr(255)))
        #ser.write(str(ord(self.buildPacket)))
        print "Byte: " + bin(self.buildPacket())
        
   
        
    def buildPacket(self) :
        global controlByte
        
        print controlByte
        return controlByte

        
       
if __name__ == "__main__":    
    clock = pygame.time.Clock()
    if len(sys.argv) < 2:
        print __doc__
    else:
        pygame.init()
        font = pygame.font.Font(None, 17)
        pygame.mouse.set_visible(cursor_visible)
        pygame.event.set_grab(True)
        screen = pygame.display.set_mode((W,H), 32)
        t = Trendnet(screen,ip)
        t.start()
        o = Overlay(screen)
        o.start()   
        e=eventHandler(screen)
        e.start()                

        while True:    
             
            if exit :         #  This is the only way to grab the exit signal from the handler       
                sys.exit(0)

            pygame.display.update()
           # time.sleep(.01)
            clock.tick(60)
 



