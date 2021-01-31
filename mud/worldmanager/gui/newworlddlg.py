# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Sat Jan 22 14:00:25 2005

import wx
from mud.world.shared.worldconfigpanel import WorldConfigPanel

class NewWorldDlg(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: NewWorldDlg.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.sizer_1_staticbox = wx.StaticBox(self, -1, "")
        self.label_2 = wx.StaticText(self, -1, "World Name")
        self.worldNameTextCtrl = wx.TextCtrl(self, -1, "")
        self.worldConfigPanel = WorldConfigPanel(self, -1)
        self.button_1 = wx.Button(self, wx.ID_OK, "OK")
        self.button_2 = wx.Button(self, wx.ID_CANCEL, "Cancel")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: NewWorldDlg.__set_properties
        self.SetTitle("New World")
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: NewWorldDlg.__do_layout
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(3, 1, 4, 4)
        sizer_3 = wx.FlexGridSizer(1, 2, 8, 16)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.label_2, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        sizer_2.Add(self.worldNameTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1.Add(sizer_2, 1, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_1.Add(self.worldConfigPanel, 1, wx.EXPAND, 0)
        sizer_3.Add(self.button_1, 0, wx.FIXED_MINSIZE, 0)
        sizer_3.Add(self.button_2, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1.Add(sizer_3, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_1.Add(grid_sizer_1, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()
        # end wxGlade

# end of class NewWorldDlg


