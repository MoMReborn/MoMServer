# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from mud.client.playermind import GetMoMClientDBConnection,PyDoCommand
from mud.worlddocs.utils import GetTWikiName
from tomeGui import TomeGui
TomeGui = TomeGui.instance


CRAFTINGWND = None


class CraftingWnd:
    def __init__(self):
        self.window = TGEObject("CRAFTINGWND_WINDOW")
        self.craftingButtons = dict((x,TGEObject("CRAFTING_BUTTON%i"%(x-RPG_SLOT_CRAFTING_BEGIN))) for x in xrange(RPG_SLOT_CRAFTING_BEGIN,RPG_SLOT_CRAFTING_END))
    
    
    def setFromCharacterInfo(self,cinfo):
        from partyWnd import PARTYWND
        
        self.window.setText("%s's Crafting"%cinfo.NAME)
        
        self.charInfo = cinfo
        for slot,butt in self.craftingButtons.iteritems():
            butt.number = -1
            if not cinfo.ITEMS.has_key(slot): #only clear the ones we need to so we don't have to relock texture!
                butt.SetBitmap("")
        
        for slot,ghost in cinfo.ITEMS.iteritems():
            try:
                self.craftingButtons[slot].setBitmap("~/data/ui/items/%s/0_0_0"%ghost.BITMAP)
                if ghost.STACKMAX > 1:
                    self.craftingButtons[slot].number = ghost.STACKCOUNT
            except KeyError:
                pass



def OnCraft():
    cinfo = CRAFTINGWND.charInfo
    charItems = cinfo.ITEMS
    
    # Get all items present in the crafting window.
    citems = [charItems[slot] for slot in xrange(RPG_SLOT_CRAFTING_BEGIN, RPG_SLOT_CRAFTING_END) if charItems.has_key(slot)]
    # If there are no items present in the crafting window, give a message and return.
    if not len(citems):
        TomeGui.receiveGameText(RPG_MSG_GAME_DENIED,"You first need to put the desired ingredients into the crafting window.\\n")
        return
    
    con = GetMoMClientDBConnection()
    
    # Check if the items in crafting window form a valid recipe.
    recipe = None
    for recipe_id,skillname,skill_level in con.execute("SELECT DISTINCT id,skillname,skill_level FROM recipe WHERE id in (SELECT recipe_id FROM recipe_ingredient WHERE item_proto_id=%i);"%citems[0].PROTOID):
        ingredients = dict((item_proto_id,count) for item_proto_id,count in con.execute("SELECT item_proto_id,count FROM recipe_ingredient WHERE recipe_id=%i AND count!=0"%recipe_id).fetchall())
        
        passed = True
        for item in citems:
            found = False
            for item_proto_id,count in ingredients.iteritems():
                if item.PROTOID == item_proto_id:
                    sc = item.STACKCOUNT
                    if not sc:
                        sc = 1
                    ingredients[item_proto_id] -= sc
                    found = True
                    break
            if not found:
                passed = False
                break
        # All items were found in the current recipe.
        else:
            for x in ingredients.itervalues():
                if x:  # Can be negative if too much
                    passed = False
                    break
            # All ingredients no longer have a required count assigned.
            else:
                recipe = recipe_id
                # Check skill requirements
                charSkillLevel = cinfo.SKILLS.get(skillname,0)
                if charSkillLevel < skill_level:
                    TomeGui.receiveGameText(RPG_MSG_GAME_DENIED,"%s requires a %i skill in <a:Skill%s>%s</a>.\\n"%(cinfo.NAME,skill_level,GetTWikiName(skillname),skillname))
                    return
                # Check for crafting delays
                if skillname.upper() in cinfo.SKILLREUSE:
                    TomeGui.receiveGameTextPersonalized(RPG_MSG_GAME_DENIED,"$src is still cleaning $srchis tools,\\n$srche can use the <a:Skill%s>%s</a> skill again in about %i seconds.\\n"%(GetTWikiName(skillname),skillname,cinfo.SKILLREUSE[skillname.upper()]),cinfo)
                    return
                break
    
    if not recipe and cinfo.SKILLS.get("Scribing",0):
        if "SCRIBING" in cinfo.SKILLREUSE:
            TomeGui.receiveGameTextPersonalized(RPG_MSG_GAME_DENIED,"$src is still cleaning $srchis tools,\\n$srche can use the <a:SkillScribing>Scribing</a> skill again in about %i seconds.\\n"%(cinfo.SKILLREUSE["SCRIBING"]),cinfo)
            return
        
        spellEnhanceLevel = citems[0].spellEnhanceLevel
        name = citems[0].NAME
        passed = True
        if spellEnhanceLevel > 0 and spellEnhanceLevel < 10:
            count = 0
            for item in citems:
                if spellEnhanceLevel != item.spellEnhanceLevel or name != item.NAME:
                    passed = False
                    break
                count += item.STACKCOUNT
            # Player has the correct amount of tomes in crafting window for a merge
            if count == 2 and passed:
                recipe = -1  # Hack for tome merging
    
    if not recipe:
        TomeGui.receiveGameText(RPG_MSG_GAME_DENIED,r'%s is unable to craft anything with these items.\n'%(cinfo.NAME))
    else:
        # Send craft command.
        from partyWnd import PARTYWND
        PARTYWND.mind.perspective.callRemote("PlayerAvatar","onCraft",PARTYWND.curIndex,recipe,True)


def OnCraftingToggle():
    if int(CRAFTINGWND.window.isAwake()):
        TGEEval("Canvas.popDialog(CraftingWnd);")
    else:
        TGEEval("Canvas.pushDialog(CraftingWnd);")


def OnCraftEmpty():
    PyDoCommand(("PyDoCommand","/empty"))



def PyExec():
    global CRAFTINGWND
    CRAFTINGWND = CraftingWnd()
    
    TGEExport(OnCraftingToggle,"Py","OnCraftingToggle","desc",1,1)
    
    TGEExport(OnCraft,"Py","OnCraft","desc",1,1)
    TGEExport(OnCraftEmpty,"Py","OnCraftEmpty","desc",1,1)
