# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
import time
import math
#BUFFWND_CHAR0_PANE
#BUFFWND_CHAR0_NAME
#BUFFWND_CHAR0_EFFECT0

BUFFWND = None

class SingleBuffPane:
    def __init__(self):
        self.nameCtrl = TGEObject("BUFFWND_SINGLE_NAME")
        self.effectCtrls = dict((x,TGEObject("BUFFWND_SINGLE_EFFECT%i"%x)) for x in xrange(0,24))
            
        self.lastTime = time.time()
        self.lastPID = 0
        self.buffCount = 0
        
    def setCharInfo(self,cinfo):
        
            
        #spell effects
        
        self.nameCtrl.SetValue(cinfo.NAME)
        
        tm = time.time()
            
        delta = tm - self.lastTime
        delta *= 0.96
        self.lastTime = tm
        
        x = 0
        
        # Buffs only need sorted if:
        # - There is more than one buff.
        # - The count of buffs have changed (something was added or removed).
        # - The last PID (process ID) has changed (new buff).
        spellEffects = cinfo.SPELLEFFECTS
        if 1 < len(spellEffects) and (self.buffCount != len(spellEffects) or self.lastPID != spellEffects[-1].PID):
            
            # Buffs are sorted so that hamrful effects appear first and are 
            # sorted by remaining time.  Buffs that fade sooner appear first.            
            spellEffects = [( not effect.HARMFUL, effect.TIME, i, effect) for i, effect in enumerate(spellEffects)]
            spellEffects.sort()
            cinfo.SPELLEFFECTS = spellEffects = [effect[-1] for effect in spellEffects]   
            
            # Store post-sort information.
            self.lastPID = spellEffects[-1].PID
            self.buffCount = len(spellEffects)            

        # Iterate over spell effects.
        for effect in spellEffects:
            ctrl = self.effectCtrls[x]
            
            ICON = ""
            if effect.SRCMOBID == cinfo.MOBID:
                ICON = effect.ICONSRC
            if effect.DSTMOBID == cinfo.MOBID:
                ICON = effect.ICONDST
                
                
            if ICON:
                
                effect.TIME -= delta
                
                if effect.TIME < 12:
                    if effect.TIME < 0:
                        effect.TIME = 0
                    if math.sin(tm*4)>0:
                        ctrl.visible = False
                        x+=1
                        if x == 24:
                            break
                        continue
                    
                minutes,seconds = divmod(effect.TIME,60)
                tim = ""
                if minutes:
                    if seconds < 10:
                        tim = " - %i:0%i"%(int(minutes),int(seconds))
                    else:
                        tim = " - %i:%i"%(int(minutes),int(seconds))
                elif seconds:
                    if seconds < 10:
                        tim = " - :0%i"%(int(seconds))
                    else:
                        tim = " - :%i"%(int(seconds))
                        
                
                ctrl.toolTip = "XXX:"+effect.NAME+tim
                ctrl.visible = True
                
                    
                if "/" not in ICON:
                    if ICON.startswith("SPELLICON_"):
                        split = ICON.split("_")
                        
                        #gems are 10x10
                        page = int(split[1])-1
                        index=int(split[2])
                        
                        slot = page*36+index
                        page,slot = divmod(slot,100)
                        page += 1
                        
                        
                        u0=(float(slot%10)*24.0)/256.0
                        v0=(float(slot/10)*24.0)/256.0
                        u1=(24.0/256.0)
                        v1=(24.0/256.0)
                        
                        ctrl.setBitmapUV("~/data/ui/icons/gemicons0%i"%page,u0,v0,u1,v1)
                    else:
                        ctrl.setBitmap("~/data/ui/icons/%s"%ICON)
                    
                else:
                    ctrl.setBitmap("~/data/ui/%s"%ICON)
                    
                if effect.HARMFUL:
                    ctrl.setActive(False)
                else:
                    ctrl.setActive(True)
                x+=1
                if x == 24:
                    break
                    
        for y in xrange(x,24):
            ctrl = self.effectCtrls[y]
            ctrl.toolTip = ""
            ctrl.visible=False
            ctrl.setActive(False)


class CharBuffPane:
    def __init__(self, index):
        self.paneCtrl = TGEObject("BUFFWND_CHAR%i_PANE"%index)
        self.nameCtrl = TGEObject("BUFFWND_CHAR%i_NAME"%index)
        self.effectCtrls = dict((x,TGEObject("BUFFWND_CHAR%i_EFFECT%i"%(index,x))) for x in xrange(0,12))
            
        self.lastTime = time.time()
        self.lastPID = 0
        self.buffCount = 0

    def setCharInfo(self,cinfo):
        #spell effects
        
        self.nameCtrl.SetValue(cinfo.NAME)
        
        tm = time.time()
            
        delta = tm - self.lastTime
        delta *= 0.96
        self.lastTime = tm
        
        x = 0
        
        # Buffs only need sorted if:
        # - There is more than one buff.
        # - The count of buffs have changed (something was added or removed).
        # - The last PID (process ID) has changed (new buff).
        spellEffects = cinfo.SPELLEFFECTS
        if 1 < len(spellEffects) and (self.buffCount != len(spellEffects) or self.lastPID != spellEffects[-1].PID):
            
            # Buffs are sorted so that hamrful effects appear first and are 
            # sorted by remaining time.  Buffs that fade sooner appear first.            
            spellEffects = [( not effect.HARMFUL, effect.TIME, i, effect) for i, effect in enumerate(spellEffects)]
            spellEffects.sort()
            cinfo.SPELLEFFECTS = spellEffects = [effect[-1] for effect in spellEffects]   
            
            # Store post-sort information.
            self.lastPID = spellEffects[-1].PID
            self.buffCount = len(spellEffects)            

        # Iterate over spell effects.
        for effect in spellEffects:
            ctrl = self.effectCtrls[x]
            
            ICON = ""
            if effect.SRCMOBID == cinfo.MOBID:
                ICON = effect.ICONSRC
            if effect.DSTMOBID == cinfo.MOBID:
                ICON = effect.ICONDST
                
                
            if ICON:
                
                effect.TIME -= delta
                
                if effect.TIME < 12:
                    if effect.TIME < 0:
                        effect.TIME = 0
                    if math.sin(tm*4)>0:
                        ctrl.visible = False
                        x+=1
                        if x == 12:
                            break
                        continue
                    
                minutes,seconds = divmod(effect.TIME,60)
                tim = ""
                if minutes:
                    if seconds < 10:
                        tim = " - %i:0%i"%(int(minutes),int(seconds))
                    else:
                        tim = " - %i:%i"%(int(minutes),int(seconds))
                elif seconds:
                    if seconds < 10:
                        tim = " - :0%i"%(int(seconds))
                    else:
                        tim = " - :%i"%(int(seconds))
                        
                
                ctrl.toolTip = "XXX:"+effect.NAME+tim
                ctrl.visible = True
                
                    
                if "/" not in ICON:
                    if ICON.startswith("SPELLICON_"):
                        split = ICON.split("_")
                        
                        #gems are 10x10
                        page = int(split[1])-1
                        index=int(split[2])
                        
                        slot = page*36+index
                        page,slot = divmod(slot,100)
                        page += 1
                        
                        
                        u0=(float(slot%10)*24.0)/256.0
                        v0=(float(slot/10)*24.0)/256.0
                        u1=(24.0/256.0)
                        v1=(24.0/256.0)
                        
                        ctrl.setBitmapUV("~/data/ui/icons/gemicons0%i"%page,u0,v0,u1,v1)
                    else:
                        ctrl.setBitmap("~/data/ui/icons/%s"%ICON)
                    
                else:
                    ctrl.setBitmap("~/data/ui/%s"%ICON)
                    
                if effect.HARMFUL:
                    ctrl.setActive(False)
                else:
                    ctrl.setActive(True)
                x+=1
                if x == 12:
                    break
                    
        for y in xrange(x,12):
            ctrl = self.effectCtrls[y]
            ctrl.toolTip = ""
            ctrl.visible=False
            ctrl.setActive(False)


class BuffWnd:
    def __init__(self):
        
        self.window = TGEObject("BuffWnd_Window")

        self.partyPane = TGEObject("BUFFWND_PARTYPANE")
        self.singlePane = TGEObject("BUFFWND_SINGLE_PANE")
        
        self.sbp = SingleBuffPane()
        
        self.window.visible = False
        self.window.setActive(False)
            
        self.charInfos = None
        
        self.panes = [CharBuffPane(x) for x in xrange(0,6)]
        for pane in self.panes:
            pane.paneCtrl.visible = False
            
    def tick(self):
        if not self.charInfos:
            return
        
        #health, mana, stamina are on "fast update" from server
        #target, target health
        
        #keep this order independent so we can swap characters around on command windows
        
        from partyWnd import PARTYWND
        
        #MoMWndProfile
        if len(self.charInfos) > 1:
            for index,cinfo in self.charInfos.iteritems():
                pane = self.panes[index]
                if index == PARTYWND.curIndex:
                    pane.paneCtrl.setProfile("MoMSelectedWndProfile")
                else:
                    pane.paneCtrl.setProfile("MoMWndProfile")
    
                pane.setCharInfo(cinfo)
        else:
            self.sbp.setCharInfo(self.charInfos[0])
        
    def setCharInfos(self,cinfos):
        
        for x in xrange(0,6):
            self.panes[x].paneCtrl.visible = False
            
        
        self.partyPane.visible = False
        self.singlePane.visible = False
        
        self.charInfos = cinfos
        
        num = len(cinfos)
        
        self.window.visible = True
        
        if num == 1:
            self.singlePane.visible = True            
            extent= '128 230'
        else:
            self.partyPane.visible = True
            extent = '121 %i'%int(121 + 92*(num-1))
            
            for x in xrange(0,num):
                self.panes[x].paneCtrl.visible = True
            
        self.window.extent = extent
        self.window.setActive(True)

def PyExec():
    global BUFFWND
    BUFFWND = BuffWnd()
