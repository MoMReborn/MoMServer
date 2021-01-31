# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.shared.playdata import IsTacticalDirty

TACTICALGUI = None
class TacticalGui:
    def __init__(self):
        self.enemiesList = TGEObject("tactical_enemies_list")
        self.threatsList = TGEObject("tactical_threats_list")
        self.alliesList =  TGEObject("tactical_allies_list")
        self.charInfo = None
        
        
        
    def tick(self, cinfo,rootInfo):
        return
        if not IsTacticalDirty() and cinfo == self.charInfo:
            return
            
        self.charInfo = cinfo
                    
        tinfo = rootInfo.TACTICAL
        
        self.enemiesList.setVisible(False)
        self.threatsList.setVisible(False)
        self.alliesList.setVisible(False)
                
        self.enemiesList.clear()
        self.threatsList.clear()
        self.alliesList.clear()
        
        #enemies
        i = 0
        for enemy in tinfo.ENEMIES:
            self.enemiesList.addRow(i,"%s %im"%(enemy[0],enemy[2])) #name and range
            i+=1
            
        #tc.sort(1) # this sorts alphabetically
        self.enemiesList.setSelectedRow(0)
        self.enemiesList.scrollVisible(0)
        self.enemiesList.setActive(True)
        self.enemiesList.setVisible(True)
        
        #THREATS
        i = 0
        for threat in tinfo.THREATS:
            if threat[0]==cinfo.SPAWNID:
                self.threatsList.addRow(i,"%s %im"%(threat[1],threat[3])) #name and range
                i+=1
        
        self.threatsList.setSelectedRow(0)
        self.threatsList.scrollVisible(0)
        self.threatsList.setActive(True)
        self.threatsList.setVisible(True)
        
        
            
        
def OnEnemiesList():
    print "Enemies List"
            
def OnThreatsList():
    print "Threats List"
        

def PyExec():
    global TACTICALGUI
    TACTICALGUI = TacticalGui()
    TGEExport(OnEnemiesList,"Py","OnEnemiesList","desc",1,1)
    TGEExport(OnThreatsList,"Py","OnThreatsList","desc",1,1)
