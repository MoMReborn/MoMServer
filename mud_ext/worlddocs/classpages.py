# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#Quest Pages

from mud.world.defines import *
from utils import *
from mud.world.career import ClassProto
from mud.world.spell import SpellProto
from mud.world.advancement import *
from collections import defaultdict



ClassPage = """
---+ ^^CLASSNAME^^

---++ Skills
^^SKILLTEXT^^

---++ Spells
^^SPELLTEXT^^

---++ Advancement
^^ADVANCEMENTTEXT^^

"""



CLASSSKILLS = {}



def SortAdvancement(a,b):
    classes1 = list(a.classes)
    classes2 = list(b.classes)
    
    level1 = a.level
    
    for c in classes1:
        if c.classname == a.klass.name:
            if c.level > level1:
                level1 = c.level
            break
    
    level2 = b.level
    
    for c in classes2:
        if c.classname == b.klass.name:
            if c.level > level2:
                level2 = c.level
            break
            
    if level1 < level2:
        return -1
    
    if level1 > level2:
        return 1
    
    return 0


def GenAdvancementText(c):
    advances = []
    
    for advance in AdvancementProto.select():
        advance.myLevel = advance.level
        q = True
        
        classes = list(advance.classes)
        races = list(advance.races)
        if len(races) and not len(classes):
            continue #racial
        
        if len(classes):
            q = False
            for cl in classes:
                if cl.classname == c.name:
                    if cl.level > advance.myLevel:
                        advance.myLevel = cl.level #stash
                    q = True
                    break
                
        if not q:
            continue
        advance.klass = c #stash for sort
        advances.append(advance)
    
    if not len(advances):
        return ""
    
    atable = "| *Advancement* | *Level* | *Cost* | *Max Rank* | *Description*| *Requirements* | *Exclusion* |\n"
    
    for a in sorted(advances,cmp=SortAdvancement):
        reqtext = []
        for r in a.requirements:
            if r.rank > 1:
                reqtext.append("%s (%i)"%(r.require,r.rank))
            else:
                reqtext.append(r.require)
        
        reqtext.append(', '.join('(Race) %s'%r.racename for r in a.races))
        
        atable += "| %s | %i | %i | %i | %s | %s | %s |\n"%(a.name,a.myLevel,a.cost,a.maxRank,a.desc,', '.join(reqtext),', '.join(ex.exclude for ex in a.exclusions))
        
    return atable


def GenSkillText(c):
    stext = "| *Skill* | *Level Gained* | *Level Capped* | *Max* | *Trained* |\n"
    for s in sorted(c.skills,key=lambda obj:obj.levelGained):
        skillname = s.skillname
        twiki = "Skill%s"%GetTWikiName(skillname)
        if s.trained:
            trained = "Yes"
        else:
            trained = "No"
        
        # pretty big sorting...
        if skillname in CLASSSKILLS:
            CLASSSKILLS[skillname][0].append(c.name)
            CLASSSKILLS[skillname][1][s.levelGained].append(c.name)
            CLASSSKILLS[skillname][2][s.levelCapped].append(c.name)
            CLASSSKILLS[skillname][3][s.minReuseTime].append(c.name)
            CLASSSKILLS[skillname][4][s.maxReuseTime].append(c.name)
            CLASSSKILLS[skillname][5][s.maxValue].append(c.name)
            CLASSSKILLS[skillname][6][trained].append(c.name)
            raceReq = s.raceRequirementsInternal[:]
            if len(raceReq):
                racenames = frozenset(req.race for req in raceReq)
                CLASSSKILLS[skillname][7][racenames].append(c.name)
            if s.spellProto:
                CLASSSKILLS[skillname][8][s.spellProto.name].append(c.name)
        else:
            CLASSSKILLS[skillname] = [[c.name], defaultdict(list, {s.levelGained: [c.name]}), defaultdict(list, {s.levelCapped: [c.name]}), defaultdict(list, {s.minReuseTime: [c.name]}), defaultdict(list, {s.maxReuseTime: [c.name]}), defaultdict(list, {s.maxValue: [c.name]}), defaultdict(list, {trained: [c.name]}), defaultdict(list), defaultdict(list)]
            raceReq = s.raceRequirementsInternal[:]
            if len(raceReq):
                racenames = frozenset(req.race for req in raceReq)
                CLASSSKILLS[skillname][7][racenames].append(c.name)
            if s.spellProto:
                CLASSSKILLS[skillname][8][s.spellProto.name].append(c.name)
        
        stext += "| [[%s][%s]] | %i | %i | %i | %s |\n"%(twiki,skillname,s.levelGained,s.levelCapped,s.maxValue,trained)
    
    return stext


def GenSpellText(c,spellClasses):
    stext = ""
    stable = "| *Spell* | *Level Gained* |\n"
    
    # better do this here, class spells by level need a special sort
    spellPage = "---+ %s Spells\n\n"%c.name
    
    spells = spellClasses.get(c.name, [])
    
    for sname,level in sorted(spells,key=lambda obj:obj[1]):
        twiki = "Spell%s"%GetTWikiName(sname)
        stable += "| [[%s][%s]] | %i |\n"%(twiki,sname,level)
        spellPage += "\t* (%i)\t [[%s][%s]]\n"%(level,twiki,sname)
    
    f = file("./distrib/twiki/data/MoMWorld/Spell%sIndex.txt"%GetTWikiName(c.name),"w")
    f.write(spellPage)
    f.close()
    stext += stable
    return stext


def CreateClassPages(spellClasses):
    indexPage = '%META:TOPICINFO{author="JoshRitter" date="1121799107" format="1.0" version="1.1"}%\n'
    indexPage += "---+ Class Index\n\n"
    
    for c in ClassProto.select(orderBy="name"):
        page = ClassPage
        
        TWIKINAME = "Class%s"%GetTWikiName(c.name)
        indexPage += "\t* [[%s][%s]]\n"%(TWIKINAME,c.name)
        SKILLTEXT = GenSkillText(c)
        ADVANCEMENTTEXT = GenAdvancementText(c)
        SPELLTEXT = GenSpellText(c,spellClasses)
        page = page.replace("^^CLASSNAME^^",c.name)
        page = page.replace("^^SKILLTEXT^^",SKILLTEXT)
        page = page.replace("^^SPELLTEXT^^",SPELLTEXT)
        page = page.replace("^^ADVANCEMENTTEXT^^",ADVANCEMENTTEXT)
        
        f = file("./distrib/twiki/data/MoMWorld/%s.txt"%TWIKINAME,"w")
        f.write(page)
        f.close()
    
    f = file("./distrib/twiki/data/MoMWorld/ClassIndex.txt","w")
    f.write(indexPage)
    f.close()
    
    return CLASSSKILLS


 