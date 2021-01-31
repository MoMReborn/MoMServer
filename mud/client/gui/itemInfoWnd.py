# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#this is used for spells, items, etc

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from mud.gamesettings import *
from time import time
import os
from lootWnd import LootWnd
LootWnd = LootWnd.instance


#ItemInfoWnd_InfoText
#ItemInfoWnd_NameText
#ItemInfoWnd_FlagsText
#ITEMINFOWND_BITMAP

TEXT_BIG_HEADER = """<font:Arial Bold:16><just:center><shadow:1:1><shadowcolor:000000>"""
TEXT_HEADER = """<font:Arial Bold:14><just:center><shadow:1:1><shadowcolor:000000>"""


ITEMINFOWND = None

SLOTNAMES = {
RPG_SLOT_HEAD:"Head",
RPG_SLOT_LEAR:"LEar",
RPG_SLOT_REAR:"REar",
RPG_SLOT_NECK:"Neck",
RPG_SLOT_SHOULDERS:"Shoulders",
RPG_SLOT_BACK:"Back",
RPG_SLOT_CHEST:"Chest", 
RPG_SLOT_ARMS:"Arms",
RPG_SLOT_HANDS:"Hands",
RPG_SLOT_LFINGER:"LFinger",
RPG_SLOT_RFINGER:"RFinger",
RPG_SLOT_PRIMARY:"Primary",
RPG_SLOT_SECONDARY:"Secondary",
RPG_SLOT_RANGED:"Ranged",
RPG_SLOT_AMMO:"Ammo",
RPG_SLOT_WAIST:"Waist", 
RPG_SLOT_LEGS:"Legs",
RPG_SLOT_FEET:"Feet",
RPG_SLOT_LWRIST:"LWrist",
RPG_SLOT_RWRIST:"RWrist",
RPG_SLOT_SHIELD:"Shield",
RPG_SLOT_LIGHT:"Light"
}

NICESLOTNAMES = {
RPG_SLOT_HEAD:"Head",
RPG_SLOT_LEAR:"Left Ear",
RPG_SLOT_REAR:"Right Ear",
RPG_SLOT_NECK:"Neck",
RPG_SLOT_SHOULDERS:"Shoulders",
RPG_SLOT_BACK:"Back",
RPG_SLOT_CHEST:"Chest", 
RPG_SLOT_ARMS:"Arms",
RPG_SLOT_HANDS:"Hands",
RPG_SLOT_LFINGER:"Left Finger",
RPG_SLOT_RFINGER:"Right Finger",
RPG_SLOT_PRIMARY:"Primary",
RPG_SLOT_SECONDARY:"Offhand",
RPG_SLOT_RANGED:"Ranged",
RPG_SLOT_AMMO:"Ammo",
RPG_SLOT_WAIST:"Waist", 
RPG_SLOT_LEGS:"Legs",
RPG_SLOT_FEET:"Feet",
RPG_SLOT_LWRIST:"Left Wrist",
RPG_SLOT_RWRIST:"Right Wrist",
RPG_SLOT_SHIELD:"Shield",
RPG_SLOT_LIGHT:"Light"

}


class ItemInfoWnd:
    def __init__(self):
        self.bitmap = TGEObject("ITEMINFOWND_BITMAP")
        self.lastBitmap = ""
        self.bitmapIteration = 0
        self.bitmapTimer = 0
        self.ctrl = TGEObject("ITEMINFOWND")
        
        self.invButtons = dict((slot,TGEObject("SLOT_"+name)) for slot,name in SLOTNAMES.iteritems())
        #carry slots
        for i in xrange(0,30):
            self.invButtons[i+RPG_SLOT_CARRY_BEGIN] = TGEObject("SLOT_CARRY%i"%i)
        for i in xrange(30,60):
            self.invButtons[i+RPG_SLOT_CARRY_BEGIN] = TGEObject("SLOT_CARRY%i"%(i-30))
        
        #trade buttons
        self.tradeButtons = {}
        for x in xrange(0,12):
            self.tradeButtons[x]    = TGEObject("TRADE_P0_BUTTON%i"%x)
            self.tradeButtons[x+12] = TGEObject("TRADE_P1_BUTTON%i"%x)
        
        #spell slots
        self.spellButtons = dict((i,TGEObject("SPELLPANE_SPELL%i"%i)) for i in xrange(0,25))
        
        #on partywnd spellpane
        self.spellText = TGEObject("SPELLPANE_SPELLTEXT")
        self.spellPic = TGEObject("SPELLPANE_SPELLPIC")
        
        self.ghost = -1 #-1 so we catch update ghost != self.ghost where ghost is None
        self.isItem = False
        self.setItem(None)
    
    
    def tick(self,cinfo):
        from partyWnd import PARTYWND
        from tradeWnd import TRADEWND
        from mud.client.playermind import PLAYERMIND

        #check inventory
        found = False
        ghost = None
        isSpell = False
        isLoot = False
        isCraft = False
        isBank = False
        invSlot = -1
        page = PARTYWND.invPane.page
        
        for slot,button in self.invButtons.iteritems():
            if page == 0 and (RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN+30):
                continue
            if page == 1 and (RPG_SLOT_CARRY_BEGIN+30 > slot >= RPG_SLOT_CARRY_BEGIN):
                continue
            
            if int(button.mouseOver):
                found = True
                invSlot = slot
                if cinfo.ITEMS.has_key(slot):
                    ghost = cinfo.ITEMS[slot]
                    break
        
        #check trade buttons
        if not found and TRADEWND.tradeInfo:
            if PLAYERMIND.rootInfo.PLAYERNAME == TRADEWND.tradeInfo.P0NAME:
                p0Items = TRADEWND.tradeInfo.P0ITEMS
                p1Items = TRADEWND.tradeInfo.P1ITEMS
            else:
                p1Items = TRADEWND.tradeInfo.P0ITEMS
                p0Items = TRADEWND.tradeInfo.P1ITEMS
            
            for slot,button in self.tradeButtons.iteritems():
                if int(button.mouseOver):
                    found = True
                    cslot = slot
                    if cslot > 11:
                        #player 2
                        if p1Items.has_key(slot-12):
                            ghost = p1Items[slot-12]
                    else:
                        #player 1
                       if p0Items.has_key(slot):
                            ghost = p0Items[slot]
                    break
        
        if not found:
            found,itemGhost = LootWnd.getMouseOver()
            if itemGhost:
                ghost = itemGhost
                isLoot = True
        
        if not found:
            lootwnd = TGEObject("PetWnd")
            if int(lootwnd.isAwake()):
                from petWnd import PETWND
                for slot,button in PETWND.invButtons.iteritems():
                    if int(button.mouseOver):
                        found = True
                        if cinfo.ITEMS.has_key(slot):
                            ghost = cinfo.ITEMS[slot]
                            break
        
        if not found:
            craftwnd = TGEObject("CraftingWnd")
            if int(craftwnd.isAwake()):
                from craftingWnd import CRAFTINGWND
                for slot,button in CRAFTINGWND.craftingButtons.iteritems():
                    if int(button.mouseOver):
                        found = True
                        if cinfo.ITEMS.has_key(slot):
                            ghost = cinfo.ITEMS[slot]
                            isCraft = True
                            break
        
        if not found:
            npcwnd = TGEObject("NPCWND")
            if int(npcwnd.isAwake()):
                from npcWnd import NPCWND
                for slot,button in NPCWND.bankPane.bankButtons.iteritems():
                    if int(button.mouseOver):
                        found = True
                        bank = NPCWND.bankPane.bank
                        if bank.has_key(slot):
                            ghost = bank[slot]
                            isBank = True
                            break
        
        if not found:
            #not an inventory item, check spells
            sindex = PARTYWND.spellPane.currentPage*25
            for slot,button in self.spellButtons.iteritems():
                if int(button.mouseOver):
                    if cinfo.SPELLS.has_key(slot+sindex):
                        found = True
                        ghost = cinfo.SPELLS[slot+sindex]
                        isSpell = True
                        break
                    else:
                        break
        
        if ghost:
            if isSpell:
                self.setSpell(ghost)
            else:
                self.setItem(ghost,isLoot,isCraft,isBank)
        else:
            self.setItem(PARTYWND.mind.cursorItem)
        
        money = TGEObject("INVMONEY_PANE")
        money.visible = False
        
        if not self.ghost:
            if invSlot != -1:
                if NICESLOTNAMES.has_key(invSlot):
                    TGEObject("PartyWnd_INVITEMNAME").setText(TEXT_HEADER+NICESLOTNAMES[invSlot])
                else:
                    TGEObject("PartyWnd_INVITEMNAME").setText("")
                    money.visible = True
            else:
                TGEObject("PartyWnd_INVITEMNAME").setText("")
                money.visible = True
            self.bitmap.SetBitmap("")
            self.lastBitmap = ""
        else:
            if self.isItem or self.isLoot or self.isCraft:
                if self.lastBitmap != self.ghost.BITMAP:
                    self.bitmap.SetBitmap("~/data/ui/items/%s/0_0_0"%self.ghost.BITMAP)
                    self.lastBitmap = self.ghost.BITMAP
                    self.bitmapIteration = 0
                    self.bitmapTimer = time()
                elif time() - self.bitmapTimer > 0.2:
                    self.bitmapIteration += 1
                    if not os.path.exists("./%s/data/ui/items/%s/0_0_%i.png"%(GAMEROOT,self.ghost.BITMAP,self.bitmapIteration)):
                        self.bitmapIteration = 0
                    self.bitmap.SetBitmap("~/data/ui/items/%s/0_0_%i"%(self.ghost.BITMAP,self.bitmapIteration))
                    self.bitmapTimer = time()
    
    
    def setSpell(self,ghost):
        if self.ghost == ghost:
            return
        
        self.isItem = False
        self.isLoot = False
        self.isCraft = False
        self.ghost = ghost
        sinfo = ghost.SPELLINFO
        self.spellText.setText(TEXT_HEADER+sinfo.NAME)
        

        icon = sinfo.SPELLBOOKPIC
        if icon.startswith("SPELLICON_"):
            split = icon.split("_")
            index=int(split[2])
            u0=(float(index%6)*40.0)/256.0
            v0=(float(index/6)*40.0)/256.0
            u1=(40.0/256.0)
            v1=(40.0/256.0)
            
            self.spellPic.SetBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
            self.bitmap.SetBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
            self.lastBitmap = ""
        else:
            self.spellPic.SetBitmap("~/data/ui/spellicons/%s"%icon)
            self.bitmap.SetBitmap("~/data/ui/spellicons/%s"%icon)
            self.lastBitmap = ""
        
        eval = r'ItemInfoWnd_NameText.setText("%s");'%(TEXT_BIG_HEADER+sinfo.NAME)
        TGEEval(eval)
        eval = 'ItemInfoWnd_FlagsText.setText("");'
        TGEEval(eval)
        eval = 'ItemInfoWnd_InfoText.setText("%s");'%(TEXT_HEADER+sinfo.text)
        TGEEval(eval)
        
            
        
    def setItem(self,ghost,isLoot=False,isCraft=False,isBank=False):
        if not (ghost and ghost.infoDirty) and self.ghost == ghost and isCraft == self.isCraft:
            return
        
        self.isLoot = isLoot
        self.isCraft = isCraft
        self.isItem = False
        
        self.ghost = ghost
        
        if ghost:
            ghost.infoDirty = False
            if not isLoot and not isCraft:
                self.isItem = True
            
            # flags
            text = ' '.join(r'\cp\c2%s\co'%ftext for f,ftext in RPG_ITEM_FLAG_TEXT.iteritems() if ghost.FLAGS&f)
            eval = 'ItemInfoWnd_FlagsText.setText("%s%s");'%(TEXT_HEADER,text)
            TGEEval(eval)

            eval = 'ItemInfoWnd_NameText.setText("%s%s");'%(TEXT_BIG_HEADER,ghost.NAME)
            TGEEval(eval)
            
            eval = 'ItemInfoWnd_InfoText.setText("%s%s");'%(TEXT_HEADER,ghost.text)
            TGEEval(eval)
            
            currentBitmap = "~/data/ui/items/%s/0_0_0"%ghost.BITMAP
            
            if not isLoot and not isCraft and not isBank:
                TGEObject("PartyWnd_InvItemBitmap").SetBitmap(currentBitmap)
                eval = 'PartyWnd_INVITEMNAME.setText("%s%s");'%(TEXT_HEADER,ghost.NAME)
                TGEEval(eval)
                
                TGEObject("PetWnd_InvItemBitmap").SetBitmap(currentBitmap)
                eval = 'PetWnd_INVITEMNAME.setText("%s%s");'%(TEXT_HEADER,ghost.NAME)
                TGEEval(eval)

            elif isLoot:
                TGEObject("LOOT_ITEMPIC").SetBitmap(currentBitmap)
                eval = 'LOOT_ITEMTEXT.setText("%s%s");'%(TEXT_HEADER,ghost.NAME)
                TGEEval(eval)
            elif isCraft:
                TGEObject("CRAFTING_ITEMPIC").SetBitmap(currentBitmap)
                eval = 'CRAFTING_ITEMTEXT.setText("%s%s");'%(TEXT_HEADER,ghost.NAME)
                TGEEval(eval)
            elif isBank:
                TGEObject("NPCWnd_InvItemBitmap").SetBitmap(currentBitmap)
                eval = 'NPCWnd_INVITEMNAME.setText("%s%s");'%(TEXT_HEADER,ghost.NAME)
                TGEEval(eval)
            
                

        else:
            eval = 'ItemInfoWnd_NameText.setText("");'
            TGEEval(eval)
            eval = 'ItemInfoWnd_FlagsText.setText("");'
            TGEEval(eval)
            eval = 'ItemInfoWnd_InfoText.setText("");'
            TGEEval(eval)
            self.bitmap.SetBitmap("")
            self.lastBitmap = ""
            TGEObject("PartyWnd_InvItemBitmap").SetBitmap("")
            eval = 'PartyWnd_INVITEMNAME.setText("");'
            TGEEval(eval)
            
            TGEObject("PetWnd_InvItemBitmap").SetBitmap("")
            eval = 'PetWnd_INVITEMNAME.setText("");'
            TGEEval(eval)


            TGEObject("LOOT_ITEMPIC").SetBitmap("")
            eval = 'LOOT_ITEMTEXT.setText("");'
            TGEEval(eval)

            TGEObject("CRAFTING_ITEMPIC").SetBitmap("")
            eval = 'CRAFTING_ITEMTEXT.setText("");'
            
            TGEEval(eval)
            TGEObject("NPCWnd_InvItemBitmap").SetBitmap("")
            eval = 'NPCWnd_INVITEMNAME.setText("");'
            TGEEval(eval)

            
            self.spellText.setText("")
            self.spellPic.SetBitmap("")



def PyExec():
    global ITEMINFOWND
    ITEMINFOWND = ItemInfoWnd()
    
    