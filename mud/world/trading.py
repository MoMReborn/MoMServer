# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.world.shared.playdata import TradeInfo
from defines import *

# The Trade class handles players trading. To trade, a player must either double click on the other with
#  an item in cursor, or use the '/interact' macro.
class Trade:
    def __init__(self, p0, p1):
        self.traded = False
        p0.trade = p1.trade = self
        
        self.p0 = p0
        self.p0Accepted = False
        
        self.p0Items = {}
        # If the current character of player p0 has items in
        #  trade limbo, restore them now.
        for item in p0.curChar.items:
            if RPG_SLOT_TRADE_BEGIN <= item.slot < RPG_SLOT_TRADE_END:
                self.p0Items[item.slot - RPG_SLOT_TRADE_BEGIN] = item
        self.p0Tin = 0L

        self.p1 = p1
        self.p1Accepted = False
        
        self.p1Items = {}
        # If the current character of player p1 has items in
        #  trade limbo, restore them now.
        for item in p1.curChar.items:
            if RPG_SLOT_TRADE_BEGIN <= item.slot < RPG_SLOT_TRADE_END:
                self.p1Items[item.slot - RPG_SLOT_TRADE_BEGIN] = item
        self.p1Tin = 0L
        
        self.tradeInfo = TradeInfo(self)
        
        p0.mind.callRemote("openTradeWindow",self.tradeInfo)
        p1.mind.callRemote("openTradeWindow",self.tradeInfo)
    
    
    def end(self):
        p0 = self.p0
        p1 = self.p1
        
        if self.traded:
            p0.sendGameText(RPG_MSG_GAME_GAINED,"The trade has been completed.\\n")
            p1.sendGameText(RPG_MSG_GAME_GAINED,"The trade has been completed.\\n")
        else:
            p0.sendGameText(RPG_MSG_GAME_DENIED,"The trade has been canceled.\\n")
            p1.sendGameText(RPG_MSG_GAME_DENIED,"The trade has been canceled.\\n")
        
        p0.trade = p1.trade = None
        if not p0.loggingOut:
            p0.mind.callRemote("closeTradeWindow")
        if not p1.loggingOut:
            p1.mind.callRemote("closeTradeWindow")
        p0.cinfoDirty = True
        p1.cinfoDirty = True
    
    
    def submitMoney(self, player, money):
        if self.p0Accepted or self.p1Accepted:
            if self.p0 == player:
                return self.p0Tin
            else:
                return self.p1Tin
        
        if not player.checkMoney(money):
            #don't have enough
            print "WARNING: trading.py submitMoney Player with insufficient funds!"
            money = 0L
        if self.p0 == player:
            self.p0Tin = money
        else:
            self.p1Tin = money
        
        self.refresh()
        return money
    
    
    def cancel(self):
        #the trade is being canceled, restore items
        self.p0.restoreTradeItems()
        self.p1.restoreTradeItems()
        self.end()
    
    
    def accept(self, player):
        if self.p0 == player:
            self.p0Accepted = True
        if self.p1 == player:
            self.p1Accepted = True
        
        # If both players have accepted trade, check if the trade can occur.
        if self.p0Accepted and self.p1Accepted:
        
            p0Items = self.p0Items.values()
            p1Items = self.p1Items.values()
            p1ItemsCopy = p1Items[:]  # Copy needed for later check due to stacking removing items.

            p0FreeSlots = 0
            p1FreeSlots = 0
            p0CheckStack = {}
            p1CheckStack = {}
            
            for item in p0Items:
            
                # If the item is in a carry slot, then when it is traded the slot becomes free.
                if RPG_SLOT_CARRY_END > item.slot >= RPG_SLOT_CARRY_BEGIN:
                    p0FreeSlots+=1
                    
                # If the item stacks and is not a max stack, check stackability later.
                if item.itemProto.stackMax > item.stackCount > 1:
                    if not p0CheckStack.has_key(item.name):
                        p0CheckStack[item.name] = []
                    p0CheckStack[item.name].append([item,item.stackCount])
                    
            for item in p1Items:
                
                # If the item is in a carry slot, then when it is traded the slot becomes free.
                if RPG_SLOT_CARRY_END > item.slot >= RPG_SLOT_CARRY_BEGIN:
                    p1FreeSlots+=1
                    
                # If the item stacks and is not a max stack, check stackability later.
                if item.itemProto.stackMax > item.stackCount > 1:
                    if not p1CheckStack.has_key(item.name):
                        p1CheckStack[item.name] = []
                    p1CheckStack[item.name].append([item,item.stackCount])
            
            #  Check if player 0 has enough slots for player 1's items after stacking occurs.
            p0UpdatedStacks = {}
            p1Erase = []
            for char in self.p0.party.members:
                freeSlots = range(RPG_SLOT_CARRY_BEGIN,RPG_SLOT_CARRY_END)
                
                # For all items on the character.
                for item in char.items:
                
                    # For player 0's inventory item, get the stack max.
                    stackMax = item.itemProto.stackMax
                    
                    # If player 0's item stacks, is not being traded to Player 1, and Player 1 is trading
                    # an item that stacks, check stacking.
                    if stackMax > 1 and item not in p0Items and item.name in p1CheckStack:
                    
                        # Calculate how many items are needed to complete Player 0's stack.
                        diff = stackMax - item.stackCount
                        
                        # Iterate over items Player 1 is trading that stack with Player 0's item.
                        for stackItem in p1CheckStack[item.name][:]:
                        
                            # If Player 0's item is at max, break out of loop.
                            if diff <= 0:
                                break
                                
                            # If Player 0's item has space for Player 1's item, updating counts.
                            if diff >= stackItem[1]:
                            
                                # Update counts.
                                if item in p0UpdatedStacks:
                                    p0UpdatedStacks[item] += stackItem[1]
                                else:
                                    p0UpdatedStacks[item] = item.stackCount + stackItem[1]
                                    
                                # Update Player 1's count.
                                diff -= stackItem[1]
                                
                                # Player 0's item's stack count will be updated.  Player 1's item 
                                # will stack completely with Player 0's item so it needs to be destroyed
                                # if the trade is completed.
                                p1Items.remove(stackItem[0])
                                p1Erase.append(stackItem[0])
                                p1CheckStack[item.name].remove(stackItem)
                                
                                # Player 0's item still has stack space, but Player 1 is not trading more items
                                # that stack with Player 0's item.
                                if not len(p1CheckStack[item.name]):
                                    del p1CheckStack[item.name]
                                    break
                                    
                            # Player 0's item stack does not have enough space for all of Player 1's stack item,
                            # but it has room for some.
                            else:
                                
                                p0UpdatedStacks[item] = stackMax # Player 0's item will be max.
                                stackItem[1] -= diff # The item being traded may still stack with another item.
                                p0UpdatedStacks[stackItem[0]] = stackItem[1] # The item being traded will need updated.
                                break

                    # Remove item slot from free slots.
                    try:
                        freeSlots.remove(item.slot)
                    except:
                        continue
                        
                # Update free slot count.
                p0FreeSlots += len(freeSlots)
                
            #  Check if player 1  has enough slots for player 0's items after stacking occurs.
            p1UpdatedStacks = {}
            p0Erase = []
            for char in self.p1.party.members:
                freeSlots = range(RPG_SLOT_CARRY_BEGIN,RPG_SLOT_CARRY_END)
                
                # For all items on the character.
                for item in char.items:
                
                    # For player 1's inventory item, get the stack max.
                    stackMax = item.itemProto.stackMax
                    
                    # If player 1's item stacks, is not being traded to Player 0, and Player 0 is trading
                    # an item that stacks, check stacking.
                    if stackMax > 1 and item not in p1ItemsCopy and item.name in p0CheckStack:
                    
                        # Calculate how many items are needed to complete Player 1's stack.
                        diff = stackMax - item.stackCount
                        
                        # Iterate over items Player 0 is trading that stack with Player 1's item.
                        for stackItem in p0CheckStack[item.name][:]:
                        
                            # If Player 1's item is at max, break out of loop.
                            if diff <= 0:
                                break
                                
                            # If Player 1's item has space for Player 0's item, updating counts.    
                            if diff >= stackItem[1]:
                            
                                # Update counts.
                                if item in p1UpdatedStacks:
                                    p1UpdatedStacks[item] += stackItem[1]
                                else:
                                    p1UpdatedStacks[item] = item.stackCount + stackItem[1]
                                    
                                # Update Player 0's count.   
                                diff -= stackItem[1]
                                
                                # Player 1's item's stack count will be updated.  Player 0's item 
                                # will stack completely with Player 1's item so it needs to be destroyed
                                # if the trade is completed.
                                p0Items.remove(stackItem[0])
                                p0Erase.append(stackItem[0])
                                p0CheckStack[item.name].remove(stackItem)
                                
                                # Player 1's item still has stack space, but Player 0 is not trading more items
                                # that stack with Player 1's item.
                                if not len(p0CheckStack[item.name]):
                                    del p0CheckStack[item.name]
                                    break
                                    
                            # Player 1's item stack does not have enough space for all of Player 0's stack item,
                            # but it has room for some.
                            else:

                                p1UpdatedStacks[item] = stackMax # Player 1's item will be max.
                                stackItem[1] -= diff # The item being traded may still stack with another item.
                                p1UpdatedStacks[stackItem[0]] = stackItem[1] # The item being traded will need updated.
                                break
                                
                    # Remove item slot from free slots.
                    try:
                        freeSlots.remove(item.slot)
                    except:
                        continue
                        
                # Update free slot count.
                p1FreeSlots += len(freeSlots)
            
            # Calculate needed slots based on free slots and length of traded items.
            p0Needed = len(p1Items) - p0FreeSlots
            p1Needed = len(p0Items) - p1FreeSlots
            
            # Player 0 needs more free slots.
            if p0Needed > 0:
                self.p0.sendGameText(RPG_MSG_GAME_DENIED,"You need %i more free carry slot to complete this trade.\\n"%p0Needed)
                self.p1.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough free slots to complete this trade.\\n"%self.p0.charName)
            
            # Player 1 needs more free slots.
            if p1Needed > 0:
                self.p1.sendGameText(RPG_MSG_GAME_DENIED,"You need %i more free carry slot to complete this trade.\\n"%p1Needed)
                self.p0.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough free slots to complete this trade.\\n"%self.p1.charName)
            
            # Trade cannot be complete because one of the players needs more free slots.
            if p0Needed > 0 or p1Needed > 0:
                self.p0Accepted = False
                self.p1Accepted = False
                self.refresh({'P0ACCEPTED':False,'P1ACCEPTED':False})
                return
            
            # Trade Player 0's items to Player 1.
            for item in p0Items:
                item.setCharacter(None)
                self.p1.giveItemInstance(item)
            
            # Trade Player 1's items to Player 0.
            for item in p1Items:
                item.setCharacter(None)
                self.p0.giveItemInstance(item)
                
            # Update stack counts for Player 0.
            for item,amount in p0UpdatedStacks.iteritems():
                item.stackCount = amount
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
            
            # Update stack counts for Player 1.
            for item,amount in p1UpdatedStacks.iteritems():
                item.stackCount = amount
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
            
            # Destroy items Player 0 was trading that completely stacked into an existing Player 1 item.
            for item in p0Erase:
                self.p0.takeItem(item)
                
            # Destroy items Player 1 was trading that completely stacked into an existing Player 0 item.
            for item in p1Erase:
                self.p1.takeItem(item)
            
            # Trade money.
            self.p0.takeMoney(self.p0Tin)
            self.p1.takeMoney(self.p1Tin)
            self.p0.giveMoney(self.p1Tin)
            self.p1.giveMoney(self.p0Tin)
            
            self.traded = True
            self.end()
        
        else:
            self.refresh()
    
    
    def refresh(self,dict = None):
        if dict:
            self.tradeInfo.refreshDict(dict)
        else:
            self.tradeInfo.refresh()
        try:
            self.p0.cinfoDirty = True
            self.p1.cinfoDirty = True
        except:
            pass


