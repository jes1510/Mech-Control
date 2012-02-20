
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
BYTE1 = 255
BYTE2 = LENGTH
BYTE3 = MODE
XXX   = DATA
BYTEX = CHECKSUM = (B0+B1+B2+B3+B4+XXX) & 255)

"""



import sys, time, pygame, httplib
from pygame.locals import *
import base64
import StringIO
from threading import Thread 
import os
import serial
import time

RGUNSPEED = 120
LGUNSPEED = 120

ser = serial.Serial('/dev/tty', 38400, timeout=.1)
MAXRETRIES = 16
retries = 0
    
exit = 0                # Variable that allows exiting from outside of main thread

ip = sys.argv[1]        # IP of cam

lastMouseTime = 0       #  Init a tracker for polling the mouse
fireMode = 3            # Default firing mode
firing = 0              # Set when the guns are firing

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
outBuff = []
inBuff = []



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
        print errcode, errmsg, headers
        self.file=h.getfile()
        self.filecount = 0
        #<if errcode is 200 go on the the next part>
        global overlaySync
       


    def run(self) :
        while True :   
            time.sleep(.033)   
           
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
        global firing
  
    def run(self) :
      #  self.drawCrosshairs(crossSize, 412, 384)  # 512, 384 is exact center
      #  self.drawCrosshairs(crossSize, 612, 384) 
     #   self.circleCrosshairs(412,384)
     #   self.circleCrosshairs(612,384)
        while True :
            self.states = [crossMode, fireMode, firing]    
                  
            if set(self.states) != set(self.lastState) :    
               # print "toggle"             
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
        bigFont = pygame.font.Font(None, 60)    
        fmtext = font.render('Fire Mode: ', True, (255,255, 255), (139, 26, 26))        
        if fireMode == 1 :
            fireModeText = font.render('LEFT', True, (255,255, 255), (139, 26, 26))
        if fireMode == 2 :
            fireModeText = font.render('RIGHT', True, (255,255, 255), (139, 26, 26))
        if fireMode == 3 :
            fireModeText = font.render('BOTH', True, (255,255, 255), (139, 26, 26))
        if firing :
            firingText = bigFont.render('FIRING', True, (255,255, 255), (139, 26, 26))
            
        if not firing :            
            firingText = bigFont.render('FIRING', True, (139, 26, 26), (139, 26, 26))
            
        self.surface.blit(firingText, (420, 0))
        self.surface.blit(fireModeText, (100,0))
        self.surface.blit(fmtext, (0,0))           

  #  def showError(self, txt):          
  #      bigFont = pygame.font.Font(None, 60)  
  #      errorText = bigFont.render(txt,  True, (139, 26, 26), (139, 26, 26))
  #      self.surface.blit(errorText, (0,0))        
        
#   Reads the pygame event engine and does stuff with keyboard and mouse events 
class eventHandler(Thread) :    
    def __init__(self, screen):
        Thread.__init__(self)
        self.setDaemon(True)    

        
    def run(self):  
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
        global firing

      #  o = Overlay('txt')
       # o.showError("Over Temp")
    
        while True:         
            event = pygame.event.wait()  #  Blocks until an event pops in the que                        font.render('BOTH', True, (255,255, 255), (139, 26, 26))
            if event.type == QUIT:  
                exit = 1
                
            if event.type == pygame.MOUSEBUTTONDOWN:
               if event.button == 3: # right mouse button
                   print "Cycle Guns"
                   fireMode = fireMode + 1
                   if fireMode > 3:
                       fireMode = 1

               if event.button == 1: # left mouse button
                   firing = 1
                   if fireMode == 1 :
                       print "Left only"
                       c.send('g', [0,RGUNSPEED])
                       gun1 = 8
                       gun0 = 0
                   if fireMode == 2 :
                       print "right only"
		       c.send('g', [LGUNSPEED,0])
                       gun1 = 0
                       gun2 = 4

                   if fireMode == 3 :
                       c.send('g', [LGUNSPEED,RGUNSPEED])
                       print "Both"
                       gun1 = 8
                       gun2 = 4                        
                    
            if event.type == KEYDOWN:  
                print "KEY: " + str(event.key)
                if event.key == K_ESCAPE:                        
                    exit = 1
                    print "Exiting"

                if event.key ==  K_PERIOD:
                       # crossMode = crossMode + 1
                       # print crossMode
                       # if crossMode == 2 :
                       #     crossMode = 0
 
                       # Overlay(screen).drawCrosshairs()
                     Overlay(screen).drawCrosshairs()

		

                if event.key ==  K_w:
                    print "Forward"                    
                    c.send('w', '')                    
                    backward = 0                    

                if event.key ==  K_s:
                    print "Backward"
                    c.send('s', '')
                    forward = 0
                    

                if event.key ==  K_a:
                    print "Left"  
                    c.send('a', '')                  
                    right = 0
                        
                if event.key ==  K_d:
                    print "right"
                    c.send('d', '')
                    left = 0
                    

                if event.key ==  K_c:
                    c.send('c', '')
                    print "Center_Turret"

		if event.key ==  K_q:
                    c.send('q', '')
                    print "Increment Turret"

		if event.key ==  K_z:
                    c.send('z', '')
                    print "dECREMENT Turret"


		if event.key ==  K_i:    
                    moved_y = -5           
                    highY = (moved_y >> 8) & 255
                    lowY = moved_y & 255
		    c.send('m', [highY, lowY, 0, 0])           
                    
                    print "Turret Up"

		if event.key ==  K_k:
                    moved_y = 5           
                    highY = (moved_y >> 8) & 255
                    lowY = moved_y & 255
		    c.send('m', [highY, lowY, 0, 0])  
                    print "Turret Down"

		if event.key ==  K_j:
                    c.send('c', '')
                    print "Turret Left"

		if event.key ==  K_l:
                    c.send('c', '')
                    print "turret rught"


                if event.key ==  K_t:
                    c.send('t', '')
                    print "Get Temperatures from servos"
                    t = c.recv()
                    if t :
                        for i in t :
                            print ord(i)


                if event.key ==  K_e:
                    c.send('e', '')
                    print "Get Servo Errors"
                    e = c.recv()
                    if e :
                        for i in e :
                            print ord(i)
        
            #   Com().send()
            if event.type == KEYUP:     
                c.send('l', '')   
                print "STOP"        

                forward = 0
                backward = 0
                left = 0
                right = 0
                
                

            if event.type == pygame.MOUSEBUTTONUP:
		c.send('g', [0,0])
                gun1 = 0
                gun2 = 0
                firing = 0
                #print "UP"   
         
            

            #  Only do this every so often
            if time.time() - lastMouseTime > mouseFramerate :
                pos= pygame.mouse.get_pos()
                w,h = pos
                moved = pygame.mouse.get_rel()
                moved_x, moved_y = moved    
                highX = (moved_x  >> 8) & 255
                lowX = moved_x & 255
                
                highY = (moved_y >> 8) & 255
                lowY = moved_y & 255
                if moved_x != 0 or moved_y !=0 :
                    #c.send('m', [highY, lowY, highX, lowX])
		    c.send('m', [0, 0, highX, lowX])
                  
                    print "M_x: " + str(moved_x)
                    print "M_y: " + str(moved_y)                                 
                  
                lastMouseTime = time.time()

           # controlByte = forward | backward | left | right | gun1 | gun2 | controlBit1 | controlBit0
           
                

class Com (Thread) :
    def __init__(self):
        Thread.__init__(self)
        self.setDaemon(True)  
        self.doneReading = 0      
	

        

    def send(self, mode, data) :
	global MAXRETRIES
        global retries
      #  print "Length: " + str(len(data))
	print
        print "Sending Data -> " + mode
        
	newData  = []
	dataOut = []

	checkSum = ((ord(mode) + sum(data)) & 255)

	#ser.flush()

	for i in range(len(data)) :		# Convert to serial char				
		newData.append(chr(data[i]))
		
        headerA = (chr(255))      
        headerB = (chr(255))    
	length = chr(len(data) + 1)
	
	dataOut = [headerA, headerB, length, mode]
	dataOut.extend(newData)		#  append would make it a 2d list

	dataOut.append(chr(checkSum))
	
	for i in dataOut :
		ser.write(i)
			
        incoming = ser.read()
	if not incoming :
		print "COM's LOST!!!!!"

	if incoming :
		print "Incoming: " + str(ord(incoming)) + "		checksum: " + str(checkSum)        

        	if incoming == chr(checkSum) :      
		    retries = 0    
	            print "YAY!!!!!!!"  
        	   

	#	if incoming != chr(checkSum) and self.retries < self.MAXRETRIES + 1 :                             
       # 	    print "Retrying"
       # 	    self.retries = self.retries + 1
       # 	    self.send(mode, data)

	if incoming != chr(checkSum) and retries < MAXRETRIES:		
		retries = retries + 1
		print "!!!!!!!!!!!!! Checkum fail !!!!!!!!!!!!!!!"
		print "Retry #: " + str(retries) 
		self.send(mode, data)
		retries = retries + 1

	
		
	print        
            
	if not incoming :
            print "Timeout"


        

    def recv(self) :   
          print "waiting"     
          datum = ser.read()
          if datum == chr(255) :
                print "ok"
                datum = ser.read()
                if datum == chr(255) :
                    length = ser.read()     
                    inBuff = ser.read(ord(length))
                    return inBuff
                    
                    
                    

        
       
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
        c = Com()             

        while True:    
             
            if exit :         #  This is the only way to grab the exit signal from the handler       
                sys.exit(0)
            if not e.isAlive() :        # Since we exit from the event handler we need to exit if that thread crashes
                sys.exit(0)

            pygame.display.update()
           # time.sleep(.01)
            clock.tick(60)
 



