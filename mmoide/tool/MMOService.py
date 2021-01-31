import ProjectEditor
#import DebuggerService
import UICommon
import Wizard
import database
import process
import os, sys, traceback, shutil
import wx
_ = wx.GetTranslation


class MMOService(wx.lib.pydocview.DocService):
    
    CREATE_MASTERDB_ID = wx.NewId()
    CREATE_CHARACTERDB_ID = wx.NewId()
    
    RUN_CLIENT_ID = wx.NewId()
    
    RUN_MASTERSERVER_ID = wx.NewId()
    RUN_CHARACTERSERVER_ID = wx.NewId()
    RUN_WORLDDAEMON_ID = wx.NewId()
    
    def InstallControls(self, frame, menuBar = None, toolBar = None, statusBar = None, document = None):
        
        menu = wx.Menu()
        
        index = menuBar.FindMenu(_("&World"))
        menuBar.Insert(index + 1, menu, _("&MMO"))

        menu = menuBar.GetMenu(menuBar.FindMenu(_("&MMO")))
        
        wx.EVT_MENU(frame, MMOService.RUN_CLIENT_ID, self.ProcessEvent)        
        menu.Append(MMOService.RUN_CLIENT_ID, ("Run MMO Client"), ("Runs the MMO Client"))
        
        menu.AppendSeparator()

        
        wx.EVT_MENU(frame, MMOService.RUN_MASTERSERVER_ID, self.ProcessEvent)        
        menu.Append(MMOService.RUN_MASTERSERVER_ID, ("Run Master Server"), ("Runs the Master Server"))

        wx.EVT_MENU(frame, MMOService.RUN_CHARACTERSERVER_ID, self.ProcessEvent)        
        menu.Append(MMOService.RUN_CHARACTERSERVER_ID, ("Run Character Server"), ("Runs the Character Server"))
        
        wx.EVT_MENU(frame, MMOService.RUN_WORLDDAEMON_ID, self.ProcessEvent)        
        menu.Append(MMOService.RUN_WORLDDAEMON_ID, ("Run World Daemon"), ("Runs the World Daemon"))
        
        menu.AppendSeparator()

        wx.EVT_MENU(frame, MMOService.CREATE_MASTERDB_ID, self.ProcessEvent)        
        menu.Append(MMOService.CREATE_MASTERDB_ID, ("Create Master DB"), ("Creates the Master Server Database"))

        wx.EVT_MENU(frame, MMOService.CREATE_CHARACTERDB_ID, self.ProcessEvent)        
        menu.Append(MMOService.CREATE_CHARACTERDB_ID, ("Create Character DB"), ("Creates the Character Server Database"))

        
    def ProcessEvent(self, event):
        
        id = event.GetId()
        
        if id == MMOService.CREATE_MASTERDB_ID:
            self.OnCreateMasterDB()

        if id == MMOService.CREATE_CHARACTERDB_ID:
            self.OnCreateCharacterDB()
            
        if id == MMOService.RUN_WORLDDAEMON_ID:
            self.OnRunWorldDaemon()

        if id == MMOService.RUN_CHARACTERSERVER_ID:
            self.OnRunCharacterServer()

        if id == MMOService.RUN_MASTERSERVER_ID:
            self.OnRunMasterServer()

        if id == MMOService.RUN_CLIENT_ID:
            self.OnRunClient()
            
    def OnCreateMasterDB(self):
        runner = process.ProcessDialog(wx.GetApp().frame)
        runner.SetSize((640, 480))
        runner.CenterOnParent(wx.BOTH)
        msg = "Creating Master Database"
        
        cmdline = ""
            
        runner.ShowModal("mud/masterserver/createdb.py", cmdline,msg)

    def OnCreateCharacterDB(self):
        
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
        project = projectService.GetCurrentProject()
        
        model = project.GetModel()
        gameRoot = model.gameRoot

        if not project:
            wx.MessageBox("Please create a project first", "Create Character Database", wx.OK | wx.ICON_EXCLAMATION)
            return
        
        baselinepath = "%s/data/worlds/multiplayer.baseline/world.db"%gameRoot
        
        if not os.path.exists(baselinepath):
            wx.MessageBox("Please compile the world database first", "Create Character Database", wx.OK | wx.ICON_EXCLAMATION)
            return

        runner = process.ProcessDialog(wx.GetApp().frame)
        runner.SetSize((640, 480))
        runner.CenterOnParent(wx.BOTH)
        msg = "Creating Character Database"
        
        cmdline = ""
            
        runner.ShowModal("mud/characterserver/createdb.py", cmdline,msg)
    

    def OnRunMasterServer(self):
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
        project = projectService.GetCurrentProject()
        base, ext = os.path.splitext(project.GetFilename())
        gameConfig = os.path.basename(base)+".cfg"
        
        cmd  = sys.executable
        path = os.getcwd()
        
        script = "mud/masterserver/main.py"
        
        cmdline = '%s/%s '%(path, script)
        cmdline += "gameconfig=%s"%gameConfig
        cmdline += " -wx"
        
        if sys.platform[:6]!='darwin':
            s = 'start '+sys.executable+" "+cmdline
            s = os.path.normpath(s)
            os.system(s)
        else:
            cmd = sys.executable
            args = cmdline.split(" ")
            args.insert(0,cmd)
            
            s = '/usr/local/bin/pythonw2.5 -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)

                
    def OnRunCharacterServer(self):
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
        project = projectService.GetCurrentProject()
        base, ext = os.path.splitext(project.GetFilename())
        gameConfig = os.path.basename(base)+".cfg"
        
        cmd  = sys.executable
        path = os.getcwd()
        
        script = "mud/characterserver/server.py"
        
        cmdline = '%s/%s '%(path, script)        
        cmdline += "gameconfig=%s"%gameConfig
        cmdline += " -wx"

        if sys.platform[:6]!='darwin':
            s = 'start '+sys.executable+" "+cmdline
            s = os.path.normpath(s)
            os.system(s)
        else:
            cmd = sys.executable
            args = cmdline.split(" ")
            args.insert(0,cmd)
            
            s = '/usr/local/bin/pythonw2.5 -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)

    def OnRunWorldDaemon(self):
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
        project = projectService.GetCurrentProject()
        base, ext = os.path.splitext(project.GetFilename())
        gameConfig = os.path.basename(base)+".cfg"
        
        cmd  = sys.executable
        path = os.getcwd()
        
        script = "WorldDaemon.py"
        
        cmdline = '%s/%s '%(path, script)
        cmdline += "-worldname=Premium_MMORPG -publicname=starter -password=mmo"
        cmdline += " gameconfig=%s"%gameConfig
        cmdline += " -wx"

        if sys.platform[:6]!='darwin':
            s = 'start '+sys.executable+" "+cmdline
            s = os.path.normpath(s)
            os.system(s)
        else:
            cmd = sys.executable
            args = cmdline.split(" ")
            args.insert(0,cmd)
            
            s = '/usr/local/bin/pythonw2.5 -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)
        
    def OnRunClient(self):
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
        project = projectService.GetCurrentProject()
        base, ext = os.path.splitext(project.GetFilename())
        gameConfig = os.path.basename(base)+".cfg"
        
        cmd  = sys.executable
        path = os.getcwd()
        
        script = "Client.pyw"
        
        cmdline = '%s/%s '%(path, script)
        cmdline += "gameconfig=%s"%gameConfig
        
        if sys.platform[:6]!='darwin':
            s = 'start '+sys.executable+" "+cmdline
            s = os.path.normpath(s)
            os.system(s)
        else:
            cmd = sys.executable
            args = cmdline.split(" ")
            args.insert(0,cmd)
            
            s = '/usr/local/bin/pythonw2.5 -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)


