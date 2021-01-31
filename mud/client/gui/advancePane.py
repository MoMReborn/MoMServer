# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from mud.world.shared.playdata import AdvancementsDirty
from mud.client.playermind import GetMoMClientDBConnection
import traceback


ADVANCEPANE = None


class AdvancePane:
    
    def __init__(self):
        global ADVANCEPANE
        ADVANCEPANE = self
        self.advancePointsText = TGEObject("ADVANCEPANE_ADVANCEPOINTS")
        self.descText = TGEObject("ADVANCEPANE_DESCTEXT")
        self.currentDescText = TGEObject("ADVANCEPANE_CURRENTDESCTEXT")
        self.currentScroll = TGEObject("AdvanceCurrentScroll")
        self.currentTextList = TGEObject("AdvanceCurrentTextList")
        self.availableScroll = TGEObject("AdvanceAvailableScroll")
        self.availableTextList = TGEObject("AdvanceAvailableTextList")
        self.chooseButton = TGEObject("ADVANCEPANE_CHOOSEBUTTON")
        
        self.cinfo = None
        self.currentChoices = []
        self.availableChoices = []
        
        self.advancementCollection = []
        con = GetMoMClientDBConnection()
        for selection in con.execute("SELECT id,name,level,desc,cost,max_rank FROM advancement_proto ORDER BY name;"):
            myid = selection[0]
            exclusions = tuple(item[0] for item in con.execute("SELECT DISTINCT exclude FROM advancement_exclusion WHERE advancement_proto_id = ?;",(myid,)))
            if len(exclusions) > 1:
                exclusionsRedux = tuple(item[0] for item in con.execute("SELECT DISTINCT exclude FROM advancement_exclusion WHERE advancement_proto_id = ? AND exclude NOT IN (SELECT DISTINCT exclude FROM advancement_exclusion WHERE advancement_proto_id IN (SELECT id FROM advancement_proto WHERE name IN (SELECT exclude FROM advancement_exclusion WHERE advancement_proto_id = ?)));",(myid,myid)))
            else:
                exclusionsRedux = exclusions
            
            classReqs = con.execute("SELECT classname,level FROM advancement_class WHERE advancement_proto_id = ?;",(myid,)).fetchall()
            raceReqs = con.execute("SELECT racename,level FROM advancement_race WHERE advancement_proto_id = ?;",(myid,)).fetchall()
            advanceReqs = con.execute("SELECT require,rank FROM advancement_requirement WHERE advancement_proto_id = ?;",(myid,)).fetchall()
            
            self.advancementCollection.append( \
                (selection,(exclusions,exclusionsRedux,classReqs,raceReqs,advanceReqs)))
    
    
    def onAvailableChoice(self):
        
        self.descText.setText("")
        index = int(self.availableTextList.getSelectedId())
        if index >= len(self.availableChoices):
            return
        a = self.availableChoices[index]
        text = a[3]
        if len(a[4]):
            text += "\\n\\nExcludes: %s"%', '.join(a[4])
        
        TGEEval('ADVANCEPANE_DESCTEXT.setText("%s");'%text)

    def onCurrentChoice(self):
        
        self.descText.setText("")
        index = int(self.currentTextList.getSelectedId())
        if index >= len(self.currentChoices):
            return
        a = self.currentChoices[index]
        
        text = a[3]
        if len(a[4]):
            text += "\\n\\nExcludes: %s"%', '.join(a[4])
        
        TGEEval('ADVANCEPANE_CURRENTDESCTEXT.setText("%s");'%text)
        
        
    
    
    def setFromCharacterInfo(self,cinfo):
        newCharData = False
        if self.cinfo != cinfo:    # on first run, or when switching characters
            newCharData = True
            self.cinfo = cinfo
        
        self.advancePointsText.setText("Points: %i"%int(cinfo.ADVANCE))
        
        try:    # duality check
            if not AdvancementsDirty() and not newCharData:
                return
            
            index = int(self.availableTextList.getSelectedId())
            aprev = ""
            if len(self.availableChoices) > index >= 0:
                aprev = self.availableTextList.getRowText(index)
            atc = self.availableTextList
            atc.setVisible(False)
            atc.clear()
            self.availableChoices = []
            aprevindex = 0
            index = int(self.currentTextList.getSelectedId())
            cprev = ""
            if len(self.currentChoices) > index >= 0:
                cprev = self.currentTextList.getRowText(index)
            ctc = self.currentTextList
            ctc.setVisible(False)
            ctc.clear()
            self.currentChoices = []
            cprevindex = 0
            
            cinfo.ADVANCEMENTS.sort(key=lambda x:x[0])
            currentNames = [cur[0] for cur in cinfo.ADVANCEMENTS]
            currentExclusions = []
            con = GetMoMClientDBConnection()
            
            #fill it up
            ci = 0
            for selection,values in self.advancementCollection:
                myid,name,level,desc,cost,maxRank = selection
                exclusions,exclusionsRedux,classReqs,raceReqs,advanceReqs = values
                
                try:
                    rank = cinfo.ADVANCEMENTS[currentNames.index(name)][1]
                    TGEEval(r'AdvanceCurrentTextList.addRow(%i,"%s" TAB "%s");'% \
                        (ci,name,"(%i/%i)"%(rank,maxRank)))
                    self.currentChoices.append((name,rank,maxRank,desc,exclusionsRedux))
                    currentExclusions.extend(exclusions)
                    
                    if name in cprev:
                        cprevindex = ci
                    ci += 1
                    
                    if rank >= maxRank:
                        continue
                except ValueError:
                    pass
                
                if cost > cinfo.ADVANCE or level > cinfo.PLEVEL:
                    continue
                
                if len(classReqs):
                    for classname,level in classReqs:
                        if (classname == cinfo.PCLASS and level <= cinfo.PLEVEL) or (classname == cinfo.SCLASS and level <= cinfo.SLEVEL) or (classname == cinfo.TCLASS and level <= cinfo.TLEVEL):
                            break
                    else:
                        continue
                
                if len(raceReqs):
                    for racename,level in raceReqs:
                        if racename == cinfo.RACE and level <= cinfo.PLEVEL:
                            break
                    else:
                        continue
                
                passed = True
                if len(advanceReqs):
                    for require,rank in advanceReqs:
                        if require not in currentNames or rank > cinfo.ADVANCEMENTS[currentNames.index(require)][1]:
                            passed = False
                            break
                
                if passed:
                    self.availableChoices.append( \
                        (name,cost,maxRank,desc,exclusionsRedux))
            
            ai = 0
            offset = 0
            for i in xrange(len(self.availableChoices)):
                choice = self.availableChoices[i - offset]
                name = choice[0]
                if name in currentExclusions:
                    del self.availableChoices[i - offset]
                    offset += 1
                    continue
                
                TGEEval(r'AdvanceAvailableTextList.addRow(%i,"%s" TAB "%s");'%(ai,name,"(%i/%i)"%(choice[1],choice[2])))
                if name in aprev:
                    aprevindex = ai
                ai += 1
            
            atc.setSelectedRow(aprevindex)
            atc.scrollVisible(aprevindex)
            atc.setActive(True)
            atc.setVisible(True)
            ctc.setSelectedRow(cprevindex)
            ctc.scrollVisible(cprevindex)
            ctc.setActive(True)
            ctc.setVisible(True)
        
            if not len(self.availableChoices):
                self.chooseButton.visible = False
            else:
                self.chooseButton.visible = True
        
        except:
            traceback.print_exc()



def PyOnAdvanceAvailableChoose():
    ADVANCEPANE.onAvailableChoice()
    
def PyOnAdvanceCurrentChoose():
    ADVANCEPANE.onCurrentChoice()


def PyOnReallyAdvanceChoose(args):
    from partyWnd import PARTYWND
    PARTYWND.mind.chooseAdvancement(ADVANCEPANE.cinfo.NAME,args[1])



def PyOnAdvanceChoose():
    
    index = int(ADVANCEPANE.availableTextList.getSelectedId())
    if index >= len(ADVANCEPANE.availableChoices):
        return
    a = ADVANCEPANE.availableChoices[index]

    TGEEval('MessageBoxYesNo("Advance?", "Do you really want to advance %s?","Py::ReallyAdvanceChoose(\\"%s\\");");'%(a[0],a[0]))
    
TGEExport(PyOnAdvanceChoose,"Py","AdvanceChoose","desc",1,1)
TGEExport(PyOnReallyAdvanceChoose,"Py","ReallyAdvanceChoose","desc",2,2)
TGEExport(PyOnAdvanceAvailableChoose,"Py","OnAdvanceAvailableChoose","desc",1,1)
TGEExport(PyOnAdvanceCurrentChoose,"Py","OnAdvanceCurrentChoose","desc",1,1)

    
 
