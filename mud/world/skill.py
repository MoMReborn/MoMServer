# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from core import *

from random import randint
from math import floor,ceil,sqrt
from damage import Damage
from defines import *
import traceback
from mud.worlddocs.utils import GetTWikiName

from mud.common.persistent import Persistent
from sqlobject import *

class ClassSkillQuestRequirement(Persistent):
    classSkill = ForeignKey('ClassSkill')
    choiceIdentifier = StringCol()
    levelBarrier = IntCol()    # level that still can be reached without the required quest

class ClassSkillRaceRequirement(Persistent):
    classSkill = ForeignKey('ClassSkill')
    race = StringCol()
    
class ClassSkill(Persistent):
    skillname = StringCol(default = "")
    levelGained = IntCol(default = 0)
    levelCapped = IntCol(default = 0)
    minReuseTime = IntCol(default = 0)
    maxReuseTime = IntCol(default = 0)
    maxValue = IntCol(default = 0)
    trained = BoolCol(default = False)
    spellProto = ForeignKey('SpellProto',default = None)
    classProtos = RelatedJoin('ClassProto')
    raceRequirementsInternal = MultipleJoin('ClassSkillRaceRequirement')
    questRequirementsInternal = MultipleJoin('ClassSkillQuestRequirement')
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        self.raceRequirements = []
        for r in list(self.raceRequirementsInternal):
            self.raceRequirements.append(r.race)
        self.questRequirements = []
        for qreq in list(self.questRequirementsInternal):
            self.questRequirements.append((qreq.choiceIdentifier,qreq.levelBarrier))
        
        

    
    def getMaxValueForLevel(self,level):
        if level < self.levelGained:
            return 0
        if not self.maxValue:
            return 0
        if not self.levelGained:
            return 0
        
        if level >= self.levelCapped:
            return self.maxValue
        
        if self.levelGained == self.levelCapped:
            return self.maxValue

            
        step = floor((self.maxValue/(self.levelCapped-self.levelGained)))
        
        value = floor((level - self.levelGained) * step+step) 
        if value > self.maxValue:
            value = self.maxValue
        return int(value)
        
    def getReuseTimeForLevel(self,level):
        if not self.maxReuseTime or not self.minReuseTime:
            return 0
        if not self.maxValue:
            return 0        
        if level < self.levelGained:
            return 0   

        if level > self.levelCapped:
            level = self.levelCapped

        
        if self.levelGained == self.levelCapped:
            return self.minReuseTime
        
        spread = float(self.maxReuseTime) - float(self.minReuseTime)
        gap = float(self.levelCapped) - float(self.levelGained)
        
        if not gap:
            return self.maxReuseTime
        
        phase = float((level-self.levelGained))/gap
        spread*=phase
        
        t = floor(self.maxReuseTime-spread)
            
        if t < self.minReuseTime:
            t = self.minReuseTime
            
        return int(t)



# Estimate a targets valuables.
def DoAssess(mob):
    # Assess does no good for mobs, so they shouldn't use it.
    if not mob.player:
        print "WARNING: Non-player mob attempting to assess."
        return (False,False)
    
    # Get handles to the player using the skill and the target.
    player = mob.player
    tgt = mob.target
    
    # Assess needs a target.
    if not tgt or tgt == mob:
        player.sendGameText(RPG_MSG_GAME_DENIED, \
               "$src's <a:SkillAssess>assess</a> failed, no target.\\n",mob)
        return (False,False)
    
    # Check if the target is in range.
    if GetRangeMin(mob,tgt) > 5.0:
        player.sendGameText(RPG_MSG_GAME_DENIED, \
               "$src's <a:SkillAssess>assess</a> failed, out of range.\\n",mob)
        return (False,False)
    
    # End current looting.
    if player.looting:
        player.looting.looter = None
        player.looting = None
    
    # Get the assess skill level.
    alevel = mob.skillLevels.get('Assess',0)
    
    # Dictionary in which we'll store the items the Player's Character
    #  could assess correctly.
    assessDict = {}
    
    # If the target is a player, check worn items. Rest isn't visible at all.
    # (Keep some privacy)
    if tgt.player:
        # If the target is stunned, take the complete list.
        if tgt.stun > 0:
            assessDict = dict((x,item.itemInfo) \
                              for x,item in enumerate(tgt.worn.itervalues()))
        else:
            x = 0
            for item in tgt.worn.itervalues():
                # Small jewelry is the hardest to detect of the worn items.
                if item.slot in (RPG_SLOT_LEAR,RPG_SLOT_REAR,RPG_SLOT_NECK, \
                                 RPG_SLOT_LFINGER,RPG_SLOT_RFINGER):
                    if item.level <= alevel:
                        assessDict[x] = item.itemInfo
                        x += 1
                # Bigger jewelry items and accessories come next.
                elif item.slot in (RPG_SLOT_WAIST,RPG_SLOT_LWRIST, \
                                   RPG_SLOT_RWRIST,RPG_SLOT_LIGHT):
                    if item.level <= alevel * 2:
                        assessDict[x] = item.itemInfo
                        x += 1
                # Items in the more obvious slots are always visible.
                else:
                    assessDict[x] = item.itemInfo
                    x += 1
    
    # No player, so parse complete loot.
    else:
        # Get the targets loot table.
        loot = tgt.loot
        # Create the complete loot table for the target if needed.
        if loot and loot.generateCorpseLoot():
            # Build the assess dictionary from the loot table.
            # If the target is stunned, take the complete list.
            # Do the same if the Thief has the assess skill maxed.
            if tgt.stun > 0 or alevel == 250:
                assessDict = dict((x,item.itemInfo) \
                                  for x,item in enumerate(loot.items))
            else:
                x = 0
                for item in loot.items:
                    # Always show items flagged for pick pocket.
                    try:
                        if loot.lootProto.itemDetails[item.itemProto.name] & \
                           RPG_LOOT_PICKPOCKET:
                            assessDict[x] = item.itemInfo
                            x += 1
                            continue
                    except:
                        pass
                    # Always show quest items.
                    if item.flags & RPG_ITEM_QUEST:
                        assessDict[x] = item.itemInfo
                        x += 1
                        continue
                    # For worn items use the same rules as when assessing
                    #  a fellow Player's property.
                    if item.slot != -1:
                        # Small jewelry is the hardest to detect of the worn items.
                        if item.slot in (RPG_SLOT_LEAR,RPG_SLOT_REAR,RPG_SLOT_NECK, \
                                         RPG_SLOT_LFINGER,RPG_SLOT_RFINGER):
                            if item.level <= alevel:
                                assessDict[x] = item.itemInfo
                                x += 1
                        # Bigger jewelry items and accessories come next.
                        elif item.slot in (RPG_SLOT_WAIST,RPG_SLOT_LWRIST, \
                                           RPG_SLOT_RWRIST,RPG_SLOT_LIGHT):
                            if item.level <= alevel * 2:
                                assessDict[x] = item.itemInfo
                                x += 1
                        # Items in the more obvious slots are always visible.
                        else:
                            assessDict[x] = item.itemInfo
                            x += 1
                        continue
                    # Items with level 1 (default) that can't be equipped are
                    #  the hardest to detect of all items.
                    # This includes potions, ingredients, tomes, foci and so on.
                    if item.level == 1 and len(item.itemProto.slots) == 0:
                        if tgt.level * 2.5 <= alevel:
                            assessDict[x] = item.itemInfo
                            x += 1
                        continue
                    # Otherwise just linearly base off item level.
                    if item.level * 2 <= alevel:
                        assessDict[x] = item.itemInfo
                        x += 1
    
    # If the assess dictionary is empty, return skill failure.
    if not len(assessDict):
        player.sendGameText(RPG_MSG_GAME_DENIED, \
               "$tgt doesn't seem to have anything of particular worth.\\n",mob)
        return (False,True)
    
    # Give feedback to the player.
    player.mind.callRemote("setLoot",assessDict,True)
    player.sendGameText(RPG_MSG_GAME_GAINED, \
           "$src tries to assess $tgt's possessions.\\n",mob)
    
    # Skill was successfully used.
    return (True,True)


# Disarm a target, return a tuple with (success,used).
# Valid target and all conditions met means used = True.
# Succeed in disarming means success = True.
def DoDisarm(mob):
    # Mobs can't disarm for now. If disarm gets added for PvP, mobs may learn how to do it.
    if not mob.player:
        print "WARNING: Non-player mob attempting to disarm."
        return (False,False)
    
    tgt = mob.target
    player = mob.player
    
    # Disarm needs a target.
    if not tgt:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillDisarm>disarm</a> failed, no target.\\n",mob)
        return (False,False)
    
    # Don't allow disarm in PvP for now.
    if tgt.player or (tgt.master and tgt.master.player):
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillDisarm>disarm</a> failed, can't disarm other players.\\n",mob)
        return (False,False)
    
    # Get a possible weapon to disarm.
    weapon = tgt.worn.get(RPG_SLOT_SECONDARY)
    if not weapon:
        weapon = tgt.worn.get(RPG_SLOT_PRIMARY)
    if not weapon:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillDisarm>disarm</a> failed, $tgt carries no weapon.\\n",mob)
        return (False,False)
    
    # Check if target is in disarm range.
    if GetRangeMin(mob,tgt) > 2.0:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillDisarm>disarm</a> failed, $tgt is out of range.\\n",mob)
        return (False,False)
    
    # Fairly simple disarm success calculation. Needs redoing sometime.
    pplevel = mob.plevel#skillLevels['Disarm']/10
    spread = pplevel-mob.target.plevel
    
    failed = False
    if spread < -5:
        failed = True
    else:
        chance = 6 + spread
        r = randint(0,chance)
        if not r:
            failed = True
    
    # Attempted to disarm, add aggro if necessary.
    if not tgt.aggro.get(mob,0):
        tgt.addAggro(mob,10)
    
    # Failed to disarm target.
    if failed:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src has failed to <a:SkillDisarm>disarm</a> $tgt!\\n",mob)
        return (False,True)
    
    # Disarm succeeded, unequip weapon and put it into loot table.
    tgt.unequipItem(weapon.slot)
    weapon.slot = -1
    tgt.mobInfo.refresh()
    
    stolen = False
    # If weapon is not soulbound or unique, thiefs have a chance
    #  to directly steal the disarmed weapon. Success depends on
    #  pick pocket skill.
    if not weapon.flags&RPG_ITEM_SOULBOUND and not weapon.flags&RPG_ITEM_UNIQUE:
        pplevel = mob.skillLevels.get('Pick Pocket',0) / 10
        mod = mob.target.difficultyMod
        if pplevel:
            difficulty = int(round(5.0 * (mod * mod * float(mob.target.plevel)) / float(pplevel)))
            # Success! not only disarm, but also steal weapon.
            if not randint(0,difficulty):
                if player.giveItemInstance(weapon):
                    player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully yanks away $tgt's <a:Item%s>%s</a>!\\n"%(weapon.character.name,GetTWikiName(weapon.itemProto.name),weapon.name),mob)
                    loot = tgt.loot
                    loot.items.remove(weapon)
                    if not len(loot.items):
                        tgt.loot = None
                    stolen = True
    
    # If the weapon wasn't stolen, inform about successful disarm.
    if not stolen:
        player.sendGameText(RPG_MSG_GAME_GAINED,"$src has <a:SkillDisarm>disarmed</a> $tgt's <a:Item%s>%s</a>.\\n"%(GetTWikiName(weapon.itemProto.name),weapon.name),mob)
    
    # Give a possible skill raise and play a nice sound.
    mob.character.checkSkillRaise("Disarm")
    player.mind.callRemote("playSound","sfx/Hit_HugeMetalPlatformDrop.ogg")
    return (True,True)


# Pick pocket something from target, return a tuple with (success,used).
# Used is True if all necessary conditions have been met.
# Success is True if pick pocket succeeded.
def DoPickPocket(mob):
    # Mobs shouldn't pick pocket at all. Could be fun in some
    #  instances, but needs a special implementation.
    if not mob.player:
        print "WARNING: Non-player mob attempting to pick pocket"
        return (False,False)
    
    # Check if there is a target to pick pocket.
    tgt = mob.target
    if not tgt or tgt == mob:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillPickPocket>pick pocket</a> failed, no target.\\n",mob)
        return (False,False)
    
    # Cannot pick pocket players, maybe in the future for PvP.
    if tgt.player or (tgt.master and tgt.master.player):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillPickPocket>pick pocket</a> failed, can't pick pocket other players.\\n",mob)
        return (False,False)
    
    # Store if the target is disabled in a flag for easier query.
    tgtDisabled = tgt.sleep > 0 or tgt.stun > 0
    
    if tgt.target:
        # Can't pick pocket mobs that are in combat with someone else.
        # Prevent grieving.
        if tgt.target.player != mob.player:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"<a:SkillPickPocket>Pick pocket</a> failed, can't pick pocket targets in combat with other players.\\n",mob)
            return (False,False)
        # Can't pick pocket mobs that are attacking the thief.
        if tgt.target == mob and not tgtDisabled:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"<a:SkillPickPocket>Pick pocket</a> failed, $tgt has a keen eye on $src.\\n",mob)
            return (False,False)
    # Can't pick pocket when fighting.
    if mob.attacking:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src is too occupied with combat to <a:SkillPickPocket>pick pocket</a>.\\n",mob)
        return (False,False)
    
    # Check if target is in range.
    if GetRangeMin(mob,tgt) > 2.0:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillPickPocket>pick pocket</a> failed, out of range.\\n",mob)
        return (False,False)
    
    # Get the targets loot table.
    loot = tgt.loot
    
    # Generate loot if necessary, check if there's
    #  anything in it.
    nothing = True
    if loot and loot.generateCorpseLoot():
        nothing = False
    
    # If the loot table is empty, target has nothing to steal.
    if nothing:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"<a:SkillPickPocket>Pick pocket</a> failed, $tgt has nothing to steal.\\n",mob)
        return (False,True)
    
    # Gather lists of items that can be pick pocketed.
    pickPocketNormal = []  # Normal pick pocket list.
    pickPocketSpecial = []  # Items specially flagged for thieves.
    for item in loot.items:
        if loot.lootProto.itemDetails.has_key(item.itemProto.name):
            if loot.lootProto.itemDetails[item.itemProto.name] & RPG_LOOT_PICKPOCKET:
                pickPocketSpecial.append(item)
            # If the item is in the standard loot table but is equipped allow it
            #  as long as it's not soulbound. Soulbound items resist the thiefs
            #  clutches by themselves, not only the owner.
            elif not item.flags & RPG_ITEM_SOULBOUND and item.slot != -1:
                # Check if the specific item actually can be pickpocketed
                #  successfully.
                if item.slot in (RPG_SLOT_SHOULDERS,RPG_SLOT_HANDS,RPG_SLOT_FEET) and \
                    not tgtDisabled:
                    continue
                elif item.slot in (RPG_SLOT_CHEST,RPG_SLOT_ARMS,RPG_SLOT_LEGS) and \
                    tgt.stun <= 0:
                    continue
                pickPocketNormal.append(item)
            continue
        pickPocketNormal.append(item)
    
    # Bummer, no items to steal.
    if not loot.tin and not len(pickPocketNormal) and not len(pickPocketSpecial):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"<a:SkillPickPocket>Pick pocket</a> failed, $tgt has nothing to steal.\\n",mob)
        return (False,True)
    
    # Calculate possibility for a pick pocket success.
    pplevel = mob.skillLevels.get('Pick Pocket',0)
    
    # Give a base of 500.
    succ = 500.0
    # Start with paranoia, the longer it was since last pick pocket,
    #  the less the mob pays attention until paranoia no longer applies.
    # Modifier range: 0.0 - 1.0.
    # Skip paranoia factor if target is asleep or stunned.
    if not tgtDisabled:
        succ *= sqrt(1.0 - loot.pickPocketTimer / 270.0)
    # Now check level difference. Considering pplevel / 10 equal level,
    #  equal level is standard, linearly increase difficulty for higher
    #  level targets and decrease for lower level targets.
    # Four times as easy for 100 level lower, impossible for 100 level higher.
    # Modifier range: 0.002 - 3.98.
    succ *= 2.0 - float(tgt.plevel * 10 - pplevel) / 500.0
    # Include targets difficulty modifier in the calculation.
    # Modifier range: 0.0 - 0.995.
    mod = tgt.difficultyMod / 100.0
    if mod > 1.0:
        mod = 1.0
    succ *= sqrt(1.0 - mod)
    # It's easier to pick pockets on a stunned or sleeping mob.
    if tgtDisabled:
        succ *= 1.5
    
    # Clamp success modifier high to 975 (equals 97.5%)
    succ = int(succ)
    if succ > 975:
        succ = 975
    # Give at least 0.5% chance.
    if succ < 5:
        succ = 5
    
    # Pick pocket timer doesn't prevent continuous pick pocketing,
    #  but serves as a diminishing difficulty to pick pocket again.
    loot.pickPocketTimer = 270  # 45 seconds
    
    # Initialize the noticed flag to false.
    noticed = False
    
    # Determine if pick pocket was a success or not.
    if randint(1,1000) > succ:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$tgt has noticed $src's <a:SkillPickPocket>pick pocketing</a>!\\n",mob)
        if tgt.sleep > 0:  # wake up
            tgt.cancelSleep()
        if not tgt.aggro.get(mob,0):
            tgt.addAggro(mob,10)
        if succ >= 600:
            mob.character.checkSkillRaise("Pick Pocket",4,4)
        return (False,True)
    elif tgt.sleep > 0 and randint(0,1500) > succ:  # wake up
        tgt.cancelSleep()
        if not tgt.aggro.get(mob,0):
            tgt.addAggro(mob,10)
        noticed = True
    if succ <= 750:
        mob.character.checkSkillRaise("Pick Pocket",2,2)
    
    # First of all, try to pick pocket items specially flagged for thieves.
    if len(pickPocketSpecial):
        # Choose one randomly from the special pick pocket list.
        x = len(pickPocketSpecial) - 1
        if x >= 1:
            x = randint(0,x)
        item = pickPocketSpecial[x]
        
        # Save item slot here because it will eventually be altered.
        slot = item.slot
        
        # Try to give the item to the thief.
        if mob.player.giveItemInstance(item):
            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully <a:SkillPickPocket>pick pockets</a> a <a:Item%s>%s</a>!\\n"%(item.character.name,GetTWikiName(item.itemProto.name),item.name))
            # Remove the pick pocketed item from the loot table.
            loot.items.remove(item)
            if not loot.tin and not len(loot.items):
                tgt.loot = None
            # If the mob was wearing the item pick pocketed,
            #  need to unequip it.
            if slot != -1:
                tgt.unequipItem(slot)
                tgt.mobInfo.refresh()
            return (True,True)
    
    # Check if we try to pick pocket an item or money.
    takeItem = False
    if len(pickPocketNormal):
        if loot.tin:
            # 66.67% chance to prefer item even if money is available.
            if randint(0,2):
                takeItem = True
        else:
            takeItem = True
    
    # We want an item.
    if takeItem:
        # Choose the item to pick pocket.
        x = len(pickPocketNormal) - 1
        if x >= 1:
            x = randint(0,x)
        item = pickPocketNormal[x]
        
        # Save item slot here because it will eventually be altered.
        slot = item.slot
        
        # If the item is being worn, some special rules apply.
        if slot != -1:
            # Tiered difficulty for equipped items.
            # Jewelry behaves like normal, so don't test for the following slots:
            #  RPG_SLOT_LEAR, RPG_SLOT_REAR, RPG_SLOT_LFINGER, RPG_SLOT_RFINGER
            #  RPG_SLOT_NECK, RPG_SLOT_LWRIST ,RPG_SLOT_RWRIST
            skip = doNotice = False
            # First difficulty stage: there's always a chance to wake up if
            #  sleeping and to trigger aggro.
            if slot in (RPG_SLOT_HEAD,RPG_SLOT_WAIST,RPG_SLOT_BACK,RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY,RPG_SLOT_RANGED,RPG_SLOT_AMMO,RPG_SLOT_SHIELD,RPG_SLOT_LIGHT):
                doNotice = not noticed
            # Second difficulty stage: can only pick pocket if stunned or asleep
            #  and has a chance to wake up if sleeping and to trigger aggro.
            elif slot in (RPG_SLOT_SHOULDERS,RPG_SLOT_HANDS,RPG_SLOT_FEET):
                doNotice = not noticed
            # Third difficulty stage: second check if pick pocketing succeeds.
            # Also can only pick pocket if stunned and there's always a chance
            #  to trigger aggro.
            elif slot in (RPG_SLOT_CHEST,RPG_SLOT_ARMS,RPG_SLOT_LEGS):
                # Fail by 25% straight.
                skip = not randint(0,3)
                doNotice = not noticed
            
            # If by any of the above rules set, check if the thief gets noticed.
            if doNotice:
                span = pplevel - 10 * tgt.plevel
                # If the target is less than 20 levels below the associated
                #  pick pocket level, there's an increasing chance to get noticed.
                if span < 200:
                    # If the target is more than 10 levels above the associated
                    #  pick pocket level, always get noticed.
                    if span < -100:
                        noticed = True
                    # Otherwise distribute linearly between 100% and 50%.
                    else:
                        noticed = randint(1,100) > (span + 100) / 6
                # There's always at least a chance of 50% to get noticed.
                else:
                    noticed = randint(0,1)
                # If we got noticed, wake up and add aggro.
                if noticed:
                    mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$tgt has noticed $src's <a:SkillPickPocket>pick pocketing</a>!\\n",mob)
                    if tgt.sleep > 0:
                        tgt.cancelSleep()
                    tgt.addAggro(mob,10)
            
            if skip:
                mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src fails to remove the <a:Item%s>%s</a> from its victim. It's not as easy as it looks after all.\\n"%(GetTWikiName(item.itemProto.name),item.name),mob)
                return (False,True)
        
        # Try to give the item to the thief.
        if mob.player.giveItemInstance(item):
            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s successfully <a:SkillPickPocket>pick pockets</a> a <a:Item%s>%s</a>!\\n"%(item.character.name,GetTWikiName(item.itemProto.name),item.name))
            # Remove the pick pocketed item from the loot table.
            loot.items.remove(item)
            if not loot.tin and not len(loot.items):
                tgt.loot = None
            # If the mob was wearing the item pick pocketed,
            #  need to unequip it.
            if slot != -1:
                tgt.unequipItem(slot)
                tgt.mobInfo.refresh()
            return (True,True)
    
    # Try to take some money.
    if loot.tin:
        half = loot.tin / 2    # divide in half
        tin = loot.tin - half    # for odd numbers
        loot.tin = half
        
        worth = GenMoneyText(tin)
        mob.player.giveMoney(tin)
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"$src successfully <a:SkillPickPocket>pick pockets</a> %s.\\n"%worth,mob)
        if not loot.tin and not len(loot.items):
            tgt.loot = None
        return (True,True)
    # Pick pocket failed, probably because there was
    #  no money to be pick pocketed and player had no
    #  place for pick pocketed item to go into.
    else:
        if tgt.sleep > 0:  # wake up
            tgt.cancelSleep()
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src quickly retracts $srchis hand before $tgt notices $srchim.\\n",mob)
        return (True,True)


def DoBackstab(mob):
    if not mob.player:
        print "WARNING: Non-player mob attempting to backstab"
        return (False,False)
    
    tgt = mob.target
    
    # Check if we have a valid target.
    if not tgt or not AllowHarmful(mob,tgt):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillBackstab>backstab</a> failed, no valid target.\\n",mob)
        return (False,False)
    
    # Can't backstab targets more than 10 levels above own.
    if tgt.plevel - 10 > mob.plevel:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src lacks the skill to <a:SkillBackstab>backstab</a> $tgt, $tgt is too strong.\\n",mob)
        return (False,False)
    
    wpnRange = 0
    # Cannot backstab with impact or fists as weapons.
    # Wouldn't make sense.
    pweapon = mob.worn.get(RPG_SLOT_PRIMARY,None)
    if not pweapon or not pweapon.skill or pweapon.skill == "Fists":
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src cannot <a:SkillBackstab>backstab</a> with $srchis fists.\\n",mob)
        return (False,False)
    noBackstab = ("1H Impact","2H Impact")
    if pweapon.skill in noBackstab:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src cannot backstab with a %s weapon.\\n"%pweapon.skill,mob)
        return (False,False)
    # If we get here, mob carries a valid weapon for
    #  backstabbing, get range.
    if pweapon and pweapon.wpnRange > wpnRange:
        wpnRange = pweapon.wpnRange / 5.0
    
    # Check if target is within range.
    if GetRangeMin(mob,tgt) > wpnRange:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src cannot <a:SkillBackstab>backstab</a> $tgt, out of range.\\n",mob)
        return (False,False)
    
    # Check that we are behind the mob. (wmrojer)
    if not mob.isBehind(tgt):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src must be behind the enemy to be able to <a:SkillBackstab>backstab</a>.\\n",mob)
        return (False,False)
    
    # Backstab possible, add aggro.
    tgt.addAggro(mob,200)
    
    # Calculate the backstab damage done.
    bs = mob.skillLevels.get("Backstab",0) / 8
    spread = mob.level - tgt.level + 10
    if spread > 40:
        spread = 40
    dmgMod = 0.25 + spread * 0.09375
    backstabDamage = (randint(bs,bs * bs) + 300) * dmgMod
    
    # Damage the target.
    Damage(tgt,mob,backstabDamage,RPG_DMG_PHYSICAL,"backstabs",False)
    
    # Give a possible skill raise and give feedback of success.
    mob.character.checkSkillRaise("Backstab",3,3)
    mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
    mob.player.mind.callRemote("playSound","sfx/DarkMagic_ProjectileLaunch.ogg")
    return (True,True)


def DoRescue(mob):
    if not mob.player:
        print "WARNING: Non-player mob attempting to rescue"
        return (False,False)
    
    # Get all alliance members.
    allianceMembers = []
    for player in mob.player.alliance.members:
        for character in player.party.members:
            cmob = character.mob
            if cmob.pet:
                allianceMembers.append(cmob.pet)
            allianceMembers.append(cmob)
    
    # Cannot rescue oneself.
    if len(allianceMembers) <= 1:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "There is no one to <a:SkillRescue>rescue</a>.\\n")
        return (False,False)
    
    # Gather aggro on alliance members.
    # Always take highest aggro for a specific mob.
    aggro = {}
    for m in mob.zone.activeMobs:
        if m.player:
            continue
        for amob,amt in m.aggro.iteritems():
            if amob in allianceMembers:
                if amt > aggro.get(m,0):
                    aggro[m] = amt
    
    # If there is no aggro on any member, no one
    #  needs rescuing.
    if not len(aggro):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"There is no one in need of <a:SkillRescue>rescue</a>.\\n")
        return (False,False)
    
    # Increase aggro on rescuer for all mobs that have aggro
    #  on any alliance member above previous max aggro.
    for m,amt in aggro.iteritems():
        m.aggro[mob] = amt * 1.25
    
    # Give possible skill raise and feedback.
    mob.character.checkSkillRaise("Rescue")
    mob.player.sendGameText(RPG_MSG_GAME_BLUE,"$src <a:SkillRescue>rescues</a> the alliance!\\n",mob)
    mob.player.mind.callRemote("playSound","sfx/Fireball_Launch5.ogg")
    return (True,True)


# Okay, Evade... here goes!
def DoEvade(mob):
    if not mob.player:
        print "WARNING: Non-player mob attempting to evade"
        return (False,False)
    
    # Get all alliance members.
    allianceMembers = []
    for player in mob.player.alliance.members:
        for character in player.party.members:
            cmob = character.mob
            if cmob.pet:
                allianceMembers.append(cmob.pet)
            allianceMembers.append(cmob)
    
    # Can only evade aggro if there's someone else
    #  to take it.
    if len(allianceMembers) <= 1:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src needs a member of $srchis alliance to shift the focus of the aggressor onto.\\n",mob)
        return (False,False)
    
    # Gather aggro on alliance members.
    mobAggro = {}
    memberAggro = {}
    for m in mob.zone.activeMobs:
        if m.player:
            continue
        for amob,amt in m.aggro.iteritems():
            if amob == mob:
                if amt > mobAggro.get(m,0):
                    mobAggro[m] = amt
            elif amob in allianceMembers:
                if amt > memberAggro.get(m,0):
                    memberAggro[m] = amt
    
    # If there's no mob that has aggro on the user of the skill,
    #  then there's no one to evade.
    if not len(mobAggro):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src has no one to <a:SkillEvade>evade</a>.\\n",mob)
        return (False,False)
    
    # Evade is stronger the higher the skill level.
    slevel = mob.skillLevels.get("Evade",0)
    aggroMod = 0.05 * slevel / 1000.0
    # Evade all mobs that have aggro on the user and are
    #  already hostile towards another alliance member.
    # Don't create new aggro.
    for m,amt in mobAggro.iteritems():
        try:
            memberAmt = memberAggro[m]
        except:
            continue
        # One of skill users alliance members has highest aggro.
        # Decrease skill users aggro a bit.
        if amt < memberAmt:
            m.aggro[mob] -= int(ceil(aggroMod * m.aggro[mob]))
        # Skill user has highest aggro, decrease skill users aggro
        #  to something below an alliance members.
        else:
            m.aggro[mob] = memberAmt - int(ceil(aggroMod * m.aggro[mob]))
    
    # Give possible skillup and feedback.
    mob.character.checkSkillRaise("Evade")
    mob.player.sendGameText(RPG_MSG_GAME_BLUE,"$src <a:SkillEvade>evades</a> the focus of the aggressor!\\n",mob)
    mob.player.mind.callRemote("playSound","sfx/Fireball_Launch5.ogg")
    return (True,True)


def DoShieldBash(mob):
    tgt = mob.target
    
    # If there's no target, shield bash is impossible.
    if not tgt:
        if mob.player:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:SkillShieldBash>shield bash</a> failed, no target.\\n",mob)
        return (False,False)
    
    # Shield bash is only possible with a shield equipped.
    wshield = mob.worn.get(RPG_SLOT_SHIELD,None)
    if not wshield or not wshield.skill or wshield.skill != "Shields":
        if mob.player:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src cannot <a:SkillShieldBash>shield bash</a> without a shield.\\n",mob)
        return (False,False)
    
    # Check if target is within range.
    if GetRangeMin(mob,tgt) > 1:
        if mob.player:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"$src cannot <a:SkillShieldBash>shield bash</a> $tgt, out of range.\\n",mob)
        return (False,False)
    
    # Make target angry.
    tgt.addAggro(mob,15)
    
    # There will be further processing in the spell part of this skill.
    mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
    return (True,True)


#------------------------------------------------------


# Different skill specific functions. Each function should
#  return a tuple of two booleans, (success,used).
# If used is True, the skill had a valid target and was used.
# If success is True, the skill was successful and if there
#  is an effect tied to the skill as well, this one will be
#  executed.
SKILLS = {}
SKILLS['Assess']      = DoAssess
SKILLS['Backstab']    = DoBackstab
SKILLS['Disarm']      = DoDisarm
SKILLS['Evade']       = DoEvade
SKILLS['Pick Pocket'] = DoPickPocket
SKILLS['Rescue']      = DoRescue
SKILLS['Shield Bash'] = DoShieldBash


#------------------------------------------------------


# Process spell part of a skill.
# Return True if the skill fired, otherwise False.
# Return value gives no indication if skill was
#  successful or not, just if it got used.
def DoSkillSpell(mob,skillname):
    from projectile import Projectile
    from spell import SpawnSpell
    
    player = mob.player
    
    mobSkill = mob.mobSkillProfiles[skillname]
    classSkill = mobSkill.classSkill
    
    # Assert that mob knows the skill.
    skillLevel = mob.skillLevels.get(skillname,0)
    if not skillLevel:
        return False
    
    # Modify skill spells strength by skill level.
    mod = float(skillLevel) / float(classSkill.maxValue)
    
    # Clamp mod to produce at least 10% of maximum effect.
    if mod < .1:
        mod = .1
    
    proto = classSkill.spellProto
    
    # Get the appropriate target for this skill spell.
    tgt = mob.target
    if proto.target == RPG_TARGET_SELF:
        tgt = mob
    elif proto.target == RPG_TARGET_PARTY:
        tgt = mob
    elif proto.target == RPG_TARGET_ALLIANCE:
        tgt = mob
    elif proto.target == RPG_TARGET_PET:
        tgt = mob.pet
    elif player and proto.spellType&RPG_SPELL_HEALING and proto.target == RPG_TARGET_OTHER:
        tgt = GetPlayerHealingTarget(mob,tgt,proto)
    
    # If no valid target could be found, return in failure.
    # Here's one last chance to still acquire one.
    if not tgt:
        if player:
            if proto.spellType&RPG_SPELL_HARMFUL:
                from command import CmdTargetNearest
                CmdTargetNearest(mob,None,False,True)
                tgt = mob.target
                if not tgt:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Skill%s>%s</a> skill failed, no target.\\n"%(GetTWikiName(skillname),skillname),mob)
            else:
                tgt = mob
    # Still no target, now definitely abort skill.
    # If the mob is a player mob, message has already be sent.
    if not tgt:
        return False
    
    # For harmful skill spells, check if target may
    #  be harmed at all. Abort if not.
    if proto.spellType&RPG_SPELL_HARMFUL:
        if not AllowHarmful(mob,tgt) and not proto.aoeRange:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"$src's <a:Skill%s>%s</a> skill failed, no valid target.\\n"%(GetTWikiName(skillname),skillname),mob)
            return False
        if not player and not (mob.master and mob.master.player) and not IsKOS(mob,tgt):
            return False
    
    # If the skill spell isn't harmful and the target is hostile,
    #  retarget self.
    if not proto.spellType&RPG_SPELL_HARMFUL and mob.target == tgt:
        if tgt and IsKOS(tgt,mob):
            tgt = mob
    
    # Check for a skill raise.
    if mob.character:
        c = 10
        if mobSkill.reuseTime > 180:
            c = 5
        if mobSkill.reuseTime > 180*2:
            c = 3
        mob.character.checkSkillRaise(skillname,c)
    
    # Play animation and trigger particles if available.
    if proto.animOverride:
        mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,proto.animOverride)
    if len(proto.particleNodes):
        mob.zone.simAvatar.mind.callRemote("triggerParticleNodes",mob.simObject.id,proto.particleNodes)
    
    # Launch a projectile if necessary, otherwise spawn skill spell.
    if proto.projectile:
        p = Projectile(mob,mob.target)
        p.spellProto = proto
        p.launch()
    else:
        SpawnSpell(proto,mob,tgt,tgt.simObject.position,mod,skillname)
    
    # Return True, so skill was used.
    return True


def UseSkill(mob,tgt,skillname):
    if not mob or mob.detached or not mob.simObject:
        return
    
    player = mob.player
    
    # Check if mob is in a condition to use a skill.
    if 0 < mob.sleep or 0 < mob.stun or mob.isFeared:
        if player:
            player.sendGameText(RPG_MSG_GAME_DENIED, r'$src is in no condition to use a skill!\n', mob)
        return
 
    # Find the skill.
    mobSkill = mob.mobSkillProfiles.get(skillname,None)
    if not mobSkill:
        #todo, better warning
        if player:
            player.sendGameText(RPG_MSG_GAME_DENIED,"$src has lost $srchis ability in <a:Skill%s>%s</a>!\\n"%(GetTWikiName(skillname),skillname),mob)
        return
    
    classSkill = mobSkill.classSkill
    
    # Only passive skills don't have a reuse time.
    # Skip if such a skill should end up here.
    if not mobSkill.reuseTime:
        return
    # Can't use that skill yet.
    if mob.skillReuse.has_key(classSkill.skillname):
        return
    
    # If there is one, process the non-spell part
    #  of the skill.
    success = used = False
    if skillname in SKILLS:
        if skillname not in mob.skillLevels:
            traceback.print_stack()
            print "AssertionError: mob %s doesn't know the skill %s!"%(mob.name,skillname)
            return
        success,used = SKILLS[skillname](mob)
    else:
        success = True
    
    # If the non-spell part of the skill succeeded,
    #  continue with spell part if there is one.
    if success and classSkill.spellProto:
        used = DoSkillSpell(mob,skillname)
    
    # If the skill got actually used, set reuse timer.
    if used:
        mob.skillReuse[classSkill.skillname] = mobSkill.reuseTime
        # Also cancel feign death, unless this was the skill used.
        if skillname != "Feign Death":
            mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    
    # Player just did a special action which might have helped
    #  or hurt in PvP. Reset counter on encounter setting.
    if player:
        player.mind.callRemote("disturbEncounterSetting")


