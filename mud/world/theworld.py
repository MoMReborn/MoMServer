# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from twisted.internet import reactor

from mud.common.persistent import Persistent
from mud.world.core import *
from mud.world.cserveravatar import CharacterServerAvatar
from mud.world.defines import *
from mud.world.zone import TempZoneLink,Zone,ZoneInstance
from mud.world.shared.worlddata import ZoneOption
from mud.worldserver.charutil import ExtractPlayer
# Those avatars aren't actually used here, but the classes
#  need to be registered.
import mud.world.guardianavatar
import mud.world.immortalavatar
import mud.world.statsavatar

from base64 import encodestring
from copy import copy
from cPickle import dumps
from datetime import datetime
import os
from shutil import copyfile
from sqlobject import *
import sys
from time import time as sysTime
import traceback
try:
    import win32api,win32process
except ImportError:
    win32api = win32process = None



class Time:
    def __init__(self):
        self.second = 0
        self.minute = 15
        self.hour = 12
        self.day = 0
        self.ticks = 0
        self.lasttime = -1
    
    def tick(self):
        #advance time, tick this 6x a second
        if self.lasttime == -1:
            self.lasttime = sysTime()
        delta = sysTime() - self.lasttime
        self.lasttime = sysTime()
        
        self.ticks += 3
        self.second += delta * 24.0 #1 game day = 1 real hour
        if self.second > 59:
            self.second -= 59
            self.minute += 1
            if self.minute > 59:
                self.minute = 0
                self.hour += 1
                if self.hour > 23:
                    self.hour = 0
                    self.day += 1


class World(Persistent):
    name = StringCol(alternateID = True, default="TheWorld")
    
    #configuration
    allowGuests = BoolCol(default=True)
    pwNewPlayer = StringCol(default="")
    pwCreateZone = StringCol(default="")
    
    #metrics
    maxLiveZones = IntCol(default=1024)
    maxLivePlayers = IntCol(default=4096)
    
    #time
    second = IntCol(default=0)
    minute = IntCol(default=15)
    hour = IntCol(default=12)
    day = IntCol(default=0)
    ticks = IntCol(default=0)
    
    zones = MultipleJoin('Zone')
    
    singlePlayer = BoolCol(default=False)
    
    aggroOn = BoolCol(default = True)
    
    genesisTime = DateTimeCol(default = datetime.now)
    
    #todo, realm support
    startZone = StringCol(default="")
    dstartZone = StringCol(default="")
    mstartZone = StringCol(default="")

    #-1 = custom world?
    #versionMajor = IntCol(default = 0)
    #versionMinor - IntCol(default = 0)
        
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        
        self.shuttingDown = False
        self.liveZoneInstances = []
        self.waitingZoneInstances = []
        self.activePlayers = []
        self.globalPlayers = {}
        self.mutedPlayers = {}
        self.time = Time()
        
        #from db
        self.time.second = 0
        self.time.minute = self.minute
        self.time.hour = self.hour
        self.time.day = self.day
        self.time.ticks = 0
        
        self.lasttime = -1
        
        self.transaction = False
        self.tickTransaction = None
        self.singlePlayer = False
        self.singlePlayerBackupTimer = 120 # Once every minute
        
        self.liveZoneCallback = None
        
        self.usedZonePorts = []
        
        self.running = False
        self.dbFile = None
        self.backupTick = 30 #once every 30 minutes
        
        self.paused = False
        self.pauseTime = sysTime()
        
        self.daemonPerspective = None
        self.daemonMind = None
        
        self.clusterNum = -1
        self.worldPort = -1
        
        self.staticZoneNames = []
        
        self.priority = 1
        
        self.deathMarkers = {}
        self.characterInfos = {}
        
        self.allowConnections = True
        
        self.cpuSpawn = 0
        self.cpuDespawn = 0
        self.spawnZoneIndex = 0
        self.isShuttingDown = False
    
    
    def tick(self):
        if not self.running:
            return
        
        reactor.callLater(.5,self.tick) #2x sec
        
        if False:#CoreSettings.PGSERVER:
            if len(self.liveZoneInstances)==len(self.staticZoneNames) and self.allowConnections:
                if not len(self.activePlayers) and self.priority:
                    self.priority = 0
                    win32process.SetPriorityClass(win32process.GetCurrentProcess(),win32process.IDLE_PRIORITY_CLASS)
                    
                if len(self.activePlayers) and not self.priority:
                    self.priority = 1
                    win32process.SetPriorityClass(win32process.GetCurrentProcess(),win32process.NORMAL_PRIORITY_CLASS)
                    
                #if not self.priority:
                #    win32api.Sleep(2000)
            elif not self.priority:
                self.priority = 1
                win32process.SetPriorityClass(win32process.GetCurrentProcess(),win32process.NORMAL_PRIORITY_CLASS)
                
        
        if False:#RPG_BUILD_DEMO:
            t = sysTime() - self.pauseTime
            if 13*60 >= t >= 12*60:
                self.paused = True
            elif t>13*60:
                self.paused = False
                self.pauseTime = sysTime()
            else:
                self.paused=False
        
        
        
        self.time.tick()
        
        #store in db
        if self.time.hour != self.hour:
            self.minute = self.time.minute
            self.hour = self.time.hour
            self.day = self.time.day
            
        CharacterServerAvatar.tick()
            
        #if self.lasttime == -1:
        #    self.lasttime = sysTime()-2
        #delta = sysTime()-self.lasttime
        
        #if delta > .5:
            #self.lasttime = sysTime()
            
        
        if CoreSettings.PGSERVER:
            if self.isShuttingDown:
                self.cpuSpawn = 0
                self.cpuDespawn = 0
            else:
                self.cpuSpawn = 4
                self.cpuDespawn = 8
        else:
            self.cpuSpawn = 1000000
            self.cpuDespawn = 1000000
        
        # Select the zone which will be allowed to spawn mobs.
        spawnZone = None
        if len(self.liveZoneInstances) > 0:
            if self.spawnZoneIndex > len(self.liveZoneInstances) - 1:
                self.spawnZoneIndex = 0
            spawnZone = self.liveZoneInstances[self.spawnZoneIndex]
            self.spawnZoneIndex += 1
        
        # Tick all live zone instances.
        for z in self.liveZoneInstances:
            z.tick(spawnZone)
        
        #weed out dynamic zones that haven't any players for x amount of time
        #we need to weed out failed zones (stuck in waiting, etc)
        
        if not self.singlePlayer:
            timedOut = []
            for z in self.liveZoneInstances:
                if not z.dynamic:
                    continue
                if not len(z.players) and not len(z.playerQueue):
                    if z.timeOut == -1:
                        z.timeOut = sysTime()
                    elif (sysTime() - z.timeOut)/60 > 20: # 20 minutes
                        timedOut.append(z)
                    
                else:
                    z.timeOut = -1
            
            for z in timedOut:
                self.closeZone(z)
        
        # Backup single player data every minute.
        else:
            self.singlePlayerBackupTimer -= 1
            if self.singlePlayerBackupTimer < 0:
                # Reset timer to one minute.
                self.singlePlayerBackupTimer = 120
                
                for player in self.activePlayers:
                    # If there's no party, player hasn't logged in yet and
                    #  there's no need to back up.
                    if player.party:
                        player.backupPlayer()
                
                # Force a write to database.
                conn = Persistent._connection.getConnection()
                cursor = conn.cursor()
                cursor.execute("END;")
                cursor.execute("BEGIN;")
                cursor.close()
    
    
    def commit(self, commitOnly=False):
        if self.tickTransaction:
            self.tickTransaction.cancel()
        self.transactionTick(commitOnly)
    
    
    def transactionTick(self, commitOnly=False):
        print "... Commit World Database ..."
        
        conn = Persistent._connection.getConnection()
        cursor = conn.cursor()
        
        if self.transaction:
            cursor.execute("END;")
        
        if self.dbFile and not commitOnly:
            self.backupTick -= 1
            if not self.backupTick:
                print "Backing up world database"
                self.backupTick = 30 #once every 30 minutes
                try:
                    BackupWorld(self.dbFile)
                except:
                    traceback.print_exc()
        
        self.transaction = True
        
        cursor.execute("BEGIN;")
        cursor.close()
        
        self.tickTransaction = reactor.callLater(60,self.transactionTick)
    
    
    def startup(self):
        from mud.world.archetype import InitClassSkills
        from mud.world.faction import InitKOS
        from mud.world.loot import Loot
        from mud.world.mobspells import InitMobSpells
        
        InitClassSkills()
        InitKOS()
        Loot.initRandomLoot()
        InitMobSpells()
        self.running = True
    
    
    def shutdown(self):
        if self.running:  # else reentrant in single player worlds through player logout
            self.running = False
            
            for p in self.activePlayers[:]:
                p.logout()
            
            self.shuttingDown = True
            if self.tickTransaction:
                self.tickTransaction.cancel()
                self.tickTransaction = None
            
            conn = Persistent._connection.getConnection()
            cursor = conn.cursor()
            if self.transaction:
                cursor.execute("END;")
            
            cursor.close()
            
            self.transaction = False
        
        #move me
        

            
    def playerJoinWorld(self,player):
        if player in self.activePlayers:
            traceback.print_stack()
            print "AssertionError: player already in active players!"
            return
        player.world = self
        self.activePlayers.append(player)
        player.zone = None
        player.enteringWorld = True
        
        if CoreSettings.PGSERVER:
            self.daemonPerspective.callRemote("playerJoinedWorld",player.publicName)
    
    
    def playerLeaveWorld(self, player):
        zones = copy(self.liveZoneInstances)
        zones.extend(self.waitingZoneInstances)
        
        if CoreSettings.PGSERVER:
            self.daemonPerspective.callRemote("playerLeftWorld",player.publicName,player.transfering)
        
        if CoreSettings.MAXPARTY == 1 and not player.transfering:
            self.clearDeathMarker(player)
        
        for zinst in zones:
            if player == zinst.owningPlayer: #XXX remove all this owningPlayer crap, it was a good idea at the time
                self.closeZone(zinst)
         
        #hm       
        self.activePlayers.remove(player)
        player.zone = None
        
        if player.extract:
            CharacterServerAvatar.extractLoggingPlayer(player,not player.enteringWorld)
        
        if self.singlePlayer:
            self.shutdown()
            
    
    def playerJumped(self,result,player):
        
        player.extract = False
        try:
            player.mind.broker.transport.loseConnection()
        except:
            pass
        if player.avatar:
            
            player.avatar.logout()

        
        
    def playerTransfered(self,result,party,player):
        wip,wport,wpassword,zport,zpassword = result
        d = player.mind.callRemote("jumpServer",wip,wport,wpassword,zport,zpassword,party)
        d.addCallback(self.playerJumped,player)
        d.addErrback(self.playerJumped,player)
    
    
    #change the world login to use this too
    def onZoneTrigger(self,player,zoneLink):
        zoneName = zoneLink.dstZoneName
        
        # If the player who has triggered a zone trigger is trading, then cancel
        # the trade.  This is important so that a Character buffer does not get
        # extracted before a trade is accepted.  If this was to occur, then the
        # buffer sent to another cluster may contain an item that was traded
        # while waiting for the daemon to respond.
        if player.trade:
            player.trade.cancel()
        
        if CoreSettings.PGSERVER:
            if not self.allowConnections:
                player.backupItems()
                
                #we're shutting down, so log out character
                if player.darkness:
                    player.darknessLogTransformInternal = zoneLink.dstZoneTransform
                    player.darknessLogZone = Zone.byName(zoneLink.dstZoneName)
                elif player.monster:
                    player.monsterLogTransformInternal = zoneLink.dstZoneTransform
                    player.monsterLogZone = Zone.byName(zoneLink.dstZoneName)
                else:
                    player.logTransformInternal = zoneLink.dstZoneTransform
                    player.logZone = Zone.byName(zoneLink.dstZoneName)
                
                publicName,pbuffer,cbuffer,cvalues = ExtractPlayer(player.publicName,player.id,player.party.members[0].id,False)
                pbuffer = encodestring(dumps(pbuffer, 2))
                cbuffer = encodestring(dumps(cbuffer, 2))
                
                player.transfering = True
                from mud.world.cserveravatar import AVATAR
                AVATAR.mind.callRemote("savePlayerBuffer", \
                    publicName,pbuffer,cbuffer,cvalues)
                
                player.extract = False
                self.kickPlayer(player)
                return
            
            elif zoneName not in self.staticZoneNames:
                # we need to transfer
                player.prepForZoneOut()
                player.zone.removePlayer(player)
                player.zone = None
                
                if player.darkness:
                    player.darknessLogTransformInternal = zoneLink.dstZoneTransform
                    player.darknessLogZone = Zone.byName(zoneLink.dstZoneName)
                elif player.monster:
                    player.monsterLogTransformInternal = zoneLink.dstZoneTransform
                    player.monsterLogZone = Zone.byName(zoneLink.dstZoneName)
                else:
                    player.logTransformInternal = zoneLink.dstZoneTransform
                    player.logZone = Zone.byName(zoneLink.dstZoneName)
                
                publicName,pbuffer,cbuffer,cvalues = ExtractPlayer(player.publicName,player.id,player.party.members[0].id,False)
                pbuffer = encodestring(dumps(pbuffer, 2))
                cbuffer = encodestring(dumps(cbuffer, 2))
                
                player.transfering = True
                aname = player.publicName
                if player.alliance:
                    aname = player.alliance.remoteLeaderName
                else:
                    print "Warning: Player %s has no alliance on zone trigger, could mess up alliances!!!!!"%player.publicName
                
                from mud.world.cserveravatar import AVATAR
                
                guildInfo = (player.guildName,player.guildInfo,player.guildMOTD,player.guildRank)
                d = AVATAR.mind.callRemote("transferPlayer", \
                    player.publicName,pbuffer,player.party.members[0].name, \
                    cbuffer,zoneName,cvalues,aname,guildInfo)
                d.addCallback(self.playerTransfered,[player.party.members[0].name],player)
                return
        
        
        zone = Zone.byName(zoneName)
        
        
        if self.singlePlayer:
            self.closeZone(player.zone)
        
        allzi = []
        allzi.extend(self.liveZoneInstances)
        allzi.extend(self.waitingZoneInstances)
        
        zoptions = []
        
        if not self.singlePlayer:
            found = False
            for zi in allzi:
                if zi.zone == zone:
                    found = True
                    break
            if not found:
                allzi.append(self.startZoneProcess(zoneName))
        
        for zi in allzi:
            if zi.zone == zone:
                zo = ZoneOption()
                zo.zoneName = zoneName
                zo.zoneInstanceName = zi.name
                if zi.owningPlayer:
                    zo.owner = zi.owningPlayer.fantasyName
                else:
                    zo.owner = None  # dedicated
                zo.status = zi.status
                zoptions.append(zo)
        
        player.prepForZoneOut()
        player.zone.removePlayer(player)
        player.zone = None
        
        # can be a spell trigger too
        player.triggeredZoneLink = zoneLink
        player.triggeredZoneOptions = zoptions #store zone options (these need to expire)
        
        player.mind.callRemote("setZoneOptions",zoptions)
    
    
    def getPlayerZone(self, pavatar, simPort, simPassword):
        # If the world is shutting down, return None.
        if self.shuttingDown:
            return None
        
        player = pavatar.player
        
        allzi = []
        allzi.extend(self.liveZoneInstances)
        allzi.extend(self.waitingZoneInstances)
        
        #select zone
        if player.darkness:
            logZone = player.darknessLogZone
        elif player.monster:
            logZone = player.monsterLogZone
        else:
            logZone = player.logZone
        
        for z in allzi:
            if z.zone == logZone:
                #for now if zone is up just join that one
                return z
        
        #zone isn't up
        if CoreSettings.PGSERVER:
            raise AssertionError,"Error, Zone %s isn't up!"%logZone.name
        
        if self.singlePlayer:
            ip = '127.0.0.1'
            z = ZoneInstance(logZone,ip,simPort,simPassword,None)
            z.world = self
            z.time = self.time
            self.waitingZoneInstances.append(z)
            return z
        else:
            #the zone isn't up and we are multiplayer, so we need to launch the process
            return self.startZoneProcess(logZone.name)
        
        return z
    
    
    def playerSelectZone(self, pavatar, simPort, simPassword):
        # If the world is shutting down, return None.
        if self.shuttingDown:
            return None
        
        return self.getPlayerZone(pavatar,simPort,simPassword)
    
    
    def closeZone(self,zinst):
        try:
            if zinst in self.liveZoneInstances:
                self.liveZoneInstances.remove(zinst)
            if zinst in self.waitingZoneInstances:
                self.waitingZoneInstances.remove(zinst)
            zinst.stop()
            if zinst.port in self.usedZonePorts:
                self.usedZonePorts.remove(zinst.port)
        except:
            traceback.print_exc()
            
            
        #zone crashed, restart immediately
        if not self.shuttingDown:
            if not zinst.dynamic and not self.singlePlayer:
                self.startZoneProcess(zinst.zone.name,False)
            
            
        
    def closePlayerZone(self,player):
        for zinst in self.liveZoneInstances:
            if zinst.owningPlayer == player:
                self.closeZone(zinst)
                break
                
        for zinst in self.waitingZoneInstances:
            if zinst.owningPlayer == player:
                self.closeZone(zinst)
                break
    
    
    def startSimulation(self, zoneInstanceName, pid):
        zinst = None
        for z in self.waitingZoneInstances:
            if z.name == zoneInstanceName:
                zinst = z
                break
        
        if not zinst: #could happen on waiting timeout
            traceback.print_stack()
            print "AssertionError: zinst is empty!"
            return
        
        zinst.pid = pid
        
        self.waitingZoneInstances.remove(zinst)
        self.liveZoneInstances.append(zinst)
        zinst.status = "Live"
        
        if self.liveZoneCallback:
            self.liveZoneCallback(zinst)
        
        if self.daemonPerspective:
            zpid = []
            zport = []
            zpassword = []
            
            for zname in self.staticZoneNames:
                for z in self.liveZoneInstances:
                    if zname == z.zone.name:
                        if z.pid == None:
                            traceback.print_stack()
                            print "AssertionError: z.pid is empty!"
                            return
                        zpid.append(z.pid)
                        zpassword.append(z.password)
                        zport.append(z.port)

            self.daemonPerspective.callRemote("setZonePID",zpid,zport,zpassword)
            
        return zinst
    
    
    def spawnDedicatedZone(self,simAvatar,zoneName,simPort):
        if zoneName == 'any':
            #we pick
            znames = [zone.name for zone in self.zones]
            #list of all instances
            zinstances = []
            for zi in self.liveZoneInstances:
                zinstances.append(zi)
            for zi in self.waitingZoneInstances:
                zinstances.append(zi)
                
            for zi in zinstances:
                if zi.zone.name in znames:
                    znames.remove(zi.zone.name)
                    
            if not len(znames):
                #all zones served
                raise "all zones server, this isn't actually an error... eventually we serve another zone instance, based on waiting etc"
                
            zoneName = znames[0]
        else:
            #let's see if we launched this zone
            for zi in self.waitingZoneInstances:
                if zi.port == simPort:
                    return zi
            
        #this is a dedicated server that has been launched remotely, 
        #shouldn't happen for right now... so we'll assert
        traceback.print_stack()
        print "AssertionError: dedicated server launched remotely, shouldn't happen for now!"
        return
        
        zone = Zone.byName(zoneName)
        #hrm
        ip = self.zoneIP #see world server main.py
        simPassword = ""
        z = ZoneInstance(zone,ip,simPort,simPassword,None)
        z.time = self.time
        self.waitingZoneInstances.append(z)
        return z
            
    def startZoneProcess(self,zoneName,dynamic=True):
        port = None
        for x in xrange(self.zoneStartPort,self.zoneStartPort+100):
            if x in self.usedZonePorts:
                continue
            port = x
            self.usedZonePorts.append(x)
            break
            
        if port == None:
            traceback.print_stack()
            print "AssertionError: no port assigned!"
            return
        
        zone = Zone.byName(zoneName)
        #hrm
        ip = self.zoneIP #see world server main.py
        simPassword = ""
        z = ZoneInstance(zone,ip,port,simPassword,None)
        z.world = self
        z.time = self.time
        z.dynamic = dynamic
        
        self.waitingZoneInstances.append(z)
        
        if self.frozen:
            cmd  =  r'..\bin\ZoneServer.exe'
            args = ""
        else:
            cmd  = sys.executable
            path = os.getcwd()
            args = r'%s/zoneserver.py'%path
        
        args += r' -dedicated'
        args += r' -serverport %i -zone %s -world %s -worldport %i'%(port,zoneName,self.multiName,self.worldPort)
        if dynamic:
            args += r' -dynamic'
        
        for arg in sys.argv:
            if arg.startswith("gameconfig="):
                args += " %s"%arg
        
        if sys.platform[:6] != "darwin":
            # Just don't provide cluster number via gameconfig until
            #  MoM uses gameconfig as well.
            args += r' -cluster=%i'%self.clusterNum
            s = 'start "%s" %s %s'%(os.getcwd(),cmd,args)
            s = os.path.normpath(s)
            print s
            os.system(s)
        
        else:
            if arg.startswith("-wx"):
                args += " -wx"
            
            cmd = sys.executable
            args = args.split(" ")
            args.insert(0,cmd)
            s = 'pythonw -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)
        
        return z
    
    
    def getZoneByInstanceName(self,iname):
            for zi in self.liveZoneInstances:
                if zi.name == iname:
                    return zi
                
            for zi in self.waitingZoneInstances:
                if zi.name == iname:
                    return zi
                    
            return None
        

    def reallySetDeathMarker(self,publicName,info):
        charName,realm,zoneName,pos,rot = info
        self.deathMarkers[publicName]=info
        for zi in self.liveZoneInstances:
            if zi.zone.name == zoneName:
                zi.setDeathMarker(publicName,charName,realm,pos,rot)
                return
        
    
    def reallyClearDeathMarker(self,publicName):
        if not self.deathMarkers.has_key(publicName):
            return
        
        #charName,realm,zoneName,pos,rot = self.deathMarkers[publicName]
        del self.deathMarkers[publicName]
        
        #just clear on all to be sure
        for zi in self.liveZoneInstances:
            zi.clearDeathMarker(publicName)
        
    def setDeathMarkerInfo(self,info):
        #get rid of the ones that are just gone
        for p in self.deathMarkers.keys():
            if p not in info:
                self.reallyClearDeathMarker(p)
        
        #remaining
        for pname,dm in info.items():
            charName,realm,zoneName,pos,rot = dm
            if pname in self.deathMarkers:
                #we are holding a death marker
                if dm == self.deathMarkers[pname]:
                    continue #it's the same
                
                #it's changed, so first clear
                self.reallyClearDeathMarker(pname)
                
                if zoneName in self.staticZoneNames:
                    #it's on this zone cluster
                    self.reallySetDeathMarker(pname,dm)
            else:
                if zoneName in self.staticZoneNames:
                    self.reallySetDeathMarker(pname,dm)
                    
                
    
    def clearDeathMarker(self,player):
        if not self.daemonPerspective:
            return
        try:
            self.daemonPerspective.callRemote("clearDeathMarker",player.publicName)
        except:
            traceback.print_exc()
    
    
    def setDeathMarker(self, player, character):
        if not self.daemonPerspective:
            return
        # Death markers only exist on servers that restrict party size to 1.
        # So remove any death marker set by an eventual previous character.
        self.clearDeathMarker(player)
        if not character.deathZone:
            return
        zoneName = character.deathZone.name
        dt = character.deathTransform
        realm = player.realm
        charname = player.party.members[0].name
        pos = (dt[0],dt[1],dt[2])
        rot = (dt[3],dt[4],dt[5],dt[6])
        
        try:
            self.daemonPerspective.callRemote("setDeathMarker",player.publicName,charname,realm,zoneName,pos,rot)
        except:
            traceback.print_exc()
    
    
    def sendCharacterInfo(self, player):
        try:
            if self.daemonPerspective:
                c = player.party.members[0]
                s = c.spawn
                prefix = ""
                if player.avatar and player.avatar.masterPerspective:
                    if player.avatar.masterPerspective.avatars.has_key("GuardianAvatar"):
                        prefix = "(Guardian) "
                    if player.avatar.masterPerspective.avatars.has_key("ImmortalAvatar"):
                        prefix = "(Immortal) "
    
                cinfo = (prefix,c.name,s.realm,s.pclassInternal,s.sclassInternal,s.tclassInternal,s.plevel,s.slevel,s.tlevel,player.zone.zone.niceName,player.guildName)
                
                self.daemonPerspective.callRemote("setCharacterInfo",player.publicName,cinfo)
        except:
            traceback.print_exc()
    
    
    def onPlayerDeath(self,player):
        #back to your bindpoint fool!
        
        xpLoss = -1
        if len(player.party.members) > 1:
            xpLoss = 0
            for c in player.party.members:
                if c.xpDeathPrimary or c.xpDeathSecondary or c.xpDeathTertiary:
                    xpLoss = 1
                    break
        
        player.mind.callRemote("partyWipe", xpLoss)
        
        czone = player.zone.zone
        
        # Revive the player.
        for c in player.party.members:
            c.dead = False
            c.mob.health = 1
            c.mob.mana = 1
            c.mob.stamina = 1
        
        # Get the players bind zone and bind transform.
        if player.darkness:
            bzone = player.darknessBindZone
            btransform = player.darknessBindTransformInternal
        elif player.monster:
            bzone = player.monsterBindZone
            btransform = player.monsterBindTransformInternal
        else:
            bzone = player.bindZone
            btransform = player.bindTransformInternal
        
        # Check if player is bound in the zone they died in.
        if czone == bzone:
            # Good.  We just need to respawn the player, whew.
            player.zone.respawnPlayer(player)
        
        # Player is going tp zone.
        else:
            
            # Flush messages to player.
            player.flushMessages()
            
            # Create a zone link and trigger the link.
            zlink = TempZoneLink(bzone.name,btransform)
            self.onZoneTrigger(player,zlink)
    
    
    def kickPlayer(self,player):
        player.loggingOut = True
        if player.zone:
            player.zone.kickPlayer(player)
        avatar = player.avatar
        player.logout()
        if avatar:
            if avatar.mind:
                avatar.mind.broker.transport.loseConnection()
        


        

def BackupWorld(worldfile):
    n = datetime.now()
    s = n.strftime("%B_%d_%Y")
    d,f = os.path.split(worldfile)
    
    f,ext = os.path.splitext(f)
    
    backfolder = d+"/"+s
    if not os.path.exists(backfolder):
        os.makedirs(backfolder)
        
    x = 1
    while True:
        backupfile = backfolder+"/"+"%s_backup_%i%s"%(f,x,ext)
        if os.path.exists(backupfile):
            x+=1
            continue
        
        copyfile(worldfile,backupfile)
        break


