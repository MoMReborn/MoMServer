# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import sys
from os import getcwd
sys.path.append(getcwd())

USE_WX = "-wx" in sys.argv

if sys.platform == 'win32' and not USE_WX:
    from twisted.internet.iocpreactor import install
else:
    USE_WX = True
    import wx
    from twisted.internet.wxreactor import install

install()

from mud.gamesettings import *
from config import *
from twisted.internet import reactor
from twisted.spread import pb
from twisted.cred.credentials import UsernamePassword
from serverdb import CreateDatabase,CharDB,ReplicateDB
from zlib import decompress
from traceback import print_stack,print_exc
from base64 import encodestring,decodestring
from cPickle import dumps,loads
from time import time
from md5 import md5
import random
from mud.server.config import LoadConfiguration
#import MySQLdb

if USE_WX:
    from gui import Setup
    app = Setup(reactor)
    reactor.registerWxApp(app)


CONFIG = {}
LoadConfiguration(CONFIG)

MASTER_IP = CONFIG["Master IP"]
MASTER_PORT = CONFIG["Master Port"]
MASTER_PASSWORD = CONFIG["Character Server Password"]

MYSQL_USER = CONFIG["MySQL User"]
MYSQL_PASSWORD = CONFIG["MySQL Password"]

CHARDB = CharDB("data/character/character.db")
CHARDB.checkIntegrity()

WORLD_CONNECTIONS = {}

IMMORTALS = [
]

GUARDIANS = [
]

WORLD_LOGINS = {}

#publicname -> times
ACTIVE_PLAYER_TIMES = {}
PLAYER_KICK_TIMES = {}
SUBNET_KICK_TIMES = {}
PLAYER_SUBNETS = {}
PLAYER_MUTE_TIMES = {}

class WorldConnection(pb.Root):
    def __init__(self,worldName,worldIP,port):
        self.worldName = worldName
        self.worldIP = worldIP
        self.worldPort = port
        self.perspective = None
        WORLD_CONNECTIONS[worldName]=self
        self.connect()
        
    def remote_deleteCharacter(self,pname,cname):
        return CHARDB.deleteCharacter(pname,cname)
        
    def remote_getCharacterInfos(self,publicName):
        return CHARDB.getCharacterInfos(publicName)
    
    def remote_getCharacterBuffer(self,publicName,characterName):
        b = CHARDB.getCharacterBuffer(publicName,characterName)
        if not b:
            return None
        #does str(bufferobject) mess up sometimes?
        buffer = encodestring(dumps(str(b), 2))
        return buffer
    
    
    def remote_savePlayerBuffer(self, publicName, pbuffer, cbuffer, cvalues, \
                                      logout=False, save=True):
        if save:
            wname = WORLD_LOGINS.get(publicName,None)
            
            if pbuffer:
                pbuffer = loads(decodestring(pbuffer))
            if cbuffer:
                cbuffer = loads(decodestring(cbuffer))
            
            if wname != self.worldName:
                print "Warning %s trying to save on none world login %s"% \
                    (publicName,self.worldName)
                return
            
            print "Saving buffer for %s:%s"%(publicName,cvalues[0])
            
            try:
                dbuffer = decompress(pbuffer)
            except:
                print_stack()
                print "Warning: %s bad zlib decompress on pbuffer"%publicName
                return
            
            try:
                dbuffer = decompress(cbuffer)
            except:
                print_stack()
                print "Warning: %s bad zlib decompress on cbuffer for %s"% \
                    (publicName,cvalues[0])
                return
            
            CHARDB.insertPlayerBuffer(publicName,pbuffer)
            CHARDB.insertCharacterBuffer(publicName,cvalues,cbuffer)
            CHARDB.commit(True)
        
        # Immediately remove this player from active players if logging
        #  out.
        if logout:
            del ACTIVE_PLAYER_TIMES[publicName]
    
    
    def remote_checkCharacterName(self, cname):
        cursor = CHARDB.conn.cursor()
        cursor.execute("SELECT id from cserver_character WHERE name LIKE '%s';"%(cname.upper()))
        exists = False
        if len(cursor.fetchall()):
            exists = True
        if not exists:
            #immediately dump into the record in case two people just happen to be trying this at the same time
            cursor.execute("INSERT INTO cserver_character VALUES(NULL,'%s');"%(cname.upper()))
        cursor.close()
        return exists
    
    
    def remote_renameCharacter(self, oldname, newname):
        try:
            cursor = CHARDB.conn.cursor()
            
            if oldname==newname:
                cursor.execute("UPDATE character_buffer SET rename=0 WHERE character_name LIKE '%s';"%oldname) 
                return 0
                
            try:
                cursor.execute("SELECT public_name FROM character_buffer WHERE character_name LIKE '%s';"%oldname)            
            except:
                cursor.close()
                return -1
            
            r = cursor.fetchone()
            
            if r == None:
                return -1
            
            pname = r[0]
            
            try:
                if ACTIVE_PLAYER_TIMES[pname][3] and time() - wtime < 110:
                    return -1
            except KeyError:
                pass
                
            return CHARDB.renameCharacter(oldname,newname)
        except:
            print_exc()
            return -1
        
        
        
    #might not be successful (perhaps player is already on world, etc)
    def playerInstalledResult(self,result):
        return result
        
    def errorInstallingPlayer(self,reason):
        return (False,reason)
    
    def kickPlayer(self,publicName):
        self.perspective.callRemote("kickPlayer",publicName)
        
        
    def installPlayer(self,publicName,premium):
        WORLD_LOGINS[publicName]=self.worldName
        b = CHARDB.getPlayerBuffer(publicName)
        
        if b:
            #does str(bufferobject) mess up sometimes?
            buffer = encodestring(dumps(str(b), 2))
        else:
            buffer = None
        
        code = 0
        if publicName in IMMORTALS:
            code = 2
        elif publicName in GUARDIANS:
            code = 1
            
        ginfo = CHARDB.getGuildInfo(publicName)
            
        try:
            d = self.perspective.callRemote("installPlayer",publicName,buffer,code,premium,ginfo) 
        except:
            del WORLD_CONNECTIONS[self.worldName]
            return (False,"Please try another world or wait a minute and try this world again.")
        d.addCallback(self.playerInstalledResult)
        d.addErrback(self.errorInstallingPlayer)
        return d
    
    def checkGenesisTimeResult(self,result):
        print result
        r, message = result
        if not r:
            del WORLD_CONNECTIONS[self.worldName]

    #todo, ADD A VERSION CHECK HERE FOR GENESISTIME on CHARACTER and WORLD DB!
    def connected(self,perspective):
        self.perspective = perspective
        d = perspective.callRemote("checkGenesisTime",CHARDB.genesisTime)
        d.addCallback(self.checkGenesisTimeResult)
        d.addErrback(self.failure)
        
        
    def failure(self,reason):
        #hm
        del WORLD_CONNECTIONS[self.worldName]


    def connect(self):
        factory = pb.PBClientFactory()
        reactor.connectTCP(self.worldIP,7001,factory)
        password = md5(CONFIG["World Password"]).digest()

        factory.login(UsernamePassword(CONFIG["World Username"], password),self).addCallbacks(self.connected, self.failure)
        
    #guilds
    
    def remote_getGuildCharacters(self,name,publicName,who):
        return CHARDB.getGuildCharacters(name,publicName,who)

    def remote_getGuildPublicName(self,name,publicName,characterName):
        return CHARDB.getGuildPublicName(name,publicName,characterName)
    
    def remote_createGuild(self,name,publicName,mnames):
        return CHARDB.createGuild(name,publicName,mnames)
    
    def remote_deleteGuild(self,name):
        return CHARDB.deleteGuild(name)

    def remote_addGuildMember(self,name,publicName,inviter):
        return CHARDB.addGuildMember(name,publicName,inviter)

    def remote_removeGuildMember(self,name,publicName):
        return CHARDB.removeGuildMember(name,publicName)
    
    def remote_promoteGuildMember(self,name,publicName,promoteName):
        return CHARDB.promoteGuildMember(name,publicName,promoteName)

    def remote_setGuildLeader(self,name,publicName,promoteName):
        return CHARDB.setGuildLeader(name,publicName,promoteName)

    def remote_demoteGuildMember(self,name,publicName,demoteName):
        return CHARDB.demoteGuildMember(name,publicName,demoteName)

    def remote_removeGuildMember(self,name,publicName,removeName):
        return CHARDB.removeGuildMember(name,publicName,removeName)

    def remote_setGuildMOTD(self,name,publicName,motd):
        return CHARDB.setGuildMOTD(name,publicName,motd)

    def remote_clearGuildMOTD(self,name,publicName):
        return CHARDB.clearGuildMOTD(name,publicName)

    def remote_getGuildRoster(self,name,publicName):
        return CHARDB.getGuildRoster(name,publicName)

    def remote_leaveGuild(self,name,publicName):
        return CHARDB.leaveGuild(name,publicName)
    def remote_disbandGuild(self,name,publicName):
        return CHARDB.disbandGuild(name,publicName)
    
    
    def remote_recordActivePlayers(self, worldname, players):
        for pname,cname,gname,zname in players:
            ACTIVE_PLAYER_TIMES[pname] = (self.worldName,cname,gname,zname,time())
        
        gplayers = {}
        t = time()
        for pname,info in ACTIVE_PLAYER_TIMES.iteritems():
            wname,cname,gname,zname,tm = info
            if t - tm < 80:
                gplayers[cname.upper()] = (cname,gname,wname,zname)
        
        remove = []
        muted = {}
        for pname,tm in PLAYER_MUTE_TIMES.iteritems():
            mt = tm - t
            if mt <= 0:
                remove.append(pname)
                continue
            muted[pname] = mt
        
        for p in remove:
            del PLAYER_MUTE_TIMES[p]
        
        return (gplayers,muted)
    
    
    def remote_contestLevelUpEvent(self,publicName,levelType,Level):
        return 0
        
        if MASTER_IP == "test.prairiegames.com":
            return 0
        
        try:
            if AwardTicket(publicName,levelType,Level):
                return 1
        except:
            print_exc()
        return 0
            
MASTERCONNECTION = None
class MasterConnection(pb.Root):
    def __init__(self):
        global MASTERCONNECTION
        MASTERCONNECTION = self
        self.perspective = None
    
    
    def remote_installPlayer(self, publicName, worldName, premium, subnet):
        # Store the subnet for the new player in the table of player subnets.
        PLAYER_SUBNETS[publicName] = subnet
        
        # Check if the player is under a temporary ban.
        if PLAYER_KICK_TIMES.has_key(publicName):
            t = PLAYER_KICK_TIMES[publicName] - time()
            t /= 60
            if int(t) > 0:
                return (False,"This account is temporarily banned.\\n\\n It will be available in %i minutes."%t)
        
        # Check if the player is under a temporary IP ban.
        elif SUBNET_KICK_TIMES.has_key(subnet):
            t = SUBNET_KICK_TIMES[subnet] - time()
            t /= 60
            if int(t) > 0:
                return (False,"Your IP is temporarily banned.\\n\\n It will be available in %i minutes."%t)
        
        try:
            t = time() - ACTIVE_PLAYER_TIMES[publicName][4]
            if t < 120:
                return (False,"This account is currently in use.\\n\\nIf you couldn't log out correctly, please wait %s seconds before trying to reconnect."%(120 - int(t)))
        except KeyError:
            pass
        
        if not WORLD_CONNECTIONS.has_key(worldName):
            (False,"Please select another world server.")
            
        ACTIVE_PLAYER_TIMES[publicName] = (worldName,"","","",time())
            
        return WORLD_CONNECTIONS[worldName].installPlayer(publicName,premium)
    
    
    def remote_announceWorld(self,worldName,worldIP,port):
        if not WORLD_CONNECTIONS.has_key(worldName):
            #connect to world
            WorldConnection(worldName,worldIP,port)
    
    
    def connected(self,perspective):
        self.perspective = perspective
        #perspective.callRemote("CharacterAvatar","sayHi")
        print "Character Server is up!"
    
    
    def failure(self,reason):
        print reason
    
    
    def connect(self):
        password = md5(MASTER_PASSWORD).digest()
        factory = pb.PBClientFactory()
        reactor.connectTCP(MASTER_IP,MASTER_PORT,factory)
        factory.login(UsernamePassword("CharacterServer-CharacterServer", password),self).addCallbacks(self.connected, self.failure)
        print "Connecting to Master Server..."



#GM Connection

class GMConnection(pb.Root):
    def __init__(self):
        self.perspective = None
            
    def connected(self,perspective):
        self.perspective = perspective
        
    def failure(self,reason):
        print reason
       
    def connect(self):
        factory = pb.PBClientFactory()
        reactor.connectTCP(GMSERVER_IP,GMSERVER_PORT,factory)
        password = md5(GMSERVER_PASSWORD).digest()
        factory.login(UsernamePassword("CharacterServer-CharacterServer", password),self).addCallbacks(self.connected, self.failure)
       
    def remote_gmRenameCharacter(self,oldname):
        
        cursor = CHARDB.conn.cursor()
        try:
            cursor.execute("SELECT public_name FROM character_buffer WHERE character_name LIKE '%s';"%oldname)            
        except:
            cursor.close()
            return -2
        
        r = cursor.fetchone()
        
        if r == None:
            return None
        
        pname = r[0]

        cursor.execute("UPDATE character_buffer SET rename=2 WHERE character_name LIKE '%s';"%oldname)            

        return 1#CHARDB.renameCharacter(oldname,newname)
        
        
    def remote_gmKickCharacter(self,cname,minutes):
        cursor = CHARDB.conn.cursor()
        try:
            cursor.execute("SELECT public_name FROM character_buffer WHERE character_name LIKE '%s';"%cname)            
        except:
            cursor.close()
            return None
        
        r = cursor.fetchone()
        
        if r == None:
            return None
        
        pname = r[0]
        
        PLAYER_KICK_TIMES[pname] = time()+(minutes*60)
        
        try:
            SUBNET_KICK_TIMES[PLAYER_SUBNETS[pname]] = time()+(minutes*60)
        except KeyError:
            pass
        try:
            wname,cname,gname,zname,wtime = ACTIVE_PLAYER_TIMES[pname]
            if time() - wtime < 120:
                wconn = WORLD_CONNECTIONS[wname]
                wconn.kickPlayer(pname)
                return (cname,pname,minutes,wname)
        except KeyError:
            pass
        
        return (cname,pname,minutes,"")

    def remote_gmMuteCharacter(self,cname,minutes):
        cursor = CHARDB.conn.cursor()
        try:
            cursor.execute("SELECT public_name FROM character_buffer WHERE character_name LIKE '%s';"%cname)            
        except:
            cursor.close()
            return None
        
        r = cursor.fetchone()
        
        if r == None:
            return None
        
        pname = r[0]
        
        PLAYER_MUTE_TIMES[pname] = time()+(minutes*60)
        
        return (cname,pname,minutes,"")

    def remote_gmUnmuteCharacter(self,cname):
        cursor = CHARDB.conn.cursor()
        try:
            cursor.execute("SELECT public_name FROM character_buffer WHERE character_name LIKE '%s';"%cname)            
        except:
            cursor.close()
            return None
        
        r = cursor.fetchone()
        
        if r == None:
            return None
        
        pname = r[0]
        
        try:
            del PLAYER_MUTE_TIMES[pname]
        except:
            pass
        
        return (cname,pname)


    def remote_gmGetCharacterInfo(self,cname):
        cursor = CHARDB.conn.cursor()
        try:
            cursor.execute("SELECT public_name FROM character_buffer WHERE character_name LIKE '%s';"%cname)            
        except:
            cursor.close()
            return None
        
        r = cursor.fetchone()
        
        if r == None:
            return None
        
        pname = r[0]
        
        cursor.execute("SELECT character_name FROM character_buffer WHERE public_name LIKE '%s';"%pname)
        
        characters = cursor.fetchall()
        
        cursor.close()

        active = None
        try:
            wname,cname,gname,zname,wtime = ACTIVE_PLAYER_TIMES[pname]
            active = (wname,time()-wtime)
        except KeyError:
            pass
        subnet = "No Subnet Information"
        try:
            subnet = PLAYER_SUBNETS[pname]
        except KeyError:
            pass
            
            
        return (cname,pname,characters,active,subnet)
        
    def remote_gmWho(self,whoworld):
        who = {}
        for pname,info in ACTIVE_PLAYER_TIMES.iteritems():
            wname,cname,gname,zname,wtime = info
            if whoworld and whoworld.upper() != wname.upper():
                continue
            
            t = time()-wtime
            if t > 120:
                continue
            
            if not who.has_key(wname):
                who[wname]={}
                
            who[wname][pname]=cname
            
        return who

    def remote_gmAwardTicket(self,pname):
        return AwardTicket(fname)
        
        
"""
def AwardTicket(pname,levelType="",level=None):

    return ""

    try:
        connection = MySQLdb.connect(host="localhost", user=MYSQL_USER, passwd=MYSQL_PASSWORD, db="minions" ) 
    except:
        print_exc()
        return ""
        
    cursor = connection.cursor()
    
    cursor.execute("SELECT forumname FROM minions_contestentry WHERE publicname LIKE '%s';"%pname) 
    
    if not len(cursor.fetchall()):
        return ""
        
    
    if levelType:
        cursor.execute("SELECT level FROM minions_contestentry_level WHERE publicname LIKE '%s' AND leveltype LIKE '%s' AND level=%i;"%(pname,levelType,level))
        if len(cursor.fetchall()):
            #already awarded
            return ""
        
        #store level complete
        cursor.execute("INSERT INTO minions_contestentry_level (publicname,leveltype,level) VALUES ('%s','%s',%i);"%(pname,levelType,level))
        
        print "%s has been awarded a %s %i raffle ticket"%(pname,levelType,level)
        
    else:
        print "%s has been awarded a raffle ticket"%pname
    
        
    #got one!
    cursor.execute("UPDATE minions_contestentry SET tickets=tickets+1 WHERE publicname LIKE '%s';"%pname)
    
    connection.commit()

    cursor.close()
    connection.close()
            
    return pname
"""


def ReplicateDatabases():
    reactor.callLater(60*60,ReplicateDatabases) #every hour
    ReplicateDB(WORLD_CONNECTIONS.values(),MASTERCONNECTION.perspective)

mc = MasterConnection()
mc.connect()

gm = GMConnection()
gm.connect()

reactor.callLater(60*60,ReplicateDatabases)
    
    
reactor.run()

cursor = CHARDB.conn.cursor()
cursor.execute("END TRANSACTION;")
cursor.close()
CHARDB.conn.close()



    


"""
the character server holds all player information, free and otherwise... 

Master Server Requirements

When being forwarded to a official server, use the character server connection to make sure characters are installed
on the destination world before forwarding... Master and Character Server should be on same box
It also generates a temporary password, for logging into world... the player no longer needs to remember a per
world password for official servers... and this adds a security layer (no direct IP connection)... official worlds
are always "password protected"... the master server also needs to keep a list of official worlds and disallow
people from making official worlds named similar

Character Server Requirements

a connection to the official world.db for checking spawn names, and things
a list of all official world servers + ports for logging into the world's character server avatar 
a connection to the master server for various stuff

We can probably delete orphaned items here without additional logic on the world server.. items need a masterId from the character server added

Official World Server (Free and Premium) Requirements

A way to completely delete a player from the world (will be injected from the Character Server upon connection)
Character Creation on the World Server needs to check with the character server for name (that's about it)
At intervals and when a player leaves a world serialization and upload to main character server
Item craziness, notification to character server when items are deleted

"""


