#----------------------------------------------------------------------------
# Name:         FindService.py
# Purpose:      Find Service for pydocview
#
# Author:       Peter Yared, Morgan Hua
#
# Created:      8/15/03
# CVS-ID:       $Id: FindService.py 6631 2005-12-19 19:00:59Z mhua $
# Copyright:    (c) 2003-2005 ActiveGrid, Inc.
# License:      wxWindows License
#----------------------------------------------------------------------------

import wx
import wx.lib.docview
import wx.lib.pydocview
import re
_ = wx.GetTranslation


#----------------------------------------------------------------------------
# Constants
#----------------------------------------------------------------------------
FIND_MATCHPATTERN = "FindMatchPattern"
FIND_MATCHREPLACE = "FindMatchReplace"
FIND_MATCHCASE = "FindMatchCase"
FIND_MATCHWHOLEWORD = "FindMatchWholeWordOnly"
FIND_MATCHREGEXPR = "FindMatchRegularExpr"
FIND_MATCHWRAP = "FindMatchWrap"
FIND_MATCHUPDOWN = "FindMatchUpDown"

FIND_SYNTAXERROR = -2

SPACE = 10
HALF_SPACE = 5


#----------------------------------------------------------------------------
# Classes
#----------------------------------------------------------------------------

class FindService(wx.lib.pydocview.DocService):

    #----------------------------------------------------------------------------
    # Constants
    #----------------------------------------------------------------------------
    FIND_ID = wx.NewId()            # for bringing up Find dialog box
    FINDONE_ID = wx.NewId()         # for doing Find
    FIND_PREVIOUS_ID = wx.NewId()   # for doing Find Next
    FIND_NEXT_ID = wx.NewId()       # for doing Find Prev
    REPLACE_ID = wx.NewId()         # for bringing up Replace dialog box
    REPLACEONE_ID = wx.NewId()      # for doing a Replace
    REPLACEALL_ID = wx.NewId()      # for doing Replace All
    GOTO_LINE_ID = wx.NewId()       # for bringing up Goto dialog box

    # Extending bitmasks: wx.FR_WHOLEWORD, wx.FR_MATCHCASE, and wx.FR_DOWN
    FR_REGEXP = max([wx.FR_WHOLEWORD, wx.FR_MATCHCASE, wx.FR_DOWN]) << 1
    FR_WRAP = FR_REGEXP << 1


    def __init__(self):
        self._replaceDialog = None
        self._findDialog = None
        self._findReplaceData = wx.FindReplaceData()
        self._findReplaceData.SetFlags(wx.FR_DOWN)


    def InstallControls(self, frame, menuBar = None, toolBar = None, statusBar = None, document = None):
        """ Install Find Service Menu Items """
        editMenu = menuBar.GetMenu(menuBar.FindMenu(_("&Edit")))
        editMenu.AppendSeparator()
        editMenu.Append(FindService.FIND_ID, _("&Find...\tCtrl+F"), _("Finds the specified text"))
        wx.EVT_MENU(frame, FindService.FIND_ID, frame.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, FindService.FIND_ID, frame.ProcessUpdateUIEvent)
        editMenu.Append(FindService.FIND_PREVIOUS_ID, _("Find &Previous\tShift+F3"), _("Finds the specified text"))
        wx.EVT_MENU(frame, FindService.FIND_PREVIOUS_ID, frame.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, FindService.FIND_PREVIOUS_ID, frame.ProcessUpdateUIEvent)
        editMenu.Append(FindService.FIND_NEXT_ID, _("Find &Next\tF3"), _("Finds the specified text"))
        wx.EVT_MENU(frame, FindService.FIND_NEXT_ID, frame.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, FindService.FIND_NEXT_ID, frame.ProcessUpdateUIEvent)
        editMenu.Append(FindService.REPLACE_ID, _("R&eplace...\tCtrl+H"), _("Replaces specific text with different text"))
        wx.EVT_MENU(frame, FindService.REPLACE_ID, frame.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, FindService.REPLACE_ID, frame.ProcessUpdateUIEvent)
        editMenu.Append(FindService.GOTO_LINE_ID, _("&Go to Line...\tCtrl+G"), _("Goes to a certain line in the file"))
        wx.EVT_MENU(frame, FindService.GOTO_LINE_ID, frame.ProcessEvent)
        wx.EVT_UPDATE_UI(frame, FindService.GOTO_LINE_ID, frame.ProcessUpdateUIEvent)

        # wxBug: wxToolBar::GetToolPos doesn't exist, need it to find cut tool and then insert find in front of it.
        toolBar.InsertTool(6, FindService.FIND_ID, getFindBitmap(), shortHelpString = _("Find"), longHelpString = _("Finds the specified text"))
        toolBar.InsertSeparator(6)
        toolBar.Realize()

        frame.Bind(wx.EVT_FIND, frame.ProcessEvent)
        frame.Bind(wx.EVT_FIND_NEXT, frame.ProcessEvent)
        frame.Bind(wx.EVT_FIND_REPLACE, frame.ProcessEvent)
        frame.Bind(wx.EVT_FIND_REPLACE_ALL, frame.ProcessEvent)


    def ProcessUpdateUIEvent(self, event):
        id = event.GetId()
        if (id == FindService.FIND_ID
        or id == FindService.FIND_PREVIOUS_ID
        or id == FindService.FIND_NEXT_ID
        or id == FindService.REPLACE_ID
        or id == FindService.GOTO_LINE_ID):
            event.Enable(False)
            return True
        else:
            return False


    def ShowFindReplaceDialog(self, findString="", replace = False):
        """ Display find/replace dialog box.
        
            Parameters: findString is the default value shown in the find/replace dialog input field.
            If replace is True, the replace dialog box is shown, otherwise only the find dialog box is shown. 
        """
        if replace:
            if self._findDialog != None:
                # No reason to have both find and replace dialogs up at the same time
                self._findDialog.DoClose()
                self._findDialog = None

            self._replaceDialog = FindReplaceDialog(self.GetDocumentManager().FindSuitableParent(), -1, _("Replace"), size=(320,200), findString=findString)
            self._replaceDialog.CenterOnParent()
            self._replaceDialog.Show(True)
        else:
            if self._replaceDialog != None:
                # No reason to have both find and replace dialogs up at the same time
                self._replaceDialog.DoClose()
                self._replaceDialog = None

            self._findDialog = FindDialog(self.GetDocumentManager().FindSuitableParent(), -1, _("Find"), size=(320,200), findString=findString)
            self._findDialog.CenterOnParent()
            self._findDialog.Show(True)



    def OnFindClose(self, event):
        """ Cleanup handles when find/replace dialog is closed """
        if self._findDialog != None:
            self._findDialog = None
        elif self._replaceDialog != None:
            self._replaceDialog = None


    def GetCurrentDialog(self):
        """ return handle to either the find or replace dialog """
        if self._findDialog != None:
            return self._findDialog
        return self._replaceDialog


    def GetLineNumber(self, parent):
        """ Display Goto Line Number dialog box """
        line = -1
        dialog = wx.TextEntryDialog(parent, _("Enter line number to go to:"), _("Go to Line"))
        dialog.CenterOnParent()
        if dialog.ShowModal() == wx.ID_OK:
            try:
                line = int(dialog.GetValue())
                if line > 65535:
                    line = 65535
            except:
                pass
        dialog.Destroy()
        # This one is ugly:  wx.GetNumberFromUser("", _("Enter line number to go to:"), _("Go to Line"), 1, min = 1, max = 65535, parent = parent)
        return line


    def DoFind(self, findString, replaceString, text, startLoc, endLoc, down, matchCase, wholeWord, regExpr = False, replace = False, replaceAll = False, wrap = False):
        """ Do the actual work of the find/replace.
        
            Returns the tuple (count, start, end, newText).
            count = number of string replacements
            start = start position of found string
            end = end position of found string
            newText = new replaced text 
        """
        flags = 0
        if regExpr:
            pattern = findString
        else:
            pattern = re.escape(findString)  # Treat the strings as a literal string
        if not matchCase:
            flags = re.IGNORECASE
        if wholeWord:
            pattern = r"\b%s\b" % pattern
            
        try:
            reg = re.compile(pattern, flags)
        except:
            # syntax error of some sort
            import sys
            msgTitle = wx.GetApp().GetAppName()
            if not msgTitle:
                msgTitle = _("Regular Expression Search")
            wx.MessageBox(_("Invalid regular expression \"%s\". %s") % (pattern, sys.exc_value),
                          msgTitle,
                          wx.OK | wx.ICON_EXCLAMATION,
                          self.GetView())
            return FIND_SYNTAXERROR, None, None, None

        if replaceAll:
            newText, count = reg.subn(replaceString, text)
            if count == 0:
                return -1, None, None, None
            else:
                return count, None, None, newText

        start = -1
        if down:
            match = reg.search(text, endLoc)
            if match == None:
                if wrap:  # try again, but this time from top of file
                    match = reg.search(text, 0)
                    if match == None:
                        return -1, None, None, None
                else:
                    return -1, None, None, None
            start = match.start()
            end = match.end()
        else:
            match = reg.search(text)
            if match == None:
                return -1, None, None, None
            found = None
            i, j = match.span()
            while i < startLoc and j <= startLoc:
                found = match
                if i == j:
                    j = j + 1
                match = reg.search(text, j)
                if match == None:
                    break
                i, j = match.span()
            if found == None:
                if wrap:  # try again, but this time from bottom of file
                    match = reg.search(text, startLoc)
                    if match == None:
                        return -1, None, None, None
                    found = None
                    i, j = match.span()
                    end = len(text)
                    while i < end and j <= end:
                        found = match
                        if i == j:
                            j = j + 1
                        match = reg.search(text, j)
                        if match == None:
                            break
                        i, j = match.span()
                    if found == None:
                        return -1, None, None, None
                else:
                    return -1, None, None, None
            start = found.start()
            end = found.end()

        if replace and start != -1:
            newText, count = reg.subn(replaceString, text, 1)
            return count, start, end, newText

        return 0, start, end, None


    def SaveFindConfig(self, findString, wholeWord, matchCase, regExpr = None, wrap = None, upDown = None, replaceString = None):
        """ Save find/replace patterns and search flags to registry.
        
            findString = search pattern
            wholeWord = match whole word only
            matchCase = match case
            regExpr = use regular expressions in search pattern
            wrap = return to top/bottom of file on search
            upDown = search up or down from current cursor position
            replaceString = replace string
        """
        config = wx.ConfigBase_Get()

        config.Write(FIND_MATCHPATTERN, findString)
        config.WriteInt(FIND_MATCHCASE, matchCase)
        config.WriteInt(FIND_MATCHWHOLEWORD, wholeWord)
        if replaceString != None:
            config.Write(FIND_MATCHREPLACE, replaceString)
        if regExpr != None:
            config.WriteInt(FIND_MATCHREGEXPR, regExpr)
        if wrap != None:
            config.WriteInt(FIND_MATCHWRAP, wrap)
        if upDown != None:
            config.WriteInt(FIND_MATCHUPDOWN, upDown)


    def GetFindString(self):
        """ Load the search pattern from registry """
        return wx.ConfigBase_Get().Read(FIND_MATCHPATTERN, "")


    def GetReplaceString(self):
        """ Load the replace pattern from registry """
        return wx.ConfigBase_Get().Read(FIND_MATCHREPLACE, "")


    def GetFlags(self):
        """ Load search parameters from registry """
        config = wx.ConfigBase_Get()

        flags = 0
        if config.ReadInt(FIND_MATCHWHOLEWORD, False):
            flags = flags | wx.FR_WHOLEWORD
        if config.ReadInt(FIND_MATCHCASE, False):
            flags = flags | wx.FR_MATCHCASE
        if config.ReadInt(FIND_MATCHUPDOWN, False):
            flags = flags | wx.FR_DOWN
        if config.ReadInt(FIND_MATCHREGEXPR, False):
            flags = flags | FindService.FR_REGEXP
        if config.ReadInt(FIND_MATCHWRAP, False):
            flags = flags | FindService.FR_WRAP
        return flags


class FindDialog(wx.Dialog):
    """ Find Dialog with regular expression matching and wrap to top/bottom of file. """

    def __init__(self, parent, id, title, size, findString=None):
        wx.Dialog.__init__(self, parent, id, title, size=size)

        config = wx.ConfigBase_Get()
        borderSizer = wx.BoxSizer(wx.VERTICAL)
        gridSizer = wx.GridBagSizer(SPACE, SPACE)

        lineSizer = wx.BoxSizer(wx.HORIZONTAL)
        lineSizer.Add(wx.StaticText(self, -1, _("Find what:")), 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, SPACE)
        if not findString:
            findString = config.Read(FIND_MATCHPATTERN, "")
        self._findCtrl = wx.TextCtrl(self, -1, findString, size=(200,-1))
        lineSizer.Add(self._findCtrl, 0)
        gridSizer.Add(lineSizer, pos=(0,0), span=(1,2))
        choiceSizer = wx.BoxSizer(wx.VERTICAL)
        self._wholeWordCtrl = wx.CheckBox(self, -1, _("Match whole word only"))
        self._wholeWordCtrl.SetValue(config.ReadInt(FIND_MATCHWHOLEWORD, False))
        self._matchCaseCtrl = wx.CheckBox(self, -1, _("Match case"))
        self._matchCaseCtrl.SetValue(config.ReadInt(FIND_MATCHCASE, False))
        self._regExprCtrl = wx.CheckBox(self, -1, _("Regular expression"))
        self._regExprCtrl.SetValue(config.ReadInt(FIND_MATCHREGEXPR, False))
        self._wrapCtrl = wx.CheckBox(self, -1, _("Wrap"))
        self._wrapCtrl.SetValue(config.ReadInt(FIND_MATCHWRAP, False))
        choiceSizer.Add(self._wholeWordCtrl, 0, wx.BOTTOM, SPACE)
        choiceSizer.Add(self._matchCaseCtrl, 0, wx.BOTTOM, SPACE)
        choiceSizer.Add(self._regExprCtrl, 0, wx.BOTTOM, SPACE)
        choiceSizer.Add(self._wrapCtrl, 0)
        gridSizer.Add(choiceSizer, pos=(1,0), span=(2,1))

        self._radioBox = wx.RadioBox(self, -1, _("Direction"), choices = ["Up", "Down"])
        self._radioBox.SetSelection(config.ReadInt(FIND_MATCHUPDOWN, 1))
        gridSizer.Add(self._radioBox, pos=(1,1), span=(2,1))

        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        findBtn = wx.Button(self, FindService.FINDONE_ID, _("Find Next"))
        findBtn.SetDefault()
        wx.EVT_BUTTON(self, FindService.FINDONE_ID, self.OnActionEvent)
        cancelBtn = wx.Button(self, wx.ID_CANCEL)
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self.OnClose)
        BTM_SPACE = HALF_SPACE
        if wx.Platform == "__WXMAC__":
            BTM_SPACE = SPACE
        buttonSizer.Add(findBtn, 0, wx.BOTTOM, BTM_SPACE)
        buttonSizer.Add(cancelBtn, 0)
        gridSizer.Add(buttonSizer, pos=(0,2), span=(3,1))

        borderSizer.Add(gridSizer, 0, wx.ALL, SPACE)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetSizer(borderSizer)
        self.Fit()
        self._findCtrl.SetFocus()

    def SaveConfig(self):
        """ Save find patterns and search flags to registry. """
        findService = wx.GetApp().GetService(FindService)
        if findService:
            findService.SaveFindConfig(self._findCtrl.GetValue(),
                                       self._wholeWordCtrl.IsChecked(),
                                       self._matchCaseCtrl.IsChecked(),
                                       self._regExprCtrl.IsChecked(),
                                       self._wrapCtrl.IsChecked(),
                                       self._radioBox.GetSelection(),
                                       )


    def DoClose(self):
        self.SaveConfig()
        self.Destroy()


    def OnClose(self, event):
        findService = wx.GetApp().GetService(FindService)
        if findService:
            findService.OnFindClose(event)
        self.DoClose()


    def OnActionEvent(self, event):
        self.SaveConfig()

        if wx.GetApp().GetDocumentManager().GetFlags() & wx.lib.docview.DOC_MDI:
            if wx.GetApp().GetTopWindow().ProcessEvent(event):
                return True
        else:
            view = wx.GetApp().GetDocumentManager().GetLastActiveView()
            if view and view.ProcessEvent(event):
                return True
        return False


class FindReplaceDialog(FindDialog):
    """ Find/Replace Dialog with regular expression matching and wrap to top/bottom of file. """

    def __init__(self, parent, id, title, size, findString=None):
        wx.Dialog.__init__(self, parent, id, title, size=size)

        config = wx.ConfigBase_Get()
        borderSizer = wx.BoxSizer(wx.VERTICAL)
        gridSizer = wx.GridBagSizer(SPACE, SPACE)

        gridSizer2 = wx.GridBagSizer(SPACE, SPACE)
        gridSizer2.Add(wx.StaticText(self, -1, _("Find what:")), flag=wx.ALIGN_CENTER_VERTICAL, pos=(0,0))
        if not findString:
            findString = config.Read(FIND_MATCHPATTERN, "")
        self._findCtrl = wx.TextCtrl(self, -1, findString, size=(200,-1))
        gridSizer2.Add(self._findCtrl, pos=(0,1))
        gridSizer2.Add(wx.StaticText(self, -1, _("Replace with:")), flag=wx.ALIGN_CENTER_VERTICAL, pos=(1,0))
        self._replaceCtrl = wx.TextCtrl(self, -1, config.Read(FIND_MATCHREPLACE, ""), size=(200,-1))
        gridSizer2.Add(self._replaceCtrl, pos=(1,1))
        gridSizer.Add(gridSizer2, pos=(0,0), span=(1,2))
        choiceSizer = wx.BoxSizer(wx.VERTICAL)
        self._wholeWordCtrl = wx.CheckBox(self, -1, _("Match whole word only"))
        self._wholeWordCtrl.SetValue(config.ReadInt(FIND_MATCHWHOLEWORD, False))
        self._matchCaseCtrl = wx.CheckBox(self, -1, _("Match case"))
        self._matchCaseCtrl.SetValue(config.ReadInt(FIND_MATCHCASE, False))
        self._regExprCtrl = wx.CheckBox(self, -1, _("Regular expression"))
        self._regExprCtrl.SetValue(config.ReadInt(FIND_MATCHREGEXPR, False))
        self._wrapCtrl = wx.CheckBox(self, -1, _("Wrap"))
        self._wrapCtrl.SetValue(config.ReadInt(FIND_MATCHWRAP, False))
        choiceSizer.Add(self._wholeWordCtrl, 0, wx.BOTTOM, SPACE)
        choiceSizer.Add(self._matchCaseCtrl, 0, wx.BOTTOM, SPACE)
        choiceSizer.Add(self._regExprCtrl, 0, wx.BOTTOM, SPACE)
        choiceSizer.Add(self._wrapCtrl, 0)
        gridSizer.Add(choiceSizer, pos=(1,0), span=(2,1))

        self._radioBox = wx.RadioBox(self, -1, _("Direction"), choices = ["Up", "Down"])
        self._radioBox.SetSelection(config.ReadInt(FIND_MATCHUPDOWN, 1))
        gridSizer.Add(self._radioBox, pos=(1,1), span=(2,1))

        buttonSizer = wx.BoxSizer(wx.VERTICAL)
        findBtn = wx.Button(self, FindService.FINDONE_ID, _("Find Next"))
        findBtn.SetDefault()
        wx.EVT_BUTTON(self, FindService.FINDONE_ID, self.OnActionEvent)
        cancelBtn = wx.Button(self, wx.ID_CANCEL)
        wx.EVT_BUTTON(self, wx.ID_CANCEL, self.OnClose)
        replaceBtn = wx.Button(self, FindService.REPLACEONE_ID, _("Replace"))
        wx.EVT_BUTTON(self, FindService.REPLACEONE_ID, self.OnActionEvent)
        replaceAllBtn = wx.Button(self, FindService.REPLACEALL_ID, _("Replace All"))
        wx.EVT_BUTTON(self, FindService.REPLACEALL_ID, self.OnActionEvent)
        
        BTM_SPACE = HALF_SPACE
        if wx.Platform == "__WXMAC__":
            BTM_SPACE = SPACE
            
        buttonSizer.Add(findBtn, 0, wx.BOTTOM, BTM_SPACE)
        buttonSizer.Add(replaceBtn, 0, wx.BOTTOM, BTM_SPACE)
        buttonSizer.Add(replaceAllBtn, 0, wx.BOTTOM, BTM_SPACE)
        buttonSizer.Add(cancelBtn, 0)
        gridSizer.Add(buttonSizer, pos=(0,2), span=(3,1))

        borderSizer.Add(gridSizer, 0, wx.ALL, SPACE)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.SetSizer(borderSizer)
        self.Fit()
        self._findCtrl.SetFocus()
        

    def SaveConfig(self):
        """ Save find/replace patterns and search flags to registry. """
        findService = wx.GetApp().GetService(FindService)
        if findService:
            findService.SaveFindConfig(self._findCtrl.GetValue(),
                                       self._wholeWordCtrl.IsChecked(),
                                       self._matchCaseCtrl.IsChecked(),
                                       self._regExprCtrl.IsChecked(),
                                       self._wrapCtrl.IsChecked(),
                                       self._radioBox.GetSelection(),
                                       self._replaceCtrl.GetValue()
                                       )


#----------------------------------------------------------------------------
# Menu Bitmaps - generated by encode_bitmaps.py
#----------------------------------------------------------------------------
from wx import ImageFromStream, BitmapFromImage
import cStringIO


def getFindData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x01\xb1IDAT8\x8d\xa5\x93=o\xd3P\x14\x86\x1f\xa7\x11\x95<\xdc\xc6\xecN+5\
[\x86B\x99\xacLQ2Zr[\x89\xa1\xfd\x0b%\x95\x90\x00\xf1\x03\x80\x01\x98\x80\
\x19G\xac\x0cm\xff@Y\xd9:\xd9Ck\x94\xd6\xddb\x94\x9b\x98\xc8\xd2e1C\xe5\x8b\
\xdd\x14\x96\xbe\xdb=\x1f\xefy\xef\xf90\x8c\xda\x12wA\xbd\xfc\x18\xfa\x9fs\
\x80\xf9|\x0e\xc0\x93\xc1\x81\x01\xf0\xe6\xf5\xab\x1c`:\x9d\x02\xf0\xf6\xdd{\
\xa3\xc8\xa9\xddd\xec\xf5z\xb4Z\xeb\x00\x1c\x1f\x1d\xe6\x85\xdd\xf3<\x06\x83\
\xc1\x82\xbd\xa2 \x0cCL\xd3d<\x1e\x13\xc71\xb6m\x030\x1a\x8d\x08\x82\x00\x80\
\xb3\xb3s:\x9d\x8e\xce\xa9(h6\x9b8\x8e\x83m\xdb4\x1a\r\x82 \xe0\xc5\xf3g\xb9\
eY\xb4\xdbm\x1c\xc7Y\xe8\x81&\xf8\xf4\xf1C\xde\xedv+\xce\x97Owx\xfc\xe8k\xc5\
\xb6\xb7\xb7\x8b\xef\x0foW \x84\xe0\xea\xea\x02\xa5\x94n\x18\x80\x94\x92\xd9\
l\x02@\x96e\x95>\xd4nVO\xd3\xb9\x0e\xba\r\xa6i\xd2\xef\xf7\xf0\xfd!\xc7G\x87\
y\xed:)\xd5\x01J\xfd\xd6c\xfc~\x9a\xfc\x93\xe8\xf2\xf2\x02(Ma6\x9b \x84@)\
\xa5\t}\xff\x0b\xd0\'I~R\x14\xca\xb2L\xfb\x97\x97\xef-\xeeA!_J\x89\xeb\xba\
\xb8\xae\xab\xbf\x06\x7f\x97\xacP[\x87\xeb9\x0b!H\x92\ta\x18"\xa5\xd4U\xbd\
\xadm\xe3\xe1\x83\x8d<\x8a~\x90\xa6\xbf\x88\xe3\x18)\xa5&\xa9\x03X\x96E\xab\
\xb5\x8em7\xf5\xc2\x94\xb1\xba\xba\xc6\xe6\xe6\x06++\xf7\x89\xa2\xa8\xe2\xd3\
=89\xf9Va.\x14\x14\xd8\xdf?X VJa\x14\xd7X\xde\xef2\xbc\xadm\xe3\x7f~\xe3\xae\
\xe7\xfc\x07\x84;\xc5\x82\xa1m&\x95\x00\x00\x00\x00IEND\xaeB`\x82' 


def getFindBitmap():
    return BitmapFromImage(getFindImage())


def getFindImage():
    stream = cStringIO.StringIO(getFindData())
    return ImageFromStream(stream)

