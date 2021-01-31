# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



from tgenative import *
from mud.tgepython.console import TGEExport

BUTTONS = None

def SetFromCharacterInfos(cinfos):
    
    canvas = TGEObject("Canvas")
    sizeX,sizeY = canvas.extent.split(' ')
    sizeX = int(sizeX)
    sizeY = int(sizeY)
    
    num = len(cinfos)

    #buttons are 32, 32
    #8 between buttons    
    pixels = 40*num
    
    startX = sizeX/2-pixels/2
    
    for x in xrange(0,6):
        BUTTONS[x].position = "%i 12"%startX
        startX+=40

    
    if num == 1:
        num = 0 #disable all if only one character
    for x in xrange(0,num):
        BUTTONS[x].visible = True
        BUTTONS[x].setActive("true")
        
    BUTTONS[0].performClick()
        
    

def OnCharButton(args):
    index = int(args[1])
    from partyWnd import PARTYWND
    PARTYWND.setFromCharacterInfo(index)
    
    


def PyExec():
    global BUTTONS
    BUTTONS = []
    for x in xrange(0,6):
        BUTTONS.append(TGEObject("PartyWnd_CharButton%i"%x))
        BUTTONS[x].visible = False
        BUTTONS[x].setActive("false")

    TGEExport(OnCharButton,"Py","OnCharButton","desc",2,2)
    