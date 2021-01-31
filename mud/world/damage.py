# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup damage damage
#  @ingroup world
#  @brief The damage module provides functions to heal and damage a Mob.
#  @{


from mud.world.core import *
from mud.world.defines import *
from mud.world.messages import GameMessage
from mud.world.shared.vocals import *

from math import ceil,floor
from random import randint
import time



## @brief ExtraDamageInfo provides a way to temporarily modify a Mob's
#         damage mitigation based on resist modifiers.
class ExtraDamageInfo:

    ## @brief Initialize the class, delgating responsibility to clear().
    #  @param self (ExtraDamageInfo) The object pointer.
    def __init__(self):
        self.clear()


    ## @brief Clears all resist modifiers within the ExtraDamageInfo.
    def clear(self):

        ## @brief (RPG_RESIST_TYPE) The type of resist being modified.
        self.resistDebuff = None

        ## @brief (Integer) The amount by which the resist will be reduced.
        self.resistDebuffMod = 0


## @brief XPDamage is used to track damage a way to temporarily modify a Mob's
#         damage mitigation based on resist modifiers.
class XPDamage:

    ## @brief Initialize the class.
    #  @param self (XPDamage) The object pointer.
    #  @todo TWS: This should probably accept the initial amount.
    def __init__(self):

        ## @brief (Float) The last time damage was added.
        self.lastTime = time.time()

        ## @brief (Integer) The total amount of damage that has been inflicted.
        self.amount = 0

    ## @brief Initialize the class.
    #  @param self (XPDamage) The object pointer.
    #  @param amount (Integer) The amount of damage being added.
    def addDamage(self, amount):

        # Increase the total amount of damage inflicted by the new damage
        # amount.
        self.amount += amount

        # Update the last time damage was added to now.
        self.lastTime = time.time()


## @brief (Dictionary) Dictionary containing the text for a damage type (value)
#         for the type of damage (RPG_DMG_TYPE - key) when there is a known
#         inflictor.
DAMAGETEXT = {}
DAMAGETEXT[RPG_DMG_FIRE]="burns"
DAMAGETEXT[RPG_DMG_COLD]="freezes"
DAMAGETEXT[RPG_DMG_POISON]="poisons"
DAMAGETEXT[RPG_DMG_DISEASE]="diseases"
DAMAGETEXT[RPG_DMG_ACID]="corrodes"
DAMAGETEXT[RPG_DMG_ELECTRICAL]="zaps"
DAMAGETEXT[RPG_DMG_MAGICAL]="oppresses"
DAMAGETEXT[RPG_DMG_SLASHING]="slashes"
DAMAGETEXT[RPG_DMG_IMPACT]="crushes"
DAMAGETEXT[RPG_DMG_CLEAVE]="cleaves"
DAMAGETEXT[RPG_DMG_PIERCING]="pierces"
DAMAGETEXT[RPG_DMG_PHYSICAL]="damages"
DAMAGETEXT[RPG_DMG_PUMMEL]="pummels"
DAMAGETEXT[RPG_DMG_CLAWS]="claws"
DAMAGETEXT[RPG_DMG_CRITICAL]="critically wounds"
DAMAGETEXT[RPG_DMG_DRAIN]="drains"
DAMAGETEXT[RPG_DMG_FOREST]="chops"
DAMAGETEXT[RPG_DMG_MINE]="mines"

## @brief (Dictionary) Dictionary containing the text for a damage type (value)
#         for the type of damage (RPG_DMG_TYPE - key) when there is no known
#         inflictor.
DAMAGETEXTNOINFLICTOR = {}
DAMAGETEXTNOINFLICTOR[RPG_DMG_FIRE]="burned"
DAMAGETEXTNOINFLICTOR[RPG_DMG_COLD]="frozen"
DAMAGETEXTNOINFLICTOR[RPG_DMG_POISON]="poisoned"
DAMAGETEXTNOINFLICTOR[RPG_DMG_DISEASE]="diseased"
DAMAGETEXTNOINFLICTOR[RPG_DMG_ACID]="corroded"
DAMAGETEXTNOINFLICTOR[RPG_DMG_ELECTRICAL]="zapped"
DAMAGETEXTNOINFLICTOR[RPG_DMG_MAGICAL]="oppressed"
DAMAGETEXTNOINFLICTOR[RPG_DMG_SLASHING]="slashed"
DAMAGETEXTNOINFLICTOR[RPG_DMG_IMPACT]="crushed"
DAMAGETEXTNOINFLICTOR[RPG_DMG_CLEAVE]="cleaved"
DAMAGETEXTNOINFLICTOR[RPG_DMG_PUMMEL]="pummeled"
DAMAGETEXTNOINFLICTOR[RPG_DMG_PIERCING]="pierced"
DAMAGETEXTNOINFLICTOR[RPG_DMG_CLAWS]="clawed"
DAMAGETEXTNOINFLICTOR[RPG_DMG_CRITICAL]="critically wounded"
DAMAGETEXTNOINFLICTOR[RPG_DMG_DRAIN]="drains"
DAMAGETEXTNOINFLICTOR[RPG_DMG_PHYSICAL]="damaged"


## @brief Heal a mob, recovering health for the Mob.
#  @param mob (Mob) The recipient of the heal.
#  @param healer (Mob) The source of the heal.
#  @param amount (Integer) The amount of health to be recovered.
#  @param isRegen (Boolean) Indicates if heal is regen
#  @return None.
#  @todo TWS: Should move this to iterative instead of recursive.
#  @todo TWS: Optimize math, do x + x instead of x * 2.
def Heal(mob, healer, amount, isRegen=False):

    # If the mob is already at max health, then there is no health to recover
    # so return early.
    if mob.health >= mob.maxHealth:
        return

    # Get the max amount of health that may be recovered.
    gap = mob.maxHealth - mob.health

    # If the amount to heal is greater than the amount that may be recovered,
    # then clamp the amount of health that will be recovered to never exceed
    # the amount of health that may be recovered.  Otherwise, the mob would
    # have a health value higher than the Mob's max health.
    if amount > gap:
        amount = gap

    # Heal the Mob, increasing the Mob's health.
    mob.health += amount

    # If the healer and the mob are not the same, and heal is not a regen, then
    # it is possible that the healer has assisted another mob's enemy.
    if mob != healer and not isRegen:

        # If the healer was a Player and some health was healed, then the healer
        # needs to be added to the hate list of mob's that are currently
        # aggroing the mob healed.
        if healer.player and amount>1:

            # Iterate over the active mobs in the Mob's ZoneInstance.
            for m in mob.zone.activeMobs:

                # If the iterated mob is a Player, continue to the next mob.
                if m.player:
                    continue

                # If the mob that was healed is on the iterated mob's hate list,
                # then add the healer to the itearted mob's hate list because
                # the healer has assisted the iterated mob's enemy.
                if m.aggro.get(mob,0) > 0:

                    # Add aggro to the iterated mob towards the healer.
                    m.addAggro(healer,amount/2)

    # If the mob is a Player and the heal is not a regen, then inform the
    # Player.
    if mob.player and not isRegen:
        mob.player.sendGameText(RPG_MSG_GAME_GOOD,"%s has been healed for %i points!\\n"%(mob.name,amount))


## @brief Inflicts damage to a Mob, reducing the Mob's health.
#  @param mob (Mob) The recipient of the damage.
#  @param inflictor (Mob/None) The source of the damage.
#  @param amount (Integer) The amount of unmitigated damage to be done.
#  @param dmgType (RPG_DMG_TYPE) The type of damage being inflicted.
#  @param textDesc (String) Damage text that will substitute the default damage
#                  message.
#  @param doThorns (Boolean) Indicates if damage reflection should be performed.
#  @param outputText (Boolean) Indicates if Players will receive a message
#                    containing the damage information.
#  @param isDrain (Boolean) Indicates if the source of the damage is a drain
#                 effect.
#  @return (Integer) The amount of damage inflicted to Mob.
#  @todo TWS: Should move this to iterative instead of recursive.
#  @todo TWS: Optimize math, move x*2 to x + x.
#  @bug TWS: If damage reflection kills an inflictor, the inflictor may not
#       receive the killing damage message because the mob.tick() may notice
#       the dead mob before the message is added to the player.
def Damage(mob, inflictor, amount, dmgType, textDesc=None, doThorns=True, \
           outputText=True, isDrain=False):
    
    # If the target is invulnerable return immediately.
    if mob.invulnerable > 0:
        return 0

    # If the dmgType is not unstoppable and the inflictor is not allowed to harm
    # the mob, then return 0 damage.
    if dmgType != RPG_DMG_UNSTOPPABLE and not AllowHarmful(inflictor,mob):
        return 0

    # When a mob takes damage the mob's combat timer is reset.  If the mob's
    # combat timer is below 72, then reset the timer to 72.  This prevents a
    # Mob's natural regen from occuring until the combat timer is satisfied.    
    if mob.combatTimer < 72:
        mob.combatTimer = 72

    # If the mob is not a Player and has not been initialized, then initialize
    # the mob so the mob will have proper max health values.
    if not mob.player:

        # If the mob is not initialized, then initialize it.
        if not mob.mobInitialized:
            mob.initMob()
    else:
        if CoreSettings.IDE and CoreSettings.IDE_ZONE:
            #editing zone... no damage
            return 0
            
    #-- Check for Harvest Tool
    pweapon = ""
    sweapon = ""
    if len(mob.spawn.requiresWeapon):
        try:
            pweapon = inflictor.worn.get(RPG_SLOT_PRIMARY).itemProto.skill
            sweapon = inflictor.worn.get(RPG_SLOT_SECONDARY).itemProto.skill
        except:
            pass
    if pweapon == mob.spawn.requiresWeapon or sweapon == mob.spawn.requiresWeapon:
        pass
    else:
        inflictor.player.sendGameText(RPG_MSG_GAME_DENIED,"You may only affect %s with a %s item equipped.\\n"%(mob.name,mob.spawn.requiresWeapon))
        return

    # If the damage is less than 1, then clamp the damage to be at least 1.
    # Without this, damage could become a negative value and result in healing
    # the mob.
    if 0 >= amount:
        amount = 1

    # If there is an inflictor, then remove invulnerability and apply damage
    # multiplier if necessary.
    if inflictor:

        # Any aggressive attack by an invulnerable character will remove the
        # character's invulnerability state.  If the Character performing the
        # attack is invulnerable, then cancel the invulnerability effect.
        if inflictor.character:
            inflictor.cancelStatProcess("invulnerable", \
                "$tgt is no longer protected from death!\\n")

        # If thorns is being handled and the inflictor has a difficult or a
        # damage mod, then modify the damage by the inflictor's difficulty 
        # or damage mod, whichever is greatest.  Thorns not being checked 
        # usually indicates a spell, rank attack, or a riposte.
        if (inflictor.difficultyMod > 1.0 or inflictor.damageMod > 1.0) and doThorns:
            if inflictor.damageMod > inflictor.difficultyMod:
                amount += amount * (inflictor.damageMod/4.0)
                amount = ceil(amount)
            else:
                amount += amount * (inflictor.difficultyMod/4.0)
                amount = ceil(amount)
                

    # If it is not a drain, then get resist from the mob.
    if not isDrain:
        rtype = RESISTFORDAMAGE[dmgType]
        resist = mob.resists.get(rtype, 0)

    # Drain damage cannot be mitigated so do not get the resist.
    else:
        resist = 0


    # Get the current extra damage info on the mob.  This may contain resist
    # modifiers.
    extraDamageInfo = mob.extraDamageInfo

    # If the Mob has some resist, and the extra damage info has a resist debuff
    # of the same type as the resist for the damage type, then adjust the mob's
    # resist.
    if 0 < resist and extraDamageInfo.resistDebuffMod and rtype == extraDamageInfo.resistDebuff:
        resist -= mob.extraDamageInfo.resistDebuffMod

        # Never drop the resist below zero.  If the mob's resist is below zero, 
        # then clamp the mob's resist to be no less than 0.
        if 0 > resist:
            resist = 0

    # If the mob has resist for the damage type, then multiply or mitigate the
    # damage amount.
    if resist:

        # If the mob has no resist to the damage, then the damage is receives
        # a bonus multiplier.
        # Note: Currently the damage multiplier is never applied because resist
        # is is clamped to zero
        if 0 > resist:

            # Calculate the multipied damage.
            # Note: -resist gives positive value.
            adjustedAMount = amount + ( -resist * 3 )

            # If the damage bonus is more than 200%, then cap the damage bonus
            # to not exceed 200%..
            if adjustedAMount > amount * 2:
                adjustedAMount = amount * 2

            amount = adjustedAMount

        # Otherwise, the mob has some resist.  Mitigate the damage based on the
        # resist.
        else:

            # Calculate the mitigated damage.
            adjustedAMount= amount - ( resist * 2 )

            # If the damage being mitigated is more than 50%, then cap the
            # damage mitigation at not exceed 50%.
            if adjustedAMount/amount < .5:
                amount *= .5
            
            # Otherwise, use the mitigated amount.    
            else:
                amount = adjustedAMount

    
    # Round the damage down to an integer.
    amount = floor(amount)
    
    # If the damage is less than 1, then clamp the damage to be at least 1.
    # Without this, damage could become a negative value and result in healing
    # the mob.
    if 1 > amount:
        amount = 1

    # If there is an inflictor, then mob aggro, xpDamage, and items may need
    # updated.
    if inflictor:

        # For Players, add agro based on each Character in the Party.
        if inflictor.player:

            # Iterate over the Player's Party members.
            for char in inflictor.player.party.members:

                # Make a local reference to this Character's Mob.
                charMob = char.mob

                # If the Character's Mob is not in zone (probably dead), then
                # continue to the next Character.
                if charMob.detached:
                    continue

                # The amount of damage being done is the hate value.
                hate = amount

                # If the iterated Character is the inflicitor, then add a hate
                # bonus.
                if charMob == inflictor:
                    hate *= 2

                # Add aggro on the damaging Mob towards the Character's Mob.
                mob.addAggro(charMob, hate)

        # Otherwise, the inflicitor is not a Player, so just add hate the mob.
        # This can occur when NPCs fight one another.
        else:
            mob.addAggro(inflictor, amount * 2)


        # If the inflictor is not in the mob's xpDamage dictionary, then create
        # a new XPDamage entry for the inflictor.
        # The xpDamage data needs to be updated.  This is used for determining
        # which Mob is rewarded the kill when the mob dies.
        mob.xpDamage.setdefault(inflictor,XPDamage()).addDamage(amount)

        # If a Player is taking damage from in an inflictor, then gear may
        # break.
        if mob.player and not isDrain:

            # Iterate over breakable items.
            for item in mob.wornBreakable.itervalues():

                # If the item still has a repair value and the random result
                # is zero (1 out of 21 chance of breaking), then damage the
                # item.
                if item.repair and not randint(0, 20):

                    # Damage the item.
                    item.repair -= 1

                    # The item may damaged enough that it warrants informing the
                    # Player with a message and sound.

                    # Calcaulate a ratio of the current repair value to the
                    # max repair value.
                    repairRatio = float(item.repair)/float(item.repairMax)

                    # If the ratio is zero, then the item is completely broken.
                    if not repairRatio:

                        # Inform the Player with a message and sound.
                        mob.player.sendGameText(RPG_MSG_GAME_RED,"%s's %s has broken! (0/%i)\\n"%(mob.name,item.name,item.repairMax))
                        mob.playSound("sfx/Shatter_IceBlock1.ogg")

                    # Otherwise, check if the ratio is below the 20% threshold.
                    # If so, it is severely damaged.
                    elif .2 > repairRatio:

                        # Inform the Player with a message and sound.
                        mob.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s's %s is severely damaged! (%i/%i)\\n"%(mob.name,item.name,item.repair,item.repairMax))
                        mob.playSound("sfx/Menu_Horror24.ogg")

                    # Updating the item's stats, recalculating the penalty from
                    # the updated repair value.  Refreshing only the repair
                    # value will not work since the new repair value may affect
                    # other attributes.
                    item.setCharacter(mob.character,True)

    # Cancel feign death and sleep conditions.
    # TWS: Should probaby check for conditions before itearting over processes
    # and trying to cancel the conditions.  This should probably be handled by
    # mob.cancel calls.
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.cancelSleep()

    # If the mob being damaged is Player and is casting without combat casting,
    # then check if an interruption occurs based on damge and concentration
    # skill.
    if mob.player and mob.casting and not mob.combatCasting:

        # Flag used to indicate if the casting was interrupted.
        cancel = True

        # Get the mob's concentration skill.
        conc = mob.skillLevels.get("Concentration",0)

        # If the mob has a concentration skill, then do a random check based
        # on the damage amount.  The higher the damage, the more likely it will
        # interrupt the casting.
        if conc:

            # Get a random number ranging from 0 to the amount of damage being
            # inflicted.
            r = randint(0,amount)

            # If the number is less than the modified concentration skill value,
            # then the casting is not interrupted.
            if r <= conc*2:

                # Flag the casting as not interrupted.
                cancel = False

                # Attempt to increase the Character's concentration skill.
                mob.character.checkSkillRaise("Concentration",2,10)

        # If the damage interrupted the spell, then cancel the mob's casting.
        if cancel:

            # Calculate an adjusted recast time for the spell the mob was
            # casting.
            t =mob.casting.spellProto.recastTime/5

            # Update the mob's recast time, based on the adjusted time.
            if t:
                mob.recastTimers[mob.casting.spellProto]=t

            # Cancel the mob's casting.
            mob.casting.cancel()

            # Inform the Player.
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s's casting has been interrupted!\\n"%(mob.name))

    # Characters are never assigned a battle and to prevent battle spam, filter
    # out messages if both inflictor and mob are members of a Battle.  Also, do
    # not print or invoke sounds on drains.
    if (not mob.battle or not (inflictor and inflictor.battle)) and not isDrain:

        # If output is enabed, then the mesasge needs to be built.
        if outputText:

            # If a text description is not supplied, determine the text based on
            # the type of damage being inflicted.
            if not textDesc:

                # Get specific text based on the presence of an inflictor.
                if inflictor:
                    dmgText = DAMAGETEXT[dmgType]
                else:
                    dmgText = DAMAGETEXTNOINFLICTOR[dmgType]

            # Otherwise, the caller provided the damage text to be used.
            else:
                dmgText = textDesc

            # Build the message to be sent.
            if inflictor:
                text = r'%s %s %s for %i damage!\n'%(inflictor.name,dmgText,mob.name,amount)
            else:
                text = r'%s is %s for %i damage!\n'%(mob.name,dmgText,amount)

            # Send the game message to the mob, inflictor, and characters in
            # range.  This should occur before damage is applied so that the
            # zone does not detach a mob controled by a Player before sending
            # the sending the damage message to the Player.  Otherwise, a
            # Player may not receive the messagec with the damage information
            # that killed the Player's Character.
            GameMessage(RPG_MSG_GAME_COMBAT,mob.zone,inflictor,mob,text,mob.simObject.position,20)

        # Play the pain animation.
        mob.zone.simAvatar.mind.callRemote("pain",mob.simObject.id)

        # Get a random pain sound from the Spawn.
        snd = mob.spawn.getSound("sndPain")

        # If there is a sound, check if it is played.
        if snd:

             # The pain sound is only played 50% of the time.
             if not randint(0,1):
                # Play the sound.
                mob.playSound(snd)

        # Otherwise, the Spawn did not have a pain sound in its
        # SpawnSoundProfile.
        else:

            # Vocalize a grunt sound 1 out of 3 times
            if not randint(0,2):
                # Play sounds.
                mob.vocalize(VOX_HURTGRUNT)

            # Otherwise, vocalize a punch.
            else:
                # Play sounds.
                mob.vocalize(VOX_HURTPUNCH)


    # The original damage amount has been mitigated, and all simulation and
    # output has been handled.  Therefore, the damage is ready to be applied.

    # Inflict the damage to the Mob, reducing the Mob's health.
    mob.health -= amount

    # Store the amount of damage being inflicted to a variable that will be
    # returned at the end of the function.
    DAMAGEAMOUNT = amount

    # Set a flag to indicate the Mob has taken damage.
    # TWS: Is this flag needed?
    mob.tookDamage = True


    # Check for damage reflection (thorns).  This is handled after regular the
    # intial damage has been handled to emulates the concept that a mob hits a
    # target, does damage, then receives damage reflection.

    # If the damage reflection is to be checked, there is an inflictor, the mob
    # has at least one spell effect, and the damage is not a drain, then damage
    # reflection may occur.
    if doThorns and inflictor and len(mob.processesIn) and not isDrain:

        # Get the damage reflection type based on the initial damage type.
        thornDmgType = DAMAGEFORRESIST[RESISTFORDAMAGE[dmgType]]

        # Get a list of effects on the Mob based on the thorn damage type.
        dmgReflection = mob.dmgReflectionEffects.get(thornDmgType, None)

        # If the mob has thorns (damage reflection), check each effect to find
        # the highest damage reflection.
        if dmgReflection:

            # bestThornDamage and thornDamage are used to locate the highest
            # damage reflection amount.
            bestThornDamage = 0
            thornDamage = 0

            # Iterate over al the damage reflection effects, calculating the
            # thorn damage for each.
            for effect in dmgReflection:

                # Calculate the thorn damage based on the effect's reflection
                # percent.
                thornDamage = ceil(amount * effect.dmgReflectionPercent)

                # Cap the damage based on the max reflection.  If the damage
                # return would be higher than the effect's max damage 
                # reflection, then set the damage reflection to not exceed the
                # max.
                if thornDamage > effect.dmgReflectionMax:
                    thornDamage = effect.dmgReflectionMax

                # If the amount of damage is higher than the highest damage
                # amount, then update the highest damage amount.
                if thornDamage > bestThornDamage:
                    bestThornDamage = thornDamage

            # Calculate damage through a recursive call.  This will return the
            # actual damage thorns does to the inflictor after resist and
            # mitigation is applied.
            # TWS: This needs to be done iteratively!
            thornDamageTaken = Damage( mob = inflictor, # The current inflictor becomes the inflicted.
                                           inflictor = None, # There is no inflictor.  This prevents agro generation.
                                           amount = bestThornDamage, # Damage amount is the non-mitiated thorn damage.
                                           dmgType = thornDmgType, # Damage is based on thorn damage type.
                                           textDesc = None, # No text because output is not used.
                                           doThorns = False, # Thorns set to false.
                                           outputText = False) # Handle output after the recursive call.

            # Create and send the thorn damage message.  This is handled
            # manually because there is no inflictor on the recursive call to
            # prevent agro and damage experience updating.
            thornText = r'%s is %s for %i damage!\n'%(inflictor.name,DAMAGETEXTNOINFLICTOR[thornDmgType],thornDamageTaken)
            GameMessage(RPG_MSG_GAME_COMBAT,mob.zone,mob,inflictor,thornText,mob.simObject.position,20)

    # Remove extraDamageInfo from a mob.
    # TWS: The extra damage info is cleared the doAttack of a CombatProcess.
    # Does it need to be cleared here as well?
    extraDamageInfo.clear()

    # Return the amount of damage inflicted to the mob.
    return DAMAGEAMOUNT


## @} # End damage group.
