# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.persistent import Persistent
from mud.world.core import *
from mud.world.defines import *
from mud.world.effect import Effect
from mud.world.messages import GameMessage
from mud.world.process import Process
from mud.world.projectile import Projectile
from mud.worlddocs.utils import GetTWikiName

from collections import defaultdict
from math import ceil,floor
from random import randint
from sqlobject import *
from time import time as sysTime
import traceback



class SpellClass(Persistent):
    spellProto = ForeignKey('SpellProto')
    classname = StringCol()
    level = IntCol()

class SpellComponent(Persistent):
    spellProto = ForeignKey('SpellProto')
    itemProto = ForeignKey('ItemProto')
    count = IntCol()
    
class SpellParticleNode(Persistent):
    spellProto = ForeignKey('SpellProto')
    node = StringCol()
    particle = StringCol()
    texture = StringCol()
    duration = IntCol() 
    
class SpellExclusion(Persistent):
    spellProto = ForeignKey('SpellProto')
    otherProtoName = StringCol()
    #whether or not spellproto overwrites otherProto
    overwrites = BoolCol(default=False)
    
class SpellStore(Persistent):
    character = ForeignKey('Character')
    spellProto = ForeignKey('SpellProto')
    time = IntCol(default=0)
    mod = FloatCol(default=1.0)
    healMod = FloatCol(default=0.0)
    damageMod = FloatCol(default=0.0)
    level = IntCol(default=1)
    
class SpellProto(Persistent):
    name = StringCol(alternateID = True)
    spellType = IntCol(default = RPG_SPELL_HARMFUL|RPG_SPELL_AICAST|RPG_SPELL_PERSISTENT)
    
    filterClass = StringCol(default="")
    filterRealm = IntCol(default=-1)
    filterRace = StringCol(default="")
    filterLevelMin = IntCol(default=0)
    filterLevelMax = IntCol(default=1000)
    
    filterTimeStart = IntCol(default=-1)
    filterTimeEnd = IntCol(default=-1)
    
    target = IntCol(default = RPG_TARGET_SELF)
    
    castTime =   IntCol(default=30)
    recastTime = IntCol(default=60)
    failureTime = IntCol(default=0)
    
    duration = IntCol(default = 0)
    
    castRange = FloatCol(default=20)
    aoeRange = FloatCol(default=0)
    
    manaCost = IntCol(default=0) #for setting mana requirements
    manaScalar = FloatCol(default=1.0) #for scaling mana
    
    difficulty = FloatCol(default=1.0) #casting difficulty mod?
    skillname = StringCol(default="")
    
    classesInternal = MultipleJoin('SpellClass')
    componentsInternal = MultipleJoin('SpellComponent')
    effectProtosInternal = RelatedJoin('EffectProto')
    itemSpellsInternal = MultipleJoin('ItemSpell')
    
    spellbookPic = StringCol(default="")
    iconSrc = StringCol(default="")
    iconDst = StringCol(default="")
    
    castingMsg = StringCol(default="")
    beginMsg = StringCol(default="")
    tickMsg = StringCol(default="")
    endMsg = StringCol(default="")

    projectile  = StringCol(default="")
    projectileSpeed = FloatCol(default=0)
    
    particleCasting = StringCol(default="")
    particleBegin = StringCol(default="")
    particleTick = StringCol(default="")
    particleEnd = StringCol(default="")
    
    particleTextureCasting = StringCol(default="")
    particleTextureBegin = StringCol(default="")
    
    afxSpellEffectCasting = StringCol(default="")
    afxSpellEffectBegin = StringCol(default="")
    afxSpellEffectEnd = StringCol(default="")

    explosionBegin = StringCol(default="")
    
    sndCasting = StringCol(default = "")
    sndBegin = StringCol(default="")
    sndBeginDuration = IntCol(default=0)#looping sounds
    sndTick = StringCol(default="")
    sndEnd = StringCol(default="")
    
    leechTickMsg = StringCol(default="")
    drainTickMsg = StringCol(default="")
    regenTickMsg = StringCol(default="")
    damageMsg = StringCol(default="")
    
    desc = StringCol(default="")
    
    animOverride = StringCol(default="")
    particleNodesInternal = MultipleJoin("SpellParticleNode")
    
    exclusionsInternal = MultipleJoin("SpellExclusion")
    
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        #cache
        self.particleNodes = [(pn.node,pn.particle,pn.texture,pn.duration) for pn in self.particleNodesInternal]
        
        self.components = self.componentsInternal[:]
        self.classes = self.classesInternal[:]
        self.effectProtos = self.effectProtosInternal[:]
        self.itemSpells = self.itemSpellsInternal[:]
        
        self.exclusions = dict((e.otherProtoName,e.overwrites) for e in self.exclusionsInternal)
        
        #overall spell proto level, used for filtering what spells have an effect on what mobs
        self.level = 100
        if len(self.classes):
            self.level = min(self.classes,key=lambda obj:obj.level).level
        self.petCache = False  # False != None, init to False so we can check if already set or not
    
    
    def qualify(self,mob):
        if not len(self.classes):
            return True
        mclasses = (mob.pclass,mob.sclass,mob.tclass)
        mlevels = (mob.plevel,mob.slevel,mob.tlevel)
        for cl,level in zip(mclasses,mlevels):
            if not cl or not level:
                break
            for klass in self.classes:
                if klass.classname == cl.name and level >= klass.level:
                    return True
        return False
    
    
    def affectsStat(self,statname):
        for e in self.effectProtos:
            if e.affectsStat(statname):
                return True
        return False
    
    
    def _get_pet(self):
        if self.petCache == False:
            con = self._connection.getConnection()
            pet = con.execute("SELECT summon_pet_id FROM effect_proto WHERE id IN (SELECT effect_proto_id FROM effect_proto_spell_proto WHERE spell_proto_id=%i) AND summon_pet_id!=0 LIMIT 1;"%self.id).fetchone()
            if pet:
                from mud.world.spawn import Spawn
                self.petCache = Spawn.get(pet[0])
            else:
                self.petCache = None
        return self.petCache



RESISTTEXT = {
RPG_RESIST_PHYSICAL:"physical",
RPG_RESIST_MAGICAL:"magical",
RPG_RESIST_FIRE:"fire",
RPG_RESIST_COLD:"cold",
RPG_RESIST_POISON:"poison",
RPG_RESIST_DISEASE:"disease",
RPG_RESIST_ACID:"acid",
RPG_RESIST_ELECTRICAL:"electrical"
}



class Spell(Process):
    def __init__(self,src,dst,spellProto,mod=1.0,time=0,skill=None,doParticles=True,fromStore=False,level=1,proc=False):
        Process.__init__(self,src,dst)
        self.spellProto = spellProto
        self.time = time
        self.mod = mod
        self.spellEffectInfo = None #pb.Cacheable
        self.effects = []
        self.skill = skill
        self.doParticles = doParticles
        self.fromStore = fromStore
        self.level = level
        
        # Special healing and damage mods for effects.
        self.healMod = 0.0
        self.damageMod = 0.0
        # Don't apply damage or healing cast mods on skills and procs.
        if src and not skill and not proc:
            self.healMod = src.castHealMod
            self.damageMod = src.castDmgMod
    
    
    def globalPush(self):
        Process.globalPush(self)
    
    
    def begin(self):
        proto = self.spellProto
        src = self.src
        dst = self.dst
        time = self.time
        
        eprotos = proto.effectProtos[:]
        
        # Check resist based on spell proto level.
        # Low level spells on high level opponents will not land.
        if src.player and proto.spellType&RPG_SPELL_HARMFUL:
            if dst.plevel - proto.level > 30:
                src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> spell is too low level and has been resisted!\\n"%(GetTWikiName(proto.name),proto.name),src)
                self.cancel()
                return
        
        # Beneficial spells fail on player targets if target is too low level.
        # This restriction doesn't affect immortals or teleport spells.
        if not self.skill and dst.player and not proto.spellType&RPG_SPELL_HARMFUL and dst != src:
            if not src.player or src.player.role.name != "Immortal":
                if proto.level - dst.plevel > 20 and not self.hasTeleport():
                    dst.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> spell is too high level and will not hold on %s!\\n"%(GetTWikiName(proto.name),proto.name,dst.name),src)
                    if src.player:
                        src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> spell is too high level and will not take hold on %s!\\n"%(GetTWikiName(proto.name),proto.name,dst.name),src)
                    self.cancel()
                    return
        
        #todo check for partial resist based on effects
        
        #stackin'
        
        #filters
        passed = False
        if proto.filterLevelMax >= dst.plevel >= proto.filterLevelMin:
            passed = True
        
        if passed and proto.filterRealm != -1:
            passed = False
            if dst.spawn.realm == proto.filterRealm:
                passed = True
        
        if passed and proto.filterClass:
            passed = False
            if dst.pclassInternal == proto.filterClass:  # already checked level above
                passed = True
            elif dst.sclassInternal == proto.filterClass and proto.filterLevelMax >= dst.slevel >= proto.filterLevelMin:
                passed = True
            elif dst.tclassInternal == proto.filterClass and proto.filterLevelMax >= dst.tlevel >= proto.filterLevelMin:
                passed = True
        
        if passed and proto.filterRace:
            passed = False
            if dst.spawn.race == proto.filterRace:  # already checked level above
                passed = True
        
        if not passed:
            if src.player and not self.skill:
                src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> spell has no effect on %s!\\n"%(GetTWikiName(proto.name),proto.name,dst.name),src)
            self.cancel()
            return
        
        if proto.spellType&RPG_SPELL_HARMFUL:
            resisted = []
            for e in eprotos:
                resist = dst.resists.get(e.resist, 0)
                if resist > 0:
                    # we might possibly resist this effect, todo figure in mob level, etc
                    if randint(0,int(resist/2)) > 10:
                        resisted.append(e)
            for e in resisted:
                eprotos.remove(e)
            
            if not len(eprotos):
                if not self.skill:
                    if src.player:
                        txt = RESISTTEXT[resisted[0].resist]
                        src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> spell has been resisted!\\n"%(GetTWikiName(proto.name),proto.name),src)
                    if dst.player:
                        dst.player.sendGameText(RPG_MSG_GAME_DENIED,"%s resisted $src's <a:Spell%s>%s</a> spell!\\n"%(dst.character.name,GetTWikiName(proto.name),proto.name),src)
                else:
                    if src.player:
                        txt = RESISTTEXT[resisted[0].resist]
                        src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Skill%s>%s</a> skill has been resisted!\\n"%(GetTWikiName(self.skill),self.skill),src)
                    if dst.player:
                        dst.player.sendGameText(RPG_MSG_GAME_DENIED,"%s resisted $src's <a:Skill%s>%s</a> skill!\\n"%(dst.character.name,GetTWikiName(self.skill),self.skill),src)
                self.cancel()
                return
            
            if len(resisted):
                if src.player and not self.skill:
                    txt = RESISTTEXT[resisted[0].resist]
                    src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's %s spell was partially resisted!\\n"%(txt),src)
                if dst.player and not self.skill:
                    dst.player.sendGameText(RPG_MSG_GAME_DENIED,"%s partially resisted $src's <a:Spell%s>%s</a> spell!\\n"%(dst.character.name,GetTWikiName(proto.name),proto.name),src)
        
        
        # stacking!
        cancel = []
        for process in dst.processesIn.copy():
            if not isinstance(process,Spell):
                continue
            sp = process.spellProto
            if sp == proto:
                process.cancel()
                continue  # refresh
            
            if sp.name in proto.exclusions:
                if proto.exclusions[sp.name]:
                    # overwrites! (only cancel if we aren't excluded below)
                    cancel.append(process)
                    continue
                else:
                    if src.player:
                        src.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s <a:Spell%s>%s</a> spell is supressed by <a:Spell%s>%s</a>!\n'%(src.name,GetTWikiName(proto.name),proto.name,GetTWikiName(sp.name),sp.name))
                    if dst.player and src.player and dst.player != src.player:
                        dst.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s <a:Spell%s>%s</a> spell is supressed by <a:Spell%s>%s</a>!\n'%(src.name,GetTWikiName(proto.name),proto.name,GetTWikiName(sp.name),sp.name))
                    self.cancel()
                    return
            elif proto.name in sp.exclusions:
                if sp.exclusions[proto.name]:
                    if src.player:
                        src.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s <a:Spell%s>%s</a> spell is supressed by <a:Spell%s>%s</a>!\n'%(src.name,GetTWikiName(proto.name),proto.name,GetTWikiName(sp.name),sp.name))
                    if dst.player and src.player and dst.player != src.player:
                        dst.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s <a:Spell%s>%s</a> spell is supressed by <a:Spell%s>%s</a>!\n'%(src.name,GetTWikiName(proto.name),proto.name,GetTWikiName(sp.name),sp.name))
                    self.cancel()
                    return
                else:
                    cancel.append(process)
        
        for p in cancel:
            p.cancel()
        # message
        if proto.beginMsg and not dst.battle and not self.fromStore:
            GameMessage(RPG_MSG_GAME_SPELLBEGIN,src.zone,src,dst,proto.beginMsg+'\\n',src.simObject.position,20)
        
        for ep in eprotos:
            effect = Effect(self,src,dst,ep,time,self.mod,self.fromStore,self.healMod,self.damageMod)
            self.effects.append(effect)
        
        Process.begin(self)
        for e in self.effects:
            e.begin()
        
        
        # apply beginning stuff
        if self.time == 0:
            doEffects = True
            if src.player:
                if sysTime() - src.player.spellEffectBeginTime < 5:
                    doEffects = False
                else:
                    src.player.spellEffectBeginTime = sysTime()
            
            hasTP = self.hasTeleport()
            zone = self.src.zone
            
            if proto.afxSpellEffectBegin and not hasTP and self.doParticles and doEffects:
                zone.simAvatar.mind.callRemote("newSpellEffect",self.dst.simObject.id,proto.afxSpellEffectBegin,False)

            if proto.explosionBegin and not hasTP and self.doParticles and doEffects:
                zone.simAvatar.mind.callRemote("spawnExplosion",self.dst.simObject.id,proto.explosionBegin,0)
            
            if proto.particleBegin and not hasTP and self.doParticles and doEffects:
                t = 3000 #base this on emitter?
                #base this on failed time if necessary
                zone.simAvatar.mind.callRemote("newParticleSystem",self.dst.simObject.id,"SpellBeginEmitter",proto.particleTextureBegin,t)
            
            if proto.sndBegin and not hasTP and self.doParticles:
                if not proto.sndBeginDuration: #hack for dragons, atm
                    self.dst.playSound(proto.sndBegin)
        
        return True
    
    
    # generator function
    def tick(self):
        proto = self.spellProto
        while 1:
            if proto.duration == 0:
                yield True  # will exit next tick
            if self.time >= proto.duration:
                return
            
            self.time += 3
            
            for e in self.effects:
                e.iter.next()
            
            yield True
    
    
    def end(self):
        proto = self.spellProto
        src = self.src
        dst = self.dst
        for e in self.effects:
            e.end()
        if proto.endMsg and not dst.battle:
            GameMessage(RPG_MSG_GAME_SPELLEND,src.zone,src,dst,proto.endMsg+'\\n',dst.simObject.position,0)
        self.globalPop()
    
    
    def takeOwnership(self,newOwner):
        self.src = newOwner
        for e in self.effects:
            e.takeOwnership(newOwner)
    
    
    def cancel(self):
        if self.canceled:
            return
        self.canceled = True
        self.iter = None
        for e in self.effects:
            e.cancel()
        self.globalPop()
    
    
    def globalPop(self):
        for e in self.effects:
            e.globalPop()
        Process.globalPop(self)
    
    
    def grantsFlying(self):
        for e in self.effects:
            for st in e.effectProto.stats:
                if st.stage == RPG_EFFECT_STAGE_GLOBAL:
                    if st.statname == 'flying' and st.value > 0:
                        return True
        return False
    
    
    def grantsInvisibility(self):
        for e in self.effects:
            for st in e.effectProto.stats:
                if st.stage == RPG_EFFECT_STAGE_GLOBAL:
                    if st.statname == 'visibility' and st.value < 0:
                        return True
        return False
    
    
    def hasTeleport(self):
        for e in self.effects:
            if e.effectProto.teleport:
                return True
        return False
    
    
    def hasSleep(self):
        for e in self.effects:
            for st in e.effectProto.stats:
                if st.stage == RPG_EFFECT_STAGE_GLOBAL:
                    if st.statname == 'sleep':
                        return True
        return False


def CheckResist(src,dst,proto,skill=None):
    # R = .01 to .99   at  MYLEVEL = 100 DFDLEVEL = 1 (best)
    # R= 1.0  at  MYLEVEL = 100 DFDLEVEL = 100
    # R = 1.0 to 100 at MYLEVEL = 1 DFDLEVEL = 100 (worst)
    
    # Get value to check resist based on level difference, clamp low at 1.
    R = max(1,int(floor(GetLevelSpread(src, dst)*100)))
    
    if randint(0,R) > 90:
        if src.player:
            if skill:
                src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Skill%s>%s</a> skill has been resisted!\\n"%(GetTWikiName(skill),skill),src)
            else:
                src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> spell has been resisted!\\n"%(GetTWikiName(proto.name),proto.name),src)
        
        if dst.player and not skill:
            dst.player.sendGameText(RPG_MSG_GAME_DENIED,"$src resisted %s's <a:Spell%s>%s</a> spell!\\n"%(src.name,GetTWikiName(proto.name),proto.name),dst)
        
        return True
    
    return False


# and spell-like skills, beware!
def SpawnSpell(proto,src,dst,pos=(0,0,0),mod=1.0,skill=None,spellLevel=1,proc=False):
    
    if src.detached or dst.detached:
        return
    
    dstSimObject = dst.simObject

    # List of SimObjects that can be seen b the destination.
    simObjects = []    
    
    # If the proto has an AoE range, then iterate over all mobs the destination
    # can see.  Mobs are moving and updating their position while iterating, so
    # it is critical that this loop occur as soon as possible and be fast, 
    # caching positions to increase accurate processing.
    if proto.aoeRange:
        
        # Get a handle to the SimLookup dictionary.
        simLookup = src.zone.simAvatar.simLookup
        
        # Iterate over mobs the destination can see.
        for id in dstSimObject.canSee:
            try:
                simObject = simLookup[id]
                
                # Cache a copy of the position.
                simObjects.append((simObject, simObject.position[:]))
                
            except KeyError:
                continue  # Not spawned yet, though in cansee.
            
        # Add the destination to the list of SimObjects.  If the destination is
        # in range of the spell, it is guaranteed to be in range of the AE.
        simObjects.append((dstSimObject, pos))

    
    if proto.spellType&RPG_SPELL_HARMFUL:
        if src.character:
            src.cancelStatProcess("invulnerable", \
                "$tgt is no longer protected from death!\\n")
        
        if not proto.aoeRange:
            if not src.player:
                if not IsKOS(src,dst):
                    return
            elif not AllowHarmful(src,dst):
                if skill:
                    src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Skill%s>%s</a> skill failed, no valid target.\\n"%(GetTWikiName(skill),skill),src)
                else:
                    src.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> spell failed, no valid target.\\n"%(GetTWikiName(proto.name),proto.name),src)
                return
    
    srcPlayer = None
    if src.player:
        srcPlayer = src.player
    elif src.master and src.master.player:
        srcPlayer = src.master.player
    
    # Modify cast range by spell skill level, max + 20%.
    castRange = proto.castRange
    if proto.skillname:
        try:
            slevel = src.skillLevels[proto.skillname]
            diff = slevel - (proto.level - 2) * 10
            if diff > 0:
                if diff > 20:
                    diff = 20
                castRange += castRange * 0.2 * float(diff) / 20.0
        except KeyError:
            pass
    
    if proto.target == RPG_TARGET_OTHER:
        
        # The spell will fail if all of the following conditions are true:
        # - The source is a Player.
        # - The destination's player is not the source's player.
        # - The source cannot see the destination.
        if src.player and dst.player != src.player and dstSimObject.id not in src.simObject.canSee:
                if skill:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"<a:Skill%s>%s</a> failed, $src can't see the skill target!\\n"%(GetTWikiName(skill),skill),src)
                else:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"<a:Spell%s>%s</a> failed, $src can't see the spell target!\\n"%(GetTWikiName(proto.name),proto.name),src)
                return
        
        # If the distance between the source and destination is greater than
        # the cast range, then a failure occurs.
        if GetRangeMin(src,dst) > castRange:
            if src.player:
                if skill:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"$src's target is out of range for the <a:Skill%s>%s</a> skill!\\n"%(GetTWikiName(skill),skill),src)
                else:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"$src's target is out of range for the <a:Spell%s>%s</a> spell!\\n"%(GetTWikiName(proto.name),proto.name),src)
            return
        
        # Check if the user is facing the target.
        if not src.isFacing(dst):
            if src.player:
                if skill:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"<a:Skill%s>%s</a> failed, $src is facing the wrong way!\\n"%(GetTWikiName(skill),skill),src)
                else:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"<a:Spell%s>%s</a> failed, $src is facing the wrong way!\\n"%(GetTWikiName(proto.name),proto.name),src)
            return

    
    # resists
    if proto.spellType&RPG_SPELL_HARMFUL and dst != src and not proto.aoeRange:
        # any way you cut it we are going to be pissing someone off
        if not proto.spellType&RPG_SPELL_NOAGGRO:
            dst.addAggro(src,10)
        
        if CheckResist(src,dst,proto,skill):
            return
        
        if src.player and not skill and not proc:
            # spell criticals
            crit = src.skillLevels.get("Spell Critical")
            
            if crit:
                #crit = int(ceil(float(crit)/100.0)) #1-10
                #crit = 15-crit
                if not randint(0,5):
                    r = randint(0,100)
                    
                    if r >= 95:
                        icrit = 3
                    elif r >= 75:
                        icrit = 2
                    else:
                        icrit = 1
                    
                    # Calculate the muliplier cap based on skill.
                    #   1 - 500 = +100%.
                    # 501 - 750 = +200%
                    # 751+      = +300%  
                    crit = ceil(crit / 250) - 1
                    
                    # If the crit cap is below 100%, then clamp the crit cap to
                    # be at least +100%.  This sets the +100% bonus to be 
                    # effective for the skill range of 1 - 500.
                    if crit < 1:
                        crit = 1
                    
                    # If the crit multiplier is greater than the skill capped
                    # multiplier, then clamp the actual multiplier to not
                    # exceed the relative cap.      
                    if icrit > crit:
                        icrit = crit
                    
                    if src.player:
                        srcPlayer.sendGameText(RPG_MSG_GAME_WHITE,r'%s lands a spell critical! (%ix)\n'%(src.name,icrit+1))
                    mod += icrit
                    
                    if src.character:
                        src.character.checkSkillRaise("Spell Critical",1,2)
    
    # over 10 levels from getting spell you can get up to 100% better
    myclasses = ((src.spawn.pclassInternal,src.plevel),(src.spawn.sclassInternal,src.slevel),(src.spawn.tclassInternal,src.tlevel))
    best = 0
    chLevel = 0
    for pcl in proto.classes:
        for c,level in myclasses:
            if not c or not level:
                continue
            if c == pcl.classname and level >= pcl.level:
                r = level - pcl.level
                if r > best:
                    best = r
                    chLevel = level	# best class level for this spell
    if best:
        if best > 10:
            best = 10
        mod += (float(best)*0.1)*0.5
    
    try:
        if src.character and proto.skillname:
            src.character.checkSkillRaise("Concentration",2,10)
            try:
                slevel = src.skillLevels[proto.skillname]
                diff = slevel - (chLevel - 2) * 10
                # diminishing returns!
                if diff >= 0:
                    if diff > 20:
                        # our skill can maybe raise, but our best class level is too low
                        # make very hard to raise, chance 1:40
                        src.character.checkSkillRaise(proto.skillname,39,39)
                    else:
                        sel = float(diff) / 20.0
                        sel = int(round(36.0 * sel*(2-sel))) + 3
                        src.character.checkSkillRaise(proto.skillname,sel,sel)
                else:
                    src.character.checkSkillRaise(proto.skillname)
            except KeyError:
                pass
    except:
        traceback.print_exc()
    
    
    # If the proto has an AE range, check targeting and range..
    if proto.aoeRange:
        
        # Calculate the square distance to prevent having to calculate the
        # squareroot on all deltas.
        squaredAoeRange = proto.aoeRange * proto.aoeRange
        
        # Get a handle to the MobLookup dictionary.
        mobLookup = src.zone.mobLookup
        
        # The validTarget flag indiciates if at least one target was valid.
        validTarget = False
        
        # Set flags to indicate is the spell is harmful or generates aggro.
        isHarmful = proto.spellType & RPG_SPELL_HARMFUL
        isAggro = not proto.spellType & RPG_SPELL_NOAGGRO
        
        # Get the source player's encounter settings.
        if srcPlayer:
            srcEncounterSetting = newEncounterSetting = srcPlayer.encounterSetting
        
        # Iterate over all SimObjects.
        for simObject, cachedPosition in simObjects:
    
            # Get the mob associated with the SimObject.
            try:
                mobInSight = mobLookup[simObject]
            except KeyError:
                continue # The mob has not spawned yet.
            
            # Calculate position deltas.
            dX = cachedPosition[0] - pos[0]
            dY = cachedPosition[1] - pos[1]
            dZ = cachedPosition[2] - pos[2]

            # If the range is greater than the distance, then the mob is in
            # range of the AoE.
            # Note: This does not account for spawn scale.  The distance checks
            # against the center of the mob's feet.
            if squaredAoeRange >= (dX * dX + dY * dY + dZ * dZ):
            
                # If the mob is not a player, then add the mob to the list of
                # mobs in range.
                if not mobInSight.player:
                    mobsInRange = [mobInSight]
                    
                # Otherwise, the mob is a player.  Get a generator object to the
                # list of mobs in the player's party.
                else:
                    mobsInRange = (character.mob for character in mobInSight.player.party.members if character.mob)

                # Iterate over the mobs in range. 
                for mob in mobsInRange:
           
                    # If the mob is not detached, then the spell may target the
                    # mob.
                    if not mob.detached:
                        
                        # If the spell is harmful, check if source is allowed to
                        # harm the target.
                        if isHarmful:
                            
                            # If the source is an NPC and the mob is not KOS
                            #  to the source, continue to the next mob.
                            if not src.player:
                                if not IsKOS(src, mob):
                                    continue
                            
                            # Otherwise the source is a player.
                            else:
                                
                                # Check if the player is allowed to harm the
                                #  target. If not, continue to the next mob.
                                if not AllowHarmful(src, mob):
                                    continue
                                
                                # If the mob is not the target, do some additional
                                #  checks so the player doesn't accidentally aggro
                                #  a friendly mob.
                                # Treat the pet of the target as the target itself.
                                if dst != mob and (not mob.master or mob.master != dst):
                                    
                                    # Get the master of the mob if there is one
                                    #  so the player check can be done correctly.
                                    # The pet of a player has to be treated the
                                    #  same as the master.
                                    testMob = mob if not mob.master else mob.master
                                    
                                    # If the mob is an NPC and the mob is not KOS
                                    #  towards the player, then continue to the
                                    #  next mob.
                                    if not testMob.player:
                                        if not IsKOS(mob, src):
                                            continue
                                    
                                    # Flow only reaches this point if the source
                                    #  and mob are both players.  To prevent auto
                                    #  targeting lower level players in PvP,
                                    #  check the level difference.  If the source
                                    #  is at least 11 levels higher than the
                                    #  destination, then continue to the next mob.
                                    elif (src.level - testMob.level) > 10:
                                        continue
                        
                        # The spell is not harmful.  If the source is a Player,
                        # then the players encounter settings may change.
                        elif srcPlayer:
                            
                            # Use the mob as the destination, or the mob's
                            # master if one is present.
                            dstMob = mob if not mob.master else mob.master
                            
                            # If the mob is associated with a different player,
                            # then check encounter setting.
                            if srcPlayer != dstMob.player:
                                
                                # Get the mob's encounter setting.
                                dstEncounterSetting = dstMob.player.encounterSetting
                                
                                # If the mob's encounter setting is greater than
                                # the source, then the source's setting may be
                                # updated.
                                if dstEncounterSetting > srcEncounterSetting:
                                    
                                    # If the dstMob is not the the direct target 
                                    # and if the source is at least 11 levels
                                    # higher than the destination, then continue
                                    # to the next mob.  This prevents the 
                                    # sources setting from changing for 
                                    # indirectly helping a lower level.
                                    if dst != dstMob and (src.level - dstMob.level) > 10:
                                        continue
                                    
                                    # If the destination setting is higher than
                                    # the max, update the max.  The max will be
                                    # used later to update the source's setting.
                                    if dstEncounterSetting > newEncounterSetting:
                                        dstEncounterSetting = newEncounterSetting
                        
                        
                        # Target filtering has been done.  The spell will now 
                        # attempt to be casted on the target.
                        validTarget = True
                        
                        # If the spell is harmful, then check resist.
                        if isHarmful:
                        
                            # If the spell adds aggro, then add aggro on the
                            # mob torwards the source.
                            if isAggro:
                                mob.addAggro(src, 10)
                               
                            # If the target did not resist the spell, create
                            # the Spell and append the process to the source.
                            if not CheckResist(src, mob, proto, skill):
                                src.processesPending.add(Spell(src, mob, proto, mod, 0, skill, proc=proc))
                        
                        # Otherwise, the spell is helpful, so do not check
                        # resist.  Create the Spell, and append the process
                        # to the source.
                        else:
                            src.processesPending.add(Spell(src, mob, proto, mod, 0, skill, proc=proc))
    

        # If the source player, then inform the player if no targets were 
        # available, or update the player encounter settings if needed.
        if srcPlayer:
            
            # If there was no valid target, then inform the source Player.
            if not validTarget:
                if skill:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Skill%s>%s</a> failed, there was no valid target in range!\\n"%(GetTWikiName(skill),skill),src)
                else:
                    srcPlayer.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Spell%s>%s</a> failed, there was no valid target in range!\\n"%(GetTWikiName(proto.name),proto.name),src)
                
            # Otherwise, if the source player assisted someone with a higher 
            # encounter setting, then update the source's encounter setting.
            elif newEncounterSetting > srcEncounterSetting:
                srcPlayer.applyEncounterSetting(newEncounterSetting, True)
              
        # Return, as the spell has been handled.  
        return
    
    
    if proto.target == RPG_TARGET_PARTY or proto.target == RPG_TARGET_ALLIANCE:
        if src.player and srcPlayer.alliance:
            for p in srcPlayer.alliance.members:
                doParticles = True
                passed = False
                # If a player helps another player, make sure to inherit this ones
                #  encounter setting if higher than own.
                if p.encounterSetting > srcPlayer.encounterSetting:
                    srcPlayer.applyEncounterSetting(p.encounterSetting, True)
                for c in p.party.members:
                    if not c.mob or c.mob.detached:
                        continue
                    # all mobs in the same party are at the same location, only test once per party
                    if not passed:
                        if c.mob.zone == src.zone and GetRangeMin(c.mob,src) <= castRange:
                            passed = True
                        else:
                            break
                    src.processesPending.add(Spell(src,c.mob,proto,mod,0,skill,doParticles,False,spellLevel,proc=proc))
                    doParticles = False
        elif src.player:
            doParticles = True
            for c in srcPlayer.party.members:
                if not c.mob or c.mob.detached:
                    continue
                src.processesPending.add(Spell(src,c.mob,proto,mod,0,skill,doParticles,False,spellLevel,proc=proc))
                doParticles = False
        else:
            src.processesPending.add(Spell(src,src,proto,mod,0,skill,True,False,spellLevel,proc=proc))
        return
    
    # If a player helps another player, make sure to inherit this ones
    #  encounter setting if higher than own.
    if srcPlayer and not proto.spellType&RPG_SPELL_HARMFUL:
        dstPlayer = None
        if dst.player:
            dstPlayer = dst.player
        elif dst.master and dst.master.player:
            dstPlayer = dst.master.player
        if dstPlayer and dstPlayer.encounterSetting > srcPlayer.encounterSetting:
            srcPlayer.applyEncounterSetting(dstPlayer.encounterSetting, True)
    src.processesPending.add(Spell(src,dst,proto,mod,0,skill,True,False,spellLevel,proc=proc))



class SpellCasting:
    def __init__(self,mob,spellProto,level = 1):  # level 10 is the best
        self.mob = mob
        self.spellProto = spellProto
        haste = 1.0
        haste -= mob.castHaste
        if level != 1:
            haste -= (level / 10.0) * 0.25  # 25% cast haste at level X
        
        # cast haste depending on spell skill level, max an additional 10%
        if spellProto.skillname:
            try:
                slevel = mob.skillLevels[spellProto.skillname]
                diff = slevel - (spellProto.level - 2) * 10
                if diff > 0:
                    if diff > 20:
                        diff = 20
                    haste -= 0.1 * float(diff) / 20.0
            except KeyError:
                pass
        
        if haste > 2.0:
            haste = 2.0
        if haste < 0.25:
            haste = 0.25
        self.timer = spellProto.castTime*haste
        self.failed = False
        # precalculate failure time so we can send to simulation etc (particle times)
        self.failedTime = 0
        self.level = level
    
    
    def begin(self):
        # check components and stuff (for player)
        # check mana
        # do skillcheck
        # calculate failure, etc
        
        mob = self.mob
        player = mob.player
        proto = self.spellProto
        
        if self.spellProto in mob.recastTimers:
            return False  # should "never" happen client shouldn't allow this
        
        # Check if mob is in a condition to cast.
        if 0 < mob.sleep or 0 < mob.stun or mob.isFeared or 0 < mob.suppressCasting:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED, r'$src\'s casting failed $srche is in no condition to cast a spell!\n', mob)
            return False
        
        self.manaCost = proto.manaCost
        if self.level != 1:
            self.manaCost += (self.level / 10.0) * 0.35  # 35% more mana at level 10
        
        # reduced mana cost depending on spell skill level, max -10%
        if proto.skillname:
            try:
                slevel = mob.skillLevels[proto.skillname]
                diff = slevel - (proto.level - 2) * 10
                if diff > 0:
                    if diff > 20:
                        diff = 20
                    self.manaCost -= int(round(self.manaCost * 0.1 * float(diff) / 20.0))
            except KeyError:
                pass
        
        if proto.target == RPG_TARGET_PET and not mob.pet:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"$src's casting of <a:Spell%s>%s</a> failed, $src has no pet.\\n"%(GetTWikiName(proto.name),proto.name),mob)
            return False
        
        filterTimeBegin = proto.filterTimeStart
        filterTimeEnd = proto.filterTimeEnd
        
        if filterTimeBegin != -1 and filterTimeEnd != -1:
            time = mob.zone.time
            passed = False
            if filterTimeEnd < filterTimeBegin:
                # spell crosses day boundry
                if (24 >= time.hour >= filterTimeBegin) or (filterTimeEnd > time.hour >= 0):
                    passed = True
            elif filterTimeEnd > time.hour >= filterTimeBegin:
                # spell doesn't cross day boundry
                passed=True
            if not passed:
                if player:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"$src's casting failed, the <a:Spell%s>%s</a> spell does not work at this time of day.\\n"%(GetTWikiName(proto.name),proto.name),mob)
                return False
        
        if mob.mana < self.manaCost:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"$src's casting of <a:Spell%s>%s</a> failed, not enough mana.\\n"%(GetTWikiName(proto.name),proto.name),mob)
            else:
                traceback.print_stack()
                print "AssertionError: ai mobs should check mana before cast!"
            return False
        
        # check components
        if player:
            if len(proto.components):
                # Gather a dictionary of the required spell components
                #  with their counts.
                components = defaultdict(int)
                for c in proto.components:
                    if c.count > 0:
                        components[c.itemProto] += c.count
                
                # Check if the player has the required components and give
                #  feedback if not.
                if not player.checkItems(components.copy(),True):
                    player.sendGameText(RPG_MSG_GAME_DENIED,"$src lacks the spell components to cast <a:Spell%s>%s</a>,\\n$srche needs: %s\\n"%(GetTWikiName(proto.name),proto.name,', '.join('<a:Item%s>%i %s</a>'%(GetTWikiName(ip.name),c,ip.name) for ip,c in components.iteritems())),mob)
                    return False
        
        if proto.recastTime:
            mob.recastTimers[proto] = proto.recastTime
        
        doEffects = True
        if player:
            if sysTime() - player.spellEffectCastTime < 5:
                doEffects = False
            else:
                player.spellEffectCastTime = sysTime()
        
        mob.cancelInvisibility()
        mob.cancelFlying()
        mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
        mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
        if player:
            player.mind.callRemote("disturbEncounterSetting")
        
        zone = self.mob.zone
        if doEffects:
            t = self.timer / 6
            t *= 1000
            if proto.particleCasting:
                #base this on failed time if necessary
                zone.simAvatar.mind.callRemote("newParticleSystem",mob.simObject.id,"CastingEmitter",proto.particleTextureCasting,t)
            if proto.sndCasting:
                zone.simAvatar.mind.callRemote("newAudioEmitterLoop",mob.simObject.id,proto.sndCasting,t)
            if proto.afxSpellEffectCasting:
                zone.simAvatar.mind.callRemote("newSpellEffect",mob.simObject.id,proto.afxSpellEffectCasting)
        
        zone.simAvatar.mind.callRemote("casting",mob.simObject.id,True)
        
        if proto.castingMsg:
            msg = proto.castingMsg
            msg = msg.replace("$src",mob.name) + "\\n"
        else:
            msg = r'%s begins casting a spell.\n'%mob.name
        
        if not mob.battle:
            if player:
                GameMessage(RPG_MSG_GAME_CASTING,mob.zone,mob,None,msg,mob.simObject.position,range=30)
            else:
                GameMessage(RPG_MSG_GAME_CASTING_NPC,mob.zone,mob,None,msg,mob.simObject.position,range=30)
        
        return True
    
    
    # failure is handled in here too
    def tick(self):
        mob = self.mob
        player = mob.player
        
        if self.timer <= 0:
            proto = self.spellProto
            
            componentsConsumed = None
            
            # do one last check, if mana is too low from drain, etc
            # need to check components again in case we lost component from cast begin!
            if player:
                if len(proto.components):
                    # Gather a dictionary of the required spell components
                    #  with their counts.
                    componentsConsumed = defaultdict(int)
                    for c in proto.components:
                        if c.count > 0:
                            componentsConsumed[c.itemProto] += c.count
                    
                    # Check if the player has the required components and give
                    #  feedback if not.
                    if not player.checkItems(componentsConsumed.copy(),True):
                        player.sendGameText(RPG_MSG_GAME_DENIED,"$src lacks the spell components to cast <a:Spell%s>%s</a>,\\n$srche needs: %s\\n"%(GetTWikiName(proto.name),proto.name,', '.join('<a:Item%s>%i %s</a>'%(GetTWikiName(ip.name),c,ip.name) for ip,c in componentsConsumed.iteritems())),mob)
                        if proto.recastTime and proto in mob.recastTimers:
                            player.cinfoDirty = True
                            del mob.recastTimers[proto]
                        mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False)
                        return True
            
            # otherwise, casting was a success!
            
            if proto.target == RPG_TARGET_PET and not mob.pet:
                mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False)
                if player:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"$src's casting of <a:Spell%s>%s</a> failed, $src has no pet.\\n"%(GetTWikiName(proto.name),proto.name),mob)
                if proto.recastTime and proto in mob.recastTimers:
                    if player:
                        player.cinfoDirty = True
                    del mob.recastTimers[proto]
                return True
            
            if mob.spellTarget:
                tgt = mob.spellTarget
                mob.spellTarget = None
            else:
                tgt = mob.target
            
            if tgt and tgt == mob.pet and proto.target == RPG_TARGET_OTHER:
                tgt = mob
            if proto.target in (RPG_TARGET_SELF,RPG_TARGET_PARTY,RPG_TARGET_ALLIANCE):
                tgt = mob
            elif proto.target == RPG_TARGET_PET:
                tgt = mob.pet
            elif player and proto.target == RPG_TARGET_OTHER and proto.spellType&RPG_SPELL_HEALING:
                tgt = GetPlayerHealingTarget(mob,tgt,proto)
            
            if not proto.spellType&RPG_SPELL_HARMFUL and tgt != mob and tgt != mob.pet:
                if not tgt or all([player or (mob.master and mob.master.player),tgt.player or (tgt.master and tgt.master.player),AllowHarmful(mob,tgt)]):
                    kos = True
                else:
                    kos = IsKOS(tgt,mob)
                if kos:
                    tgt = mob
            
            if not tgt:
                if player:
                    if proto.spellType&RPG_SPELL_HARMFUL:
                        from mud.world.command import CmdTargetNearest
                        CmdTargetNearest(mob,None,False,True)
                        tgt = mob.target
                    else:
                        tgt = mob
                
                if not tgt:
                    mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False)
                    if player:
                        player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s casting failed, no target.\n'%mob.name)
                    if proto.recastTime and proto in mob.recastTimers:
                        if player:
                            player.cinfoDirty = True
                        del mob.recastTimers[proto]
                    return True
            
            
            if proto.spellType&RPG_SPELL_HARMFUL:
                if not proto.aoeRange and not AllowHarmful(mob,tgt):
                    if player:
                        player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s casting failed, cannot cast a harmful spell on this target.\n'%mob.name)
                    if proto.recastTime and proto in mob.recastTimers:
                        if player:
                            player.cinfoDirty = True
                        del mob.recastTimers[proto]
                    mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False)
                    return True
            
            
            if proto.target == RPG_TARGET_OTHER:
                dist = GetRangeMin(mob,tgt)
                
                # cast range reduction based on spell skill level, max +20%
                castRange = proto.castRange
                if proto.skillname:
                    try:
                        slevel = mob.skillLevels[proto.skillname]
                        diff = slevel - (proto.level - 2) * 10
                        if diff > 0:
                            if diff > 20:
                                diff = 20
                            castRange += castRange * 0.2 * float(diff) / 20.0
                    except KeyError:
                        pass
                
                if dist > castRange:
                    if player:
                        player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s target is out of range for this spell!\n'%mob.name)
                    mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False)
                    return True
                
                if tgt.simObject.id not in mob.simObject.canSee:
                    if player and tgt.player != player:
                        player.sendGameText(RPG_MSG_GAME_DENIED,r'%s can\'t see the spell target!\n'%mob.name)
                        mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False)
                        return True
                
                if proto.projectile and not mob.isFacing(tgt):
                    if player:
                        player.sendGameText(RPG_MSG_GAME_DENIED, \
                            "$src is facing the wrong way!\\n",mob)
                    mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False)
                    return True
            
            if componentsConsumed != None and player:
                player.takeItems(componentsConsumed)
            
            if proto.animOverride:
                mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,proto.animOverride)
            if len(proto.particleNodes):
                mob.zone.simAvatar.mind.callRemote("triggerParticleNodes",mob.simObject.id,proto.particleNodes)
            
            if proto.recastTime:
                mob.recastTimers[proto] = proto.recastTime
            
            # alright, actually casting spell
            mob.mana -= self.manaCost
            
            if proto.projectile:
                mob.zone.simAvatar.mind.callRemote("cast",mob.simObject.id,True)
                p = Projectile(mob,tgt,self.level)
                p.spellProto = proto
                p.launch()
                if proto.sndBegin:
                    mob.playSound(proto.sndBegin)
            else:
                mob.zone.simAvatar.mind.callRemote("cast",mob.simObject.id)
                
                #move me
                if proto.sndBeginDuration:
                    t = proto.sndBeginDuration/6
                    t *= 1000
                    mob.zone.simAvatar.mind.callRemote("newAudioEmitterLoop",mob.simObject.id,proto.sndBegin,t)
                
                mod = 1.0
                if self.level != 1.0:
                    mod += (self.level / 10.0) * 0.5
                
                SpawnSpell(proto,mob,tgt,tgt.simObject.position,mod,None,self.level)
            return True
        return False
    
    
    def cancel(self):
        mob = self.mob
        mob.zone.simAvatar.mind.callRemote("casting",mob.simObject.id,False,True)
        mob.casting = None
        
        if self.spellProto.recastTime and self.spellProto in mob.recastTimers:
            if mob.player:
                mob.player.cinfoDirty = True
            del mob.recastTimers[self.spellProto]


