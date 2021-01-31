# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.worlddocs.utils import GetTWikiName
from mud.world.defines import *
from tomeGui import TomeGui



# Dictionary for relation color coding
relationColoring = {
    RPG_FACTION_HATED: 'FF0000',  # Red
    RPG_FACTION_DISLIKED: '00CCFF',  # Blue
    RPG_FACTION_UNDECIDED: 'FFFFFF',  # White
    RPG_FACTION_LIKED: 'CCCC00',  # Yellow
    RPG_FACTION_ADORED: '00FF00'  # Green
}

# Dictionary for encounter setting color coding
encounterSettingColoring = {
    RPG_ENCOUNTER_PVE: '00FF00',  # Green
    RPG_ENCOUNTER_RVR: 'CCCC00',  # Yellow
    RPG_ENCOUNTER_GVG: '00CCFF',  # Blue
    RPG_ENCOUNTER_PVP: 'FF0000'  # Red
}

# Global target description window, don't need more than one
TGTDESCWND = None


class TgtDescWnd:
    def __init__(self):
        # Cache TGEObjects
        self.bitmap = TGEObject("TGTDESCWND_BITMAP")
        
        self.nameDesc = TGEObject("TGTDESCWND_NAME")
        self.classesDesc = TGEObject("TGTDESCWND_CLASSES")
        self.raceDesc = TGEObject("TGTDESCWND_RACE")
        self.realmDesc = TGEObject("TGTDESCWND_REALM")
        
        self.npcInfo = TGEObject("TGTDESCWND_NPCINFO")
        self.npcPet = TGEObject("TGTDESCWND_NPCPET")
        
        self.pcInfo = TGEObject("TGTDESCWND_PCINFO")
        self.pcGuildName = TGEObject("TGTDESCWND_GUILDNAME")
        self.pcBirthDate = TGEObject("TGTDESCWND_BIRTHDATE")
        self.pcEncounterSetting = TGEObject("TGTDESCWND_PCENCOUNTERSETTING")
        
        self.myDescStuff = TGEObject("TGTDESCWND_MYDESCSTUFF")
        self.myDesc = TGEObject("TGTDESCWND_MYDESC")
        self.setMyDesc = TGEObject("TGTDESCWND_SETMYDESC")
        self.tgtScroll = TGEObject("TGTDESCWND_DESCSCROLL")
        self.tgtDesc = TGEObject("TGTDESCWND_DESCTEXT")
        
        self.mobID = 0
    
    
    def setInfo(self,infoDict):
        # Store mob id
        self.mobID = infoDict['TGTID']
        
        # Set target bitmap
        if infoDict['DEADTGT']:
            self.bitmap.SetBitmap("~/data/ui/charportraits/death")
        elif infoDict.has_key('PORTRAIT'):
            self.bitmap.SetBitmap("~/data/ui/charportraits/%s"%infoDict['PORTRAIT'])
        else:
            self.bitmap.SetBitmap("")
        
        # Set general target information
        classesDesc = "<a:gamelinkClass%s>%i %s</a>"%(GetTWikiName(infoDict['PCLASS']),infoDict['PLEVEL'],infoDict['PCLASS'])
        try:
            classesDesc += " / <a:gamelinkClass%s>%i %s</a>"%(GetTWikiName(infoDict['SCLASS']),infoDict['SLEVEL'],infoDict['SCLASS'])
            try:
                classesDesc += " / <a:gamelinkClass%s>%i %s</a>"%(GetTWikiName(infoDict['TCLASS']),infoDict['TLEVEL'],infoDict['TCLASS'])
            except KeyError:
                pass
        except KeyError:
            pass
        self.classesDesc.SetText(classesDesc)
        self.raceDesc.SetText(infoDict['RACE'])
        self.realmDesc.SetText(RPG_REALM_TEXT[infoDict['REALM']])
        
        # Set character specific information
        if infoDict['CHARTGT']:
            self.nameDesc.SetText("<a:gamelinkcharlink%s>%s %s</a>"%(infoDict['NAME'].replace(' ','_'),infoDict['NAME'],infoDict['VARIANTNAME']))
            self.npcInfo.visible = False
            guildname = infoDict['GUILDNAME']
            if guildname == "":
                self.pcGuildName.SetText("None")
            else:
                self.pcGuildName.SetText(guildname)
            self.pcBirthDate.SetText(infoDict['BIRTHDATE'])
            setting = infoDict['ENCOUNTERSETTING']
            self.pcEncounterSetting.SetText("<color:%s>%s"%(encounterSettingColoring[setting],RPG_ENCOUNTER_SETTING_FORINDEX[setting]))
            self.pcInfo.visible = True
        # Set npc specific information
        else:
            self.nameDesc.SetText("<a:gamelinkSpawn%s>%s %s</a>"%(GetTWikiName(infoDict['NAME']),infoDict['VARIANTNAME'],infoDict['NAME']))
            self.pcInfo.visible = False
            if infoDict['PET']:
                self.npcPet.visible = True
            else:
                self.npcPet.visible = False
            self.npcInfo.visible = True
        
        # Set target description
        if infoDict['MYSELF']:
            # If the description is my own, get the editable version
            self.tgtScroll.visible = False
            self.setMyDesc.setActive(False)
            self.myDesc.SetText(infoDict['DESC'])
            self.myDescStuff.visible = True
        else:
            # Not mine, disable editable version
            self.myDescStuff.visible = False
            relation,relationDesc = infoDict['STANDING']
            desc = "%s\n\n<color:%s>%s"%(infoDict['DESC'],relationColoring[relation],relationDesc)
            self.tgtDesc.setText(desc)
            self.tgtScroll.visible = True
        
        # Show the dialog
        TGEEval("canvas.pushDialog(TgtDescWnd);")
        if infoDict['MYSELF']:
            self.myDesc.makeFirstResponder(True)


def tgtDescWndOnSetMyDesc():
    global TGTDESCWND
    TGTDESCWND.setMyDesc.setActive(False)
    myDesc = TGTDESCWND.myDesc.GetText()
    from mud.client.playermind import PLAYERMIND
    PLAYERMIND.perspective.callRemote("PlayerAvatar","setSpawnDesc",myDesc,TGTDESCWND.mobID)
    TomeGui.instance.receiveGameText(RPG_MSG_GAME_EVENT,"New Character description set!\\n")



def PyExec():
    # Instantiate one target description window, we don't need multiple
    global TGTDESCWND
    TGTDESCWND = TgtDescWnd()
    
    TGEExport(tgtDescWndOnSetMyDesc,"Py","TgtDescWndOnSetMyDesc","desc",1,1)
