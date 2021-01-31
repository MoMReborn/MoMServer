# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from math import floor
from mud.world.defines import *
from twisted.internet import reactor


LEADERWND = None

class LeaderWnd:
    def __init__(self):
        self.alliesList = TGEObject("LEADER_MEMBERSLIST")
        self.inviteButton = TGEObject("LEADER_INVITE_BTN")
        self.kickButton = TGEObject("LEADER_KICK_BTN")
        self.disbandButton = TGEObject("LEADER_DISBAND_BTN")
        
        self.allynames = []
        
        
    def disable(self):
        self.alliesList.visible = False
        self.inviteButton.setActive(False)
        self.kickButton.setActive(False)
        self.disbandButton.setActive(False)
        
    def enable(self):
        self.alliesList.visible = True
        self.inviteButton.setActive(True)
        self.kickButton.setActive(True)
        self.disbandButton.setActive(True)
        
    def clearAllianceInfo(self):
        if self.allianceInfo:
            self.allianceInfo.broker.transport.loseConnection()
        self.allianceInfo = None
        
    def setAllianceInfo(self,ainfo):
        from mud.client.playermind import PLAYERMIND
        
        if not PLAYERMIND or not PLAYERMIND.rootInfo:
            return
        
        self.allianceInfo = ainfo
        
        if ainfo.LEADER == PLAYERMIND.rootInfo.PLAYERNAME:
            self.enable()
        else:
            self.alliesList.clear()
            self.disable()
            return
        
        self.alliesList.setVisible(False)
        self.alliesList.clear()
        self.allynames = []

        
        x = 0
        xx = 0
        for pname in ainfo.PNAMES:
            if pname == PLAYERMIND.rootInfo.PLAYERNAME:
                xx+=1
                continue

            
            cname = ainfo.NAMES[xx][0]
            self.alliesList.addRow(x,"%s"%cname) #name and range
            self.allynames.append(cname)
            
            x+=1
            xx+=1

        self.alliesList.setSelectedRow(0)
        self.alliesList.scrollVisible(0)
        self.alliesList.setActive(True)
        self.alliesList.setVisible(True)

        
    def tick(self):
        pass

def PyOnInvite():
    from partyWnd import PARTYWND
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","invite")

def PyOnDisband():
    from partyWnd import PARTYWND
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","disband")

def PyOnKick():
    from partyWnd import PARTYWND
    if not len(LEADERWND.allynames):
        return
    id = int(LEADERWND.alliesList.getSelectedId())
    
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","kick",LEADERWND.allynames[id])
    
def PyExec():
    global LEADERWND
    LEADERWND = LeaderWnd()
    TGEExport(PyOnInvite,"Py","OnInvite","desc",1,1)
    TGEExport(PyOnDisband,"Py","OnDisband","desc",1,1)
    TGEExport(PyOnKick,"Py","OnKick","desc",1,1)
