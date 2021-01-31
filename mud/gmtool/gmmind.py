# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword
import traceback
from md5 import md5
from mud.gamesettings import GMSERVER_IP,GMSERVER_PORT



def SimpleLog(text):
    print text


LOGFUNCTION = SimpleLog


def setLogFunction(logFunction):
    global LOGFUNCTION
    LOGFUNCTION = logFunction


def LogText(text):
    global LOGFUNCTION
    LOGFUNCTION(text)



class GMFactory(pb.PBClientFactory):
    reconnect = False
    gmConnection = None
    
    
    def __init__(self, gmConnection, *args, **kw):
        pb.PBClientFactory.__init__(self, *args, **kw)
        
        self.reconnect = False
        self.gmConnection = gmConnection
    
    
    def clientConnectionMade(self, broker):
        self.reconnect = False
        pb.PBClientFactory.clientConnectionMade(self,broker)
    
    
    def clientConnectionFailed(self, connector, reason):
        LogText("\nConnection to GM Server failed, %s\n"%reason.getErrorMessage().split(':',1)[0])
    
    
    def clientConnectionLost(self, connector, reason):
        self.reconnect = True    # reconnect on command input
    #    LogText("\nConnection to GM Server lost, %s\nTrying to reconnect...\n"%reason.getErrorMessage().split(':',1)[0])
    #    if not self.serverUnreachable:
    #        connector.connect()
    
    
    def checkConnectionForCommand(self):
        if self.reconnect:
            self.gmConnection.reconnect()
            return False
        return True



class GMConnection(pb.Root):
    factory = None
    username = ""
    password = ""
    role = ""
    
    commandBuffer = []
    chatBuffer = []
    
    
    def __init__(self, *args, **kw):
        self.perspective = None
        
        self.alive = False
    
    
    def processInput(self, line):
        # Check if the connection to the GM server has been established.
        if not self.alive:
            
            # If the connection hasn't been set up, give feedback and
            #  return.
            LogText("\nYou are not connected to the GM Server.\n")
            return
        
        # Check if the line is an admin command.
        if line.startswith('/adm'):
            if " " in line:
                pass
        
        # Check if the line is a guardian command.
        elif line.startswith('/gm'):
            if " " in line:
                if self.factory.checkConnectionForCommand():
                    self.perspective.callRemote("GM","command",line)
                else:
                    self.commandBuffer.append(line)
        
        # Otherwise assume the text entered was chat.
        else:
            if self.factory.checkConnectionForCommand():
                self.perspective.callRemote("GM","chat",line)
            else:
                self.chatBuffer.append(line)
    
    
    def connect(self, username, password, role):
        self.alive = False
        
        self.username = username
        self.password = md5(password).digest()
        self.role = role
        
        if not self.factory:
            self.factory = GMFactory(self)
        
        reactor.connectTCP(GMSERVER_IP,GMSERVER_PORT,self.factory)
        
        self.factory.login(UsernamePassword("%s-%s"%(username,role), self.password),self).addCallback(self.connected)
        
        LogText("\nConnecting to GM Server as User: %s Role: %s\n"%(username,role))
    
    
    def reconnect(self):
        self.alive = False
        
        if not self.username or not self.password or not self.role:
            return
        
        if not self.factory:
            self.factory = GMFactory(self)
        
        reactor.connectTCP(GMSERVER_IP,GMSERVER_PORT,self.factory)
        
        self.factory.login(UsernamePassword("%s-%s"%(self.username,self.role), self.password),self).addCallback(self.connected)
        
        LogText("\nConnecting to GM Server as User: %s Role: %s\n"%(self.username,self.role))
    
    
    def connected(self, perspective):
        self.alive = True
        
        self.perspective = perspective
        
        LogText("\nConnected to GM Server.\n")
        
        for command in self.commandBuffer:
            self.perspective.callRemote("GM","command",command)
        self.commandBuffer = []
        
        for line in self.chatBuffer:
            self.perspective.callRemote("GM","chat",line)
        self.chatBuffer = []
    
    
    def disconnect(self):
        self.alive = False
        
        if self.perspective:
            self.perspective.broker.transport.loseConnection()
            self.perspective = None
        
        self.factory = None
    
    
    def failure(self, reason):
        LogText("Error: %s\n"%reason.getErrorMessage().split(':',1)[0])
    
    
    def remote_logText(self, text):
        LogText(text)

