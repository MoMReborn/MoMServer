# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *

PETWND = None

SLOTNAMES = {
RPG_SLOT_PET_HEAD:"Head",
RPG_SLOT_PET_LEAR:"LEar",
RPG_SLOT_PET_REAR:"REar",
RPG_SLOT_PET_NECK:"Neck",
RPG_SLOT_PET_SHOULDERS:"Shoulders",
RPG_SLOT_PET_BACK:"Back",
RPG_SLOT_PET_CHEST:"Chest", 
RPG_SLOT_PET_ARMS:"Arms",
RPG_SLOT_PET_HANDS:"Hands",
RPG_SLOT_PET_LFINGER:"LFinger",
RPG_SLOT_PET_RFINGER:"RFinger",
RPG_SLOT_PET_PRIMARY:"Primary",
RPG_SLOT_PET_SECONDARY:"Secondary",
RPG_SLOT_PET_RANGED:"Ranged",
RPG_SLOT_PET_AMMO:"Ammo",
RPG_SLOT_PET_WAIST:"Waist", 
RPG_SLOT_PET_LEGS:"Legs",
RPG_SLOT_PET_FEET:"Feet",
RPG_SLOT_PET_LWRIST:"LWrist",
RPG_SLOT_PET_RWRIST:"RWrist",
RPG_SLOT_PET_SHIELD:"Shield",
RPG_SLOT_PET_LIGHT:"Light"
}
 
 
class PetWnd:
    def __init__(self):
        
        self.playerMind = None
        self.invButtons = {}
        for slot,name in SLOTNAMES.iteritems():
            self.invButtons[slot]=TGEObject("PET_SLOT_"+name)
        
            
    def onInvSlot(self,slot):
        self.playerMind.onInvSlot(self.charInfo,slot)

    def onInvSlotAlt(self,slot):
        self.playerMind.onInvSlotAlt(self.charInfo,slot)

            
    def setFromCharacterInfo(self,cinfo):
        from mud.client.playermind import PLAYERMIND
        
        petwnd = TGEObject("PetWnd_Window")
        petwnd.setText(cinfo.NAME+"'s Pet")
        

        self.playerMind = PLAYERMIND
        cursorItem = PLAYERMIND.cursorItem
        rootInfo = PLAYERMIND.rootInfo
        
        self.charInfo = cinfo
        for slot,butt in self.invButtons.iteritems():
            butt.pulseRed = False
            butt.pulseGreen = False
            if cursorItem and (slot-RPG_SLOT_PET_BEGIN) in cursorItem.SLOTS:
                butt.pulseGreen = True

            if not cinfo.ITEMS.has_key(slot): #only clear the ones we need to so we don't have to relock texture!
                butt.SetBitmap("")

        for slot,ghost in cinfo.ITEMS.iteritems():
            if self.invButtons.has_key(slot):
                self.invButtons[slot].setBitmap("~/data/ui/items/"+ghost.BITMAP+"/0_0_0")
                
                
def PyExec():
    global PETWND
    PETWND = PetWnd()

