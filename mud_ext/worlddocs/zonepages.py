# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.world.zone import Zone
from mud.world.defines import *
from utils import *
from mud.world.loot import ZONE_ENCHANTINGITEMS

ENCHANT_FocusPowersNice = {
'Health':'Max Health',
'Ether':'Max Mana',
'Endurance':'Max Stamina',
'Strength':'Strength',
"Constitution":'Body',
"Instinct":'Reflex',
"Nimbleness":'Agility',
"Quickness":'Dexterity',
"Insight":'Mind',
'Clarity':'Wisdom',
"the Arcane":'Mysticism',
'Defense':'Armor',
'Physical Protection':'Physical Resistance',
'Magic Protection':'Magical Resistance',
'Fiery Protection':'Fire Resistance',
'Cold Protection':'Cold Resistance',
'Electrical Resistance':'Electrical Resistance',
'Acidity':'Acid Resistance',
'Poison Resist':'Poison Resistance',
'Disease Resist':'Disease Resistance',
'the Sphinx':'Cast Time',
'the Dwarven King':'Health Regeneration',
'Volsh':'Melee Haste',
'Speed':'Movement Speed',
'Lightning':'Spell Damage',
'the Warling Cleric':'Healing Spell Modifier',
'Aelieas':'Mana Regeneration',
'the Cavebear':'Stamina Regeneration',
'the Ghoul Slayer':'Undead Bane'
}

ZonePage = """
---+ ^^ZONENAME^^

*Quick Links:* [[#MySpawns][Spawns]],[[#MyLoot][Loot]]

---++ Description

^^DESCTEXT^^
#MyLoot
---++ Loot
^^LOOTTEXT^^
#MySpawns
---++ Spawns
^^SPAWNTEXT^^
    
"""


def GenSpawnText(spawns):
    #generate twiki names
    twiki = dict((s,'Spawn%s'%GetTWikiName(s.name)) for s in spawns)
    
    vendors  = []
    npc      = []
    monsters = []
    dialog   = []
    uniques  = []
    inns     = []
    
    for s in sorted(spawns,key=lambda obj:obj.name):
        if s.vendorProto:
            vendors.append(s)
        if s.flags&RPG_SPAWN_UNIQUE:
            uniques.append(s)
        if s.realm == RPG_REALM_MONSTER:
            monsters.append(s)
        else:
            npc.append(s)
        if s.dialog:
            dialog.append(s)
        if s.flags&RPG_SPAWN_INN:
            inns.append(s)
    
    stext = ""
    if len(dialog):
        stext += "\n\n*Quests, Trainers, Dialog:* %s"%', '.join('[[%s][%s]]'%(twiki[s],s.name) for s in dialog)
    
    if len(inns):
        stext += "\n\n*Innkeepers:* %s"%', '.join('[[%s][%s]]'%(twiki[s],s.name) for s in inns)
    
    if len(vendors):
        stext += "\n\n*Vendors:* %s"%', '.join('[[%s][%s]]'%(twiki[s],s.name) for s in vendors)
    
    if len(uniques):
        stext += "\n\n*Uniques:* %s"%', '.join('[[%s][%s]]'%(twiki[s],s.name) for s in uniques)
    
    if len(npc):
        stext += "\n\n*NPC:* %s"%', '.join('[[%s][%s]]'%(twiki[s],s.name) for s in npc)
    
    if len(monsters):
        stext += "\n\n*Monsters:* %s"%', '.join('[[%s][%s]]'%(twiki[s],s.name) for s in monsters)
    
    return stext


def CreateZonePages():
    climate = {
        RPG_CLIMATE_POLAR: 'Polar',
        RPG_CLIMATE_TROPICAL: 'Tropical',
        RPG_CLIMATE_TEMPERATE: 'Temperate',
        RPG_CLIMATE_DRY: 'Dry',
        RPG_CLIMATE_COLD: 'Cold'
    }
    
    indexPage = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    indexPage += "---+ Zone Index\n\n"
    
    FocusLootDetailPage = """
---+ Enchanting Focus Loot Details

In every zone that allows for focus drops there is a slight chance to get a focus from all mobs living in that zone. The special zone foci are especially rare.
The dropped foci have a random variety in quality [[FocusMergingDetails][(Focus Merging Details)]]. Higher quality is significantly rarer. The special zone foci always come at maximum quality.
Raw focus types are never dropped and can only be gained through disenchanting.


---++ Zones in which to find Foci
"""
    
    
    #ZONES
    for zone in Zone.select(orderBy = "niceName"):
        page = ZonePage
        addToFocusPage = zone.name in ZONE_ENCHANTINGITEMS
        
        TWIKINAME = GetTWikiName(zone.niceName)
        indexPage+="\t* [[Zone%s][%s]]\n"%(TWIKINAME,zone.niceName)
        if addToFocusPage:
            FocusLootDetailPage += "\n\n---++++ [[Zone%s][%s]]\n \t*Raw Type:* %s <br> \t*Random Foci:* <br>"%(TWIKINAME,zone.niceName,ZONE_ENCHANTINGITEMS[zone.name][0].split(' of ',1)[0])
            for focusName in ZONE_ENCHANTINGITEMS[zone.name][:-1]:
                FocusLootDetailPage += "\t\t    %s (%s) <br>"%(focusName,ENCHANT_FocusPowersNice[focusName.split(' of ',1)[1]])
            specialFocus = ZONE_ENCHANTINGITEMS[zone.name][-1]
            FocusLootDetailPage += " \t*Special Focus:* %s (%s) <br>"%(specialFocus,ENCHANT_FocusPowersNice[specialFocus.split(' of ',1)[1]])
        
        DESCTEXT = "*Climate:* "+climate[zone.climate]+"<br>\n"
        b = (int(zone.xpMod*100)-100)
        if b:
            DESCTEXT += "*Experience Bonus:* %i%%<br>"%b
        
        spawns = set(si.spawn for sg in zone.spawnGroups for si in sg.spawninfos)
        SPAWNTEXT = GenSpawnText(spawns)
        items = set(lootitem.itemProto for s in spawns if s.lootProto for lootitem in s.lootProto.lootItems)
        LOOTTEXT = ', '.join('[[Item%s][%s]]'%(GetTWikiName(item.name),item.name) for item in sorted(items,key=lambda obj:obj.name))
        
        page = page.replace("^^DESCTEXT^^",DESCTEXT)
        page = page.replace("^^ZONENAME^^",zone.niceName)
        page = page.replace("^^SPAWNTEXT^^",SPAWNTEXT)
        page = page.replace("^^LOOTTEXT^^",LOOTTEXT)
        
        f = file("./distrib/twiki/data/MoMWorld/Zone%s.txt"%TWIKINAME,"w")
        f.write(page)
        f.close()
    
    
    f = file("./distrib/twiki/data/MoMWorld/ZoneIndex.txt","w")
    f.write(indexPage)
    f.close()
    f = file("./distrib/twiki/data/MoMWorld/FocusLootDetails.txt","w")
    f.write(FocusLootDetailPage)
    f.close()
        
        
 