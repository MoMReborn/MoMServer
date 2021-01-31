# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import wx
from twisted.internet import _threadedselect
_threadedselect.install()
from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.credentials import UsernamePassword

from shutil import rmtree,copyfile
import os,sys,imp
from cPickle import load,dump
from md5 import md5
from traceback import print_stack

from gui.mainpanel import MainPanel
from gui.masterlogindlg import MasterLoginDlg
from gui.newworlddlg import NewWorldDlg

from mud.world.shared.worlddata import WorldConfig,WorldInfo
from mud_ext.world.defines import *
from mud.gamesettings import *



def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze


def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])



FROZEN = False
if main_is_frozen():
    FROZEN = True
    maindir = get_main_dir()
    sys.path.append(maindir)


if not os.path.exists("%s/cache"%GAMEROOT):
    os.makedirs("%s/cache"%GAMEROOT)

try:
    f = file('%s/cache/worldmanager.tmp'%GAMEROOT, 'r')
    SETTINGS = load(f)
    f.close()
except:
    SETTINGS = {}
    f = file('%s/cache/worldmanager.tmp'%GAMEROOT, 'w')
    SETTINGS['PublicName'] = ''
    SETTINGS['Password'] = ''
    dump(SETTINGS,f)
    f.close()



class MyMainPanel(MainPanel,pb.Root):
    def __init__(self,parent,id):
        MainPanel.__init__(self,parent,id)
        ctrl = self.myWorldsListCtrl
        ctrl.InsertColumn(0,"World Name")
        
        ctrl = self.liveWorldsListCtrl
        ctrl.InsertColumn(0,"World Name")
        ctrl.InsertColumn(1,"Players")
        ctrl.InsertColumn(2,"Password")
        ctrl.InsertColumn(3,"Guests")
        
        #listctrl has no get selected item, grrrr
        self.myWorld = None
        
        self.progress = 0
        self.progressDlg = wx.ProgressDialog("Working...","",100,self,wx.PD_AUTO_HIDE|wx.PD_APP_MODAL)
        self.progressDlg.Hide()
        #start ticking progress
        reactor.callLater(0,self.tickProgress)

        self.perspective = None
        
        self.Bind(wx.EVT_BUTTON, self.OnLog, self.logButton)
        self.Bind(wx.EVT_BUTTON, self.OnNewWorld, self.newWorldBtn)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteWorld, self.deleteWorldBtn)
        self.Bind(wx.EVT_BUTTON, self.OnLaunchWorld, self.launchWorldBtn)
        
        self.Bind(wx.EVT_BUTTON, self.OnRefreshLiveWorlds, self.refreshWorldsBtn)
        self.Bind(wx.EVT_BUTTON, self.OnCoServeWorld, self.coServeBtn)
        
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnMyWorldsItemSelected, self.myWorldsListCtrl)
        
        self.enableControls(False)
        
    def enumLiveWorldsResults(self,winfos):
        self.progressDlg.Hide()
        
        for w in winfos:
            self.liveWorldsListCtrl.InsertStringItem(0,w.worldName)

        
    def OnRefreshLiveWorlds(self,evt=None):
        if evt:
            evt.Skip()
            
        self.liveWorldsListCtrl.DeleteAllItems()    

        self.progressDlg.Update(0,"Enumerating Live Worlds...")           
        self.progressDlg.Show()
        self.perspective.callRemote("EnumWorldsAvatar","enumLiveWorlds",False,RPG_BUILD_DEMO,True,not RPG_BUILD_LIVE).addCallbacks(self.enumLiveWorldsResults,self.failure)
    
    
    
    def OnCoServeWorld(self,evt=None):
        print "WARNING: co-serving not yet implemented!"
        evt.Skip()
            
        
        
    def OnMyWorldsItemSelected(self, event):
        self.myWorld = self.myWorldsListCtrl.GetItemText(event.m_itemIndex)
        event.Skip()

        
    def enableControls(self,enable=True):
        controls = [self.refreshWorldsBtn,self.coServeBtn,self.launchWorldBtn,self.newWorldBtn,self.deleteWorldBtn]
        for c in controls:
            c.Enable(enable)
        
    def connected(self,perspective):
        self.progressDlg.Hide()
        self.perspective = perspective
        self.logButton.SetLabel("Logout")
        
        self.enableControls(True)
        
        #enumerate my worlds
        self.OnEnumMyWorlds()
        
        
    def failure(self,error):
        self.progressDlg.Hide()
        self.perspective = None
        self.enableControls(False)
        self.logButton.SetLabel("Connect!")
        wx.MessageBox("%s"%error,"Failure!")
        
    def OnLaunchWorld(self,evt):
        evt.Skip()
        
        if not self.myWorld or not len(self.myWorld):
            return
        
        worldname = self.myWorld
        worldname = worldname.replace(" ","_")
        print 'Launching ',worldname
        
        cwd = os.getcwd()
        
        if FROZEN:
            cmd  =  r'..\bin\WorldDaemon.exe'
            args = ""
        else:
            cmd  =  sys.executable
            args =  "%s/mud/worlddaemon/main.py"%cwd
        
        args += r' -worldname=%s'%worldname
        args += r' -publicname=%s -password=%s'%(SETTINGS['PublicName'],SETTINGS['Password'])
        args += r' -wx'
        
        if sys.platform[:6] != 'darwin':
            s = 'start "%s" %s %s'%(os.getcwd(),cmd,args)
            s = os.path.normpath(s)
            os.system(s)
        else:
            cmd = sys.executable
            args = args.split(" ")
            args.insert(0,cmd)
            
            s = 'pythonw -c \'import os;os.spawnv(os.P_NOWAIT,"%s",[%s])\''%(cmd,','.join('"%s"'%arg for arg in args))
            print s
            os.system(s)
    
    
    def enumMyWorldsResult(self,worlds):
        self.progressDlg.Hide()
        
        for w in worlds:
            self.myWorldsListCtrl.InsertStringItem(0,w)
            
    def OnEnumMyWorlds(self,evt=None):
        if evt:
            evt.Skip()
        self.progressDlg.Update(0,"Enumerating my worlds...")           
        self.progressDlg.Show()
        
        self.myWorld = None
        self.myWorldsListCtrl.DeleteAllItems()    
        self.perspective.callRemote("EnumWorldsAvatar","enumMyWorlds",RPG_BUILD_DEMO, not RPG_BUILD_LIVE).addCallbacks(self.enumMyWorldsResult,self.failure)
        
    def deleteWorldResult(self,result):
        self.progressDlg.Hide()
        
        code = result[0]
        msg = result[1]
        worldname = result[2].replace(" ","_")
        title = "Success!"
        if code:
            title = "Failure"
        else:
            self.OnEnumMyWorlds()
            #can this folder be manipulated?
            if '..' in worldname:
                print_stack()
                print "AssertionError: '..' in worldname!"
                return
            try:
                rmtree('./%s/data/worlds/multiplayer/%s'%(GAMEROOT,worldname))
            except: 
                pass
            
            
        wx.MessageBox(msg,title)

        
    def OnDeleteWorld(self,evt):
        evt.Skip()
        if not self.myWorld or not len(self.myWorld):
            return
            
        dlg = wx.MessageDialog(self, 'Are you sure you want to delete the world known as %s?'%self.myWorld,
                               'Delete World?',
                               wx.YES_NO
                               # wx.OK|wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_INFORMATION
                               )
        result = dlg.ShowModal()
        dlg.Destroy()
        
        if result != wx.ID_YES:
            return

            
        self.progressDlg.Update(0,"Deleting World...")           
        self.progressDlg.Show()
        self.perspective.callRemote("NewWorldAvatar","deleteWorld",self.myWorld).addCallbacks(self.deleteWorldResult,self.failure)
            
        
            
        
    def newWorldResult(self,result):
        self.progressDlg.Hide()
        
        code = result[0]
        msg = result[1]
        worldname = result[2].replace(" ","_")
        title = "Success!"
        if code:
            title = "Failure"
        else:
            self.OnEnumMyWorlds()
            
        wx.MessageBox(msg,title)
        
        if not os.path.exists('./%s/data/worlds/multiplayer/%s'%(GAMEROOT,worldname)):
            os.makedirs('./%s/data/worlds/multiplayer/%s'%(GAMEROOT,worldname))
            
        copyfile('./%s/data/worlds/multiplayer.baseline/world.db'%GAMEROOT,'./%s/data/worlds/multiplayer/%s/world.db'%(GAMEROOT,worldname))
        
        
        config = """
        
#WORLD SERVER CONFIGURATION 

CLUSTERNAMES = [
    ("trinst","desertmohrum"),
]

WORLDPORT = %i
ZONESTARTPORT = %i

#UNSUPPORTED
MAXDYNAMICZONES = -1
MAXPLAYERS = %i
ALLOWGUESTS = False

PLAYERPASSWORD = "%s"
ZONEPASSWORD = ""

MOTD = "%s\\n"
"""%(self.worldPort,self.wconfig.zonePort,self.wconfig.maxLivePlayers,self.wconfig.playerPassword,self.wconfig.motd)
    
        f = file('./serverconfig/%s.py'%worldname,'w')
        f.write(config)
        f.close()
        
        
    def OnNewWorld(self,evt):
        evt.Skip()

        dlg = NewWorldDlg(self)
        dlg.Centre()
        
        wcp = dlg.worldConfigPanel
        
        wcp.worldPortTextCtrl.SetValue("2006")
        wcp.zonePortTextCtrl.SetValue("29000")
        wcp.playerPasswordTextCtrl.SetValue("")
        wcp.zonePasswordTextCtrl.SetValue("")
        wcp.maxLivePlayersTextCtrl.SetValue("-1")
        wcp.maxLiveZonesTextCtrl.SetValue("-1")
        wcp.allowGuestsCheckBox.SetValue(False)

        
        if dlg.ShowModal() == wx.ID_OK:
            worldName = dlg.worldNameTextCtrl.GetValue()

            if len(worldName) < 5:
                wx.MessageBox("World Name must be at least 5 character","Failure!")
                return
            
            if not worldName.replace(' ','').isalnum():
                wx.MessageBox("Please only use letters and numbers in your world's name","Failure!")
                return 

                
            
            
            try:
                worldPort = int (wcp.worldPortTextCtrl.GetValue())
            except:
                wx.MessageBox("Invalid World Port","Failure!")
                return


            #try:
            #    worldPort = int (wcp.worldPortTextCtrl.GetValue())
            #except:
            #    wx.MessageBox("Invalid World Port","Failure!")
            #    return
                
            self.worldPort = worldPort

            zonePort = wcp.zonePortTextCtrl.GetValue()
            motd = wcp.motdTextCtrl.GetValue()
            playerPassword = wcp.playerPasswordTextCtrl.GetValue()
            zonePassword = wcp.zonePasswordTextCtrl.GetValue()
            maxLivePlayers = wcp.maxLivePlayersTextCtrl.GetValue()
            maxLiveZones = wcp.maxLiveZonesTextCtrl.GetValue()
            allowGuests = wcp.allowGuestsCheckBox.GetValue()
            
            try:
                zonePort = int(zonePort)
            except:
                wx.MessageBox("Zone Start Port must be an integer", "Failure!")
            try:
                maxLivePlayers = int(maxLivePlayers)
            except:
                wx.MessageBox("Max Live Players must be an integer","Failure!")
                return
                
            try:
                maxLiveZones = int(maxLiveZones)
            except:
                wx.MessageBox("Max Live Zones must be an integer","Failure!")
                return
                
            wconfig = WorldConfig()
            wconfig.worldName = worldName
            wconfig.worldPort = worldPort
            wconfig.playerPassword = playerPassword
            wconfig.zonePassword = zonePassword
            wconfig.allowGuests = allowGuests
            wconfig.maxLiveZones = maxLiveZones
            wconfig.maxLivePlayers = maxLivePlayers
            wconfig.zonePort = zonePort
            wconfig.motd = motd
            wconfig.demoWorld = False
            if RPG_BUILD_DEMO:
                wconfig.demoWorld = True
                
            
            self.wconfig = wconfig
            
            self.progressDlg.Update(0,"Submitting World to Master Server...")           
            self.progressDlg.Show()

            testing = False
            if not RPG_BUILD_DEMO and not RPG_BUILD_LIVE:
                testing = True
            
            self.perspective.callRemote("NewWorldAvatar","newWorld",wconfig,testing).addCallbacks(self.newWorldResult,self.failure)

    
    def OnLog(self,evt):
        evt.Skip()
        
        if not self.perspective:
            #not connection
            dlg = MasterLoginDlg(self)
            dlg.Centre()
            dlg.publicNameTextCtrl.SetValue(SETTINGS['PublicName'])
            dlg.passwordTextCtrl.SetValue(SETTINGS['Password'])
            if dlg.ShowModal()==wx.ID_OK:
                pname = dlg.publicNameTextCtrl.GetValue()
                pw =  dlg.passwordTextCtrl.GetValue()
                
                if len(pname) and len(pw):
                    SETTINGS['PublicName']=pname
                    SETTINGS['Password']=pw
                
                #login
                self.progressDlg.Update(0,"Logging into the Master Server...")           
                self.progressDlg.Show()
                
                username=pname+"-"+"World"
                password=pw
                
                factory = pb.PBClientFactory()
                reactor.connectTCP(MASTERIP,MASTERPORT,factory)
                password = md5(password).digest()

                factory.login(UsernamePassword(username, password),self).addCallbacks(self.connected, self.failure)
        else: #logout
            self.myWorldsListCtrl.DeleteAllItems()
            self.liveWorldsListCtrl.DeleteAllItems()    
            self.perspective = None
            self.enableControls(False)
            self.logButton.SetLabel("Connect!")

     
    def tickProgress(self):
        self.progressDlg.Centre()
        self.progress+=1
        self.progress%=100
        self.progressDlg.Update(self.progress)           
        reactor.callLater(.025,self.tickProgress)

        

class MainFrame(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, -1, title,
                          style=wx.MINIMIZE_BOX | wx.CAPTION | wx.CLIP_CHILDREN,size=wx.Size(344, 534))
                        
        menu = wx.Menu()
        menu.Append(wx.ID_EXIT, "E&xit", "Terminate the program")
        menuBar = wx.MenuBar()
        menuBar.Append(menu, "&File")
        self.SetMenuBar(menuBar)
        wx.EVT_MENU(self, wx.ID_EXIT,  self.DoExit)
        
        mmp = MyMainPanel(self,-1)

        reactor.interleave(wx.CallAfter)

    def DoExit(self, event):
        reactor.addSystemEventTrigger('after', 'shutdown', self.Close, True)
        reactor.stop()
        
        

class WorldManagerApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        
        

        frame = MainFrame(None, -1, "MoM World Manager")
        frame.Centre()
        #frame.Maximize()
        frame.Show(1)
        
        return True


def main():
    app = WorldManagerApp(0)
    app.MainLoop()

    f = file('%s/cache/worldmanager.tmp'%GAMEROOT, 'w')
    dump(SETTINGS,f)
    f.close()


