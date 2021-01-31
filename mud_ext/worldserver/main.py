# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#world server, yargh!

try:

    #this file is getting a tad ugly with supporting player worlds, pg worlds, and now zone clusters :)
    from time import time as curTime
    from base64 import encodestring
    from cPickle import dumps
    from shutil import rmtree,copyfile
    from traceback import print_stack,format_exc
    import sys,os,imp
    from md5 import md5

    try:
        import win32api,win32process
    except ImportError:
        win32api = win32process = None

    USE_WX = "-wx" in sys.argv

    if sys.platform == 'win32' and not USE_WX:
        from twisted.internet.iocpreactor import install
    else:
        USE_WX = True
        import wx
        from twisted.internet.wxreactor import install

    install()

    from twisted.spread import pb
    from twisted.internet import reactor
    from twisted.cred.credentials import UsernamePassword


    if USE_WX:
        from gui import Setup
        app = Setup(reactor)
        reactor.registerWxApp(app)


    WORLDNAME = None
    PUBLICNAME = None
    PASSWORD = None



    def SetupProcessors(cluster):
        if sys.platform != "win32":
            return

        handle = win32api.GetCurrentProcess()
        processMask,systemMask = win32process.GetProcessAffinityMask(handle)

        ht = False
        if systemMask&8:
            #we're going to count this as a hyperthreaded system
            #as we don't currently have any servers with > 2 physical cpu
            ht = True

        mask = 1
        if cluster == 0:
            if ht:
                mask = 3
            else:
                mask = 1
        elif cluster == 1:
            if ht:
                mask = 12
            else:
                mask = 2

        print "Setting Processor Affinity Mask to",mask
        win32process.SetProcessAffinityMask(handle,mask)


    CLUSTER = -1
    ZONENAMES = []
    DAEMONIP = "127.0.0.1"

    for arg in sys.argv:
        if arg.startswith('-worldname='):
            WORLDNAME = arg[11:]
        if arg.startswith('-publicname='):
            PUBLICNAME = arg[12:]
        if arg.startswith('-password='):
            PASSWORD = arg[10:]
        if arg.startswith('-cluster='):
            CLUSTER = int(arg[9:])
            SetupProcessors(CLUSTER)
        if arg.startswith('-zones='):
            print str(arg[7:])
            z = arg[7:]
            ZONENAMES = z.split('!')
        if arg.startswith('-daemonip='):
            DAEMONIP = arg[10:]


    print ZONENAMES


    if not WORLDNAME:
        print "World not specified"
        sys.exit(-1)



    def main_is_frozen():
        return (hasattr(sys, "frozen") or # new py2exe
                hasattr(sys, "importers") # old py2exe
                or imp.is_frozen("__main__")) # tools/freeze

    def get_main_dir():
        if main_is_frozen():
            return os.path.dirname(sys.executable)
        return os.path.dirname(sys.argv[0])

    FROZEN = False
    if main_is_frozen():
        FROZEN = True
        maindir = get_main_dir()
        sys.path.append(maindir)
    else:
        if sys.platform == "win32":
            #os.chdir('c:/PrairieGames/mom_testing')
            #sys.path.insert(0,'c:/PrairieGames/mom_testing')
            pass
        else:
            topDir = os.path.split(os.path.split(os.path.abspath(os.path.dirname(__file__)))[0])[0]
            print "Setting working directory to %s ..."%topDir
            os.chdir(topDir)
            sys.path.insert(0,topDir)    # so it won't parse the whole path list everytime...


    from mud.world.defines import *
    from mud.gamesettings import *
    from mud_ext.server.serversettings import *
    #this is so we only need one binary version of dws
    if "FREE_" in WORLDNAME.upper():
        SetVersion(True)

    from mud.world.core import *
    if ("FREE_" in WORLDNAME.upper() or "PREMIUM_" in WORLDNAME.upper()):
        CoreSettings.PGSERVER = True
    else:
        CoreSettings.PGSERVER = False

    from mud.common.dbconfig import SetDBConnection

    #SOME DEFAULT STUFF THAT SHOULD BE SOMEWHERE ELSE

    MOTD = None
    ANNOUNCE = True
    MAXPARTY = 6
    SSH_ENABLED = False
    SSH_PORT = 6000
    SSH_IPS=['127.0.0.1']
    STATSERVERPASSWORD = "WHEE"

    try:
        exec("from serverconfig.%s import *"%WORLDNAME)
    except:
        print "Error reading server configuration"
        print_stack()
        print format_exc()
        sys.exit(-1)

    if len(ZONENAMES):
        STATICZONES = ZONENAMES

    if CLUSTER >=0:
        WORLDPORT+=CLUSTER

    try:
        CoreSettings.MOTD = MOTD
    except:
        print "No MOTD set"

    try:
        CoreSettings.WORLDTEXT = WORLDTEXT
    except:
        print "No World Text set"
        CoreSettings.WORLDTEXT = "%s World Server"%GAMENAME

    CoreSettings.MAXPARTY = MAXPARTY

    #cache the world graphic, if any
    WORLDPICPATH = "./serverconfig/%s.jpg"%WORLDNAME

    try:
        f = file(WORLDPICPATH,"rb")
        CoreSettings.WORLDPIC = f.read()
        f.close()
    except:
        print "No World Banner set"
        CoreSettings.WORLDPIC = None




    if CoreSettings.PGSERVER:
        print "Copying fresh baseline"
        d = "./%s/data/worlds/multiplayer/%s/cluster%i"%(GAMEROOT,WORLDNAME,CLUSTER)
        try:
            rmtree(d)
        except:
            pass
        os.makedirs(d)
        DATABASE = d+"/world.db"
        copyfile("./%s/data/worlds/multiplayer.baseline/world.db"%GAMEROOT,DATABASE)
    else:
        DATABASE = "./%s/data/worlds/multiplayer/%s/world.db"%(GAMEROOT,WORLDNAME)

    from mud.utils import getSQLiteURL
    SetDBConnection(getSQLiteURL(DATABASE),True)


    #--- Avatars
    from mud.world.theworld import World
    THEWORLD = World.byName("TheWorld")
    THEWORLD.multiName = WORLDNAME
    if CLUSTER!=-1:
        ZONESTARTPORT+=CLUSTER*100
    THEWORLD.zoneStartPort = ZONESTARTPORT
    THEWORLD.pwNewPlayer = PLAYERPASSWORD
    THEWORLD.staticZoneNames = STATICZONES

    if not CoreSettings.PGSERVER:
        THEWORLD.allowConnections = False
        THEWORLD.dbFile = "%s/%s/data/worlds/multiplayer/%s/world.db"%(os.getcwd(),GAMEROOT,WORLDNAME)


    #now replace to non-file friendly
    WORLDNAME = WORLDNAME.replace("_"," ")
    print THEWORLD.multiName

    from mud.world.newplayeravatar import NewPlayerAvatar,QueryAvatar
    import mud.world.playeravatar
    import mud.world.simavatar
    from   mud.common.avatar import RoleAvatar

    from mud.common.permission import User,Role


    #XXX clean this up, there is no reason for creating and destroying these, also are the roles bloating the db or are they destroyed?
    #destroy the new player user, and recreate
    try:
        user = User.byName("NewPlayer")
        user.destroySelf()
    except:
        pass

    newuser = User(name="NewPlayer",password="")
    newuser.addRole(Role.byName("NewPlayer"))

    try:
        user = User.byName("Query")
        user.destroySelf()
    except:
        pass

    newuser = User(name="Query",password="-")
    newuser.addRole(Role.byName("Query"))


    try:
        stats = User.byName("Stats")
        stats.destroySelf()
    except:
        pass

    stats = User(name="Stats",password=STATSERVERPASSWORD)
    stats.addRole(Role.byName("Stats"))

    NewPlayerAvatar.ownerPublicName = PUBLICNAME

    #--- Application
    from mud.server.app import Server


    THESERVER = Server(WORLDPORT)
    THESERVER.allowConnections = False
    THESERVER.throttleUsage = True
    if MAXPLAYERS == -1:
        MAXPLAYERS = 1024

    THESERVER.roleLimits["Player"]=MAXPLAYERS
    THESERVER.startServices()


    GAMEPROCESS = None

    ZONESSPAWNED = False


    #XXX starting zones simultaneously crashes

    ZONECOUNT = 0
    def LiveZoneCallback(zinst):
        global ZONECOUNT
        if ZONECOUNT == -1: #hack!
            return
        print zinst.name, "is live"
        ZONECOUNT+=1
        if ZONECOUNT == len(STATICZONES):
            ZONECOUNT = -1
            # if not CoreSettings.PGSERVER:
            #     THESERVER.allowConnections = True
            #     THEWORLD.allowConnections = True
            #     AnnounceWorld()
            # else:
            ConnectToDaemon()




    def SpawnZone(zoneName):
        print "####Spawning zone" + zoneName
        THEWORLD.startZoneProcess(zoneName,False)

    def SpawnZones():
        time = 0
        for x in xrange(0,len(STATICZONES)):
            reactor.callLater(time,SpawnZone,STATICZONES[x])
            time+=5


    def AnnounceSuccess(result,perspective):
        perspective.broker.transport.loseConnection()
        #from mud.common.gclog import gc_check
        #gc_check()
        #reactor.callLater(60,AnnounceWorld)

    def AnnounceConnected(perspective):
        pw = False
        if THEWORLD.pwNewPlayer:
            pw = True

        players = THESERVER.getActiveUsersByRole("Player")


        #we'll public player/passwords here for now, in the future this will be persistent

        #ZoneServer
        #NewPlayer
        users = []
        if not CoreSettings.PGSERVER:
            User.doPasswordHack = False
            for user in User.select():
                if user.name in ("ZoneServer","NewPlayer"):
                    continue
                users.append((user.name,user.password))
            User.doPasswordHack = True

        perspective.callRemote("WorldAvatar","announceWorld",WORLDNAME,WORLDPORT,pw,users,(players,MAXPLAYERS)).addCallbacks(AnnounceSuccess,AnnounceFailure,(perspective,))

    def AnnounceFailure(error):
        print "ANNOUNCE FAILURE!!!!!",error

    def AnnounceWorld():
        if not ANNOUNCE:
            return

        reactor.callLater(60,AnnounceWorld)

        username = "%s-World"%PUBLICNAME
        password = PASSWORD

        print "Announcing World"

        factory = pb.PBClientFactory()
        reactor.connectTCP(MASTERIP,MASTERPORT,factory)
        #the pb.Root() is a bit of a hack, I don't know how to get host address on server without
        #sending it, and I don't want to take the time to figure it out at the moment
        password = md5(password).digest()
        factory.login(UsernamePassword(username, password),pb.Root()).addCallbacks(AnnounceConnected, AnnounceFailure)

    #XXX Fix this, there must be a way to get the WAN address?
    import re
    import httplib

    _ip_regex = '([\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3})'
    def get_IP():
        # LAN-server-fix 
        if DO_LAN_SERVER_FIX: 
            return MASTERIP
        if MASTERIP == '127.0.0.1':
            return '127.0.0.1'
        conn = httplib.HTTPConnection("checkip.dyndns.org")
        conn.request("GET", "")
        res = conn.getresponse()
        if res.reason == "OK":
            ip = re.split(_ip_regex, res.read())[1]
        else:
            ip = None
        conn.close()
        return ip


    #daemon stuff

    DAEMON = None
    class DaemonMind(pb.Root):

        def __init__(self,world):
            global DAEMON
            DAEMON = self
            self.world = world
            self.world.daemon = self
            self.perspective = None

        def remote_setMasterAllianceInfo(self,info):
            from mud.world.alliance import Alliance
            Alliance.masterAllianceInfo = info

        def shipPlayerBuffer(self,result):
            from mud.worldserver.charutil import PLAYER_BUFFERS
            from mud.world.cserveravatar import AVATAR

            done = not len(PLAYER_BUFFERS)

            try:
                if len(PLAYER_BUFFERS):
                    pname,pbuffer,cbuffer,cvalues = PLAYER_BUFFERS.pop(0)
                    pbuffer = encodestring(dumps(pbuffer, 2))
                    if cbuffer:
                        cbuffer = encodestring(dumps(cbuffer, 2))


                    print "Sending Player/Character buffers: %s (%ik/%ik)"%(pname,len(pbuffer)/1024,len(cbuffer)/1024)
                    d = AVATAR.mind.callRemote("savePlayerBuffer",pname,pbuffer,cbuffer,cvalues) #xxx add callback/errback
                    d.addCallback(self.shipPlayerBuffer)
                    d.addErrback(self.shipPlayerBuffer)
            except:
                done = True #abort
                self.perspective.callRemote("printException",format_exc())

            if done:
                self.perspective.callRemote("playersExported")


        def remote_setDeathMarkerInfo(self,minfo):
            self.world.setDeathMarkerInfo(minfo)

        def remote_setCharacterInfos(self,cinfos):
            self.world.characterInfos = cinfos


        def remote_announceReboot(self,minutes):
            THESERVER.allowConnections = False
            self.world.isShuttingDown = True
            self.world.allowConnections = False
            msg = r'SYSTEM: This world will be rebooted in %i minutes.  Please camp now.\n'%minutes
            if minutes == 1:
                msg = r'SYSTEM: This world is about to reboot.  Please camp NOW!!!\n'

            for p in self.world.activePlayers:
                try:
                    p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,msg)
                except:
                    pass


        def remote_announceWorldToMaster(self):
            AnnounceWorld()


        def remote_sendWorldMsg(self, name, msg):
            for p in self.world.activePlayers:
                try:
                    p.sendSpeechText(RPG_MSG_SPEECH_WORLD,msg,name)
                except:
                    pass


        def remote_sendGuildMsg(self, name, msg, guildName):
            for p in self.world.activePlayers:
                if p.guildName != guildName:
                    continue
                try:
                    p.sendSpeechText(RPG_MSG_SPEECH_GUILD,msg,name)
                except:
                    pass


        def remote_sendAllianceMsg(self, name, msg, leader):
            for p in self.world.activePlayers:
                try:
                    if p.alliance.remoteLeaderName == leader:
                        p.sendSpeechText(RPG_MSG_SPEECH_ALLIANCE,msg,name)
                except:
                    pass


        def remote_announceShutdown(self,minutes):
            THESERVER.allowConnections = False
            self.world.allowConnections = False
            self.world.isShuttingDown = True
            msg = r'SYSTEM: This world will be shutdown in %i minutes.  Please camp now.\n'%minutes
            if minutes == 1:
                msg = r'SYSTEM: This world is about to shutdown.  Please camp NOW!!!\n'

            for p in self.world.activePlayers:
                try:
                    p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,msg)
                except:
                    pass

        def remote_shutdown(self):
            print self.perspective
            try:
                THESERVER.allowConnections = False
                self.world.shutdown()
            except:
                ex = format_exc()
                print ex
                self.perspective.callRemote("printException",ex)

            from mud.worldserver.charutil import PLAYER_BUFFERS
            print "Shutdown: %i player buffers to export"%len(PLAYER_BUFFERS)

            try:
                #we may have a bunch of player buffers to deal with
                self.shipPlayerBuffer(True)
            except:
                try:
                    ex = format_exc()
                    print ex
                    self.perspective.callRemote("printException",ex)
                finally:
                    raise "error shutting down world"


        def remote_resurrectionRequest(self,publicName,xpRecover,healthRecover,manaRecover,staminaRecover,tm,cname):
            for p in self.world.activePlayers:
                if p.zone and p in p.zone.players:
                    if p.party.members[0].name == cname and p.party.members[0].deathZone:
                        #got it and we are on this cluster
                        if p.resurrectionRequest:
                            timer = p.resurrectionRequest[0]
                            if curTime() - timer < 30:
                                return

                        p.resurrectionRequest = (curTime(),xpRecover,healthRecover,manaRecover,staminaRecover,cname)
                        p.mind.callRemote("resurrectionRequest",publicName,xpRecover)
                        return


        def remote_sendSysMsg(self, msg):
            for p in self.world.activePlayers:
                try:
                    p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,msg)
                except:
                    pass


        def remote_setTime(self, hour, minute):
            # Get a handle to the current world instance.
            world = self.world

            # Set the new time for the current world instance.
            world.time.hour = hour
            world.time.minute = minute

            # Send a message to all players in the current world instance and
            #  synchronize new time.
            for p in self.world.activePlayers:
                try:
                    p.mind.callRemote("syncTime",world.time.hour,world.time.minute)
                    p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,"\n<Scribe of Mirth> And time moves...\n\n")
                except:
                    pass


        def remote_setWorldAggro(self, aggroState):
            # Update the current world instances aggro state.
            self.world.aggroOn = aggroState


        def remote_receiveGMChat(self, name, msg):
            for p in self.world.activePlayers:
                if p.role.name == "Guardian" or p.role.name == "Immortal":
                    try:
                        p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,msg,name)
                    except:
                        pass



    def GotCSMind(result):
        from mud.world.cserveravatar import AVATAR
        AVATAR.mind = result


    def DaemonConnected(perspective):
        from mud.world.cserveravatar import CharacterServerAvatar
        csa = CharacterServerAvatar()
        world = World.byName("TheWorld")
        world.daemonPerspective = perspective
        DAEMON.perspective = perspective

        d = perspective.callRemote("setWorldPID",os.getpid(),WORLDPORT,str(world.genesisTime),csa)
        d.addCallback(GotCSMind)
        zpid = []
        zport = []
        zpassword = []

        for zname in STATICZONES:
            for z in world.liveZoneInstances:
                if zname == z.zone.name:
                    if z.pid == None:
                        print_stack()
                        print "AssertionError: z.pid is None!"
                        return
                    zpid.append(z.pid)
                    zpassword.append(z.password)
                    zport.append(z.port)

        #this also marks this cluster server as live
        perspective.callRemote("setZonePID",zpid,zport,zpassword)

        from mud.worldserver.charutil import SetClusterNum
        SetClusterNum(CLUSTER)
        THESERVER.allowConnections = True
        THEWORLD.allowConnections = True

    def DaemonFailure(error):
        print "Daemon Connection Error",error

    def ConnectToDaemon():
        print "Connecting to World Deamon at: %s"%DAEMONIP
        world = World.byName("TheWorld")

        factory = pb.PBClientFactory()
        reactor.connectTCP(DAEMONIP,7000,factory)
        world.daemonMind = mind = DaemonMind(world)
        password = md5("daemon").digest()
        factory.login(UsernamePassword(str(CLUSTER),password),mind).addCallbacks(DaemonConnected, DaemonFailure)


    def LaunchSuccess(result,perspective):
        print "####Launch succeeded"
        world = World.byName("TheWorld")
        ip = get_IP()
        if not ip:
            print_stack()
            print "AssertionError: Error getting WAN address!"
            return
        print "WAN IP found: ",ip
        #temporary, need to be able to set individual zone ip's
        world.zoneIP = ip
        perspective.broker.transport.loseConnection()
        if len(STATICZONES):
            SpawnZones()
        else:
            # if not CoreSettings.PGSERVER:
            #     THESERVER.allowConnections = True
            #     AnnounceWorld()
            # else:
            ConnectToDaemon()

    def LaunchWorldConnected(perspective):
        print "####Connected to Master Running launchWorld"
        perspective.callRemote("WorldAvatar","launchWorld",WORLDNAME,WORLDPORT).addCallbacks(LaunchSuccess,AnnounceFailure,(perspective,))

    def LaunchWorld():
        print "####Launching world"
        if not CoreSettings.PGSERVER:
            username=PUBLICNAME+"-"+"World"
            password=PASSWORD
            password = md5(password).digest()

            factory = pb.PBClientFactory()
            reactor.connectTCP(MASTERIP,MASTERPORT,factory)
            print "####Connecting to Master: " + str([MASTERIP, MASTERPORT])
            factory.login(UsernamePassword(username, password),pb.Root()).addCallbacks(LaunchWorldConnected, AnnounceFailure)
        else:
            world = World.byName("TheWorld")
            ip = get_IP()
            if not ip:
                print_stack()
                print "AssertionError: Error getting WAN address!"
                return
            print "WAN IP found: ",ip
            #temporary, need to be able to set individual zone ip's
            world.zoneIP = ip
            SpawnZones()


    def main():
        print "####Starting world server"
        from twisted.python import log

        LOG = not USE_WX

        if SSH_ENABLED:
            print "Security Warning: SSH Enabled on port %i for ip addresses:"%SSH_PORT,SSH_IPS
            from manhole import MakeFactory
            ips = SSH_IPS
            f= MakeFactory(ips,"me","me")
            reactor.listenTCP(SSH_PORT, f)


        if LOG:
            fname = "./logs/WorldServer.txt"
            if CLUSTER != -1:
                fname = "./logs/ZoneCluster%i.txt"%CLUSTER

            LOGFILE = file(fname,"w")
            log.startLogging(LOGFILE)


        #kickstart the heart
        print "####Getting world info"
        world = World.byName("TheWorld")
        world.frozen = FROZEN
        world.clusterNum = CLUSTER
        world.worldPort = WORLDPORT

        world.launchTime = curTime()
        world.liveZoneCallback = LiveZoneCallback
        world.startup()
        world.transactionTick()
        world.tick()

        reactor.callLater(0,LaunchWorld)
        reactor.addSystemEventTrigger('before', 'shutdown', world.shutdown)
        reactor.run()

        #world.shutdown()

        if LOG:
            LOGFILE.close()



    if __name__ == '__main__':
        #import profile
        #profile.runctx("main()","profile.prof",globals(),locals())
        #import hotshot
        #prof = hotshot.Profile("hotshot.prof")
        #prof.runctx("main()",globals(),locals())
        #prof.close()


        main()

except:
    print_stack()
    print format_exc()
    raw_input("Press Enter to terminate")
