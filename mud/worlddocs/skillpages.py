# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud.world.defines import *
from mud.world.skill import ClassSkill,ClassSkillRaceRequirement
from utils import *


# done are /genesis/skill/... barbarian.py,bard.py,cleric.py,combatant.py
# done also those mentioned in the 'GettingStarted.pdf'
SKILLDESCS = {
"1H Slash":"The character's ability to wield a 1 handed slash weapon. Examples include: Falchion, Kama, Kukri, Longsword, Short Sword, and Sickle.<br>A higher skill will allow a character to hit his foes harder and more often.",
"1H Impact":"The character's ability to wield a 1 handed impact weapon. Examples include: Club, Flail, Hooked Hammer, Light Flail, Light Mace, and Spiked Club.<br>A higher skill will allow a character to hit his foes harder and more often.",
"1H Cleave":"The character's ability to wield a 1 handed cleaving weapon. Examples include: Handaxe.<br>A higher skill will allow a character to hit his foes harder and more often.",
"1H Pierce":"The character's ability to wield a 1 handed piercing weapon. Examples include: Dagger, Halfspear, Light Pick, Pick, Punching Dagger, Ranseur, Rapier, Siangham, and Trident.<br>A higher skill will allow a character to hit his foes harder and more often.",
"2H Slash":"The character's ability to wield a 2 handed slash weapon. Examples include: Greatsword, Scythe.<br>A higher skill will allow a character to hit his foes harder and more often.",
"2H Impact":"The character's ability to wield a 2 handed impact weapon. Examples include: Heavy Flail, Heavy Mace, Heavy Warhammer, Morningstar, and Quarterstaff.<br>A higher skill will allow a character to hit his foes harder and more often.",
"2H Cleave":"The character's ability to wield a 2 handed cleaving weapon. Examples include: Battleaxe, Doubleaxe, Halberd, Glaive, Greataxe, Guisarme, and Waraxe.<br>A higher skill will allow a character to hit his foes harder and more often.",
"2H Pierce":"The character's ability to wield a 2 handed piercing weapon. Examples include: Heavy Pick, Javelin, Longspear, Shortspear.<br>A higher skill will allow a character to hit his foes harder and more often.",
"Acrobatics":"The character's ability to fall without receiving damage.  The higher this skill, the less damage a character will take from falling.",
"Archery":"The character's ability to use and craft ranged weapons.",
"Armor Craft":"Allows you to craft your own armor.<br>To craft, either put the required ingredients into the crafting window and hit the craft button, or have the ingredients available in your inventory and type '/craft {recipename}' into your chatbox.",
"Assess":"Try to determine what valuables the target has in its inventory.",
"Block":"The character's ability to block a physical attack with weapons or even bare hands.",
"Combat Casting":"The character's ability to continue casting while in combat mode, this is an essential skill for all spell casters.",
"Disarm":"Attempt to disarm your foe.<br>Note: other players can't be disarmed, the disarmed weapon lands in the backpack of your enemy.",
"Double Attack":"Perform two attacks in quick succession.",
"Dual Wield":"Allows you to wield two 1H weapons, one in each hand.",
"Fists":"The character's ability to fight without the use of weaponry in their primary and/or offhand weapon slots.",
"Heavy Armor":"Allows you to wear heavy armor.",
"Hold Breath":"The character's ability to stay underwater. The higher the skill, the longer the character can stay underwater without coming up for air. There is a breath bar that opens in the Character Window replacing the stamina bar when the player is underwater, which displays how much air is remaining per character. Don't let your air run out!",
"Inflict Critical":"Get a chance to critically wound your opponent.",
"Kick":"Kick your foe.",
"Light Armor":"The character's ability to wear light armor. Examples include: Leather, Ornate Leather, Padded, and Woven.",
"Medium Armor":"The character's ability to wear medium armor. Examples include: Chainmail, Brass.",
"Power Wield":"Allows you to dual wield 2H weapons.",
"Rage":"",    # this is still missing an implementation
"Repairing":"The character's ability to repair equipped items that are breaking or broken. A higher repair skill allows to repair higher quality weapons. All repairs cost money. The amount can be determined by single-clicking on a repair button, double click will issue the repair.",
"Rescue":"Taunt an opponent to attack you instead of a fellow party or alliance member.<br>Note: if the ally keeps attacking, the enemy might reconsider and get back to attacking him again.",
"Riposte":"Get a chance to launch a counterattack when attacked.",
"Sacred Stone":"Protect your alliance from physical and magical attacks and regenerate mana.",
"Shields":"Allows you to use a shield and block attacks with it.",
"Singing":"Sing songs to strengthen your allies and hurt your foes. As it doesn't take as much concentration as casting a spell, singing doesn't hinder combat effectiveness.",
"Sorrow Song":"Begin a song of sorrow, draining away your foes motivation to fight.",
"Sprint":"Useful skill for a quick speedburst but not so much for traveling. Unlike other speed buffs, this one will even work indoors.",
"Swimming":"The character's ability to swim. The higher the skill, the faster the character will move while swimming.",
"Tactics Defense":"Improve your ability to avoid damage in combat.",
"Tactics Offense":"Improve your ability to inflict damage in combat.",
"Tracking":"The character's ability to track. The higher the skill, the further the range the character will be able to track monsters, players, and NPC's.",
"Triple Attack":"Perform three attacks in a blink of an eye.",
"Turn Undead":"Turn the undead, make them lose all motivation to haunt you.",
"Weapon Craft":"Allows you to craft your own weapons.<br>To craft, either put the required ingredients into the crafting window and hit the craft button, or have the ingredients available in your inventory and type '/craft {recipename}' into your chatbox.",
"Whirling Fury":"Whirl into a fury, attacking with increased speed."
}


def CreateSkillDesc(skill,classSkills):
    # classSkills = [[cname],{levelGained:[cname]},{levelCapped:[cname]},{minReuseTime:[cname]},{maxReuseTime:[cname]},{maxValue:[cname]},{trained:[cname]},{raceRequirements:[cname]},{spellProtoName:[cname]}]
    # maybe color code values so they don't vanish in class lists where we get one
    skillPage = "---+ %s\n\n"%skill
    
    if skill in SKILLDESCS:
        skillPage += "%s\n\n"%SKILLDESCS[skill]
    
    if len(classSkills[0]):
        skillPage += "*Available to:* %s<br>"%', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classSkills[0])
    
    if len(classSkills[7]):
        for racenames,classnames in classSkills[7].iteritems():
            skillPage += "%s require one of the following races for this skill: %s<br>"%(', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames),', '.join(racenames))
    
    if len(classSkills[1]) == 1:
        skillPage += "<br> *Level Gained:* %i<br>"%classSkills[1].keys()[0]
    else:
        skillPage += "<br> *Level Gained:* %s<br>"%', '.join('%i (%s)'%(levelGained,', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames)) for levelGained,classnames in classSkills[1].iteritems())
    
    if len(classSkills[2]) == 1:
        skillPage += " *Level Capped:* %i<br>"%classSkills[2].keys()[0]
    else:
        skillPage += " *Level Capped:* %s<br>"%', '.join('%i (%s)'%(levelCapped,', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames)) for levelCapped,classnames in classSkills[2].iteritems())
    
    if len(classSkills[5]) == 1:
        skillPage += " *Max Value:* %i<br>"%classSkills[5].keys()[0]
    else:
        skillPage += " *Max Value:* %s<br>"%', '.join('%i (%s)'%(maxValue,', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames)) for maxValue,classnames in classSkills[5].iteritems())
    
    if len(classSkills[4]) == 1:
        skillPage += " *Max Reuse Time:* %i seconds<br>"%int(float(classSkills[4].keys()[0])/float(durSecond))
    else:
        skillPage += " *Max Reuse Time:* %s<br>"%', '.join('%i seconds (%s)'%(int(float(maxReuseTime)/float(durSecond)),', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames)) for maxReuseTime,classnames in classSkills[4].iteritems())
    
    if len(classSkills[3]) == 1:
        skillPage += " *Min Reuse Time:* %i seconds<br>"%int(float(classSkills[3].keys()[0])/float(durSecond))
    else:
        skillPage += " *Min Reuse Time:* %s<br>"%', '.join('%i seconds (%s)'%(int(float(minReuseTime)/float(durSecond)),', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames)) for minReuseTime,classnames in classSkills[3].iteritems())
    
    if len(classSkills[6]) == 1:
        skillPage += " *Trained:* %s\n\n"%classSkills[6].keys()[0]
    else:
        skillPage += " *Trained:* %s\n\n"%', '.join('%s (%s)'%(trained,', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames)) for trained,classnames in classSkills[6].iteritems())
    
    if len(classSkills[8]) == 1:
        sname = classSkills[8].keys()[0]
        skillPage += " *Skill Spell:* [[Spell%s][%s]]\n\n"%(GetTWikiName(sname),sname)
    elif len(classSkills[8]):
        skillPage += " *Skill Spell:* %s\n\n"%', '.join('[[Spell%s][%s]] (%s)'%(GetTWikiName(sname),sname,', '.join('[[Class%s][%s]]'%(GetTWikiName(cname),cname) for cname in classnames)) for sname,classnames in classSkills[8].iteritems())
    
    f = file("./distrib/twiki/data/MoMWorld/Skill%s.txt"%GetTWikiName(skill),"w")
    f.write(skillPage)
    f.close()


def CreateSkillPages(classSkills):
    skillIndex = "---+ Skill Index\n\n"
    indexPage = "---+ Skill Spells\n\n"
    skillSpells = []
    for skill in sorted(classSkills.iterkeys()):
        skillIndex += "\t* [[Skill%s][%s]]\n"%(GetTWikiName(skill),skill)
        CreateSkillDesc(skill,classSkills[skill])
        for sname in classSkills[skill][8].keys():
            if sname not in skillSpells:
                skillSpells.append(sname)
                indexPage += "\t* [[Spell%s][%s]]\n"%(GetTWikiName(sname),sname)
    f = file("./distrib/twiki/data/MoMWorld/SpellSkillsIndex.txt","w")
    f.write(indexPage)
    f.close()
    f = file("./distrib/twiki/data/MoMWorld/SkillIndex.txt","w")
    f.write(skillIndex)
    f.close()
