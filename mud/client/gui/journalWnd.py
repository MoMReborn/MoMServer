# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from mud.gamesettings import *
from math import floor
from tomeGui import TomeGui



def CreateDefaultJournal(realm):
    journal = {}
    
    defaultTopic = journal["Welcome"] = [{}, False]
    defaultTopic = defaultTopic[0]
    
    defaultTopic["A little help please!!!!"] = ["""<color:BBBBFF>Click on the 'Help' button on your Tome window.""", False]
    
    return journal



JOURNALWND = None

class JournalWnd:
    def __init__(self):
        self.journalScroll = TGEObject("JOURNAL_SCROLL")
        self.journalText = TGEObject("JOURNAL_TEXT")
        
        self.topicScroll = TGEObject("JOURNAL_TOPICSCROLL")
        self.topicTextList = TGEObject("JOURNAL_TOPICTEXTLIST")
        
        self.entryScroll = TGEObject("JOURNAL_ENTRYSCROLL")
        self.entryTextList = TGEObject("JOURNAL_ENTRYTEXTLIST")
        
        self.hideTopic = TGEObject("JOURNAL_HIDETOPIC")
        self.hideEntry = TGEObject("JOURNAL_HIDEENTRY")
        
        self.showHidden = TGEObject("JOURNAL_SHOWHIDDEN")
        self.showHidden.setValue(0)
        
        self.newEntryTopic = TGEObject("JournalNewEntry_Topic")
        self.newEntryEntry = TGEObject("JournalNewEntry_Entry")
        self.newEntryText = TGEObject("JournalNewEntry_Text")
        
        self.journal = None
    
    
    def setJournal(self,journal,force=False):
        if force or self.journal != journal:
            self.journal = journal
            
            eTL = self.entryTextList
            eTL.setVisible(False)
            eTL.clear()
            eTL.setVisible(True)
            
            tTL = self.topicTextList
            tTL.setVisible(False)
            tTL.clear()
            
            topicIndex = 0
            for topic,topicData in sorted(journal.iteritems()):
                if int(self.showHidden.getValue()) or not topicData[1]:
                    tTL.addRow(topicIndex,topic)
                    topicIndex += 1
            
            topic = tTL.getRowText(0)
            self.setSelection(topic)
            tTL.setActive(True)
            tTL.setVisible(True)
            
            if topicIndex == 0:
                TGEEval('JOURNAL_TEXT.setText("");')
                eTL.clear()
    
    
    def setSelection(self,topic,entry=None):
        tTL = self.topicTextList
        eTL = self.entryTextList
        
        # See if topic is valid.
        if topic:
            for x in xrange(0,int(tTL.rowCount())):
                if tTL.getRowText(x) == topic:
                    tTL.setSelectedRow(x)
                    tTL.scrollVisible(x)
                    # Update hide topic button text.
                    if self.journal[topic][1]:
                        self.hideTopic.setText("Show Topic")
                    else:
                        self.hideTopic.setText("Hide Topic")
                    # See if entry is valid.
                    if entry:
                        for x in xrange(0,int(eTL.rowCount())):
                            if eTL.getRowText(x) == entry:
                                eTL.setSelectedRow(x)
                                eTL.scrollVisible(x)
                                # Update hide entry button text.
                                if self.journal[topic][0][entry][1]:
                                    self.hideEntry.setText("Show Entry")
                                else:
                                    self.hideEntry.setText("Hide Entry")
                                break
                    break
    
    
    def addEntry(self,topic,entry,text,custom=False):
        from npcWnd import NPCWND
        from playerSettings import PLAYERSETTINGS
        
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        ptopic = tTL.getRowTextById(sr)
        
        eTL = self.entryTextList
        sr = int(eTL.getSelectedId())
        pentry = eTL.getRowTextById(sr)
        
        if NPCWND.title and not custom:
            text = "<color:FFFFFF>%s: <color:BBBBFF>%s"%(NPCWND.title,text)
        else:
            text = "<color:BBBBFF>%s"%text
        
        needsUpdate,journal = PLAYERSETTINGS.addJournalEntry(topic,entry,text)
        
        if needsUpdate:
            self.setJournal(journal,True)
            
            TomeGui.instance.receiveGameText(RPG_MSG_GAME_GAINED,r'Your journal\'s \"%s\" topic has been updated with a \"%s\" entry!\n'%(topic,entry))
            eval = 'alxPlay(alxCreateSource(AudioMessage, "%s/data/sound/sfx/Pencil_WriteOnPaper2.ogg"));'%GAMEROOT
            TGEEval(eval)
            
            # Reset to previous selection.
            self.setSelection(ptopic,pentry)
    
    
    def OnJournalTopic(self):
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        # Update hide topic button text.
        if self.journal[topic][1]:
            self.hideTopic.setText("Show Topic")
        else:
            self.hideTopic.setText("Hide Topic")
        
        # Setup entry list.
        eTL = self.entryTextList
        eTL.setVisible(False)
        eTL.clear()
        
        entryIndex = 0
        for entry,entryData in sorted(self.journal[topic][0].iteritems()):
            if int(self.showHidden.getValue()) or not entryData[1]:
                eTL.addRow(entryIndex,entry)
                entryIndex += 1
        
        eTL.setSelectedRow(0)
        eTL.scrollVisible(0)
        eTL.setActive(True)
        eTL.setVisible(True)
        
        # Update hide entry button text.
        entry = eTL.getRowTextById(0)
        if self.journal[topic][0][entry][1]:
            self.hideEntry.setText("Show Entry")
        else:
            self.hideEntry.setText("Hide Entry")
        
        if entryIndex == 0:
            TGEEval('JOURNAL_TEXT.setText("");')
            eTL.clear()
    
    
    def OnJournalEntry(self):
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        # Get chosen entry.
        eTL = self.entryTextList
        sr = int(eTL.getSelectedId())
        entry = eTL.getRowTextById(sr)
        
        # Update hide entry button text.
        if self.journal[topic][0][entry][1]:
            self.hideEntry.setText("Show Entry")
        else:
            self.hideEntry.setText("Hide Entry")
        
        try:
            fontsize = int(floor(float(TGEGetGlobal("$pref::Game::ChatFontSize"))))
            fontsize += 3
        except:
            fontsize = 13
        
        if fontsize < 13:
            fontsize = 13
        if fontsize > 23:
            fontsize = 23
        
        if not self.journal.get(topic) or not self.journal[topic][0].get(entry):
            eval = 'JOURNAL_TEXT.setText("");'
        else:
            eval = 'JOURNAL_TEXT.setText("<font:Arial:%i><shadowcolor:000000><shadow:1:1>%s");'%(fontsize,self.journal[topic][0][entry][0])
            eval = eval.replace("\n","")
        TGEEval(eval)
    
    
    def OnJournalHideTopic(self):
        from playerSettings import PLAYERSETTINGS
        
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        needsUpdate,journal = PLAYERSETTINGS.hideJournalTopic(topic,not self.journal[topic][1])
        if needsUpdate:
            self.setJournal(journal,True)
            # If hidden topics are shown, try to restore selection.
            self.setSelection(topic)
    
    
    def OnJournalHideEntry(self):
        from playerSettings import PLAYERSETTINGS
        
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        # Get chosen entry.
        eTL = self.entryTextList
        sr = int(eTL.getSelectedId())
        entry = eTL.getRowTextById(sr)
        
        needsUpdate,journal = PLAYERSETTINGS.hideJournalEntry(topic,entry,not self.journal[topic][0][entry][1])
        if needsUpdate:
            self.setJournal(journal,True)
            
            # Reset selection to previously selected topic if possible.
            # Entry can be restored as well if we show hidden entries.
            self.setSelection(topic,entry)
    
    
    def OnJournalReallyClearTopic(self):
        from playerSettings import PLAYERSETTINGS
        
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        needsUpdate,journal = PLAYERSETTINGS.clearJournalTopic(topic)
        if needsUpdate:
            self.setJournal(journal,True)
    
    
    def OnJournalReallyClearEntry(self):
        from playerSettings import PLAYERSETTINGS
        
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        # Get chosen entry.
        eTL = self.entryTextList
        sr = int(eTL.getSelectedId())
        entry = eTL.getRowTextById(sr)
        
        needsUpdate,journal = PLAYERSETTINGS.clearJournalEntry(topic,entry)
        if needsUpdate:
            self.setJournal(journal,True)
            
            # Reset selection to previously selected topic if possible.
            self.setSelection(topic)
    
    
    def OnJournalShowHidden(self):
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        # Get chosen entry.
        eTL = self.entryTextList
        sr = int(eTL.getSelectedId())
        entry = eTL.getRowTextById(sr)
        
        # Redisplay journal.
        self.setJournal(self.journal,True)
        
        # Restore topic and entry selection.
        self.setSelection(topic,entry)
    
    
    def OnJournalApplyEntry(self):
        # Get journal entry values.
        topic = self.newEntryTopic.getValue()
        entry = self.newEntryEntry.getValue()
        text = self.newEntryText.getValue()
        
        # Need to reformat those newlines.
        text = text.replace('\\r','\n')
        text = text.replace('\r','\n')
        text = text.replace('\\n','\n')
        text = text.replace('\n','\\n')
        
        # Add entry to current journal or update.
        self.addEntry(topic,entry,text,True)
        
        # Set selection to new or edited entry.
        self.setSelection(topic,entry)
    
    
    def OnJournalEditEntry(self):
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        # Get chosen entry.
        eTL = self.entryTextList
        sr = int(eTL.getSelectedId())
        entry = eTL.getRowTextById(sr)
        
        # Set text values in entry editor.
        self.newEntryTopic.setText(topic)
        self.newEntryEntry.setText(entry)
        self.newEntryText.setText(self.journal[topic][0][entry][0].replace('\\n','\n'))
    
    
    def OnJournalClearTopic(self):
        # Get chosen topic.
        tTL = self.topicTextList
        sr = int(tTL.getSelectedId())
        topic = tTL.getRowTextById(sr)
        
        TGEEval('MessageBoxYesNo("Delete Journal Topic?", "Do you really want to completely delete topic %s?","Py::OnJournalReallyClearTopic();");'%topic)
    
    
    def OnJournalClearEntry(self):
        # Get chosen entry.
        eTL = self.entryTextList
        sr = int(eTL.getSelectedId())
        entry = eTL.getRowTextById(sr)
        
        TGEEval('MessageBoxYesNo("Delete Journal Entry?", "Do you really want to completely delete entry %s?","Py::OnJournalReallyClearEntry();");'%entry)



def PyExec():
    global JOURNALWND
    JOURNALWND = JournalWnd()
    
    TGEExport(JOURNALWND.OnJournalTopic,"Py","OnJournalTopic","desc",1,1)
    TGEExport(JOURNALWND.OnJournalEntry,"Py","OnJournalEntry","desc",1,1)
    TGEExport(JOURNALWND.OnJournalHideTopic,"Py","OnJournalHideTopic","desc",1,1)
    TGEExport(JOURNALWND.OnJournalHideEntry,"Py","OnJournalHideEntry","desc",1,1)
    TGEExport(JOURNALWND.OnJournalReallyClearTopic,"Py","OnJournalReallyClearTopic","desc",1,1)
    TGEExport(JOURNALWND.OnJournalReallyClearEntry,"Py","OnJournalReallyClearEntry","desc",1,1)
    TGEExport(JOURNALWND.OnJournalClearTopic,"Py","OnJournalClearTopic","desc",1,1)
    TGEExport(JOURNALWND.OnJournalClearEntry,"Py","OnJournalClearEntry","desc",1,1)
    TGEExport(JOURNALWND.OnJournalShowHidden,"Py","OnJournalShowHidden","desc",1,1)
    TGEExport(JOURNALWND.OnJournalApplyEntry,"Py","OnJournalApplyEntry","desc",1,1)
    TGEExport(JOURNALWND.OnJournalEditEntry,"Py","OnJournalEditEntry","desc",1,1)

