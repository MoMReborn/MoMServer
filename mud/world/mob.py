# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from twisted.internet import reactor

from mud.gamesettings import *
from mud.simulation.shared.simdata import SimMobInfo
from mud.world.combat import CombatProcess
from mud.world.command import DoCommand
from mud.world.core import *
from mud.world.damage import Damage,ExtraDamageInfo
from mud.world.defines import *
from mud.world.item import ItemSetProto
from mud.world.loot import GenerateLoot
from mud.world.messages import GameMessage
from mud.world.mobspells import MobSpells
from mud.world.mobvariants import GenerateVariant
from mud.world.process import Process
from mud.world.projectile import Projectile
from mud.world.race import GetRace
from mud.world.skill import UseSkill
from mud.world.spell import Spell,SpellCasting,SpellProto,SpawnSpell,SpellStore
from mud.world.tactical import Tactical
from mud.world.shared.vocals import *
from mud.worlddocs.utils import GetTWikiName

from collections import defaultdict
from copy import copy
from itertools import repeat,imap
from math import acos,asin,ceil,degrees,floor,pi,sqrt
from operator import attrgetter
from random import randint
from time import time as sysTime
import traceback



class MobSkillProfile:
    def __init__(self):
        self.skillname = ""
        self.reuseTime = 0
        self.maxValue = 0
        self.absoluteMax = 0
        self.questRequirements = []


class Mob:
    id = 1L
    
    MODIFIER_ATTRIBUTES = ("damageMod", "healthMod", "offenseMod", "defenseMod")
    
    def __init__(self,spawn,zone,player=None,char=None,master=None,sizemod=1.0):
        self.race = GetRace(spawn.race)
        self.zone = zone
        self.extraDamageInfo = ExtraDamageInfo()
        self.player = player
        self.playerPet = False
        self.tacticalTimer = 0
        self.character = char
        self.realm = spawn.realm
        if master:
            self.realm = master.realm
        
        self.aggroOff = False
        
        self.dmgBonusPrimary = 0
        self.dmgBonusOffhand = 0
        
        
        #player -> time
        self.playerAggro = {}
        self.playerInitiate = {}
        
        self.equipParticles = None
        
        #slot -> list of mod tuples
        self.equipMods = {}
        
        self.advancements = defaultdict(float)
        
        self.attacking = False
        self.light = 0
        self.flying = 0
        self.feignDeath = 0
        
        self.kingKiller = None
        self.kingTimer = 0
        
        self.unstick = 0
        self.unstickReuse = 0
        self.petCounter = 0
        
        self.charmEffect = None
        self.charmBackupRealm = None
        self.charmBegin = 0
        
        # If the difficulty setting is set to easy or the mob is a player, then
        # clamp modifiers to never exceed 1.0.
        if CoreSettings.DIFFICULTY == RPG_DIFFICULTY_EASY or player:
            self.difficultyMod = 1.0
            self.damageMod = 1.0
            self.healthMod = 1.0
            self.defenseMod = 1.0
            self.offenseMod = 1.0
            
        # Otherwise, set modifiers based on spawn.
        else:
        
            # If the spawn's difficulty mod is greater than 1.0, then it will
            # be used.
            if 1.0 < spawn.difficultyMod:
                self.difficultyMod = difficultyMod = spawn.difficultyMod
                
            # Otherwise, clamp the difficult mod to be at least 1.0.
            else:
                self.difficultyMod = difficultyMod = 1.0
            
            # Set damage, health, offense, and defense modifiers based on the
            # spawn's modifiers, but guarantee that they will be at least equal
            # to the difficulty modifier.  This forces the minimum of each mod
            # to be at least 1.0.
            # Note: SQLObject __dict__ cannot be used due to SQLObject's 
            # attribute wrapping.  Therefore, getattr is used.      
            for mod in Mob.MODIFIER_ATTRIBUTES:
                if getattr(spawn, mod) < difficultyMod:
                    self.__dict__[mod] = difficultyMod
                else:
                    self.__dict__[mod] = getattr(spawn, mod)
                                        
        self.simObject = None
        
        self.combatCasting = 0
        self.combatTimer = 0
        self.regenCombat = 0.0
        self.castHealMod = 0.0
        self.castDmgMod = 0.0
        self.meleeDmgMod = 1.0
        
        self.corpseRemoval = None
        self.corpseCount = 0
        self.detached = False
        self.zombie = False
        self.spawnpoint = None
        #player
        self.looter = None
        self.loot = None
        
        self.interacting = None
        self.vendor = None

        #todo fix up name a little based on unique, etc
        self.name = spawn.name 
        self.variantName = ""
        self.id = Mob.id
        Mob.id += 1
        
        self.target = None
        
        self.genLoot = False
        
        self.sex = spawn.sex
        
        if not player:
            if not spawn.flags&RPG_SPAWN_FIXEDSEX and not spawn.flags&RPG_SPAWN_UNIQUE:
                if spawn.race in RPG_PC_RACES:
                    self.sex = RPG_SEXES[randint(0,1)]
        
        self.visibility = 1.0
        self.seeInvisible = spawn.seeInvisible
        if self.race.seeInvisible > self.seeInvisible:
            self.seeInvisible = self.race.seeInvisible
        
        self.size = sizemod
        self.fear = 0
        #we don't use the above because fear doesn't work indoor and we don't want to mess with effect code
        self.isFeared = False
        self.sleep = 0
        self.stun = 0 #mob doesn't wake up
        self.sneak = 0
        self.suppressCasting = 0
        self.invulnerable = 0
        
         #haste
        self.castHaste = 0.0
        self.itemHaste = 0
        self.effectHaste = (None,0)
        self.innateHaste = 0 
        self.slow = 0

        
        self.noise = 0
        
        self.light = 0
        
        # If the player is indoors, move gets clamped to 1,
        #  doesn't get clamped for non-Player Mobs.
        self.move = spawn.move
        self.swimMove = spawn.move
        # Speed mod works even indoors, but shares clamp with Mob.move,
        #  so any special bonus can potentially be nullified by large move.
        self.speedMod = 1.0
        
        if not player:
            presence = 0
            presenceFactor = 0.0
            if not zone.world.singlePlayer:
                presenceFactor += 2.0
                
            if CoreSettings.DIFFICULTY == RPG_DIFFICULTY_NORMAL:
                presenceFactor += 1.0
                
            if CoreSettings.DIFFICULTY == RPG_DIFFICULTY_HARDCORE:
                presenceFactor += 2.0
                
            presenceFactor += self.difficultyMod - 1.0
            
            if presenceFactor < 0.0:
                presenceFactor = 0.0
                
            presence = int(spawn.plevel*2.0*presenceFactor)
            
            if not master:
                if spawn.plevel >= 90:
                    self.stun = -2
                    self.fear = -2
                    self.castHaste = float(spawn.plevel)/33.0 
                    #self.innateHaste = float(spawn.plevel)/33.0 

                elif spawn.plevel < 7:
                    if spawn.plevel < 5:
                        self.move *= .75
                        self.slow = .4
                    else:
                        self.move *= .8
                        self.slow = .2

            self.strBase = spawn.plevel*10+100
            self.dexBase = spawn.plevel*10+100
            self.refBase = spawn.plevel*10+100
            self.agiBase = spawn.plevel*10+100
            self.wisBase = spawn.plevel*10+100
            self.bdyBase = spawn.plevel*10+100
            self.mndBase = spawn.plevel*10+100
            self.mysBase = spawn.plevel*10+100
            self.preBase = presence
            
            self.str = spawn.plevel*10+100
            self.dex = spawn.plevel*10+100
            self.ref = spawn.plevel*10+100
            self.agi = spawn.plevel*10+100
            self.wis = spawn.plevel*10+100
            self.bdy = spawn.plevel*10+100
            self.mnd = spawn.plevel*10+100
            self.mys = spawn.plevel*10+100
            self.pre = presence
            
            self.armor = spawn.plevel*10
            
            
        else:
            self.strBase = spawn.strBase
            self.dexBase = spawn.dexBase
            self.refBase = spawn.refBase
            self.agiBase = spawn.agiBase
            self.wisBase = spawn.wisBase
            self.bdyBase = spawn.bdyBase
            self.mndBase = spawn.mndBase
            self.mysBase = spawn.mysBase
            self.preBase = spawn.preBase
            if self.preBase > RPG_MAX_PRESENCE:
                self.preBase = RPG_MAX_PRESENCE
                spawn.preBase = RPG_MAX_PRESENCE
            
            self.str = self.strBase
            self.dex = self.dexBase
            self.ref = self.refBase
            self.agi = self.agiBase
            self.wis = self.wisBase
            self.bdy = self.bdyBase
            self.mnd = self.mndBase
            self.mys = self.mysBase
            self.pre = self.preBase
            
            self.armor = 0
                    
            self.wornBreakable = {}
            
            
        
        self.pclass = spawn.pclass
        self.sclass = spawn.sclass
        self.tclass = spawn.tclass
        
        self.level = spawn.plevel #synonymous
        self.plevel = spawn.plevel
        self.slevel = spawn.slevel
        self.tlevel = spawn.tlevel
        
        self.offenseScalar = 1.0
        self.defenseScalar = 1.0
        self.maxManaScalar = 1.0
        self.maxHealthScalar = 1.0
        self.maxStaminaScalar = 1.0
        
        
        self.damagedProcs = []
        
        self.xpScalar = 1.0

        self.health = 100
        self.maxHealth = 100
        self.mana = 100
        self.maxMana = 100
        self.stamina = 100
        self.maxStamina = 100
        
        self.regenHealth = spawn.regenHealth
        self.regenMana = spawn.regenMana
        self.regenStamina = spawn.regenStamina
        
        self.regenHealthScalar = 1.0
        self.regenManaScalar = 1.0
        self.regenStaminaScalar = 1.0
        
        
        # Used to prevent zombie regen, this flag is used for keeping triggered spawn health
        self.preventZombieRegen = False
        
        
        self.spawn = spawn
        
        
        self.aggro = defaultdict(int)
        self.aggroRange = spawn.aggroRange
        self.followRange = spawn.followRange
        if self.followRange < self.aggroRange:
            #fix
            self.followRange = self.aggroRange + 20
        
        self.assists = not spawn.flags&RPG_SPAWN_NOASSIST
        
        self.tactical = Tactical(self)
        
        #mobs can wear stuff now.. based on loot... this allows us
        #to see if they have an item, etc
        #characters need to be updated, 
        
        
        self.items = []
        self.itemSets = {}
        self.itemSetHastes = []
        self.itemSetSpells = {}
        # Dictionary which holds items that need to be ticked,
        #  meaning items with a reuse timer or with limited
        #  life time. List would suffice but dictionary has
        #  better performance.
        self.itemRequireTick = {}
        # Dictionaries which hold the mobs food and drink.
        # This variables exist only for character mobs and are
        #  used for faster access.
        self.itemFood = {}
        self.itemDrink = {}
        
        #name -> ticks
        self.skillReuse = {}
        #spellproto->timer
        self.recastTimers = {}

        self.skillLevels = {}
        
        
        #processes where I am the src and which havn't been started
        self.processesPending = set()
        #processes where I am the dst
        self.processesIn = set()
        #processes where I am the src
        self.processesOut = set()
        
        #spells
        self.casting = None
        
        self.regenTimer = 36 #every 6 seconds
        
        #mob -> XPDamage class
        self.xpDamage = {}
        
        #pets
        self.pet = None
        self.petScalar = 1.0
        self.petSpawning = False
        self.petMode = RPG_PET_FOLLOWME
        self.petAcceptItemTimer = 0
        self.master = None
        self.followTarget = None
        self.petSpeedMod = 0.0
        
        self.worn = {}
        
        self.autoAttack = False
        
        self.aiSkills = []
        self.aiSkillTimer = 72
        
        
        self.wornTimer = 180
        
        self.tookDamage = False
        self.combatInhibited = 0
        
        self.xpMod = spawn.xpMod
        
        # setup resists dict
        self.resists = defaultdict(int, ((r.resistType,r.resistAmount) for r in spawn.resists))
        
        self.waterCoverage = 0
        self.underWater = 0
        self.holdBreathTimer = 60
        self.waterBreathing = 0.0
        self.lastSwimPos = (0,0,0)
        self.underWaterRatio = 1.0
        
        for s in self.spawn.spawnStats:
            self.__dict__[s.statname] += s.value
        
        # variance
        self.uniqueVariant = False
        if not self.player:
            GenerateVariant(self)
        
        self.mobSpells = None
        
        # ai mobs can attack one mob and cast on another
        self.spellTarget = None
        
        
            
        self.mobInfo = SimMobInfo(self)        
        if char:
            self.updateClassStats()
        
            char.mob = self
            char.equipItems()
            char.applyAdvancementStats()
            
            self.updateDerivedStats()
        
                
                
        #change this for players eventually
        self.health = self.maxHealth
        self.mana = self.maxMana
        self.stamina = self.maxStamina
        
        
        #setup vocals
        self.vocals = None
        self.vocalSet = 'A'
        if spawn.vocalSet:
            sex = self.sex
            if sex == 'Neuter':
                print "Warning: spawn %s has vocal set and is neuter, setting to male"%self.name
                sex = "Male"
                
            if GAMEROOT == "minions.of.mirth":
                self.vocalSet = spawn.vocalSet
                vs = sex.upper()+"_%c"%self.vocalSet.upper()
                try:
                    self.vocals = VOCALSETS[vs]
                except KeyError:
                    print "Warning: spawn %s has invalid vocal set %c"%(spawn.name,self.vocalSet)
            else:
                vs = sex.upper()+"_A"
                try:
                    self.vocals = VOCALSETS[vs]
                except KeyError:
                    print "Warning: spawn %s has invalid vocal set %c"%(spawn.name,self.vocalSet)
        
        self.battle = None
        
        self.despawnTimer = 0
        
        self.eatTimer = randint(60,6*60*5) # 5 minutes
        self.drinkTimer = randint(60,6*60*3) # 3 minutes
        
        self.lootInitialized = False
        
        
        
        self.illusionEffect = None
        
        # Dictionary to store info for nonlinear effect stacking.
        self.effectStackNonlinear = {}
        
        self.mobInfo.refresh()
        
        self.derivedDirty = True
        
        self.combatIds = []
        self.rangedReuse = 0
        
        self.hungry = False
        self.thirsty = False
        
        self.stopCastingTimer = 0
        
        
        self.dmgReflectionEffects = dict()
        
        #player -> time
        self.interactTimes = {}
        
        if self.character:
            # Persistent spells
            for store in self.character.spellStore:
                if not self.character.dead:
                    restoreSpell = Spell(self,self,store.spellProto,store.mod,store.time,None,False,True,store.level)
                    restoreSpell.healMod = store.healMod
                    restoreSpell.damageMod = store.damageMod
                    self.processesPending.add(restoreSpell)
                store.destroySelf()
            
            self.items = self.character.items
            
            # Fill special item dictionaries...
            for item in self.items:
                if item.lifeTime:
                    self.itemRequireTick[item] = item.lifeTime
                if item.food:
                    self.itemFood[item] = item.food
                if item.drink:
                    self.itemDrink[item] = item.drink
        
        self.mobInitialized = False
        
        
    def initMob(self):
        if self.player:
            traceback.print_stack()
            print "AssertionError: player already initialized!"
            return
        self.mobInitialized = True
        self.updateClassStats()
        
        self.mobSpells = MobSpells(self,self.master)
        if not self.mobSpells.hasSpells:
            self.mobSpells = None #no spells
        
        self.updateDerivedStats()
        
        if self.master and self.master.player:
            char = self.master.character
            if int(sysTime()) - char.petHealthTimer < 600:    # 10 minutes
                # +1 just to make sure it doesn't die upon summon in very weird circumstances
                lowCap = int(float(self.maxHealth)*0.1) + 1
                if char.petHealthBackup > lowCap:
                    if char.petHealthBackup > self.maxHealth:
                        self.health = self.maxHealth
                    else:
                        self.health = char.petHealthBackup
                        self.master.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s mourns the loss of %s's former pet.\\n"%(self.name,self.master.character.name))
                else:
                    self.health = lowCap
                    self.master.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s mourns the loss of %s's former pet.\\n"%(self.name,self.master.character.name))
            else:
                self.health = self.maxHealth
        else:
            self.health = self.maxHealth
            # Make sure the pet inherits the masters home transform.
            if self.master:
                self.zone.simAvatar.mind.callRemote("inheritHomeTransform",self.simObject.id,self.master.simObject.id)
        
        self.mana = self.maxMana
        self.stamina = self.maxStamina
        
        self.mobInfo.refresh()
    
    
    def hasClass(self,klass):
        if self.spawn.plevel and self.spawn.pclassInternal == klass:
            return True
        if self.spawn.slevel and self.spawn.sclassInternal == klass:
            return True
        if self.spawn.tlevel and self.spawn.tclassInternal == klass:
            return True
    
    
    def initLoot(self):
        self.lootInitialized = True
        if self.player or self.master:
            return
        GenerateLoot(self)
        
        map(self.aiEquipItem,self.loot.items)
        
        self.mobInfo.refresh()
    
    
    def updateDerivedStats(self):
        
        self.derivedDirty = False
        stats = self.pclass.getClassStats(self,self.plevel)
        #secondary class
        if self.sclass:
            sstats = self.sclass.getClassStats(self,self.slevel)
            for st,value in sstats.iteritems():
                if value > stats[st]:
                    stats[st]=value
        #tertiary class
        if self.tclass:
            tstats = self.tclass.getClassStats(self,self.tlevel)
            for st,value in tstats.iteritems():
                if value > stats[st]:
                    stats[st]=value
        
        self.__dict__.update(stats)
        
        #finally add derived stats
        for p in self.processesIn:
            if isinstance(p,Spell):
                for e in p.effects:
                    for stname,value in e.derivedStatMods.iteritems():
                        self.__dict__[stname] += value
        
        for item in self.worn.itervalues():
            for st,value in item.stats:
                if st in RPG_DERIVEDSTATS:
                    self.__dict__[st] += value
        
        map(ItemSetProto.updateDerived,self.itemSets.iterkeys(),repeat(self,len(self.itemSets)))
        
        #add in derived stuff
        if self.character and hasattr(self,"advancementStats"):
            for st,value in self.advancementStats:
                if st in RPG_DERIVEDSTATS:
                    self.__dict__[st] += value
        
        self.maxHealth *= self.healthMod
        
        self.maxHealth *= self.maxHealthScalar
        self.maxStamina *= self.maxStaminaScalar
        self.maxMana *= self.maxManaScalar
        self.offense *= self.offenseScalar
        self.defense *= self.defenseScalar
        
        if not self.player:
            if self.master:
                improved = self.master.advancements.get("improvePet",0.0)
                if improved:
                    self.maxHealth += self.maxHealth * improved
                    self.offense += self.offense * improved
                    self.defense += self.defense * improved
            
            if CoreSettings.DIFFICULTY < RPG_DIFFICULTY_HARDCORE:
                if self.plevel < 8:
                    self.maxHealth = ceil(self.maxHealth * .5)
            
            elif CoreSettings.DIFFICULTY == RPG_DIFFICULTY_HARDCORE:
                self.maxHealth *= 4
            
            if self.plevel > 10 and not self.zone.world.singlePlayer:
                self.maxHealth += self.maxHealth * (float(self.plevel) / 120.0)
            #tweak
            #if self.plevel < 40:
            #    if self.master and self.master.player:
            #        pass
            #    elif not (self.spawn.flags&RPG_SPAWN_UNIQUE) and not self.difficultyMod and not self.uniqueVariant:
            #        self.maxHealth/=2
            #        if self.maxHealth<10:
            #            self.maxHealth = 10
        
        else:
            if CoreSettings.DIFFICULTY == RPG_DIFFICULTY_EASY:
                self.maxHealth *= 2
    
    
    # This is an expensive function, especially for character mobs!
    #  only call when necessary
    def updateClassStats(self):
        from mud.world.character import CharacterSkill
        
        charskills = None
        if self.player:
            self.player.cinfoDirty = True
            charskills = dict((cs.skillname,cs) for cs in self.character.skills)
        
        self.updateDerivedStats()
        
        # collapse skill list
        self.mobSkillProfiles = {}
        self.skillLevels = {}
        self.aiSkills = []
        classes = [(self.pclass,self.plevel),(self.sclass,self.slevel),(self.tclass,self.tlevel)]
        for cl,level in classes:
            if not cl:
                break
            
            for cskill in cl.classSkills:
                if level < cskill.levelGained:
                    if not self.player:
                        continue
                    if charskills == None or not charskills.has_key(cskill.skillname):
                        continue  # don't qualify
                
                if len(cskill.raceRequirements) and self.spawn.race not in cskill.raceRequirements:
                    continue
                
                if charskills != None and cskill.trained and self.player and \
                    self.player.realm != RPG_REALM_MONSTER:
                    if not charskills.has_key(cskill.skillname):
                        continue
                
                maxValue = cskill.getMaxValueForLevel(level)
                reuseTime = cskill.getReuseTimeForLevel(level)
                
                # don't actually qualify in this class, though charskills has value or something
                if not maxValue or not reuseTime:
                    if cskill.minReuseTime or cskill.maxReuseTime:
                        continue

                # Mobs: If a skill is not in the mobs skill list then check the trained flag
                #       and the level requirement plus deny all implicit skills except block and
                #       fist for race "Animal".
                if not self.player:
                    for sskill in self.spawn.skills:
                        if sskill.skillname == cskill.skillname:
                            break
                    else:
                        if self.spawn.race == "Animal" and not (cskill.skillname == "Fists" or cskill.skillname == "Block" or cskill.skillname == "1H Pierce" or cskill.skillname == "1H Slash" or cskill.skillname == "1H Impact" or cskill.skillname == "1H Cleave" or cskill.skillname == "2H Pierce" or cskill.skillname == "2H Slash" or cskill.skillname == "2H Impact" or cskill.skillname == "2H Cleave"):
                            continue
                        if self.spawn.race == "Reptile" and not (cskill.skillname == "Fists" or cskill.skillname == "Block" or cskill.skillname == "1H Pierce" or cskill.skillname == "1H Slash" or cskill.skillname == "1H Impact" or cskill.skillname == "1H Cleave" or cskill.skillname == "2H Pierce" or cskill.skillname == "2H Slash" or cskill.skillname == "2H Impact" or cskill.skillname == "2H Cleave"):
                            continue
                        if cskill.trained or level < cskill.levelGained:
                            continue

                if not self.mobSkillProfiles.has_key(cskill.skillname):
                    # not entered yet, just copy it in
                    mskill = MobSkillProfile()
                    mskill.classSkill = cskill
                    self.mobSkillProfiles[cskill.skillname] = mskill
                    mskill.skillname = cskill.skillname
                    mskill.maxValue = maxValue
                    mskill.absoluteMax = cskill.maxValue
                    mskill.reuseTime = reuseTime
                    mskill.questRequirements = cskill.questRequirements
                else:
                    # we get the best
                    mskill = self.mobSkillProfiles[cskill.skillname]
                    if maxValue > mskill.maxValue:
                        mskill.maxValue = maxValue
                    if reuseTime < mskill.reuseTime:
                        mskill.reuseTime = reuseTime
        
        for mskill in self.mobSkillProfiles.itervalues():
            if charskills == None:
                if CoreSettings.DIFFICULTY != RPG_DIFFICULTY_HARDCORE and self.plevel < 5:
                    # in easy and normal, mobs don't get (improved) skills until level 5
                    self.skillLevels[mskill.skillname] = 1
                else:
                    self.skillLevels[mskill.skillname] = mskill.maxValue
                
                if mskill.skillname=="Dual Wield":
                    self.aiSkills.append(mskill)
                elif mskill.reuseTime and mskill.classSkill.spellProto:
                    if not mskill.classSkill.spellProto.affectsStat("feignDeath"):
                        self.aiSkills.append(mskill)
            else:
                if not charskills.has_key(mskill.skillname):
                    #this is a pretty crappy place for this
                    if mskill.classSkill.levelGained != 1:
                        self.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s has learned <a:Skill%s>%s</a>!\\n"%(self.name,GetTWikiName(mskill.skillname),mskill.skillname))
                    level = 1
                    
                    if self.player.realm == RPG_REALM_MONSTER and \
                        mskill.skillname not in RPG_CRAFT_SKILLS:
                        level = mskill.maxValue
                    
                    charskills[mskill.skillname] = CharacterSkill( \
                        character=self.character,skillname=mskill.skillname, \
                        level=level)
                
                self.skillLevels[mskill.skillname] = charskills[mskill.skillname].level
    
    
    # can be up or down
    def levelChanged(self):
        spawn = self.spawn
        self.pclass = spawn.pclass
        self.sclass = spawn.sclass
        self.tclass = spawn.tclass
        
        self.level =  spawn.plevel  # synonymous
        self.plevel = spawn.plevel
        self.slevel = spawn.slevel
        self.tlevel = spawn.tlevel
        
        self.updateClassStats()
        if self.character:
            self.character.unequipItems()
            self.character.refreshItems()
            self.character.equipItems(False)
        self.updateDerivedStats()
        
        if self.player:
            self.player.world.sendCharacterInfo(self.player)
    
    
    def calcItemHaste(self):
        # find best haste
        self.itemHaste = 0
        for item in self.worn.itervalues():
            for stat in item.stats:
                if stat[0] == "haste" and stat[1] > self.itemHaste:
                    self.itemHaste = stat[1]
        # item sets can be processed more easily
        #  since they don't have the ability to change their stats due to a process
        if len(self.itemSetHastes):
            maxSetHaste = max(self.itemSetHastes)
            if maxSetHaste > self.itemHaste:
                self.itemHaste = maxSetHaste
    
    
    def aiEquipItem(self,item):
        itemSlots = list(item.itemProto.slots)
        powerwield = self.skillLevels.get("Power Wield")
        if "2H" in item.skill:
            dualwield = powerwield
            if powerwield and RPG_SLOT_PRIMARY in itemSlots:
                if RPG_SLOT_SECONDARY not in itemSlots:
                    itemSlots.append(RPG_SLOT_SECONDARY)
        else:
            dualwield = self.skillLevels.get("Dual Wield") or powerwield
        
        for slot in itemSlots:
            if slot == RPG_SLOT_SECONDARY:
                if not dualwield:
                    continue
            if slot in self.worn:
                continue
            self.equipItem(slot,item)
            item.slot = slot
            self.mobInfo.refresh()
            break
    
    
    def equipItem(self, slot, item, printSets=True, reequip=False):
        if slot < RPG_SLOT_WORN_BEGIN or slot >= RPG_SLOT_WORN_END:
            traceback.print_stack()
            print "AssertionError: trying to equip %s in non-wearable slot!"%item.name
            if item.character:  # Try to fix previously wrong equipped items
                item.character.player.giveItemInstance(item)
            return False
        if slot in self.worn:
            print "Warning Mob.equipItem",self.worn[slot].name,"is already worn in slot %i!!!"%slot
            return False
        # Removed in 1.3 SP2
        """
        if slot == RPG_SLOT_SECONDARY and RPG_SLOT_SHIELD in self.worn:
            return
        if slot == RPG_SLOT_SHIELD and RPG_SLOT_SECONDARY in self.worn:
            return

        # Scan items for wearability conflicts.
        for iitem in self.worn.itervalues():
            # If there is already a secondary weapon, a shield or
            # a 2H weapon equipped then don't wear another 2H weapon.
            if (iitem.slot == RPG_SLOT_SECONDARY) or (iitem.slot == RPG_SLOT_SHIELD) or \
               (iitem.slot == RPG_SLOT_PRIMARY and "2H" in iitem.skill):
                if "2H" in item.skill:
                    return
            # If there is already a 2H weapon equipped then don't wear a shield.
            if iitem.slot == RPG_SLOT_PRIMARY and "2H" in iitem.skill:
                if item.skill == "Shields":
                    return
        """
        # If this item is unique, check if one is already worn by the mob.
        if item.flags & RPG_ITEM_UNIQUE:
            for testItem in self.worn.itervalues():
                if testItem.itemProto == item.itemProto:
                    # If this is a player mob, give feedback to the player.
                    if self.player:
                        self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s can only use one <a:Item%s>%s</a> at a time!\n'%(self.name,GetTWikiName(item.itemProto.name),item.name))
                    # Otherwise, if this is the pet of a player mob, give
                    #  feedback as well.
                    elif self.master and self.master.player:
                        self.master.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s can only use one <a:Item%s>%s</a> at a time!\n'%(self.name,GetTWikiName(item.itemProto.name),item.name))
                    # Equip failed, return False.
                    return False
        
        self.derivedDirty = True
        self.worn[slot] = item
        self.equipMods[slot] = []
        
        ip = item.itemProto
        if not reequip and ip.equippedParticle and (slot == RPG_SLOT_PRIMARY or slot == RPG_SLOT_SECONDARY):
            if not self.simObject:
                if not self.equipParticles:
                    self.equipParticles = []
                self.equipParticles.append((slot,ip.equippedParticle,ip.equippedParticleTexture))
            else:
                try:
                    self.zone.simAvatar.mind.callRemote("itemParticleNode",self.simObject.id,slot,ip.equippedParticle,ip.equippedParticleTexture)
                except:
                    pass
        
        if self.player:
                
            # Only add items with repair max and not in a weapon-type slot.
            if ip.repairMax and not RPG_SLOT_PRIMARY <= slot <= RPG_SLOT_AMMO:
                self.wornBreakable[slot] = item
            
            if not reequip and ip.equipMessage:
                self.player.sendGameText(RPG_MSG_GAME_GAINED,"%s\\n"%ip.equipMessage,self)
            
            for set in ip.itemSets:
                setProto = set.itemSetProto
                # set flag that this set got a change
                self.itemSets.setdefault(setProto, [{},True])[1] = True
                contributors = self.itemSets[setProto][0]
                setContribution = contributors.setdefault(set.contribution,[0,0])
                # general item count
                setContribution[0] += 1
                # non-penalty item count
                if not item.penalty:
                    setContribution[1] += 1
            # Don't use iterkeys here as dict gets modified
            #  during loop.
            for set in self.itemSets.keys():
                set.checkAndApply(self,printSets)
                if not len(self.itemSets[set][0]):
                    del self.itemSets[set]
        
        # make this an item stat?
        self.armor += item.armor
        self.equipMods[slot].append(("armor",item.armor))
        
        try:
            for st in item.stats:
                if st[0] == "haste":
                    self.calcItemHaste()
                elif st[0] in RPG_RESISTSTATS:
                    self.equipMods[slot].append(st)
                    self.resists[RPG_RESISTLOOKUP[st[0]]] += st[1]
                else:
                    self.equipMods[slot].append(st)
                    setattr(self,st[0],getattr(self,st[0],0) + st[1])
        except:
            traceback.print_exc()
        
        # damaged proc counter
        for spell in item.spells:
            if spell.trigger == RPG_ITEM_TRIGGER_DAMAGED:
                self.damagedProcs.append(item)
                break
        
        # Equipping the item worked, return True.
        return True
    
    
    def unequipItem(self,slot,reequip=False):
        if slot not in self.worn:
            return
        
        item = self.worn[slot]
        self.derivedDirty = True
        
        ip = item.itemProto
        if not reequip and ip.equippedParticle and (slot == RPG_SLOT_PRIMARY or slot == RPG_SLOT_SECONDARY):
            try:
                self.zone.simAvatar.mind.callRemote("clearParticleNode",self.simObject.id,slot)
            except:
                pass
        
        # damaged proc counter
        if item in self.damagedProcs:
            self.damagedProcs.remove(item)
        
        # armor handled by equip mods
        #self.armor -= item.armor
        
        del self.worn[slot]
        
        if self.player:
            
            # Attempt to remove the item from breakable item list.
            try: 
                del self.wornBreakable[slot]
            except:
                pass # Item was not breakable.
        
            for set in ip.itemSets:
                setProto = set.itemSetProto
                try:  # set flag that this set got a change
                    self.itemSets[setProto][1] = True
                except KeyError:
                    continue  # this shouldn't happen, ever
                contributors = self.itemSets[setProto][0]
                # general item count
                try:
                    contributors[set.contribution][0] -= 1
                except KeyError:
                    continue  # this shouldn't happen, ever
                # non-penalty item count
                if not item.penalty:
                    contributors[set.contribution][1] -= 1
            # Don't use iterkeys here as dict gets modified
            #  during loop.
            for set in self.itemSets.keys():
                set.checkAndApply(self)
                if not len(self.itemSets[set][0]):
                    del self.itemSets[set]
        
        self.calcItemHaste()
        
        for st in self.equipMods[slot]:
            if st[0] in RPG_RESISTSTATS:
                self.resists[RPG_RESISTLOOKUP[st[0]]] -= st[1]
            else:
                self.__dict__[st[0]] -= st[1]
        
        del self.equipMods[slot]
    
    
    def tick(self):
        if not self.player and not self.mobInitialized:
            self.initMob()
        if not self.lootInitialized:
            self.initLoot()
        if self.loot:
            if self.loot.pickPocketTimer:
                self.loot.pickPocketTimer -= 3
                if self.loot.pickPocketTimer < 0:
                    self.loot.pickPocketTimer = 0
        
        #yet another hack
        if self.equipParticles:
            for slot,p,pt in self.equipParticles:
                self.zone.simAvatar.mind.callRemote("itemParticleNode",self.simObject.id,slot,p,pt)
            self.equipParticles = None
        
        # Don't use iterkeys here as dict gets modified
        #  during loop.
        for m in self.aggro.keys():
            if m.detached:
                print "WARNING: detached mob %s in %s aggro"%(m.name,self.name)
                del self.aggro[m]
        
        # Handle player mobs.
        if self.player:
            # Don't use iterkeys here as dict gets modified
            #  during loop.
            for p in self.playerAggro.keys():
                if self.playerAggro[p] > 120:
                    del self.playerAggro[p]
                    map(self.aggro.__delitem__,list(m for m in self.aggro.iterkeys() if m.player == p))
                    try:
                        othermob = self.playerInitiate[p][1]
                        del othermob.playerInitiate[self.player]
                    except:
                        pass
                    try:
                        del self.playerInitiate[p]
                    except KeyError:
                        pass
                else:
                    self.playerAggro[p] += 3
            
            self.isFeared = self.fear > 0
            
            if self.feignDeath > 0:
                if self.pet:
                    self.pet.zone.removeMob(self.pet)
            
            #tp. must come before process logic
            if self.player.telelink:
                if self.health <= 0:
                    self.health = 1 #alive no matter what
                from mud.world.effect import DoTeleportReal
                DoTeleportReal(self.player.telelink[0],self.player.telelink[1],self.player.telelink[2])
                return
            
            if self.stopCastingTimer:
                self.stopCastingTimer -= 3
                if self.stopCastingTimer < 0:
                    self.stopCastingTimer = 0
            
            if self.simObject.waterCoverage >= .45:
                p1 = self.simObject.position
                p2 = self.lastSwimPos
                x = p1[0] - p2[0]
                y = p1[1] - p2[1]
                z = p1[2] - p2[2]
                d = x * x + y * y + z * z
                if d > 9:
                    self.character.checkSkillRaise("Swimming")
                    self.lastSwimPos = self.simObject.position
                
                swim = float(self.skillLevels.get("Swimming",0.0))
                self.swimMove = .25 + swim / 100.0
            
            hb = self.skillLevels.get("Hold Breath",0)
            hb /= 3 #1 second every 3 points =333 possible seconds
            hb += 30 #30 base seconds
            
            if self.simObject.waterCoverage >= 1.0 and not (self.waterBreathing > 0):
                self.underWater += .5
                if self.underWater > 999999:
                    self.underWater = 999999
                
                self.holdBreathTimer -= 3
                if self.holdBreathTimer <= 0:
                    self.holdBreathTimer = 60 #10 seconds
                    self.character.checkSkillRaise("Hold Breath",5,10)
                    if hb < self.underWater:
                        damage = int((self.underWater - hb) * 4.5)
                        if damage < 15:
                            damage = 15
                        Damage(self,None,damage,RPG_DMG_PHYSICAL, None,False,False)
                        self.player.sendGameText(RPG_MSG_GAME_DENIED,"%s drowns for %i points of damage!\\n"%(self.name,damage))
            
            else:
                if self.underWater > 30:
                    self.underWater = 30
                self.underWater -= .5
                if self.underWater < 0:
                    self.underWater = 0
            
            if self.underWater and not self.waterBreathing:
                self.underWaterRatio = (float(hb) - float(self.underWater)) / hb
                if self.underWaterRatio > 1.0:
                    self.underWaterRatio = 1.0
                elif self.underWaterRatio < .01:
                    self.underWaterRatio = .01
            else:
                self.underWaterRatio = 1.0
            
            # Check eat and drink timers. If hungry also check
            #  if we have gained food/water in the meantime
            self.drinkTimer -= 3 * self.race.consumeWater
            if self.drinkTimer <= 0:
                self.character.drink()
                self.drinkTimer = durMinute * 10
            elif self.thirsty:
                self.character.drink(False)
            self.eatTimer -= 3 * self.race.consumeFood
            if self.eatTimer <= 0:
                self.character.eat()
                self.eatTimer = durMinute * 15
            elif self.hungry:
                self.character.eat(False)
            
            if self.unstickReuse:
                self.unstickReuse -= 3
                if self.unstickReuse < 0:
                    self.unstickReuse = 0
            
            if self.unstick:
                self.unstick -= 3
                if self.unstick <= 0:
                    self.unstick = 0
                    self.flying -= 1.0
            
            if self.rangedReuse > 0:
                self.rangedReuse -= 1
        
        # Handle non-player mobs.
        else: 
            self.tacticalTimer -= 3 
            if self.tacticalTimer <= 0:
                self.tactical.tick()
                self.tacticalTimer = 12 #once every 2 seconds
            
            if self.despawnTimer:
                self.despawnTimer -= 3
                if not self.despawnTimer:
                    self.zone.removeMob(self)
                    return
            
            if not self.battle:
                zombie = not len(self.aggro)
                
                if self.master:
                    zombie = self.master.zombie
                
                #this could probably be improved, any active spell keeps a mob
                #from being a zombie
                if len(self.processesPending) or len(self.processesIn):
                    zombie = False
                
                if zombie != self.zombie:
                    self.zombie = zombie
                    self.mobInfo.refresh()
                
                if zombie:
                    if not self.preventZombieRegen:
                        self.health = self.maxHealth
                        self.mana = self.maxMana
                        self.stamina = self.maxStamina
                    if self.casting:
                        self.casting.cancel()
                    return
            
            self.isFeared = self.simObject.canKite and self.fear > 0
            
            #aiskills
            if not self.master and self.target and not self.combatInhibited and len(self.aiSkills):
                self.aiSkillTimer -= 3
                if self.aiSkillTimer <= 0:
                    self.aiSkillTimer = 72
                    for sk in self.aiSkills:
                        if not self.skillReuse.has_key(sk.skillname):
                            if not randint(0,2):
                                UseSkill(self,self.target,sk.skillname)
                                # Make sure reuse gets always set for mobs.
                                self.skillReuse[sk.skillname] = sk.reuseTime
            
            if self.master:
                master = self.master
                self.petSpeedMod = master.move * 1.1 - self.move
                if self.petSpeedMod < 0.0:
                    self.petSpeedMod = 0.0
                self.speedMod = master.speedMod
                self.flying = master.flying
                self.light = 0
                self.visibility = master.visibility
        
        if len(self.itemRequireTick):
            for item in self.itemRequireTick.copy().iterkeys():
                if not item.tick():
                    try:
                        del self.itemRequireTick[item]
                    # Already removed by item deletion.
                    except KeyError:
                        continue
        
        if len(self.xpDamage):
            tm = sysTime()
            remove = []
            for damager,xpdmg in self.xpDamage.iteritems():
                if tm - xpdmg.lastTime > 60:
                    #every minute that we haven't done any damage reduces damage by 80%
                    xpdmg.lastTime = tm
                    xpdmg.amount *= .8
                    
                    if xpdmg.amount < 1:
                        remove.append(damager)
            
            map(self.xpDamage.__delitem__,remove)
        
        #worn procs
        self.wornTimer -= 3
        if self.wornTimer <= 0:
            self.wornTimer = 180
            spellProcs = self.itemSetSpells.get(RPG_ITEM_TRIGGER_WORN, [])[:]
            spellsGetter = attrgetter('spells')
            map(spellProcs.extend,imap(spellsGetter,self.worn.itervalues()))
            
            for ispell in spellProcs:
                if ispell.trigger == RPG_ITEM_TRIGGER_WORN:
                    if ispell.frequency <= 1 or not randint(0,ispell.frequency):
                        proto = ispell.spellProto
                        
                        if proto.target == RPG_TARGET_SELF:
                            tgt = self
                        elif proto.target == RPG_TARGET_PARTY:
                            tgt = self
                        elif proto.target == RPG_TARGET_ALLIANCE:
                            tgt = self
                        elif proto.target == RPG_TARGET_PET:
                            tgt = self.pet
                        else:
                            tgt = self.target
                        if tgt:
                            SpawnSpell(proto,self,tgt,tgt.simObject.position,1.0,proc=True)
        
        #combat tick
        self.combatTimer -=3
        if self.combatTimer < 0:
            self.combatTimer = 0
        
        #regen tick
        self.regenTimer -= 3
        if self.regenTimer <= 0:
            self.regenTimer = 36
            #racial regen
            if self.player:
                if not self.combatTimer or self.regenCombat:
                    hr = float((12*self.race.regenHealth+((self.race.regenHealth*self.bdy/50)*(self.plevel/10.0))+self.plevel/2)*(self.regenHealthScalar))*2.0
                    mr = float(((self.race.regenMana+self.plevel/2)*(self.regenManaScalar))*2.0)+(self.pre/2*2.0)
                    sr = float((12*self.race.regenStamina+((self.race.regenStamina*self.bdy/50)*(self.plevel/4.0))+self.plevel)*(self.regenStaminaScalar))*2.0

                    hr+=int(self.regenHealth*self.regenHealthScalar)*2
                    mr+=int(self.regenMana*self.regenManaScalar)*2
                    sr+=int(self.regenStamina*self.regenStaminaScalar)
                    
                    if self.combatTimer:
                        hr*=self.regenCombat
                        mr*=self.regenCombat
                        sr*=self.regenCombat
                        
                    if not self.thirsty and not self.hungry:
                        self.stamina+=sr
                        
                    self.mana+=mr
                    self.health+=hr
                        
                # if regeneration is negative, continue draining even while attacking
                else:
                    if self.regenHealth < 0:
                        self.health += int(self.regenHealth*self.regenHealthScalar)*2
                    if self.regenMana < 0:
                        self.mana += int(self.regenMana*self.regenManaScalar)*2
                    if self.regenStamina < 0:
                        self.stamina += int(self.regenStamina*self.regenStaminaScalar)
            else:
                self.stamina = self.maxStamina
                if not self.attacking:
                    # 30 seconds every 10 levels or so
                    d = float(((self.plevel / 10 + 1) * 30)) / 6
                    
                    h = self.maxHealth / d
                    if h < 3:
                        h = 3
                    self.health += h
                    
                    m = self.maxMana / d
                    if m < 3:
                        m = 3
                    self.mana += m
                
                self.health += int(self.regenHealth)
                self.mana += int(self.regenMana)
            
            if self.thirsty:
                self.stamina -= 2
            if self.hungry:
                self.stamina -= 2
            if self.stamina < 0:
                self.stamina = 0
        
        
        if len(self.processesPending):
            # Start all pending processes that still have a source
            #  and destination assigned.
            for p in self.processesPending:
                if p.src and p.dst:
                    if p.dst.player:
                        p.dst.player.cinfoDirty = True
                    if p.src.player:
                        p.src.player.cinfoDirty = True
                    p.begin()
            self.processesPending.clear()
        
        # copy list because it's being modifed during loop
        if len(self.processesIn):
            for p in self.processesIn.copy():
                if not p.iter:
                    continue
                
                p.tickCounter -= 3
                if p.tickCounter <= 0:
                    p.tickCounter = p.tickRate
                    try:
                        p.iter.next()
                    except StopIteration:
                        p.end()
                        if self.player:
                            self.player.cinfoDirty = True
                    except:
                        traceback.print_exc()
                        p.end()
                        if self.player:
                            self.player.cinfoDirty = True
        
        rm = []
        if len(self.recastTimers):
            for sproto,tm in self.recastTimers.iteritems():
                if self.casting and self.casting.spellProto == sproto:
                    continue
                tm -= 3
                if tm <= 0:
                    if self.player:
                        self.player.cinfoDirty = True
                    
                    rm.append(sproto)
                else:
                    self.recastTimers[sproto] = tm
        
        map(self.recastTimers.__delitem__,rm)
        
        # tick reuse timers
        if len(self.skillReuse):
            reuse = {}
            for skill,v in self.skillReuse.iteritems():
                v -= 3
                if v > 0:
                    reuse[skill] = v
                elif self.player:
                    self.player.cinfoDirty = True
            self.skillReuse = reuse
        
        if self.casting:
            #remove function call
            if self.sleep > 0 or self.stun > 0 or self.isFeared or 0 < self.suppressCasting:
                self.zone.simAvatar.mind.callRemote("casting",self.simObject.id,False)
                if self.player:
                    self.player.sendGameText(RPG_MSG_GAME_DENIED,r'$src\'s casting failed $srche is in no condition to cast a spell!\n',self)
                self.casting = None
            else:
                self.casting.timer -= 3
                if self.casting.timer <= 0:
                    try:
                        if self.casting.tick():
                            self.casting = None
                    except:
                        traceback.print_exc()
                        try:
                            self.casting.cancel()
                        except:
                            traceback.print_exc()
                        self.casting = None
        
        
        #for now don't update non player
        #grab current mods
        
        
        # Restore characters health, mana and stamina after
        #  zoning or logging. Has to be done after starting
        #  pending processes since these include reloaded buffs.
        # Maybe better to move this out of the tick function though.
        if self.character:
            if self.derivedDirty or self.character.stamina != -999999:
                self.updateDerivedStats()
                if self.character.stamina != -999999:
                    self.stamina = self.character.stamina
                    self.mana = self.character.mana
                    self.health = self.character.health
                    self.character.stamina = self.character.health = self.character.mana = -999999
        
        
        self.mobInfo.refresh()
        
        
        # Clamp Health.
        if self.health < 0:
            self.health = 0
        elif self.health > self.maxHealth:
            self.health = self.maxHealth
        
        # Clamp Mana.
        if self.mana < 0:
            self.mana = 0
        elif self.mana > self.maxMana:
            self.mana = self.maxMana
        
        # Clamp Stamina.
        if self.stamina < 0:
            self.stamina = 0
        elif self.stamina > self.maxStamina:
            self.stamina = self.maxStamina
        
        
        if self.health == 0:
            # No more health, so die.
            self.die()
        else:
            # we aren't dead
            if not self.target:
                self.tookDamage = self.combatInhibited = 0
            if self.tookDamage and self.combatInhibited > 6:  # missed 6 attack opps
                self.combatInhibited = 0
                # warp to target
                
                #if not self.player and self.move > 0 and not self.simObject.canKite:
                #    self.zone.simAvatar.mind.callRemote("warp",self.simObject.id, self.target.simObject.id)
                
            else:
                #todo ai pets
                # Only handle pet warping if pet isn't feared, stunned, asleep or rooted and
                #  master isn't feared either.
                # Only warp player pets.
                if self.master and self.master.player:
                    if not self.isFeared and self.stun <= 0 and self.move > 0 and self.sleep <= 0 and not self.master.isFeared:
                        # If pet isn't fighting make sure pet keeps up with master.
                        if not self.target and (GetRange(self,self.master) > 20 or self.simObject.id not in self.master.simObject.canSee) and (self.followTarget == self.master):
                            self.simObject.position = self.master.simObject.position
                            self.zone.simAvatar.mind.callRemote("warp",self.simObject.id, self.master.simObject.id)
            
            self.tookDamage = False
            
            if self.mobSpells:
                self.mobSpells.think()
    
    
    def testAFX(self,effect,target=None):
        if not target:
            target = self
        self.zone.simAvatar.mind.callRemote("newSpellEffect",target.simObject.id,effect,False)
    
    
    def removeCorpse(self):
        if self.looter and self.zone == self.looter.zone and self.corpseCount < 5:
            self.corpseRemoval = reactor.callLater(30,self.removeCorpse)
            self.corpseCount += 1
            return
        
        self.corpseRemoval = None
        self.zone.removeMob(self)
    
    
    ## @brief The Mob has died.
    #  @param self (Mob) The object pointer.
    #  @param immortalOverride (Boolean) Flag if invulnerability should be
    #                          overridden.
    #  @return None.
    #  @bug TWS: Should the master and the pet have a combined damage count when
    #        calculating who did the most damage?
    #  @bug TWS: Player initiate list does not look like it is multi-character
    #        party friendly.
    def die(self, immortalOverride=False):
        
        # Don't let invulnerable Mobs die, unless an immortal commands so.
        if self.invulnerable > 0 and not immortalOverride:
            self.health = 1
            return
        
        # Play the screaming death.
        snd = self.spawn.getSound("sndDeath")
        if snd:
            self.playSound(snd)
        else:
            self.vocalize(VOX_DEATH)
        
        # The Mob has died, so disable auto attack.
        self.autoAttack = False
        
        # Detach this dead Mob from the zone. This will prevent the
        #  ZoneInstance from calling management routines on the dead Mob.
        self.zone.detachMob(self)
        
        # If this Mob was a player pet, give feedback to the master and directly
        #  remove the pet's corpse, player pets don't leave corpses and give no xp.
        if self.master and self.master.player:
            self.master.player.sendGameText(RPG_MSG_GAME_PET_SPEECH, \
                 "Your pet screams, \"I'm a goner master!!!\"\\n")
            self.removeCorpse()
            return
        
        # Used to compare damage amounts done by each damager.
        most = 0
        
        # The Mob that did the most damage to this Mob.
        killer = None
        
        # Iterate over this Mob's xpDamage dictionary to determine which
        #  damager gets the kill reward.
        for damager,xpdmg in self.xpDamage.iteritems():
            
            # If the amount of damage the damager did is higher than the highest
            #  damage amount, then update the damager as the new killer.
            if xpdmg.amount > most:
                most = xpdmg.amount
                killer = damager
        
        # If a pet did the most damage, then reassign the pet's master as
        #  the source for the damage.
        if killer and killer.master:
            killer = killer.master
        
        # Get a handle to this Mob's Player.
        player = self.player
        
        # If there is a Mob that did damage to this Mob, the killer is a Player
        #  and this Mob is not part of a battle.
        if killer and killer.player and not self.battle:
            
            # Store who killed this Mob.
            self.kingKiller = killer
            self.kingTimer = durMinute * 2
            
            # If this dead Mob is a Player Mob
            if player:
                
                # Reward the kill to the killing Player's Alliance.
                if killer.player.alliance.rewardKillXP(killer.player,self):
                    
                    # Get a handle to this Mob's Players's guildname.
                    guildname = player.guildName
                    
                    # If there is a guild name, alter the text that will be
                    #  used for the kill message.
                    if guildname:
                        guildname = ' of %s'%guildname
                    
                    # Create the kill message that will be sent to Players.
                    killmsg = "%s has killed %s%s!!!\\n"% \
                              (killer.character.name,self.name,guildname)
                    
                    # For all Players in the zone, send a message about this
                    #  Character Mob being killed.
                    for p in self.zone.players:
                        p.sendGameText(RPG_MSG_GAME_YELLOW,killmsg)
            
            # Otherwise need to handle differently.
            else:
                
                # Get a handle to this Mob's spawn.
                spawn = self.spawn
                
                # If the spawn is flagged to give experience, reward it to the
                #  killer's alliance.
                if not spawn.flags&RPG_SPAWN_NOXP:
                    killer.player.alliance.rewardKillXP(killer.player,self)
                
                # Reward any faction points to the killer's alliance.
                killer.player.alliance.rewardKillFaction(killer.player,self)
                
                # If the spawn has an automatic respawn assigned, respawn now.
                if spawn.respawn and self.spawnpoint:
                    self.spawnpoint.spawnMobByName(spawn.respawn.name)
                    return
                
                # If this spawn is flagged to leave no corpse, immediately
                #  remove it.
                if spawn.flags&RPG_SPAWN_NOCORPSE:
                    self.removeCorpse()
                
                # Otherwise schedule corpse removal.
                else:
                    self.zone.simAvatar.mind.callRemote("die",self.simObject.id)
                    self.corpseRemoval = reactor.callLater(180,self.removeCorpse)
                    self.genLoot = not (self.master or self.spawn.respawn)
        
        # This Mob either has no killer, is part of a battle or was killed by a
        #  non-Player pet / non-Player Mob.
        else:
            
            # If there was no killer or the killer was not a player, then this
            #  Mob's Character is going to lose experience for the death.
            if player:
                
                # Calculate the experience lost factor based on the Mob's level.
                factor = float(self.level) / 50.0
                
                # Clamp the factor to be at least 1.0.
                if factor < 1.0:
                    factor = 1.0
                
                # Make this Mob's Character lose experience.
                self.character.loseXP(factor)
            
            # Directly remove the Mob's corpse if we get here with a non-Player Mob.
            else:
                self.removeCorpse()
        
        # A Character's Mob may be reattached from a resurrection. In order
        #  to prevent battle data from carrying over, such as damager information
        #  and hate list, perform some cleanup.
        if player:
            
            # Get a handle to this Mob's Character.
            character = self.character
            
            # Flag this Mob's Character as dead.
            character.dead = True
            
            # Get a handle to this Mob's SimGhost.
            so = self.simObject
            
            # Create transform based on the Mob's position and rotation.
            transform = list(so.position)
            transform.extend(list(so.rotation))
            transform[-1] = degrees(transform[-1])
            
            # Required to prevent doxygen warning:
            ## @var deathZone
            ## @brief (Persistent Zone) Zone in which the Character's most
            #         recent death occured.
            
            # Store the Zone in which this Character died.
            ## @brief (Persistent Zone) Zone in which the Character's most
            #         recent death occured.
            character.deathZone = self.zone.zone
            
            # Store the transform at which this Character died.
            ## @brief (Persistent String) Transform storing the Character's
            #         most recent death position and rotation.
            character.deathTransform = transform
            
            # If this server only supports single Character parties, death
            #  markers are supported. Clear any old death markers if needed.
            if CoreSettings.MAXPARTY == 1:
                self.zone.world.clearDeathMarker(player)
            
            # Make sure to reset health (for /suicide), mana and stamina.
            # Need to reset on Mob for displaying purposes and on Character
            #  for respawns in same zone.
            self.health = 1
            character.health = 1
            self.mana = 1
            character.mana = 1
            self.stamina = 1
            character.stamina = 1
            
            # Clear the damager information.
            self.xpDamage.clear()
            
            # Clear the aggro information.
            self.aggro.clear()
            
            # Clear the Player aggro information.
            self.playerAggro.clear()
            
            # Iterate over the list of Players with whom this Player initiated
            #  combat.
            # TWS: This should be done even if the mob is never able to reattach.
            for otherPlayer,info in self.playerInitiate.iteritems():
                
                # Try to remove this Player from the other Player's initiated
                #  combat list.
                try:
                    del info[1].playerInitiate[player]
                # Just a safety precaution.
                # Not sure how to catch expired mobs, so catch all exceptions.
                except:
                    pass
            
            # Clear the list of Players that initiated combat with this Mob.
            self.playerInitiate.clear()
            
            # After a Character dies, the Character is invulnerable for one minute.
            # This helps to prevent death loops.
            # Use a spell store so effect gets applied on Mob (re)attach.
            SpellStore(character=character, \
                       spellProto=SpellProto.byName("Invulnerability"), \
                       time=0,mod=1.0,healMod=0.0,damageMod=0.0,level=1)
            
            # Check if this was the Player's current Character that died.
            if player.curChar == character:
                
                # Too bad, try to switch to a living Party member.
                # Iterate over this Player's Party members.
                for index,char in enumerate(player.party.members):
                    
                    # If the Character is alive, then break the loop. This will
                    #  cause the for-else clause to skip the else.
                    if not char.dead:
                        
                        # At least one Character in the Party is alive. Set the
                        #  current Character to the found non-dead Character.
                        player.curChar = char
                        
                        # Update the client to use the current Character.
                        player.mind.callRemote("setCurCharIndex",index)
                        
                        # Break out of the loop, skip the next else.
                        break
                
                # No more live Party members, so play death.
                else:
                    self.simObject.dyingMob = self
                    self.zone.simAvatar.mind.callRemote("die",self.simObject.id)
        
        # Check if we need to schedule a respawn for this Mob.
        elif self.spawnpoint:
            
            # Set a delay of 3 minutes plus 3 seconds every level.
            delay = 3 * (durMinute + durSecond * int(self.level))
            
            # Get a delay modifier based on server settings.
            d = (100.0 - CoreSettings.RESPAWNTIME) - 50.0
            if d > 0:
                d *= 4.0
            d /= 100.0
            
            # Apply the delay modifier to the delay.
            delay += int(d * delay)
            
            # Schedule the respawning.
            self.spawnpoint.setDelay(delay)
    
    
    def shootRanged(self):
        if self.character.dead:
            return
        
        player = self.player
        
        if RPG_SLOT_RANGED not in self.worn:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have a ranged weapon equipped.\\n"%self.name)
            return
        rangedWpn = self.worn[RPG_SLOT_RANGED]
        if not rangedWpn.isUseable(self) or rangedWpn.penalty:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot currently use this %s.\\n"%(self.name,rangedWpn.name))
            return
        if self.sleep > 0 or self.stun > 0  or self.isFeared:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"$src cannot use $srchis %s while asleep, stunned, or feared.\\n"%rangedWpn.name,self)
            return
        if self.rangedReuse > 0:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"$src can't reuse $srchis %s yet.\\n"%rangedWpn.name,self)
            return
        if not self.worn.has_key(RPG_SLOT_AMMO):
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"$src needs more ammunition for $srchis %s.\\n"%rangedWpn.name,self)
            return
        
        if self.target and self.target != self:
            if not AllowHarmful(self,self.target):
                return
            dist = GetRangeMin(self,self.target)
            if dist > rangedWpn.wpnRange:
                if player:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"Target is out of %s's bow range.\\n"%self.name)
                return
            
            ammo = self.worn[RPG_SLOT_AMMO]
            if dist > ammo.wpnRange:
                if player:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"%s's arrows won't fly that far.\\n"%self.name)
                return
            
            # Check that we are facing the target. +- 30 degrees. (wmrojer)
            if not self.isFacing(self.target,30.0):
                if player:
                    player.sendGameText(RPG_MSG_GAME_DENIED, \
                        "$src needs to face $srchis enemy to use the bow.\\n",self)
                return
            
            if not self.autoAttack or dist > 5.0:
                self.zone.simAvatar.mind.callRemote("playAnimation",self.simObject.id,"bowattack")
            
            self.cancelInvisibility()
            self.cancelStatProcess("flying", "$tgt can no longer fly!\\n")
            self.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
            
            p = Projectile(self,self.target)
            p.weapon = rangedWpn
            p.ammoDamage = ammo.wpnDamage
            p.ammoSpells = ammo.spells[:]
            p.projectile = ammo.projectile
            p.speed = ammo.speed
            p.launch()
            
            rangedWpn.reuseTimer = rangedWpn.wpnRate
            rangedWpn.itemInfo.refresh()
            self.rangedReuse = rangedWpn.reuseTimer
            self.itemRequireTick[rangedWpn] = rangedWpn.reuseTimer
            
            if player:
                ammo.stackCount -= 1
                if ammo.stackCount <= 0:
                    self.unequipItem(RPG_SLOT_AMMO)
                    player.takeItem(ammo)
                else:
                    ammo.itemInfo.refreshDict({'STACKCOUNT':ammo.stackCount})
        
        return
    
    
    def cast(self,spellProto,level=1):
        if self.casting:
            return
        
        self.casting = SpellCasting(self,spellProto,level)
        
        if not self.casting.begin():
            self.casting = None
        
        if self.casting and self.player:
            self.player.mind.callRemote("beginCasting",self.charIndex,self.casting.timer/6)
    
    
    def detachSelf(self):
        if self.detached:
            return
        
        self.detached = True
        
        self.attacking = False
        
        if self.battle:
            self.battle.detachMob(self)
        
        if self.casting:
            self.casting.cancel()
        
        for p in self.zone.players:
            if p.inn and p.inn.innkeeper == self:
                p.inn.endInteraction()
        
        if self.vendor:
            self.vendor.destroyStock()
        
        if self.pet:
            self.zone.removeMob(self.pet)
        
        if self.master:
            self.master.pet = None
            
            # Recalculate penalties on items in pet slots.
            if self.master.character and not self.master.detached:
                self.master.character.refreshPetItems()
        
        persistent = []
        selfPersistent = False
        if self.player and self.health > 0 and not self.character.dead:
            selfPersistent = True
            self.character.health = int(self.health)
            self.character.mana = int(self.mana)
            self.character.stamina = int(self.stamina)
        
        # save character items
        if self.character:
            self.character.backupItems()
        
        # Pending processes may occur if the mob is detached before a tick.
        # If this is the case, add persistent spells to the spell store.
        for p in self.processesPending.copy():
            if selfPersistent:
                if isinstance(p,Spell) and p.spellProto.spellType&RPG_SPELL_PERSISTENT:
                    if p in persistent:
                        traceback.print_stack()
                        print "AssertionError: pending process already in persistent processes!"
                        continue
                    persistent.append(p)
                    continue

            if not p.canceled:
                p.cancel()
                    
        for p in self.processesIn.copy():
            if selfPersistent:
                if isinstance(p,Spell) and p.spellProto.spellType&RPG_SPELL_PERSISTENT:
                    if p in persistent:
                        traceback.print_stack()
                        print "AssertionError: in process already in persistent processes!"
                        continue
                    persistent.append(p)
                    continue

            if not p.canceled:
                p.cancel()
        
        #we want to keep some of these, buffs to other players, etc
        for p in self.processesOut.copy():
            if isinstance(p,Spell) and p.spellProto.spellType&RPG_SPELL_PERSISTENT and p.dst and p.src and p.dst.player and p.src.player and p.dst!=self:
                if p in persistent:
                    traceback.print_stack()
                    print "AssertionError: out process already in persistent processes!"
                    continue
                persistent.append(p)
                continue
            if not p.canceled:
                p.cancel()
                if p.dst.player:
                    p.dst.player.cinfoDirty = True
        
        if len(persistent):
            for spell in persistent:
                if spell.dst == self:
                    #need to pickle this spell
                    SpellStore(spellProto=spell.spellProto,character=self.character,time=spell.time,mod=spell.mod,healMod=spell.healMod,damageMod=spell.damageMod,level=spell.level)
                    if spell.canceled:
                        spell.cancel()
                else:
                    #this is an outgoing spell, the dst needs to take ownership of it
                    spell.takeOwnership(spell.dst)
                    if spell not in spell.dst.processesIn or spell in spell.dst.processesOut:
                        traceback.print_stack()
                        print "AssertionError: spell process ownership whackiness!"
                        continue
                    
                    spell.dst.processesOut.add(spell)

        self.processesPending.clear()
        self.processesIn.clear()
        self.processesOut.clear()
    
    
    def detachMob(self, other):
        if not other.detached:
            traceback.print_stack()
            print "AssertionError: other mob not detached!"
            return
        
        try:
            del self.xpDamage[other]
        except KeyError:
            pass
        
        try:
            del self.aggro[other]
        except KeyError:
            pass
        
        if self.spellTarget == other:
            self.spellTarget = None
            if self.casting:
                self.casting.cancel()
        
        if self.followTarget == other:
            self.zone.setFollowTarget(self,None)
        
        for p in self.processesIn.copy():
            if p.src == other or p.dst == other:
                p.cancel()
        
        for p in self.processesOut.copy():
            if p.src == other or p.dst == other:
                p.cancel()
        
        for p in self.processesPending.copy():
            if p.src == other or p.dst == other:
                self.processesPending.discard(p)
        
        if self.target == other:
            self.attacking = False
            target = other
            self.target = None
            if self.battle:
                self.battle.updateMobTarget(self)
            # Immediately tick tactical so we don't have Mobs walking
            #  away and coming back after the update.
            self.tactical.tick()
            if not self.target:
                self.target = other
                self.zone.setTarget(self,None)
    
    
    def cancelAttack(self):
        self.attacking = False
        for p in self.processesPending:
            if isinstance(p,CombatProcess):
                self.processesPending.discard(p)
                break
        
        for p in self.processesOut:
            if isinstance(p,CombatProcess):
                p.cancel()
                break
        
        self.mobInfo.refresh()
    
    
    def attackOn(self):
        #self.zone.simAvatar.mind.callRemote("setAttacking",self.simObject.id,True)
        
        #already attacking?    
        resetPetCounter = True
        for p in self.processesOut:
            if isinstance(p,CombatProcess):
                if p.src == self and p.dst == self.target:
                    return #already attacking
                p.cancel()
                resetPetCounter = False
                break
                
        self.cancelAttack()
        
        if not AllowHarmful(self,self.target):
            return
                
        if self.target:
            #attack target
            self.processesPending.add(CombatProcess(self,self.target))
            if self.target.id in self.combatIds: #this is so you can't rapidly switch
                self.primaryAttackTimer = 30
                self.secondaryAttackTimer = 30
            else:
                self.combatIds.insert(0,self.target.id)
                self.combatIds = self.combatIds[0:50] #last 50
                
            self.attacking = True
            self.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
            if resetPetCounter:
                self.petCounter = 0
        self.mobInfo.refresh()
    
    
    def attackOff(self):
        #self.zone.simAvatar.mind.callRemote("setAttacking",self.simObject.id,False)
        self.attacking = False
        self.cancelAttack()
    
    
    def setTarget(self, target):
        if target and not self.player and target != self.target:
            msg = None
            #find an appropriate attack message if any
            if target.player:
                pfactions = target.character.characterFactions
            
            for f in self.spawn.factions:
                for r in f.relations:
                    if r.relation < 0:
                        if target.player:
                            for pf in pfactions:
                                if pf.points > 0 and pf.faction == r.otherFaction:
                                    msg = r.otherFaction.enemyMsg
                                    break
                            if msg:
                                break
                        elif target.spawn in r.otherFaction.spawns:
                            msg = r.otherFaction.enemyMsg
                            break
                if msg:
                    break
            
            if not msg and target.player:
                #look for an attack message
                for f in self.spawn.factions:
                    for pf in pfactions:
                        if pf.faction == f and pf.points < 0:
                            msg = f.attackMsg
                            break
                    if msg:
                        break
            
            if msg:
                msg = r'%s screams, \"%s\"\n'%(self.spawn.name,msg)
                GameMessage(RPG_MSG_GAME_SPELLBEGIN,self.zone,self,target,msg,self.simObject.position,20)
        
        self.target = target
        if self.player:
            if self.player.interacting != target:
                self.player.endInteraction()
            if target:
                kos = IsKOS(target,self)
                if not kos:
                    self.autoAttack = False
                    self.attackOff()
        else:
            self.autoAttack = target and self.aggro.has_key(target)
        
        if self.autoAttack and target:
            self.attackOn()
        else:
            self.attackOff()
    
    
    def setFollowTarget(self, followTarget):
        self.followTarget = followTarget
    
    
    
    # ---------------------------------------------------------------------------
    # Effect tie-ins
    
    # Nonlinear stacking means that the strongest effect will count
    #  with 100%, the second strongest at 50%, the third at 25% and
    #  so on.
    # Apply this special stacking rule to all stats listed in
    #  EFFECTSTACK_NONLINEAR in effect.py. This function here doesn't
    #  check if the supplied effect is indeed in that tuple though.
    
    # A nonlinearly stacking effect got activated.
    # If positive is true, all negative effects will count 100% and
    #  vice versa. This function only works as it should on effect
    #  applications done by it. Also make sure to clear such an effect
    #  with doEffectUnstackNonlinear if no longer used.
    def doEffectStackNonlinear(self, statname, value, positive=True):
        # Get all data on currently existing effects of the same stat.
        effectData = self.effectStackNonlinear.setdefault(statname,[[],0])
        # Add the new value to the effect list.
        effectData[0].append(value)
        
        # Calculate the new effect value.
        newValue = 0
        valMod = 1.0
        if positive:
            for v in sorted(effectData[0],reverse=True):
                if v > 0:
                    newValue += valMod * float(v)
                    valMod *= 0.5
                else:
                    newValue += v
        else:
            for v in sorted(effectData[0]):
                if v < 0:
                    newValue += valMod * float(v)
                    valMod *= 0.5
                else:
                    newValue += v
        
        # Get the current modifier on the mob, subtract previous
        #  stat effect and add new one.
        final = getattr(self,statname) - effectData[1] + newValue
        # Clamp new attribute value in a small range to zero,
        #  so comparison against zero doesn't fail even with
        #  floating point precision problems.
        if abs(final) < 0.0009:
            final = 0
        # Apply the effect to this mob.
        setattr(self,statname,final)
        # Store the new stat effect in the stacking dictionary.
        effectData[1] = newValue
    
    
    # A nonlinearly stacking effect got deactivated.
    # If positive is true, all negative effects will count 100% and
    #  vice versa.
    def doEffectUnstackNonlinear(self, statname, value, positive=True):
        # Get all data on currently existing effects of the same stat.
        try:
            effectData = self.effectStackNonlinear[statname]
        except KeyError:
            traceback.print_exc()
            return
        # Remove the provided value from the effect list.
        try:
            effectData[0].remove(value)
        except:
            traceback.print_exc()
            return
        
        # Calculate the new effect value.
        newValue = 0
        valMod = 1.0
        if positive:
            for v in sorted(effectData[0],reverse=True):
                if v > 0:
                    newValue += valMod * float(v)
                    valMod *= 0.5
                else:
                    newValue += v
        else:
            for v in sorted(effectData[0]):
                if v < 0:
                    newValue += valMod * float(v)
                    valMod *= 0.5
                else:
                    newValue += v
        
        # Get the current modifier on the mob, subtract previous
        #  stat effect and add new one.
        final = getattr(self,statname) - effectData[1] + newValue
        # Clamp new attribute value in a small range to zero,
        #  so comparison against zero doesn't fail even with
        #  floating point precision problems.
        if abs(final) < 0.0009:
            final = 0
        # Update the effect on this mob.
        setattr(self,statname,final)
        # Store the new stat effect in the stacking dictionary.
        effectData[1] = newValue
    
    
    def cancelInvisibility(self):
        gotone = False
        for p in self.processesIn.copy():
            if isinstance(p,Spell) and p.grantsInvisibility():
                gotone = True
                p.cancel()
        
        if gotone and self.player:
            self.player.sendGameText(RPG_MSG_GAME_BLUE,"%s appears!\\n"%self.name)
    
    
    def cancelFlying(self):
        if not self.player:
            return
        gotone = False
        for p in self.processesIn.copy():
            if isinstance(p,Spell) and p.grantsFlying():
                gotone = True
                p.cancel()
        
        if gotone and self.player:
            self.player.sendGameText(RPG_MSG_GAME_BLUE,"%s can no longer fly!\\n"%self.name)
    
    
    def cancelSleep(self):
        for p in self.processesIn.copy():
            if isinstance(p,Spell) and p.hasSleep():
                p.cancel()
    
    
    def cancelStatProcess(self, stat, msg=None):
        processes = []
        for p in self.processesIn:
            if isinstance(p,Spell):
                for e in p.effects:
                    for st in e.effectProto.stats:
                        if st.stage == RPG_EFFECT_STAGE_GLOBAL:
                            if st.statname == stat:
                                processes.append(p)
        
        map(Process.cancel,processes)
        
        if len(processes) and msg and self.player:
            msg = msg.replace("$tgt",self.name)
            self.player.sendGameText(RPG_MSG_GAME_BLUE,msg)
    
    # ---------------------------------------------------------------------------
    
    
    
    def cancelProcess(self,pid):
        for p in self.processesIn:
            if p.pid == pid:
                p.cancel()
                break
    
    
    #this is called once mob has been spawned on simserver, and is moving to active
    def spawned(self):
        #hook up pet
        if self.master:
            self.master.petSpawning = False
            if self.master.pet:
                self.zone.removeMob(self.master.pet)
            self.master.pet = self
            self.battle = self.master.battle
            
            from mud.world.pet import PetCmdFollowMe
            PetCmdFollowMe(self)
            
            if self.master.character:
                self.master.character.setPetEquipment()
                
            self.mobInfo.refresh()
    
    
    def addAggro(self, other, amount, recurse=True):
        if self.spawn.flags&RPG_SPAWN_RESOURCE:
            return 
        try:
            if other.detached:
                traceback.print_stack()
                print "AssertionError: other mob is detached!"
                return
        except:
            traceback.print_exc()
            return
        
        if self == other:
            return
        
        selfPlayer = None
        selfPlayerMob = None
        if self.player:
            selfPlayer = self.player
            selfPlayerMob = self
        elif self.master and self.master.player:
            selfPlayer = self.master.player
            selfPlayerMob = self.master
        otherPlayer = None
        otherPlayerMob = None
        if other.player:
            otherPlayer = other.player
            otherPlayerMob = other
        elif other.master and other.master.player:
            otherPlayer = other.master.player
            otherPlayerMob = other.master
        
        if not AllowHarmful(self,other):
            if selfPlayer and otherPlayer:
                try:
                    del selfPlayerMob.playerAggro[otherPlayer]
                except KeyError:
                    pass
                try:
                    del otherPlayerMob.playerInitiate[selfPlayer]
                except KeyError:
                    pass
                try:
                    del selfPlayerMob.playerInitiate[otherPlayer]
                except KeyError:
                    pass
            try:
                del self.aggro[other]
            except KeyError:
                pass
            return
        
        if selfPlayer and otherPlayer:
            if not self.playerInitiate.has_key(otherPlayer):
                # other initiated combat, mark as such
                self.playerInitiate[otherPlayer] = (False,otherPlayerMob)
                otherPlayerMob.playerInitiate[selfPlayer] = (True,self)
            selfPlayerMob.playerAggro[otherPlayer] = 0
        
        self.aggro[other] += amount
        
        if recurse:
            if self.pet:
                self.pet.addAggro(other,amount/2+1,False)
            elif self.master:
                self.master.addAggro(other,amount/2+1,False)
        
        self.preventZombieRegen = False
    
    
#vocals

    def playSound(self, sound, player=None):
        try:
            sound = sound.lower()
            if "$vocalize" in sound:
                #v,vox = sound.split("/")
                self.vocalize(VOX_DEATH,player) #todo add more if needed
        except:
            return
        
        if player:
            #to specific client only
            player.mind.callRemote("playSound",sound)
        else:
            #otherwise 3d
            bigSound = 4 < self.spawn.modifiedScale
            self.zone.simAvatar.mind.callRemote("playSound",sound,self.simObject.position,bigSound)
    
    
    def vocalize(self, vox, player=None):
        vocals = self.vocals
        if not vocals:
            return
        
        sex = 1 if self.sex == 'Female' else 0
        
        if not vocals[vox]:
            print "warning: spawn %s is being asked to vocalize with no vocals for vox %i"%(self.spawn.name,vox)
            return
        
        which = randint(1,vocals[vox])
        
        if player:
            #to specific client only
            player.mind.callRemote("vocalize",sex,self.vocalSet,vox,which)
        else:
            #otherwise 3d
            self.zone.simAvatar.mind.callRemote("vocalize",sex,self.vocalSet,vox,which,self.simObject.position)
    
    
    def onImpact(self, invelocity):
        if self.detached:
            return
        
        acro = self.skillLevels.get("Acrobatics",0)
        
        if invelocity < 15:
            if acro:
                self.character.checkSkillRaise("Acrobatics",1)
            return
        
        #50 is huge
        #200
        
        velocity = invelocity * 2.5
        velocity -= acro / 10
        if velocity <= 0:
            self.character.checkSkillRaise("Acrobatics",4,20)
            return
        
        velocity = int(velocity)
        
        if acro:
            chance = velocity / 10
            if chance < 1:
                chance = 1
            if not randint(0,chance):
                self.character.checkSkillRaise("Acrobatics",1,2)
                return
        
        damage = (invelocity / 2) * (invelocity / 2)
        if velocity > 55:
            damage *= 6
        damage -= acro
        if damage < 10:
            damage = 10
        
        damage = Damage(self,None,damage,RPG_DMG_IMPACT, None,False,False)
        
        self.player.sendGameText(RPG_MSG_GAME_DENIED,"%s has fallen for %i points of damage!\\n"%(self.name,damage))
    
    
    # Returns True if we are facing the other mob (default +- 60 degrees).
    def isFacing(self, otherMob, maxAngle=60.0):
        if not otherMob:
            return False
        
        pos = self.simObject.position
        rot = self.simObject.rotation
        
        tpos = otherMob.simObject.position
        
        # Calculate the distance to the target.
        dposx = tpos[0] - pos[0]
        dposy = tpos[1] - pos[1]
        dposz = tpos[2] - pos[2]
        dz = sqrt(dposx * dposx + dposy * dposy + dposz * dposz)
        
        # Short circuit if we are right ontop of the other mob.
        if dz < 0.5:
            return True
        if dposy == 0.0 and dposx == 0.0:
            if dz > 2.0:
                # Too far above or below the other mob.
                return False
            else:
                return True
        
        # Calculate our facing angle.
        if rot[2] < 0.0:
            angle = degrees(-rot[3])
        else:
            angle = degrees(rot[3])
        if angle > 180.0:
            angle -= 360.0
        elif angle < -180.0:
            angle += 360.0
        
        # Calculate the angle towards the other mob.
        dxy = sqrt(dposx * dposx + dposy * dposy)
        nx = dposx / dxy
        ny = dposy / dxy
        if abs(nx) > abs(ny):
            if nx < 0.0:
                zangle = degrees(-acos(ny))
            else:
                zangle = degrees(acos(ny))
        else:
            if ny < 0.0:
                zangle = degrees(pi - asin(nx))
            else:
                zangle = degrees(asin(nx))
        
        # Calculate the Y-angle, above / below.
        nz = dposz / dz
        yangle = degrees(asin(nz))
        
        # Are we facing the other mob?
        fangle = angle - zangle
        if fangle < -180.0:
            fangle += 360.0
        elif fangle > 180.0:
            fangle -= 360.0
        fangle = abs(fangle)
        yangle = abs(yangle)
        if (fangle < maxAngle and yangle < maxAngle) or (fangle < 90 and dz < 2.0):
            return True
        
        return False
    
    
    # Returns True if you are behind the other mob facing it.
    def isBehind(self, otherMob, maxAngle=60.0):
        if not otherMob:
            return False
        
        pos = self.simObject.position
        rot = self.simObject.rotation
        
        tpos = otherMob.simObject.position
        trot = otherMob.simObject.rotation
        
        dposx = tpos[0] - pos[0]
        dposy = tpos[1] - pos[1]
        dposz = tpos[2] - pos[2]
        
        if dposy == 0.0 and dposx == 0.0:
            # Right on top of, so we can't be behind.
            return False
        
        # Calculate our facing angle.
        if rot[2] < 0.0:
            angle = degrees(-rot[3])
        else:
            angle = degrees(rot[3])
        if angle > 180.0:
            angle -= 360.0
        elif angle < -180.0:
            angle += 360.0
        
        # Calculate the other mobs facing angle.
        if trot[2] < 0.0:
            tangle = degrees(-trot[3])
        else:
            tangle = degrees(trot[3])
        if tangle > 180.0:
            tangle -= 360.0
        elif tangle < -180.0:
            tangle += 360.0
        
        # Calculate the angle towards the other mob.
        dxy = sqrt(dposx * dposx + dposy * dposy)
        nx = dposx / dxy
        ny = dposy / dxy
        if abs(nx) > abs(ny):
            if nx < 0.0:
                zangle = degrees(-acos(ny))
            else:
                zangle = degrees(acos(ny))
        else:
            if ny < 0.0:
                zangle = degrees(pi - asin(nx))
            else:
                zangle = degrees(asin(nx))
        
        # Calculate the Y-angle, above / below.
        dz = sqrt(dposx * dposx + dposy * dposy + dposz * dposz)
        nz = dposz / dz
        yangle = degrees(asin(nz))
        
        # Are we facing the other mob (or really close)?
        fangle = angle - zangle
        if fangle < -180.0:
            fangle += 360.0
        elif fangle > 180.0:
            fangle -= 360.0
        fangle = abs(fangle)
        yangle = abs(yangle)
        if (fangle < maxAngle and yangle < maxAngle) or (fangle < 90 and dz < 2.0) \
            or dz < 0.5:
            
            # Are we behind the other mob?
            bangle = angle - tangle
            if bangle < -180.0:
                bangle += 360.0
            elif bangle > 180.0:
                bangle -= 360.0
            bangle = abs(bangle)
            if (bangle < maxAngle) or (bangle < 90.0 and dz < 2.0):
                return True
        
        return False
