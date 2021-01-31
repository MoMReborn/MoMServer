# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.client.playermind import PlayerMind

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword

NewPlayerPerspective = None
WORLDINFO = None

def SetWorldInfo(wi):
    global WORLDINFO
    WORLDINFO = wi

def PlayerConnected(perspective,mind):
    
        TGECall("CloseMessagePopup")
        mind.setPerspective(perspective)
        
        #alright, we are connected time to make the donuts
        from worldGui import Setup
        Setup(perspective)
        
        pw = TGEObject("WORLDLOGIN_PASSWORD").getValue()
        if "Premium " not in WORLDINFO.worldName and "Free " not in WORLDINFO.worldName:
            wn = WORLDINFO.worldName.replace(" ","_")
            TGESetGlobal("$pref::WorldPassword_%s"%wn,pw)
        
        TGESetGlobal("$pref::WorldPassword",pw)


def OnWorldLoginCancel():
    global NewPlayerPerspective
    if NewPlayerPerspective:
        NewPlayerPerspective.broker.transport.loseConnection()
    NewPlayerPerspective = None
    
    from masterLoginDlg import DoMasterLogin
    DoMasterLogin()


def OnWorldLogin(args):
    
    guardian = int(args[1])==1
    immortal = int(args[1])==2
    
    avatar = "Player"
    
    if guardian:
        avatar = "Guardian"
    
    if immortal:
        avatar = "Immortal"
    
    worldpassword = TGEObject("WORLDLOGIN_PASSWORD").getValue()
    
    if len(worldpassword) < 6:
        TGECall("MessageBoxOK","Error!","World passwords are at least 6 characters long.")        
    else:
        TGECall("MessagePopup","Logging into world...","Please wait...")
        
        factory = pb.PBClientFactory()
        reactor.connectTCP(WORLDINFO.worldIP,WORLDINFO.worldPort,factory)
        mind = PlayerMind()
        from md5 import md5
        password = md5(worldpassword).digest()

        factory.login(UsernamePassword("%s-%s"%(TGEGetGlobal("$pref::PublicName"),avatar), password),mind).addCallbacks(PlayerConnected, Failure,(mind,))
    
    
def GotNewPlayerResult(result):
    
    #done with this perspective
    global NewPlayerPerspective
    NewPlayerPerspective = None

    
    TGECall("CloseMessagePopup")
    
    code = result[0]
    msg = result[1]
    pw = result[2]
    
    if code:
        title = "Error!"
    else:
        #success
        title = "Success!"
        TGESetGlobal("$pref::WorldPassword",pw)
        if "Premium " not in WORLDINFO.worldName and "Free " not in WORLDINFO.worldName:
            wn = WORLDINFO.worldName.replace(" ","_")
            TGESetGlobal("$pref::WorldPassword_%s"%wn,pw)
        TGEObject("WORLDLOGIN_PASSWORD").setValue(pw)
        TGEEval("Canvas.pushDialog(WorldLoginDlg);")
    
    TGECall("MessageBoxOK",title,msg)
    
        
def OnWorldRegister():
    fname = TGEObject("WORLDREGISTER_FANTASYNAME").getValue()
    
    pw = TGEObject("WORLDREGISTER_PLAYERPASSWORD").getValue()
        
    if len(fname) < 4:
        TGECall("MessageBoxOK","Invalid Entry","Your avatar name must be at least 4 characters.")
        return
    
    if not fname.isalpha():
        TGECall("MessageBoxOK","Invalid Entry","Your avatar name must not have numbers or other punctuation.")
        return

        
    TGESetGlobal("$pref::FantasyName",fname)
    pname = TGEGetGlobal("$pref::PublicName")
    
    TGECall("MessagePopup","Creating Account...","Please wait...")
    NewPlayerPerspective.callRemote("NewPlayerAvatar","newPlayer",pname,fname,pw).addCallbacks(GotNewPlayerResult,Failure)    
    
    

def GotQueryPlayerResult(result):
    TGECall("CloseMessagePopup")
    if not result:
        #we ain't got no account
        TGEEval("Canvas.pushDialog(WorldRegisterDlg);")
    else:
        #done with this perspective
        global NewPlayerPerspective
        NewPlayerPerspective = None
        
        TGEEval("Canvas.pushDialog(WorldLoginDlg);")
        
def Failure(reason):
    
    TGECall("CloseMessagePopup")
    
    #todo, proper error messages
    #TGECall("MessageBoxOK","Error!",reason.value)        
    
    TGECall("MessageBoxOK","Error!",reason.getErrorMessage())        
    
    global NewPlayerPerspective
    if NewPlayerPerspective:
        NewPlayerPerspective.broker.transport.loseConnection()
    NewPlayerPerspective = None
    
    from masterLoginDlg import DoMasterLogin
    DoMasterLogin()


#we have selected the world on the MasterGui, we need to find out if we have an account on 
#the world and take the appropriate actions
def Setup(npperspective,winfo):
    global NewPlayerPerspective
    global WORLDINFO
    if winfo.hasPlayerPassword:
        TGEObject("WORLDREGISTER_PASSWORDTEXT").visible = True
        TGEObject("WORLDREGISTER_PLAYERPASSWORD").visible = True
    else:
        TGEObject("WORLDREGISTER_PASSWORDTEXT").visible = False
        TGEObject("WORLDREGISTER_PLAYERPASSWORD").visible = False
        
        
    WORLDINFO = winfo
    NewPlayerPerspective = npperspective
    NewPlayerPerspective.callRemote("NewPlayerAvatar","queryPlayer",TGEGetGlobal("$pref::PublicName")).addCallbacks(GotQueryPlayerResult,Failure)
    
        

def PyExec():
    TGEExport(OnWorldRegister,"Py","OnWorldRegister","desc",1,1)
    TGEExport(OnWorldLogin,"Py","OnWorldLogin","desc",2,2)
    TGEExport(OnWorldLoginCancel,"Py","OnWorldLoginCancel","desc",1,1)
