# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup combat combat
#  @ingroup world
#  @brief The combat module contains the CombatProcess class which encapsulates
#         melee combat rules, calculations, and incremental processing.
#  @{


from mud.world.core import AllowHarmful,CoreSettings,GetLevelSpread,GetRangeMin
from mud.world.damage import Damage
from mud.world.defines import *
from mud.world.process import Process
from mud.world.spell import SpawnSpell
from mud.worlddocs.utils import GetTWikiName

from math import ceil,floor
from random import randint



## @brief UnarmedSoundProfile contains the default unarmed sound profile.
class UnarmedSoundProfile:

    ## @brief Initialize class.  Setting the default unarmed sound variables.
    #  @todo TWS: Consider using list to make adding/removing sounds much
    #        easier.
    def __init__(self):

        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack1 = "character/Boxing_FemalePunchBreath06.ogg"
        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack2 = "character/Boxing_FemalePunchBreath07.ogg"
        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack3 = "character/Boxing_FemalePunchBreath09.ogg"
        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack4 = "character/Boxing_MalePunchGrunt01.ogg"
        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack5 = "character/Boxing_MalePunchGrunt02.ogg"
        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack6 = "character/Boxing_MalePunchGrunt05.ogg"
        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack7 = "character/Boxing_MalePunchGrunt03.ogg"
        ## @brief (String) Path to an unarmed attack sound file.
        self.sndAttack8 = "character/Boxing_MalePunchBreath02.ogg"
        ## @brief (Integer) The count of unarmed attack sounds file.
        self.numSndAttack = 8

        ## @brief
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit1 = "character/Punch_Boxing_BodyHit01.ogg"
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit2 = "character/Punch_Boxing_BodyHit02.ogg"
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit3 = "character/Punch_Boxing_BodyHit03.ogg"
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit4 = "character/Punch_Boxing_BodyHit04.ogg"
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit5 = "character/Punch_Boxing_FaceHit1.ogg"
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit6 = "character/Punch_Boxing_FaceHit2.ogg"
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit7 = "character/Punch_Boxing_FaceHit3.ogg"
        ## @brief (String) Path to an unarmed hit sound file.
        self.sndHit8 = "character/Punch_Boxing_FaceHit4.ogg"
        ## @brief (Integer) The count of unarmed hit sounds.
        self.numSndHit = 8


    ## @brief Gets a path to a random unarmed sound file.
    #  @param self (UnarmedSoundProfile) The object pointer.
    #  @param snd (String) Indicates if the sound file to get is an attack or
    #             hit.
    #  @return (String) Path to a sound file.
    #  @todo TWS: Could probaby just pass true/false instead of string for the
    #        snd arguement.  This should provide faster and safer logical
    #        checks.
    def getSound(self, snd):

        # If the sound to play is an attack, then get and return a random
        # attack file path.
        if snd == "sndAttack":

            # Return a random attack sound file path.
            return getattr(self,"sndAttack%i"%randint(1,8))

        # Otherwise, the sound to return is a hit sound.  Thus, return a random
        # hit sound file path.
        return getattr(self,"sndHit%i"%randint(1,8))


## @brief (UnarmedSoundProfile) UnarmedSoundProfile providing unarmed combat
#         sound file paths mobs.
UNARMEDSOUNDPROFILE = UnarmedSoundProfile()


## @brief Handles skill raise checks for a succesful attack.
#  @param mob (Mob) The Mob that performed the attack.
#  @param offhand (Boolean) Indicates if the attack was primary or offhand.
#  @return None.
#  @todo TWS: Should this be part of a combat process?  What if a skill or spell
#        needs to directly invoke an attack.
def SuccessfulAttack(mob, offhand=False):

    # Make a local handle to the Mob's Character.
    char = mob.character

    # Skill indicates the skill being used for the attack.  This defaults to
    # fists.
    skill = "Fists"

    # If the attack was offhand, then get the item in the secondary slot.
    if offhand:
        wpn = mob.worn.get(RPG_SLOT_SECONDARY, None)

    # Otherwise, the attack was from the primary so get the item in the primary
    # slot.
    else:
        wpn = mob.worn.get(RPG_SLOT_PRIMARY, None)

    # If there was an item in the appropriate slot and the item has an associted
    # skill, get the skill.
    if wpn and wpn.skill:
        skill = wpn.skill

    # Attempt to raise the weapon skill.
    char.checkSkillRaise(skill,1,8)

    # Attempt to raise Tactics Offense.
    char.checkSkillRaise("Tactics Offense",1,8)

    # If the attack was from the offhand, then check for other skill raises.
    if offhand:

        # Get the primary weapon.
        pweapon = mob.worn.get(RPG_SLOT_PRIMARY, None)

        # If there is a weapon in primary and secondary slots, then check
        # the weapons.
        if pweapon and wpn:

            # Attempt to raise the Power Wield skill under either of the
            # following conditions:
            # - This is an offhand attack, so if the primary weapon is a
            #   two-hander, then the Mob has Power Wield.
            # - If the secondary weapon is a two-hander and the Mob has the
            #   Power Wield skill.
            if "2H" in pweapon.skill or "2H" in skill and mob.skillLevels.get("Power Wield"):
                char.checkSkillRaise("Power Wield",1,8)

            # Otherwise, the Mob does not have Power Wield, so just
            # attempt to raise Dual Wield.
            else:
                char.checkSkillRaise("Dual Wield",1,8)

        # The mob may not have a weapon equipped in primary or secondary, but
        # this is an offhand attack, so attempt to raise Dual Wield.
        else:
            char.checkSkillRaise("Dual Wield",1,8)


## @brief Handles skill raise checks for a succesful defend.
#  @param mob (Mob) The Mob that succesfully defended.
#  @return None.
#  @todo TWS: Should this be part of a combat process?  What if a skill or spell
#        needs to directly invoke an attack.
def SuccessfulDefense(mob):

    # Attempt to raise Tactics Defense.
    mob.character.checkSkillRaise("Tactics Defense",1,5)


## @brief Handle procs caused by attack, either melee triggered or poisons.
#  @param attacker (Mob) The attacking Mob.
#  @param defender (Mob) The defending Mob.
#  @param weapon (ItemInstance) The weapon used in the attack, if any..
#  @param additionalProcs (ItemSpell List) Additional procs that may trigger.
#  @return None.
#  @todo TWS: RPG_ITEM_TRIGGER_MELEE should probably be renamed to
#        RPG_ITEM_TRIGGER_ATTACK since ranged combat may use it.
def doAttackProcs(attacker, defender, weapon=None, additionalProcs=None):

    # If there is no attacker, then return early.
    if not attacker:
        return

    # List that will store all possible procs.
    spellProcs = []

    # If a weapon is provided, then add the weapon procs to the proc list.
    if weapon:

        # If the weapon has no penalty, then add the weapon's spells to the proc
        # list.
        if not weapon.penalty:
            spellProcs.extend(weapon.spells)

        # Add the weapon's additional procs (poison and spell enchantments)
        # regardless of the penalty.
        spellProcs.extend(weapon.procs.keys())

    # If a list of additional procs has been provided, then add them to the proc
    # list.
    if additionalProcs:
        spellProcs.extend(additionalProcs)

    # Add procs from the attacker's item sets, item set procs ged added
    #  to itemSetSpells when the set activates.
    spellProcs.extend(attacker.itemSetSpells.get(RPG_ITEM_TRIGGER_MELEE, []))

    # Flag used to indicate if volatile procs on weapon need refresh.
    refreshProcs = False

    # Dexterity may increase the proc frequency.  The higher the
    # dexterity, the higher the chance to proc.

    # Calculate a dex modifier based on the attacker's dexterity.
    # Clamp any bonus at a dexterity of 7500.
    dexMod = float(min(attacker.dex,7500)) / 750.0 - 10.0
    dexMod = 0.75 + dexMod * dexMod / 400.0

    # Iterate through all the gathered spell procs, attempting to trigger each.
    for proc in spellProcs:

        # Only melee and poison proc types trigger on attack.  If the proc's
        # trigger is either melee or poison, then it may trigger.
        if proc.trigger == RPG_ITEM_TRIGGER_MELEE or proc.trigger == RPG_ITEM_TRIGGER_POISON:

            # Apply the dexterity modifier to the proc's frequency.
            modFreq = int(round(dexMod * proc.frequency))

            # Trigger the proc if any of the following conditions are true:
            # - The proc is set to always trigger based on modified frequency.
            # - Generate a random number to see if the proc triggered.  The
            #   proc has a 1 out of modified frequency + 1 chance to proc, and 0
            #   indicates success.
            if modFreq <= 1 or not randint(0,modFreq):

                # Make a local handle to the proc's SpellProto.
                proto = proc.spellProto

                # Get a valid target for the proc based on the SpellProto.
                tgt = defender
                if proto.target == RPG_TARGET_SELF:
                    tgt = attacker
                elif proto.target == RPG_TARGET_PARTY:
                    tgt = attacker
                elif proto.target == RPG_TARGET_ALLIANCE:
                    tgt = attacker
                elif proto.target == RPG_TARGET_PET:
                    tgt = attacker.pet

                # If a valid proc target was found, then trigger the proc.
                if tgt:

                    # Poison type procs on weapons are limited in the amount of
                    # times they may be triggered.  Therefore, if the trigger
                    # is a poison and there i weapon, then decrease the amount
                    # of remaining times the proc may
                    if proc.trigger == RPG_ITEM_TRIGGER_POISON and weapon:

                        # Decrement the amount of times the proc may trigger.
                        weapon.procs[proc][0] -= 1

                        # If the proc may not trigger anymore times, then remove
                        # it  from the weapon.
                        if weapon.procs[proc][0] <= 0:

                            # Remove the proc from the weapon.
                            del weapon.procs[proc]

                            # If the attacking mob was a Player or a Player's pet,
                            #  then inform the Player that the proc has faded and
                            #  flag the weapon to be refreshed.
                            if attacker.player or (attacker.master and attacker.master.player):

                                # Inform the Player.
                                if attacker.player:
                                    player = attacker.player
                                else:
                                    player = attacker.master.player
                                player.sendGameText(RPG_MSG_GAME_SPELLEND,"The <a:Spell%s>%s</a> on %s's <a:Item%s>%s</a> has worn off.\\n"%(GetTWikiName(proto.name),proto.name,attacker.name,GetTWikiName(weapon.itemProto.name),weapon.name))

                                # Set a flag to indicate the ItemInfo needs
                                #  refreshed.
                                refreshProcs = True

                    # Trigger the proc by spawning the Spell.
                    SpawnSpell(proto,attacker,tgt,tgt.simObject.position,1.0,proc=True)


    # If there were volatile procs used or expired, then the weapon's ItemInfo
    # needs refreshed so observing clients see the updates.
    if refreshProcs:

        # If there was a weapon, then its ItemInfo needs refreshed.
        if weapon:

            # Refresh ItemInfo so observing clients see the new stack count.
            weapon.itemInfo.refreshProcs()



## @brief CombatProcess is a Process that encapsulates comabt rules,
#         calculations, and incremental processing.
#  @todo TWS: Level spread is calculated a lot, as well as other values.  Review
#        which calculations can be done once, stored, and then retreived.
class CombatProcess(Process):

    ## @brief Initialize class.
    #  @param self (CombatProcess) The object pointer.
    #  @param src (Mob) The attacking Mob.
    #  @param dst (Mob) The defending Mob.
    def __init__(self, src, dst):
        
        # Delegate some initialization to parent class.
        Process.__init__(self,src,dst)

        ## @brief (String) The Process type.
        self.type = "Combat"

        ## @brief (RPG_DMG_TYPE) The type of damage used in an attack.
        self.dmgType = 0

        ## @brief (Mob) The Mob attacking the defending Mob.
        self.attacker = src

        ## @brief (Mob) The Mob being attacked and defending.
        self.defender = dst

        ## @brief (Integer) Timer value indicating how much longer the attacker
        #         must wait to attempt to perform a primary attack.
        src.primaryAttackTimer = 0

        ## @brief (Integer) Timer value indicating how much longer the attacker
        #         must wait to attempt to perform a secondary attack.
        src.secondaryAttackTimer = 0


    ## @brief Gets the base damage for the attacker's primary attack.
    #  @param self (CombatProcess) The object pointer.
    #  @return (Float) The base damage for the attacker's primary attack.
    def getPrimaryDamage(self):

        # Get a damamge based on the attacker's level.
        dmg = self.attacker.level*3+10

        # Calculate the damage modifier.
        ratio = float(self.damage)/100.0

        # Increase the damage modifier if the skill being used by the attack is
        # two-handed.
        if "2H" in self.skill:
            ratio+=.66

        # Increase the damage based on the attacker's presence.
        dmg+=self.attacker.pre/3

        # Return a calculation based on the damage and the modifier.
        return dmg*ratio+dmg*ratio


    ## @brief Gets the base damage for the attacker's secondary attack.
    #  @param self (CombatProcess) The object pointer.
    #  @return (Float) The base damage for the attacker's secondary attack.
    def getSecondaryDamage(self):

        # Get a damamge based on the attacker's level.
        dmg = self.attacker.level*2+10

        # Calculate the damage modifier.
        ratio = float(self.damage)/100.0

        # Increase the damage modifier if the skill being used by the attack is
        # two-handed.
        if "2H" in self.skill:
            ratio+=.66

        # Increase the damage based on the attacker's presence.
        dmg+=self.attacker.pre/5

        # Return a calculation based on the damage and the modifier.
        return dmg*ratio+dmg*ratio


    ## @brief Gets the delay for the attacker's primary attack.
    #  @details CombatProcess counts down the primary attack timer 3 per tick,
    #          with 2 ticks occuring a second.
    #  @param self (CombatProcess) The object pointer.
    #  @return (Integer) The delay for the attacker's primary attack.
    #  @todo TWS: Optimize some weapon rate lookups.  A dictionary could
    #        probably be used.
    def getPrimaryAttackRate(self):

        # Make a local handle to the attacking Mob.
        mob = self.attacker

        # Get the base primary attack rate for the Mob.
        base = float(mob.primaryAttackRate)

        # Set the primary attack rate to a default of 16.
        wpnRate = 16.0

        # Get handles to items, if any, in the primary and secondary slots.
        pweapon = mob.worn.get(RPG_SLOT_PRIMARY)
        sweapon = mob.worn.get(RPG_SLOT_SECONDARY)

        # Check for fist advancements if the mob is a Player and any of the
        # following conditions are true:
        # - The mob has no primary weapon equipped.
        # - The equipped primary weapon is not associated with a skill.
        # - The equipped primary weapon is associated with the Fists skill.
        if mob.player and (not pweapon or not pweapon.skill or "Fists" == pweapon.skill):

            # Get the monk fist advancement value.
            monkfists = mob.advancements.get("monkFists",0)

            # If there is a monk fist advancement, then set the primary attack
            # rate based on the monk fist advancement.
            if monkfists:
                if monkfists == 1:
                    wpnRate = 14
                elif monkfists == 2:
                    wpnRate = 13
                elif monkfists == 3:
                    wpnRate = 12
                else:
                    wpnRate = 10
        
        # Otherwise set monkfists to zero, so we know later on that
        #  we still have to acquire the weapon rate.
        else:
            monkfists = 0

        # Slow is used to increase the primary attack delay.
        slow = 0

        # If there is a primary and secondary weapon, then the attacker may be
        # power wielding.
        if pweapon and sweapon:

            # Get the power wield advancement value.
            improve = mob.advancements.get("powerWield",0.0)
            
            # No speed penalty for 1h-2h and 2h-2h combinations with maximum
            #  power wield advancement.
            if improve < 1.0:

                # Add a 15% slow for a two-handed weapon equipped in primary or
                # secondary slots.
                if '2H' in pweapon.skill:
                    slow += .15
                if '2H' in sweapon.skill:
                    slow += .15

                # If the attacker is power wielding, then reduce the slow based on
                # power wield advancements.
                if slow == .3:

                    # If there is a power wield advancement, then modify the slow value.
                    if improve:

                        # Decrease the slow value.
                        slow *= 1.0 - improve

        # If there is an item in the primary slot, then set the primary attack
        #  rate based on the weapon's weapon rate.
        # Skip this step if we got a weapon rate assigned from monk fists.
        if pweapon and not monkfists:
            wpnRate = float(pweapon.wpnRate)

        # Increase the base primary attack rate based on the weapon rate.
        base += wpnRate

        # Calculate the total haste.  Haste is equal to the sum of a mob's item
        # haste, innate haste, and effect haste, minus the mob's slow and the
        # slow from two-handed weapons.
        haste = mob.itemHaste + mob.innateHaste + float(mob.effectHaste[1])
        haste -= mob.slow
        haste -= slow

        # If the attacker is out of stamina, reduce the haste value.
        if not mob.stamina:
            haste -= .2

        # Modify the primary attack rate based on the haste.
        # Check for less than zero to steer the direction floor
        #  will take.
        if haste < 0:
            base += floor(base * -haste)
        else:
            base -= floor(base * haste)

        # Increase the hasted primary attack rate by a constant value.
        base += 4

        # If the primary attack rate is below 8, then clamp the lowest possible
        # primary attack rate to be at least 8.
        if base < 8:
            base = 8

        # Return the primary attack rate.
        return ceil(base)


    ## @brief Gets the delay for the attacker's secondary attack.
    #  @details CombatProcess counts down the secondary attack timer 3 per tick,
    #          with 2 ticks occuring a second.
    #  @param self (CombatProcess) The object pointer.
    #  @return (Integer) The delay for the attacker's secondary attack.
    #  @todo TWS: Optimize some weapon rate lookups.  A dictionary could
    #        probably be used.
    def getSecondaryAttackRate(self):

        # Make a local handle to the attacking Mob.
        mob = self.attacker

        # Get the base secondary attack rate for the Mob.
        base = float(mob.secondaryAttackRate)

        # Set the secondary attack rate to a default of 20.
        wpnRate = 20.0

        # Get handles to items, if any, in the primary and secondary slots.
        pweapon = mob.worn.get(RPG_SLOT_PRIMARY)
        sweapon = mob.worn.get(RPG_SLOT_SECONDARY)

        # Check for fist advancements if the mob is a Player and any of the
        # following conditions are true:
        # - The mob has no secondary weapon equipped.
        # - The equipped secondary weapon is not associated with a skill.
        # - The equipped secondary weapon is assciated with the Fists skill.
        if (not sweapon or not sweapon.skill or "Fists" == sweapon.skill) and mob.player:

            # Get the monk fist advancement value.
            monkfists = mob.advancements.get("monkFists",0.0)

            # If there is a monk fist advancement, then set the secondary attack
            # rate based on the monk fist advancement.
            if monkfists:
                if monkfists == 1:
                    wpnRate = 14
                elif monkfists == 2:
                    wpnRate = 13
                elif monkfists == 3:
                    wpnRate = 12
                else:
                    wpnRate = 10
        
        # Otherwise set monkfists to zero, so we know later on that
        #  we still have to acquire the weapon rate.
        else:
            monkfists = 0

        # Slow is used to increase the secondary attack delay.
        slow = 0

        # If there is a primary and secondary weapon, then the attacker may be
        # power wielding.
        if pweapon and sweapon:

            # Get the power wield advancement value.
            improve = mob.advancements.get("powerWield",0.0)
            
            # No speed penalty for 1h-2h and 2h-2h combinations with maximum
            #  power wield advancement.
            if improve < 1.0:

                # Add a 15% slow for a two-handed weapon equipped in primary or
                # secondary slots.
                if '2H' in pweapon.skill:
                    slow += .15
                if '2H' in sweapon.skill:
                    slow += .15

                # If the attacker is power wielding, then reduce the slow based on
                # power wield advancements.
                if slow == .3:

                    # If there is a power wield advancement, then modify the slow value.
                    if improve:

                        # Decrease the slow value.
                        slow *= 1.0 - improve

        # If there is an item in the secondary slot, then set the secondary attack
        #  rate based on the weapon's weapon rate.
        # Skip this step if we got a weapon rate assigned from monk fists.
        if sweapon and not monkfists:
            wpnRate = float(sweapon.wpnRate)

        # Increase the base secondary attack rate based on the weapon rate.
        base += wpnRate

        # Calculate the total haste.  Haste is equal to the sum of a mob's item
        # haste, innate haste, and effect haste, minus the mob's slow and the
        # slow from two-handed weapons.
        haste = mob.itemHaste + mob.innateHaste + float(mob.effectHaste[1])
        haste -= mob.slow
        haste -= slow

        # If the attacker is out of stamina, reduce the haste value.
        if not mob.stamina:
            haste -= .2

        # Modify the secondary attack rate based on the haste.
        # Check for less than zero to steer the direction floor
        #  will take.
        if haste < 0:
            base += floor(base * -haste)
        else:
            base -= floor(base * haste)

        # Increase the hasted secondary attack rate by a constant value.
        base += 6

        # If the secondary attack rate is beow 11, then clamp the lowest
        # possible secondary attack rate to be at least 11.
        if base < 11:
            base = 11

        # Return the secondary attack rate.
        return ceil(base)


    ## @brief Cancels the CombatProcess and clears the attacker.
    #  @param self (CombatProcess) The object pointer.
    #  @return None.
    #  @deprecated TWS: This looks as if it is never used.  Does it need to be
    #             removed?  It just looks like it is wasting some time with
    #             unnecessary function resolution.
    def clearSrc(self):

        # Cancel this CombatProcess.
        self.cancel()

        # Clear the process source.
        ## @brief (Mob) The source (attacker) of the CombatProcess.
        self.src = None


    ## @brief Cancels the CombatProcess and clears the defender.
    #  @param self (CombatProcess) The object pointer.
    #  @return None.
    #  @deprecated TWS: This looks as if it is never used.  Does it need to be
    #             removed?  It just looks like it is wasting some time with
    #             unnecessary function resolution.
    def clearDst(self):

        # Cancel this CombatProcess.
        self.cancel()

        # Clear the process source.
        ## @brief (Mob) The destination (defender) of the CombatProcess.
        self.dst = None


    ## @brief Begins the CombatProcess, attaching the process to both the
    #         attacker and defender.
    #  @param self (CombatProcess) The object pointer.
    #  @return None.
    #  @deprecated TWS: Why overwrite default impementation?  Does this need to
    #             be removed?  It just looks like it is wasting some time with
    #             unnecessary function resolution.
    def begin(self):

        # Begin this CombatProcess.  This will attach the process to both the
        # attacker and defender.
        Process.begin(self)


    ## @brief Cancels the CombatProcess, dettaching the process from both the
    #         attacker and defender.
    #  @param self (CombatProcess) The object pointer.
    #  @return None.
    #  @todo TWS: Maybe this sould set the attacker's attack to false.  This
    #        would allow tick to raise StopIteration, and then the mob would
    #        end the process.  This could save some possible iterations.  Mob
    #        info woud also need refreshed.
    #  @deprecated TWS: Why overwrite default impementation?  Does this need to
    #             be removed?  It just looks like it is wasting some time with
    #             unnecessary function resolution.
    def end(self):

        # End this CombatProcess.  This will dettach the process from both the
        # attacker and defender.
        Process.end(self)


    ## @brief Incremental processing of combat.  The attacker's timers are
    #         counted down and an attack may occur.
    #  @details Tick is iterated in the defending Mob's tick.  Thus, the
    #          CombatProcess is ticked 2 times a second.
    #  @param self (CombatProcess) The object pointer.
    #  @return (Generator) Yields True while combat may continue.  Otherwise,
    #          StopIteration exception is raised.
    #  @todo TWS: Optimize: Many variables can have local references created
    #        outside of the while loop.  Move as much as possible out so that
    #        dot resolution does not need to occur as often.
    #  @todo TWS: Consider moving range inhibitation checks inside of the mob
    #        condition check.  This prevents having to do calculations while
    #        feared, stunned, or asleep.
    #  @todo TWS: Combat inhibitation messages need reworked.  Some wasteful
    #        processing occurs, and some of this may be able to be pushed onto
    #        the client.
    #  @todo TWS: The weapon range adjustment of x / 5.0 should realy only occur
    #        once.  This needs to be centralized during ItemInstance
    #        instantiation of when weapons are equipped on the mob.
    #  @todo TWS: Optimize, if the range between attacker and defender is below
    #        zero, then skip checking weapon ranges.
    #  @todo TWS: Weapon slots are pulled a few times.  Should only have to do
    #        it once.
    def tick(self):

        # Make a local handle to this CombatProcess' source Mob and destination
        # Mob.
        src = self.src
        dst = self.dst

        # Set a flag to indicate if the source may get offensive skill ups
        # during the combat.  Skill ups can only occur if the source is a
        # Player's Character and the destination is not associated with a
        # Player.
        attackerSkillup = src.character and not dst.player and not (dst.master and dst.master.player)

        # Combat may continue only under the following conditions:
        # - The source Mob is still targeting the destination Mob.
        # - The destination Mob has health.
        while src.target == dst and dst.health:

            # For NPC AI, if the destination feigns death, then combat will end.
            # Thus, if the source is not associated with a Player and the
            # destination has feigned death, then clear the source's target and
            # exit the loop.
            if not src.player and dst.feignDeath:

                # Clear the source's target.
                src.zone.setTarget(src,None)

                # Exit the loop.  This will cause a StopIteration exception to
                # be raised.
                break

            # Inhibit flag indicates if the combat round is prevented due to
            # visibility or range.
            inhibit = False

            # Make a local handle to this CombatProcess' attacking Mob,
            # defending Mob, and the attacker's Player.
            attacker = self.attacker
            defender = self.defender
            player = attacker.player

            # If the attacker is a Player, then check if the the combat round
            # needs to be prevented.
            if player:

                # If the attacker is not allowed to harm the defender, then
                # turn off the attacker's attack.
                if not AllowHarmful(attacker, defender):

                    # Turn off the attacker's attack.  This will cause this
                    # CombatProcess to be canceled.
                    # TWS: Consider reworking the flow to just return, raising a
                    # StopIteration and have the mob handle it like it handles
                    # all of its processes.  If the tick is called, then the
                    # process has already been globally pushed, so it is not in
                    # a pending queue.
                    attacker.attackOff()

                    # Yield True.  The next tick iteration will return
                    # immediately after this line of code.
                    yield True

                    # Continue to next iteration of the loop.  This will recheck
                    # combat conditions.
                    continue

                # If the attacker is casting, then the combat round may be
                # prevented.
                if attacker.casting:

                    # If the spell being casted is not singing and the attacker
                    # does not have combat casting, then prevent this combat
                    # round.
                    if attacker.casting.spellProto.skillname != "Singing" and not attacker.combatCasting:

                        # Yield True.  The next tick iteration will return
                        # immediately after this line of code.
                        yield True

                        # Continue to next iteration of the loop.  This will
                        # recheck combat conditions.
                        continue

            # Flags indicating if primary or secondary attack is inhibited.
            inhibitPrimary = False
            inhibitSecondary = False

            # If either attack timer would be satisfied this combat round, then
            # check if the attack will be inhibited.
            if src.primaryAttackTimer <= 3 or src.secondaryAttackTimer <= 3:

                # If the defender is not in the attacker's can see list, then
                # there is an something obstructing the view.  This check is
                # based on simulation data, and does not check visibility.
                if defender.simObject.id not in attacker.simObject.canSee:

                    # Increase the attacker's combat inhibited count.
                    # TWS: This looks as if it could just be a true or false.
                    # It affects NPC AI skill usage, but was previous part of
                    # warping code.
                    attacker.combatInhibited += 3

                    # If the attacker is a player and the player's cannot see
                    # message timer has been satisfied, then inform the Player
                    # This throttling prevents spamming the player with the
                    # message.
                    # TWS: Previous comments mention that this should be done on
                    # client.
                    if player and not player.msgCombatCantSee:

                        # Set the Player's cannot see message timer so that the
                        # message is not sent again for 10 seconds.  The
                        # Player's tick counts down the cannot see timer 1 per
                        # tick, with 2 ticks occuring a second.
                        player.msgCombatCantSee = 20

                        # Inform the Player.
                        player.sendGameText(RPG_MSG_GAME_DENIED,"%s's adversary is obstructed!\\n"%attacker.character.name)

                    # Set the flag to indicate combat was inhibited.
                    inhibit = True
                
                # If the attacker is not facing the defender, then combat is
                #  inhibited. (wmrojer)
                else:
                    if not attacker.isFacing(defender):
                        if player and not player.msgCombatNotFacing:
                            
                            # Set the Player's not facing message timer so
                            #  that the message is not sent again for 10 seconds.
                            # The Player's tick counts down the not facing timer 1
                            #  per tick, with 2 ticks occuring a second.
                            player.msgCombatNotFacing = 20
                            
                            # Inform the Player.
                            player.sendGameText(RPG_MSG_GAME_DENIED, \
                                "%s is facing the wrong way!\\n"% \
                                attacker.character.name)
                        
                        inhibit = True


                # Get the minimum range between the attacker and defender.
                crange = GetRangeMin(attacker,defender)

                # wpnRange will hold the highest weapon range.
                wpnRange = 0

                # The adjusted ranges for primary and secondary.
                primaryRangeAdjusted = 0
                secondaryRangeAdjusted = 0

                # Get handles to items, if any, in the primary and secondary
                # slots.
                pweapon = attacker.worn.get(RPG_SLOT_PRIMARY)
                sweapon = attacker.worn.get(RPG_SLOT_SECONDARY)

                # If there is a primary weapon and the primary weapon's range is
                # greater than the currennt highest weapon range, then calculate
                # the adjusted primary weapon range and update the highest
                # weapon range.
                # TWS: Is the greater than check required?  wpnRange is always
                # zero at this point.
                if pweapon and pweapon.wpnRange > wpnRange:

                    # Calculate the adjusted primary weapon range.
                    primaryRangeAdjusted = pweapon.wpnRange / 5.0

                    # Set the new highest weapon range.
                    wpnRange = primaryRangeAdjusted

                # If there is a secondary weapon equipped, then calculate its
                # adjust range and check if primary or secondary is inhibited.
                if sweapon:

                    # Calculate the adjusted secondary weapon range.
                    secondaryRangeAdjusted = sweapon.wpnRange / 5.0

                    # If the adjusted secondary weapon range is greater than
                    # the current highest weapon range, then update the highest
                    # weapon range and see if primary is inhibited.
                    if secondaryRangeAdjusted > wpnRange:

                        # Set the new highest weapon range.
                        wpnRange = secondaryRangeAdjusted

                        # If there is a primary weapon and the distance between
                        # the attacker and defender is greater than the adjusted
                        # primary weapon range, then the primary attack is
                        # inhibited.
                        if pweapon and crange > primaryRangeAdjusted:

                            # Flag primary attack as inhibited.
                            inhibitPrimary = True

                    # Otherwise, if the distance between the attacker and
                    # defender is greater than the adjusted secondary weapon
                    # range, then the secondary attack is inhibited.
                    elif crange > secondaryRangeAdjusted:

                        # Flag secondary attack as inhibited.
                        inhibitSecondary = True


                # If the distance between the attacker and defender is larger
                # then the highest equipped weapon range, then combat is
                # inhibited.
                if crange > wpnRange:

                    # Increase the attacker's combat inhibited count.
                    # TWS: This looks as if it could just be a true or false.
                    # It affects NPC AI skill usage, but was previous part of
                    # warping code.
                    attacker.combatInhibited += 3

                    # If the attacker is a player and the player's not close
                    # enough message timer has been satisfied, then inform the
                    # Player.  This throttling prevents spamming the player with
                    # the message.
                    # TWS: Previous comments mention that this should be done on
                    # client.
                    if player and not player.msgCombatNotCloseEnough:

                        # Set the Player's not close enough message timer so
                        # that the message is not sent again for 10 seconds.
                        # The Player's tick counts down the cannot see timer 1
                        # per tick, with 2 ticks occuring a second.
                        player.msgCombatNotCloseEnough = 20

                        # Inform the Player.
                        player.sendGameText(RPG_MSG_GAME_DENIED,"%s's adversary is out of melee range!\\n"%attacker.character.name)

                    # Set the flag to indicate combat was inhibited.
                    inhibit = True

                # If the attacker is not facing the defender, then combat is inhibited. (wmrojer)
                if not inhibit:
                    if not attacker.isFacing(defender):
                        if player and not player.msgCombatNotFacing:

                            # Set the Player's not facing message timer so
                            # that the message is not sent again for 10 seconds.
                            # The Player's tick counts down the not facing timer 1
                            # per tick, with 2 ticks occuring a second.
                            player.msgCombatNotFacing = 20

                            # Inform the Player.
                            player.sendGameText(RPG_MSG_GAME_DENIED,"%s is facing the wrong way!\\n"%attacker.character.name)
                        inhibit = True


            # Attacks will be attempted only under the following conditions:
            # - The source Mob is not sleeping.
            # - The source Mob is not stunned.
            # - The source Mob is not feared.
            # - Combat is not flagged as inhibited.
            if src.sleep <= 0 and src.stun <= 0 and not src.isFeared and not inhibit:

                # If the primary attack is not inhibited, then countdown primary
                # attack timer.
                if not inhibitPrimary:

                    # Countdown the primary attack timer.
                    src.primaryAttackTimer -= 3

                    # If the primary attacker time has been satisfied, then reset
                    # the timer and attempt an attack.
                    if src.primaryAttackTimer <= 0:
    
                        # Increase the primary attack timer by the primary
                        # attack rate.
                        src.primaryAttackTimer += self.getPrimaryAttackRate()

                        # Count of attacks to attempt.
                        attacks = 1

                        # Get the attacker's Double Attack skill level.
                        da = src.skillLevels.get('Double Attack',0)

                        # If the attacker has a Double Attack skill, then check
                        # if the skill is succesful.
                        if da:

                            # Calculate the chance of a double attack based on
                            # the attacker's skill and the defender's level.
                            da = 1000 - da
                            da /= 40
                            da += dst.plevel / 10

                            # If the chance for a double attack is less than 10,
                            # then clamp the chance for a double attack to be at
                            # least 10.  This sets the best double attack chance
                            # to be 1 out of 11.
                            if da < 10:
                                da = 10

                            # Generate a random number to see if the double
                            # attack was succesful.  The double attack has a 1
                            # out of da + 1 chance to occur, and 0 indicates
                            # success.
                            if not randint(0,int(da)):

                                # Increase the number of attacks to attempt.
                                attacks = 2

                                # If the attacker can skill up, then attempt
                                # to increase the attacker's Double Attack
                                # skill.
                                if attackerSkillup:
                                    src.character.checkSkillRaise("Double Attack",2,2)

                        # Get the attacker's Triple Attack skill level.
                        ta = src.skillLevels.get('Triple Attack',0)

                        # If the attacker has a Triple Attack skill, then check
                        # if the skill is succesful.
                        if ta:

                            # Calculate the chance for a triple attack based on
                            # the attacker's skill and the defender's level.
                            ta = 1000 - ta
                            ta /= 15
                            ta += dst.plevel / 10

                            # If the chance for a triple attack is less than 10,
                            # then clamp the chance for a triple attack to be at
                            # least 10.  This sets the best triple attack chance
                            # to be 1 out of 11.
                            if ta < 10:
                                ta = 10

                            # Generate a random number to see if the triple
                            # attack was succesful.  The triple attack has a 1
                            # out of ta + 1 chance to occur, and 0 indicates
                            # success.
                            if not randint(0,int(ta)):

                                # Increase the number of attacks to attempt.
                                attacks = 3

                                # If the attacker can skill up, then attempt
                                # to increase the attacker's Tripe Attack skill.
                                if attackerSkillup:
                                    src.character.checkSkillRaise("Triple Attack",2,2)

                        # If Double Attack or Triple Attack was succesful, then
                        # inform the Player of the additional attacks.
                        if src.player:
                            if attacks == 2:
                                src.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s double attacks!\\n"%src.name)
                            elif attacks == 3:
                                src.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s triple attacks!\\n"%src.name)

                        # Set the default attack skill to be fist.
                        self.skill = "Fists"

                        # Set the default attack damage type to be
                        # RPG_DMG_PUMMEL.
                        self.dmgType = RPG_DMG_PUMMEL

                        # If the source is not a Player, then set the NPC's
                        # damage based on the primary level.  This makes higher
                        # level mobs hit harder.
                        if not src.player:

                            ## @brief (Float) The base damage for an attack.
                            self.damage = src.plevel/2

                        # Otherwise, set the base unarmed damage to be 4.
                        else:
                            self.damage = 4

                        # Get a handle to the item in the primary slot, if any.
                        ## @brief (ItemInstance) The item being used to perform
                        #         an attack.
                        self.weapon = src.worn.get(RPG_SLOT_PRIMARY, None)

                        # If there is a weapon, then update the attack based on
                        # the weapon.
                        if self.weapon:

                            # Set the attack damage type based on the weapon.
                            self.dmgType = self.weapon.dmgType

                            # Set the base damage based on the weapon.
                            self.damage = int(self.weapon.wpnDamage*15)

                            # If there is skill associated with the weapon, then
                            # set the attack skill based on the weapon.
                            if self.weapon.skill:

                                ## @brief (String) The name of the skill being
                                #         used by an attack.
                                self.skill = self.weapon.skill

                        # If the attack skill is Fist and the source is a
                        # Player, then check for monk fist advancements.
                        if self.skill == "Fists" and src.player:

                            # Get the monk fist advancement value.
                            monkfists = attacker.advancements.get("monkFists",0.0)

                            # If there is a monk fist advancement, then set the
                            # base damage based on the monk fist advancement.
                            if monkfists:
                                if monkfists == 1:
                                    self.damage=15*15
                                elif monkfists == 2:
                                    self.damage=20*15
                                elif monkfists == 3:
                                    self.damage=30*15
                                else:
                                    self.damage = 40*15

                        # Increase the base damage based on the attacker's
                        # skill level for the skill being used by the attack.
                        self.damage += int(src.skillLevels[self.skill]*1.5)

                        # Attempt to perform an attack and skill ups for each
                        # attack.
                        for a in xrange(0,attacks):

                            # Attempt to do an attack based on the primary
                            # damage from the primary hand.
                            dmg = self.doAttack(self.getPrimaryDamage(),False)

                            # If the attack was succesful (damage was done) and
                            # the attacker can skill up, then attempt to
                            # increase skills for the primary hand.
                            if dmg and attackerSkillup:
                                SuccessfulAttack(src)


                # If the secondary attack is not inhibited, then check attack
                # conditions.
                if not inhibitSecondary:

                    # Secondary attacks may occur if the attacker has trained
                    # the Power Wield or Dual Wield skills.  Double or Triple
                    # Attacks may not occur on a secondary attack.  Overall, the
                    # secondary base damage multipliers are less than the 
                    # primary.
    
                    # Get the attacker's Power Wield skill level.
                    powerWield = src.skillLevels.get("Power Wield", 0)
    
                    # If the attacker has a Dual Wield skill or Power Wield, 
                    # then a secondary may occur.
                    if src.skillLevels.has_key("Dual Wield") or powerWield:
    
                        # Flag indicating if the secondary attack will be
                        # skipped.
                        skip = False
    
                        # Get handles to items, if any, in the primary and
                        # secondary slots.
                        w = src.worn.get(RPG_SLOT_PRIMARY)
                        s = src.worn.get(RPG_SLOT_SECONDARY)
    
                        # Count of two-handed weapons equipped.
                        twohanded = 0
    
                        # Increase the count of two-handed weapons if the
                        # equipped items are two-handed weapons.
                        if w and "2H" in w.skill:
                            twohanded+=1
                        if s and "2H" in s.skill:
                            twohanded+=1
    
                        # The secondary attack is skiped if a two-handed weapon 
                        # is equipped and any of the following conditions are
                        # true:
                        # - There is no weapon equipped in primary.
                        # - There is no weapon equipped in secondary.
                        # - The attacker has no Power Wield skill.
                        # Note: This requires a weapon in secondary, so a
                        # two-handed weapon in primary and fist in secondary
                        # will cause the secondary attack to skip.
                        if twohanded and (not w or not s or not powerWield):
    
                            # Set a flag to indicate the secondary attack will
                            # be skipped.
                            skip = True
    
                        # If the attacker has a base secondary attack rate and
                        # the secondary attack is not flagged to be skipped,
                        # then count down the secondary attack timer.
                        if src.secondaryAttackRate > 0 and not skip:
    
                            # Count down the secondary attack timer.
                            src.secondaryAttackTimer -= 3
    
                            # If the secondary attack timer has been satisfied, then
                            # an attack may occur.
                            if src.secondaryAttackTimer <= 0:
                                
                                # Increase the secondary attack timer by the
                                # secondary attack rate.
                                src.secondaryAttackTimer += self.getSecondaryAttackRate()

                                # Set the default attack skill to be fist.
                                self.skill = "Fists"

                                # Set the default attack damage type to be
                                # RPG_DMG_PUMMEL.
                                self.dmgType = RPG_DMG_PUMMEL

                                # If the source is not a Player, then set the
                                # NPC's damage based on the primary level.  This
                                # makes higher level mobs hit harder.
                                if not src.player:
                                    self.damage = src.plevel/2

                                # Otherwise, set the base unarmed damage to be
                                # 4.
                                else:
                                    self.damage = 4

                                # Get a handle to the item in the secondary
                                # slot, if any.
                                self.weapon = src.worn.get(RPG_SLOT_SECONDARY, None)

                                # If there is a weapon, then update the attack
                                # based on the weapon.
                                if self.weapon:

                                    # Set the attack damage type based on the
                                    # weapon.
                                    self.dmgType = self.weapon.dmgType

                                    # Set the base damage based on the weapon.
                                    self.damage = int(self.weapon.wpnDamage*15)

                                    # If there is skill associated with the
                                    # weapon, then set the attack skill based on
                                    # the weapon.
                                    if self.weapon.skill:
                                        self.skill = self.weapon.skill

                                # If the attack skill is Fist and the source is
                                # a Player, then check for monk fist
                                # advancements.
                                if self.skill == "Fists" and src.player:

                                    # Get the monk fist advancement value.
                                    monkfists = attacker.advancements.get("monkFists",0.0)

                                    # If there is a monk fist advancement, then
                                    # set the  base damage based on the monk
                                    # fist advancement.
                                    if monkfists:
                                        if monkfists == 1:
                                            self.damage=15*10
                                        elif monkfists == 2:
                                            self.damage=20*10
                                        elif monkfists == 3:
                                            self.damage=30*10
                                        else:
                                            self.damage = 40*10

                                # Increase the base damage based on the
                                # attacker's skill level for the skill being
                                # used by the attack.
                                self.damage += int(src.skillLevels[self.skill])

                                # Attempt to do an attack based on the secondary
                                # damage from the offhand.
                                dmg = self.doAttack(self.getSecondaryDamage(),True)

                                # If the attack was succesful (damage was done)
                                # and attacker can skill up, then attempt to
                                # increase skills for the offhand.
                                if dmg and attackerSkillup:
                                    SuccessfulAttack(src,True)


            # Yield True.  The next tick iteration will return immediately after
            # this line of code, which is the last statement in the while loop.
            # Thus, the next iteration will start with checking the while loop's
            # conditions.
            yield True


    ## @brief Calculates a random damage amount based on the max damage.
    #  @param self (CombatProcess) The object pointer.
    #  @param MAXDMG (Float) The maximum damage possible.
    #  @return (Integer) Returns a random damage amount at or below the max
    #          damage.
    #  @todo TWS: Zone damage modifiers should be stored in the World database,
    #        and added to the combat process during initialization.
    #  @todo TWS: NPC level based damage multipliers and clamps should be
    #        calculated at initilization.  There is no need to redo if checks
    #        on each damage calculation.
    #  @todo TWS: Some math simplification and conditions to clean up
    #        readability and speed.
    def calcDamageActual(self, MAXDMG):

        # Make a local handle to this CombatProcess' attacking Mob and
        # defending Mob.
        attacker = self.attacker
        defender = self.defender

        # Get the level spread.  1 indicates equal levels; less than 1 indicates
        # the attacker has a higher level than defender; greater than 1
        # indicates the defender has a higher level than attacker.
        spread = GetLevelSpread(attacker, defender)

        # Random chance for adding additive damage to the actual damage.
        R = randint(0,99)

        # If there is a weapon advance mod, then increase the maximum amount of
        # damage based on the mod.
        if self.wpnAdvanceMod:
            MAXDMG+=MAXDMG*self.wpnAdvanceMod

        # Set the base actual damage to be 33% of the max damage.
        d = MAXDMG / 3.0

        # Set the additive damage to be 33% of the max damage.
        additive = MAXDMG / 3.0

        # If the random chance for adding the additive damage was less than or
        # equal to 10, then set the additive to 0.  This sets it so that chance
        # for an additive damage of 33% of the max damage is added 89% of the
        # time.
        if R <= 10:
            additive = 0;

        # If the base damage is less than 1, then clamp the base damage to be at
        # least 1.
        if d < 1.0:
            d = 1.0;

        # Get the possible range for damage.  If the attacker is a higher level
        # than the defender, then the spread is low.  Thus, the damage range
        # will be higher.  If the defender is a higher level than the attacker,
        # then the spread is high.  Thus, the damage range will be lower.
        R = ceil(d/spread)

        # If the range is zero, then clamp the range to be at least 1.
        if not R:
            R = 1

        # Set the actual damage to be a randomly generated number between 1 and
        # the range.
        damage = randint(1,R)

        # Increase the actual damage by the additive.
        damage = damage + additive

        # If the random actual damage is above the max damage, then clamp the
        # actual damage to not go above the max damage.
        if damage > MAXDMG:
            damage = MAXDMG

        # If the attacker is an NPC, then modify the actual damage based on
        # level.
        if not attacker.player:

            # If the mob is below level 30, then reduce the actual damage by 35%
            # and clamp the actual damage to be at least the mob's primary
            #level.
            if attacker.plevel < 30:

                # Reduce the actual damage by 35%.
                damage = int(ceil(damage*.65))

                # If the actual damage is less than the attacker's level, then
                # clamp the actual damage to be at least the attacker's primary
                # level.
                if damage < attacker.plevel:
                    damage = attacker.plevel

            # Otherwise, if the mob is below level 60, then clamp the actual
            # damage to be at least 5 times the attacker's level.
            elif attacker.plevel < 60:

                # If the actual damage is less than 5 times the attacker's
                # level, then clamp the actual damage to be at least 5 times
                # the attacker's primary level.
                if damage < attacker.plevel*5:
                    damage = attacker.plevel*5

            # Otherwise, if the mob is below level 80, then clamp the actual
            # damage to be at least 10 times the attacker's level.
            elif attacker.plevel < 80:

                # If the actual damage is less than 10 times the attacker's
                # level, then clamp the actual damage to be at least 10 times
                # the attacker's primary level.
                if damage < attacker.plevel*10:
                    damage = attacker.plevel*10

            # Otherwise, if the mob is below level 90, then clamp the actual
            # damage to be at least 20 times the attacker's level.
            elif attacker.plevel < 90:

                # If the actual damage is less than 20 times the attacker's
                # level, then clamp the actual damage to be at least 20 times
                # the attacker's primary level.
                if damage < attacker.plevel*20:
                    damage = attacker.plevel*20

            # Otherwise, clamp the actual damage to be at least 30 times the
            # attacker's level.  This will occur for mobs greater than or equal
            # to level 90.
            else:

                # If the actual damage is less than 30 times the attacker's
                # level, then clamp the actual damage to be at least 30 times
                # the attacker's primary level.
                if damage < attacker.plevel*30:
                    damage = attacker.plevel*30


            # If the attacker is in the Burning Field ZoneInstance, then the
            # damage may have a multipier applied.
            if attacker.zone.zone.name == 'field':
                
                # Modify the damage based on the attacker's damage mod.
                damage = int(ceil(damage*attacker.damageMod))

            # If the attacker is a pet, then reduce the actual damage by 50%.
            if attacker.master:

                # Reduce actual damage by 50%.
                damage*=.5

                # If the actual damage is less than 10, then clamp the actual
                # pet damage to be at least 10.
                if damage < 10:
                    damage = 10

        # Return the actual damage.
        return int(damage)


    ## @brief Calculates the adjusted max damage based on the base damage,
    #         attacker's offense, defender's defense, and levels.
    #  @param self (CombatProcess) The object pointer.
    #  @param damage (Float) The base damage for which the adjusted max is
    #                calculated.
    #  @return (Float) Returns the adjusted max damage based on the base
    #          damage, attacker's offense, defender's defense, and levels.
    #  @todo TWS: Algebra simplification on the spread.
    #  @todo TWS: MANY way overly complication calculations.  This should be
    #        simplier.
    #  @todo TWS: Armor rating is almost completely useless at lower levels. It
    #        only begins to become important at higher levels.  Should this
    #        be reviewed for changing so that armor is somewhat helpful at all
    #        levels.
    def calcDamageAdjustedMax(self, damage):

        # Make a local handle to this CombatProcess' attacking Mob and
        # defending Mob.
        attacker = self.attacker
        defender = self.defender

        # If the attacker is a Player, then use the skill being used for the
        # attack as the attacker's level.
        if attacker.player:

            # Get and modify the attacker's skill level for the skill being used
            # by the attack.  The attack level should not exceed the max mob
            # level possible (100), so the skill level is divided by 1/100th
            # (10) of the max skill level (1000).
            plevel = attacker.skillLevels[self.skill]/10

            # If the attack level is less than 1, then camp the attack level to
            # be at least 1.
            if plevel < 1:
                plevel = 1

        # Otherwise, the attacker is an NPC.  Thus, use the attacker's level.
        else:
            plevel = attacker.plevel

        # Get the defenders level, the attackers level, and the defender's
        # defense.
        DFDLEVEL = defender.level
        ATTLEVEL = attacker.level
        DFDDEFENSE = defender.defense

        # If the defender level is above 100, then clamp it to never exceed 100.
        if DFDLEVEL > 100:
            DFDLEVEL = 100


        # Calculate a level spread based on the defender's level and the
        # attack level.  For PCs, the level being used is based on the
        # Character's skill for the attack.  1 indicates equal levels; less than
        # 1 indicates the attacker has a higher level than defender; greater
        # than 1 indicates the defender has a higher level than attacker.
        spread = defender.plevel - plevel
        if plevel < defender.plevel:
            spread = spread + ((defender.plevel - plevel) ** 2)
        LS = ((spread + 100.0) * 10.0) / 1000.0

        # Reduce the spread by half.
        R=LS*.5

        # Calculate the base adjusted max from the base damage and the level
        # spread.  If the attacker is a higher level than the defender, then the
        # spread is low.  Thus, the adjusted max damage will be higher.  If the
        # defender is a higher level than the attacker, then the spread is high.
        # Thus, the adjusted max damage will be lower.
        ADJUSTEDMAX = damage / R

        # Perform damage mitigation, reducing the adjusted max damage based on
        # the defender's defense and level.
        ADJUSTEDMAX = ADJUSTEDMAX - (DFDDEFENSE / 100) * (DFDLEVEL * 4 / 100)


        # Calculate an adjusted armor rating from the defender's armor level
        # and the level spread.  If the attacker is a higher level than the
        # defender, then the spread is low.  Thus, the armor rating will be
        # higher.  If the defender is a higher level than the attacker, then the
        # spread is high.  Thus, the armor rating will be lower.
        a = defender.armor/LS

        # If the adjusted armor rating is higher than the natural armor rating,
        # then clamp the adjusted armor rating to never exceed the natural
        # armor rating.
        # TWS: In essence, this clamp prevents any armor bonus if the spread
        # is below 1.  Maybe the spread can be checked before the adjusted
        # calculation.
        if a > defender.armor:
            a = defender.armor

        # Modify the adjusted armor rating baed on the defenders level.
        a*=(defender.plevel/100.0)
        a*=.5
        a = int(a)

        # Randomly reduce the armor rating 40% of the time by 66%, 40% of the
        # time by 50%, and do not modify it 20% of the time.
        rand = randint(0,9)
        if rand < 4:
            a = a/3
        elif rand <=7:
            a = a/2

        # If the adjusted armor rating is higher than the adjusted max damage,
        # then set the adjusted armor rating equal to the adjusted max damage.
        if a > ADJUSTEDMAX:
            a = ADJUSTEDMAX

        # Calculate a modifier based on the difference between the adjusted
        # max damage and the armor modifer.
        a = ADJUSTEDMAX-a

        # The adjusted max damage will be divided by armor rating modiifer.
        # If the armor rating modifier is zero, then set the armor rating
        # modifier to be at least 1 to prevent dividing by 0.
        if not a:
            a = 1

        # Perform damage mitigation, dividing the adjusted max damage by the
        # armor rating.  Limit the damage mitigation to never exceed 33%.
        # TWS: x/a ? x/b; x/a < x/b if a > b.  Thus, the if statement should
        # be ablel to use if a > 3:
        if ADJUSTEDMAX/a < ADJUSTEDMAX/3:
            ADJUSTEDMAX/=3
        else:
            ADJUSTEDMAX/=a

        # Increased the adjusted max damage by 33%.
        ADJUSTEDMAX*=1.3333

        # Modify the adjusted max damage based on the attack level and the
        # attacker's strength.  The higher the attack level, then the more the
        # attacker's strength will increase the adjusted max damage.
        s = 0
        d = 5.0-(plevel/20.0)
        if d < 2:
            d = 2
        s = (attacker.str/d)
        ADJUSTEDMAX+=s

        # If the adjusted max damage is less than 3.5 times the attack level,
        # then clamp the adjusted max damage to be at least 3.5 times the attack
        # level.
        if ADJUSTEDMAX < plevel*3.5:
            ADJUSTEDMAX =  plevel*3.5

        # Increase the adjusted max damage based on the attack level.
        ADJUSTEDMAX+=plevel*2

        # If the adjusted max damage is greater than half of the base damage,
        # then camp the adjusted max damage to be at least half of the base
        # damage.
        if ADJUSTEDMAX > damage/2:
            ADJUSTEDMAX = damage/2

        # If the adjusted max damage is less than 6, then clamp the adjusted max
        # damage to be at least 6.
        if ADJUSTEDMAX < 6:
            ADJUSTEDMAX = 6

        # If the adjusted max damage is greater than 6500, then clamp the
        # adjusted max damage to never exceed 6500.
        elif ADJUSTEDMAX > 6500:
            ADJUSTEDMAX = 6500

        # Return the adjusted max damage.
        return int(ADJUSTEDMAX)


    ## @brief Calculates the base hit percentage.
    #  @param self (CombatProcess) The object pointer.
    #  @param attoffense (Integer) The modified attacker's offense.
    #  @param defdefense (Integer) The modified defender's defendse.
    #  @return (Float) Returns the base hit percentage between 1 and 99.
    def calcBaseHitPercentage(self, attoffense, defdefense):

        # Make a local handle to this CombatProcess' attacking Mob and
        # defending Mob.
        attacker = self.attacker
        defender = self.defender

        # Get the level spread.  1 indicates equal levels; less than 1 indicates
        # the attacker has a higher level than defender; greater than 1
        # indicates the defender has a higher level than attacker.
        R = GetLevelSpread(attacker, defender)

        # Modify the spread.
        R*=.5

        # Modify the defense rating based on the level spread.  If the attacker
        # is a higher level than the defender, then the spread is low.  Thus,
        # the defense rating will be lower.  If the defender is a higher level
        # than the attacker, then the spread is high.  Thus, the defense rating
        # will be higher.
        d = defdefense * (R * R)

        # The adjusted attack rating will be divided by the adjusted defense
        # modifier.  If the adjusted defense modifier is zero, then set the
        # adjusted defense modifier to be at least 1 to prevent dividing by 0.
        if not d:
            d=1

        # Calculate the base hit percentage based on the adjusted attack rating
        # and the adjusted defense rating.
        base = (attoffense * 60) / d

        # If the base hit chance is greater than 99, then set the base hit
        # chance to never exceed 99.
        if base > 99:
            base = 99

        # Otherwise, if the base hit chance is less than 1, then set the base
        # hit chance to be at least 1.
        elif base < 1:
            base = 1

        # Calculate the minimum chance possible based on the attacker's level.
        # At level 100, the lowest chance is 25%
        lc = attacker.plevel/4

        # If the base hit chance is less than the minimum chance possible based
        # on the attacker's level, then set the base hit chance to be at least
        # the minimum chance possible based on the attacker's level.
        if base < lc:
            base = lc

        # Return the base hit chance.
        return base


    ## @brief Calculates the base hit percentage.
    #  @param self (CombatProcess) The object pointer.
    #  @param dmg (Float) Base damage for the attack.
    #  @param offhand (Boolean) Indicates if the attack is being performed from
    #                 the offhand.
    #  @return (Integer) Returns the amount of non-mitigated damage inflicted by
    #          the attack.
    #  @todo TWS: Many variables can be pushed to local scope.  Many checks can
    #        be avoided and done once too.
    #  @todo TWS: Many of the offensive state cancels (flying, invisiblity, etc)
    #        only occur if the attack is not blocked, dodged, or shielded, but
    #        occur on a riposte.  They should all be stripped on all cases.
    def doAttack(self, dmg, offhand=False):

        # Make a local handle to this CombatProcess' attacking Mob and
        # defending Mob.
        attacker = self.attacker
        defender = self.defender

        # Set flags to indicate if the attacker or defender may get skill ups.
        # Skill ups can only occur if neither the source nor destination are
        # associated with a Player.
        attackerSkillup = attacker.character and not defender.player and not (defender.master and defender.master.player)
        defenderSkillup = defender.character and not attacker.player and not (attacker.master and attacker.master.player)

        # If the attacker is a Player, then consume stamina and remove
        # invulnerability.
        if attacker.player:

            # Calculate the base stamina based on the attacker's primary level.
            stm = attacker.plevel*3

            # Reduce the stamina cost for offhand attacks.
            if offhand:
                stm=int(stm*.6)

            # If the stamina cost is less than 1, then clamp the stamina cost
            # to be at least 1.
            if stm < 1:
                stm = 1

            # Reduce the attacker's stamina.
            attacker.stamina-=stm

            # If the attacker's stamina is less than 0, then clamp the
            # attacker's stamina to 0.
            if attacker.stamina<0:
                attacker.stamina = 0

            # Any aggressive attack by an invulnerable character will remove the
            # character's invulnerability state.  If the Character performing
            # the attack is invulnerable, then cancel the invulnerability effect.
            attacker.cancelStatProcess("invulnerable", \
                "$tgt is no longer protected from death!\\n")

        # Regardless if the attacker is succesful on the attack or not, the
        # defending mob will be mad.  If the attacker is not in the defender's
        # aggro list, then add aggro to the defender towards the attacker.
        if not defender.aggro.get(attacker,0):
            defender.addAggro(attacker,10)

        # When a mob is the target for an attack, the defending mob's combat
        # timer is reset.  If the mob's combat timer is below 72, then reset the
        # timer to 72.  This prevents a Mob's natural regen from occuring until
        # the combat timer is satisfied.
        if not defender.combatTimer:
            defender.combatTimer = 72


        # Get the defender's Block skill level.
        block = defender.skillLevels.get("Block",0)

        # If the defender has a Block skill and the attacker is no more than 5
        # levels above the defender, then the defender may block the attack.
        if block and defender.plevel+5>=attacker.plevel:

            # If the attacker's level is higher than the defender's level, then
            # reduce the block chance by 2 times the level difference.
            if attacker.plevel > defender.plevel:
                block-=(attacker.plevel-defender.plevel)*2

            # Modify the block chance.
            block/=2

            # If the block chance is less than 1, then clamp the block chance to
            # be at least 1.
            if block < 1:
                block = 1

            # Calculate the defender's total block chance range based on level.
            x = defender.plevel*15

            # If the range is less than the block chance times 10, then clamp
            # the range to be at least the block chance times 10.  This sets
            # the best block chance to be 1 out of 11.
            if x < block*10:
                x = block*10

            # Generate a random number to see if the block was succesful.  The
            # block has a block out of x + 1 chance to occur.
            if randint(0,x) < block:

                # If the attacker is a Player, then inform the attacker that the
                # attack was blocked.
                if attacker.player:
                    attacker.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s blocks %s's attack!\\n"%(defender.name,attacker.name))

                # If the defender was a Player, then inform the defender of the
                # successful block.
                if defender.player:
                    defender.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s blocks %s's attack!\\n"%(defender.name,attacker.name))

                # If the defender can skill up and the defender is no more than
                # 10 levels above the attacker, then attempt to increase the
                # defender's Block skill.
                if defenderSkillup and attacker.plevel>=defender.plevel-10:
                    defender.character.checkSkillRaise("Block",1,1)

                # Return 0 to indicate no damage was inflicted to the defender.
                return 0


        # Get the defender's Dodge skill level.
        block = defender.skillLevels.get("Dodge",0)

        # If the defender has a Dodge skill and the attacker is no more than 5
        # levels above the defender, then the defender may dodge the attack.
        if block and defender.plevel+5>=attacker.plevel:

            # If the attacker's level is higher than the defender's level, then
            # reduce the dodge chance by 2 times the level difference.
            if attacker.plevel > defender.plevel:
                block-=(attacker.plevel-defender.plevel)*2

            # Modify the dodge chance.
            block/=2

            # If the dodge chance is less than 1, then clamp the dodge chance to
            # be at least 1.
            if block < 1:
                block = 1

            # Calculate the defender's total dodge chance range based on level.
            x = defender.plevel*15

            # If the range is less than the dodge chance times 10, then clamp
            # the range to be at least the dodge chance times 10.  This sets
            # the best dodge chance to be 1 out of 11.
            if x < block*10:
                x = block*10

            # Generate a random number to see if the dodge was succesful.  The
            # dodge has a block out of x + 1 chance to occur.
            if randint(0,x) < block:

                # If the attacker is a Player, then inform the attacker that the
                # attack was dodged.
                if attacker.player:
                    attacker.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s dodges %s's attack!\\n"%(defender.name,attacker.name))

                # If the defender was a Player, then inform the defender of the
                # successful dodge.
                if defender.player:
                    defender.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s dodges %s's attack!\\n"%(defender.name,attacker.name))

                # If the defender can skill up and the defender is no more than
                # 10 levels above the attacker, then attempt to increase the
                # defender's Dodge skill.
                if defenderSkillup and attacker.plevel>=defender.plevel-10:
                    defender.character.checkSkillRaise("Dodge",1,1)

                # Return 0 to indicate no damage was inflicted to the defender.
                return 0


        # Get the defender's Shield skill level.
        block = defender.skillLevels.get("Shields",0)

        # If the defender has a Shield skill and the defender has an item
        # equipped in the shield slot, then defender may shield the attack.
        if block and defender.worn.has_key(RPG_SLOT_SHIELD):

            # Flag used to indicate if the shielding will be skipped.  This
            # can occur if the defender has a two-handed weapon equipped.
            skip = False

            # Get handles to items, if any, in the primary and secondary slots.
            wpn = defender.worn.get(RPG_SLOT_PRIMARY, None)
            wpn2 = defender.worn.get(RPG_SLOT_SECONDARY, None)

            # If either the primary or secondary weapon is a two-handed weapon,
            # then set the skip flag to True.
            if wpn and "2H" in wpn.skill:
                skip = True
            elif wpn2 and "2H" in wpn2.skill:
                skip = True

            # If the skip flag was not set, then the defender does not have a
            # two-handed weapon equipped and may use the shield skill if the
            # attacker is not too high of a level.
            if not skip:

                # If the defender has a Shield skill and the attacker is no more
                # than 5 levels above the defender, then the defender may shield
                # the attack.
                if block and defender.plevel+5>=attacker.plevel:

                    # If the attacker's level is higher than the defender's
                    # level, then reduce the shield chance by 2 times the level
                    # difference.
                    if attacker.plevel > defender.plevel:
                        block-=(attacker.plevel-defender.plevel)*2

                    # Modify the shield chance.
                    block/=2

                    # If the shield chance is less than 1, then clamp the shield
                    # chance to be at least 1.
                    if block < 1:
                        block = 1

                    # Calculate the defender's total shield chance range based
                    # on level.
                    x = defender.plevel*15

                    # If the range is less than the shield chance times 10, then
                    # clamp the range to be at least the shield chance times 10.
                    # This sets the best shield chance to be 1 out of 11.
                    if x < block*10:
                        x = block*10

                    # Generate a random number to see if the shield was
                    # succesful.  The shiled has a block out of x + 1 chance to
                    # occur.
                    if randint(0,x) < block:

                        # Get the reflexive pronoun depending on the defender's
                        # sex.  This is used in the messages sent to Players.
                        sex = "itself"
                        if defender.spawn.sex == "Male":
                            sex = "himself"
                        elif defender.spawn.sex == "Female":
                            sex = "herself"

                        # If the attacker is a Player, then inform the attacker
                        # that the attack was shielded.
                        if attacker.player:
                            attacker.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s shields %s from %s's attack!\\n"%(defender.name,sex,attacker.name))

                        # If the defender was a Player, then inform the defender
                        # of the successful shielding.
                        if defender.player:
                            defender.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s shields %s from %s's attack!\\n"%(defender.name,sex,attacker.name))

                        # If the defender can skill up and the defender is no
                        # more than 10 levels above the attacker, then attempt
                        # to increase the defender's Shield skill.
                        if defenderSkillup and attacker.plevel>=defender.plevel-10:
                            defender.character.checkSkillRaise("Shields",1,1)

                        # Play the shield block animation.
                        defender.zone.simAvatar.mind.callRemote("playAnimation",defender.simObject.id,"shieldblock")

                        # Return 0 to indicate no damage was inflicted to the
                        # defender.
                        return 0


        # Slot indicates the slot from which a weapon will be retrieved.
        slot = RPG_SLOT_PRIMARY

        # If the attack is an offhand attack, then set the secondary slot to
        # be retrieved.
        if offhand:
            slot = RPG_SLOT_SECONDARY

        # Get a handle to an item, if any, in the primary or secondary slot.
        wpn = attacker.worn.get(slot, None)

        # If the attacker has visibility modifiers, then cancel any visibility
        # modifer effects.
        if attacker.visibility <= 0:
            attacker.cancelInvisibility()

        # If the attacker is flying, then cancel flying effects.
        if attacker.flying > 0:
            attacker.cancelFlying()

        # If the attacker has feigned death, then cancel feign death effects.
        if attacker.feignDeath > 0:
            attacker.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")

        # Make a local handle to the attacker's Player.
        player = attacker.player


        # The attacker has attempted to perform an attack, so reset the combat
        # inhibited count.
        attacker.combatInhibited = 0

        # The actualdmg variable will store the amount of unmitigated damage
        # inflicted to the defender.
        actualdmg = 0

        # Get the attacker's offense and the defender's defense.
        offense = attacker.offense
        defense = defender.defense

        # Modify the offense by the attacker's Tactics Offense skill, and modify
        # the defense by defender's Tactics Defense.
        offense += attacker.skillLevels.get('Tactics Offense', 0) * 2
        defense += defender.skillLevels.get('Tactics Defense', 0)

        # Modify the offense by the attacker's skill level for the skill being
        # used by the attack.
        offense += attacker.skillLevels[self.skill]

        # Modify the defender's defense by the defender's armor and level.
        defense += defender.armor*(defender.plevel/15)

        # Modify the offense based on the attacker's offense modifier.
        offense += offense*(attacker.offenseMod/5.0)

        # Modify the defense based on the defenders's defense modifier.
        defense += defense*(defender.defenseMod/5.0)

        # Get the attacker's weapon advancement value, if any, for the skill
        # being used by the attack.
        self.wpnAdvanceMod = attacker.advancements.get(self.skill,0.0)

        # If there is a weapon advance mod, then modify the offense.
        if self.wpnAdvanceMod:
            offense += offense*self.wpnAdvanceMod


        # Indicates the index for RPG_BANEWEAPON_OFFENSE which defines the race
        # bane modifier.  An invalid index is used to indicate no racial bane
        # is applicable based on the weapon and the defender.
        bane = -1

        # Flag used to indicate if the weapon being used by the attack is a
        # two-handed weapon.
        # TWS: Why is this done.  The twohanded variable is not used!
        twohanded = False

        # If a weapon is being used, then bane or resist modifiers may need to
        # be applied.
        if wpn:

            # If weapon's race bane is same as the defender's race, then get
            # the weapon's race bane index.
            if wpn.wpnRaceBane == defender.spawn.race:
                bane = wpn.wpnRaceBaneMod

            # If the weapon has a resist debuff modifier, then update the
            # defender's ExtraDamageInfo based on the weapon's resist debuff
            # type and modifier.
            if wpn.wpnResistDebuffMod:
                defender.extraDamageInfo.resistDebuff = wpn.wpnResistDebuff
                defender.extraDamageInfo.resistDebuffMod = wpn.wpnResistDebuffMod

            # If the weapon being used by the attack is a two-handed weapon,
            # then set the twohanded flag.
            # TWS: Why is this done.  The twohanded variable is not used!
            if "2H" in wpn.skill:
                twohanded=True

        # If the bane index was updated, then the weapon contained an applicable
        # offense modifier based on racial bane.  Thus, the offense needs to
        # be updated.
        if bane != -1:

            # Modify the offense based on the bane provided by the weapon.
            offense += offense*RPG_BANEWEAPON_OFFENSE[bane]


        # If the attacker is a Player and the difficulty setting is not
        # hardcore, then increase the offense by 20%.
        if attacker.player and CoreSettings.DIFFICULTY != RPG_DIFFICULTY_HARDCORE:
            offense = int(offense*1.20)

        # If the attacker is a Player and the difficult setting is easy, then
        # increase the offense by 110%.
        if attacker.player and CoreSettings.DIFFICULTY == RPG_DIFFICULTY_EASY:
            offense += int(offense*1.10)

        # Cast offense and defense into integers, losing any decimal values.
        offense = int(offense)
        defense = int(defense)

        # Calculate the base hit percentage based on offense and defense.
        # This will return a value between 1 and 99.
        hitp = self.calcBaseHitPercentage(offense,defense)

        # If the attacker is a Player and the difficulty setting is easy, then
        # increase the Player's hit chance by 30%.
        if attacker.player and CoreSettings.DIFFICULTY == RPG_DIFFICULTY_EASY:
            hitp+=int(hitp*.30)


        # To account for low levels and the Player learning curve, modify hit
        # chances.  Increase the Players chance to hit a low level NPC, and
        # decrease the chance for a low leve NPC to hit a defending Mob.

        # If the attacker is a Player and the difficult setting is not hardcore
        # and the defender is below level five, then increase the Player's hit
        # chance by 100%.
        if attacker.player and CoreSettings.DIFFICULTY != RPG_DIFFICULTY_HARDCORE and defender.plevel < 5:
            hitp+=int(hitp)

        # If the attacker is an NPC and the attacker's level is below five and
        # the NPC has a least a 5 out of 100 chance to hit the defending Mob,
        # then reduce the attacker's hit chance by 50%.
        # TWS: This could probably be part of an if/else statement.
        if not attacker.player and attacker.plevel < 5 and hitp > 4:
            hitp/=2

        # The actualdmg variable will store the amount of unmitigated damage
        # inflicted to the defender.
        # TWS: Why is this set again?
        actualdmg = 0

        # Generate a random number to see if the attacker did not miss the
        # attack.  The attacker has a hitp out of 101 chance to hit the target.
        # The unmodified hitp is 1 to 99, so in best case, the attacker has a
        # 99 out of 101 chance, and at worse case the attacker has a 1 out of
        # 101 chance to hit.
        if randint(0,100) < hitp:

            # Calculate the adjusted max damage based on the base damage.
            maxdmg = self.calcDamageAdjustedMax(dmg)

            # Calculate the actual unmitigated damage based on the adjusted
            # max damage.
            actualdmg = self.calcDamageActual(maxdmg)

            # Multiple the actual damage by the attacker's melee damage mod.
            actualdmg*=attacker.meleeDmgMod

            # If the bane index was updated, then the weapon contained an
            # applicable damage modifier based on racial bane.  Thus, the actual
            # damage needs to be updated.
            if bane != -1:

                # Modify the actual damage based on the bane provided by the
                # weapon.
                actualdmg+=actualdmg*RPG_BANEWEAPON_DAMAGE[bane]

            # If damage is being done, then either the attacker or defender
            # will be receiving damage.
            # TWS: At this point, isn't actualdmg guaranteed to be at least 1?
            #  DamageActual does a random of (0,X) + 1.
            if actualdmg:

                # If the defender is a Player and the difficulty setting is
                # easy, then reduce the damage by 33%.
                if defender.player and CoreSettings.DIFFICULTY == RPG_DIFFICULTY_EASY:
                    actualdmg/=3

                    # If the modified damage is less than 1, then clamp the
                    # damage to be at least 1.
                    if actualdmg < 1:
                        actualdmg = 1

                # If the defender is a Player, the difficult setting is not
                # hardcore, and the attacker is below level five, then decrease
                # the damage by 50%.
                elif defender.player and CoreSettings.DIFFICULTY != RPG_DIFFICULTY_HARDCORE and attacker.plevel < 5:
                    actualdmg = int(actualdmg*.5)

                    # If the modified damage is less than 1, then clamp the
                    # damage to be at least 1.
                    if actualdmg < 1:
                        actualdmg = 1

                # If the attacker is out of stamina, then reduce the damage by
                # 25%.
                if not attacker.stamina:
                    actualdmg = int(actualdmg*.75)

                    # If the modified damage is less than 1, then clamp the
                    # damage to be at least 1.
                    if actualdmg < 1:
                        actualdmg = 1


                # Flag used to indicate if the attack is a critical attack.
                critical = False

                # Criticals can only occur from primary attack.  If the attack
                # is not offhand and the attacker has stamina, then a critical
                # attack may occur.
                if not offhand and attacker.stamina:

                    # Get the attacker's Inflict Critical skill level.
                    try:
                        icrit = attacker.skillLevels["Inflict Critical"]
                    except:
                        icrit = 0

                    # If the attacker has an Inflict Critical skill, then the
                    # attack may become a critical attack.
                    if icrit:

                        # Calculate the base critical chance range from the
                        # attacker's critical attribute.
                        c = 20.0/attacker.critical

                        # Reduce the critical chance range based on the
                        # attacker's Inflict Critical skill level.
                        c-=icrit/200

                        # If the critical chance range is below 10, then clamp
                        # the critical change range to be at least 10.  This
                        # sets the best critical chance to be 1 out of 11.
                        if c < 10:
                            c = 10

                        # Round the chance up to an integer.
                        chance = int(ceil(c))

                        # Generate a random number to see if a critical occurs.
                        # The attack has a 1 out of chance + 1 chance to
                        # critical, and 0 indicates success.
                        if not randint(0,chance):

                            # If the attacker can skill up, then attempt to
                            # increase the attacker's Inflict Critical skill.
                            if attackerSkillup:
                                attacker.character.checkSkillRaise("Inflict Critical",8)

                            # Generate a random number to determine the critical
                            # damage multiplier.
                            c = randint(0,8)

                            # Randomly set the damage multiplier by 1 out of 9
                            # times by +300%, 3 out of 9 times by +200%, and 5
                            # out of 9 times by 100%.
                            # TWS: This should probably occur within the if
                            # statement where player damage is multipied.
                            if c == 8:
                                icrit = 4
                            elif c >= 5:
                                icrit = 3
                            else:
                                icrit = 2

                            # If the attacker is an NPC, increase the damage by
                            # +100%.
                            if not attacker.player:
                                actualdmg*=2.0

                            # Otherwise, use the attacker's critical attribute
                            # and the result of the random.
                            else:
                                actualdmg*=attacker.critical
                                actualdmg*=icrit

                            # Set the critical flag to indicate a critical
                            # attack is occuring.  This will prevent the
                            # defender from being capable of performing a
                            # Riposte.
                            critical = True


                            # Get the attacker's Grievous Wound skill level.
                            try:
                                gwnd = attacker.skillLevels["Grievous Wound"]
                            except:
                                gwnd = 0

                            # Grievous Wound has a max skill of 250.  Level
                            # range and chance range are modified based on the
                            # value.

                            # Increase the level range for which an attacker may
                            # land grievious wound upon a defender by 0 to 5
                            # based on the grievous wound skill level.  If the
                            # attacker is more than the modified level range
                            # above the defender, then grievious wound may not
                            # occur so set the modified skill level to 0.
                            if attacker.plevel + int(floor(gwnd/45.0)) < defender.plevel:
                                gwnd = 0

                            # If the attacker is an NPC, then reduce the chance
                            # for a Grievious Wound.
                            if not attacker.player:
                                gwnd /= 3

                            # Grievious Wound may only occur if all of the
                            # following conditions are true:
                            # - The modified grievouns wound skill level is not
                            #   zero.
                            # - Generate a randon number between 0 and a
                            #   modified range based on skill level.  The range
                            #   will be between 3 and 19.  Thus, in best case
                            #   with a max skill level, the attacker has a 1 out
                            #   of 4 chance, and at worst case with the lowest
                            #   skil, the attacker has 1 out of 20 chance.  0
                            #   indicates success.
                            if gwnd and not randint(0,int(20.0 - float(gwnd)/15.0)):

                                # If the attacker can skill up, then attempt to
                                # increase the attacker's Grievous Wound skill.
                                if attackerSkillup:
                                    attacker.character.checkSkillRaise("Grievous Wound",2,2)

                                # Modify the actual damage based on the grievous
                                # wound skill level.  This will increase the
                                # damage from a range of +20% to +100%.
                                actualdmg *= 1.1967 + 0.0033*gwnd

                                # If the attacker has a primary bonus damage,
                                # then add the attacker's primary bonus damage
                                # to the damage being inflicted.  Adding the
                                # bonus here prevents it from being calculated
                                # in the critical bonus.
                                if attacker.dmgBonusPrimary:
                                    actualdmg += attacker.dmgBonusPrimary

                                # Inflict critical damage to the defender.
                                Damage(defender,attacker,actualdmg,RPG_DMG_CRITICAL,"grievously wounds")


                            # Otherwise, Grievious Wound failed, but the attack
                            # is still a critical.
                            else:

                                # If the attacker has a primary bonus damage,
                                # then add the attacker's primary bonus damage
                                # to the damage being inflicted.  Adding the
                                # bonus here prevents it from being calculated
                                # in the critical bonus.
                                if attacker.dmgBonusPrimary:
                                    actualdmg += attacker.dmgBonusPrimary

                                # Inflict critical damage to the defender.
                                Damage(defender,attacker,actualdmg,RPG_DMG_CRITICAL)


                # If a critical did not occur, then the defender may riposte the
                # attack.
                if not critical:

                    # Get the defender's Riposte skill level.
                    r = defender.skillLevels.get('Riposte',0)
                    if r:

                        # Calculate the base riposte chance range.
                        r = 1000-r
                        r/=50

                        # Modify the riposte chance range based on the
                        # attacker's level.
                        r+=attacker.plevel/10

                        # If the riposte chance range is below 10, then clamp
                        # the riposte change range to be at least 10.  This sets
                        # the best riposte chance to be 1 out of 11.
                        if r<10:
                            r = 10

                        # Generate a random number to see if a riposte occurs.
                        # The defender has a 1 out of r + 1 chance to riposte,
                        # and 0 indicates success.
                        if not randint(0,int(r)):

                            # If the defender can skill up, then attempt to
                            # increase the defender's Riposte skill.
                            if defenderSkillup:
                                defender.character.checkSkillRaise("Riposte",10)

                            # Inflict 50% damage to the attacker.
                            Damage(attacker,defender,actualdmg/2,RPG_DMG_PHYSICAL,"ripostes",False)


                    # The attacker's damage bonuses are applied after the
                    # occurance of a riposte, if any.

                    # If the attacker has a primary bonus damage and the attack
                    # is a primary attack, then add the attacker's primary
                    # bonus damage to the damage being inflicted.
                    # TWS: the offhand parts of the conditions should be done
                    # first and possible contain the bonus check within it.
                    if attacker.dmgBonusPrimary and not offhand:
                        actualdmg+=attacker.dmgBonusPrimary

                    # Otherwise, if the attacker has an offhand bonus damage and
                    # the attack an offhand attack, then add the attacker's
                    # secondary bonus damage to the damage being inflicted.
                    elif attacker.dmgBonusOffhand and offhand:
                        actualdmg+=attacker.dmgBonusOffhand

                    # Inflict damage to the defender based on the damage type
                    # for the attack.
                    Damage(defender,attacker,actualdmg,self.dmgType)


        # Otherwise, the attacker missed.  If the defender can skil up and the
        # defender is no more than 4 levels higher than the attacker, then
        # attempt to raise defensive skills.
        elif defenderSkillup and defender.plevel-attacker.plevel<5:
            SuccessfulDefense(defender)


        # Set the unarmed sound profile to be used.
        sndProfile = UNARMEDSOUNDPROFILE

        # If a weapon is equipped and it has a ItemSoundProfile, then set the
        # weapon's ItemSoundProfile to be used.
        if wpn and wpn.sndProfile:
            sndProfile = wpn.sndProfile

        # Get a random attack sound from the attacker.
        snd = attacker.spawn.getSound("sndAttack")

        # If an attack sound was found, then play the attack sound.
        if snd:
            attacker.playSound(snd)


        # If the defender was not damaged, then just play the weapon's attack
        # sound.
        if not actualdmg:

            # Get a random attack sound from the weapon or unarmed SoundProfile.
            snd = sndProfile.getSound("sndAttack")

            # If an attack sound was found, then play the attack sound.
            if snd:
                attacker.playSound(snd)

        # Otherwise, the defender was damaged.
        # TWS: This should probably be the first case in the if statement, and
        # not be the else case.
        else:

            # Get a random hit sound from the weapon or unarmed SoundProfile.
            snd = sndProfile.getSound("sndHit")

            # If a hit sound was found, then play the hit sound.
            if snd:
                attacker.playSound(snd)


            # The attacker hit the defender.  The defender may have damage procs
            # that trigger, and the attacker may have attack procs that trigger.

            # Get a copy of damage procs on the defender.
            # TWS: Should items with penalties still provide procs?  Items with
            # penalties do not provide procs on attacks.
            damagedProcs = defender.damagedProcs[:]

            # Add a copy of the damage procs provided by item sets on the
            # defender.
            damagedProcs.extend(defender.itemSetSpells.get(RPG_ITEM_TRIGGER_DAMAGED, []))

            # If there are any damage procs, then a proc may occur.
            if len(damagedProcs):

                # Iterate through all gathered items, checking each for procs.
                for item in damagedProcs:

                    # Iterate through all damage procs, attempting to trigger
                    # each.
                    for ispell in item.spells:

                        # Only damage procs may trigger.  If the proc's trigger
                        # is damage, then it may proc.
                        if ispell.trigger == RPG_ITEM_TRIGGER_DAMAGED:

                            # Trigger the proc if any of the following
                            # conditions are true:
                            # - The proc is set to always trigger based on
                            #   frequency.
                            # - Generate a random number to see if the proc
                            #   triggered.  The proc has a 1 out of
                            #   frequency + 1 chance to proc, and 0 indicates
                            #   success.
                            if ispell.frequency <= 1 or not randint(0,ispell.frequency):

                                # Make a local handle to the proc's SpellProto.
                                proto = ispell.spellProto

                                # Get a valid target for the proc based on the
                                # SpellProto.
                                if proto.target == RPG_TARGET_SELF:
                                    tgt = defender
                                elif proto.target == RPG_TARGET_PARTY:
                                    tgt = defender
                                elif proto.target == RPG_TARGET_ALLIANCE:
                                    tgt = defender
                                elif proto.target == RPG_TARGET_PET:
                                    tgt = defender.pet
                                else:
                                    tgt = attacker

                                # If a valid proc target was found, then trigger
                                # the proc.
                                if tgt:
                                    SpawnSpell(proto,defender,tgt,tgt.simObject.position,1.0,proc=True)


            # Additional procs may need to be gathered from rings.
            additionalProcs = None

            # If the attack skill is Fist, then check fingers for additional
            # procs.
            if self.skill == "Fists":

                # Item is used as a handle to an equipped item in either the
                # left or right finger slot.
                item = None

                # If the attack is an offhand attack, then get the item, if any,
                # on the left finger.
                if offhand:
                    item = attacker.worn.get(RPG_SLOT_LFINGER,None)

                # Otherwise, the attack is a primary attack.  Get the item, if
                # any, on the right finger.
                else:
                    item = attacker.worn.get(RPG_SLOT_RFINGER,None)

                # If an item was found and the item's skill is Fist, then set
                # the item's spells as the additional procs.
                if item and item.skill == "Fists":
                    additionalProcs = item.spells

            # Perform attack procs. This includes innate procs on weapon,
            # enchanted procs, poisons, item set procs, as well as additional
            # procs such as those from monk rings.
            doAttackProcs(attacker,defender,wpn,additionalProcs)


            # If a weapon was used in the attack, then the weapon may receive
            # some damage.
            if wpn:

                # The weapon receives damage if all of the following conditions
                # are true:
                # - The attacker is a Player.
                # - The weapon has a repair max.
                # - The weapon is not completely broken.
                # - Generate a random number to see if weapon is damaged.  The
                #   weapon has a 1 out of 21 chance to be damaged, and 0 the
                #   weapon being damaged.
                if attacker.player and wpn.repairMax and wpn.repair and not randint(0,20):

                    # Damage the weapon.
                    wpn.repair -= 1

                    # The weapon may damaged enough that it warrants informing
                    # the Player with a message and sound.

                    # Calculate a ratio of the current repair value to the
                    # max repair value.
                    repairRatio = float(wpn.repair) / float(wpn.repairMax)

                    # If the ratio is zero, then the weapon is completely
                    # broken.
                    if not repairRatio:

                        # Inform the Player with a message and sound.
                        attacker.player.sendGameText(RPG_MSG_GAME_RED,"%s's <a:Item%s>%s</a> has broken! (%i/%i)\\n"%(attacker.name,GetTWikiName(wpn.itemProto.name),wpn.name,wpn.repair,wpn.repairMax))
                        attacker.playSound("sfx/Shatter_IceBlock1.ogg")

                    # Otherwise, check if the ratio is below the 20% threshold.
                    # If so, it is severely damaged.
                    elif repairRatio < .2:

                        # Inform the Player with a message and sound.
                        attacker.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s's <a:Item%s>%s</a> is severely damaged! (%i/%i)\\n"%(attacker.name,GetTWikiName(wpn.itemProto.name),wpn.name,wpn.repair,wpn.repairMax))
                        attacker.playSound("sfx/Menu_Horror24.ogg")

                    # Updating the weapon's stats, recalculating the penalty
                    # from the updated repair value.  Refreshing only the repair
                    # value will not work since the new repair value may affect
                    # other attributes.
                    wpn.setCharacter(attacker.character,True)


        # Clear the defender's ExtraDamageInfo.
        defender.extraDamageInfo.clear()

        # Return the unmitigated damage inflicted to the defender.
        return actualdmg



## @} # End combat group.
