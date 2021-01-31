# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.gamesettings import *

CHARPORTRAITWND = None
CHOOSEPORTRAITCALLBACK = None

class CharPortraitWnd:
    def __init__(self):
        self.portraitPic = TGEObject("charportraitwnd_pic")
        
        self.nextButton = TGEObject("CharPortraitWnd_NextButton")
        self.prevButton = TGEObject("CharPortraitWnd_PrevButton")
        
        self.pbuttons = dict((x,TGEObject("charportraitwnd_pbutton%i"%x)) for x in xrange(0,18))
        
        self.pics = []
        
        import os
        dir = os.listdir("./%s/data/ui/charportraits"%GAMEROOT)
        
        for f in dir:
            if f.find(".png") != -1 or f.find(".jpg") != -1:
                if f.find(".alpha.") != -1:
                    continue
                base = os.path.basename(f)
                base = os.path.splitext(base)[0]
                
                if base not in self.pics:
                    self.pics.append(base)
        
        self.chosen = 0
        self.curPage = 0            
        self.setButtonPage(-1)
        
                    
                    
    #-1 clears, which should be done as it frees up the bitmaps
    def setButtonPage(self,index):
        if index == -1:
            for butt in self.pbuttons.itervalues():
                butt.setBitmap("")
            self.portraitPic.setBitmap("")
            
            self.nextButton.visible = False
            self.prevButton.visible = False
            return
            
        self.curPage = index
        
        pindex = index*18
        
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
            self.pbuttons[x].visible = True
            self.pbuttons[x].setBitmap("~/data/ui/charportraits/%s"%self.pics[pindex+x])
            
        
                    
        
def SetChoosePortraitCallback(cb):
    global CHOOSEPORTRAITCALLBACK
    CHOOSEPORTRAITCALLBACK = cb
    
    CHARPORTRAITWND.chosen = 0
    
    if not cb:
        #clear
        CHARPORTRAITWND.setButtonPage(-1)        
        TGEEval("canvas.popDialog(CharPortraitWnd);")
    else:
        CHARPORTRAITWND.chosen = 0
        CHARPORTRAITWND.portraitPic.setBitmap("~/data/ui/charportraits/%s"%CHARPORTRAITWND.pics[0])
        CHARPORTRAITWND.setButtonPage(0)
        
        
    
def OnChoosePortrait():
    global CHOOSEPORTRAITCALLBACK
    if CHOOSEPORTRAITCALLBACK:
        CHOOSEPORTRAITCALLBACK(CHARPORTRAITWND.pics[CHARPORTRAITWND.chosen])
        
    SetChoosePortraitCallback(None) #also clears


def OnPortraitButton(args):
    slot = int(args[1])
    slot = slot + CHARPORTRAITWND.curPage*18
    CHARPORTRAITWND.chosen = slot
    CHARPORTRAITWND.portraitPic.setBitmap("~/data/ui/charportraits/%s"%CHARPORTRAITWND.pics[slot])


def OnPrevPortraits():
    CHARPORTRAITWND.setButtonPage(CHARPORTRAITWND.curPage-1)
    
def OnNextPortraits():
    CHARPORTRAITWND.setButtonPage(CHARPORTRAITWND.curPage+1)
    
def OnCloseCharPortraitWnd():
    
    global CHOOSEPORTRAITCALLBACK
    if CHOOSEPORTRAITCALLBACK:
        CHOOSEPORTRAITCALLBACK(None)

    SetChoosePortraitCallback(None) #also clears
    


def PyExec():
    global CHARPORTRAITWND
    CHARPORTRAITWND = CharPortraitWnd()
    
    TGEExport(OnChoosePortrait,"Py","OnChoosePortrait","desc",1,1)
    TGEExport(OnPortraitButton,"Py","OnPortraitButton","desc",2,2)
    
    TGEExport(OnPrevPortraits,"Py","OnPrevPortraits","desc",1,1)
    TGEExport(OnNextPortraits,"Py","OnNextPortraits","desc",1,1)
    
    TGEExport(OnCloseCharPortraitWnd,"Py","OnCloseCharPortraitWnd","desc",1,1)
    
    
    
    
    
    
    
    
    
    
    
    