# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

"""
OpenSRD

Copyright (C) 2004 Prairie Games, Inc

This program is free software under the terms of the BSD License
http://www.opensource.org/licenses/bsd-license.php
"""

#this is the notebook at the bottom of the screen with some neat stuff

import wx
import wx.py as py


class MyLog(wx.PyLog):
    def __init__(self, textCtrl, logTime=0):
        wx.PyLog.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime
        
        return
        
        #redirect stdout
        import sys
        sys.oldstdout = sys.stdout
        sys.oldstderr = sys.stderr
        class mywriter:
            def write(self, text):
                wx.LogMessage(text) #strip \n
                sys.oldstdout.write(text)
                sys.oldstdout.flush()
            def __del__(self):
                sys.stdout = sys.oldstdout
                sys.stderr = sys.oldstderr
        sys.stdout = mywriter()
        sys.stderr = mywriter()

    def DoLogString(self, message, timeStamp):
        if self.logTime:
            message = time.strftime("%X", time.localtime(timeStamp)) + \
                      ": " + message
        if self.tc:
            
            x= len(self.tc.GetValue())
            if x>8192:
                self.tc.Remove(0,4096)
            
            self.tc.AppendText(message)

class UtilityNotebook(wx.Notebook):
    def __init__(self,parent,id=-1):
        wx.Notebook.__init__(self,parent,id,style = wx.NB_TOP)
        
        
        # Set up a log on the View Log Notebook page
        self.log = wx.TextCtrl(self, -1,
                              style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        wx.Log_SetActiveTarget(MyLog(self.log))
        
        self.AddPage(self.log,"Log") 
        
        self.shell = py.shell.Shell(self, -1, introText="MoM Shell")
        
        self.AddPage(self.shell,"Shell") 
        
        #wx.LogMessage('window handle: %s' % self.GetHandle())
        
        #add a shell
        
