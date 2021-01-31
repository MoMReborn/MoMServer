# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword

from mud.gamesettings import *
from mud.client.irc import IRCConnect
from mud.client.playermind import PlayerMind,SimMind
from mud.client.gui.worldGui import Setup as worldSetup
from mud.world.worldupdate import WorldUpdate
from mud.worldserver.embedded import SetupEmbeddedWorld,ShutdownEmbeddedWorld
from mud.world.defines import *

from md5 import md5
import os
from shutil import rmtree,copyfile
import traceback



WORLDS = []


def Error(value):
    print value


def EnumSinglePlayerWorlds():
    global WORLDS
    
    worlds = []
    
    if not os.path.exists("./%s/data/worlds/singleplayer"%GAMEROOT):
        os.makedirs("./%s/data/worlds/singleplayer"%GAMEROOT)
    dir = os.listdir("./%s/data/worlds/singleplayer"%GAMEROOT)
    
    for fn in dir:
        if os.path.isdir('./%s/data/worlds/singleplayer/%s'%(GAMEROOT,fn)):
            worlds.append(fn)
    
    WORLDS = worlds
    
    tc = TGEObject("SINGLEPLAYER_WORLDLIST")
    tc.setVisible(False)
    tc.clear()
    for i,wi in enumerate(worlds):
        TGEEval(r'SINGLEPLAYER_WORLDLIST.addRow(%i,"%s" TAB "%s");'%(i,wi,""))
    
    #tc.sort(1) # this sorts alphabetically
    tc.setSelectedRow(0)
    tc.scrollVisible(0)
    tc.setActive(True)#this should be based on any worlds found
    tc.setVisible(True)


WORLDDB = None
def PlayerConnected(perspective,args):
    args[0].setPerspective(perspective)
    
    #alright, we are connected time to make the donuts
    worldSetup(perspective)
    
    #if we got here, the world has been loaded successfully (or so we hope), so lets take a snapshot
    copyfile(WORLDDB,WORLDDB+".good")


def OnLoadSingleWorld(worldname=None):
    global WORLDDB
    TGESetGlobal("$Py::ISSINGLEPLAYER",1)
    TGESetGlobal("$Py::LastTell","")
    if not worldname:
        tc = TGEObject("SINGLEPLAYER_WORLDLIST")
        sr = int(tc.getSelectedId())
        if sr >= 0 and len(WORLDS):
            worldname = WORLDS[sr]

    if worldname:
        TGECall("MessagePopup","Loading World...","Please wait...")
        TGEEval("Canvas.repaint();")
        
        try:
            try:
                WORLDDB = "%s/%s/data/worlds/singleplayer/%s/world.db"%(os.getcwd(),GAMEROOT,worldname)
                r = WorldUpdate(WORLDDB,"%s/%s/data/worlds/multiplayer.baseline/world.db"%(os.getcwd(),GAMEROOT),True)
            except:
                TGECall("CloseMessagePopup")
                TGECall("MessageBoxOK","Problem Updating World!","There was an error updating this world!")
                return
            
            if not r:
                SetupEmbeddedWorld(worldname)
            else:
                TGECall("CloseMessagePopup")
                return
        except:
            TGECall("CloseMessagePopup")
            TGECall("MessageBoxOK","Problem Loading World!","There was an error loading this world!")
            traceback.print_exc()
            ShutdownEmbeddedWorld()
            return
        
        TGECall("CloseMessagePopup")
        
        TGESetGlobal("$Py::WORLDNAME",worldname)
        
        # log into world
        factory = pb.PBClientFactory()
        reactor.connectTCP("localhost",3013,factory)
        mind = PlayerMind()
        password = md5("ThePlayer").digest()
        
        d = factory.login(UsernamePassword("ThePlayer-Immortal", password),mind)
        d.addCallback(PlayerConnected,(mind,))
        d.addErrback(Error)
        
        if False:#RPG_BUILD_DEMO:
            TGEObject("SPONSORBREAK_BAR").visible = True
        else:
            TGEObject("SPONSORBREAK_BAR").visible = False


DWORLD = ""
def OnReallyDeleteSingleWorld():
    if os.path.isdir('./%s/data/worlds/singleplayer/%s'%(GAMEROOT,DWORLD)):
        try:
            rmtree('./%s/data/worlds/singleplayer/%s'%(GAMEROOT,DWORLD))
        except:
            traceback.print_exc()
            pass
    EnumSinglePlayerWorlds()


def OnDeleteSingleWorld():
    global DWORLD
    tc = TGEObject("SINGLEPLAYER_WORLDLIST")
    sr = int(tc.getSelectedId())
    if sr >= 0 and len(WORLDS):
        DWORLD = WORLDS[sr]
        TGEEval('MessageBoxYesNo("Delete World?", "Do you really want to delete %s?","Py::OnReallyDeleteSingleWorld();");'%(WORLDS[sr]))


#this is from the dialog
def OnNewSingleWorld():
    name = TGEObject("SINGLEPLAYER_WORLDNAME").getValue()
    if not len(name):
        TGECall("MessageBoxOK","Invalid World Name!","Please enter SOME world name")
        return
    
    if name in WORLDS:
        TGECall("MessageBoxOK","World Exists","That world already exists")
        return
    
    if not name.replace(' ','').isalnum():
        TGECall("MessageBoxOK","Invalid World Name!","Please only use letters and numbers in your world name.")
        return
    
    TGEEval("canvas.popDialog(NewSinglePlayerWorldDlg);")
    
    os.makedirs('./%s/data/worlds/singleplayer/%s'%(GAMEROOT,name))
    copyfile('./%s/data/worlds/multiplayer.baseline/world.db'%GAMEROOT,'./%s/data/worlds/singleplayer/%s/world.db'%(GAMEROOT,name))
    
    EnumSinglePlayerWorlds()


#SINGLE PLAYER GLOBAL CHAT GUI STUFF
#$pref::SPGlobalChatUserName
#Py::OnSPGlobalChatLogin();

def OnSPGlobalChatLogin():
    username = TGEGetGlobal("$pref::SPGlobalChatUserName")
    try:
        if len(username) < 4 or len(username) > 12:
            TGECall("MessageBoxOK","Invalid Username","Your username must be more than 4 characters and less than 13")
            return
    except:
        TGECall("MessageBoxOK","Invalid Username","Your username must be more than 4 characters and less than 13","SPGCUSERTEXT.makeFirstResponder(true);")
        return
    
    if not username.isalpha():
        TGECall("MessageBoxOK","Invalid Username","Your username must not include numbers or other punctuation.","SPGCUSERTEXT.makeFirstResponder(true);")
        return
    
    IRCConnect(username)
    TGEEval("Canvas.popDialog(SPGlobalChatGui);")


def Setup():
    SimMind.directConnect = ""
    EnumSinglePlayerWorlds()


def PyExec():
    Setup()
    #TGEObject("SINGLEPLAYER_WORLDNAME").setText("MyWorld")
    TGEExport(OnNewSingleWorld,"Py","OnNewSingleWorld","desc",1,1)
    TGEExport(OnLoadSingleWorld,"Py","OnLoadSingleWorld","desc",1,1)
    TGEExport(OnReallyDeleteSingleWorld,"Py","OnReallyDeleteSingleWorld","desc",1,1)
    TGEExport(OnDeleteSingleWorld,"Py","OnDeleteSingleWorld","desc",1,1)
    TGEExport(OnSPGlobalChatLogin,"Py","OnSPGlobalChatLogin","desc",1,1)
    
    if RPG_BUILD_DEMO:
        TGESetGlobal("$Py::FREEEDITION",1)
        TGEObject("NPN_ONE").visible = True
        TGEObject("NPN_TWO").visible = True
    else:
        TGESetGlobal("$Py::FREEEDITION",0)
        TGEObject("NPN_ONE").visible = False
        TGEObject("NPN_TWO").visible = False


