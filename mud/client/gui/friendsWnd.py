# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport

from mud.gamesettings import *
from mud.client.gui.tomeGui import TomeGui
TomeGui = TomeGui.instance
receiveGameText = TomeGui.receiveGameText
from mud.world.defines import *

from cPickle import load,dump
from time import time as sysTime
import traceback



class FriendsWnd(object):
    instance = None
    
    
    def __new__(cl, *p, **k):
        if not FriendsWnd.instance:
            FriendsWnd.instance = object.__new__(cl, *p, **k)
        return FriendsWnd.instance
    
    
    def __init__(self):
        self.remoteFriendsInfo = {}
        self.active = []
        self.lastSoundTime = sysTime() - 15
    
    
    @staticmethod
    def getInstance(self):
        return FriendsWnd.instance
    
    
    def initTGEObjects(self):
        self.addEditCtrl = TGEObject("FRIENDSWND_ADDEDIT")
        self.scrollCtrl = TGEObject("FRIENDSWND_SCROLL")
        self.textList = TGEObject("FRIENDSWND_LIST")
    
    
    def update(self, finfo=None, fromServer=False):
        from playerSettings import PLAYERSETTINGS
        
        try:
            FRIENDS = PLAYERSETTINGS.friends
            if finfo == None:
                finfo = self.remoteFriendsInfo
            else:
                self.remoteFriendsInfo = finfo
            
            playsound = False
            
            if fromServer:
                if sysTime() - self.lastSoundTime >= 15:
                    if TGEGetGlobal("$pref::game::friendsAudioAlerts") == "1":
                        playsound = True
            
            pos = self.scrollCtrl.childRelPos.split(" ")
            
            tc = self.textList
            tc.setVisible(False)
            tc.clear()
            
            online = set()
            offline = dict((friend.upper(),friend) for friend in FRIENDS)
            
            # Add online friends to list.
            for index,friend in enumerate(finfo.iterkeys()):
                friendUpper = friend.upper()
                matchGuild,wname,zname = finfo[friend]
                online.add(friend)
                try:
                    del offline[friendUpper]
                except KeyError:
                    pass
                if matchGuild:
                    # To be collected and forwarded to guild gui once this exists.
                    guildTag = " (Guild Member)"
                else:
                    guildTag = ""
                self.textList.addRow(index,"%s%s\t%s\t%s"%(friend,guildTag,wname,zname))
            
            # Add offline friends to list.
            for index,friend in enumerate(offline.itervalues()):
                self.textList.addRow(index,"%s\tAway\t"%(friend))
            
            if fromServer:
                for name in online.difference(self.active):
                    receiveGameText(RPG_MSG_GAME_LEVELGAINED, \
                        "Your friend %s has joined the game!\\n"%name)
                    if playsound:
                        TGEEval('alxPlay(alxCreateSource(AudioMessage, "%s/data/sound/sfx/Heartbeat_Loop1.ogg"));'%GAMEROOT)
                        self.lastSoundTime = sysTime()
                
                for name in self.active.difference(online):
                    receiveGameText(RPG_MSG_GAME_BLUE, \
                        "Your friend %s has left the game!\\n"%name)
                    if playsound:
                        TGEEval('alxPlay(alxCreateSource(AudioMessage, "%s/data/sound/sfx/BoneTowerPercussionRattle7.ogg"));'%GAMEROOT)
                        self.lastSoundTime = sysTime()
            
            self.active = online
            
            tc.setActive(True)
            tc.setVisible(True)
            
            self.scrollCtrl.scrollRectVisible(pos[0],pos[1],1,444)
        
        except:
            traceback.print_exc()
    
    
    def onAddFriend(self, name=None):
        from playerSettings import PLAYERSETTINGS
        
        if len(PLAYERSETTINGS.friends) >= 64:
            receiveGameText(RPG_MSG_GAME_DENIED, \
                "You may have up to 64 friends in your list.\\n")
            return
        
        if name == None:
            name = self.addEditCtrl.getValue()
        
        if not name or len(name) < 4:
            receiveGameText(RPG_MSG_GAME_DENIED,"Add friend: invalid name.\\n")
            return
        
        if not PLAYERSETTINGS.addFriend(name):
            receiveGameText(RPG_MSG_GAME_DENIED, \
                "This friend is already in your list.\\n")
            return
        
        receiveGameText(RPG_MSG_GAME_GAINED,"You have added %s as a friend.  It might take a moment to refresh their status.\\n"%name)
        
        self.submitFriendsList()
    
    
    def onRemoveFriend(self, name=None):
        from playerSettings import PLAYERSETTINGS
        FRIENDS = PLAYERSETTINGS.friends
        
        if name == None:
            if len(FRIENDS) <= 0:
                return
            index = int(self.textList.getSelectedId())
            if index > len(FRIENDS):
                return
            
            friend = FRIENDS[index]
            PLAYERSETTINGS.removeFriend(friend)
            
            receiveGameText(RPG_MSG_GAME_GAINED, \
                "You have removed %s from your friend list.\\n"%friend)
        
        else:
            name = name.upper()
            if PLAYERSETTINGS.removeFriend(name):
                receiveGameText(RPG_MSG_GAME_GAINED, \
                    "You have removed %s from your friend list.\\n"%name)
            else:
                receiveGameText(RPG_MSG_GAME_DENIED, \
                    "%s is not in your friend list.\\n"%name)
        
        self.submitFriendsList()
    
    
    def onClickFriend(self):
        from playerSettings import PLAYERSETTINGS
        FRIENDS = PLAYERSETTINGS.friends
        
        # Bound checks on selected item.
        if len(FRIENDS) <= 0:
            return
        index = int(self.textList.getSelectedId())
        if index > len(FRIENDS):
            return
        
        # Open chat window.
        TGECall("PushChatGui")
        
        # Get a handle to the tome control.
        commandCtrl = TomeGui.tomeCommandCtrl
        
        # Set text in tome control to /tell.
        commandCtrl.visible = True
        commandCtrl.makeFirstResponder(True)
        commandCtrl.setValue("/tell %s "% \
            FRIENDS[index].capitalize().replace(' ','_'))
    
    
    def submitFriendsList(self):
        from mud.client.playermind import PLAYERMIND
        from playerSettings import PLAYERSETTINGS
        
        if not PLAYERMIND or not PLAYERMIND.perspective:
            return
        
        try:
            PLAYERMIND.perspective.callRemote("PlayerAvatar","submitFriends", \
                PLAYERSETTINGS.friends)
        except:
            pass
        
        self.update()
    
    
    def setFriendsInfo(self, finfo):
        try:
            self.update(finfo,True)
        except:
            traceback.print_exc()



FriendsWnd()



def PyExec():
    FRIENDSWND = FriendsWnd.instance
    FRIENDSWND.initTGEObjects()
    
    TGEExport(FRIENDSWND.onAddFriend,"Py","OnAddFriend","desc",1,1)
    TGEExport(FRIENDSWND.onRemoveFriend,"Py","OnRemoveFriend","desc",1,1)
    TGEExport(FRIENDSWND.onClickFriend,"Py","OnClickFriend","desc",1,1)


