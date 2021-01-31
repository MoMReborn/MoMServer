# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



from twisted.spread import pb
from mud.world.defines import *
import traceback

class WorldConfig(pb.Copyable,pb.RemoteCopy):
    def __init__(self):
        self.worldName = ""
        self.worldPort = 0
        self.playerPassword = ""
        self.zonePassword = ""
        self.allowGuests = ""
        self.demoWorld = True
        
        self.maxLiveZones = 0
        self.maxLivePlayers = 0
    
pb.setUnjellyableForClass(WorldConfig, WorldConfig) 


class WorldInfo(pb.Copyable,pb.RemoteCopy):
    def __init__(self):
        self.worldName = ""
        self.worldIP = ""
        self.worldPort = 0
        self.hasPlayerPassword = False
        self.hasZonePassword = False
        self.allowGuests = False
        self.numLivePlayers = 0
        self.numLiveZones = 0
        
    
pb.setUnjellyableForClass(WorldInfo, WorldInfo) 

#a little wasteful
class NewCharacter(pb.Copyable,pb.RemoteCopy):
    def __init__(self):
        self.reset()
        
    def reset(self):
        self.name = ""
        self.scores = {}
        self.adjs = {}
        
        self.portraitPic = "p001"
        
        self.klass = "Warrior"
        self.race = "Human"
        self.sex = "Male"
        self.look = 0
        
        for s in RPG_STATS:
            self.scores[s]=0
            self.adjs[s]=0
            
        self.ptsRemaining = 100
        
pb.setUnjellyableForClass(NewCharacter, NewCharacter) 
        
class CharacterInfo(pb.Copyable,pb.RemoteCopy):
    def __init__(self,char=None):     
        self.name = ""
        self.klasses = []
        self.levels = []
        self.race = ""
        self.realm = RPG_REALM_NEUTRAL
        self.rename = 0
        self.status = ""
    
        
        if char:
            if char.dead:
                self.status = "Dead"
            else:
                self.status = "Alive"
                
            self.name = char.name
            self.race = char.spawn.race
            self.realm = char.spawn.realm
            self.klasses.append(char.spawn.pclassInternal)
            self.levels.append(char.spawn.plevel)
            if char.spawn.sclassInternal:
                self.klasses.append(char.spawn.sclassInternal)
                self.levels.append(char.spawn.slevel)
            if char.spawn.tclassInternal:
                self.klasses.append(char.spawn.tclassInternal)
                self.levels.append(char.spawn.tlevel)
            
        
pb.setUnjellyableForClass(CharacterInfo, CharacterInfo) 

class ZoneConnectionInfo(pb.Copyable,pb.RemoteCopy):
    def __init__(self):     
        self.ip = ""
        self.port = 0
        self.password = ""
        self.niceName = ""
        self.missionFile = ""
        self.instanceName = ""
        self.playerZoneConnectPassword=""
        
pb.setUnjellyableForClass(ZoneConnectionInfo, ZoneConnectionInfo) 


class ZoneOption(pb.Copyable,pb.RemoteCopy):
    def __init__(self):
        self.zoneName = ""
        self.zoneInstanceName = ""
        self.owner = ""
        self.numPlayers = 0
        self.hasPassword = False
        self.status = "Live"
        
        
pb.setUnjellyableForClass(ZoneOption, ZoneOption) 


class WeatherConditions(pb.Copyable,pb.RemoteCopy):
    def __init__(self):
        self.cloudCover = 0
        self.precip = 0
        self.lightning = 0
        
        
pb.setUnjellyableForClass(WeatherConditions, WeatherConditions) 





# -------------------------------------------------------------
# SpawnInfo Jelly pair


class SpawnInfo(pb.Cacheable):
    def __init__(self):
        self.observers = []
        self.state = None
    
    
    def stoppedObserving(self, perspective, observer):
        #if observer in self.observers:
        self.observers.remove(observer)
    
    
    def getFullState(self):
        try:
            self.state = state = {}
            state["name"] = self.name
            state["modelname"] = self.modelname
            state["radius"] = self.radius
            state["scale"] = self.scale
            state["animation"] = self.animation
            state["textureSingle"] = self.textureSingle
            state["textureBody"] = self.textureBody
            state["textureHead"] = self.textureHead
            state["textureLegs"] = self.textureLegs
            state["textureHands"] = self.textureHands
            state["textureFeet"] = self.textureFeet
            state["textureArms"] = self.textureArms
            state["realm"] = self.realm
            state["sex"] = self.sex
            state["race"] = self.race
            return state
        except:
            traceback.print_exc()
    
    
    def getStateToCacheAndObserveFor(self, perspective, observer):
        self.observers.append(observer)
        if not self.state:
            self.getFullState()
        return self.state
    
    
    def refresh(self):
        try:
            if not self.state:
                self.getFullState()
            
            state = self.state
            changed = {}
            
            if state["name"] != self.name:
                changed["name"] = state["name"] = self.name
            
            if state["modelname"] != self.modelname:
                state["modelname"] = changed["modelname"] = self.modelname
            
            if state["radius"] != self.radius:
                state["radius"] = changed["radius"] = self.radius
            
            if state["scale"] != self.scale:
                state["scale"] = changed["scale"] = self.scale
            
            if state["animation"] != self.animation:
                state["animation"] = changed["animation"] = self.animation
            
            if state["textureSingle"] != self.textureSingle:
                state["textureSingle"] = changed["textureSingle"] = self.textureSingle
            
            if state["textureBody"] != self.textureBody:
                state["textureBody"] = changed["textureBody"] = self.textureBody
            
            if state["textureHead"] != self.textureHead:
                state["textureHead"] = changed["textureHead"] = self.textureHead
            
            if state["textureLegs"] != self.textureLegs:
                state["textureLegs"] = changed["textureLegs"] = self.textureLegs
            
            if state["textureHands"] != self.textureHands:
                state["textureHands"] = changed["textureHands"] = self.textureHands
            
            if state["textureFeet"] != self.textureFeet:
                state["textureFeet"] = changed["textureFeet"] = self.textureFeet
            
            if state["textureArms"] != self.textureArms:
                state["textureArms"] = changed["textureArms"] = self.textureArms
            
            if state["realm"] != self.realm:
                state["realm"] = changed["realm"] = self.realm
            
            if state["sex"] != self.sex:
                state["sex"] = changed["sex"] = self.sex
            
            if state["race"] != self.race:
                state["race"] = changed["race"] = self.race
            
            if len(changed):
                for o in self.observers: o.callRemote('updateChanged', changed)
        except:
            traceback.print_exc()



class SpawnInfoGhost(pb.RemoteCache):
    def __init__(self):
        self.look = 0
        self.dirty = True
    
    
    def setCopyableState(self, state):
        self.dirty = True
        self.__dict__.update(state)
    
    
    def observe_updateChanged(self,changed):
        self.dirty = True
        try:
            self.__dict__.update(changed)
            
            if changed.get('race',None) in RPG_PC_RACES:
                self.textureSingle = ""
                self.textureBody = ""
                self.textureHead = ""
                self.textureLegs = ""
                self.textureHands = ""
                self.textureFeet = ""
                self.textureArms = ""
            
            from mud.simulation.simmind import SIMMIND
            SIMMIND.updateSpawnInfo(self)
        except:
            traceback.print_exc()



pb.setUnjellyableForClass(SpawnInfo, SpawnInfoGhost) 

class RaceGraphicInfo(pb.Copyable,pb.RemoteCopy):
    def __init__(self,rg=None):
        
        self.name = ""
    
        self.model_fit_male = ""
        self.model_heavy_male = ""
        self.model_thin_male = ""
        
        self.model_fit_female = ""
        self.model_heavy_female = ""
        self.model_thin_female = ""
        
        self.animation_male = ""
        self.animation_female = ""
        
        self.texture_head_male = ""
        self.texture_body_male = ""
        self.texture_arms_male = ""
        self.texture_legs_male = ""
        self.texture_hands_male = ""
        self.texture_feet_male = ""
        self.texture_special_male = ""
    
        self.texture_head_female = ""
        self.texture_body_female = ""
        self.texture_arms_female = ""
        self.texture_legs_female = ""
        self.texture_hands_female = ""
        self.texture_feet_female = ""
        self.texture_special_female = ""
        
        self.size_male = ""
        self.size_female = ""
        
        self.hmount_fit_male = ""
        self.hmount_heavy_male = ""
        self.hmount_thin_male = ""
    
        self.hmount_fit_female = ""
        self.hmount_heavy_female = ""
        self.hmount_thin_female = ""
        
        if rg:
            
            self.name = rg.name
        
            self.model_fit_male = rg.model_fit_male
            self.model_heavy_male = rg.model_heavy_male
            self.model_thin_male = rg.model_thin_male
            
            self.model_fit_female = rg.model_fit_female
            self.model_heavy_female = rg.model_heavy_female
            self.model_thin_female = rg.model_thin_female
            
            self.animation_male = rg.animation_male
            self.animation_female = rg.animation_female
            
            self.texture_head_male = rg.texture_head_male
            self.texture_body_male = rg.texture_body_male
            self.texture_arms_male = rg.texture_arms_male
            self.texture_legs_male = rg.texture_legs_male
            self.texture_hands_male = rg.texture_hands_male
            self.texture_feet_male = rg.texture_feet_male
            self.texture_special_male = rg.texture_special_male
        
            self.texture_head_female = rg.texture_head_female
            self.texture_body_female = rg.texture_body_female
            self.texture_arms_female = rg.texture_arms_female
            self.texture_legs_female = rg.texture_legs_female
            self.texture_hands_female = rg.texture_hands_female
            self.texture_feet_female = rg.texture_feet_female
            self.texture_special_female = rg.texture_special_female
            
            self.size_male = rg.size_male
            self.size_female = rg.size_female
                        
            self.hmount_fit_male = rg.hmount_fit_male
            self.hmount_heavy_male = rg.hmount_heavy_male
            self.hmount_thin_male = rg.hmount_thin_male
        
            self.hmount_fit_female = rg.hmount_fit_female
            self.hmount_heavy_female = rg.hmount_heavy_female
            self.hmount_thin_female = rg.hmount_thin_female
    
    
    
pb.setUnjellyableForClass(RaceGraphicInfo, RaceGraphicInfo) 

