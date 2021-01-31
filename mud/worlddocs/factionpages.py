# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

# Faction Pages

from mud.world.faction import Faction
from mud.world.defines import *
from utils import *

SPAWNFACTIONS = None
QUESTFACTIONS = None


def CreateFactionPages(spawnFactions, questFactions):
    
    global SPAWNFACTIONS
    global QUESTFACTIONS
    SPAWNFACTIONS = spawnFactions
    QUESTFACTIONS = questFactions
      
    factionTopPage = "---+ Index of all Factions\n\n"
    
    for faction in Faction.select(orderBy="name"):
        twikiFactionName = "Faction%s"%GetTWikiName(faction.name)
        factionTopPage += "\t* [[%s][%s]]\n"%(twikiFactionName,faction.name)
        
        factionPage = "---+ %s"%faction.name
        factionPage += GenFactionRelationshipsText(faction)
        factionPage += GenFactionSpawnsText(faction)
        factionPage += GenFactionQuestRewards(faction)
        factionPage += GenFactionQuestRequirements(faction)

        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%(twikiFactionName),"w")
        f.write(factionPage)
        f.close()    
    
    f = file("./distrib/twiki/data/MoMWorld/FactionIndex.txt","w")
    f.write(factionTopPage)
    f.close()
 
    
def GenFactionRelationshipsText(faction):
    
    factionText = "\n\n---++ Relations"

    factionText += "\n\n*Realm:* %s"%(RPG_REALM_TEXT[faction.realm])
        
    # Get relationships.
    friends  = list()
    undecided = list()
    enemies   = list()
    for fr in faction.relations:
        if RPG_FACTION_UNDECIDED < fr.relation:
            friends.append(fr.otherFaction.name)
        elif RPG_FACTION_UNDECIDED == fr.relation:
             undecided.append(fr.otherFaction.name)
        else:
             enemies.append(fr.otherFaction.name)
    
    # Print friends.
    factionText += "\n\n*Friends:* "
    if len(friends):
        factionText += ', '.join("[[Faction%s][%s]]"%(GetTWikiName(otherFaction),otherFaction) for otherFaction in sorted(friends))
    else:
        factionText += "None"  
    
    # Print undecided.    
    factionText += "\n\n*Undecided:* "
    if len(undecided):
        factionText += ', '.join("[[Faction%s][%s]]"%(GetTWikiName(otherFaction),otherFaction) for otherFaction in sorted(undecided))
    else:
        factionText += "None"  
        
    # Print enemies.
    factionText += "\n\n*Enemies:* "
    if len(enemies):
        factionText += ', '.join("[[Faction%s][%s]]"%(GetTWikiName(otherFaction),otherFaction) for otherFaction in sorted(enemies))
    else:
        factionText += "None"  
        
    return factionText


def GenFactionSpawnsText(faction):
    
    factionText = "\n\n---++ Spawns"
  
    factionText += "\n\n*Lowers:* "
    spawns = SPAWNFACTIONS[faction.name].lowers
    if len(spawns):
        factionText += ', '.join("[[Spawn%s][%s]]"%(GetTWikiName(spawn),spawn) for spawn in sorted(spawns))
    else:
        factionText += "None"  

    factionText += "\n\n*Raises:* "
    spawn = SPAWNFACTIONS[faction.name].raises
    if len(spawn):
        factionText += ', '.join("[[Spawn%s][%s]]"%(GetTWikiName(spawn),spawn) for spawn in sorted(spawn))
    else:
        factionText += "None"
        
    return factionText


def GenFactionQuestRewards(faction):
    
    factionText = "\n\n---++ Quest Rewards"
        
    factionText += "\n\n*Lowers:* "
    quests = QUESTFACTIONS[faction.name].lowers
    if len(quests):
        factionText += ', '.join("[[Quest%s][%s]]"%(GetTWikiName(quest),quest) for quest in sorted(quests))
    else:
        factionText += "None"  

    factionText += "\n\n*Raises:* "
    quests = QUESTFACTIONS[faction.name].raises
    if len(quests):
        factionText += ', '.join("[[Quest%s][%s]]"%(GetTWikiName(quest),quest) for quest in sorted(quests))
    else:
        factionText += "None"
        
    return factionText

def GenFactionQuestRequirements(faction):
    factionText = "\n\n---++ Quest Requires"
        
    factionText += "\n\n*Requires:* "
    quests = QUESTFACTIONS[faction.name].requires
    if len(quests):
        factionText += ', '.join("[[Quest%s][%s]]"%(GetTWikiName(quest),quest) for quest in sorted(quests))
    else:
        factionText += "None"  

    return factionText

    

    
    