# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud.common.persistent import Persistent
from mud.world.defines import *
from mud.world.item import Item,ItemSpellTemp
from mud.world.spell import SpellProto

from copy import copy
from math import fabs
from random import randint
from sqlobject import *
import traceback



# Types of item variants
# Stats
V_STAT = 0
# Special weapon stats, namely rate, damage, resist and debuff
V_WEAPON = 1
# Bane weapons
V_BANEWEAPON = 2
# Weapon procs, poisons and enchantings. Permanent procs are handled differently.
V_WEAPONPROC = 3



#(code,min level, max level, x in y (chance), weaponsonly)
VARIANTS=[
(V_BANEWEAPON,10,100,1,25,True),
(V_WEAPON,5,100,1,15,True),
#up to 10 stats (generated and collapsed) ... up to +110/-110 on a stat
(V_STAT,1,100,1,20,False),
(V_STAT,10,100,1,15,False),
(V_STAT,20,100,1,10,False),
(V_STAT,30,100,1,5,False),
(V_STAT,40,100,1,5,False),
(V_STAT,50,100,1,5,False),
(V_STAT,60,100,1,3,False),
(V_STAT,70,100,1,3,False),
(V_STAT,80,100,1,2,False),
(V_STAT,90,100,1,2,False),
]


class ItemVariant(Persistent):
    item = ForeignKey("Item")
    
    code = IntCol()
    
    value = IntCol(default = 0) 
    value2 = IntCol(default = 0) 
    value3 = IntCol(default = 0) 
    value4 = IntCol(default = 0) 
    value5 = IntCol(default = 0)
    
    svalue = StringCol(default="")


def ItemVariantsLoad(item):
    dbItem = item.item
    restoredVariants = {}
    for variant in list(dbItem.variants):
        if variant.code == V_STAT:
            if dbItem.spellEnhanceLevel == 9999:  # indicates an enchanted item, additional stat value
                if variant.value2:	# hack for float values
                    statValue = float(variant.value) + float(variant.value2) / 100.0
                else:
                    statValue = variant.value
                var = (variant.svalue,statValue)
            else:
                var = (variant.svalue,variant.value)
            try:
                restoredVariants[V_STAT].append(var)
            except KeyError:
                restoredVariants[V_STAT] = [var]
        # Because of their unique abilities, V_WEAPON mods need to be kept separately.
        # They get stored in a list so one can still edit them independently.
        elif variant.code == V_WEAPON:
            restoredVariants[V_WEAPON] = [variant.value,variant.value2,variant.value3,variant.value4]
        elif variant.code == V_BANEWEAPON:
            restoredVariants[V_BANEWEAPON] = (variant.svalue,variant.value)
        elif variant.code == V_WEAPONPROC:
            proc = ItemSpellTemp(SpellProto.byName(variant.svalue),RPG_ITEM_TRIGGER_POISON,variant.value)
            item.procs[proc] = [variant.value2,variant.value3]
    item.variants = restoredVariants

def ItemVariantsSave(item):
    dbItem = item.item
    variantList = list(dbItem.variants)
    if not item.hasVariants and not len(item.procs):
        for variant in variantList:
            variant.destroySelf()
        return
    
    # Meh, copy is too shallow and deepcopy too far...
    # Parse list manually
    currentVariants = dict((key,copy(value)) for key,value in item.variants.iteritems())
    currentProcs = dict(((proc.spellProto.name,proc.frequency),data) for proc,data in item.procs.iteritems())
    
    # first clear out all variants that don't need new saving
    for variant in variantList:
        if variant.code == V_STAT:
            if item.spellEnhanceLevel == 9999:  # indicates an enchanted item, additional stat value
                if variant.value2:	# hack for float values
                    statValue = float(variant.value) + float(variant.value2) / 100.0
                else:
                    statValue = variant.value
                var = (variant.svalue,statValue)
            else:
                var = (variant.svalue,variant.value)
            try:
                currentVariants[V_STAT].remove(var)
                if not len(currentVariants[V_STAT]):
                    del currentVariants[V_STAT]
            except:
                variant.destroySelf()
        elif variant.code == V_WEAPON:
            try:
                if currentVariants[V_WEAPON] != [variant.value,variant.value2,variant.value3,variant.value4]:
                    variant.value,variant.value2,variant.value3,variant.value4 = currentVariants[V_WEAPON]
                del currentVariants[V_WEAPON]
            except KeyError:
                variant.destroySelf()
        elif variant.code == V_BANEWEAPON:
            try:
                if currentVariants[V_BANEWEAPON] != (variant.svalue,variant.value):
                    variant.svalue,variant.value = currentVariants[V_BANEWEAPON]
                del currentVariants[V_BANEWEAPON]
            except KeyError:
                variant.destroySelf()
        elif variant.code == V_WEAPONPROC:
            try:
                procid = (variant.svalue,variant.value)
                if currentProcs[procid] != [variant.value2,variant.value3]:
                    variant.value2,variant.value3 = currentProcs[procid]
                del currentProcs[procid]
            except KeyError:
                variant.destroySelf()
        # No longer supported or defect variant.
        else:
            variant.destroySelf()
    
    # for the rest generate new ItemVariant db entries
    for code,variants in currentVariants.iteritems():
        if code == V_STAT:
            if item.spellEnhanceLevel == 9999:  # indicates an enchanted item, additional stat value
                for var in variants:
                    intValue = int(var[1])
                    floatHack = int(round((var[1] - intValue) * 100.0))
                    ItemVariant(item = dbItem,code = code,svalue = var[0],value = intValue,value2 = floatHack)
            else:
                for var in variants:
                    ItemVariant(item = dbItem,code = code,svalue = var[0],value = var[1])
        elif code == V_WEAPON:
            ItemVariant(item = dbItem,code = code,value = variants[0],value2 = variants[1],value3 = variants[2],value4 = variants[3])
        elif code == V_BANEWEAPON:
            ItemVariant(item = dbItem,code = code,svalue = variants[0],value = variants[1])
    
    # Generate new ItemVariant entries for volatile procs to store.
    for procid,procdata in currentProcs.iteritems():
        ItemVariant(item = dbItem,code = V_WEAPONPROC,svalue = procid[0],value = procid[1],value2 = procdata[0],value3 = procdata[1])




# --- VSTAT (adds a single stat to an item)

VSTAT_STATS = ("str","mnd","dex","bdy","agi","wis","mys","ref",
"resistPhysical","resistMagical","resistCold","resistFire","resistAcid","resistPoison","resistDisease","resistElectrical",
"armor","maxMana","maxHealth")

VSTAT_VALUES = {}
VSTAT_VALUES["str"]=(-11,-7,-5,-3,-1,1,3,5,7,11)
VSTAT_VALUES["mnd"]=(-11,-7,-5,-3,-1,1,3,5,7,11)
VSTAT_VALUES["dex"]=(-11,-7,-5,-3,-1,1,3,5,7,11)
VSTAT_VALUES["bdy"]=(-11,-7,-5,-3,-1,1,3,5,7,11)
VSTAT_VALUES["agi"]=(-11,-7,-5,-3,-1,1,3,5,7,11)
VSTAT_VALUES["wis"]=(-11,-7,-5,-3,-1,1,3,5,7,11)
VSTAT_VALUES["mys"]=(-11,-7,-5,-3,-1,1,3,5,7,11)
VSTAT_VALUES["ref"]=(-11,-7,-5,-3,-1,1,3,5,7,11)

VSTAT_VALUES["resistPhysical"]=(1,2,3,4,5,6,7,8,9,10)
VSTAT_VALUES["resistMagical"]=(1,2,3,4,5,6,7,8,9,10)
VSTAT_VALUES["resistFire"]=(1,2,3,4,5,6,7,8,9,10)
VSTAT_VALUES["resistCold"]=(1,2,3,4,5,6,7,8,9,10)
VSTAT_VALUES["resistElectrical"]=(1,2,3,4,5,6,7,8,9,10)
VSTAT_VALUES["resistAcid"]=(1,2,3,4,5,6,7,8,9,10)
VSTAT_VALUES["resistDisease"]=(1,2,3,4,5,6,7,8,9,10)
VSTAT_VALUES["resistPoison"]=(1,2,3,4,5,6,7,8,9,10)

VSTAT_VALUES["armor"]=(5,15,25,40,80,100,150,250,300,400)

VSTAT_VALUES["maxMana"]=(5,15,25,40,80,100,150,250,300,400)
VSTAT_VALUES["maxHealth"]=(5,15,25,40,80,100,150,250,300,400)

VSTAT_SUFFIXES = {}
VSTAT_SUFFIXES["str"]=("of Impotence","of Feebleness","of Weakness","of Failing","of Deficiency","of Strength","of Might","of Clout","of Force","of Power")
VSTAT_SUFFIXES["dex"]=("of Ineptitude","of Uncoordination","of Clumsiness","of Awkwardness","of Tribulation","of Dexterity","of Proficiency","of Handiness","of Adroitness","of Finesse")
VSTAT_SUFFIXES["agi"]=("of Oafishness","of Ungainliness","of Gawkiness","of Inelegance","of Gracelessness","of Agility","of Briskness","of Nimbleness","of Spryness","of Alacrity")
VSTAT_SUFFIXES["ref"]=("of Lethargy","of Sluggishness","of Listlessness","of Languidness","of Stiffness","of Reflex","of Response","of Impulse","of Spontaneity","of Instinct")
VSTAT_SUFFIXES["bdy"]=("of Consumption","of Infirmity","of Sickness","of Affliction","of Hardship","of Fortitude","of Chutzpah","of Hardiness","of Perseverance","of Stability",)
VSTAT_SUFFIXES["wis"]=("of Foolishness","of Folly","of Silliness","of Triviality","of Rashness","of Wisdom","of Sense","of Discernment","of Prudence","of Judgement")
VSTAT_SUFFIXES["mys"]=("of Materialism","of Mundaneness","of Temporalness","of Corporealness","of Normality","of Mysticism","of Abstruseness","of Esotericism","of Spirtiualism","of Trancendence")
VSTAT_SUFFIXES["mnd"]=("of Stupidity","of Idiocy","of Dumbness","of Dullness","of Denseness","of Comprehension","of Understanding","of Savvy","of Ingenuity","of Sagacity")
VSTAT_SUFFIXES["maxMana"]=("of Presage","of Thaumaturgy","of Thaumaturgy","of Invocation","of Sorcery","of Channeling","of Incantation","of Allurement","of Soothsaying","of Enlightenment")
VSTAT_SUFFIXES["maxHealth"]=("of Zeal","of Verve","of Hardiness","of Robustness","of Wholeness","of Heroism","of Tenacity","of Perseverance","of Persistance","of Permanence")

VSTAT_PREFIXES = {}
VSTAT_PREFIXES["resistPhysical"]=("Obstinate","Steadfast","Reliable","Staunch","Unwavering","Unyielding","Resolute","Unfaltering","Faithful","Eternal")
VSTAT_PREFIXES["resistMagical"]=("Shimmering","Lustrous","Luminous","Radiant","Dazzling","Scintillating","Opalescent","Prismatic","Chromatic","Astral")
VSTAT_PREFIXES["resistFire"]=("Flickering","Ardent","Fervent","Sizzling","Fiery","Blazing","Conflagrant","Searing","Scalding","Torrid")
VSTAT_PREFIXES["resistCold"]=("Shivering","Frigid","Numbing","Bitter","Frosty","Icy","Frozen","Polar","Arctic","Glacial")
VSTAT_PREFIXES["resistElectrical"]=("Tingling","Insulated","Grounded","Arcing","Isolating","Dissipating","Capacitive","Recalcitrant","Resistive","Anionic")
VSTAT_PREFIXES["resistDisease"]=("Filthy","Repulsive","Feculent","Viral","Infectious","Festering","Putrid", "Pestilent","Corrupt","Vile")
VSTAT_PREFIXES["resistPoison"]=("Toxic","Toxic","Noxious","Noxious","Lethal","Septic","Tainted","Viperous","Nocuous","Envenomed")
VSTAT_PREFIXES["resistAcid"]=("Biting","Biting","Caustic","Caustic","Corrosive","Corrosive","Consumptive","Pungent","Trenchant","Acerbic")
VSTAT_PREFIXES["armor"]=("Hardened","Sturdy","Strong","Noble","Glorious","Blessed","Saintly","Holy","Divine","Godly")


def ApplyVStats(item):
    try:
        variantList = item.variants[V_STAT]
    except KeyError:
        variantList = []
    
    stats = dict((s,v) for s,v in item.stats)
    kingValue = 0
    prefix,suffix = "",""
    
    for variant in variantList[:]:
        stat = variant[0]  # get svalue
        value = VSTAT_VALUES[stat][variant[1]]
        if fabs(value) > kingValue:
            kingValue = fabs(value)
            if VSTAT_SUFFIXES.has_key(stat):
                suffix = VSTAT_SUFFIXES[stat][variant[1]]
            if VSTAT_PREFIXES.has_key(stat):
                prefix = VSTAT_PREFIXES[stat][variant[1]]
        
        try:
            stats[stat] += value
        except KeyError:
            stats[stat] = value
    
    item.stats = [(s,v) for s,v in stats.iteritems()]
    
    return prefix,suffix


def GenVStat(item,level):
    allgood = ("resistPhysical","resistMagical","resistFire","resistCold","resistElectrical","resistDisease","resistPoison","resistAcid",
    "armor","maxMana","maxHealth")
    
    try:
        variants = item.variants[V_STAT]
    except KeyError:
        variants = []
    
    if len(variants) and randint(0,3):  # 75% chance of sticking with an existing stat
        if len(variants)==1:
            x = 0
        else:
            x = randint(0,len(variants)-1)
        stat = variants[x][0]  # get svalue
    else:  # random stat
        stat = VSTAT_STATS[randint(0,len(VSTAT_STATS)-1)]
    
    if stat not in allgood:
        levels = (10,20,40,80)
        x = 0
        for lev in levels:
            if lev>level:
                break
            x+=1
        
        #0-5 = how much
        basechances = (10,8,4,1)
        v = 0
        for c in xrange(0,x):
            if randint(1,basechances[c]) == 1:
                v = c+1
                #don't break and we'll have a shot at higher level stuff break
        
        gotone = False
        for var in variants:
            if var[0] == stat:  # var[0] equals the stats svalue
                if var[1] >= 5:  # keep going in same direction on existing stat
                    v += 5
                gotone = True
                break
        if not gotone:  # first one on this stat sets the stage
            v += 5
            if not randint(0,9):  # one in 10 is crap
                v -= 5
    
    else:  # allgood
        levels = (10,20,30,40,50,60,70,80,90)
        x = 0
        for lev in levels:
            if lev>level:
                break
            x+=1
        chances = (20,15,15,15,10,10,10,5,2)
        v = 0
        for c in xrange(0,x):
            if randint(1,chances[c]) == 1:
                v = c+1
    
    try:
        item.variants[V_STAT].append((stat,v))
    except KeyError:
        item.variants[V_STAT] = [(stat,v)]




# --- V_WEAPON

VWEAPON_TEXT = {}
VWEAPON_DEBUFFS_VALUES = (5,15,25,50,75,100)
VWEAPON_DEBUFFS = (RPG_RESIST_PHYSICAL,RPG_RESIST_MAGICAL,RPG_RESIST_FIRE,RPG_RESIST_COLD,RPG_RESIST_POISON,RPG_RESIST_DISEASE,RPG_RESIST_ACID,RPG_RESIST_ELECTRICAL)
VWEAPON_TEXT["debuff"]=("of Lucidity","of Warding","of Warmth","of Frost","of Remedy","of Vigor","of Corrosion","of Conductivity")
VWEAPON_DAMAGE_VALUES = (1,2,3,5,10,15)
VWEAPON_TEXT["dmg"]=("Savage","Vicious", "Ruthless", "Cruel","Merciless","Vorpal")
VWEAPON_RATE_VALUES = (1,2,3,4,5,6)
VWEAPON_TEXT["rate"]=("Snappy","Swift","Quick", "Rapid","Screaming", "Velocious")
# damage + rate mods + resist debuffs


# Only one Weapon variation per item
def ApplyVWeapon(item):
    try:
        dmg,rate,resist,debuff = item.variants[V_WEAPON]
    except KeyError:
        return "",""
    except ValueError:  # silently delete invalid weapon variant (probably just an empty tuple)
        del item.variants[V_WEAPON]
        return "",""
    
    if dmg != -1:
        d = item.wpnDamage + VWEAPON_DAMAGE_VALUES[dmg]
        item.wpnDamage = d
    
    if rate != -1:
        #hm
        r = item.wpnRate - VWEAPON_RATE_VALUES[rate]
        if r < 1:
            r = 1
        item.wpnRate = r
    
    if debuff != -1:
        #overwrite whatever is there, gah
        item.wpnResistDebuff = VWEAPON_DEBUFFS[resist]
        item.wpnResistDebuffMod = VWEAPON_DEBUFFS_VALUES[debuff]
    
    prefix = ""
    if dmg != -1 or rate != -1:
        if rate > dmg:
            key,value = "rate",rate
        else:
            key,value = "dmg",dmg
        prefix = VWEAPON_TEXT[key][value]
    
    suffix = ""
    if debuff != -1:
        suffix = VWEAPON_TEXT["debuff"][resist]
    
    return prefix,suffix


def GenVWeapon(item,level):
    levels = (0,10,20,40,60,80)
    chances = (-1,15,10,5,4,2)
    
    x = 0
    for lev in levels:
        if lev>level:
            break
        x+=1
    
    dmg = -1
    rate = -1
    debuff = -1
    
    #1 in 10 chance of having
    if not randint(0,9):
        dmg = 0
    if not randint(0,9):
        rate = 0
    if not randint(0,9):
        debuff = 0
    
    if dmg == -1 and rate == -1 and debuff == -1:
        #didn't get any so it'll be one
        r = randint(1,3)
        if r == 1:
            dmg = 0
        elif r == 2:
            rate = 0
        else:
            debuff = 0
    
    if dmg == 0:
        for c in xrange(1,x):
            if randint(1,chances[c])==1:
                dmg += 1
    if rate == 0:
        for c in xrange(1,x):
            if randint(1,chances[c])==1:
                rate += 1
    if debuff == 0:
        for c in xrange(1,x):
            if randint(1,chances[c])==1:
                debuff += 1
    
    item.variants[V_WEAPON] = [dmg,rate,randint(0,len(VWEAPON_DEBUFFS) - 1),debuff]




# --- BANE WEAPONS

VBANEWEAPON_RACES = ("Undead","Giant","Human","Dwarf","Elf","Halfling","Drakken","Ogre","Troll","Goblin","Orc","Gnome","Plant","Animal","Dark Elf","Titan")
VBANEWEAPON_MODS = (0,2,3,4,6,8)
VBANEWEAPON_TEXT = ("of %s Butchering","of %s Slaughtering","of %s Slaying","of %s Annihilation","of %s Eradication","of %s Bane")


# Only one bane variation per weapon
def ApplyVBaneWeapon(item):
    try:
        race,value = item.variants[V_BANEWEAPON]
    except KeyError:
        return "",""
    except ValueError:  # silently delete invalid weapon variant (probably just an empty tuple)
        del item.variants[V_BANEWEAPON]
        return "",""
    
    item.wpnRaceBane = race
    item.wpnRaceBaneMod = VBANEWEAPON_MODS[value]
    
    return "",VBANEWEAPON_TEXT[value]%race


def GenVBaneWeapon(item,level):
    levels = (0,10,20,40,60,80)
    chances = (-1,10,5,4,3,2)
    
    x = 0
    for lev in levels:
        if lev > level:
            break
        x += 1
    
    v  = 0
    for c in xrange(1,x):
        if randint(1,chances[c]) == 1:
            v += 1
    
    #what race?
    r = randint(0,len(VBANEWEAPON_RACES)-1)
    race = VBANEWEAPON_RACES[r]
    
    item.variants[V_BANEWEAPON] = (race,v)




#-------------------------------------------------------------------------------

#GENERATION FUNCTIONS
GENERATE = {}
GENERATE[V_STAT]       = GenVStat
GENERATE[V_WEAPON]     = GenVWeapon
GENERATE[V_BANEWEAPON] = GenVBaneWeapon

#-------------------------------------------------------------------------------




def ApplyVariants(item):
    try:
        proto = item.itemProto
        newname = proto.name
        
        variants = item.variants
        numVariants = item.numVariants()
        
        if numVariants:
            #repair baseline
            repairMax = item.levelOverride * 5
            if item.repairMax < repairMax and proto.repairMax > 0:
                item.repairMax = repairMax
        
        prefix,suffix   = ApplyVBaneWeapon(item)
        pPrefix,pSuffix = ApplyVWeapon(item)
        if not prefix:
            prefix = pPrefix
        if not suffix:
            suffix = pSuffix
        pPrefix,pSuffix = ApplyVStats(item)
        if not prefix:
            prefix = pPrefix
        if not suffix:
            suffix = pSuffix
        
        if prefix:
            newname = "%s %s"%(prefix,newname)
        if suffix:
            newname = "%s %s"%(newname,suffix)
        item.name = newname
        
    except:
        traceback.print_exc()


def GenVariantItem(item,level,force = False):
    try:
        proto = item.itemProto
        #do not apply to items that are artifacts, stackable or cannot be equipped
        if item.flags&RPG_ITEM_ARTIFACT or not len(proto.slots) or proto.stackMax > 1:
            return
        
        variants = item.variants
        gotone = False
        for code,min,max,x,y,weapons in VARIANTS:
            if weapons and not item.wpnDamage:
                continue
            if level < min:
                continue
            if level > max:
                continue
            
            r = randint(x,y)
            if force and code == V_STAT:
                force = False
                r = x-1
            if r > x:
                continue
            
            gotone = True
            GENERATE[code](item,level)
        
        if gotone:
            item.hasVariants = True
            item.levelOverride = level - 10
            if item.levelOverride < 1:
                item.levelOverride = 1
            item.refreshFromProto()
    
    except:
        traceback.print_exc()




# Function to add a single specific variant to an item.
# Bane modifications come with statname '<race> Bane'
ADDITIONAL_STATS = ("maxStamina","regenHealth","regenMana","regenStamina","haste","castHaste","move",'castHealMod','castDmgMod')

def AddStatVariant(item,statname,statvalue):
    try:
        if statname == 'Damage Mod':
            item.variants.setdefault(V_WEAPON,[-1,-1,-1,-1])[0] = statvalue
        elif statname == 'Weapon Speed':
            item.variants.setdefault(V_WEAPON,[-1,-1,-1,-1])[1] = statvalue
        elif statname == 'Debuff':
            item.variants.setdefault(V_WEAPON,[-1,-1,-1,-1])[2] = statvalue[0]
            item.variants[V_WEAPON][3] = statvalue[1]
        else:
            splitter = statname.rsplit(' ',1)
            if statvalue:
                if splitter[-1].upper() == "BANE" and splitter[0] in VBANEWEAPON_RACES:
                    value = int(round(statvalue))
                    if value < 0:
                        value = 0
                    elif value > 12:
                        value = 12
                    item.variants[V_BANEWEAPON] = (splitter[0],value)
                elif statname in VSTAT_STATS or statname in ADDITIONAL_STATS:
                    var = (statname,statvalue)
                    try:
                        item.variants[V_STAT].append(var)
                    except KeyError:
                        item.variants[V_STAT] = [var]
    except:
        traceback.print_exc()


# Function to apply the enchantment specific variants.
def ApplyEnchantment(item):
    from mud.world.crafting import ENCHANT_SlotLUT
    
    # apply variants
    try:
        # all necessary attributes have been sorted on creation of variants, just overwrite existing
        item.stats = []
        item.wpnRaceBane = ""
        item.wpnRaceBaneMod = 0
        proto = item.itemProto
        # Check if the item is allowed to bear an enhancement.
        for islot in proto.slots:
            if islot in ENCHANT_SlotLUT:
                break
        else:  # Not allowed!
            return
        rel = proto.level / 100.0
        enchStatMod = 0.005 + 0.995 * rel * rel
        
        try:
            statVariants = item.variants[V_STAT]
        except KeyError:
            statVariants = []
        
        if len(statVariants):
            stats = {}
            for svalue,value in statVariants:
                for prop in ENCHANT_SlotLUT['all'].itervalues():
                    if prop[0] == svalue:
                        maxVal = enchStatMod * prop[1]
                        if prop[1] >= 10:
                            maxVal = int(maxVal)
                        break
                else:
                    try:
                        for prop in ENCHANT_SlotLUT[proto.slots[0]].itervalues():
                            if prop[0] == svalue:
                                maxVal = enchStatMod * prop[1]
                                if prop[1] >= 10:
                                    maxVal = int(maxVal)
                                break
                        else:  # huh, we seem to have removed that enchantment type, did we
                            continue
                    except KeyError:
                        continue
                if value > maxVal:
                    value = maxVal
                try:
                    stats[svalue] += value
                except KeyError:
                    stats[svalue] = value
            item.stats = [(s,v) for s,v in stats.iteritems()]
        
        try:
            maxBane = int(enchStatMod * ENCHANT_SlotLUT[RPG_SLOT_PRIMARY]["the Ghoul Slayer"][1])
            race,bane = item.variants[V_BANEWEAPON]
            item.wpnRaceBane = race
            if bane > maxBane:  # fix messed up stats in db
                item.variants[V_BANEWEAPON] = (race,maxBane)
                bane = maxBane
            elif bane < 0:  # fix messed up stats in db
                item.variants[V_BANEWEAPON] = (race,0)
                bane = 0
            item.wpnRaceBaneMod = bane
        except KeyError:
            pass
    except:
        traceback.print_exc()


