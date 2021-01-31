# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from twisted.cred.portal import Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.internet import reactor
from zope.interface import implements
from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.portal import IRealm
import os,sys,imp
from twisted.python import components, failure, log

import math
try:
    import win32api,win32con,win32event
    signal = None
except ImportError:
    win32api = win32con = win32event = None
    import signal
import time,traceback

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze
        
        
#zone cluster services
class ZoneClusterAvatar(pb.Avatar):
    
    avatars = {}
    clusterCount = 0
    numPlayers = 0
    
    #publicname (leader) -> [(pname,cname)]
    masterAllianceInfo = {}
    
    #publicname -> (charname,realm,zonename,transform)
    deathMarkerInfo = {}
    
    characterInfos = {}
    
    
    def __init__(self, clusternum, zonenames, worldname, publicname, password, \
        gmConnection=None):
        ZoneClusterAvatar.avatars[clusternum] = self
        self.clusterNum = clusternum
        self.zoneNames = zonenames
        self.zonePorts = []
        self.zonePasswords = []
        self.worldName = worldname
        self.publicName = publicname
        self.password = password
        self.worldPID = None
        self.zonePID = []
        self.reboot = True
        self.numPlayers = 0
        self.live = False
        self.worldPort = -1
        self.mind = None
        self.killed = False
        self.imp = None
        self.gmConnection = gmConnection
    
    
    def spawnRemoteWorldProcess(self,imp,spawnedCallback):
        print "spawning remote world process on imp %i"%imp.id

        znames="-zones=%s"%'!'.join(self.zoneNames)
        args= r' -cluster=%i -worldname=%s -publicname=%s -password=%s %s'%(self.clusterNum,self.worldName,self.publicName,self.password,znames)
        
        self.imp = imp
        self.spawnedCallback = spawnedCallback
        
        #XXX security, do not pass the login information here!
        self.imp.spawnWorldProcess(args)
        
        
    def spawnWorldProcess(self,spawnedCallback):
        print "spawning world process"
        
        frozen = main_is_frozen()
        
        cwd = os.getcwd()
        
        if frozen:
            cmd  =  r'..\bin\WorldServer.exe'
            args = ""
        else:
            cmd  =  sys.executable
            args =  "%s/WorldServer.py"%cwd
        
        znames = "-zones=%s"%'!'.join(self.zoneNames)
        args += r' -cluster=%i -worldname=%s -publicname=%s -password=%s %s'%(self.clusterNum,self.worldName,self.publicName,self.password,znames)
        
        for arg in sys.argv:
            if arg.startswith("gameconfig="):
                args += " %s"%arg
            elif arg.startswith("-wx"):
                args += " -wx"
        
        self.spawnedCallback = spawnedCallback
        
        print "####Spawning World Server: " + str(args)
		
        if sys.platform[:6] != 'darwin':
            s = 'start "%s" %s %s'%(os.getcwd(),cmd,args)
            s = os.path.normpath(s)
            os.system(s)
        else:
            cmd = sys.executable
            args = args.split(" ")
            args.insert(0,cmd)
            
            s = 'pythonw -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)
    
#remote
    
    def sendCharacterInfos(self):        
        for z in ZoneClusterAvatar.avatars.itervalues():
            try:
                z.mind.callRemote("setCharacterInfos", ZoneClusterAvatar.characterInfos)
            except:
                traceback.print_exc()


    def perspective_setCharacterInfo(self,publicName,cinfo):
        if not ZoneClusterAvatar.characterInfos.has_key(publicName) or ZoneClusterAvatar.characterInfos[publicName]!=cinfo:
            ZoneClusterAvatar.characterInfos[publicName]=cinfo
            self.sendCharacterInfos()
            
    def clearCharacterInfo(self,publicName):
        if not ZoneClusterAvatar.characterInfos.has_key(publicName):
            return
        
        del ZoneClusterAvatar.characterInfos[publicName]
        self.sendCharacterInfos()
    
    
    def perspective_resurrectionRequest(self,publicName,xpRecover,healthRecover,manaRecover,staminaRecover,tm,cname):
        for z in ZoneClusterAvatar.avatars.itervalues():
            try:
                z.mind.callRemote("resurrectionRequest",publicName,xpRecover,healthRecover,manaRecover,staminaRecover,tm,cname)
            except:
                traceback.print_exc()
    
    
    def sendDeathMarkerInfo(self):        
        for z in ZoneClusterAvatar.avatars.itervalues():
            try:
                z.mind.callRemote("setDeathMarkerInfo", ZoneClusterAvatar.deathMarkerInfo)
            except:
                traceback.print_exc()

    def perspective_setDeathMarker(self,publicName,charName,realm,zoneName,pos,rot):
        ZoneClusterAvatar.deathMarkerInfo[publicName]=(charName,realm,zoneName,pos,rot)
        self.sendDeathMarkerInfo()
        
    def perspective_clearDeathMarker(self,publicName):
        if not ZoneClusterAvatar.deathMarkerInfo.has_key(publicName):
            return
        del ZoneClusterAvatar.deathMarkerInfo[publicName]
        self.sendDeathMarkerInfo()

    def sendAllianceInfo(self):        
        for z in ZoneClusterAvatar.avatars.itervalues():
            try:
                z.mind.callRemote("setMasterAllianceInfo", ZoneClusterAvatar.masterAllianceInfo)
            except:
                traceback.print_exc()
                

                
    def clearAllianceInfo(self,publicName):
        changed = False
        remove = []
        for leader,a in ZoneClusterAvatar.masterAllianceInfo.iteritems():
            for pname,cname in a:
                if pname == publicName:
                    changed = True
                    a.remove((pname,cname))
                    break
                
        if ZoneClusterAvatar.masterAllianceInfo.has_key(publicName):
            changed = True
            del ZoneClusterAvatar.masterAllianceInfo[publicName]
                
        if changed:
            self.sendAllianceInfo()
            
    def perspective_clearAllianceInfo(self,publicName):
        self.clearAllianceInfo(publicName)
        
    def perspective_setAllianceInfo(self,leaderName,info):
        
        members = []
        for pname,cname in info:
            members.append(pname)
        
        remove = []
        for leader,a in ZoneClusterAvatar.masterAllianceInfo.iteritems():
            for pname,cname in a[:]:
                if pname in members:
                    a.remove((pname,cname))
            if not len(a):
                remove.append(leader)
                
        for r in remove:
            del ZoneClusterAvatar.masterAllianceInfo[r]
                
                    
        ZoneClusterAvatar.masterAllianceInfo[leaderName]=info
        self.sendAllianceInfo()
    
    def perspective_joinAlliance(self,leaderName,publicName,characterName):
        if ZoneClusterAvatar.masterAllianceInfo.has_key(publicName):
            del ZoneClusterAvatar.masterAllianceInfo[publicName]
            
        a = ZoneClusterAvatar.masterAllianceInfo[leaderName]
        for pname,cname in a:
            if pname == publicName:
                print "Warning: %s already in %s's alliance"%(publicName,leaderName)
                return
        a.append((publicName,characterName))
        self.sendAllianceInfo()
    
    
    def perspective_setWorldPID(self,pid,worldport,genesisTime,csavatar):
        from charservices import CServerAvatar,CServerMind
        
        if CServerAvatar.genesisTime:
            if CServerAvatar.genesisTime != genesisTime:
                traceback.print_stack()
                print "AssertionError: CServerAvatar.genesisTime != genesisTime!"
                return
        else:
            CServerAvatar.genesisTime = genesisTime
            
        CServerAvatar.worldCSAvatars[self.clusterNum]=csavatar
        mind = CServerMind.worldCSMinds[self.clusterNum]=CServerMind()
        
        self.worldPort = worldport        
        self.worldPID = pid
        
        return mind
        
        
        
    def perspective_setZonePID(self,pids,zports,zpasswords):
        self.zonePID = pids
        self.zonePorts = zports
        self.zonePasswords = zpasswords
        
        
        if not self.live:
            print "Zone Cluster %i is live"%self.clusterNum
            self.live = True
            ZoneClusterAvatar.clusterCount-=1
            self.spawnedCallback(self)
            self.spawnedCallback = None
            
            
            #if not ZoneClusterAvatar.clusterCount:
            #    print "All clusters are live announcing to master server"
            #    #ZoneClusterAvatar.avatars[0].mind.callRemote("announceWorldToMaster")
    
    
    def perspective_playerJoinedWorld(self, publicname):
        ZoneClusterAvatar.numPlayers += 1
    
    
    def perspective_playerLeftWorld(self, publicname, transfering):
        if not transfering:
            self.clearAllianceInfo(publicname)
            self.clearCharacterInfo(publicname)
        
        ZoneClusterAvatar.numPlayers -= 1
    
    
    def perspective_printException(self, exp):
        print exp
    
    
    def killWorld(self):
        try:
            d = self.mind.callRemote("shutdown")
            
            #we'll get an error in perspective->playersExported if there is nothing to export *or* if there is an error when we kill the process
            #so, this is just a safeguard
            d.addErrback(self.killWorldNow)
        except:
            self.killWorldNow(True)
        
    def perspective_playersExported(self):
        print "Players Exported"
        self.killWorldNow(True)
        
    def killProcess(self,pid):
        if self.imp:
            return
        print "Killing Process",pid
        try:
            if win32api:
                handle = win32api.OpenProcess(win32con.SYNCHRONIZE|win32con.PROCESS_TERMINATE, 0, pid)
                if handle:
                    win32api.TerminateProcess(handle,-1)
                    win32api.CloseHandle(handle)
            else:
                os.kill(pid,signal.SIGKILL)
        except:
            #oh no!
            traceback.print_exc()
                
    def killWorldNow(self,result):
        if self.killed:
            return
        
        self.killed = True
        
        if self.imp:
            self.imp.mind.callRemote("killWorldNow",self.worldPID,self.zonePID)
            
        else:
            print "Killing World"
            for p in self.zonePID:
                self.killProcess(p)
            self.killProcess(self.worldPID)
            
        del ZoneClusterAvatar.avatars[self.clusterNum]
    
    
    def perspective_propagateCmd(self, cmd, *args, **kwargs):
        # At least the command argument must be present.
        # Also don't propagate command if world is being killed.
        if self.killed or not cmd:
            return
        
        # If the command is to send guild or GM chat, also forward
        #  it to eventual other worlds via GM server.
        try:
            if self.gmConnection != None and self.gmConnection.perspective:
                if cmd == "sendGuildMsg":
                    self.gmConnection.perspective.callRemote("WorldDaemon", \
                        "sendGuildMsg",*args,**kwargs)
                elif cmd == "receiveGMChat":
                    self.gmConnection.perspective.callRemote("WorldDaemon", \
                        "receiveGMChat",*args,**kwargs)
        except:
            traceback.print_exc()
        
        # Call the desired command on all zone clusters.
        for avatar in ZoneClusterAvatar.avatars.itervalues():
            # Skip ourselves.
            if avatar == self:
                continue
            try:
                avatar.mind.callRemote(cmd,*args,**kwargs)
            except:
                traceback.print_exc()



class SimpleRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        
        
        
        if not mind:
            raise BadConnectionError("no mind")

        ip = mind.broker.transport.getPeer()
        
        print ip,avatarId,mind
        
        #if ip.host != '127.0.0.1':
        #    raise BadConnectionError("bad ip")
        
        if pb.IPerspective in interfaces:
            p = ZoneClusterAvatar.avatars[int(avatarId)]
            p.mind = mind
            return pb.IPerspective, p, lambda : None
        else:
            raise NotImplementedError("no interface")
        
def StartServices():
    #fire up the World Stuff
    portal = Portal(SimpleRealm())
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    from md5 import md5
    password = md5("daemon").digest()
    for x in range(0,100):
        checker.addUser(str(x), password)
    portal.registerChecker(checker)
    reactor.listenTCP(7000,pb.PBServerFactory(portal))
    
    


