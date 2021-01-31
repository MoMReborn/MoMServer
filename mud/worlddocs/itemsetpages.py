# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud.world.defines import *
from utils import *


def CreateItemSetPages(itemSetDict):
    itemSetTopPage = "---+ Index of all Item Sets\n\n"
    
    truthSelector = {True: 'Yes', False: 'No'}
    testSelector = {RPG_ITEMSET_TEST_LESSEQUAL: 'less than or exactly', RPG_ITEMSET_TEST_EQUAL: 'exactly', RPG_ITEMSET_TEST_GREATEREQUAL: 'at least'}
    trigger = {
        RPG_ITEM_TRIGGER_WORN: 'Worn',
        RPG_ITEM_TRIGGER_MELEE: 'Melee',
        RPG_ITEM_TRIGGER_DAMAGED: 'Damaged',
        RPG_ITEM_TRIGGER_USE: 'Use',
        RPG_ITEM_TRIGGER_POISON: 'Poison'
    }
    
    for set,contributions in sorted(itemSetDict.iteritems(), key=lambda obj:obj[0].name):
        TWIKINAME = "ItemSet%s"%GetTWikiName(set.name)
        itemSetTopPage += "\t* [[%s][%s]]\n"%(TWIKINAME,set.name)
        
        itemSetPage = "---+ %s\n\n"%set.name
        itemSetPage += "---++ Set Powers\n\n"
        
        for power in set.powers:
            itemSetPage += "---+++ '%s'\n"%power.name
            itemSetPage += "\t*Harmful:* %s\n"%truthSelector[power.harmful]
            itemSetPage += "\t*Prerequisites:*\n%s\n"%'\n'.join("\t\t* Must have %s %i %s items equipped."%(testSelector[req.countTest],req.itemCount,req.name) for req in power.requirements)
            if len(power.spells):
                itemSetPage += "\t*Spell Procs:* %s\n"%', '.join("[[Spell%s][%s]] (%s)"%(GetTWikiName(proc.spellProto.name),proc.spellProto.name,trigger[proc.trigger]) for proc in power.spells)
            else:
                itemSetPage += "\t*Spell Procs:* None\n"
            
            stext = []
            for st in power.stats:
                name = st.statname
                value = st.value
                if name == "haste":
                    stext.append("%%GREEN%%HASTE %i%% %%ENDCOLOR%%"%int(value*100.0))
                elif name.lower() == "casthaste":
                    stext.append("%%GREEN%%CASTING HASTE %i%% %%ENDCOLOR%%"%int(value*100.0))
                elif name == "regenHealth":
                    stext.append("%%GREEN%%HEALTH REGEN %i %%ENDCOLOR%%"%int(value))
                elif name == "regenMana":
                    stext.append("%%BLUE%%MANA REGEN %i %%ENDCOLOR%%"%int(value))
                elif name == "regenStamina":
                    stext.append("%%YELLOW%%STAMINA REGEN %i %%ENDCOLOR%%"%int(value))
                elif name == "move":
                    stext.append("%%GREEN%%MOVE +%i%% %%ENDCOLOR%%"%int(value*100.0))
                elif value != round(value):
                    if value > 0:
                        stext.append("%%GREEN%%%s %i%% %%ENDCOLOR%%"%(name.upper(),int(value*100.0)))
                    else:
                        stext.append("%%RED%%%s %i%% %%ENDCOLOR%%"%(name.upper(),int(value*100.0)))
                else:
                    if value > 0:
                        stext.append("%%GREEN%%%s %i %%ENDCOLOR%%"%(name.upper(),int(value)))
                    else:
                        stext.append("%%RED%%%s %i %%ENDCOLOR%%"%(name.upper(),int(value)))
        
        if len(stext):
            itemSetPage += "\t*Stats:* %s\n\n"%', '.join(stext)
        else:
            itemSetPage += "\t*Stats:* None\n\n"
        itemSetPage += "---++ Item Contributions\n\n%s\n"%'\n'.join("\t* %s: %s"%(con,', '.join("[[Item%s][%s]]"%(GetTWikiName(itemname),itemname) for itemname in items)) for con,items in contributions.iteritems())
        
        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAME,"w")
        f.write(itemSetPage)
        f.close()
    
    f = file("./distrib/twiki/data/MoMWorld/ItemSetIndex.txt","w")
    f.write(itemSetTopPage)
    f.close()


