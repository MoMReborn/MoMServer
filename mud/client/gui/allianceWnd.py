# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from math import floor
from mud.world.defines import *
from twisted.internet import reactor
import traceback

ALLIANCEWND = None

class AllianceWnd:
    def __init__(self):
        self.allianceInfo = None
        self.inviteName = ""
        self.window = TGEObject("AllianceWnd_Window")
        self.leaveDeclineButton = TGEObject("ALLIANCE_LEAVEDECLINE")
        self.joinButton = TGEObject("ALLIANCE_JOIN")
        self.allianceMsg = TGEObject("ALLIANCE_MESSAGE")
        
        self.multiPane = TGEObject("ALLIANCEWND_MCHARPANE")
        self.cnames = {}
        self.chealths = {}
        self.pnames = []
        self.invite = None
        for x in xrange(0,5):
            self.pnames.append(TGEObject("ALLIANCE_P%i_NAME"%x))
            self.cnames[x] = []
            self.chealths[x] = []
            for y in xrange(0,6):
                self.chealths[x].append(TGEObject("ALLIANCE_P%i_C%i_HEALTH"%(x,y)))
                self.cnames[x].append(TGEObject("ALLIANCE_P%i_C%i_NAME"%(x,y)))
                
        #single char stuff
        
        
        self.singlePane = TGEObject("ALLIANCE_SCMY_PANE")
        self.singlePetHealth = TGEObject("ALLIANCE_SCMY_PETHEALTH")
        self.nameCtrl = TGEObject("ALLIANCE_SCMY_NAME")
        self.healthCtrl = TGEObject("ALLIANCE_SCMY_HEALTH")
        self.targetHealthCtrl = TGEObject("ALLIANCE_SCMY_TARGETHEALTH")
        self.targetCtrl = TGEObject("ALLIANCE_SCMY_TARGET")
        self.manaCtrl = TGEObject("ALLIANCE_SCMY_MANA")
        self.staminaCtrl = TGEObject("ALLIANCE_SCMY_STAMINA")
        
        self.castingTick = None
        self.castingCtrl = TGEObject("ALLIANCE_SCMY_CASTING")
        self.castingCtrl.visible = False
        
        self.petHealth  = TGEObject("ALLIANCE_SCMY_PETHEALTH")

        
        self.allianceLookup={}
        
        self.singleOthers = dict((x,(TGEObject("ALLIANCE_SC%i_GUICONTROL"%x),TGEObject("ALLIANCE_SC%i_HEALTH"%x),TGEObject("ALLIANCE_SC%i_NAME"%x))) for x in xrange(0,5))

        self.single = False
        self.myCharInfo = None
        self.setSingle()
        self.hideAll()
        
        
    def setSingle(self):
        self.single = True
        self.multiPane.visible = False
        self.singlePane.visible = True   
        
        self.window.extent = '128 320'     

    def setMulti(self):
        self.single = False
        self.multiPane.visible = True
        self.singlePane.visible = False
        
        self.window.extent = '217 364'
        
    def hideAll(self):
        
        self.allianceMsg.visible = False
        self.joinButton.visible = False
        self.leaveDeclineButton.visible = False
        
        for x in xrange(0,5):
            self.singleOthers[x][0].visible=False
            
            self.pnames[x].visible = False
            for y in xrange(0,6):
                self.chealths[x][y].visible = False
                self.cnames[x][y].visible = False
    
    
    def clearAllianceInfo(self):
        if self.allianceInfo:
            self.allianceInfo.broker.transport.loseConnection()
        self.allianceInfo = None
    
    
    def setAllianceInfo(self,ainfo):
        try:
            from mud.client.playermind import PLAYERMIND
            
            #self.hideAll()
            
            if not PLAYERMIND or not PLAYERMIND.rootInfo:
                return
            
            #self.allianceMsg.visible = True
            
            # Set text strings and enable buttons according to alliance status.
            if len(ainfo.PNAMES) > 1:
                self.allianceMsg.setText("You are a member of %s's alliance."%ainfo.PNAMES[0])
                self.leaveDeclineButton.visible = True
                self.leaveDeclineButton.text = "Leave"
            else:
                if not self.invite:
                    self.allianceMsg.setText("You are not currently in an alliance.")
                    self.joinButton.visible = False
                    self.leaveDeclineButton.visible = False
                else:
                    self.joinButton.visible = True
                    self.leaveDeclineButton.visible = True
                    self.leaveDeclineButton.text = "Decline"
                    self.allianceMsg.setText("You have been invited to %s's alliance."%self.invite)
            
            #XXX Twisted bug, setting this to the same value
            #causes a stopped observing on the server
            if ainfo != self.allianceInfo:
                self.allianceInfo = ainfo
            
            self.mobIds = {}
            self.allianceLookup = {}
            
            # Disable alliance info elements and reenable only needed ones later.
            for x in xrange(0,5):
                self.pnames[x].visible = False
                for y in xrange(0,6):
                    self.chealths[x][y].visible = False
                    self.cnames[x][y].visible = False
                self.singleOthers[x][0].visible = False
            
            allianceIndex = 0
            for enumerator,pname in enumerate(ainfo.PNAMES):
                if pname == PLAYERMIND.rootInfo.PLAYERNAME:
                    # Information about self always in slot 0.
                    self.allianceLookup[0] = ainfo.MOBIDS[enumerator][0]
                    continue
                
                self.mobIds[allianceIndex] = []
                
                self.pnames[allianceIndex].visible = True
                self.pnames[allianceIndex].setValue(pname)
                
                for y,cname in enumerate(ainfo.NAMES[enumerator]):
                    self.cnames[allianceIndex][y].visible = True
                    self.cnames[allianceIndex][y].setValue(cname)
                    self.chealths[allianceIndex][y].visible = True
                    self.chealths[allianceIndex][y].setValue(ainfo.HEALTHS[enumerator][y])
                    self.mobIds[allianceIndex].append(ainfo.MOBIDS[enumerator][y])
                
                self.allianceLookup[allianceIndex+1] = ainfo.MOBIDS[enumerator][0]
                p,h,name = self.singleOthers[allianceIndex]
                p.visible = True
                h.setValue(ainfo.HEALTHS[enumerator][0])
                name.setValue(ainfo.NAMES[enumerator][0])
                self.singleOthers[allianceIndex] = (TGEObject("ALLIANCE_SC%i_GUICONTROL"%allianceIndex),TGEObject("ALLIANCE_SC%i_HEALTH"%allianceIndex),TGEObject("ALLIANCE_SC%i_NAME"%allianceIndex))
                allianceIndex += 1
        
        except:
            traceback.print_exc()
    
    
    def setInvite(self,who):
        self.invite = who
        if who:
            self.joinButton.visible = True
            self.leaveDeclineButton.visible = True
            self.leaveDeclineButton.text = "Decline"
            self.allianceMsg.setText("You have been invited to %s's alliance."%who)
            #self.allianceMsg.visible = True
        #elif "affiliated" not in text:
        #    self.joinButton.visible = False
        #    self.leaveDeclineButton.visible = True
        #    self.leaveDeclineButton.text = "Leave"
        #    self.allianceMsg.setText(text)
        #    self.allianceMsg.visible = True
        else:
            self.joinButton.visible = False
            self.leaveDeclineButton.visible = False
            self.allianceMsg.setText("You are not currently in an alliance.")
            #self.allianceMsg.visible = True
    
    
    def tick(self):
        if self.myCharInfo:
            self.setCharInfo(self.myCharInfo)
        
        if not self.allianceInfo or len(self.allianceInfo.PNAMES) < 2:
            return
        
        self.leaveDeclineButton.visible = True
        self.leaveDeclineButton.text = "Leave"
        ainfo = self.allianceInfo
        
        from mud.client.playermind import PLAYERMIND
        
        allianceIndex = 0
        for enumerator,pname in enumerate(ainfo.PNAMES):
            # Info about self gets handled separately.
            if pname == PLAYERMIND.rootInfo.PLAYERNAME:
                continue
            # Update healths of alliance members.
            for y,health in enumerate(ainfo.HEALTHS[enumerator]):
                self.chealths[allianceIndex][y].setValue(health)
            p,h,name = self.singleOthers[allianceIndex]
            h.setValue(ainfo.HEALTHS[enumerator][0])
            allianceIndex += 1
    
    
    def setCharInfo(self,cinfo):
        rInfo = cinfo.RAPIDMOBINFO
        
        self.myCharInfo = cinfo
        self.nameCtrl.SetValue(cinfo.NAME)
        
        self.healthCtrl.SetValue(rInfo.HEALTH/rInfo.MAXHEALTH)

        if rInfo.MAXMANA:
            self.manaCtrl.SetValue(rInfo.MANA/rInfo.MAXMANA)
        else:
            self.manaCtrl.SetValue(0)
            
        if rInfo.PETNAME:
            self.petHealth.setValue(rInfo.PETHEALTH)
            self.petHealth.visible = True
        else:
            self.petHealth.visible = False    



        if cinfo.UNDERWATERRATIO != 1.0:
            self.staminaCtrl.setProfile("GuiBreathBarProfile")
            self.staminaCtrl.SetValue(cinfo.UNDERWATERRATIO)       
        else:
            self.staminaCtrl.setProfile("GuiStaminaBarProfile")
            self.staminaCtrl.SetValue(rInfo.STAMINA/rInfo.MAXSTAMINA)

        
        if rInfo.TGT:
            self.targetCtrl.SetValue(rInfo.TGT)
            self.targetCtrl.visible = True
            self.targetHealthCtrl.SetValue(rInfo.TGTHEALTH)
            self.targetHealthCtrl.visible = True
        else:
            self.targetCtrl.visible = False
            self.targetHealthCtrl.visible = False
            
    def tickCasting(self):
        #print self.castingTime,self.castingMaxTime
        self.castingTime+=.1
        
        if self.castingTime >= self.castingMaxTime:
            self.castingTime = 0
            self.castingCtrl.visible = False
            self.castingTick = None
            return
            
        percent = 1 - (self.castingTime/self.castingMaxTime)
        
        self.castingCtrl.SetValue(percent)
        
        self.castingTick = reactor.callLater(.1,self.tickCasting)
            
    def beginCasting(self,time):
        if self.castingTick:
            self.castingTick.cancel()
            self.castingTick = None
        self.castingMaxTime = time
        self.castingTime = 0
        self.castingTick = reactor.callLater(.1,self.tickCasting)
        
        self.castingCtrl.visible = True
        self.castingCtrl.SetValue(1)
        
    def endCasting(self):
        if self.castingTick:
            self.castingTick.cancel()
            self.castingTick = None
        
        self.castingCtrl.visible = False



def PyOnLeaveDeclineAlliance():
    from partyWnd import PARTYWND
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","leaveDecline")
    ALLIANCEWND.setInvite(None)
    

def PyOnJoinAlliance():
    from partyWnd import PARTYWND
    PARTYWND.mind.perspective.callRemote("PlayerAvatar","joinAlliance")
    ALLIANCEWND.setInvite(None)
    
def PyOnAllianceSelect(args):
    from partyWnd import PARTYWND
    
    pindex = int(args[1])
    cindex = int(args[2])
    
    ainfo = ALLIANCEWND.allianceInfo
    
    if len(ainfo.PNAMES) == 1:
        return #how did we get here?
        
    try:
        mobId = ALLIANCEWND.mobIds[pindex][cindex]
    except:
        return
    
    if mobId == -1:
        return
        
    PARTYWND.mind.charSetTarget(PARTYWND.curIndex,mobId)
    
    
#ALLIANCEWND_MCHARPANE
#size for multichar -> 217 364

#ALLIANCEWND_SCHARPANE
#size for singlechar -> 128 320




    
def OnAllianceSelectByIndex(args):
    index = int(args[1])
    from partyWnd import PARTYWND
    try:
        mobId = ALLIANCEWND.allianceLookup[index]    
        PARTYWND.mind.charSetTarget(0,mobId)
    except:
        pass
    
    
def PyExec():
    global ALLIANCEWND
    ALLIANCEWND = AllianceWnd()
    TGEExport(PyOnLeaveDeclineAlliance,"Py","OnLeaveDeclineAlliance","desc",1,1)
    TGEExport(PyOnJoinAlliance,"Py","OnJoinAlliance","desc",1,1)        
    TGEExport(PyOnAllianceSelect,"Py","AllianceSelect","desc",3,3)
    
    TGEExport(OnAllianceSelectByIndex,"Py","OnAllianceSelectByIndex","desc",2,2)
    