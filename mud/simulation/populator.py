# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
import random
from mud.simulation.shared.simdata import SpawnpointInfo
import math

class Populator:
    def __init__(self,spawnpoints,paths):
        self.spawnpoints = spawnpoints
        self.paths = paths
        
        self.maxWanderGroup = 0
        
        self.calcBounds()
        
        #bins are 192x192 areas of the map
        self.bins = {}
        self.binPaths = {}
        self.spawnpoints = []
        self.paths = {}
        self.waypoints = {}
        
        
        for y in xrange(self.boundsMin[1],self.boundsMax[1],48):
            for x in xrange(self.boundsMin[0],self.boundsMax[0],48):
                z = float(TGECall('MyCheckGridPoint',"%f %f %f"%(x,y,self.midZ)))
                if z:
                    bx = x/192
                    by = y/192
                    if not self.bins.has_key((bx,by)):
                        self.bins[(bx,by)]=[]
                    self.bins[(bx,by)].append((x,y,z))
        
        
        numpoints = 0
        #bin paths
        for bin,points in self.bins.items():
            num = len(points)
            if num < 4:
                del self.bins[bin]
                continue
            numpoints += num
            
            x = 0            
            for p1 in points:
                y = 0
                for p2 in points:                    
                    if x == y:
                        y+=1
                        continue
                    #if math.fabs(p1[2]-p2[2]<8) #XXX: We actually do need to do this so that mobs are'nt trying to walk up too steep of incluses
                    #but it messes with stuff below, and there might be a bug with waypoints/paths without it
                    result = TGECall('MyCastRay',"%f %f %f"%(p1[0],p1[1],p1[2]+4),"%f %f %f"%(p2[0],p2[1],p2[2]+4))
                    
                    if int(result):
                        if not self.binPaths.has_key(bin):
                            self.binPaths[bin]={}
                            
                        if not self.binPaths[bin].has_key(x):
                            self.binPaths[bin][x]=[]
                        self.binPaths[bin][x].append(y)
                        
                    y+=1
                x+=1
        
        
        wgroup = self.maxWanderGroup+1
        num = 0
        for bin,points in self.bins.iteritems():
            wander = False
            
            if self.binPaths.has_key(bin):
                if len(self.binPaths[bin])>=4:
                    wander = True
                    self.paths[wgroup]=self.binPaths[bin]
                    self.waypoints[wgroup]=[]
                    for p in points:
                        self.waypoints[wgroup].append((p[0],p[1],p[2],1, 0, 0, 0))
                
                for p in points:
                    if not random.randint(0,3): #1 in 4 chance of spawn point
                        spoint = SpawnpointInfo()
                        rot = TGECall("MyRandomRotation")                        
                        rot = rot.split(" ")                        
                        spoint.transform = (p[0],p[1],p[2],float(rot[0]),float(rot[1]),float(rot[2]),float(rot[3]))
                        
                        
                        spoint.group = "POPULATOR_%i"%num
                        if wander and not random.randint(0,2): #1 in 3 wander this might be too high even, very expensive
                            spoint.wanderGroup = wgroup                        
                        else:
                            spoint.wanderGroup = -1
                            
                        self.spawnpoints.append(spoint)
                                
                #bump the wander group
                if wander:
                    wgroup+=1
                num+=1
                
        #print self.binPaths
        print "%i bins with a total of %i points"%(len(self.bins),numpoints)
        print "%i spawnpoints added"%len(self.spawnpoints)
                
            
        
        
    def calcBounds(self):
        minx=miny=minz = 1000000
        maxx=maxy=maxz = -1000000
        for sp in self.spawnpoints:
            if sp.wanderGroup > self.maxWanderGroup:
                self.maxWanderGroup = sp.wanderGroup
            t = sp.transform
            if t[0] < minx:
                minx = t[0]
            if t[1] < miny:
                miny = t[1]
            if t[2] < minz:
                minz = t[2]
            if t[0] > maxx:
                maxx = t[0]
            if t[1] > maxy:
                maxy = t[1]
            if t[2] > maxz:
                maxz = t[2]
                
        self.boundsMin = (int(minx),int(miny),int(minz))
        self.boundsMax = (int(maxx),int(maxy),int(maxz))
        
        self.midZ = minz+(maxz-minz)/2
        
            
            
        
        
        

def Populate(spawnpoints,paths):
    p = Populator(spawnpoints,paths)
    return p.spawnpoints,p.paths,p.waypoints
    
