# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from math import floor
from mud.world.defines import *
from mud.gamesettings import *
from mud.world.repair import CheckRepairItem,CheckRepairAll,CheckRepairParty

from mud.client.playermind import PyDoCommand
from skillinfo import GetSkillInfo
from tomeGui import TomeGui
TomeGui = TomeGui.instance

from mud.world.shared.playdata import AreSkillsDirty
from time import time as systemTime

from mud.worlddocs.utils import GetTWikiName



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



def SetColoredText(controlName, text):
        # We are using colors so TGE has to compile the command, blarg
        # Example: modtext = """\cp\c%i%s\co"""%(cindex,text)
        TGEEval('%s.setText("%s");'%(controlName,text))


# Provide a list of tuples with (control name, formatted text).
def SetColoredTextMany(evaluationList):
    if not len(evaluationList):
        return
    evaluation = ''.join('%s.setText("%s");'%(controlName,text) for controlName,text in evaluationList)
    TGEEval(evaluation)



class SpellPane:
    def __init__(self):
        self.currentPage = 0
        self.spellButtons = dict((x,TGEObject("SPELLPANE_SPELL%i"%x)) for x in xrange(0,25))
        self.spellText = TGEObject("SPELLPANE_SPELLTEXT")
        self.spellPic = TGEObject("SPELLPANE_SPELLPIC")
        
        self.swapSlot = -1
    
    
    def setFromCharacterInfo(self,cinfo):
        self.charInfo = cinfo
        spells = cinfo.SPELLS
        sindex = self.currentPage * 25
        for x in xrange(sindex,sindex + 25):
            button = self.spellButtons[x - sindex]
            button.pulseGreen = False
            if spells.has_key(x):
                sinfo = spells[x].SPELLINFO
                
                if self.swapSlot == x:
                    button.pulseGreen = True
                icon = sinfo.SPELLBOOKPIC
                if icon.startswith("SPELLICON_"):
                    split = icon.split("_")
                    index = int(split[2])
                    u0 = (float(index % 6) * 40.0) / 256.0
                    v0 = (float(index / 6) * 40.0) / 256.0
                    u1 = 40.0 / 256.0
                    v1 = 40.0 / 256.0
                    
                    button.setBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
                else:
                    button.setBitmap("~/data/ui/spellicons/%s"%icon)
                if spells[x].RECASTTIMER or cinfo.RAPIDMOBINFO.CASTING:
                    button.SetValue(1)
                    button.toggleLocked = True
                else:
                    button.SetValue(0)
                    button.toggleLocked = True
            else:
                button.SetBitmap("")
        
        TGEObject("SPELLPANE_PAGETEXT").setText("Page %i"%(self.currentPage+1))
    
    
    def swapSpells(self,slot):
        if self.swapSlot == slot:
            self.swapSlot = -1
        elif self.swapSlot == -1:
            if self.charInfo.SPELLS.has_key(slot):
                self.swapSlot = slot
        else:    # swap!
            PARTYWND.mind.onSpellSlotSwap(self.charInfo,self.swapSlot,slot)
            self.swapSlot = -1
            return
    
    
    def onSpellPagePrev(self):
        if self.currentPage == 0:
            return
        self.currentPage -= 1
        self.setFromCharacterInfo(self.charInfo)
    
    
    def onSpellPageNext(self):
        if self.currentPage == 9:
            return
        self.currentPage += 1
        self.setFromCharacterInfo(self.charInfo)
    
    
    def onSpellButton(self,args):
        slot = self.currentPage * 25 + int(args[1])

        # If an item is on the cursor or the slot is in the spell book.
        if PARTYWND.mind.cursorItem or self.charInfo.SPELLS.has_key(slot):
            PARTYWND.mind.onSpellSlot(self.charInfo,slot)
    
    
    # shift-single-click to jump to related encyc entry
    def onSpellButtonShift(self,args):
        slot = self.currentPage * 25 + int(args[1])
        try:
            spellProtoName = "Spell%s"%GetTWikiName(self.charInfo.SPELLS[slot].SPELLINFO.BASENAME)
            from encyclopediaWnd import ENCWND
            if not ENCWND.setPage(spellProtoName):
                TGECall("MessageBoxOK","Invalid Link","Sorry, you just stumbled upon an invalid encyclopedia link, page %s not found."%spellProtoName)
            else:
                TGEEval("canvas.pushDialog(EncyclopediaWnd);")
        except KeyError:
            pass
    
    
    # shift-right-click to enter item name/link in chat line
    def onSpellButtonShiftRight(self,args):
        slot = self.currentPage * 25 + int(args[1])
        try:
            spellProtoName = self.charInfo.SPELLS[slot].SPELLINFO.BASENAME
            commandCtrl = TomeGui.tomeCommandCtrl
            txt = ""
            if not commandCtrl.visible:
                TGECall("PushChatGui")
                commandCtrl.visible = True
                commandCtrl.makeFirstResponder(True)
            else:
                txt = commandCtrl.GetValue()
            commandCtrl.SetValue("%s <%s>"%(txt,spellProtoName))
        except KeyError:
            pass
    
    
    def onSpellButtonAlt(self,args):
        from macro import CURSORMACRO
        
        slot = self.currentPage * 25 + int(args[1])
        
        if CURSORMACRO.macroType == "SPELL" and CURSORMACRO.charIndex == PARTYWND.curIndex:
            if CURSORMACRO.macroInfo != slot:
                self.swapSlot = CURSORMACRO.macroInfo
                self.swapSpells(slot)
            CURSORMACRO.clear()
            return
        
        sinfo = self.charInfo.SPELLS.get(slot,None)
        
        if sinfo:
            CURSORMACRO.setMacro("SPELL",slot,None,PARTYWND.curIndex)
            cursor = TGEObject("DefaultCursor")
            icon = sinfo.SPELLINFO.SPELLBOOKPIC
            u0 = v0 = 0.0
            u1 = v1 = 1.0
            if icon.startswith("SPELLICON_"):
                split = icon.split("_")
                index = int(split[2])
                u0 = (float(index % 6) * 40.0) / 256.0
                v0 = (float(index / 6) * 40.0) / 256.0
                u1 = 40.0 / 256.0
                v1 = 40.0 / 256.0
                cursor.bitmapName="%s/data/ui/icons/spells0%s"%(GAMEROOT,split[1])
            else:
                cursor.bitmapName="%s/data/ui/spellicons/%s"%(GAMEROOT,icon)
            
            cursor.u0 = u0
            cursor.v0 = v0
            cursor.u1 = u1
            cursor.v1 = v1
            cursor.sizeX = 50
            cursor.sizeY = 50



class SettingsPane:
    def __init__(self):
        self.currentChar = None
        self.linkMouseTarget        = TGEObject("PARTYWND_LINKMOUSETARGETING")
        self.linkTarget             = TGEObject("PARTYWND_LINKCHARACTERTARGET")
        self.defaultTarget          = TGEObject("PARTYWND_DEFAULTTARGET")
        self.encounterSetting       = TGEObject("PARTYWND_ENCOUNTERSETTING")
        self.encounterSettingStatic = TGEObject("PARTYWND_ENCOUNTERSETTING_STATIC")
        self.encounterSettingTimer  = TGEObject("PARTYWND_ENCOUNTERSETTING_TIMER")
        self.encounterPVEZone       = TGEObject("PARTYWND_ENCOUNTERPVE_ZONE")
        self.encounterPVEDie        = TGEObject("PARTYWND_ENCOUNTERPVE_DIE")
        
        self.encounterSetting.add('PvE', RPG_ENCOUNTER_PVE)
        self.encounterSetting.add('RvR', RPG_ENCOUNTER_RVR)
        self.encounterSetting.add('GvG', RPG_ENCOUNTER_GVG)
        self.encounterSetting.add('PvP', RPG_ENCOUNTER_PVP)
        self.encounterSettingCurrent = RPG_ENCOUNTER_PVE
    
    
    def setFromCharacterInfo(self,cinfo,force = False):
        if cinfo == self.currentChar and not force:
            return
        
        self.currentChar = cinfo
        
        self.linkTarget.clear()
        self.linkTarget.add("",0)
        self.defaultTarget.clear()
        self.defaultTarget.add("",0)
        x = 1
        for c in PARTYWND.charInfos.itervalues():
            if c == cinfo:
                continue
            self.linkTarget.add(c.NAME,x)
            self.defaultTarget.add(c.NAME,x)
            x += 1
        
        if cinfo.clientSettings['LINKTARGET']:
            self.linkTarget.SetValue(cinfo.clientSettings['LINKTARGET'])
        else:
            self.linkTarget.SetValue("")
        
        if cinfo.clientSettings['DEFAULTTARGET']:
            self.defaultTarget.SetValue(cinfo.clientSettings['DEFAULTTARGET'])
        else:
            self.defaultTarget.SetValue("")
        
        self.linkMouseTarget.SetValue(cinfo.clientSettings['LINKMOUSETARGET'])
        
        try:
            self.encounterPVEZone.SetValue(cinfo.clientSettings['ENCOUNTERPVEZONE'])
            self.encounterPVEDie.SetValue(cinfo.clientSettings['ENCOUNTERPVEDIE'])
        except KeyError:  # new settings, may not exist yet
            self.encounterPVEZone.SetValue(1)
            self.encounterPVEDie.SetValue(1)



class SkillPane:
    def __init__(self):
        self.currentPage = 0
        self.buttonSkillNames = {}
        self.skillButtons = dict((x,TGEObject("SKILLBUTTON%i"%x)) for x in xrange(0,16))
        
        for sb in self.skillButtons.itervalues():
            sb.visible = False
        
        self.skillList =     TGEObject("PARTYWND_SKILLLIST")
        self.skillScroll =   TGEObject("PARTYWND_SKILLSCROLL")
        self.skillPageText = TGEObject("SKILLPAGETEXT")
    
    
    def setFromCharacterInfo(self,cinfo):
        self.charInfo = cinfo
        self.setPage(self.currentPage)
    
    
    def setPage(self,page):
        for sb in self.skillButtons.itervalues():
            sb.visible = False
        
        if not self.charInfo:
            return
        
        cinfo = self.charInfo
        self.currentPage = page
        
        skills = cinfo.SKILLS.keys()
        if not len(skills):
            return
        skills.sort()
        
        begin = page*16
        
        #CHAR LIST
        tc = self.skillList
        tc.setVisible(False)
        tc.clear()
        i = 0
        askills = []
        for sk in skills:
            skinfo = GetSkillInfo(sk)
            if skinfo.passive:
                TGEEval(r'PARTYWND_SKILLLIST.addRow(%i,"%s" TAB "%i");'%(i,skinfo.name,cinfo.SKILLS[sk]))
                i += 1
                continue
            askills.append(sk)
        
        #active skills
        if begin >= len(askills):
            page = len(askills)/16
            self.currentPage = page
            begin = page*16
        
        self.skillPageText.setText("Page %i"%(self.currentPage+1))
        
        for x,sk in enumerate(askills[begin:begin+16]):
            skinfo = GetSkillInfo(sk)
            
            button = self.skillButtons[x]
            button.visible = True
            button.setText("%s (%i)"%(skinfo.name,cinfo.SKILLS[sk]))
            self.buttonSkillNames[x] = sk
            button.setActive(True)
            begin += 1
            
            if cinfo.SKILLREUSE.has_key(sk.upper()) or cinfo.DEAD:
                button.setValue(1)
                button.toggleLocked = True
            else:
                button.setValue(0)
                button.toggleLocked = False
        
        tc.sort(0)
        tc.setSelectedRow(0)
        tc.scrollVisible(0)
        tc.setActive(True)
        tc.setVisible(True)
    
    
    def onSkillButtonPrev(self):
        if self.currentPage == 0:
            return
        self.setPage(self.currentPage - 1)
    
    
    def onSkillButtonNext(self):
        if self.currentPage == 9:
            return
        self.setPage(self.currentPage + 1)
    
    
    def onSkillButton(self,args):
        index = int(args[1])
        if int(self.skillButtons[index].toggleLocked):
            #already down
            return
        
        self.skillButtons[index].toggleLocked = True
        self.skillButtons[index].setValue(1)
        
        skill = self.buttonSkillNames[index]
        PyDoCommand(['PyDoCommand','/SKILL %i %s'%(PARTYWND.curIndex,skill)],False)
    
    
    # shift-single-click to jump to related encyc entry
    def onSkillButtonShift(self,args):
        index = int(args[1])
        try:
            skillName = "Skill%s"%GetTWikiName(self.buttonSkillNames[index])
            from encyclopediaWnd import ENCWND
            if not ENCWND.setPage(skillName):
                TGECall("MessageBoxOK","Invalid Link","Sorry, you just stumbled upon an invalid encyclopedia link, page %s not found."%skillName)
            else:
                TGEEval("canvas.pushDialog(EncyclopediaWnd);")
        except KeyError:
            pass
    
    
    # shift-right-click to enter item name/link in chat line
    def onSkillButtonShiftRight(self,args):
        index = int(args[1])
        try:
            skillName = self.buttonSkillNames[index]
            commandCtrl = TomeGui.tomeCommandCtrl
            txt = ""
            if not commandCtrl.visible:
                TGECall("PushChatGui")
                commandCtrl.visible = True
                commandCtrl.makeFirstResponder(True)
            else:
                txt = commandCtrl.GetValue()
            commandCtrl.SetValue("%s <%s>"%(txt,skillName))
        except KeyError:
            pass
    
    
    def onSkillButtonAlt(self,args):
        index = int(args[1])
        button = self.skillButtons[index]
        skillname = self.buttonSkillNames[index]
        skinfo = GetSkillInfo(skillname)
        if skinfo.passive:
            return
        
        from macro import CURSORMACRO
        CURSORMACRO.setMacro("SKILL",skillname,button,PARTYWND.curIndex)



class InvPane:
    def __init__(self):
        self.invButtons = dict((slot,TGEObject("SLOT_"+name)) for slot,name in SLOTNAMES.iteritems())
        #carry slots
        for i in xrange(0,30):
            self.invButtons[i+RPG_SLOT_CARRY_BEGIN]=TGEObject("SLOT_CARRY%i"%i)
        for i in xrange(30,60):
            self.invButtons[i+RPG_SLOT_CARRY_BEGIN]=TGEObject("SLOT_CARRY%i"%(i-30))
        
        self.tin =      TGEObject("INVPANE_TIN")
        self.copper =   TGEObject("INVPANE_COPPER")
        self.silver =   TGEObject("INVPANE_SILVER")
        self.gold =     TGEObject("INVPANE_GOLD")
        self.platinum = TGEObject("INVPANE_PLATINUM")
        self.page = 0
    
    def onInvSlot(self,slot):
        #if we have something in our cursor then this is valid
        from macro import CURSORMACRO
        CURSORMACRO.clear()
        if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
            slot+=self.page*30
        PARTYWND.mind.onInvSlot(self.charInfo,slot)
    
    def onInvSlotAlt(self,slot):
        #if we have something in our cursor then this is valid
        if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
            slot+=self.page*30
        PARTYWND.mind.onInvSlotAlt(self.charInfo,slot)
    
    def onInvSlotCtrl(self,slot):
        #if we have something in our cursor then this is valid
        if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
            slot+=self.page*30
        PARTYWND.mind.onInvSlotCtrl(self.charInfo,slot)
    
    # shift-single-click to jump to related encyc entry
    def onInvSlotShiftSingle(self,slot):
        if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
            slot += self.page*30
        try:
            itemProtoName = "Item%s"%GetTWikiName(self.charInfo.ITEMS[slot].PROTONAME)
            from encyclopediaWnd import ENCWND
            if not ENCWND.setPage(itemProtoName):
                TGECall("MessageBoxOK","Invalid Link","Sorry, you just stumbled upon an invalid encyclopedia link, page %s not found."%itemProtoName)
            else:
                TGEEval("canvas.pushDialog(EncyclopediaWnd);")
        except KeyError:
            pass
    
    # shift-right-click to enter item name/link in chat line
    def onInvSlotShiftRight(self,slot):
        if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
            slot += self.page*30
        try:
            itemProtoName = self.charInfo.ITEMS[slot].PROTONAME
            commandCtrl = TomeGui.tomeCommandCtrl
            txt = ""
            if not commandCtrl.visible:
                TGECall("PushChatGui")
                commandCtrl.visible = True
                commandCtrl.makeFirstResponder(True)
            else:
                txt = commandCtrl.GetValue()
            commandCtrl.SetValue("%s <%s>"%(txt,itemProtoName))
        except KeyError:
            pass
    
    def setPage(self,page):
        if self.page == page:
            return
        self.page = page
        self.setFromCharacterInfo(self.charInfo)
    
    def setFromCharacterInfo(self,cinfo):
        from mud.world.core import CollapseMoney
        cursorItem = PARTYWND.mind.cursorItem
        rootInfo = PARTYWND.mind.rootInfo
        tin,copper,silver,gold,platinum = CollapseMoney(rootInfo.TIN)
        self.tin.setText(str(tin))
        self.copper.setText(str(copper))
        self.silver.setText(str(silver))
        self.gold.setText(str(gold))
        # Need to format plat a bit since there's currently no specific upper bound.
        # Let's just hope nobody reaches 1G plat.
        if platinum > 1000:
            if platinum > 1000000:
                if platinum > 100000000:
                    self.platinum.setText("%s M"%str((platinum / 100000) / 10.0))
                else:
                    self.platinum.setText("%s M"%str((platinum / 10000) / 100.0))
            else:
                if platinum > 100000:
                    self.platinum.setText("%s K"%str((platinum / 100) / 10.0))
                else:
                    self.platinum.setText("%s K"%str((platinum / 10) / 100.0))
        else:
            self.platinum.setText(str(platinum))
        
        self.charInfo = cinfo
        for slot,butt in self.invButtons.iteritems():
            if self.page == 0 and RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN+30:
                continue
            if self.page == 1 and RPG_SLOT_CARRY_BEGIN+30 > slot >= RPG_SLOT_CARRY_BEGIN:
                continue
            
            butt.number = -1
            butt.pulseRed = False
            butt.pulseGreen = False
            
            if cursorItem and slot in cursorItem.SLOTS:
                if cursorItem.isUseable(cinfo):
                    butt.pulseGreen = True
            
            elif cursorItem and slot == RPG_SLOT_SECONDARY and RPG_SLOT_PRIMARY in cursorItem.SLOTS and "2H" in cursorItem.SKILL and cinfo.SKILLS.get("Power Wield"):
                if cursorItem.isUseable(cinfo):
                    butt.pulseGreen = True
            
            if not cinfo.ITEMS.has_key(slot): #only clear the ones we need to so we don't have to relock texture!
                butt.SetBitmap("")
        
        for slot,ghost in cinfo.ITEMS.iteritems():
            if self.page == 0 and RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN+30:
                continue
            if self.page == 1 and RPG_SLOT_CARRY_BEGIN+30 > slot >= RPG_SLOT_CARRY_BEGIN:
                continue
            
            if self.invButtons.has_key(slot):
                self.invButtons[slot].setBitmap("~/data/ui/items/"+ghost.BITMAP+"/0_0_0")
                if ghost.REPAIRMAX:
                    if RPG_SLOT_WORN_END > slot >= RPG_SLOT_WORN_BEGIN:
                        if float(ghost.REPAIR)/float(ghost.REPAIRMAX) < .2:
                            self.invButtons[slot].pulseRed = True
                
                if ghost.STACKMAX > 1:
                    self.invButtons[slot].number = ghost.STACKCOUNT


class StatsPane:
    resists = {RPG_RESIST_COLD:"STATS_RESISTCOLD",RPG_RESIST_FIRE:"STATS_RESISTFIRE",RPG_RESIST_DISEASE:"STATS_RESISTDISEASE",RPG_RESIST_MAGICAL:"STATS_RESISTMAGICAL",RPG_RESIST_PHYSICAL:"STATS_RESISTPHYSICAL",RPG_RESIST_POISON:"STATS_RESISTPOISON",RPG_RESIST_ELECTRICAL:"STATS_RESISTELECTRIC",RPG_RESIST_ACID:"STATS_RESISTACID"}
    
    def __init__(self):
        self.textCharName = TGEObject("Stats_CharacterName")
        self.textRace = TGEObject("Stats_Race")
        
        #self.textPClass = TGEObject("Stats_pclass")
        #self.textSClass = TGEObject("Stats_sclass")
        #self.textTClass = TGEObject("Stats_tclass")
        
        self.textSTR = TGEObject("Stats_STR")
        self.textDEX = TGEObject("Stats_DEX")
        self.textMND = TGEObject("Stats_MND")
        self.textMYS = TGEObject("Stats_MYS")
        self.textWIS = TGEObject("Stats_WIS")
        self.textBDY = TGEObject("Stats_BDY")
        self.textAGI = TGEObject("Stats_AGI")
        self.textREF = TGEObject("Stats_REF")
        
        self.textArmor =   TGEObject("Stats_Armor")
        self.textOffense = TGEObject("Stats_Offense")
        self.textDefense = TGEObject("Stats_Defense")
        self.textHealth =  TGEObject("Stats_Health")
        self.textMana =    TGEObject("Stats_Mana")
        
        self.textStamina =  TGEObject("Stats_Stamina")
        self.textPresence = TGEObject("Stats_Presence")
        self.textAdvance =  TGEObject("Stats_Advance")
        
        self.pxpBar =    TGEObject("STATS_PRIMARYXPBAR")
        self.pxpSlider = TGEObject("STATS_PRIMARYXPSLIDER")
        self.sxpBar =    TGEObject("STATS_SECONDARYXPBAR")
        self.sxpSlider = TGEObject("STATS_SECONDARYXPSLIDER")
        self.txpBar =    TGEObject("STATS_TERTIARYXPBAR")
        self.txpSlider = TGEObject("STATS_TERTIARYXPSLIDER")
        
        self.tclassLabel =  TGEObject("Stats_tclass_label")
        self.sclassLabel =  TGEObject("Stats_sclass_label")
        self.tclassHeader = TGEObject("Stats_tclass_header")
        self.sclassHeader = TGEObject("Stats_sclass_header")
        
        #self.textInfo = TGEObject("STATS_INFOTEXT")
    
    def setFromCharacterInfo(self,cinfo):
        self.charInfo = cinfo
        self.pxpBar.setValue(cinfo.PXPPERCENT)
        
        if cinfo.SLEVEL:
            self.pxpSlider.visible = True
            self.sxpBar.setValue(cinfo.SXPPERCENT)
            self.sxpBar.visible = True
            self.sxpSlider.visible = True
            self.sclassLabel.visible = True
            self.sclassHeader.visible = True
        else:
            self.pxpSlider.visible = False
            self.sxpBar.visible = False
            self.sxpSlider.visible = False
            self.sclassLabel.visible = False
            self.sclassHeader.visible = False
        
        if cinfo.TLEVEL:
            self.txpBar.setValue(cinfo.TXPPERCENT)
            self.txpBar.visible = True
            self.txpSlider.visible = True
            self.tclassLabel.visible = True
            self.tclassHeader.visible = True
        else:
            self.txpBar.visible = False
            self.txpSlider.visible = False
            self.tclassLabel.visible = False
            self.tclassHeader.visible = False
        
        evaluationList = []
        # Name
        evaluationList.append(("Stats_CharacterName","""\cp\c0%s\co"""%cinfo.NAME))
        # Race
        evaluationList.append(("Stats_Race","""\cp\c0%s\co"""%cinfo.RACE))
        # Sex
        evaluationList.append(("Stats_SEX","""\cp\c0%s\co"""%cinfo.SEX))
        # Presence
        evaluationList.append(("Stats_Presence","""\cp\c0%i\co"""%cinfo.PRE))
        # Primary Class
        evaluationList.append(("Stats_pclass","""\c0%s\c3(\c0%i\c3)"""%(cinfo.PCLASS,cinfo.PLEVEL)))
        # Secondary Class
        text = ""
        if cinfo.SLEVEL:
            text = """\c0%s\c3(\c0%i\c3)"""%(cinfo.SCLASS,cinfo.SLEVEL)
        evaluationList.append(("Stats_sclass",text))
        # Tertiary Class
        text = ""
        if cinfo.TLEVEL:
            text = """\c0%s\c3(\c0%i\c3)"""%(cinfo.TCLASS,cinfo.TLEVEL)
        evaluationList.append(("Stats_tclass",text))
        
        for st in RPG_STATS:
            ctrl = "Stats_%s"%st
            cur = getattr(cinfo,st)
            score = getattr(cinfo,st+"BASE")
            
            stcolor = 0
            if cur > score:
                stcolor = 2 #GREEN
            elif score > cur:
                stcolor = 1 #RED
            
            evaluationList.append((ctrl,"""\cp\c%i%i\co"""%(stcolor,cur)))
        
        evaluationList.append(("Stats_Offense","%i"%cinfo.OFFENSE))
        evaluationList.append(("Stats_Defense","%i"%cinfo.DEFENSE))
        
        rinfo = cinfo.RAPIDMOBINFO
        
        evaluationList.append(("Stats_Health","%i/%i"%(rinfo.HEALTH,rinfo.MAXHEALTH)))
        evaluationList.append(("Stats_Mana","%i/%i"%(rinfo.MANA,rinfo.MAXMANA)))
        evaluationList.append(("Stats_Stamina","%i/%i"%(rinfo.STAMINA,rinfo.MAXSTAMINA)))
        
        self.textArmor.setText(int(cinfo.ARMOR))
        self.textAdvance.setText(int(cinfo.ADVANCE))
        
        for resist,ctrlname in StatsPane.resists.iteritems():
            found = False
            for r,amt in cinfo.RESISTS:
                if r == resist:
                    found = True
                    if amt < 0:
                        evaluationList.append((ctrlname,r'\c1%i'%amt))
                    else:
                        evaluationList.append((ctrlname,r'\c2%i'%amt))
                    break
            if not found:
                TGEObject(ctrlname).setValue(0)
        
        SetColoredTextMany(evaluationList)


PARTYWND = None
class PartyWnd:
    def __init__(self):
        self.mind = None
        self.curIndex = -1
        self.charInfos = None
        
        self.dirtySkills = True
        self.buttonStats =     TGEObject("PartyWnd_ButtonStats")
        self.buttonInventory = TGEObject("PartyWnd_ButtonInventory")
        self.buttonSkills =    TGEObject("PartyWnd_ButtonSkills")
        self.buttonSpells =    TGEObject("PartyWnd_ButtonSpells")
        self.buttonSettings =  TGEObject("PartyWnd_ButtonSettings")
        
        self.paneStats =     TGEObject("StatsPane")
        self.paneInventory = TGEObject("InventoryPane")
        self.paneSkills =    TGEObject("SkillsPane")
        self.paneSpells =    TGEObject("SpellsPane")
        self.paneSettings =  TGEObject("SettingsPane")
        self.paneAdvance =   TGEObject("AdvancePane")
        
        self.statsPane = StatsPane()
        self.invPane = InvPane()
        self.skillPane  = SkillPane()
        self.settingsPane = SettingsPane()
        self.spellPane = SpellPane()
        from advancePane import AdvancePane
        self.advancePane  = AdvancePane()
        
        self.panes = {self.paneStats:self.statsPane,self.paneInventory:self.invPane,self.paneSkills:self.skillPane,self.paneSpells:self.spellPane, self.paneSettings:self.settingsPane,self.paneAdvance:self.advancePane}
        self.activePane = None
        self.disablePanes()
        
        self.encounterTimer = 0
        self.encounterBlock = 0
    
    def tick(self):
        global XPSLIDERS_DIRTY
        if self.curIndex != -1:
            self.setFromCharacterInfo(self.curIndex,True)
            self.dirtySkills |= AreSkillsDirty(self.charInfos[self.curIndex])
        
        #someoneDiedOrWasRezzed = False
        #for cinfo in self.charInfos.values():
            #if cinfo.wasDead != cinfo.DEAD:
                #cinfo.wasDead = cinfo.DEAD
                #if cinfo == self.charInfos[self.curIndex]:
                    #current char died, try and find a live one
                    #for x in range(0,len(self.charInfos)):
                        #if not self.charInfos[x].DEAD:
                            #self.setFromCharacterInfo(x)
                            #break
                #someoneDiedOrWasRezzed = True
        
        #if len(self.dirtySkills) or someoneDiedOrWasRezzed:
        
        if len(XPSLIDERS_DIRTY):
            PyOnSendXPSliders()
            XPSLIDERS_DIRTY = []
        
        if self.encounterBlock < 0:
            self.encounterBlock = 0
            self.encounterTimer = 0
            self.settingsPane.encounterSettingStatic.setVisible(False)
            self.settingsPane.encounterSettingTimer.setVisible(False)
            self.settingsPane.encounterSetting.setVisible(True)
        elif not self.encounterBlock and 0 < self.encounterTimer:
            timeDelta = int(self.encounterTimer - systemTime())
            if timeDelta <= 0:
                self.encounterTimer = 0
                self.settingsPane.encounterSettingStatic.setVisible(False)
                self.settingsPane.encounterSettingTimer.setVisible(False)
                self.settingsPane.encounterSetting.setVisible(True)
            else:
                self.settingsPane.encounterSettingTimer.setText('(blocked for another %i seconds)'%timeDelta)
    
    def disablePanes(self):
        for p in self.panes.iterkeys():
            p.visible = False
        
    def changeCharacterInfo(self,result,args):
        index = args[0]
        self.curIndex = index
        self.setFromCharacterInfo(index)
        from npcWnd import NPCWND
        NPCWND.refreshList()
        from playerSettings import PLAYERSETTINGS
        PLAYERSETTINGS.updateMainCharIndex(index)
    
    def setCursorItem(self):
        if not self.mind:
            return
        if self.curIndex != -1:
            self.invPane.setFromCharacterInfo(self.charInfos[self.curIndex])
    
    def encounterSettingDisturbed(self):
        if not self.encounterTimer:
            self.settingsPane.encounterSetting.setVisible(False)
            self.settingsPane.encounterSettingStatic.setVisible(True)
        if self.encounterBlock != 0:
            TGEEval('PARTYWND_ENCOUNTERSETTING_STATIC.setText("\cp\c1%s\co");'%self.settingsPane.encounterSetting.getValue())
            self.settingsPane.encounterSettingTimer.setVisible(False)
        else:
            self.settingsPane.encounterSettingStatic.setText(self.settingsPane.encounterSetting.getValue())
            self.settingsPane.encounterSettingTimer.setText('(blocked for another 120 seconds)')
            self.settingsPane.encounterSettingTimer.setVisible(True)
        newTime = systemTime() + 120  # 2 minutes
        if newTime > self.encounterTimer:
            self.encounterTimer = newTime
    
    def setFromCharacterInfo(self,index,isTick=False):
        cinfo = self.charInfos[index]
        
        if self.curIndex != index and self.curIndex != -1:
            d = self.mind.perspective.callRemote("PlayerAvatar","setCurrentCharacter",index)
            if d:
                d.addCallback(self.changeCharacterInfo,(index,))
            # Inform the player about the new active Character.
            TomeGui.receiveGameText(RPG_MSG_GAME_EVENT, "%s is now your active character.\\n"%cinfo.NAME)
            return
        else:
            self.curIndex = index #this initializes if necessary
        
        if not isTick:
            from macro import CURSORMACRO
            CURSORMACRO.setMacro(None,None)
            
            # Get experience distribution values based on the client's settings.
            pvalue = cinfo.clientSettings['PXPGAIN']
            svalue = cinfo.clientSettings['SXPGAIN']
            tvalue = cinfo.clientSettings['TXPGAIN']
            
            # Update the GUI experience sliders based on the distribution
            # values.
            PARTYWND.statsPane.pxpSlider.setValue(pvalue*100.0)
            PARTYWND.statsPane.sxpSlider.setValue(svalue*100.0)
            PARTYWND.statsPane.txpSlider.setValue(tvalue*100.0)
            
            # The character may have changed, and the new character may have
            # different experience distribution settings.  Send the client's
            # settings for experience distribution to the world so that the
            # distribution is in sync.
            self.mind.perspective.callRemote("PlayerAvatar","setXPGain",index,pvalue,svalue,tvalue)
            
            self.skillPane.setFromCharacterInfo(cinfo)
            self.invPane.charInfo = cinfo
        
        TGEObject("PartyWnd_Window").SetText(cinfo.NAME)
        TGEObject("MacroWnd_Window").SetText(cinfo.NAME)
       
        picCtrl = TGEObject("PARTYWND_PORTRAITPIC")
        if picCtrl.visible:
            if cinfo.DEAD:
                picCtrl.setBitmap("~/data/ui/charicons/dead")
            else:
                picCtrl.setBitmap("~/data/ui/charportraits/%s"%cinfo.PORTRAITPIC)
        
        if self.activePane:
            if self.activePane != self.paneSkills:
                self.panes[self.activePane].setFromCharacterInfo(cinfo)
            elif isTick and self.dirtySkills:
                self.skillPane.setFromCharacterInfo(cinfo)
                self.dirtySkills = False
            if not self.activePane.visible:    # set visible after update
                self.disablePanes()
                self.activePane.visible = True
        
        from petWnd import PETWND
        from craftingWnd import CRAFTINGWND
        from vaultWnd import VAULTWND
        if VAULTWND.vaultWnd.visible:
            VAULTWND.setFromCharacterInfo(cinfo)
        if TGEObject("PetWnd_Window").visible:
            PETWND.setFromCharacterInfo(cinfo)
        if CRAFTINGWND.window.visible:
            CRAFTINGWND.setFromCharacterInfo(cinfo)


#baseline
def SetFromCharacterInfos(cinfos):
    PARTYWND.curIndex = -1
    PARTYWND.charInfos = cinfos
    
    from playerSettings import PLAYERSETTINGS
    PLAYERSETTINGS.setCharacterInfos(cinfos)
    
    PARTYWND.setFromCharacterInfo(0)
    PARTYWND.buttonStats.performClick()

#Py::OnPartyWndStats();

def OnInvSlot(args):
    slot = int(args[1])
    PARTYWND.invPane.onInvSlot(slot)

def OnInvSlotCtrl(args):
    slot = int(args[1])
    PARTYWND.invPane.onInvSlotCtrl(slot)

def OnInvSlotAlt(args):
    slot = int(args[1])
    PARTYWND.invPane.onInvSlotAlt(slot)

def OnInvSlotShiftSingle(args):
    slot = int(args[1])
    PARTYWND.invPane.onInvSlotShiftSingle(slot)

def OnInvSlotShiftRight(args):
    slot = int(args[1])
    PARTYWND.invPane.onInvSlotShiftRight(slot)

def OnInvButton(args):
    slot = int(args[1])
    PARTYWND.invPane.onInvSlot(slot)

def OnPartyWndStats():
    if PARTYWND.activePane:
        PARTYWND.activePane.visible = False
    PARTYWND.activePane = PARTYWND.paneStats
    
def OnPartyWndInventory():
    if PARTYWND.activePane:
        PARTYWND.activePane.visible = False
    PARTYWND.activePane = PARTYWND.paneInventory
    
def OnPartyWndSkills():
    if PARTYWND.activePane:
        PARTYWND.activePane.visible = False
    PARTYWND.activePane = PARTYWND.paneSkills

def OnPartyWndSpells():
    if PARTYWND.activePane:
        PARTYWND.activePane.visible = False
    PARTYWND.activePane = PARTYWND.paneSpells

def OnPartyWndSettings():
    if PARTYWND.activePane:
        PARTYWND.activePane.visible = False
    PARTYWND.activePane = PARTYWND.paneSettings

def OnPartyWndAdvance():
    if PARTYWND.activePane:
        PARTYWND.activePane.visible = False
    PARTYWND.activePane = PARTYWND.paneAdvance



#OnDefaultCharacterTarget
#PARTYWND_DEFAULTTARGET
def OnDefaultCharacterTarget():
    from playerSettings import PLAYERSETTINGS
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    defaulttarget = TGEObject("PARTYWND_DEFAULTTARGET").GetValue()
    if defaulttarget:
        cinfo.clientSettings['DEFAULTTARGET'] = defaulttarget
    else:
        cinfo.clientSettings['DEFAULTTARGET'] = None
    PLAYERSETTINGS.storeCharacterSettings()


def OnEncounterSetting():
    newSetting = RPG_ENCOUNTER_SETTINGS[TGEObject("PARTYWND_ENCOUNTERSETTING").GetValue()]
    if newSetting != PARTYWND.settingsPane.encounterSettingCurrent:
        PARTYWND.mind.perspective.callRemote("PlayerAvatar", "setEncounterSetting", newSetting)
        PARTYWND.settingsPane.encounterSettingCurrent = newSetting
        PARTYWND.encounterSettingDisturbed()


def OnEncounterPVEZone():
    from playerSettings import PLAYERSETTINGS
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    PvEZone = TGEObject("PARTYWND_ENCOUNTERPVE_ZONE").GetValue()
    if int(PvEZone):
        cinfo.clientSettings['ENCOUNTERPVEZONE'] = 1
    else:
        cinfo.clientSettings['ENCOUNTERPVEZONE'] = 0
    PLAYERSETTINGS.storeCharacterSettings()


def OnEncounterPVEDie():
    from playerSettings import PLAYERSETTINGS
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    PvEDeath = TGEObject("PARTYWND_ENCOUNTERPVE_DIE").GetValue()
    if int(PvEDeath):
        cinfo.clientSettings['ENCOUNTERPVEDIE'] = 1
    else:
        cinfo.clientSettings['ENCOUNTERPVEDIE'] = 0
    PLAYERSETTINGS.storeCharacterSettings()


def OnLinkCharacterTarget():
    from playerSettings import PLAYERSETTINGS
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    linktarget = TGEObject("PARTYWND_LINKCHARACTERTARGET")
    mouselink = TGEObject("PARTYWND_LINKMOUSETARGETING")
    
    target = linktarget.GetValue()
    if target:
        cinfo.clientSettings['LINKTARGET'] = target
    else:
        cinfo.clientSettings['LINKTARGET'] = None
    
    mouselink.SetValue(0)
    cinfo.clientSettings['LINKMOUSETARGET'] = 0
    
    PLAYERSETTINGS.storeCharacterSettings()


def CharSetTarget(args):
    cindex = int(args[1])
    cinfo = PARTYWND.charInfos[cindex]
    PARTYWND.mind.charSetTarget(PARTYWND.curIndex,cinfo.MOBID)


def OnMyAvatar():
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    PyDoCommand(['PyDoCommand','/AVATAR %s'%cinfo.NAME],True)


def OnMyDesc():
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    PyDoCommand(['PyDoCommand','/mydesc'],True)


def OnLinkMouseTargeting():
    from playerSettings import PLAYERSETTINGS
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    linktarget = TGEObject("PARTYWND_LINKCHARACTERTARGET")
    mouselink = TGEObject("PARTYWND_LINKMOUSETARGETING")
    
    if int(mouselink.GetValue()):
        cinfo.clientSettings['LINKMOUSETARGET'] = 1
    else:
        cinfo.clientSettings['LINKMOUSETARGET'] = 0
    
    linktarget.SetValue("")
    cinfo.clientSettings['LINKTARGET'] = None
    
    PLAYERSETTINGS.storeCharacterSettings()



def OnReallyExpungeItem():
    # Get the item on the cursor.
    item = PARTYWND.mind.cursorItem
    
    # If there's no item on the cursor, just return.
    if not item:
        return
    
    # Don't allow expunging of quest items. Inform the player.
    if item.FLAGS&RPG_ITEM_QUEST:
        TGEEval('MessageBoxOk("Quest Item", "%s is an essential quest item. Please keep it in your inventory.");'%item.NAME)
        return
    
    # Expunge the item.
    PARTYWND.mind.expungeItem()


def OnExpungeItem():
    # Get the item on the cursor.
    item = PARTYWND.mind.cursorItem
    
    # If there's no item on the cursor, just return.
    if not item:
        return
    
    # Don't allow expunging of quest items. Inform the player.
    if item.FLAGS&RPG_ITEM_QUEST:
        TGEEval('MessageBoxOk("Quest Item", "%s is an essential quest item. Please keep it in your inventory.");'%item.NAME)
        return
    
    # Require the player to confirm deletion.
    TGEEval('MessageBoxYesNo("Expunge Item?", "Do you really want to expunge %s?","Py::OnReallyExpungeItem();");'%item.NAME)



SPLITITEM = None

def OnReallySplitItem():
    try:
        ssize = int(TGEObject("SPLITSTACK_STACKSIZE").getValue())
    except:
        return
    
    if 1 > ssize or ssize >= SPLITITEM.STACKCOUNT:
        return
    
    TGEEval("canvas.popDialog(SplitStackGui);")
    PARTYWND.mind.splitItem(ssize)

def OnSplitItem():
    global SPLITITEM
    SPLITITEM = None
    item = PARTYWND.mind.cursorItem
    if not item:
        return
    
    if item.STACKCOUNT <= 1 or item.STACKMAX <=1:
        return
    
    pic = TGEObject("SPLITSTACK_ITEMPIC")
    pic.setBitmap("~/data/ui/items/"+item.BITMAP+"/0_0_0")
    pic.number = -1
    
    TEXT_HEADER = """<font:Arial Bold:14><just:center><shadow:1:1><shadowcolor:000000>"""
    
    eval = 'SPLITSTACK_CURRENTSTACK.setText("%i");SPLITSTACK_ITEMTEXT.setText("%s");Canvas.pushDialog(SplitStackGui);SPLITSTACK_STACKSIZE.makeFirstResponder(true);'%(item.STACKCOUNT,TEXT_HEADER+item.NAME)
    TGEEval(eval)
    
    SPLITITEM = item


XPSLIDER_RENTRANT = False #this guards against infinite recursion between sliders... yuck
def PyOnXPSlider(which):
    global XPSLIDER_RENTRANT
    
    if XPSLIDER_RENTRANT:
        return
    
    XPSLIDER_RENTRANT = True
    
    pvalue = float(PARTYWND.statsPane.pxpSlider.getValue())/100.0
    svalue = float(PARTYWND.statsPane.sxpSlider.getValue())/100.0
    tvalue = float(PARTYWND.statsPane.txpSlider.getValue())/100.0
    
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    
    if not cinfo.SLEVEL and cinfo.TLEVEL:
        #why are we here?
        pvalue = 1
        svalue = 0
        tvalue = 0
    elif not cinfo.TLEVEL:
        if which == 0:
            svalue = 1.0 - pvalue
            tvalue = 0
        if which == 1:
            pvalue = 1.0 - svalue
            tvalue = 0
    else:
        if which == 0:
            leftover = 1.0 - pvalue
            svalue = tvalue = leftover*.5
        if which == 1:
            leftover = 1.0 - svalue
            pvalue = tvalue = leftover*.5
        if which == 2:
            leftover = 1.0 - tvalue
            svalue = pvalue = leftover*.5
    
    PARTYWND.statsPane.pxpSlider.setValue(pvalue*100.0)
    PARTYWND.statsPane.sxpSlider.setValue(svalue*100.0)
    PARTYWND.statsPane.txpSlider.setValue(tvalue*100.0)
    
    XPSLIDER_RENTRANT = False


def PyOnPrimaryXPSlider():
    pass
    #PyOnXPSlider(0)

def PyOnSecondaryXPSlider():
    pass
    #PyOnXPSlider(1)

def PyOnTertiaryXPSlider():
    pass
    #PyOnXPSlider(2)

XPSLIDERS_DIRTY = []
def PyOnXPSlider():
    global XPSLIDERS_DIRTY
    XPSLIDERS_DIRTY.append(PARTYWND.curIndex)
    
    pvalue = float(PARTYWND.statsPane.pxpSlider.getValue())/100.0
    svalue = float(PARTYWND.statsPane.sxpSlider.getValue())/100.0
    tvalue = float(PARTYWND.statsPane.txpSlider.getValue())/100.0
    
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    cinfo.clientSettings['PXPGAIN'] = pvalue
    cinfo.clientSettings['SXPGAIN'] = svalue
    cinfo.clientSettings['TXPGAIN'] = tvalue

#on mouse button up on slider send away
def PyOnSendXPSliders(override = None):
    from playerSettings import PLAYERSETTINGS
    if not override:
        override = XPSLIDERS_DIRTY
    
    for index,cinfo in PARTYWND.charInfos.iteritems():
        if index in override:
            pvalue = cinfo.clientSettings['PXPGAIN']
            svalue = cinfo.clientSettings['SXPGAIN']
            tvalue = cinfo.clientSettings['TXPGAIN']
            PARTYWND.mind.perspective.callRemote("PlayerAvatar","setXPGain",index,pvalue,svalue,tvalue)
    PLAYERSETTINGS.storeCharacterSettings()

def PyOnTargetChar(args):
    index = int(args[1])
    mobId = PARTYWND.charInfos[index].MOBID
    PARTYWND.mind.charSetTarget(PARTYWND.curIndex,mobId)

def OnInvPage(args):
    page = int(args[1])
    PARTYWND.invPane.setPage(page)

def OnInvPageAlt(args):    
    PyDoCommand(("PyDoCommand", "/sort %s" % args[1]))    

def PyOnTargetCharTarget(args):
    index = int(args[1])
    rInfo = PARTYWND.charInfos[index].RAPIDMOBINFO
    mobId = rInfo.TGTID
    #if index == PARTYWND.curIndex:
    PARTYWND.mind.charSetTarget(index,mobId,True)
    #else:
        #PARTYWND.mind.charSetTarget(PARTYWND.curIndex,mobId,False)


def GetMouseOverItem():
    #returns tuple (code,slot)
    #code 'INV'=inv, 'SKILL'=skill, 'SPELL'=spell, 'CMD' = default command
    #XXX these need to take current page into account (for spells, skills)
    
    if PARTYWND.paneSpells.mouseOver:
        for slot,button in PARTYWND.spellPane.spellButtons.iteritems():
            if button.mouseOver:
                return ('SPELL',slot)
    elif PARTYWND.paneInventory.mouseOver:
        for slot,button in PARTYWND.invPane.invButtons.iteritems():
            if button.mouseOver:
                return ('INV',slot)
    elif PARTYWND.paneSkills.mouseOver:
        for slot,button in PARTYWND.skillPane.skillButtons.iteritems():
            if button.mouseOver:
                return ('SKILL',PARTYWND.skillPane.buttonSkillNames[slot])
    
    from defaultCommandsWnd import DEFAULTCOMMANDWND
    for slot,button in DEFAULTCOMMANDWND.commandButtons.iteritems():
        if button.mouseOver:
            return ('CMD',slot)
    
    return None


def ChoosePortrait(chosen):
    if not chosen:
        return
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","setPortraitPic",chosen)

def OnPartyWndChoosePortrait():
    from charPortraitWnd import SetChoosePortraitCallback
    SetChoosePortraitCallback(ChoosePortrait)
    TGEEval("canvas.pushDialog(CharPortraitWnd);")


# REPAIR
def PyOnRepairItem():
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","repairItem",PARTYWND.curIndex)

def PyOnRepairAll():
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","repairAll",PARTYWND.curIndex)

def PyOnRepairParty():
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","repairParty",PARTYWND.curIndex)

def PyOnCheckRepairItem():
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    CheckRepairItem(cinfo.NAME,cinfo.SKILLS.get('Repair',0),PARTYWND.mind.rootInfo,PARTYWND.mind.cursorItem)

def PyOnCheckRepairAll():
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    CheckRepairAll(cinfo.NAME,cinfo.SKILLS.get('Repair',0),PARTYWND.mind.rootInfo,cinfo.ITEMS)

def PyOnCheckRepairParty():
    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
    CheckRepairParty(cinfo.NAME,cinfo.SKILLS.get('Repair',0),PARTYWND.mind.rootInfo,PARTYWND.charInfos)


def PyExec():
    global PARTYWND
    PARTYWND = PartyWnd()
    
    TGEExport(OnPartyWndChoosePortrait,"Py","OnPartyWndChoosePortrait","desc",1,1)
    
    TGEExport(OnPartyWndStats,"Py","OnPartyWndStats","desc",1,1)
    TGEExport(OnPartyWndInventory,"Py","OnPartyWndInventory","desc",1,1)
    TGEExport(OnPartyWndSkills,"Py","OnPartyWndSkills","desc",1,1)
    TGEExport(OnPartyWndSpells,"Py","OnPartyWndSpells","desc",1,1)
    TGEExport(OnPartyWndSettings,"Py","OnPartyWndSettings","desc",1,1)
    
    TGEExport(OnPartyWndAdvance,"Py","OnPartyWndAdvance","desc",1,1)
    
    TGEExport(PyOnTargetChar,"Py","OnTargetChar","desc",2,2)
    TGEExport(PyOnTargetCharTarget,"Py","OnTargetCharTarget","desc",2,2)
    
    # Settings
    TGEExport(OnLinkCharacterTarget,"Py","OnLinkCharacterTarget","desc",1,1)
    TGEExport(OnMyAvatar,"Py","OnMyAvatar","desc",1,1)
    TGEExport(OnMyDesc,"Py","OnMyDesc","desc",1,1)
    TGEExport(OnLinkMouseTargeting,"Py","OnLinkMouseTargeting","desc",1,1)
    TGEExport(OnDefaultCharacterTarget,"Py","OnDefaultCharacterTarget","desc",1,1)
    TGEExport(OnEncounterSetting,"Py","OnEncounterSetting","desc",1,1)
    TGEExport(OnEncounterPVEZone,"Py","OnEncounterPVEZone","desc",1,1)
    TGEExport(OnEncounterPVEDie,"Py","OnEncounterPVEDie","desc",1,1)
    
    # Inventory
    TGEExport(OnInvSlot,"Py","OnInvSlot","desc",2,2)
    TGEExport(OnInvSlotAlt,"Py","OnInvSlotAlt","desc",2,2)
    TGEExport(OnInvSlotCtrl,"Py","OnInvSlotCtrl","desc",2,2)
    TGEExport(OnInvSlotShiftSingle,"Py","OnInvSlotShiftSingle","desc",2,2)
    TGEExport(OnInvSlotShiftRight,"Py","OnInvSlotShiftRight","desc",2,2)
    
    TGEExport(CharSetTarget,"Py","CharSetTarget","desc",2,2)
    
    TGEExport(OnInvPage,"Py","OnInvPage","desc",2,2)
    TGEExport(OnInvPageAlt,"Py","OnInvPageAlt","desc",2,2)
    
    TGEExport(OnSplitItem,"Py","OnSplitItem","desc",1,1)
    TGEExport(OnReallySplitItem,"Py","OnReallySplitStack","desc",1,1)
    
    TGEExport(OnExpungeItem,"Py","OnExpungeItem","desc",1,1)
    TGEExport(OnReallyExpungeItem,"Py","OnReallyExpungeItem","desc",1,1)
    
    # XP Sliders
    TGEExport(PyOnPrimaryXPSlider,"Py","OnPrimaryXPSlider","desc",1,1)
    TGEExport(PyOnSecondaryXPSlider,"Py","OnSecondaryXPSlider","desc",1,1)
    TGEExport(PyOnTertiaryXPSlider,"Py","OnTertiaryXPSlider","desc",1,1)
    
    TGEExport(PyOnSendXPSliders,"Py","OnSendXPSliders","desc",1,1)
    TGEExport(PyOnXPSlider,"Py","OnXPSlider","desc",1,1)
    
    # Spell pane functionalities
    spellPane = PARTYWND.spellPane
    TGEExport(spellPane.onSpellPagePrev,"Py","OnSpellPagePrev","desc",1,1)
    TGEExport(spellPane.onSpellPageNext,"Py","OnSpellPageNext","desc",1,1)
    TGEExport(spellPane.onSpellButton,"Py","OnSpellButton","desc",2,2)
    TGEExport(spellPane.onSpellButtonShift,"Py","OnSpellButtonShift","desc",2,2)
    TGEExport(spellPane.onSpellButtonShiftRight,"Py","OnSpellButtonShiftRight","desc",2,2)
    TGEExport(spellPane.onSpellButtonAlt,"Py","OnSpellButtonAlt","desc",2,2)
    
    # Settings pane functionalities
    # uhmm... nothing yet, all that probably should be here is in partyWnd
    #settingsPane = PARTYWND.settingsPane
    
    # Skill pane functionalities
    skillPane = PARTYWND.skillPane
    TGEExport(skillPane.onSkillButtonPrev,"Py","OnSkillButtonPrev","desc",1,1)
    TGEExport(skillPane.onSkillButtonNext,"Py","OnSkillButtonNext","desc",1,1)
    TGEExport(skillPane.onSkillButton,"Py","OnSkillButton","desc",2,2)
    TGEExport(skillPane.onSkillButtonShift,"Py","OnSkillButtonShift","desc",2,2)
    TGEExport(skillPane.onSkillButtonShiftRight,"Py","OnSkillButtonShiftRight","desc",2,2)
    TGEExport(skillPane.onSkillButtonAlt,"Py","OnSkillButtonAlt","desc",2,2)
    
    # Repair
    TGEExport(PyOnRepairItem,"Py","OnRepairItem","desc",1,1)
    TGEExport(PyOnRepairAll,"Py","OnRepairAll","desc",1,1)
    TGEExport(PyOnRepairParty,"Py","OnRepairParty","desc",1,1)
    
    TGEExport(PyOnCheckRepairItem,"Py","OnCheckRepairItem","desc",1,1)
    TGEExport(PyOnCheckRepairAll,"Py","OnCheckRepairAll","desc",1,1)
    TGEExport(PyOnCheckRepairParty,"Py","OnCheckRepairParty","desc",1,1)


