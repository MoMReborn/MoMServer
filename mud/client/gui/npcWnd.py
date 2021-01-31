# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from twisted.spread import pb
from twisted.internet import reactor
from mud.world.defines import *
from mud.world.core import GenMoneyText
from mud.client.playermind import GetMoMClientDBConnection
import math,traceback

NPCWND = None

TEXT_HEADER = """<font:Arial Bold:14><just:center><shadow:1:1><shadowcolor:000000>"""

class InteractPane(pb.Root):
    def __init__(self):
        self.pane = TGEObject("NPCWND_INTERACTPANE")
        self.interText = TGEObject("NPCWND_INTERACTTEXT")
        self.interChoices = TGEObject("NPCWND_CHOICELIST")
        self.interChoiceButton = TGEObject("NPCWND_CHOOSEBUTTON")
        self.interScroll = TGEObject("NPCWND_INTERACTSCROLL")
        self.text = ""
        
        self.interactButton = TGEObject("NPCWND_INTERACTBUTTON")
        
    def remote_set(self,text,choices,journalEntryID=None):
        self.setInteraction(text,choices)
        if journalEntryID:
            from journalWnd import JOURNALWND
            con = GetMoMClientDBConnection()
            journalTopic,journalEntry = con.execute("SELECT topic,entry FROM journal_entry WHERE id = %i LIMIT 1;"%journalEntryID).fetchone()
            JOURNALWND.addEntry(journalTopic,journalEntry,text)

    def setInteraction(self,text,choices):
        self.text+= text
        if len(self.text)>3000:
            self.text = self.text[256:] #shave off 256 characters
            
        eval = 'NPCWND_INTERACTTEXT.setText("<shadowcolor:000000><shadow:1:1>%s");'%self.text
        TGEEval(eval)
        
        if not int(self.interScroll.isMouseLocked()):
            self.interScroll.scrollToBottom()
            
        self.setChoices(choices)
        
        if len(choices):
            self.interChoiceButton.setActive(True)
        
    def setChoices(self,choices):
        self.interChoices.setVisible(False)
                
        self.interChoices.clear()
        
        for i,choice in enumerate(choices):
            self.interChoices.addRow(i,"%s"%choice)
        
        self.interChoices.setSelectedRow(0)
        self.interChoices.scrollVisible(0)
        self.interChoices.setActive(True)
        self.interChoices.setVisible(True)
        
    def onChoice(self):
        index = int(self.interChoices.getSelectedId())
        NPCWND.perspective.callRemote("PlayerAvatar","onInteractionChoice",index,self)        
        self.interChoiceButton.setActive(False)
        
    def enable(self):
        self.enabled = True
        self.interactButton.setActive(True)
        self.interactButton.visible = True
        
        
    def disable(self):
        self.enabled = False
        self.pane.visible = False
        self.interactButton.setActive(False)
        self.interactButton.visible = False
        
    def tick(self):
        pass



class TradePane:
    def __init__(self):
        self.pane           = TGEObject("NPCWND_TRADEPANE")
        self.itemPic        = TGEObject("NPCWND_TRADEITEM_PIC")
        self.itemName       = TGEObject("NPCWND_TRADEITEM_NAME")
        self.itemFlags      = TGEObject("NPCWND_TRADEITEM_FLAGS")
        self.itemInfoScroll = TGEObject("NPCWND_TRADEITEM_SCROLL")
        self.itemInfoText   = TGEObject("NPCWND_TRADEITEM_INFOTEXT")
        self.priceText      = TGEObject("NPCWND_PRICETEXT")
        self.itemListScroll = TGEObject("NPCWND_TRADELIST_SCROLL")
        self.itemList       = TGEObject("NPCWND_TRADELIST")
        self.tradeButton    = TGEObject("NPCWND_TRADEBUTTON")
        self.buyButton      = TGEObject("NPCWND_BUYBUTTON")
        self.sellButton     = TGEObject("NPCWND_SELLBUTTON")
        
        self.lastInfoText = ""
        self.markup = 1
        self.stock = []
    
    
    def enable(self):
        self.enabled = True
        self.tradeButton.setActive(True)
        self.tradeButton.visible = True
    
    def disable(self):
        self.enabled = False
        self.pane.visible = False
        self.tradeButton.setActive(False)
        self.tradeButton.visible = False
    
    
    def setStock(self,stock,markup):
        self.stock = stock
        self.markup = markup
        self.refreshList()
    
    def refreshList(self):
        from partyWnd import PARTYWND
        cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
        stock = self.stock
        markup = self.markup
        self.itemList.setVisible(False)
        self.itemList.clear()
        
        if len(stock):
            for i,ghost in enumerate(stock.iterkeys()):
                color = 2 #green
                if not ghost.isUseable(cinfo):
                    color = 3
                
                n = ghost.NAME
                
                level = 1000
                if n.startswith("Scroll of") and ghost.SPELLINFO:
                    n = n[9:]
                    for cl,lev in ghost.SPELLINFO.CLASSES:
                        if lev < level:
                            level = lev
                
                for cl,lev in ghost.CLASSES:
                    if lev < level:
                        level = lev
                
                if level == 1000:
                    level = ghost.LEVEL
                
                lev = ""
                if level != 1000 and (level != 1 or ghost.SPELLINFO):
                    lev = str(level)
                
                eval = r'NPCWND_TRADELIST.addRow(%i,"%s" TAB "\c%s%s");'%(i,lev,color,n)
                TGEEval(eval)
            
            self.itemList.sortNumerical(0)
            self.itemList.setSelectedRow(0)
            self.itemList.scrollVisible(0)
            self.itemList.setActive(True)
            self.itemList.setVisible(True)
        
        self.tick()
    
    
    def setItemInfo(self):
        buying = False
        ghost = None
        from itemInfoWnd import ITEMINFOWND
        if ITEMINFOWND.isItem:
            ghost = ITEMINFOWND.ghost
        if not ghost:
            buying = True
            ghost = self.getSelectionItem()
        
        #generate worth
        if ghost:
            if buying:
                mod = self.markup
            else:
                mod = self.markup*0.1
            
            if buying:
                worth = GenMoneyText(ghost.getWorth(mod))
                if len(worth):
                    self.priceText.setText("I'll sell this to you for %s."%worth)
                else:
                    self.priceText.setText("I'll give this to you for free.")
            else:
                worth = GenMoneyText(ghost.getWorth(mod,True))
                if len(worth):
                    self.priceText.setText("I'll give you %s for this item."%worth)
                else:
                    self.priceText.setText("This item doesn't have any worth for me.")
            
            text = ' '.join(r'\cp\c2%s\co '%ftext for f,ftext in RPG_ITEM_FLAG_TEXT.iteritems() if (f&ghost.FLAGS))
            
            eval = 'NPCWND_TRADEITEM_FLAGS.setText("%s%s");'%(TEXT_HEADER,text)
            TGEEval(eval)
            
            text = ghost.text
            if ghost.SPELLINFO:
                text += r'\n\n%s'%ghost.SPELLINFO.text
            itext = TEXT_HEADER + text
            if itext != self.lastInfoText:
                self.lastInfoText = itext
                eval = 'NPCWND_TRADEITEM_INFOTEXT.setText("%s");'%(itext)
                TGEEval(eval)
            
            self.itemName.setText(TEXT_HEADER+ghost.NAME)
            self.itemPic.setBitmap("~/data/ui/items/%s/0_0_0"%ghost.BITMAP)
        
        else:
            self.itemPic.SetBitmap("")
            self.priceText.setText("")
            self.itemName.setText("")
            self.itemFlags.setText("")
            self.itemInfoText.setText("")
    
    
    def getSelectionItem(self):
        if not len(self.stock):
            return None  # nothing in stock, which is valid
        
        index = int(self.itemList.getMouseOverId())
        return self.stock.keys()[index]
    
    
    def tick(self):
        from partyWnd import PARTYWND
        if PARTYWND.mind.cursorItem:
            self.buyButton.setActive(False)
            self.sellButton.setActive(True)
        else:
            if not len(self.stock):
                self.buyButton.setActive(False)
            else:
                self.buyButton.setActive(True)
            self.sellButton.setActive(False)
        
        #setup info
        self.setItemInfo()


#handed to server, probably should have done this in general?
class NPCWnd:
    def __init__(self):
        self.open = False
        self.interactPane = InteractPane()
        self.tradePane = TradePane()
        self.bankPane = BankPane()
        self.title = None
        
        self.panes = [self.interactPane,self.tradePane]
        
    def openWindow(self,perspective,title=None,banker=False):
        if not banker:
            self.bankPane.pane.visible = False
            self.bankPane.bankButton.visible = False
        else:
            self.bankPane.pane.visible = True
            self.bankPane.bankButton.visible = True
        
        self.title=title
        self.perspective = perspective
        if banker:
            self.bankPane.bankButton.performClick()
            
        elif self.interactPane.enabled:
            self.interactPane.interactButton.performClick()
        elif self.tradePane.enabled:
            self.tradePane.tradeButton.performClick()
        else:
            traceback.print_stack()
            print "AssertionError: no interaction!"
            return
            
        
        TGEEval("canvas.pushDialog(NPCWND);")
        self.open = True
        
    def tick(self):
        if not self.open:
            return
        for p in self.panes:
            if p.enabled:
                p.tick()
    
    def closeWindow(self):
        TGEEval("canvas.popDialog(NPCWND);")
        self.perspective = None
        self.open = False
    
    def setStock(self,isVendor,stock,markup):
        if isVendor:
            if not markup:
                traceback.print_stack()
                print "AssertionError: vendor with no markup defined!"
                return
        
        if not isVendor:
            self.tradePane.disable()
            return
        self.tradePane.enable()
        self.tradePane.setStock(stock,markup)
    
    def refreshList(self):
        self.tradePane.refreshList()
    
    
    def setInitialInteraction(self, dialogLine, choices, title=None):
        self.title = title
        
        if dialogLine == None:
            self.interactPane.disable()
            return
        
        con = GetMoMClientDBConnection()
        
        try:
            text,journalEntryID = con.execute("SELECT text,journal_entry_id FROM dialog_line WHERE id=? LIMIT 1;",(dialogLine,)).fetchone()
        except:
            text = None
            journalEntryID = None
        
        if text:
            self.interactPane.text = ""
            self.interactPane.enable()
            self.interactPane.setInteraction(text,choices)
        else:
            self.interactPane.disable()
        
        if journalEntryID:
            from journalWnd import JOURNALWND
            journalTopic,journalEntry = con.execute("SELECT topic,entry FROM journal_entry WHERE id = %i LIMIT 1;"%journalEntryID).fetchone()
            JOURNALWND.addEntry(journalTopic,journalEntry,text)


def PyOnNPCWndChoose():
    NPCWND.interactPane.onChoice()

def PyOnCloseNPCWnd():
    TGEEval("canvas.popDialog(NPCWND);")
    NPCWND.perspective.callRemote("PlayerAvatar","endInteraction")


def PyOnNPCTradeButton():
    if not NPCWND.tradePane.enabled:
        traceback.print_stack()
        print "AssertionError: npc trade pane not enabled!"
        return
    for p in NPCWND.panes:
        p.pane.visible = False
    
    NPCWND.tradePane.pane.visible = True

def PyOnNPCInteractButton():
    if not NPCWND.interactPane.enabled:
        traceback.print_stack()
        print "AssertionError: npc interact pane not enabled!"
        return
    for p in NPCWND.panes:
        p.pane.visible = False
    
    NPCWND.interactPane.pane.visible = True


def PyOnNPCSellButton():
    from partyWnd import PARTYWND
    cursorItem = PARTYWND.mind.cursorItem
    if not cursorItem:
        return
    
    NPCWND.perspective.callRemote("PlayerAvatar","sellItem",PARTYWND.curIndex,RPG_SLOT_CURSOR)

def PyOnNPCBuyButton():
    from partyWnd import PARTYWND
    cursorItem = PARTYWND.mind.cursorItem
    if cursorItem:
        return
    
    ghost = NPCWND.tradePane.getSelectionItem()
    if not ghost:
        return
    
    index = NPCWND.tradePane.stock[ghost]
    NPCWND.perspective.callRemote("PlayerAvatar","buyItem",PARTYWND.curIndex,index)

# shift-double-click for quick sell
def PyOnInvSlotShift(args):
    from partyWnd import PARTYWND
    
    if not NPCWND.perspective:
        return
    
    slot = int(args[1])
    if RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN:
        page = PARTYWND.invPane.page
        slot += page*30
    
    try:
        item = PARTYWND.charInfos[PARTYWND.curIndex].ITEMS[slot]
    except:
        return
    NPCWND.perspective.callRemote("PlayerAvatar","sellItem",PARTYWND.curIndex,item.SLOT)


#The freaking bank
#NPCWND_BANKBUTTON
#NPCWND_BANKPANE
#NPCWnd_InvItemBitmap
#NPCWND_INVITEMNAME
#BANK72_BUTTON
#Py::OnBankSlot(72);


class BankPane:
    def __init__(self):
        self.pane = TGEObject("NPCWND_BANKPANE")
        self.bankButton = TGEObject("NPCWND_BANKBUTTON")
        self.bankButtons = dict((x,TGEObject("BANK%i_BUTTON"%(x-RPG_SLOT_BANK_BEGIN))) for x in xrange(RPG_SLOT_BANK_BEGIN,RPG_SLOT_BANK_END))
        self.bank = {}
    
    def set(self,bank):
        self.bank = bank
        for slot in xrange(RPG_SLOT_BANK_BEGIN,RPG_SLOT_BANK_END):
            butt = self.bankButtons[slot]
            butt.number = -1
            
            if not bank.has_key(slot): #only clear the ones we need to so we don't have to relock texture!
                butt.SetBitmap("")
        
        for slot,ghost in bank.iteritems():
            butt = self.bankButtons[slot]
            butt.setBitmap("~/data/ui/items/%s/0_0_0"%ghost.BITMAP)
            if ghost.STACKMAX > 1:
                butt.number = ghost.STACKCOUNT

def PyOnNPCBankButton():
    for p in NPCWND.panes:
        p.pane.visible = False
    NPCWND.bankPane.pane.visible = True

def PyOnBankSlot(args):
    from mud.client.playermind import PLAYERMIND
    slot = int(args[1])
    
    if not PLAYERMIND.cursorItem and not NPCWND.bankPane.bank.get(slot+RPG_SLOT_BANK_BEGIN,None):
        return
    
    PLAYERMIND.onBankSlot(slot+RPG_SLOT_BANK_BEGIN)


def PyExec():
    global NPCWND
    NPCWND = NPCWnd()
    
    TGEExport(PyOnNPCWndChoose,"Py","OnNPCWndChoose","desc",1,1)
    TGEExport(PyOnCloseNPCWnd,"Py","OnCloseNPCWnd","desc",1,1)
    
    TGEExport(PyOnNPCTradeButton,"Py","OnNPCTradeButton","desc",1,1)
    TGEExport(PyOnNPCInteractButton,"Py","OnNPCInteractButton","desc",1,1)
    TGEExport(PyOnNPCBankButton,"Py","OnNPCBankButton","desc",1,1)
    
    TGEExport(PyOnNPCSellButton,"Py","OnNPCWndSellButton","desc",1,1)
    TGEExport(PyOnNPCBuyButton,"Py","OnNPCWndBuyButton","desc",1,1)
    
    TGEExport(PyOnInvSlotShift,"Py","OnInvSlotShift","desc",2,2)
    
    TGEExport(PyOnBankSlot,"Py","OnBankSlot","desc",2,2)
    
    