# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-
# generated by wxGlade 0.3.5.1 on Sat Jan 22 13:54:55 2005

import wx

class WorldConfigPanel(wx.Panel):
    def __init__(self, *args, **kwds):
        # begin wxGlade: WorldConfigPanel.__init__
        kwds["style"] = wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, *args, **kwds)
        self.sizer_1_staticbox = wx.StaticBox(self, -1, "World Configuration")
        self.label_1_copy = wx.StaticText(self, -1, "World Port")
        self.worldPortTextCtrl = wx.TextCtrl(self, -1, "")
        self.label_7_copy = wx.StaticText(self, -1, "Zone Start Port")
        self.zonePortTextCtrl = wx.TextCtrl(self, -1, "")
        self.label_2_copy = wx.StaticText(self, -1, "Player Password")
        self.playerPasswordTextCtrl = wx.TextCtrl(self, -1, "")
        self.label_3_copy = wx.StaticText(self, -1, "Zone Password")
        self.zonePasswordTextCtrl = wx.TextCtrl(self, -1, "")
        self.label_4_copy = wx.StaticText(self, -1, "Max Live Players")
        self.maxLivePlayersTextCtrl = wx.TextCtrl(self, -1, "")
        self.label_5_copy = wx.StaticText(self, -1, "Max Live Zones")
        self.maxLiveZonesTextCtrl = wx.TextCtrl(self, -1, "")
        self.label_6_copy = wx.StaticText(self, -1, "Allow Guests")
        self.allowGuestsCheckBox = wx.CheckBox(self, -1, "")
        self.label_8_copy = wx.StaticText(self, -1, "Message of the Day")
        self.motdTextCtrl = wx.TextCtrl(self, -1, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: WorldConfigPanel.__set_properties
        pass
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: WorldConfigPanel.__do_layout
        sizer_1 = wx.StaticBoxSizer(self.sizer_1_staticbox, wx.HORIZONTAL)
        grid_sizer_1_copy = wx.FlexGridSizer(6, 2, 4, 2)
        grid_sizer_1_copy.Add(self.label_1_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.worldPortTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_7_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.zonePortTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_2_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.playerPasswordTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_3_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.zonePasswordTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_4_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.maxLivePlayersTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_5_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.maxLiveZonesTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_6_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.allowGuestsCheckBox, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.label_8_copy, 0, wx.ALIGN_CENTER_VERTICAL|wx.FIXED_MINSIZE, 0)
        grid_sizer_1_copy.Add(self.motdTextCtrl, 0, wx.FIXED_MINSIZE, 0)
        sizer_1.Add(grid_sizer_1_copy, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        # end wxGlade

# end of class WorldConfigPanel


