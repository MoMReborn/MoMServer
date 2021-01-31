# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.gamesettings import *
from mud.worlddocs.utils import GetTWikiName
from tomeGui import TomeGui
TomeGui = TomeGui.instance
import tarfile
import traceback

import re

# Checks for html links, metainfo, quicklinks and tags
PURGE_PARSER = re.compile(r'(<a +[\s\S]*?</a>+\s+)|(%META:TOPICINFO+[\s\S]*?%+\s+)|(\*Quick Links:+.*\s+)|(#[a-zA-Z]*\s+)')

LINK_PARSER = re.compile(r'\[\[(.*?)\]\[(.*?)\]\]')

HEADER1_PARSER = re.compile(r'(---\+)+(.*)')
HEADER2_PARSER = re.compile(r'(---\+\+)+(.*)')
HEADER3_PARSER = re.compile(r'(---\+\+\+)+(.*)')
HEADER4_PARSER = re.compile(r'(---\+\+\+\+)+(.*)')
HEADER5_PARSER = re.compile(r'(---\+\+\+\+\+)+(.*)')

BOLD_PARSER = re.compile(r'\*+(.*?)\*+')


ENCYC = {}

HEADER = """<color:2DCBC9><linkcolor:AAAA00><shadowcolor:000000><shadow:1:1><just:center><lmargin%%:2><rmargin%%:98><font:Arial Bold:20>Encyclopedia
<font:Arial:14><just:right><a:chatlink%s>Add to Chat</a>\n<just:left>"""

HOME = """
<a:ZoneIndex>Zones</a>
<a:SpawnIndex>Spawns (NPCs)</a>
<a:SpawnIndexByLevel>Spawns by Level</a>
<a:FactionIndex>Factions</a>
<a:ItemIndex>Items</a>
<a:ItemSetIndex>Item Sets</a>
<a:QuestIndex>Quests</a>
<a:SpellIndex>Spells</a>
<a:SkillIndex>Skills</a>
<a:ClassIndex>Classes</a>
<a:RecipeIndex>Recipes</a><br>
<a:EnchantingDisenchantingIndex>Enchanting / Disenchanting</a>
"""

PAGECACHE = {}

ENCWND = None



class EncWindow:
    def __init__(self):
        self.encText = TGEObject("ENCYC_TEXT")
        self.encScroll = TGEObject("ENCYC_SCROLL")
        self.history = []
        self.positions = {}
        self.curIndex = -1
    
    
    def setPage(self,mypage,append = True):
        try:
            page = ENCYC[mypage]
        except:
            return False
        
        try:
            text = PAGECACHE[mypage]
        except KeyError:
            text = ""
        
        pos = self.encScroll.childRelPos.split(" ")
        self.positions[self.curIndex] = (pos[0],pos[1])
        
        if append:
            if self.curIndex >= 0:
                self.history = self.history[:self.curIndex+1]
                self.history.append(mypage)
                self.curIndex = len(self.history) - 1
            else:
                self.history.append(mypage)
                self.curIndex += 1
        
        if not text:
            text = HEADER%mypage + page
            
            # Strip out html links, metainfo, quick links and tags
            text = PURGE_PARSER.sub('',text)
            
            # Reformat bold font
            text = BOLD_PARSER.sub(r'<font:Arial Bold:14>\1<font:Arial:14>',text)
            
            # HEADERS
            text = HEADER5_PARSER.sub(r'<font:Arial Bold:15><color:2DCBC9><just:center>\2<font:Arial:14><just:left><color:D5E70A>',text)
            text = HEADER4_PARSER.sub(r'<font:Arial Bold:16><color:2DCBC9><just:center>\2<font:Arial:14><just:left><color:D5E70A>',text)
            text = HEADER3_PARSER.sub(r'<font:Arial Bold:17><color:2DCBC9><just:center>\2<font:Arial:14><just:left><color:D5E70A>',text)
            text = HEADER2_PARSER.sub(r'<font:Arial Bold:18><color:2DCBC9><just:center>\2<font:Arial:14><just:left><color:D5E70A>',text)
            text = HEADER1_PARSER.sub(r'<font:Arial Bold:20><color:2DCBC9><just:center>\2<font:Arial:14><just:left><color:D5E70A>',text)
            
            # Text coloring
            text = text.replace(r'%GREEN%',"<color:00FF00>")
            text = text.replace(r'%BLUE%',"<color:3030FF>")
            text = text.replace(r'%RED%',"<color:FF0000>")
            text = text.replace(r'%YELLOW%',"<color:FFC000>")
            text = text.replace(r'%ENDCOLOR%',"<color:D5E70A>")
            
            text = text.replace('\r',"\\r")
            text = text.replace('\n',"\\n")  # valid quote
            text = text.replace('\a',"\\a")  # valid quote
            text = text.replace('"','\\"')  # invalid quote
            
            text = LINK_PARSER.sub(r'<a:\1>\2</a>',text)
        
        TGEEval(r'ENCYC_TEXT.setText("");')
        
        # get around some tge poop
        x = 0
        while x < len(text):
            add = 1024
            t = text[x:x+add]
            if t[len(t)-1] == '\\':
                add += 1
                t = text[x:x+add]
            
            TGEEval(r'ENCYC_TEXT.addText("%s",false);'%t)
            x += add
        
        PAGECACHE[mypage] = text
        
        # reformat
        TGEEval(r'ENCYC_TEXT.addText("\n",true);')
        
        return True
    
    
    def home(self):
        self.curIndex = -1
        self.history = []
        self.setPage("Home")
    
    
    def back(self):
        if self.curIndex < 1:
            return
        
        pos = self.encScroll.childRelPos.split(" ")
        self.positions[self.curIndex] = (pos[0],pos[1])
        
        self.setPage(self.history[self.curIndex-1],False)
        self.curIndex -= 1
        pos = self.positions[self.curIndex]
        
        self.encScroll.scrollRectVisible(pos[0],pos[1],1,444)
    
    
    def forward(self):
        if self.curIndex >= len(self.history)-1 or not len(self.history):
            return
        
        pos = self.encScroll.childRelPos.split(" ")
        self.positions[self.curIndex] = (pos[0],pos[1])
        
        self.setPage(self.history[self.curIndex+1],False)
        self.curIndex += 1
        pos = self.positions[self.curIndex]
        self.encScroll.scrollRectVisible(pos[0],pos[1],1,444)



def encyclopediaSearch(searchvalue):
    if not ENCWND:
        PyExec()
    formatted = GetTWikiName(searchvalue)
    page = None
    if ENCYC.has_key("Item%s"%formatted):
        page = "Item%s"%formatted
    elif ENCYC.has_key("ItemSet%s"%formatted):
        page = "ItemSet%s"%formatted
    elif ENCYC.has_key("Spell%s"%formatted):
        page = "Spell%s"%formatted
    elif ENCYC.has_key("Recipe%s"%formatted):
        page = "Recipe%s"%formatted
    elif ENCYC.has_key("Skill%s"%formatted):
        page = "Skill%s"%formatted
    elif ENCYC.has_key("Class%s"%formatted):
        page = "Class%s"%formatted
    elif ENCYC.has_key("Spawn%s"%formatted):
        page = "Spawn%s"%formatted
    elif ENCYC.has_key("Quest%s"%formatted):
        page = "Quest%s"%formatted
    elif ENCYC.has_key("Zone%s"%formatted):
        page = "Zone%s"%formatted
    elif ENCYC.has_key("Faction%s"%formatted):
        page = "Faction%s"%formatted
    
    if page:
        ENCWND.setPage(page)
        TGEEval("canvas.pushDialog(EncyclopediaWnd);")
    else:
        TGECall("MessageBoxOK","Entry not found","No entry for %s in encyclopedia."%searchvalue)
    return


def encyclopediaGetLink(searchvalue):
    if not searchvalue:
        return None
    if not ENCWND:
        PyExec()
    formatted = GetTWikiName(searchvalue)
    link = None
    if ENCYC.has_key(formatted):
        link = "<a:%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Item%s"%formatted):
        link = "<a:Item%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("ItemSet%s"%formatted):
        link = "<a:ItemSet%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Spell%s"%formatted):
        link = "<a:Spell%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Recipe%s"%formatted):
        link = "<a:Recipe%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Skill%s"%formatted):
        link = "<a:Skill%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Class%s"%formatted):
        link = "<a:Class%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Spawn%s"%formatted):
        link = "<a:Spawn%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Quest%s"%formatted):
        link = "<a:Quest%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Zone%s"%formatted):
        link = "<a:Zone%s>%s</a>"%(formatted,searchvalue)
    elif ENCYC.has_key("Faction%s"%formatted):
        link = "<a:Faction%s>%s</a>"%(formatted,searchvalue)
    return link


def OnEncyclopediaOnURL(args):
    page = args[1]
    if page.startswith('chatlink'):
        # If a chatlink is clicked from encyclopedia, then
        # the command control is not visible because the
        # encyclopedia would have gained focus.
        commandCtrl = TomeGui.tomeCommandCtrl
        TGECall("PushChatGui")
        commandCtrl.visible = True
        commandCtrl.makeFirstResponder(True)
        txt = commandCtrl.GetValue()
        commandCtrl.SetValue("%s <%s>"%(txt,page[8:]))
    elif not ENCWND.setPage(page):
        TGECall("MessageBoxOK","Invalid Link","Sorry, you just stumbled upon an invalid encyclopedia link, page %s not found."%page)

def externEncyclopediaLinkURL(args):
    page = args[1].replace('gamelink','')
    if page.startswith('charlink'):  # link to tell, not encyc
        commandCtrl = TomeGui.tomeCommandCtrl
        if not commandCtrl.visible:
            TGECall("PushChatGui")
            commandCtrl.visible = True
            commandCtrl.makeFirstResponder(True)
        commandCtrl.SetValue("/tell %s "%page[8:].replace(' ','_'))
    elif not ENCWND.setPage(page):
        TGECall("MessageBoxOK","Invalid Link","Sorry, you just stumbled upon an invalid encyclopedia link, page %s not found."%page)
    else:
        TGEEval("canvas.pushDialog(EncyclopediaWnd);")


def OnEncyclopediaHome():
    ENCWND.home()


def OnEncyclopediaBack():
    ENCWND.back()


def OnEncyclopediaForward():
    ENCWND.forward()



def PyExec():
    global ENCWND
    ENCWND = EncWindow()
    
    #read the encyclopedia
    try:
        tar = tarfile.open("./%s/data/ui/encyclopedia/momworld.tar.gz"%GAMEROOT,'r:gz')
        for tarinfo in tar:
            if tarinfo.name.startswith("twiki/data/MoMWorld") and tarinfo.isreg():
                f = tar.extractfile(tarinfo)
                data = f.read()
                ENCYC[tarinfo.name[20:-4]] = data
        tar.close()
    except:
        traceback.print_exc()
        
    
    ENCYC["Home"]=HOME
    
    ENCWND.setPage("Home")
    
    TGEExport(OnEncyclopediaOnURL,"Py","OnEncyclopediaOnURL","desc",2,2)
    TGEExport(externEncyclopediaLinkURL,"Py","ExternEncyclopediaLinkURL","desc",2,2)
    
    TGEExport(OnEncyclopediaHome,"Py","OnEncyclopediaHome","desc",1,1)
    TGEExport(OnEncyclopediaForward,"Py","OnEncyclopediaForward","desc",1,1)
    TGEExport(OnEncyclopediaBack,"Py","OnEncyclopediaBack","desc",1,1)
    
    
    
