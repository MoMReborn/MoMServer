# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import math,traceback

#WORLDSERVER SIDE
from mud.common.avatar import Avatar
from mud.world.player import Player
from mud.world.theworld import World
from mud.world.spawn import SpawnGroup
from mud.world.core import *


import mud.simulation.shared.simdata 
import mud.simulation.simobject

from mud.world.shared.worlddata import ZoneConnectionInfo

class SimAvatar(Avatar):
    def __init__(self,username,role,mind):
        Avatar.__init__(self,username,role,mind)
        self.mind = mind
        self.username = username
        if username == "ZoneServer":
            self.dedicated = True
            self.player = None #dedicated!
        else:
            self.player = Player.byPublicName(username)
            self.dedicated = False
            
        self.zone = None
        self.world = World.byName("TheWorld")
        
        self.playerLookup ={}
        self.simObjects = []
        self.simLookup = {}
        
    def addSimObject(self,so):
        self.simObjects.append(so)
        self.simLookup[so.id]=so
        
        
    def error(self,error):
        print error
    
    
    def setDisplayName(self,player):
        name = player.charName
        if player.curChar.lastName:
            name += " %s"%player.curChar.lastName
        role = player.role.name
        if role != "Player":
            name += " (%s)"%role
        guildName = player.guildName
        if guildName:
            name += "<%s>"%guildName
        self.mind.callRemote("setDisplayName",player.simObject.id,name)
    
    
    def sendWeather(self,weather):
        from mud.world.shared.worlddata import WeatherConditions
        wc = WeatherConditions()
        wc.cloudCover = float(weather.cloudCover)/10.0
        wc.precip = float(weather.precip)/10.0
        wc.lightning = 0
        wc.winddir = weather.winddir
        wc.windspeed = weather.windspeed/10.0
        wc.climate = weather.climate
        self.mind.callRemote("setWeather",wc)
        
    def setTarget(self,simObject,targetSimObject):
        self.mind.callRemote("setTarget",simObject.id,targetSimObject.id)
    
    def setFollowTarget(self,simObject,targetSimObject):
        if targetSimObject:
            self.mind.callRemote("setFollowTarget",simObject.id,targetSimObject.id)
        else:
            self.mind.callRemote("setFollowTarget",simObject.id,0)
            
    def clearTarget(self,simObject):
        self.mind.callRemote("clearTarget",simObject.id)
        
    def immobilize(self,simObject):
        self.mind.callRemote("immobilize",simObject.id)
        
    def deleteObject(self,simObject):
        self.mind.callRemote("deleteObject",simObject.id)
        if self.playerLookup.has_key(simObject.id):
            traceback.print_stack()
            print "AssertionError: simObject id still in playerLookup!"
            return
        self.simObjects.remove(simObject)
        del self.simLookup[simObject.id]
        
        
    def removePlayer(self,simObject):
        if not simObject:
            return
        del self.playerLookup[simObject]
        self.simObjects.remove(simObject)
        del self.simLookup[simObject.id]
        
        
        
        
        
        
        
        
        
    #XXX need to add zone in point information
    def perspective_onZoneTrigger(self,simObject,zoneLink):#,zoneIn):
        if simObject not in self.simObjects:
            traceback.print_stack()
            print "AssertionError: simObject is not in SimAvatars simObject list!"
            return
        if not self.playerLookup.has_key(simObject):
            traceback.print_stack()
            print "AssertionError: simObject is not in SimAvatars playerLookup list!"
            return


        from zone import Zone,ZoneLink

        zlink = ZoneLink.byName(zoneLink)
        
        player = self.playerLookup[simObject]
        if player.zone:
            z = Zone.byName(zlink.dstZoneName)
            czone = player.zone.zone
            
            if czone == z:
                #good
                #we just need to respawn player, whew
                player.zone.respawnPlayer(player,zlink.dstZoneTransform)
                return


        #we want to present the player with a choice of active zones 
        #and/or to launch their own zone instance (if they are allowed to)
        self.world.onZoneTrigger(self.playerLookup[simObject],zlink)
        
        
        
        
        
    #player is actually in the world now
    #SIMOBJECT ->
    def perspective_setPlayerSimObject(self,publicName,simObject):
        #XXX security, check that player is in Zone
        #this could be used maliciously 
        player = Player.byPublicName(publicName)
        player.simObject = simObject
        self.zone.playerEnterZone(player)
        self.addSimObject(simObject)
        
        self.playerLookup[simObject]=player
        
        
    #additional connection information
    def perspective_onClientEnterGame(self,publicName):
        
        player = Player.byPublicName(publicName)
        
        #get spawn infos for each party member
        spinfos = []
        for c in player.party.members:
            spinfos.append(c.spawn.getSpawnInfo())

        mobInfos = []
        for c in player.party.members:
            mobInfos.append(c.mob.mobInfo)
        
        transform = player.logTransform
        if player.darkness:
            transform = player.darknessLogTransform
        if player.monster:
            transform = player.monsterLogTransform

        r = player.avatar.masterPerspective.role.name
        if player.monster:
            r = "Monster"
        return (transform,spinfos,mobInfos,player.modelIndex,r)
        
        
    def logout(self):
        if self.zone:
            print "Zone Down!"
            #if any other players in zone, suspend and do a pass off
            self.world.closeZone(self.zone)
            
    def stop(self):
        try:
            self.mind.callRemote("stop")
        except:
            pass
        
    def setPlayerPasswords(self,passwords):
        return self.mind.callRemote("setPlayerPasswords",passwords)
                
                
    #SIMOBJECT ->
    def botSpawned(self,bot):
        self.addSimObject(bot)
        
        return bot
        
    def spawnBot(self,spawn,transform,wanderGroup,mobInfo):
        name = spawn.name
        sinfo = spawn.getSpawnInfo(mobInfo.mob.sex)
        sinfo.sex = mobInfo.mob.sex
        sinfo.name += mobInfo.mob.sex
        d = self.mind.callRemote("spawnBot",name,transform,wanderGroup,sinfo,mobInfo)
        d.addCallback(self.botSpawned)
        return d
        
        
    def gotBindpoints(self,bindpoints):
        #this will be moved, bindpoints will be in db
        
        self.zone.bindpoints = bindpoints
    
    
    def gotSpawnpoints(self,spawnpoints):
        #this will be moved, spawnpoints will be in db
        
        spawns = []
        spawnnames = []
        for sp in spawnpoints:
            for g in self.zone.zone.spawnGroups:
                if sp.group == g.groupName:
                    for si in g.spawninfos:
                        spawn = si.spawn
                        if spawn.name not in spawnnames:
                            spawnnames.append(spawn.name)
                            si = spawn.getSpawnInfo()
                            spawns.append(si)

        #TODO, make a pb.remotecopyable if there is more data than scale limit
        #eventually, we could add physics changes etc here    
        #must become before setSpawnInfos as we use this info in some datablocks
        self.mind.callRemote("setZoneInfo",self.zone.zone.scaleLimit)
        
        if len(spawns):
            self.mind.callRemote("setSpawnInfos",spawns)
        
        self.zone.createSpawnpoints(spawnpoints)
    
    
    def refreshBindpoints(self):
        self.mind.callRemote("getBindPoints").addCallbacks(self.gotBindpoints,self.error)
    
    
    #this has the side effect of refreshing DialogTriggers too 
    def refreshSpawnPoints(self):
        self.mind.callRemote("getSpawnPoints").addCallbacks(self.gotSpawnpoints,self.error)
        
                
    def perspective_startSimulation(self,simmind,zoneInstanceName,pid=None):
        #this is called when simserver has loaded mission
        #XXX SECURITY!!!
        zinst = self.world.startSimulation(zoneInstanceName,pid)
        self.zone = zinst
        zinst.simAvatar = self
        self.mind = simmind
        
        self.refreshBindpoints()
        self.refreshSpawnPoints()
        
        self.zone.start()
    
    
    #mouse selection
    def perspective_select(self,srcId,tgtId,charIndex,doubleClick,modifier_shift):
        try:  # can be deleted in the meantime
            self.zone.select(self.simLookup[srcId],self.simLookup[tgtId],charIndex,doubleClick,modifier_shift)
        except KeyError:
            pass
    
    
    #dedicated
    def perspective_spawnDedicatedZone(self,zoneName,simPort):
        #zoneName can be a specific zone or "any" which allows the world to pick the zone served
        
        
        zone = self.world.spawnDedicatedZone(self,zoneName,simPort)
        self.zone = zone
        
        zconnect = ZoneConnectionInfo()
        zconnect.ip = zone.ip
        zconnect.password = zone.password
        zconnect.port = zone.port
        zconnect.niceName = zone.zone.niceName
        zconnect.missionFile = zone.zone.missionFile
        zconnect.instanceName = zone.name
        
        from race import GetRaceGraphics
        zconnect.raceGraphics = GetRaceGraphics()
        
        return zconnect
    
    
    def respawnPlayer(self,player,transform=None):
        if not transform:
            if player.darkness:
                transform = player.darknessBindTransformInternal
            elif player.monster:
                transform = player.monsterBindTransformInternal
            else:
                transform = player.bindTransformInternal
        
        return self.mind.callRemote("respawnPlayer",player.simObject.id,transform)
    
    
    def perspective_projectileCollision(self,pid,hitId,hitPos):
        self.zone.projectileCollision(pid,self.simLookup[hitId],hitPos)
        
    def perspective_onImpact(self,simId,velocity,pos):
        try:
            so = self.simLookup[simId]
        except KeyError:  # not spawned yet?
            return
        so.position = (pos[0],pos[1],pos[2])
        self.zone.onImpact(so,velocity)

    
    def perspective_deleteProjectile(self,pid):
        
        self.zone.deleteProjectile(pid)
        
    def launchProjectile(self,p):
        self.mind.callRemote("launchProjectile",p.id,p.src.simObject.id,p.dst.simObject.id,p.projectile,p.speed)
        
    #dialog triggers
    
    def perspective_setDialogTriggers(self,tinfos):
        self.zone.setDialogTriggers(tinfos)
        
        
    def perspective_dialogTrigger(self,srcId,trigger):
        from command import CmdZoneInteract
        
        if self.simLookup.has_key(srcId):
            so = self.simLookup[srcId]
            if self.playerLookup.has_key(so):
                player = self.playerLookup[so]
                CmdZoneInteract(player.curChar.mob,[],trigger)
                
    def perspective_bindTrigger(self,srcId):
        from command import CmdBind
        
        if self.simLookup.has_key(srcId):
            so = self.simLookup[srcId]
            if self.playerLookup.has_key(so):
                player = self.playerLookup[so]
                CmdBind(player.curChar.mob,[])
        
            
    def kickPlayer(self,player):
        id = -1
        if player.simObject:
            id = player.simObject.id
                
        self.mind.callRemote("kickPlayer",id,player.publicName)
                
    def pause(self,pause):        
        self.mind.callRemote("pause",pause)
        

    def setDeathMarker(self,publicName,charName,realm,pos,rot):        
        self.mind.callRemote("setDeathMarker",publicName,realm,pos,rot,charName)
    
    def clearDeathMarker(self,publicName):
        self.mind.callRemote("clearDeathMarker",publicName)


    def perspective_updateSimObjects(self,updates):
        
        for id,pos,rot,v in updates:
            try:
                so = self.simLookup[id]
            except KeyError:
                continue
            
            so.position = pos
            so.rotation = rot
            
            if self.playerLookup.has_key(so):
                so.waterCoverage=v
            else:
                so.canKite=v
                
            try:
                mob = self.zone.mobLookup[so]
                
            except:
                pass
