#!/usr/bin/python
import pygame as pg
import math
import time
import socket   #for sockets
import sys      #for exit

class ProgressBar:
    def __init__(self, rect, **kwargs):
        
        self.rect = pg.Rect(rect)
        self.maxwidth = self.rect.width
        self.timer = 0.0
        self.process_kwargs(kwargs)
        self.complete = False
        self.tinit = time.clock()
        if self.text:
            self.text = self.font.render(self.text,True,self.font_color)
    
    def process_kwargs(self,kwargs):
        settings = {
            'color'       : (0,0,0),
            'bg_color'    : (255,255,255),
            'border_color': (0,255,0),
            'border_buff' : 1,
            'increment'   : 10,
            'time'        : 1.0,
            'percent'     : 50,
            'repetitive'  : False,
            
            'text'        : None,
            'font'        : pg.font.Font(None,20),
            'font_color'  : (0,0,0),
            'text_always' : False
        }
        for kwarg in kwargs:
            if kwarg in settings:
                settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("{} has no keyword: {}".format(self.__class__.__name__, kwarg))
        self.__dict__.update(settings)
        
    def progress(self):
        #tnow = time.clock()-self.tinit
        #self.percent = 50.0+10.0*math.cos(2*math.pi*tnow/2)
        pass

    def update(self):
        self.current_time = pg.time.get_ticks()
        if self.current_time-self.timer > 1000/self.time: #auto progress
            self.progress() 
            self.timer = self.current_time
        
    def render(self, screen):
        height =  self.percent*self.rect.height/100
        if height >= self.rect.height:
            height = self.rect.height
            self.complete = True
        else:
            self.complete = False
        pg.draw.rect(screen, self.border_color, 
            (self.rect.left-self.border_buff, self.rect.top-self.border_buff, 
            self.rect.width+self.border_buff*2, self.rect.height+self.border_buff*2))
        pg.draw.rect(screen, self.bg_color, 
            (self.rect.left, self.rect.top, self.rect.width, self.rect.height))
        pg.draw.rect(screen, self.color, 
            (self.rect.left, self.rect.top, self.rect.width, self.rect.height-height))
        if self.text:
            if self.complete or self.text_always:
                text_rect = self.text.get_rect(center=self.rect.center)
                screen.blit(self.text, text_rect)

class Control:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((800,600))
        self.fullscreen = False
        self.done = False
        self.clock = pg.time.Clock()
        
        config = {
            'text'       : 'POWER',
            'color'      : (255,0,0),
            'bg_color'   : (0,255,0),
            'increment'  : .1, 
            'time'       : 100, 
            'text_always': True,
        }
        self.bar = ProgressBar((self.screen.get_width()/3,50,self.screen.get_width()/3,self.screen.get_height()-100), **config)
        self.bar.percent = 0    # Jin added for definition of variable in bar class
        self.bars = [self.bar]
        
        # Jin UDP Server
        host = '';      #recieve from all interfaces
        port = 10000  #int(raw_input("Enter Listening Port:"))
        
        # Create a UDP socket and bind to it
        try:
            print 'Init UDP Server: Port: %s...' % port
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.bind((host,port))
            self.sock.setblocking(0)
            print 'Server init complete'
        except socket.error, msg:
            print 'Server init failed. Error Code: ' + str(msg[0]) + ' Message ' +msg[1]
            sys.exit()
        
        
    def events(self):
        # Jin UDP server
        try:
            # if sock has data, get data from client
            alpha = float(self.sock.recv(1024))
            alpha = max(0, min(alpha,1))    # clamp alpha
            self.bar.percent = alpha * 100
        except socket.error, msg:
            if (str(msg[0]) != "10035"):    # non-blocking, no data received, do not print err if 10035            
                print '\nError Code: ' + str(msg[0]) + ' Message: ' + msg[1]
        except ValueError:
            pass
        
        # ProgressBar event
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEBUTTONDOWN:
                pass
            elif event.type == pg.KEYDOWN:                
                if event.key == pg.K_f:
                    self.fullscreen = not self.fullscreen
                    
                    if self.fullscreen:
                        screen = pg.display.set_mode((800,600))
                    else:
                        screen = pg.display.set_mode((800,600),pg.FULLSCREEN,16)
                if  event.key == pg.K_ESCAPE:
                    self.done = True
                
    def update(self):
        for bar in self.bars:
            bar.update()
        
    def render(self):
        for bar in self.bars:
            bar.render(self.screen)
        
    def run(self):
        while not self.done:
            self.events()
            self.update()
            self.render()
            pg.display.update()
            self.clock.tick(60)
        
        print >>sys.stderr, '\nClosing socket'	
        self.sock.close()
        sys.exit()
 
# root program 
app = Control()
app.run()