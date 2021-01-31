# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#Quest Pages

from mud.world.spawn import Spawn
from mud.world.zone import Zone
from mud.world.dialog import Dialog
from mud.world.defines import *
from mud.world.core import GenMoneyText
from utils import *
from collections import defaultdict

QuestPage = """
---+ ^^QUESTNAME^^


---++ Spawns

^^SPAWNTEXT^^

---++ Rewards
^^REWARDTEXT^^

---++ Requirements
^^REQUIRETEXT^^

*Please note that results may reflect subquests contained inside this quest.*
"""

# from left to right: takes, checks, gives
QUESTITEMS = [{},{},{}]

class QuestFactionContainer:
    def __init__(self):
        self.lowers = set()
        self.raises = set()
        self.requires = set()
QUESTFACTIONS = defaultdict(QuestFactionContainer)


def GenSpawnText(quest,spawnQuests):
    spawns = spawnQuests.get(quest, [])
    
    if not len(spawns):
        return "*Environmental Trigger*"
    
    stext = "*Spawns:* %s"%', '.join('[[Spawn%s][%s]]'%(GetTWikiName(s.name),s.name) for s in spawns)
    return stext


def GenRewardText(quest):
    itext = ""
    
    # Generate Lists
    gitems = []
    money = 0L
    experience = []
    cmf = []
    classes = []
    skills = []
    teleportZone = None
    respawns = []
    triggers = []
    res = []
    for action in quest.actions:
        gitems.extend([item.itemProto for item in action.giveItems])
        money += action.giveTin
        if action.giveXP:
            experience.append(action.giveXP)
        cmf.extend(list(action.factions))
        if action.trainClass:
            classes.append(action.trainClass)
        skills.extend(list(action.trainSkills))
        if action.teleportZone:
            teleportZone = action.teleportZone
        if action.respawn and action.respawn not in respawns:
            respawns.append(action.respawn)
        if action.triggerSpawnGroup and action.triggerSpawnGroup not in triggers:
            triggers.append(action.triggerSpawnGroup)
        if action.resurrect and action.resurrectXP not in res:
            res.append(action.resurrectXP)
    
    # Items Given
    if len(gitems):
        itext += "<br> *Items Given:* "
        for item in gitems:
            itext+="[[Item%s][%s]], "%(GetTWikiName(item.name),item.name)
            try:
                QUESTITEMS[2][item].append(quest)
            except KeyError:
                QUESTITEMS[2][item] = [quest]
        itext = itext[:-2]
    
    # Money
    if money:
        itext += "<br> *Money Given:* %s"%GenMoneyText(money)
    
    # Experience
    if len(experience):
        itext += "<br> *Experience:* %s"%', '.join(map(str,experience))
    
    # Factions
    if len(cmf):
        itext += "<br> *Faction:* %s"%', '.join('[[Faction%s][%s]] (%i)'%(GetTWikiName(f.faction.name),f.faction.name,f.amount) for f in cmf)
        
        for f in cmf:
            questFaction = QUESTFACTIONS[f.faction.name]  
            if 0 < f.amount:
                questFaction.raises.add(quest.name)
            else:
                questFaction.lowers.add(quest.name)
            
    
    # Train in class
    if len(classes):
        itext += "<br> *Train Class:* %s"%', '.join('[[Class%s][%s]]'%(GetTWikiName(cl),cl) for cl in classes)
    
    # Train in skill
    if len(skills):
        itext += "<br> *Train Skill:* %s"%', '.join('[[Skill%s][%s]]'%(GetTWikiName(sk.skill),sk.skill) for sk in skills)
    
    # Teleport
    if teleportZone:
        z = Zone.byName(teleportZone)
        itext += "<br> *Teleport:* [[Zone%s][%s]]"%(GetTWikiName(z.niceName),z.niceName)
    
    """
    respawn = ForeignKey('Spawn',default=None)
    triggerSpawnGroup = StringCol(default="") #todo, move spawnpoints to database, somehow
    
    resurrect = BoolCol(default = False)
    resurrectXP = FloatCol(default = 0)
    """
    
    # Respawns
    if len(respawns):
        itext += "<br> *Respawn:* %s"%', '.join('[[Spawn%s][%s]]'%(GetTWikiName(s.name),s.name) for s in respawns)
    
    # Triggers
    if len(triggers):
        itext += "<br> *Trigger Spawn Group:* %s"%', '.join(triggers)
    
    # Resurrect
    if len(res):
        itext += "<br> *Resurrection:* %s"%', '.join('%i%%'%int(r*100.0) for r in res)
    
    return itext


def GenRequireText(quest):
    itext = ""
    
    # Generate Lists
    citems = []
    titems = []
    money = 0L
    minFactions = []
    maxFactions = []
    for action in quest.actions:
        titems.extend([item.itemProto for item in action.takeItems])
        citems.extend([item.itemProto for item in action.checkItems])
        money += action.takeTin
        minFactions.extend(action.checkMinFactions)
        maxFactions.extend(action.checkMaxFactions)
    
    # Items Checked
    if len(citems):
        itext += "<br> *Items Checked:* "
        for item in citems:
            itext += "[[Item%s][%s]], "%(GetTWikiName(item.name),item.name)
            try:
                if quest not in QUESTITEMS[1][item]:
                    QUESTITEMS[1][item].append(quest)
            except KeyError:
                QUESTITEMS[1][item] = [quest]
        itext = itext[:-2]
    
    # Items Taken
    if len(titems):
        itext += "<br> *Items Taken:* "
        for item in titems:
            itext += "[[Item%s][%s]], "%(GetTWikiName(item.name),item.name)
            try:
                if quest not in QUESTITEMS[0][item]:
                    QUESTITEMS[0][item].append(quest)
            except KeyError:
                    QUESTITEMS[0][item] = [quest]
        itext = itext[:-2]
    
    # Money
    if money:
        itext += "<br> *Required Money:* %s"%GenMoneyText(money)
    
    # Min Factions
    if len(minFactions):
        itext += "<br> *Minimum Faction:* %s"%', '.join('[[Faction%s][%s]] (%i)'%(GetTWikiName(f.faction.name),f.faction.name,f.amount) for f in minFactions)
        
        for f in minFactions:
            QUESTFACTIONS[f.faction.name].requires.add(quest.name)
    
    # Max Factions
    if len(maxFactions):
        itext += "<br> *Maximum Faction:* %s"%', '.join('[[Faction%s][%s]] (%i)'%(GetTWikiName(f.faction.name),f.faction.name,f.amount) for f in maxFactions)
        
        for f in maxFactions:
            QUESTFACTIONS[f.faction.name].requires.add(quest.name)
    
    return itext


def CreateQuestPages(spawnQuests):
    quests = [d for d in Dialog.select(orderBy = "name") if len(d.actions)]
    
    indexPage = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    indexPage += "---+ Quest Index\n\n"
    
    for q in quests:
        page = QuestPage
        
        TWIKINAME = "Quest"+GetTWikiName(q.name)
        indexPage+="\t* [[%s][%s]]\n"%(TWIKINAME,q.name)
        
        SPAWNTEXT = GenSpawnText(q,spawnQuests)
        
        REQUIRETEXT = GenRequireText(q)
        REWARDTEXT = GenRewardText(q)
        
        page=page.replace("^^QUESTNAME^^",q.name)
        page=page.replace("^^SPAWNTEXT^^",SPAWNTEXT)
        page=page.replace("^^REQUIRETEXT^^",REQUIRETEXT)
        page=page.replace("^^REWARDTEXT^^",REWARDTEXT)
        
        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAME,"w")
        f.write(page)
        f.close()
    
    f = file("./distrib/twiki/data/MoMWorld/QuestIndex.txt","w")
    f.write(indexPage)
    f.close()
    
    return QUESTITEMS, QUESTFACTIONS
        
    
    

 