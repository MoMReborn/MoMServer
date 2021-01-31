import ProjectEditor
#import DebuggerService
import UICommon
import Wizard
import database
import process
import os, sys, traceback, shutil
import wx
_ = wx.GetTranslation


class WorldService(wx.lib.pydocview.DocService):
    
    COMPILEWORLD_ID = wx.NewId()
    
    def InstallControls(self, frame, menuBar = None, toolBar = None, statusBar = None, document = None):

        menu = wx.Menu()
        
        index = menuBar.FindMenu(_("&Project"))
        menuBar.Insert(index + 1, menu, _("&World"))
        
        wx.EVT_MENU(frame, WorldService.COMPILEWORLD_ID, self.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, WorldService.COMPILEWORLD_ID, self.ProcessUpdateUIEvent)
        menu.Append(WorldService.COMPILEWORLD_ID, ("Compile World...\tCtrl+W"), ("Compiles world database scripts"))

        menu.AppendSeparator()
        
    def OnCompileWorld(self):
        #checks
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
    
        project = projectService.GetCurrentProject()

        if not project:
            wx.MessageBox("Please create a project first", "Compile World", wx.OK | wx.ICON_EXCLAMATION)
            return

        model = project.GetModel()
        gameRoot = model.gameRoot
        
        #check that world config exists (this is created upon first zone creation
        if not os.path.exists("%s/genesis/world/world.py"%gameRoot):
            wx.MessageBox("Please create at least one zone before compiling the world", "Compile World", wx.OK | wx.ICON_EXCLAMATION)
            return
        
        runner = process.ProcessDialog(wx.GetApp().frame)
        
        runner.SetSize((640, 480))
        runner.CenterOnParent(wx.BOTH)
        cmdline = "-ideworkspace=%s"%model.gameRoot
        runner.ShowModal("Genesis.py", cmdline,"Compiling World")
        
        if runner.error:
            wx.MessageBox("There was an error compiling the world.  Please see the message window for more information.", "Compile Error", wx.OK | wx.ICON_EXCLAMATION)
            


    def ProcessEvent(self, event):
        id = event.GetId()
        
        if id == WorldService.COMPILEWORLD_ID:
            self.OnCompileWorld()
            return None
        
        
    def ProcessUpdateUIEvent(self, event):
        pass
    

    def GetCurrentProject(self):

        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)

        if projectService:

            projView = projectService.GetView()

            return projView.GetSelectedProject()

        return None
