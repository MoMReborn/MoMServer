# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from math import floor
from mud.world.defines import *
from mud.world.core import CollapseMoney
from twisted.internet import reactor


TRADEWND = None

class TradeWnd:
    def __init__(self):
                
        self.p0Tin = TGEObject("TRADE_P0_TIN")
        self.p0Copper = TGEObject("TRADE_P0_COPPER")
        self.p0Silver = TGEObject("TRADE_P0_SILVER")
        self.p0Gold = TGEObject("TRADE_P0_GOLD")
        self.p0Platinum = TGEObject("TRADE_P0_PLATINUM")
        
        self.p1Tin = TGEObject("TRADE_P1_TIN")
        self.p1Copper = TGEObject("TRADE_P1_COPPER")
        self.p1Silver = TGEObject("TRADE_P1_SILVER")
        self.p1Gold = TGEObject("TRADE_P1_GOLD")
        self.p1Platinum = TGEObject("TRADE_P1_PLATINUM")
        
        self.p0Items = {}
        self.p1Items = {}
        for x in xrange(0,12):
            self.p0Items[x]=TGEObject("TRADE_P0_BUTTON%i"%x)
            self.p1Items[x]=TGEObject("TRADE_P1_BUTTON%i"%x)
            
        self.tradeInfo = None
        
        
    def setFromTradeInfo(self,tradeInfo):
        
        from mud.client.playermind import PLAYERMIND
        
        if PLAYERMIND.rootInfo.PLAYERNAME == tradeInfo.P0NAME:
            p0name = tradeInfo.P0NAME
            p1name = tradeInfo.P1NAME

            c0name = tradeInfo.C0NAME
            c1name = tradeInfo.C1NAME
            
            p0Tin,p0Copper,p0Silver,p0Gold,p0Platinum = CollapseMoney(tradeInfo.P0TIN)
            p1Tin,p1Copper,p1Silver,p1Gold,p1Platinum = CollapseMoney(tradeInfo.P1TIN)
            
            p0Items = tradeInfo.P0ITEMS
            p1Items = tradeInfo.P1ITEMS
            
            p0Accepted = tradeInfo.P0ACCEPTED
            p1Accepted = tradeInfo.P1ACCEPTED
        else:
            #flip
            p1name = tradeInfo.P0NAME
            p0name = tradeInfo.P1NAME
            c1name = tradeInfo.C0NAME
            c0name = tradeInfo.C1NAME
            
            p1Tin,p1Copper,p1Silver,p1Gold,p1Platinum = CollapseMoney(tradeInfo.P0TIN)
            p0Tin,p0Copper,p0Silver,p0Gold,p0Platinum = CollapseMoney(tradeInfo.P1TIN)
            
            p1Items = tradeInfo.P0ITEMS
            p0Items = tradeInfo.P1ITEMS
            
            p1Accepted = tradeInfo.P0ACCEPTED
            p0Accepted = tradeInfo.P1ACCEPTED
            
            
        if p0Accepted:
            eval = r'TRADE_P0_NAME.setText("\c2%s");'%c0name
        else:
            eval = r'TRADE_P0_NAME.setText("\c1%s");'%c0name
            
        TGEEval(eval)
            
        if p1Accepted:
            eval = r'TRADE_P1_NAME.setText("\c2%s");'%c1name
        else:
            eval = r'TRADE_P1_NAME.setText("\c1%s");'%c1name
            
        TGEEval(eval)

        self.p0Tin.setText(str(p0Tin))
        self.p0Copper.setText(str(p0Copper))
        self.p0Gold.setText(str(p0Gold))
        self.p0Silver.setText(str(p0Silver))
        self.p0Platinum.setText(str(p0Platinum))
        
        if p0Accepted or p1Accepted:
            self.p0Tin.setActive(False)
            self.p0Copper.setActive(False)
            self.p0Gold.setActive(False)
            self.p0Silver.setActive(False)
            self.p0Platinum.setActive(False)
        else:
            self.p0Tin.setActive(True)
            self.p0Copper.setActive(True)
            self.p0Gold.setActive(True)
            self.p0Silver.setActive(True)
            self.p0Platinum.setActive(True)
            
            

        
        self.p1Tin.setText(str(p1Tin))
        self.p1Copper.setText(str(p1Copper))
        self.p1Gold.setText(str(p1Gold))
        self.p1Silver.setText(str(p1Silver))
        self.p1Platinum.setText(str(p1Platinum))
        
        for slot,butt in self.p0Items.iteritems():
            if not p0Items.has_key(slot): #only clear the ones we need to so we don't have to relock texture!
                butt.SetBitmap("")
                butt.number = -1
            
        for slot,butt in self.p1Items.iteritems():
            if not p1Items.has_key(slot): #only clear the ones we need to so we don't have to relock texture!
                butt.SetBitmap("")
                butt.number = -1
            
        for slot,ghost in p0Items.iteritems():
            self.p0Items[slot].setBitmap("~/data/ui/items/"+ghost.BITMAP+"/0_0_0") 
            if ghost.STACKMAX > 1:
                self.p0Items[slot].number = ghost.STACKCOUNT
            else:
                self.p0Items[slot].number = -1
                
                

        for slot,ghost in p1Items.iteritems():
            self.p1Items[slot].setBitmap("~/data/ui/items/"+ghost.BITMAP+"/0_0_0") 
            if ghost.STACKMAX > 1:
                self.p1Items[slot].number = ghost.STACKCOUNT
            else:
                self.p1Items[slot].number = -1
    
    def open(self,tradeInfo):
        self.tradeInfo = tradeInfo
        self.setFromTradeInfo(tradeInfo)
        TGEEval("canvas.pushDialog(TradeWnd);")
        
    def close(self):
        TGEEval("canvas.popDialog(TradeWnd);")
        self.tradeInfo = None
        
def PyOnTradeItemButton(args):
    slot = int (args[2])
    from partyWnd import PARTYWND
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","onPlayerTradeSlot",slot)
    
def PyOnTradeCancel():
    from partyWnd import PARTYWND
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","onPlayerTradeCancel")
    
def PyOnTradeAccept():
    from partyWnd import PARTYWND
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","onPlayerTradeAccept")

def GotMoneyResponse(money):
    money = CollapseMoney(money)
    TRADEWND.p0Tin.setText(str(money[0]))
    TRADEWND.p0Copper.setText(str(money[1]))
    TRADEWND.p0Silver.setText(str(money[2]))
    TRADEWND.p0Gold.setText(str(money[3]))
    TRADEWND.p0Platinum.setText(str(money[4]))

def PyValidateTradeMoney():
    from partyWnd import PARTYWND
    rootInfo = PARTYWND.mind.rootInfo
    
    try:
        t = long(TRADEWND.p0Tin.getValue())
    except:
        t = 0L
    try:
        c = long(TRADEWND.p0Copper.getValue())
    except:
        c = 0L
    
    try:
        s = long(TRADEWND.p0Silver.getValue())
    except:
        s = 0L
    
    try:
        g = long(TRADEWND.p0Gold.getValue())
    except:
        g = 0L
    
    try:
        p = long(TRADEWND.p0Platinum.getValue())
    except:
        p = 0L
        
    if t < 0:
        t = 0
    if c < 0:
        c = 0
    if s < 0:
        s = 0
    if g < 0:
        g = 0
    if p < 0:
        p = 0
    
    #this is how much we are typing in
    #convert to tin
    itin = t
    itin += c*100L
    itin += s*10000L
    itin += g*1000000L
    itin += p*100000000L
    
    if itin <= rootInfo.TIN:
        #this is fine send it on up for further validation
        d = PARTYWND.mind.perspective.callRemote("PlayerAvatar","onPlayerTradeMoney",itin)
        if d:
            d.addCallback(GotMoneyResponse)
    else:
        #we have entered in more than we have... we'll clear in this case for now
        d = PARTYWND.mind.perspective.callRemote("PlayerAvatar","onPlayerTradeMoney",0L)
        if d:
            d.addCallback(GotMoneyResponse)
        TRADEWND.p0Tin.setText("0")
        TRADEWND.p0Copper.setText("0")
        TRADEWND.p0Silver.setText("0")
        TRADEWND.p0Gold.setText("0")
        TRADEWND.p0Platinum.setText("0")
    
    
def PyExec():
    global TRADEWND
    TRADEWND = TradeWnd()
    TGEExport(PyOnTradeItemButton,"Py","OnTradeItemButton","desc",3,3)        
    TGEExport(PyOnTradeCancel,"Py","OnTradeCancel","desc",1,1)        
    TGEExport(PyOnTradeAccept,"Py","OnTradeAccept","desc",1,1)        
    TGEExport(PyValidateTradeMoney,"Py","ValidateTradeMoney","desc",1,1)        
    
    