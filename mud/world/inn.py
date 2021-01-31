# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#masochism for sure


from twisted.spread import pb
from twisted.internet.defer import Deferred

from mud.world.character import Character
from mud.world.core import *
from mud.world.defines import *
from mud.world.shared.worlddata import CharacterInfo
from mud.worldserver.charutil import ExtractPlayer,InstallCharacterBuffer

from time import time as sysTime
from base64 import decodestring
from cPickle import loads



class Inn(pb.Root):
    def __init__(self, innkeeper, player):
        self.innkeeper = innkeeper
        self.innWnd = None
        self.player = player
        player.mind.callRemote("getInnWnd").addCallbacks(self.gotInnWnd,self.error)
    
    
    def remote_removeFromParty(self, cname):
        # Do not allow a player to change party members while in a trade.
        if self.player.trade:
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"You must finish a trade before using the Inn.\\n")
            return
        
        try:
            c = Character.byName(cname)
        except:
            return
        
        if c not in self.player.party.members:
            return
        
        if len(self.player.party.members) == 1:
            return
        
        if not c.dead:
            gotone = False
            for dc in self.player.party.members:
                if dc == c:
                    continue
                if not dc.dead:
                    gotone = True
                    break
            if not gotone:
                self.player.sendGameText(RPG_MSG_GAME_DENIED,"You must have at least one living member of your party!\\n")
                return
        
        self.player.party.removeCharacter(c)
        
        self.player.alliance.allianceInfo.refresh()
        
        self.sendLists()
    
    
    def gotCharacterBuffer(self,cbuffer,cname):
        if not self.player:
            return
        player = self.player
        
        if cbuffer:
            cbuffer = loads(decodestring(cbuffer))
            c = None
            try:
                c = Character.byName(cname)
                try:
                    c.destroySelf()
                except:
                    print "ERROR SWAPPING TO %s"%cname
                    return
            except:
                pass
                
            InstallCharacterBuffer(self.player.id,cname,cbuffer)
            
        c = Character.byName(cname)
        if c.dead:
            c.dead = False
            c.health = -999999
            c.stamina = -999999
            c.mana = -999999

        ec = self.player.party.members[0]
        
        self.player.party.addCharacter(c)
        ec.backupItems()
        self.player.party.removeCharacter(ec)
            
        self.player.alliance.allianceInfo.refresh()
            
        self.sendLists()
        
        ExtractPlayer(player.publicName,player.id,ec.id)    
        ec.destroySelf()
            
        player.world.sendCharacterInfo(player)
        
        player.charName = c.name
        player.zone.simAvatar.setDisplayName(player)
    
    
    def remote_addToParty(self, cname):
        # Get a handle to the player.
        player = self.player
        
        # Do not allow a player to change party members while in a trade.
        if player.trade:
            player.sendGameText(RPG_MSG_GAME_DENIED,"You must finish a trade before using the Inn.\\n")
            return
        
        from mud.world.cserveravatar import AVATAR
        
        if AVATAR:
            if player.cserverInfos:
                for ci in player.cserverInfos:
                    if ci.rename == 2 and ci.name.lower() == cname.lower():
                        player.sendGameText(RPG_MSG_GAME_DENIED,"You must rename this character before bringing them into the game.  You can rename the character by logging in with them from the main world login screen.\\n")
                        return
            
            #should be on client
            if cname == player.party.members[0].name:
                return
            
            t = sysTime() - player.lastInnAddTime
            if t < 30:
                player.sendGameText(RPG_MSG_GAME_DENIED,"You can change characters in %i seconds.\\n"%(31-t))
                return
            
            player.lastInnAddTime = sysTime()
            
            d = AVATAR.mind.callRemote("getCharacterBuffer", \
                    player.publicName,cname)
            d.addCallback(self.gotCharacterBuffer,cname)
            return d
        
        else:
            try:
                c = Character.byName(cname)
            except:
                return
            
            if c.player != player:
                print "WARNING: Player at inn attempting to add a character that isn't theres!"
                return
            
            if len(player.party.members) == 6:
                return
            
            if len(player.party.members) >= CoreSettings.MAXPARTY:
                player.sendGameText(RPG_MSG_GAME_DENIED,"This world allows at most %i characters in your party.\\n"%(CoreSettings.MAXPARTY))
                return
            
            if c in player.party.members:
                return
            
            #add the character!!!!
            player.party.addCharacter(c)
            
            # Monsters don't like to party...
            if player.realm == RPG_REALM_MONSTER:
                for member in player.party.members:
                    if member != c:
                        player.party.removeCharacter(member)
                player.sendGameText(RPG_MSG_GAME_EVENT, \
                                         "Rawr! Monsters don't like to party.\\n")
            
            player.alliance.allianceInfo.refresh()
            
            self.sendLists()
            return
    
    
    def remote_leaveInn(self):
        self.endInteraction()
    
    
    def sendLists(self):
        cinfos = []
        names = []
        
        if self.player.cserverInfos:
            for ci in self.player.cserverInfos:
                if ci.realm != self.player.realm:
                    continue
                
                cinfos.append(ci)
                names.append(ci.name)
        
        for c in self.player.characters:
            if c in self.player.party.members:
                continue
            
            if c.name in names:
                continue
            
            if c.spawn.realm != self.player.realm:
                continue
            
            cinfo = CharacterInfo(c)
            cinfos.append(cinfo)
        
        pinfos = [CharacterInfo(c) for c in self.player.party.members]
        
        self.innWnd.callRemote("set",cinfos,pinfos)
    
    
    def endInteraction(self):
        if self.innWnd:
            if not self.player.loggingOut:
                self.innWnd.callRemote("close")
            self.innWnd = None
        
        if self.player:
            self.player.inn = None
        self.player = None
        self.innkeeper = None
        
    def error(self):
        self.player.endInteraction()
        
    def gotInnWnd(self,innWnd):
        if not self.player:
            return
        self.innWnd = innWnd
        self.sendLists()
        innWnd.callRemote("open",self,self.innkeeper.name)


