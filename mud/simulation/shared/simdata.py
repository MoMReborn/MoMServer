# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



from twisted.spread import pb
from mud.world.defines import *
import traceback

#this will likely move, for now we are feeding spawnpoints off simulation server
class SpawnpointInfo(pb.Copyable,pb.RemoteCopy):
    def __init__(self):
        self.transform = [0,0,0,0,0,0,0]
        self.group = "easy"
    
pb.setUnjellyableForClass(SpawnpointInfo, SpawnpointInfo) 


class DialogTriggerInfo(pb.Copyable,pb.RemoteCopy):
    def __init__(self):
        self.position = (0,0,0)
        self.dialogTrigger = ""
        self.dialogRange = 0
    
pb.setUnjellyableForClass(DialogTriggerInfo, DialogTriggerInfo) 


#world -> simserver
#the bulk of the simulation state control for world mob-> simobject on simserver should 
#be changed to use this!
class SimMobInfo(pb.Cacheable):
    def __init__(self,mob):
        self.mob = mob
        self.state = {}
        self.observers = []
        
        self.state['NAME'] = mob.name
        self.state['ID'] = mob.id
        self.state['REALM'] = mob.realm
        self.state['MOVE'] = mob.move + mob.petSpeedMod
        self.state['SPEEDMOD'] = mob.speedMod * 8.0
        self.state['SIZE'] = mob.size
        self.state['SEEINVISIBLE'] = mob.seeInvisible
        self.state['VISIBILITY'] = mob.visibility
        if mob.attacking or mob.casting:
            self.state['VISIBILITY'] += 0.5
            if self.state['VISIBILITY'] > 1.0:
                self.state['VISIBILITY'] = 1.0
        self.state['AGGRORANGE'] = mob.spawn.aggroRange
        self.state['FEAR'] = mob.isFeared
        self.state['SLEEP'] = mob.sleep > 0 or mob.stun > 0
        self.state['FEIGNDEATH'] = mob.feignDeath
        self.state['DETACHED'] = mob.detached
        if mob.spawn.dialog and mob.spawn.dialog.greeting and mob.spawn.dialog.greeting.numChoices:
            self.state['VARNAME'] = "0" + mob.name
        elif mob.spawn.flags&RPG_SPAWN_UNIQUE or mob.spawn.name != mob.name:
            self.state['VARNAME'] = "1" + mob.name
        elif mob.spawn.difficultyMod > 1.0 or mob.spawn.damageMod > 1.0 or mob.spawn.healthMod > 1.0 or mob.spawn.defenseMod > 1.0 or mob.spawn.offenseMod > 1.0:
            self.state['VARNAME'] = "2%s %s"%(mob.variantName,mob.name)
        else:
            self.state['VARNAME'] = '%s %s'%(mob.variantName,mob.name)
            
        self.state['SEX'] = mob.sex
        self.state['ATTACKING'] = mob.attacking
        self.state['RANGEDATTACK'] = False
        self.state['ZOMBIE'] = mob.zombie
        self.state['TGTID'] = 0
        if mob.target:
            self.state['TGTID'] = mob.target.simObject.id
        
        
        self.state['PLAYERPET'] = False
        if not mob.player:
            self.state['WALK'] = mob.sneak
            self.state['ROLE'] = 'MOB'
            if mob.master and mob.master.player:
                masterPlayer = mob.master.player
                self.state['PLAYERPET'] = True
                self.state['VARNAME'] += "<%s>"%mob.master.name
                self.state['ENCOUNTERSETTING'] = masterPlayer.encounterSetting
                self.state['OVERRIDESCALE'] = False
                self.state['PRIMARYLEVEL'] = mob.master.level
                if masterPlayer.alliance and masterPlayer.alliance.leader:
                    self.state['ALLIANCELEADER'] = masterPlayer.alliance.leader.id
                else:
                    self.state['ALLIANCELEADER'] = masterPlayer.id
                self.state['GUILDNAME'] = masterPlayer.guildName
            else:
                self.state['ENCOUNTERSETTING'] = RPG_ENCOUNTER_PVE
                self.state['OVERRIDESCALE'] = False
                self.state['PRIMARYLEVEL'] = mob.level
                self.state['ALLIANCELEADER'] = 0
                self.state['GUILDNAME'] = ""
        else:
            player = mob.player
            self.state['WALK'] = mob.sneak or player.walk
            self.state['ROLE'] = player.avatar.masterPerspective.role.name
            self.state['ENCOUNTERSETTING'] = player.encounterSetting
            self.state['PRIMARYLEVEL'] = mob.level
            self.state['OVERRIDESCALE'] = player.overrideScale
            if player.alliance and player.alliance.leader:
                self.state['ALLIANCELEADER'] = player.alliance.leader.id
            else:
                self.state['ALLIANCELEADER'] = player.id
            self.state['GUILDNAME'] = player.guildName
        
        bestlight = mob.light
        for item in mob.worn.itervalues():
            if bestlight < item.light:
                bestlight = item.light
            
        self.state['LIGHT'] = bestlight
        
        self.state['FLYING'] = mob.flying
        
        
        try:
            self.state['MATBODY'] = mob.worn[RPG_SLOT_CHEST].material
        except KeyError:
            self.state['MATBODY'] = ""
        try:
            self.state['MATARMS'] = mob.worn[RPG_SLOT_ARMS].material
        except KeyError:
            self.state['MATARMS'] = ""
        try:
            self.state['MATFEET'] = mob.worn[RPG_SLOT_FEET].material
        except KeyError:
            self.state['MATFEET'] = ""
        try:
            self.state['MATHANDS'] = mob.worn[RPG_SLOT_HANDS].material
        except KeyError:
            self.state['MATHANDS'] = ""
        try:
            self.state['MATLEGS'] = mob.worn[RPG_SLOT_LEGS].material
        except KeyError:
            self.state['MATLEGS'] = ""
        
        shield = mob.worn.get(RPG_SLOT_SHIELD)
        if shield:
            self.state['MOUNT2'] = shield.model
            self.state['MOUNT2_MAT'] = shield.material
        else:
            self.state['MOUNT2'] = self.state['MOUNT2_MAT'] = ""
        
        headItem = mob.worn.get(RPG_SLOT_HEAD)
        if headItem:
            self.state['MOUNT3'] = headItem.model
            self.state['MOUNT3_MAT'] = headItem.material
        else:
            self.state['MOUNT3'] = self.state['MOUNT3_MAT'] = ""
        
        secondaryWeapon = mob.worn.get(RPG_SLOT_SECONDARY)
        if secondaryWeapon:
            self.state['MOUNT1'] = secondaryWeapon.model
            self.state['MOUNT1_MAT'] = secondaryWeapon.material
        else:
            self.state['MOUNT1'] = self.state['MOUNT1_MAT'] = ""
        
        self.state['TWOHANDED'] = False
        primaryWeapon = mob.worn.get(RPG_SLOT_PRIMARY)
        if primaryWeapon:
            self.state['MOUNT0'] = primaryWeapon.model
            self.state['MOUNT0_MAT'] = primaryWeapon.material
            if '2H' in primaryWeapon.skill and (not secondaryWeapon or not mob.skillLevels.get("Power Wield")):
                self.state['MOUNT1'] = self.state['MOUNT1_MAT'] = ""
                self.state['MOUNT2'] = self.state['MOUNT2_MAT'] = ""
                self.state['TWOHANDED'] = True
        else:
            self.state['MOUNT0'] = self.state['MOUNT0_MAT'] = ""
    
    
    def stoppedObserving(self, perspective, observer):
        #if observer in self.observers:
        self.observers.remove(observer)
    
    def getStateToCacheAndObserveFor(self, perspective, observer):
        self.observers.append(observer)
        mob = self.mob
        return self.state
    
    def refresh(self):
        try:
            mob = self.mob
            state = self.state
            changed = {}
            
            move = mob.move + mob.petSpeedMod
            speedMod = mob.speedMod * 8.0
            flying = mob.flying
            if mob.simObject:
                if mob.simObject.waterCoverage >= .45:
                    move = mob.swimMove
            
            size = mob.size
            
            # Clamp visibility at lower end.  World data can have
            # visibility of values lower than 0.
            visibility = mob.visibility
            if visibility < 0:
                visibility = 0
                
            # Modify visibility if the mob if it or its pet is attacking
            # or casting.
            pet = mob.pet
            if mob.attacking or mob.casting or (pet and (pet.attacking or pet.casting)):
                visibility += 0.5
            sleep = mob.sleep > 0 or mob.stun > 0
            seeinvisible = mob.seeInvisible
            fear = mob.isFeared
            
            feignDeath = mob.feignDeath
            
            if mob.master:
                if mob.realm != self.state['REALM']:  # pets get their realm changed during assignment
                    changed['REALM'] = state['REALM'] = mob.realm
            
            bestlight = mob.light
            for item in mob.worn.itervalues():
                if bestlight < item.light:
                    bestlight = item.light
            
            # Clamp
            if move < 0:
                move = 0
            elif move > 4:
                move = 4
            if speedMod < 0:
                speedMod = 0
            elif speedMod * move > 32:
                speedMod = 32 / move
            if size < .1:
                size = .1
            elif size > 3:
                size = 3
            if visibility < 0:
                visibility = 0
            elif visibility > 1:
                visibility = 1
            if seeinvisible < 0:
                seeinvisible = 0
            elif seeinvisible > 1:
                seeinvisible = 1
            if flying > 1:
                flying = 1
            elif flying < 0:
                flying = 0
            
            attacking = mob.attacking
            playerpet = False
            if mob.player:
                player = mob.player
                walk = mob.sneak or player.walk
                if mob.casting and mob.casting.spellProto.skillname != "Singing":
                    attacking = False
                encounterSetting = player.encounterSetting
                overrideScale = player.overrideScale
                primaryLevel = mob.level
                if player.alliance and player.alliance.leader:
                    allianceLeader = player.alliance.leader.id
                else:
                    allianceLeader = player.id
                guildName = player.guildName
            elif mob.master and mob.master.player:
                walk = mob.sneak
                playerpet = True
                petname = "%s %s<%s>"%(mob.variantName,mob.name,mob.master.name)
                if petname != state['VARNAME']:
                    changed['VARNAME'] = state['VARNAME'] = petname
                masterPlayer = mob.master.player
                encounterSetting = masterPlayer.encounterSetting
                overrideScale = False
                primaryLevel = mob.master.level
                if masterPlayer.alliance and masterPlayer.alliance.leader:
                    allianceLeader = masterPlayer.alliance.leader.id
                else:
                    allianceLeader = masterPlayer.id
                guildName = masterPlayer.guildName
            else:
                walk = mob.sneak
                # If we were previously charmed, need to check some additional stuff again.
                if state['PLAYERPET']:
                    if mob.spawn.dialog and mob.spawn.dialog.greeting and mob.spawn.dialog.greeting.numChoices:
                        varname = "0" + mob.name
                    elif mob.spawn.flags&RPG_SPAWN_UNIQUE or mob.spawn.name != mob.name:
                        varname = "1" + mob.name
                    elif mob.spawn.difficultyMod > 1.0 or mob.spawn.damageMod > 1.0 or mob.spawn.healthMod > 1.0:
                        varname = "2%s %s"%(mob.variantName,mob.name)
                    else:
                        varname = '%s %s'%(mob.variantName,mob.name)
                    if varname != state['VARNAME']:
                        changed['VARNAME'] = state['VARNAME'] = varname
                encounterSetting = RPG_ENCOUNTER_PVE
                overrideScale = False
                primaryLevel = mob.level
                allianceLeader = 0
                guildName = ""
            
            if encounterSetting != state['ENCOUNTERSETTING']:
                changed['ENCOUNTERSETTING'] = state['ENCOUNTERSETTING'] = encounterSetting
            if overrideScale != state['OVERRIDESCALE']:
                changed['OVERRIDESCALE'] = state['OVERRIDESCALE'] = overrideScale
            if primaryLevel != state['PRIMARYLEVEL']:
                changed['PRIMARYLEVEL'] = state['PRIMARYLEVEL'] = primaryLevel
            if allianceLeader != state['ALLIANCELEADER']:
                changed['ALLIANCELEADER'] = state['ALLIANCELEADER'] = allianceLeader
            if guildName != state['GUILDNAME']:
                changed['GUILDNAME'] = state['GUILDNAME'] = guildName
            
            if playerpet != state['PLAYERPET']:
                changed['PLAYERPET'] = state['PLAYERPET'] = playerpet
            
            if attacking != state['ATTACKING']:
                changed['ATTACKING'] = state['ATTACKING'] = attacking
            if mob.simObject:
                if mob.simObject.rangedAttack != state['RANGEDATTACK']:
                    changed['RANGEDATTACK'] = state['RANGEDATTACK'] = mob.simObject.rangedAttack
            
            if move != state['MOVE']:
                changed['MOVE'] = state['MOVE'] = move
            if speedMod != state['SPEEDMOD']:
                changed['SPEEDMOD'] = state['SPEEDMOD'] = speedMod
            if walk != state['WALK']:
                changed['WALK'] = state['WALK'] = walk
            
            if size != state['SIZE']:
                changed['SIZE'] = state['SIZE'] = size
            
            if visibility != state['VISIBILITY']:
                changed['VISIBILITY'] = state['VISIBILITY'] = visibility
            if seeinvisible != state['SEEINVISIBLE']:
                changed['SEEINVISIBLE'] = state['SEEINVISIBLE'] = seeinvisible
            
            if fear != state['FEAR']:
                changed['FEAR'] = state['FEAR'] = fear
            
            if bestlight != state['LIGHT']:
                changed['LIGHT'] = state['LIGHT'] = bestlight
            
            if sleep != state['SLEEP']:
                changed['SLEEP'] = state['SLEEP'] = sleep
            
            if flying != state['FLYING']:
                changed['FLYING'] = state['FLYING'] = flying
            
            if feignDeath != state['FEIGNDEATH']:
                changed['FEIGNDEATH'] = state['FEIGNDEATH'] = feignDeath
            
            if mob.detached != state['DETACHED']:
                changed['DETACHED'] = state['DETACHED'] = mob.detached
            
            if mob.zombie != state['ZOMBIE']:
                changed['ZOMBIE'] = state['ZOMBIE'] = mob.zombie
            
            if not mob.target and state['TGTID']:
                changed['TGTID'] = state['TGTID'] = 0
            elif mob.target:
                if mob.target.simObject.id != state['TGTID']:
                    state['TGTID'] = changed['TGTID'] = mob.target.simObject.id
            
            shield = mob.worn.get(RPG_SLOT_SHIELD)
            if shield:
                mount2 = shield.model
                mount2_material = shield.material
            else:
                mount2 = mount2_material = ""
            
            headItem = mob.worn.get(RPG_SLOT_HEAD)
            if headItem:
                mount3 = headItem.model
                mount3_material = headItem.material
            else:
                mount3 = mount3_material = ""
            
            twohanded = False
            ranged = mob.worn.get(RPG_SLOT_RANGED)
            if not state['RANGEDATTACK'] or not ranged:
                secondaryWeapon = mob.worn.get(RPG_SLOT_SECONDARY)
                if secondaryWeapon:
                    mount1 = secondaryWeapon.model
                    mount1_material = secondaryWeapon.material
                else:
                    mount1 = mount1_material = ""
                
                primaryWeapon = mob.worn.get(RPG_SLOT_PRIMARY)
                if primaryWeapon:
                    mount0 = primaryWeapon.model
                    mount0_material = primaryWeapon.material
                    if '2H' in primaryWeapon.skill and (not secondaryWeapon or not mob.skillLevels.get("Power Wield")):
                        mount1 = mount1_material = ""
                        mount2 = mount2_material = ""
                        twohanded = True
                else:
                    mount0 = mount0_material = ""
            else:
                mount0 = ranged.model
                mount0_material = ranged.material
                mount1 = mount1_material = ""
            
            if mount0 != state['MOUNT0']:
                changed['MOUNT0'] = state['MOUNT0'] = mount0
            if mount0_material != state['MOUNT0_MAT']:
                changed['MOUNT0_MAT'] = state['MOUNT0_MAT'] = mount0_material
            if mount1 != state['MOUNT1']:
                changed['MOUNT1'] = state['MOUNT1'] = mount1
            if mount1_material != state['MOUNT1_MAT']:
                changed['MOUNT1_MAT'] = state['MOUNT1_MAT'] = mount1_material
            if mount2 != state['MOUNT2']:
                changed['MOUNT2'] = state['MOUNT2'] = mount2
            if mount2_material != state['MOUNT2_MAT']:
                changed['MOUNT2_MAT'] = state['MOUNT2_MAT'] = mount2_material
            if mount3 != state['MOUNT3']:
                changed['MOUNT3'] = state['MOUNT3'] = mount3
            if mount3_material != state['MOUNT3_MAT']:
                changed['MOUNT3_MAT'] = state['MOUNT3_MAT'] = mount3_material
            if twohanded != state['TWOHANDED']:
                changed['TWOHANDED'] = state['TWOHANDED'] = twohanded
            
            # Update materials
            try:
                mbody = mob.worn[RPG_SLOT_CHEST].material
            except KeyError:
                mbody = ""
            try:
                marms = mob.worn[RPG_SLOT_ARMS].material
            except KeyError:
                marms = ""
            try:
                mfeet = mob.worn[RPG_SLOT_FEET].material
            except KeyError:
                mfeet = ""
            try:
                mhands = mob.worn[RPG_SLOT_HANDS].material
            except KeyError:
                mhands = ""
            try:
                mlegs = mob.worn[RPG_SLOT_LEGS].material
            except KeyError:
                mlegs = ""
            if mbody != state['MATBODY']:
                changed['MATBODY'] = state['MATBODY'] = mbody
            if mfeet != state['MATFEET']:
                changed['MATFEET'] = state['MATFEET'] = mfeet
            if marms != state['MATARMS']:
                changed['MATARMS'] = state['MATARMS'] = marms
            if mlegs != state['MATLEGS']:
                changed['MATLEGS'] = state['MATLEGS'] = mlegs
            if mhands != state['MATHANDS']:
                changed['MATHANDS'] = state['MATHANDS'] = mhands
            
            if not len(changed):
                return
            
            for o in self.observers: o.callRemote('updateChanged', changed)
        except:
            traceback.print_exc()
            



class SimMobInfoGhost(pb.RemoteCache):
    def __init__(self):
        self.dirty = True
    
    
    def setCopyableState(self, state):
        self.dirty = True
        self.__dict__.update(state)
    
    
    def observe_updateChanged(self, changed):
        self.dirty = True
        self.__dict__.update(changed)



pb.setUnjellyableForClass(SimMobInfo, SimMobInfoGhost)

