# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup battle battle
#  @ingroup world
#  @brief The battle module provides both persistent data types and classes
#         providing flow logic for sequenced battles between two forces of
#         multiple mobs.
#  @{


import random
import traceback

from sqlobject import *
from mud.common.persistent import Persistent
from defines import *
from core import *
from messages import ZoneMessage, ZoneSound


## @brief Persistent data type defining a group of mobs (SpawnGroup) that will
#         spawn during a BattleSequence.
class BattleGroup(Persistent):

    # Attributes.
    ## @brief (Persistent String) SpawnGroup associated with the SpawnPoint in 
    #         mission file.
    triggerSpawnGroup = StringCol(default="")
    ## @brief (Persistent String) The groupName of the SpawnGroup being spawned.
    spawnGroup = StringCol(default="")
    ## @brief (Persistent Integer) Delay before spawned Mobs in the spawnGroup 
    #         will begin to attack Mobs belonging to opposing BattleGroups if 
    #         this BattleGroup is not passive.
    #  @details Delay counts down 18 per tick, with the countdown throttled
    #           to occur once every 6 ticks.  Countdown logic handled in
    #           BattleSide.tick().
    attackDelay = IntCol(default=0)
    ## @brief (Persistent Integer) Indicates the aggresive or non-aggresive
    #         behavior of spawns.
    passive = BoolCol(default=False)

    # Relationships.
    ## @brief (Persistent BattleSequence) BattleSequence of which the
    #         BattleGroup is a part.
    battleSequence = ForeignKey('BattleSequence', default=None)


## @brief Persistent data type defining an event processed in a BattleProto.
#  @details BattleSequences can setup a linked-list.  This alows for a simple
#           state machine that will move to the next BattleSequence in overall
#           sequence.  BattleSequences can spawn BattleGroups, send a message
#           or play a sound to all Players in a ZoneInstance.
class BattleSequence(Persistent):

    # Attributes.
    ## @brief (Persistent String) Sound played to all Players in a ZoneInstance.
    zoneSound = StringCol(default="")
    ## @brief (Persistent String) Message send to all Players in a ZoneInstance.
    zoneMessage = StringCol(default="")
    ## @brief (Persistent Integer) Delay till a BatteSequence triggers once it
    #         is the active sequence.
    #  @details Delay counts down 3 per tick, with 2 ticks occuring a second.
    delay = IntCol(default=0)

    # Relationships.
    ## @brief (Persistent BattleGroup List) BattleGroups spawned during the
    #          BattleSequence.
    battleGroups = MultipleJoin('BattleGroup')
    ## @brief (Persistent BattleSequence) The BattleSequence that begins after 
    #         this sequence ends.
    nextSequence = ForeignKey("BattleSequence", default=None)


## @brief Persistent data type defining events processed at the end of a Battle.
#  @details This can spawn a group of mobs (SpawnGroup), send a message or
#           play a sound to all Players in a ZoneInstance.
class BattleResult(Persistent):

    # Attributes.
    ## @brief (Persistent String) SpawnGroup associated with the SpawnPoint in 
    #         mission file.
    triggerSpawnGroup = StringCol(default="")
    ## @brief (Persistent String) The groupName of the SpawnGroup being spawned.
    spawnGroup = StringCol(default="")
    ## @brief (Persistent String) Sound played to all Players in a ZoneInstance.
    zoneSound = StringCol(default="")
    ## @brief (Persistent String) Message send to all Players in a ZoneInstance.
    zoneMessage = StringCol(default="")


## @brief Persistent data type defining a Spawn that must survive during a
#         Battle for a specific BatteProto.
class BattleMustSurvive(Persistent):
    # Attributes.
    ## @brief (Persistent String) Spawn name of Mob in a BattleGroup that must
    #         survive.
    #  @details If a Mob of this Spawn type is detached, the BattleSide with
    #           the BattleSeuqence that had the BattleGroup containing the
    #           Spawn will forfeit the Battle.
    name = StringCol()

    # Relationships.
    ## @brief (Persistent BattleProto) BattleProto that requires the Mob to
    #          survive.
    battleProto = ForeignKey('BattleProto')


## @brief Persistent data type defining the contents of scripted battle between
#         two sides.
class BattleProto(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of the BattleProto.  This must be unique.
    name = StringCol(alternateID=True)
    ## @brief (Persistent String) Name of the Zone in which the Battle takes
    #         place.
    zoneName = StringCol(default="")
    ## @brief (Persistent String) Message send to all Players in a ZoneInstance.
    zoneMessage = StringCol(default="")
    ## @brief (Persistent String) Sound played to all Players in a ZoneInstance.
    zoneSound = StringCol(default="")

    # Relationships.
    ## @brief (Persistent BattleSequence) Side 1's beginning BattleSequence for
    #         the Battle.
    side1StartSequence = ForeignKey('BattleSequence', default=None)
    ## @brief (Persistent BattleSequence) Side 2's beginning BattleSequence for
    #         the Battle.
    side2StartSequence = ForeignKey('BattleSequence', default=None)
    ## @brief (Persistent BattleResult) Side 1's victory BattleResult for the
    #         Battle.
    side1VictoryResult = ForeignKey('BattleResult', default=None)
    ## @brief (Persistent BattleResult) Side 2's victory BattleResult for the
    #         Battle.
    side2VictoryResult = ForeignKey('BattleResult', default=None)
    ## @brief (Persistent BattleResult) Side 1's defeat BattleResult for the
    #         Battle.
    #  @deprecated TWS: Are defeat results even used?
    side1DefeatResult = ForeignKey('BattleResult', default=None)
    ## @brief (Persistent BattleResult) Side 2's defeat BattleResult for the
    #         Battle.
    #  @deprecated TWS: Are defeat results even used?
    side2DefeatResult = ForeignKey('BattleResult', default=None)
    ## @brief (Persistent BattleMustSurvive List) Mobs that must survive during
    #         a Battle.
    battleMustSurvive = MultipleJoin('BattleMustSurvive')


## @brief Object encapsulating the behavior and management of a single side
#         participating in a Battle.
class BattleSide:

    ## @brief Initialize class.
    #  @param self (BattleSide) The object pointer.
    #  @todo Should accept params and initialize values instead of having
    #        instantiator initialize values.
    def __init__(self):

        ## @brief (BattleProto) The Battle of which the BattleSide is a member.
        self.battle = None

        ## @brief (ZoneInstance) The ZoneInstance in which the BattleSide
        #          resides.
        self.zone = None

        ## @brief (Integer) Delay (3 per tick) till a sequence is triggered.
        self.delay = 0

        ## @brief (BattleSequence) The next BattleSequence to trigger.
        self.sequence = None

        ## @brief (Dictionary) Contains BattleGroups (key) and a list of mobs in
        #         each BattleGroup (value).
        self.battleGroups = {}

        ## @brief (Dictionary) Attack timers (value) for BattleGroups (key).
        self.battleGroupAttackTimers = {}

        ## @brief (Integer) Stores a tick timer used for tracking when 
        #         updateMobTarget is called.
        self.thinkTimer = 0

        ## @brief (Booean) Inidicates if the BattleSide has forfeighted.
        #  @todo TWS: Should really just update a refernce to this BattleSide
        #        in the Battle.  BattleSide does not care if it has forfeighed.
        self.forfeit = False

        ## @brief (Mob List) List of all mobs belonging to this BattleSide.
        self.mobs = []


    ## @brief Trigger the current BattleSequence, and shift to the next
    #         BattleSequence.
    #  @param self (BattleSide) The object pointer.
    #  @return None.
    def triggerSequence(self):

        # If the BattleSide has not been assigned a BattleSequence, then return
        # early.
        if not self.sequence:
            traceback.print_stack()
            print "AssertionError: battle side has no sequence assigned!"
            return

        # Clear mob information (BattleGroup, attack timers, mob list) for
        # previous BattleSequence.
        self.battleGroups = {}
        self.battleGroupAttackTimers = {}
        self.mobs = []

        # Make a local handle to the BattleSequence being triggered.
        sequence = self.sequence

        # If the BattleSequence has a ZoneMessage, then send the message to each
        # Player in the ZoneInstance.
        if sequence.zoneMessage:
            ZoneMessage(self.zone, sequence.zoneMessage)

        # If the BattleSequence has a ZoneSound, then play the sound to each
        # Player in the ZoneInstance.
        if sequence.zoneSound:
            ZoneSound(self.zone, sequence.zoneSound)

        # For each BattleGroup, process any spawns, and setup attack timers.
        for bg in sequence.battleGroups:
            
            # Create an empty batte group list.
            self.battleGroups[bg] = []
            
            # Set the BattleGroup's attack timer based on the BattleGrou's
            # attackDelay.
            self.battleGroupAttackTimers[bg] = bg.attackDelay

            # Used to store a handle to the SpawnGroup.
            override = None

            # If the BattleGroup has a SpawnGroup groupName, then find the
            # SpawnGroup.
            if bg.spawnGroup:

                # Iterate over the Zone's SpawnGroups.
                for sg in self.zone.zone.spawnGroups:
                    
                    # If the SpawnGroup was found, then set a handle to the
                    # SpawnGroup.
                    if sg.groupName == bg.spawnGroup:
                        
                        # Set a handle to the SpawnGroup.
                        override = sg
                        
                        # The SpawnGroup was found, so exit the loop.
                        break

                # Iterate over the ZoneInstance's SpawnPoints.
                for sp in self.zone.spawnpoints:

                    # If the SpawnPoint is associated with the SpawnGroup
                    # being triggered, then spawn the SpawnGroup.
                    if sp.groupName == bg.triggerSpawnGroup:

                        # Spawn the SpawnGroup at the SpawnPoint.
                        mob = sp.triggeredSpawn(override)

                        # If a Mob was succesfully spawned, then attach the
                        # newly spawned Mob to the BattleSide and Battle.
                        if mob:
                            
                            # Attach the Mob to the BattleGroup.
                            self.battleGroups[bg].append(mob)
                            
                            # Attach the Mob to the BattleSide.
                            self.mobs.append(mob)
                            
                            # Set the Mob to be associated with this Battle.
                            mob.battle = self.battle

        # Setup the next BatteSequence that will be triggered.
        self.sequence = sequence.nextSequence


    ## @brief Updates a Mob's attack target.
    #  @param self (BattleSide) The object pointer.
    #  @param mob (Mob) The mob whose target will be updated.
    #  @return None.
    #  @todo TWS: Optimize.  Does the enemy side ever change?  If not, why
    #        determine it each time this is called for every mob.
    def updateMobTarget(self, mob):

        # If the mob is already fighting another mob, then return early.
        if mob.target:
            return

        # Find the opposing BattleSide.
        oside = self.battle.side1
        if oside == self:
            oside = self.battle.side2

        # Randomly select a mob from the opposing BattleSide.
        x = len(oside.mobs)
        if x:
            if x > 1:
                x = random.randint(0, x-1)
            else:
                x = 0
            target = oside.mobs[x]

            # The commented code finds the closest enemy instead of picking a
            # random one
            # target = None
            # best = 1000000
            # for omobs in oside.battleGroups.values():
            #    for omob in omobs:
            #        r = GetRange(mob,omob)
            #        if r < best:
            #            best = r
            #            target = omob

            # If the selected target is available, not detached (dead), and the
            # target is not in the mob's aggro list, then add the target to
            # the mob's aggro list.  After this, standard target selection code
            # and AI will occur.
            if target and not target.detached:
                if target not in mob.aggro.keys():
                    mob.addAggro(target, 10)


    ## @brief Routine management of a BattleSide.  Responsible for triggering
    #         BattleSequences, BattleGroup AI, and determining defeat.
    #  @param self (BattleSide) The object pointer.
    #  @return (Boolean) True if the BattleSide is defeated.  Otherwise, False.
    #  @bug TWS: Possible bug.  If there is a delay on the last sequence, then
    #       delay will decrease, but since the sequence has not triggered, the
    #       battle group length will be zero and there will be no more sequence
    #       so defeat will be returned!  Possible solutions: if there is a delay,
    #       then only handle the delay and ignore other functionality.
    #  @todo Battle group attack timers get throttled with the think timer.  This
    #        may not be the behavior desired, but might be required to control
    #        process resources.
    #  @todo TWS: Optimize: In think logic, just check if attack timer is greater
    #        than 18, if so, decrement and continue.  At the end of the for loop,
    #        the group is guaranteed to be in an attackable update state.
    #  @todo TWS: Optimize: Do not loop over each mob calling updateMobTarget.
    #        Either change updateMobTarget to support a list or use map.
    def tick(self):

        # If there is a delay, then countdown.
        if self.delay:
            
            # Countdown the delay.
            self.delay -= 3

            # If the delay has been satisfied, then a sequence needs triggered.
            if self.delay <= 0:
                
                # Clear the delay timer.  This prevents counting down the delay
                # more and triggering another sequence.
                self.delay = 0
                
                # Trigger the BattleSequence.
                self.triggerSequence()

        # If all of the BattleGroups have died, then check if defeat has
        # occured or if another BattleSequence needs triggered.
        if not len(self.battleGroups):

            # If this was the last BattleSequence, then this BattleSide has
            # been defeated.
            if not self.sequence:
                
                # Return True to indicate the BattleSide has been defeated as
                # there are no more BattleSequences to trigger.
                return True

            # Set a delay.  When the next time tick is invoked, it will begin
            # counting down the delay and eventually trigger the BattleSequence.
            self.delay = self.sequence.delay + 3

        # Otherwise, there are BattleGroups alive.
        else:

            # Countdown think timer.
            self.thinkTimer -= 3

            # If the think timer has been satisfied, then think.
            if self.thinkTimer <= 0:
                
                # Reset think timer.
                self.thinkTimer = 18

                # Iterate over all BattleGroups.
                for bg, mobs in self.battleGroups.iteritems():

                    # If the BattleGroup is passive, then skip it.
                    if bg.passive:
                        continue

                    # If the BattleGroup has an attack delay, then count it
                    # down.
                    if self.battleGroupAttackTimers.get(bg) > 0:
                        self.battleGroupAttackTimers[bg] -= 18

                    # If the attack timer has been satisfied, then update the
                    # mob's targets.
                    if self.battleGroupAttackTimers.get(bg) <= 0:

                        # For each mob in the BattleGroup, update the Mob's
                        # target.
                        for mob in mobs:
                            self.updateMobTarget(mob)


        # Return False to indicate no defeat occured.  There are either mobs
        # alive or more BattleSequences to trigger.
        return False


    ## @brief Detach a Mob from the BattleSide.
    #  @param self (BattleSide)The object pointer.
    #  @param mob (Mob) The mob being detached from the BattleSide.
    #  @return (Boolean) True if the Mob was detached.  Otherwise, False.
    def detachMob(self, mob):

        # Iterate over BattleGroups.
        for bg, mobs in self.battleGroups.iteritems():

            # If the mob being detached is in the BattleGroup.
            if mob in mobs:

                # Remove the mob from the BattleGroup.
                mobs.remove(mob)

                # Remove the mob from the BattleSide.
                self.mobs.remove(mob)

                # If there are no more mobs in the Battlegroup, then delete the
                # BattleGroup.
                if not len(mobs):
                    del self.battleGroups[bg]

                # Return True since the mob was detached.
                return True

        # Return False since the mob was not in any of the BattleGroups for
        # this BattleSide.
        return False


## @brief Battle provides a means to initiate a scripted battle between two
#         sides.
#  @details Battle is a controller for two opposing BattleSides.  It is
#           responsible for initiating both BattleSides, routinely calling
#           each side's heartbeat method, and processing results of the Battle.
class Battle:

    ## @brief Initialize class based on the provided BattleProto.
    #  @param self (Battle) The object pointer.
    #  @param zone (ZoneInstance) The ZoneInstance in which the Battle will
    #              occur.
    #  @param bproto (BattleProto) The BattleProto to load and use for this 
    #                Battle.
    def __init__(self, zone, bproto):

        ## @brief (Boolean) Indicates if the Battle has finished.
        self.over = False

        ## @brief (Boolean)  Indicates if a side has forfeighted.
        #  @todo TWS: Should this just be a reference to a BattleSide?
        self.forfeit = False

        ## @brief (String) The name of the Batte.
        self.name = bproto.name

        ## @brief (ZoneInstance) The ZoneInstance in which the Batte will occur.
        self.zone = zone

        # Add the battle to the ZoneInstance's battle list.
        zone.battles.append(self)

        ## @brief (BatteProto) The BatteProto to load and use for this Battle.
        self.battleProto = bproto

        ## @var side1
        #  @brief (BattleSide) Side1 is the BattleSide opposing Side2.
        
        ## @var side2
        #  @brief (BattleSide) Side2 is the BattleSide opposing Side1.

        # Create both BatteSide.
        side1 = self.side1 = BattleSide()
        side2 = self.side2 = BattleSide()

        # Assosciate each BattleSide with this Batte.
        side1.battle = self
        side2.battle = self

        # Get the start sequences for from the BattleProto.
        s1seq = bproto.side1StartSequence
        s2seq = bproto.side2StartSequence

        # If there are no sequences, then return early.
        if not s1seq or not s2seq:
            traceback.print_stack()
            print "AssertionError: battle %s is missing a start sequence!" \
                % self.name
            return

        # TWS: These should really be set as part of init'ing the side.
        side1.zone = zone
        side2.zone = zone
        side1.sequence = s1seq
        side2.sequence = s2seq

        # Initial delays for actions.  This is required so that the sequence 
        # will be counted down and may trigger for the Battleside.
        side1.delay = s1seq.delay + 3
        side2.delay = s2seq.delay + 3

        ## @brief (String List) Contains names of mobs that must survive.
        self.battleMustSurvive = []
        
        # Populate the names of mobs that must survive based on the BattleProto.
        for ms in bproto.battleMustSurvive:
            self.battleMustSurvive.append(ms.name)

        # If the BattleProto has a ZoneMessage, then send the message to each
        # Player in the ZoneInstance.
        if bproto.zoneMessage:
            ZoneMessage(zone, bproto.zoneMessage)

        # If the BattleProto has a ZoneSound, then play the sound to each Player
        # in the ZoneInstance.
        if bproto.zoneSound:
            ZoneSound(zone, bproto.zoneSound)


    ## @brief Detach a Mob from the Battle.
    #  @param self (Battle) The object pointer.
    #  @param mob (Mob) The mob being detached from the Battle.
    #  @return None.
    #  @todo TWS: Optimize.  If it detaches from side1, should it attempt to
    #             detach from side2?  (if/else)?
    #  @todo TWS: Optimize.  Shoud a mob known to which group or side it
    #        belongs? Might be better as it allows for a direct call
    #        instead of iterating the battlegroups.  
    def detachMob(self, mob):

        # Flag indicating if a forfeit is to occur.
        forfeit = False

        # If the mob was in the must survive list, then if a forfeit has not 
        # occured yet, announce the mob's death to the Players in the
        # ZoneInstance and set a forfeit to occur.
        if mob.spawn.name in self.battleMustSurvive and not self.forfeit:
            ZoneMessage(self.zone, "%s has been slain!!!" % mob.spawn.name)
            forfeit = self.forfeit = True

        # Attempt to deatch the mob for side1.  If the mob was succesfully
        # detached from side1, then a forfeit may occur.
        if self.side1.detachMob(mob):

            # If the forfeit flag is set, then side1 will forfeight.
            if forfeit:
                self.side1.forfeit = True

        # Attempt to deatch the mob for side2.  If the mob was succesfully
        # detached from side2, then a forfeit may occur.
        if self.side2.detachMob(mob):

            # If the forfeit flag is set, then side2 will forfeight.
            if forfeit:
                self.side2.forfeit = True


    ## @brief End of a Battle.  Resets conditions back to pre-battle settings.
    #  @param self (Battle) The object pointer.
    #  @return None.
    def end(self):

        # Set the Battle as being over.
        self.over = True

        # Removes the Battle from the ZoneInstance.
        self.zone.battles.remove(self)

        # Set all mobs in the Battle to despawn in 10 minutes.
        for m in self.side1.mobs:
            m.despawnTimer = 60 * 10 * 6
        for m in self.side2.mobs:
            m.despawnTimer = 60 * 10 * 6


    ## @brief Updates a Mob's attack target.
    #  @details Delegates responsibility to the Mob's BattleSide.
    #  @param self (Battle) The object pointer.
    #  @param mob (Mob) The mob whose target will be updated.
    #  @return None.
    #  @remarks TWS: Would it be better set the sides updateMobTarget
    #           as a function-pointer Mob attribute?
    def updateMobTarget(self, mob):

        # Find the BatteSide the Mob is on and update the Mob's attack target.
        if mob in self.side1.mobs:
            self.side1.updateMobTarget(mob)
        else:
            self.side2.updateMobTarget(mob)


    ## @brief Processes a BattleResult.
    #  @param self (Battle) The object pointer.
    #  @param result (BattleResult) The BattleResult being processed.
    #  @return None.
    #  @todo TWS: Overly compicated spawning, redo flow.
    def doResult(self, result):

        # If the BattleProto has a ZoneMessage, then send the message to each
        # Player in the ZoneInstance.
        if result.zoneMessage:
            ZoneMessage(self.zone, result.zoneMessage)

        # If the BattleProto has a ZoneSound, then play the sound to each
        # Player in the ZoneInstance.
        if result.zoneSound:
            ZoneSound(self.zone, result.zoneSound)


        # Used to store a handle to the SpawnGroup.
        override = None

        # If the result has a SpawnGroup groupName, then find the SpawnGroup.
        if result.spawnGroup:

            # Iterate over the Zone's SpawnGroups.
            for sg in self.zone.zone.spawnGroups:
                
                # If the SpawnGroup was found, then set a handle to the
                # SpawnGroup.
                if sg.groupName == result.spawnGroup:
                    
                    # Set a handle to the SpawnGroup.
                    override = sg
                    
                    # The SpawnGroup was found, so exit the loop.
                    break

            # Iterate over the ZoneInstance's SpawnPoints.
            for sp in self.zone.spawnpoints:

                # If the SpawnPoint is associated with the SpawnGroup being
                # triggered, then spawn the SpawnGroup.
                if sp.groupName == result.triggerSpawnGroup:

                    # Spawn the SpawnGroup at the SpawnPoint.
                    mob = sp.triggeredSpawn(override)

                    # If a Mob was succesfully spawned, then set the Mob to
                    # despawn in 10 minutes and associate it with this Battle.
                    if mob:
                        
                        # Set the Mob to depsawn in 10 minutes.
                        mob.despawnTimer = 60*10*6
                        
                        # Set the Mob to be associated with this Battle.
                        mob.battle = self


    ## @brief Routine management of a Battle.  Invokes management for each
    #         BattleSide, and check for end Battle conditions.
    #  @param self (Battle) The object pointer.
    #  @return None.
    def tick(self):

        # Flag indicating if the Battle has ended.
        end = False

        # Stores a handle to the Result (if any) when a Battle ends.
        result = None

        # Invoke side1's management.  If side1's management indicates defeat or
        # side1 has forfeighted, then the Battle is ending.
        if self.side1.tick() or self.side1.forfeit:

            # The Battle is ending, side1 has lost.
            end = True

            # Side2 has won.  Use side2's victory result.
            result = self.battleProto.side2VictoryResult

            # Remove all of side1's mobs from the ZoneInstance.
            for m in self.side1.mobs[:]:
                m.zone.removeMob(m)

        # Invoke side2's management.  If side2's management indicates defeat or
        # side2 has forfeighted, then the Battle is ending.
        if self.side2.tick() or self.side2.forfeit:

            # The Battle is ending, side2 has lost.
            end = True

            # Side1 has won.  Use side1's victory result.
            result = self.battleProto.side1VictoryResult

            # Remove all of side2's mobs from the ZoneInstance.
            for m in self.side2.mobs[:]:
                m.zone.removeMob(m)

        # If one of the sides have forfeighted, then process BattleResults and
        # end the Battle.
        if end:

            # If there are any results, then end the process the
            # victor's BattleResult.
            if result:
                self.doResult(result)

            # End the Battle.
            self.end()


## @} # End battle group.
