# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#SpawnPages

from mud.world.spawn import Spawn
from mud.world.defines import *
from utils import *
import os
from collections import defaultdict
import re



SpawnPage = """
^^IMAGELINK^^
---+ ^^SPAWNNAME^^

*Quick Links:* [[#MyLoot][Loot]],[[#MyFactions][Factions]],[[#MyVendor][Vendor]]

*Realm:* ^^REALMTEXT^^

*Habitat:* ^^HABITATTEXT^^

*Description:* ^^DESCTEXT^^

---++ Stats

^^LEVELTEXT^^

^^STATSTEXT^^

^^QUESTTEXT^^

#MyFactions
---++ Factions

^^FACTIONSTEXT^^

#MyLoot
---++ Loot

^^LOOTTEXT^^

#MyVendor
---++ Vendor

^^VENDORTEXT^^
 
"""

QUESTDIALOGS = defaultdict(set)
SPAWNSPELLS = defaultdict(set)

LINKPARSER = re.compile(r'<a:([\s\S]*?)>([\s\S]*?)</a>')



class SpawnFactionContainer:
    def __init__(self):
        self.lowers = set()
        self.raises = set()
SPAWNFACTIONS = defaultdict(SpawnFactionContainer)



def CreateSpawnIndexByLevel():
    page = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    page += "---+ Spawn Index by Level\n\n"
    
    level = 0
    for spawn in Spawn.select(orderBy="plevel"):
        if level != spawn.level:
            page += "---++ Level %i<br>\n"%spawn.level
            level = spawn.level
        page += "\t* [[Spawn%s][%s]]\n"%(GetTWikiName(spawn.name),spawn.name)
    
    f = file("./distrib/twiki/data/MoMWorld/SpawnIndexByLevel.txt","w")
    f.write(page)
    f.close()


def GenFactionsText(spawn):
    factions = list(spawn.factions)
    killfactions = list(spawn.killFactions)
    if not len(factions) and not len(killfactions):
        return "*None*"
    
    for f in factions:
        SPAWNFACTIONS[f.name].lowers.add(spawn.name)
        
    ftext = ', '.join('[[Faction%s][%s]]'%(GetTWikiName(f.name),f.name) for f in factions)
    
    if len(killfactions):

        ftext += "\n\n*Kill Faction Adjustments:* "
        for kf in killfactions:
            faction = kf.faction
            percent = kf.percent
            twiki = GetTWikiName(faction.name)
            if percent < 0:
                ftext += "[[Faction%s][%s]] :(, "%(twiki,faction.name)
                SPAWNFACTIONS[faction.name].lowers.add(spawn.name)
            else:
                ftext += "[[Faction%s][%s]] :), "%(twiki,faction.name)
                SPAWNFACTIONS[faction.name].raises.add(spawn.name)
        
        ftext = ftext[:-2]
    
    return ftext


def GenStatsText(spawn):
    stext = "*Race:* [[Race%s][%s]], *Gender:* %s "%(GetTWikiName(spawn.race),spawn.race,spawn.sex)
    
    if spawn.respawn:
        stext += "*Respawns:* [[Spawn%s][%s]] "%(GetTWikiName(spawn.respawn.name),spawn.respawn.name)
    
    stext += "*Move:* %.1f "%(spawn.move)
    
    # Resistances
    if len(spawn.resists):
        stext += "*Resistances:* %s"%', '.join('%s (%i)'%(RPG_RESIST_TEXT[r.resistType],r.resistAmount) for r in spawn.resists)
    
    # Special Abilities
    if len(spawn.spawnStatsInternal) or len(spawn.spawnSpellsInternal):
        stext += "\n\n*Special Abilities:* "
        
        for s in spawn.spawnSpellsInternal:
            stext += "[[Spell%s][%s]], "%(GetTWikiName(s.spellname),s.spellname)
            SPAWNSPELLS[s.spellname].add(spawn.name)
        
        for stat in list(spawn.spawnStatsInternal):
            #statname,value
            if stat.statname == "innateHaste":
                stext += "Haste (%i%%), "%int(stat.value*100)
            elif stat.statname == "flying":
                stext += "Flight, "
            elif stat.statname == "light":
                stext += "Illumination, "
        
        stext = stext[:-2]+" "
    
    return stext


def MySort(a,b):
    if a.name < b.name:
        return -1
    if a.name > b.name:
        return 1
    return 0


def GenLootText(spawn):
    from mud.world.core import GenMoneyText
    
    if spawn.flags&RPG_SPAWN_NOCORPSE or spawn.respawn:
        loottext = "*Note: This spawn does not leave a corpse!*\n\n"
    else:
        loottext = ""
    
    loot = spawn.lootProto
    if not loot:
        return loottext + "*None*"
    
    if loot.tin:
        loottext += "Money: %s\n\n"%GenMoneyText(loot.tin)
    
    lootItems = list(loot.lootItems)
    if len(lootItems):
        loottext += "| *Item Name* | *Frequency*|\n"
        
        freqs = ("Always","Common","Uncommon","Rare","Very Rare","Impossible","???")
        
        for f in freqs:
            for lootitem in lootItems:
                freq = RPG_FREQ_TEXT.get(lootitem.freq)
                if not freq or freq == "Impossible":
                    freq = "???"
                if f != freq:
                    continue
                
                iproto = lootitem.itemProto
                loottext+="|[[Item%s][%s]]|%s|\n"%(GetTWikiName(iproto.name),iproto.name,freq)
    
    return loottext


def GenVendorText(spawn):
    vproto = spawn.vendorProto
    if not vproto:
        return "*None*"
    
    vTable = "| *Item Name* | *Frequency*|\n"
    freqs = ("Always","Common","Uncommon","Rare","Very Rare","Impossible","???")
    
    vitems = list(vproto.vendorItems)
    for f in freqs:
        for vitem in vitems:
            freq = RPG_FREQ_TEXT.get(vitem.frequency)
            iproto = vitem.itemProto
            if not freq:
                freq = "???"
            if f != freq:
                continue
            
            iproto = vitem.itemProto
            vTable += "|[[Item%s][%s]]|%s|\n"%(GetTWikiName(iproto.name),iproto.name,freq)
    
    return vTable


def GenQuestText(spawn):
    if not spawn.dialog:
        return ""
    
    qtext = ""
    dialogs = []
    for c in spawn.dialog.choices:
        for d in c.dialogs:
            if not len(d.actions):
                continue
            if d not in dialogs:
                dialogs.append(d)
    if len(spawn.dialog.actions):
        QUESTDIALOGS[spawn.dialog].add(spawn)
    
    if not len(dialogs):
        return ""
    
    qtext = "---++ Quests\n"
    for d in dialogs:
        qtext += "[[Quest%s][%s]], "%(GetTWikiName(d.name),d.name)
        QUESTDIALOGS[d].add(spawn)
    qtext = qtext[:-2]
    return qtext


def CreateSpawnPages():
    #SpawnIndex
    CreateSpawnIndexByLevel()
    
    indexPage = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    indexPage += "---+ Spawn (NPC) Index\n\n"
    
    for spawn in Spawn.select(orderBy="name"):
        SPAWNNAME = spawn.name
        TWIKINAME = 'Spawn'+GetTWikiName(SPAWNNAME)
        indexPage += "\t* [[%s][%s]]\n"%(TWIKINAME,SPAWNNAME)
        if spawn.flags&RPG_SPAWN_UNIQUE and spawn.realm == RPG_REALM_MONSTER:
            if spawn.flags&RPG_SPAWN_INN:
                SPAWNNAME += " (Unique Monster Innkeeper)"
            else:
                SPAWNNAME += " (Unique Monster)"
        elif spawn.flags&RPG_SPAWN_UNIQUE:
            if spawn.flags&RPG_SPAWN_INN:
                SPAWNNAME += " (Unique NPC Innkeeper)"
            else:
                SPAWNNAME += " (Unique NPC)"
        
        #levels
        levels = ((spawn.plevel,spawn.pclassInternal),(spawn.slevel,spawn.sclassInternal),(spawn.tlevel,spawn.tclassInternal))
                
        LEVELTEXT = ""
        for level,klass in levels:
            if not level or not klass:
                break
            LEVELTEXT += "[[Class%s][%s]] (%i) "%(GetTWikiName(klass),klass,level)
        
        DESCTEXT = "None"
        if spawn.desc:
            DESCTEXT = LINKPARSER.sub(r'[[\1][\2]]',spawn.desc)
        
        #HABITAT
        zones = []
        for sinfo in spawn.spawnInfos:
            for sgroup in sinfo.spawnGroups:
                if sgroup.zone not in zones:
                    zones.append(sgroup.zone)
        
        HABITATTEXT = ', '.join('[[Zone%s][%s]]'%(GetTWikiName(z.niceName),z.niceName) for z in zones)
        if not HABITATTEXT:
            HABITATTEXT = "Summoned"
        
        LOOTTEXT = GenLootText(spawn)
        FACTIONSTEXT = GenFactionsText(spawn)
        QUESTTEXT = GenQuestText(spawn)
        
        STATSTEXT = GenStatsText(spawn)
        VENDORTEXT = GenVendorText(spawn)
        
        if spawn.realm == RPG_REALM_NEUTRAL:
            realmtext = "Neutral"
        if spawn.realm == RPG_REALM_DARKNESS:
            realmtext = "Minions of Darkness"
        if spawn.realm == RPG_REALM_LIGHT:
            realmtext = "Fellowship of Light"
        if spawn.realm == RPG_REALM_MONSTER:
            realmtext = "Monster"
        
        image = spawn.model+spawn.textureSingle
        image = image.upper()
        image = image.replace(".DTS","")
        image = image.replace("/","")
        
        IMAGELINK = ""
        if image:
            if os.path.isfile("./mud/worlddocs/images/%s.jpg"%image):
                pass
            else:
                if "QUARANTINE" not in image:
                    print image+'.jpg'
                image = "UNKNOWN.jpg"
            
            IMAGELINK = r'<a href="http://www.prairiegames.com/twiki/pub/MoMWorld/%s.jpg"><img src="http://www.prairiegames.com/twiki/pub/MoMWorld/%s.jpg" width="192" height="192" align="right"  /></a>'%(image,image)
        
        page = SpawnPage
        page = page.replace("^^SPAWNNAME^^",SPAWNNAME)
        page = page.replace("^^LEVELTEXT^^",LEVELTEXT)
        page = page.replace("^^DESCTEXT^^",DESCTEXT)
        page = page.replace("^^LOOTTEXT^^",LOOTTEXT)
        page = page.replace("^^FACTIONSTEXT^^",FACTIONSTEXT)
        page = page.replace("^^STATSTEXT^^",STATSTEXT)
        page = page.replace("^^HABITATTEXT^^",HABITATTEXT)
        page = page.replace("^^VENDORTEXT^^",VENDORTEXT)
        page = page.replace("^^QUESTTEXT^^",QUESTTEXT)
        page = page.replace("^^IMAGELINK^^",IMAGELINK)
        page = page.replace("^^REALMTEXT^^",realmtext)
        
        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAME,"w")
        f.write(page)
        f.close()
    
    f = file("./distrib/twiki/data/MoMWorld/SpawnIndex.txt","w")
    f.write(indexPage)
    f.close()
    
    return QUESTDIALOGS,SPAWNSPELLS,SPAWNFACTIONS
    
        
        
        
 
