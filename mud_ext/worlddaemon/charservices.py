# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#character services provided by worlddaemon

from twisted.cred.portal import Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.internet import reactor
from zope.interface import implements
from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.portal import IRealm
import os,imp
from twisted.python import components, failure, log

import math
try:
    import win32api,win32con,win32event
except ImportError:
    win32api = win32con = win32event = None
import time,traceback
import os,sha

import zlib
from sqlite3 import dbapi2 as sqlite

#publicname->pbuffer
PBUFFERS = {}

#publicname->(code,premium)
PINFOS = {}

#publicname->cbuffer
CBUFFERS = {}


#CSERVER ------> WORLDSERVER

class CServerAvatar(pb.Avatar):
    genesisTime = None
    #cluster num -> 
    worldCSAvatars = {}
    
    def __init__(self):
        self.repfiles = {}
        
    def perspective_kickPlayer(self,publicName):
        for avatar in CServerAvatar.worldCSAvatars.itervalues():
            avatar.callRemote("kickPlayer",publicName)
        
    def perspective_checkGenesisTime(self,genesisTime):
        if CServerAvatar.genesisTime == genesisTime:
            return (True,"Genesis Time Matches")
        return (False, "Genesis Time Mismatch: Character Server %s : World Server %s"%(genesisTime,CServerAvatar.genesisTime))

    def perspective_installPlayer(self,publicName,buffer,code,premium,guildInfo):
        from worldservices import ZoneClusterAvatar
        
        if not len(CServerAvatar.worldCSAvatars):
            raise "World maybe in a reboot."
            
        
        PBUFFERS[publicName]=buffer
        PINFOS[publicName]=(code,premium)
        
        #as the dst zonecluster depends on the realm log zone, and we have no idea what realm and thus
        #what zone the player will be logging into, just use the first zone cluster for the login process
        #iterative design flaw or feature, you decide
        avatar = CServerAvatar.worldCSAvatars[0]
        return avatar.callRemote("installPlayer",publicName,buffer,code,premium,guildInfo)
    
    def perspective_beginReplication(self,filename):
        #print "Begin Replication",filename
        try:
            self.repfiles[filename].close()
        except:
            pass
            
        d,f = os.path.split(filename)
        
        rdir = "./replication/"+d
        if not os.path.exists(rdir):
            os.makedirs(rdir)
        
        f = "./replication/"+filename
            
        self.repfiles[filename] = file(f,"wb")
        
        
    def perspective_receiveBuffer(self,filename,buffer,digest):
        f = self.repfiles[filename]
        
        f.write(buffer)
        
        if digest:
            f.close()
            del self.repfiles[filename]
            f = file("./replication/"+filename,"rb")
            buffer = f.read()
            f.close()
            m = sha.new()
            m.update(buffer)
            if m.hexdigest() != digest:
                print "File Replication Error!",filename
                os.remove("./replication/"+filename)
            else:
                print "File Replication Successful",filename


 
#CSERVER <----- WORLDSERVER, gets handed to WORLDSERVER
class CServerMind(pb.Root):
    
    worldCSMinds = {}
    
    #the mind of the actual character off in prairie games, inc land
    themind = None
    
    def __init__(self):
        pass
        
    def remote_deleteCharacter(self,pname,cname):
        return CServerMind.themind.callRemote("deleteCharacter",pname,cname)
        
    def remote_getCharacterInfos(self,publicName):
        return CServerMind.themind.callRemote("getCharacterInfos",publicName)
    
    def gotCharacterBuffer(self,cbuffer,publicName):
        CBUFFERS[publicName]=cbuffer
        return cbuffer
    
    def remote_getCharacterBuffer(self,publicName,characterName):
        d = CServerMind.themind.callRemote("getCharacterBuffer",publicName,characterName)
        d.addCallback(self.gotCharacterBuffer,publicName)
        return d
    
    
    def remote_recordActivePlayers(self, worldname, players):
        #hm, this happens at book up, should probably catch on world server
        if not CServerMind.themind:
            return ({},{})
        return CServerMind.themind.callRemote("recordActivePlayers",worldname,players)
    
    
    def remote_savePlayerBuffer(self, publicName, pbuffer, cbuffer, cvalues, \
                                      logout=False, save=True):
        PBUFFERS[publicName] = pbuffer
        CBUFFERS[publicName] = cbuffer
        return CServerMind.themind.callRemote("savePlayerBuffer",publicName, \
            pbuffer,cbuffer,cvalues,logout,save)
    
    
    def remote_renameCharacter(self,oldname,newname):
        return CServerMind.themind.callRemote("renameCharacter",oldname,newname)
        
    def remote_checkCharacterName(self,cname):
        print "####Checking character name"
        return CServerMind.themind.callRemote("checkCharacterName",cname)

    def playerTransferredAndInstalled(self,result,wip,wport,zport,zpassword):
        if not result[0] or not result[1]:
            traceback.print_stack()
            print "AssertionError: result has an empty value!"
            return
        wpassword = result[1]
        return (wip,wport,wpassword,zport,zpassword)

    def playerTransfered(self,result,avatar,publicname,charname,remoteLeaderName,wip,wport,zport,zpassword):
        if not result[0] or not result[1]:
            traceback.print_stack()
            print "AssertionError: result has an empty value!"
            return
        cbuffer = CBUFFERS[publicname]
        d = avatar.callRemote("transferPlayerInstalled", publicname, charname, cbuffer, remoteLeaderName)
        d.addCallback(self.playerTransferredAndInstalled,wip,wport,zport,zpassword)
        return d

    def remote_zoneTransferPlayer(self,publicname,pbuffer,charname,cbuffer,zonename,cvalues,remoteLeaderName,guildInfo):
        from worldservices import ZoneClusterAvatar
        if not cbuffer:
            traceback.print_stack()
            print "AssertionError: cbuffer is empty!"
            return
        
        #whenever we're not entering world we'll save (cvalues is NULL in this case)
        if cvalues:
            try:
                self.remote_savePlayerBuffer(publicname,pbuffer,cbuffer,cvalues)
            except:
                traceback.print_exc()
        
        if pbuffer:
            PBUFFERS[publicname]=pbuffer
        else:
            pbuffer = PBUFFERS[publicname]
            
        CBUFFERS[publicname]=cbuffer
            
        for cluster,a in ZoneClusterAvatar.avatars.iteritems():
            index =0
            if zonename in a.zoneNames:
                code,premium = PINFOS[publicname]
                avatar = CServerAvatar.worldCSAvatars[cluster]
                # MoM slightly different to TMMOKit - Install the player, afterwards we need to call callRemote("transferPlayerInstalled", ...)
                d = avatar.callRemote("installPlayer",publicname,pbuffer,code,premium,guildInfo)
                ip = None
                if a.imp:
                    ip = a.imp.ip
                wip = ip
                wport = a.worldPort
                zport = a.zonePorts[index]
                zpassword = a.zonePasswords[index]
                
                d.addCallback(self.playerTransfered,avatar,publicname,charname,remoteLeaderName,wip,wport,zport,zpassword)
                return d
            index+=1
                
        raise Exception("Unknown Zone!",zonename)
    
#guilds
    def remote_getGuildCharacters(self,name,publicName,who):        
        return CServerMind.themind.callRemote("getGuildCharacters",name,publicName,who)

    def remote_getGuildPublicName(self,name,publicName,characterName):        
        return CServerMind.themind.callRemote("getGuildPublicName",name,publicName,characterName)

    def remote_createGuild(self,name,publicName,mnames):
        return CServerMind.themind.callRemote("createGuild",name,publicName,mnames)
    def remote_removeGuildMember(self,name,publicName):
        return CServerMind.themind.callRemote("removeGuildMember",name,publicName)
    def remote_addGuildMember(self,name,publicName,inviter):
        return CServerMind.themind.callRemote("addGuildMember",name,publicName,inviter)
    def remote_promoteGuildMember(self,name,publicName,promoteName):
        return CServerMind.themind.callRemote("promoteGuildMember",name,publicName,promoteName)
    def remote_setGuildLeader(self,name,publicName,promoteName):
        return CServerMind.themind.callRemote("setGuildLeader",name,publicName,promoteName)

    def remote_demoteGuildMember(self,name,publicName,demoteName):
        return CServerMind.themind.callRemote("demoteGuildMember",name,publicName,demoteName)
    def remote_removeGuildMember(self,name,publicName,removeName):
        return CServerMind.themind.callRemote("removeGuildMember",name,publicName,removeName)
    def remote_setGuildMOTD(self,name,publicName,motd):
        return CServerMind.themind.callRemote("setGuildMOTD",name,publicName,motd)
    def remote_clearGuildMOTD(self,name,publicName):
        return CServerMind.themind.callRemote("clearGuildMOTD",name,publicName)
    def remote_getGuildRoster(self,name,publicName):
        return CServerMind.themind.callRemote("getGuildRoster",name,publicName)
    def remote_leaveGuild(self,name,publicName):
        return CServerMind.themind.callRemote("leaveGuild",name,publicName)
    def remote_disbandGuild(self,name,publicName):
        return CServerMind.themind.callRemote("disbandGuild",name,publicName)

    def remote_contestLevelUpEvent(self,publicName,levelType,level):
        return CServerMind.themind.callRemote("contestLevelUpEvent",publicName,levelType,level)

    def remote_checkGrants(self, publicName):
        return CServerMind.themind.callRemote("checkGrants", publicName)
        
class SimpleRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        
        if not mind:
            raise BadConnectionError("no mind")

        ip = mind.broker.transport.getPeer()
        
        #if ip.host != '127.0.0.1':
        #    raise BadConnectionError("bad ip")
        
        if pb.IPerspective in interfaces:
            p = CServerAvatar()
            CServerMind.themind = mind
            p.mind = mind
            return pb.IPerspective, p, lambda : None
        else:
            raise NotImplementedError("no interface")
        
def StartServices(username,password):
    from md5 import md5
    password = md5(password).digest()
    
    portal = Portal(SimpleRealm())
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    checker.addUser(username,password)
    portal.registerChecker(checker)
    reactor.listenTCP(7001,pb.PBServerFactory(portal))

