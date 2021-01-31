# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#spells have effects, skills can too
#stacking


from mud.common.persistent import Persistent
from mud.world.core import *
from mud.world.damage import Damage,Heal
from mud.world.defines import *
import spell

from collections import defaultdict
from math import ceil,floor
from random import randint
from sqlobject import *
from time import time as sysTime
import traceback



#RPG_EFFECT_LEECH #dd and dot leech
#RPG_EFFECT_DRAIN
#RPG_EFFECT_DAMAGE #dd and dot
#RPG_EFFECT_AGGRO

#RPG_EFFECT_RESIST <-- stat

#RPG_EFFECT_ROOT

#RPG_EFFECT_ABSORPTION #certain amount, # of attacks, #of spells

#RPG_EFFECT_LIGHTSOURCE #also darkness
#RPG_EFFECT_RESURRECTION
#RPG_EFFECT_STUN
#RPG_EFFECT_SLEEP
#RPG_EFFECT_HEAL
#RPG_EFFECT_CURE
#RPG_EFFECT_NEGATE #negate effects
#RPG_EFFECT_INTERRUPT #interrupt casting

#RPG_EFFECT_MELEEHASTE
#RPG_EFFECT_SPELLHASTE
#RPG_EFFECT_MELEESLOW
#RPG_EFFECT_SPELLSLOW

#RPG_EFFECT_POINT #point to something, north, nearest animal, etc


#RPG_EFFECT_TELEPORT #between zones, safe spot in same zone, evacs, to bindpoint, random in zone
#RPG_EFFECT_SIZE
#RPG_EFFECT_ILLUSION

#RPG_EFFECT_LEVITATION
#RPG_EFFECT_SWIM
#RPG_EFFECT_HOLDBREATH

#RPG_EFFECT_REGEN

#RPG_EFFECT_ENCHANT

#RPG_EFFECT_MODULATE #modulate another effect

#RPG_EFFECT_STATMOD

#RPG_EFFECT_IMMUNITY
#RPG_EFFECT_INVISIBILITY
#RPG_EFFECT_VISION
#RPG_EFFECT_BANISH

#RPG_EFFECT_DAMAGESHIELD

#RPG_EFFECT_SACRIFICE


#RPG_EFFECT_FEAR
#RPG_EFFECT_CHARM

#RPG_EFFECT_MELEEREFLECTION
#RPG_EFFECT_SPELLREFLECTION

#one shot
#RPG_EFFECT_SUMMONITEM
#RPG_EFFECT_SUMMONPET
#RPG_EFFECT_SUMMONMONSTER
#RPG_EFFECT_SUMMONALLY

#RPG_EFFECT_COMBAT

#RPG_EFFECT_TRIGGER_HIT 
#RPG_EFFECT_TRIGGER_STRIKE
#RPG_EFFECT_TRIGGER_DEATH
#RPG_EFFECT_TRIGGER_EFFECT_CREATE
#RPG_EFFECT_TRIGGER_EFFECT_BEGIN

#RPG_EFFECT_FACTION


#global stats should never be health,mana,stamina... globals
#get popped on the end... likewise, str, bdy, etc should always
#be global



class EffectDamage(Persistent):
    type = IntCol(default=RPG_DMG_PHYSICAL)
    amount = IntCol(default=1)
    stage = IntCol(default=RPG_EFFECT_STAGE_GLOBAL)
    effectProto = ForeignKey('EffectProto')



class EffectStat(Persistent):
    statname = StringCol()
    value = FloatCol()
    stage = IntCol()
    effectProto = ForeignKey('EffectProto')



class EffectPermanentStat(Persistent):
    statname = StringCol()
    value = FloatCol()
    effectProto = ForeignKey('EffectProto')



class EffectLeech(Persistent):
    leechType = StringCol(default="")
    leechBegin = IntCol(default=0)
    leechEnd = IntCol(default=0)
    leechTick = IntCol(default=0)
    leechTickRate = IntCol(default=0)
    effectProto = ForeignKey('EffectProto')



class EffectDrain(Persistent):
    drainType = StringCol(default="")
    drainBegin = IntCol(default=0)
    drainEnd = IntCol(default=0)
    drainTick = IntCol(default=0)
    drainTickRate = IntCol(default=0)
    effectProto = ForeignKey('EffectProto')



class EffectRegen(Persistent):
    regenType = StringCol(default="")
    regenBegin = IntCol(default=0)
    regenEnd = IntCol(default=0)
    regenTick = IntCol(default=0)
    regenTickRate = IntCol(default=0)
    effectProto = ForeignKey('EffectProto')



class EffectIllusion(Persistent):
    illusionModel = StringCol(default="")
    illusionAnimation = StringCol(default="")
    illusionTextureSingle = StringCol(default="")
    illusionTextureExtra = StringCol(default="")
    illusionTextureBody = StringCol(default="")
    illusionTextureHead = StringCol(default="")
    illusionTextureLegs = StringCol(default="")
    illusionTextureHands = StringCol(default="")
    illusionTextureFeet = StringCol(default="")
    illusionTextureArms = StringCol(default="")
    illusionSex = StringCol(default="")
    illusionRace = StringCol(default="")
    illusionSndProfile = ForeignKey('SpawnSoundProfile',default=None)
    # if non-zero sets the illusion to a size rather than scaling (to do)
    illusionSize = FloatCol(default=0.0)



class EffectProto(Persistent):
    name = StringCol(alternateID=True)
    
    leechEffect = ForeignKey('EffectLeech',default=None)
    drainEffect = ForeignKey('EffectDrain',default=None)
    regenEffect = ForeignKey('EffectRegen',default=None)
    
    #aggro
    aggro = IntCol(default=0)
    
    #stats
    stats = MultipleJoin('EffectStat')
    permanentStats = MultipleJoin('EffectPermanentStat')
    giveSkill = StringCol(default="")
    damage = MultipleJoin('EffectDamage')
    
    flags = IntCol(default=0)
    
    #absorption
    absorbType = StringCol(default="")
    absorbCount = IntCol(default=0)
    
    #light
    light = FloatCol(default=0)
    
    invisibility = FloatCol(default=0)
    seeinvisibile = FloatCol(default=0)
    
    # Resurrection, percent of experience the target will regain.
    resurrectionXP = FloatCol(default=0)
    
    cure = IntCol(default=0)
    negate = IntCol(default=0)
    negateMaxLevel = IntCol(default=0)
    
    point = StringCol(default="")
    
    teleport = StringCol(default="") #zone, random, safespot
    teleportDst = StringCol(default="") #for zone
    
    size = FloatCol(default=1.0)
    
    illusion = ForeignKey('EffectIllusion',default=None)
    
    enchantItem = ForeignKey('ItemProto',default=None)
    
    immunityType = StringCol(default="")
    
    sacrificeLevel = StringCol(default="")
    sacrificeItem = ForeignKey('ItemProto',default=None)
    
    dmgReflectionType = IntCol(default=RPG_DMG_PHYSICAL)
    dmgReflectionPercent = FloatCol(default=0)
    dmgReflectionMax = IntCol(default=0)
    
    spellReflectionPercent = FloatCol(default=0)
    spellReflectionMax = IntCol(default=0)
    
    summonPet = ForeignKey('Spawn',default=None)
    summonItem = ForeignKey('ItemProto',default=None)
    
    #XXX TO DO COMBAT
    
    level =    IntCol(default=1)
    tickRate = IntCol(default=0)
    harmful =  BoolCol(default=False)
    resist =   IntCol(default=RPG_RESIST_MAGICAL) #also dictates type of damage
    trigger =  IntCol(default=0)
    
    spellProtos = RelatedJoin('SpellProto')
    
    
    def affectsStat(self,statname):
        for st in self.stats:
            if st.statname == statname:
                return True
        return False
    
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        
        if len(self.permanentStats):
            self.hasPermanentStats = True
        else:
            self.hasPermanentStats = False



def UndoIllusion(effect):
    dst = effect.dst
    if not dst.player:
        return
    
    if dst.illusionEffect == effect:
        ieffect = None
        sndProfile = None
        for p in dst.processesIn:
            if isinstance(p,spell.Spell):
                for e in p.effects:
                    if e == effect:
                        continue
                    proto = e.effectProto
                    if proto.illusion:
                        ieffect = e
                        sndProfile = proto.illusion.illusionSndProfile
                        #break
        
        dst.illusionEffect = ieffect
        dst.spawn.sndProfileOverride = sndProfile
        
        if not ieffect:
            si = dst.spawn.getSpawnInfo()
            si.refresh()
        else:
            DoIllusion(ieffect,ieffect.src,ieffect.dst)


def BreakCharm(effect):
    proto = effect.effectProto
    if not proto.flags&RPG_EFFECT_CHARM:
        return
    
    src = effect.src
    dst = effect.dst
    
    if not src.pet or src.pet != dst:
        return
    
    pet = src.pet
    zone = pet.zone
    
    pet.realm = pet.charmBackupRealm
    pet.aggro = pet.charmBackupAggro
    pet.petSpeedMod = 0.0
    pet.charmEffect = None
    pet.master = None
    src.pet = None
    pet.playerPet = False
    
    if src.character:
        # Unequip the items given by the Character master.
        map(pet.unequipItem,xrange(RPG_SLOT_WORN_BEGIN,RPG_SLOT_WORN_END))
        
        # Refresh the items given by the Character master.
        src.character.refreshPetItems()
        
        # And reequip own gear.
        map(pet.aiEquipItem,pet.loot.items)
        pet.mobInfo.refresh()
    
    zone.setTarget(pet,None)
    zone.setFollowTarget(pet,None)
    
    # Reset home transform in case the player used a /pet stay command.
    zone.simAvatar.mind.callRemote("resetHomeTransform",pet.simObject.id)
    
    # Make the released pet angry at its former master.
    # The longer the charm duration and the higher the pet level, the more angry.
    pet.addAggro(src,int(ceil(10 * pet.plevel * (sysTime() - pet.charmBegin))))


def DoCharm(effect, src, dst):
    proto = effect.effectProto
    if not proto.flags&RPG_EFFECT_CHARM:
        return
    
    if dst.player:
        return
    
    if src.pet or src.petSpawning:
        return
    
    if dst.master:
        return
    
    pet = dst
    
    pet.charmBackupRealm = pet.realm
    pet.charmBackupAggro = pet.aggro
    pet.charmBegin = sysTime()
    pet.realm = src.realm
    pet.master = src
    src.pet = pet
    if src.player:
        pet.playerPet = True
        src.character.refreshPetItems()
    
    from mud.world.pet import PetCmdFollowMe
    PetCmdFollowMe(pet)
    
    pet.aggro = defaultdict(int)
    pet.setTarget(None)
    
    pet.charmEffect = effect
    
    petPet = pet.pet
    if petPet:
        if petPet.charmEffect:
            petPet.charmEffect.parent.cancel()
            if pet.pet:
                traceback.print_stack()
                print "AssertionError: pet charm effect resisted breaking!"
            return
        petPet.zone.removeMob(petPet)


def DoIllusion(effect,src,dst):
    proto = effect.effectProto
    if not dst.player:
        return
    if not proto.illusion:
        return
    
    si = dst.spawn.spawnInfo
    gotone = False
    illusion = proto.illusion
    if illusion.illusionRace:
        gotone = True
        si.race = illusion.illusionRace
        si.modelname = ""
        si.textureSingle = ""
        si.textureBody = ""
        si.textureHead = ""
        si.textureLegs = ""
        si.textureArms = ""
        si.textureHands = ""
        si.textureFeet = ""
        si.textureExtra = illusion.illusionTextureExtra
    
    if illusion.illusionModel:
        gotone = True
        si.modelname = illusion.illusionModel
        si.race = "Illusion" #hack
        si.textureSingle = illusion.illusionTextureSingle
        si.textureExtra= illusion.illusionTextureExtra
        si.textureBody = illusion.illusionTextureBody
        si.textureHead = illusion.illusionTextureHead
        si.animation = illusion.illusionAnimation
    
    if gotone:
        dst.spawn.sndProfileOverride = illusion.illusionSndProfile
        dst.illusionEffect = effect
        si.refresh()


def DoPermanentStats(effect,src,dst):
    proto = effect.effectProto
    if not proto.hasPermanentStats:
        return
    
    if not dst.character:
        return
    
    for stat in proto.permanentStats:
        
        stname = stat.statname
        
        if stname.lower() == "advancementpoints":
            dst.character.advancementPoints+=int(stat.value)
            return
            
        
        stname = stname.replace("Perm","Base")
        
        c = dst.character
        
        rname = stname.replace("Base","Raise")
        
        r = getattr(c,rname)
        
        v = stat.value
        
        if v > r:
            v = r
        
        try:
            setattr(c,rname,int(getattr(c,rname)-v))
        except:
            traceback.print_exc()
        
        try:
            setattr(dst.spawn,stname,int(getattr(dst.spawn,stname)+v))
        except:
            traceback.print_exc()
            
        if "Base" in stname:
            st = stname[:-4]
            try:
                setattr(dst,st,int(getattr(dst,st)+v))
            except:
                traceback.print_exc()


def DoGiveSkill(effect, src, dst):
    skill = effect.effectProto.giveSkill
    
    if not skill:
        return
    
    if not dst.character:
        return
    
    if not dst.skillLevels.get(skill,0):
        dst.player.sendGameText(RPG_MSG_GAME_YELLOW, \
            "%s has learned %s!\\n"%(dst.name,skill))
        from mud.world.character import CharacterSkill
        CharacterSkill(character=dst.character,skillname=skill,level=1)
        dst.skillLevels[skill] = 1


def DoSummonItem(effect,src):
    proto = effect.effectProto
    
    if not proto.summonItem:
        return
    
    if not src.character:
        return
        
    if not src.character.checkGiveItems(1):
        return
        
    src.character.giveItemProtos([proto.summonItem],[1])


def DoSummonPet(effect,src):
    proto = effect.effectProto
    if not proto.summonPet:
        return
    
    if src.battle:
        #XXX - don't cast this at all eventually
        return
    
    if src.pet and src.pet.charmEffect:
        src.pet.charmEffect.parent.cancel()
        if src.pet:
            traceback.print_stack()
            print "AssertionError: charm effect resisted breaking!"
            return
    
    zone = src.zone
    if src.pet:
        zone.removeMob(src.pet) #remove existing pet
    pos = src.simObject.position
    rot = src.simObject.rotation
    
    spawn = proto.summonPet

    transform = (pos[0], pos[1], pos[2], rot[0], rot[1], rot[2], rot[3])
    if not src.player and not src.target:
        x1 = randint(0,1)
        y1 = randint(0,1)
        if not x1:
            x1 = -1
        if not y1:
            y1 = -1
        
        s = src.spawn.modifiedScale / 2.0
        if s < 1.0:
            s = 1.0
        if s > 3.0:
            s = 3.0
        x,y = pos[0] + float(x1) * s, pos[1] + float(y1) * s
        
        transform = (x, y, pos[2] + 1.0, rot[0], rot[1], rot[2], rot[3])
    
    sizemod = 1.0
    if not src.player:
        sizemod = src.spawn.modifiedScale * .8 / spawn.modifiedScale
    
    try:
        pet = zone.spawnMob(spawn, transform, -1, src, sizemod)
    except:
        pass
    
    if not src.player:
        pet.petSpeedMod = src.move * 1.1 - spawn.move
        if pet.petSpeedMod < 0.0:
            pet.petSpeedMod = 0.0
        pet.speedMod = src.speedMod
        pet.flying = src.flying
    

    #pet will not be in actionMobs until simserver has spawned the bot
    #so, we set the pet's master here and we'll set the master's pet attribute later
    
    pet.realm = src.realm
    pet.master = src
    if src.player:
        pet.playerPet = True
        
    src.petSpawning = True
    
    mod = effect.mod
    if mod > 1:
        mod = 1.0 + (mod-1.0)*.25
    
    if not src.player:
        pet.maxHealthScalar = .5
    else:
        pet.maxHealthScalar = mod
    
    if effect.parent and isinstance(effect.parent,spell.Spell):
        adj = floor(effect.parent.level/3)
        if effect.parent.level == 10:
            adj+=1
        pet.level+=adj        
        pet.plevel+=adj
        if adj:
            pet.updateClassStats()
        
    pet.offenseScalar=mod
    pet.defenseScalar=mod
    pet.updateDerivedStats()
    pet.health = pet.maxHealth


def DoBanish(effect,src,dst):
    proto = effect.effectProto
    if not proto.flags&RPG_EFFECT_BANISH:
        return
    
    if dst.pet:
        if dst.pet.charmEffect:
            dst.pet.charmEffect.parent.cancel()
            if dst.pet:
                traceback.print_stack()
                print "AssertionError: pet charm effect resisted breaking!"
            return
        if dst.player:
            dst.player.sendGameText(RPG_MSG_GAME_PET_SPEECH,r'%s\'s pet screams, \"I\'m banished master!!!\"\n'%dst.name)
        dst.pet.zone.removeMob(dst.pet)
    elif dst.master:
        if dst.charmEffect:
            dst.charmEffect.parent.cancel()
            return
        if dst.master.player:
            dst.master.player.sendGameText(RPG_MSG_GAME_PET_SPEECH,r'%s\'s pet screams, \"I\'m banished master!!!\"\n'%dst.master.name)
        dst.zone.removeMob(dst)


def DoInterrupt(effect,src,dst):
    proto = effect.effectProto
    if not proto.flags&RPG_EFFECT_INTERRUPT:
        return
    
    if dst.casting:
        dst.zone.simAvatar.mind.callRemote("casting",dst.simObject.id,False)
        if dst.player:
            dst.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s\'s casting got interrupted by %s!\n'%(dst.name,src.name))
        dst.casting = None


def DoNegate(effect,src,dst):
    proto = effect.effectProto
    if not proto.negate or not proto.negateMaxLevel:
        return
    
    cancel = []
    for p in dst.processesIn:
        if isinstance(p,spell.Spell) and p.spellProto.spellType&RPG_SPELL_HARMFUL and p.spellProto.duration and p.spellProto.level <= proto.negateMaxLevel:
            cancel.append(p)
            if len(cancel) >= proto.negate:
                break
    
    # If there is a surplus of negative spells that could be removed, see if the pet
    #  if present has negative spells on it and remove those.
    if dst.pet and len(cancel) < proto.negate:
        for p in dst.pet.processesIn:
            if isinstance(p,spell.Spell) and p.spellProto.spellType&RPG_SPELL_HARMFUL and p.spellProto.duration and p.spellProto.level <= proto.negateMaxLevel:
                cancel.append(p)
                if len(cancel) >= proto.negate:
                    break
    
    for p in cancel:
        p.cancel()


def DoDrain(effect):
    proto = effect.effectProto
    drain = proto.drainEffect
    if drain:
        effect.drainTimer -= 3
        if effect.drainTimer <= 0:
            dst = effect.dst
            effect.drainTimer = drain.drainTickRate
            if drain.drainType == "health":
                Damage(dst,effect.src,drain.drainTick * (effect.mod + effect.damageMod),DAMAGEFORRESIST[proto.resist],None,False,False,True)
            elif drain.drainType == "mana":
                dst.mana -= drain.drainTick*effect.mod
                if dst.mana < 0:
                    dst.mana = 0
            elif drain.drainType == "stamina":
                dst.stamina -= drain.drainTick*effect.mod
                if dst.stamina < 0:
                    dst.stamina = 0


def DoRegen(effect):
    proto = effect.effectProto
    regen = proto.regenEffect
    if regen:
        effect.regenTimer -= 3
        if effect.regenTimer <= 0:
            dst = effect.dst
            effect.regenTimer = regen.regenTickRate
            if regen.regenType == "health":
                dst.health += regen.regenTick * (effect.mod + effect.healMod)
                if dst.health > dst.maxHealth:
                    dst.health = dst.maxHealth
            elif regen.regenType == "mana":
                dst.mana += regen.regenTick*effect.mod
                if dst.mana > dst.maxMana:
                    dst.mana = dst.maxMana
            elif regen.regenType == "stamina":
                dst.stamina += regen.regenTick*effect.mod
                if dst.stamina > dst.maxStamina:
                    dst.stamina = dst.maxStamina


def DoLeech(effect):
    proto = effect.effectProto
    leech = proto.leechEffect
    if not leech:
        return
    effect.leechTimer -= 3
    if effect.leechTimer <= 0:
        src = effect.src
        effect.leechTimer = leech.leechTickRate
        if leech.leechType == 'health':
            src.health += leech.leechTick * (effect.mod + effect.healMod)
            if src.health > src.maxHealth:
                src.health = src.maxHealth
        elif leech.leechType == 'mana':
            src.mana += leech.leechTick*effect.mod
            if src.mana > src.maxMana:
                src.mana = src.maxMana
        elif leech.leechType == 'stamina':
            src.stamina += leech.leechTick*effect.mod
            if src.stamina > src.maxStamina:
                src.stamina = src.maxStamina


def DoResurrection(effect,src,dst):
    proto = effect.effectProto
    if not proto.flags&RPG_EFFECT_RESURRECTION:
        return False
    
    healthRecover = manaRecover = staminaRecover = 0
    for st in proto.stats:
        statname = st.statname
        if statname == 'health':
            if value > 0:
                healthRecover += st.value * (effect.mod + effect.healMod)
        elif statname == 'mana':
            manaRecover += st.value * effect.mod
        elif statname == 'stamina':
            staminaRecover += st.value * effect.mod
    
    if CoreSettings.MAXPARTY != 1:
        player = dst.player
        if not player:
            return False
        
        for c in player.party.members:
            if c.dead:
                c.resurrect(proto.resurrectionXP)
                mob = c.mob
                if healthRecover:
                    mob.health += healthRecover
                    if mob.health > mob.maxHealth:
                        mob.health = mob.maxHealth
                    c.health = int(mob.health)
                if manaRecover:
                    mob.mana += manaRecover
                    if mob.mana > mob.maxMana:
                        mob.mana = mob.maxMana
                    c.mana = int(mob.mana)
                if staminaRecover:
                    mob.stamina += staminaRecover
                    if mob.stamina > mob.maxStamina:
                        mob.stamina = mob.maxStamina
                    c.stamina = int(mob.stamina)
        return True
    else:
        if src.player:
            # Player resurrection of grave. Gather up the corpses in the zone.
            cnames = []
            srcZoneName = src.player.zone.zone.name
            srcPos = src.simObject.position
            for pname,dm in src.player.world.deathMarkers.iteritems():
                try:
                    charName,realm,zoneName,dstPos,rot = dm
                    if zoneName == srcZoneName:
                        x = srcPos[0] - dstPos[0]
                        y = srcPos[1] - dstPos[1]
                        z = srcPos[2] - dstPos[2]
                        r = x*x + y*y + z*z
                        # Test radius squared, no need to take root on vector.
                        if r < 50:
                            cnames.append(charName)
                except:
                    traceback.print_exc()
            
            # If the list of possible resurrection targets is empty,
            #  notify caster and return.
            if not len(cnames):
                src.player.sendGameText(RPG_MSG_GAME_DENIED,r'There are no graves near enough to resurrect.\n')
                return False
            
            # Send a list of names of possible resurrection targets to the caster.
            src.player.mind.callRemote("setResurrectNames",cnames)
            src.player.resurrection = (sysTime(),proto.resurrectionXP,healthRecover,manaRecover,staminaRecover,cnames)
            return True
        
        else:
            #hm, this is a mob resurrection, we could wipe the grave location and return some XP
            #for now, do nothing
            return False


def DoTeleportReal(effect,src,dst):
    if not dst.player:
        return

    player = dst.player
    proto = effect.effectProto
    
    player.telelink = None
    
    if proto.teleport:
        if not player.zone or not player.zone.zone:
            return #fix this, one teleport effect per character please
        
        teleport = proto.teleport
        teleportDst = proto.teleportDst
        if teleport.lower() == 'bindstone':
            if player.darkness:
                teleport = player.darknessBindZone.name
                trans = player.darknessBindTransform
            elif player.monster:
                teleport = player.monsterBindZone.name
                trans = player.monsterBindTransform
            else:
                teleport = player.bindZone.name
                trans = player.bindTransform
            teleportDst = ' '.join(str(i) for i in trans)
        
        #are we in the same zone?
        if player.zone.zone.name == teleport:
            #good
            #we just need to respawn player, whew
            player.zone.respawnPlayer(player,teleportDst)
        else:
            from mud.world.zone import TempZoneLink
            zlink = TempZoneLink(teleport,teleportDst)
            player.world.onZoneTrigger(player,zlink)


def DoTeleport(effect, src, dst):
    #sets the tp, will tp next tick
    if not dst.player:
        return
    
    if effect.effectProto.teleport:
        dst.player.telelink = (effect,src,dst)
        return



# Nonlinear stacking means that the strongest effect will
#  count with 100%, the second strongest at 50%, the third
#  at 25% and so on.
# Apply this special stacking rule to all stats listed in
#  the following dictionary. The value is true if the stat
#  is beneficial when positive.
# Before just adding a stat here, first check where in effect
#  application the function doEffectStackNonlinear actually
#  gets called. Doesn't work on stats in RPG_DERIVEDSTATS,
#  RPG_RESISTSTATS, fear or effectHaste.

EFFECTSTACK_NONLINEAR = {'move': True, 'swim': True}



class Effect:
    def __init__(self,parent,src,dst,proto,time,mod=1.0,fromStore=False,healMod=1.0,damageMod=1.0):
        self.effectProto = proto
        self.time = time
        self.parent = parent #can be a spell, etc
        self.src = src
        self.dst = dst
        self.fromStore = fromStore
        
        self.leechTimer = 0
        self.drainTimer = 0
        self.regenTimer = 0
        
        self.mod = mod
        self.popped = False
        
        #accumulated damage (spell outputs this stuff)
        self.damage = 0
        self.stats = {}
        
        self.healMod = healMod
        self.damageMod = damageMod
        
        self.statMods = defaultdict(int)
        self.derivedStatMods = defaultdict(int)
    
    
    def takeOwnership(self,newOwner):
        self.src = newOwner
    
    
    def globalPush(self):
        #apply stats and stuff
        proto = self.effectProto
        src = self.src
        dst = self.dst
        dst.derivedDirty = True
        fromStore = self.fromStore
        
        if not fromStore:
            for dmg in proto.damage:
                if dmg.stage == RPG_EFFECT_STAGE_GLOBAL:
                    value = dmg.amount * (self.mod + self.damageMod)
                    Damage(dst,src,value,dmg.type)
        
        nonlinears = defaultdict(int)
        for st in proto.stats:
            if st.stage == RPG_EFFECT_STAGE_GLOBAL:
                statname = st.statname
                if statname == "feignDeath":
                    src.autoAttack = False
                    src.attackOff()
                    if src.casting:
                        src.casting.cancel()
                        if src.player:
                            src.player.sendGameText(RPG_MSG_GAME_DENIED,"%s's casting has been interrupted!\\n"%(src.name))
                
                value = st.value * self.mod
                
                # Don't heal again after zoning or login.
                doMore = True
                if not fromStore:
                    if statname == 'health':
                        if value < 0:
                            Damage(dst,src,-value + st.value * self.damageMod,DAMAGEFORRESIST[proto.resist])
                        else:
                            Heal(dst,src,value + st.value * self.healMod)
                        doMore = False
                    elif statname in ('mana','stamina'):
                        setattr(dst,statname,getattr(dst,statname) + value)
                        doMore = False
                if doMore:
                    if statname in RPG_DERIVEDSTATS:
                        self.derivedStatMods[statname] += value
                    elif statname in RPG_RESISTSTATS:
                        dst.resists[RPG_RESISTLOOKUP[statname]] += value
                        self.statMods[statname] += value
                    else:
                        if src.player and statname == "fear" and not dst.simObject.canKite:
                            src.player.sendGameText(RPG_MSG_GAME_DENIED,r'Fear effects only work in open areas.\n')
                        
                        if statname == "effectHaste":
                            effect,oldValue = dst.effectHaste
                            if oldValue < value:
                                dst.effectHaste = (self,value)
                                self.statMods[statname] += value
                            continue
                        if statname in EFFECTSTACK_NONLINEAR:
                            nonlinears[statname] += value
                            continue
                        try:
                            newValue = getattr(dst,statname) + value
                            # Clamp new attribute value in a small range to zero,
                            #  so comparison against zero doesn't fail even with
                            #  floating point precision problems.
                            if abs(newValue) < 0.0009:
                                newValue = 0
                            setattr(dst,statname,newValue)
                            self.statMods[statname] += value
                        except:
                            traceback.print_exc()
        
        # Apply the nonlinearly stacking stats.
        for statname,value in nonlinears.iteritems():
            dst.doEffectStackNonlinear(statname,value)
            self.statMods[statname] = value
        
        # If the effect provides damage reflection, update mobs reflection information.
        if proto.dmgReflectionMax:
            
            # Get list of protos or create an empty list based on the reflection type.
            try:
                dmgReflectionEffects = dst.dmgReflectionEffects[proto.dmgReflectionType]
            except:
                dst.dmgReflectionEffects[proto.dmgReflectionType] = dmgReflectionEffects = list()
                
            # Add proto to list.
            dmgReflectionEffects.append(proto)
 
  
    def begin(self):
        src = self.src
        dst = self.dst
        
        # First handle resurrection. Since all effects need to be applied to target,
        #  resurrection does stats itself. Only health, mana and stamina can be
        #  coupled with this effect, rest gets ignored.
        # This because resurrection target is volatile and dynamic and other
        #  stats / effects may not be cancelled on spell end.
        try:
            if not self.fromStore:
                if DoResurrection(self,src,dst):
                    return True
        except:
            traceback.print_exc()
        
        self.globalPush()
        self.iter = self.tick()
        proto = self.effectProto
        dst.derivedDirty = True
        
        if self.time == 0:
            for dmg in proto.damage:
                if dmg.stage == RPG_EFFECT_STAGE_BEGIN:
                    value = dmg.amount * (self.mod + self.damageMod)
                    Damage(dst,src,value,dmg.type)
            
            nonlinears = defaultdict(int)
            for st in proto.stats:
                if st.stage == RPG_EFFECT_STAGE_BEGIN:
                    statname = st.statname
                    value = st.value * self.mod
                    if statname == 'health' and value < 0:
                        Damage(dst,src,-value + st.value * self.damageMod,DAMAGEFORRESIST[proto.resist])#, textDesc = None):
                    elif statname == 'health' and value > 0:
                        Heal(dst,src,value + st.value * self.healMod)
                    elif statname in ('mana','stamina'):
                        setattr(dst,statname,getattr(dst,statname) + value)
                    elif statname in EFFECTSTACK_NONLINEAR:
                        nonlinears[statname] += value
                    else:
                        try:
                            newValue = getattr(dst,statname) + value
                            # Clamp new attribute value in a small range to zero,
                            #  so comparison against zero doesn't fail even with
                            #  floating point precision problems.
                            if abs(newValue) < 0.0009:
                                newValue = 0
                            setattr(dst,statname,newValue)
                            self.statMods[statname] += value
                        except:
                            traceback.print_exc()
            
            # Apply the nonlinearly stacking stats.
            for statname,value in nonlinears.iteritems():
                dst.doEffectStackNonlinear(statname,value)
                self.statMods[statname] = value
        
        try:
            if not self.fromStore:
                DoTeleport(self,src,dst)
                DoSummonPet(self,src)
                DoSummonItem(self,src)
                DoPermanentStats(self,src,dst)
                DoGiveSkill(self,src,dst)
                DoCharm(self,src,dst)
                DoNegate(self,src,dst)
                DoBanish(self,src,dst)
                DoInterrupt(self,src,dst)
            DoIllusion(self,src,dst)
        except:
            traceback.print_exc()
        
        return True
    
    
    #generator function
    def tick(self):
        while 1:
            DoDrain(self)
            DoLeech(self)
            DoRegen(self)
            
            self.time += 1
            
            yield True
    
    
    def end(self):
        #parent will global pop
        #self.globalPop()
        return
    
    
    def cancel(self):
        self.canceled = True
        self.iter = None
        #self.end() don't get end stuff
    
    
    def globalPop(self):
        dst = self.dst
        dst.derivedDirty = True
        UndoIllusion(self)
        BreakCharm(self)
        
        for statname,value in self.statMods.iteritems():
            if statname == "effectHaste":
                effect,effectValue = dst.effectHaste
                if effect == self:
                    #find best
                    bestEffect = None
                    bestEffectValue = 0
                    for process in dst.processesIn:
                        if process == self.parent:
                            continue
                        if isinstance(process,spell.Spell):
                            for effect in process.effects:
                                try:
                                    v = effect.statMods['effectHaste']
                                except KeyError:
                                    continue
                                if v > bestEffectValue:
                                    bestEffectValue = v
                                    bestEffect = effect
                    dst.effectHaste = (bestEffect,bestEffectValue)
                continue
            
            if statname in RPG_RESISTSTATS:
                dst.resists[RPG_RESISTLOOKUP[statname]] -= value
            elif statname in EFFECTSTACK_NONLINEAR:
                dst.doEffectUnstackNonlinear(statname,value)
            else:
                try:
                    newValue = getattr(dst, statname) - value
                    # Clamp new attribute value in a small range to zero,
                    #  so comparison against zero doesn't fail even with
                    #  floating point precision problems.
                    if abs(newValue) < 0.0009:
                        newValue = 0
                    setattr(dst, statname, newValue)
                except:
                    traceback.print_exc()

        # If the effect provides damage reflection, remote it from mobs list.
        proto = self.effectProto
        if proto.dmgReflectionMax:
            
            try:
                
                # Get list of protos based on damage reflection type.
                dmgReflectionEffects = dst.dmgReflectionEffects[proto.dmgReflectionType]

                # Remove the proto.
                dmgReflectionEffects.remove(proto)
                
                # Remove from dictionary if there are no more protos.
                if not len(dmgReflectionEffects):
                    del dst.dmgReflectionEffects[proto.dmgReflectionType]

            except:
                pass
            


"""

mob types:
normal
undead
summoned
plant
planar
demon
elemental
animal

some of this stuff goes into spell/skill

cast time
recast time
fizzle time
range
activated

skill
mana cost 


components

target self
target aoe
target single
target party
target pet
target alliance


harmful <-- flag
watchful aura that notifies you when invaded (area when mob walks into)

#combat
#modify combat stats
increased melee damage (with damage type), dual wield every round, every hit a critical,etc
impossible to miss,always riposte, damage to me every time I hit

"""


