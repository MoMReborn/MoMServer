
from mud.world.advancement import *

#around 5300 points available

#basic stat advancement

p = AdvancementProto(name = "Enhance Strength",desc = "Increases strength by 2.",maxRank=10)
AdvancementStat(statname="str",value=2,advancementProto=p)

p = AdvancementProto(name = "Enhance Mind",desc = "Increases mind by 2.",maxRank=10)
AdvancementStat(statname="mnd",value=2,advancementProto=p)

p = AdvancementProto(name = "Enhance Agility",desc = "Increases agility by 2.",maxRank=10)
AdvancementStat(statname="agi",value=2,advancementProto=p)
 
p = AdvancementProto(name = "Enhance Body",desc = "Increases body by 2.",maxRank=10)
AdvancementStat(statname="bdy",value=2,advancementProto=p)

p = AdvancementProto(name = "Enhance Wisdom",desc = "Increases wisdom by 2.",maxRank=10)
AdvancementStat(statname="wis",value=2,advancementProto=p)

p = AdvancementProto(name = "Enhance Reflexes",desc = "Increases reflexes by 2.",maxRank=10)
AdvancementStat(statname="ref",value=2,advancementProto=p)

p = AdvancementProto(name = "Enhance Dexterity",desc = "Increases dexterity by 2.",maxRank=10)
AdvancementStat(statname="dex",value=2,advancementProto=p)

p = AdvancementProto(name = "Enhance Mysticism",desc = "Increases mysticism by 2.",maxRank=10)
AdvancementStat(statname="mys",value=2,advancementProto=p)


p = AdvancementProto(name = "Greater Strength",desc = "Increases strength by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="str",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Strength",rank=10,advancementProto=p)

p = AdvancementProto(name = "Greater Mind",desc = "Increases mind by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="mnd",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Mind",rank=10,advancementProto=p)

p = AdvancementProto(name = "Greater Agility",desc = "Increases agility by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="agi",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Agility",rank=10,advancementProto=p)
 
p = AdvancementProto(name = "Greater Body",desc = "Increases body by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="bdy",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Body",rank=10,advancementProto=p)

p = AdvancementProto(name = "Greater Wisdom",desc = "Increases wisdom by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="wis",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Wisdom",rank=10,advancementProto=p)

p = AdvancementProto(name = "Greater Reflexes",desc = "Increases reflexes by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="ref",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Reflexes",rank=10,advancementProto=p)

p = AdvancementProto(name = "Greater Dexterity",desc = "Increases dexterity by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="dex",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Dexterity",rank=10,advancementProto=p)

p = AdvancementProto(name = "Greater Mysticism",desc = "Increases mysticism by 5.",maxRank=10,cost=15,level=20)
AdvancementStat(statname="mys",value=5,advancementProto=p)
AdvancementRequirement(require="Enhance Mysticism",rank=10,advancementProto=p)

p = AdvancementProto(name = "Toughness",desc = "Increases Health by 10.",maxRank=5,cost=2)
AdvancementStat(statname="maxHealth",value=10,advancementProto=p)

p = AdvancementProto(name = "Vitality",desc = "Increases Health by 100.",maxRank=5,cost=40,level=25)
AdvancementStat(statname="maxHealth",value=100,advancementProto=p)
AdvancementRequirement(require="Toughness",rank=5,advancementProto=p)


#HEALTH REGEN
p = AdvancementProto(name = "Rejuvenation",desc = "Increase health regeneration by 5%.",maxRank=1,cost=36,level=20)
AdvancementStat(statname="regenHealthScalar",value=.05,advancementProto=p)

p = AdvancementProto(name = "Renewal",desc = "Increase health regeneration by 10%.",maxRank=1,cost=125,level=50)
AdvancementStat(statname="regenHealthScalar",value=.1,advancementProto=p)
AdvancementRequirement(require="Rejuvenation",advancementProto=p)
AdvancementExclusion(exclude="Rejuvenation",advancementProto=p)

p = AdvancementProto(name = "Regeneration",desc = "Increase health regeneration by 15%.",maxRank=1,cost=250,level=75)
AdvancementStat(statname="regenHealthScalar",value=.15,advancementProto=p)
AdvancementRequirement(require="Renewal",advancementProto=p)
AdvancementExclusion(exclude="Renewal",advancementProto=p)
AdvancementExclusion(exclude="Rejuvenation",advancementProto=p)


#STAMINA REGEN
p = AdvancementProto(name = "Continuance",desc = "Increase stamina regeneration by 20%.",maxRank=1,cost=36,level=20)
AdvancementStat(statname="regenStaminaScalar",value=.2,advancementProto=p)

p = AdvancementProto(name = "Stability",desc = "Increase stamina regeneration by 40%.",maxRank=1,cost=125,level=50)
AdvancementStat(statname="regenStaminaScalar",value=.4,advancementProto=p)
AdvancementRequirement(require="Continuance",advancementProto=p)
AdvancementExclusion(exclude="Continuance",advancementProto=p)

p = AdvancementProto(name = "Persistence",desc = "Increase stamina regeneration by 60%.",maxRank=1,cost=250,level=75)
AdvancementStat(statname="regenStaminaScalar",value=.6,advancementProto=p)
AdvancementRequirement(require="Stability",advancementProto=p)
AdvancementExclusion(exclude="Stability",advancementProto=p)
AdvancementExclusion(exclude="Continuance",advancementProto=p)


#MAX STAMINA
p = AdvancementProto(name = "Improved Stamina",desc = "Increase stamina reserves by 25%.",maxRank=1,cost=30,level=20)
AdvancementStat(statname="maxStaminaScalar",value=.25,advancementProto=p)

p = AdvancementProto(name = "Greater Stamina",desc = "Increase stamina reserves by 50%.",maxRank=1,cost=200,level=45)
AdvancementStat(statname="maxStaminaScalar",value=.5,advancementProto=p)
AdvancementRequirement(require="Improved Stamina",advancementProto=p)
AdvancementExclusion(exclude="Improved Stamina",advancementProto=p)

p = AdvancementProto(name = "Massive Stamina",desc = "Increase stamina reserves by 100%.",maxRank=1,cost=350,level=75)
AdvancementStat(statname="maxStaminaScalar",value=1.0,advancementProto=p)
AdvancementRequirement(require="Greater Stamina",advancementProto=p)
AdvancementExclusion(exclude="Improved Stamina",advancementProto=p)
AdvancementExclusion(exclude="Greater Stamina",advancementProto=p)



#MAX HEALTH
#11/07/2007 -- Changed descriptions to match code effects. Original code commented out so we know where it stood originally.
'''p = AdvancementProto(name = "Resolution",desc = "Increase health reserves by 10%.",maxRank=1,cost=30,level=20)
AdvancementStat(statname="maxHealthScalar",value=.05,advancementProto=p)

p = AdvancementProto(name = "Fortitude",desc = "Increase health reserves by 15%.",maxRank=1,cost=200,level=45)
AdvancementStat(statname="maxHealthScalar",value=.1,advancementProto=p)
AdvancementRequirement(require="Resolution",advancementProto=p)
AdvancementExclusion(exclude="Resolution",advancementProto=p)

p = AdvancementProto(name = "Perseverance",desc = "Increase health reserves by 25%.",maxRank=1,cost=350,level=75)
AdvancementStat(statname="maxHealthScalar",value=.15,advancementProto=p)
AdvancementRequirement(require="Fortitude",advancementProto=p)
AdvancementExclusion(exclude="Resolution",advancementProto=p)
AdvancementExclusion(exclude="Fortitude",advancementProto=p)'''

p = AdvancementProto(name = "Resolution",desc = "Increase health reserves by 5%.",maxRank=1,cost=30,level=20)
AdvancementStat(statname="maxHealthScalar",value=.05,advancementProto=p)

p = AdvancementProto(name = "Fortitude",desc = "Increase health reserves by 10%.",maxRank=1,cost=200,level=45)
AdvancementStat(statname="maxHealthScalar",value=.1,advancementProto=p)
AdvancementRequirement(require="Resolution",advancementProto=p)
AdvancementExclusion(exclude="Resolution",advancementProto=p)

p = AdvancementProto(name = "Perseverance",desc = "Increase health reserves by 15%.",maxRank=1,cost=350,level=75)
AdvancementStat(statname="maxHealthScalar",value=.15,advancementProto=p)
AdvancementRequirement(require="Fortitude",advancementProto=p)
AdvancementExclusion(exclude="Resolution",advancementProto=p)
AdvancementExclusion(exclude="Fortitude",advancementProto=p)

ALLCLASSES = ["Necromancer","Revealer","Wizard","Cleric","Druid","Tempest","Shaman","Monk","Paladin","Barbarian","Ranger","Bard","Assassin","Doom Knight","Thief","Warrior"]
PURECASTERS = ["Necromancer","Revealer","Wizard","Cleric","Druid","Tempest","Shaman"]
PURECOMBAT = ["Monk","Paladin","Barbarian","Ranger","Warrior","Doom Knight"]
PUREROGUE = ["Assassin","Thief"]

#11/07/2007 -- Changed descriptions to match code effects. Original code commented out so we know where it stood originally.
'''p = AdvancementProto(name = "Combat Celerity",desc = "Increase attack speed by 5%.",maxRank=1,cost=35,level=20)
AdvancementStat(statname="innateHaste",value=.02,advancementProto=p)
for cl in ALLCLASSES:
    if cl not in PURECASTERS:
        AdvancementClass(classname=cl,level=1,advancementProto=p)

p = AdvancementProto(name = "Combat Alacrity",desc = "Increase attack speed by 15%.",maxRank=1,cost=260,level=40)
AdvancementStat(statname="innateHaste",value=.03,advancementProto=p)
for cl in ALLCLASSES:
    if cl not in PURECASTERS:
        AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Celerity",advancementProto=p)
AdvancementExclusion(exclude="Combat Celerity",advancementProto=p)

p = AdvancementProto(name = "Combat Rapidity",desc = "Increase attack speed by 25%.",maxRank=1,cost=450,level=80)
AdvancementStat(statname="innateHaste",value=.04,advancementProto=p)
for cl in ALLCLASSES:
    if cl not in PURECASTERS:
        AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Alacrity",advancementProto=p)
AdvancementExclusion(exclude="Combat Alacrity",advancementProto=p)
AdvancementExclusion(exclude="Combat Celerity",advancementProto=p)'''

p = AdvancementProto(name = "Combat Celerity",desc = "Increase attack speed by 2%.",maxRank=1,cost=35,level=20)
AdvancementStat(statname="innateHaste",value=.02,advancementProto=p)
for cl in ALLCLASSES:
    if cl not in PURECASTERS:
        AdvancementClass(classname=cl,level=1,advancementProto=p)

p = AdvancementProto(name = "Combat Alacrity",desc = "Increase attack speed by 3%.",maxRank=1,cost=260,level=40)
AdvancementStat(statname="innateHaste",value=.03,advancementProto=p)
for cl in ALLCLASSES:
    if cl not in PURECASTERS:
        AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Celerity",advancementProto=p)
AdvancementExclusion(exclude="Combat Celerity",advancementProto=p)

p = AdvancementProto(name = "Combat Rapidity",desc = "Increase attack speed by 4%.",maxRank=1,cost=450,level=80)
AdvancementStat(statname="innateHaste",value=.04,advancementProto=p)
for cl in ALLCLASSES:
    if cl not in PURECASTERS:
        AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Alacrity",advancementProto=p)
AdvancementExclusion(exclude="Combat Alacrity",advancementProto=p)
AdvancementExclusion(exclude="Combat Celerity",advancementProto=p)

#criticals
p = AdvancementProto(name = "Combat Brutality",desc = "Increase criticals by 2%.",maxRank=1,cost=30,level=24)
AdvancementStat(statname="critical",value=.02,advancementProto=p)
for cl in PURECOMBAT:
    AdvancementClass(classname=cl,level=1,advancementProto=p)

#11/07/2007 -- Changed descriptions to match code effects. Original code commented out so we know where it stood originally.
'''p = AdvancementProto(name = "Combat Ferocity",desc = "Increase criticals by 4%.",maxRank=1,cost=125,level=44)
AdvancementStat(statname="critical",value=.03,advancementProto=p)
for cl in PURECOMBAT:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Brutality",advancementProto=p)
AdvancementExclusion(exclude="Combat Brutality",advancementProto=p)

p = AdvancementProto(name = "Combat Savagery",desc = "Increase criticals by 6%.",maxRank=1,cost=500,level=84)
AdvancementStat(statname="critical",value=.04,advancementProto=p)
for cl in PURECOMBAT:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Ferocity",advancementProto=p)
AdvancementExclusion(exclude="Combat Brutality",advancementProto=p)
AdvancementExclusion(exclude="Combat Ferocity",advancementProto=p)'''

p = AdvancementProto(name = "Combat Ferocity",desc = "Increase damage and chance of criticals by 3%.",maxRank=1,cost=125,level=44)
AdvancementStat(statname="critical",value=.03,advancementProto=p)
for cl in PURECOMBAT:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Brutality",advancementProto=p)
AdvancementExclusion(exclude="Combat Brutality",advancementProto=p)

p = AdvancementProto(name = "Combat Savagery",desc = "Increase damage and chance of criticals by 4%.",maxRank=1,cost=500,level=84)
AdvancementStat(statname="critical",value=.04,advancementProto=p)
for cl in PURECOMBAT:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Combat Ferocity",advancementProto=p)
AdvancementExclusion(exclude="Combat Brutality",advancementProto=p)
AdvancementExclusion(exclude="Combat Ferocity",advancementProto=p)

#(rogue) criticals
p = AdvancementProto(name = "Improved Criticals",desc = "Increase damage and chance of criticals by 2%.",maxRank=1,cost=25,level=15)
AdvancementStat(statname="critical",value=.02,advancementProto=p)
for cl in PUREROGUE:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
    

#11/07/2007 -- Changed descriptions to match code effects. Original code commented out so we know where it stood originally.
'''p = AdvancementProto(name = "Greater Criticals",desc = "Increase criticals by 4%.",maxRank=1,cost=160,level=40)
AdvancementStat(statname="critical",value=.03,advancementProto=p)
for cl in PUREROGUE:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Improved Criticals",advancementProto=p)
AdvancementExclusion(exclude="Improved Criticals",advancementProto=p)

p = AdvancementProto(name = "Assassination",desc = "Increase criticals by 6%.",maxRank=1,cost=250,level=75)
AdvancementStat(statname="critical",value=.04,advancementProto=p)
AdvancementClass(classname="Assassin",level=75,advancementProto=p)
AdvancementRequirement(require="Greater Criticals",advancementProto=p)
AdvancementExclusion(exclude="Improved Criticals",advancementProto=p)
AdvancementExclusion(exclude="Greater Criticals",advancementProto=p)'''

p = AdvancementProto(name = "Greater Criticals",desc = "Increase damage and chance of criticals by 3%.",maxRank=1,cost=160,level=40)
AdvancementStat(statname="critical",value=.03,advancementProto=p)
for cl in PUREROGUE:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Improved Criticals",advancementProto=p)
AdvancementExclusion(exclude="Improved Criticals",advancementProto=p)

p = AdvancementProto(name = "Assassination",desc = "Increase damage and chance of criticals by 4%.",maxRank=1,cost=250,level=75)
AdvancementStat(statname="critical",value=.04,advancementProto=p)
AdvancementClass(classname="Assassin",level=75,advancementProto=p)
AdvancementRequirement(require="Greater Criticals",advancementProto=p)
AdvancementExclusion(exclude="Improved Criticals",advancementProto=p)
AdvancementExclusion(exclude="Greater Criticals",advancementProto=p)

#CASTING HASTE
p = AdvancementProto(name = "Casting Proficiency",desc = "Decreases spell casting time by 5%.",maxRank=1,cost=28,level=25)
AdvancementStat(statname="castHaste",value=.05,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)

#11/07/2007 -- Changed descriptions to match code effects. Original code commented out so we know where it stood originally.
'''p = AdvancementProto(name = "Casting Expertise",desc = "Decreases spell casting time by 15%.",maxRank=1,cost=100,level=50)
AdvancementStat(statname="castHaste",value=.1,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Casting Proficiency",advancementProto=p)
AdvancementExclusion(exclude="Casting Proficiency",advancementProto=p)

p = AdvancementProto(name = "Casting Mastery",desc = "Decreases spell casting time by 20%.",maxRank=1,cost=200,level=75)
AdvancementStat(statname="castHaste",value=.15,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Casting Expertise",advancementProto=p)
AdvancementExclusion(exclude="Casting Proficiency",advancementProto=p)
AdvancementExclusion(exclude="Casting Expertise",advancementProto=p)'''

p = AdvancementProto(name = "Casting Expertise",desc = "Decreases spell casting time by 10%.",maxRank=1,cost=100,level=50)
AdvancementStat(statname="castHaste",value=.1,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Casting Proficiency",advancementProto=p)
AdvancementExclusion(exclude="Casting Proficiency",advancementProto=p)

p = AdvancementProto(name = "Casting Mastery",desc = "Decreases spell casting time by 15%.",maxRank=1,cost=200,level=75)
AdvancementStat(statname="castHaste",value=.15,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Casting Expertise",advancementProto=p)
AdvancementExclusion(exclude="Casting Proficiency",advancementProto=p)
AdvancementExclusion(exclude="Casting Expertise",advancementProto=p)


#MANA REGEN
p = AdvancementProto(name = "Mana Gathering",desc = "Increase mana regeneration by 20%.",maxRank=1,cost=45,level=20)
AdvancementStat(statname="regenManaScalar",value=.2,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)

p = AdvancementProto(name = "Mana Focusing",desc = "Increase mana regeneration by 40%.",maxRank=1,cost=200,level=40)
AdvancementStat(statname="regenManaScalar",value=.4,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Mana Gathering",advancementProto=p)
AdvancementExclusion(exclude="Mana Gathering",advancementProto=p)


p = AdvancementProto(name = "Mana Magnetism",desc = "Increase mana regeneration by 60%.",maxRank=1,cost=450,level=60)
AdvancementStat(statname="regenManaScalar",value=.6,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Mana Focusing",advancementProto=p)
AdvancementExclusion(exclude="Mana Gathering",advancementProto=p)
AdvancementExclusion(exclude="Mana Focusing",advancementProto=p)

p = AdvancementProto(name = "Mana Supremacy",desc = "Increase mana regeneration by 80%.",maxRank=1,cost=600,level=80)
AdvancementStat(statname="regenManaScalar",value=.8,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Mana Magnetism",advancementProto=p)
AdvancementExclusion(exclude="Mana Gathering",advancementProto=p)
AdvancementExclusion(exclude="Mana Focusing",advancementProto=p)
AdvancementExclusion(exclude="Mana Magnetism",advancementProto=p)


#MAX MANA
p = AdvancementProto(name = "Mana Injection",desc = "Increase mana reserves by 10%.",maxRank=1,cost=40,level=20)
AdvancementStat(statname="maxManaScalar",value=.1,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
    
p = AdvancementProto(name = "Mana Infusion",desc = "Increase mana reserves by 20%.",maxRank=1,cost=200,level=45)
AdvancementStat(statname="maxManaScalar",value=.2,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Mana Injection",advancementProto=p)
AdvancementExclusion(exclude="Mana Injection",advancementProto=p)

p = AdvancementProto(name = "Mana Saturation",desc = "Increase mana reserves by 40%.",maxRank=1,cost=350,level=75)
AdvancementStat(statname="maxManaScalar",value=.4,advancementProto=p)
for cl in PURECASTERS:
    AdvancementClass(classname=cl,level=1,advancementProto=p)
AdvancementRequirement(require="Mana Infusion",advancementProto=p)
AdvancementExclusion(exclude="Mana Injection",advancementProto=p)
AdvancementExclusion(exclude="Mana Infusion",advancementProto=p)


#XP SCALAR
p = AdvancementProto(name = "Savvy",desc = "Increase experience gains by 10%.",maxRank=1,cost=12,level=10)
AdvancementStat(statname="xpScalar",value=.1,advancementProto=p)

p = AdvancementProto(name = "Expertise",desc = "Increase experience gains by 20%.",maxRank=1,cost=100,level=25)
AdvancementStat(statname="xpScalar",value=.2,advancementProto=p)
AdvancementRequirement(require="Savvy",advancementProto=p)
AdvancementExclusion(exclude="Savvy",advancementProto=p)

p = AdvancementProto(name = "Mastery",desc = "Increase experience gains by 30%.",maxRank=1,cost=250,level=50)
AdvancementStat(statname="xpScalar",value=.3,advancementProto=p)
AdvancementRequirement(require="Expertise",advancementProto=p)
AdvancementExclusion(exclude="Savvy",advancementProto=p)
AdvancementExclusion(exclude="Expertise",advancementProto=p)

p = AdvancementProto(name = "Supremacy",desc = "Increase experience gains by 40%.",maxRank=1,cost=500,level=75)
AdvancementStat(statname="xpScalar",value=.4,advancementProto=p)
AdvancementRequirement(require="Mastery",advancementProto=p)
AdvancementExclusion(exclude="Savvy",advancementProto=p)
AdvancementExclusion(exclude="Expertise",advancementProto=p)
AdvancementExclusion(exclude="Mastery",advancementProto=p)


#MOVEMENT

p = AdvancementProto(name = "Jaunting",desc = "Increase movement speed by 10%.",maxRank=1,cost=20,level=8)
AdvancementStat(statname="move",value=.1,advancementProto=p)

p = AdvancementProto(name = "Striding",desc = "Increase movement speed by 15%.",maxRank=1,cost=40,level=20)
AdvancementStat(statname="move",value=.15,advancementProto=p)
AdvancementRequirement(require="Jaunting",advancementProto=p)
AdvancementExclusion(exclude="Jaunting",advancementProto=p)


p = AdvancementProto(name = "Traveling",desc = "Increase movement speed by 20%.",maxRank=1,cost=80,level=40)
AdvancementStat(statname="move",value=.20,advancementProto=p)
AdvancementRequirement(require="Striding",advancementProto=p)
AdvancementExclusion(exclude="Jaunting",advancementProto=p)
AdvancementExclusion(exclude="Striding",advancementProto=p)

p = AdvancementProto(name = "Fleet Feet",desc = "Increase movement speed by 25%.",maxRank=1,cost=200,level=65)
AdvancementStat(statname="move",value=.25,advancementProto=p)
AdvancementRequirement(require="Traveling",advancementProto=p)
AdvancementExclusion(exclude="Jaunting",advancementProto=p)
AdvancementExclusion(exclude="Striding",advancementProto=p)
AdvancementExclusion(exclude="Traveling",advancementProto=p)




