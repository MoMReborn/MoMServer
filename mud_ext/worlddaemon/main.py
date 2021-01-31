# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#world daemon, log into world server, tell it to shutdown in 10 minutes
#world kills all zones


import imp
import os
import sys

USE_WX = "-wx" in sys.argv

if sys.platform == 'win32' and not USE_WX:
    from twisted.internet.iocpreactor import install
else:
    USE_WX = True
    import wx
    from twisted.internet.wxreactor import install

install()

from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.cred.credentials import UsernamePassword
from twisted.cred.portal import IRealm,Portal
from twisted.internet import reactor
from twisted.python import components,failure,log
from twisted.spread import pb
from zope.interface import implements
from sqlite3 import dbapi2 as sqlite
from traceback import print_exc,print_stack

if USE_WX:
    from mud_ext.worlddaemon.gui import Setup
    app = Setup(reactor)
    reactor.registerWxApp(app)

from mud.gamesettings import *
from mud_ext.worlddaemon.charservices import \
    StartServices as startCharacterServices,CServerAvatar
from mud_ext.worlddaemon.gmservices import GMServices
from mud_ext.worlddaemon.telnetmanhole import MakeFactory
from mud_ext.worlddaemon.worldimp import StartServices as startImpServices
from mud_ext.worlddaemon.worldservices import \
    StartServices as startWorldServices,ZoneClusterAvatar

from math import ceil
from md5 import md5
from time import localtime,time as sysTime
import traceback
try:
    import win32api,win32con,win32event
except ImportError:
    win32api = win32con = win32event = None



ANNOUNCECALLBACK = None

#the first cluster is the announce server, where players will initially connect and should probably be low cpu usage

WORLDIMPS = {}

REMOTECLUSTERS = []

ZONECLUSTERS = []

WORLDNAME = None
PUBLICNAME = None
PASSWORD = None

GMCONNECTION = None



for arg in sys.argv:
    if arg.startswith('-worldname='):
        WORLDNAME = arg[11:]
    elif arg.startswith('-publicname='):
        PUBLICNAME = arg[12:]
    elif arg.startswith('-password='):
        PASSWORD = arg[10:]


if not WORLDNAME or not PUBLICNAME or PASSWORD is None:
    print "Usage: WorldDaemon -worldname=MYWORLD -publicname=MYPUBLICNAME -password=MYPASSWORD"
    raise "Incorrect Usage"



class BadConnectionError(Exception):
    def __str__(self):
        return "Bad Connection"



#military time!
REBOOT = True
REBOOT_HOUR = 3
REBOOT_MINUTE = 0
REBOOT_TIME = sysTime()
ANNOUNCE_MINUTE = -1

FORCEKILL_TIME = None

KILLED = False

SPAWNED = False

try:
    exec ("from serverconfig.%s import *" % WORLDNAME)
except:
    print "Error reading server configuration, %s" % WORLDNAME
    sys.exit(-1)

def AnnounceShutdownReboot():
    for z in ZONECLUSTERS:
        try:
            if REBOOT:
                z.mind.callRemote("announceReboot",ANNOUNCE_MINUTE)
            else:
                z.mind.callRemote("announceShutdown",ANNOUNCE_MINUTE)
        except:
            pass
        

def Tick():
    global REBOOT_TIME, ANNOUNCE_MINUTE,FORCEKILL_TIME,ANNOUNCECALLBACK,KILLED,REBOOT,SPAWNED,ZONECLUSTERS
    
    reactor.callLater(15,Tick)
    
    if KILLED:
        if not len(ZoneClusterAvatar.avatars):
            if not REBOOT:
                reactor.stop()
            else:
                print "Rebooting"
                KILLED = False
                SpawnWorld()
        return
    
    #are we live?
    if SPAWNED:
        if not ANNOUNCECALLBACK and len(ZONECLUSTERS)==len(CLUSTERNAMES):
            for z in ZONECLUSTERS:
                if not z.live:
                    break
            else:
                SPAWNED = False
                AnnounceWorld()
    
    if FORCEKILL_TIME != None:
        if ANNOUNCECALLBACK:
            ANNOUNCECALLBACK.cancel()
            ANNOUNCECALLBACK = None
            
        
        minutes = int(ceil((FORCEKILL_TIME - sysTime())/60.0))
        if minutes<=0:
            FORCEKILL_TIME = None
            ANNOUNCE_MINUTE = -1
            REBOOT_TIME = sysTime()
            
            KILLED = True
            CServerAvatar.worldCSAvatars = {}
            for z in ZONECLUSTERS:
                z.killWorld()
            ZONECLUSTERS = []

            
        else:
            if minutes < 11 and ANNOUNCE_MINUTE!=minutes:
                if REBOOT:
                    print "Reboot in %i minutes"%minutes
                else:
                    print "Shutdown in %i minutes"%minutes
                    
                ANNOUNCE_MINUTE = minutes
                
                AnnounceShutdownReboot()
                
            
        
    
    elif sysTime()-REBOOT_TIME > 60*60*2: #if we haven't rebooted within the last 2 hours

        #automated reboot
        lt =  localtime()
        hour,minute =  lt[3],lt[4]
        
        nm = hour*60+minute
        rm = REBOOT_HOUR*60+REBOOT_MINUTE
        
        minutes = 0
        
        if rm > nm:
            minutes = rm-nm
        elif rm < nm:
            minutes = 24*60 - (nm-rm)
        
        if minutes < 0:
            minutes = 0
                        
        if minutes and minutes < 11 and ANNOUNCE_MINUTE != minutes:
            print "Reboot in %i minutes"%minutes
            ANNOUNCE_MINUTE = minutes
            if ANNOUNCECALLBACK:
                ANNOUNCECALLBACK.cancel()
                ANNOUNCECALLBACK = None
            AnnounceShutdownReboot()
            
        
        if hour == REBOOT_HOUR and minute >= REBOOT_MINUTE:
            ANNOUNCE_MINUTE = -1
            REBOOT_TIME = sysTime()
            KILLED = True
            REBOOT = True
            CServerAvatar.worldCSAvatars = {}

            for z in ZONECLUSTERS:                
                z.killWorld()
            ZONECLUSTERS = []

    

def ShutdownWorld(minutes = 10):
    global FORCEKILL_TIME,REBOOT, ANNOUNCE_MINUTE
    REBOOT = False
    FORCEKILL_TIME = sysTime()+minutes*60
    ANNOUNCE_MINUTE = minutes
    AnnounceShutdownReboot()

def RebootWorld(minutes = 10):
    global FORCEKILL_TIME,REBOOT, ANNOUNCE_MINUTE
    FORCEKILL_TIME = sysTime()+minutes*60
    REBOOT = True
    ANNOUNCE_MINUTE = minutes
    AnnounceShutdownReboot()

    
    
def ZoneClusterSpawned(cluster=None):
    if cluster:
        ZONECLUSTERS.append(cluster)
    else:
        znames = CLUSTERNAMES[0]
        cluster = ZoneClusterAvatar(0,znames,WORLDNAME,PUBLICNAME,PASSWORD, \
            GMCONNECTION)
        cluster.spawnWorldProcess(ZoneClusterSpawned)
        return
    
    
    cnum = cluster.clusterNum+1    
    
    #done? some of the announce stuff up in tick could probably be moved here
    if cnum == len(CLUSTERNAMES):
        if GMCONNECTION:
            GMCONNECTION.registerZoneClusterAvatars(ZONECLUSTERS)
        return
    
    znames = CLUSTERNAMES[cnum]
    cluster = ZoneClusterAvatar(cnum,znames,WORLDNAME,PUBLICNAME,PASSWORD, \
        GMCONNECTION)
    
    if cnum not in REMOTECLUSTERS:
        cluster.spawnWorldProcess(ZoneClusterSpawned)
    else:
        cluster.spawnRemoteWorldProcess(WORLDIMPS[0],ZoneClusterSpawned)
    
    
    

def SpawnWorld():
    global SPAWNED
    SPAWNED = True
    
    print "Spawning World Zone Clusters"
    ZoneClusterAvatar.clusterCount = len(CLUSTERNAMES)
    
    #start spawning
    ZoneClusterSpawned()
        
        
        
        
#announce stuff
def AnnounceSuccess(result,perspective):
    perspective.broker.transport.loseConnection()

def AnnounceConnected(perspective):
    #we'll always connect on zone cluster 0 first
    wname = WORLDNAME.replace("_"," ")
    perspective.callRemote("WorldAvatar","announceWorld",wname,ZoneClusterAvatar.avatars[0].worldPort,False,[],(ZoneClusterAvatar.numPlayers,1024)).addCallbacks(AnnounceSuccess,AnnounceFailure,(perspective,))
    
def AnnounceFailure(error):
    print "ANNOUNCE FAILURE!!!!!",error

def AnnounceWorld():
    global ANNOUNCECALLBACK
    ANNOUNCECALLBACK = reactor.callLater(60,AnnounceWorld)
    
    username = "%s-World"%PUBLICNAME
    password = PASSWORD
    password = md5(password).digest()


    print "Announcing World"
    
    factory = pb.PBClientFactory()
    reactor.connectTCP(MASTERIP,MASTERPORT,factory)
    #the pb.Root() is a bit of a hack, I don't know how to get host address on server without
    #sending it, and I don't want to take the time to figure it out at the moment
    factory.login(UsernamePassword(username, password),pb.Root()).addCallbacks(AnnounceConnected, AnnounceFailure)

def ImpConnected(imp):
    print "Imp %i connected... spawning world"%imp.id
    WORLDIMPS[imp.id]=imp
    #kickstart my heart
    reactor.callLater(0,SpawnWorld)
    reactor.callLater(0,Tick)
    
def LoadZoneClusterNames():
    try:
        print str(CLUSTERNAMES)
        #should probably remove the CLUSTERNAMES from the gamesettings entirely
        if not len(CLUSTERNAMES):
            print "./%s/data/worlds/multiplayer.baseline/world.db"%(GAMEROOT)
            conn = sqlite.connect("./%s/data/worlds/multiplayer.baseline/world.db"%(GAMEROOT))
            conn.text_factory = sqlite.OptimizedUnicode
            
            cursor = conn.cursor()
            cursor.execute("SELECT cluster_id,name FROM zone;")
            
            zones = {}
            for row in cursor.fetchall():
                print row
                if not zones.has_key(row[0]):
                    zones[row[0]]=[]
                zones[row[0]].append(row[1])
                
            for x in range(0,10):
                if not zones.has_key(x):
                    break
                CLUSTERNAMES.append(zones[x])
            
            cursor.close()
            conn.close()
    except:
        print_exc()
        

def main():
    global GMCONNECTION
    GMCONNECTION = GMServices(WORLDNAME)
    GMCONNECTION.connect()
    
    LoadZoneClusterNames()
    
    startWorldServices()
    startCharacterServices(PUBLICNAME,PASSWORD)
    #startImpServices(ImpConnected)
    reactor.callLater(0,SpawnWorld)
    reactor.callLater(0,Tick)
    
    #open up a manhole
    FACTORY = MakeFactory("me","me",ShutdownWorld,RebootWorld)
    reactor.listenTCP(7002, FACTORY)
    #print "Waiting for Imp connections..."
    reactor.run()

 
