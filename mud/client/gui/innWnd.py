# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from math import floor
from mud.world.defines import *
from twisted.internet import reactor
from twisted.spread import pb



INNWND = None



class InnWnd(pb.Root):
    def __init__(self):
        self.partyListCtrl = TGEObject("INNPARTY_SCROLLLIST")
        self.charListCtrl = TGEObject("INNCHARS_SCROLLLIST")
        self.inn = None
        self.partyList = []
        self.charList = []
    
    
    def remote_set(self, cList, pList):
        self.partyList = pList
        self.charList = cList
        
        #PARTY LIST
        tc = self.partyListCtrl
        tc.setVisible(False)
        tc.clear()
        for i,ci in enumerate(pList):
            name = ci.name
            klass = ci.klasses[0]
            level = ci.levels[0]
            status = ci.status
            
            TGEEval(r'INNPARTY_SCROLLLIST.addRow(%i,"%s" TAB "%s (%i)" TAB "%s");'%(i,name,klass,level,status))
        
        tc.setSelectedRow(0)
        tc.scrollVisible(0)
        tc.setActive(True)
        tc.setVisible(True)
        
        #CHAR LIST
        tc = self.charListCtrl
        tc.setVisible(False)
        tc.clear()
        for i,ci in enumerate(cList):
            name = ci.name
            klass = ci.klasses[0]
            level = ci.levels[0]
            status = ci.status
            
            TGEEval(r'INNCHARS_SCROLLLIST.addRow(%i,"%s" TAB "%s (%i)" TAB "%s");'%(i,name,klass,level,status))
        
        tc.sort(0)
        tc.setSelectedRow(0)
        tc.scrollVisible(0)
        tc.setActive(True)
        tc.setVisible(True)
    
    
    def remote_open(self, inn, title):
        self.inn = inn
        TGEObject("INNWND_Window").setText(title)
        TGEEval("canvas.pushDialog(InnWnd);")
    
    
    def remote_close(self):
        self.inn = None
        TGEEval("canvas.popDialog(InnWnd);")



def PyOnInnAddToParty():
    if not len(INNWND.charList) or len(INNWND.partyList) == 6:
        return
    sr = int(INNWND.charListCtrl.getSelectedId())
    INNWND.inn.callRemote("addToParty",INNWND.charList[sr].name)


def PyOnInnRemoveFromParty():
    if len(INNWND.partyList) == 1:
        return
    sr = int(INNWND.partyListCtrl.getSelectedId())
    INNWND.inn.callRemote("removeFromParty",INNWND.partyList[sr].name)


def PyOnInnWndClose():
    INNWND.inn.callRemote("leaveInn")



def PyExec():
    global INNWND
    INNWND = InnWnd()
    
    TGEExport(PyOnInnAddToParty,"Py","OnInnAddToParty","desc",1,1)
    TGEExport(PyOnInnRemoveFromParty,"Py","OnInnRemoveFromParty","desc",1,1)
    TGEExport(PyOnInnWndClose,"Py","OnInnWndClose","desc",1,1)
