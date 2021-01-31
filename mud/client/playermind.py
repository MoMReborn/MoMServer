# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport

from twisted.spread import pb
from twisted.internet import defer,reactor
from twisted.cred.credentials import UsernamePassword

from mud.gamesettings import *
from mud.client.sounds import SOUNDS
from mud.client.gui.clientcommands import DoClientCommand
from mud.client.gui.encyclopediaWnd import \
    encyclopediaGetLink,OnEncyclopediaOnURL,encyclopediaSearch
from mud.client.gui.friendsWnd import FriendsWnd
FriendsWnd = FriendsWnd.instance
from mud.client.gui.gamebreak import DisplayBreak
from mud.client.gui.itemContainerWnd import ItemContainerWnd
ItemContainerWnd = ItemContainerWnd.instance
from mud.client.gui.lootWnd import LootWnd
LootWnd = LootWnd.instance
from mud.client.gui.macroWnd import MacroWnd
MacroWnd = MacroWnd.instance
from mud.client.gui.masterLoginDlg import DoMasterLogin
from mud.client.gui.tomeGui import TomeGui
TomeGui = TomeGui.instance
receiveGameText = TomeGui.receiveGameText
from mud.simulation.simmind import SimMind,SetRaceGraphics
from mud.world.shared.playdata import IsDirty
from mud.world.shared.worlddata import ZoneConnectionInfo
from mud.world.core import CoreSettings
from mud.world.defines import *
from mud.world.shared.vocals import *

from md5 import md5
import re
from sqlite3 import dbapi2 as sqlite
import sys
from time import time as sysTime
import traceback
import types



LASTCHANNEL = 'M'
IRCCHANNELS = ('H', 'HELP', 'O', 'OFFTOPIC', 'M', 'MOM')
CHATCHANNELS = ('H', 'HELP', 'O', 'OFFTOPIC', 'M', 'MOM', 'W', 'WORLD',
                'Z', 'ZONE', 'S', 'SAY', 'A', 'ALLIANCE', 'G', 'GUILD',
                'E', 'EMOTE', 'ME', 'GC', 'GMCHAT')
# TOGGLEABLECHANNELS, channels that can be toggled with either a special button on the tome gui
#  or with a /channel <channelname> <on|off>. Same indexes will be used in playerSettings.py, by name.
TOGGLEABLECHANNELS = {
    'H': 1, 'HELP': 1,
    'O': 1 << 1, 'OFFTOPIC': 1 << 1,
    'M': 1 << 2, 'MOM': 1 << 2,
    'W': 1 << 3, 'WORLD': 1 << 3,
    'Z': 1 << 4, 'ZONE': 1 << 4,
    'COMBAT': 1 << 5
}


QUOTE_REPLACER = re.compile(r'(?<!\\)"')

PLAYERMIND = None
DOQUITNAG = True
CLIENTEXITED = False
EXITFORCED = False



PAUSED_CALLBACK = DisplayBreak
def SetPausedCallback(cb):
    global PAUSED_CALLBACK
    PAUSED_CALLBACK = cb


CEREBRUM = None
def GetMoMClientDBConnection():
    global CEREBRUM
    if not CEREBRUM:
        CEREBRUM = sqlite.connect("./%s/data/worlds/multiplayer.baseline/world.db"%GAMEROOT)
        CEREBRUM.text_factory = sqlite.OptimizedUnicode
    return CEREBRUM



class PerspectiveWrapper:
    def __init__(self,perp):
        self.perspective = perp
        self.broker = perp.broker
        self.commands = []
        self.running = None
        self.lasttime = sysTime()
    
    
    def commandDone(self,result):
        self.running = False
        return result
    
    
    def tick(self):
        if self.running or not len(self.commands):
            return
        delta = sysTime() - self.lasttime
        if delta < .25:
            return
        self.lasttime = sysTime()
        d,_name,args,kw = self.commands.pop(0)
        nd = self.perspective.callRemote(_name,*args,**kw)
        nd.chainDeferred(d)
        self.running = True
    
    
    def callRemote(self,_name,*args, **kw):
        num = 25
        if PLAYERMIND and PLAYERMIND.charInfos and len(PLAYERMIND.charInfos):
            num = len(PLAYERMIND.charInfos) * 8
        if len(self.commands) < num:
            d = defer.Deferred()
            d.addCallback(self.commandDone)
            d.addErrback(self.commandDone)
            
            c = (d,_name,args,kw)
            self.commands.append(c)
            return d
        else:
            receiveGameText(RPG_MSG_GAME_DENIED,"The command buffer is full.\\n")
            return None



class PlayerMind(pb.Root):
    directConnect = ""
    
    def __init__(self):
        from gui.partyWnd import PARTYWND
        
        global PLAYERMIND
        PLAYERMIND = self
        self.perspective = None
        self.simMind = None
        
        PARTYWND.mind = self
        self.cursor = TGEObject("DefaultCursor")
        self.cursorItem = None
        
        self.nagTime = 180
        self.inventoryCmdAvailableTime = 0
        self.resizeCmdAvailableTime = 0
        
        self.running = True
        self.rootInfo = None
        
        #local so people don't spam trying to stop casting
        t = sysTime()
        self.stopCastingTimers = {0:t,1:t,2:t,3:t,4:t,5:t}
        
        self.paused = False
        TGESetGlobal("$GamePaused",self.paused)
        self.lastAdTime = sysTime()
        
        self.freeWorld = RPG_BUILD_DEMO
        self.party = None
        
        self.ircNick = None
        
        self.charInfos = {}
        
        self.pgserver = False
        
        self.initialFriendsSubmit = False
        
    
    def setPerspective(self,perp):
        self.perspective = PerspectiveWrapper(perp)
    
    
    #these are on the NEW MIND created in jumpserver
    def gotJumpServerResult(self,perspective):
        self.setPerspective(perspective)
        perspective.callRemote("PlayerAvatar","jumpIntoWorld",self.party[0])
    
    def gotJumpServerFailure(self,reason):
        print "jump failure",reason
    
    
    def remote_jumpServer(self, wip, wport, wpassword, zport, zpassword, party):
        
        if self.rootInfo:
            from gui.playerSettings import PLAYERSETTINGS
            PLAYERSETTINGS.storeWindowSettings()
        
        ip = wip
        if ip == None:
            ip = self.worldIP
            
        print "JumpServer",ip,wport
            
        mind = PlayerMind()
        mind.freeWorld = self.freeWorld
        mind.worldIP = self.worldIP
        mind.ircNick = self.ircNick
        mind.pgserver = self.pgserver
        self.running = False
        
        
        #hmmmm
        #try:
        #    self.perspective.broker.transport.loseConnection()
        #except:
        #    pass
            
        TGEEval("disconnect();Canvas.setContent(LoadingGui);")

        mind.party = party
        
        factory = pb.PBClientFactory()
        factory.unsafeTracebacks = PB_UNSAFE_TRACEBACKS
        reactor.connectTCP(ip,wport,factory)    
        
        #LAME!, role could be passed in instead
        MASTER_LOGIN_PLAYER = TGEObject("MASTER_LOGIN_PLAYER")
        MASTER_LOGIN_GUARDIAN = TGEObject("MASTER_LOGIN_GUARDIAN")
        MASTER_LOGIN_IMMORTAL = TGEObject("MASTER_LOGIN_IMMORTAL")

        role = "Player"
        if TGEGetGlobal("$pref::GM_LOGIN") == "1":
            TGESetGlobal("$pref::GM_LOGIN_ROLE","Player")
            if int(MASTER_LOGIN_GUARDIAN.getValue()):
                TGESetGlobal("$pref::GM_LOGIN_ROLE","Guardian")
                role = "Guardian"
            if int(MASTER_LOGIN_IMMORTAL.getValue()):
                TGESetGlobal("$pref::GM_LOGIN_ROLE","Immortal")
                role = "Immortal"
        
        password = md5(wpassword).digest()

        d = factory.login(UsernamePassword("%s-%s"%(TGEGetGlobal("$pref::PublicName"),role), password),mind)
        d.addCallbacks(mind.gotJumpServerResult, mind.gotJumpServerFailure)
        return d
    
    
    def tick(self):
        if self.perspective:
            if self.perspective.broker.disconnected:
                self.running = False
                from mud.client.irc import IRCDisconnect
                
                try:
                    IRCDisconnect()
                except:
                    traceback.print_exc()

                TGEEval("""
                if (PlayGui.isAwake())
                {
                    disconnect();
                    Canvas.setContent(MainMenuGui);
                    MessageBoxOK( "Disconnected", "You have been disconnected from the server." );    
                }
                """)
                TGESetGlobal("$Py::WORLDNAME","")
            else:
                self.perspective.tick()
            
            if not self.initialFriendsSubmit:
                self.initialFriendsSubmit = True
                FriendsWnd.submitFriendsList()
        
        if not self.running:
            return
            
            
        try:
            from gui.partyWnd import PARTYWND
            from gui.tacticalGui import TACTICALGUI
            from gui.itemInfoWnd import ITEMINFOWND            
            from gui.charMiniWnd import CHARMINIWND
            from gui.npcWnd import NPCWND
            from gui.allianceWnd import ALLIANCEWND
            from gui.leaderWnd import LEADERWND
            from gui.buffWnd import BUFFWND
            
            itemInfo = self.cursorItem
            cursor = self.cursor
            
            #yagh (yet another gross hack)
            if not itemInfo and not cursor.bitmapName.startswith("%s/data/ui/icons/"%GAMEROOT) and not cursor.bitmapName.startswith("%s/data/ui/spellicons/"%GAMEROOT):
                cursor.bitmapName = "common/ui/CUR_3darrow"
                cursor.sizeX = -1
                cursor.sizeY = -1
                cursor.hotSpot = "0 0"
                cursor.number = -1
                cursor.u0=0
                cursor.v0=0
                cursor.u1=1
                cursor.v1=1
            elif itemInfo:
                cursor.bitmapName ="%s/data/ui/items/%s/0_0_0"%(GAMEROOT,itemInfo.BITMAP)
                cursor.sizeX = 50
                cursor.sizeY = 50
                cursor.u0=0
                cursor.v0=0
                cursor.u1=1
                cursor.v1=1
                cursor.hotSpot = "0 0"
                cursor.number = -1
                if itemInfo.STACKMAX > 1:
                    cursor.number = itemInfo.STACKCOUNT

            
            if self.rootInfo.bankDirty:
                NPCWND.bankPane.set(self.rootInfo.BANK)
                self.rootInfo.bankDirty = False
    
            
            cinfo = self.charInfos[PARTYWND.curIndex]
            TGESetGlobal("$Py::SelectionCharacterIndex",PARTYWND.curIndex)
    
        
            #character link targets
            if False:
                for x,c in self.charInfos.iteritems():
                    linktarget = c.clientSettings['LINKTARGET']
                    if linktarget:
                        for y,lt in self.charInfos.iteritems():
                            if lt.NAME == linktarget:
                                assert c != lt #make sure we aren't linked to ourself
                                if lt.RAPIDMOBINFO.TGTID:
                                    if lt.RAPIDMOBINFO.TGTID != c.RAPIDMOBINFO.TGTID:
                                        self.perspective.callRemote("PlayerAvatar","doCommand","TARGETID",[x,lt.RAPIDMOBINFO.TGTID,0])    
                                        break
                    defaulttarget = c.clientSettings['DEFAULTTARGET']
                    if defaulttarget and not c.RAPIDMOBINFO.TGTID:
                        for y,lt in self.charInfos.iteritems():
                            if lt.NAME == defaulttarget:
                                self.perspective.callRemote("PlayerAvatar","doCommand","TARGETID",[x,lt.MOBID,0])    
                                break
                    
                
            if self.pgserver and self.ircNick != self.charInfos[0].NAME:
                self.ircNick = self.charInfos[0].NAME
                from irc import ChangeNick
                ChangeNick(self.ircNick)
            
            PARTYWND.tick()
                
            
            CHARMINIWND.tick()
            #TACTICALGUI.tick(cinfo,self.rootInfo)  # instead of just return in the tick, take it out here
            NPCWND.tick()
            ALLIANCEWND.tick()
            #LEADERWND.tick()  # don't even call instead of just returning
            BUFFWND.tick()
            MacroWnd.setFromCharacterInfos(self.charInfos)
            
            
            ITEMINFOWND.tick(cinfo)
            
            #tracking
            from gui.trackingWnd import TRACKINGWND
            if TRACKINGWND.trackingId or TRACKINGWND.trackInterest:
                frame = TGEGetTrackingFrame(TRACKINGWND.trackLocation)
                TRACKINGWND.trackingBitmap.setBitmap("~/data/ui/tracking/tracking%i"%frame)
            else:
                TRACKINGWND.trackingBitmap.setBitmap("")
            
            from gui.macro import MACROMASTER
            MACROMASTER.tick()
        except:
            traceback.print_exc()
        

        if False:#self.freeWorld:
            if self.rootInfo.PAUSED:
                if not self.paused:                    
                    PAUSED_CALLBACK(True)
                self.paused=True
            else:
                PAUSED_CALLBACK(False)
                if self.paused:
                    self.lastAdTime = sysTime()
                self.paused=False
                
            TGESetGlobal("$GamePaused",self.paused)
            
            t = sysTime()-self.lastAdTime
            if t > 12*60:
                self.lastAdTime = sysTime()
                t = 0
                
            TGEObject("SPONSORBREAK_BAR").SetValue(1.0 - float(t)/(12.0*60.0))

        
        
        t = TGEGetGlobal("$Gui::ToolTip")
        if t == "None" or t == None:
            #TGEObject("MOM_TOOLTIP").setText("")
            TGEObject("MOM_TOOLTIP_BORDER").visible = False
        else:
            tips = TGEGetGlobal("$pref::game::tooltips")
            if tips == None or tips == "None":
                tips = 1 
                TGESetGlobal("$pref::game::tooltips","1")
            tips = int(tips)
            if not tips and not t.startswith("XXX:"):
                TGEObject("MOM_TOOLTIP_BORDER").visible = False
            else:
            
                tt = TGEObject("MOM_TOOLTIP")
                
                if t.startswith("XXX:"):
                    t = t[4:]
            
                border = TGEObject("MOM_TOOLTIP_BORDER")
                tt.setText(t)
                extentx = int(tt.getTextWidth())
                border.visible = True
                border.setExtent(extentx+48,27)
        
        self.playermindTick = reactor.callLater(.1,self.tick)
    
    
    def camp(self, result, quit=False):
        TGESetGlobal("$Py::CAMPQUIT",1)
        TGEEval("Canvas.setContent(MainMenuGui);")
        
        try:
            self.simMind.canSeeTick.cancel()
        except:
            pass
        try:
            self.simMind.updateSimObjectsTick.cancel()
        except:
            pass
        try:
            self.simMind.brainsTick.cancel()
        except:
            pass
        
        try:
            self.playermindTick.cancel()
        except:
            pass
        
        if reactor.running:
            reactor.runUntilCurrent()
            reactor.doIteration(0)
        
        # On forced exit reactors don't really work anymore.
        if not EXITFORCED:
            d = self.perspective.perspective.callRemote("PlayerAvatar","logout")
            d.addCallback(self.camp_main,quit)
            d.addErrback(self.camp_main,quit)
            return d
        else:
            self.camp_main(None,quit)
            return None
    
    
    def camp_main(self, result, quit=False):
        from mud.client.gui.worldGui import ClearPlayerPerspective
        from mud.client.irc import IRCDisconnect
        try:
            IRCDisconnect()
        except:
            traceback.print_exc()
        
        self.running = False
        
        # Clean up different cacheables.
        if self.rootInfo:
            try:
                from gui.petWnd import PETWND
                PETWND.charInfo = None
                from gui.tacticalGui import TACTICALGUI
                TACTICALGUI.charInfo = None
                from gui.craftingWnd import CRAFTINGWND
                CRAFTINGWND.charInfo = None
                from gui.advancePane import ADVANCEPANE
                ADVANCEPANE.cinfo = None
                from gui.vaultWnd import VAULTWND
                VAULTWND.cinfo = None
                from gui.partyWnd import PARTYWND
                PARTYWND.skillPane.charInfo = None
                PARTYWND.spellPane.charInfo = None
                PARTYWND.statsPane.charInfo = None
                PARTYWND.invPane.charInfo = None
                PARTYWND.settingsPane.currentChar = None
                PARTYWND.charInfos = None
                from gui.charMiniWnd import CHARMINIWND
                CHARMINIWND.charInfos = None
                from gui.buffWnd import BUFFWND
                BUFFWND.charInfos = None
                from gui.playerSettings import PLAYERSETTINGS
                PLAYERSETTINGS.charInfos = None
                from gui.worldGui import CHARINFOS
                CHARINFOS = None
                for cinfo in self.charInfos.itervalues():
                    for item in cinfo.ITEMS.itervalues():
                        item.broker.transport.loseConnection()
                    cinfo.ITEMS.clear()
                    for spell in cinfo.SPELLS.itervalues():
                        spell.broker.transport.loseConnection()
                    cinfo.SPELLS.clear()
                    cinfo.SPELLEFFECTS = []
                    cinfo.RAPIDMOBINFO.broker.transport.loseConnection()
                    cinfo.RAPIDMOBINFO = None
                    cinfo.broker.transport.loseConnection()
                self.charInfos.clear()
                self.clearAllianceInfo()
                from gui.npcWnd import NPCWND
                NPCWND.bankPane.set({})
                for bankItem in self.rootInfo.BANK.itervalues():
                    bankItem.broker.transport.loseConnection()
                self.rootInfo.BANK.clear()
                self.rootInfo.CHARINFOS = None
                self.rootInfo.broker.transport.loseConnection()
                self.rootInfo = None
            except:
                traceback.print_exc()
        
        # If the perspective wrapper exists and has a perspective attached
        #  disconnect the broker and free the perspectives reference.
        if self.perspective and self.perspective.perspective:
            self.perspective.perspective.broker.transport.loseConnection()
            self.perspective.perspective = None
        
        # Free the perspectives reference in worldgui.py->PlayerPerspective.
        ClearPlayerPerspective()
        
        # Free the reference to the perspective wrapper.
        self.perspective = None
        
        # On forced exit reactors don't really work anymore.
        if not EXITFORCED:
            reactor.callLater(0.1,self.camp_callLater,quit)
        else:
            self.camp_callLater(quit)
    
    
    def camp_callLater(self, quit=False):
        TGEEval("disconnect();")
        TGESetGlobal("$Py::WORLDNAME","")
        TGESetGlobal("$Py::CAMPQUIT",0)
        
        if quit:
            TGEEval("Py::OnQuit();")
        else:
            try:
                SPVal = TGEGetGlobal("$Py::ISSINGLEPLAYER")
                if SPVal and int(SPVal):
                    from mud.worldserver.embedded import ShutdownEmbeddedWorld
                    ShutdownEmbeddedWorld()
                    TGEEval("Canvas.setContent(SinglePlayerGui);")
                    return
            except:
                pass
            DoMasterLogin()
    
    
    def campQuit(self):
        self.camp(None,True)
        return
    
    
    def doCommand(self,cmd,args):
        global DOQUITNAG,PREORDER_QUIT
        if RPG_BUILD_DEMO:
            if cmd.upper() == "QUIT":
                DOQUITNAG = False
                PREORDER_QUIT = True
                TGEObject("DEMOINFO_BITMAP").setBitmap("~/data/ui/demo/main")
                TGEObject("DEMOINFOWIND_LATERBUTTON").command = "Py::OnCampQuit();"
                TGEEval("canvas.pushDialog(DemoInfoWnd);")
                return
        
        if cmd.upper() == "QUIT" or cmd.upper() == "CAMP":
            from gui.partyWnd import PARTYWND
            from gui.playerSettings import PLAYERSETTINGS
            self.running = False
            PLAYERSETTINGS.storeWindowSettings()
            PARTYWND.encounterBlock = -1  # reset on negative block during next iteration
            PARTYWND.settingsPane.encounterSettingCurrent = RPG_ENCOUNTER_PVE
            PARTYWND.settingsPane.encounterSetting.SetValue(RPG_ENCOUNTER_SETTING_FORINDEX[RPG_ENCOUNTER_PVE])
            
            self.camp(None,cmd.upper()=="QUIT")
            return
        try:
            if cmd.upper() == "STOPCAST":
                t = sysTime()
                index = int(args[0])
                if t - self.stopCastingTimers[index] < 12:
                    receiveGameText(RPG_MSG_GAME_DENIED,"%s cannot stop casting at this time.\\n"%self.charInfos[index].NAME)
                    return
                self.stopCastingTimers[index] = t
        except:
            traceback.print_exc()
        
        d = self.perspective.callRemote("PlayerAvatar","doCommand",cmd,args)
    
    
    #INVENTORY

    #this is called when swapping inventory around, cursor item is called seperately
    
    def remote_setItemSlot(self,charId,itemInfo,slot):
        from gui.partyWnd import PARTYWND
        
        for index,cinfo in self.charInfos.iteritems():
            if cinfo.CHARID == charId:
                if itemInfo:
                    itemInfo.SLOT = slot
                    cinfo.ITEMS[slot]=itemInfo
                else:
                    if cinfo.ITEMS.has_key(slot):
                        del cinfo.ITEMS[slot]
                if index == PARTYWND.curIndex:
                    PARTYWND.invPane.setFromCharacterInfo(cinfo)
                return
    
    
    def onInvSlot(self,cinfo,slot):
        self.perspective.callRemote("PlayerAvatar","onInvSlot",cinfo.CHARID,slot)
    
    def onInvSlotAlt(self,cinfo,slot):
        # Search for the item in the clicked slot.
        clickedItem = cinfo.ITEMS.get(slot)
        # If there's no item, we don't have anything to process, so return.
        if not clickedItem:
            return
        # If the item is a container, no need to send command to server,
        #  display contents ourselves.
        if clickedItem.CONTAINERSIZE:
            ItemContainerWnd.openContainer(clickedItem)
            return
        self.perspective.callRemote("PlayerAvatar","onInvSlotAlt",cinfo.CHARID,slot)
    
    def onBankSlot(self,slot):
        self.perspective.callRemote("PlayerAvatar","onBankSlot",slot)
    
    def onInvSlotCtrl(self,cinfo,slot):
        # Search for the item in the clicked slot.
        clickedItem = cinfo.ITEMS.get(slot)
        # If there's no item, we don't have anything to process, so return.
        if not clickedItem:
            return
        # If the item is a container, no need to send command to server,
        #  display contents ourselves.
        if clickedItem.CONTAINERSIZE:
            ItemContainerWnd.openContainer(clickedItem)
            return
        self.perspective.callRemote("PlayerAvatar","onInvSlotCtrl",cinfo.CHARID,slot)

        
    def onSpellSlot(self,cinfo,slot):
        if cinfo.DEAD:
            return
        self.perspective.callRemote("PlayerAvatar","onSpellSlot",cinfo.CHARID,slot)

    def onSpellSlotSwap(self,cinfo,source,dest):
        self.perspective.callRemote("PlayerAvatar","onSpellSlotSwap",cinfo.CHARID,source,dest)
    
    
    def remote_setCursorItem(self, itemInfo):
        from gui.partyWnd import PARTYWND
        
        if itemInfo:
            itemInfo.SLOT = RPG_SLOT_CURSOR
        
        self.cursorItem = itemInfo
        PARTYWND.setCursorItem()
    
    
    def remote_checkIgnore(self, charName):
        from gui.playerSettings import PLAYERSETTINGS
        
        if charName and charName.upper() in PLAYERSETTINGS.ignored:
            return True
        
        return False
    
    
    def remote_receiveTextList(self,messages):
        from gui.playerSettings import PLAYERSETTINGS
        
        for t,textCode,text,src,stripML in messages:
            if src and src in PLAYERSETTINGS.ignored:
                continue  # messages is a list which may contain different sources
            if t == 0:
                self.remote_receiveGameText(textCode,text,stripML)
            elif t == 1:
                self.remote_receiveSpeechText(textCode,text)
    
    
    def remote_receiveGameText(self,textCode,text,stripML):
        # Replace invalid quotes
        text = QUOTE_REPLACER.sub('\\"',text)
        if stripML:
            text = TGECall('StripMLControlChars',text)
        receiveGameText(textCode,text)
    
    
    def remote_receiveSpeechText(self,textCode,text):
        # Replace invalid quotes
        text = QUOTE_REPLACER.sub('\\"',text)
        TomeGui.receiveSpeechText(textCode,text)
    
    
    #connection stuff
    def remote_createServer(self,zconnect):
        print "CreateServer"
        if self.simMind:
            self.simMind.destroyServer()
        
        self.simMind = SimMind(self.perspective,zconnect.instanceName)
        SetRaceGraphics(zconnect.raceGraphics)
        
        TGEEval("""
            LOAD_ZONEBITMAP.setBitmap("~/data/ui/loading/SPCreateZone");
            LoadingProgress.setValue(0);
            LOAD_MapDescription.setText("");
            LoadingProgressTxt.setText("... Populating Zone ... Please Wait ...");
            canvas.setcontent(LoadingGui);
            LOAD_MapName.setText("Traveling");
            canvas.repaint();""")
        
        TGEEval('CreateLocalMission("%s","%s");'%(zconnect.missionFile,zconnect.password))
    
    
    def remote_connect(self,zconnect,fantasyName=None):
        from gui.playerSettings import PLAYERSETTINGS
        
        # Update player settings with where we are.
        PLAYERSETTINGS.updateZone(zconnect.niceName)
        
        if fantasyName:
            TGESetGlobal("$pref::FantasyName",fantasyName)
        
        #TGECall("MessagePopup","Connecting to Zone...","Please wait...")
        TGEEval("Canvas.repaint();")
        #print zconnect.ip,zconnect.port,zconnect.password,zconnect.niceName,zconnect.missionFile
        TGESetGlobal("$Py::RPG::ShowPlayers",1)
        TGESetGlobal("$Py::RPG::ShowNPCs",1)
        TGESetGlobal("$Py::RPG::ShowEnemies",1)
        TGESetGlobal("$Py::RPG::ShowPoints",1)
        
        #stash the zoneconnectpassword
        TGESetGlobal("$Py::playerZoneConnectPassword",zconnect.playerZoneConnectPassword)
        
        if SimMind.directConnect:
            zconnect.ip = SimMind.directConnect
        
        if int(TGEGetGlobal("$Py::ISSINGLEPLAYER")):
            print "CONNECT",zconnect.ip
            TGEEval('ConnectLocalMission();')
        else:
            print "CONNECT",zconnect.ip
            connectstring = "%s:%i"%(zconnect.ip,zconnect.port)
            TGEEval('ConnectRemoteMission("%s","%s");'%(connectstring,""))
    
    
    # --- play stuff
    
    
    def remote_setRootInfo(self,rootInfo,pauseTime=None):
        from gui.partyWnd import SetFromCharacterInfos
        
        #turn off autowalk (for zoning, ect)
        if int(TGEGetGlobal("$mvAutoForward")):
            TGESetGlobal("$mvAutoForward",2) #turn off
        
        doTick = False
        if not self.rootInfo:
            doTick = True
            
        if pauseTime:
            self.lastAdTime = sysTime()-pauseTime

        self.rootInfo = rootInfo
        self.charInfos = rootInfo.CHARINFOS
        SetFromCharacterInfos(self.charInfos)
        #from gui.charSelectGui import SetFromCharacterInfos
        #SetFromCharacterInfos(self.charInfos)

        MacroWnd.setFromCharacterInfos(self.charInfos)

        
        for x in xrange(0,6):
            TGEObject("PARTYWND_CHAR%i"%x).visible = False
        
        if len(self.charInfos) > 1:    
            for x in xrange(0,len(self.charInfos)):
                TGEObject("PARTYWND_CHAR%i"%x).visible = True
        
        from gui.allianceWnd import ALLIANCEWND
        ALLIANCEWND.setCharInfo(self.charInfos[0])
        
        from gui.charMiniWnd import CHARMINIWND
        CHARMINIWND.setCharInfos(self.charInfos)
        from gui.buffWnd import BUFFWND
        BUFFWND.setCharInfos(self.charInfos)
        
        TGEObject("MACROWND_CHAR0").performClick()
        TGEObject("INVPANE_PAGEBUTTON0").performClick()
        if doTick:
            self.tick()
        
    def remote_setCurCharIndex(self,index):
        from gui.partyWnd import PARTYWND
        PARTYWND.setFromCharacterInfo(index)


    def remote_openPetWindow(self):
        TGEEval("canvas.pushDialog(PetWnd);")
    
    
    def charSetTarget(self,charIndex,mobId,cycle=False):
        self.perspective.callRemote("PlayerAvatar","doCommand","TARGETID",[charIndex,mobId,cycle])
        
        
    def remote_mouseSelect(self,charIndex,mobId):
        for x,cinfo in self.charInfos.iteritems():
            if x == charIndex:
                
                if cinfo.clientSettings['LINKTARGET']:
                    from gui.partyWnd import PARTYWND
                    cinfo.clientSettings['LINKTARGET']=None # clear link target
                    if PARTYWND.settingsPane.currentChar == cinfo:
                        PARTYWND.settingsPane.setFromCharacterInfo(cinfo,True)
                    
                continue #already set on server
            if cinfo.clientSettings['LINKMOUSETARGET']:
                self.perspective.callRemote("PlayerAvatar","doCommand","TARGETID",[x,mobId,0])
    
    
    #spell casting
    def remote_beginCasting(self,charIndex,time):
        from gui.charMiniWnd import CHARMINIWND
        from gui.allianceWnd import ALLIANCEWND
        
        CHARMINIWND.beginCasting(charIndex,time)
        ALLIANCEWND.beginCasting(time)
    
    
    # Loot a mob or assess a target.
    def remote_setLoot(self, loot, assess=False):
        LootWnd.setLoot(loot,assess)
    
    
    def expungeItem(self):
        self.perspective.callRemote("PlayerAvatar","expungeItem")

    def splitItem(self,newStackSize):
        self.perspective.callRemote("PlayerAvatar","splitItem",newStackSize)
        
        
    #inns
    
    def remote_getInnWnd(self):
        from gui.innWnd import INNWND
        return INNWND
            
    
        
    #zoning
    def remote_setZoneOptions(self,zoptions):
        from gui.playerSettings import PLAYERSETTINGS
        
        print zoptions
        PLAYERSETTINGS.storeWindowSettings()
        
        
        self.simMind = None
        TGEEval("disconnect();")
        
        #eventually this will bring up a dialog for us to either:
        #a) join a specific existing zone server
        #b) start our own, possible private zone server
        #for now, we just use the first one givem
        if not len(zoptions):
            #we HAVE to launch a new zone
            self.perspective.callRemote("PlayerAvatar","chooseZone","new")
            return
            
        self.perspective.callRemote("PlayerAvatar","chooseZone",zoptions[0].zoneInstanceName)
            
        
        
    def remote_syncTime(self,hour,minute):
        TGEEval(r'TGEDayNightSyncTime(%i,%i);'%(hour,minute))
        
    #INTERACTION
    def remote_openNPCWnd(self,title,banker=False):
        TGEObject("NPCWnd_Window").setText(title)
        from gui.npcWnd import NPCWND        
        NPCWND.openWindow(self.perspective, title,banker)
    def remote_closeNPCWnd(self):
        from gui.npcWnd import NPCWND
        NPCWND.closeWindow()
        
    def remote_setVendorStock(self,isVendor,stock,markup):
        from gui.npcWnd import NPCWND
        NPCWND.setStock(isVendor,stock,markup)
        
    def remote_setInitialInteraction(self,dialogLine,choices,title=None):
        from gui.npcWnd import NPCWND
        NPCWND.setInitialInteraction(dialogLine,choices,title)
        
        
    #Alliance
    
    def clearAllianceInfo(self):
        from gui.allianceWnd import ALLIANCEWND
        from gui.leaderWnd import LEADERWND
        ALLIANCEWND.clearAllianceInfo()
        LEADERWND.clearAllianceInfo()
        
    
    def remote_setAllianceInfo(self,ainfo):
        from gui.allianceWnd import ALLIANCEWND
        from gui.leaderWnd import LEADERWND
        ALLIANCEWND.setAllianceInfo(ainfo)
        LEADERWND.setAllianceInfo(ainfo)
        
    #this could go away
    def remote_setAllianceInvite(self,who):
        from gui.allianceWnd import ALLIANCEWND
        ALLIANCEWND.setInvite(who)
        if who:
            TGEEval("canvas.pushDialog(AllianceWnd);")
        
    #Player trading
    
    def remote_openTradeWindow(self,tradeInfo):
        from gui.tradeWnd import TRADEWND
        TRADEWND.open(tradeInfo)
        
    def remote_closeTradeWindow(self):
        from gui.tradeWnd import TRADEWND
        TRADEWND.close()
        
    #tracking
    def remote_setMuteTime(self,t):
        from irc import SetMuteTime
        SetMuteTime(t)
    
    def remote_setTracking(self,tracking):
        from gui.trackingWnd import TRACKINGWND
        TRACKINGWND.set(tracking)
        
    #conversation
    def remote_setTell(self,teller):
        teller = teller.replace(" ","_")
        TGESetGlobal("$Py::LastTell",teller)
    
    # Evaluation
    def remote_setTgtDesc(self,infoDict):
        from gui.tgtDescWnd import TGTDESCWND
        TGTDESCWND.setInfo(infoDict)
    
    #sound effects
    
    def remote_vocalize(self,sexcode,set,vox,which):
        sex = "Male"
        if sexcode == 1:
            sex = "Female"
        if which < 10:
            num = "0%i"%which
        else:
            num = str(which)
        filename = "vocalsets/%s_LongSet_%s/%s_LS_%s_%s%s.ogg"%(
        sex,set,sex,set,VOCALFILENAMES[vox],num)
        
        
        self.remote_playSound(filename)
        
        
    
    def remote_playSound(self,sound):
        if type(sound) == types.IntType:
            eval = 'alxPlay(alxCreateSource(AudioMessage, "%s/data/sound/%s"));'%(GAMEROOT,SOUNDS[sound])
        else:
            eval = 'alxPlay(alxCreateSource(AudioMessage, "%s/data/sound/%s"));'%(GAMEROOT,sound)
        
       
        TGEEval(eval)
        
    #journal
    
    def remote_addJournalEntry(self,journalEntryID):
        from gui.journalWnd import JOURNALWND
        con = GetMoMClientDBConnection()
        journalTopic,journalEntry,text = con.execute("SELECT topic,entry,text FROM journal_entry WHERE id = %i LIMIT 1;"%journalEntryID).fetchone()
        JOURNALWND.addEntry(journalTopic,journalEntry,text)
        
        
    def remote_openDemoInfoWnd(self,screen):
        
        TGEObject("DEMOINFO_BITMAP").setBitmap("~/data/ui/demo/%s"%screen)
        TGEEval("canvas.pushDialog(DemoInfoWnd);")

        

    def remote_setResurrectNames(self,names):
        if len(names):
            from gui.resurrectionGui import RESURRECTIONWND
            RESURRECTIONWND.set(names)
            TGEEval('Canvas.pushDialog("ResurrectionGui");')
        else:
            TGEEval('Canvas.popDialog("ResurrectionGui");')
    
    def resurrect(self,cname):
        self.perspective.callRemote("PlayerAvatar","onResurrect",cname)
        
    def remote_resurrectionRequest(self,resurrector,xp):
        TGEEval('MessageBoxYesNo("Resurrection", "Would you like to be resurrected by %s with %i%% experience recovery?","Py::OnResurrectAccept();");'%(resurrector,int(xp*100.0)))
        
    def acceptResurrect(self):
        self.perspective.callRemote("PlayerAvatar","onAcceptResurrect")
    
    
    def remote_partyWipe(self, xpLoss=-1):
        from gui.partyWnd import PARTYWND
        
        self.remote_playSound("sfx/HauntingVoices1.ogg")
        
        if xpLoss == 0:
            self.remote_receiveGameText(RPG_MSG_GAME_PARTYDEATH, \
            "Your party has been wiped out!!!\\n",False)
        elif xpLoss == 1:
            self.remote_receiveGameText(RPG_MSG_GAME_PARTYDEATH, \
            "Your party has been wiped out and permanently lost experience!!!\\n", \
            False)
        
        # A negative blocking value forces an encounter setting reset
        #  during next iteration.
        PARTYWND.encounterBlock = -1
        if int(PARTYWND.settingsPane.encounterPVEDie.GetValue()):
            PARTYWND.settingsPane.encounterSettingCurrent = RPG_ENCOUNTER_PVE
            PARTYWND.settingsPane.encounterSetting.SetValue( \
                              RPG_ENCOUNTER_SETTING_FORINDEX[RPG_ENCOUNTER_PVE])
            self.perspective.callRemote("PlayerAvatar","setEncounterSetting", \
                                        RPG_ENCOUNTER_PVE,True)
    
    
    def remote_checkEncounterSetting(self, zoning=False, \
        newIndex=RPG_ENCOUNTER_PVE, force=False):
        from gui.partyWnd import PARTYWND
        
        settingsPane = PARTYWND.settingsPane
        if not force and (PARTYWND.encounterBlock > 0 or PARTYWND.encounterTimer):
            self.perspective.callRemote("PlayerAvatar", "setEncounterSetting", settingsPane.encounterSettingCurrent, True)
            if zoning:
                PARTYWND.encounterBlock = 0
        elif zoning:
            if int(settingsPane.encounterPVEZone.GetValue()):
                settingsPane.encounterSettingCurrent = RPG_ENCOUNTER_PVE
                settingsPane.encounterSetting.SetValue(RPG_ENCOUNTER_SETTING_FORINDEX[RPG_ENCOUNTER_PVE])
            else:
                self.perspective.callRemote("PlayerAvatar", "setEncounterSetting", settingsPane.encounterSettingCurrent, True)
        else:
            settingsPane.encounterSettingCurrent = newIndex
            settingsPane.encounterSetting.SetValue(RPG_ENCOUNTER_SETTING_FORINDEX[newIndex])
            if force:  # if force, assume that server sets his side automatically
                PARTYWND.encounterSettingDisturbed()
            else:
                settingsPane.encounterSettingStatic.setVisible(False)
                settingsPane.encounterSettingTimer.setVisible(False)
                settingsPane.encounterSetting.setVisible(True)
    
    
    def remote_disturbEncounterSetting(self):
        from gui.partyWnd import PARTYWND
        PARTYWND.encounterSettingDisturbed()
    
    
    def chooseAdvancement(self,cname,advancement):
        self.perspective.callRemote("PlayerAvatar","chooseAdvancement",cname,advancement)
    
    
    def remote_setFriendsInfo(self,finfo):
        FriendsWnd.setFriendsInfo(finfo)
        
        
"""
      Con::setIntVariable("ServerInfo::Status",info.status);
      Con::setVariable("ServerInfo::Address",addrString);
      Con::setVariable("ServerInfo::Name",info.name);
      Con::setVariable("ServerInfo::GameType",info.gameType);
      Con::setVariable("ServerInfo::MissionName",info.missionName);
      Con::setVariable("ServerInfo::MissionType",info.missionType);
      Con::setVariable("ServerInfo::State",info.statusString);
      Con::setVariable("ServerInfo::Info",info.infoString);
      Con::setIntVariable("ServerInfo::PlayerCount",info.numPlayers);
      Con::setIntVariable("ServerInfo::MaxPlayers",info.maxPlayers);
      Con::setIntVariable("ServerInfo::BotCount",info.numBots);
      Con::setIntVariable("ServerInfo::Version",info.version);
      Con::setIntVariable("ServerInfo::Ping",info.ping);
      Con::setIntVariable("ServerInfo::CPUSpeed",info.cpuSpeed);
      Con::setBoolVariable("ServerInfo::Favorite",info.isFavorite);
      Con::setBoolVariable("ServerInfo::Dedicated",info.isDedicated());
      Con::setBoolVariable("ServerInfo::Password",info.isPassworded());
"""



def OnReallyQuit(forced=False):
    global EXITFORCED,PLAYERMIND
    
    EXITFORCED = forced
    
    if PLAYERMIND:
        PLAYERMIND.doCommand("QUIT",[0])
        PLAYERMIND = None
    else:
        OnUltimateQuit()


def OnGameOptionsQuit():
    TGEEval('MessageBoxYesNo( "Quit?", "Do you really want to venture forth to reality?", "Py::OnReallyQuit();", "");')


def OnReallyCamp():
    global PLAYERMIND
    PLAYERMIND.doCommand("CAMP",[0])
    PLAYERMIND = None


def OnGameOptionsCamp():
    TGEEval('MessageBoxYesNo("Camp?", "Do you really want to camp and return to the Main Menu?","Py::OnReallyCamp();");')


# Enums for substitution indexes.
(SUB_MALE, SUB_FEMALE, SUB_OTHER) = range(3)

# Sex-based substitution values.
SUBSTITUTION_SUBJECTIVE = ("he" , "she", "it" )
SUBSTITUTION_OBJECTIVE  = ("him", "her", "it" )
SUBSTITUTION_POSSESSIVE = ("his", "her", "its")

## @brief Substitutes context characters based on character info.
#  @param characterInfo (CharacterInfoGhost) Character info that may provide
#                       data for context substitution. 
#  @param str (String) String for which conext subsitition will occur.
#  @return (String) String with stripped multiple whitespace, stripped escapped
#          characters, and conntext substitution.
def substituteContext(characterInfo, str):
    
    # Get a handle to the mob info.
    mobInfo = characterInfo.RAPIDMOBINFO 
    
    # Split the string into a list of words.  This allows for small string
    # rebuildling during context substitution, and when re-joined, it will have
    # effectively stripped multiple whitespaces.
    words = str.split()
    
    # For each word, check if it is a context substitution character.  Strings
    # are not mutable, so access through index must occur after each substituion
    # to ensure substitution is attempted on the updated string.
    # Note: the context specific substitution variables are case-sensitive.
    # Escape character ('\') will become ('\\').
    # %t = target name
    # %g = taget's gender
    # %s = target in third-person pronoun subjective
    # %o = target in third-person pronoun objective
    # %p = target in third-person pronoun possessive
    for index in xrange(len(words)):
        
        # Prevent backslashes from being used as escape characters.
        words[index] = words[index].replace("\\", "\\\\")
        
        # All other substitutions require a valid target.
        if mobInfo.TGTID:
            
            words[index] = words[index].replace("%t", mobInfo.TGT) # Target name.
            words[index] = words[index].replace("%r", mobInfo.TGTRACE) # Target race.
            words[index] = words[index].replace("%g", mobInfo.TGTSEX) # Target sex.
            
            # Determine the sex of the mob, all personal pronouns cases are dependent
            # on the target's sex/gender.
            if RPG_SEXES[SUB_MALE] == mobInfo.TGTSEX:
                tgtSexIndex = SUB_MALE
            elif RPG_SEXES[SUB_FEMALE] == mobInfo.TGTSEX:
                tgtSexIndex = SUB_FEMALE
            else:
                tgtSexIndex = SUB_OTHER
                
            # Substitute values.
            words[index] = words[index].replace("%s", SUBSTITUTION_SUBJECTIVE[tgtSexIndex]) # Subjective pronoun.
            words[index] = words[index].replace("%o", SUBSTITUTION_OBJECTIVE[tgtSexIndex]) # Objective pronoun.
            words[index] = words[index].replace("%p", SUBSTITUTION_POSSESSIVE[tgtSexIndex]) # Possesive pronoun.
    
    # Return a string of the words joined together by spaces.        
    return ' '.join(words)
            

# The regular expression is a non-greedy inner-most <text> match.
# Matches must begin with "<" and continue up to a ">".  For example,
# "<a> <b<c>" will return matches for "<a>" and "<c>" match, and
# ignore "<b".  By the time the regex match is performed, all markup
# has been stripped.  With the  guarantee of no markup, it is safe
# to ignore "<b".
# Match[0] returns: <text>
# Match[1] returns: text
MARKUP_PARSER = re.compile(r'(<([^<>]*)>)')
def formatMLString(formatString):
    # This little function will clear out any possible ML commands
    # so custom formatting from players doesn't screw up chat.
    if not formatString:
        return ""
    formatString = TGECall('StripMLControlChars',formatString)
    for match in MARKUP_PARSER.findall(formatString):
        # Format encyc links!
        link = encyclopediaGetLink(match[1])
        if link:
            formatString = formatString.replace(match[0],link)
    
    return formatString


def formatChatString(sendString):
    # Don't bother with short strings
    if len(sendString) < 7:
        return sendString
    
    if sendString.isupper():
        sendString = sendString.lower()
    
    charList = list(sendString)
    charNum = len(set(charList))
    if charNum < 3:
        TGEEval("""MessageBoxOK("Message ignored", "The chat message you tried to send was filtered out, it didn't seem to make much sense.");""")
        return None
    
    prevChar = ''
    repeatCount = 0
    nonAlphanumCount = 0
    
    for i,char in enumerate(charList):
        # Not more than five non-text characters in a row (smilies, live!)
        if char == ' ' or char.isalpha() or char.isdigit():
            nonAlphanumCount = 0
        else:
            nonAlphanumCount += 1
            if nonAlphanumCount > 5:
                charList[i] = ''
                continue
        
        # Don't allow repeating of a specific character more than thrice in a row
        if char == prevChar:
            repeatCount += 1
            if repeatCount > 3:
                charList[i] = ''
        else:
            repeatCount = 0
        prevChar = char
    
    sendString = ''.join(charList)
    
    sendString.replace(' u ', 'you')
    sendString.replace(' r ', 'are')
    
    return sendString


def PyDoCommand(myargs, insertCurChar=True, indexHack=None):
    from gui.partyWnd import PARTYWND
    
    global LASTCHANNEL
    from mud.client.irc import SendIRCMsg,IRCConnect,IRCTell,IRCEmote,SetAwayMessage
    
    
    # If the flag is set to insert current character, then use the current
    # Character info for context substitution.            
    if insertCurChar:
        text = substituteContext(PLAYERMIND.charInfos[PARTYWND.curIndex], \
                                 myargs[1])    

    # Otherwise, if an index hack is present, then use the hacked index to get
    # the Character info for context substitution.
    elif indexHack != None:
        text = substituteContext(PLAYERMIND.charInfos[indexHack], \
                                 myargs[1])    
        
    # Otherwise, no context substitution will occur.
    else:
        text = myargs[1]
    
    # Attempt to do a client-commannd.  If the command is handed, then return
    # early.
    if DoClientCommand((0,text),indexHack):
        return
    
    # If the text begins with the imm command, use the immortal avatar.
    if text.startswith('/imm'):
        #immortal command
        text = text.split(' ')
        cmd = text[1].upper()
        args = text[2:]
        PLAYERMIND.perspective.callRemote("ImmortalAvatar","command",cmd,args)
        return
    
    # If the text begins with the gm command, use the guardian avatar.
    elif text.startswith('/gm'):
        #guardian command
        text = text.split(' ')
        cmd = text[1].upper()
        args = text[2:]
        PLAYERMIND.perspective.callRemote("GuardianAvatar","command",cmd,args)
        return
    
    # If the text does not begin with a slash, then the player is just chatting
    # on the last used channel.
    if not text.startswith('/'):
        
        # Set the last channel to be the current command.
        cmd = LASTCHANNEL
        
        # Pack all the text into a single element list.  This allows for code
        # reuse of arg handling.
        args = [text]
        
    # Otherwise, the player has supplied a command.     
    else:
        
        # Strip whitespace and split the text into a list of string elements.
        text = text.strip().split(' ')
        
        # The first word is a cmmand.  Thus, get the text after the first 
        # character ("/").  Turn it to uppercase to prevent case sensitive 
        # checks.
        cmd = text[0][1:].upper()
        
        # If there is nothing after the "/", then there is no command to process
        # so return early.
        if not cmd:
            return
        
        # Args are items after the commmand in the text list.
        args = text[1:]
    
    # If the command is a chat channel command, some chat formatting needs to
    # occur to prevent malicious markup.
    if cmd in CHATCHANNELS:
        
        # If the command is not an emote, then update the last channel.
        if cmd not in ('E', 'EMOTE', 'ME'):
            LASTCHANNEL = cmd

        # Chat rules:
        #  FormatMLString:        
        #   formatMLString is only called on outgoing to world, not irc server.
        #   Client will call formatMLString when receiving messages from IRC.
        # Args Type:
        #   Tuple/list for world server.
        #   String for irc.
        args = formatChatString(' '.join(args))
        
        # If the message is going to a world-specific channel, then perform 
        # some string ceanup with markup stripping.
        if cmd not in IRCCHANNELS:
            
            # Strip markup and split string into list.
            args = formatMLString(args).split()
                                        
            # If there is no text left after cleanup, then return early.
            if not args:
                return
            
            # If the channel is GM chat, send it off to GM avatar.
            if cmd in ('GC','GMCHAT'):
                PLAYERMIND.perspective.callRemote("GuardianAvatar","chat",args)
                return
            
            # If the flag is set to insert current character, then insert the
            # current character index at the front of the arg list.            
            if insertCurChar:
                args.insert(0, PARTYWND.curIndex)        
        
            # Otherwise, if an index hack is present, then insert the index
            # hack at the front of the arg list.
            elif indexHack != None:
                args.insert(0, indexHack) 
            
            # Delegate the command to PlayerMind.
            PLAYERMIND.doCommand(cmd, args)
            
            # Return as the command has been handled.
            return
        
        # Otherwise, the message is going to global channel (IRC).
        else:
            
            # If there is no text to send then return early.
            if not args:
                return
            
            # Send the IRC message.
            SendIRCMsg(cmd , args)
            
            # Return as the command has been handled.
            return
    
    if "/" == cmd[0]:
        receiveGameText(RPG_MSG_GAME_YELLOW, "Memo: %s\\n"%(formatMLString(' '.join(text)[2:].replace('\\','\\\\'))))
        return
    
    if cmd == "CHANNEL":
        if len(args) != 2:
            receiveGameText(RPG_MSG_GAME_DENIED, "Usage: /channel <channel> <on|off>\\n")
            return
        if args[1].upper() == "ON":
            on = True
        else:
            on = False
        channelUpper = args[0].upper()
        chatChannel = TOGGLEABLECHANNELS.get(channelUpper,0)
        if chatChannel <= 0:
            receiveGameText(RPG_MSG_GAME_DENIED, "Channel %s can't be toggled.\\n"%args[0])
            return
        # Syntax is correct and channel can be toggled. Update player settings.
        from gui.playerSettings import PLAYERSETTINGS
        PLAYERSETTINGS.setChannel(chatChannel,on)
        # Check if channel provided is an irc channel, those get filtered on client.
        if channelUpper in ('M',"MOM"):
            TomeGui.onGlobalChannelToggle(on)
            return
        elif channelUpper in ('O',"OFFTOPIC"):
            TomeGui.onOffTopicChannelToggle(on)
            return
        elif channelUpper in ('H','HELP'):
            TomeGui.onHelpChannelToggle(on)
            return
        # Otherwise continue with this function, channel needs to be filtered server side.
    
    if cmd == 'MCONNECT' and PLAYERMIND.ircNick:
        IRCConnect(PLAYERMIND.ircNick)
        return
    
    elif cmd == 'T'or cmd == 'TELL':
        IRCTell(args[0], ' '.join(args[1:]))
        return
    elif cmd == 'GE'or cmd == 'GEMOTE':
        args = formatChatString(' '.join(args))
        if args:
            IRCEmote(LASTCHANNEL, args)
        return
    
    # Reduce  inventory command processing for server processing
    # by client cooldown.
    elif cmd in ("SORT", "EMPTY", "STACK"):

        # Compare current systemtime to the next allowed
        # runtime.
        timestamp = sysTime()
        timeDelta = int(PLAYERMIND.inventoryCmdAvailableTime - timestamp)
        if 0 < timeDelta:
            receiveGameText(RPG_MSG_GAME_DENIED, "You cannot use this command for another %u seconds.\\n" % timeDelta)
            return

        # Set the next allowed runtime for these commands
        # to be 15 seconds from the current time.
        PLAYERMIND.inventoryCmdAvailableTime = timestamp + 15      
      
    elif "RESIZE" == cmd:
        # Compare current systemtime to the next allowed
        # runtime.
        timestamp = sysTime()
        timeDelta = int(PLAYERMIND.resizeCmdAvailableTime - timestamp)
        if 0 < timeDelta:
            receiveGameText(RPG_MSG_GAME_DENIED, "You cannot use the resize command for another %u seconds.\\n" % timeDelta)
            return

        # Set the next allowed runtime for these commands
        # to be 120 seconds from the current time.
        PLAYERMIND.resizeCmdAvailableTime = timestamp + 120
    
    # Insert index of current character so server knows what
    # party member is performing the skill
    if insertCurChar:
        args.insert(0, PARTYWND.curIndex)
    
    elif indexHack != None:
        args.insert(0, indexHack)
    
    PLAYERMIND.doCommand(cmd,args)


def PyMissionDownloadComplete():
    from gui.playerSettings import PLAYERSETTINGS
    from gui.partyWnd import PyOnSendXPSliders
    
    PLAYERSETTINGS.loadWindowSettings()
    
    TGEEval("""
    FadeWnd.fadeinTime = 2000;
    Canvas.pushDialog( FadeWnd );
    """)
    
    PyOnSendXPSliders([0,1,2,3,4,5])
    
    
    
    if CoreSettings.IDE and CoreSettings.IDE_ZONE and CoreSettings.IDE_EDITZONE:
        TGEEval("toggleEditor(1);")

def PyClearCharTarget():
    from gui.partyWnd import PARTYWND
    
    try:
        curIndex = PARTYWND.curIndex

        PLAYERMIND.charSetTarget(curIndex,0)
    except:
        pass
    
def OnCharEffect(args):
    cindex,slot = int(args[1]),int(args[2])
    cinfo = PLAYERMIND.charInfos[cindex]
    sinfo = cinfo.SPELLEFFECTS[slot]
    PLAYERMIND.perspective.callRemote("PlayerAvatar","cancelProcess",cinfo.CHARID,sinfo.PID)
    
def OnCharEffectShift(args):
    """ OnCharEffectShift:
    
        Called when an effect is shift left clicked from the buff gui.  This function 
        will open the encyclopedia to the effect's page.
    """
    characterIndex,slot = int(args[1]),int(args[2])
    effectName = PLAYERMIND.charInfos[characterIndex].SPELLEFFECTS[slot].NAME.split()
    if effectName[-1] in RPG_ROMAN:
        effectName.pop()
    encyclopediaSearch(' '.join(effectName))
    
    
def OnCharEffectShiftRight(args):
    """ OnCharEffectShiftRight:
    
        Called when an effect is shift right clicked from the buff gui.  This function 
        will insert a chatlink to the effect's encyclopedia page.
    """
    characterIndex,slot = int(args[1]),int(args[2])
    effectName = PLAYERMIND.charInfos[characterIndex].SPELLEFFECTS[slot].NAME.split()
    if effectName[-1] in RPG_ROMAN:
        effectName.pop()
    OnEncyclopediaOnURL((None,"chatlink%s"%(' '.join(effectName))))



PREORDER_QUIT = False
def OnPreOrder():
    TGEEval('canvas.popDialog(DemoInfoWnd);')
    
    
    
    global PREORDER_QUIT
    if PREORDER_QUIT:
        TGEEval('gotoWebPage(\"http://www.prairiegames.com/index.php?option=com_content&task=view&id=25\");Py::OnUltimateQuit();')
    else:
        fs = int(TGEGetGlobal("$pref::video::fullscreen"))
        
        if not fs:
            TGEEval('gotoWebPage(\"http://www.prairiegames.com/index.php?option=com_content&task=view&id=25\");')
            return
        
        TGECall("MessageBoxYesNo","Thanks for ordering!","Do you want to exit the game and go to the ordering web page?",'gotoWebPage(\"http://www.prairiegames.com/index.php?option=com_content&task=view&id=25\");Py::OnUltimateQuit();',"")        
        
"""        
        #we're fullscreen, if we can go windowed, do so and go to web page... otherwise, launch brower and quit
        desktop = TGECall("GetDesktopResolution").split(" ")
        xres = int(desktop[0])
        bpp = int(desktop[2])
        
        
        neededx = 1024
        if sys.platform[:6] != 'darwin':
            neededx=1025 #need > 1024 on windows
        if xres >= neededx and bpp>=32:
            TGEEval('setScreenMode( 1024, 768, 32, 0 );')
            TGEEval('gotoWebPage(\"http://www.prairiegames.com/ordering.html\");')
        else:
            #must quit
            TGECall("MessageBoxOK","Thanks for pre-ordering!","The game will now exit and bring you to the pre-ordering web page.","'gotoWebPage(\"http://www.prairiegames.com/ordering.html\");Py::OnUltimateQuit();'")        
"""            


def OnUltimateQuit():
    global CLIENTEXITED
    
    #I guess one more
    try:
        SPVal = TGEGetGlobal("$Py::ISSINGLEPLAYER")
        if SPVal and (int(SPVal)):
            from mud.worldserver.embedded import ShutdownEmbeddedWorld
            ShutdownEmbeddedWorld()
    except:
        traceback.print_exc()
    
    TGEEval("quit();")
    
    CLIENTEXITED = True


def OnQuit():
    global PREORDER_QUIT,CLIENTEXITED
    
    #HOW MANY QUIT FUNCTIONS DO WE NEED?!?!?!
    if RPG_BUILD_DEMO and DOQUITNAG:
        PREORDER_QUIT = True
        TGEObject("DEMOINFO_BITMAP").setBitmap("~/data/ui/demo/main")
        TGEObject("DEMOINFOWIND_LATERBUTTON").command = "Py::OnUltimateQuit();"
        TGEEval("canvas.pushDialog(DemoInfoWnd);")
    else:
        try:
            SPVal = TGEGetGlobal("$Py::ISSINGLEPLAYER")
            if SPVal and (int(SPVal)):
                from mud.worldserver.embedded import ShutdownEmbeddedWorld
                ShutdownEmbeddedWorld()
        except:
            traceback.print_exc()
        
        TGEEval("quit();")
    
    CLIENTEXITED = True


def OnResurrectAccept():
    PLAYERMIND.acceptResurrect()


def OnCampQuit():
    global PLAYERMIND
    if not PLAYERMIND:
        return
    PLAYERMIND.campQuit()
    PLAYERMIND = None


def OnCamp():
    global PLAYERMIND
    if not PLAYERMIND:
        return
    PLAYERMIND.camp(None,False)
    PLAYERMIND = None



TGEExport(PyMissionDownloadComplete,"Py","MissionDownloadComplete","desc",1,1)
TGEExport(PyDoCommand,"Py","DoCommand","desc",2,2)
TGEExport(OnGameOptionsCamp,"Py","OnGameOptionsCamp","desc",1,1)
TGEExport(OnGameOptionsQuit,"Py","OnGameOptionsQuit","desc",1,1)
TGEExport(OnCharEffect,"Py","OnCharEffect","desc",3,3)
TGEExport(OnCharEffectShift,"Py","OnCharEffectShift","desc",3,3)
TGEExport(OnCharEffectShiftRight,"Py","OnCharEffectShiftRight","desc",3,3)
TGEExport(OnReallyCamp,"Py","OnReallyCamp","desc",1,1)
TGEExport(OnReallyQuit,"Py","OnReallyQuit","desc",1,1)
TGEExport(OnQuit,"Py","OnQuit","desc",1,1)
TGEExport(OnUltimateQuit,"Py","OnUltimateQuit","desc",1,1)
TGEExport(OnPreOrder,"Py","OnPreOrder","desc",1,1)
TGEExport(OnCampQuit,"Py","OnCampQuit","desc",1,1)
TGEExport(OnCamp,"Py","OnCamp","desc",1,1)

TGEExport(OnResurrectAccept,"Py","OnResurrectAccept","desc",1,1)


TGEExport(PyClearCharTarget,"Py","ClearCharTarget","desc",1,1)

