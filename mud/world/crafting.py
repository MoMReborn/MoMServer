# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.persistent import Persistent
from mud.world.core import GenMoneyText
from mud.world.defines import *
from mud.world.item import getTomeAtLevelForScroll,ItemProto,ItemSpellTemp
from mud.world.itemvariants import AddStatVariant,V_BANEWEAPON,V_STAT,V_WEAPON
from mud.world.spell import Spell,SpellProto
from mud.world.shared.sounddefs import *
from mud.worlddocs.utils import GetTWikiName

from collections import defaultdict
from math import ceil
from random import randint
from sqlobject import *



#Blacksmithing
#Tailoring
#Weapon Craft 
#Armor Craft 
#Alchemy
#Enchanting
#Cooking
#Scribing

WEAPON_SKILLS = (
"1H Pierce",
"2H Pierce",
"1H Impact",
"2H Impact",
"1H Cleave",
"2H Cleave",
"1H Slash",
"2H Slash",
"Archery"
)

ARMOR_SKILLS = (
"Light Armor",
"Medium Armor",
"Heavy Armor",
"Shield"
)


"""
# -------------------------------------------------------------------------------------
not yet implemented, future stuff - Llarlen


# Advanced ingredients are ingredients for the advanced recipes described further below,
#  packed up in advanced ingredient constellations.
# Unlike 'standard' ingredients they don't link to an item proto but to an ingredient type
#  which will have to be set on the specific item protos.
#  Multiple item protos can link to the same advanced ingredient.
#  Also advanced ingredients already contain the basic effect they apply to the crafting output.
class RecipeIngredientAdvanced(Persistent):
    name = StringCol(alternateID=True)
    itemProtos = RelatedJoin('ItemProto')
    count = IntCol(default=1)
    ingredientConstellation = ForeignKey('RecipeIngredientConstellationAdvanced')
    recipe = ForeignKey('RecipeAdvanced')
    ... more fields



# Advanced ingredient constellations serve to pack up different advanced ingredients, so
#  exclusion and non-linear stacking checks can be made.
# Also may be used to apply additional effects to crafting output.
# Like: ingredient 1 has effect a, ingredient 2 has effect b,
#  ingredient 1 and 2 applied simultaneously has effect a, b and c; or only c.
class RecipeIngredientConstellationAdvanced(Persistent):
    name = StringCol(alternateID=True)
    ingredients = MultipleJoin('RecipeIngredientAdvanced')
    recipes = RelatedJoin('RecipeAdvanced')
    ... more fields



# Advanced recipes can be used to describe a whole bunch of various recipes at once,
#  with many dynamic modifications to the output.
# Unlike the 'standard' recipes, advanced recipes get defined some basic ingredients
#  (if any) and some variable ingredients. The base ingredients are always required.
#  Variable ingredients are different constellations of ingredients. Every constellation
#  may modify the output in a different way. Those ingredient constellations either
#  exclude each other or can be defined to produce a stacking effect.
#
# Purpose: to simplify enchanting (at least partially) code-wise and open up its
#  crafting functionality to other crafting types like alchemy, socketing, ...
class RecipeAdvanced(Persistent):
    name = StringCol(alternateID=True)
    
    # Sound that will be played on craft success
    craftSound = StringCol(default="")
    #--spell on success
    #--spell on failure
    
    # Required skill
    skillname = StringCol()
    
    # Base costs for a product.
    costTPBase = IntCol(default=0L)
    costHealthBase = IntCol(default=0)
    costStaminaBase = IntCol(default=0)
    costManaBase = IntCol(default=0)
    
    # Factors that determine how costs will diminish with increasing skill.
    # Setting a value < 1.0 will increase costs.
    costTPSkillMod = FloatCol(default=1.0)
    costHealthSkillMod = FloatCol(default=1.0)
    costStaminaSkillMod = FloatCol(default=1.0)
    costManaSkillMod = FloatCol(default=1.0)
    
    # Factors that determine how costs will increase with increasing difficulty.
    # Setting a value < 1.0 will decrease costs.
    costTPDiffMod = FloatCol(default=1.0)
    costHealthDiffMod = FloatCol(default=1.0)
    costStaminaDiffMod = FloatCol(default=1.0)
    costManaDiffMod = FloatCol(default=1.0)
    
    # Various filters to who is allowed crafting this stuff
    filterClass = StringCol(default="")
    filterRealm = IntCol(default=-1)
    filterRace = StringCol(default="")
    filterSkillLevelMin = IntCol(default=0)
    filterSkillLevelMax = IntCol(default=1000)
    
    # Base ingredients for this recipe type
    ingredientsStdBase = MultipleJoin('RecipeIngredient')
    ingredientsAdvancedBase = MultipleJoin('RecipeIngredientAdvanced')
    # Possible ingredient constellations for this recipe type
    ingredientConstellations = RelatedJoin('RecipeIngredientConstellationAdvanced')
    
    ... more fields


# -------------------------------------------------------------------------------------
"""


class RecipeIngredient(Persistent):
    recipe = ForeignKey('Recipe')
    itemProto = ForeignKey('ItemProto')
    count = IntCol(default=1)
    
class Recipe(Persistent):
    name = StringCol(alternateID = True)
    
    #result item
    craftedItemProto = ForeignKey('ItemProto')
    craftSound = StringCol(default="")
    
    skillname = StringCol()
    skillLevel = IntCol()
    
    filterClass = StringCol(default="")
    filterRealm = IntCol(default=-1)
    filterRace = StringCol(default="")
    filterLevelMin = IntCol(default=0)
    filterLevelMax = IntCol(default=1000)
    
    costTP = IntCol(default=0L)
    
    ingredients = MultipleJoin('RecipeIngredient')



# --- Blacksmithing
# list of forges per zone, list contains (location,active radius squared)
# Warning: active radiuses need testing
FORGE_LOOKUP = {
"anidaenforest":(654.112, -175.686, 146.782, 100),
"hazerothkeep":(716, 472, 210, 100),
"kauldur":(-245, -493, 150, 100),
"mountain":(650.116, -607.307, 160.346, 100),
"trinst":(128, 186, 127, 100)
}


def getBlacksmithingMods(mob,craftProto,skillLevel):
    noForge = False
    notify = False
    
    # Do not use forge if skill level is lower than or
    #  equal to 100.
    if 100 >= skillLevel or not mob.simObject:
        noForge = True
    
    # Set no forge and notify player if zone has no forge.
    elif mob.zone.zone.name not in FORGE_LOOKUP:
        noForge = True
        notify = True
    
    # The zone has a forge and player has a high enough
    #  skill level to use the forge.
    else:
        mobPos = mob.simObject.position
        forgePos = FORGE_LOOKUP[mob.zone.zone.name]
        x = mobPos[0] - forgePos[0]
        y = mobPos[1] - forgePos[1]
        z = mobPos[2] - forgePos[2]
        
        # If the player is out of range, do not use a forge
        #  and notify player.
        # Range tested is squared, so no need to take root of vector.
        if x*x + y*y + z*z > forgePos[3]:
            noForge = True
            notify = True
    
    # Get handles for faster lookups.
    player = mob.player
    char = mob.character
    
    # Notify player that they cannot use a forge.
    if notify:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s can't use a forge here and may only craft items of lesser quality.\\n"%char.name)
    
    # Get blacksmithing mods.
    protoUseMax = craftProto.useMax
    protoStackDefault = craftProto.stackDefault
    protoStackMax = craftProto.stackMax
    
    # Player is not using forge, use defaults.
    if noForge:
        charges = int(ceil(0.5 * float(protoUseMax)))
        stackCount = protoStackDefault
        moneyMod = 5.0
    
    # Player is using a forge.  Use the player's skill level
    #  to modify the resulting charges, stack count, and price.
    else:
        
        # Get modifier based on skill level.
        mod = float(skillLevel - 10) / 900.0
        
        # If the crafted item uses charges.
        if 1 < protoUseMax:
            charges = int(ceil(0.5 * float(protoUseMax) * (1.0 + mod)))
            if charges > protoUseMax:  # just a failsafe
                charges = protoUseMax
            stackCount = protoStackDefault
            moneyMod = 0.2 * (float(charges) - float(protoUseMax) / 2.0) + 1.0
        
        # If the crafted item stacks.
        elif 1 < protoStackMax:
            charges = protoUseMax
            stackCount = int(float(protoStackDefault) * (1.0 + mod))
            moneyMod = 0.2 * float(stackCount - protoStackDefault) + 1.0
        
        # Item neither uses charges nor stacks.
        else:
            charges = protoUseMax
            stackCount = 1
            moneyMod = 1.5 - mod
    
    # Return the calculated modifiers
    return (moneyMod,stackCount,charges)



# --- ENCHANTING / DISENCHANTING ---
# Some definitions for easier modding
ENCHANT_skillname = 'Enchanting'
# How many lower level enchanting materials will be needed to produce one of a higher level:
ENCHANT_MergeCount = 2
# How many different enchantments can be put on an item at maximum:
ENCHANT_MaxEnchantTypes = 5
# At which level a spell has to be known before a proc enchantment is allowed:
ENCHANT_MinSpellLevelReq = 3
# How many times normal amount of components are needed for the spell proc enchantment
ENCHANT_SpellComponentMod = 3
# list of raw materials
ENCHANT_RawItems = ["Sandstone","Coal","Icy Shard","Bark","Limestone","Quartz","Blighted Shard","Vine","Muck-Covered Stone"]
# list of quality prefixes, 'raw' is not yet enchanted item (Coal, Sandstone, ...), raw can't be dropped, only gained from disenchanting so this prefix won't be used normally and is just here for completion/easier list use
ENCHANT_QualityPrefix = ["Raw","Fractured","Rough","Jagged","Smooth","Clear","Pristine","Exquisite"]
# list of skill required to use or produce an enchanting item with the prefix from above
# rough is still for level 1 since merging ENCHANT_MergeCount fractured foci is the lowest enchantment possible
ENCHANT_QualitySkillReq = [1,1,1,60,120,180,240,300]
# all the quality lists share the same length:
ENCHANT_QualityCount = len(ENCHANT_QualityPrefix)
# list of attributes that raw materials can be enchanted with, their corresponding item attrib strings and difficulty
ENCHANT_RawAttribsLUT = {
"HEALTH":["Health",50],
"MANA":["Ether",50],"ETHER":["Ether",50],
"STAMINA":["Endurance",50],"ENDURANCE":["Endurance",50],
"STRENGTH":["Strength",200],
"BODY":["Constitution",200],"CONSTITUTION":["Constitution",200],
"REFLEX":["Instinct",200],"INSTINCT":["Instinct",200],
"AGILITY":["Nimbleness",200],"NIMBLENESS":["Nimbleness",200],
"DEXTERITY":["Quickness",200],"QUICKNESS":["Quickness",200],
"MIND":["Insight",200],"INSIGHT":["Insight",200],
"WISDOM":["Clarity",200],"CLARITY":["Clarity",200],
"MYSTICISM":["the Arcane",200],"THE ARCANE":["the Arcane",200]
}
# lookuptable of possible focus's per slot, overall max possible value and needed skill (as to suffer no penalty)
# 'all' = applicable to all crafted items whatever the slot
# everything up to and with the 'of' in focus names will be cut before tests
# Max values get scaled with a funcion of second order depending on item level. So absolute max is really hard to achieve with insufficient skill, with insufficient item level even impossible.
# An exquisite focus can only provide 1/10 of this max value, foci of lesser quality even less.
# not all stats can be active at the same time (max ENCHANT_MaxEnchantTypes different types)
# WARNING: to safe another variable, all maxvalues >10 indicate a stat of type int, max values <=10 indicate no conversion from float
ENCHANT_SlotLUT = {
'all':{"Strength":['str',400,300],"Constitution":['bdy',400,300],"Instinct":['ref',400,300],"Nimbleness":['agi',400,300],"Quickness":['dex',400,300],"Insight":['mnd',400,300],"Clarity":['wis',400,300],"the Arcane":['mys',400,300]},
RPG_SLOT_HEAD:{"Health":["maxHealth",800,1],"Ether":["maxMana",4000,1],"Defense":['armor',300,100],"Physical Protection":["resistPhysical",60,500],"Magic Protection":["resistMagical",60,500],"Aelieas":["regenMana",50,800]},
RPG_SLOT_BACK:{"Ether":["maxMana",2400,1],"Defense":['armor',200,100],"Magic Protection":["resistMagical",80,500],"the Sphinx":["castHaste",.15,800]},
RPG_SLOT_CHEST:{"Health":["maxHealth",4000,1],"Endurance":["maxStamina",1500,1],"Defense":['armor',600,100],"Physical Protection":["resistPhysical",80,500],"Fiery Protection":["resistFire",80,500],"Cold Protection":["resistCold",80,500],"Acidity":["resistAcid",80,500],"Electrical Resistance":["resistElectrical",80,500],"the Dwarven King":["regenHealth",30,800]},
RPG_SLOT_ARMS:{"Health":["maxHealth",600,1],"Defense":['armor',300,100],"Fiery Protection":["resistFire",30,500],"Cold Protection":["resistCold",30,500],"Lightning":['castDmgMod',0.5,900]},
RPG_SLOT_HANDS:{"Health":["maxHealth",600,1],"Ether":["maxMana",900,1],"Defense":['armor',200,100],"Fiery Protection":["resistFire",30,500],"Cold Protection":["resistCold",30,500],"Acidity":["resistAcid",30,500],"Electrical Resistance":["resistElectrical",30,500],"the Warling Cleric":['castHealMod',0.5,700],"the Sphinx":["castHaste",.4,800]},
# undead bane enchantment is handled as a special case, if further races are wanted, search for 'undead' and modify accordingly in code, it's easier to test for undead than to evaluate which bane should be applied if multiple are chosen.
RPG_SLOT_PRIMARY:{"the Ghoul Slayer":["Undead Bane",10,400]},  # also different spell procs
RPG_SLOT_SECONDARY:{"the Ghoul Slayer":["Undead Bane",10,400]},  # also different spell procs
RPG_SLOT_RANGED:{"the Ghoul Slayer":["Undead Bane",10,400]},  # also different spell procs
RPG_SLOT_WAIST:{"Health":["maxHealth",600,1],"Defense":['armor',100,100],"Poison Resist":["resistPoison",80,500],"Disease Resist":["resistDisease",80,500],"Volsh":["haste",1.25,800]},
RPG_SLOT_LEGS:{"Health":["maxHealth",800,1],"Endurance":["maxStamina",1200,1],"Defense":['armor',400,100],"Physical Protection":["resistPhysical",60,500],"the Dwarven King":["regenHealth",20,800],"the Cavebear":["regenStamina",20,800]},
RPG_SLOT_FEET:{"Health":["maxHealth",600,1],"Endurance":["maxStamina",3000,1],"Defense":['armor',300,100],"Poison Resist":["resistPoison",75,500],"Disease Resist":["resistDisease",75,500],"Acidity":["resistAcid",50,500],"Electrical Resistance":["resistElectrical",50,500],"the Cavebear":["regenStamina",35,800],"Speed":["move",2.0,800]},
RPG_SLOT_SHIELD:{"Defense":['armor',800,100],"Physical Protection":["resistPhysical",120,500],"Magic Protection":["resistMagical",120,500],"Fiery Protection":["resistFire",120,500],"Cold Protection":["resistCold",120,500],"Poison Resist":["resistPoison",120,500],"Disease Resist":["resistDisease",120,500],"Acidity":["resistAcid",120,500],"Electrical Resistance":["resistElectrical",120,500]},
RPG_SLOT_SHOULDERS:{"Defense":['armor',500,100],"Physical Protection":["resistPhysical",80,500]},
RPG_SLOT_LEAR:{},
RPG_SLOT_REAR:{},
RPG_SLOT_NECK:{"Magic Protection":["resistMagical",110,500],"Fiery Protection":["resistFire",90,500],"Cold Protection":["resistCold",90,500],"Poison Resist":["resistPoison",80,500],"Disease Resist":["resistDisease",80,500],"Acidity":["resistAcid",80,500],"Electrical Resistance":["resistElectrical",110,500]},
RPG_SLOT_LFINGER:{},
RPG_SLOT_RFINGER:{},
RPG_SLOT_LWRIST:{},
RPG_SLOT_RWRIST:{}
}

def FocusGenSpecific(focusname):
    try:
        focusQuality,focusType = focusname.split(' ',1)
        focusQuality = focusQuality.capitalize()
        if not focusQuality in ENCHANT_QualityPrefix:
            return None
        if focusQuality == 'Raw':    # better use directly ItemProto.byName without the raw prefix
            return None
        con = ItemProto._connection.getConnection()
        protoID,name = con.execute("SELECT id,name FROM item_proto WHERE lower(name)=lower(\"%s\") LIMIT 1;"%focusType).fetchone()
        enchFocus = ItemProto.get(protoID)
        focus = enchFocus.createInstance()
        # spellEnhanceLevel is used for quality of this item type (less attribs),
        #  values < 10 are used to identify tomes, so use values 10 - 17
        focus.spellEnhanceLevel = ENCHANT_QualityPrefix.index(focusQuality) + 10
        # Map to str since torque has problems handling unicode.
        focus.name = str("%s %s"%(focusQuality,name))
        focus.slot = -1
        return focus
    except:
        return None



# This function gets invoked when the user uses a '/Enchant ...' command in the console.
# No attributes to this function tries to enchant the crafted item in the crafting window with the foci also therein or if no crafted item is available tries to merge the foci in the crafting window. Else the attribute specifies the desired enchantment upon a raw material or proc on a weapon.
# Only stat - related enchantments can be put on a raw material (str,bdy,ref,agi,dex,mnd,wis,mys,health,mana,stamina), specials stay rare. Before such an added enchantment, these raw materials are of no use for item enchantments. Command used to enchant a raw material is "/enchant focus of ...". Costs for this function are really high. The player looses either stat points, health, mana, stamina and again some mana. Random foci drops are made specially rare so that the player uses this function in conjunction with disenchanting more often. Enchanting as it is is designed for players with high expectations. Other players will have to wait for socketing. This can be made much easier and less costly but should also generate items of lesser value than enchanting. The stat decrease is handled like stat potions, that means they use the same cap. Virtually you could put a stat potion in the crafting window for the enchantment.
# A weapon can be enchanted to proc a specified spell, enchanter has to know this spell for at least ENCHANT_MinSpellLevelReq levels before being able to attempt this and only harmful spells are allowed - no stun, sleep, fear or charms.
def EnchantCmd(mob,enchName):
    # init vars
    player = mob.player
    char = mob.character
    # List of all items that aid in enchanting, sorted by level
    enchFoci = [[] for i in xrange(ENCHANT_QualityCount)]
    # List of all enchantable items in crafting window (should be only one!)
    enchTarget = []
    # Holds all empty slots in crafting window
    emptySlots = range(RPG_SLOT_CRAFTING_BEGIN,RPG_SLOT_CRAFTING_END)
    # If enchanted is true we merged or enchanted something
    enchanted = False
    # Enchanting eventually uses health, this variable holds the costs
    healthCost = 0
    # All enchanting uses mana, this variable holds the costs
    manaCost = 0
    # Enchanting eventually uses stamina, this variable holds the costs
    staminaCost = 0
    # Enchanting eventually drains a stat, this variable holds the costs
    statCost = []
    slevel = mob.skillLevels.get(ENCHANT_skillname,0)
    if not slevel:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't know how to enchant anything.\\n"%char.name)
        return
    if ENCHANT_skillname in mob.skillReuse:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is still recovering from a previous enchant, and can enchant again in about %i seconds.\\n"%(char.name, mob.skillReuse[ENCHANT_skillname]))
        return
    mskill = mob.mobSkillProfiles[ENCHANT_skillname]
    mob.skillReuse[ENCHANT_skillname] = mskill.reuseTime
    # 'required' skill, for skillup check purposes
    skillReq = 0
    # With 1000 skill, only half costs for enchanting anything
    costMod = 1 - 5e-4 * slevel
    costModSQ = costMod * costMod
    
    # Don't allow enchanting while doing anything else
    if mob.attacking or mob.charmEffect or mob.isFeared or (mob.sleep > 0) or (mob.stun > 0) or mob.casting:
        player.sendGameText(RPG_MSG_GAME_DENIED,r'$src\'s enchanting failed, $srche is in no condition to enchant anything!\n',mob)
        return
    mob.cancelInvisibility()
    mob.cancelFlying()
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
    
    
    # Get a list of all items in the crafting inventory, sort them accordingly
    # If true we found at least one enchanting focus
    foundFocus = False
    for item in char.items:
        if RPG_SLOT_CRAFTING_END > item.slot >= RPG_SLOT_CRAFTING_BEGIN:
            emptySlots.remove(item.slot)
            if item.crafted:
                for islot in item.itemProto.slots:
                    if islot in ENCHANT_SlotLUT:
                        enchTarget.append(item)
                        break
            # Only foci should have this skill attached
            elif item.skill == ENCHANT_skillname:
                spellEnhanceLevel = item.spellEnhanceLevel
                # raw foci may have a spellEnhanceLevel of 0 because spellEnhanceLevel is item wise and not itemProto, so can only be set dynamically
                if spellEnhanceLevel:
                    spellEnhanceLevel -= 10
                (enchFoci[spellEnhanceLevel]).append(item)
                foundFocus = True
    
    
    # no focusing item found, nothing to enchant here
    if not foundFocus:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s can't focus on anything to enchant.\\n"%char.name)
        return
    
    
    # check if an attribute has been specified
    if len(enchName):
        firstWord = enchName.split(' ',1)[0]
        
        # raw focus enchantment
        if firstWord == 'FOCUS':
            if not len(enchFoci[0]):
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have a raw focus to enchant.\\n"%char.name)
                return
            
            skillReq = 1000
            enchNameAttrib = enchName.split(' OF ',1)[-1]
            try:
                skillReq = ENCHANT_RawAttribsLUT[enchNameAttrib][1]
                enchNameAttrib = ENCHANT_RawAttribsLUT[enchNameAttrib][0]
            except:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s can't enchant a focus with this attribute.\\n"%char.name)
                return
            
            # pick first available focus
            enchTarget = None
            # no more room in crafting inventory, try to find a raw focus with stackcount <=1
            if not len(emptySlots):
                for foc in enchFoci[0]:
                    if foc.stackCount <= 1:
                        enchTarget = foc
                        break
                if not enchTarget:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no more room in the crafting inventory.\\n"%char.name)
                    return
            else:
                enchTarget = enchFoci[0][0]
            
            basicCost = skillReq * costModSQ
            if enchNameAttrib == "Health":
                healthCost = int(basicCost * 4)
                manaCost = int(basicCost) << 1
            elif enchNameAttrib == "Ether":
                manaCost = int(basicCost * 6)
            elif enchNameAttrib == "Endurance":
                staminaCost = int(basicCost * 4)
                manaCost = int(basicCost) << 1
            else:
                manaCost = int(basicCost * 8)
                statCost.append(ENCHANT_SlotLUT['all'][enchNameAttrib][0])
                statCost.append(statCost[0]+"Base")
                statCost.append(statCost[0]+"Raise")
                statCost.append(-1)
                statCost.append(getattr(char,statCost[2]))
                # 300 as defined as default in character.py, we don't want this to get any higher
                if statCost[-1] >= 300:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"%s isn't powerful enough for this enchantment.\\n"%char.name)
                    return
            # Make sure player can't die from enchantment
            if mob.health < healthCost + 1:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough health to power the focus.\\n"%char.name)
                return
            if mob.mana < manaCost:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough mana to power the focus.\\n"%char.name)
                return
            if mob.mana < staminaCost:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough stamina to power the focus.\\n"%char.name)
                return
            
            # check for critical failure, no stat drain if not successful.
            # only crit if enchanter hasn't enough skill, min 10% chance for success.
            if slevel < skillReq and randint(0,int((1.0 - float(slevel)/float(skillReq)) * 10.0)):
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s failed the focus enchantment.\\n"%char.name)
                # linearly decrease drain with higher skill level
                buffMod = 2.0 - float(slevel) / 1000.0
                mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Enchanting - Mana drain"),buffMod,0,'Mana Drain'))
                mob.mana -= manaCost
                mob.stamina -= staminaCost
                mob.health -= healthCost
                # Don't let player die because of enchanting failure
                if mob.health < 1:
                    mob.health = 1
                return
            
            # generate new focus
            newFocus = enchTarget.itemProto.createInstance()
            # can create up to Exquisite (only with highest skill level)
            newFocus.spellEnhanceLevel = int(1 + slevel / 166)
            newFocus.name = "%s %s of %s"%(ENCHANT_QualityPrefix[newFocus.spellEnhanceLevel],enchTarget.name,enchNameAttrib)
            # Foci use spellEnhanceLevel 10 - 17; < 10 is used for tomes
            newFocus.spellEnhanceLevel += 10
            newFocus.descOverride = "This %s gleams with a magical hue. It may be used to enchant items."%enchTarget.name
            if enchTarget.stackCount <= 1:
                newFocus.slot = enchTarget.slot
                player.takeItem(enchTarget)
            else:
                newFocus.slot = emptySlots.pop()
                enchTarget.stackCount -= 1
                enchTarget.itemInfo.refreshDict({'STACKCOUNT':enchTarget.stackCount})
            newFocus.setCharacter(char)
            
            player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully enchanted a raw focus with mystic power.\\n"%char.name)
            enchanted = True
        
        
        # Weapon proc enchantment, procs are only temporary, duration depending on skill and luck.
        # Only harmful spells can be applied to a weapon - no stun, sleep, fear or charm; and only if the caster knows this spell at least at level ENCHANT_MinSpellLevelReq.
        # To prevent these procs from getting overpowered, the costs for an actual enchantment are pretty high (at least 10* normal spell mana costs added again the item level *50). A spell also needs at least an item of spell level / 0.9 to be allowed. High-end nukes are automagically taken out like this. As a further restriction, the proc only lasts for about one fight, if at all and there's a high chance for failure.
        # One application may be that several players can bestow their power upon a single weapon, shortly before the tank in their group tries to finish off the dangerous mob in a quick strike. Some new kind of preparing for battle.
        else:
            # none or too much enchantment targets in crafting window
            if not len(enchTarget) == 1:
                player.sendGameText(RPG_MSG_GAME_DENIED,"You need to put one single crafted item into the crafting window.\\n")
                return
            # Else just get this single target
            enchTarget = enchTarget[0]
            enchProto = enchTarget.itemProto
            
            # only weapons can be enchanted with a proc, that means bows and melee weapons
            # exclude arrows because of possible stack with bow procs
            if not enchProto.wpnDamage or enchProto.projectile:
                player.sendGameText(RPG_MSG_GAME_DENIED,"Only melee weapons or bows can be enchanted with a proc.\\n")
                return
            
            # don't allow more than RPG_ITEMPROC_MAX simultaneous procs, included any poisons
            if len(enchTarget.procs) >= RPG_ITEMPROC_MAX:
                player.sendGameText(RPG_MSG_GAME_DENIED,"This weapon can't hold any more power enchantments.\\n")
                return
            
            enchSpell = None
            cspell = None
            
            # Try to get specified spell.
            for knownSpell in char.spells:
                
                # Check spell proto for a matching name.
                knownSpellProto = knownSpell.spellProto
                if knownSpellProto.name.upper() == enchName:
                    
                    # Check if the mob can cast the spell.
                    if knownSpellProto.qualify(mob):
                        enchSpell = knownSpell
                        cspell = knownSpellProto
                        
                    # The spell was found, so break out of loop.
                    break

            if not enchSpell:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot cast this spell.\\n"%char.name)
                return
            if not cspell.spellType&RPG_SPELL_HARMFUL:
                player.sendGameText(RPG_MSG_GAME_DENIED,"Weapons can only be enchanted with harmful spells.\\n")
                return
            if not enchSpell.level >= ENCHANT_MinSpellLevelReq:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't know this spell enough to enchant a weapon with it.\\n"%char.name)
                return
            # check if this spell contains stunning, 'sleeping', fearing or charming - don't allow them
            charms = False
            for eff in cspell.effectProtos:
                if eff.flags&RPG_EFFECT_CHARM:
                    charms = True
                    break
            if charms or cspell.affectsStat("stun") or cspell.affectsStat("sleep") or cspell.affectsStat("fear"):
                player.sendGameText(RPG_MSG_GAME_DENIED,"Stun, sleep, fear and charm spells aren't allowed for weapon enchantments.\\n")
                return
            if mob.recastTimers.has_key(cspell):
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s has to wait another %i seconds before attempting to cast this spell again.\\n"%(char.name,int(mob.recastTimers[cspell]/6)))
                return
            
            # costs depending on spell mana cost and item level
            # manaCosts scale only linearly here
            manaCost = int((cspell.manaCost + enchTarget.level * 5) * 10 * costMod)
            staminaCost = int(0.2 * mob.maxStamina * costModSQ)
            if mob.mana < manaCost:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough mana to enchant this item.\\n"%char.name)
                return
            if mob.stamina < staminaCost:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough stamina to enchant this item.\\n"%char.name)
                return
            
            components = defaultdict(int)
            # check for component costs
            if len(cspell.components):
                # Gather a dictionary of the required spell components
                #  with their counts.
                for c in cspell.components:
                    if c.count > 0:
                        components[c.itemProto] += int(c.count * ENCHANT_SpellComponentMod)
                
                # Check if the player has the required components and give
                #  feedback if not.
                if not player.checkItems(components.copy(),True):
                    player.sendGameText(RPG_MSG_GAME_DENIED,"$src lacks the spell components for this enchantment,\\n$srche needs: %s\\n"%', '.join('<a:Item%s>%i %s</a>'%(GetTWikiName(ip.name),c,ip.name) for ip,c in components.iteritems()),mob)
                    return
            
            # from now on, count the spell as casted
            if cspell.recastTime:
                mob.recastTimers[cspell] = cspell.recastTime
            
            # check if item is allowed to hold that kind of spell power
            # only drain half mana and stamina and don't charge spell ingredients on failure
            if enchTarget.itemProto.level * 0.9 < cspell.level:
                player.sendGameText(RPG_MSG_GAME_DENIED,"The %s can't hold this amount of power and it just seeps out again.\\n"%enchTarget.name)
                mob.mana -= manaCost >> 1
                mob.stamina -= staminaCost >> 1
                return
            
            # If we get here, the components will get used.
            if len(components):
                player.takeItems(components)
            
            # Calculate difficulty for enchantment.
            # Start out with the item level, an item is harder to enchant the nearer it
            #  is to the requirement posed by the spell enchanted upon the item.
            # Result should be in a range from about 1 to 50; max cspell.level that can be used is 90.
            skillReq = float(cspell.level) / float(enchTarget.level) * 54.0 + 1.0
            # Apply spell level, higher level means higher difficulty, quadratic function.
            # Need a range of about 1 to 20, multiply with value from before.
            reqMod = float(cspell.level) / 90.0 * 4.4
            skillReq *= reqMod * reqMod + 1.0
            # Apply item repair value, lower repair value relative to max means higher difficulty.
            if enchTarget.repairMax > 0:
                if enchTarget.repair > 0:
                    skillReq *= float(enchTarget.repairMax) / float(enchTarget.repair)
                # The item is shattered, make it pretty much impossible to succeed.
                else:
                    skillReq = 9999999
            skillReq = int(skillReq)
            
            # Check for critical failure, on failure, no enchantment and no skillup but mana drain.
            # Also hurt enchanter (never kill) and damage weapon that should have been enchanted.
            # Get a random success value based on difficulty. This value then gets directly compared
            #  against the skill level. Even with max skill, there's always still a chance for failure.
            # With a fully repaired enchanting target, the failure rate with max skill level
            #  should never exceed 2:7.
            success = randint(0,skillReq * 7 / 5)
            if success > slevel:
                mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Enchanting failure")))
                player.sendGameText(RPG_MSG_GAME_LOST,"The enchantment was too unstable and vanishes in an explosion!\\n")
                mob.mana -= manaCost
                mob.stamina -= staminaCost
                mob.health -= int(mob.maxHealth * 0.1)
                # Don't let player die because of enchanting failure
                if mob.health < 1:
                    mob.health = 1
                if enchTarget.repairMax and enchTarget.repair:
                    enchTarget.repair -= randint(1,25)
                    if enchTarget.repair < 0:
                        enchTarget.repair = 0
                    repairRatio = float(enchTarget.repair)/float(enchTarget.repairMax)
                    if not repairRatio:
                        player.sendGameText(RPG_MSG_GAME_RED,"%s's %s has shattered in the explosion! (%i/%i)\\n"%(char.name,enchTarget.name,enchTarget.repair,enchTarget.repairMax))
                        mob.playSound("sfx/Shatter_IceBlock1.ogg")
                    elif repairRatio < .2:
                        player.sendGameText(RPG_MSG_GAME_YELLOW,"%s's %s got severely damaged by the explosion! (%i/%i)\\n"%(char.name,enchTarget.name,enchTarget.repair,enchTarget.repairMax))
                        mob.playSound("sfx/Menu_Horror24.ogg")
                
                enchTarget.itemInfo.refresh()
                return
            
            # Cap difficulty to 1000 for skillup check purposes.
            skillReq = min(skillReq,1000)
            
            # Apply proc like a poison, effective only for a certain amount of hits.
            # Duration depends on skill level by 2 - 10; there's also an additional
            #  "luck"-modifier of -3 to 2; yields a nonlinear range of 1-12 (caps at 1).
            duration = int(round(0.008*slevel+2)) - randint(-3,2)
            if duration < 1:
                duration = 1
            # Frequency depends on level by 10 - 2 and on an additional "luck"-modifier of -1 to +5;
            #  this yields a nonlinear range of 15 - 2 (caps at 2).
            # Higher frequency = less often, so more like an inverse frequency.
            frequency = int(round(10-0.008*slevel)) + randint(-1,5)
            if frequency < 2:
                frequency = 2
            newProc = ItemSpellTemp(cspell,RPG_ITEM_TRIGGER_POISON,frequency)
            enchTarget.procs[newProc] = [duration,RPG_ITEMPROC_ENCHANTMENT]
            enchTarget.itemInfo.refresh()
            
            player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully enchanted the %s with %s.\\n"%(char.name,enchTarget.name,cspell.name))
            enchanted = True
    
    
    # check if we got an enchanting target. If so, apply enchantment
    elif len(enchTarget):
        # too many crafted items that could be enchanted currently in crafting window
        if len(enchTarget) > 1:
            player.sendGameText(RPG_MSG_GAME_DENIED,"It's too stressful to enchant multiple items at once.\\n")
            return
        
        # Else just get this single item
        enchTarget = enchTarget[0]
        # Get the basic item
        basicProto = enchTarget.itemProto
        
        # The difficulty of the enchantment, 1.0 = succeeds always,
        #  used for failure mods
        primarySuccessMod = 1.0
        # List of desired enchantments along with previous values and assigned foci,
        #  internally like: {<statname>:[<value>,[<list of assigned foci>]]}
        desiredEnchantments = {}
        # DesiredEnchantments holds foci which are just wasted with the key 0;
        #  value is here number of foci
        desiredEnchantments[0] = [0,[]]
        # Check if the enchanter has basic ability to enchant this item. If not, decrease primary success mod.
        # From 500 skill on, there will be no penalty for enchanting an item of any level.
        skillReq = basicProto.level * 5
        modif = float(slevel) / float(skillReq)
        if modif < 1:
            primarySuccessMod *= modif
        
        # calculate modifier for max possible stat as a function of second order, depending on item level
        # /100 to scale by max item level, +0.005 to set base value for x = 1,
        #  0.995* to scale once more so level 100 gets us max value
        rel = basicProto.level / 100.0
        enchStatMod = 0.005 + 0.995 * rel * rel
        
        # concatenate the focus lists for further use, raw items can't be focused on so drop them
        enchFoci = reduce(list.__add__,enchFoci[1:])
        
        # get all active enchantments on this item
        try:
            for var in enchTarget.variants[V_STAT]:
                try:  # shouldn't happen normally, but you never know
                    desiredEnchantments[var[0]][0] += var[1]
                except KeyError:
                    desiredEnchantments[var[0]] = [var[1],[]]
        except KeyError:
            pass
        try:
            baneRace,baneMod = enchTarget.variants[V_BANEWEAPON]
            # Item variants bane only stores the race and mod.  Enchanting
            # system uses a format of "<race> Bane".  Thus, take the baneRace
            # and create a key useable by the enchanting system.
            desiredEnchantments[baneRace + " Bane"] = [baneMod,[]]
        except KeyError:
            pass
        
        
        # run through all foci, sorting them and calculating difficulty mods, manaCost and perform different checks
        foundFocus = False
        clampedStats = []
        for foc in enchFoci:
            # Check if this focus can actually be applied to the base item typewise
            # Strip everything up to and with the of
            enchAttrName = foc.name.split(' of ',1)[-1]
            focusType = None
            try:
                focusType = ENCHANT_SlotLUT['all'][enchAttrName]
            except:
                try:
                    focusType = ENCHANT_SlotLUT[basicProto.slots[0]][enchAttrName]
                except:  # this focus can't be used with this item
                    continue
            foundFocus = True
            focusSuccessMod = primarySuccessMod
            # 0 is in meaning equal to 1, but 1 is easier for calculating stuff further down
            if not foc.stackCount:
                foc.stackCount = 1
            # apply focus specific difficulty
            skillReq += int(focusType[2] / 10.0 * float(foc.stackCount))
            modif = float(slevel) / focusType[2]
            if modif < 1:
                focusSuccessMod *= modif
            
            # check if enchanter has enough skill to use this focus quality. If not, decrease focus success mod
            # double the skill is needed to successfully (100%) apply a focus to an item than merging two lower focus's to this one
            spellEnhanceLevel = foc.spellEnhanceLevel - 10
            modif = 0.5 * slevel / float(ENCHANT_QualitySkillReq[spellEnhanceLevel])
            skillReq += int(float(ENCHANT_QualitySkillReq[spellEnhanceLevel]) / 10.0 * float(foc.stackCount))
            if modif < 1:
                focusSuccessMod *= modif
            
            # get stat enchantment value, depending on focus quality, max stat enchantment of that kind and focusSuccessMod
            # values result in 1/40 to 1/10 of what can be maximally achieved, of course nonlinear
            focusEnchantValue = 0.2 * focusType[1] / float(9 - spellEnhanceLevel)
            if focusSuccessMod < 0.01:
                focusSuccessMod = 0.01
            # modify enchantment value by successmod. Successmod = 1 yields 0.8 to 1.2 times standard value, the lower the successmod, the broader the distribution. Max value is always 1.2 but min value goes down to -1.2 (this is per focus)
            # instead of going through a loop for every single focus, directly modify the calculation with the stack count
            focusEnchantValue *= (randint(40*foc.stackCount,60*foc.stackCount) - randint(0,foc.stackCount*int(round(1/focusSuccessMod - 1)))) / 50.0
            
            
            # check if this enchantment is allowed relative to max enchantments, store focus accordingly
            if desiredEnchantments.has_key(focusType[0]):
                # It's more difficult to modify an already existing enchantment than to create a new one, because the existing forces have to be altered
                manaCost += 2*focusType[2]*foc.stackCount
                desiredEnchantments[focusType[0]][0] += focusEnchantValue
                desiredEnchantments[focusType[0]][1].append(foc)
                # clamp to max value, also power wasted drains additionally on mana
                focMaxValue = enchStatMod*focusType[1]
                if desiredEnchantments[focusType[0]][0] > focMaxValue:
                    manaCost += int(200 * (desiredEnchantments[focusType[0]][0]/focMaxValue - 1.0))
                    desiredEnchantments[focusType[0]][0] = focMaxValue
                    clampedStats.append(foc.name)
                # all max values <= 10 indicate a float type for stat value as per definition of the ENCHANT_SlotLUT
                if focusType[1] >= 10:
                    desiredEnchantments[focusType[0]][0] = int(ceil(desiredEnchantments[focusType[0]][0]))
            # 0 item is always present, but doesn't count
            elif len(desiredEnchantments) <= ENCHANT_MaxEnchantTypes:
                manaCost += focusType[2]*foc.stackCount
                desiredEnchantments[focusType[0]] = [focusEnchantValue,[foc]]
                # clamp to max value, also power wasted drains additionally on mana
                focMaxValue = enchStatMod*focusType[1]
                if desiredEnchantments[focusType[0]][0] > focMaxValue:
                    manaCost += int(100 * (desiredEnchantments[focusType[0]][0]/focMaxValue - 1.0))
                    desiredEnchantments[focusType[0]][0] = focMaxValue
                    clampedStats.append(foc.name)
                # all max values <= 10 indicate a float type for stat value as per definition of the ENCHANT_SlotLUT
                if focusType[1] >= 10:
                    desiredEnchantments[focusType[0]][0] = int(ceil(desiredEnchantments[focusType[0]][0]))
            # Else this focus just gets wasted, big number of wasted foci will
            #  further increase primary successmod.
            else:
                # Trying to enchant an item with energy it can't hold uses up more
                #  mana than normal. It's a more realistic warning to the player
                #  when he can't afford the enchantment.
                manaCost += 3 * focusType[2] * foc.stackCount
                desiredEnchantments[0][1].append(foc)
                desiredEnchantments[0][0] += foc.stackCount
        # apply cost mod on mana costs
        manaCost = int(manaCost * costMod)
        
        
        # check if we still have some applicable foci left and if player can afford the enchantment manawise
        if not foundFocus:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't know how to use these foci in conjuction with the %s.\\n"%(char.name,enchTarget.name))
            return
        if mob.mana < manaCost:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough mana for this enchantment.\\n"%char.name)
            return
        
        # modify primary successmod by the number of foci, the player tries to force enchant. Two are allowed without penalty
        if desiredEnchantments[0][0]:
            modif = 2.0 / desiredEnchantments[0][0]
            if modif < 1.0:
                primarySuccessMod *= modif
        
        # check for critical failure (item gets destroyed, along with all focus ingredients)
        # if this test gets passed, the item will be enchanted, for good or worse
        if primarySuccessMod < 1:
            if not randint(0,int(primarySuccessMod*10)):
                mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Enchanting failure")))
                player.takeItem(enchTarget)
                for foc in enchFoci:
                    player.takeItem(foc)
                mob.mana -= manaCost
                mob.health -= int(mob.maxHealth * 0.4)
                # Don't let player die because of enchanting failure
                if mob.health < 1:
                    mob.health = 1
                player.sendGameText(RPG_MSG_GAME_LOST,"%s accidentally turned this enchantment into a puff of smoke.\\n"%char.name)
                return
        
        # cap skill weight
        if skillReq > 1000:
            skillReq = 1000
        
        
        # generate enchanted item
        enchTarget.levelOverride = basicProto.level
        enchTarget.clearVariants()
        if desiredEnchantments[0][0]:
            player.sendGameText(RPG_MSG_GAME_LOST,"The %s can't hold all of that power and some of it just seeps out again.\\n"%enchTarget.name)
        expungeList = desiredEnchantments.pop(0)
        expungeList = expungeList[1]
        map(player.takeItem, expungeList)
        for attr in desiredEnchantments:
            enchValue = desiredEnchantments[attr][0]
            map(player.takeItem, desiredEnchantments[attr][1])
            if not enchValue:
                continue
            enchanted = True
            AddStatVariant(enchTarget,attr,enchValue)
            # Increase item level by 2 for every added stat
            enchTarget.levelOverride += 2
        if enchanted:
            enchTarget.name = "Enchanted " + basicProto.name
            if enchTarget.levelOverride > 100:
                enchTarget.levelOverride = 100
            enchTarget.descOverride = enchTarget.descOverride.split('\\nEnchanted by')[0] + "\\nEnchanted by %s"%char.name
            enchTarget.hasVariants = True
            # Flag as enchanted, hack
            enchTarget.spellEnhanceLevel = 9999
        else:
            # Strip eventual "Enchanted by".
            enchTarget.descOverride = enchTarget.descOverride.split('\\nEnchanted by')[0]
            enchTarget.hasVariants = False
            # Hack, flag as not enchanted
            enchTarget.spellEnhanceLevel = 0
            # Reset quality, worth and enchanted flag, leave artifact flag if present.
            enchTarget.flags = enchTarget.flags & ~RPG_ITEM_ENCHANTED
            enchTarget.quality = RPG_QUALITY_NORMAL
            enchTarget.worthIncreaseTin = 0
        enchTarget.crafted = True
        enchTarget.refreshFromProto()
        enchanted = True
        
        # Inform enchanter that some stats have reached the items max value.
        numClampedStats = len(clampedStats)
        if numClampedStats:
            if 1 == numClampedStats:
                player.sendGameText(RPG_MSG_GAME_LOST,"The %s become stable as some of %s's energy escapes.\\n"%(enchTarget.name, clampedStats[0]))
            elif 2 == numClampedStats:
                player.sendGameText(RPG_MSG_GAME_LOST,"The %s become stable as some of %s and %s's energy escapes.\\n"%(enchTarget.name, clampedStats[0] ,clampedStats[1]))                
            else:
                player.sendGameText(RPG_MSG_GAME_LOST,"The %s become stable as some of %s, and %s's energy escapes.\\n"%(enchTarget.name, ', '.join(clampedStats[:-1]) , clampedStats[-1]))
    
    
    # try to merge foci (only one appliance even if there are more possibilities)
    else:
        # Ignore raw and exquisite items, since they can't be merged.
        # qualityIndex actually stores the index of the higher focus.
        for qualityIndex,partialFociList in zip(range(2,ENCHANT_QualityCount),enchFoci[1:-1]):
            # no focus at this level, skip
            if not len(partialFociList):
                continue
            
            # Check for skill level and mana.
            # Merging foci is a more "traditional" process, player needs exact skill to merge.
            skillReq = ENCHANT_QualitySkillReq[qualityIndex]
            if slevel < skillReq:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't know how to merge these items yet.\\n"%char.name)
                return
            # Merging uses up to 3000 mana for highest merge
            manaCost = int(skillReq * 10 * costModSQ)
            if mob.mana < manaCost:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough mana to merge these items.\\n"%char.name)
                return
            
            # look for something to merge
            # first, get a list of all entries with the same name on this level
            focusName = partialFociList[0].name
            focusCount = partialFociList[0].stackCount
            # stackCount = 0 is the same as = 1, but 1 is easier for calculation and tests
            if not focusCount:
                focusCount = 1
            for counter in xrange(1,len(partialFociList)):
                foc = partialFociList[counter]
                if foc.name == focusName:
                    if not foc.stackCount:
                        focusCount += 1
                    else:
                        focusCount += foc.stackCount
                else:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"Only foci of the same kind can be merged.\\n")
                    return
            
            # not enough of this focus type
            if focusCount < ENCHANT_MergeCount:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s hasn't enough %s to merge.\\n"%(char.name,focusName))
                return
            
            # check if we have enough place in the crafting inventory to store the new focus
            if not len(emptySlots):
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no more room in the crafting inventory.\\n"%char.name)
                return
            
            # Else try to merge:
            # Away with the quality prefix
            focusNameStripped = focusName.split(' ',1)[-1]
            focusShort = focusNameStripped.split(' of ',1)[0]
            newFocusKind = ItemProto.byName(focusShort)
            newFocus = newFocusKind.createInstance()
            newFocus.name = ENCHANT_QualityPrefix[qualityIndex] + " " + focusNameStripped
            newFocus.descOverride = "This %s gleams with a magical hue. It may be used to enchant items."%focusShort
            # Focus spellEnhanceLevel range is 10-17 (and 0) because of tomes
            newFocus.spellEnhanceLevel = qualityIndex + 10
            newFocus.slot = emptySlots.pop()
            newFocus.setCharacter(char)
            # remove correct amount of lesser foci
            remainingKills = ENCHANT_MergeCount
            for eraseFoc in partialFociList:
                eraseCount = eraseFoc.stackCount
                if not eraseCount:
                    eraseCount = 1
                if eraseCount <= remainingKills:
                    player.takeItem(eraseFoc)
                    remainingKills -= eraseCount
                else:
                    eraseFoc.stackCount -= remainingKills
                    eraseFoc.itemInfo.refreshDict({'STACKCOUNT':eraseFoc.stackCount})
                    break
                if not remainingKills:
                    break
            
            enchanted = True
            player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully merged %i foci.\\n"%(char.name,ENCHANT_MergeCount))
            break
    
    
    if not enchanted:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s wasn't able to do anything with these items.\\n"%char.name)
        return
    
    
    else:
        mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Dis - Enchanting")))
        mob.health -= healthCost
        mob.mana -= manaCost
        mob.stamina -= staminaCost
        if len(statCost):
            setattr(char,statCost[2],int(statCost[4]-statCost[3]))
            setattr(mob.spawn,statCost[1],int(getattr(mob.spawn,statCost[1])+statCost[3]))
            setattr(mob,statCost[0],int(getattr(mob,statCost[0])+statCost[3]))
            player.cinfoDirty = True
        
        mlevel = mskill.maxValue
        cap = mskill.absoluteMax
        if not cap or slevel < cap:
            if slevel >= mlevel:
                player.sendGameText(RPG_MSG_GAME_YELLOW,"%s currently cannot gain any more skill in %s.\\n"%(char.name,ENCHANT_skillname))
            elif slevel - skillReq < 10:
                char.checkSkillRaise(ENCHANT_skillname,1,1)
            else:
                player.sendGameText(RPG_MSG_GAME_YELLOW,"%s can't learn anything new from this enchantment.\\n"%char.name)
        player.sendGameText(RPG_MSG_GAME_YELLOW,"%s feels drained.\\n"%char.name)
    
    return



# This function allows the user to disenchant an artifact class item (which has been put into crafting window). If the item to be disenchanted is a player-enchanted item, the attribute to be stripped can be specified in the command line (attribute like in the automatic item stat description). Else the item gets stripped of all attributes and there is a chance to gain raw enchantment materials or trigger a mana regen spell, based on skill level (low chance). Soulbound items can't be disenchanted as to prevent quest item disenchantment.
def DisenchantCmd(mob,attribs):
    player = mob.player
    char = mob.character
    slevel = mob.skillLevels.get('Disenchanting',0)
    if not slevel:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't know how to disenchant anything.\\n"%char.name)
        return
    if 'Disenchanting' in mob.skillReuse:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src is still recovering from a previous disenchant,\\n$srche can disenchant again in about %i seconds.\\n"%mob.skillReuse['Disenchanting'],mob)
        return
    mskill = mob.mobSkillProfiles['Disenchanting']
    mob.skillReuse['Disenchanting'] = mskill.reuseTime
    disenchanted = False
    # Required skill to disenchant something, for skillup check purposes
    #  (in general there isn't a specific skill required, but outcome
    #  depends upon skill).
    skillReq = 0
    # Difficulty of the disenchantment (depends upon item/skill level and
    #  kind of disenchantment); diffMod < 0 means char has some 'experience'
    #  with these things, cap to -500.
    diffMod = 1000
    # How much mana this disenchanting costs.
    manaCost = 0
    
    
    # don't allow disenchanting while doing anything else
    if mob.attacking or mob.charmEffect or mob.isFeared or (mob.sleep > 0) or (mob.stun > 0) or mob.casting:
        player.sendGameText(RPG_MSG_GAME_DENIED,r'$src\'s disenchanting failed, $srche is in no condition to disenchant anything!\n',mob)
        return
    mob.cancelInvisibility()
    mob.cancelFlying()
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
    
    
    # get a list of all items in the crafting inventory
    disenchTarget = [item for item in char.items if (RPG_SLOT_CRAFTING_END > item.slot >= RPG_SLOT_CRAFTING_BEGIN)]
    
    
    # if there's more than one or no item in the crafting window, warn the user and return
    if not len(disenchTarget) == 1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You need to put one single item or stack into the crafting window.\\n")
        return
    
    
    disenchTarget = disenchTarget[0]  # else just get the single item
    
    
    # an enchanted focus can be disenchanted to gain a raw focus
    if disenchTarget.skill == ENCHANT_skillname:  # only foci should have this skill attached
        spellEnhanceLevel = disenchTarget.spellEnhanceLevel
        # raw foci may have a spellEnhanceLevel of 0 because
        #  spellEnhanceLevel is item wise and not itemProto, so can only be set dynamically.
        if not spellEnhanceLevel:
            player.sendGameText(RPG_MSG_GAME_DENIED,"A raw focus can't be disenchanted.\\n")
            return
        spellEnhanceLevel -= 10
        
        # use predefined difficulty mod, but modify by an additional amount to get a better
        #  difference from Fractured to Rough and to have an initial failure rate to those as well.
        diffMod = ENCHANT_QualitySkillReq[spellEnhanceLevel] - slevel + spellEnhanceLevel * 10
        if diffMod <= 0:
            diffMod = 1
        # calculate manaCost according to difficulty, min ~500 mana, max 5000
        manaCost = int(float(diffMod) / 37.0 * 450.0) + 500
        if mob.mana < manaCost:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough mana to disenchant this item.\\n"%char.name)
            return
        
        # critical failure, destroy focus, no skillup or anything but drain mana, double the amount
        #  or as much as possible.
        if diffMod >= 10 and randint(0,int(diffMod/10.0)):
            mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Enchanting failure")))
            player.sendGameText(RPG_MSG_GAME_LOST,"Whoops! Disenchanting this focus didn't go as intended.\\n")
            player.takeItem(disenchTarget)
            mob.mana -= manaCost * 2
            if mob.mana < 0:
                mob.mana = 0
            return
        
        # Create a fresh raw focus.
        proto = ItemProto.byName(disenchTarget.itemProto.name.split(' of ')[0])
        newFocus = proto.createInstance()
        newFocus.slot = disenchTarget.slot
        newFocus.setCharacter(char)
        
        # Destroy the previous focus.
        disenchTarget.destroySelf()
        
        # reward with eventual skillup, fancy graphics and mana costs
        #  here, because we don't want additional benefits like raw foci and mana regen.
        mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Dis - Enchanting")))
        player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully disenchanted the focus.\\n"%char.name)
        mob.mana -= manaCost
        
        mlevel = mskill.maxValue
        cap = mskill.absoluteMax
        if not cap or slevel < cap:
            if slevel >= mlevel:
                player.sendGameText(RPG_MSG_GAME_YELLOW,"%s currently cannot gain any more skill in Disenchanting.\\n"%char.name)
            elif slevel - skillReq < 10:
                char.checkSkillRaise('Disenchanting',1,1)
            else:
                player.sendGameText(RPG_MSG_GAME_YELLOW,"%s can't learn anything new from this disenchantment.\\n"%char.name)
        
        return
    
    
    # no focus, so extract enchantments currently applied to the item
    disenchTargetStats = []
    if not disenchTarget.spellEnhanceLevel == 9999:
        disenchTargetStats = [(st.statname,st.value) for st in disenchTarget.itemProto.stats]
    try:
        disenchTargetStats.extend(disenchTarget.variants[V_STAT])
    except KeyError:
        pass
    try:
        baneRace,baneMod = disenchTarget.variants[V_BANEWEAPON]
        # Item variants bane only stores the race and mod.  Enchanting
        # system uses a format of "<race> Bane".  Thus, take the baneRace
        # and create a key useable by the enchanting system.
        disenchTargetStats.append((baneRace + " Bane", baneMod))
    except KeyError:
        pass
    try:
        dmg,rate,resist,debuff = item.variants[V_WEAPON]
        if dmg != -1:
            disenchTargetStats.append(('Damage Mod',dmg))
        if rate != -1:
            disenchTargetStats.append(('Weapon Speed',rate))
        if debuff != -1:
            disenchTargetStats.append(('Debuff',(resist,debuff)))
    except KeyError:
        pass
    numEnchantments = len(disenchTargetStats)
    if not numEnchantments:
        player.sendGameText(RPG_MSG_GAME_DENIED,"This item doesn't bear any enchantments and therefore can't be disenchanted.\\n")
        return
    # Get the level of the item to be disenchanted.
    disenchItemLevel = disenchTarget.level
    
    # modify item level by class recommendations
    # take max level for difficulty calculations
    classes = list(disenchTarget.itemProto.classes)
    if len(classes):
        for cl in classes:
            if cl.level > disenchItemLevel:
                disenchItemLevel = cl.level
    
    # create a list of all free crafting slots
    freeslots = range(RPG_SLOT_CRAFTING_BEGIN,RPG_SLOT_CRAFTING_END)
    freeslots.remove(disenchTarget.slot)
    
    
    # player enchanted item, strip one single enchantment
    if disenchTarget.flags&RPG_ITEM_ENCHANTED and disenchTarget.crafted:
        # it's more difficult to just remove a single enchantment
        skillReq = disenchItemLevel*10
        diffMod = skillReq - slevel
        if diffMod < -500:
            diffMod = -500
        
        # charge the player mana for disenchanting
        # mana costs increase cubic with item level and decrease quadratic with skill level
        # 1000 skillpoints - lvl 100 item ~ (4096 * stat count) mana
        # 1000 skillpoints - lvl 1 item ~ (2 * stat count) mana
        # 1 skillpoint - lvl 100 item ~ (65536 * stat count) mana
        # 1 skillpoint - lvl 1 item ~ (24 * stat count) mana
        iScale = float(disenchItemLevel) * 0.15 + 1.0
        sScale = (1000.0 - float(slevel)) / 333.0 + 1.0
        isScale = iScale * sScale
        manaCost = int(round(isScale * isScale * iScale * numEnchantments))
        numEnchantments = 1  # since only one enchantment gets stripped on enchanted items
        if mob.mana < manaCost:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough mana to disenchant this item.\\n"%char.name)
            return
        
        # critical failure, destroy item, no skillup or anything but drain mana
        if diffMod>0 and randint(0,int(diffMod/10.0)):
            mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Enchanting failure")))
            player.sendGameText(RPG_MSG_GAME_LOST,"%s drained too much energy, accidentally destroying the %s.\\n"%(char.name,disenchTarget.name))
            player.takeItem(disenchTarget)
            mob.mana -= manaCost
            return
        
        # get stat names
        disenchTypeNames = [dts[0].upper() for dts in disenchTargetStats]
        # if no attribute specified just strip the first stat attribute in list
        disenchIndex = 0
        # try to strip specified attribute (only allowed on player enchanted items)
        if len(attribs):
            try:
                if attribs == 'HEALTH':
                    attribs = 'maxHealth'
                elif attribs == 'MANA':
                    attribs = 'maxMana'
                elif attribs == 'STAMINA':
                    attribs = 'maxStamina'
                elif attribs == 'MELEE HASTE':
                    attribs = 'haste'
                elif attribs == 'CASTING HASTE':
                    attribs = 'castHaste'
                elif attribs == 'REGENERATION':
                    attribs = 'regenHealth'
                elif attribs == 'REVITALIZATION':
                    attribs = 'regenStamina'
                elif attribs == 'MANA REGEN':
                    attribs = 'regenMana'
                disenchIndex = disenchTypeNames.index(attribs)
            except:
                player.sendGameText(RPG_MSG_GAME_DENIED,"Couldn't find %s in %s's stats. Possible stats are: %s\\n"%(attribs,disenchTarget.name,', '.join(disenchTypeNames)))
                return
        disenchTargetStats.pop(disenchIndex)
        
        # recreate partially disenchanted item
        disenchTarget.clearVariants()
        disenchTarget.name = disenchTarget.itemProto.name
        if len(disenchTargetStats):
            disenchTarget.name = "Enchanted " + disenchTarget.name
            for oldStat in disenchTargetStats:
                AddStatVariant(disenchTarget,oldStat[0],oldStat[1])
            # increase itemlevel by 2 per stat
            disenchTarget.levelOverride = disenchTarget.itemProto.level + 2*len(disenchTargetStats)
            if disenchTarget.levelOverride > 100:
                disenchTarget.levelOverride = 100
            disenchTarget.hasVariants = True
            # Flag the item as enchanted, hack.
            disenchTarget.spellEnhanceLevel = 9999
        else:
            disenchTarget.descOverride = disenchTarget.descOverride.split('\\nEnchanted by')[0]
            disenchTarget.levelOverride = disenchTarget.itemProto.level
            disenchTarget.hasVariants = False
            disenchTarget.spellEnhanceLevel = 0  # hack, flag as not enchanted
            # Reset quality, worth and enchanted flag, leave artifact flag if present.
            disenchTarget.flags = disenchTarget.flags & ~RPG_ITEM_ENCHANTED
            disenchTarget.quality = RPG_QUALITY_NORMAL
            disenchTarget.worthIncreaseTin = 0
        disenchTarget.crafted = True
        disenchTarget.refreshFromProto()
        
        disenchanted = True
    
    
    elif disenchTarget.flags&RPG_ITEM_ARTIFACT and not disenchTarget.flags&RPG_ITEM_SOULBOUND:
        # only allow disenchanting of stackable items of which at least a default stack size is present
        disenchProto = disenchTarget.itemProto
        if disenchProto.stackDefault > 1:
            if disenchTarget.stackCount < disenchProto.stackDefault:
                player.sendGameText(RPG_MSG_GAME_DENIED,"At least %i %s are required to attempt disenchanting.\\n"%(disenchProto.stackDefault,disenchTarget.name))
                return
        
        # the following means, that it is possible to gain disenchanting skill levels by disenchanting artifacts only up to 750. After that, disenchanting previously enchanted items is necessary (of at least item level 75). Currently it is not possible to get 1000 in skill due to crafted item levels limitations.
        skillReq = int(disenchItemLevel*7.4)
        diffMod = skillReq - slevel  # min: 7-1000=-993
        if diffMod < -500:
            diffMod = -500
        
        # charge the player mana for disenchanting, only half costs for this kind of disenchantment
        # mana costs increase cubic with item level and decrease quadratic with skill level
        # 1000 skillpoints - lvl 100 item ~ (2048 * stat count) mana
        # 1000 skillpoints - lvl 1 item ~ (1 * stat count) mana
        # 1 skillpoint - lvl 100 item ~ (32768 * stat count) mana
        # 1 skillpoint - lvl 1 item ~ (12 * stat count) mana
        iScale = float(disenchItemLevel) * 0.15 + 1.0
        sScale = (1000.0 - float(slevel)) / 333.0 + 1.0
        isScale = iScale * sScale
        manaCost = int(round(0.5 * isScale * isScale * iScale * numEnchantments))
        if mob.mana < manaCost:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough mana to disenchant this item.\\n"%char.name)
            return
        
        # critical failure, destroy item, no skillup or anything but drain mana
        # chance for critical failure for artifacts is higher than for player enchanted items, even if the skill required is lower here because the enchantments on artifacts are more ancient.
        if diffMod > 0 and randint(0,int(diffMod/5.0)):
            mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Enchanting failure")))
            player.sendGameText(RPG_MSG_GAME_LOST,"%s drained too much energy, accidentally turning the %s to dust.\\n"%(char.name,disenchTarget.name))
            player.takeItem(disenchTarget)
            mob.mana -= manaCost
            return
        
        # strip all stats but otherwise leave the item 'intact'
        else:
            disenchTarget.name = "Powerless " + disenchTarget.name
            disenchTarget.clearVariants()
            disenchTarget.descOverride = "\\n\\n".join([disenchTarget.itemProto.desc,"Stripped from its power by %s"%char.name])
            # as class recommendations are based on itemProto, these can't be adjusted.
            # they also don't need to...
            disenchTarget.levelOverride = disenchTarget.itemProto.level - 10
            if disenchTarget.levelOverride < 1:
                disenchTarget.levelOverride = 1
            # Set hasVariants to true to ensure all stats get removed.
            disenchTarget.hasVariants = True
            # 9999 used as 'enchanted' identifier, hack.
            disenchTarget.spellEnhanceLevel = 9999
            disenchTarget.refreshFromProto()
        disenchanted = True
    
    
    # no other items than enchanted or artifacts and no soulbounds allowed for disenchanting
    else:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s can't disenchant this kind of item.\\n"%char.name)
        return
    
    
    # if we disenchanted something, check for skillup and item/regen gains
    if disenchanted:
        mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Dis - Enchanting")))
        player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully disenchanted the artifact.\\n"%char.name)
        mob.mana -= manaCost
        
        # chance to get raw enchanting materials, nonlinear distribution ranging from 5% to 100%
        if not randint(0,int(ceil((diffMod+500)/75.0))):
            # number of raw enchanting materials we can salvage, max 5 from 900 skill on
            numEnchItems = randint(1,int(slevel/225)+1)
            if numEnchItems > numEnchantments:
                numEnchItems = numEnchantments
            for i in xrange(numEnchItems):
                enchItem = ItemProto.byName(ENCHANT_RawItems[randint(0,len(ENCHANT_RawItems)-1)])
                item = enchItem.createInstance()
                if len(freeslots):
                    item.slot = freeslots.pop()
                    item.setCharacter(char)
                else:
                    break
            player.sendGameText(RPG_MSG_GAME_GAINED,"Some of the mystic energy drained from the item forms into solid matter.\\n")
            
        # small chance to trigger a mana regen effect upon disenchanting, depending on skill level
        # 1 skill - 1%, 1000 skill - 10%
        if not randint(0,int(100-slevel*0.09)):
            # modify strength of the spell by skill level - lvl 1 ~ 1.0, lvl 1000 ~ 11.0
            buffMod = slevel / 100.0 + 1.0
            mob.processesPending.add(Spell(mob,mob,SpellProto.byName("Disenchanting Focus"),buffMod))
            player.sendGameText(RPG_MSG_GAME_GAINED,"%s managed to harness some mystic energy drained from the item.\\n"%char.name)
        
        mlevel = mskill.maxValue
        cap = mskill.absoluteMax
        if not cap or slevel < cap:
            if slevel >= mlevel:
                player.sendGameText(RPG_MSG_GAME_YELLOW,"%s currently cannot gain any more skill in Disenchanting.\\n"%char.name)
            elif slevel - skillReq < 10:
                char.checkSkillRaise('Disenchanting',1,1)
            else:
                player.sendGameText(RPG_MSG_GAME_YELLOW,"%s can't learn anything new from this disenchantment.\\n"%char.name)
    return



def Craft(mob,recipeID,useCraftWindow):
    player = mob.player
    char = mob.character
    
    # Get the itemlist we check for usable ingredients
    if useCraftWindow:
        
        # If the player clicked the craft button, only get items
        #  present in the crafting window.
        useItems = [item for item in char.items if (RPG_SLOT_CRAFTING_END > item.slot >= RPG_SLOT_CRAFTING_BEGIN)]
        if not len(useItems):
            return
    
    # Player used the /craft command. Get all items in characters posession.
    else:
        useItems = char.items
    
    # Client checks its local database for valid names and ingredients and handles
    #  case sensitivitiy. Only id gets passed to server.
    # Even though ingredients already got checked on client, need to check again to
    #  prevent any forms of cheating / hacking or client-server communication problems.
    
    # First check if player attempts to combine tomes.
    # Can combine two tomes into one of higher level.
    if recipeID == -1:  # Hack for now, use advanced recipes later.
        
        # Combining tomes requires the Scribing skill, check if available.
        if mob.skillLevels.get("Scribing",0):
            if "Scribing" in mob.skillReuse:
                player.sendGameText(RPG_MSG_GAME_DENIED,"$src is still cleaning $srchis tools,\\n$srche can use the <a:SkillScribing>Scribing</a> skill again in about %i seconds.\\n"%(mob.skillReuse["Scribing"]),mob)
                return
            
            # Get the tome defining variables to check for more of
            #  its kind in crafting window.
            spellEnhanceLevel = useItems[0].spellEnhanceLevel
            name = useItems[0].name
            
            passed = True
            
            # If the spellEnhanceLevel is outside the range 1...9 it either
            #  isn't a tome or can't be combined into a higher level one.
            if spellEnhanceLevel > 0 and spellEnhanceLevel < 10:
                count = 0
                
                # Check for additional tomes of the same kind, count their number.
                for item in useItems:
                    if spellEnhanceLevel != item.spellEnhanceLevel or name != item.name:
                        passed = False
                        break
                    count += item.stackCount
                
                # Upgrade tome if there were enough equal tomes found.
                if count == 2 and passed:
                    
                    # Mark skill as used.
                    mobSkill = mob.mobSkillProfiles["Scribing"]
                    mob.skillReuse["Scribing"] = mobSkill.reuseTime
                    
                    # Try to increase crafters skill.
                    char.checkSkillRaise("Scribing",1,2)
                    
                    # Give some feedback to crafter.
                    player.mind.callRemote("playSound","sfx/Pencil_WriteOnPaper2.ogg")
                    player.sendGameText(RPG_MSG_GAME_GOOD,r'%s has successfully combined the knowledge of the %s tomes.\n'%(char.name,name))
                    
                    # Create the new tome and place in crafting window.
                    spellname = useItems[0].itemProto.spellProto.name
                    scroll = ItemProto.byName("Scroll of %s"%spellname)
                    nitem = getTomeAtLevelForScroll(scroll, spellEnhanceLevel + 1)
                    nitem.slot = RPG_SLOT_CRAFTING0
                    # No itemInfo reset needed after setting character
                    nitem.setCharacter(char)
                    
                    # Take old items.
                    for item in useItems:
                        player.takeItem(item)
                    return
        
        # Somehow the client sent the command to combine tomes even though
        #  crafter doesn't have necessary ingredients in inventory.
        # Abort and give feedback.
        player.sendGameText(RPG_MSG_GAME_DENIED,r'%s is unable to craft anything with these items.\n'%(char.name))
        return
    
    # Find the desired recipe by id passed from client.
    try:
        recipe = Recipe.get(recipeID)
    except:
        player.sendGameText(RPG_MSG_GAME_DENIED,"Server received invalid recipe id. Crafting had to be aborted.\\n")
        print "WARNING: %s used invalid recipe id %i."%(mob.name,recipeID)
        return
    
    # Check skill requirements
    skillname = recipe.skillname
    charSkillLevel = mob.skillLevels.get(skillname,0)
    if charSkillLevel < recipe.skillLevel:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s requires a %i skill in <a:Skill%s>%s</a>.\\n"%(char.name,recipe.skillLevel,GetTWikiName(skillname),skillname))
        return
    
    # Get the item the player attempts to craft and some of its fields.
    craftProto = recipe.craftedItemProto
    craftStackMax = craftProto.stackMax
    craftStackDefault = craftProto.stackDefault
    craftUseMax = craftProto.useMax
    
    # Blacksmithing has some special rules about crafting costs
    #  and craft result. Get special modifiers here.
    if skillname == "Blacksmithing":
        moneyMod,craftStackCount,craftCharges = getBlacksmithingMods(mob,craftProto,charSkillLevel)
    
    # No blacksmithing, get normal modifiers.
    else:
        moneyMod,craftStackCount,craftCharges = (1.0,craftStackDefault,craftUseMax)
    
    # Check money requirements.
    cost = long(moneyMod * recipe.costTP)
    if not player.checkMoney(cost):
        player.sendGameText(RPG_MSG_GAME_DENIED, \
            "This <a:Skill%s>%s</a> requires %s.\\n"% \
            (GetTWikiName(skillname),skillname,GenMoneyText(cost)))
        return
    
    # Check for crafting delays and set new use time
    if skillname in mob.skillReuse:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src is still cleaning $srchis tools,\\n$srche can use the <a:Skill%s>%s</a> skill again in about %i seconds.\\n"%(GetTWikiName(skillname),skillname,mob.skillReuse[skillname]),mob)
        return
    mobSkill = mob.mobSkillProfiles[skillname]
    if skillname != 'Archery':
        mob.skillReuse[skillname] = mobSkill.reuseTime
    else:
        mob.skillReuse[skillname] = 12
    
    # Get the list of needed ingredients.
    ingredients = defaultdict(int)
    for i in list(recipe.ingredients):
        ingredients[i.itemProto] += i.count
    
    # Get a list of all crafting slots.
    emptySlots = range(RPG_SLOT_CRAFTING_BEGIN,RPG_SLOT_CRAFTING_END)
    
    consumed = {}
    stackItems = []
    
    # Define two different loops, so we don't have to check for stackMax in the loop each time.
    # Also directly check ingredients and consumables within the same loop.
    if not useCraftWindow and craftStackMax > 1:
        
        # Calculate needed space, either as charges or as item count.
        if craftUseMax > 1:
            neededSpace = craftStackCount * craftCharges
        else:
            neededSpace = craftStackCount
        
        # Check character's inventory for items and space availability.
        for item in useItems:
            
            # If the item is used for the recipe.
            proto = item.itemProto
            if proto in ingredients:
                
                # Charges on an ingredient represent its durability if max charges
                #  is greater than one.
                if proto.useMax > 1:
                    
                    # Only use one charge per craft.
                    ingredients[proto] -= 1
                    
                    # If the item is consumed, add to consumed list.
                    if proto.craftConsumed:
                        consumed[item] = 1
                
                # Use stack count instead.
                else:
                    
                    # The required quantity can be more than one, so use
                    #  the entire stack.
                    ingredients[proto] -= item.stackCount
                    
                    # If the item is consumed check how many are used.
                    if proto.craftConsumed:
                        
                        # The player has a larger quantity than is required,
                        #  set to use the amount the recipe requires.
                        if ingredients[proto] < 0:
                            consumed[item] = item.stackCount + ingredients[proto]
                        
                        # The player has a quantity that is less than or equal
                        #  to amount the recipe requires.
                        else:
                            consumed[item] = item.stackCount
                
                # If the ingredients requirement has been met, remove
                #  it from the list.
                if ingredients[proto] <= 0:
                    del ingredients[proto]
            
            # Remove slot from empty slots, as an item is in the slot.
            if RPG_SLOT_CRAFTING_END > item.slot >= RPG_SLOT_CRAFTING_BEGIN:
                emptySlots.remove(item.slot)
                
                # Check if craft result can be stacked on this item.
                if craftProto.name == item.name:
                    
                    # Get free charges or item counts.
                    if craftUseMax > 1:
                        diff = (craftStackMax - item.stackCount + 1) * craftUseMax - item.useCharges
                    else:
                        diff = craftStackMax - item.stackCount
                    
                    # If stacking is possible, add the stacking target to the
                    #  stacking list for later use and update needed space.
                    if diff > 0:
                        stackItems.append((item,diff))
                        neededSpace -= diff
        
        # There are no empty slots in craft window and craft item can't be fully stacked.
        if neededSpace > 0 and not len(emptySlots):
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no more room in the crafting inventory.\\n"%(char.name))
            return
    
    # No stacking checks required here. Run without them.
    else:
        
        # Check character's inventory or craft window for items and space availability.
        for item in useItems:
            
            # If the item is used for the recipe.
            proto = item.itemProto
            if proto in ingredients:
                
                # Charges on an ingredient represent its durability if max charges
                #  is greater than one.
                if proto.useMax > 1:
                    
                    # Only use one charge per craft.
                    ingredients[proto] -= 1
                    
                    # If the item is consumed, add to consumed list.
                    if proto.craftConsumed:
                        consumed[item] = 1
                
                # Use stack count instead.
                else:
                    
                    # The required quantity can be more than one, so use
                    #  the entire stack.
                    ingredients[proto] -= item.stackCount
                    
                    # If the item is consumed check how many are used.
                    if proto.craftConsumed:
                        
                        # The player has a larger quantity than is required,
                        #  set to use the amount the recipe requires.
                        if ingredients[proto] < 0:
                            consumed[item] = item.stackCount + ingredients[proto]
                        
                        # The player has a quantity that is less than or equal
                        #  to amount the recipe requires.
                        else:
                            consumed[item] = item.stackCount
                
                # If the ingredients requirement has been met, remove
                #  it from the list.
                if ingredients[proto] <= 0:
                    del ingredients[proto]
            
            # Remove slot from empty slots, as an item is in the slot.
            if useCraftWindow:
                
                # Player clicked on the craft button in crafting window.
                # Slot is only occupied if the item there isn't consumed.
                if not proto.craftConsumed:
                    emptySlots.remove(item.slot)
            elif RPG_SLOT_CRAFTING_END > item.slot >= RPG_SLOT_CRAFTING_BEGIN:
                emptySlots.remove(item.slot)
        
        # There are no empty slots in craft window.
        if not len(emptySlots):
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no more room in the crafting inventory.\\n"%char.name)
            return
    
    # If there are still need ingredients, the player is missing some items.
    if len(ingredients):
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s lacks %s for this craft.\\n"%(char.name,', '.join("%i <a:Item%s>%s</a>"%(count,GetTWikiName(item.name),item.name) for item,count in ingredients.iteritems())))
        return
    
    # All crafting requirements fulfilled, take away consumed ingredients.
    for item,count in consumed.items():
        proto = item.itemProto
        
        # If item uses charges, reduce a charge.
        if proto.useMax > 1:
            item.useCharges -= 1
            
            # If the item is out of charges, reduce stack count.
            if item.useCharges <= 0:
                item.stackCount -= 1
                
                # If the stack is empty, remove the item from player.
                if item.stackCount <= 0:
                    player.takeItem(item)
                
                # An item still exists in the stack, udpate the
                #  count and use max charges.
                else:
                    item.useCharges = proto.useMax
                    item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})
            
            # Item still has charges.
            else:
                item.itemInfo.refreshDict({'USECHARGES':item.useCharges})
        
        # Item does not use charges, so reduce stack count.
        else:
            item.stackCount -= count
            
            # If the stack is empty, remove from player.
            if item.stackCount <= 0:
                player.takeItem(item)
            
            # An item still exists in the stack, update the count.
            else:
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
    
    # Take money from player.
    player.takeMoney(cost)
    
    # Try stacking the craft result. Define two different loops
    #  one with and one without charges.
    if craftStackMax > 1 and craftUseMax > 1:
        
        # Get total charges.
        totalCharges = craftCharges * craftStackCount
        
        # Run through all possible stacking targets and stack.
        for item,diff in stackItems:
            if diff > totalCharges:
                diff = totalCharges
            item.stackCount += diff / craftUseMax
            item.useCharges += diff % craftUseMax
            if item.useCharges > craftUseMax:
                item.useCharges -= craftUseMax
                item.stackCount += 1
            totalCharges -= diff
            item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})
            if totalCharges <= 0:
                craftCharges = 0
                craftStackCount = 0
                break
        
        # There are still charges remaining. Recalculate
        #  stack count and charges.
        else:
            craftStackCount = totalCharges / craftUseMax  # Get count of stacks with full charges.
            craftCharges = totalCharges % craftUseMax  # Get remaining charges.
        
            # If there are no remaining charges, then the stack
            #  is full and has the max charges.
            if not craftCharges:
                craftCharges = craftUseMax
            
            # Otherwise, there exists an item without full charges.
            # Since stack count currently is the number of items with
            #  full charges, need to increment stack count by one.
            else:
                craftStackCount += 1
    
    # No charges, run without additional calculation.
    elif craftStackMax > 1:
        
        # Run through all possible stacking targets and stack.
        for item,diff in stackItems:
            if diff > craftStackCount:
                diff = craftStackCount
            item.stackCount += diff
            craftStackCount -= diff
            item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
            if craftStackCount <= 0:
                break
    
    # If there are items remaining, create a new stack (or a new item if it doesn't stack anyway).
    if craftStackCount:
        item = craftProto.createInstance()
        item.slot = emptySlots.pop()
        item.stackCount = craftStackCount
        item.useCharges = craftCharges
        item.setCharacter(char)
        item.descOverride = "\\n\\n".join([craftProto.desc,"Crafted by %s"%char.name])
        item.crafted = True
    
    # Display success and cost to player.
    player.sendGameText(RPG_MSG_GAME_GAINED,"%s has crafted a <a:Item%s>%s</a>!\\n"%(char.name,GetTWikiName(craftProto.name),craftProto.name))
    costTotalText = GenMoneyText(cost)
    if costTotalText:
        player.sendGameText(RPG_MSG_GAME_YELLOW,"This <a:Skill%s>%s</a> consumes %s.\\n"%(GetTWikiName(skillname),skillname,costTotalText))
    
    # Check for skill increases.
    maxLevel = mobSkill.maxValue
    cap = mobSkill.absoluteMax
    if not cap or charSkillLevel < cap:
        if charSkillLevel >= maxLevel:
            player.sendGameText(RPG_MSG_GAME_YELLOW,"%s currently cannot gain any more skill in <a:Skill%s>%s</a>.\\n"%(char.name,GetTWikiName(skillname),skillname))
        
        # A character can gain skill in blacksmithing independent of the
        #  recipes difficulty. In return, there is a lower chance for a skillup.
        elif skillname == 'Blacksmithing':
            char.checkSkillRaise('Blacksmithing',3,4)
        
        # Non-blacksmithing crafting skills follow a 15 skill level rule.
        # Does the character have more than 15 skill levels over the required
        #  skill, he will no longer gain skillups.
        elif charSkillLevel - recipe.skillLevel < 15:
            char.checkSkillRaise(skillname,1,2)
    
    # Finally, if assigned play the crafting sound.
    if recipe.craftSound:
        player.mind.callRemote("playSound",recipe.craftSound)


