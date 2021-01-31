# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import wx
import traceback
import sys

REACTOR = None

class RedirectText:
    def __init__(self,ctrl):
        self.out=ctrl

    def write(self,string):
        self.out.WriteText(string)

class MainPanel(wx.Panel):
    def __init__(self,parent,id):
        wx.Panel.__init__(self,parent,id)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        output = wx.TextCtrl(self, -1,"",size=(512, 384), style=wx.TE_MULTILINE|wx.TE_READONLY)

        sys.stdout=RedirectText(output)
        sys.stderr=sys.stdout

        sizer.Add(output, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)


class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title,size=wx.Size(512, 384),style=wx.CAPTION|wx.MINIMIZE_BOX| wx.SYSTEM_MENU|wx.TAB_TRAVERSAL| wx.CLOSE_BOX)
                        
        menu = wx.Menu()
        menu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")        
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        wx.EVT_MENU(self, wx.ID_EXIT,  self.DoExit)
        
        try:
            mp = MainPanel(self,-1)
            
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            sizer.Add(mp, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 0)
            
            self.SetSizer(sizer)
            sizer.Fit(self)
        
        except:
            traceback.print_exc()
            return

        
    def DoExit(self, event):        
        REACTOR.stop()


class GMApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()

        frame = MainFrame(None, -1, "Master Server")
        frame.Centre()
        #frame.Maximize()
        frame.Show(1)
        
        self.mainFrame = frame
        
        return True
    
def Setup(reactor):
    global REACTOR
    REACTOR = reactor
    app = GMApp()
    return app
    
