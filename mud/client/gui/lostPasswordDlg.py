# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



from tgenative import *
from mud.tgepython.console import TGEExport

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword


#need publicname, email address tied to account

#GuiTextEditCtrl(LOSTPASSWORD_PUBLICNAME) 
#GuiTextEditCtrl(LOSTPASSWORD_EMAIL) 
#Py::OnRequestLostPassword();

PUBLICNAME = ""
EMAILADDRESS = ""

RegPerspective = None

def Result(results):
    global RegPerspective
    RegPerspective = None
    
    TGECall("CloseMessagePopup")
    

    ret = results[0]
    msg = results[1]
    
    if ret:
        title = "Error!"
    else:
        #success
        title = "Success!"
        
    
    if not ret:
        TGEEval('canvas.popDialog(LostPasswordDlg);')
    
    
    TGEEval(r'MessageBoxOK("%s","%s");'%(title,msg))


    

def Connected(perspective):
    
    global RegPerspective
    RegPerspective  = perspective
    
    TGECall("CloseMessagePopup")

    TGECall("MessagePopup","Communicating with Master Server...","Requesting password...")
    
        
    perspective.callRemote("RegistrationAvatar","requestPassword",PUBLICNAME,EMAILADDRESS).addCallbacks(Result,Failure)
    

def Failure(reason):
    TGECall("CloseMessagePopup")
    TGECall("MessageBoxOK","Error!",reason.value)        
    
def OnRequestLostPassword():
    global PUBLICNAME,EMAILADDRESS
    pname = TGEObject("LOSTPASSWORD_PUBLICNAME").getValue()
    email = TGEObject("LOSTPASSWORD_EMAIL").getValue()

    if not pname:
        TGECall("MessageBoxOK","Lost Password","Invalid Public Name")
        return

    if "@" not in email or "." not in email:
        TGECall("MessageBoxOK","Lost Password","Invalid email address")
        return
    
    PUBLICNAME,EMAILADDRESS = pname,email
    
    masterIP = TGEGetGlobal("$Py::MasterIP")
    masterPort = int(TGEGetGlobal("$Py::MasterPort"))
    
    TGECall("MessagePopup","Contacting Master Server...","Please wait...")
    
    factory = pb.PBClientFactory()
    reactor.connectTCP(masterIP,masterPort,factory)
    from md5 import md5
    password = md5("Registration").digest()

    factory.login(UsernamePassword("Registration-Registration", password),pb.Root()).addCallbacks(Connected, Failure)


def PyExec():
    TGEExport(OnRequestLostPassword,"Py","OnRequestLostPassword","desc",1,1)
