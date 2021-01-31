#----------------------------------------------------------------------------
# Name:         IDE.py
# Purpose:      IDE using Python extensions to the wxWindows docview framework
#
# Author:       Peter Yared
#
# Created:      5/15/03
# Copyright:    (c) 2003-2005 ActiveGrid, Inc.
# CVS-ID:       $Id: IDE.py 6631 2005-12-19 19:00:59Z mhua $
# License:      wxWindows License
#----------------------------------------------------------------------------

import wx
import wx.lib.docview
import wx.lib.pydocview
import sys
import wx.grid
import os.path
import mmoide.util.sysutils as sysutilslib
import mmoide.util.appdirs as appdirs

#the IDE doesn't (currently need these) and they are solely here for the binary build 
#as twisted has a bunch of warnings regarding Python 2.6 (with becoming a reserved keyword)
#and by importing here, we get this in the console the first time and not when running Genesis
#which interprets it as an error
from twisted.spread import pb
from twisted.internet import reactor

_ = wx.GetTranslation
ACTIVEGRID_BASE_IDE = False
#----------------------------------------------------------------------------
# Helper functions for command line args
#----------------------------------------------------------------------------

# Since Windows accept command line options with '/', but this character
# is used to denote absolute path names on other platforms, we need to
# conditionally handle '/' style arguments on Windows only.
def printArg(argname):
    output = "'-" + argname + "'"
    if wx.Platform == "__WXMSW__":
        output = output + " or '/" + argname + "'"
        
    return output
        
def isInArgs(argname, argv):
    result = False
    if ("-" + argname) in argv:
        result = True
    if wx.Platform == "__WXMSW__" and ("/" + argname) in argv:
        result = True
        
    return result

#----------------------------------------------------------------------------
# Classes
#----------------------------------------------------------------------------

class IDEApplication(wx.lib.pydocview.DocApp):

    def __init__(self, redirect=False):
        wx.lib.pydocview.DocApp.__init__(self, redirect=redirect)

    def OnInit(self):
        global ACTIVEGRID_BASE_IDE
        
        args = sys.argv
                    
        if "-h" in args or "-help" in args or "--help" in args\
            or (wx.Platform == "__WXMSW__" and "/help" in args):
            print "Usage: ActiveGridAppBuilder.py [options] [filenames]\n"
            # Mac doesn't really support multiple instances for GUI apps
            # and since we haven't got time to test this thoroughly I'm 
            # disabling it for now.
            if wx.Platform != "__WXMAC__":
                print "    option " + printArg("multiple") + " to allow multiple instances of application."
            print "    option " + printArg("debug") + " for debug mode."
            print "    option '-h' or " + printArg("help") + " to show usage information for command."
            print "    option " + printArg("baseide") + " for base IDE mode."
            print "    [filenames] is an optional list of files you want to open when application starts."
            return False
        elif isInArgs("dev", args):
            self.SetAppName(_("ActiveGrid Application Builder Dev"))
            self.SetDebug(False)
        elif isInArgs("debug", args):
            self.SetAppName(_("ActiveGrid Application Builder Debug"))
            self.SetDebug(True)
            self.SetSingleInstance(False)
        elif isInArgs("baseide", args):
            self.SetAppName(_("Torque MMO Kit IDE"))
            ACTIVEGRID_BASE_IDE = True
        else:
            self.SetAppName(_("ActiveGrid Application Builder"))
            self.SetDebug(False)
        if isInArgs("multiple", args) and wx.Platform != "__WXMAC__":
            self.SetSingleInstance(False)

            
        if not wx.lib.pydocview.DocApp.OnInit(self):
            return False
        
        jpg = wx.Image('./mmoide/tool/data/splash.jpg', wx.BITMAP_TYPE_JPEG).ConvertToBitmap()

        self.ShowSplash(jpg)

        import STCTextEditor
        import FindInDirService
        import MarkerService
        import project as projectlib
        import ProjectEditor
        import PythonEditor
        import OutlineService
        import TabbedView
        import MessageService
        import Service
        import wx.lib.ogl as ogl
        #import DebuggerService
        import AboutDialog
        #import SVNService
        import ExtensionService
        
        import ZoneService
        import WorldService
        import MMOService
                            
        _EDIT_LAYOUTS = True
        
        # This creates some pens and brushes that the OGL library uses.
        # It should be called after the app object has been created, but
        # before OGL is used.
        ogl.OGLInitialize()

        config = wx.FileConfig(self.GetAppName(),"MMOWorkshop.com",os.getcwd()+"/projects/ideconfig.ini","",style = wx.CONFIG_USE_LOCAL_FILE)
        wx.ConfigBase_Set(config)
        
        if not config.Exists("MDIFrameMaximized"):  # Make the initial MDI frame maximize as default
            config.WriteInt("MDIFrameMaximized", True)
        if not config.Exists("MDIEmbedRightVisible"):  # Make the properties embedded window hidden as default
            config.WriteInt("MDIEmbedRightVisible", False)

        docManager = wx.lib.docview.DocManager(flags = self.GetDefaultDocManagerFlags())
        self.SetDocumentManager(docManager)

        defaultTemplate = wx.lib.docview.DocTemplate(docManager,
                _("Any"),
                "*.*",
                _("Any"),
                _(".txt"),
                _("Text Document"),
                _("Text View"),
                STCTextEditor.TextDocument,
                STCTextEditor.TextView,
                wx.lib.docview.TEMPLATE_INVISIBLE,
                icon = STCTextEditor.getTextIcon())
        docManager.AssociateTemplate(defaultTemplate)



        projectTemplate = ProjectEditor.ProjectTemplate(docManager,
                _("Project"),
                "*.agp",
                _("Project"),
                _(".agp"),
                _("Project Document"),
                _("Project View"),
                ProjectEditor.ProjectDocument,
                ProjectEditor.ProjectView,
                icon = ProjectEditor.getProjectIcon())
        docManager.AssociateTemplate(projectTemplate)

        pythonTemplate = wx.lib.docview.DocTemplate(docManager,
                _("Python"),
                "*.py",
                _("Python"),
                _(".py"),
                _("Python Document"),
                _("Python View"),
                PythonEditor.PythonDocument,
                PythonEditor.PythonView,
                icon = PythonEditor.getPythonIcon())
        docManager.AssociateTemplate(pythonTemplate)


        textTemplate = wx.lib.docview.DocTemplate(docManager,
                _("Text"),
                "*.text;*.txt",
                _("Text"),
                _(".txt"),
                _("Text Document"),
                _("Text View"),
                STCTextEditor.TextDocument,
                STCTextEditor.TextView,
                icon = STCTextEditor.getTextIcon())
        docManager.AssociateTemplate(textTemplate)

        
        textService             = self.InstallService(STCTextEditor.TextService())
        pythonService           = self.InstallService(PythonEditor.PythonService())
        projectService          = self.InstallService(ProjectEditor.ProjectService("Projects", embeddedWindowLocation = wx.lib.pydocview.EMBEDDED_WINDOW_TOPLEFT))
        findService             = self.InstallService(FindInDirService.FindInDirService())
        outlineService          = self.InstallService(OutlineService.OutlineService("Outline", embeddedWindowLocation = wx.lib.pydocview.EMBEDDED_WINDOW_BOTTOMLEFT))
        filePropertiesService   = self.InstallService(wx.lib.pydocview.FilePropertiesService())
        markerService           = self.InstallService(MarkerService.MarkerService())
        messageService          = self.InstallService(MessageService.MessageService("Messages", embeddedWindowLocation = wx.lib.pydocview.EMBEDDED_WINDOW_BOTTOM))
        #debuggerService         = self.InstallService(DebuggerService.DebuggerService("Debugger", embeddedWindowLocation = wx.lib.pydocview.EMBEDDED_WINDOW_BOTTOM))
        extensionService        = self.InstallService(ExtensionService.ExtensionService())
        optionsService          = self.InstallService(wx.lib.pydocview.DocOptionsService(supportedModes=wx.lib.docview.DOC_MDI))
        aboutService            = self.InstallService(wx.lib.pydocview.AboutService(AboutDialog.AboutDialog))
        #svnService              = self.InstallService(SVNService.SVNService())
        
        worldService             = self.InstallService(WorldService.WorldService())
        zoneService             = self.InstallService(ZoneService.ZoneService())
        mmoService             = self.InstallService(MMOService.MMOService())

        # order of these added determines display order of Options Panels
        optionsService.AddOptionsPanel(ProjectEditor.ProjectOptionsPanel)
        #optionsService.AddOptionsPanel(DebuggerService.DebuggerOptionsPanel)
        optionsService.AddOptionsPanel(PythonEditor.PythonOptionsPanel)
        optionsService.AddOptionsPanel(STCTextEditor.TextOptionsPanel)
        #optionsService.AddOptionsPanel(SVNService.SVNOptionsPanel)
        optionsService.AddOptionsPanel(ExtensionService.ExtensionOptionsPanel)

        filePropertiesService.AddCustomEventHandler(projectService)

        outlineService.AddViewTypeForBackgroundHandler(PythonEditor.PythonView)
        outlineService.AddViewTypeForBackgroundHandler(ProjectEditor.ProjectView) # special case, don't clear outline if in project
        outlineService.AddViewTypeForBackgroundHandler(MessageService.MessageView) # special case, don't clear outline if in message window
        outlineService.StartBackgroundTimer()
        
        projectService.AddLogicalViewFolderDefault(".gif", _("Images"))
        projectService.AddLogicalViewFolderDefault(".jpeg", _("Images"))
        projectService.AddLogicalViewFolderDefault(".jpg", _("Images"))
        projectService.AddLogicalViewFolderDefault(".py", None)
    
        
        self.SetDefaultIcon(getActiveGridIcon())
        embeddedWindows = wx.lib.pydocview.EMBEDDED_WINDOW_TOPLEFT | wx.lib.pydocview.EMBEDDED_WINDOW_BOTTOMLEFT |wx.lib.pydocview.EMBEDDED_WINDOW_BOTTOM
        if self.GetUseTabbedMDI():
            self.frame = IDEDocTabbedParentFrame(docManager, None, -1, wx.GetApp().GetAppName(), embeddedWindows=embeddedWindows)
        else:
            self.frame = IDEMDIParentFrame(docManager, None, -1, wx.GetApp().GetAppName(), embeddedWindows=embeddedWindows)
        self.frame.Show(True)


        wx.lib.pydocview.DocApp.CloseSplash(self)
        self.OpenCommandLineArgs()

        if not projectService.OpenSavedProjects() and not docManager.GetDocuments() and self.IsSDI():  # Have to open something if it's SDI and there are no projects...
            projectTemplate.CreateDocument('', wx.lib.docview.DOC_NEW).OnNewDocument()
            
        tips_path = os.path.join(sysutilslib.mainModuleDir, "activegrid", "tool", "data", "tips.txt")
            
        # wxBug: On Mac, having the updates fire while the tip dialog is at front
        # for some reason messes up menu updates. This seems a low-level wxWidgets bug,
        # so until I track this down, turn off UI updates while the tip dialog is showing.
        #wx.UpdateUIEvent.SetUpdateInterval(-1)
        #appUpdater = updater.AppUpdateService(self)
        #appUpdater.RunUpdateIfNewer()
        if os.path.isfile(tips_path):
            self.ShowTip(docManager.FindSuitableParent(), wx.CreateFileTipProvider(tips_path, 0))

        wx.UpdateUIEvent.SetUpdateInterval(1000)  # Overhead of updating menus was too much.  Change to update every n milliseconds.

        # we need this for a while due to the Mac 1.0 release which put things
        # in ~/Documents/ActiveGrid Projects/demos.
        # Now it should be ~/Documents/ActiveGrid Demos/ 
        base_path = appdirs.documents_folder
        if os.path.isdir(os.path.join(base_path, "ActiveGrid Projects", "demos")):
            message = _("The location where demo files are stored has changed between the 1.0 and 1.1 release as a result of improved multi-user support across platforms. In order for ActiveGrid Application Builder to find these files, they need to be moved from '%s/ActiveGrid Projects/demos' to '%s/ActiveGrid Demos'. Click OK to move the files.") % (base_path, base_path)
            wx.MessageBox(message, _("Demo Files Location Update"))
            import shutil
            shutil.copytree(os.path.join(base_path, "ActiveGrid Projects", "demos"), os.path.join(base_path, "ActiveGrid Demos"))
            shutil.rmtree(os.path.join(base_path, "ActiveGrid Projects"))

        
        return True


class IDEDocTabbedParentFrame(wx.lib.pydocview.DocTabbedParentFrame):
    
    # wxBug: Need this for linux. The status bar created in pydocview is
    # replaced in IDE.py with the status bar for the code editor. On windows
    # this works just fine, but on linux the pydocview status bar shows up near
    # the top of the screen instead of disappearing. 
    def CreateDefaultStatusBar(self):
       pass
       
class IDEMDIParentFrame(wx.lib.pydocview.DocMDIParentFrame):
    
    # wxBug: Need this for linux. The status bar created in pydocview is
    # replaced in IDE.py with the status bar for the code editor. On windows
    # this works just fine, but on linux the pydocview status bar shows up near
    # the top of the screen instead of disappearing. 
    def CreateDefaultStatusBar(self):
       pass

#----------------------------------------------------------------------------
# Icon Bitmaps - generated by encode_bitmaps.py
#----------------------------------------------------------------------------
from wx import ImageFromStream, BitmapFromImage
import cStringIO

#----------------------------------------------------------------------

#----------------------------------------------------------------------
def getActiveGridData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x02\
\x00\x00\x00\x90\x91h6\x00\x00\x00\x03sBIT\x08\x08\x08\xdb\xe1O\xe0\x00\x00\
\x02\x10IDAT(\x91\x95\x92Kk\x13a\x14\x86\xcf7\xb7d\x92I\xa7I\'7\xa9)\x1a\xab\
\xb5\xc1R\xabh\x15\x04\x91\xd2\x8d\x08\xaet\'\xf4?\xf87\xfc\r\xee\xdc\xb8\
\xd0E\xc1\x8d(bP\xf0\x86Z/i\x02m\x9a\x98\xa9\xc9d&\x9d\xc9\xdc\xe7\x9b\xf9\
\xdc\x84Rb@|\x97\xe7\x9c\x07^x\x0e"\x84\xc0\xff\x84\x998m\x7f}j\xd4\x9f\xc8n\
\xd1d\xe7o\xdf\xd9@\x88:\\Q\x7f_\xebJ\xb3\xbd\xb59-\xb2y\xde\xc8\xe3\xf7\xb5\
7\x8f\x8e\xb6\x98\x00\xb4\xb66\tv\xf6~\xfb\x10\x1a\t\xc6\xea\xec~&Q8\xb9R\
\x14a\xa3\xbf\xa7\xb6\xbf$hp\xfc\xa0\xa6\x10u\x18\x9d\xb9P\xa1hf\x1c\xc0\xbe\
\xd3\xf9\xf1Lm\xbeS\x15\x99\xa1B+ \x1e\x06\x96\x02\x9a\xa6OWV}[e\xe3"\xa2\
\x98\x11\xe0Y\x83\xed\x97\x0f8\xbf)q H\xa4\xa3\x11\xdb\x8b,\x8f\xeckAnv\xc5\
\xb4\xd9~\xf5q\x02\xf6sgoN\x1f\xbf\xc4\x00@\xe3\xedC\xceo\n1\x12ci!\x81x6\
\xdc\xe9\xa1\xbe\x11F\x84.\xcc\x9d\xcag\x93;\xdb\xbf\x1c\xaf^\xab\x0eS\xd2+\
\n\x00\xec\xeeG\x8e&b:#-,%\xc5l\x8c\xa3\xae,\x1d\xbbq1wn\x8e\xf9\xf6\xe1E*\
\x9d\xe1\xd3E3\x10\xf2\x8bk\xf9\xf2U\x06\x00\x10\x10\x00\xc4\xcf\xe4P\xa1\
\x14*\xdd\x08h\x96\x17y\xd7\x88s(I\xe9\x8d\xfa\xcf\xd2\xca]~\xba\x14\xf4?iz\
\x86\x01\x00N<\xe9\xb9MM\x96\x13\xba\xae\xabj\x80#\xa5\xd7\x1b\x98\x9e\x87!\
\x19G\xc3AO\xa8,\x0b\xe7oEx]\xdb}M\x01\xc0\x89\xcb\x1b.\x11z\x8a\xd1i\xc9\
\x86\xe5\x99\x0e\x96\xbb\x9a6\xb0\\\x0f|\x8cf2\xe2H\x19\x13\x93\xe6\xd7(\x00\
\x98\xca\x96\xcb\xd7\xef\xe3\xd8\xec\x81\x03\xa6\x0b\xa6K\x0c;\xd4\xed\xe8\
\xc0\x8e0\x95,\x96\x16\x8e\xbaB\x87\xda\xb1o\xb7\xbe?\x97\x1bUC\x95]\x0f\x0f\
\x1d\x12\xd2S\xab\xeb\xf7\x16\x97\xafM\x06F\xb2\xc3@W\xe5\xa1\xaeF@K\x85\x92\
\x90J\x8f=\xce8\xf0\xcf\xfc\x01\xc1h\x0bqbR\xd1\'\x00\x00\x00\x00IEND\xaeB`\
\x82' 

def getActiveGridBitmap():
    return BitmapFromImage(getActiveGridImage())

def getActiveGridImage():
    stream = cStringIO.StringIO(getActiveGridData())
    return ImageFromStream(stream)

def getActiveGridIcon():
    return wx.IconFromBitmap(getActiveGridBitmap())
    
#----------------------------------------------------------------------
def getSkinData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01CIDAT8\x8d\x85\x931K\xc3@\x14\x80\xbf\xd4\xba\xb5\xfe\x04\x03J\xe9Vp\
5\x83Z\x97\xacB;dppw\x10\x04\x05\xa9\xa0\x90:\xa8\xa3\x14qs(8\xd4\xa1\x9bd\
\xa9\x8b\x08\x15\xe2$\x82\xb4)U\x8b\x93\x8b\x11\x1d\x14\xe2\x10\x936\xb9$}\
\x10\xc8\xe3\xe5\xfb\xde\xbb\xcb\x9dt\xdb6\x1dB\xd1\xee}\xf9\xef\x1b\xda\x82\
\x14\xae\x8fF\n \x93\x9f\x0b<EU\x01@V\x14\xd6\xab\x17B\x03A\x10\x17\xb3YX^-%\
J\xd2I\x82\xb3Z#\xa9\x9c,\x90\x15\x05\xd9]\t\xa7\xbbGB\xfd\xa7\xba\xe2\x00\
\xa4F7\xcc\x8b\xae\x9d\xdc\xd5\x83#'\x08\xc3\xe1\xdc\x83_\xee\xbf9\xb7\x1e\
\x87\x82\xa8\xae\xe3\xe0\xfa\xd3\xaf+\x18\xd75\x0e\xee|\x0e\xa4t\xc7z\xf37+v\
\x92\xcb\x13\xeaK:\x00\xbd\xc1\x9e\x0fC\xe8\x1c\x84\xe1BS\xa3\xd0\xd4\xa8\
\xed\xcc\xa3\xb7*\x00\x01\xd8\x17t\xedh\x18 S\xdc\x02`[\x9dDoU\x020\x80\xa4\
\xae\x1d\n\xa7l3o\x06\xe0\x87\xe32\xaf\x96\xfb\xd9\xbe\xd9\x0f\n\xa4\xd4\x84\
\x9f\x18\x07eA\xd67\xef\xc8\x19\xef\x00,~\xd8\xc2\xc5\xf2\x7f\xe3\xf5T\xd6\
\x996\x87\xebx6n\x00\xc8\xfd\xe7Q\xb00\x81UR\x85\tf\x1aW\x89\xd7\xf9\x0f\x9f\
\xff\x90p\xb7%\x8e\xf9\x00\x00\x00\x00IEND\xaeB`\x82" 

def getSkinBitmap():
    return BitmapFromImage(getSkinImage())

def getSkinImage():
    stream = cStringIO.StringIO(getSkinData())
    return ImageFromStream(stream)

def getSkinIcon():
    return wx.IconFromBitmap(getSkinBitmap())

