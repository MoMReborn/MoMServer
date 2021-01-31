# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from sqlobject import *
from mud.common.persistent import Persistent
from twisted.internet import reactor

from item import ItemProto,ItemInstance
from defines import *
from random import randint
import spawn
import math
from core import *
import traceback



class VendorItem(Persistent):
    # Link to the real item.
    itemProto = ForeignKey('ItemProto')
    # Chance for the vendor to have this specific item in
    #  stock.
    frequency = IntCol(default=RPG_FREQ_ALWAYS)
    # Amount of items of this kind the vendor has in stock,
    #  -1 signifies an infinite amount.
    count = IntCol(default=-1)
    # Vendors that sell this item.
    vendorProtos = RelatedJoin('VendorProto')



class VendorProto(Persistent):
    # Name of the vendor. Must be unique.
    name = StringCol(alternateID=True)
    # Factor that modifies selling / buying ratio.
    # Number > 1.0 means vendor charges more for sales
    #  and gives less on buys.
    markup = FloatCol(default=1.0)
    # How fast the vendor restocks in realtime minutes.
    # Might be nice if this was per item, but hey...
    # Restock timer only ticks if no one is interacting
    #  to prevent stock changes during interaction.
    restockRate = IntCol(default=10)
    # Items the vendor will restock.
    vendorItems = RelatedJoin('VendorItem')
    
    # Spawns representing this vendor.
    spawns = MultipleJoin('Spawn')
    
    
    def createVendorInstance(self, mob):
        mob.vendor = VendorInstance(self,mob)



# !!! Restock timer only ticks if no one is interacting
class VendorInstance:
    def __init__(self, vendorProto, mob):
        self.mob = mob
        self.vendorProto = vendorProto
        self.markup = vendorProto.markup
        self.restockRate = vendorProto.restockRate * durMinute
        # We do this to ensure that this is always ordered the same.
        # I am not entirely sure that the related join ensures this.
        self.selection = vendorProto.vendorItems[:]
        # Items currently in stock, can be different from full stock.
        self.stock = {}
        
        # Items players sold to this vendor and that this vendor
        #  offers for resell.
        self.playerSubmitted = []
        self.regenerateStock()
    
    
    def destroyStock(self):
        self.stock.clear()
        
        map(ItemInstance.destroySelf,self.playerSubmitted)
        self.playerSubmitted = []
    
    
    def regenerateStock(self):
        if self.mob.detached:
            return
        
        if not self.mob.interacting:
            self.stock.clear()
            for vitem in self.selection:
                count = vitem.count
                if vitem.frequency != RPG_FREQ_ALWAYS:
                    if count > 0:
                        count = 0
                        for x in xrange(vitem.count):
                            if not randint(0,vitem.frequency - 1):
                                count += 1
                    elif count == -1:  # infinite amount
                        if randint(0,vitem.frequency - 1):
                            count = 0
                if count != 0:
                    myItem = vitem.itemProto.createInstance(False,True)
                    self.stock[myItem] = count
        
        reactor.callLater(self.restockRate,self.regenerateStock)
    
    
    def sendStock(self, player):
        # indexes 20 and above are reserved for vendor default items
        itemInfos = dict((item.itemInfo,i+20) for i,item in enumerate(self.stock.iterkeys()))
        
        if len(self.playerSubmitted) > 20:
            remove = self.playerSubmitted[0:len(self.playerSubmitted) - 20]
            for x in remove:
                self.playerSubmitted.remove(x)
                x.destroySelf()
        
        for i,p in enumerate(self.playerSubmitted):
            itemInfos[p.itemInfo] = i
        
        player.mind.callRemote("setVendorStock",True,itemInfos,self.markup)
    
    
    def getItem(self, lookitem):
        if lookitem < 20:
            if 0 <= lookitem < len(self.playerSubmitted):  # valid index
                return self.playerSubmitted[lookitem]
        elif lookitem - 20 < len(self.stock):  # valid index
            return self.stock.keys()[lookitem - 20]
        
        return None
    
    
    def removeItem(self, item):
        if item in self.playerSubmitted:
            self.playerSubmitted.remove(item)
            return True
        
        if item in self.stock:
            if self.stock[item] != -1:
                self.stock[item] -= 1
                if self.stock[item] == 0:
                    del self.stock[item]
                return True
        
        return False
    
    
    def sellItem(self, player, char, itemIndex):
        # validate and get the item by index
        buyitem = self.getItem(itemIndex)
        if not buyitem:
            print "Warning: Player buying item vendor doesn't have!!!!"
            return
        
        money = buyitem.getWorth(self.markup)
        
        #first check $$$
        if not player.checkMoney(money):
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot afford this.\\n"%char.name)
            return
        
        if player.cursorItem:
            player.sendGameText(RPG_MSG_GAME_DENIED,"Please empty your cursor first.\\n")
            return
        
        myitem = buyitem
        
        # Check for stackability.
        stackMax = buyitem.itemProto.stackMax
        needStack = 0
        if stackMax > 1:
            needStack = buyitem.stackCount
            for item in char.items:
                amt = stackMax - item.stackCount
                if item.name == buyitem.name and amt > 0:
                    needStack -= amt
                    if needStack <= 0:
                        needStack = 0
                        myitem = None
                        break
            
            doStack = buyitem.stackCount - needStack
            # New item can be stacked.
            if doStack > 0:
                for item in char.items:
                    amt = stackMax - item.stackCount
                    if item.name == buyitem.name and amt > 0:
                        add = min(doStack,amt)
                        item.stackCount += add
                        item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
                        doStack -= add
                        if not doStack:
                            break
            
            if myitem != None and needStack > 0:
                if buyitem not in self.playerSubmitted:
                    myitem = buyitem.itemProto.createInstance()
                # Update stack count to remaining count.
                myitem.stackCount = needStack
        elif buyitem not in self.playerSubmitted:
            myitem = buyitem.itemProto.createInstance()
        
        if myitem and not player.giveItemInstance(myitem):
            if myitem != buyitem:
                myitem.destroySelf() #optimize should check earlier than making item!
            if needStack == 0:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s's inventory is full.\\n"%char.name)
                return
            else:
                diff = buyitem.stackCount - needStack
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s's inventory is full, only %i items could be bought.\\n"%(char.name,diff))
                money = long(math.ceil(float(money) * float(diff) / float(buyitem.stackCount)))
        
        if not money:
            player.sendGameText(RPG_MSG_GAME_GAINED,"%s receives the item for free.\\n"%char.name)
        else:
            wtext = GenMoneyText(money)
            player.sendGameText(RPG_MSG_GAME_LOST,"%s pays %s for the item.\\n"%(char.name,wtext))
            player.takeMoney(money)
        
        refresh = False
        if not myitem and buyitem in self.playerSubmitted:  # was stacked
            refresh = self.removeItem(buyitem)
            buyitem.destroySelf()
        else:
            refresh = self.removeItem(buyitem)
        if refresh:
            self.sendStock(player)
    
    
    def buyItem(self, player, item):
        proto = item.itemProto
        if item.flags&(RPG_ITEM_SOULBOUND|RPG_ITEM_ETHEREAL|RPG_ITEM_WORLDUNIQUE) or not proto.worthTin:
            player.sendGameText(RPG_MSG_GAME_DENIED,"That item cannot be sold.\\n")
            return
        
        for c in player.party.members:
            if c == item.character:
                item.setCharacter(None)
                item.slot = -1
                if item == player.cursorItem:
                    player.cursorItem = None
                    player.updateCursorItem(item)
                
                money = item.getWorth(self.markup * 0.1,True)
                player.giveMoney(money)
                
                if not money:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"%s receives nothing for the item.\\n"%c.name)
                else:
                    wtext = GenMoneyText(money)
                    player.sendGameText(RPG_MSG_GAME_GAINED,"%s receives %s for the item.\\n"%(c.name,wtext))
                
                # Vendors are not responsible for persistent management of Items
                # in their stock, so just destroy the persistent part of the
                # Item.
                item.destroySelf()
                
                # If the Item the vendor bought is not crafted, not enchanted,
                # and not stackable, then store the ItemInstance.
                if not item.crafted and item.spellEnhanceLevel != 9999 and proto.stackMax <= 1:
                    item.repair = item.repairMax
                    item.itemInfo.refreshDict({'REPAIR':item.repair})
                    self.playerSubmitted.append(item)
                    self.sendStock(player)
                
                return
        
        print "Warning: Player item selling wackiness!!!"


