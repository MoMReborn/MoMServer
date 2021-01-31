# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#EMBEDDED world server, yargh!

from time import time as currentTime
import traceback,sys,os
from tgenative import *
from mud.world.core import CoreSettings
from mud.gamesettings import *

from mud.tgepython.console import TGEExport

import mud.world.newplayeravatar
import mud.world.playeravatar
import mud.world.simavatar
from mud.world.theworld import World
from mud.world.zone import Zone
from mud.world.player import Player,PlayerXPCredit

from mud.common.avatar import RoleAvatar
from mud.common.permission import User,Role
from mud.common.dbconfig import SetDBConnection

WORLDSERVER = None
MANHOLE = None

def CreatePlayer():
    try:
        Player.byPublicName("ThePlayer")
    except:
        world = World.byName("TheWorld")
        
        #move me
        zone = Zone.byName(world.startZone)
        dzone = Zone.byName(world.dstartZone)
        mzone = Zone.byName(world.mstartZone)
        
        p = Player(publicName="ThePlayer",password="ThePlayer",fantasyName="ThePlayer",logZone=zone,bindZone=zone,darknessLogZone=dzone,darknessBindZone=dzone,
        monsterLogZone=mzone,monsterBindZone=mzone)

        #temp
        
        t = zone.immTransform
        dt = dzone.immTransform
        mt = mzone.immTransform
        
        p.logTransformInternal= t
        p.bindTransformInternal= t
        p.darknessLogTransformInternal= dt
        p.darknessBindTransformInternal= dt
        p.monsterLogTransformInternal= mt
        p.monsterBindTransformInternal= mt
        
        user = User(name="ThePlayer",password="ThePlayer")
        user.addRole(Role.byName("Player"))
        user.addRole(Role.byName("Immortal"))

def IDESetup():
    if not CoreSettings.IDE:
        return
    if CoreSettings.IDE_ZONE:
        z = Zone.byName(CoreSettings.IDE_ZONE)
        p = Player.byPublicName("ThePlayer")
        
        settransform = False
        if p.logZone != z or p.darknessLogZone != z or p.monsterLogZone != z:
            settransform = True
        p.logZone=z
        p.bindZone=z
        p.darknessLogZone=z
        p.darknessBindZone=z
        p.monsterLogZone=z
        p.monsterBindZone=z
        
        if settransform:
            t = z.immTransform
    
            p.logTransformInternal= t
            p.bindTransformInternal= t
            p.darknessLogTransformInternal= t
            p.darknessBindTransformInternal= t
            p.monsterLogTransformInternal= t
            p.monsterBindTransformInternal= t


def ShutdownEmbeddedWorld():
    global WORLDSERVER,MANHOLE
    if not WORLDSERVER:
        return
    
    world = World.byName("TheWorld")
    world.shutdown()
    WORLDSERVER.shutdown()
    WORLDSERVER = None
    
    if MANHOLE:
        MANHOLE.stopListening()
    
    MANHOLE = None
    SetDBConnection(None)


# Create a single player world
def SetupEmbeddedWorld(worldname):
    global WORLDSERVER
    global MANHOLE
    
    DATABASE = "sqlite:///%s/%s/data/worlds/singleplayer/%s/world.db"%(os.getcwd(),GAMEROOT,worldname)
    SetDBConnection(DATABASE,True)
    
    #destroy the new player user, and recreate
    try:
        user = User.byName("NewPlayer")
        user.destroySelf()
    except:
        pass
    
    CreatePlayer()
    IDESetup()
    
    #--- Application
    
    from twisted.spread import pb
    from twisted.internet import reactor
    from twisted.cred.credentials import UsernamePassword
    
    from mud.server.app import Server
    
    WORLDSERVER = server = Server(3013)
    server.startServices()
    
    #kickstart the heart
    world = World.byName("TheWorld")
    
    #TODO, single player backups
    #world.dbFile = os.getcwd()+"/minions.of.mirth/data/worlds/singleplayer/"+worldname+"/world.db"
    
    try:
        v = int(TGEGetGlobal("$pref::gameplay::difficulty"))
    except:
        v = 0
        TGESetGlobal("$pref::gameplay::difficulty",0)
    try:
        respawn = float(TGEGetGlobal("$pref::gameplay::monsterrespawn"))
    except:
        TGESetGlobal("$pref::gameplay::monsterrespawn",0.0)
        respawn = 0.0
    try:
        SPpopulators = int(TGEGetGlobal("$pref::gameplay::SPpopulators"))
    except:
        SPpopulators = 0
        TGESetGlobal("$pref::gameplay::SPpopulators",0)
    
    if v == 1:
        CoreSettings.DIFFICULTY = 0
    elif v == 2:
        CoreSettings.DIFFICULTY = 2
    else:
        CoreSettings.DIFFICULTY = 1
    
    CoreSettings.RESPAWNTIME = respawn
    CoreSettings.SPPOPULATORS = SPpopulators
    
    CoreSettings.SINGLEPLAYER = True
    world.launchTime = currentTime()
    world.singlePlayer = True
    
    world.startup()
    world.transactionTick()
    
    world.tick()
    
    #telnet access
    #import telnet
    
    #try:
    #    from manhole import MakeFactory
    #    ips = ["127.0.0.1"]
    #    f= MakeFactory(ips,"me","me")
    #    MANHOLE = reactor.listenTCP(22, f)
    #except:
    #    print "Warning: Couldn't create single player manhole"


