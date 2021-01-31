# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import mud.world.faction
from mud.world.core import *
from mud.world.defines import *
from mud.world.shared.vocals import *

from collections import defaultdict



class Tactical:
    def __init__(self, mob):
        self.mob = mob
    
    
    # Consider a mob for adding to this tacticals mob.
    def doMob(self, otherMob):
        # Get a handle to this processes mob.
        mob = self.mob
        
        #todo factions
        
        # If the other mob has been flagged to draw no aggro, skip.
        # ("/imm myaggro off" as an example)
        if otherMob.aggroOff:
            return
        
        # A new enemy, so perform some additional checks.
        if not mob.aggro.has_key(otherMob):
            
            # Get range to target and our aggro range.
            tgtRange = GetRange(mob,otherMob)
            aggroRange = mob.aggroRange * mob.zone.zone.aggroMod
            
            # Get target visibility.
            vis = otherMob.visibility + mob.seeInvisible
            # Clamp visibility to [0.001;1].
            # Lower end needs to be unequal zero because of following division.
            if vis < 0.001:
                vis = 0.001
            if vis > 1:
                vis = 1
            
            # Modify the target range by the targets visibility.
            # If the visibility is < 1, the perceived range will increase.
            tgtRange /= vis
            
            # Check if the target is in our aggro range.
            if tgtRange < aggroRange:
                # In aggro range, so we got us a new enemy!
                
                # If the other mob is sneaking, could still escape our perception.
                if otherMob.sneak:
                    # Get the other mobs skill level in sneaking.
                    sn = otherMob.skillLevels.get("Sneak",0)
                    # Check if we are able to notice the new enemy.
                    # Can't sneak past level 90 and higher mobs.
                    if mob.plevel >= 90 or sn + 100 < mob.plevel * 10:
                        otherMob.cancelStatProcess("sneak","$tgt has been noticed!\\n")
                    else:
                        return
                
                # Add aggro for the new enemy.
                mob.addAggro(otherMob,10)
        
        # Otherwise we already hate this target.
        else:
            # We are observing this target, so it should be impossible to sneak by.
            if otherMob.sneak:
                otherMob.cancelStatProcess("sneak","$tgt has been noticed!\\n")
    
    
    # The tactical tick function, update tactical map and assign new target.
    def tick(self):
        # Get a handle to this processes mob.
        mob = self.mob
        
        # If aggro has been disabled world-wide, don't update tactical.
        if not mob.zone.world.aggroOn:
            return
        
        # If the mob is a player or detached, don't bother updating tactical.
        if mob.player or mob.detached:
            return
        
        # Get handles to the zone and the zones sim avatar.
        zone = mob.zone
        simAvatar = zone.simAvatar
        
        # Store a flag if the mob processed needs to update its target.
        doNewAggro = not mob.target
        
        # If the mob processed has no aggro range, there's no need to
        #  build the tactical map.
        # Also skip building the tactical map if the current mob is part
        #  of a battle, aggro in battle is handled specially so the two
        #  sides continue to fight each other.
        if mob.aggroRange and not mob.battle:
            
            # Build up the tactical map.
            for id in mob.simObject.canSee:
                
                # Try to find the other mob in can see.
                try:
                    otherMob = zone.mobLookup[simAvatar.simLookup[id]]
                # If the mob can't be found, the other mob hasn't spawned yet
                #  but is already in can see.
                except KeyError:
                    continue
                
                # Never aggro on self.
                if mob == otherMob:
                    continue
                
                # Already detached but still in can see, skip.
                if not otherMob.player and otherMob.detached:
                   continue
                
                # Can't attack invulnerable mobs.
                if otherMob.invulnerable > 0:
                    continue
                
                # Mobs lower than level 50 only attack if the target
                #  is less than 20 levels above them.
                if mob.plevel < 50:
                    if mob.plevel < otherMob.plevel - 20:
                        continue
                
                # If the target mob doesn't have an area to defend,
                #  check next mob.
                if not otherMob.aggroRange:
                    continue
                
                # Player mobs don't initiate.
                if mob.master and mob.master.player:
                    if not mob.aggro.get(otherMob,0):
                        continue
                
                # Don't interfere with battles, aggro there is handled
                #  specially, so the two sides will continue fighting
                #  each other.
                if otherMob.battle:
                    continue
                
                # If we don't hate the target, check for assistance.
                if not IsKOS(mob,otherMob):
                    # Never check for assistance with pets, they should
                    #  inherit this from their master.
                    if mob.master or otherMob.master:
                        continue
                    
                    # If the other mob is no player, check if the other
                    #  mob would assist us.
                    if not otherMob.player:
                        if otherMob.assists and mob.realm == otherMob.realm:
                            # Copy aggro list over to friendly assisting mob
                            #  if current mob is in other mobs aggro range.
                            if GetRange(mob,otherMob) <= (otherMob.spawn.aggroRange * mob.zone.zone.aggroMod) * .65:
                                for m in mob.aggro.iterkeys():
                                    if not otherMob.aggro.get(m,0):
                                        otherMob.addAggro(m,5)
                    
                    # Otherwise check if we would assist the player mob.
                    # Such assistance is only provided in PvP fights, normal
                    #  mobs get their separate aggro check to prevent fights
                    #  with invalid targets.
                    # Note: is this functionality here even needed? It might
                    #  prove useful if there ever are different realms that
                    #  do not hate each other. Otherwise it will just add
                    #  unnecessary calculations as the mob will aggro the
                    #  additional targets anyway.
                    else:
                        # Check if we want to assist.
                        if mob.assists and mob.realm == otherMob.realm:
                            # Only treat the current other mob. The remaining
                            #  party members get treated automatically when
                            #  running through the list of mobs in canSee.
                            # First check if the player mob is in aggro range.
                            if GetRange(mob,otherMob) <= (mob.spawn.aggroRange * mob.zone.zone.aggroMod) * .65:
                                # Run through the list of mobs hostile
                                #  to the player.
                                for m in otherMob.aggro.iterkeys():
                                    # Only consider valid player mobs.
                                    if not m.player or m.detached:
                                        continue
                                    # If we don't hate the target anyway...
                                    if not mob.aggro.get(m,0):
                                        # New possible target has to be of different
                                        #  realm. Only assist if both players can
                                        #  engage each other and the new target is
                                        #  in sight.
                                        if m.realm != mob.realm and AllowHarmful(m,otherMob) and m.simObject.id in mob.simObject.canSee:
                                            mob.addAggro(m,5)
                    
                    # Other mob has been handled, so continue to the next.
                    continue
                
                # From here on otherMob is clearly evil, at least
                #  from our perspective.
                
                # If we haven't already a target assigned...
                if doNewAggro:
                    # If the target is a player, need to run through
                    #  all party members and check for initial aggro.
                    if otherMob.player:
                        # Store if we already hate this player.
                        initial = not mob.aggro.get(otherMob,0)
                        # Run through all the players mobs.
                        for c in otherMob.player.party.members:
                            if c.mob.detached:
                                continue
                            # Consider the other mob for addition to our aggro list.
                            self.doMob(c.mob)
                        # If we didn't hate the player before but do now, modify
                        #  the aggro on each member such that we hate the party
                        #  members in their order in the party. This allows for
                        #  tactical positioning in the party (tanks first). Also
                        #  aggro on the characters pet instead of the character
                        #  directly if present.
                        if initial and mob.aggro.get(otherMob,0):
                            # Set initial aggro modifier.
                            a = 10
                            # Run through all party members.
                            for member in otherMob.player.party.members:
                                # Skip detached or sneaking party members, they don't
                                #  draw additional aggro.
                                if not member.mob.detached and not member.mob.sneak:
                                    # If the target has a pet, add more aggro to that.
                                    if member.mob.pet:
                                        mob.addAggro(member.mob.pet,a)
                                    # Otherwise focus on the character.
                                    else:
                                        mob.addAggro(member.mob,a)
                                    # Decrease aggro modifier each step.
                                    a -= 1
                    else:
                        # Consider the other mob for addition to our aggro list.
                        self.doMob(otherMob)
        
        # If there are possible targets in sight and range...
        if len(mob.aggro):
            mostHated = None
            bestAggro = -999999
            bestRange = 999999
            bestRangeAggro = -999999
            bestRangeMob = None
            
            # If we already have a target, take it into consideration.
            if mob.target:
                bestRange = GetRange(mob,mob.target)
                if bestRange <= mob.followRange or mob.battle:
                    bestRangeAggro = bestAggro = mob.aggro.get(mob.target,0)
                    if bestAggro:
                        mostHated = mob.target
                        bestRangeMob = mob.target
            
            # Now run through the whole aggro list to determine best target.
            for m,hate in mob.aggro.iteritems():
                # Ignore targets that are feigning death.
                if m.feignDeath:
                    continue
                
                if hate:
                    testRange = GetRange(mob,m)
                    if testRange <= mob.followRange or mob.battle:
                        if hate > bestAggro: #XXX: do a hate falloff on distance
                            bestAggro = hate
                            mostHated = m
                        if testRange < bestRange:
                            bestRange = testRange
                            bestRangeAggro = hate
                            bestRangeMob = m
            
            # If we can't attack most hated or move to attack,
            #  attack nearest mob if available.
            if mob.move <= 0 and bestRangeMob:
                # Check if we can reach our most hated target.
                crange = GetRangeMin(mob,mostHated)
                wpnRange = 0
                # Take highest weapon range.
                pweapon = mob.worn.get(RPG_SLOT_PRIMARY)
                sweapon = mob.worn.get(RPG_SLOT_SECONDARY)
                if pweapon and pweapon.wpnRange > wpnRange:
                    wpnRange = pweapon.wpnRange / 5.0
                if sweapon:
                    secondaryRangeAdjusted = sweapon.wpnRange / 5.0
                    if secondaryRangeAdjusted > wpnRange:
                        wpnRange = secondaryRangeAdjusted
                # Target is too far away, we can't reach it.
                if crange > wpnRange:
                    mostHated = bestRangeMob
                    bestAggro = bestRangeAggro
            # If we found a viable target...
            if mostHated:
                # Player pets don't attack that quickly, check for threshold.
                if mob.master and mob.master.player:
                    if bestAggro < RPG_PLAYERPET_AGGROTHRESHOLD * mob.level:
                        zone.setTarget(mob,None)
                        return
                # If the target is feared and has a master, switch to master
                #  if possible.
                if mostHated.isFeared and mostHated.master:
                    master = mostHated.master
                    if mob.aggro.has_key(master):
                        testRange = GetRange(mob,master)
                        if testRange <= mob.followRange or mob.battle:
                            mostHated = master
                if mostHated != mob.target:
                    # Alert and vocalization
                    snd = mob.spawn.getSound("sndAlert")
                    if snd:
                        mob.playSound(snd)
                    else:
                        mob.vocalize(VOX_MADSCREAM)
                    
                    zone.setTarget(mob,mostHated)
                    
                # set combat timer
                if mostHated.combatTimer < 72:
                    mostHated.combatTimer = 72
            # There's no possible target to attack,
            #  calm down.
            else:
                mob.aggro = defaultdict(int)
                if mob.target:
                    zone.setTarget(mob,None)
        
        # We don't hate anyone, calm down.
        else:
            zone.setTarget(mob,None)


