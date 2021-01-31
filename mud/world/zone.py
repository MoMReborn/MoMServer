# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from twisted.internet import reactor

from mud.common.persistent import Persistent
from mud.world.core import *
from mud.world.defines import *
from mud.world.mob import Mob
from mud.world.spawn import Spawnpoint
from mud.world.spell import Spell
from mud.world.weather import Weather

from copy import copy
from itertools import repeat
from random import choice
from sqlobject import *
import string
from time import time as sysTime
import traceback



def GenPasswd(length=8, chars=string.letters + string.digits):
    return ''.join([choice(chars) for i in xrange(length)])


#--- Updated 9/19/07 by BellyFish
#---    Modified code in 'def Tick()'
#---    PURPOSE:
#---    Additions and modifications to enable spawning mobs based on
#---    the Day of the Year.


class ZoneInstance:
    instanceCounter = 0
    def __init__(self, zone, ip, port, zonepassword, owningPlayer):
        self.zone = zone
        self.name = "%s_INSTANCE_%i"%(zone.name,ZoneInstance.instanceCounter)
        self.xpMod = zone.xpMod
        ZoneInstance.instanceCounter += 1
        
        self.status = "Launching"
        
        self.dedicated = not owningPlayer
        self.owningPlayer = owningPlayer
        
        self.ip = ip
        self.port = port
        self.password = zonepassword
        
        self.time = None
        
        self.simAvatar = None
    
        self.players = []
        #simObject -> mob
        self.mobLookup = {}
        self.spawnpoints = None
        self.live = False
        
        self.activeMobs = []
        self.spawnedMobs = []
        
        #queued players, which have been submitted before zone went live
        self.playerQueue = {}
        #publicName -> password (temporary zone connection passwords)
        self.playerPasswords = {}
        
        self.tickRootInfo = None
        #self.charInfoTick()
        self.rootInfoTick()
        
        self.weather = Weather(self.zone)
        
        #tuples of (x,y,z)
        self.bindpoints = []
        
        self.projectiles = {}
        
        self.dialogTriggers = []
        
        self.dynamic = False
        self.timeOut = -1
        self.stopped = False
        
        self.spawnpoints =[]
        
        self.battles = []
        
        self.paused = False
        
        self.charTickCounter = 4
        
        self.pid = None
        self.populatorGroups = {}
        
        self.spawnIndex = 0
        self.allSpawnsTicked = False
        self.launchQue = [] 
        self.tickLaunchProjectile = None 
    
    
    def failure(self,error):
        print error
    
    
    #THE PLAYER IS OFFICIALLY IN THE ZONE AT THIS POINT... whew
    def playerEnterZone(self,player):
        
        if not player.world:
            print "WARNING: Player Entering Zone not attached to world... probably lost connection to world while zoning in"
            return
        
        player.zone.simAvatar.setDisplayName(player)
        
        # announce to other players
        if player.role.name not in ("Guardian","Immortal"):
            if player.enteringWorld:
                for p in self.players:
                    p.sendGameText(RPG_MSG_GAME_BLUE, \
                        r'%s has entered the zone.\n'%player.charName)
                for p in player.world.activePlayers:
                    if p == player:
                        continue
                    if p.enteringWorld:
                        continue
                    if p in self.players: #already told that we entered zone
                        continue
                    p.sendGameText(RPG_MSG_GAME_BLUE, \
                        r'%s has entered the world.\n'%player.charName)
            else:
                pmob = player.curChar.mob
                for p in self.players:
                    if AllowHarmful(pmob,p.curChar.mob):
                        continue
                    p.sendGameText(RPG_MSG_GAME_BLUE, \
                        r'%s has entered the zone.\n'%player.charName)
                       
        # If the player was logging in and not zoning, we still need to reset 
        #  the flag denoting him/her entering the world.
        player.enteringWorld = False 

        #we use queue to keep dynamic zones alive
        try:
            del self.playerQueue[player]
        except KeyError:
            pass
        
        # Check if encounter setting will be preserved or not
        #  yeah, 5 minutes are long, this is just to make sure ...
        if sysTime() - player.encounterPreserveTimer < 300:
            player.mind.callRemote("checkEncounterSetting", True)
        player.encounterPreserveTimer = 0
        player.encounterSetting = RPG_ENCOUNTER_PVE  # go safe until required otherwise
        
        self.players.append(player)
        
        for c in player.party.members:
            # Get a handle to this Character's Mob.
            mob = c.mob
            # Add the Mob to the Mob lookup table. Even if the player
            #  has multiple Characters in the party, there will be only
            #  one lookup table entry.
            self.mobLookup[player.simObject] = mob
            # Set the Mob's simulation object.
            mob.simObject = player.simObject
            # Append this Mob to this Zone's list of active Mobs.
            self.activeMobs.append(mob)
            
            # If the Character zoned in dead, detach the Mob again.
            if c.dead:
                self.detachMob(mob)
        
        # If this world doesn't allow more than a single party member,
        #  then set the death marker of the zoned in Player.
        if CoreSettings.MAXPARTY == 1:
            player.world.setDeathMarker(player,player.party.members[0])
        
        if CoreSettings.PGSERVER:
            player.world.sendCharacterInfo(player)
    
    
    def connectPlayer(self,result,player,zconnect):
        #XXX fixme, we are passing the avatar name (fantasyName) here to client
        #and client is responsible for passing this to simulation zone
        #client shouldn't be responsible for this... 
        player.mind.callRemote("connect",zconnect,player.fantasyName)
    
    
    def connectQueuedPlayers(self, result):
        for p,z in self.playerQueue.iteritems():
            self.connectPlayer(None,p,z)
        self.playerQueue.clear()
    
    
    def submitPlayer(self, player, zconnect):
        player.zone = self
        pw = GenPasswd()
        self.playerPasswords[player.publicName] = pw
        zconnect.playerZoneConnectPassword = pw
        self.playerQueue[player] = zconnect
        if not self.live:
            if zconnect.ip == '127.0.0.1' and CoreSettings.SINGLEPLAYER:
                #tell client to kick off zone
                from race import GetRaceGraphics
                zconnect.raceGraphics = GetRaceGraphics()
                player.mind.callRemote('createServer',zconnect)
        else:
            d = self.simAvatar.setPlayerPasswords(self.playerPasswords)
            #only connect once player passwords are set
            d.addCallback(self.connectPlayer,player,zconnect)
    
    
    def start(self):
        if not self.simAvatar:
            traceback.print_stack()
            print "AssertionError: simAvatar doesn't exist!"
            return
        self.live = True
        d = self.simAvatar.setPlayerPasswords(self.playerPasswords)
        d.addCallback(self.connectQueuedPlayers)
    
    
    def stop(self):
        if self.stopped:
            return
        self.stopped = True
        
        print "Stopping Zone"
        self.weather.cancel()
        
        try:
            self.tickRootInfo.cancel()
        except:
            pass
            
        try: 
            self.tickLaunchProjectile.cancel() 
        except: 
            pass 
            
        map(self.removeMob,list(mob for mob in self.activeMobs if not mob.master))
        
        self.simAvatar.stop()
    
    
    def createSpawnpoints(self, spinfos):
        self.spawnpoints = [Spawnpoint(self,si.transform,si.group, \
            si.wanderGroup) for si in spinfos]
    
    
    def mobBotSpawned(self,simObject,mob):
        self.mobLookup[simObject] = mob
        mob.simObject = simObject
        self.activeMobs.append(mob)
        self.spawnedMobs.remove(mob)
        mob.spawned()
    
    
    def spawnMob(self,spawn,transform,wanderGroup,master = None,sizemod = 1.0):
        #create a bot
        mob = Mob(spawn,self,None,None,master,sizemod)
        self.spawnedMobs.append(mob)
        self.simAvatar.spawnBot(spawn,transform,wanderGroup,mob.mobInfo).addCallback(self.mobBotSpawned,mob)
        self.world.cpuSpawn-=1
        return mob
    
    
    def tick(self,spawnZone=None):
        self.charTickCounter -= 1
        
        try:
            if self.world.paused:
                if not self.paused:
                    self.paused = True
                    self.simAvatar.pause(True)
                if not self.charTickCounter:
                    self.charTickCounter = 5
                return
            elif self.paused:
                self.simAvatar.pause(False)
                self.paused = False
            
            if not self.allSpawnsTicked and self.spawnpoints and len(self.spawnpoints):
                self.world.cpuSpawn = 1000000
                self.world.cpuDespawn = 1000000
                self.allSpawnsTicked = True
                for s in self.spawnpoints:
                    try:
                        s.tick()
                    except:
                        traceback.print_exc()
                self.world.cpuSpawn = 0
                self.world.cpuDespawn = 0
            
            if spawnZone == self and self.allSpawnsTicked:
                if self.spawnpoints and len(self.spawnpoints) > 0:
                    start = self.spawnIndex
                    while self.world.cpuSpawn > 0 and self.world.cpuDespawn > 0:
                        s = self.spawnpoints[self.spawnIndex]
                        
                        go = True
                        if len(s.activeMobs) and s.activeInfo:
    #following line modified by BellyFish for Seasonal NPC's
                            if (s.activeInfo.startTime == -1 or s.activeInfo.endTime == -1) and (s.activeInfo.startDayRL == "" or s.activeInfo.endDayRL == ""):

                                go = False
                        if go:
                            try:
                                s.tick()
                            except:
                                traceback.print_exc()
                        
                        self.spawnIndex += 1
                        if self.spawnIndex == len(self.spawnpoints):
                            self.spawnIndex = 0
                        if start == self.spawnIndex:
                            break
            
            for mob in self.mobLookup.itervalues():
                if mob.detached and mob.kingTimer > 0:
                    mob.kingTimer -= 3
            
            # If we parse the list in reversed order,
            #  no need to copy to prevent problems
            #  while removing items during loop.
            # battle.tick() may remove battles from the list.
            for b in reversed(self.battles):
                b.tick()
            
            if len(self.players):
                # If we parse the list in reversed order,
                #  no need to copy to prevent problems
                #  while removing items during loop.
                # mob.tick() may remove mobs from the list.
                for mob in reversed(self.activeMobs):
                    try:
                        if not mob.detached and not mob.simObject.simZombie:
                            mob.tick()
                    except:
                        traceback.print_exc()
            
            if self.weather.dirty and self.simAvatar:
                self.simAvatar.sendWeather(self.weather)
                self.weather.dirty = False
            
            for p in self.players:
                try:
                    p.tick()
                    dirty = p.cinfoDirty
                    if not self.charTickCounter:
                        if not p.party or not p.party.members or not len(p.party.members):
                            continue
                        for c in p.party.members:
                            if dirty:
                                c.charInfo.refresh()
                            else:
                                c.charInfo.refreshLite(True)
                except:
                    traceback.print_exc()
        
        except:
            traceback.print_exc()
        
        if not self.charTickCounter:
            self.charTickCounter = 5
    
    
    def rootInfoTick(self):
        for p in self.players:
            try:
                if p.rootInfo:
                    p.rootInfo.tick()
            except:
                traceback.print_exc()
        
        self.tickRootInfo = reactor.callLater(0.5,self.rootInfoTick)
    
    
    def setTarget(self, mob, target, checkVisibility=False):
        ''' setTarget: Sets a mob's target for zone and simulation. '''
        
        # If there is a target and the target is detached, clear target.
        if target and target.detached:
            target = None
            
        # If the target is already targeted, return early.
        if target == mob.target:
            return
            
        # If there a target.
        if target:
            
            # If the targeter is deatched, do not target.
            if mob.detached:
                return
            
            # If the targeter is a player or player pet, and the target
            # is not visisble to the mob, return early.
            if checkVisibility and (mob.player or (mob.master and mob.master.player)) and not IsVisible(mob, target):
                return
        
        mob.setTarget(target)
        
        # Tell simulation side for pathfinding.
        if not mob.player:
            if target:
                self.simAvatar.setTarget(mob.simObject,target.simObject)
            else:                
                if mob.detached:
                    self.simAvatar.immobilize(mob.simObject)
                else:
                    # When a mob's target is cleared, it will go its spawnlocation.
                    self.simAvatar.clearTarget(mob.simObject)
                    
        else:
            for index,c in enumerate(mob.player.party.members):
                if c.mob == mob:
                    break
            if target:
                self.simAvatar.mind.callRemote("setSelection",mob.simObject.id,target.simObject.id,index)
            else:
                self.simAvatar.mind.callRemote("setSelection",mob.simObject.id,0,index)
    
    
    def setFollowTarget(self,mob,target):
        if mob.player:
            return #nope!
        
        if target:
            if mob.detached:
                return
            if target.detached:
                target = None
        
        mob.setFollowTarget(target)
        
        #tell simulation side for pathfinding
        if target:
            self.simAvatar.setFollowTarget(mob.simObject,target.simObject)
        else:
            self.simAvatar.setFollowTarget(mob.simObject,None)
    
    
    def setTargetById(self,mob,mobId):
        if mob.detached:
            return
        if mobId == 0:
            self.setTarget(mob,None)
        for m in self.activeMobs:
            if mobId == m.id:
                self.setTarget(mob,m)
                break
    
    
    #player gui selecting
    def select(self,srcSimObject,tgtSimObject,charIndex,doubleClick,modifier_shift):
        # modifier_shift reserved for mob/character info window
        mob = self.mobLookup[srcSimObject]
        player = mob.player
        if not player:
            traceback.print_stack()
            print "AssertionError: mob is no player mob!"
            return
        mob = player.party.members[charIndex].mob
        
        if mob.detached:
            player.sendGameText(RPG_MSG_GAME_DENIED,r'%s is no longer of this world and cannot interact with it.\n'%mob.name)
        
        target = self.mobLookup[tgtSimObject]
        
        if modifier_shift:
            player.avatar.sendTgtDesc(mob,target)
            return
        
        if target.detached and not target.player:
            try:
                if target.kingKiller and target.kingTimer > 0:
                    cmobs = [m.mob for m in target.kingKiller.player.party.members]
                    
                    for a in target.kingKiller.player.alliance.members:
                        for m in a.party.members:
                            cmobs.append(m.mob)
                    
                    if mob not in cmobs:
                        player.sendGameText(RPG_MSG_GAME_LOOT,r'You cannot loot this corpse at this time.\n')
                        return
            except:
                traceback.print_exc()
            
            #monsters get flesh and blood, bad place for this
            
            if target.genLoot and target.loot:
                target.genLoot = False
                if not target.loot.generateCorpseLoot():
                    target.loot = None
            
            if player.realm == RPG_REALM_MONSTER and \
                target.spawn.race not in ("Undead","Golem"):
                if target.loot and not target.loot.fleshDone and \
                    len(target.loot.items) < 16:
                    from item import ItemProto
                    fproto = ItemProto.byName("Flesh and Blood")
                    flesh = fproto.createInstance()
                    flesh.slot = -1
                    target.loot.items.append(flesh)
                    target.loot.fleshDone = True
            
            #currently the only reason mobs get detached is due to death
            if not target.loot or not len(target.loot.items):
                if target.loot:
                    target.loot.giveMoney(player)
                player.sendGameText(RPG_MSG_GAME_LOOT,r'The corpse crumbles to dust!\n')
                self.removeMob(target)
                return
            if target.master and target.master.player:
                player.sendGameText(RPG_MSG_GAME_LOOT,r'You cannot loot player pets.\n')
                return
            if target.looter and target.looter != mob.player:
                player.sendGameText(RPG_MSG_GAME_LOOT,r'%s is already looting the corpse.\n'%target.looter.curChar.name)
                return
            elif target.looter == player:
                return #no reloot
            
            #end current looting
            if player.looting:
                player.looting.looter = None
                player.looting = None
            
            #loot!
            target.looter = player
            player.looting = target
            loot = dict((x,item.itemInfo) for x,item in enumerate(target.loot.items))
            
            target.loot.giveMoney(player)
            
            player.mind.callRemote("setLoot",loot)
            
            return False
        
        if target.player:
            #find first attached party member
            for c in target.player.party.members:
                if not c.dead:
                    target = c.mob
                    break
        
        self.setTarget(mob,target, checkVisibility = True)
        if doubleClick:
            #holy cow
            player.avatar.perspective_doCommand("INTERACT",[mob.player.curChar.mob.charIndex])
        #send player mob's id for mouse link
        player.mind.callRemote("mouseSelect",charIndex,target.id)
        return True
    
    
    #mob reattaching (player death and rebirth)
    def reattachMob(self,mob):
        if not mob.detached:
            traceback.print_stack()
            print "AssertionError: mob is not detached!"
            return
        mob.detached = False
        if mob.character:
            # Persistent spells, needed for invulnerability and maybe future stuff.
            for store in mob.character.spellStore:
                if not mob.character.dead:
                    restoreSpell = Spell(mob,mob,store.spellProto,store.mod,store.time,None,False,True,store.level)
                    restoreSpell.healMod = store.healMod
                    restoreSpell.damageMod = store.damageMod
                    mob.processesPending.add(restoreSpell)
                store.destroySelf()
        self.activeMobs.append(mob)
    
    
    #mob detaching
    def detachMob(self, mob):
        if mob.detached:
            return
        
        mob.detachSelf()
        
        try:
            self.activeMobs.remove(mob)
        except ValueError:
            pass
        
        map(Mob.detachMob,self.activeMobs,repeat(mob,len(self.activeMobs)))
        
        if mob.interacting:
            mob.interacting.endInteraction()
        
        self.setTarget(mob,None)
        
        if not mob.player:
            mob.setFollowTarget(None)
            if not self.stopped:
                self.simAvatar.setFollowTarget(mob.simObject,None)
    
    
    #mob removal
    def removeMob(self, mob, despawnTime=0):
        if mob.master and mob.master.player:
            mob.master.character.petHealthBackup = mob.health
            mob.master.character.petHealthTimer = int(sysTime())
        
        if mob.corpseRemoval:
            mob.corpseRemoval.cancel()
            mob.corpseRemoval = None
        
        if mob.spawnpoint:
            mob.spawnpoint.removeMob(despawnTime)
        
        mob.kingKiller = None
        
        if not mob.detached:
            self.detachMob(mob)
        
        if mob.looter:
            mob.looter.looting = None
            try:
                mob.looter.mind.callRemote("setLoot",{})
            except:
                pass
        
        if mob.loot:
            mob.loot.mob = None
            for item in mob.loot.items:
                item.destroySelf()
        
        if not mob.player:
            try:
                self.simAvatar.deleteObject(mob.simObject)
            except:
                pass
            try:
                del self.mobLookup[mob.simObject]
            except KeyError:
                pass
        
        mob.simObject = None
        self.world.cpuDespawn -= 1
    
    
    def removePlayer(self,player):
        #todo, fixup for queued but not in zone, etc
        if player in self.players:
            self.players.remove(player)
        
        for c in player.party.members:
            try:
                del self.mobLookup[c.mob.simObject]
            except KeyError:
                pass
            
            self.detachMob(c.mob)
            self.removeMob(c.mob)
            
            c.mob.character = None
            c.mob.player = None
            c.mob = None
        
        if self.simAvatar:
            self.simAvatar.removePlayer(player.simObject)
        
        player.simObject = None
    
    
    def playerRespawned(self,result,args):
        player = args[0]
        for c in player.party.members:
            if not c.dead and c.mob.detached:
                self.reattachMob(c.mob)
    
    
    def respawnPlayer(self,player,transform=None):
        # Clean up still active player mobs before teleporting.
        for char in player.party.members:
            mob = char.mob
            if not mob.detached:
                if mob.interacting:
                    mob.interacting.endInteraction()
                for otherMob in self.activeMobs:
                    if otherMob.followTarget == mob and otherMob.master != mob:
                        self.setFollowTarget(otherMob,None)
        self.simAvatar.respawnPlayer(player,transform).addCallback(self.playerRespawned,(player,))
    
    
    def projectileCollision(self,pid,hitObj,hitPos):
        if self.mobLookup.has_key(hitObj):
            proj = self.projectiles[pid]
            proj.dst = self.mobLookup[hitObj]
            proj.onCollision(hitPos)
            
    def onImpact(self,simObject,velocity):
        mob = self.mobLookup.get(simObject,None)
        if mob:
            if not mob.player: #only players
                return
            if mob.player:
                for c in mob.player.party.members:
                    c.mob.onImpact(velocity)
                
            
        
            
        #del self.projectiles[pid] (will be called on simserver projectile delete)
    def deleteProjectile(self,pid):
        del self.projectiles[pid]
        
    def launchProjectile(self,p): 
        self.projectiles[p.id]=p 
        # Add the arrow the the launch queue 
        self.launchQue.append(p) 
        # Delay the launch of the projectile 1 second to allow for the bow animation 
        self.tickLaunchProjectile = reactor.callLater(1,self.launchProjectile_later) 
    
    def launchProjectile_later(self): 
        try: 
            p = self.launchQue.pop(0) 
        except: 
            return 
        self.simAvatar.launchProjectile(p)
    
    
    #dialog triggers
    def setDialogTriggers(self, tinfos):
        from dialog import DialogTrigger
        self.dialogTriggers = [DialogTrigger(t) for t in tinfos]
    
    
    def kickPlayer(self, player):
        self.simAvatar.kickPlayer(player)
    
    
    def setDeathMarker(self, publicName, charName, realm, pos, rot):
        self.simAvatar.setDeathMarker(publicName,charName,realm,pos,rot)
    
    
    def clearDeathMarker(self, publicName):
        self.simAvatar.clearDeathMarker(publicName)



class ZoneLink(Persistent):
    name = StringCol(alternateID = True) 
    dstZoneName = StringCol() 
    dstZoneTransform = StringCol() 

class TempZoneLink:
    def __init__(self,dstZoneName,dstZoneTransform):
        self.dstZoneName = dstZoneName
        self.dstZoneTransform = dstZoneTransform
    
        

class Zone(Persistent):
    name = StringCol(alternateID=True)
    niceName = StringCol()
    missionFile = StringCol()
    climate = IntCol(default = RPG_CLIMATE_TEMPERATE)
    xpMod = FloatCol(default=1.0)
    aggroMod = FloatCol(default = 1.0)
    scaleLimit = FloatCol(default=20.0)
    clusterId = IntCol(default=0)
    
    immTransform = StringCol(default="0 0 0 1 0 0 0")
    
    #add src and version info!
    #contentInfo = ForeignKey('ContentInfo')
    allowGuest = BoolCol(default=False)
    spawnGroups = MultipleJoin('SpawnGroup')
    world = ForeignKey('World')


