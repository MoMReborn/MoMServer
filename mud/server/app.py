# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from sqlobject import *
from mud.common.dbconfig import GetDBConnection

from twisted.internet import reactor,protocol,defer
from twisted.spread import pb
from twisted.cred.portal import Portal,IRealm
from twisted.cred.credentials import IUsernamePassword,IUsernameHashedPassword
from twisted.cred.checkers import ICredentialsChecker
from twisted.cred import error, credentials,checkers
from twisted.python import components, failure, log

from mud.common.avatar import Avatar
from mud.common.permission import Role,User,BannedUser,BannedIP

from md5 import md5
from time import time as sysTime
import traceback



class UnauthorizedError(Exception):
    def __str__(self):
        return "Your login information is incorrect."

class InUseError(Exception):
    def __str__(self):
        return "This account is currently in use."

class BannedError(Exception):
    def __str__(self):
        return "You have been banned from this server."

class BannedIPError(Exception):
    def __str__(self):
        return "The IP address you are connecting from is banned."

class ServerFullError(Exception):
    def __str__(self):
        return "This server is full."

class AllowConnectionsError(Exception):
    def __str__(self):
        return "This server is currently unavailable.  Please try again in a few minutes."

class PerspectiveCallError(Exception):
    def __str__(self):
        return "Error in perspective call."

class NoAvatarError(Exception):
    def __str__(self):
        return "Error No Avatar."
class NoFunctionError(Exception):
    def __str__(self):
        return "Error No Function."
class PerspectiveCallError(Exception):
    def __str__(self):
        return "Error in perspective call."

    
class Checker:
    __implements__ = ICredentialsChecker

    credentialInterfaces = (IUsernamePassword,IUsernameHashedPassword)
    
    def __init__(self,useMD5):
        self.useMD5 = useMD5
        
    def _cbPasswordMatch(self, matched, username,password,temppassword):
        
        if not matched:
            #check temp
            if password == temppassword:
                matched = True
        
        if matched:
            user,role=username.split('-')

            #check role
            user=User.byName(user)
            r = user.getRole(role)
            if r:
                return username
                        
        #either password not matched or bad role
        
        return failure.Failure(UnauthorizedError())

    def requestAvatarId(self, credentials):

        if len(credentials.username.split('-'))!=2:
            return failure.Failure(UnauthorizedError())
            
            
        username,role=credentials.username.split('-')
        
        try:
            banned = BannedUser.byName(username)
            return failure.Failure(BannedError())
        except:
            pass
        
        if THESERVER.roleLimits.has_key(role):
            limit = THESERVER.roleLimits[role]
            if not limit:
                return failure.Failure(ServerFullError())
            n = 0
            for x in MasterPerspective.users:
                
                if role == x[1]:
                    n+=1
                    if n == limit:
                        return failure.Failure(ServerFullError())
                        
        
        roles = ('Player','Immortal','Guardian','World')
        if role in roles:
            for r in roles:
                if (username,r) in MasterPerspective.users[:]:
                    for avatar in THESERVER.realm.avatars[:]:
                        if avatar.username == username and avatar.role.name == r:
                            #kick
                            try:
                                avatar.logout()
                            except:
                                traceback.print_exc()
                                

        
        try:
            user = User.byName(username)

        except SQLObjectNotFound:
            print "User not found",username
            return failure.Failure(UnauthorizedError())
        
        if self.useMD5:
            matched = credentials.checkPassword(md5(user.password).digest())
            if not matched:
                matched = credentials.checkPassword(md5(user.tempPassword).digest())
                
            #XXX REMOVE ME AT A LATER TIME, LEGACY non-md5 using CLIENTS!!! 9-10-06
            if not matched:
                matched = credentials.checkPassword(user.password)

        else:
            matched = credentials.checkPassword(user.password)
            if not matched:
                matched = credentials.checkPassword(user.tempPassword)
            
        if not matched:
            return failure.Failure(UnauthorizedError())
            
        r = user.getRole(role)
        if r:
            print r
            return credentials.username
                        
        #bad role
        
        return failure.Failure(UnauthorizedError())
            
            
        
        #return defer.maybeDeferred(
        #    credentials.checkPassword,
        #    user.password).addCallback(
        #    self._cbPasswordMatch, credentials.username,credentials.password,user.tempPassword)
            
class MasterPerspective(pb.Avatar):
    users = []

    #(username,role) -> [call,call,...]
    deferredCalls = {}

    def __init__(self,role,username,mind,realm):
        self.avatars = {}
        self.role = role
        self.mind = mind
        self.username=username
        self.cpuTime = 0
        
        self.throttle = role.name in ('Player','Guardian','Immortal')
        
        MasterPerspective.users.append((self.username,self.role.name))
        MasterPerspective.deferredCalls[self]=[]
        
        for avatar in role.avatars:
            a = Avatar.createAvatar(avatar.name)
            a.__init__(username,role,mind)
            a.realm = realm            
            self.avatars[avatar.name]=a
            a.masterPerspective = self
    
    def removeAvatar(self,name):
        if self.avatars.has_key(name):
            del self.avatars[name]        
            
    def __getattr__(self,attr):
        #XXX this could maybe be a little better than stuff into _interface
        if attr.startswith('perspective_'):
            
            self._interface=attr[12:]
            return self.perspective_call
            
        raise AttributeError
        
    def perspective_enumAvatars(self):
        return self.avatars.keys()
    
    
    def perspective_call(self,*args):
        if THESERVER.throttleUsage and self.throttle:
            if self.cpuTime > 0:
                dc = MasterPerspective.deferredCalls[self]
                d = defer.Deferred()
                dc.append((d,args))
                #print "Throttling",args
                return d
            
        tm = sysTime()
        function = args[0]
        interface = self._interface
        try:
            avatar=self.avatars[interface]
        except KeyError:
            try: 
                interface = interface + "Avatar"
                avatar=self.avatars[interface]
            except:
                return failure.Failure(NoAvatarError())
            
        function = "perspective_"+function
        if not hasattr(avatar,function):
            return failure.Failure(NoFunctionError())
            
            
        nargs=args[1:]
        #on any function call we set the player's info to dirty
        if hasattr(avatar,"player"):
            if avatar.player:
                avatar.player.cinfoDirty = True
        try:
            result = getattr(avatar,function)(*nargs)
        except:
            #use errback
            traceback.print_exc()
            return failure.Failure(PerspectiveCallError())
        
        t = sysTime() - tm
        if t > .1:
            print "Warning: %s %s took %f seconds"%(self.username,args,t)
        self.cpuTime+=t
            
        return result
    
    
    def logout(self):
        if (self.username,self.role.name) not in MasterPerspective.users:
            return
        
        MasterPerspective.users.remove((self.username,self.role.name))
        
        del MasterPerspective.deferredCalls[self]
        
        for avatar in self.avatars.itervalues():
            try:
                avatar.logout()
                avatar.masterPerspective = None
            except AttributeError:
                pass
        
        try:
            if self.realm:
                self.realm.avatars.remove(self)
        except AttributeError:
            pass
        except:
            traceback.print_exc()
        
        try:
            if self.mind:
                self.mind.broker.transport.loseConnection()
                self.mind = None
        except:
            traceback.print_exc()



class Realm:
    __implements__ = IRealm
    def __init__(self,server):
        self.avatars = []
        self.server = server
    
    def requestAvatar(self, avatarId, mind, *interfaces):
        
        if pb.IPerspective in interfaces:
            username,role=avatarId.split('-')
            
            #user and ip banning
            if mind: #blah, I wish I could get this regardless!!!!
                ip = mind.broker.transport.getPeer()
                try:
                    subnet=ip.host[:ip.host.rfind('.')]
                except:
                    print "Warning:  IP logging isn't working... Windows 2000?"
                    subnet = ""
                
                
                if role == 'Registration' and subnet: #old client didn't pass pb.Root here... grr
                    try:
                        bi = BannedIP.byAddress(subnet)
                        return failure.Failure(BannedIPError())
                    except:
                        pass
        
                    
                if role in ('Player','Guardian','Immortal'):
                    u = User.byName(username)
                    if subnet:
                        u.lastConnectSubnet = subnet

            if role in ('Player','Guardian','Immortal'):
                if not THESERVER.allowConnections:
                    return failure.Failure(AllowConnectionsError())
            
            role=Role.byName(role)       
            print "-------->",THESERVER.__class__.__name__,role.name                     
            avatar = MasterPerspective(role,username,mind,self)
            avatar.realm = self
            self.avatars.append(avatar)
            return pb.IPerspective, avatar, avatar.logout 
        else:
            raise NotImplementedError("no interface")

THESERVER = None
class Server:
    def __init__(self,port,useMD5 = True):
        global THESERVER
        if THESERVER:
            traceback.print_stack()
            print "AssertionError: server already exists!"
            return
        
        THESERVER = self
        self.port = port
        self.realm = None
        self.portal = None
        self.checker = None
        self.listen = None
        self.allowConnections = True
        
        self.roleLimits = {}
        MasterPerspective.users = []
        self.throttleUsage = False
        self.throttleTickCallback = None
        
        self.useMD5 = useMD5
        
    def getActiveUsersByRole(self,role):
        n = 0
        for username,urole in MasterPerspective.users:
            if urole == role:
                n+=1
                
        return n

    def throttleTick(self):
        reactor.callLater(.2,self.throttleTick)    
        
        for avatar,dcalls in MasterPerspective.deferredCalls.iteritems():
            if not len(dcalls):
                if avatar.cpuTime:
                    avatar.cpuTime-=.025
                    if avatar.cpuTime<0:
                        avatar.cpuTime = 0.0
                continue
            deferred,args = dcalls[0]
            avatar.cpuTime-=.025
            if avatar.cpuTime<=0:
                avatar.cpuTime = 0
                dcalls.pop(0)
                try:
                    result = avatar.perspective_call(*args)
                    
                    # The function "perspective_call" returns a deferred or a
                    #  normal result, depending on the call that has been queued.
                    # Deferreds have to be chained, only normal results may be
                    #  processed via callback.
                    if isinstance(result, defer.Deferred):
                        result.chainDeferred(deferred)
                    else:
                        deferred.callback(result)
                except:
                    traceback.print_exc()
    
    
    def startServices(self):
        #create our server's services
        
        port = self.port
        self.realm = Realm(self)
        self.portal = Portal(self.realm)
        self.checker = Checker(self.useMD5)
        self.portal.registerChecker(self.checker)
        self.listen = reactor.listenTCP(port,pb.PBServerFactory(self.portal))
        
        #only do this when child servers are all up?
        """
        if self.config.parentProcessPort:
            from process import ClientProcessFactory
            f = ClientProcessFactory()
            reactor.connectTCP("localhost", self.config.parentProcessPort, f)
        """
        self.throttleTickCallback = self.throttleTick()
    
    
    def shutdown(self):
        global THESERVER
        THESERVER = None
        
        for avatar in self.realm.avatars:
            avatar.mind.broker.transport.loseConnection()
        
        if self.listen:
            self.listen.stopListening()
            
        if self.throttleTickCallback:
            self.throttleTickCallback.cancel()
            self.throttleTickCallback = None
            
        

            
        
        


            

