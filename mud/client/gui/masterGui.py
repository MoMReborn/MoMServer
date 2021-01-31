# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.shared.worlddata import WorldInfo

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword
from mud.world.defines import *
from mud.gamesettings import *
import os
import time

MasterPerspective = None

WORLDS = []
FILTERED_WORLDS = []
WORLDINFO = None
CWORLDNAME = None

WORLDINFOCACHE = {}

RETRIEVETIMES = {}

WORLDTEXT = """<shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98><font:Arial Bold:20>Minions of Mirth
<font:Arial:18><color:BBBBFF>World Server

<font:Arial:16><color:FFFFFF>No Information Available"""

#bah
WORLDTEXT = WORLDTEXT.replace('\r',"\\r")
WORLDTEXT = WORLDTEXT.replace('\n',"\\n") #valid quote
WORLDTEXT = WORLDTEXT.replace('\a',"\\a") #valid quote
WORLDTEXT = WORLDTEXT.replace('"','\\"') #invalid quote

RETRIEVETEXT = """<shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98><font:Arial Bold:20>Minions of Mirth
<font:Arial:18><color:BBBBFF>World Server

<font:Arial:20><color:FFFFFF>Retrieving World Server Information"""

#bah
RETRIEVETEXT = RETRIEVETEXT.replace('\r',"\\r")
RETRIEVETEXT = RETRIEVETEXT.replace('\n',"\\n") #valid quote
RETRIEVETEXT = RETRIEVETEXT.replace('\a',"\\a") #valid quote
RETRIEVETEXT = RETRIEVETEXT.replace('"','\\"') #invalid quote


SERVER_PREMIUM = 0
SERVER_FREE = 1
SERVER_PLAYER = 2
SERVER_PG = 3
SERVERTYPE = SERVER_PG

#if RPG_BUILD_DEMO:
#    SERVERTYPE = SERVER_FREE
    
MASTER_LOGIN_PLAYER = None
MASTER_LOGIN_GUARDIAN = None
MASTER_LOGIN_IMMORTAL = None


def GotWorldInfo(results,perspective,worldName):
    perspective.broker.transport.loseConnection()
    text,banner = results
    #print text,banner,perspective,worldName
    
    
    text = text.replace('\r',"\\r")
    text = text.replace('\n',"\\n") #valid quote
    text = text.replace('\a',"\\a") #valid quote
    text = text.replace('"','\\"') #invalid quote

    hasBanner = False
    if banner and len(banner):
        hasBanner = True
        #save it off to disc
        filename = "./%s/cache/worldbanners/%s.jpg"%(GAMEROOT,worldName)
        try:
            path = os.path.dirname(filename)
            
            os.makedirs(path)
        except:
            pass
        
        f = file(filename,"wb")
        f.write(banner)
        f.close()
        
        
    WORLDINFOCACHE[worldName]=(text,hasBanner)
    
    if CWORLDNAME == worldName:
        SetWorldInfo(worldName)
        
    

#World Graphic and Info stuff
def QueryWorldInfoConnected(perspective,worldName):
    perspective.callRemote("QueryAvatar","retrieveWorldInfo").addCallbacks(GotWorldInfo,QueryWorldInfoFailure,(perspective,worldName,),{},(worldName,))

def QueryWorldInfoFailure(reason,worldName):
    if CWORLDNAME == worldName:
        bitmap = TGEObject("WORLD_BANNER")
        bitmap.setBitmap("~/data/ui/elements/mmws")
        TGEEval('WORLD_DESC.setText("%s");'%WORLDTEXT)

    

def QueryWorldInfo(worldname):
    for winfo in WORLDS:
        if winfo.worldName == worldname:
            factory = pb.PBClientFactory()
            reactor.connectTCP(winfo.worldIP,winfo.worldPort,factory)
            from md5 import md5
            password = md5("").digest()
            factory.login(UsernamePassword("Query-Query", password),pb.Root()).addCallbacks(QueryWorldInfoConnected, QueryWorldInfoFailure,(winfo.worldName,),{},(winfo.worldName,))
            return True
    return False
            
    
#End World Graphic and Info Stuff


def NewPlayerConnected(npperspective):
    from worldLoginDlg import Setup
    Setup(npperspective,WORLDINFO)

def WorldPasswordResult(args):
    if not args[0]:
        wname = args[3]
        if "Premium " not in wname and "Free " not in wname:
            wn = wname.replace(" ","_")
            TGESetGlobal("$pref::WorldPassword_%s"%wn,args[2])
        
        
        TGESetGlobal("$pref::WorldPassword",args[2])
    
    TGECall("MessageBoxOK","World Password Request",args[1])
    
    
def OnMasterRequestWorldPassword():
    if not MasterPerspective:
        return
    tc=TGEObject("MasterWorldList")
    sr = int(tc.getSelectedId())
    winfo = FILTERED_WORLDS[sr]
    if "Free " in winfo.worldName or "Premium " in winfo.worldName:
        return
    
    MasterPerspective.callRemote("EnumWorldsAvatar","requestWorldPassword",winfo.worldName).addCallbacks(WorldPasswordResult,Failure)
    
    
def PlayerSubmittedToWorld(result):
    
    
    if not result[0]:
        TGECall("CloseMessagePopup")
        TGEEval(r'MessageBoxOK("Error","%s");'%(result[1]))
        return
    
    from mud.client.playermind import PlayerMind
    from mud.client.gui.worldLoginDlg import PlayerConnected,SetWorldInfo
    from mud.client.gui.worldLoginDlg import Failure as MyFailure
    
    SetWorldInfo(WORLDINFO)
    
    mind = PlayerMind()
    #mind.ircNick = TGEGetGlobal("$pref::PublicName")
    if not RPG_BUILD_DEMO:
        if "Free " in WORLDINFO.worldName:
            mind.freeWorld = True
    factory = pb.PBClientFactory()
    factory.unsafeTracebacks = PB_UNSAFE_TRACEBACKS
    #WORLDINFO.worldIP = '10.0.0.4'
    
    mind.worldIP = WORLDINFO.worldIP
    
    reactor.connectTCP(WORLDINFO.worldIP,WORLDINFO.worldPort,factory)    
    
    
    role = "Player"
    if TGEGetGlobal("$pref::GM_LOGIN") == "1":
        TGESetGlobal("$pref::GM_LOGIN_ROLE","Player")
        if int(MASTER_LOGIN_GUARDIAN.getValue()):
            TGESetGlobal("$pref::GM_LOGIN_ROLE","Guardian")
            role = "Guardian"
        if int(MASTER_LOGIN_IMMORTAL.getValue()):
            TGESetGlobal("$pref::GM_LOGIN_ROLE","Immortal")
            role = "Immortal"
    
    from md5 import md5
    password = md5(result[1]).digest()

    factory.login(UsernamePassword("%s-%s"%(TGEGetGlobal("$pref::PublicName"),role), password),mind).addCallbacks(PlayerConnected, MyFailure,(mind,))
    

def OnMasterSelectWorld():
    global WORLDINFO
    pname = TGEGetGlobal("$pref::PublicName")
    if pname == "ThePlayer": #this causes problems, conflict with Single Player ?
        TGESetGlobal("$pref::PublicName","")
        
    tc=TGEObject("MasterWorldList")
    sr = int(tc.getSelectedId())
    winfo = FILTERED_WORLDS[sr]
    
    WORLDINFO = winfo
    
    if "Free " not in WORLDINFO.worldName and RPG_BUILD_DEMO:
        TGECall("MessageBoxOK","Premium Edition Required","This server requires the Premium Edition.\n\nPlease see http://www.prairiegames.com for more information.")
        return
    
    #if "Free " in WORLDINFO.worldName:
    TGEObject("SPONSORBREAK_BAR").visible = False
        
    if "Free " in WORLDINFO.worldName or "Premium " in WORLDINFO.worldName:
        TGESetGlobal("$Py::WORLDNAME","PrairieWorld")
    else:
        TGESetGlobal("$Py::WORLDNAME",winfo.worldName)
    
    #if the world has a player password, snag it here
    password=""
    
    #connect to world and see if we have an account
    
    TGECall("MessagePopup","Contacting World...","Please wait...")
    
    try:
        wn = WORLDINFO.worldName.replace(" ","_")        
        x = TGEGetGlobal("$pref::WorldPassword_%s"%wn)
        if len(x) == 8:
            TGESetGlobal("$pref::WorldPassword",x)
    except:
        pass
        
    if "Premium " in winfo.worldName or "Free " in winfo.worldName:
        
        #official server
        MasterPerspective.callRemote("PlayerAvatar","submitPlayerToWorld",winfo.worldName).addCallbacks(PlayerSubmittedToWorld,Failure)
    else:
        factory = pb.PBClientFactory()
        reactor.connectTCP(winfo.worldIP,winfo.worldPort,factory)
        from md5 import md5
        password = md5(password).digest()

        factory.login(UsernamePassword("NewPlayer-NewPlayer", password),pb.Root()).addCallbacks(NewPlayerConnected, Failure)
    
    
    
    
    #if the world has a zone password prompt the player to enter it or whatever
    
    #for now no passworded worlds
    #we can log off master at this point, if we can connect to world
    
    #we need world login information
    

#MASTERGUI_WORLDSCROLL /
#MasterWorldList  /  
#MASTER_GUI_PASSWORDTEXT
#MASTER_GUI_STATUSTEXT
#MASTERGUI_POPULATION

#MASTERGUI_SS0

def EnumLiveWorldsResults(worlds):
    TGECall("CloseMessagePopup")
    global WORLDS, FILTERED_WORLDS
    WORLDS = worlds
    FILTERED_WORLDS = []
    
    TGEObject("MASTERGUI_WORLDPANEL").visible = True
    
    wscroll = TGEObject("MASTERGUI_WORLDSCROLL")
    wlist = TGEObject("MasterWorldList")
    passtext = TGEObject("MASTER_GUI_PASSWORDTEXT")
    statustext = TGEObject("MASTER_GUI_STATUSTEXT")
    wnametext = TGEObject("MASTERGUI_WORLDNAME")

    ss = []
    for x in xrange(0,10):
        s = TGEObject("MASTERGUI_SS%i"%x)
        s.visible = False
        ss.append(s)
    
    if SERVERTYPE == SERVER_PG:
        wscroll.extent = "141 215"
        wlist.extent = "146 8"
        passtext.visible = False
        statustext.visible=False
        wnametext.visible = False
        
    else:
        wscroll.extent = "260 215"
        wlist.extent = "256 51"
        passtext.visible = True
        statustext.visible=True
        wnametext.visible = True
        
        
    
    
    tc=TGEObject("MasterWorldList")
    tc.setVisible(False)
    tc.clear()
    i=0
    
    for wi in worlds:
        
        pg = "FREE " in wi.worldName.upper() or "PREMIUM " in wi.worldName.upper()
        
        if pg and SERVERTYPE != SERVER_PG:
            continue
        
        if not pg and SERVERTYPE==SERVER_PG:
            continue
        
        
        FILTERED_WORLDS.append(wi)
        
            
        pw = 'N'
        if wi.hasPlayerPassword:
            pw = 'Y'
        
        p = "-1/-1"

        if SERVERTYPE == SERVER_PG:# or SERVERTYPE == SERVER_PREMIUM:
            p = "Open"
            if hasattr(wi,"maxPlayers"):
                if wi.numLivePlayers<wi.maxPlayers:
                    p="Open"
                else:
                    p="Full"
        #wi.worldIP,wi.worldPort
        elif hasattr(wi,"maxPlayers"):
            p="%i/%i"%(wi.numLivePlayers,wi.maxPlayers)
        
        if SERVERTYPE == SERVER_PG:
            tc.addRow(i,"%s"%wi.worldName)
            ss[i].visible = True
            f = float(wi.numLivePlayers)/80.0
            if f > 1.0:
                f = 1.0
            ss[i].setValue(f)
        else:
            tc.addRow(i,"%s \t %s \t %s"%(wi.worldName,p,pw))
            
        i+=1
        
                
    #tc.sort(1) # this sorts alphabetically
    tc.setSelectedRow(0)
    tc.scrollVisible(0)
    tc.setActive(True)#this should be based on any worlds found
    tc.setVisible(True)
    
    PyOnWorldChoose()
    
def Failure(reason):
    TGECall("CloseMessagePopup")
    TGECall("MessageBoxOK","Error!",reason.value)        

    
def OnRefreshWorlds():
    global MasterPerspective
    if not MasterPerspective:
        return
    TGECall("MessagePopup","Refreshing Worlds...","Please wait...")

        
    #self.liveWorldsListCtrl.DeleteAllItems()    

    #self.progressDlg.Update(0,"Enumerating Live Worlds...")           
    #self.progressDlg.Show()
    try:
        MasterPerspective.callRemote("EnumWorldsAvatar","enumLiveWorlds", False, RPG_BUILD_DEMO,False,not RPG_BUILD_LIVE).addCallbacks(EnumLiveWorldsResults,Failure)
    except:
        TGECall("CloseMessagePopup")
        TGECall("MessageBoxOK","Error!","Connection to the Master Server has been lost...")        


def MasterLogout():
    global MasterPerspective
    if MasterPerspective:
        MasterPerspective.broker.transport.loseConnection()
    MasterPerspective = None


def OnMasterGuiLogout():
    MasterLogout()
    TGEEval("Canvas.setContent(MainMenuGui);")
    TGESetGlobal("$Py::WORLDNAME","")


DISPLAYPATCH = True
def Setup(perspective):
    global DISPLAYPATCH
    from mud.client.playermind import SimMind
    SimMind.directConnect = ""
    
    TGEObject("MASTERGUI_WORLDPANEL").visible = False
    
    MASTER_LOGIN_PLAYER.visible = False
    MASTER_LOGIN_GUARDIAN.visible = False
    MASTER_LOGIN_IMMORTAL.visible = False
    
    if TGEGetGlobal("$pref::GM_LOGIN") == "1":
        MASTER_LOGIN_PLAYER.visible = True
        MASTER_LOGIN_GUARDIAN.visible = True
        MASTER_LOGIN_IMMORTAL.visible = True
        
        v =TGEGetGlobal("$pref::GM_LOGIN_ROLE") 
        if v!=None and v.lower() == "guardian":
            MASTER_LOGIN_PLAYER.setValue(0)
            MASTER_LOGIN_GUARDIAN.setValue(1)
            MASTER_LOGIN_IMMORTAL.setValue(0)
        elif v!= None and v.lower() == "immortal":
            MASTER_LOGIN_PLAYER.setValue(0)
            MASTER_LOGIN_GUARDIAN.setValue(0)
            MASTER_LOGIN_IMMORTAL.setValue(1)
        else:
            MASTER_LOGIN_PLAYER.setValue(1)
            MASTER_LOGIN_GUARDIAN.setValue(0)
            MASTER_LOGIN_IMMORTAL.setValue(0)
    
    
    from patcherGui import DisplayPatchInfo
    TGESetGlobal("$Py::ISSINGLEPLAYER",0)
    TGESetGlobal("$Py::LastTell","")
    global MasterPerspective
    MasterPerspective = perspective
            
    TGEEval("Canvas.setContent(MasterGui);")

    if DISPLAYPATCH:
        DISPLAYPATCH = False
        DisplayPatchInfo()
        
    
    TGEObject("SPONSORBREAK_BAR").visible = False

    
    OnRefreshWorlds()
    
def SetWorldInfo(worldname):
    
    text,hasBanner = WORLDINFOCACHE[worldname]
    if not text:
        text = WORLDTEXT
    TGEEval('WORLD_DESC.setText("%s");'%text)
    bitmap = TGEObject("WORLD_BANNER")
    if not hasBanner:
        bitmap.setBitmap("~/data/ui/elements/mmws")
    else:
        bitmap.setBitmap("~/cache/worldbanners/%s.jpg"%worldname)

def PyOnWorldChoose():
    global CWORLDNAME
    tc=TGEObject("MasterWorldList")
    sr = int(tc.getSelectedId())
    try:
        winfo = FILTERED_WORLDS[sr]
    except:
        return
    
    CWORLDNAME = winfo.worldName
    
    i = WORLDINFOCACHE.get(winfo.worldName,None)
    
    if i:
        #cached
        #WORLD_BANNER
        #WORLD_DESC
        SetWorldInfo(winfo.worldName)
    else:
        #not cached
        if RETRIEVETIMES.has_key(winfo.worldName):
            t = RETRIEVETIMES[winfo.worldName]
            t = time.time()-t

            if t < 30:
                bitmap = TGEObject("WORLD_BANNER")
                bitmap.setBitmap("~/data/ui/elements/mmws")
                TGEEval('WORLD_DESC.setText("%s");'%WORLDTEXT)
                return
            
        bitmap = TGEObject("WORLD_BANNER")
        bitmap.setBitmap("~/data/ui/elements/mmws")
        TGEEval('WORLD_DESC.setText("%s");'%RETRIEVETEXT)

        RETRIEVETIMES[winfo.worldName]=time.time()
        QueryWorldInfo(winfo.worldName)
    
def PyOnDirectSelectWorld():
    global WORLDINFO
    TGEEval("Canvas.popDialog(DirectConnectWnd);")
    pname = TGEGetGlobal("$pref::PublicName")
    if pname == "ThePlayer": #this causes problems, conflict with Single Player ?
        TGESetGlobal("$pref::PublicName","")
        
    ip = TGEObject("DIRECTIP_IP").getValue()  

    #FIX ME!!!
    if "72.36." in ip:
        return
    if "72.232." in ip:
        return
    
    TGECall("MessagePopup","Contacting World...","Please wait...")

      
    port = TGEObject("DIRECTIP_PORT").getValue()    
    #if you just paste into a textctrl it's variable isn't being updated, unless you type into it... grrrr
    TGESetGlobal("$pref::DirectConnectIP",ip)
    TGESetGlobal("$pref::DirectConnectPort",port)
    
    try:
        port = int(port)
    except:
        port = 2006
        
    from mud.client.playermind import SimMind
    SimMind.directConnect = ip


    WORLDINFO = WorldInfo()
    WORLDINFO.worldName = "DirectConnection"
    WORLDINFO.worldIP = ip
    WORLDINFO.worldPort = port
    WORLDINFO.hasPlayerPassword = True
    
    
    TGESetGlobal("$Py::WORLDNAME","DirectConnection")

    password = ""
    from md5 import md5
    password = md5(password).digest()

    factory = pb.PBClientFactory()
    reactor.connectTCP(ip,port,factory)
    factory.login(UsernamePassword("NewPlayer-NewPlayer", password),pb.Root()).addCallbacks(NewPlayerConnected, Failure)

    

    
#DIRECTIP_TEXT
#Py::OnDirectSelectWorld();   
#Py::OnDirectRequestPassword(); 
#$pref::DirectConnectIP

def PyOnFreeServers():
    global SERVERTYPE
    if SERVERTYPE != SERVER_FREE:
        SERVERTYPE=SERVER_FREE
        EnumLiveWorldsResults(WORLDS)
        
def PyOnPlayerServers():
    global SERVERTYPE
    if SERVERTYPE != SERVER_PLAYER:
        SERVERTYPE=SERVER_PLAYER
        EnumLiveWorldsResults(WORLDS)
    
def PyOnPremiumServers():
    global SERVERTYPE
    if SERVERTYPE != SERVER_PREMIUM:
        SERVERTYPE=SERVER_PREMIUM
        EnumLiveWorldsResults(WORLDS)

def PyOnPGServers():
    global SERVERTYPE
    if SERVERTYPE != SERVER_PG:
        SERVERTYPE=SERVER_PG
        EnumLiveWorldsResults(WORLDS)



def PyExec():

    global MASTER_LOGIN_PLAYER,MASTER_LOGIN_GUARDIAN,MASTER_LOGIN_IMMORTAL
    
    MASTER_LOGIN_PLAYER = TGEObject("MASTER_LOGIN_PLAYER")
    MASTER_LOGIN_GUARDIAN = TGEObject("MASTER_LOGIN_GUARDIAN")
    MASTER_LOGIN_IMMORTAL = TGEObject("MASTER_LOGIN_IMMORTAL")
    
    
    
    TGEExport(OnMasterSelectWorld,"Py","OnMasterSelectWorld","desc",1,1)
    TGEExport(OnMasterGuiLogout,"Py","OnMasterGuiLogout","desc",1,1)
    TGEExport(OnRefreshWorlds,"Py","OnRefreshWorlds","desc",1,1)
    TGEExport(OnMasterRequestWorldPassword,"Py","OnMasterRequestWorldPassword","desc",1,1)
    TGEExport(PyOnWorldChoose,"Py","OnWorldChoose","desc",1,1)
    TGEExport(PyOnDirectSelectWorld,"Py","OnDirectSelectWorld","desc",1,1)
    #TGEExport(PyOnDirectRequestPassword,"Py","OnDirectRequestPassword","desc",1,1)
    
    
    #Py::OnFreeServers();
    #Py::OnPremiumServers();
    #Py::OnPlayerServers(); #only premium
    
    TGEExport(PyOnFreeServers,"Py","OnFreeServers","desc",1,1)
    TGEExport(PyOnPremiumServers,"Py","OnPremiumServers","desc",1,1)
    TGEExport(PyOnPlayerServers,"Py","OnPlayerServers","desc",1,1)
    TGEExport(PyOnPGServers,"Py","OnPGServers","desc",1,1)
    
    #if RPG_BUILD_DEMO:
    #    TGEObject("SERVER_FREE_BUTTON").performClick()
    #else:
    #    TGEObject("SERVER_PREMIUM_BUTTON").performClick()
        
    TGEObject("SERVER_PGSERVERS_BUTTON").performClick()
    
    
#Py::OnPGServers();
#
    
