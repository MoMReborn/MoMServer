# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#master manhole

import os, sys

from mud_ext.masterserver.masterdb import *
from mud.common.permission import Role,User,TablePermission,ColumnPermission,BannedIP
from mud.common.avatar import RoleAvatar

def QueueProduct(email,product):
    
    email=email.lower()
    product=product.upper()
    
    if "@" not in email:
        raise "invalid email"
    
    try:
        a = Account.byEmail(email)
        if a.hasProduct(product):
            print "Email address linked to public name %s, which already has this product"%a.publicName
            return
        a.addProduct(product)
        print "%s product added to existing account by public name %s"%(product,a.publicName)
        return
    except:
        pass
    
    ProductEmail(email=email,product=product.upper())
    print "Product: %s queued for email address: %s"%(product,email)
    
        
def RemoveAccount(publicname):
    #XXX this should really be in a transaction
    a = Account.byPublicName(publicname)
    user = User.byName(publicname)
    regkey = RegKey.byKey(a.regkey)
    
    try:
        pe = ProductEmail.byEmail(a.email)
        pe.destroySelf()
    except:
        pass
    
    for p in a.products:
        p.destroySelf()
        
    for w in a.worlds:
        w.destroySelf()
        
    for r in list(user.roles):
        r.removeUser(user)
        
    a.destroySelf()
    user.destroySelf()
    regkey.destroySelf()
    
    

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
        
        print "WARNING: Unauthorized manhole attempt from: %s"%addr.host
        if addr.host not in self.allowedIP:
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


def SetUserBanLevel(publicname,banlevel):
    user = User.byName(publicname)
    user.banLevel = banlevel

def UnbanSubnet(subnet):
    bi = BannedIP.byAddress(subnet)
    bi.destroySelf()    

#bans IP and sets banLevel to 3
def NukeUser(publicname):
    user = User.byName(publicname)
    if user.lastConnectSubnet:
        try:
            BannedIP(address=user.lastConnectSubnet)
        except:
            pass
    else:
        print "WARNING: User had no last connection subnet, ip ban not possible"
    user.banLevel=3    

def MakeFactory(allowedIP,username,password):

    namespace = {}
    namespace["Account"]=Account
    namespace["RemoveAccount"]=RemoveAccount
    namespace["QueueProduct"]=QueueProduct
    namespace["SetUserBanLevel"]=SetUserBanLevel
    namespace["NukeUser"]=NukeUser
    namespace["UnbanSubnet"]=UnbanSubnet
    


    telnetRealm = _StupidRealm(telnet.TelnetBootstrapProtocol,
                               insults.ServerProtocol,
                               manhole.ColoredManhole,
                               namespace)



    checker = checkers.InMemoryUsernamePasswordDatabaseDontUse(**{username: password})
    
    telnetPortal = portal.Portal(telnetRealm, [checker])

    telnetFactory = MyFactory()
    telnetFactory.allowedIP = allowedIP
    telnetFactory.protocol = makeTelnetProtocol(telnetPortal)
    #telnetService = strports.service(port,telnetFactory)
    #telnetService.setServiceParent(svc)
    
    #strports.service(port, telnetFactory).setServiceParent(application)
    
    return telnetFactory
    
    
    
    
    
    
    
    

 