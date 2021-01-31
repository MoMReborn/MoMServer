# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#ability to remotely GM without being in the game
#monitoring some chat

import wx
import  wx.lib.anchors as anchors
from twisted.internet import wxreactor
wxreactor.install()
from twisted.internet import reactor
import traceback
from gmmind import GMConnection,setLogFunction



VERSION = "v1.1"

USERNAME = ""
PASSWORD = ""
ROLE = ""



class LoginDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):
        global USERNAME,PASSWORD

        pre = wx.PreDialog()
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, "GM Server Login")
        sizer.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Username:")        
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.userTextCtrl = text = wx.TextCtrl(self, -1, USERNAME, size=(80,-1))        
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, "Password:")
        
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)

        self.passwordTextCtrl = text = wx.TextCtrl(self, -1, PASSWORD, size=(80,-1),style=wx.TE_PASSWORD)        
        box.Add(text, 1, wx.ALIGN_CENTRE|wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        line = wx.StaticLine(self, -1, size=(20,-1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.RIGHT|wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)        
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)



GMCONNECTION = None
def ShowLoginDialog(parent):
    dlg = LoginDialog(parent, -1, "GM Login", size=(350, 200),
                     #style = wxCAPTION | wxSYSTEM_MENU | wxTHICK_FRAME
                     style = wx.DEFAULT_DIALOG_STYLE
                     )
    dlg.CenterOnScreen()

    # this does not return until the dialog is closed.
    val = dlg.ShowModal()

    if val == wx.ID_OK:
        pass
    else:
        dlg.Destroy()
        return
    
    global USERNAME,PASSWORD,ROLE
        
    USERNAME = dlg.userTextCtrl.GetValue()
    PASSWORD = dlg.passwordTextCtrl.GetValue()
    ROLE = "GM" #todo, add admin
    
    dlg.Destroy()
    
    global GMCONNECTION
    GMCONNECTION = GMConnection()
    GMCONNECTION.connect(USERNAME,PASSWORD,ROLE)


OUTPUTWINDOW = None
EDITCONTROL = None

def LogText(text):
    OUTPUTWINDOW.AppendText(text)



class CommandPanel(wx.Panel):
    def __init__(self,parent):
        global OUTPUTWINDOW,EDITCONTROL
        
        wx.Panel.__init__(self,parent)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        OUTPUTWINDOW = output = wx.TextCtrl(self, -1,"",size=(900, 600), style=wx.TE_MULTILINE|wx.TE_READONLY)
        
        self.edit = EDITCONTROL = edit = wx.TextCtrl(self, -1,"",size=(900, -1),style=wx.TE_PROCESS_ENTER)
        
        self.edit.Bind(wx.EVT_TEXT_ENTER, self.EvtTextEnter)
        
        self.edit.Bind(wx.EVT_CHAR, self.EvtChar)
        
        sizer.Add(output, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        sizer.Add(edit,0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)
        
        self.history = []
        self.historyPosition = -1
    
    
    def EvtTextEnter(self, event):
        # Get the command entered.
        command = self.edit.GetValue()
        
        # Reset the edit field.
        self.edit.SetValue("")
        
        # If there's no command, just skip and return.
        if len(command):
            
            # Only append command to command history if it isn't a repetition
            #  of the previous one.
            if not len(self.history) or command != self.history[-1]:
                self.history.append(command)
                self.historyPosition = len(self.history)
            
            # Print the command entered to output window.
            LogText("\n>>> %s\n"%command)
            
            global GMCONNECTION
            
            # If the connection hasn't been set up, give feedback and
            #  return.
            if not GMCONNECTION:
                LogText("\nYou are not connected to the GM Server.\n")
                return
            
            # Let the GM Connection object handle the input.
            GMCONNECTION.processInput(command)
    
    
    def EvtChar(self, event):
        k = event.GetKeyCode()
        #317 up and 319 down
        #LogText('EvtChar: %d\n' % k)
        #up
        if k == 317 and self.historyPosition > 0:
            self.historyPosition -= 1
            EDITCONTROL.SetValue(self.history[self.historyPosition])

        elif k == 319 and self.historyPosition < len(self.history) - 1:
            self.historyPosition += 1
            EDITCONTROL.SetValue(self.history[self.historyPosition])
            
        elif k == 319:
            EDITCONTROL.SetValue("")
            
            
        event.Skip()

        


class MyMainPanel(wx.Panel):
    def __init__(self,parent,id):
        wx.Panel.__init__(self,parent,id)
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        p1 = CommandPanel(self)

        sizer.Add(p1, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 5)
        
        self.SetSizer(sizer)
        sizer.Fit(self)




class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title,size=wx.Size(800, 600),style=wx.CAPTION|wx.MINIMIZE_BOX| wx.SYSTEM_MENU|wx.TAB_TRAVERSAL| wx.CLOSE_BOX)
                        
        menu = wx.Menu()
        menu.Append(1000, "Login", "Login to GM Server")
        menu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")        
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        wx.EVT_MENU(self, wx.ID_EXIT,  self.DoExit)
        wx.EVT_MENU(self, 1000,  self.DoLogin)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        try:
            mmp = MyMainPanel(self,-1)
        except:
            traceback.print_exc()
            
            
        sizer.Add(mmp, 0, wx.ALIGN_CENTRE|wx.ALL|wx.EXPAND, 0)
        
        self.SetSizer(sizer)
        sizer.Fit(self)
    
    
    def DoLogin(self, event):
        ShowLoginDialog(self)
    
    
    def DoExit(self, event):
        global GMCONNECTION
        if GMCONNECTION:
            GMCONNECTION.disconnect()
        GMCONNECTION = None
        reactor.stop()



class GMApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        
        

        frame = MainFrame(None, -1, "GM Tool")
        frame.Centre()
        #frame.Maximize()
        frame.Show(1)
        
        
        self.mainFrame = frame
            
        LogText("GM Tool %s Initialized.\nSelect File->Login to connect to GM Server\n"%VERSION)
        EDITCONTROL.SetFocus()
        
        return True



def main():
    app = GMApp()
    reactor.registerWxApp(app)
    
    setLogFunction(LogText)
    
    #reactor.callLater(.1,ShowLoginDialog,app.mainFrame)
    
    try:
        reactor.run()
    except:
        traceback.print_exc()


main()

