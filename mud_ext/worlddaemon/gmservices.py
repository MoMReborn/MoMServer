# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from twisted.internet import reactor
from twisted.spread import pb
from twisted.cred.credentials import UsernamePassword

from md5 import md5
import traceback

from mud.gamesettings import *
from mud_ext.server.config import LoadConfiguration

CONFIG = {}
LoadConfiguration(CONFIG)

class GMServices(pb.Root):
    
    def __init__(self, worldName):
        self.perspective = None
        self.worldName = worldName
        self.avatars = []
    
    
    def connected(self, perspective):
        self.perspective = perspective
    
    
    def failure(self, reason):
        print reason.getErrorMessage()
    
    
    def connect(self):
        factory = pb.PBClientFactory()
        
        try:
            reactor.connectTCP(GMSERVERIP,GMSERVERPORT,factory)
            password = md5(CONFIG["World Password"]).digest()
            
            d = factory.login(UsernamePassword("%s-WorldDaemon" % CONFIG["World Username"],password),self)
            d.addCallback(self.connected)
            d.addErrback(self.failure)
        except KeyError:
            print "World Daemon couldn't connect to GM server, password not found."
        except:
            print "Error connecting World Daemon to GM server!"
    
    
    def disconnect(self):
        if self.perspective:
            self.perspective.broker.transport.loseConnection()
            self.perspective = None
    
    
    def registerZoneClusterAvatars(self, avatars):
        self.zoneClusterAvatars = avatars
    
    
    def remote_receiveGMChat(self, name, msg):
        for avatar in self.zoneClusterAvatars:
            try:
                avatar.mind.callRemote("receiveGMChat",name,msg)
            except:
                traceback.print_exc()
    
    
    def remote_sendGuildMsg(self, name, msg, guildName):
        for avatar in self.zoneClusterAvatars:
            try:
                avatar.mind.callRemote("sendGuildMsg",name,msg,guildName)
            except:
                traceback.print_exc()


