# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import random
from random import randint
from defines import *

from twisted.internet import reactor

class Weather:
    def __init__(self,zone):
        
        self.zone = zone
        self.climate = zone.climate
        self.cloudCover = randint(0,10)
        self.precip = 0
        if self.cloudCover > 5:
            if not randint(0,10):
                self.precip = randint(0,self.cloudCover)
                
        
        self.lightning = 0#randint(0,10)
        self.windspeed = randint(1,10) #never have windspeed of 0
        self.winddir = randint(0,360)
        
        self.lastCoverChange = 0
        self.lastPrecipChange = 0
        self.lastWindChange = 0
        self.lastWindDirChange = 0
        self.lastLightningChange = 0
        
        self.dirty = True
        
        self.tick()
        
        
    def tick(self):
        #ticks at 2x a minute
        
        
        #first do cloud cover
        if not random.randint(0,2):
            #change
            
            #spontaneous
            if not random.randint(0,20):
                self.cloudCover = 1
            if not random.randint(0,40):
                self.cloudCover = 8
                
            
            
            amt = 0
            if self.lastCoverChange!=0:
                if random.randint(0,2): #most likely head in same direction
                    amt=self.lastCoverChange
                else:
                    amt=-self.lastCoverChange
                    
            if not amt:
                amt=random.randint(-1,1)
                
                
            if amt:
                self.lastCoverChange = amt
                self.dirty = True
                self.cloudCover+=amt
                if self.cloudCover < 0:
                    self.cloudCover = 0
                    
                if self.cloudCover > 10:
                    self.cloudCover = 10
                    
        
        if not random.randint(0,3):
            #change
            amt = 0
            
            if self.lastPrecipChange!=0:
                if random.randint(0,5): #most likely head in same direction
                    amt=self.lastPrecipChange
                else:
                    amt=-self.lastPrecipChange
                    
            if not amt:
                amt=random.randint(-1,1) 
                
            if not self.precip and amt:
                if random.randint(0,3):
                    amt = 0 #stay not raining
            
            if amt:
                self.lastPrecipChange = amt
                self.dirty = True
                self.precip+=amt
                if self.precip < 0:
                    self.precip = 0
                    
                if self.precip > 10:
                    self.precip = 10
                    
        if not random.randint(0,2):
            #change
            amt = 0
            
            if self.lastWindChange!=0:
                if random.randint(0,4): #most likely head in same direction
                    amt=self.lastWindChange
                else:
                    amt=-self.lastWindChange
                    
            if not amt:
                amt=random.randint(-1,1)
                
                
            if amt:
                self.lastWindChange = amt
                self.dirty = True
                self.windspeed+=amt
                #windspeed of 0 causes problems with cloud rendering
                if self.windspeed < 1:
                    self.windspeed = 1
                    
                if self.windspeed > 10:
                    self.windspeed = 10

        if not random.randint(0,2):
            #change
            amt = 0
            
            if self.lastWindDirChange!=0:
                if random.randint(0,4): #most likely head in same direction
                    amt=self.lastWindDirChange
                else:
                    amt=-self.lastWindDirChange
                    
            if not amt:
                amt=random.randint(-1,1)
                
                
            if amt:
                self.lastWindDirChange = amt
                self.dirty = True
                self.winddir+=amt
                if self.winddir < 0:
                    self.winddir = 359 + self.winddir
                    
                if self.winddir > 359:
                    self.winddir = self.winddir-359

        if self.cloudCover < 1:
            self.dirty = True
            self.cloudCover = 1
        
        if self.cloudCover <= 3 and self.precip:
            self.dirty = True
            self.precip = 0  
            self.lastPrecipChange = -1          
        if self.precip > self.cloudCover:
            self.dirty = True
            self.precip = self.cloudCover
            
        #a couple zone specific hacks
        if self.zone.name == "trinstsewer":
            self.precip = 0
                
        #self.windspeed = 0
        #self.cloudCover = 4
        #self.precip = 0
        #self.dirty = True
        
        self.mytick = reactor.callLater(10,self.tick)
        
    def cancel(self):
        try:
            self.mytick.cancel()
        except:
            pass
        
    
            
            
            
                
                
                
                
                
                
            
            
            
            
        
        
        
        
        