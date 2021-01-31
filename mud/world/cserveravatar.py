# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from twisted.spread import pb

from mud.gamesettings import GAMEROOT
from mud.common.permission import User,Role
from mud.world.defines import *
from mud.world.player import Player
from mud.world.zone import Zone
from mud.worldserver.charutil import ExtractPlayer,InstallCharacterBuffer, \
    InstallPlayerBuffer

from base64 import decodestring,encodestring
from cPickle import dumps,loads
from random import choice
from string import letters
from time import time as sysTime
import traceback



def GenPasswd(length=8, chars=letters):
    return ''.join([choice(chars) for i in xrange(length)])

AVATAR = None
#public name -> time of last extraction
EXTRACT_TIMES = {}

TICK_COUNTER = 6*15 #once every minute


class CharacterServerAvatar(pb.Root):
    def __init__(self):
        from mud.world.theworld import World
        
        global AVATAR
        self.world = World.byName("TheWorld")
        AVATAR = self
        self.mind = None
    
    
    def extractLoggingPlayer(player, save=True):
        if not AVATAR:
            return
        
        if save:
            if not player.party or not len(player.party.members):
                return
            
            from mud.worldserver.charutil import PLAYER_BUFFERS
            for pname,pbuffer,cbuffer,cvalues in PLAYER_BUFFERS[:]:
                if pname == player.publicName:
                    PLAYER_BUFFERS.remove((pname,pbuffer,cbuffer,cvalues))
            
            player.backupItems()
            publicName,pbuffer,cbuffer,cvalues = \
                ExtractPlayer(player.publicName,player.id, \
                    player.party.members[0].id,False)
            pbuffer = encodestring(dumps(pbuffer, 2))
            cbuffer = encodestring(dumps(cbuffer, 2))
            
            publicName = player.publicName
            player.destroySelf()
            try:
                user = User.byName(publicName)
                for r in user.roles:
                    r.removeUser(user)
                user.destroySelf()
            except:
                pass
            
            AVATAR.mind.callRemote("savePlayerBuffer",publicName,pbuffer, \
                cbuffer,cvalues,True)
        else:
            AVATAR.mind.callRemote("savePlayerBuffer",player.publicName,None, \
                None,None,True,False)
    
    extractLoggingPlayer = staticmethod(extractLoggingPlayer)
    
    
    def gotGlobalPlayers(self, results):
        players,muted = results
        AVATAR.world.globalPlayers = players
        AVATAR.world.mutedPlayers = muted
    
    
    def tick():    
            
        global TICK_COUNTER
        
        if not AVATAR:
            return #not official
        
        #error?
        if not AVATAR.mind:
            return 
        
        if AVATAR.world.shuttingDown:
            return
        
        try:

            now = sysTime()
            
            #ship off any player buffers from the last time
            
            try:
                from mud.worldserver.charutil import PLAYER_BUFFERS
                for pname,pbuffer,cbuffer,cvalues in PLAYER_BUFFERS[:]:
                    pbuf = encodestring(dumps(pbuffer, 2))
                    cbuf = None
                    if cbuffer:
                        cbuf = encodestring(dumps(cbuffer, 2))

                    print "Sending Player/Character buffers: %s (%ik/%ik)"%(pname,len(pbuf)/1024,len(cbuf)/1024)
                    AVATAR.mind.callRemote("savePlayerBuffer",pname,pbuf,cbuf,cvalues) #xxx add callback/errback
                    EXTRACT_TIMES[pname]=now
                    #should be removing these upon success
                    PLAYER_BUFFERS.remove((pname,pbuffer,cbuffer,cvalues))
            except:
                traceback.print_exc()
            
            
            TICK_COUNTER -= 3
            if TICK_COUNTER > 0:
                return
            
            TICK_COUNTER = 6 * 15 #once every minute
            
            pnames = []
            extractTarget = None
            best = 0
            for p in AVATAR.world.activePlayers:
                if not p.zone or p.enteringWorld:
                    continue
                
                pname = p.publicName
                pnames.append(pname)
                
                extractionTimer = EXTRACT_TIMES.setdefault(pname,now)
                t = now - extractionTimer
                
                if t < (60 * 10):
                    continue
                
                if t > best:
                    best = t
                    extractTarget = pname
            
            remove = []
            for k in EXTRACT_TIMES.iterkeys():
                if k not in pnames:
                    remove.append(k)
            map(EXTRACT_TIMES.__delitem__,remove)
            
            if extractTarget:
                p = Player.byPublicName(extractTarget) #already in active chars
                if p and p.party:
                    p.backupItems()
                    ExtractPlayer(p.publicName,p.id,p.party.members[0].id)
        except:
            traceback.print_exc()
        
        #send off all players
        
        try:
            pnames = []
            #it's still possible that the player is installed but isn't active
            #so 2 people sharing an account could still cause problems
            for p in AVATAR.world.activePlayers:
                cname = ""
                if p.curChar:
                    cname = p.curChar.name
                
                zname = ""
                if p.zone:
                    zname = p.zone.zone.niceName
                
                pnames.append((p.publicName,cname,p.guildName,zname))
            
            d = AVATAR.mind.callRemote("recordActivePlayers",AVATAR.world.multiName,pnames)
            d.addCallback(AVATAR.gotGlobalPlayers)
        
        except:
            traceback.print_exc()
            
        
        
    tick = staticmethod(tick)
        
    #this should probably be on the characterserver, somehow
    def createPlayer(self,publicName,code):
        #from newplayeravatar import NewPlayerAvatar
        #XXX if you change this function, also change it's mirror in cserveravatar!!!

                
        password = GenPasswd().upper()

        #move me
        zone = Zone.byName(self.world.startZone)
        dzone = Zone.byName(self.world.dstartZone)
        mzone = Zone.byName(self.world.mstartZone)
        
        t = zone.immTransform
        dt = dzone.immTransform
        mt = mzone.immTransform
        
        p = Player(publicName=publicName,password=password,fantasyName=publicName,logZone=zone,bindZone=zone,darknessLogZone=dzone,darknessBindZone=dzone,monsterLogZone=mzone,monsterBindZone=mzone)
        #temp
        
        p.logTransformInternal=t
        p.bindTransformInternal=t

        p.darknessLogTransformInternal=dt
        p.darknessBindTransformInternal=dt

        p.monsterLogTransformInternal=mt
        p.monsterBindTransformInternal=mt

        
        user = User(name=publicName,password=password)
        user.addRole(Role.byName("Player"))
        
        if code == 2: 
            user.addRole(Role.byName("Immortal"))
            user.addRole(Role.byName("Guardian"))
        elif code == 1:
            user.addRole(Role.byName("Guardian"))
            
            
        return p
        
        
    def installPlayerBuffer(self,buffer):
        InstallPlayerBuffer(buffer)
        
    def remote_transferPlayer(self,publicName,pbuffer,charname,cbuffer,code,premium,remoteLeaderName,guildInfo):
        
        #pbuffer = loads(decodestring(pbuffer))
        
        presults = self.remote_installPlayer(publicName,pbuffer,code,premium,guildInfo)
        if not presults[0]:
            #failure!
            return presults    
        
        player = Player.byPublicName(publicName)
        Player.remoteLeaderNames[publicName]=remoteLeaderName
        
        cbuffer = loads(decodestring(cbuffer))
        InstallCharacterBuffer(player.id,charname,cbuffer)
            
        return presults
        
        #self.enterWorld(party,simPort,simPassword)

    def remote_kickPlayer(self,publicName):
        try:
            player = Player.byPublicName(publicName)
        except:
            return
        
        try:
            world = player.world
            world.kickPlayer(player)
        except:
            traceback.print_exc()
            
    def gotContestLevelUp(self,result,player,levelType,level):
        if result:
            try:
                player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"\\nYou have been awarded a Halloween Raffle ticket for %s level %i!!!  You can view your current contest level matrix at: http://minions.prairiegames.com\\n"%(levelType,level))
            except:
                pass
                    
    def doContestLevelUp(self,player,levelType,level):
        d = self.mind.callRemote("contestLevelUpEvent",player.publicName,levelType,level)
        d.addCallback(self.gotContestLevelUp,player,levelType,level)
        

    def remote_installPlayer(self,publicName,buffer,code,premium,guildInfo):
        from mud.server.app import THESERVER
        
        if buffer:
            buffer = loads(decodestring(buffer))
        
        if not THESERVER.allowConnections:
            return (False,"This world is currently unavailable.  Please try again in a few minutes.")
        
        for p in self.world.activePlayers:
            if p.publicName == publicName:
                return (False,"Player already on world")
        
        #destroy player
        p = None
        try:
            p = Player.byPublicName(publicName)
        except:
            pass
        
        if p:
            #we must destroy this player (this should probably be changed to raw sql for speed)
            p.destroySelf()
            
        try:
            user = User.byName(publicName)
            for r in user.roles:
                r.removeUser(user)
            user.destroySelf()
        except:
            pass
            
        
        
        if buffer and buffer != "None":
            error = self.installPlayerBuffer(buffer)
            if error:
                return (False,"Error installing player buffer")
            
            try:
                p = Player.byPublicName(publicName)
                password = GenPasswd().upper()
                p.password = password
                user = User(name=publicName,password=password)
                user.addRole(Role.byName("Player"))
                
                if code == 2: 
                    user.addRole(Role.byName("Immortal"))
                    user.addRole(Role.byName("Guardian"))
                elif code == 1:
                    user.addRole(Role.byName("Guardian"))
                    
                
            except:
                traceback.print_exc()
                return (False,"Error setting up installed player")
                

        else:
            try:
                p = self.createPlayer(publicName,code)
            except:
                traceback.print_exc()
                return (False,"Error creating new player")
        
        p.premium = premium
        p.fantasyName = p.publicName #legacy
        
        p.guildName = guildInfo[0]
        p.guildInfo = guildInfo[1]
        p.guildMOTD = guildInfo[2]
        p.guildRank = guildInfo[3]
        return (True,p.password)


