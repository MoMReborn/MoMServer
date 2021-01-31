# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import imp
import os
import sys
from traceback import format_exc,print_exc,print_stack



try:
    RUNNING = True
    
    
    def main_is_frozen():
        return (hasattr(sys, "frozen") or # new py2exe
            hasattr(sys, "importers") # old py2exe
            or imp.is_frozen("__main__")) # tools/freeze
    
    
    if main_is_frozen():
        #maindir = get_main_dir()
        
        if sys.platform[:6] == 'darwin':
            #need to go up three folders
            os.chdir("../../../mom")
            maindir = os.getcwd()
        else:
            os.chdir("../common")
            maindir = os.getcwd()
        
        sys.path.append(maindir)
    
    
    import pytorque
    
    try:
        import win32api,win32process
    except ImportError:
        win32api = win32process = None
    
    
    USE_WX = "-wx" in sys.argv
    
    if sys.platform == 'win32' and not USE_WX:
        from twisted.internet.iocpreactor import install
    else:
        import wx
        from twisted.internet.wxreactor import install
    
    install()
    
    
    from twisted.internet import reactor
    
    
    
    if USE_WX:
        REACTOR = None
        
        
        class RedirectText:
            def __init__(self, ctrl):
                self.out = ctrl
            
            def write(self, string):
                self.out.WriteText(string)
        
        
        class MainPanel(wx.Panel):
            def __init__(self, parent, id):
                wx.Panel.__init__(self,parent,id)
                
                sizer = wx.BoxSizer(wx.VERTICAL)
                
                output = wx.TextCtrl(self,-1,"",size=(512,384), \
                    style=wx.TE_MULTILINE|wx.TE_READONLY)
                
                sys.stdout = RedirectText(output)
                sys.stderr = sys.stdout
                
                sizer.Add(output, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND,5)
                
                self.SetSizer(sizer)
                sizer.Fit(self)
        
        
        class MainFrame(wx.Frame):
            def __init__(self, parent, id, title):
                wx.Frame.__init__(self,parent,-1,title,size=wx.Size(512, 384), \
                    style=wx.CAPTION|wx.MINIMIZE_BOX|wx.SYSTEM_MENU| \
                    wx.TAB_TRAVERSAL|wx.CLOSE_BOX)
                
                menu = wx.Menu()
                menu.Append(wx.ID_EXIT,"E&xit","Terminate the program")
                menuBar = wx.MenuBar()
                menuBar.Append(menu, "&File")
                self.SetMenuBar(menuBar)
                wx.EVT_MENU(self, wx.ID_EXIT,self.DoExit)
                
                try:
                    mp = MainPanel(self,-1)
                    
                    sizer = wx.BoxSizer(wx.VERTICAL)
                    
                    sizer.Add(mp,0,wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND,0)
                    
                    self.SetSizer(sizer)
                    sizer.Fit(self)
                
                except:
                    print_exc()
                    return
            
            def DoExit(self, event):
                global RUNNING
                RUNNING = False
        
        
        class GMApp(wx.App):
            def OnInit(self):
                wx.InitAllImageHandlers()
                
                frame = MainFrame(None,-1,"Zone Server")
                frame.Centre()
                frame.Show(1)
                
                self.mainFrame = frame
                
                return True
        
        
        app = GMApp()
    
    
    
    def SetupProcessors(cluster):
        if sys.platform != "win32":
            return
        
        handle = win32api.GetCurrentProcess()
        processMask,systemMask = win32process.GetProcessAffinityMask(handle)
        
        ht = False
        if systemMask & 8:
            #we're going to count this as a hyperthreaded system
            #as we don't currently have any servers with > 2 physical cpu
            ht = True
        
        if cluster == 0:
            mask = 3 if ht else 1
        elif cluster == 1:
            mask = 12 if ht else 2
        else:
            mask = 1
        
        print "Setting Processor Affinity Mask to",mask
        win32process.SetProcessAffinityMask(handle,mask)
    
    
    if not main_is_frozen() and sys.platform == "win32":
        os.chdir(os.path.dirname(sys.argv[0]))
    
    from mud.gamesettings import *
    from mud.world.core import CoreSettings
    
    sys.argv.append("-game")
    sys.argv.append(GAMEROOT)
    
    pytorque.Init(len(sys.argv),sys.argv)
    
    if USE_WX:
        reactor.registerWxApp(app)
    
    DYNAMIC = '-dynamic' in sys.argv
    
    CLUSTER = 0
    for arg in sys.argv:
        if arg.startswith("-cluster="):
            CLUSTER = int(arg[9:])
            SetupProcessors(CLUSTER)
    
    
    from mud.simulation.simmind import NumPlayersInZone
    from mud.world.core import CoreSettings
    from tgenative import TGEGetGlobal,TGESetGlobal
    
    
    QUARANTINE = 0
    
    PRIORITY = 1
    TGESetGlobal("$Server::DedicatedSleeping",False)
    
    
    while pytorque.Tick() and RUNNING:
        num = NumPlayersInZone()
        if False:
            if not num:
                if PRIORITY:
                    TGESetGlobal("$Server::DedicatedSleeping",True)
                    PRIORITY = 0
                    win32process.SetPriorityClass( \
                        win32process.GetCurrentProcess(), \
                        win32process.IDLE_PRIORITY_CLASS)
                else:
                    win32api.Sleep(2000)
            elif not PRIORITY:
                TGESetGlobal("$Server::DedicatedSleeping",False)
                PRIORITY = 1
                win32process.SetPriorityClass(win32process.GetCurrentProcess(), \
                    win32process.NORMAL_PRIORITY_CLASS)
    
    if not RUNNING:
        sys.exit()
    
    if win32process != None:
        win32process.SetPriorityClass(win32process.GetCurrentProcess(), \
            win32process.NORMAL_PRIORITY_CLASS)
    
    pytorque.Shutdown()

except:
    print_stack()
    print format_exc()
    raw_input("Press Enter to terminate")
