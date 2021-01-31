# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.client.playermind import PyDoCommand
from mud.client.gui.tomeGui import TomeGui
receiveGameText = TomeGui.instance.receiveGameText
from mud.world.defines import *
import traceback
from math import sqrt, ceil



TRACKINGWND = None


class TrackingWnd:
    def __init__(self):
        self.trackingBitmap = TGEObject("TRACKING_TRACKBITMAP")
        self.trackingList = TGEObject("TRACKING_TRACKINGLIST")
        self.trackingScroll = TGEObject("TRACKING_SCROLL")
        self.trackingText = TGEObject("TRACKING_TEXT")
        self.trackingButton = TGEObject("TRACKING_TRACKBUTTON")
        self.trackingWindow = TGEObject("TRACKINGWND_WINDOW")
        self.trackingSubWindow = TGEObject("TRACKING_SUBWINDOW")
        self.tracking = {}
        self.trackingId = 0
        self.trackLocation = (0,0,0)
        self.trackInterest = ""
        self.interestLookup = {}
        self.trackingRangeDisplay = True
    
    
    def OnToggleScale(self):
        if self.trackingSubWindow.visible:
            self.trackingSubWindow.visible = False
            self.trackingButton.visible = False
            self.trackingWindow.minExtent = "128 200"
            self.trackingWindow.setExtent(128,220)
            self.trackingText.resize(7,32,114,16)
            self.trackingBitmap.resize(4,80,120,120)
            self.trackingWindow.setExtent(128,200)
            self.trackingWindow.resizeHeight = False
            self.trackingRangeDisplay = False
            self.trackingWindow.setText("Tracking")
        else:
            self.trackingWindow.minExtent = "128 300"
            self.trackingWindow.setExtent(364,316)
            self.trackingSubWindow.resize(9,31,228,269)
            self.trackingText.resize(242,95,114,16)
            self.trackingBitmap.resize(239,160,120,120)
            self.trackingSubWindow.visible = True
            self.trackingButton.visible = True
            self.trackingWindow.resizeHeight = True
            self.trackingRangeDisplay = True
    
    
    def set(self, trackingData=None):
        from mud.client.playermind import PLAYERMIND
        if not PLAYERMIND:
            return
        
        if trackingData:
            self.range = trackingData['RANGE']
            del trackingData['RANGE']
            self.tracking = trackingData
        
        try:
            mw = TGEObject("MapViewPort")
            mw.clearContacts()
            
            # Get points of interest for current zone.
            from playerSettings import PLAYERSETTINGS
            poi = PLAYERSETTINGS.poi
            
            self.interestLookup = {}
            x = -1
            found = False
            for description,location in poi.iteritems():
                if self.trackInterest == description:
                    found = True
                    self.trackLocation = location
                mw.addContact(description,6,location[0],location[1],location[2])
                self.interestLookup[x] = description
                x -= 1
            
            if not found:
                self.trackInterest = ""
            
            if not self.trackInterest and self.trackingId > 0:
                try:
                    self.trackLocation = self.tracking[self.trackingId][1]
                except KeyError:
                    # If we didn't find the actively tracked mob in the trackable
                    #  mob list, notify player and reset tracking target.
                    self.trackingId = 0
                    receiveGameText(RPG_MSG_GAME_EVENT,"The trail has grown cold.\\n")
            
            if not self.trackingId and not self.trackInterest:
                #self.trackingBitmap.setBitmap("") <--- handled in playermind
                self.trackingText.visible = False
            else:
                if self.trackInterest:
                    self.trackingText.setText("<font:Arial Bold:14><just:center><shadow:1:1><shadowcolor:000000>Tracking: %s"%(self.trackInterest))
                else:
                    self.trackingText.setText("<font:Arial Bold:14><just:center><shadow:1:1><shadowcolor:000000>Tracking: %s at %im"%(self.tracking[self.trackingId][0],ceil(self.tracking[self.trackingId][2])))
                
                self.trackingText.visible = True
            
            
            prevSelected = int(self.trackingList.getSelectedId())
            x,y = self.trackingScroll.childRelPos.split(" ")
            
            tc = self.trackingList
            tc.setVisible(False)
            tc.clear()
            
            found = False
            for id,values in self.tracking.iteritems():
                #(m.name,m.simObject.position,r)
                if values[3] != 6:
                    mw.addContact(values[0],values[3],values[1][0],values[1][1],values[1][2])
                
                if id == prevSelected:
                    found = True
                if id == self.trackingId:
                    TGEEval(r'TRACKING_TRACKINGLIST.addRow(%i,"\c2%s" TAB %i @"m");'%(id,values[0],ceil(values[2])))
                else:
                    if values[3]==1:
                        TGEEval(r'TRACKING_TRACKINGLIST.addRow(%i,"\c3%s" TAB %i @"m");'%(id,values[0],ceil(values[2])))
                    else:
                        TGEEval(r'TRACKING_TRACKINGLIST.addRow(%i,"%s" TAB %i @"m");'%(id,values[0],ceil(values[2])))
                        
                
                
            
            tc.sortNumerical(1)
            
            id = -1
            for description,location in poi.iteritems():
                mw.addContact(description,6,location[0],location[1],location[2])
                pos = PLAYERMIND.rootInfo.POSITION
                xDist = pos[0] - location[0]
                yDist = pos[1] - location[1]
                zDist = pos[2] - location[2]
                dist = sqrt(xDist * xDist + yDist * yDist + zDist * zDist)
                TGEEval(r'TRACKING_TRACKINGLIST.addRow(%i,"\c4%s" TAB %i @"m");'%(id,description,ceil(dist)))
                if id == prevSelected:
                    found = True
                id -= 1
            
            if not found:
                row = 0
            else:
                row = tc.getRowNumById(prevSelected)
            
            tc.setSelectedRow(row)
            self.trackingScroll.scrollTo(x,y)
            #tc.scrollVisible(tcell)
            
            tc.setActive(True)
            tc.setVisible(True)
            
            if self.trackingRangeDisplay:
                self.trackingWindow.setText("Tracking - Range %im"%ceil(self.range))
        except:
            traceback.print_exc()



def OnTrack():
    from mud.client.playermind import PLAYERMIND
    if not int(TRACKINGWND.trackingList.rowCount()):
        return
    id = int (TRACKINGWND.trackingList.getSelectedId())
    
    if 0 <= id:
        TRACKINGWND.trackInterest = ""
        TRACKINGWND.trackingId = id
    else:
        #we're tracking a location
        TRACKINGWND.trackInterest = TRACKINGWND.interestLookup[id]
        TRACKINGWND.trackingId = 0
    
    # Update the tracking window with the new tracking target.
    TRACKINGWND.set()


def OnAltClickTrackingList():   
    
    # Return if there are no tracking targets.
    if not int(TRACKINGWND.trackingList.rowCount()):
        return
    
    # Get the id of the item selected.
    id = int (TRACKINGWND.trackingList.getSelectedId())
    
    # Only attempt to set target if a mob's name was
    # selected.  A negative value indicates a point
    # of interest.
    if 0 <= id:        
        # True indicates cycling.  This allows for 
        # cycling through a targets party members
        # if a player is clicked on multiple times.
        #
        # Note: This should probably change to a remote
        #       call to  player avatar.
        PyDoCommand(("PyDoCommand","/TARGETID %i 1 %s"%(id, TRACKINGWND.tracking[id][0])))



#"Py::OnTrack();";
def PyExec():
    global TRACKINGWND
    TRACKINGWND = TrackingWnd()
    TGEExport(OnTrack,"Py","OnTrack","desc",1,1)
    TGEExport(OnAltClickTrackingList,"Py","OnAltClickTrackingList","desc",1,1)
    TGEExport(TRACKINGWND.OnToggleScale,"Py","OnToggleTrackingScale","desc",1,1)

