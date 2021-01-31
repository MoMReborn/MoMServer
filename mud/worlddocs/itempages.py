# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud.world.vendor import VendorProto
from mud.world.loot import LootProto
from mud.world.spell import SpellProto
from mud.world.dialog import Dialog
from mud.world.crafting import Recipe

from mud.world.defines import *
from utils import *
from collections import defaultdict

ItemPage = """
---+ ^^ITEMNAME^^

---++ Description

^^DESCTEXT^^

---++ Stats

---+++++ ^^FLAGTEXT^^

^^STATTEXT^^

---++ Procurement
^^PROCUREMENTTEXT^^

---++ Quests
^^QUESTTEXT^^
"""


#we'll only document items that actually drop, can be bought, can be summoned, or are the results of a quest

SUMMONEDITEMS = set()
QUESTITEMS = set()

CRAFTITEMS = defaultdict(set)
INGREDIENTS = defaultdict(set) #itemproto -> list of recipes
RECIPES = defaultdict(set) #itemproto->list of recipes


#[itemproto]->spawns
LOOT = defaultdict(set)

#[item]->dialog
QUESTSGIVE = defaultdict(set)
QUESTSTAKE = defaultdict(set)
QUESTSCHECK = defaultdict(set)

#[item]->spells
SUMMONED = defaultdict(set)

#item->spawns
VENDORS = defaultdict(set)

# sub indexes, syntax: [file name, title, associated item list]
ItemSubIndexes = []
ItemSubIndexes.append(("ItemSummonedIndex","Summoned Items",SUMMONEDITEMS))
ItemSubIndexes.append(("ItemQuestIndex","Quest Items",QUESTITEMS))


def GetItemList(spellSummonItems,questItems):
    items = set()
    
    #CRAFTED
    for rproto in Recipe.select():
        iproto = rproto.craftedItemProto
        craftskill = rproto.skillname
        if iproto:
            CRAFTITEMS[craftskill].add(iproto)
            
            items.add(iproto)
            RECIPES[iproto].add(rproto)
            
            for ing in rproto.ingredients:
                iproto = ing.itemProto
                CRAFTITEMS[craftskill].add(iproto)
                
                items.add(iproto)
                INGREDIENTS[iproto].add(rproto)
    
    
    #LOOT
    for proto in LootProto.select():
        for lootitem in proto.lootItems:
            items.add(lootitem.itemProto)
            LOOT[lootitem.itemProto].update(proto.spawns)
    
    #VENDORS
    for proto in VendorProto.select():
        for vitem in proto.vendorItems:
            items.add(vitem.itemProto)
            VENDORS[vitem.itemProto].update(proto.spawns)
    
    #SUMMONED
    for summonItem in spellSummonItems.iterkeys():
        items.add(summonItem)
        SUMMONEDITEMS.add(summonItem)
        SUMMONED[summonItem].update(spellSummonItems[summonItem])
    
    #QUEST
    # first come the items taken
    for qitem in questItems[0].iterkeys():
        items.add(qitem)
        QUESTITEMS.add(qitem)
        QUESTSTAKE[qitem].update(questItems[0][qitem])
    # then items checked
    for qitem in questItems[1].iterkeys():
        items.add(qitem)
        QUESTITEMS.add(qitem)
        QUESTSCHECK[qitem].update(questItems[1][qitem])
    # then items given
    for qitem in questItems[2].iterkeys():
        items.add(qitem)
        QUESTITEMS.add(qitem)
        QUESTSGIVE[qitem].update(questItems[2][qitem])
    
    
    for craftskill,itemlist in CRAFTITEMS.iteritems():
        ItemSubIndexes.append(("Item%sIndex"%GetTWikiName(craftskill),"%s Crafts and Ingredients"%craftskill,itemlist))
    
    return items


def GenProcurementText(item):
    
    ptext = []
    
    #crafted
    recipes = RECIPES.get(item,set())
    if len(recipes):
        ptext.append("<br> *Recipe:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Recipe%s"%GetTWikiName(r.name),r.name) for r in recipes))

    #craft ingredient
    recipes = INGREDIENTS.get(item,set())
    if len(recipes):
        ptext.append("<br> *Craft Ingredient:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Recipe%s"%GetTWikiName(r.name),r.name) for r in recipes))
    
    #vendors
    vendors = VENDORS.get(item,set())
    if len(vendors):
        ptext.append("<br> *Vendors:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Spawn%s"%GetTWikiName(v.name),v.name) for v in vendors))
    
    #spawns    
    spawns = LOOT.get(item,set())
    if len(spawns):
        ptext.append("<br> *Spawns:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Spawn%s"%GetTWikiName(s.name),s.name) for s in spawns))
    
    #quests    
    quests = QUESTSGIVE.get(item,set())
    if len(quests):
        ptext.append("<br> *Quests:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Quest%s"%GetTWikiName(q.name),q.name) for q in quests))
    
    #summoned
    spells = SUMMONED.get(item,set())
    if len(spells):
        ptext.append("<br> *Summoning Spells:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Spell%s"%GetTWikiName(s.name),s.name) for s in spells))
    
    return ''.join(ptext)

def GenQuestText(item):
    ptext = []
    
    #quests    
    quests = QUESTSGIVE.get(item,set())
    if len(quests):
        ptext.append("<br> *Rewarded By:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Quest%s"%GetTWikiName(q.name),q.name) for q in quests))

    quests = QUESTSTAKE.get(item,set())
    if len(quests):
        ptext.append("<br> *Taken By:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Quest%s"%GetTWikiName(q.name),q.name) for q in quests))

    quests = QUESTSCHECK.get(item,set())
    if len(quests):
        ptext.append("<br> *Checked By:* ")
        ptext.append(', '.join("[[%s][%s]]"%("Quest%s"%GetTWikiName(q.name),q.name) for q in quests))

    return ''.join(ptext)


def GenStatText(item,contributes):
    stext = []
    
    #races
    
    if item.level > 1:
        stext.append("*Recommended Level:* %i<br> "%item.level)
    
    
    races = item.races
    if len(races):
        stext.append("*Races:* ")
        stext.append(', '.join("[[%s][%s]]"%("Race%s"%GetTWikiName(race),race) for race in races))
        stext.append(' ')
    
    #classes
    classes = list(item.classes)
    if len(classes):
        stext.append("*Classes:* ")
        stext.append(', '.join("[[%s][%s]] (%i)"%("Class%s"%GetTWikiName(klass.classname),klass.classname,klass.level) for klass in classes))
        stext.append(' ')
    
    #slots
    if len(item.slots):
        stext.append("*Slots:* ")
        stext.append(', '.join(RPG_SLOT_TEXT[slot] for slot in item.slots))
        stext.append(' ')
    
    #skill
    if item.skill:
        stext.append("*Skill:* %s "%item.skill)

    #weapon
    if item.wpnDamage:
        stext.append("*Weapon:* %i/%i/%i "%(int(item.wpnDamage),int(item.wpnRate),int(item.wpnRange)))

    #armor
    if item.armor:
        stext.append("*Armor:* %i "%(item.armor))

    #light
    if item.light:
        stext.append("*Light:* %i "%(int(item.light)))
        
        
    #stats
    stats = list(item.stats)
    if len(stats):
        stext.append("<br> *Special:* ")
        for st in stats:
            name = st.statname
            value = st.value
            
            if name=="haste":
                stext.append("%%GREEN%%HASTE %i%% %%ENDCOLOR%%, "%int(value*100.0))
            elif name.lower()=="casthaste":
                stext.append("%%GREEN%%CASTING HASTE %i%% %%ENDCOLOR%%, "%int(value*100.0))
            elif name=="regenHealth":
                stext.append("%%GREEN%%HEALTH REGEN %i %%ENDCOLOR%%, "%int(value))
            elif name=="regenMana":
                stext.append("%%BLUE%%MANA REGEN %i %%ENDCOLOR%%, "%int(value))
            elif name=="regenStamina":
                stext.append("%%YELLOW%%STAMINA REGEN %i %%ENDCOLOR%%, "%int(value))
            elif name=="move":
                stext.append("%%GREEN%%MOVE +%i%% %%ENDCOLOR%%, "%int(value*100.0))
            elif value != round(value):
                if value > 0:
                    stext.append("%%GREEN%%%s %i%% %%ENDCOLOR%%, "%(name.upper(),int(value*100.0)))
                else:
                    stext.append("%%RED%%%s %i%% %%ENDCOLOR%%, "%(name.upper(),int(value*100.0)))
            else:
                if value > 0:
                    stext.append("%%GREEN%%%s %i %%ENDCOLOR%%, "%(name.upper(),int(value)))
                else:
                    stext.append("%%RED%%%s %i %%ENDCOLOR%%, "%(name.upper(),int(value)))
                
            
        stext[-1] = stext[-1][:-2]+" "
        
    #procs
    
    
    trigger = {
        RPG_ITEM_TRIGGER_WORN: 'Worn',
        RPG_ITEM_TRIGGER_MELEE: 'Melee',
        RPG_ITEM_TRIGGER_DAMAGED: 'Damaged',
        RPG_ITEM_TRIGGER_USE: 'Use',
        RPG_ITEM_TRIGGER_POISON: 'Poison'
    }
    
    spells = list(item.spells)
    if len(spells):
        stext.append("<br> *Procs:* ")
        stext.append(', '.join("[[Spell%s][%s]] (%s)"%(GetTWikiName(s.spellProto.name),s.spellProto.name,trigger[s.trigger]) for s in spells))
        stext.append(' ')
    
    if len(contributes):
        stext.append("<br> *Associated Item Sets:* ")
        stext.append(', '.join("[[ItemSet%s][%s]]"%(GetTWikiName(setname),setname) for setname in contributes))
        stext.append(' ')
    
    if item.spellProto:
        spellName = item.spellProto.name
        stext.append("<br> *Teaches the Spell* [[Spell%s][%s]]"% \
            (GetTWikiName(spellName),spellName))
    
    return ''.join(stext)


def CreateItemSubIndex(indexFile,indexTitle,itemList):
    subpage = "---+ %s\n\n"%indexTitle
    subpage += ''.join("\t* [[%s][%s]]\n"%("Item%s"%GetTWikiName(item.name),item.name) for item in sorted(itemList,key=lambda obj:obj.name))
    f = file("./distrib/twiki/data/MoMWorld/%s.txt"%indexFile,"w")
    f.write(subpage)
    f.close()

def CreateItemIndex(items):
    # top index
    indexPage = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    indexPage += "---+ Item Index\n\n"
    indexPage += "\t* [[ItemAllIndex][Index of all Items]]\n"
    indexPage += "\t* [[ItemAllLevelIndex][Index of all Items by Level]]\n\n"
    
    subpage = "---+ Index of all Items by Level\n\n"
    level = 0
    for item in sorted(items,key=lambda obj:obj.level):
        # filter out all uninteresting items
        if not any([len(item.slots), len(item.spells), item.level > 1]):
            continue
        if item.level != level:
            level = item.level
            subpage += "---+++ Level %i<br>\n"%level
        TWIKINAME = "Item"+GetTWikiName(item.name)
        subpage+="\t* [[%s][%s]]\n"%(TWIKINAME,item.name)
    f = file("./distrib/twiki/data/MoMWorld/ItemAllLevelIndex.txt","w")
    f.write(subpage)
    f.close()
    
    for index in ItemSubIndexes:
        indexPage += "\t* [[%s][%s]]\n"%(index[0],index[1])
        CreateItemSubIndex(index[0],index[1],index[2])
    # the table for spell scrolls will be generated in spellpages.py
    # since we go through all scrolls there anyway
    indexPage += "\t* [[ItemSpellScrollsIndex][Spell Scrolls]]\n"
    
    f = file("./distrib/twiki/data/MoMWorld/ItemIndex.txt","w")
    f.write(indexPage)
    f.close()

        
def CreateItemPages(spellSummonItems,questItems):
    ITEMSETDICT = defaultdict(dict)
    items = GetItemList(spellSummonItems,questItems)
    
    allPage = "---+ Index of all Items\n\n"
    
    for item in sorted(items,key=lambda obj:obj.name):
        contributes = set()
        for itemSet in item.itemSets:
            ITEMSETDICT[itemSet.itemSetProto].setdefault(itemSet.contribution, set()).add(item.name)
            contributes.add(itemSet.itemSetProto.name)
        page = ItemPage
        
        TWIKINAME = "Item"+GetTWikiName(item.name)
        allPage += "\t* [[%s][%s]]\n"%(TWIKINAME,item.name)
        
        PROCUREMENTTEXT = GenProcurementText(item)
        FLAGTEXT = ' '.join([t for f,t in RPG_ITEM_FLAG_TEXT.iteritems() if item.flags&f])
        STATTEXT = GenStatText(item,contributes)
        QUESTTEXT = GenQuestText(item)
        
        page = page.replace("^^ITEMNAME^^",item.name)
        if item.desc:
            page = page.replace("^^DESCTEXT^^",item.desc)
        else:
            page = page.replace("^^DESCTEXT^^","None")
        
        page = page.replace("^^PROCUREMENTTEXT^^",PROCUREMENTTEXT)
        page = page.replace("^^FLAGTEXT^^",FLAGTEXT)
        page = page.replace("^^STATTEXT^^",STATTEXT)
        page = page.replace("^^QUESTTEXT^^",QUESTTEXT)
        
        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAME,"w")
        f.write(page)
        f.close()
    
    f = file("./distrib/twiki/data/MoMWorld/ItemAllIndex.txt","w")
    f.write(allPage)
    f.close()
    CreateItemIndex(items)
    
    return ITEMSETDICT
        
        
    


    

 