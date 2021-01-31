# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.avatar import Avatar
from mud.common.permission import User,Role
from mud.world.core import *
from mud.world.player import Player
from mud.world.theworld import World

from random import choice
import string



def GenPasswd(length=8, chars=string.letters):
    return ''.join([choice(chars) for i in xrange(length)])

#also query
class NewPlayerAvatar(Avatar):
    ownerPublicName = None
    
    
    def __init__(self,username,role,mind):
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.world = World.byName("TheWorld")
    
    def perspective_newPlayer(self,publicName,fantasyName, playerPassword = None):
        #XXX if you change this function, also change it's mirror in cserveravatar!!!
        
        if self.world.pwNewPlayer and playerPassword != self.world.pwNewPlayer:
            return (-1,"Incorrect player password.",None)

        #does player already exist?
        try:
            player = Player.byPublicName(publicName)
        except:
            pass
        else:
            return (-1,"You already have an account on this world.",None)
     
        try:
            player = Player.byFantasyName(fantasyName)
        except:
            pass
        else:
            return (-1,"That avatar name is taken, please choose another.",None)
                
        password = GenPasswd().upper()

        #move me
        from mud.world.zone import Zone
        zone = Zone.byName(self.world.startZone)
        dzone = Zone.byName(self.world.dstartZone)
        mzone = Zone.byName(self.world.mstartZone)

        t = zone.immTransform
        dt = dzone.immTransform
        mt = mzone.immTransform
        
        p = Player(publicName=publicName,password=password,fantasyName=publicName,logZone=zone,bindZone=zone,darknessLogZone=dzone,darknessBindZone=dzone,monsterLogZone=mzone,monsterBindZone=mzone)
        #temp
        
        p.logTransformInternal=t
        p.bindTransformInternal=t

        p.darknessLogTransformInternal=dt
        p.darknessBindTransformInternal=dt

        p.monsterLogTransformInternal=mt
        p.monsterBindTransformInternal=mt

        
        user = User(name=publicName,password=password)
        user.addRole(Role.byName("Player"))
        
        if publicName == NewPlayerAvatar.ownerPublicName: 
            user.addRole(Role.byName("Immortal"))
            user.addRole(Role.byName("Guardian"))
            
            return (0,"Immortal Account Created.\nYour password is %s"%password,password)
        
        
        return (0,"Account Created.\nYour password is %s"%password,password)
        
    #returns True if player has an account, otherwise false
    def perspective_queryPlayer(self,publicName):
        #does player already exist?
        try:
            player = Player.byPublicName(publicName)
        except:
            return False
        else:
            return True
        
        
        
    
#also query
class QueryAvatar(Avatar):
    def perspective_retrieveWorldInfo(self):
        return CoreSettings.WORLDTEXT,CoreSettings.WORLDPIC


