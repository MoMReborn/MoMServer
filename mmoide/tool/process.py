
import ProjectEditor
import MessageService
import wx
import sys, os

class ProcessDialog(wx.Dialog):
    def __init__(self, parent, ID=-1):
        wx.Dialog.__init__(self, parent, ID)

        self.process = None
        self.pid = None
        self.title = None
        self.error = False
        
        # We can either derive from wx.Process and override OnTerminate
        # or we can let wx.Process send this window an event that is
        # caught in the normal way...
        self.Bind(wx.EVT_END_PROCESS, self.OnProcessEnded)
        self.Bind(wx.EVT_CLOSE, self.OnCloseEvent)

        self.out = wx.TextCtrl(self, -1, '', 
                               style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH2)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.out, 1, wx.EXPAND|wx.ALL, 10)
        #sizer.Add(box2, 0, wx.EXPAND|wx.ALL, 10)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)


    def __del__(self):
        if self.process is not None:
            self.process.Detach()
            self.process.CloseOutput()
            self.process = None
            
            
    def OnCloseEvent(self, evt):
        evt.Skip() #propgate
        if self.process:
            self.process.Kill(self.pid, wx.SIGKILL)
            self.process = None
            self.pid = None
            
            messageService = wx.GetApp().GetService(MessageService.MessageService)
            messageService.ShowWindow()
    
            view = messageService.GetView()
            if view:
                view.ClearLines()
                view.AddLines("Canceled...\n")

        
            
            
    def Tick(self):
        if self.process is not None:
            self.timer = wx.CallLater(500, self.Tick)
            stream = self.process.GetInputStream()

            if stream.CanRead():
                text = stream.read()
                self.out.AppendText(text)
                
            estream = self.process.GetErrorStream()
            if estream.CanRead():
                self.error = True
                text = estream.read()
                self.out.SetDefaultStyle(wx.TextAttr(wx.RED))
                self.out.AppendText(text)
                self.out.SetDefaultStyle(wx.TextAttr(wx.BLACK))

    def OnProcessEnded(self, evt):
        #self.log.write('OnProcessEnded, pid:%s,  exitCode: %s\n' %
        #               (evt.GetPid(), evt.GetExitCode()))

        stream = self.process.GetInputStream()

        if stream.CanRead():
            text = stream.read()
            self.out.AppendText(text)
            
        estream = self.process.GetErrorStream()
        if estream.CanRead():
            self.error = True
            text = estream.read()
            self.out.SetDefaultStyle(wx.TextAttr(wx.RED))
            self.out.AppendText(text)
            self.out.SetDefaultStyle(wx.TextAttr(wx.BLACK))
            

        self.process.Destroy()
        self.process = None
        self.pid = None
        if self.title and not self.error:
            self.SetTitle(self.title+"...Done")
            self.out.AppendText("\nFinished.")
        elif self.title:
            #for right now, exiting the client raises some exceptions for 
            #remote objects not cleaned up properly, so, we'll just say "done" for now
            
            #self.SetTitle(self.title+"...Error!")
            #self.out.AppendText("\nERROR!")
            self.SetTitle(self.title+"...Done")
            self.out.AppendText("\nFinished.")
        
        #wx.GetApp().frame.Raise()
        #self.Raise()
        
        messageService = wx.GetApp().GetService(MessageService.MessageService)
        messageService.ShowWindow()

        view = messageService.GetView()
        if view:
            view.ClearLines()
            view.AddLines(self.out.GetValue())

        
        self.Close()
        
            
    
    def Execute(self, script, cmdline, title = ""):
        
        self.out.AppendText("\nRunning...\n\n")
        
        if title:
            self.title = title
            self.SetTitle(title)
        
        #retrieve game config info
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
        project = projectService.GetCurrentProject()
        base, ext = os.path.splitext(project.GetFilename())
        gameConfig = os.path.basename(base)+".cfg"
        
        #spawn process
        self.process = wx.Process(self)
        self.process.Redirect();
        cmd  = sys.executable
        path = os.getcwd()
        cmd = '%s %s/%s %s'%(cmd, path, script, cmdline)
        cmd += " gameconfig=%s"%gameConfig
        self.pid = wx.Execute(cmd, wx.EXEC_ASYNC, self.process)
        self.Tick()
        
    def ShowModal(self, script, cmdline, title):
        
        self.Execute(script, cmdline, title)
        wx.Dialog.ShowModal(self)
