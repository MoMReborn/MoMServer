# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#spells and procs

from mud.world.defines import *
from mud.world.spell import SpellProto
from utils import *
from collections import defaultdict

SpellPage = """
---+ ^^SPELLNAME^^
^^DESCTEXT^^

---++ Stats

^^STATTEXT^^

---++ Effects

^^EFFECTTEXT^^


"""

SPELLSUMMONITEMS = defaultdict(set)
SPELLCLASSES = defaultdict(list)
SpellIndexPages = {}
SpellIndexPages["SpellRComponentIndex"] = "---+ Spells with Component requirements\n\n"


def GenDescText(spell,spawnSpells,TWIKINAME):
    dtext = "---++ Description\n\n%s"%spell.desc
    if spell.desc:
        dtext += "<br>"
    
    # Classes
    classes = list(spell.classes)
    if len(classes):
        dtext += "<br> *Classes:* "
        for sc in classes:
            SPELLCLASSES[sc.classname].append((spell.name,sc.level))
            dtext += "[[Class%s][%s]] (%i), "%(GetTWikiName(sc.classname),sc.classname,sc.level)
        dtext = dtext[:-2]
    
    # Innate to spawns
    spawns = spawnSpells.get(spell.name, [])
    if len(spawns):
        dtext += "<br> *Spawn Ability:* %s"%', '.join('[[Spawn%s][%s]]'%(GetTWikiName(spname),spname) for spname in spawns)
    
    # Procs
    trigger = {
        RPG_ITEM_TRIGGER_WORN: 'Worn',
        RPG_ITEM_TRIGGER_MELEE: 'Melee',
        RPG_ITEM_TRIGGER_DAMAGED: 'Damaged',
        RPG_ITEM_TRIGGER_USE: 'Use',
        RPG_ITEM_TRIGGER_POISON: 'Poison'
    }
    
    ispells = list(spell.itemSpells)
    if len(ispells):
        dtext += "<br> *Item Procs:* %s"%', '.join('[[Item%s][%s]] (%s)'%(GetTWikiName(s.itemProto.name),s.itemProto.name,trigger[s.trigger]) for s in ispells)
    
    components = list(spell.componentsInternal)
    if len(components):
        dtext += "<br> *Components Needed:* %s"%', '.join('[[Item%s][%s (%i)]]'%(GetTWikiName(component.itemProto.name),component.itemProto.name,component.count) for component in components)
        SpellIndexPages["SpellRComponentIndex"] += "\t* [[%s][%s]]\n"%(TWIKINAME,spell.name)
    
    return dtext


def GenStatText(spell):
    stext = ""
    
    h = "No"
    if spell.spellType&RPG_SPELL_HARMFUL:
        h = "Yes"
    stext = "*Harmful:* %s *Target:* %s <br>"%(h,RPG_TARGET_TEXT[spell.target])
    
    casttime = int(float(spell.castTime)/float(durSecond))
    if casttime:
        casttime = "%i seconds"%casttime
    else:
        casttime = "Instant"
    
    recasttime = int(float(spell.recastTime)/float(durSecond))
    if recasttime:
        recasttime = "%i seconds"%recasttime
    else:
        recasttime = "Instant"
    
    duration = int(float(spell.duration)/float(durSecond))
    if duration:
        duration = "%i seconds"%duration
    else:
        duration = "Instant"
    
    stext += " *Cast Time:* %s *Recast Time:* %s *Cast Range:* %im<br>"%(casttime,recasttime,spell.castRange)
    
    stext += " *Duration:* %s <br>"%(duration)
    
    if spell.aoeRange:
        stext += " *AoE Range:* %im<br>"%(spell.aoeRange)
    
    if spell.manaCost:
        stext += " *Mana:* %i<br>"%(spell.manaCost)
    
    if spell.skillname:
        stext += " *Skill:* %s<br>"%(spell.skillname)
    
    if spell.projectile:
        stext += " *Projectile Speed:* %f<br>"%(spell.projectileSpeed)
    
    return stext


def GenEffectText(spell):
    etext = []
    
    stages = {
        RPG_EFFECT_STAGE_GLOBAL: " *Global Stats:* ",
        RPG_EFFECT_STAGE_BEGIN: " *Begin Stats:* ",
        RPG_EFFECT_STAGE_TICK: " *Tick Stats:* ",
        RPG_EFFECT_STAGE_END: " *End Stats:* "
    }
    
    for e in spell.effectProtos:
        etext.append("---++++ %s\n"%e.name)
        
        # Summoning (Pet)
        if e.summonPet:
            etext.append("<br> *Summon Pet:* [[Spawn%s][%s]]"%(GetTWikiName(e.summonPet.name),e.summonPet.name))
        
        # Summoning (Item)
        if e.summonItem:
            summonItem = e.summonItem
            SPELLSUMMONITEMS[summonItem].add(spell)
            etext.append("<br> *Summon Item:* [[Item%s][%s]]"%(GetTWikiName(summonItem.name),summonItem.name))
        
        # Damage Reflection
        if e.dmgReflectionMax:
            etext.append("<br> *Damage Reflection:* %i%% of %s with a maximum of %i"%(int(e.dmgReflectionPercent*100.0),RPG_RESIST_TEXT[RESISTFORDAMAGE[e.dmgReflectionType]],e.dmgReflectionMax))
        
        if e.negate and e.negateMaxLevel:
            etext.append("<br> *Negate:* %i of max level %i"%(e.negate,e.negateMaxLevel))
        
        # Resurrection
        if e.flags&RPG_EFFECT_RESURRECTION:
            etext.append("<br> *Resurrection:* %i%% XP"%(int(e.resurrectionXP*100.0)))
        
        # Banishing
        if e.flags&RPG_EFFECT_BANISH:
            etext.append("<br> *Banishes targets Pet*")
        
        # Spell casting interrupt
        if e.flags&RPG_EFFECT_INTERRUPT:
            etext.append("<br> *Interrupts targets Spell Casting*")
        
        # Leeching
        if e.leechEffect:
            leech = e.leechEffect
            etext.append("<br> *Leech:* %s "%leech.leechType.upper())
            if leech.leechBegin:
                etext.append("*Begin:* %i "%leech.leechBegin)
            if leech.leechTick and leech.leechTickRate:
                seconds = int (float(leech.leechTickRate/float(durSecond)))
                etext.append("*Tick:* %i every %i seconds "%(leech.leechTick,seconds))
            if leech.leechBegin:
                etext.append("*Begin:* %i "%leech.leechBegin)
        
        # Drain
        if e.drainEffect:
            drain = e.drainEffect
            etext.append("<br> *Drain:* %s "%drain.drainType.upper())
            if drain.drainBegin:
                etext.append("*Begin:* %i "%drain.drainBegin)
            if drain.drainTick and drain.drainTickRate:
                seconds = int (float(drain.drainTickRate/float(durSecond)))
                etext.append("*Tick:* %i every %i seconds "%(drain.drainTick,seconds))
            if drain.drainBegin:
                etext.append("*Begin:* %i "%drain.drainBegin)
        
        # Regen
        if e.regenEffect:
            regen = e.regenEffect
            etext.append("<br> *Regen:* %s "%regen.regenType.upper())
            if regen.regenBegin:
                etext.append("*Begin:* %i "%regen.regenBegin)
            if regen.regenTick and regen.regenTickRate:
                seconds = int (float(regen.regenTickRate/float(durSecond)))
                etext.append("*Tick:* %i every %i seconds "%(regen.regenTick,seconds))
            if regen.regenBegin:
                etext.append("*Begin:* %i "%regen.regenBegin)
        
        # Damage
        damage = list(e.damage)
        if len(damage):
            etext.append("<br> *Damage:* ")
            etext.append(', '.join("%s (%i)"%(RPG_RESIST_TEXT[RESISTFORDAMAGE[ed.type]],ed.amount) for ed in e.damage))
        
        stats = {
            RPG_EFFECT_STAGE_GLOBAL: defaultdict(int),
            RPG_EFFECT_STAGE_BEGIN: defaultdict(int),
            RPG_EFFECT_STAGE_TICK: defaultdict(int),
            RPG_EFFECT_STAGE_END: defaultdict(int)
        }
        for es in e.stats:
            stats[es.stage][es.statname] += es.value
        
        for stage,stext in stages.iteritems():
            if len(stats[stage]):
                etext.append("<br> %s <br> "%stext)
                if stage == RPG_EFFECT_STAGE_TICK:
                    etext.append("Tick Rate: %i<br> "%e.tickRate)
                for name,value in stats[stage].iteritems():
                    if name == "meleeDmgMod":
                        if value > 0:
                            etext.append("%%GREEN%% MELEE DAMAGE %i%% %%ENDCOLOR%%,"%int(value*100.0))
                        else:
                            etext.append("%%RED%% MELEE DAMAGE -%i%% %%ENDCOLOR%%,"%int(value*100.0))
                    elif name == "haste":
                        etext.append("%%GREEN%% HASTE %i%% %%ENDCOLOR%%,"%int(value*100.0))
                    elif name == "castHaste":
                        etext.append("%%GREEN%% CASTING HASTE %i%% %%ENDCOLOR%%,"%int(value*100.0))
                    elif name == "innateHaste":
                        etext.append("%%GREEN%% INNATE HASTE %i%% %%ENDCOLOR%%,"%int(value*100.0))

                    elif name == "regenHealth":
                        etext.append("%%GREEN%% HEALTH REGEN %i %%ENDCOLOR%%,"%int(value))
                    elif name == "regenMana":
                        etext.append("%%BLUE%% MANA REGEN %i %%ENDCOLOR%%,"%int(value))
                    elif name == "regenStamina":
                        etext.append("%%YELLOW%% STAMINA REGEN %i %%ENDCOLOR%%,"%int(value))
                    elif name == "regenCombat":
                        etext.append("%%GREEN%% COMBAT REGEN %i%% %%ENDCOLOR%%,"%int(value*100.0))
                    elif name == "move":
                        if value > 0:
                            etext.append("%%GREEN%% MOVE +%i%% %%ENDCOLOR%%,"%int(value*100.0))
                        else:
                            etext.append("%%RED%% MOVE %i%% %%ENDCOLOR%%,"%int(value*100.0))
                    elif name == "slow":
                        etext.append("%%RED%% SLOW %i%% %%ENDCOLOR%%,"%int(value*100.0))
                    elif value != round(value):
                        if value > 0:
                            etext.append("%%GREEN%% %s %i%% %%ENDCOLOR%%,"%(name.upper(),int(value*100.0)))
                        else:
                            etext.append("%%RED%% %s %i%% %%ENDCOLOR%%,"%(name.upper(),int(value*100.0)))
                    else:
                        if value > 0:
                            etext.append("%%GREEN%% %s %i %%ENDCOLOR%%,"%(name.upper(),int(value)))
                        else:
                            etext.append("%%RED%% %s %i %%ENDCOLOR%%,"%(name.upper(),int(value)))
                
                etext[-1] = etext[-1][:-1] + " "
    
    return ''.join(etext)


def CreateSpellIndex(spawnSpells):
    # spell class by level index will be generated in classpages.py to save on loops
    indexPage = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    indexPage += "---+ Spell Index\n\n"
    indexPage += "\t* [[SpellAllIndex][Index of all Spells]]\n\n"
    indexPage += ''.join("\t* [[Spell%sIndex][%s Spells]]\n"%(GetTWikiName(cname),cname) for cname in sorted(SPELLCLASSES.iterkeys()))
    indexPage += "\n\t* [[SpellSpawnSpellsIndex][Spawn Spells]]\n"
    indexPage += "\t* [[SpellSkillsIndex][Skill Spells]]\n"
    indexPage += "\t* [[SpellRComponentIndex][Spells with Component requirements]]\n"
    f = file("./distrib/twiki/data/MoMWorld/SpellIndex.txt","w")
    f.write(indexPage)
    f.close()
    
    indexPage = "---+ Spawn Spells\n\n"
    indexPage += ''.join("\t* [[Spell%s][%s]]\n"%(GetTWikiName(sname),sname) for sname in spawnSpells.iterkeys())
    f = file("./distrib/twiki/data/MoMWorld/SpellSpawnSpellsIndex.txt","w")
    f.write(indexPage)
    f.close()
    
    f = file("./distrib/twiki/data/MoMWorld/SpellRComponentIndex.txt","w")
    f.write(SpellIndexPages["SpellRComponentIndex"])
    f.close()
    
    
def CreateSpellPages(spawnSpells):
    
    indexPage = "---+ Index of all Spells\n\n"
    spellScrollPage = "---+ Spell Scrolls\n\n"
    
    for s in SpellProto.select(orderBy="name"):
        page = SpellPage
        
        TWIKINAME = "Spell%s"%GetTWikiName(s.name)
        indexPage += "\t* [[%s][%s]]\n"%(TWIKINAME,s.name)
        
        DESCTEXT = GenDescText(s,spawnSpells,TWIKINAME)
        STATTEXT = GenStatText(s)
        EFFECTTEXT = GenEffectText(s)
        
        page = page.replace("^^SPELLNAME^^",s.name).replace("^^DESCTEXT^^",DESCTEXT).replace("^^STATTEXT^^",STATTEXT).replace("^^EFFECTTEXT^^",EFFECTTEXT)
        
        if len(s.exclusions):
            overwritings = {True: [], False: []}
            for sname,overwrites in s.exclusions.iteritems():
                overwritings[overwrites].append(sname)
            page += "*Overwrites:* %s\n\n"%', '.join("[[Spell%s][%s]]"%(GetTWikiName(sname),sname) for sname in overwritings[True])
            page += "*Gets overwritten by:* %s\n\n\n"%', '.join("[[Spell%s][%s]]"%(GetTWikiName(sname),sname) for sname in overwritings[False])
        
        if len(s.classes):
            scrollname = "Scroll of %s"%s.name
            TWIKISCROLLNAME = GetTWikiName(scrollname)
            page += "*Spell Scroll:* [[Item%s][%s]]\n"%(TWIKISCROLLNAME,scrollname)
            spellScrollPage += "\t* [[Item%s][%s]]\n"%(TWIKISCROLLNAME,scrollname)
        
        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAME,"w")
        f.write(page)
        f.close()
    
    f = file("./distrib/twiki/data/MoMWorld/ItemSpellScrollsIndex.txt","w")
    f.write(spellScrollPage)
    f.close()
    f = file("./distrib/twiki/data/MoMWorld/SpellAllIndex.txt","w")
    f.write(indexPage)
    f.close()
    
    CreateSpellIndex(spawnSpells)
    
    return SPELLSUMMONITEMS,SPELLCLASSES
