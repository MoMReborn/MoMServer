# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#I have to disable this on client until it has SSL 
#from twisted.internet.iocpreactor import install
#install()

import imp, os, sys,time,shutil,traceback
from mud.gamesettings import *

if sys.platform[:6] != 'darwin':
    
    
    import win32con
    import win32api
    import win32event
    import winerror
    import win32gui
    import struct

    #only allow one instance
    if "-patch" in sys.argv:
        HMUTEX = win32event.CreateMutex(None, 1, "PrairieGamesMinionsOfMirthPatcher")
    else:
        HMUTEX = win32event.CreateMutex(None, 1, "PrairieGamesMinionsOfMirth")
        
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        win32api.MessageBox(0, 'There is another instance of MinionsOfMirth.exe running.  Please close this instance down or restart your computer and try again.', "Error",win32con.MB_OK)
        sys.exit()

        
def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])

def main():
    #if we're running from py2exe add the cwd
    if main_is_frozen():
        #maindir = get_main_dir()
        
        if sys.platform[:6] == 'darwin':
            #need to go up three folders
            os.chdir("../../../common")
            maindir = os.getcwd()
        else:
            
            os.chdir("../common")
            maindir = os.getcwd()
            

        sys.path.append(maindir)
        print "main dir",maindir            
        print "cwd",os.getcwd()
        
        
    

    #editor is importing this and running it
    import pytorque
    from twisted.internet import reactor
    from mud.world.core import CoreSettings
    
    sys.argv.append("-game")    
    sys.argv.append(GAMEROOT)
    
    if "-ide" in sys.argv:
        CoreSettings.IDE = True
        #we're launching from ide
        for v in sys.argv:
            if v.startswith("-idezone="):
                CoreSettings.IDE_ZONE = v[9:]
            if v.startswith("-editzone"):
                CoreSettings.IDE_EDITZONE = True
    
    pytorque.Init(len(sys.argv),sys.argv)
    
    
    import tgenative
    from tgenative import TGESetGlobal,TGEGetGlobal,TGEEval
 
    from mud.world.defines import RPG_BUILD_DEMO,RPG_BUILD_TESTING
    import mud.client
    import mud.client.jukebox

    if "-ide" in sys.argv:
        TGESetGlobal("$pref::developer",1)
        
    if RPG_BUILD_DEMO:
        gui = ["SinglePlayerGui","MultiplayerGui","NewCharacterGui","MainMenuGui","MasterGui","WorldGui","PatcherGui"]
        for g in gui:
            tgenative.TGEObject(g).setBitmap("~/client/ui/mom_menu_background_demo")
    elif RPG_BUILD_TESTING:
        gui = ["SinglePlayerGui","MultiplayerGui","NewCharacterGui","MainMenuGui","MasterGui","WorldGui","PatcherGui"]
        for g in gui:
            tgenative.TGEObject(g).setBitmap("~/client/ui/mom_menu_background_test")
    else:
        gui = ["SinglePlayerGui","MultiplayerGui","NewCharacterGui","MainMenuGui","MasterGui","WorldGui","PatcherGui"]
        for g in gui:
            tgenative.TGEObject(g).setBitmap("~/client/ui/mom_menu_background")
        
     
    cf = "./log_MoMChat.txt"
    gf = "./log_MoMGame.txt"
    
    if sys.platform[:6] != 'darwin':
        gf = "./log_Game.txt"
        cf = "./log_Chat.txt"

    from twisted.python.logfile import LogFile
    
    try:
        os.remove(cf)
    except:
        pass
        
    try:
        os.remove(gf)
    except:
        pass
    
    if sys.platform[:6] != 'darwin':    
        CoreSettings.LOGCHAT = LogFile("log_Chat.txt","./",None)
        CoreSettings.LOGGAME = LogFile("log_Game.txt","./",None)
    else:
        CoreSettings.LOGCHAT = LogFile("log_Chat.txt","./",None)
        CoreSettings.LOGGAME = LogFile("log_Game.txt","./",None)
        
    
    import datetime
    n = datetime.datetime.now()
    s = n.strftime("%A %B %d %I:%M:%S %p %Y")

    CoreSettings.LOGCHAT.write("\n-------------------------------------------\n")
    CoreSettings.LOGCHAT.write("%s - Chat Log Opened\n"%s)
    CoreSettings.LOGCHAT.write("-------------------------------------------\n")
    CoreSettings.LOGGAME.write("\n-------------------------------------------\n")
    CoreSettings.LOGGAME.write("%s - Game Log Opened\n"%s)
    CoreSettings.LOGGAME.write("-------------------------------------------\n")
    
    checkide = True
    while pytorque.Tick():
        if checkide:
            checkide = False
            if CoreSettings.IDE and CoreSettings.IDE_ZONE:
                TGEEval("Canvas.setContent(SinglePlayerGui);")
                from mud.client.gui.singleplayerGui import OnLoadSingleWorld
                OnLoadSingleWorld("editworld")

    # Make sure to clean up if we exited by shortcut.
    from mud.client.playermind import CLIENTEXITED,OnReallyQuit
    if not CLIENTEXITED:
        OnReallyQuit(True)

    sys.stdout = sys.oldstdout
    sys.stderr = sys.oldstderr
    
    CoreSettings.LOGCHAT.close()
    CoreSettings.LOGGAME.close()
    
    
    pytorque.Shutdown()
    
    
if __name__ == '__main__':
    if "-patch" in sys.argv:
        from patcher import RunPatcher
        RunPatcher()
    else:
        #import profile
        from twisted.python import log
        
        f = "./log_Client.txt"
        
        LOGFILE = file(f,"w")
        log.startLogging(LOGFILE,setStdout=True)

        #profile.run("main()","profile.prof")
        main()
        
    LOGFILE.close()
    
if sys.platform[:6] != 'darwin':
    win32api.CloseHandle(HMUTEX)
    
