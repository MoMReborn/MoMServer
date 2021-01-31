
import ProjectEditor
#import DebuggerService
import UICommon
import Wizard
import database
import process
import os, sys, traceback, shutil, string
import wx
_ = wx.GetTranslation


class ZoneService(wx.lib.pydocview.DocService):
    
    NEW_ZONE_ID = wx.NewId()
    EDITLAST_ZONE_ID = wx.NewId()
    EDIT_ZONE_ID = wx.NewId()

    TESTLAST_ZONE_ID = wx.NewId()
    TEST_ZONE_ID = wx.NewId()

    
    def __init__(self):
        self.lastZone = ""
        

    def InstallControls(self, frame, menuBar = None, toolBar = None, statusBar = None, document = None):

        menu = menuBar.GetMenu(menuBar.FindMenu(_("&World")))

        wx.EVT_MENU(frame, ZoneService.TESTLAST_ZONE_ID, self.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, ZoneService.TESTLAST_ZONE_ID, self.ProcessUpdateUIEvent)
        self.testLastMenuItem = menu.Append(ZoneService.TESTLAST_ZONE_ID, ("Test Last Zone...\tCtrl+T"), ("Tests the last zone"))
        self.testLastMenuItem.Enable(False)
        
        wx.EVT_MENU(frame, ZoneService.TEST_ZONE_ID, self.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, ZoneService.TEST_ZONE_ID, self.ProcessUpdateUIEvent)
        menu.Append(ZoneService.TEST_ZONE_ID, ("Test Zone"), ("Tests a chosen zone"))

        menu.AppendSeparator()
        
        wx.EVT_MENU(frame, ZoneService.EDITLAST_ZONE_ID, self.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, ZoneService.EDITLAST_ZONE_ID, self.ProcessUpdateUIEvent)
        self.editLastMenuItem = menu.Append(ZoneService.EDITLAST_ZONE_ID, ("Edit Last Zone...\tCtrl+E"), ("Edits the last zone"))
        self.editLastMenuItem.Enable(False)
        
        wx.EVT_MENU(frame, ZoneService.EDIT_ZONE_ID, self.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, ZoneService.EDIT_ZONE_ID, self.ProcessUpdateUIEvent)
        menu.Append(ZoneService.EDIT_ZONE_ID, ("Edit Zone"), ("Edits a chosen zone"))

        menu.AppendSeparator()

        wx.EVT_MENU(frame, ZoneService.NEW_ZONE_ID, self.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, ZoneService.NEW_ZONE_ID, self.ProcessUpdateUIEvent)
        menu.Append(ZoneService.NEW_ZONE_ID, ("New Zone"), ("Create a New Zone"))

        menu.AppendSeparator()

        
    def ProcessEvent(self, event):
        
        id = event.GetId()
        
        if id == ZoneService.NEW_ZONE_ID:
            self.OnNewZone()
            return None

        if id == ZoneService.EDIT_ZONE_ID:
            self.OnEditZone(None,True)
            return None

        if id == ZoneService.EDITLAST_ZONE_ID:
            self.OnEditZone(self.lastZone,True)
            return None

        if id == ZoneService.TEST_ZONE_ID:
            self.OnEditZone()
            return None

        if id == ZoneService.TESTLAST_ZONE_ID:
            self.OnEditZone(self.lastZone)
            return None


        
    def OnEditZone(self, choice = None, edit = False):
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
        project = projectService.GetCurrentProject()
        
        model = project.GetModel()
        gameRoot = model.gameRoot

        if not project:
            wx.MessageBox("Please create a project first", "Edit Zone", wx.OK | wx.ICON_EXCLAMATION)
            return
        
        baselinepath = "%s/data/worlds/multiplayer.baseline/world.db"%gameRoot
        worldpath = "%s/data/worlds/singleplayer/editworld"%gameRoot
        
        if not os.path.exists(baselinepath):
            wx.MessageBox("Please compile the world database first", "Edit Zone", wx.OK | wx.ICON_EXCLAMATION)
            return
        
        #copy baseline over effectively creating new world
        #we may want to move this if there are more instances of where the world
        #should be created before a given operation
        if not os.path.exists(worldpath):
            os.makedirs(worldpath)
            shutil.copyfile(baselinepath, worldpath+"/world.db")
            
        try:
            choices = database.QueryWorldZones(gameRoot, "editworld")
        except:
            wx.MessageBox("Please compile the world database first", "Edit Zone", wx.OK | wx.ICON_EXCLAMATION)
            return

        if not len(choices):
            wx.MessageBox("No zones found in database.  Please compile the world database first", "Edit Zone", wx.OK | wx.ICON_EXCLAMATION)
            return
            
            
        if not choice:
            dlg = wx.SingleChoiceDialog(
                    wx.GetApp().GetTopWindow(), 'Please choose a zone to edit', 'Choose Zone', 
                    choices, 
                    wx.CHOICEDLG_STYLE
                    )

            if dlg.ShowModal() == wx.ID_OK:
                choice = dlg.GetStringSelection()
            dlg.Destroy()
        
        if choice:
            #we need to launch the client and connect to zone
            self.lastZone = choice
            self.editLastMenuItem.Enable(True)
            self.editLastMenuItem.SetText("Edit Last Zone (%s)\tCtrl+E"%choice)

            self.testLastMenuItem.Enable(True)
            self.testLastMenuItem.SetText("Test Last Zone (%s)\tCtrl+E"%choice)

            
            cmdline = "-ide -idezone=%s"%choice
            if edit:
                cmdline+=" -editzone"
            
            runner = process.ProcessDialog(wx.GetApp().frame)
            runner.SetSize((640, 480))
            runner.CenterOnParent(wx.BOTH)
            msg = "Testing Zone..."
            if edit:
                msg = "Editing Zone..."
                
            runner.ShowModal("Client.pyw", cmdline,msg)
            
            

    def OnNewZone(self):
        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)
    
        project = projectService.GetCurrentProject()

        if not project:
            wx.MessageBox("Please create a project first", "New Zone", wx.OK | wx.ICON_EXCLAMATION)
            return

        model = project.GetModel()
        gameRoot = model.gameRoot
        
        wiz = NewZoneWizard(wx.GetApp().GetTopWindow())
        status = wiz.RunWizard()
        zoneID = None
        missionFile = None
        zoneClimate = None
        zoneName = None
        if status:
            zoneID = wiz.zoneID
            zoneClimate = wiz.zoneClimate
            zoneName = wiz.zoneName
            missionFile = wiz.missionFile
    
        wiz.Destroy()
        
        if zoneID:
            #create the zone files and add them to the project
            folder = os.getcwd()
            
            zoneFolder = folder+"/%s/genesis/zone/%s"%(gameRoot, zoneID)
            
            if os.path.exists(zoneFolder):
                wx.MessageBox("Zone folder already exists:\n%s"%zoneFolder, "New Zone", wx.OK | wx.ICON_EXCLAMATION)
                return None
            
            mfile = "%s/data/missions/%s"%(gameRoot, missionFile)
            if os.path.exists(mfile):
                wx.MessageBox("Mission file already exists:\n%s"%mfile, "New Zone", wx.OK | wx.ICON_EXCLAMATION)

            #check that world config exists (this is created upon first zone creation
            wpath = "%s/genesis/world"%gameRoot
            if not os.path.exists(wpath+"/world.py"):
                os.makedirs(wpath)
                f = file(wpath+"/world.py", "w")
                f.write(WORLDFILE%(zoneID,zoneID,zoneID))
                f.close()
                #__init__.py
                f = file(wpath+"/__init__.py", "w")
                f.write("#__init__.py")
                f.close()
                
                files = ["%s/genesis/world/__init__.py"%gameRoot,"%s/genesis/world/world.py"%gameRoot]
                project.AddFiles(files, "%s/genesis/world"%(gameRoot))

            zoneTransform = "31.7615 -274.927 115.2 0 0 -1 4.20118"
                
            zfile = ZONEFILE%(zoneID, zoneName, missionFile, zoneClimate,zoneTransform)
            
            os.makedirs(zoneFolder)
            
            #zone.py
            f = file(zoneFolder+"/%s.py"%zoneID, "w")
            f.write(zfile)
            f.close()
            
            #__init__.py
            f = file(zoneFolder+"/__init__.py", "w")
            f.write("#__init__.py")
            f.close()
            
            #spawns.py
            f = file(zoneFolder+"/spawns.py", "w")
            f.write(SPAWNSFILE)
            f.close()
            
            #spawngroups.py
            f = file(zoneFolder+"/spawngroups.py", "w")
            f.write(SPAWNGROUPSFILE%zoneID)
            f.close()

            #items.py
            f = file(zoneFolder+"/items.py", "w")
            f.write(ITEMSFILE)
            f.close()

            #quests.py
            f = file(zoneFolder+"/quests.py", "w")
            f.write(QUESTSFILE)
            f.close()
            
            #mission and terrain files
            shutil.copyfile("./starter.mmo/data/newMission.ter", "./%s/data/missions/%s.ter"%(gameRoot, zoneID))
            shutil.copyfile("./starter.mmo/data/newMission.ml", "./%s/data/missions/%s.ml"%(gameRoot, zoneID))

            f_in=file("./starter.mmo/data/newMission.mis", "r")
            f_out=file("./%s/data/missions/%s.mis"%(gameRoot, zoneID), "w")
            for line in f_in:
                lineno = 0
                lineno = string.find(line, "newMission.ter")
                if lineno > 0:
                    line = line.replace("newMission.ter", "%s.ter"%zoneID)
                f_out.write(line)
            f_in.close()
            f_out.close()
            
            #add the files to the project
            
            #mission
            project.AddFiles(["%s/data/missions/%s.mis"%(gameRoot, zoneID)], "%s/data/missions"%gameRoot)
            
            #python files
            bfiles = ["__init__.py", "%s.py"%zoneID, "spawns.py", "spawngroups.py", "items.py", "quests.py"]
            files = []
            for bf in bfiles:
                files.append("%s/genesis/zone/%s/%s"%(gameRoot, zoneID, bf))
            files.sort()
            project.AddFiles(files, "%s/genesis/zone/%s"%(gameRoot, zoneID))
            
            #add to zonemain
            f = file("%s/genesis/zone/zonemain.py"%gameRoot, "r")
            t = f.read()
            f.close()
            if "import %s.%s"%(zoneID, zoneID) not in t:
                t+="\nimport %s.%s\n"%(zoneID, zoneID)
                f = file("%s/genesis/zone/zonemain.py"%gameRoot, "w")
                f.write(t)
                f.close()
                
            project.OnSaveDocument(project.GetFilename())
        

    def ProcessUpdateUIEvent(self, event):
        pass
    

    def GetCurrentProject(self):

        projectService = wx.GetApp().GetService(ProjectEditor.ProjectService)

        if projectService:

            projView = projectService.GetView()

            return projView.GetSelectedProject()

        return None
    
    
    
class NewZoneWizard(Wizard.BaseWizard):

    WIZTITLE = _("New Zone Wizard")


    def __init__(self, parent):
        self._parent = parent
        self._fullProjectPath = None
        Wizard.BaseWizard.__init__(self, parent, self.WIZTITLE)
        self._zoneSettingsPage = self.CreateZoneSettings(self)
        wx.wizard.EVT_WIZARD_PAGE_CHANGING(self, self.GetId(), self.OnWizPageChanging)

    def CreateZoneSettings(self, wizard):
        page = Wizard.TitledWizardPage(wizard, _("Zone Settings"))
        psizer = page.GetSizer()
        
        idLabelText = wx.StaticText(page, -1, "Please enter the zone's database identifier :\n(ex. \"twilightforest\")")
        self._idControl = wx.TextCtrl(page, -1, "", size=(200, -1))
        
        nameLabelText = wx.StaticText(page, -1, "Please enter a descriptive name for your zone :\n(ex.  \"The Forest of Twilight\")")
        self._nameControl = wx.TextCtrl(page, -1, "", size=(200, -1))
        
        #climate
        climateLabelText = wx.StaticText(page, -1, "Please choose a zone climate:")
        choices =["Temperate", "Tropical", "Dry", "Cold", "Arctic"]
        self._climateControl = wx.ComboBox(page, -1, size=(200, -1), choices=choices, style=wx.CB_DROPDOWN)
        self._climateControl.SetValue("Temperate")

        psizer.Add(idLabelText)
        psizer.AddSpacer(4)
        psizer.Add(self._idControl)
        psizer.AddSpacer(10)
        
        psizer.Add(nameLabelText)
        psizer.AddSpacer(4)
        psizer.Add(self._nameControl)
        psizer.AddSpacer(10)
        psizer.Add(climateLabelText)
        psizer.Add(self._climateControl)
        psizer.AddSpacer(4)

        self._idControl.SetValue("base")
        self._nameControl.SetValue("A simple mission")

        wizard.Layout()
        wizard.FitToPage(page)
        return page

    def RunWizard(self, existingTables = None, existingRelationships = None):
        status = wx.wizard.Wizard.RunWizard(self, self._zoneSettingsPage)
        self.Destroy()
        return status


    def OnWizPageChanging(self, event):
        if event.GetDirection():  # It's going forwards
            if event.GetPage() == self._zoneSettingsPage:
                
                #validation
                self.zoneID = self._idControl.GetValue()
                if not self.zoneID or not self.zoneID.isalpha() or not self.zoneID.islower():
                    wx.MessageBox("Please provide a zone id comprised solely of lowercase letters.", "Invalid Zone ID") 
                    event.Veto()
                    return

                self.zoneName = self._nameControl.GetValue()
                if not self.zoneName:
                    wx.MessageBox("Please provide a descriptive zone name.", "Invalid Zone Name") 
                    event.Veto()
                    return
                
                climateLookup = {"Temperate":"RPG_CLIMATE_TEMPERATE", "Tropical":"RPG_CLIMATE_TROPICAL", "Dry":"RPG_CLIMATE_DRY", "Cold":"RPG_CLIMATE_COLD", "Arctic":"RPG_CLIMATE_POLAR"}
                
                self.zoneClimate = climateLookup[self._climateControl.GetValue()]
                
                self.missionFile = self.zoneID+".mis"


    def OnShowCreatePages(self):
        self.Hide()
        import DataModelEditor
        requestedPos = self.GetPositionTuple()
        projectService = wx.GetApp().GetService(ProjectService)
        projectView = projectService.GetView()

        wiz = DataModelEditor.ImportExportWizard(projectView.GetFrame(), pos=requestedPos)
        if wiz.RunWizard(dontDestroy=True):
           self._schemaName.SetValue(wiz.GetSchemaFileName())
        wiz.Destroy()
        self.Show(True)


#static

ZONEFILE = """from mud.world.defines import *
from genesis.dbdict import DBZone
from mud.world.zone import ZoneLink

zone = DBZone()
zone.name = "%s"
zone.niceName = "%s"
zone.missionFile = "%s"
zone.climate = %s
zone.immTransform = "%s"

import spawns
import spawngroups
import items
import quests
"""

SPAWNSFILE = """from mud.world.defines import *
from mud.world.spawn import SpawnSoundProfile
from genesis.dbdict import *
"""

SPAWNGROUPSFILE = """from mud.world.defines import *
from genesis.dbdict import DBSpawnInfo,DBSpawnGroup

#--- wolf
wolf = DBSpawnInfo(spawn="Grey Wolf")
sg = DBSpawnGroup(zone="%s",groupName="GREYWOLF")
sg.addSpawnInfo(wolf)
"""

ITEMSFILE = """from genesis.dbdict import *
from mud.world.defines import *"""

QUESTSFILE = """from mud.world.defines import *
from genesis.dbdict import *
"""
WORLDFILE = """from mud.world.theworld import World
world = World.byName("TheWorld")

world.startZone = "%s"
world.dstartZone = "%s"
world.mstartZone = "%s"

"""

        