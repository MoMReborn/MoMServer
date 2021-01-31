# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#master manhole

from zope.interface import implements

from twisted.internet import protocol
from twisted.application import service, strports
from twisted.conch.ssh import session
from twisted.conch import interfaces as iconch
from twisted.cred import portal, checkers,error, credentials
from twisted.python import components, usage,failure, log

from twisted.conch.insults import insults
from twisted.conch import manhole, manhole_ssh, telnet
from twisted.conch.ssh import factory, keys, session
from zope import interface

from mud.masterserver.masterdb import *
from mud.common.permission import Role,User,TablePermission,ColumnPermission
from mud.common.avatar import RoleAvatar




class ConchFactory(factory.SSHFactory):
    publicKey = 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAGEArzJx8OYOnJmzf4tfBEvLi8DVPrJ3/c9k2I/Az64fxjHf9imyRJbixtQhlH9lfNjUIx+4LmrJH5QNRsFporcHDKOTwTTYLh5KmRpslkYHRivcJSkbh/C+BR3utDS555mV'

    publicKeys = {
        'ssh-rsa' : keys.getPublicKeyString(data = publicKey)
    }
    del publicKey

    privateKey = """-----BEGIN RSA PRIVATE KEY-----
MIIByAIBAAJhAK8ycfDmDpyZs3+LXwRLy4vA1T6yd/3PZNiPwM+uH8Yx3/YpskSW
4sbUIZR/ZXzY1CMfuC5qyR+UDUbBaaK3Bwyjk8E02C4eSpkabJZGB0Yr3CUpG4fw
vgUd7rQ0ueeZlQIBIwJgbh+1VZfr7WftK5lu7MHtqE1S1vPWZQYE3+VUn8yJADyb
Z4fsZaCrzW9lkIqXkE3GIY+ojdhZhkO1gbG0118sIgphwSWKRxK0mvh6ERxKqIt1
xJEJO74EykXZV4oNJ8sjAjEA3J9r2ZghVhGN6V8DnQrTk24Td0E8hU8AcP0FVP+8
PQm/g/aXf2QQkQT+omdHVEJrAjEAy0pL0EBH6EVS98evDCBtQw22OZT52qXlAwZ2
gyTriKFVoqjeEjt3SZKKqXHSApP/AjBLpF99zcJJZRq2abgYlf9lv1chkrWqDHUu
DZttmYJeEfiFBBavVYIF1dOlZT0G8jMCMBc7sOSZodFnAiryP+Qg9otSBjJ3bQML
pSTqy7c3a2AScC/YyOwkDaICHnnD3XyjMwIxALRzl0tQEKMXs6hH8ToUdlLROCrP
EhQ0wahUTCk1gKA4uPD6TMTChavbh4K63OvbKg==
-----END RSA PRIVATE KEY-----"""
    privateKeys = {
        'ssh-rsa' : keys.getPrivateKeyObject(data = privateKey)
    }
    del privateKey

    def __init__(self, portal):
        self.portal = portal
        
        
    def buildProtocol(self, addr):
        
        if addr.host not in self.allowedIP:
            raise "Unauthorized"
        
        
        return factory.SSHFactory.buildProtocol(self,addr)



class chainedProtocolFactory:
    def __init__(self, namespace):
        self.namespace = namespace
    
    def __call__(self):
        return insults.ServerProtocol(manhole.ColoredManhole, self.namespace)


class ManholeChecker:

    interface.implements(checkers.ICredentialsChecker)

    credentialInterfaces = (credentials.IUsernamePassword,
        credentials.IUsernamePassword)

    def __init__(self,username,password):
        self.username = username
        self.password = password

    def requestAvatarId(self, credentials):
        if credentials.username == self.username and credentials.password == self.password:
            return credentials.username
            
        else:
            return failure.Failure(error.UnauthorizedLogin())
        

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

def MakeFactory(allowedIP,username,password):

    #svc = service.MultiService()
    
    
    
    namespace = {}
    namespace["Account"]=Account
    namespace["RemoveAccount"]=RemoveAccount
    namespace["QueueProduct"]=QueueProduct
    #namespace["LiveZones"]=World.byName("TheWorld").liveZoneInstances
    #namespace["ActivePlayers"]=World.byName("TheWorld").activePlayers
    #namespace["Player"]=Player

    checker = ManholeChecker(username,password)

    sshRealm = manhole_ssh.TerminalRealm()
    sshRealm.chainedProtocolFactory = chainedProtocolFactory(namespace)

    sshPortal = portal.Portal(sshRealm, [checker])
    sshFactory = ConchFactory(sshPortal)
    sshFactory.allowedIP = allowedIP

    #sshService = strports.service(8000,sshFactory)
    #sshService.setServiceParent(svc)

    return sshFactory
 