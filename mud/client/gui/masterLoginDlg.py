# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword

#
#

def Connected(perspective):
    TGECall("CloseMessagePopup")
    
    from masterGui import Setup
    Setup(perspective)
        
    #RegPerspective.callRemote("RegistrationAvatar","submitKey",regkey,email).addCallbacks(Result,Failure)
    

def Failure(reason):
    TGECall("CloseMessagePopup")
    
    #todo, proper error messages
    #TGECall("MessageBoxOK","Error!",reason)        
    TGEEval("Canvas.setContent(MainMenuGui);")
    TGECall("MessageBoxOK","Error!",reason.getErrorMessage())        
    
def DoMasterLogin():
    
    from masterGui import MasterPerspective
    if MasterPerspective and not MasterPerspective.broker.disconnected:
        from masterGui import Setup
        Setup(MasterPerspective)        
        return
    
    regkey = TGEObject("MASTERLOGIN_PUBLICNAME").getValue()
    password = TGEObject("MASTERLOGIN_PASSWORD").getValue()
    
    #if you just paste into a textctrl it's variable isn't being updated, unless you type into it... grrrr
    TGESetGlobal("$pref::PublicName",regkey)
    TGESetGlobal("$pref::MasterPassword",password)
    
    #print type(regkey),type(email),type(verify)
    
    if not len(regkey) or not len(password):
        TGEEval("Canvas.setContent(MainMenuGui);")
        TGECall("MessageBoxOK","Error","Invalid username or password.")                
        return
    
    TGEObject("PATCHLOGIN_PUBLICNAME").setText(regkey)
    TGEObject("PATCHLOGIN_PASSWORD").setText(password)
    TGEObject("MASTERLOGIN_PUBLICNAME").setText(regkey)
    TGEObject("MASTERLOGIN_PASSWORD").setText(password)



    #todo, validate email form
    masterIP = TGEGetGlobal("$Py::MasterIP")
    masterPort = int(TGEGetGlobal("$Py::MasterPort"))
    
    TGECall("MessagePopup","Logging into Master Server...","Please wait...")
    
    factory = pb.PBClientFactory()
    reactor.connectTCP(masterIP,masterPort,factory)
    from md5 import md5
    password = md5(password).digest()

    factory.login(UsernamePassword("%s-Player"%regkey, password),pb.Root()).addCallbacks(Connected, Failure)

def PyExec():
    pass

