# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#npc spell casting
from sqlobject import *

from spell import SpellClass,SpellProto
from defines import *
from core import *
import random

#we need spell lines, for casting logic! (ie best pet, etc)
#todo, healing logic

#sorts in reverse order
def SpellSort(a,b):
    alevel,blevel = 1000,1000
    
    for sc in a.classes:
        if sc.level < alevel:
            alevel = sc.level
    
    for sc in b.classes:
        if sc.level < blevel:
            blevel =sc.level

    #sorts in reverse order!!!
    if alevel > blevel:
        return -1
    if alevel < blevel:
        return 1
    return 0


MOB_SPELLS = {}
def InitMobSpells():
    con = SpellClass._connection.getConnection()
    for scname,protoid,sclevel in con.execute("SELECT classname,spell_proto_id,level FROM spell_class WHERE (SELECT spell_type FROM spell_proto WHERE id=spell_proto_id)&%i;"%RPG_SPELL_AICAST):
        d = MOB_SPELLS.setdefault(scname,{}).setdefault(sclevel,{'pet': set(), 'harmful': set(), 'beneficial': set(), 'healing': set()})
        
        proto = SpellProto.get(protoid)
        if proto.pet:
            d["pet"].add(proto)
            continue
        if proto.spellType&RPG_SPELL_HARMFUL:
            d["harmful"].add(proto)
            continue
        if proto.spellType&RPG_SPELL_HEALING:
            d["healing"].add(proto)
            continue
        d["beneficial"].add(proto)



class MobSpells:
    def __init__(self,mob,master = None):
        self.mob = mob
        self.spawn = mob.spawn
        self.petSpell = None
        
        harmful = set()
        healing = set()
        beneficial = set()
        harmfulSpawnSpells = set()
        slow = set()
        
        bestPet = None
        bestPetSpell = None
        bestPetLevel = 0
        
        self.hasSpells = False
        
        #grab spells from all classes
        
        for klass,level in zip((self.spawn.pclassInternal,self.spawn.sclassInternal,self.spawn.tclassInternal),(self.spawn.plevel,self.spawn.slevel,self.spawn.tlevel)):
            if MOB_SPELLS.has_key(klass):
                classSpells = MOB_SPELLS[klass]
                for x in xrange(level-20,level+1):
                    if x < 1:
                        continue
                    levelSpells = classSpells.get(x,None)
                    if not levelSpells:
                        continue
                    
                    for t,spells in levelSpells.iteritems():
                        if not len(spells):
                            continue
                        
                        if t == "pet":
                            for p in spells:
                                pet = p.pet
                                if pet.plevel > bestPetLevel:
                                    bestPetLevel = pet.plevel
                                    bestPet = pet
                                    bestPetSpell = p
                        elif t == "harmful":
                            for p in spells:
                                if mob.master and p.affectsStat("fear"):
                                    continue
                                if p.affectsStat("slow"):
                                    slow.add(p)
                                harmful.add(p)
                        elif t == "beneficial":
                            beneficial.update(spells)
                        elif t == "healing":
                            healing.update(spells)
        
        for spell in mob.spawn.spawnSpells:
            if spell.spellType&RPG_SPELL_HARMFUL:
                harmful.add(spell) #even more likely to use spawnspell
                harmfulSpawnSpells.add(spell)
            else:
                beneficial.add(spell)
                if spell.spellType&RPG_SPELL_HEALING:
                    healing.add(s)
        
        self.petSpell = bestPetSpell
        
        # minute and a half (beneficial spells)
        self.beneTimer = random.randint(0,3*90)
        self.harmTimer = random.randint(0,40)
        self.healTimer = 0
        
        self.harmful = tuple(harmful)
        self.healing = tuple(sorted(healing,cmp=SpellSort))
        self.beneficial = tuple(beneficial)
        self.harmfulSpawnSpells = tuple(harmfulSpawnSpells)
        self.slow = tuple(slow)
        
        if self.petSpell or len(harmful) or len(healing) or len(beneficial):
            self.hasSpells = True
    
    
    def considerHealing(self):
        mob = self.mob
        zone = mob.zone
        simAvatar = zone.simAvatar
        
        found = False
        for proto in self.healing:
            if mob.mana >= proto.manaCost:
                found = True
                break
            
        if not found:
            return False
        
        #build up the tactical map
        pmobs = []
        for id in mob.simObject.canSee:
            
            try:
                otherMob = zone.mobLookup[simAvatar.simLookup[id]]
            except KeyError:
                continue #not spawned yet, though in cansee
                
            if  otherMob.detached:                
                continue
            
            if otherMob.player:
                continue
            
            r = float(otherMob.health)/float(otherMob.maxHealth)
            if r > .5:
                continue
            
            if IsKOS(mob,otherMob):
                continue
            
            pmobs.append((otherMob,r))
        
        r = float(mob.health)/float(mob.maxHealth)
        if r <= .5:
            pmobs.append((mob,r))
            
                
        if not len(pmobs):
            return False
        
        if len(pmobs) > 1:
            pmobs.sort(key=lambda x:x[1])
        
        #cast
        mob.spellTarget = pmobs[0][0]
        mob.cast(proto)
        
        return True
        
        
        
        
                
    def think(self):
        mob = self.mob
        zone = mob.zone
        
        if len(self.healing) and self.healTimer>3:
            self.healTimer-=3

        
        if mob.casting:
            return #already casting a spell
        
        if mob.sleep > 0  or mob.stun > 0:
            return
        
        if mob.master and mob.visibility <= 0:
            return
        
        if len(self.healing) and not mob.master:
            self.healTimer-=3
            if self.healTimer <= 0:
                self.healTimer = random.randint(60,180) 
                if self.considerHealing():
                    return
        
        if mob.target and len(self.harmful) and IsKOS(mob,mob.target) and mob.target.simObject.id in mob.simObject.canSee:
            self.harmTimer-=3
            if self.harmTimer > 0:
                return
            self.harmTimer = random.randint(0,40)
            if mob.master:
                self.harmTimer*=2
            
            proto = None
            if self.petSpell and not mob.pet and not mob.petSpawning and not mob.master and mob.petCounter <2:
                proto = self.petSpell
            
            elif len(self.harmfulSpawnSpells) and not random.randint(0,2): #1 in 3 chance of casting spawn spell
                
                if len(self.harmfulSpawnSpells) == 1:
                    proto = self.harmfulSpawnSpells[0]
                else:
                    proto = self.harmfulSpawnSpells[random.randint(0,len(self.harmfulSpawnSpells)-1)]
            
            if not proto:    
                if len(self.harmful) == 1:
                    proto = self.harmful[0]
                else:
                    if len(self.slow) and mob.target.slow <=0 and not random.randint(0,2):
                        if len(self.slow)==1:
                            proto = self.slow[0]
                        else:
                            proto = self.slow[random.randint(0,len(self.slow)-1)]
                    else:
                        proto = self.harmful[random.randint(0,len(self.harmful)-1)]
            
            if mob.mana < proto.manaCost:
                return
            
            if proto == self.petSpell:
                mob.petCounter+=1
            self.spellTarget = mob.target	# just to make sure
            self.mob.cast(proto)
            
        elif len(self.beneficial) and not mob.master:
            self.beneTimer-=3
            if self.beneTimer > 0:
                return
            
            self.beneTimer = random.randint(0,3*90) 
            
            proto = None
            if self.petSpell and not mob.pet and not mob.petSpawning and not mob.master:
                proto = self.petSpell

            if not proto:
                #look for someone to buff
                
                if not len(self.beneficial):
                    return  

                pmobs = [mob]
                for id in mob.simObject.canSee:
                    
                    try:
                        otherMob = zone.mobLookup[zone.simAvatar.simLookup[id]]
                    except KeyError:
                        continue #not spawned yet, though in cansee
                    
                    if otherMob.player:
                        continue
                    if otherMob == mob:
                        continue
                        
                    if not otherMob.player and otherMob.detached:
                        #detached but still in cansee
                        continue
                    
                    if IsKOS(mob,otherMob):
                        continue
                    
                    
                    pmobs.append(otherMob)
                
                if not len(pmobs):
                    return
                
                mob.spellTarget = None
                
                if len(self.beneficial) == 1:
                    proto = self.beneficial[0]
                else:
                    proto = self.beneficial[random.randint(0,len(self.beneficial)-1)]
                
                if proto.target == RPG_TARGET_OTHER:
                    if len(pmobs) == 1:
                        mob.spellTarget = pmobs[0]
                    else:
                        mob.spellTarget = pmobs[random.randint(0,len(pmobs)-1)]
                
                
            if mob.mana < proto.manaCost:
                return
            self.mob.cast(proto)
            
        
        
            
            
            
        
                
            
        
            
        