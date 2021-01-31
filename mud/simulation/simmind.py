# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

# SIMSERVER SIDE

from tgenative import *
from mud.tgepython.console import TGEExport

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword
from md5 import md5

from mud.simulation.shared.simdata import SpawnpointInfo,SimMobInfo,DialogTriggerInfo
from mud.simulation.simobject import SimObject

from mud.world.defines import *
from mud.world.core import CoreSettings
from mud.gamesettings import *
from mud.world.shared.vocals import *

# jelly
import mud.world.shared.worlddata

import os,sys
from traceback import print_exc
from math import radians,sqrt
from random import randint
import re
from itertools import chain



#XXX TODO There is a new mobinfo cacheable, a whole lot of remote calls can be removed and 
#moved over to just use the data in this cacheable... 

HMOUNT = {}

def GetModelInfo(race,sex,look):
    tex = ["","","","","","",""]
    size = 1.0
    animation = ""
    model = ""
    hmount = -1
    for ri in RACEGRAPHICS:
        if ri.name == race:
            if sex == "Female":
                size = ri.size_female
                animation = ri.animation_female
                texhead = ri.texture_head_female
                texbody = ri.texture_body_female
                texarms = ri.texture_arms_female
                texlegs = ri.texture_legs_female
                texhands = ri.texture_hands_female
                texfeet = ri.texture_feet_female
                texspecial = ri.texture_special_female
                if look == 0:
                    model = ri.model_thin_female
                    hmount = ri.hmount_thin_female
                if look == 1:
                    model = ri.model_fit_female
                    hmount = ri.hmount_fit_female
                if look == 2:
                    model = ri.model_heavy_female
                    hmount = ri.hmount_heavy_female
                    
                    
                    
            elif sex == "Male":
                size = ri.size_male
                animation = ri.animation_male
                texhead = ri.texture_head_male
                texbody = ri.texture_body_male
                texarms = ri.texture_arms_male
                texlegs = ri.texture_legs_male
                texhands = ri.texture_hands_male
                texfeet = ri.texture_feet_male
                texspecial = ri.texture_special_male
                if look == 0:
                    model = ri.model_thin_male
                    hmount = ri.hmount_thin_male
                if look == 1:
                    model = ri.model_fit_male
                    hmount = ri.hmount_fit_male
                if look == 2:
                    model = ri.model_heavy_male
                    hmount = ri.hmount_heavy_male
                    
            break

    if hmount != -1:
        if not HMOUNT.has_key((race,sex,look)):
            HMOUNT[(race,sex,look)]= hmount

    
    tex[0]=texhead
    tex[1]=texarms
    tex[2]=texlegs
    tex[3]=texbody
    tex[4]=texfeet
    tex[5]=texhands
    tex[6]=texspecial
    return size,model,tex,animation


SIMMIND = None
RACEGRAPHICS = None
DBNAME_PARSER = re.compile(r'\.|\\|/')
DATABLOCK_RAW = """
datablock PlayerData(%s)
{
   renderFirstPerson = false;
   emap = true;

   className = Armor;
   shapeFile = "~/data/shapes/%s";
   cameraMinDist = 0;
   cameraMaxDist = 4;
   computeCRC = true;

   canObserve = true;
   cmdCategory = "Clients";

   cameraDefaultFov = 75.0;
   cameraMinFov = 5.0;
   cameraMaxFov = 75.0;

    //debrisShapeName = "~/data/shapes/player/debris_player.dts";
   //debris = playerDebris;

   aiAvoidThis = %s;
  
   radius = 1;
   scale = 1;

   minLookAngle = -1.4;
   maxLookAngle = 1.4;
   maxFreelookAngle = 3.0;

   mass = 90;
   drag = 0.3;
   maxdrag = 0.4;
   density = 10;
   maxDamage = 100;
   maxEnergy =  60;
   repairRate = 0.33;
   energyPerDamagePoint = 75.0;

   rechargeRate = 0.256;

   runForce = 48 * 90;
   runEnergyDrain = 0;
   minRunEnergy = 0;
   maxForwardSpeed = 8;
   maxBackwardSpeed = 4;
   maxSideSpeed = 6;

   maxUnderwaterForwardSpeed = 1.5;
   maxUnderwaterBackwardSpeed = 0.75;
   maxUnderwaterSideSpeed = 1.125;

   jumpForce = 8.3 * 90;
   jumpEnergyDrain = 0;
   minJumpEnergy = 0;
   jumpDelay = 15;

   recoverDelay = 9;
   recoverRunForceScale = 1.2;

   minImpactSpeed = 3 * %s + 7;
   speedDamageScale = 0.4;

   boundingBox = "1.2 1.2 2.3";
   pickupRadius = 0.75;

   // Damage location details
   boxNormalHeadPercentage       = 0.83;
   boxNormalTorsoPercentage      = 0.49;
   boxHeadLeftPercentage         = 0;
   boxHeadRightPercentage        = 1;
   boxHeadBackPercentage         = 0;
   boxHeadFrontPercentage        = 1;

   // Foot Prints
   decalData   = PlayerFootprint;
   decalOffset = 0.25;

   //footPuffEmitter = LightPuffEmitter;
   footPuffNumParts = 10;
   footPuffRadius = 0.25;

   dustEmitter = LiftoffDustEmitter;

   splash = PlayerSplash;
   splashVelocity = 4.0;
   splashAngle = 67.0;
   splashFreqMod = 300.0;
   splashVelEpsilon = 0.60;
   bubbleEmitTime = 0.4;
   splashEmitter[0] = PlayerFoamDropletsEmitter;
   splashEmitter[1] = PlayerFoamEmitter;
   splashEmitter[2] = PlayerBubbleEmitter;
   mediumSplashSoundVelocity = 10.0;
   hardSplashSoundVelocity = 20.0;
   exitSplashSoundVelocity = 5.0;

   // Controls over slope of runnable/jumpable surfaces
   runSurfaceAngle  = 55;
   jumpSurfaceAngle = 55;
   maxStepHeight = 0.75;

   minJumpSpeed = 20;
   maxJumpSpeed = 30;

   horizMaxSpeed = 68;
   horizResistSpeed = 33;
   horizResistFactor = 0.35;

   upMaxSpeed = 80;
   upResistSpeed = 25;
   upResistFactor = 0.3;

   footstepSplashHeight = 0.35;


   groundImpactMinSpeed    = 10.0;
   groundImpactShakeFreq   = "4.0 4.0 4.0";
   groundImpactShakeAmp    = "1.0 1.0 1.0";
   groundImpactShakeDuration = 0.8;
   groundImpactShakeFalloff = 10.0;

   //exitingWater         = ExitingWaterLightSound;

   observeParameters = "0.5 4.5 4.5";
   
   scaleLimit = %s;
};
"""



# change to pb.remotecopyable if/when there is more data to store
class ZoneInfo:
    def __init__(self):
        self.scaleLimit = 20



def CreateShapeImage(shapename):
    dbname = DBNAME_PARSER.sub('_',shapename)
    
    try:
        to = TGEObject(dbname)
        return to
    except:
        eval = """
datablock ShapeBaseImageData(%s)
{
   // Basic Item properties
   shapeFile = "~/data/shapes/equipment/%s";
};
"""%(dbname,shapename)
    
    TGEEval(eval)
    db = TGEObject(dbname)
    db.setDynamic()
    #to all existing players
    #for pconn in SIMMIND.gameConnectionIds:
    #    TGECall("SendNewDataBlock",pconn,db)
    
    return dbname


def CreateTSShapePlayerDatablock(spawn,dbname,model):
    dbname += "DTS"
    #already exists?
    try:
        to = TGEObject(dbname)
    except:
        eval = ""
        if spawn.animation:
            f = file("%s/data/shapes/character/animations/%s/animation.cfg"%(GAMEROOT,spawn.animation))
            eval = f.read()
            f.close()
            
            eval = eval.replace("$datablock",dbname)
            eval = eval.replace("$dts",model)
            eval = eval.replace("#","~/data/shapes/character/animations")
        else:
            eval = """datablock TSShapeConstructor(%s)
            {
                baseShape = "~/data/shapes/%s";
            };
            """%(dbname,model)
        
        TGEEval(eval)
    
    db = TGEObject(dbname)
    db.setDynamic()
    #to all existing players
    #for pconn in SIMMIND.gameConnectionIds:
    #    TGECall("SendNewDataBlock",pconn,db)


def CreatePlayerDatablock(spawn, isPlayer=False):
    modelname = spawn.modelname
    
    racial = False
    for ri in RACEGRAPHICS:
        if ri.name == spawn.race:
            racial = True
            break
    
    if racial:
        if isPlayer:
            #change to a spawn attr
            look = 0
            if "_fit" in spawn.modelname:
                look = 1
            if "_heavy" in spawn.modelname:
                look = 2
        else:
            look = randint(0,2)
        
        size,model,tex,animation = GetModelInfo(spawn.race,spawn.sex,look)
        spawn.look = look
        spawn.size = size
        modelname = model
        spawn.animation = animation
        if not spawn.textureHead:
            spawn.textureHead = tex[0]
        if not spawn.textureArms:
            spawn.textureArms = tex[1]
        if not spawn.textureLegs:
            spawn.textureLegs = tex[2]
        if not spawn.textureBody:
            spawn.textureBody = tex[3]
        if not spawn.textureFeet:
            spawn.textureFeet = tex[4]
        if not spawn.textureHands:
            spawn.textureHands = tex[5]
        if not spawn.textureSingle:
            spawn.textureSingle = tex[6]
    
    modelname = "character/models/%s"%modelname
    if not modelname.endswith(".dts"):
        modelname += ".dts"
    
    #quaratine hack
    if isPlayer:
        aiAvoidThis = "true"
    else:
        aiAvoidThis = "false"
    
    ext = "PlayerData"
    #if not isPlayer:
    #    ext = "AIPlayerData"
    
    dbname = DBNAME_PARSER.sub('_',modelname[:-4]) + ext
    
    scaleLimit = str(SIMMIND.zoneInfo.scaleLimit)
    if scaleLimit[0] == '.':
        #format for tge
        scaleLimit = "0" + scaleLimit
    
    try:
        return TGEObject(dbname)
    except:
        eval = DATABLOCK_RAW%(dbname,modelname,aiAvoidThis,spawn.scale,scaleLimit) #we can't use radius here due to sharing datablock on model!
        
        TGEEval(eval)
        db = TGEObject(dbname)
        #to all existing players
        #for pconn in SIMMIND.gameConnectionIds:
        #    TGECall("SendNewDataBlock",pconn,db)
        db.setDynamic()
        
        CreateTSShapePlayerDatablock(spawn,dbname,modelname)
        
        return db



class SimLookup(dict):
    # just a little dictionary that converts keys to int
    
    def __setitem__(self,item,val):
        item = int(item)
        return dict.__setitem__(self,item,val)
    
    def __getitem__(self,item):
        item = int(item)
        return dict.__getitem__(self,item)



class SimMind(pb.Root):
    def __init__(self,perspective=None,zoneInstanceName=None):
        global SIMMIND
        SIMMIND = self
        self.zoneInstanceName = zoneInstanceName
        self.perspective = perspective #-> SimAvatar on World
        self.zombieUpdateTimer = 4
        
        self.simLookup = SimLookup()
        self.simObjects = []
        
        self.updateSimObjects()
        self.tickBrains()
        
        self.updateCanSee()
        
        self.passwords = {}
        
        self.psystemCount = 0
        
        self.spawnInfos = {}
        
        self.playerConnections = {}
        self.gameConnectionIds = []
        
        #simObjectid -> mobinfo
        self.mobInfos = {}
        
        #simObjectid -> [mobinfos,]
        self.playerMobInfos = {}
        self.playerSpawnInfos = {}
        
        self.selectCredit = {}
        
        #simid -> rpgid
        self.projectiles = {}
        
        self.zoneInfo = ZoneInfo()
        
        #publicName -> tgeobject of marker
        self.deathMarkers = {}
    
    
    def onZoneTrigger(self,trigger,obj):
        # takes a TGEObject for both trigger and obj
        if obj.getClassName() != "Player":
            return  # only players can zone
        zonelink = trigger.ZoneLink
        d = self.perspective.callRemote("SimAvatar","onZoneTrigger",self.simLookup[obj.getId()],zonelink)



# -------------------------------------------
# --- Clients
    
    def remote_setZoneInfo(self,scaleLimit):
        self.zoneInfo.scaleLimit = scaleLimit
    
    
    def remote_setSpawnInfos(self,spawns):
        for spawn in spawns:
            self.spawnInfos[spawn.name] = spawn
            CreatePlayerDatablock(spawn,False)
    
    
    def remote_setPlayerPasswords(self,passwords):
        self.passwords = passwords
    
    
    def remote_addPlayerMobInfo(self,pid,mobInfo,spInfo):
        self.playerMobInfos[pid].append(mobInfo)
        self.playerSpawnInfos[pid].append(spInfo)
    
    
    def updateSpawnInfo(self,spinfo):
        for pid,spawninfos in self.playerSpawnInfos.iteritems():
            if spinfo in spawninfos:
                try:
                    simObject = self.simLookup[pid]
                    if simObject.spawnInfo == spinfo:
                        #we are using this spawninfo as our avatar
                        player = TGEObject(pid)
                        for x in xrange(0,7):
                            player.setSkin(x,"") #fix me
                        datablock = CreatePlayerDatablock(spinfo,True)
                        player.SetDataBlock(datablock)
                        
                        if spinfo.race in RPG_PC_RACES:
                            size,model,tex,animation = GetModelInfo(spinfo.race,spinfo.sex,0)
                            player.setScaleModifier(1.0)
                            player.setScale("%f %f %f"%(size,size,size))
                        else:
                            player.setScaleModifier(1.0)
                            player.setScale("%f %f %f"%(spinfo.scale,spinfo.scale,spinfo.scale))
                        
                        self.setPlayerSkins(player,simObject.mobInfo,spinfo)
                        
                        # Reset animation info for the sim object.
                        simObject.brain.noanim = True
                except KeyError:
                    pass
    
    
    def remote_setPlayerSpawnInfo(self,pid,name):
        player = TGEObject(pid)
        for x in xrange(0,7):
            player.setSkin(x,"") #fix me
        for spinfo in self.playerSpawnInfos[pid]:
            if spinfo.name == name:
                datablock = CreatePlayerDatablock(spinfo,True)
                player.SetDataBlock(datablock)
                self.simLookup[pid].spawnInfo = spinfo
                
                for m in self.playerMobInfos[pid]:
                    if m.NAME == spinfo.name:
                        self.simLookup[pid].mobInfo = m
                        break
                
                if spinfo.race in RPG_PC_RACES:
                    size,model,tex,animation = GetModelInfo(spinfo.race,spinfo.sex,0)
                    player.setScale("%f %f %f"%(size,size,size))
                else:
                    player.setScale("%f %f %f"%(spinfo.scale,spinfo.scale,spinfo.scale))
                
                self.setPlayerSkins(player,self.simLookup[pid].mobInfo,spinfo)
                player.playThread(0,"pain") #this here to force teh animation, fix me at some point.. I think this has to do with looping
                player.playThread(0,"idle")
                return
    
    
    def remote_removePlayerMobInfo(self,pid,mid):
        nlist = []
        name = None
        for minfo in self.playerMobInfos[pid]:
            if minfo.ID == mid:
                name = minfo.NAME
                continue
            nlist.append(minfo)
        
        slist = []
        if name:
            #remove from spawninfo too
            slist = list(sinfo for sinfo in self.playerSpawnInfos[pid] if sinfo.name != name)
        
        self.playerMobInfos[pid] = nlist
        self.playerSpawnInfos[pid] = slist
        
        #player = TGEObject(pid)
        #spinfo = self.playerSpawnInfos[pid][0]
        #datablock = CreatePlayerDatablock(spinfo)
        #player.SetDataBlock(datablock)
        #self.simLookup[pid].spawnInfo = spinfo
        #scale = spinfo.scale
        #player.setScale("%f %f %f"%(scale,scale,scale))
    
    
    def setPlayerSkins(self,player,mobInfo,spawninfo):
        """
          SkinHead 0 
          SkinArms 1
          SkinLegs 2
          SkinFeet 3
          SkinHands 4
          SkinBody 5
          SkinSingle 6
        """
        
        if not spawninfo.textureFeet: #only racial have feet
            player.setSkin(6,"~/data/shapes/character/textures/%s"%spawninfo.textureSingle)
            if spawninfo.textureHead:
                player.setSkin(0,"~/data/shapes/character/textures/%s"%spawninfo.textureHead)
            if spawninfo.textureBody:
                player.setSkin(5,"~/data/shapes/character/textures/%s"%spawninfo.textureBody)
            if spawninfo.textureArms:
                player.setSkin(1,"~/data/shapes/character/textures/%s"%spawninfo.textureArms)
            if spawninfo.textureLegs:
                player.setSkin(2,"~/data/shapes/character/textures/%s"%spawninfo.textureLegs)
            if spawninfo.textureHands:
                player.setSkin(4,"~/data/shapes/character/textures/%s"%spawninfo.textureHands)
            if spawninfo.textureFeet:
                player.setSkin(3,"~/data/shapes/character/textures/%s"%spawninfo.textureFeet)
        else:
            
            player.setSkin(0,"~/data/shapes/character/textures/%s"%spawninfo.textureHead)
            if mobInfo.MATARMS:
                player.setSkin(1,"~/data/shapes/character/textures/%s"%mobInfo.MATARMS)
            else:
                player.setSkin(1,"~/data/shapes/character/textures/%s"%spawninfo.textureArms)
            
            if mobInfo.MATLEGS:
                player.setSkin(2,"~/data/shapes/character/textures/%s"%mobInfo.MATLEGS)
            else:
                player.setSkin(2,"~/data/shapes/character/textures/%s"%spawninfo.textureLegs)
            
            if mobInfo.MATFEET:
                player.setSkin(3,"~/data/shapes/character/textures/%s"%mobInfo.MATFEET)
            else:
                player.setSkin(3,"~/data/shapes/character/textures/%s"%spawninfo.textureFeet)
            
            if mobInfo.MATHANDS:
                player.setSkin(4,"~/data/shapes/character/textures/%s"%mobInfo.MATHANDS)
            else:
                player.setSkin(4,"~/data/shapes/character/textures/%s"%spawninfo.textureHands)
            
            if mobInfo.MATBODY:
                player.setSkin(5,"~/data/shapes/character/textures/%s"%mobInfo.MATBODY)
            else:
                player.setSkin(5,"~/data/shapes/character/textures/%s"%spawninfo.textureBody)
                
            player.setSkin(6,"~/data/shapes/character/textures/%s"%spawninfo.textureSingle)
    
    
    def onClientEnterGameResult(self,results,connection):
        #this actually spawns the player object and stuff
        if connection not in self.gameConnectionIds:
            print "Player Dropped before Client Enter Game, possible kick"
            return
        transform,spawnInfos,mobInfos,avatarIndex,role = results
        transform[6] = radians(transform[6])
        t = ' '.join(str(val) for val in transform)
        
        conn = TGEObject(connection)
        
        #we need to set spawninfo(s) here for characters!!!
        dblocks = [CreatePlayerDatablock(sp,True) for sp in spawnInfos]
        
        #playerid  = int(conn.onClientEnterGameReal(t,"TempDummyPlayerData"))
        playerid  = int(conn.onClientEnterGameReal(t,dblocks[avatarIndex].getName()))
        player = TGEObject(playerid)
        
        player.realm = mobInfos[0].REALM
        
        if role == "Monster":
            player.setShapeName("%s (%s)"%(spawnInfos[avatarIndex].name,role))
        elif role == "Immortal" or role == "Guardian":
            sn = player.getShapeName()
            player.setShapeName("%s (%s)"%(sn,role))
        
        self.setPlayerSkins(player,mobInfos[avatarIndex],spawnInfos[avatarIndex])
        
        self.playerConnections[playerid] = conn
        
        #hrm
        so = SimObject(playerid,spawnInfos[avatarIndex],mobInfos[avatarIndex],transform,-1,True)
        #scale = spawnInfos[avatarIndex].scale
        
        spinfo = spawnInfos[avatarIndex]
        if spinfo.race in RPG_PC_RACES:
            size,model,tex,animation = GetModelInfo(spinfo.race,spinfo.sex,0)
            player.setScale("%f %f %f"%(size,size,size))
        else:
            player.setScale("%f %f %f"%((spinfo.scale,spinfo.scale,spinfo.scale)))
        
        self.addSimObject(so)
        
        if int(TGEGetGlobal("$Py::ISSINGLEPLAYER")):
            name = "ThePlayer"
        else:
            name = conn.getPublicName()
        
        self.playerMobInfos[playerid] = mobInfos
        self.playerSpawnInfos[playerid] = spawnInfos
        self.mobInfos[playerid] = mobInfos[avatarIndex] #first character
        
        d = self.perspective.callRemote("SimAvatar","setPlayerSimObject",name,so)
        
        #TGEEval("startLightning();")
        #TGEEval("startRain();")
    
    
    def onClientEnterGame(self,connection):
        if int(TGEGetGlobal("$Py::ISSINGLEPLAYER")):
            name = "ThePlayer"
        else:
            name = TGEObject(connection).getPublicName()
        
        d = self.perspective.callRemote("SimAvatar","onClientEnterGame",name)
        d.addCallback(self.onClientEnterGameResult,connection)
    
    
    def addSimObject(self,simObject):
        #we need to do a cansee type thingy
        self.simObjects.append(simObject)
        self.simLookup[simObject.id] = simObject
    
    
    #10x sec
    def updateCanSee(self):
        #mob infos
        try:
            cansee = TGEGenerateCanSee()
            if cansee:
                for id,cs in cansee.iteritems():
                    so = self.simLookup[id]
                    if int(so.tgeObject.isSimZombie()):
                        continue
                    so.updateCanSee(cs)
        except:
            pass
        self.canSeeTick = reactor.callLater(1,self.updateCanSee)
    
    
    #1x sec
    def updateSimObjects(self):
        #mob infos
        doZombie = False
        self.zombieUpdateTimer -= 1
        if not self.zombieUpdateTimer:
            self.zombieUpdateTimer = 4
            doZombie = True
        
        simUpdates = []
        
        numinzone = NumPlayersInZone()
        dedicated = int(TGEGetGlobal("$Server::Dedicated"))
        
        for so in self.simObjects:
            if not so.brain:
                continue
            tgeObject = so.tgeObject
            try:
                sz = int(tgeObject.isSimZombie())
                if sz != so.simZombie:
                    if sz and so.wanderGroup == -1:
                        tgeObject.setTransform(so.homePoint)
                    
                    so.simZombie = sz
                    so.observer.callRemote('updateSimZombie', sz)
                
                if sz:
                    if dedicated and numinzone:
                        if so.wanderGroup <= 0:
                            continue
                        if doZombie:
                            simUpdates.append(so)
                        #so.updateTransform() #wandergroup
                        continue
                    continue
                
                conn = None
                if self.playerMobInfos.has_key(so.id):
                    if not so.spawnInfo.dirty:
                        for m in self.playerMobInfos[so.id]:
                            if m.dirty:
                                break
                        # Found no dirty mobinfo.
                        else:
                            simUpdates.append(so)
                            continue
                    
                    conn = self.playerConnections[so.id]
                    zombie = False
                    worstmove = 999999
                    worstSpeedMod = 999999
                    walk = False
                    bestvis = 0
                    bestseeinvis = 0
                    bestscale = 0
                    alldead = True
                    bestlight = 0
                    flying = 1
                    attacking = False
                    overrideScale = False
                    
                    minfo = so.mobInfo
                    
                    sinfo = so.spawnInfo
                    sinfo.dirty = False
                    
                    tgeObject.role = minfo.ROLE
                    
                    target = so.brain.target
                    
                    for m in self.playerMobInfos[so.id]:
                        m.dirty = False
                        if m.DETACHED:
                            continue
                        alldead = False
                        overrideScale = False
                        # Player, can only go as fast as slowest character in party.
                        if m.MOVE < worstmove:
                            worstmove = m.MOVE
                        if m.SPEEDMOD < worstSpeedMod:
                            worstSpeedMod = m.SPEEDMOD
                        if m.WALK:
                            walk = True
                        if m.SIZE > bestscale:
                            bestscale = m.SIZE
                        if m.SEEINVISIBLE > bestseeinvis:
                            bestseeinvis = m.SEEINVISIBLE
                        # Only as invisible as most invisible character in party.
                        if m.VISIBILITY > bestvis:
                            bestvis = m.VISIBILITY
                        if m.LIGHT > bestlight:
                            bestlight = m.LIGHT
                        if m.FLYING < flying:
                            flying = m.FLYING
                        if m.SLEEP:
                            worstmove = 0
                            worstSpeedMod = 0
                        if m.FEIGNDEATH:
                            worstmove = 0
                            worstSpeedMod = 0
                            flying = 0
                        if m.ATTACKING:
                            attacking = True
                        if not target and m.TGTID:
                            target = self.simLookup.get(m.TGTID,None)
                        if m.OVERRIDESCALE:
                            overrideScale = True
                    
                    aggroRange = 100
                    if alldead:
                        move = 1
                        speedMod = 0
                        scale = 1
                        seeinvis = 0
                        vis = 1
                        flying = 0
                    else:
                        move = worstmove
                        speedMod = worstSpeedMod
                        scale = bestscale
                        seeinvis = bestseeinvis
                        vis = bestvis
                    
                    # Update the scale based on the default scale modifier (1.0).
                    # The scale modifier can be updated after the scale is properly 
                    # set, so that the scale is a multiplier from base model, and the
                    # modifier is a percent of the scale.
                    if overrideScale:
                        tgeObject.setScaleModifier(1.0)
                        tgeObject.setScale("1.0 1.0 1.0")
                    else:
                       tgeObject.setScaleModifier(1.0)
                       tgeObject.setScale("%f %f %f"%(sinfo.scale, sinfo.scale, sinfo.scale))

                
                        
                else:
                    if not so.mobInfo.dirty and not so.spawnInfo:
                        simUpdates.append(so)
                        continue
                    
                    minfo = so.mobInfo
                    # Set varname for player pets (or previous ones),
                    #  now contains master info
                    if minfo.PLAYERPET or tgeObject.playerPet:
                        tgeObject.setShapeName(minfo.VARNAME)
                    tgeObject.playerPet = minfo.PLAYERPET
                    # mob may change realm due to being a pet or breaking a charm
                    tgeObject.realm = minfo.REALM
                    minfo.dirty = False
                    sinfo = so.spawnInfo
                    sinfo.dirty = False
                    move = minfo.MOVE
                    speedMod = minfo.SPEEDMOD
                    walk = minfo.WALK
                    if minfo.SLEEP:
                        move = 0
                        speedMod = 0
                    scale = minfo.SIZE
                    seeinvis = minfo.SEEINVISIBLE
                    vis = minfo.VISIBILITY
                    bestlight = minfo.LIGHT
                    flying = minfo.FLYING
                    attacking = minfo.ATTACKING
                    zombie = minfo.ZOMBIE
                    target = self.simLookup.get(minfo.TGTID,None)
                    aggroRange = minfo.AGGRORANGE
                
                mount0 = minfo.MOUNT0
                mount1 = minfo.MOUNT1
                mount2 = minfo.MOUNT2
                mount3 = minfo.MOUNT3
                twohanded = minfo.TWOHANDED
                
                if vis > 1:
                    vis = 1
                elif vis < 0:
                    vis = 0
                if seeinvis > 1:
                    seeinvis = 1
                elif seeinvis < 0:
                    seeinvis = 0
                
                if move > 4:
                    move = 4
                elif move < 0:
                    move = 0
                if speedMod < 0:
                    speedMod = 0
                elif speedMod * move > 32:
                    speedMod = 32 / move
                if scale < .2:
                    scale = .2
                elif scale > 5:
                    scale = 5
                
                if walk:
                    move *= 0.5
                so.brain.walk = walk
                
                tgeObject.setVisibility(vis)
                if conn:
                    conn.setSeeInvisible(seeinvis)
                
                tgeObject.aggroRange = aggroRange
                tgeObject.setFlyingMod(flying)
                tgeObject.setMoveModifier(move)
                tgeObject.setMaxForwardSpeed(speedMod)
                tgeObject.setScaleModifier(scale)
                tgeObject.setLightRadius(bestlight * 3.0)
                
                #this could be an option, as it saves quite a bit of CPU to not have stuff walk around
                
                if not conn and not numinzone:
                    zombie = True
                tgeObject.setZombie(zombie)
                
                so.brain.twohanded = twohanded
                tgeObject.twoHanded = twohanded
                so.brain.attacking = attacking
                
                so.brain.setTarget(target)
                
                tgeObject.setEncounterSetting(minfo.ENCOUNTERSETTING)
                tgeObject.primaryLevel = minfo.PRIMARYLEVEL
                tgeObject.setAllianceLeader(minfo.ALLIANCELEADER)
                tgeObject.setGuildName(minfo.GUILDNAME)
                
                # Primary weapon slot
                if not mount0:
                    tgeObject.unmountImage(0)
                else:
                    if minfo.MOUNT0_MAT:
                        tgeObject.mountImage(CreateShapeImage(mount0),0,1.0,"~/data/shapes/equipment/%s"%minfo.MOUNT0_MAT)
                    else:
                        tgeObject.mountImage(CreateShapeImage(mount0),0)
                
                # Secondary weapon slot
                if not mount1:
                    tgeObject.unmountImage(1)
                else:
                    if minfo.MOUNT1_MAT:
                        tgeObject.mountImage(CreateShapeImage(mount1),1,1.0,"~/data/shapes/equipment/%s"%minfo.MOUNT1_MAT)
                    else:
                        tgeObject.mountImage(CreateShapeImage(mount1),1)
                
                # Shield slot
                if not mount2:
                    tgeObject.unmountImage(2)
                else:
                    if minfo.MOUNT2_MAT:
                        tgeObject.mountImage(CreateShapeImage(mount2),2,1.0,"~/data/shapes/equipment/%s"%minfo.MOUNT2_MAT)
                    else:
                        tgeObject.mountImage(CreateShapeImage(mount2),2)
                
                # Head slot
                if not mount3:
                    tgeObject.unmountImage(3)
                else:
                    scale = HMOUNT.get((sinfo.race,sinfo.sex,sinfo.look),1.0)
                    tgeObject.mountImage(CreateShapeImage(mount3),3,scale,"~/data/shapes/equipment/%s"%minfo.MOUNT3_MAT)
                
                self.setPlayerSkins(tgeObject,minfo,sinfo)
                
                simUpdates.append(so)
            
            except:
                print_exc()
        
        updates = []
        for so in simUpdates:
            r = so.updateTransform()
            if r:
                updates.append(r)
        
        if len(updates):
            self.perspective.callRemote("SimAvatar","updateSimObjects",updates)
        
        self.updateSimObjectsTick = reactor.callLater(2,self.updateSimObjects)
    
    
    def tickBrains(self):
        #mob infos
        
        for so in self.simObjects:
            if not so.brain or int(so.tgeObject.isSimZombie()):
                continue
            #if so.mobInfo.ZOMBIE:
            #    continue;
            try:
                so.brain.tick()
            except:
                print_exc()
        
        self.brainsTick = reactor.callLater(.1,self.tickBrains)
    
    
    def getBindPoints_r(self,simgroup,bindpoints):
        for x in xrange(0,int(simgroup.getCount())):
            tobj = TGEObject(simgroup.getObject(x))
            if tobj.getClassName() == "SimGroup":
                self.getBindPoints_r(tobj,bindpoints)
            elif tobj.getClassName() == "rpgBindPoint":
                bindpoints.append(tobj)
    
    
    def remote_getBindPoints(self):
        mg = TGEObject("MissionGroup")
        bindpoints = []
        self.getBindPoints_r(mg,bindpoints)
        #x y z AngAxis
        abindpoints = [tuple(wp.getTransform()[:3]) for wp in bindpoints]
        return abindpoints
    
    
    def getWayPoints_r(self,simgroup,waypoints):
        for x in xrange(0,int(simgroup.getCount())):
            tobj = TGEObject(simgroup.getObject(x))
            if tobj.getClassName() == "SimGroup":
                self.getWayPoints_r(tobj,waypoints)
            elif tobj.getClassName() == "rpgWayPoint":
                waypoints.append(tobj)
    
    
    def getWayPoints(self):
        self.waypoints = {} #wandergroup -> [transform,transform,...]
        mg = TGEObject("MissionGroup")
        waypoints = []
        self.getWayPoints_r(mg,waypoints)
        for wp in waypoints:
            #x y z AngAxis
            transform = wp.getTransform()
            wandergroup = int(wp.wandergroup)
            if wandergroup == -1:
                print "Warning:  Uninitialized waypoint"
                continue
            try:
                self.waypoints[wandergroup].append(transform)
            except KeyError:
                self.waypoints[wandergroup] = [transform]
        
        #now we have all our waypoints seperated into wandergroups... find out which you can get from where
        self.paths = {}
        for wgroup,waypoints in self.waypoints.iteritems():
            self.paths[wgroup] = dict((x,[]) for x in xrange(0,len(waypoints)))
            paths = self.paths[wgroup]
            
            for x,wp1 in enumerate(waypoints):
                for y,wp2 in enumerate(waypoints):
                    if x == y:
                        continue
                    result = TGECall('MyCastRay',"%f %f %f"%(wp1[0],wp1[1],wp1[2]),"%f %f %f"%(wp2[0],wp2[1],wp2[2]))
                    if int(result):
                        paths[x].append(y)
            
            print wgroup,paths
    
    
    def getDialogTriggers_r(self,simgroup,dtriggers):
        for x in xrange(0,int(simgroup.getCount())):
            tobj = TGEObject(simgroup.getObject(x))
            if tobj.getClassName() == "SimGroup":
                self.getDialogTriggers_r(tobj,dtriggers)
            elif tobj.getClassName() == "TSStatic":
                if tobj.dialogTrigger and float(tobj.dialogRange):
                    dtriggers.append(tobj)
    
    
    def getDialogTriggers(self):
        mg = TGEObject("MissionGroup")
        dtriggers = []
        self.getDialogTriggers_r(mg,dtriggers)
        tinfos = []
        for dtrigger in dtriggers:
            #x y z AngAxis
            transform = dtrigger.getTransform()
            triginfo = DialogTriggerInfo()
            triginfo.position = tuple(transform[:3])
            triginfo.dialogTrigger = dtrigger.dialogTrigger
            triginfo.dialogRange = float(dtrigger.dialogRange)
            
            tinfos.append(triginfo)
        
        if len(tinfos):
            self.perspective.callRemote("SimAvatar","setDialogTriggers",tinfos)
    
    
    def onReachDestination(self,id):
        so = self.simLookup[id]
        if so.wanderGroup != -1 and self.waypoints.has_key(so.wanderGroup) and len(self.waypoints[so.wanderGroup]) > 1:
            if so.waypoint == -1:
                p1 = so.tgeObject.getPosition()
                bestd = 999999
                best = 0
                for c,p2 in enumerate(self.waypoints[so.wanderGroup]):
                    x = p1[0] - p2[0]
                    y = p1[1] - p2[1]
                    z = p1[2] - p2[2]
                    d = x*x + y*y + z*z  # sqrt not needed, so leave out
                    if d < bestd:
                        best = c
                        bestd = d
                so.waypoint = best
                transform = self.waypoints[so.wanderGroup][so.waypoint]
                so.tgeObject.setTransform(' '.join(str(val) for val in transform))
            
            paths = self.paths[so.wanderGroup]
            bah = False
            try:
                waypoints = paths[so.waypoint]
            except KeyError:
                bah = True
            if bah or not len(waypoints):
                #print "WARNING: NO WAYPOINT FOR WANDERING MOB: Group = %i"%so.wanderGroup
                #print "Picking a random waypoint"
                transform = ' '.join(map(str,self.waypoints[so.wanderGroup][randint(0,len(self.waypoints[so.wanderGroup])-1)][:3]))
                so.tgeObject.setMoveDestination(transform,True)
                return
            
            if len(waypoints) == 1:
                so.waypoint = waypoints[0]
            else:
                so.waypoint = waypoints[randint(0,len(waypoints)-1)]
            
            transform = ' '.join(map(str,self.waypoints[so.wanderGroup][so.waypoint][:3]))
            so.tgeObject.setMoveDestination(transform,True)
        else:
            if so.wanderGroup != -1:
                print "Warning: Wandering mob with no waypoints.  Wandergroup = %i"%so.wanderGroup
            
            transform = map(str,so.tgeObject.getTransform()[:3])
            home = so.homePoint.split(" ",3)[-1]
            point = "%s %s"%(' '.join(transform),home)
            so.tgeObject.setTransform(point)
    
    
    def remote_warp(self,id,tid):
        try:
            src = self.simLookup[id]
        except:
            print "WARNING: Warp: SimObject Src doesn't exist"
        try:
            tgt = self.simLookup[tid]
        except:
            print "WARNING: Warp: SimObject Tgt doesn't exist"
        
        strans = src.tgeObject.getTransform()
        ttrans = tgt.tgeObject.getTransform()
        src.tgeObject.setVelocity("0 0 0")
        src.tgeObject.setTransform("%s %s %s %s %s %s %s"%(ttrans[0],ttrans[1],ttrans[2],strans[3],strans[4],strans[5],strans[6]))
    
    def getSpawnPoints_r(self,simgroup,spawnpoints):
        for x in xrange(0,int(simgroup.getCount())):
            tobj = TGEObject(simgroup.getObject(x))
            if tobj.getClassName() == "SimGroup":
                self.getSpawnPoints_r(tobj,spawnpoints)
            elif tobj.getClassName() == "rpgSpawnPoint":
                spawnpoints.append(tobj)
    
    
    def remote_getSpawnPoints(self):
        #we'll initialize the waypoints here too
        self.getWayPoints()
        self.getDialogTriggers()
        
        spoints = []
        mg = TGEObject("MissionGroup")
        self.getSpawnPoints_r(mg,spoints)
        thepoints = []
        for sp in spoints:
            #x y z AngAxis
            transform = sp.getGroundTransform()
            transform = tuple(float(x) for x in transform.split(" "))
            
            spoint = SpawnpointInfo()
            spoint.transform = transform
            spoint.group = sp.spawngroup.upper()
            spoint.wanderGroup = sp.wandergroup
            thepoints.append(spoint)
        
        try:
            if int(TGEGetGlobal("$Server::Dedicated")) or int(TGEGetGlobal("$pref::gameplay::SPpopulators")):
                from populator import Populate
                ppoints,ppaths,pwaypoints = Populate(thepoints,self.paths)
                thepoints.extend(ppoints)
                
                for wgroup,ppoints in pwaypoints.iteritems():
                    self.waypoints[wgroup] = ppoints
                
                for wgroup,paths in ppaths.iteritems():
                    self.paths[wgroup] = paths
        except:
            print_exc()
        
        return thepoints
    
    
    def remote_spawnBot(self,name,transform,wanderGroup,sinfo,mobInfo):
        datablock = CreatePlayerDatablock(sinfo,False)
        if not self.spawnInfos.has_key(sinfo.name):
            self.spawnInfos[sinfo.name] = sinfo
        
        spawnInfo  = self.spawnInfos[sinfo.name]
        
        dbname = datablock.getName()
        id = int(TGEEval('newNPCOrc("%s","1.0","%s","%s");'%(' '.join(map(str,transform)),mobInfo.VARNAME,dbname)))
        bot = TGEObject(id)
        
        if spawnInfo.race in RPG_PC_RACES:
            size,model,tex,animation = GetModelInfo(spawnInfo.race,spawnInfo.sex,0)
            size *= spawnInfo.scale
            bot.setScale("%f %f %f"%(size,size,size))
        else:
            scale = spawnInfo.scale
            bot.setScale("%f %f %f"%(scale,scale,scale))
        
        self.setPlayerSkins(bot,mobInfo,spawnInfo)

        so = SimObject(id,spawnInfo,mobInfo,transform,wanderGroup,False)
        
        self.mobInfos[id] = mobInfo
        
        self.addSimObject(so)
        
        self.onReachDestination(id)
        
        bot.playThread(0,"idle")
        
        return so
    
    
    def remote_setFollowTarget(self,spawnId,targetId):
        #tge = TGEObject(spawnId)
        #tge.setFollowObject(targetId)
        so = self.simLookup[spawnId]
        tgt = None
        if targetId:
            tgt = self.simLookup[targetId]
        
        so.brain.setFollowTarget(tgt)
    
    
    def remote_setTarget(self,spawnId, targetId):
        #tge = TGEObject(spawnId)
        so = self.simLookup[spawnId]
        tgt = None
        if targetId:
            tgt = self.simLookup[targetId]
        
        so.brain.setTarget(tgt)
        #print "setTarget",spawnId, targetId
    
    
    def remote_setHomeTransform(self,spawnId,homePos,homeRot):
        so = self.simLookup[spawnId]
        so.homePoint = ' '.join(map(str,chain(homePos,homeRot)))
    
    
    def remote_resetHomeTransform(self,spawnID):
        so = self.simLookup[spawnID]
        so.homePoint = so.backupHomePoint
    
    
    # Mob pets need the ability to inherit the home transform of their
    #  master. Otherwise it would be set at where they were summoned.
    # In that case, they'd constantly warp back to the summoning point
    #  when being in zombie state.
    def remote_inheritHomeTransform(self,spawnID,masterID):
        so = self.simLookup[spawnID]
        masterso = self.simLookup[masterID]
        
        so.homePoint = masterso.homePoint
        so.backupHomePoint = masterso.backupHomePoint
        # Inheriting wander group as well is important, since
        #  having a wandergroup will prevent warping to home
        #  transform when going to zombie state.
        so.wanderGroup = masterso.wanderGroup
    
    
    def remote_clearTarget(self,spawnId):
        #print "clearTarget", spawnId, transform
        so = self.simLookup[spawnId]
        so.brain.setTarget(None)
        so.tgeObject.setFollowObject(0)
        if so.wanderGroup > 0:
            if so.waypoint != -1:
                transform = self.waypoints[so.wanderGroup][so.waypoint]
                so.tgeObject.setMoveDestination("%f %f %f"%(transform[0],transform[1],transform[2]),True)
            else:
                self.onReachDestination(so.id)
        else:
            pos = so.homePoint.rsplit(' ',4)[0]
            so.waypoint = -1
            so.tgeObject.setMoveDestination(pos,False)
    
    
    def grantSelectCredit(self,result,srcId):
        self.selectCredit[srcId] = False
    
    
    def dialogTrigger(self,srcId,trigger):
        if self.selectCredit.get(srcId,None):
            return
        try:
            src = self.simLookup[srcId]
        except KeyError:
            return
        
        self.selectCredit[srcId] = True
        
        d = self.perspective.callRemote('SimAvatar','dialogTrigger',srcId,trigger)
        d.addCallback(self.grantSelectCredit,srcId)
        d.addErrback(self.grantSelectCredit,srcId)
    
    
    def bindTrigger(self,srcId):
        if self.selectCredit.get(srcId,None):
            return
        try:
            src = self.simLookup[srcId]
        except KeyError:
            return
        
        self.selectCredit[srcId] = True
        
        d = self.perspective.callRemote('SimAvatar','bindTrigger',srcId)
        d.addCallback(self.grantSelectCredit,srcId)
        d.addErrback(self.grantSelectCredit,srcId)
    
    
    def select(self,srcId,tgtId,charIndex,doubleClick,modifier_shift):
        if self.selectCredit.get(srcId,None):
            return
        try:
            src = self.simLookup[srcId]
        except KeyError:
            return
        try:
            tgt = self.simLookup[tgtId]
        except KeyError:
            return
        
        self.selectCredit[srcId] = True
        
        d = self.perspective.callRemote('SimAvatar','select',srcId,tgtId,charIndex,doubleClick,modifier_shift)
        d.addCallback(self.grantSelectCredit,srcId)
        d.addErrback(self.grantSelectCredit,srcId)
    
    
    def remote_setSelection(self,srcId,tgtId,charIndex):
        so = self.simLookup[srcId]
        tgt = self.simLookup.get(tgtId,None)
        so.brain.setTarget(tgt)
        
        conn = TGEObject(srcId)
        conn.setSelectedObjectId(tgtId,charIndex)
    
    
    def remote_setDisplayName(self,srcId,charName):
        try:
            self.simLookup[srcId].tgeObject.setShapeName(charName)
        except:
            print_exc()
    
    
    def remote_newSpellEffect(self,srcId,effect,interrupt=True):
        src = self.simLookup[srcId]
        if interrupt:
            TGEEval("interruptSpellcasting(%s);"%src.tgeObject.getId())
        src.tgeObject.castSpell(effect)
    
    
    def remote_newAudioEmitterLoop(self,srcId,sound,time):
        src = self.simLookup[srcId]
        pos = ' '.join(map(str,src.position))
        
        if src.spawnInfo.scale > 3.0:
            desc = "AudioDefaultLooping3d"
        else:
            desc = "AudioClosestLooping3d"
        
        eval = """
         %%p = new AudioEmitter(AUDIOEMITTERLOOP_%i) {
            position = "%s";
            rotation = "1 0 0 0";
            scale = "1 1 1";
            description = "%s";
            filename = "~/data/sound/%s";
            parentId = %i;
         };
         MissionCleanup.add(%%p);
         %%p.schedule(%i,"delete");        
        """%(self.psystemCount,pos,desc,sound,srcId,time)
        TGEEval(eval)
        
        #yes, this is using same counter as particle system...
        self.psystemCount += 1
    
    
    def remote_newParticleSystem(self,srcId,emitterName,particleName,time):
        src = self.simLookup[srcId]
        pos = ' '.join(map(str,src.position))
        
        eval = """
         %%p = new ParticleEmitterNode(PARTICLESYSTEM_%i) {
            position = "%s";
            rotation = "1 0 0 0";
            scale = "1 1 1";
            dataBlock = "ChimneySmokeEmitterNode";
            emitter = "%s";
            velocity = "1";
            textureOverride = "~/data/shapes/particles/%s";
            parentId = %i;
         };
         MissionCleanup.add(%%p);
         %%p.schedule(%i,"delete");        
        """%(self.psystemCount,pos,emitterName,particleName,srcId,time)
        TGEEval(eval)
        
        self.psystemCount += 1
    
    
    def remote_deleteObject(self,id):
        #print "DELETING SIMOBJECT %i"%id
        try:
            del self.mobInfos[id]
        except KeyError:
            pass
        
        tge = TGEObject(id)
        #print tge.getClassName()
        so = self.simLookup[id]
        del self.simLookup[id]
        self.simObjects.remove(so)
        tge.delete()
    
    
    def remote_immobilize(self,id):
        tge = TGEObject(id)
        if tge.getClassName()=="AIPlayer":
            tge.setMoveSpeed(0.0)
    
    
    def onPlayerDeleted(self,id):
        #in single player this is a whole new simmind so none of this has to happen
        try:
            del self.mobInfos[id]
        except KeyError:
            pass
        try:
            del self.playerMobInfos[id]
        except KeyError:
            pass
        try:
            del self.playerSpawnInfos[id]
        except KeyError:
            pass
        
        try:
            del self.playerConnections[id]
            so = self.simLookup[id]
            del self.simLookup[id]
            self.simObjects.remove(so)
        except KeyError:
            pass
    
    
    def remote_die(self,id):
        so = self.simLookup[id]
        so.brain.die()
        so.tgeObject.setDamageState("Disabled")
    
    
    def remote_casting(self,id,casting,interrupt=True):
        so = self.simLookup[id]
        if interrupt:
            TGEEval("interruptSpellcasting(%s);"%so.tgeObject.getId())
        so.brain.casting(casting)
    
    
    def remote_cast(self,id,projectile=False):
        so = self.simLookup[id]
        so.brain.cast(projectile)
    
    
    def remote_playAnimation(self,id,anim):
        so = self.simLookup[id]
        so.brain.playAnimation(anim)
    
    
    def remote_pain(self,id):
        so = self.simLookup[id]
        so.brain.pain()
    
    
    def remote_triggerParticleNodes(self,id,pnodes):
        tge = self.simLookup[id].tgeObject
        for node,particle,texture,duration in pnodes:
            tge.triggerParticleNode(node,particle,texture,duration)
    
    
    def remote_respawnPlayer(self, soId, transform):
        so = self.simLookup[soId]
        t = map(float,transform.split(" "))
        t[6] = radians(t[6])
        so.tgeObject.setTransform(t)
        so.tgeObject.setVelocity("0 0 0")
        so.position = (t[0],t[1],t[2] + 2.0)
        so.tgeObject.setDamageState("Enabled")
        so.brain.death = 0
    
    
    def remote_vocalize(self,sexcode,set,vox,which,loc):
        if sexcode == 1:
            sex = "Female"
        else:
            sex = "Male"
        if which < 10:
            num = "0%i"%which
        else:
            num = str(which)
        filename = "vocalsets/%s_LongSet_%s/%s_LS_%s_%s%s.ogg"%(
        sex,set,sex,set,VOCALFILENAMES[vox],num)
        
        self.remote_playSound(filename,loc)
    
    
    def remote_playSound(self,sound,loc,bigSound = False):
        #eval = 'alxPlay(alxCreateSource(AudioClosest3d, "~/data/sound/%s",%f, %f,%f));'%(sound,loc[0],loc[1],loc[2])
        if bigSound:
            desc = "AudioDefault3d"
        else:
            desc = "AudioClosest3d"
        
        eval = 'serverPlay3d(%s,"%s/data/sound/%s","%f %f %f");'%(desc,GAMEROOT,sound,loc[0],loc[1],loc[2])
        
        TGEEval(eval)

    def remote_spawnExplosion(self,srcId,explosion,onground=0):
        src = self.simLookup[srcId]
        loc = src.position
        eval = 'ServerSpawnExplosion(%s,"%f %f %f",%i);'%(explosion,loc[0],loc[1],loc[2],onground)
        TGEEval(eval)
    
    
    def destroyServer(self):
        try:
            self.canSeeTick.cancel()
        except:
            pass
        try:
            self.updateSimObjectsTick.cancel()
        except:
            pass
        try:
            self.brainsTick.cancel()
        except:
            pass
        
        self.simLookup = None
        self.simObjects = None
        self.spawnInfos = None
        self.playerSpawnInfos = None
        self.mobInfos = None
        self.playerMobInfos = None
        
        global SIMMIND
        SIMMIND = None
    
    
    def onGameConnectionConnect(self,connId):
        self.gameConnectionIds.append(connId)
    
    
    def onGameConnectionDrop(self,connId):
        try:
            self.gameConnectionIds.remove(connId)
        except:
            pass
        if int(TGEGetGlobal("$Py::ISSINGLEPLAYER")):
            self.destroyServer()
    
    
    def onProjectileCollision(self,projId,hitId,hitPos):
        rpgid = self.projectiles[projId]
        if self.simLookup.has_key(hitId):
            hitPos = map(float, hitPos.split(" "))
            self.perspective.callRemote("SimAvatar","projectileCollision",rpgid,hitId,hitPos)
    
    
    def onImpact(self,simId,velocity):
        try:
            src = self.simLookup[simId]
            psrc = src.tgeObject.getPosition()
            self.perspective.callRemote("SimAvatar","onImpact",simId,velocity,psrc)
        except KeyError:
            pass
    
    
    def onProjectileDeleted(self,projId):
        try:
            rpgid = self.projectiles[projId]
        except KeyError:
            return
        self.perspective.callRemote("SimAvatar","deleteProjectile",rpgid)
        del self.projectiles[projId]
    
    
    def remote_launchProjectile(self,pid,srcId,tgtId,pdata,speed):
        try:
            src = self.simLookup[srcId]
            dst = self.simLookup[tgtId]
        except KeyError:
            self.perspective.callRemote("SimAvatar","deleteProjectile",pid)
            return
        
        if not pdata.startswith("AFX_"):
            psrc = src.tgeObject.getPosition()
            pdst = dst.tgeObject.getPosition()
            
            #can't modify a tuple
            sz = psrc[2] + src.spawnInfo.radius * 0.75
            dz = pdst[2] + dst.spawnInfo.radius * 0.75
            
            x = pdst[0] - psrc[0]
            y = pdst[1] - psrc[1]
            z = dz - sz
            
            d = sqrt(x*x + y*y + z*z)
            
            if not d:
                self.perspective.callRemote("SimAvatar","deleteProjectile",pid)
                return
            
            x /= d
            y /= d
            z /= d
            
            rad = src.spawnInfo.radius / 3
            px = psrc[0] + x * rad
            py = psrc[1] + y * rad
            pz = sz + z * rad
            
            x *= speed
            y *= speed
            z *= speed
            
            myid = int(TGECall("LaunchProjectile",srcId,tgtId,"%f %f %f"%(px,py,pz),pdata,"%f %f %f"%(x,y,z)))
        
        else:
            myid = int(TGECall("LaunchAfxProjectile",srcId,tgtId,pdata[4:]))
            if myid == -1:
                self.perspective.callRemote("SimAvatar","deleteProjectile",pid)
                return #something bad happpened
        
        self.projectiles[myid] = pid
        
        #print "LaunchProjectile",
        
        return True
    
    
    def remote_setWeather(self,wc):
        from weather import SetWeather
        SetWeather(wc)
    
    
    def remote_stop(self):
        if int(TGEGetGlobal("$Server::Dedicated")):
            TGEEval("quit();")
    
    
    def remote_kickPlayer(self,id,publicName):
        conn = None
        if id != -1:
            conn = self.playerConnections.get(id,None)
        else:
            # If we parse the list in reversed order,
            #  no need to copy to prevent problems
            #  while removing items during loop.
            for i in reversed(self.gameConnectionIds):
                try:
                    c = TGEObject(i)
                except:
                    self.gameConnectionIds.remove(i)
                    continue
                
                if c.getPublicName() == publicName:
                    conn = c
                    break
        if conn:
            conn.delete("You were kicked from the server.")
    
    
    #def remote_pause(self,pause):
    #    TGESetGlobal("$GamePaused",pause)
    
    
    def remote_setDeathMarker(self,publicName,realm,pos,rot,cname):
        #remove any previous
        self.remote_clearDeathMarker(publicName)
        
        realmdata = ("","GraveMarkerFoLData","GraveMarkerMoDData","GraveMarkerMoDData")
        
        eval = """
         %%p = new Item(%s_DeathMarker) {
            position = "%f %f %f";
            rotation = "%f %f %f %f";
            scale = ".5 .5 .5";
            dataBlock = "%s";
            static = true;
         };
         MissionCleanup.add(%%p);
        """%(publicName,pos[0],pos[1],pos[2]+.25,rot[0],rot[1],rot[2],rot[3],realmdata[realm])
        TGEEval(eval)
        self.deathMarkers[publicName]=TGEObject('%s_DeathMarker'%publicName)
        
        self.deathMarkers[publicName].setShapeName("%s's Grave"%cname)
    
    
    def remote_clearDeathMarker(self,publicName):
        dm = self.deathMarkers.get(publicName,None)
        if dm:
            del self.deathMarkers[publicName]
            dm.delete()
    
    
    def remote_clearParticleNode(self,id,slot):
        tge = self.simLookup[id].tgeObject
        if slot == RPG_SLOT_PRIMARY:
            node = "Mount0"
        else:
            node = "Mount1"
        tge.clearParticleNode(node)
    
    
    def remote_itemParticleNode(self,id,slot,particle,texture):
        tge = self.simLookup[id].tgeObject
        if slot == RPG_SLOT_PRIMARY:
            node = "Mount0"
        else:
            node = "Mount1"
        tge.triggerParticleNode(node,particle,texture,-1)



# -------------------------------------------------------
# --- TGE -> Python callbacks


def PyOnImpact(args):
    objectId = int(args[1])
    velocity = int(args[2])
    SIMMIND.onImpact(objectId,velocity)


def PyOnProjectileCollision(args):
    projId = int(args[1])
    hitId = int(args[2])
    hitPos = args[3]
    SIMMIND.onProjectileCollision(projId,hitId,hitPos)


def PyOnProjectileDeleted(args):
    projId = int(args[1])
    if SIMMIND:
        SIMMIND.onProjectileDeleted(projId)


def PyOnGameConnectionConnect(args):
    connId = int(args[1])
    SIMMIND.onGameConnectionConnect(connId)


def PyOnGameConnectionDrop(args):
    connId = int(args[1])
    SIMMIND.onGameConnectionDrop(connId)


def PyOnEndSequence(args):
    id = int(args[1])
    try:
        so = SIMMIND.simLookup[id]
        so.brain.onEndSequence()
    except KeyError:
        pass


def OnReachDestination(args):
    id = int(args[1])
    SIMMIND.onReachDestination(id)


def PyOnPlayerDeleted(args):
    #print "ON PLAYER DELETED"
    id = int(args[1])
    player = TGEObject(id)
    if player.getClassName() == "Player":
        SIMMIND.onPlayerDeleted(id)


#cpp->PySelect

def OnDialogTrigger(args):
    srcId = int(args[1])
    trigger = args[2]
    SIMMIND.dialogTrigger(srcId,trigger)


def OnBindTrigger(args):
    srcId = int(args[1])
    SIMMIND.bindTrigger(srcId)


def PySelect(args):
    srcId = int(args[1])
    tgtId = int(args[2])
    charIndex = int(args[3])
    doubleClick = int(args[4])
    modifier_shift = int(args[5])
    SIMMIND.select(srcId,tgtId,charIndex,doubleClick,modifier_shift)


def PyClientBegin(args):
    print args


def PyValidatePlayer(args):
    #validate with dynamic world password
    publicName = args[1]
    password = args[2]
    try:
        if SIMMIND.passwords[publicName] == password:
            return "Validated"
        else:
            return "Error"
    except:
        return "Error"


def PyOnClientEnterGame(args):
    connection = int(args[1])
    SIMMIND.onClientEnterGame(connection)


def PyZoneTrigger(args):
    trigger = TGEObject(args[1])
    obj = TGEObject(args[2])
    SIMMIND.onZoneTrigger(trigger,obj)


def StartSimulation():
    #the server is up, start simulation connection to world
    if int(TGEGetGlobal("$Server::Dedicated")):
        SIMMIND.perspective.callRemote("SimAvatar","startSimulation",SIMMIND,SIMMIND.zoneInstanceName,os.getpid())
    else:
        from mud.client.playermind import PLAYERMIND
        SIMMIND.perspective.callRemote("SimAvatar","startSimulation",PLAYERMIND.simMind,PLAYERMIND.simMind.zoneInstanceName)



# -----------------------------------------------
# DEDICATED

#self.simMind = SimMind(self.perspective,zconnect.instanceName)
#connect to world's simulation account thru master query
#dictate zone's

def NumPlayersInZone():
    try:
        return len(SIMMIND.gameConnectionIds)
    except:
        return 0

def SetRaceGraphics(graphics):
    global RACEGRAPHICS
    RACEGRAPHICS = graphics

def GotZoneConnect(zconnect):
    global RACEGRAPHICS 
    
    print "Launching: ", zconnect.niceName
    RACEGRAPHICS = zconnect.raceGraphics
    SIMMIND.zoneInstanceName = zconnect.instanceName
    eval = """
    createServer("Multiplayer", "%s/data/missions/%s");
    """%(GAMEROOT,zconnect.missionFile)
    TGEEval(eval)


def DedicatedDisconnected(args):
    TGEEval("quit();")


def WorldConnected(perspective):
    perspective.notifyOnDisconnect(DedicatedDisconnected)
    
    #we should also be able to send a specific zone here... though for now it'll be easier if world picks
    #for this we send "any"
    SIMMIND.perspective = perspective
    #$pref::Net::Port <- client
    #$Pref::Server::Port <- server
    serverPort = int(TGEGetGlobal("$Pref::Server::Port"))
    perspective.callRemote("SimAvatar","spawnDedicatedZone",TGEGetGlobal("$zoneArg"),serverPort).addCallbacks(GotZoneConnect,Failure)


def GotWorldInfos(winfos,perspective):
    perspective.broker.transport.loseConnection()
    #worldName
    #worldIP
    #worldPort
    wname = TGEGetGlobal("$Py::DedicatedWorld")
    wname = wname.replace("_"," ")
    
    found = False
    
    for world in winfos:
        print world.worldName, wname
        if world.worldName == wname:
            found = True
            #attempt login
            factory = pb.PBClientFactory()
            world.worldIP = "127.0.0.1" #only on local host for now
            print "Connecting to: ",world.worldIP, world.worldPort
            reactor.connectTCP(world.worldIP,world.worldPort,factory)
            mind = SimMind()
            #to do add authentication (zone password)
            password = md5("ZoneServer").digest()
            
            factory.login(UsernamePassword("ZoneServer-ZoneServer",password),mind).addCallbacks(WorldConnected, Failure)
    
    if not found:
        print "World is not currently up"


def Failure(error):
    print error


def MasterConnected(perspective):
    perspective.callRemote("EnumWorlds","enumLiveWorlds",True,RPG_BUILD_DEMO,False,not RPG_BUILD_LIVE).addCallbacks(GotWorldInfos,Failure,(perspective,))


def WorldSimulationLogin():
#dedicated
    #redirect stdout
    sys.oldstdout = sys.stdout
    sys.oldstderr = sys.stderr
    class mywriter:
        def write(self, text):
            TGEPrint(text)
            #text = text.replace('\n',"")
            #TGEEval(r'echo("%s");'%text)
            #wx.LogMessage(text) #strip \n
            #sys.oldstdout.write(text)
            #sys.oldstdout.flush()
        def __del__(self):
            sys.stdout = sys.oldstdout
            sys.stderr = sys.oldstderr
    sys.stdout = mywriter()
    sys.stderr = mywriter()
    
    TGESetGlobal("$Py::ISSINGLEPLAYER",0)
    
    #masterIP = TGEGetGlobal("$Py::MasterIP")
    #masterPort = int(TGEGetGlobal("$Py::MasterPort"))
    #print masterIP, masterPort
    #factory = pb.PBClientFactory()
    #reactor.connectTCP(masterIP,masterPort,factory)
    #factory.login(UsernamePassword("EnumWorlds-EnumWorlds","EnumWorlds"),None).addCallbacks(MasterConnected, Failure)
    val = TGEGetGlobal("$Py::WorldPort")
    if val:
        worldport = int(val)
        factory = pb.PBClientFactory()
        reactor.connectTCP("127.0.0.1",worldport,factory)
        mind = SimMind()
        password = md5("ZoneServer").digest()
        
        factory.login(UsernamePassword("ZoneServer-ZoneServer",password),mind).addCallbacks(WorldConnected, Failure)



# probably change this to use the connection connect/drop stuff
TGEExport(PyOnPlayerDeleted,"Py","OnPlayerDeleted","desc",2,2)

TGEExport(PyOnImpact,"Py","OnImpact","desc",3,3)

TGEExport(PyOnGameConnectionConnect,"Py","OnGameConnectionConnect","desc",2,2)
TGEExport(PyOnGameConnectionDrop,"Py","OnGameConnectionDrop","desc",2,2)

TGEExport(OnDialogTrigger,"Py","OnDialogTrigger","desc",3,3)
TGEExport(OnBindTrigger,"Py","OnBindTrigger","desc",2,2)

TGEExport(PyZoneTrigger,"Py","ZoneTrigger","desc",3,3)
TGEExport(PySelect,"Py","Select","desc",6,6)
TGEExport(PySelect,"Py","select","desc",6,6) #<---- more string entry shit, hrm, tgescript is case insensitve should change tgeexport lookup
TGEExport(PyClientBegin,"Py","ClientBegin","desc",2,2)
TGEExport(PyValidatePlayer,"Py","ValidatePlayer","desc",3,3)
# OnClientEnterGame is being made into onClientEnterGame on cs side,
#  which is probably due to stringentry table
TGEExport(PyOnClientEnterGame,"Py","PyClientEnterGame","desc",2,2)

TGEExport(OnReachDestination,"Py","onReachDestination","desc",2,2)

TGEExport(PyOnEndSequence,"Py","onEndSequence","desc",2,2)

# server
TGEExport(StartSimulation,"Py","StartSimulation","desc",1,1)

# dedicated
TGEExport(WorldSimulationLogin,"Py","WorldSimulationLogin","desc",1,1)

TGEExport(PyOnProjectileCollision,"Py","OnProjectileCollision","desc",4,4)
TGEExport(PyOnProjectileDeleted,"Py","OnProjectileDeleted","desc",2,2)



def PyExec():
    pass
    #TGESetGlobal("$Py::DedicatedWorld","liveworld")


