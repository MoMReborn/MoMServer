# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.persistent import Persistent
from mud.world.character import Character,CharacterFaction
from mud.world.core import AllowHarmful,CollapseMoney,GetRange, \
    GetRangeMin,IsKOS
from mud.world.defines import *
from mud.world.item import ItemInstance,ItemProto
from mud.world.messages import MessagePersonalize
from mud.worlddocs.utils import GetTWikiName

from datetime import datetime
from math import ceil,degrees,sqrt
from sqlobject import *
from time import time as sysTime
import traceback



XPBONUS = (1,1.6,1.8,2.2,2.4,3.0)

class PlayerXPCredit(Persistent):
    player = ForeignKey('Player')
    xp = IntCol(default=0)
    
class PlayerMonsterSpawn(Persistent):
    player = ForeignKey('Player')
    spawn = StringCol()



class Player(Persistent):    
    publicName = StringCol(alternateID = True,default="")
    fantasyName = StringCol(alternateID = True,default="")
    password = StringCol(default="")
    
    #all characters are bound to the same fate, er bindpoint/log point
    bindTransformInternal = StringCol(default="0 0 0 1 0 0 0") 
    bindZone = ForeignKey('Zone')
    logTransformInternal = StringCol(default="0 0 0 1 0 0 0") 
    logZone = ForeignKey('Zone')

    darknessBindTransformInternal = StringCol(default="0 0 0 1 0 0 0") 
    darknessBindZone = ForeignKey('Zone')
    darknessLogTransformInternal = StringCol(default="0 0 0 1 0 0 0") 
    darknessLogZone = ForeignKey('Zone')

    monsterBindTransformInternal = StringCol(default="0 0 0 1 0 0 0") 
    monsterBindZone = ForeignKey('Zone')
    monsterLogTransformInternal = StringCol(default="0 0 0 1 0 0 0") 
    monsterLogZone = ForeignKey('Zone')
    
    xpCredits = MultipleJoin('PlayerXPCredit')
    characters = MultipleJoin('Character')
    creationTime = DateTimeCol(default = datetime.now)
    
    lightTin =      IntCol(default=0)
    lightCopper =   IntCol(default=0)
    lightSilver =   IntCol(default=0)
    lightGold =     IntCol(default=0)
    lightPlatinum = IntCol(default=0)
    
    darknessTin =      IntCol(default=0)
    darknessCopper =   IntCol(default=0)
    darknessSilver =   IntCol(default=0)
    darknessGold =     IntCol(default=0)
    darknessPlatinum = IntCol(default=0)

    monsterTin =      IntCol(default=0)
    monsterCopper =   IntCol(default=0)
    monsterSilver =   IntCol(default=0)
    monsterGold =     IntCol(default=0)
    monsterPlatinum = IntCol(default=0)
    
    monsterSpawns = MultipleJoin('PlayerMonsterSpawn')
    
    avatarCharName = StringCol(default = "")
    
    #channel filters
    channelGlobal = BoolCol(default=True)
    channelWorld = BoolCol(default=True)
    channelZone = BoolCol(default=True)
    channelCombat = BoolCol(default=False)
    
    bankItemsInternal = MultipleJoin("Item")
    
    remoteLeaderNames = {}
    
    encounterPreserveTimer = IntCol(default=0)
    
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        
        self.enteringWorld = True
        self.darkness = False
        self.monster = False
        self.party = None
        
        self.premium = False
        
        self.guildName = ""
        self.guildInfo = ""
        self.guildMOTD = ""
        self.guildRank = 0
        self.guildInvite = None
        
        #not persistent, because I don't want to update the database right now, some day
        #these should actually be client side maybe
        self.channelGlobal = True
        self.channelWorld = True
        self.channelZone = True
        
        self.channelCombat = False

        self.channelClan = True
        self.channelHelp = True
        self.channelOffTopic = True
        
        #whatever the most recent character name is
        self.charName = ""
        
        self.overrideScale = False
        
        self.reset()
    
    
    def _get_bankItems(self):
        if self.bankList == None:
            bankList = self.bankList = {}
            for item in self.bankItemsInternal:
                if item.itemProto.flags & RPG_ITEM_ETHEREAL:
                    item.destroySelf()
                    continue
                slot = item.slot
                if slot < RPG_SLOT_BANK_BEGIN or slot >= RPG_SLOT_BANK_END or bankList.has_key(slot):
                    print "WARNING: invalid bank item slot, item %s from player %s deleted!"%(item.name,self.name)
                    item.destroySelf()
                    continue
                bankList[slot] = ItemInstance(item)
        return self.bankList
    
    
    def reset(self):
        self.friends = set()
        self.friendsInfo = {}
        self.curChar = None
        self.zone = None
        self.avatar = None
        self.mind = None
        self.simObject = None
        self.cursorItem = None
        self.interacting = None
        self.dialog = None
        self.curDialogLine = None
        self.transfering = False
        self.cinfoDirty = True
        self.alliance = None
        
        self.textMessages = []
        self.textTicker = 0
        
        self.extract = True
        
        self.allianceTimeStamp = None
        
        #time, effect, cnames tuple
        self.resurrection = None
        #time, effect tuple
        self.resurrectionRequest = None

        
        self.realm = None
        self.telelink = None
        
        self.lastInnAddTime = sysTime()
        self.cserverInfos = None
        
        self.triggeredZoneOptions = []
        self.triggeredZoneLink = None
        self.invite = None
        self.name = self.fantasyName
        self.loggingOut = False
        self.trade = None
        self.world = None
        self.inn = None
        if self.party:
            for m in self.party.members:
                if m.mob:
                    m.mob.character = None
                    m.mob.player = None
                m.mob = None
        self.party = None
        self.rootInfo = None
        
        self.msgCombatNotCloseEnough = 0
        self.msgCombatCantSee = 0
        self.msgCombatNotFacing = 0
        
        self.trackingTimer = 0
        
        self.lastTell = None
        self.looting = None
        
        self.spellEffectCastTime = sysTime()
        self.spellEffectBeginTime = sysTime()
        
        self.bankList = None
        
        self.encounterSetting = RPG_ENCOUNTER_PVE
        
        # This gets set to True if the player party walks. Default is run.
        # Mobs have this handled specially and all player mobs in the same
        #  party are displayed by a single avatar. So it wouldn't make
        #  sense to put this somewhere else.
        self.walk = False


#money
    
    def _get_tin(self):
        if self.darkness:
            return self.darknessTin
        if self.monster:
            return self.monsterTin
        return self.lightTin

    def _get_copper(self):
        if self.darkness:
            return self.darknessCopper
        if self.monster:
            return self.monsterCopper
        return self.lightCopper
        
    def _get_silver(self):
        if self.darkness:
            return self.darknessSilver
        if self.monster:
            return self.monsterSilver
        return self.lightSilver

    def _get_gold(self):
        if self.darkness:
            return self.darknessGold
        if self.monster:
            return self.monsterGold
        return self.lightGold

    def _get_platinum(self):
        if self.darkness:
            return self.darknessPlatinum
        if self.monster:
            return self.monsterPlatinum
        return self.lightPlatinum

    def _set_tin(self,amount):
        if self.darkness:
            self.darknessTin = amount
            return
        if self.monster:
            self.monsterTin = amount
            return
        self.lightTin = amount

    def _set_copper(self,amount):
        if self.darkness:
            self.darknessCopper = amount
            return
        if self.monster:
            self.monsterCopper = amount
            return
        self.lightCopper = amount

    def _set_silver(self,amount):
        if self.darkness:
            self.darknessSilver = amount
            return
        if self.monster:
            self.monsterSilver = amount
            return
        self.lightSilver = amount

    def _set_gold(self,amount):
        if self.darkness:
            self.darknessGold = amount
            return
        if self.monster:
            self.monsterGold = amount
            return
        self.lightGold = amount

    def _set_platinum(self,amount):
        if self.darkness:
            self.darknessPlatinum = amount
            return
        if self.monster:
            self.monsterPlatinum = amount
            return
        self.lightPlatinum = amount
    
    
    def _get_bindTransform(self):
        return map(float, self.bindTransformInternal.split(" "))

    def _set_bindTransform(self,transform):
        self.bindTransformInternal = ' '.join(map(str,transform))
        
    def _get_logTransform(self):
        return map(float, self.logTransformInternal.split(" "))

    def _set_logTransform(self,transform):
        self.logTransformInternal = ' '.join(map(str,transform))
        
    #darkness
        
    def _get_darknessBindTransform(self):
        return map(float, self.darknessBindTransformInternal.split(" "))

    def _set_darknessBindTransform(self,transform):
        self.darknessBindTransformInternal = ' '.join(map(str,transform))
        
    def _get_darknessLogTransform(self):
        return map(float, self.darknessLogTransformInternal.split(" "))

    def _set_darknessLogTransform(self,transform):
        self.darknessLogTransformInternal = ' '.join(map(str,transform))


    #monster
        
    def _get_monsterBindTransform(self):
        return map(float, self.monsterBindTransformInternal.split(" "))

    def _set_monsterBindTransform(self,transform):
        self.monsterBindTransformInternal = ' '.join(map(str,transform))
        
    def _get_monsterLogTransform(self):
        return map(float, self.monsterLogTransformInternal.split(" "))

    def _set_monsterLogTransform(self,transform):
        self.monsterLogTransformInternal = ' '.join(map(str,transform))
    
    
    def sendGameText(self,textCode,text,mob=None,tgt=None,stripML=False):
        text = str(text)
        if mob:
            text = MessagePersonalize(text,mob,tgt)
        self.textMessages.append((0,textCode,text,"",stripML))
        #try:
        #    self.mind.callRemote("receiveGameText",textCode,str(text))
        #except:
        #    pass
        
    def sendSpeechText(self,textCode,text,src=""):
        if textCode == RPG_MSG_SPEECH_ZONE and not self.channelZone:
            return
        if textCode == RPG_MSG_SPEECH_GLOBAL and not self.channelGlobal:
            return
        if textCode == RPG_MSG_SPEECH_WORLD and not self.channelWorld:
            return
        self.textMessages.append((1,textCode,str(text),src.upper(),False))
        #try:
        #    self.mind.callRemote("receiveSpeechText",textCode,str(text))
        #except:
        #    pass
    
    
    def endInteraction(self,closeWindow=True):
        if not self.interacting:
            return
        
        if hasattr(self.interacting,"interactTimes"):
            self.interacting.interactTimes[self] = sysTime()
        
        self.interacting.interacting = None
        self.interacting = None
        
        if hasattr(self,"zone"):
            if self.zone:
                for c in self.party.members:
                    self.zone.setTarget(c.mob,None)
        
        if closeWindow:
            self.mind.callRemote("closeNPCWnd")
    
    
    def giveItem(self,itemname,fullStack=False,caseInsensitive=False):
        try:
            if caseInsensitive:
                con = ItemProto._connection.getConnection()
                ip = ItemProto.get(con.execute("SELECT id FROM item_proto WHERE lower(name)=lower(\"%s\") LIMIT 1;"%itemname).fetchone()[0])
            else:
                ip = ItemProto.byName(itemname)
        except:
            return None
        
        item = ip.createInstance()
        if fullStack:
            item.stackCount = ip.stackMax
        
        if not self.curChar.giveItemInstance(item):
            item.destroySelf()
            return None
        
        return item
    
    
    def takeItem(self,item):
        if not item:
            return
        if (item.player and item.player == self) or (item.character and item.character in self.party.members):
            item.destroySelf()
            return
        raise ValueError,"Attempting to take an item from player %s not belonging to this player!"%self.publicName
    
    
    def collapseMoney(self):
        tin = self.tin
        copper = self.copper
        silver = self.silver
        gold = self.gold
        platinum = self.platinum

        #convert to tin
        tin = long(tin)
        tin += copper*100L
        tin += silver*10000L
        tin += gold*1000000L
        tin += platinum*100000000L
        
        self.tin,self.copper,self.silver,self.gold,self.platinum = CollapseMoney(tin)
    
    def checkMoney(self,worth):
        if not worth:
            return True
        tin = self.tin
        copper = self.copper
        silver = self.silver
        gold = self.gold
        platinum = self.platinum
        
        if tin < 0 or copper < 0 or silver < 0 or gold < 0 or platinum < 0:
            traceback.print_stack()
            print "AssertionError: player %s wealth whackiness!"%self.publicName
            return
        
        tin = long(tin)
        tin += copper*100L
        tin += silver*10000L
        tin += gold*1000000L
        tin += platinum*100000000L
        
        if tin >= worth:
            return True
        return False
    
    def takeMoney(self,worth):
        if not worth:
            return
        if not self.checkMoney(worth):
            traceback.print_stack()
            print "AssertionError: player doesn't have enough money!"
            return
        
        tin = self.tin
        copper = self.copper
        silver = self.silver
        gold = self.gold
        platinum = self.platinum
        
        if tin < 0 or copper < 0 or silver < 0 or gold < 0 or platinum < 0:
            traceback.print_stack()
            print "AssertionError: player %s wealth whackiness!"%self.publicName
            return
        
        #convert to tin
        tin = long(tin)
        tin += copper*100L
        tin += silver*10000L
        tin += gold*1000000L
        tin += platinum*100000000L
        
        tin -= worth
        self.tin,self.copper,self.silver,self.gold,self.platinum = CollapseMoney(tin)
    
    def giveMoney(self,worth):
        if not worth:
            return
        #convert to tin
        tin = long(self.tin)
        tin += self.copper*100L
        tin += self.silver*10000L
        tin += self.gold*1000000L
        tin += self.platinum*100000000L
        
        tin += worth
        self.tin,self.copper,self.silver,self.gold,self.platinum = CollapseMoney(tin)
    
    
    def rewardXP(self,totalXP,compareToHighest=1):
        #the no single XP giving event reward more than 1/level*5 takes care of grouping 
        #uber and newbie characters... so just do a flat out share
            
        members = []
        for c in self.party.members:
            if not c.dead:
                members.append(c)
                
        if not len(members):
            return
        
        num = len(members)
        bonus = XPBONUS[num-1]
        totalXP*=bonus
        
        memberXP = int(ceil(totalXP/num))
        if not memberXP:
            return
        
        for c in members:
            if compareToHighest > (1.2*c.mob.plevel + 8):
                c.gainXP(memberXP,True,None,0.5)
            else:
                c.gainXP(memberXP)
    
    
    def updateCursorItem(self,oldCursorItem):
        party = self.party
        
        #catch character cursor slot wackiness 
        if not self.cursorItem:
            for c in party.members:
                for item in c.items:
                    if item.slot == RPG_SLOT_CURSOR:
                        self.cursorItem = item
                        break
            
            if not self.cursorItem and not self.trade:
                #look for trade items gone wrong
                for c in party.members:
                    for item in c.items:
                        if RPG_SLOT_TRADE_END > item.slot >= RPG_SLOT_TRADE_BEGIN:
                            self.cursorItem = item
                            break
        
        if oldCursorItem != self.cursorItem:
            if self.cursorItem:
                self.mind.callRemote("setCursorItem",self.cursorItem.itemInfo)
            else:
                self.mind.callRemote("setCursorItem",None)
    
    
    def restoreTradeItems(self):
        tradeItems = {}
        
        # Run through all party members.
        for c in self.party.members:
            # For each member run through all items.
            for item in c.items:
                # If an item has a trade slot assigned, add it to the
                #  trade item dictionary.
                if RPG_SLOT_TRADE_END > item.slot >= RPG_SLOT_TRADE_BEGIN:
                    tradeItems.setdefault(c, []).append(item)
        
        # Now run through all gathered trade items and try to place them
        #  back into inventory.
        for c,itemList in tradeItems.iteritems():
            for item in itemList:
                # If the character owning the item has no more space
                #  in inventory for the item, try to give it to a different
                #  party member.
                if not c.giveItemInstance(item):
                    for member in self.party.members:
                        # Skip the original owner.
                        if member == c:
                            continue
                        if member.giveItemInstance(item):
                            break
                    
                    # If we get here, the item must remain in limbo.
                    # It will be accessible again when emptying the cursor
                    #  or starting a new trade with the owning character.
    
    
    def giveItemInstance(self,item):
        #first try the current char
        if self.curChar.giveItemInstance(item):
            return True
        
        for c in self.party.members:
            if c == self.curChar:
                continue
            if c.giveItemInstance(item):
                return True
        return False
                
    def getFreeCarrySlots(self):
        free = 0
        for c in self.party.members:
            free+=len(c.getFreeCarrySlots())
        return free
    
    
    def updateTracking(self):
        # Don't track if we haven't spawned yet.
        if not self.zone:
            return
        
        # Update tracking every 5 seconds.
        self.trackingTimer = 30
        
        # Cache our own mob instance.
        mymob = self.party.members[0].mob
        if not mymob:
            return
        
        # Determine best tracking skill from all living
        #  party members.
        # Also skillup tracking.
        bestT = 0
        for c in self.party.members:
            if c.dead:
                continue
            c.checkSkillRaise("Tracking",20,50,False,True)
            t = c.mob.mobSkillProfiles['Tracking'].maxValue
            if t > bestT:
                bestT = t
        
        # Calculate tracking range from tracking skill.
        # Minimum tracking range with zero skill is 150.
        trackRange = 150 + bestT / 2
        
        players = []
        tracking = {}
        
        for otherMob in self.zone.activeMobs:
            # Ignore ourselves and detached mobs.
            if otherMob.player == self or otherMob.detached:
                continue
            
            if otherMob.simObject.simZombie:
                continue
            
            # Add only one mob per player. Also only fully spawned playermobs.
            if otherMob.player and (otherMob.player in players or not otherMob.player.simObject):
                continue
            
            # Pets don't show up on tracking.
            if otherMob.master:
                continue
            
            # Classify mobs: 0 = normal mobs, 1 = hostile mobs,
            #  2 = vendors, 3 = mobs with dialogs,
            #  4 = non-hostile players, 5 = inn keepers,
            #  6 = pets owned by player.
            if otherMob.player:
                if AllowHarmful(otherMob,mymob):
                    type = 1
                else:
                    type = 4
            else:
                type = 0
                kos = IsKOS(otherMob,mymob)
                if kos:
                    type = 1
                else:
                    if otherMob.vendor:
                        type = 2
                    dialog = otherMob.spawn.dialog
                    if dialog and dialog.greeting and dialog.greeting.numChoices:
                        type = 3
                    if otherMob.spawn.flags&RPG_SPAWN_INN:
                        type = 5
            
            # Calculate distance to other mob to
            #  check if it's in tracking range.
            distance = GetRange(mymob,otherMob)
            
            passed = False
            # Non-hostile players can be tracked across whole zone.
            # For other mobs, check distance.
            if type != 4:
                # If the mob can see invis, calculate rangeModifier.
                if not mymob.seeInvisible:
                    
                    # Modify track range if the mob is attacking or casting.
                    if otherMob.attacking or otherMob.casting:
                        rangeModifier = float(otherMob.visibility) + .5
                    else:
                        rangeModifier = float(otherMob.visibility)
                    
                    # Cap modifier.
                    if 1 < rangeModifier:
                        rangeModifier = 1.0
                    
                    # If the distance between the mob and otherMob is less than
                    #  the modified track range based on other mob visibility,
                    #  then add it to the track list.
                    if distance <= (float(trackRange) * rangeModifier):
                        passed = True
                
                # The mob can see invis, so do not modify the range.
                elif distance <= float(trackRange):
                    passed = True
            
            # If the current mob is trackable, add it to the tracking list.
            if type == 4 or passed:
                if otherMob.player:
                    players.append(otherMob.player)
                    # If the mob is a player who is not allowed to harm us, display a normal name.
                    if 4 == type:
                        tracking[otherMob.id] = (otherMob.player.charName,otherMob.player.simObject.position,distance,type)
                    # Otherwise, it is a player who can harm the tracker, surround the name by stars.
                    else:
                        tracking[otherMob.id] = ("*%s*"%otherMob.player.charName,otherMob.player.simObject.position,distance,type)
                else:
                    tracking[otherMob.id] = (otherMob.name,otherMob.simObject.position,distance,type)
        
        # Handle owned pets separately, add them to tracking.
        for c in self.party.members:
            m = c.mob
            if m and not m.detached and m.pet:
                m = m.pet
                tracking[m.id] = ("%s's %s"%(c.name,m.name),m.simObject.position,GetRange(mymob,m),6)
        
        tracking['RANGE'] = trackRange
        
        # Send tracking data over to client.
        self.mind.callRemote("setTracking",tracking)
    
    
    def tick(self):
        
        #move to client, send combat stats in infos
        if self.msgCombatNotCloseEnough > 0:
            self.msgCombatNotCloseEnough -= 1
        
        if self.msgCombatCantSee > 0:
            self.msgCombatCantSee -= 1
        
        if self.msgCombatNotFacing > 0:
            self.msgCombatNotFacing -= 1
        
        self.trackingTimer -= 3
        if self.trackingTimer <= 0:
            self.updateTracking()
            
            # Update mute timer at same intervals as tracking.
            try:
                muteTime = self.world.mutedPlayers[self.publicName]
            except KeyError:
                muteTime = 0
            self.mind.callRemote("setMuteTime",muteTime)
            
            # Only update friends list every 5 seconds, same as tracking.
            #OPTIMIZE
            memberNames = (c.name.upper() for c in self.party.members)
            finfo = {}
            if len(self.friends) or self.guildName:
                for charName,pinfo in self.world.globalPlayers.iteritems():
                    if charName in memberNames:
                        continue
                    cname,gname,wname,zname = pinfo
                    matchGuild = gname and gname == self.guildName
                    if matchGuild or charName in self.friends:
                        finfo[cname] = (matchGuild,wname,zname)
            
            if self.friendsInfo != finfo:
                self.friendsInfo = finfo
                try:
                    self.mind.callRemote("setFriendsInfo",finfo)
                except:
                    pass
        
        self.textTicker -= 3
        if self.textTicker < 0:
            self.textTicker = 7
            if len(self.textMessages):
                try:
                    self.mind.callRemote("receiveTextList",self.textMessages)
                except:
                    pass
            self.textMessages = []
        
        # Don't use itervalues here because item tick might modify
        #  the bank dictionary.
        for item in self.bankItems.values():
            item.tick()
        
        if self.inn:
            # to account for the new distance calculation on innkeeper interaction
            if GetRangeMin(self.party.members[0].mob,self.inn.innkeeper) > 5:
                self.inn.endInteraction()
        
        if self.interacting:
            from mud.world.dialog import DialogTrigger
            from mud.world.mob import Mob
            
            if isinstance(self.interacting,Mob):
                #make sure to sync range calc to commandinteract (this buffers a bit further out)
                range = (self.interacting.spawn.radius * self.interacting.spawn.modifiedScale) * 2.75
                pos = self.interacting.simObject.position
            elif isinstance(self.interacting,DialogTrigger):
                range = self.interacting.range
                pos = self.interacting.position
            
            myPosition = self.simObject.position
            
            x = myPosition[0] - pos[0]
            y = myPosition[1] - pos[1]
            z = myPosition[2] - pos[2]
            
            dist = sqrt(x * x + y * y + z * z)
            if dist > range:
                self.endInteraction()
    
    
    def logout(self):
        try:
            #clear inn if any
            self.lastTell = None
            
            if self.inn:
                self.inn.endInteraction()
                self.inn = None
            
            allDead = False
            if self.party and self.party.members:
                allDead = True
                for c in self.party.members:
                    if not c.dead:
                        allDead = False
                    # Since list gets parsed in reverse order, there's no need
                    #  to copy it for modification during the loop.
                    for item in reversed(c.items):
                        if item.flags & RPG_ITEM_ETHEREAL:
                            item.destroySelf()
                        else:
                            item.storeToItem()
            try:
                # Using values() instead of itervalues() already makes sure
                #  we work on a copy, so deleting during loop is safe.
                for item in self.bankList.values():
                    if item.flags & RPG_ITEM_ETHEREAL:
                        item.destroySelf()
                    else:
                        item.storeToItem()
            except:  # bankItems were never queried, no save needed
                pass
            
            self.cursorItem = None
            
            if self.looting:
                self.looting.looter = None
                self.looting = None
            
            if self.invite:
                self.invite.cancel()
                self.invite = None
                
            if self.trade:
                self.trade.cancel()
            
            if hasattr(self,"alliance") and self.alliance:
                self.alliance.leave(self)
            
            if allDead:
                if self.darkness:
                    self.darknessLogZone = self.curChar.deathZone
                    self.darknessLogTransform = self.curChar.deathTransform
                elif self.monster:
                    self.monsterLogZone = self.curChar.deathZone
                    self.monsterLogTransform = self.curChar.deathTransform
                else:
                    self.logZone = self.curChar.deathZone
                    self.logTransform = self.curChar.deathTransform
            if hasattr(self,"zone"):
                if self.zone:
                    self.endInteraction(False)
                    
                    if not allDead and self.simObject:
                        transform = list(self.simObject.position)
                        transform.extend(list(self.simObject.rotation))
                        transform[-1] = degrees(transform[-1])
                        
                        if self.darkness:
                            self.darknessLogZone = self.zone.zone
                            self.darknessLogTransform = transform
                        elif self.monster:
                            self.monsterLogZone = self.zone.zone
                            self.monsterLogTransform = transform
                        else:
                            self.logZone = self.zone.zone
                            self.logTransform = transform
                    
                    if self.zone.owningPlayer != self:
                        from mud.world.theworld import World
                        world = World.byName("TheWorld")
                        if not world.singlePlayer:
                            self.zone.kickPlayer(self)
                        self.zone.removePlayer(self)
                
                self.zone = None
        except:
            traceback.print_exc()
        
        if self.world:
            self.world.playerLeaveWorld(self)
            if not self.world.singlePlayer:
                self.world.commit(True)
        self.world = None
        
        self.reset()
        #self.expire()
    
    
    def prepForZoneOut(self):
        self.encounterPreserveTimer = int(sysTime())
        self.backupItems()
    
    
    # Function to backup volatile player data, things that aren't
    #  written to database directly - used for single player backup.
    # Could be that some things still are missing ...
    def backupPlayer(self):
        # Backup items.
        self.backupItems()
        
        # Backup mob data to character.
        allDead = False
        if self.party and self.party.members:
            allDead = True
            for char in self.party.members:
                if char.dead:
                    continue
                allDead = False
                mob = char.mob
                if mob and not mob.detached:
                    if mob.health > 0 and not char.dead:
                        char.health = int(mob.health)
                        char.mana = int(mob.mana)
                        char.stamina = int(mob.stamina)
        
        # Backup log and zone locations.
        if allDead:
            if self.darkness:
                self.darknessLogZone = self.curChar.deathZone
                self.darknessLogTransform = self.curChar.deathTransform
            elif self.monster:
                self.monsterLogZone = self.curChar.deathZone
                self.monsterLogTransform = self.curChar.deathTransform
            else:
                self.logZone = self.curChar.deathZone
                self.logTransform = self.curChar.deathTransform
        elif hasattr(self,"zone"):
            if self.zone:
                if self.simObject:
                    transform = list(self.simObject.position)
                    transform.extend(list(self.simObject.rotation))
                    transform[-1] = degrees(transform[-1])
                    
                    if self.darkness:
                        self.darknessLogZone = self.zone.zone
                        self.darknessLogTransform = transform
                    elif self.monster:
                        self.monsterLogZone = self.zone.zone
                        self.monsterLogTransform = transform
                    else:
                        self.logZone = self.zone.zone
                        self.logTransform = transform
    
    
    def backupItems(self):
        try:
            map(ItemInstance.storeToItem,self.bankList)
        except:
            # Bank items were never queried, no save needed.
            pass
        if self.party and self.party.members:
            map(Character.backupItems,self.party.members)
    
    
    # Take away a specified set of item protos from the player. The set
    #  can be provided with itemDict as a dictionary with item protos as
    #  keys and counts as values.
    # Set silent to True if the player should not get feedback of the check.
    def takeItems(self, itemDict, silent=False):
        
        # Do some sanity check on the items to be taken away.
        # Don't use iteritems so we iterate over a copy.
        for proto,count in itemDict.items():
            if count <= 0:
                del itemDict[proto]
        
        # If the dictionary to check is empty, return early.
        if not len(itemDict):
            return
        
        # Run through all of this Player's party members.
        for member in self.party.members:
            
            # Try to take away the items from the current Character.
            member.takeItems(itemDict,silent)
            
            # If all items required were taken away, return.
            if not len(itemDict):
                return
            
            # Otherwise continue to the next Character in the party.
    
    
    # Checks if the player has a specified set of item protos which can be
    #  provided with itemDict as a dictionary with item protos as keys and
    #  counts as values.
    # Set silent to True if the player should not get feedback of the check.
    # Returns True if the check was successful, False otherwise.
    def checkItems(self, itemDict, silent=False):
        
        # Do some sanity check on the item requirements.
        # Don't use iteritems so we iterate over a copy.
        for proto,count in itemDict.items():
            if count <= 0:
                del itemDict[proto]
        
        # If the dictionary to check is empty, return early.
        if not len(itemDict):
            return True
        
        # Run through all of this Player's party members.
        for member in self.party.members:
            
            # Run through all items in the current Character's possession.
            for item in member.items:
                
                # Skip items in a trade slot.
                if RPG_SLOT_TRADE_END > item.slot >= RPG_SLOT_TRADE_BEGIN:
                    continue
                # Also skip items in a loot slot.
                if RPG_SLOT_LOOT_END > item.slot >= RPG_SLOT_LOOT_BEGIN:
                    continue
                
                # Start by checking container contents.
                if item.container:
                    
                    # Run through all items in the container.
                    for citem in item.container.content:
                        
                        # Get the current container item's item proto.
                        citemProto = citem.itemProto
                        
                        # Get the amount of items we need of this specific
                        #  item proto.
                        needed = itemDict.get(citemProto,None)
                        
                        # If we don't need any, skip to the next content item.
                        if not needed:
                            continue
                        
                        # Get the stack count of the current content item.
                        sc = citem.stackCount
                        if not sc:
                            sc = 1
                        
                        # If the requirement is only partially satisfied,
                        #  decrement the needed amount and continue to the
                        #  next content item.
                        if sc < needed:
                            itemDict[citemProto] -= sc
                            continue
                        
                        # Otherwise the requirement was completely satisfied,
                        #  so remove it from the dictionary.
                        del itemDict[citemProto]
                        
                        # Check if there actually are more items to be checked
                        #  for and return success otherwise.
                        if not len(itemDict):
                            return True
                
                # Get the current item's item proto.
                itemProto = item.itemProto
                
                # Get the amount of items we need of this specific item proto.
                needed = itemDict.get(itemProto,None)
                
                # If we don't need any, skip to the next item.
                if not needed:
                    continue
                
                # Get the stack count of the current item.
                sc = item.stackCount
                if not sc:
                    sc = 1
                
                # If the requirement is only partially satisfied, decrement
                #  the needed amount and continue to the next item.
                if sc < needed:
                    itemDict[itemProto] -= sc
                    continue
                
                # Otherwise the requirement was completely satisfied, so remove
                #  it from the dictionary.
                del itemDict[itemProto]
                
                # Check if there actually are more items to be checked for and
                #  return success otherwise.
                if not len(itemDict):
                    return True
        
        # If we get here, there are still items in the dictionary that couldn't
        #  be found.
        
        # Give feedback to the player.
        if not silent:
            self.sendGameText(RPG_MSG_GAME_DENIED,"You need %s.\\n"%', '.join('<a:Item%s>%i %s</a>'%(GetTWikiName(ip.name),c,ip.name) for ip,c in itemDict.iteritems()))
        
        # Return the failure.
        return False
    
    
    def updateKOS(self):
        from mud.world.faction import KOS
        
        if self.party:
            for c in self.party.members:
                spawn = c.spawn
                KOS[spawn.name] = []
                for f in c.characterFactions:
                    for s in f.faction.spawns:
                        try:
                            if f.points < RPG_FACTION_DISLIKED:
                                #player kos
                                #KOS[spawn.name].append(s.name)
                                if spawn.name not in KOS[s.name]:
                                    KOS[s.name].append(spawn.name)
                            else:
                                if spawn.name in KOS[s.name]:
                                    KOS[s.name].remove(spawn.name)
                        except:
                            pass
    
    
    def rewardFaction(self, faction, amount):
        if faction.realm != -1:
            if faction.realm != self.realm:
                    return
        
        from mud.world.faction import KOS
        
        for c in self.party.members:
            spawn = c.spawn
            KOS[spawn.name] = []
            gotit = False
            for f in c.characterFactions:
                if f.faction == faction:
                    f.points += amount
                    gotit = True
                    for s in f.faction.spawns:
                        try:
                            if f.points < RPG_FACTION_DISLIKED:
                                if spawn.name not in KOS[s.name]:
                                    KOS[s.name].append(spawn.name)
                            else:
                                if spawn.name in KOS[s.name]:
                                    KOS[s.name].remove(spawn.name)
                        except:
                            pass
                    break
            
            if not gotit:
                CharacterFaction(faction=faction,character=c,points=amount)
        
            if amount > 0:    
                self.sendGameText(RPG_MSG_GAME_GREEN,r'%s\'s reputation with %s has increased!\n'%(c.name,faction.name))
            if amount < 0:    
                self.sendGameText(RPG_MSG_GAME_RED,r'%s\'s reputation with %s has decreased!\n'%(c.name,faction.name))
    
    
    def applyEncounterSetting(self,index,forward=False):
        if self.encounterSetting == index:
            return
        self.encounterSetting = index
        if forward:
            self.mind.callRemote("checkEncounterSetting", False, index, True)
        
        # tell pet to cease unallowed attacks
        if index != RPG_ENCOUNTER_PVP:
            for c in self.party.members:
                if c.mob and c.mob.pet:
                    pet = c.mob.pet
                    if pet.attacking and not AllowHarmful(pet,pet.target):
                        pet.cancelAttack()
        
        if index == RPG_ENCOUNTER_PVE:
            self.sendGameText(RPG_MSG_GAME_GREEN,r'You no longer have to fear attacks from fellow players. But keep an eye out, the environment still doesn\'t like you.\n')
        elif index == RPG_ENCOUNTER_RVR:
            self.sendGameText(RPG_MSG_GAME_YELLOW,r'Watch your back! Hostile encounters with players from other realms may occur.\n')
            self.mind.callRemote("playSound","sfx/College_DrumCadence11.ogg")
        elif index == RPG_ENCOUNTER_GVG:
            self.sendGameText(RPG_MSG_GAME_YELLOW,r'Watch your back! Hostile encounters with players from other guilds may occur.\n')
            self.mind.callRemote("playSound","sfx/College_DrumCadence11.ogg")
        else:
            self.sendGameText(RPG_MSG_GAME_RED,r'Stay sharp! You\'re no longer safe from the attacks of hostile players.\n')
            self.mind.callRemote("playSound","sfx/College_DrumCadence25.ogg")
    
    
    def flushMessages(self):
        if len(self.textMessages):
            try:
                self.mind.callRemote("receiveTextList",self.textMessages)
            except:
                pass
            self.textTicker = 7
            self.textMessages = []
    
    
    def destroySelf(self):
        for o in self.xpCredits:
            o.destroySelf()
            
        for o in self.characters:
            o.destroySelf()

        for o in self.monsterSpawns:
            o.destroySelf()
        
        for o in self.bankItemsInternal:
            o.destroySelf()
        
        Persistent.destroySelf(self)


