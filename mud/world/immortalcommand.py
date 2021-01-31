# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import math
from defines import *
from zone import Zone
from spawn import Spawn
from core import *
import sys
from mud.common.permission import User
from damage import XPDamage



# Volatile dictionaries for the immortal stasis functionality.
# As this generally won't be used in large scale, adding a
#  separate attribute to mobs just for this functionality
#  wouldn't make much sense.
# STASISDICT is a dictionary with zones as keys and zone dictionaries
#  as values which have a group name as key and a list with first element
#  being a set of mobs and second element a flag if the group is in stasis
#  as values.
STASISDICT = {}
# MOB_STASISDICT is a dictionary with zones as keys and zone dictionaries
#  as values which have a mob as key and a list with first element being
#  group name and second element being a flag if the related mob is in
#  stasis or not as values.
MOB_STASISDICT = {}

# Helper function for stasis groups, add a mob to a specific stasis group
#  and if already present resync stasis status.
def addMobToStasisGroup(mob, groupName):
    # Get the zone.
    zone = mob.zone
    # Get the stasis group zone dictionary.
    zoneDict = STASISDICT.setdefault(zone,{})
    # Add the mob to the group.
    group = zoneDict.setdefault(groupName,[set(),False])
    group[0].add(mob)
    # Check if this mob already was in some stasis group.
    mobZoneDict = MOB_STASISDICT.get(zone)
    if mobZoneDict:
        mobInfo = mobZoneDict.get(mob)
        # If the mob already was in a stasis group, do some cleanup.
        if mobInfo:
            if mobInfo[0] != groupName:
                stasisSet = zoneDict[mobInfo[0]][0]
                stasisSet.discard(mob)
                if not len(stasisSet):
                    del zoneDict[mobInfo[0]]
            if mobInfo[1]:
                mob.stun -= 5
                mob.invulnerable -= 1
                # If this mob is a player mob, give notice.
                if mob.player:
                    mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
                        "%s has been released from stasis!\\n"%mob.name)
    # If the group is in stasis, put the mob into stasis as well.
    if group[1]:
        mob.stun += 5
        mob.invulnerable += 1
        # If this mob is a player mob, give notice.
        if mob.player:
            mob.player.sendGameText(RPG_MSG_GAME_EVENT, \
                "%s has been put into stasis!\\n"%mob.name)
    # Add the new stasis group mapping to the mob.
    MOB_STASISDICT.setdefault(zone,{})[mob] = [groupName,group[1]]
    # Refresh mob info to propagate status changes.
    mob.mobInfo.refresh()



def CmdDespawn(mob, args):
    zone = mob.zone
    # Despawn all non-player and non-playerpet mobs. No matter what.
    mobList = zone.spawnedMobs[:]
    mobList.extend(zone.activeMobs)
    for spMob in mobList:
        if not spMob.player and not (spMob.master and spMob.master.player):
            zone.removeMob(spMob)


def CmdKill(mob, args):
    from damage import Damage
    target = mob.target
    if target:
        # Make sure the mob is properly initialized.
        if not target.player:
            if not target.mobInitialized:
                target.initMob()
        # Make sure the immortal and only the immortal gets xp.
        target.xpDamage = {}
        target.xpDamage[mob] = XPDamage()
        target.xpDamage[mob].addDamage(999999)
        # Kill.
        target.die(True)
        # Notify happy player about kill.
        mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
            "%s is struck down by lightning from the heavens!\\n"%target.name)
        # If the target was a player, notify this one as well.
        if target.player:
            target.player.sendGameText(RPG_MSG_GAME_CHARDEATH, \
                "%s is struck down by lightning from the heavens!\\n"%target.name)


def CmdStasis(mob, args):
    # Check if we got some arguments.
    if not len(args):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Syntax for immortal command stasis:\\n - '/imm stasis on/off <stasis group name>': Group name here is optional. Turn stasis for a specific group or the target on or off while adding the current target (if any) to this group.\\n - '/imm stasis add/remove <stasis group name>': Group name here is required. Add/remove the target to/from the specified group, without toggling stasis for this group. If group is in stasis, target will be set to stasis as well on add and taken out of stasis on removal.\\n - '/imm stasis info': Returns a list with all stasis groups in the current zone, their members and their status.\\n - '/imm stasis clear': Clear all stasis groups for the current zone, take all mobs out of stasis.\\n")
        return
    
    # Get the subcommand.
    subcommand = args[0].lower()
    
    # Get the immortals zone.
    zone = mob.zone
    
    # Get the immortals target.
    target = mob.target
    
    # Check if we want to clear the stasis dictionary for this zone.
    if subcommand == 'clear':
        # Clear the zone entry in the stasis dictionary.
        try:
            del STASISDICT[zone]
        except KeyError:
            pass
        # Get and clear the zone dictionary of mob stasis group mappings and
        #  take all mobs in this dictionary out of stasis if necessary.
        try:
            zoneDict = MOB_STASISDICT.pop(zone)
            for stmob,values in zoneDict.iteritems():
                if values[1]:
                    stmob.stun -= 5
                    stmob.invulnerable -= 1
                    stmob.mobInfo.refresh()
                    # If this mob is a player mob, give notice.
                    if stmob.player:
                        stmob.player.sendGameText(RPG_MSG_GAME_GAINED, \
                            "%s has been released from stasis!\\n"%stmob.name)
        except KeyError:
            pass
        # Give feedback and return.
        mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
            "All stasis groups in %s have been cleared.\\n"%zone.zone.niceName)
        return
    
    # Check if we want info on current stasis groups in this zone.
    elif subcommand == 'info':
        # Get the current stasis zone dictionary.
        zoneDict = STASISDICT.get(zone)
        if not zoneDict or not len(zoneDict):
            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"There are currently no stasis groups in %s.\\n"%zone.zone.niceName)
            return
        # Build the info string.
        mobZoneDict = MOB_STASISDICT[zone]
        stasisGroups = "\\n".join(" - %s:\\n%s"%(groupName,"\\n".join("  -- %s : %s"%(stmob.name,mobZoneDict[stmob][1]) for stmob in groupInfo[0])) for groupName,groupInfo in zoneDict.iteritems())
        # Display information to immortal and return.
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Stasis groups in %s:\\n%s\\n"%(zone.zone.niceName,stasisGroups))
        return
    
    # Check if we want to add the target to a specified stasis group.
    elif subcommand == 'add':
        # Check if we have a valid target.
        if not target:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
                "Please select a target before using this command.\\n")
            return
        # Check if a group argument is present.
        if len(args) == 1:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
                "Please provide a stasis group name with this command.\\n")
            return
        # Get the stasis group name.
        groupName = ' '.join(args[1:])
        # Add the target to the group.
        addMobToStasisGroup(target,groupName)
        # Give feedback.
        mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
            "Added %s to stasis group %s.\\n"%(target.name,groupName))
        return
    
    # Check if we want to remove the target from a specified stasis group.
    elif subcommand == 'remove':
        # Check if we have a valid target.
        if not target:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
                "Please select a target before using this command.\\n")
            return
        # Check if a group argument is present.
        if len(args) == 1:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
                "Please provide a stasis group name with this command.\\n")
            return
        # Get the stasis group name.
        groupName = ' '.join(args[1:])
        # Check if the target mob is in the specified group.
        zoneDict = MOB_STASISDICT.get(zone)
        if zoneDict:
            mobInfo = zoneDict.get(target)
            if mobInfo and mobInfo[0] == groupName:
                # Remove the target from the group.
                stasisSet = STASISDICT[zone][groupName][0]
                stasisSet.discard(target)
                if not len(stasisSet):
                    del STASISDICT[zone][groupName]
                # If the mob was in stasis, cancel stasis.
                if mobInfo[1]:
                    target.stun -= 5
                    target.invulnerable -= 1
                    target.mobInfo.refresh()
                    # If this mob is a player mob, give notice.
                    if target.player:
                        target.player.sendGameText(RPG_MSG_GAME_GAINED, \
                            "%s has been released from stasis!\\n"%target.name)
                del MOB_STASISDICT[zone][target]
                # Give feedback.
                mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
                    "Removed %s from group %s.\\n"%(target.name,groupName))
                return
        # Failed to remove target from group since group does not exist
        #  or target isn't in that group.
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "%s isn't part of the stasis group %s.\\n"%(target.name,groupName))
        return
    
    # Check if we want to enable or cancel stasis for a stasis group or target.
    elif subcommand == 'on' or subcommand == 'off':
        # Get the group name if any.
        if len(args) > 1:
            groupName = ' '.join(args[1:])
            # If there is a target, add it to the group.
            if target:
                addMobToStasisGroup(target,groupName)
                group = STASISDICT[zone][groupName]
            # Otherwise check if the group exists.
            else:
                group = None
                zoneDict = STASISDICT.get(zone)
                if zoneDict:
                    group = zoneDict.get(groupName)
                if not group:
                    mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
                        "Stasis group %s does not exist.\\n"%groupName)
                    return
        # Otherwise a target will be required.
        else:
            if not target:
                mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Please provide a stasis group name or select a target before using this command.\\n")
                return
            # Automatically generate a group name for the target.
            groupName = "%s - %i"%(target.name,target.id)
            # Add the target to the automatically generated group.
            addMobToStasisGroup(target,groupName)
            group = STASISDICT[zone][groupName]
        
        mobZoneDict = MOB_STASISDICT[zone]
        
        # If the subcommand was on, put the desired group into stasis.
        if subcommand == 'on':
            if not group[1]:
                for stmob in group[0]:
                    if not mobZoneDict[stmob][1]:
                        stmob.stun += 5
                        stmob.invulnerable += 1
                        stmob.mobInfo.refresh()
                        # If this mob is a player mob, give notice.
                        if stmob.player:
                            stmob.player.sendGameText(RPG_MSG_GAME_EVENT, \
                                "%s has been put into stasis!\\n"%stmob.name)
                        mobZoneDict[stmob][1] = True
                group[1] = True
            mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
                "Stasis group %s has been put into stasis.\\n"%groupName)
        # Otherwise cancel stasis for the desired stasis group.
        else:
            if group[1]:
                for stmob in group[0]:
                    if mobZoneDict[stmob][1]:
                        stmob.stun -= 5
                        stmob.invulnerable -= 1
                        stmob.mobInfo.refresh()
                        # If this mob is a player mob, give notice.
                        if stmob.player:
                            stmob.player.sendGameText(RPG_MSG_GAME_GAINED, \
                                "%s has been released from stasis!\\n"%stmob.name)
                        mobZoneDict[stmob][1] = False
                group[1] = False
            mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
                "Stasis has been cancelled for stasis group %s.\\n"%groupName)
        return
    
    # If we get here, the immortal needs a reminder on the command syntax.
    mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Syntax for immortal command stasis:\\n - '/imm stasis on/off <group name>': Group name here is optional. Turn stasis for a specific group or the target on or off while adding the current target (if any) to this group.\\n - '/imm stasis add/remove <group name>': Group name here is required. Add/remove the target to/from the specified group, without toggling stasis for this group. If group is in stasis, target will be set to stasis as well on add and taken out of stasis on removal.\\n - '/imm stasis info': Returns a list with all stasis groups, their members and their status.\\n - '/imm stasis clear': Clear all stasis groups for the current zone, take all mobs out of stasis.\\n")


def CmdSet(mob, args):
    if not len(args):
        return
    
    what = args[0].upper()
    args = args[1:]
    
    if not len(args):
        return
    
    SetCommands = {
        'WIND': CmdSetWind,
        'TIME': CmdSetTime,
        'WEATHER': CmdSetWeather
    }
    
    try:
        SetCommands[what](mob,args)
    except KeyError:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Only %s can be used in conjunction with the set command.\\n"%', '.join(SetCommands.iterkeys()))


def CmdSetWind(mob,args):
    # Clamp wind to a range from 1 to 10.
    wind = max(1,min(10,int(args[0])))
    mob.zone.weather.windspeed = wind
    mob.zone.weather.dirty = True
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Wind set.\\n")


def CmdSetWeather(mob,args):
    # Clamp precipitation to something below or equal to 10.
    precip = min(10,int(args[0]))
    
    weather = mob.zone.weather
    weather.cloudCover = max(1,precip)
    weather.precip = precip
    weather.lastPrecipChange = 0
    weather.lastCoverChange = 0
    weather.dirty = True
    
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Weather set.\\n")


def CmdSetTime(mob, args):
    try:
        # Get the arguments for hour and minutes to set.
        hour = int(args[0])
        minute = 0
        if len(args) == 2:
            minute = int(args[1])
        
        # Get a handle to the current world.
        world = mob.player.world
        
        # If this server uses multiple clusters, need to propagate
        #  time change across them.
        if world.daemonPerspective:
            world.daemonPerspective.callRemote("propagateCmd","setTime",hour,minute)
        
        # Set the new time for the current world instance.
        world.time.hour = hour
        world.time.minute = minute
        
        # Send a message to all players in the current world instance and
        #  synchronize new time.
        for player in world.activePlayers:
            player.mind.callRemote("syncTime",world.time.hour,world.time.minute)
            player.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,"\\n<Scribe of Mirth> And time moves...\\n\\n")
        
        # Send feedback to the immortal who used the command.
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"The time is now: %i:%i\\n"%(world.time.hour,world.time.minute))
    except:
        # Syntax was probably wrong, send feedback to calling immortal.
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Problem setting time\\n")


def CmdGiveMonster(mob,args):
    if not len(args):
        return
    
    mspawn = ' '.join(args)
    lowerSpawn = mspawn.lower()
    
    for monsterSpawn in mob.player.monsterSpawns:
        if monsterSpawn.spawn.lower() == lowerSpawn:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You already have the %s monster template.\\n"%monsterSpawn.spawn)
            return
    
    from spawn import Spawn
    try:
        con = Spawn._connection.getConnection()
        spawn = Spawn.get(con.execute("SELECT id FROM spawn WHERE lower(name)=\"%s\" LIMIT 1;"%lowerSpawn).fetchone()[0])
        mspawn = spawn.name
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"No such spawn %s.\\n"%mspawn)
        return
    
    from player import PlayerMonsterSpawn
    PlayerMonsterSpawn(player=mob.player,spawn=mspawn)
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"You now have the %s monster template.\\n"%mspawn)


def CmdGrantMonster(mob,args):
    if len(args) < 2:
        return
    
    pname = args[0]
    lowerPName = pname.lower()
    args = args[1:]
    
    mspawn = ' '.join(args)
    lowerSpawn = mspawn.lower()
    
    from player import Player
    try:
        con = Player._connection.getConnection()
        player = Player.get(con.execute("SELECT id FROM player WHERE lower(public_name) = \"%s\" LIMIT 1;"%lowerPName).fetchone()[0])
        pname = player.publicName
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"No player by public name %s.\\n"%pname)
        return

    if not player.party or not len(player.party.members):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Player isn't logged in %s.\\n"%pname)
        return

    for monsterSpawn in player.monsterSpawns:
        if monsterSpawn.spawn.lower() == lowerSpawn:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s already has the %s monster template.\\n"%(pname,monsterSpawn.spawn))
            return
    
    from spawn import Spawn
    try:
        con = Spawn._connection.getConnection()
        spawn = Spawn.get(con.execute("SELECT id FROM spawn WHERE lower(name) = \"%s\" LIMIT 1;"%lowerSpawn).fetchone()[0])
        mspawn = spawn.name
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"No such spawn %s.\\n"%mspawn)
        return
    
    from player import PlayerMonsterSpawn
    PlayerMonsterSpawn(player=player,spawn=mspawn)
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"You have granted %s the %s monster template.\\n"%(pname,mspawn))
    if player.zone:
        player.sendGameText(RPG_MSG_GAME_GAINED,"You now have the %s monster template.\\n"%mspawn)


def CmdListMonsters(mob,args):
    if len(args) < 1:
        return
    
    pname = args[0]
    lowerPName = pname.lower()
    
    from player import Player
    try:
        con = Player._connection.getConnection()
        player = Player.get(con.execute("SELECT id FROM player WHERE lower(public_name) = \"%s\" LIMIT 1;"%lowerPName).fetchone()[0])
        pname = player.publicName
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"No player by public name %s.\\n"%pname)
        return
    
    text = "%s has the following monster templates: %s\\n"%(pname,', '.join(ms.spawn for ms in player.monsterSpawns))
    
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,text)


def CmdDenyMonster(mob,args):
    if len(args) < 2:
        return
    
    pname = args[0]
    lowerPName = pname.lower()
    args = args[1:]
    
    mspawn = ' '.join(args)
    lowerSpawn = mspawn.lower()
    
    from player import Player
    try:
        con = Player._connection.getConnection()
        player = Player.get(con.execute("SELECT id FROM player WHERE lower(public_name) = \"%s\" LIMIT 1;"%lowerPName).fetchone()[0])
        pname = player.publicName
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"No player by public name %s.\\n"%pname)
        return

    if not player.party or not len(player.party.members):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Player isn't logged in %s.\\n"%pname)
        return

    for ms in player.monsterSpawns:
        if ms.spawn.lower() == lowerSpawn:
            ms.destroySelf()
            break
    else:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have the %s monster template.\\n"%(pname,mspawn))
        return

    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"You have denied %s the %s monster template.\\n"%(pname,mspawn))
    if player.zone:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You no longer have the %s monster template.\\n"%mspawn)


def CmdGrantLevel(mob,args):
    if len(args) < 2:
        return
    
    pname = args[0]
    lowerPName = pname.lower()
    klass = args[1].lower()
    
    from player import Player
    try:
        con = Player._connection.getConnection()
        player = Player.get(con.execute("SELECT id FROM player WHERE lower(public_name) = \"%s\" LIMIT 1;"%lowerPName).fetchone()[0])
        pname = player.publicName
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"No player by public name %s.\\n"%pname)
        return
    
    if not player.party or not len(player.party.members):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Player isn't logged in %s.\\n"%pname)
        return
    
    c = player.party.members[0]
    gained = False
    spawn = c.spawn
    if spawn.pclassInternal.lower() == klass:
        c.gainLevel(0)
        gained = True
    if spawn.sclassInternal.lower() == klass:
        c.gainLevel(1)
        gained = True
    if spawn.tclassInternal.lower() == klass:
        c.gainLevel(2)
        gained = True
    
    if gained:
        t = "%s %i / %s %i / %s %i"%(spawn.pclassInternal,spawn.plevel,spawn.sclassInternal,spawn.slevel,spawn.tclassInternal,spawn.tlevel)
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s is now a %s.\\n"%(c.name,t))
    else:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Character doesn't have that class\\n")


def CmdModStat(mob,args):
    if not len(args):
        return
    
    # Get the target for the effect.
    target = mob.target
    if not target:
        target = mob
    
    # If both last arguments are numbers, then the last number marks
    #  the effect duration in minutes. Default is 30 minutes.
    duration = 30 * durMinute
    if args[-2].isdigit():
        try:
            duration = int(args[-1]) * durMinute
        except ValueError:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s can't be used to set the effect duration."%args[-1])
    
    # Create an effect out of the desired values.
    mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Implementation of this command is not yet finished.")


def CmdGimme(mob,args):
    from item import ItemProto,getTomeAtLevelForScroll
    argUpper = args[0].upper()
    if argUpper == 'TOME':
        itemname = argUpper
        tomename = ' '.join(args[2:-1])    # strip "Tome of" and tome level
    elif argUpper not in ("PLEVEL","SLEVEL","TLEVEL","SKILL","MONEY","XP","RENEW","PRESENCE"):
        itemname = ' '.join(args)
    else:
        itemname = argUpper
        levels = 0
        if len(args) > 1:
            try:
                levels = int(args[1])
            except:
                pass
    
    if itemname == 'MONEY':
        if len(args) > 1:
            try:
                amount = int(args[1])
            except:
                amount = 1000
        else:
            amount = 1000
        mob.player.platinum += amount
        if mob.player.platinum < 0:
            mob.player.platinum = 0
        if amount > 0:
            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Gained %i platinum.\\n"%amount)
        else:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Lost %i platinum.\\n"%(-amount))
        return
    elif itemname == 'XP':
        for c in mob.player.party.members:
            c.gainXP(1000000)
        return
    elif itemname == 'PLEVEL':
        if levels == 0:
            return #no point in trying
        for x in xrange(0,levels):
            mob.player.curChar.gainLevel(0)
        return
    elif itemname == 'SLEVEL':
        if levels == 0:
            return #no point in trying
        for x in xrange(0,levels):
            mob.player.curChar.gainLevel(1)
        return
    elif itemname == 'TLEVEL':
        if levels == 0:
            return #no point in trying
        for x in xrange(0,levels):
            mob.player.curChar.gainLevel(2)
        return
    elif itemname == 'SKILL':
        if levels == 0:
            return #no point in trying
        m = mob.player.curChar.mob
        for x in xrange(0,levels):
            for skname in m.skillLevels.iterkeys():
                mob.player.curChar.checkSkillRaise(skname,0,0)
        return
    elif itemname == 'PRESENCE':
        if levels < 0:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"The value provided must be a positive integer.\\n")
            return
        if levels > RPG_MAX_PRESENCE:
            levels = RPG_MAX_PRESENCE
            
        currentCharacter = mob.player.curChar 
        currentCharacter.mob.pre = levels
        currentCharacter.mob.preBase = levels
        currentCharacter.spawn.preBase = levels         
        currentCharacter.mob.derivedDirty = True       

        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"You now have %i presence.\\n"%levels)
        return        
    elif itemname == 'RENEW':
        for c in mob.player.party.members:
            m = c.mob
            m.health = m.maxHealth
            m.mana = m.maxMana
            m.stamina = m.maxStamina
        
            m.skillReuse = {}
            m.recastTimers = {}
            
            if m.pet:
                m.pet.health = m.pet.maxHealth
        
        mob.player.cinfoDirty = True
        return
    elif itemname == 'TOME':
        char = mob.player.curChar
        levels = ['1','2','3','4','5','6','7','8','9','10']
        lupper = args[-1].upper()
        try:
            tomelevel = levels.index(lupper) + 1
        except:
            try:
                tomelevel = RPG_ROMAN.index(lupper) + 1
            except:
                mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s isn't a valid tome level!\\n"%args[-1])
                return
        if tomelevel <= 1:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s isn't a valid tome level!\\n"%args[-1])
            return
        try:
            con = ItemProto._connection.getConnection()
            scroll = ItemProto.get(con.execute("SELECT id FROM item_proto WHERE lower(name)=lower(\"Scroll of %s\") LIMIT 1;"%tomename).fetchone()[0])
        except:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s is no spell name!\\n"%tomename)
            return
        nitem = getTomeAtLevelForScroll(scroll,tomelevel)
        if not char.giveItemInstance(nitem):
            nitem.destroySelf()
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough inventory space\\n"%char.name)
            return
        char.refreshItems()
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Gained %s\\n"%nitem.name)
        return
    
    from crafting import FocusGenSpecific
    item = FocusGenSpecific(itemname)
    if item:
        if not mob.player.curChar.giveItemInstance(item):
            item.destroySelf()
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough inventory space\\n"%char.name)
            return
    else:
        item = mob.player.giveItem(itemname,True,True)
    
    if item:
        if RPG_SLOT_WORN_END > item.slot >= RPG_SLOT_WORN_BEGIN:
            mob.equipItem(item.slot,item)
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Gained %s\\n"%item.name)
        return
    
    mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Failure getting %s\\n"%itemname)


def CmdSpawn(mob, args):
    try:
        # Check if there were coords supplied.
        if args[-1].endswith(']'):
            # Extract the coords argument.
            # It should look like this: [x.x y.y z.z].
            x = float(args[-3][1:])
            y = float(args[-2])
            z = float(args[-1][:-1])
            spawnName = ' '.join(args[:-3])
        
        # Otherwise take the immortals position.
        else:
            mypos = mob.simObject.position
            x = mypos[0]
            y = mypos[1]
            z = mypos[2]
            spawnName = ' '.join(args)
    
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Invalid arguments to immortal spawn command. Syntax is '/imm spawn <spawn name> [x-coord y-coord z-coord]' where the coords with their '[]' brackets are optional.\\n")
        return
    
    # Get the spawn.
    try:
        con = Spawn._connection.getConnection()
        spawn = Spawn.get(con.execute("SELECT id FROM spawn WHERE lower(name)=lower(\"%s\") LIMIT 1;"%spawnName).fetchone()[0])
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "Failure spawning %s, this spawn doesn't exist.\\n"%spawnName)
        return
    
    # Put the transform together.
    rot = mob.simObject.rotation
    transform = (x,y,z,rot[0],rot[1],rot[2],rot[3])
    
    # Spawn the desired mob.
    mob.zone.spawnMob(spawn,transform,-1)
    
    # Give feedback about the successful spawning.
    mob.player.sendGameText(RPG_MSG_GAME_GAINED, \
        "%s spawned at [%0.2f %0.2f %0.2f].\\n"%(spawnName,x,y,z))


def CmdWorldAggro(mob, args):
    # Get a handle to the current world instance.
    world = mob.player.world
    
    # Get the new aggro state.
    # If there was no argument supplied, just toggle.
    newAggroState = not world.aggroOn
    if len(args):
        if args[0].lower() == 'off':
            # If the state didn't change, return and give feedback.
            if newAggroState:
                mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,"Monsters still won't initiate attacks.\\n")
                return
            newAggroState = False
        else:
            # If the state didn't change, return and give feedback.
            if not newAggroState:
                mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,"Monsters still will initiate attacks.\\n")
                return
            newAggroState = True
    
    # Set this world instance's aggro state to the new one.
    world.aggroOn = newAggroState
    
    # If the server uses multiple zone clusters, propagate the command
    #  across them.
    if world.daemonPerspective:
        world.daemonPerspective.callRemote("propagateCmd","setWorldAggro",newAggroState)
    
    # Give feedback to the calling immortal.
    if newAggroState:
        mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,"Monsters WILL initiate attacks.\\n")
    else:
        mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,"Monsters will NOT initiate an attacks.\\n")


def CmdMyAggro(mob,args):
    aggroOff = mob.aggroOff
    if not len(args):
        aggroOff = not aggroOff
    else:
        if args[0].lower()=='off':
            aggroOff = True
        else:
            aggroOff = False
        
    for c in mob.player.party.members:
        c.mob.aggroOff = aggroOff    
    
     
    if aggroOff:
        mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,"Monsters will NOT attack your party.\\n")
    else:
        mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,"Monsters WILL attack your party.\\n")
        


    
def CmdTP(mob,args):
    player = mob.player
    zname = args[0]
    
    if zname.lower() == 'bindstone':
        if player.darkness:
            z = player.darknessBindZone
            trans = player.darknessBindTransform
        elif player.monster:
            z = player.monsterBindZone
            trans = player.monsterBindTransform
        else:
            z = player.bindZone
            trans = player.bindTransform
        dst = ' '.join(str(i) for i in trans)
    else:
        try:
            z = Zone.byName(zname)
            dst = z.immTransform
        except:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown zone or zone not setup for immortal command %s.\\n"%zname)
            return
    
    #are we in the same zone?
    if player.zone.zone == z:
        #good
        #we just need to respawn player, whew
        player.zone.respawnPlayer(player,dst)
    else:
        from zone import TempZoneLink
        zlink = TempZoneLink(zname,dst)
        player.world.onZoneTrigger(player,zlink)


def CmdSystemMsg(mob, args):
    # Check if there is even a message and return if not.
    if not len(args):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Need to specify a message to use with this command.")
        return
    
    # Assemble the message.
    msg = r'SYSTEM: %s\n'%(' '.join(args))
    
    # Get a handle to the current world.
    world = mob.player.world
    
    # If this server uses multiple clusters, need to propagate the
    #  message across them.
    if world.daemonPerspective:
        world.daemonPerspective.callRemote("propagateCmd","sendSysMsg",msg)
    
    # Run through this servers players and send them the message.
    for p in world.activePlayers:
        p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,msg)


def CmdScribeMsg(mob, args):
    # Check if there is even a message and return if not.
    if not len(args):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Need to specify a message to use with this command.")
        return
    
    # Assemble the message.
    msg = "\\n<Scribe of Mirth> %s\\n\\n"%(' '.join(args))
    
    # Get a handle to the current world.
    world = mob.player.world
    
    # If this server uses multiple clusters, need to propagate the
    #  message across them.
    if world.daemonPerspective:
        world.daemonPerspective.callRemote("propagateCmd","sendSysMsg",msg)
    
    # Run through this servers players and send them the message.
    for p in world.activePlayers:
        p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,msg)


def CmdReloadCommands(mob,args):
    reload(sys.modules['mud.world.command'])
    
def CmdReloadModule(mob,args):
    reload(sys.modules[args[0]])

    
def CmdGrant(mob,args):
    from mud.common.permission import User,Role
    
    if len(args) < 2:
        return
    
    try:
        user = User.byName(args[0])
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown user %s.\\n"%args[0])
        return
    
    try:
        role = Role.byName(args[1])
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown role %s.\\n"%args[1])
        return
    
    for r in user.roles:
        if r.name == role.name:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"User %s already has the %s role.\\n"%(args[0],args[1]))
            return
        
    if role.name == "Immortal":
        from newplayeravatar import NewPlayerAvatar
        if mob.player.publicName != NewPlayerAvatar.ownerPublicName:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Immortal access can only be granted by the server's owner.\\n")
            return

            
    
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"User %s granted the %s role.\\n"%(args[0],args[1]))
    user.addRole(role)
    
def CmdDeny(mob,args):
    from mud.common.permission import User,Role
    from player import Player
    
    if len(args) < 2:
        return
    
    try:
        user = User.byName(args[0])
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown user %s.\\n"%args[0])
        return
    
    
    if not IsUserSuperior(mob.player.publicName,user.name):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You do not have the required permission for this action.\\n")
        return

    
    try:
        role = Role.byName(args[1])
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown role %s.\\n"%args[1])
        return
    
    for r in user.roles:
        if r.name == role.name:
            user.removeRole(r)
            try:
                player = Player.byPublicName(args[0])
                if player.avatar and player.avatar.masterPerspective:
                    player.avatar.masterPerspective.removeAvatar("GuardianAvatar")            
            except:
                pass

            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"User %s denied the %s role.\\n"%(args[0],args[1]))
            return
    
            
    mob.player.sendGameText(RPG_MSG_GAME_DENIED,"User %s doesn't have the %s role.\\n"%(args[0],args[1]))
    
    
def CmdSetPlayerPassword(mob,args):
    from player import Player
    
    if CoreSettings.SINGLEPLAYER:
        return

    
    if len(args) != 2:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Please specify a player and a password\\n")
        return

    try:
        player = Player.byPublicName(args[0])
    except:
        try:
            player = Player.byFantasyName(args[0])
        except:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown player %s.\\n"%args[0])
            return

    try:
        user = User.byName(args[0])
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown user %s.\\n"%args[0])
        return

    if not IsUserSuperior(mob.player.publicName,user.name):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You do not have the required permission for this action.\\n")
        return

    
    pw = args[1]
    if len(pw) < 6:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Password must be at least 6 characters.\\n")
        return
    
    user.password = player.password = pw
        
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Player %s password set to %s\\n"%(player.publicName,pw))

def CmdGetPlayerPassword(mob,args):
    
    if CoreSettings.SINGLEPLAYER:
        return

    if len(args) != 1:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Please specify a player\\n")
        return

    try:
        user = User.byName(args[0])
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown user %s.\\n"%args[0])
        return
    
    if not IsUserSuperior(mob.player.publicName,user.name):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You do not have the required permission for this action.\\n")
        return
        
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Player %s password is: %s\\n"%(user.name,user.password))


def CmdTestAFX(mob, args):
    if not len(args):
        return
    effect = ' '.join(args)
    mob.testAFX(effect,mob.target)


def CmdGetDimensions(mob, args):
    # If there is a target, get this ones dimensions.
    source = mob
    if mob.target:
        source = mob.target
    
    # Print out all relevant size information.
    mob.player.sendGameText(RPG_MSG_GAME_WHITE,"Relevant dimensions of %s are:\\n Mob Size - %f\\n Spawn Scale - %f\\n Current Scale - %f\\n Spawn Radius - %f\\n"%(source.name,source.size,source.spawn.scale,source.spawn.modifiedScale,source.spawn.radius))


def CmdCheckWealth(mob, args):
    # Check if there is a target available.
    if not mob.target:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "This command requires a target.\\n")
        return
    
    # Get a handle to the targets player.
    tplayer = mob.target.player
    
    # Query the targets wealth.
    ext = ('pp','gp','sp','cp','tp')
    worthLight = (tplayer.lightPlatinum,tplayer.lightGold,tplayer.lightSilver, \
        tplayer.lightCopper,tplayer.lightTin)
    lightString = ', '.join('%i%s'%(w,ext[i]) \
        for i,w in enumerate(worthLight) if w != 0)
    worthDarkness = (tplayer.darknessPlatinum,tplayer.darknessGold, \
        tplayer.darknessSilver,tplayer.darknessCopper,tplayer.darknessTin)
    darknessString = ', '.join('%i%s'%(w,ext[i]) \
        for i,w in enumerate(worthDarkness) if w != 0)
    worthMonster = (tplayer.monsterPlatinum,tplayer.monsterGold, \
        tplayer.monsterSilver,tplayer.monsterCopper,tplayer.monsterTin)
    monsterString = ', '.join('%i%s'%(w,ext[i]) \
        for i,w in enumerate(worthMonster) if w != 0)
    
    # And print the result to the immortal.
    mob.player.sendGameText(RPG_MSG_GAME_WHITE, \
        "%s's wealth:\\n Light: %s\\n Darkness: %s\\n Monster: %s\\n"% \
        (mob.target.name,lightString,darknessString,monsterString))


def CmdSetWealth(mob, args):
    # Check if there is a target available.
    if not mob.target:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "This command requires a target.\\n")
        return
    
    # Check if the two needed arguments are present.
    if len(args) != 2:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "Number of supplied arguments incorrect.\\nUsage: /imm setwealth <realm = light/darkness/monster> <amount in tin>.\\n")
        return
    
    # Extract the desired amount of money to set the targets wealth to.
    try:
        tp,cp,sp,gp,pp = CollapseMoney(int(args[1]))
    except ValueError:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "Can't extract amount of tin argument.\\nUsage: /imm setwealth <realm = light/darkness/monster> <amount in tin>.\\n")
        return
    
    # Get a handle to the targets player.
    tplayer = mob.target.player
    
    # Extract the realm and set wealth to the new value.
    realmText = args[0].upper()
    if realmText == 'LIGHT':
        tplayer.lightTin = tp
        tplayer.lightCopper = cp
        tplayer.lightSilver = sp
        tplayer.lightGold = gp
        tplayer.lightPlatinum = pp
    elif realmText == 'DARKNESS':
        tplayer.darknessTin = tp
        tplayer.darknessCopper = cp
        tplayer.darknessSilver = sp
        tplayer.darknessGold = gp
        tplayer.darknessPlatinum = pp
    elif realmText == 'MONSTER':
        tplayer.monsterTin = tp
        tplayer.monsterCopper = cp
        tplayer.monsterSilver = sp
        tplayer.monsterGold = gp
        tplayer.monsterPlatinum = pp
    else:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, \
            "Can't extract realm argument.\\nUsage: /imm setwealth <realm = light/darkness/monster> <amount in tin>.\\n")
        return
    
    # Generate the money string.
    ext = ('pp','gp','sp','cp','tp')
    worth = (pp,gp,sp,cp,tp)
    moneyString = ', '.join('%i%s'%(w,ext[i]) for i,w in enumerate(worth) if w != 0)
    
    # Print result to the immortal and log.
    mob.player.sendGameText(RPG_MSG_GAME_WHITE, \
        "%s's wealth in the %s realm has been set to: %s.\\nPlease inform the player once all adjustments have taken place.\\n"%(mob.target.name,args[0],moneyString))
    print "Immortal %s has set %s's wealth in the %s realm to %s."% \
        (mob.player.publicName,tplayer.fantasyName,args[0],moneyString)
    
    # Informing the player about the change is left up to the immortal.
    # Maybe several changes have to be made before the player should be informed.



COMMANDS = {}
COMMANDS['SPAWN'] = CmdSpawn
COMMANDS['DESPAWN'] = CmdDespawn

COMMANDS['SET'] = CmdSet

COMMANDS['KILL'] = CmdKill
COMMANDS['STASIS'] = CmdStasis

COMMANDS['WORLDAGGRO'] = CmdWorldAggro
COMMANDS['MYAGGRO'] = CmdMyAggro

COMMANDS['SYSMSG'] = CmdSystemMsg
COMMANDS['SCRIBE'] = CmdScribeMsg

COMMANDS['RELOADCOMMANDS'] = CmdReloadCommands
COMMANDS['RELOADMODULE'] = CmdReloadModule

COMMANDS['GIVEMONSTER'] = CmdGiveMonster
COMMANDS['GRANTMONSTER'] = CmdGrantMonster
COMMANDS['DENYMONSTER'] = CmdDenyMonster
COMMANDS['LISTMONSTERS'] = CmdListMonsters

COMMANDS['GETPLAYERPASSWORD'] = CmdGetPlayerPassword
COMMANDS['SETPLAYERPASSWORD'] = CmdSetPlayerPassword

COMMANDS['TP'] = CmdTP
COMMANDS['GIMME'] = CmdGimme

COMMANDS['MODSTAT'] = CmdModStat
COMMANDS['GRANTLEVEL'] = CmdGrantLevel

COMMANDS['GRANT'] = CmdGrant
COMMANDS['DENY'] = CmdDeny

COMMANDS['TESTAFX'] = CmdTestAFX
COMMANDS['GETDIMENSIONS'] = CmdGetDimensions

COMMANDS['CHECKWEALTH'] = CmdCheckWealth
COMMANDS['SETWEALTH'] = CmdSetWealth



def DoImmortalCommand(player,cmd,args):
    mob = player.curChar.mob
    
    if type(args)!=list:
        args = [args]
    cmd = cmd.upper()
    if COMMANDS.has_key(cmd):
        COMMANDS[cmd](mob,args)
    else:
        print "Unknown Command",cmd
        
