# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import sys,os
sys.path.append(os.getcwd())

if sys.platform == "win32":
    from twisted.internet.iocpreactor import install
else:
    from twisted.internet.threadedselectreactor import install
install()

from twisted.internet import reactor
from mud.server.app import Server
from mud.server.config import ConfigureServer
from mud.common.permission import Role,User
from mud.common.avatar import Avatar,RoleAvatar

from gmcommands import DoGMCommand
from mud.gamesettings import *

from md5 import md5
from time import strftime



sys.argv.append('database=data/gmserver')
ConfigureServer("gmserver.db")

#Always drop tables for now
TABLES = [Role,User,RoleAvatar]
for t in TABLES:
    t.dropTable(ifExists=True)
    t.createTable()


#Character Server
CHARSERVER_MIND = None
class CharacterAvatar(Avatar):
    def __init__(self,username,role,mind):
        global CHARSERVER_MIND
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.role = role
        self.mind = mind
        CHARSERVER_MIND = mind
        
        from gmcommands import SetCharServerMind
        SetCharServerMind(CHARSERVER_MIND)

    def perspective_sayHi(self):
        print "yup"
                
    def logout(self):
        global CHARSERVER_MIND
        CHARSERVER_MIND = None



class GMAvatar(Avatar):
    def __init__(self, username, role, mind):
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.role = role
        self.mind = mind
    
    
    def perspective_command(self, command):
        DoGMCommand(self,command)
    
    
    def perspective_chat(self, line):
        msg = r'GM: <%s> %s\n'%(self.username,line)
        formatted = "[%s] %s"%(strftime('%X'),msg)
        
        global server
        for avatar in server.realm.avatars:
            if avatar == self:
                continue
            if isinstance(avatar,GMAvatar):
                avatar.mind.callRemote("logText",formatted)
            elif isinstance(avatar,WorldDaemonAvatar):
                avatar.mind.callRemote("receiveGMChat",self.username,msg)
    
    
    def logout(self):
        pass



class WorldDaemonAvatar(Avatar):
    def __init__(self, username, role, mind):
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.role = role
        self.mind = mind
    
    
    def perspective_receiveGMChat(self, name, msg):
        formatted = "[%s] %s"%(strftime('%X'),msg)
        
        global server
        for avatar in server.realm.avatars:
            if avatar == self:
                continue
            if isinstance(avatar,GMAvatar):
                avatar.mind.callRemote("logText",formatted)
            elif isinstance(avatar,WorldDaemonAvatar):
                avatar.mind.callRemote("receiveGMChat",name,msg)
    
    
    def perspective_sendGuildMsg(self, name, msg, guildName):
        global server
        for avatar in server.realm.avatars:
            if avatar == self:
                continue
            if isinstance(avatar,WorldDaemonAvatar):
                avatar.mind.callRemote("sendGuildMsg",name,msg,guildName)
    
    
    def logout(self):
        pass



def ConfigureRoles():
    admin = Role(name="Administrator")
    RoleAvatar(name="AdminAvatar",role=admin)
    
    gm = Role(name="GM")
    RoleAvatar(name="GMAvatar",role=gm)
    
    character = Role(name="CharacterServer")
    RoleAvatar(name="CharacterAvatar",role=character)
    
    wdaemon = Role(name="WorldDaemon")
    RoleAvatar(name="WorldDaemonAvatar",role=wdaemon)


def ConfigureUsers():
    cserver = User(name="CharacterServer",password="&^!(*&@(*@jjjkkwiwiwu--++")
    cserver.addRole(Role.byName("CharacterServer"))
    
    for worldName,password in WORLDNAMES.iteritems():
        wdaemon = User(name=worldName,password=password)
        wdaemon.addRole(Role.byName("WorldDaemon"))
    
    from userpasswords import USERS
    for name,info in USERS.iteritems():
        password,roles = info
        user = User(name=name,password=password)
        for role in roles:
            user.addRole(Role.byName(role))
            
     
print "GM Server"
print "->Initializing"

ConfigureRoles()
ConfigureUsers()
    
server = Server(GMSERVER_PORT,True)    # True to use md5 hashing for passwords
server.startServices()

print "->GM Server is up"
reactor.run()



