# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
import math
from mud.world.core import CoreSettings
from datetime import datetime
import re



"""
RPG_MSG_GAME_GLOBAL = 0
RPG_MSG_GAME_COMBAT = 1 #generic combat
RPG_MSG_GAME_COMBAT_HIT = 2 #player's char hit somone
RPG_MSG_GAME_COMBAT_GOTHIT = 3 #player's char got hit
RPG_MSG_GAME_CASTING = 4 #player's char got hit
RPG_MSG_GAME_SPELLBEGIN = 5 #player's char got hit
RPG_MSG_GAME_SPELLEND = 6 #player's char got hit
RPG_MSG_GAME_DENIED = 7
RPG_MSG_GAME_GAINED = 8
RPG_MSG_GAME_LOST = 9
RPG_MSG_GAME_LOOT = 10
RPG_MSG_GAME_LEVELGAINED = 11
RPG_MSG_GAME_LEVELLOST = 12
RPG_MSG_GAME_CHARDEATH = 13
RPG_MSG_GAME_PARTYDEATH = 14
RPG_MSG_GAME_GOOD = 15
RPG_MSG_GAME_BAD = 16
RPG_MSG_GAME_EVENT = 17
"""

SPEECHCOLORCODES = {
#speech text
RPG_MSG_SPEECH_WORLD:"C8B560",
RPG_MSG_SPEECH_ZONE:"B8C323",
RPG_MSG_SPEECH_PARTY:"2896EA",
RPG_MSG_SPEECH_SAY:"28EA44",
RPG_MSG_SPEECH_AUCTION:"EA4828",
RPG_MSG_SPEECH_GLOBAL:"06FFFC",
RPG_MSG_SPEECH_ALLIANCE:"2896EA",
RPG_MSG_SPEECH_SYSTEM:"FFFF00",
RPG_MSG_SPEECH_TELL:"BBBBFF",
RPG_MSG_SPEECH_TOLD:"BBFFBB",
RPG_MSG_SPEECH_EMOTE:"ECB3EB",
RPG_MSG_SPEECH_OT:"E7E2EF",
RPG_MSG_SPEECH_HELP:"79FF21",
RPG_MSG_SPEECH_PLAYERJOINED:"CCCC33",
RPG_MSG_SPEECH_GUILD:"96FDED",
RPG_MSG_SPEECH_ERROR:"FF1100",

}
#game text
GAMECOLORCODES = {
RPG_MSG_GAME_GLOBAL:"FFFFFF",
RPG_MSG_GAME_COMBAT:"FFFFFF",
RPG_MSG_GAME_COMBAT_HIT:"28EFED",
RPG_MSG_GAME_COMBAT_GOTHIT:"EF7C28",
RPG_MSG_GAME_CASTING:"38EAE8",
RPG_MSG_GAME_SPELLBEGIN:"EA67E8",
RPG_MSG_GAME_SPELLEND:"EADB67",
RPG_MSG_GAME_DENIED:"FF1100",
RPG_MSG_GAME_GAINED:"00FF00",
RPG_MSG_GAME_LOST:"EA9E67",
RPG_MSG_GAME_LOOT:"67EABD",
RPG_MSG_GAME_LEVELGAINED:"E8EA38",
RPG_MSG_GAME_LEVELLOST:"FF0000",
RPG_MSG_GAME_CHARDEATH:"FF0000",
RPG_MSG_GAME_PARTYDEATH:"FF0000",
RPG_MSG_GAME_GOOD:"00FF00",
RPG_MSG_GAME_BAD:"FF0000",
RPG_MSG_GAME_EVENT:"FFFFFF",
RPG_MSG_GAME_GREEN:"00FF00",
RPG_MSG_GAME_BLUE:"09ADDC",
RPG_MSG_GAME_WHITE:"FFFFFF",
RPG_MSG_GAME_YELLOW:"F5F816",
RPG_MSG_GAME_RED:"FF1100",
RPG_MSG_GAME_NPC_SPEECH:"BAEA38",
RPG_MSG_GAME_PET_SPEECH:"E0EA38",
RPG_MSG_GAME_CASTING_NPC:"EE6644"
}



QUOTE_REPLACER = re.compile(r'(?<!\\)"')
NEWLINE_REPLACER = re.compile(r'\n(?!\Z)')



class TomeGui(object):
    pronouns = { 'Female': ('she','her','her','herself'),
                 'Male':   ('he','him','his','himself'),
                 'Neuter': ('it','it','its','itself')}
    srche,srchim,srchis,srcself = range(4)
    instance = None
    
    
    def __new__(cl, *p, **k):
        if not TomeGui.instance:
            TomeGui.instance = object.__new__(cl, *p, **k)
        return TomeGui.instance
    
    
    def __init__(self):
        self.gameFont = "Arial"
        self.speechFont = "Arial"
        self.gameText = ""
        self.speechText = ""
    
    
    @staticmethod
    def getInstance(self):
        return TomeGui.instance
    
    
    def initTGEObjects(self):
        self.gameTextScroll = TGEObject("Tome_GameTextScroll")
        self.speechTextScroll = TGEObject("Tome_SpeechTextScroll")
        self.gameTextCtrl = TGEObject("Tome_GameText")
        self.speechTextCtrl = TGEObject("Tome_SpeechText")
        self.tomeCommandCtrl = TGEObject("Tome_CommandText")
        self.tomeGui = TGEObject("TomeGui_Window")
    
    
    def reset(self):
        self.gameText = ""
        self.speechText = ""
        self.gameTextCtrl.setText("")
        self.speechTextCtrl.setText("")
    
    
    # Personalize messages with $src codes.
    def receiveGameTextPersonalized(self,textCode,text,cinfo):
        if not text:
            return
        
        if cinfo:
            genderPronouns = TomeGui.pronouns[cinfo.SEX]
            text = text.replace("$srche", genderPronouns[TomeGui.srche])
            text = text.replace("$srchim", genderPronouns[TomeGui.srchim])
            text = text.replace("$srchis", genderPronouns[TomeGui.srchis])
            text = text.replace("$srcself", genderPronouns[TomeGui.srcself])
            text = text.replace("$src", cinfo.NAME)
        
        self.receiveGameText(textCode,text)
    
    
    def receiveGameText(self,textCode,text):
        if not text:
            return
        try:
            fontsize = int(math.floor(float(TGEGetGlobal("$pref::Game::GameFontSize"))))
            fontsize += 3
        except:
            fontsize = 13
        
        if fontsize < 13:
            fontsize = 13
        if fontsize > 23:
            fontsize = 23
        
        TGESetGlobal("$pref::Game::GameFontSize",fontsize - 3)
        
        # Replace invalid quotes
        text = QUOTE_REPLACER.sub('\\"',text)
        text = text.replace(r'\"',r'"')
        text = text.replace(r'\'',"'")
        
        n = datetime.now()
        s = n.strftime("%I:%M:%S %p")
        logtext = TGECall('StripMLControlChars',text)
        # Newline replacement has to follow after the stripping of control chars.
        logtext = logtext.replace("\\n","\n")
        CoreSettings.LOGGAME.write("%s - %s"%(s,logtext))
        
        text = text.replace("\\n","\n")
        
        self.gameText += r'<linkcolor:%s><color:%s>%s'%(GAMECOLORCODES[textCode],GAMECOLORCODES[textCode],text)
        while len(self.gameText) > 4000: #lex is set to a 4096 buffer for evaluating, beware raising this
            self.gameText = self.gameText[1000:]
            #try to break on a color statement
            index = self.gameText.find("<color:")
            if index != -1:
                self.gameText = self.gameText[index:]
        
        pos = self.gameTextScroll.childRelPos.split(" ")
        self.gameTextCtrl.setText("<font:%s:%i><shadowcolor:000000><shadow:1:1>%s"%(self.gameFont,fontsize,self.gameText))
        if not int(self.gameTextScroll.isMouseLocked()):
            self.gameTextScroll.scrollToBottom()
        else:
            extenty = self.gameTextScroll.extent.split(" ")[1]
            self.gameTextScroll.scrollRectVisible(pos[0],pos[1],1,extenty)
    
    
    def receiveSpeechText(self,textCode,text):
        if not text:
            return
        try:
            fontsize = int(math.floor(float(TGEGetGlobal("$pref::Game::ChatFontSize"))))
            fontsize += 3
        except:
            fontsize = 13
        
        if fontsize < 13:
            fontsize = 13
        if fontsize > 23:
            fontsize = 23
        
        TGESetGlobal("$pref::Game::ChatFontSize",fontsize - 3)
        
        # Replace invalid quotes
        text = QUOTE_REPLACER.sub('\\"',text)
        text = text.replace(r'\"',r'"')
        text = text.replace(r'\'',"'")
        
        n = datetime.now()
        s = n.strftime("%I:%M:%S %p")
        logtext = TGECall('StripMLControlChars',text)
        # Newline replacement has to follow after the stripping of control chars.
        logtext = logtext.replace("\\n","\n")
        if textCode not in (RPG_MSG_SPEECH_SYSTEM,RPG_MSG_SPEECH_PLAYERJOINED, \
            RPG_MSG_SPEECH_ERROR):
            logtext = NEWLINE_REPLACER.sub("\n... ",logtext)
        CoreSettings.LOGCHAT.write("%s - %s"%(s,logtext))
        
        text = text.replace("\\n","\n")
        if textCode not in (RPG_MSG_SPEECH_SYSTEM,RPG_MSG_SPEECH_PLAYERJOINED, \
            RPG_MSG_SPEECH_ERROR):
            text = NEWLINE_REPLACER.sub("\n... ",text)
        
        self.speechText += r'<linkcolor:%s><color:%s>%s'%(SPEECHCOLORCODES[textCode],SPEECHCOLORCODES[textCode],text)
        while len(self.speechText) > 4000:#lex is set to a 4096 buffer for evaluating, beware raising this
            self.speechText = self.speechText[1000:]
            #try to break on a color statement
            index = self.speechText.find("<color:")
            if index != -1:
                self.speechText = self.speechText[index:]
        
        pos = self.speechTextScroll.childRelPos.split(" ")
        self.speechTextCtrl.setText("<font:%s:%i><shadowcolor:000000><shadow:1:1>%s"%(self.speechFont,fontsize,self.speechText))
        if not int(self.speechTextScroll.isMouseLocked()):
            self.speechTextScroll.scrollToBottom()
        else:
            extenty = self.speechTextScroll.extent.split(" ")[1]
            self.speechTextScroll.scrollRectVisible(pos[0],pos[1],1,extenty)
    
    
    def onChatFontSizeChanged(self):
        try:
            fontsize = int(math.floor(float(TGEGetGlobal("$pref::Game::ChatFontSize"))))
            fontsize += 3
        except:
            fontsize = 13
        
        if fontsize < 13:
            fontsize = 13
        if fontsize > 23:
            fontsize = 23
        
        self.speechTextCtrl.setText("<font:%s:%i><shadowcolor:000000><shadow:1:1>%s"%(self.speechFont,fontsize,self.speechText))
    
    
    def onGameFontSizeChanged(self):
        try:
            fontsize = int(math.floor(float(TGEGetGlobal("$pref::Game::GameFontSize"))))
            fontsize += 3
        except:
            fontsize = 13
        
        if fontsize < 13:
            fontsize = 13
        if fontsize > 23:
            fontsize = 23
        
        self.gameTextCtrl.setText("<font:%s:%i><shadowcolor:000000><shadow:1:1>%s"%(TomeGui.instance.gameFont,fontsize,TomeGui.instance.gameText))
    
    
    def onGlobalChannelToggle(self, v=None, fromStore=False):
        from mud.client.irc import FilterChannel
        if v == None:
            v = int(TGEObject("CHATGUI_GLOBAL_TOGGLE").getValue())
        else:
            TGEObject("CHATGUI_GLOBAL_TOGGLE").setValue(v)
        FilterChannel('M',v)
        if v:
            self.receiveGameText(RPG_MSG_GAME_GAINED,r'You are now listening to mom chat.\n')
        else:
            self.receiveGameText(RPG_MSG_GAME_GAINED,r'You are no longer listening to mom chat.\n')
        if not fromStore:
            from playerSettings import PLAYERSETTINGS
            from mud.client.playermind import TOGGLEABLECHANNELS
            PLAYERSETTINGS.setChannel(TOGGLEABLECHANNELS['M'],v)
    
    
    def onWorldChannelToggle(self):
        from mud.client.playermind import PLAYERMIND,TOGGLEABLECHANNELS
        v = int(TGEObject("CHATGUI_WORLD_TOGGLE").getValue())
        if v:
            PLAYERMIND.doCommand("CHANNEL",[0,"world","on"])
        else:
            PLAYERMIND.doCommand("CHANNEL",[0,"world","off"])
        from playerSettings import PLAYERSETTINGS
        PLAYERSETTINGS.setChannel(TOGGLEABLECHANNELS['W'],v)
    
    
    def onZoneChannelToggle(self):
        from mud.client.playermind import PLAYERMIND,TOGGLEABLECHANNELS
        v = int(TGEObject("CHATGUI_ZONE_TOGGLE").getValue())
        if v:
            PLAYERMIND.doCommand("CHANNEL",[0,"zone","on"])
        else:
            PLAYERMIND.doCommand("CHANNEL",[0,"zone","off"])
        from playerSettings import PLAYERSETTINGS
        PLAYERSETTINGS.setChannel(TOGGLEABLECHANNELS['Z'],v)
    
    
    def onOffTopicChannelToggle(self, v=None, fromStore=False):
        from mud.client.irc import FilterChannel
        if v == None:
            v = int(TGEObject("CHATGUI_OFFTOPIC_TOGGLE").getValue())
        else:
            TGEObject("CHATGUI_OFFTOPIC_TOGGLE").setValue(v)
        FilterChannel('O',v)
        if v:
            self.receiveGameText(RPG_MSG_GAME_GAINED,r'You are now listening to off-topic chat.\n')
        else:
            self.receiveGameText(RPG_MSG_GAME_GAINED,r'You are no longer listening to off-topic chat.\n')
        if not fromStore:
            from playerSettings import PLAYERSETTINGS
            from mud.client.playermind import TOGGLEABLECHANNELS
            PLAYERSETTINGS.setChannel(TOGGLEABLECHANNELS['O'],v)
    
    
    def onHelpChannelToggle(self, v=None, fromStore=False):
        from mud.client.irc import FilterChannel
        if v == None:
            v = int(TGEObject("CHATGUI_HELP_TOGGLE").getValue())
        else:
            TGEObject("CHATGUI_HELP_TOGGLE").setValue(v)
        FilterChannel('H',v)
        if v:
            self.receiveGameText(RPG_MSG_GAME_GAINED,r'You are now listening to help chat.\n')
        else:
            self.receiveGameText(RPG_MSG_GAME_GAINED,r'You are no longer listening to help chat.\n')
        if not fromStore:
            from playerSettings import PLAYERSETTINGS
            from mud.client.playermind import TOGGLEABLECHANNELS
            PLAYERSETTINGS.setChannel(TOGGLEABLECHANNELS['H'],v)
    
    
    def onChatCommand(self):
        tomeCommandCtrl = self.tomeCommandCtrl
        txt = ""
        if not tomeCommandCtrl.visible:
            tomeCommandCtrl.visible = True
            tomeCommandCtrl.makeFirstResponder(True)
        else:
            txt = tomeCommandCtrl.GetValue()
        from mud.client.playermind import PLAYERMIND
        cursorItem = PLAYERMIND.cursorItem
        if cursorItem:
            tomeCommandCtrl.SetValue(txt + " <%s>"%cursorItem.PROTONAME)
        else:
            from macro import CURSORMACRO
            if CURSORMACRO.macroType:
                if CURSORMACRO.macroType == 'SKILL':
                    tomeCommandCtrl.SetValue(txt + " <%s>"%CURSORMACRO.macroInfo)
                elif CURSORMACRO.macroType == 'SPELL':
                    from mud.client.gui.partyWnd import PARTYWND
                    cinfo = PARTYWND.charInfos[PARTYWND.curIndex]
                    spellName = cinfo.SPELLS[CURSORMACRO.macroInfo].SPELLINFO.BASENAME
                    tomeCommandCtrl.SetValue(txt + " <%s>"%spellName)
                CURSORMACRO.clear()
    
    
    def onGameFontChanged(self, args):
        gameFont = args[1]
        
        # Update game font type if it has changed.
        if self.gameFont != gameFont:
            self.gameFont = gameFont
            
            # Refresh game window with new font.
            self.onGameFontSizeChanged()
    
    
    def onChatFontChanged(self, args):
        speechFont = args[1]
        
        # Update chat font type if it has changed.
        if self.speechFont != speechFont:
            self.speechFont = speechFont
            
            # Refresh chat window with new font.
            self.onChatFontSizeChanged()



TomeGui()



def PyExec():
    TOMEGUI = TomeGui.instance
    TOMEGUI.initTGEObjects()
    
    TGEExport(TOMEGUI.onGameFontChanged,"Py","OnGameFontChanged","desc",2,2)
    TGEExport(TOMEGUI.onChatFontChanged,"Py","OnChatFontChanged","desc",2,2)
        
    TGEExport(TOMEGUI.onChatFontSizeChanged,"Py","OnChatFontSizeChanged","desc",1,1)
    TGEExport(TOMEGUI.onGameFontSizeChanged,"Py","OnGameFontSizeChanged","desc",1,1)
    
    TGEExport(TOMEGUI.onGlobalChannelToggle,"Py","OnGlobalChannelToggle","desc",1,1)
    TGEExport(TOMEGUI.onWorldChannelToggle,"Py","OnWorldChannelToggle","desc",1,1)
    TGEExport(TOMEGUI.onZoneChannelToggle,"Py","OnZoneChannelToggle","desc",1,1)
    TGEExport(TOMEGUI.onHelpChannelToggle,"Py","OnHelpChannelToggle","desc",1,1)
    TGEExport(TOMEGUI.onOffTopicChannelToggle,"Py","OnOffTopicChannelToggle","desc",1,1)
    
    TGEExport(TOMEGUI.onChatCommand,"Py","OnChatCommand","desc",1,1)
    
    from mud.client.irc import CycleReply
    TGEExport(CycleReply,"Py","CycleReply","desc",2,2)
