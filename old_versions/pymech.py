
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
"""

import sys, time, pygame, httplib
from pygame.locals import *
import base64
import StringIO

ip = sys.argv[1]

cursor_visible = 1
crossX = 512
crossY = 384
crossSize = 10

class trendnet:
    def __init__(self, surface, ip):
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


class Overlay:
    def __init__(self, surface):
        self.surface = surface     

    def drawCrosshairs(self, size, x, y):
        pygame.draw.line(self.surface, (255, 255, 255), (x, y-size/2), (x, y+size/2))
        pygame.draw.line(self.surface, (255, 255, 255), (x-size/2, y), (x+size/2, y))

    def drawTopBox(self):
        pygame.draw.rect(screen, (139, 26, 26), (0, 0, 1024, 50)) # color followed by x,y,width,height
     
       
if __name__ == "__main__":
    # a simple little test of our system
    if len(sys.argv) < 2:
        print __doc__
    else:
        pygame.init()
        font = pygame.font.Font(None, 17)
        pygame.mouse.set_visible(cursor_visible)
        screen = pygame.display.set_mode((1024,768),32)
        t = trendnet(screen,ip)
        o = Overlay(screen)        

        o.drawCrosshairs(crossSize, 412, 384)  # 512, 384 is exact center
        o.drawCrosshairs(crossSize, 612, 384)  
        o.drawTopBox()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:  
                    sys.exit(0)

                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        sys.exit(0)
        
            print pygame.mouse.get_rel()
            t.update()
            pygame.display.update()
            time.sleep(.01)
 



