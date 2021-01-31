# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#there is probably a better way of doing this (change from Python 2.4->2.5)
import sys, os
sys.path.append(os.getcwd())

USE_WX = False
if "-wx" in sys.argv:
    USE_WX = True

if sys.platform == 'win32' and not USE_WX:
    from twisted.internet.iocpreactor import install
else:
    import wx
    from twisted.internet.wxreactor import install
    
install()

from mud.server.config import ConfigureServer, LoadConfiguration
import traceback

from datetime import datetime

sys.argv.append('database=data/master')

ConfigureServer("master.db")


from mud.masterserver.masterdb import *
from mud.common.avatar import Avatar
from mud.world.shared.worlddata import WorldConfig, WorldInfo
from mud.common.permission import BannedIP
from newplayeremail import ConfigureEmail
from mud.gamesettings import GAMEROOT,DO_WAN_SERVER_FIX,GL_ANNOUNCE_IP
from mud.world.defines import *

WORLDPASSWORDS = {}
ACTIVEPLAYERS = {}

CONFIG = {}
LoadConfiguration(CONFIG)
ConfigureEmail(CONFIG)

TRANSACTION = None
BACKUPTICK = 15

def CheckDB():
    print "Checking Database Integrity"
    conn = Persistent._connection.getConnection()
    cursor = conn.cursor()

    cursor.execute("PRAGMA integrity_check;")
    if cursor.fetchone()[0]!='ok':
        raise "Master Database Error"
    print "... ok ..."
    
    cursor.close()


def TransactionTick(exiting=False):
    global TRANSACTION
    global BACKUPTICK
    
    from mud.common.persistent import Persistent
    conn = Persistent._connection.getConnection()
    cursor = conn.cursor()
    if TRANSACTION:
        print "-------------> Commiting Database <-------------"
        cursor.execute("END;")
        
    TRANSACTION = False
    
    if not exiting:
        cursor.execute("BEGIN;")
        TRANSACTION = True
        
        reactor.callLater(60, TransactionTick)
    
        
        BACKUPTICK-=1
        if not BACKUPTICK:
            print "Backing up master database"
            BackupMaster("./data/master/master.db")
            BACKUPTICK= 60 #once every 60 minutes

    cursor.close()
    
LASTBACKUPFILE = None
def BackupMaster(worldfile):
    global LASTBACKUPFILE
    
    import shutil
    n = datetime.now()
    s = n.strftime("%B_%d_%Y")
    d, f = os.path.split(worldfile)
    
    f, ext = os.path.splitext(f)
    
    backfolder = d+"/"+s
    if not os.path.exists(backfolder):
        os.makedirs(backfolder)
        
    x = 1
    while True:
        backupfile = backfolder+"/"+"%s_backup_%i%s"%(f, x, ext)
        if os.path.exists(backupfile):
            x+=1
            continue
        
        LASTBACKUPFILE = backupfile
        shutil.copyfile(worldfile, backupfile)
        break
        

        
#--- World Avatar (this is hooked to player login, decouple?

class WorldAvatar(Avatar):
    """The Master's World Avatar, change pw, announce, etc"""
    def __init__(self, username, role, mind):
        Avatar.__init__(username, role, mind)
        
        # Todo: only allow one login to world at a time!
        self.username = username
        self.mind = mind
        #self.world = World.byName(username)
        
    #we should be handing back a temporary password here
    #the idea is to for people who may be sharing accounts, to stop them simultaneously launching worlds
    def perspective_launchWorld(self, wname, wport):
        account = Account.byPublicName(self.username)
        
        try:
            world = World.byName(wname)
        except:
            return (-1, "Error!", None, None)
        
        if world not in account.worlds:
            return (-1, "Error!", None, None)
            
        #do we want to do this?
        """
        if world.verified:
            t = mx.DateTime.now() - world.announceTime
        
            if t.minute < 6:
                return (-1,"Please wait a few minutes before relaunching world.")
        """
        
        #this makes it so we don't get enumerated by enumworlds
        #we'll set the right time on announce
        world.announceTime = datetime(1973, 1, 1)
        world.announcePort = wport
        
        return (0, "Ok.", wname, world.announcePort)


    #to add player count, etc
    def perspective_announceWorld(self, wname, port, pw, users, players=(0, 0)):
        
        try:
            world = World.byName(wname)
        except:
            return (-1, "Error")
        
            
            
        #once you actually announce world, verified
        world.verified = True
        world.announceTime = datetime.now()
        host = self.mind.broker.transport.getPeer()
        #fix me
        #WAN Server Fix 
        if DO_WAN_SERVER_FIX: 
            world.announceIP = GL_ANNOUNCE_IP 
        else: 
            world.announceIP = host.host
        world.announcePort = port

        if CHARSERVER_MIND:
            if "Premium " in wname or "Free " in wname:
                CHARSERVER_MIND.callRemote("announceWorld", wname, world.announceIP, port)

        
        if pw:
            #we could store password on master, if we wanted to
            world.playerPassword = "PW"
        else:
            world.playerPassword = ""
        
        WORLDPASSWORDS[wname]=users
        ACTIVEPLAYERS[wname]=players
        
        return (0, "Success")
        
#--- New World Avatar


from random import choice
import string
def GenPasswd(length=8, chars=string.letters):
    return ''.join([choice(chars) for i in xrange(length)])

#also delete
class NewWorldAvatar(Avatar):
    
    def __init__(self, username, role, mind):
        Avatar.__init__(self, username, role, mind)
        self.username = username
    
    
    def perspective_newWorld(self, wconfig, allowGuests=False):
        account = Account.byPublicName(self.username)
        
        if "Premium " in wconfig.worldName or "Free " in wconfig.worldName:
            if self.username != CONFIG["World Username"]: 
                return (-1, "The words 'Premium' and 'Free' cannot be used in a world name.  Please choose another name", None)
                
                    
        
        #does world already exist?
        try:
            world = World.byName(wconfig.worldName)
        except:
            pass
        else:
            return (-1, "World Name is taken, choose another.", None)
        
        try:    
            World(name=wconfig.worldName, announcePort=wconfig.worldPort, maxLiveZones = wconfig.maxLiveZones, 
            maxLivePlayers = wconfig.maxLivePlayers, allowGuests=allowGuests, playerPassword = wconfig.playerPassword, 
            zonePassword = wconfig.zonePassword, account=account, demoWorld = wconfig.demoWorld)
        except:
            return (-1, "Error creating world, Please try again.", None)
            
        
        return (0, "World Created", wconfig.worldName)

 
    def perspective_deleteWorld(self, wname):
        
        account = Account.byPublicName(self.username)

        try:
            world = World.byName(wname)
        except:
            return (-1, "Error", None)
            
        if not world in account.worlds:
            return (-1, "Error", None)
            
        world.destroySelf()
        return (0, "World deleted.", wname)
        
        
        
from random import choice
import string
def GenRegKey(length=16, chars=string.letters):
    s = ''.join([choice(chars) for i in xrange(length)])
    t=s[:4]+"-"+s[4:8]+"-"+s[8:12]+"-"+s[12:]
    return t.upper()
        
#handle account authorization
class RegistrationAvatar(Avatar):
    
    def perspective_checkKey(self,account,regkey):
        try:
            account = Account.byPublicName(account)
        except:
            return (-1, "Invalid Account")
        
        #add me
        #if account.regkey != regkey:
        #    return (-1, "Invalid Registration Key")
        
        if not account.hasProduct("MOM"):
            return (-1, "Our records do not currently show your Premium Edition purchase.\n\nIf it has been over 24 hours since your purchase, please contact support.")
        
        return (0,"Success!")    
    
    def perspective_submitKey(self, regkey, emailaddress, publicName, fromProduct=""):
        emailaddress = emailaddress.lower()
        while 1:
            regkey = GenRegKey()
            
            #regkey isn't used now for registration, will be when we go closed
            
            #is this a valid key?
            try:
                key = RegKey.byKey(regkey)
            except:
                break
            
            #return (-1,"Invalid Key",None)
        
        #if we already have an Account with the regkey, the regkey is in use
        try:
            user = Account.byRegkey(regkey)
        except:
            pass
        else:
            return (-1, "Invalid Key", None)
        
        try:
            a = Account.byEmail(emailaddress)
            return (-1, "That email address has already been used to register.", None, None)
        except:
            pass
        
                
        conn = Persistent._connection.getConnection()
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM user WHERE name LIKE '%s';"%publicName)
        r = cursor.fetchall()
        cursor.close()
        
        if len(r):
            return (-1, "That public name is taken.\\n\\nPlease choose another name.", None, None)
            
        
        #if we already have a User with this regkey, the key is in use
        try:
            user = User.byName(publicName)
        except:
            pass
        else:
            return (-1, "That public name is taken.\\n\\nPlease choose another name.", None, None)
            
        password = GenPasswd().upper()
        key = RegKey(key=regkey)
                
        user = User(name=publicName, password = password)
        user.addRole(Role.byName("Player"))
        user.addRole(Role.byName("World"))
        
        account = Account(regkey=key.key, publicName=publicName, email=emailaddress, password=password)
        
        if GAMEROOT == "minions.of.mirth":
            fromProduct = ""
            try:
                pe = ProductEmail.byEmail(emailaddress)
                account.addProduct(pe.product.upper())
                fromProduct=pe.product.upper()
                pe.destroySelf()
            except:
                pass
        else:
            fromProduct = "MOM"
            account.addProduct("MOM")
            
        if not USE_WX:
            from newplayeremail import NewPlayerEmail
            import thread
            thread.start_new(NewPlayerEmail, (emailaddress, publicName, password, regkey, fromProduct))
        
        if RPG_SECURE_REGISTRATION:
            return(0, "Your password has been emailed to you. Please look into your mailbox and use your username and password to login.\\n\\nThank you for registering.", "", regkey)
        else:
            return(0, "Your password is:\\n\\n%s\\n\\nPlease store this for reference.\\nIt has also been emailed to you."%password, password, regkey)

    def perspective_requestPassword(self, publicname, email):
        from newplayeremail import LostPasswordEmail
        
        try:
            a = Account.byPublicName(publicname)
        except:
            return(-1, "Unknown Public Name, please check spelling and case.\\n\\n  If you continue to have problems, please contact support.")
        
        if a.email.lower() != email.lower():
            return(-1, "Email doesn't match, please make sure to specify the email used when registering.\\n\\n  If you continue to have problems, please contact support.")
        
        if not USE_WX:   
            import thread
            thread.start_new(LostPasswordEmail, (a.email, a.publicName, a.password))
        
        return(0, "Your password has been sent to the email address specified.")
        

class PlayerAvatar(Avatar):
    def __init__(self, username, role, mind):
        Avatar.__init__(self, username, role, mind)
        self.username = username
        self.role = role
        self.mind = mind
        
    def playerSubmitted(self, result):
        return result
                
    def playerSubmissionError(self, reason):
        return (False, "This world is temporarily unavailable please try again shortly.")
        
    def perspective_submitPlayerToWorld(self, worldName):
        if not CHARSERVER_MIND:
            return (False, "Character Server is down.")

        
        u = User.byName(self.username)
        if u.banLevel >= 2:
            return (False, "This account is banned.")
            
        if u.banLevel ==1 and ("Premium " in worldName or "Free " in worldName):
            return (False, "This account is banned.")
        
        subnet = ""
        if self.mind: #grrrrr, old client and client dependency on sending this
            ip = self.mind.broker.transport.getPeer()
            subnet=ip.host[:ip.host.rfind('.')]
            
            try:
                bi = BannedIP.byAddress(subnet)
                return (False, "The IP you are connected from is banned.")
            except:
                pass

        
        premium = False
        account = Account.byPublicName(self.username)
        
        account.lastActivityTime = datetime.now()
        
        if account.hasProduct("MOM"):
            premium = True
            
        if "Premium " in worldName and not premium:
            return (False, "This server requires the Premium Edition.")
        
        d = CHARSERVER_MIND.callRemote("installPlayer", self.username, worldName, premium, subnet)
        d.addCallback(self.playerSubmitted)
        d.addErrback(self.playerSubmissionError)
        return d

    def perspective_getPatchServerInfo(self, platform, version):
        
        if platform == "mac" and version == "demo":
            return (0, CONFIG["Patch Server Demo"], None)
        if platform == "windows" and version == "demo":
            return (0, CONFIG["Patch Server Demo"], None)
        
        #testing
        
        #do we have access?
            
        account = Account.byPublicName(self.username)
        
        if not account.hasProduct("MOM"):
            #print "WARNING: Account %s trying to get testing patcher information without MOM product"%self.username
            return (-1, "Our records do not currently show your Premium Edition purchase.\n\nIf it has been over 24 hours since your purchase, please contact support.")
        
        if platform == "mac" and version == "testing":
            return (0, CONFIG["Patch Server Premium"], CONFIG["Patch Server Demo"])
        
        if platform == "windows" and version == "testing":
            return (0, CONFIG["Patch Server Premium"], CONFIG["Patch Server Demo"])

        return (-1, "Unknown Patcher Information")
        

#--- Enum Worlds Avatar (may want to make another player specific avatar)
class EnumWorldsAvatar(Avatar):

    def __init__(self, username, role, mind):
        Avatar.__init__(self, username, role, mind)
        self.username = username

    def perspective_requestWorldPassword(self, worldName):
        passwords = WORLDPASSWORDS.get(worldName)
        if not passwords:
            return (-1, "Please try again later.")
        for p in passwords:
            if p[0]==self.username:
                return (0, "Your password for this world is %s."%p[1], p[1], worldName)
            
        return (-1, "You are not registered on this world or the world hasn't updated your password yet.")
        

    def perspective_worldExists(self, worldName):
        if self.username == "EnumWorlds":
            return
        try:
            w = World.byName(worldName)
        except:
            return 0
        return 1
        
    def perspective_enumMyWorlds(self, demo=False, testing=False):
        if self.username == "EnumWorlds":
            return

        account = Account.byPublicName(self.username)
        worlds = []
        for w in account.worlds:
            if bool(w.demoWorld) == bool(demo):
                if testing and not w.allowGuests:
                    continue
                if not testing and w.allowGuests:
                    continue
                
                worlds.append(w.name)
                
        return worlds
            
    
    def perspective_enumLiveWorlds(self, launching = False, demo = False, wm = False, testing = False):
        """Enumerated verified, and active worlds"""
        
        
        winfos = []
        worlds = list(World.select())
        for w in worlds:
            #if not w.verified:
                #world is not verfied, not valid until verified
            #    continue
            
            #if bool(demo) != bool(w.demoWorld):
            #    continue
            
            if testing and not w.allowGuests:
                continue
            
            if not testing and w.allowGuests:
                continue
            
            if not launching:
                t = datetime.now() - w.announceTime
                
                if t.days or t.seconds/60 > 2:
                #no announce within 2 minutes, counts as not being up
                    continue
                    
            else:
                if w.announceTime != datetime(1973, 1, 1):
                    t = datetime.now() - w.announceTime
                    
                    if t.days or t.seconds/60 > 2:
                    #no announce within 2 minutes, counts as not being up
                        continue
                
            wi = WorldInfo()
            wi.worldName = w.name
            wi.worldIP = w.announceIP
            wi.worldPort = w.announcePort
            if w.playerPassword:
                wi.hasPlayerPassword = True
            if w.zonePassword:
                wi.hasZonePassword = True
                
            wi.allowGuests = w.allowGuests
            p = ACTIVEPLAYERS.get(w.name)
            if p:
                wi.numLivePlayers = p[0]
                wi.maxPlayers = p[1]
            else:
                wi.numLivePlayers = 0
                wi.maxPlayers = 0
                
            wi.numLiveZones = 0
            
            winfos.append(wi)
        return winfos
    

#Character Server
CHARSERVER_MIND = None
class CharacterAvatar(Avatar):
    def __init__(self, username, role, mind):
        global CHARSERVER_MIND
        Avatar.__init__(self, username, role, mind)
        self.username = username
        self.role = role
        self.mind = mind
        CHARSERVER_MIND = mind

    def perspective_getLastBackupFile(self):
        return LASTBACKUPFILE
        
        
    def logout(self):
        global CHARSERVER_MIND
        CHARSERVER_MIND = None
        
        
#--- Master Server

from twisted.internet import reactor
from mud.server.app import Server


if USE_WX:
    from gui import Setup
    app = Setup(reactor)
    reactor.registerWxApp(app)


print "Master Server"
print "->Initializing"

from mud.common.permission import Role, User, TablePermission, ColumnPermission
from mud.common.avatar import RoleAvatar


def ConfigureSettings():
    print "Configuring Settings"
    #World User (clean this up.. for instance, if we change the username we'll leave row crumbs)
    try:
        user = User.byName(CONFIG["World Username"])
    except:
        user = User(name=CONFIG["World Username"], password = "")
        key = RegKey(key=CONFIG["World Username"]+"!")
        account = Account(regkey=key.key, publicName=CONFIG["World Username"], email="", password="")
        account.addProduct("MOM")
        user.addRole(Role.byName("Player"))
        user.addRole(Role.byName("World"))
        #fix me, this shouldn't really be here... and allowGuests is used for testing worlds
        World(name="Premium MMORPG", announcePort=int(CONFIG["Default World Port"]), account=account, allowGuests=True,maxLivePlayers=-1,maxLiveZones=-1,demoWorld = False)

        
    user.password = CONFIG["World Password"]
    account = Account.byPublicName(user.name)
    account.password = user.password
    
    cserver = User.byName("CharacterServer")
    cserver.password = CONFIG["Character Server Password"]
    
    
server = Server(CONFIG["Master Port"])
server.startServices()

from telnetmanhole import MakeFactory
from twisted.application import app, service, strports
ips = ["127.0.0.1"]
f= MakeFactory(ips, CONFIG["Manhole Username"], CONFIG["Manhole Password"])
reactor.listenTCP(CONFIG["Manhole Port"], f)

#from webserver import MakeWebServer
#MakeWebServer()

from mud.common.persistent import Persistent
Persistent._connection.getConnection().text_factory = lambda x: unicode(x, "utf-8", "ignore")

CheckDB()

ConfigureSettings()

TransactionTick()

print "->Server is up"

reactor.run()

TransactionTick(True)
