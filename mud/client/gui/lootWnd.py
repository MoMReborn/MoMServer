# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *



ALLIANCEWND_REF = None



class LootWnd(object):
    instance = None
    
    
    def __new__(cl, *p, **k):
        if not LootWnd.instance:
            LootWnd.instance = object.__new__(cl, *p, **k)
        return LootWnd.instance
    
    
    def __init__(self):
        self.loot = {}
        self.assess = False
    
    
    @staticmethod
    def getInstance(self):
        return LootWnd.instance
    
    
    def initTGEObjects(self):
        self.window = TGEObject("LootWnd")
        self.pane = TGEObject("LOOTWnd_Window")
        self.lootButtons = dict((x,TGEObject("LOOT_BUTTON%i"%x)) for x in xrange(16))
        self.coffin = TGEObject("LOOT_COFFIN")
        self.destroyCorpseButton = TGEObject("LOOT_DESTROYCORPSE")
    
    
    def close(self, renew=False):
        # Clean up item infos still referenced, this should
        #  prevent some more twisted exceptions on exit.
        self.loot.clear()
        
        if not renew:
            from partyWnd import PARTYWND
            PARTYWND.mind.perspective.callRemote("PlayerAvatar","endLooting")
        TGEEval("canvas.popDialog(LootWnd);")
    
    
    # Return a tuple (found,itemGhost), found being true
    #  if the mouse was indeed over a loot button and itemGhost
    #  being the item ghost of the item the mouse is hovering
    #  over or None.
    def getMouseOver(self):
        if int(self.window.isAwake()):
            for slot,button in self.lootButtons.iteritems():
                if int(button.mouseOver):
                    return (True,self.loot.get(slot,None))
        return(False,None)
    
    
    def setLoot(self, loot, assess=False):
        self.loot = loot
        self.assess = assess
        
        if not len(loot):
            if int(self.window.isAwake()):
                self.close(True)
            return
        
        if assess:
            self.coffin.visible = False
            self.pane.setText("Assess")
            self.destroyCorpseButton.setText("Close")
        else:
            self.coffin.visible = True
            self.pane.setText("Loot")
            self.destroyCorpseButton.setText("Destroy Corpse")
        
        for button in self.lootButtons.itervalues():
            button.visible = False
            button.number = -1
            button.setValue(int(assess))
            button.toggleLocked = assess
        
        for x,ghost in loot.iteritems():
            # Need to check if loot item slot is still in slot range.
            # This can be false when a mob has an extensive standard
            #  loot table (especially true on testing).
            if x > 15:
                continue
            button = self.lootButtons[x]
            button.setBitmap("~/data/ui/items/%s/0_0_0"%ghost.BITMAP)
            button.visible = True
            if ghost.STACKMAX > 1:
                button.number = ghost.STACKCOUNT
        
        if not int(self.window.isAwake()):
            TGEEval("canvas.pushDialog(LootWnd);")
    
    
    def onLoot(self, args):
        from partyWnd import PARTYWND
        
        global ALLIANCEWND_REF
        if not ALLIANCEWND_REF:
            from allianceWnd import ALLIANCEWND
            ALLIANCEWND_REF = ALLIANCEWND
        
        # Just in case current character changes we want
        #  to make choice reflect dialog no matter what.
        curIndex = PARTYWND.curIndex
        cinfo = PARTYWND.charInfos[curIndex]
        name = cinfo.NAME
        
        slot = int(args[1])
        try:
            itemGhost = self.loot[slot]
            
            # If the player is in an alliance and the item being looted
            #  is soulbound, get confirmation.
            if itemGhost.FLAGS&RPG_ITEM_SOULBOUND and ALLIANCEWND_REF.allianceInfo and 1 < len(ALLIANCEWND_REF.allianceInfo.PNAMES):
                TGEEval('MessageBoxYesNo("Loot Item?", "Do you really want %s to loot this SOULBOUND item?","Py::OnReallyLootButton(%i,%i);");'%(name,curIndex,slot))
            else:
                PARTYWND.mind.perspective.callRemote("PlayerAvatar","loot",curIndex,slot)
        except KeyError:
            return
    
    
    def onReallyLoot(self, args):
        from partyWnd import PARTYWND
        charIndex = int(args[1])
        slot = int(args[2])
        
        PARTYWND.mind.perspective.callRemote("PlayerAvatar","loot",charIndex,slot)
    
    
    def onLootAlt(self, args):
        from partyWnd import PARTYWND
        
        global ALLIANCEWND_REF
        if not ALLIANCEWND_REF:
            from allianceWnd import ALLIANCEWND
            ALLIANCEWND_REF = ALLIANCEWND
        
        # Just in case current character changes we want
        #  to make choice reflect dialog no matter what.
        curIndex = PARTYWND.curIndex
        cinfo = PARTYWND.charInfos[curIndex]
        name = cinfo.NAME
        
        slot = int(args[1])
        try:
            itemGhost = self.loot[slot]
            
            # If the player is in an alliance and the item being looted
            #  is soulbound, get confirmation.
            if itemGhost.FLAGS&RPG_ITEM_SOULBOUND and ALLIANCEWND_REF.allianceInfo and 1 < len(ALLIANCEWND_REF.allianceInfo.PNAMES):
                TGEEval('MessageBoxYesNo("Loot Item?", "Do you really want %s to loot this SOULBOUND item?","Py::OnReallyLootButtonAlt(%i,%i);");'%(name,curIndex,slot))
            else:
                PARTYWND.mind.perspective.callRemote("PlayerAvatar","loot",curIndex,slot,True)
        except KeyError:
            return
    
    
    def onReallyLootAlt(self, args):
        from partyWnd import PARTYWND
        charIndex = int(args[1])
        slot = int(args[2])
        
        PARTYWND.mind.perspective.callRemote("PlayerAvatar","loot",charIndex,slot,True)
    
    
    def destroyCorpse(self, args):
        if self.assess or int(args[1]):
            self.reallyDestroyCorpse()
            return
        
        TGEEval('MessageBoxYesNo("Destroy Corpse?", "Do you really want destroy this corpse?","Py::OnReallyDestroyCorpse();");')
    
    
    def reallyDestroyCorpse(self):
        # Clean up item infos still referenced, this should
        #  prevent some more twisted exceptions on exit.
        self.loot.clear()
        
        if self.assess:
            if int(self.window.isAwake()):
                self.close(True)
            return
        
        from partyWnd import PARTYWND
        PARTYWND.mind.perspective.callRemote("PlayerAvatar","destroyCorpse")



LootWnd()



def PyExec():
    LOOTWND = LootWnd.instance
    LOOTWND.initTGEObjects()
    
    TGEExport(LOOTWND.close,"Py","OnCloseLootWnd","desc",1,1)
    
    TGEExport(LOOTWND.onLoot,"Py","OnLootButton","desc",2,2)
    TGEExport(LOOTWND.onReallyLoot,"Py","OnReallyLootButton","desc",3,3)
    
    TGEExport(LOOTWND.onLootAlt,"Py","OnLootButtonAlt","desc",2,2)
    TGEExport(LOOTWND.onReallyLootAlt,"Py","OnReallyLootButtonAlt","desc",3,3)
    
    TGEExport(LOOTWND.destroyCorpse,"Py","OnDestroyCorpse","desc",2,2)
    TGEExport(LOOTWND.reallyDestroyCorpse,"Py","OnReallyDestroyCorpse","desc",1,1)
