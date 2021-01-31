# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#this protocol will be made secure, for now it simulates the actual process minus 
#even simple security

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *

from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword

RegPerspective = None

def Result(results):
    TGECall("CloseMessagePopup")
    
    global RegPerspective
    RegPerspective=None
    
    ret = results[0]
    msg = results[1]
    pw = results[2]
    regkey = results[3]
    
    
    if ret:
        title = "Error!"
    else:
        #success
        title = "Success!"
        #regkey = TGEObject("REGISTERDLG_REGKEY").getValue()
        publicName = TGEObject("REGISTERDLG_PUBLICNAME").getValue()
        
        TGEObject("MASTERLOGIN_PUBLICNAME").setValue(publicName)
        TGEObject("MASTERLOGIN_PASSWORD").setValue(pw)
        TGEObject("PATCHLOGIN_PUBLICNAME").setValue(publicName)
        TGEObject("PATCHLOGIN_PASSWORD").setValue(pw)
        
        TGESetGlobal("$pref::MasterPassword",pw)
        TGESetGlobal("$pref::RegKey",regkey)
        TGESetGlobal("$pref::PublicName",publicName)
        
    
    if not ret:
        TGEEval('canvas.popDialog(registerDlg);')
    
    
    TGEEval(r'MessageBoxOK("%s","%s");'%(title,msg))

def Connected(perspective):
    TGECall("CloseMessagePopup")
    global RegPerspective
    RegPerspective = perspective
    
    regkey = TGEObject("REGISTERDLG_REGKEY").getValue()
    publicName = TGEObject("REGISTERDLG_PUBLICNAME").getValue()
    email = TGEObject("REGISTERDLG_EMAILADDRESS").getValue()
    
    TGECall("MessagePopup","Communicating with Master Server...","Submitting Registation Information...")
    
    if RPG_BUILD_DEMO:
        fromProduct = ""
    else:
        fromProduct = "MOM"
        
    RegPerspective.callRemote("RegistrationAvatar","submitKey",regkey,email,publicName,fromProduct).addCallbacks(Result,Failure)
    

def Failure(reason):
    TGECall("CloseMessagePopup")
    TGECall("MessageBoxOK","Error!",reason.value)        
    global RegPerspective
    RegPerspective=None
    
#REGISTERDLG_REGKEY
#REGISTERDLG_PUBLICNAME
#REGISTERDLG_EMAILADDRESS
#REGISTERDLG_VERIFYEMAILADDRESS

def OnRegister():
    
    
    global RegPerspective
    
    regkey = TGEObject("REGISTERDLG_REGKEY").getValue()
    publicName = TGEObject("REGISTERDLG_PUBLICNAME").getValue()
    email = TGEObject("REGISTERDLG_EMAILADDRESS").getValue()
    verify = TGEObject("REGISTERDLG_VERIFYEMAILADDRESS").getValue()
    
    
    #if you just paste into a textctrl it's variable isn't being updated, unless you type into it... grrrr
    
    #print type(regkey),type(email),type(verify)
    
    try:
        #if not len(regkey) or not len(email) or not len(verify) or not len(publicName):
        if not len(email) or not len(verify) or not len(publicName):
            return
    except:
        return
        
    if len(publicName) < 4:
        TGECall("MessageBoxOK","Invalid Entry","Your public name must be at least 4 characters.")
        return
    
    if not publicName.isalpha():
        TGECall("MessageBoxOK","Invalid Entry","Your public name must not have numbers or other punctuation.")
        return
    
    if email != verify:
        TGECall("MessageBoxOK","Error!","Emails don't match.  Please carefully enter your email...")        
        return
    
    if "@" not in email:
        TGECall("MessageBoxOK","Error!","Invalid email address.  Please carefully enter your email...")        
        return
        
        
    #todo, validate email form
    masterIP = TGEGetGlobal("$Py::MasterIP")
    masterPort = int(TGEGetGlobal("$Py::MasterPort"))
    
    TGECall("MessagePopup","Communicating with Master Server...","Please wait...")
    
    factory = pb.PBClientFactory()
    reactor.connectTCP(masterIP,masterPort,factory)
    from md5 import md5
    password = md5("Registration").digest()

    factory.login(UsernamePassword("Registration-Registration",password),pb.Root()).addCallbacks(Connected, Failure)

def PyExec():
    TGEExport(OnRegister,"Py","OnRegister","desc",1,1)
    
    
    

    
    