# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.gamesettings import *


ChooseIconWnd = None
CHOOSEICONCALLBACK = None



class ChooseIconWndClass:
    def __init__(self):
        #yuck
        global ChooseIconWnd
        ChooseIconWnd = self
        
        self.iconPic = TGEObject("ChooseIconWnd_pic")
        
        self.nextButton = TGEObject("ChooseIconWnd_NextButton")
        self.prevButton = TGEObject("ChooseIconWnd_PrevButton")
        
        self.pbuttons = dict((x,TGEObject("ChooseIconWnd_pbutton%i"%x)) for x in xrange(0,18))
        
        import os
        dir = os.listdir("./%s/data/ui/icons"%GAMEROOT)
        
        # do spell icons
        self.pics = ["SPELLICON_%i_%i"%(x,y) for x in xrange(1,7) for y in xrange(0,36)]
        self.pics.append("SPELLICON_7_0")
        
        skip = ("gemicons0","spells0")
        for f in dir:
            if f.endswith(".png") or f.endswith(".jpg"):
                if f.find(".alpha.") != -1:
                    continue
                
                include = True
                for s in skip:
                    if f.find(s) != -1:
                        include = False
                
                base = os.path.basename(f)
                base = os.path.splitext(base)[0]
                
                if base not in self.pics and include:
                    self.pics.append(base)
        
        self.chosen = 0
        self.curPage = 0
        self.setButtonPage(-1)
    
    
    #-1 clears, which should be done as it frees up the bitmaps
    def setButtonPage(self,index):
        if index == -1:
            for butt in self.pbuttons.itervalues():
                butt.setBitmap("")
            self.iconPic.setBitmap("")
            
            self.nextButton.visible = False
            self.prevButton.visible = False
            return
        
        self.curPage = index
        
        pindex = index * 18
        
        for butt in self.pbuttons.itervalues():
            butt.visible = False
        
        num = 18
        if pindex + 18 >= len(self.pics):
            num = len(self.pics) - pindex
            self.nextButton.visible = False
        else:
            self.nextButton.visible = True
        
        if index == 0:
            self.prevButton.visible = False
        else:
            self.prevButton.visible = True
        
        for x in xrange(0,num):
            button = self.pbuttons[x]
            button.visible = True
            
            icon = self.pics[pindex + x]
            if icon.startswith("SPELLICON_"):
                split = icon.split("_")
                index = int(split[2])
                u0 = (float(index % 6) * 40.0) / 256.0
                v0 = (float(index / 6) * 40.0) / 256.0
                u1 = 40.0 / 256.0
                v1 = 40.0 / 256.0
                
                button.setBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
            else:
                button.setBitmap("~/data/ui/icons/%s"%icon)



def SetChooseIconCallback(cb):
    global CHOOSEICONCALLBACK
    CHOOSEICONCALLBACK = cb
    
    ChooseIconWnd.chosen = 0
    ChooseIconWnd.setButtonPage(0)
    
    if not cb:
        #clear
        ChooseIconWnd.setButtonPage(-1)
        TGEEval("canvas.popDialog(ChooseIconWnd);")
    else:
        ChooseIconWnd.chosen = 0
        icon = ChooseIconWnd.pics[0]
        
        if icon.startswith("SPELLICON_"):
            split = icon.split("_")
            index = int(split[2])
            u0 = (float(index % 6) * 40.0) / 256.0
            v0 = (float(index / 6) * 40.0) / 256.0
            u1 = 40.0 / 256.0
            v1 = 40.0 / 256.0
            
            ChooseIconWnd.iconPic.setBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
        else:
            ChooseIconWnd.iconPic.setBitmap("~/data/ui/icons/%s"%icon)


def OnChooseIcon():
    global CHOOSEICONCALLBACK
    if CHOOSEICONCALLBACK:
        CHOOSEICONCALLBACK(ChooseIconWnd.pics[ChooseIconWnd.chosen])
    
    SetChooseIconCallback(None) #also clears


def OnClearIcon():
    global CHOOSEICONCALLBACK
    if CHOOSEICONCALLBACK:
        CHOOSEICONCALLBACK("")
    
    SetChooseIconCallback(None) #also clears


def OnIconButton(args):
    slot = int(args[1])
    slot = slot + ChooseIconWnd.curPage * 18
    ChooseIconWnd.chosen = slot
    icon = ChooseIconWnd.pics[slot]
    if icon.startswith("SPELLICON_"):
        split = icon.split("_")
        index = int(split[2])
        u0 = (float(index % 6) * 40.0) / 256.0
        v0 = (float(index / 6) * 40.0) / 256.0
        u1 = 40.0 / 256.0
        v1 = 40.0 / 256.0
        
        ChooseIconWnd.iconPic.setBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
    else:
        ChooseIconWnd.iconPic.setBitmap("~/data/ui/icons/%s"%icon)


def OnPrevIcons():
    ChooseIconWnd.setButtonPage(ChooseIconWnd.curPage - 1)


def OnNextIcons():
    ChooseIconWnd.setButtonPage(ChooseIconWnd.curPage + 1)


def OnCloseChooseIconWnd():
    global CHOOSEICONCALLBACK
    if CHOOSEICONCALLBACK:
        CHOOSEICONCALLBACK(None)
    
    SetChooseIconCallback(None) #also clears



def PyExec():
    TGEExport(OnClearIcon,"Py","OnClearIcon","desc",1,1)
    TGEExport(OnChooseIcon,"Py","OnChooseIcon","desc",1,1)
    TGEExport(OnIconButton,"Py","OnIconButton","desc",2,2)
    
    TGEExport(OnPrevIcons,"Py","OnPrevIcons","desc",1,1)
    TGEExport(OnNextIcons,"Py","OnNextIcons","desc",1,1)
    
    TGEExport(OnCloseChooseIconWnd,"Py","OnCloseChooseIconWnd","desc",1,1)
    
    
    ChooseIconWndClass()

