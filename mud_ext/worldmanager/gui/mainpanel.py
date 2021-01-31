# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import wx

class MainPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.connectionBox = wx.StaticBox(self, -1, "Connection")
        self.liveWorldsBox = wx.StaticBox(self, -1, "Live Worlds")
        self.myWorldsBox = wx.StaticBox(self, -1, "My Worlds")
        self.logButton = wx.Button(self, -1, "Connect!")
        self.liveWorldsListCtrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.refreshWorldsBtn = wx.Button(self, -1, "Query Live Worlds")
        self.coServeBtn = wx.Button(self, -1, "Co-Serve World")
        self.myWorldsListCtrl = wx.ListCtrl(self, -1, style=wx.LC_REPORT|wx.LC_SINGLE_SEL|wx.SUNKEN_BORDER)
        self.launchWorldBtn = wx.Button(self, -1, "Launch World")
        self.newWorldBtn = wx.Button(self, -1, "New World")
        self.deleteWorldBtn = wx.Button(self, -1, "Delete World")

        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.logButton.SetSize((300, 32))
        self.liveWorldsListCtrl.SetSize((300,160))
        self.myWorldsListCtrl.SetSize((300,120))

    def __do_layout(self):
        mastersizer = wx.BoxSizer(wx.VERTICAL)
        mastergrid = wx.FlexGridSizer(3, 1, 8, 8)
        
        connectionBoxSizer = wx.StaticBoxSizer(self.connectionBox, wx.HORIZONTAL)
        connectionBoxSizer.Add(self.logButton, 0, wx.FIXED_MINSIZE, 0)
        mastergrid.Add(connectionBoxSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        liveWorldsBoxSizer = wx.StaticBoxSizer(self.liveWorldsBox, wx.VERTICAL)
        liveWorldsGridSizer = wx.FlexGridSizer(2, 1, 8, 8)
        liveWorldsGridSizer.Add(self.liveWorldsListCtrl, 1, wx.FIXED_MINSIZE, 0)
        liveWorldsButtonSizer = wx.FlexGridSizer(1, 2, 8, 8)
        liveWorldsButtonSizer.Add(self.refreshWorldsBtn, 0, wx.FIXED_MINSIZE, 0)
        liveWorldsButtonSizer.Add(self.coServeBtn, 0, wx.FIXED_MINSIZE, 0)
        liveWorldsGridSizer.Add(liveWorldsButtonSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        liveWorldsBoxSizer.Add(liveWorldsGridSizer, 1, 0, 0)
        mastergrid.Add(liveWorldsBoxSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        myWorldsBoxSizer = wx.StaticBoxSizer(self.myWorldsBox, wx.HORIZONTAL)
        grid_sizer_4_copy = wx.FlexGridSizer(2, 1, 8, 8)
        grid_sizer_4_copy.Add(self.myWorldsListCtrl, 1, wx.FIXED_MINSIZE, 0)
        sizer_12_copy = wx.BoxSizer(wx.HORIZONTAL)
        sizer_12_copy.Add(self.launchWorldBtn, 0, wx.FIXED_MINSIZE, 0)
        sizer_12_copy.Add(self.newWorldBtn, 0, wx.FIXED_MINSIZE, 0)
        sizer_12_copy.Add(self.deleteWorldBtn, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_4_copy.Add(sizer_12_copy, 1, 0, 0)
        myWorldsBoxSizer.Add(grid_sizer_4_copy, 1, wx.EXPAND, 0)
        mastergrid.Add(myWorldsBoxSizer, 1, wx.ALIGN_CENTER_HORIZONTAL, 0)
        
        mastersizer.Add(mastergrid, 1, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER, 8)
        self.SetAutoLayout(True)
        self.SetSizer(mastersizer)
        mastersizer.Fit(self)
        mastersizer.SetSizeHints(self)

# end of class MainPanel


