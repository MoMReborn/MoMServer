# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#world daemon, log into world server, tell it to shutdown in 10 minutes
#world kills all zones

import os, sys

from zope.interface import implements
from twisted.internet import protocol
from twisted.application import service, strports
from twisted.conch.ssh import session
from twisted.conch import interfaces as iconch
from twisted.cred import portal, checkers
from twisted.python import components, usage
from twisted.conch.insults import insults
from twisted.conch import manhole, manhole_ssh, telnet


class MyFactory(protocol.ServerFactory):
        
    def buildProtocol(self, addr):
        
        
        if addr.host != "127.0.0.1":
            print "WARNING: Unauthorized manhole attempt from: %s"%addr.host
            raise "Unauthorized"
        
        
        return protocol.ServerFactory.buildProtocol(self,addr)


class makeTelnetProtocol:
    def __init__(self, portal):
        self.portal = portal

    def __call__(self):
        auth = telnet.AuthenticatingTelnetProtocol
        args = (self.portal,)
        return telnet.TelnetTransport(auth, *args)

class chainedProtocolFactory:
    def __init__(self, namespace):
        self.namespace = namespace
    
    def __call__(self):
        return insults.ServerProtocol(manhole.ColoredManhole, self.namespace)

class _StupidRealm:
    implements(portal.IRealm)

    def __init__(self, proto, *a, **kw):
        self.protocolFactory = proto
        self.protocolArgs = a
        self.protocolKwArgs = kw

    def requestAvatar(self, avatarId, *interfaces):
        if telnet.ITelnetProtocol in interfaces:
            return (telnet.ITelnetProtocol,
                    self.protocolFactory(*self.protocolArgs, **self.protocolKwArgs),
                    lambda: None)
        raise NotImplementedError()
    

def MakeFactory(username,password,ShutdownWorld,RebootWorld):
    namespace = {}
    namespace["ShutdownWorld"]=ShutdownWorld
    namespace["RebootWorld"]=RebootWorld

    telnetRealm = _StupidRealm(telnet.TelnetBootstrapProtocol,
                               insults.ServerProtocol,
                               manhole.ColoredManhole,
                               namespace)



    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**{username: password})
    
    telnetPortal = portal.Portal(telnetRealm, [checker])

    telnetFactory = MyFactory()
    telnetFactory.protocol = makeTelnetProtocol(telnetPortal)
    #telnetService = strports.service(port,telnetFactory)
    #telnetService.setServiceParent(svc)
    
    #strports.service(port, telnetFactory).setServiceParent(application)
    
    return telnetFactory
    
 
