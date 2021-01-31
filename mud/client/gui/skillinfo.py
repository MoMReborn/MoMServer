# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


class SkillInfo:
    def __init__(self,name,passive,icon=""):
        self.name = name
        self.passive = passive
        self.icon = icon



SKILLINFOS = {}

SKILLINFOS['1HSLASH'] = SkillInfo('One Hand Slash',True)
SKILLINFOS['1HCLEAVE'] = SkillInfo('One Hand Cleave',True)
SKILLINFOS['1HIMPACT'] = SkillInfo('One Hand Impact',True)
SKILLINFOS['1HPIERCE'] = SkillInfo('One Hand Pierce',True)
SKILLINFOS['2HSLASH'] = SkillInfo('Two Hand Slash',True)
SKILLINFOS['2HCLEAVE'] = SkillInfo('Two Hand Cleave',True)
SKILLINFOS['2HIMPACT'] = SkillInfo('Two Hand Impact',True)
SKILLINFOS['2HPIERCE'] = SkillInfo('Two Hand Pierce',True)

#fix me this should be coming from world server!
SKILLINFOS['Rage'] = SkillInfo('Rage',False,"command")
SKILLINFOS['Whirling Fury'] = SkillInfo('Whirling Fury',False,"polymorph")
SKILLINFOS['Head Butt'] = SkillInfo('Head Butt',False,"SPELLICON_1_14")

SKILLINFOS['Camouflage'] = SkillInfo('Camouflage',False,"stealthupgrade")
SKILLINFOS['Death Spin'] = SkillInfo('Death Spin',False,"command")

SKILLINFOS['Invigorate'] = SkillInfo('Invigorate',False,"regenerateupgrade")
SKILLINFOS['Aggression'] = SkillInfo('Aggression',False,"command")
SKILLINFOS['Volitation'] = SkillInfo('Volitation',False,"teleportupgrade")
SKILLINFOS['Stone Skin'] = SkillInfo('Stone Skin',False,"stealthupgrade")
SKILLINFOS['Fury Fists'] = SkillInfo('Fury Fists',False,"moleculardeconstruction")
SKILLINFOS['Feign Death'] = SkillInfo('Feign Death',False,"strengthisweakness")
SKILLINFOS['Flying Tiger'] = SkillInfo('Flying Tiger',False,"SPELLICON_5_0")

SKILLINFOS['Awe'] = SkillInfo('Awe',False,"SPELLICON_3_6")

SKILLINFOS['Adrenaline'] = SkillInfo('Adrenaline',False,"SPELLICON_1_7")
SKILLINFOS['Defensive Stance'] = SkillInfo('Defensive Stance',False,"SPELLICON_3_18")
SKILLINFOS['Rescue'] = SkillInfo('Rescue',False,"SPELLICON_2_33")
SKILLINFOS['Evade'] = SkillInfo('Evade',False,"SPELLICON_2_33")

SKILLINFOS['Death Touch'] = SkillInfo('Death Touch',False,"SPELLICON_2_11")
SKILLINFOS['Merciless Strike'] = SkillInfo('Merciless Strike',False,"SPELLICON_2_6")
SKILLINFOS['Backstab'] = SkillInfo('Backstab',False,"SPELLICON_2_7")
SKILLINFOS['Sneak'] = SkillInfo('Sneak',False,"SPELLICON_1_18")
SKILLINFOS['Sprint'] = SkillInfo('Sprint',False,"SPELLICON_1_4")
SKILLINFOS['Assess'] = SkillInfo('Assess',False,"SPELLICON_3_34")

SKILLINFOS['Skullduggery'] = SkillInfo('Skullduggery',False,"SPELLICON_3_1")
SKILLINFOS['Shield Bash'] = SkillInfo('Shield Bash',False,"SPELLICON_1_7")

SKILLINFOS['Turn Undead'] = SkillInfo('Turn Undead',False,"SPELLICON_4_1")

SKILLINFOS['Lay on Hands'] = SkillInfo('Lay on Hands',False,"SPELLICON_2_1")
SKILLINFOS['Disarm'] = SkillInfo('Disarm',False,"SPELLICON_1_3")
SKILLINFOS['Pick Pocket'] = SkillInfo('Pick Pocket',False,"SPELLICON_4_18")

SKILLINFOS['Combat Casting'] = SkillInfo('Combat Casting',False,"SPELLICON_1_6")

SKILLINFOS['Kick'] = SkillInfo('Kick',False,"enhancedmovementupgrade")

SKILLINFOS['Cripple'] = SkillInfo('Cripple',False,"SPELLICON_5_3")

SKILLINFOS['Bloodletting'] = SkillInfo('Bloodletting',False,"restoration")
SKILLINFOS['Khurage'] = SkillInfo('Khurage',False,"polymorph")
SKILLINFOS['Champion of Light'] = SkillInfo('Champion of Light',False,"standarddefenceupgrade")
SKILLINFOS['Knight of Chaos'] = SkillInfo('Knight of Chaos',False,"stealthupgrade")
SKILLINFOS['BlightBane Strike'] = SkillInfo('BlightBane Strike',False,"SPELLICON_1_25")
SKILLINFOS['Rook'] = SkillInfo('Rook',False,"SPELLICON_1_29")
SKILLINFOS['Apparition'] = SkillInfo('Apparition',False,"SPELLICON_2_19")
SKILLINFOS['Mystic Might'] = SkillInfo('Mystic Might',False,"SPELLICON_4_25")
SKILLINFOS['Sorrow Song'] = SkillInfo('Sorrow Song',False,"SPELLICON_4_35")
SKILLINFOS['Des'] = SkillInfo('Des',False,"desicon")
SKILLINFOS['Fal'] = SkillInfo('Fal',False,"falicon")
SKILLINFOS['Koh'] = SkillInfo('Koh',False,"kohicon")
SKILLINFOS['Sur'] = SkillInfo('Sur',False,"suricon")
SKILLINFOS['Sacred Stone'] = SkillInfo('Sacred Stone',False,"SPELLICON_5_11")
SKILLINFOS['Power Strike'] = SkillInfo('Power Strike',False,"SPELLICON_1_7")
SKILLINFOS['Call of Wild'] = SkillInfo('Call of Wild',False,"SPELLICON_3_0")
SKILLINFOS['Shadow Fist'] = SkillInfo('Shadow Fist',False,"stealthupgrade")
SKILLINFOS['Lethal Blow'] = SkillInfo('Lethal Blow',False,"polymorph")
SKILLINFOS['Spinning Blades'] = SkillInfo('Spinning Blades',False,"SPELLICON_6_3")

#new expansion skills
SKILLINFOS['Waylay'] = SkillInfo('Waylay',False,"SPELLICON_1_5") #rogue
SKILLINFOS['Endurance'] = SkillInfo('Endurance',False,"SPELLICON_1_6") #combatant
SKILLINFOS['Dispersion'] = SkillInfo('Dispersion',False,"SPELLICON_5_22") #mage
SKILLINFOS['Sanctify'] = SkillInfo('Sanctify',False,"SPELLICON_3_24") #priest

SKILLINFOS['Healing Hands']=SkillInfo('Healing Hands',False,"SPELLICON_1_0")


def GetSkillInfo(name,autocreate=True):
    skillInfo = SKILLINFOS.get(name)
    if not skillInfo and autocreate:
        skillInfo = SKILLINFOS[name] = SkillInfo(name,True)
    
    return skillInfo
