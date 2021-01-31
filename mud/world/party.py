# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#a party is a group of up to 6 characters, controlled by the same player

#this could use a rewrite!!!!

from character import Character
from mob import Mob
from mud.world.shared.playdata import RootInfo,CharacterInfo
from defines import *
import traceback



class Party:
    def __init__(self):
        self.player = None
        self.members = []
        self.charInfos = {}
    
    
    def removeCharacter(self,char):
        player = self.player
        self.members.remove(char)
        player.curChar = self.members[0]
        # Assign cursor item to current character to avoid
        #  confusion and any item handling problems.
        if player.cursorItem and player.cursorItem.character == char:
            player.cursorItem.setCharacter(player.curChar)
        player.zone.removeMob(char.mob)
        
        player.zone.simAvatar.mind.callRemote("removePlayerMobInfo",player.simObject.id,char.mob.id)
        char.mob.character = None
        char.mob = None
        char.charInfo = None
        
        cinfos = {}
        for x,c in enumerate(self.members):
            cinfos[x] = c.charInfo
            c.mob.charIndex = x
        
        self.charInfos = cinfos
        
        player.rootInfo = RootInfo(player,self.charInfos)
        player.mind.callRemote("setRootInfo",player.rootInfo)
        
        player.mind.callRemote("setCurCharIndex",0)
        
        id = 0
        if player.curChar.mob.target:
            id = player.curChar.mob.target.id
        player.zone.simAvatar.mind.callRemote("setSelection",player.simObject.id,id,0)

        if player.modelChar == char:
            #have to change model
            player.avatarCharName = player.curChar.name
            player.modelChar = player.curChar
            player.modelIndex = player.curChar.mob.charIndex
            player.zone.simAvatar.mind.callRemote("setPlayerSpawnInfo",player.simObject.id,player.curChar.spawn.name)
            
        player.zone.mobLookup[player.simObject]=self.members[0].mob
    
    
    def addCharacter(self,char):
        player = self.player
        char.charInfo = CharacterInfo(char)
        
        m = Mob(char.spawn,player.zone,player,char)
        m.simObject = player.simObject
        m.charIndex = len(self.members)
        
        char.mob = m
        
        self.members.append(char)
        
        self.charInfos[m.charIndex] = char.charInfo
        
        for item in char.items:
            if item.slot == RPG_SLOT_CURSOR:
                player.cursorItem = item # catch any items in character cursor_slot
                # Assign cursor item to current character to avoid
                #  confusion and any item handling problems.
                player.cursorItem.setCharacter(player.curChar)
                player.updateCursorItem(None)
                break
        
        player.zone.simAvatar.mind.callRemote("addPlayerMobInfo",player.simObject.id,m.mobInfo,char.spawn.getSpawnInfo())
        
        player.zone.activeMobs.append(m)
        
        if char.dead:
            player.zone.detachMob(m)
        
        player.restoreTradeItems()
        
        player.rootInfo = RootInfo(player,self.charInfos)
        player.mind.callRemote("setRootInfo",player.rootInfo)
        
        player.updateKOS()
    
    
    #this is called when we first enter the world
    def assemble(self,player,characters):
        self.player = player
        
        alldead = True
        for x,c in enumerate(characters):
            char = Character.byName(c)
            
            if not char.dead:
                alldead = False
            
            char.charInfo = CharacterInfo(char)
            if char.player != player: #cheater!!!
                traceback.print_stack()
                print "AssertionError: %s plays a non-owned character!"%player.name
                return
            
            #create the mob
            m = Mob(char.spawn,player.zone,player,char)
            m.charIndex = x
            char.mob = m
            
            self.members.append(char)
            
            self.charInfos[x] = char.charInfo
            
            for item in char.items:
                if item.slot == RPG_SLOT_CURSOR:
                    player.cursorItem = item # catch any items in character cursor_slot
                    break
        
        index = 0
        for c in self.members:
            if c.name == player.avatarCharName:
                player.modelChar = c
                player.modelIndex = index
                break
            index += 1
        else:
            player.avatarCharName = self.members[0].name
            player.modelChar = self.members[0]
            player.modelIndex = 0
        
        if alldead:
            for c in self.members:
                c.dead = False
                c.mob.health = 1
                c.mob.mana = 1
        
        player.curChar = self.members[0]
        # Assign cursor item to current character to avoid
        #  confusion and any item handling problems.
        if player.cursorItem:
            player.cursorItem.setCharacter(player.curChar)
            player.updateCursorItem(None)
        player.restoreTradeItems()
    
    
    def reassemble(self):
        player = self.player
        
        for x,c in enumerate(self.members):
            m = Mob(c.spawn,player.zone,player,c)
            m.charIndex = x
            c.mob = m
            
            c.charInfo = CharacterInfo(c)
            self.charInfos[x] = c.charInfo
        
        player.curChar = self.members[0]
        # Assign cursor item to current character to avoid
        #  confusion and any item handling problems.
        if player.cursorItem:
            player.cursorItem.setCharacter(player.curChar)
            player.updateCursorItem(None)
        player.restoreTradeItems()


