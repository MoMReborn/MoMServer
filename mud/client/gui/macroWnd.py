# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport



class MacroWnd(object):
    instance = None
    
    
    def __new__(cl, *p, **k):
        if not MacroWnd.instance:
            MacroWnd.instance = object.__new__(cl, *p, **k)
        return MacroWnd.instance
    
    
    def __init__(self):
        self.charPages = {}
        
        self.charButtons  = {}
        self.healthBars   = {}
        self.manaBars     = {}
        self.staminaBars  = {}
        self.targetBars   = {}
        self.macroButtons = {}
    
    
    @staticmethod
    def getInstance(self):
        return MacroWnd.instance
    
    
    def initTGEObjects(self):
        self.window = TGEObject("MacroWnd_Window")
        
        for x in xrange(0,6):
            self.charButtons[x]  = TGEObject("MACROWND_CHAR%i"%x)
            self.healthBars[x]   = TGEObject("MACROWND_CHAR%i_HEALTHBAR"%x)
            self.manaBars[x]     = TGEObject("MACROWND_CHAR%i_MANABAR"%x)
            self.staminaBars[x]  = TGEObject("MACROWND_CHAR%i_STAMINABAR"%x)
            self.targetBars[x]   = TGEObject("MACROWND_CHAR%i_TARGETBAR"%x)
            self.macroButtons[x] = dict((y,TGEObject("MACROWND_MACRO%i_%i"%(x,y))) for y in xrange(0,10))
        
        self.updateActivePage(0)
    
    
    def disableButtons(self, index):
        for butt in self.macroButtons[index].itervalues():
            butt.setValue(1)
            butt.toggleLocked = True
    
    
    def enableButtons(self, index):
        for butt in self.macroButtons[index].itervalues():
            butt.setValue(0)
            butt.toggleLocked = False
    
    
    def updateActivePage(self, page):
        # Only display active page in first character button.
        # Maybe add another gui element for this in the future.
        self.charButtons[0].hotkey = str((page + 1) % 10)
    
    
    def setFromCharacterInfos(self, cinfos):
        numc = len(cinfos)
        self.window.extent = '418 %i'%(34 + 34 * numc)
        
        for x in xrange(0,6):
            self.charButtons[x].visible = False
            self.healthBars[x].visible = False
            self.manaBars[x].visible = False
            self.staminaBars[x].visible = False
            self.targetBars[x].visible = False
        
        for y in xrange(0,10):
            for x in xrange(numc,6):
                self.macroButtons[x][y].visible = False
            for x in xrange(0,numc):
                self.macroButtons[x][y].visible = True
        
        for cindex,cinfo in cinfos.iteritems():
            picCtrl = self.charButtons[cindex]
            hbar    = self.healthBars[cindex]
            mbar    = self.manaBars[cindex]
            sbar    = self.staminaBars[cindex]
            tbar    = self.targetBars[cindex]
            hbar.visible = True
            mbar.visible = True
            sbar.visible = True
            
            rInfo = cinfo.RAPIDMOBINFO
            
            hbar.SetValue(rInfo.HEALTH / rInfo.MAXHEALTH)
            
            if rInfo.MAXMANA:
                mbar.SetValue(rInfo.MANA / rInfo.MAXMANA)
            else:
                mbar.SetValue(0)
            
            if cinfo.UNDERWATERRATIO != 1.0:
                sbar.setProfile("GuiBreathBarProfile")
                sbar.SetValue(cinfo.UNDERWATERRATIO)
            else:
                sbar.setProfile("GuiStaminaBarProfile")
                sbar.SetValue(rInfo.STAMINA/rInfo.MAXSTAMINA)
            
            if rInfo.TGT:
                tbar.visible = True
                tbar.SetValue(rInfo.TGTHEALTH)
            else:
                tbar.visible = False
            
            picCtrl.visible = True
            if cinfo.DEAD:
                picCtrl.setBitmap("~/data/ui/icons/dead")
            else:
                picCtrl.setBitmap("~/data/ui/charportraits/%s"%cinfo.PORTRAITPIC)
    
    
    def onMacroCharButton(self, args):
        from mud.client.playermind import PLAYERMIND
        if not PLAYERMIND:
            return
        index = int(args[1])
        if PLAYERMIND.pgserver:
            #alliances
            from allianceWnd import OnAllianceSelectByIndex
            OnAllianceSelectByIndex((0,index))
            return
        
        from partyWnd import PARTYWND
        if index < len(PARTYWND.charInfos):
            PARTYWND.setFromCharacterInfo(index)



MacroWnd()



def PyExec():
    MACROWND = MacroWnd.instance
    MACROWND.initTGEObjects()
    
    TGEExport(MACROWND.onMacroCharButton,"Py","OnMacroCharButton","desc",2,2)

