# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#WorldImp

#basic process control for remote zone clusters
from twisted.cred.portal import Portal
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.cred.credentials import UsernamePassword
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


#Server Side
class ImpAvatar(pb.Avatar):
    
    def spawnWorldProcess(self,args):
        self.mind.callRemote("spawnWorldProcess",args)


IMPCONNECTED_CALLBACK = None

class SimpleRealm:
    implements(IRealm)

    def requestAvatar(self, avatarId, mind, *interfaces):
        
        if not mind:
            raise BadConnectionError("no mind")

        ip = mind.broker.transport.getPeer()
        
        if pb.IPerspective in interfaces:
            p = ImpAvatar()
            p.ip = ip.host
            p.id = int(avatarId)
            p.mind = mind
            IMPCONNECTED_CALLBACK(p)
            return pb.IPerspective, p, lambda : None
        else:
            raise NotImplementedError("no interface")


def StartServices(callback):
    global IMPCONNECTED_CALLBACK
    IMPCONNECTED_CALLBACK = callback
    #fire up the World Stuff
    portal = Portal(SimpleRealm())
    checker = InMemoryUsernamePasswordDatabaseDontUse()
    from md5 import md5
    password = md5("imp").digest()
    for x in range(0,100):
        checker.addUser(str(x), password)
    portal.registerChecker(checker)
    reactor.listenTCP(7005,pb.PBServerFactory(portal))


#client side

class ImpMind(pb.Root):
    def remote_spawnWorldProcess(self, args):
        args += " -daemonip=%s"%self.daemonIP
        
        frozen = main_is_frozen()
        
        cwd = os.getcwd()
        
        if frozen:
            cmd  =  r'..\bin\WorldServer.exe'
        else:
            cmd  =  sys.executable
            args =  "%s/WorldServer.py %s"%(cwd,args)
        
        if sys.platform[:6] != 'darwin':
            s = 'start "%s" %s %s'%(cwd,cmd,args)
            s = os.path.normpath(s)
            print s
            os.system(s)
        else:
            cmd = sys.executable
            args = args.split(" ")
            args.insert(0,cmd)
            
            s = 'pythonw -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)
    
    
    def killProcess(self,pid):
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
                
    def remote_killWorldNow(self,worldPID,zonePID):
        print "Killing World"
        for p in zonePID:
            self.killProcess(p)
        self.killProcess(worldPID)
            


        
    
    def connected(self,perspective):
        self.perspective = perspective
        
    def failure(self,reason):
        print reason
    
def main():
    IP,PORT = None,None
    for arg in sys.argv:
        if arg.startswith('-daemonip='):
            IP = arg[10:]
        if arg.startswith('-daemonport='):
            PORT = int(arg[12:])
            
    if not IP or not PORT:
        print "Usage:  WorldImp.exe -daemonip=x.x.x.x -daemonport=x"
        return

    factory = pb.PBClientFactory()
    reactor.connectTCP(IP,PORT,factory)
    from md5 import md5
    password = md5("imp").digest()
    mind = ImpMind()
    mind.daemonIP = IP
    factory.login(UsernamePassword("0", password),mind).addCallbacks(mind.connected, mind.failure)
    
    reactor.run()


