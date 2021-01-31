# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.permission import User
from mud.world.core import *
from mud.world.defines import *
from mud.world.guild import GuildCharacters,GuildClearMOTD,GuildCreate, \
    GuildDecline,GuildDemote,GuildDisband,GuildInvite,GuildJoin,GuildLeave, \
    GuildPromote,GuildPublicName,GuildRemove,GuildRoster,GuildSetLeader,GuildSetMOTD
from mud.world.inn import Inn
from mud.world.messages import GameMessage
from mud.world.pet import PetCmdAttack,PetCmdDismiss,PetCmdFollowMe, \
    PetCmdStandDown,PetCmdStay
from mud.world.shared.vocals import *

from datetime import timedelta
from math import degrees
from random import randint
from time import time as sysTime
import traceback



def CheckMuted(mob):
    player = mob.player
    if player.world.mutedPlayers.has_key(player.publicName):
        mt = player.world.mutedPlayers[player.publicName]
        m = mt / 60 + 1
        if m > 59:
            player.sendSpeechText(RPG_MSG_SPEECH_ERROR,r'You have been muted.\n')
        else:
            player.sendSpeechText(RPG_MSG_SPEECH_ERROR,r'You have been muted and will be able to speak in %i minutes.\n'%m)
        return True
    
    return False


#get top 10 players
def CmdLadder(mob,args):
    from mud.world.newplayeravatar import NewPlayerAvatar
    
    mob.player.sendGameText(RPG_MSG_GAME_EVENT,"The ladder command is currently inactive.\\n")
    return
    
    text= r'\n------------------------------------\n'
    text+= r'Most Experienced Characters\n'
    text+=r'------------------------------------\n'
    
    chars = {}
    players = {}
    
    cursor = mob.spawn.__class__._connection.getConnection().cursor()
    try:
        cursor.execute("select name,xp_primary,xp_secondary,xp_tertiary,player_id from character;")
        for r in cursor.fetchall():
            name,xpPrimary,xpSecondary,xpTertiary,playerID=r
    
            c2 = mob.spawn.__class__._connection.getConnection().cursor()
            c2.execute("select public_name from player where id = %i;"%playerID)
            if c2.fetchone()[0]==NewPlayerAvatar.ownerPublicName:
                c2.close()
                continue
            c2.close()

            
            c2 = mob.spawn.__class__._connection.getConnection().cursor()
            c2.execute("select realm from spawn where name = '%s';"%name)
            if c2.fetchone()[0]==RPG_REALM_MONSTER:
                c2.close()
                continue
            c2.close()
            
            xp = xpPrimary + xpSecondary + xpTertiary
            chars[name]=xp
            players[name]=playerID
        
        
        v = chars.values()
        v.sort()
        v.reverse()
        v=v[:9]
        
        x = 1
        for xp in v:
            if x > 20:
                break
            for c,cxp in chars.iteritems():
                if cxp == xp:
                    cursor.execute("select pclass_internal,plevel,sclass_internal,slevel,tclass_internal,tlevel from spawn where name = '%s';"%c)
                    pclassInternal,plevel,sclassInternal,slevel,tclassInternal,tlevel = cursor.fetchone()
                    
                    text+="%i.  <%s> %s (%i) "%(x,c,pclassInternal,plevel)
                    if slevel:
                        text+="%s (%i) "%(sclassInternal,slevel)
                    if tlevel:
                        text+="%s (%i) "%(tclassInternal,tlevel)
                        
                    cursor.execute("select fantasy_name from player where id = %i;"%players[c])
                    pname = cursor.fetchone()[0]
                    text+=r'- %s\n'%pname
                    
                    x+=1        
        text = str(text) #remove unicode
        mob.player.sendGameText(RPG_MSG_GAME_EVENT,text)
    except:
        traceback.print_exc()
    cursor.close()


def CmdSuicide(mob, args):
    for c in mob.player.party.members:
        if not c.dead:
            c.mob.die()


def CmdUnstick(mob,args):
    
    for c in mob.player.party.members:
        if c.mob.unstickReuse:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You must wait a short time before trying to unstick again.\\n")
            return

    
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Please try and unstick yourself.\\n")
    for c in mob.player.party.members:
        if not c.mob.unstick:
            c.mob.unstickReuse = 6*45
            c.mob.unstick = 18
            c.mob.flying += 1.0
            
            


def CmdAvatar(mob,args):
    if not len(args):
        return
        
    name = args[0].upper()
    index = 0
    for m in mob.player.party.members:
        if m.name.upper() == name:
            if mob.player.modelChar == m:
                return
            mob.player.modelChar = m
            mob.player.modelIndex = index
            mob.player.avatarCharName = m.name
            
            mob.player.zone.simAvatar.mind.callRemote("setPlayerSpawnInfo",mob.player.simObject.id,m.spawn.name)
            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Your avatar has been set to %s.\\n"%m.name)
            return
        index+=1

def CmdWho(mob,args):
    if not CoreSettings.PGSERVER:
        CmdWhoOld(mob, args)
        return
    
    if len(args):
        original = ' '.join(args)
        filter = original.upper()
        for pname,info in mob.player.world.characterInfos.iteritems():        
            prefix,cname,realm,pclass,sclass,tclass,plevel,slevel,tlevel,zone,guild = info
            if cname.upper() == filter:
                #MAKE THIS BETTER /who needs total redo!
                classes = (pclass,sclass,tclass)
                levels = (plevel,slevel,tlevel)
                
                text = r'%s (%s %s)\n'%(' '.join([prefix, cname]),
                            '/'.join(RPG_CLASS_ABBR[klass] for klass in classes if klass),
                            '/'.join('%i'%level for level in levels if level))
                mob.player.sendGameText(RPG_MSG_GAME_EVENT, text)
                return
        
        try:
            charname,guildname,wname,zname = mob.player.world.globalPlayers[filter]
            mob.player.sendGameText(RPG_MSG_GAME_EVENT, r'%s is on %s\n'%(charname, wname))
        except KeyError:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED, r'%s is not currently logged in.\n'%original)
        return
    
    text = ""
    for pname,info in mob.player.world.characterInfos.iteritems():
        prefix,cname,realm,pclass,sclass,tclass,plevel,slevel,tlevel,zone,guild = info
        classes = (pclass,sclass,tclass)
        levels = (plevel,slevel,tlevel)
        
        text += r'%s (%s %s)\n'%(' '.join([prefix, cname]),
                    '/'.join(RPG_CLASS_ABBR[klass] for klass in classes if klass),
                    '/'.join('%i'%level for level in levels if level))
    
    text += r'\n'
    mob.player.sendGameText(RPG_MSG_GAME_EVENT, text)


def CmdWhoOld(mob,args):
    filter = None
    if len(args):
        filter = ' '.join(args).upper()
    
    text = ""
    for p in mob.player.world.activePlayers:
        if filter and p.publicName.upper() != filter:
            continue
        
        prefix = ""
        if p.avatar and p.avatar.masterPerspective:
            if p.avatar.masterPerspective.avatars.has_key("GuardianAvatar"):
                prefix = "(Guardian) "
            if p.avatar.masterPerspective.avatars.has_key("ImmortalAvatar"):
                prefix = "(Immortal) "
        
        if p.enteringWorld:
            text += r'%s%s <Entering World> '%(prefix, p.name)
        elif p.zone:
            text += r'%s%s <%s> '%(prefix, p.name, p.zone.zone.niceName)
        else:
            text += r'%s%s '%(prefix, p.name)
            
        if p.party and len(p.party.members):
            c = p.party.members[0]
            classes = (c.spawn.pclassInternal,c.spawn.sclassInternal,c.spawn.tclassInternal)
            levels = (c.spawn.plevel,c.spawn.slevel,c.spawn.tlevel)
            text += r'(%s %s)\n'%('/'.join(RPG_CLASS_ABBR[klass] for klass in classes if klass),
                        '/'.join('%i'%level for level in levels if level))
        else:
            text += r'\n'
    
    text += r'\n'
    mob.player.sendGameText(RPG_MSG_GAME_EVENT, text)


def CmdEval(mob,args):
    target = mob.target
    if not target:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no target.\\n"%mob.name)
        return
    
    if target.level - mob.level <= -5:
        color,text = RPG_MSG_GAME_GREEN,"%s is no match for %s.\\n"%(target.name,mob.name)
    elif target.level - mob.level <= -1:
        color,text = RPG_MSG_GAME_BLUE,"%s might challenge %s.\\n"%(target.name,mob.name)
    elif target.level - mob.level == 0:
        color,text = RPG_MSG_GAME_WHITE,"%s is an even match for %s.\\n"%(target.name,mob.name)
    elif target.level - mob.level <= 2:
        color,text = RPG_MSG_GAME_YELLOW,"%s has a significant advantage over %s.\\n"%(target.name,mob.name)
    else:
        color,text = RPG_MSG_GAME_RED,"%s would cream %s.\\n"%(target.name,mob.name)
    
    if target.spawn.desc:
        if target.player:
            mob.player.sendGameText(RPG_MSG_GAME_YELLOW,target.spawn.desc.replace("\n","\\n")+"  ",stripML=True)
        else:
            mob.player.sendGameText(RPG_MSG_GAME_YELLOW,target.spawn.desc+"  ")
    
    factionRelColoring = {
        RPG_FACTION_HATED: RPG_MSG_GAME_RED,
        RPG_FACTION_DISLIKED: RPG_MSG_GAME_BLUE,
        RPG_FACTION_UNDECIDED: RPG_MSG_GAME_WHITE,
        RPG_FACTION_LIKED: RPG_MSG_GAME_YELLOW,
        RPG_FACTION_ADORED: RPG_MSG_GAME_GREEN
    }
    standing,desc = GetFactionRelationDesc(mob,target)
    mob.player.sendGameText(factionRelColoring[standing],desc)
    
    mob.player.sendGameText(color,text)


def CmdDesc(mob,args):
    target = mob.target
    player = mob.player
    if not target:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no target.\\n"%mob.name)
        return
    player.avatar.sendTgtDesc(mob,target)

def CmdMyDesc(mob,args):
    player = mob.player
    player.avatar.sendTgtDesc(mob,mob)


def CmdPet(mob,args):
    if not len(args):
        return
    
    if not mob.pet:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no pet.\\n"%mob.name)
        return
    
    cmd = args[0].upper()
    
    if cmd =='ATTACK':
        if mob.target:
            PetCmdAttack(mob.pet,mob.target)
    elif cmd == 'STAY':
        PetCmdStay(mob.pet)
    elif cmd == 'FOLLOWME':
        PetCmdFollowMe(mob.pet)
    elif cmd == 'STANDDOWN':
        PetCmdStandDown(mob.pet)
    elif cmd == 'DISMISS':
        PetCmdDismiss(mob.pet)


def CmdBind(mob,args):
    #look for a near enough bind point
    
    pos = mob.simObject.position
    for bp in mob.zone.bindpoints:
        x = pos[0]-bp[0]
        y = pos[1]-bp[1]
        z = pos[2]-bp[2]
        
        distSQ = x * x + y * y + z * z
        
        if distSQ <= 144:
            mob.player.mind.callRemote("playSound","sfx/Magic_Appear01.ogg")
            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"You feel a connection to this place.\\n")
            darkness = mob.player.darkness
            if darkness:
                mob.player.darknessBindZone = mob.zone.zone
            elif mob.player.monster:
                mob.player.monsterBindZone = mob.zone.zone
            else:
                mob.player.bindZone = mob.zone.zone
            
            transform = list(mob.simObject.position)
            transform.extend(list(mob.simObject.rotation))
            transform[-1] = degrees(transform[-1])
            
            if darkness:
                mob.player.darknessBindTransform = transform
            elif mob.player.monster:
                mob.player.monsterBindTransform = transform
            else:
                mob.player.bindTransform = transform
                
            
            return
            
    bindzone = ""
    if mob.player.darkness:
        bindzone = mob.player.darknessBindZone.niceName
    elif mob.player.monster:
        bindzone = mob.player.monsterBindZone.niceName
    else:
        bindzone = mob.player.bindZone.niceName
    mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You cannot bind here and remain bound at %s\\n"%bindzone)


#this can be called from simavatar
def CmdZoneInteract(mob, args, trigger=None):
    # Get a handle to this Mob's Player object.
    player = mob.player
    
    # Terminate all current interactions.
    player.endInteraction()
    
    # Get a handle to this Mob's Zone object.
    zone = mob.zone
    
    # Get this Mob's position.
    myPos = mob.simObject.position
    
    # Initialize variables to search for closest trigger.
    bestdt = None
    bestdistSQ = 999999
    
    # Perform the search for the closest trigger.
    for dt in zone.dialogTriggers:
        if not trigger:
            destPos = dt.position
            x = myPos[0] - destPos[0]
            y = myPos[1] - destPos[1]
            z = myPos[2] - destPos[2]
            distSQ = x * x + y * y + z * z
            if distSQ <= dt.range * dt.range and distSQ < bestdistSQ:
                bestdistSQ = distSQ
                bestdt = dt
        elif dt.dialog.name == trigger:
            bestdt = dt
            break
    
    # If a viable trigger was found, process it.
    if bestdt:
        # Get a handle to the Dialog.
        dialog = bestdt.dialog
        
        # Check if the Dialog object has some useable content.
        if dialog.greeting:
            dialog.setLine(player,dialog.greeting,dialog.title)
            
            # If there are some choices available, display the dialog.
            if player.dialog:
                player.interacting = bestdt
                player.mind.callRemote("setVendorStock",False,None,0)
                player.mind.callRemote("openNPCWnd",dialog.title)


def gotCheckIgnoreTrade(ignored, player, oplayer):
    if ignored:
        player.sendGameText(RPG_MSG_GAME_DENIED, \
            "%s is ignoring you.\\n"%oplayer.charName)
        return
    
    from mud.world.trading import Trade
    Trade(player,oplayer)


def gotCheckIgnoreTradeError(error):
    print "Error in checkIgnore: %s"%str(error)


def CmdInteract(mob, args):
    # Get a handle to this Mob's target.
    target = mob.target
    
    # If there is no target, no need to check anything.
    if not target:
        return
    
    # Get a handle to this Mob's Player.
    player = mob.player
    
    # Return if the Player is already interacting with someone.
    if player.interacting or player.trade:
        return
    
    # Dead Characters cannot interact with anything.
    if mob.character.dead:
        return
    
    # If the target is a Player, check for Player trade.
    if target.player:
        otherPlayer = target.player
        
        # No interaction with oneself!
        if otherPlayer == player:
            return
        
        # Check if there's an item on the cursor.
        if not player.cursorItem:
            return
        
        # Check if the targeted Player is already interacting with someone.
        if otherPlayer.interacting or otherPlayer.trade:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s is busy.\\n"%otherPlayer.charName)
            return
        
        # Check if the targeted Player doesn't ignore us.
        d = otherPlayer.mind.callRemote("checkIgnore",player.charName)
        d.addCallback(gotCheckIgnoreTrade,player,otherPlayer)
        d.addErrback(gotCheckIgnoreTradeError)
        
        # Player targets handled, return.
        return
    
    # The targeted Mob is no Player Mob.
    
    # If the target is hostile, attack.
    if IsKOS(target,mob):
        for c in player.party.members:
            c.mob.autoAttack = True
            c.mob.attackOn()
        return
    
    # Get a handle to the target's Spawn.
    spawn = target.spawn
    
    # Otherwise check if the target is an inn keeper.
    if spawn.flags & RPG_SPAWN_INN:
        # If the Player is not at an Inn, check the range.
        if not player.inn:
            # Making this not dependend on spawn size would require for
            #  some to stand inside innkeeper.
            if GetRangeMin(mob,target) <= 4:
                player.inn = Inn(target,player)
            else:
                player.sendGameText(RPG_MSG_GAME_DENIED, \
                    "%s is too far away.\\n"%target.name)
        return
    
    # If the target is a pet of this Player, open the pet inventory window.
    if target.master and target.master.player == player:
        player.mind.callRemote("setCurCharIndex",target.master.charIndex)
        player.mind.callRemote("openPetWindow")
        return
    
    #yuck, rush
    if spawn.vendorProto and not target.vendor:
        spawn.vendorProto.createVendorInstance(target)
    
    vendor = target.vendor
    
    # Return early if the target wouldn't have any interesting interaction.
    if not (spawn.dialog or vendor or spawn.flags & RPG_SPAWN_BANKER):
        return
    
    #make sure to sync range calc in player.tick()
    #we don't use range calc here so we are in sync with player.tick
    #which also checks dialog triggers
    
    # Check if target is in range.
    if GetRangeMin(mob,target) > 2:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is too far away.\\n"%(target.name))
        return
    
    # Check if the target is fighting or part of a battle.
    if target.target or target.battle and not target.battle.over:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is busy.\\n"%target.name)
        return
    
    # Check if the target is a banker.
    if spawn.flags & RPG_SPAWN_BANKER:
        player.mind.callRemote("setVendorStock",False,None,0)
        player.mind.callRemote("setInitialInteraction",None,None)
        player.mind.callRemote("openNPCWnd",spawn.name,True)
        return
    
    # Limit other NPC interaction on multiplayer so each Player can get a turn.
    if not CoreSettings.SINGLEPLAYER and target.interactTimes.has_key(player):
        t = sysTime() - target.interactTimes[player]
        if t < 15:
            player.sendGameText(RPG_MSG_GAME_DENIED, \
                "%s is busy and can be with you in %i seconds.\\n"% \
                (target.name,16 - t))
            return
    
    # Check if the target is already interacting with someone.
    if target.interacting:
        # Check if the NPC has been hogged long enough for an interruption.
        t = sysTime() - target.interactTimes[target.interacting]
        if t > 60:
            target.interacting.endInteraction()
        else:
            interactingPlayer = target.interacting
            interactingCharName = interactingPlayer.fantasyName
            if interactingPlayer.curChar:
                interactingCharName = interactingPlayer.curChar.name
            player.sendGameText(RPG_MSG_GAME_DENIED, \
                "%s is now busy with %s and will be available in %i seconds.\\n"% \
                (target.name,interactingCharName,61 - t))
            return
    
    # At this point we should play some vocalization.
    if not randint(0,9):
        # 1 in 10 chance of laughing.
        target.vocalize(VOX_LAUGH,player)
    elif not randint(0,4):
        # 1 in 5 of grunting.
        target.vocalize(VOX_GRUNT,player)
    else:
        # Otherwise, surprise.
        target.vocalize(VOX_SURPRISED,player)
    
    # Hack
    if not vendor and (not spawn.dialog or not spawn.dialog.greeting):
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s snorts at you.\\n"%target.name)
        return
    
    # Send or reset the vendor stock.
    if vendor:
        vendor.sendStock(player)
    else:
        player.mind.callRemote("setVendorStock",False,None,0)
    
    # Alright we should interact.
    
    # Get a handle to the target's Spawn's Dialog.
    dialog = spawn.dialog
    
    # Check for a greeting line and send this one to the Player.
    if dialog and dialog.greeting:
        # No choices, simple greeting, to do, rebuke.
        if not len(dialog.greeting.choices):
            player.sendGameText(RPG_MSG_GAME_NPC_SPEECH,"%s says, \"%s\"\\n"% \
                (target.name,dialog.greeting.text))
            if not vendor:
                return
        
        # Greeting with choices.
        dialog.setLine(player,dialog.greeting,spawn.name)
    # Otherwise reset dialog on client.
    else:
        player.mind.callRemote("setInitialInteraction",None,None)
    
    # Register the interaction.
    player.interacting = target
    target.interacting = player
    target.interactTimes[player] = sysTime()
    
    # And finally open the NPC window on the client.
    player.mind.callRemote("openNPCWnd",spawn.name)


def CmdAttack(mob, args):
    if len(args):
        if args[0].upper() == "ON":
            attacking = True
        elif args[0].upper() == "OFF":
            attacking = False
        else:
            attacking = not mob.autoAttack
    else:
        attacking = not mob.autoAttack
    mob.autoAttack = attacking
    
    if mob.character.dead:
        return
    
    if attacking and mob.target:
        if AllowHarmful(mob,mob.target):
            mob.attackOn()
        else:
            mob.attackOff()
    else:
        mob.attackOff()
    
    return


def CmdRangedAttack(mob,args):
    # everything will be handled herein
    mob.shootRanged()
    
    return
        
       
def CmdTargetId(mob, args):
    ''' CmdTargetId: Attempt to target a mob by mob id. '''

    # Function requires args to contain mobId and cycle option.
    if 2 > len(args):
        return
    
    mobToTargetId = int(args[0]) # Note: This is a mob id, not sim object id.
    cycle = int(args[1])
    
    # Clear target because mobToTargetId was zero.
    if not mobToTargetId:
        mob.zone.setTarget(mob, None)
        return
    
    # Target party members.
    for char in mob.player.party.members:
        if not char.dead and char.mob.id == mobToTargetId:
            mob.zone.setTarget(mob, char.mob)
            return
    
    # Return if the player is zoning.
    if mob.player.zone == None:
        return
    
    # Return if the mob has no simObject.
    if mob.simObject == None:
        return
    
    # Only search for mobs the source can see.
    simLookup = mob.zone.simAvatar.simLookup
    mobLookup = mob.zone.mobLookup
    for id in mob.simObject.canSee:
        
        # Try to find the mob by its sim id.
        try:
            mobInZone = mobLookup[simLookup[id]]
            
        # The mob has not spawned yet, but it is in cansee.
        except KeyError:
            continue
        
        # If the mob has been found. 
        if mobInZone.id == mobToTargetId:
  
            # Cycle only occurs if caller request.  Cycle is
            # used when wanting to target the party members
            # of another player.
            if not cycle:
                mob.zone.setTarget(mob, mobInZone, checkVisibility = True)
                return
                    
            # Cycle is enabled. 
            else:    
        
                # If the mobInZone is not a player or the 
                # player has no current target, cycling
                # can not occur, so set target to the mob.
                playerToTarget = mobInZone.player
                if not playerToTarget or not mob.target:
                    if not mobInZone.detached:
                        mob.zone.setTarget(mob, mobInZone, checkVisibility = True)
                    return
                        
                # Build a list of targets to cycle through from
                # the target player's alive party members.
                cycleMobs = [char.mob for char in playerToTarget.party.members if not char.dead]
                
                # If there are no cycle targets, return early.
                if not cycleMobs:
                    return
                
                # No cycling required, only one possible target.
                if 1 == len(cycleMobs):
                    mob.zone.setTarget(mob, cycleMobs[0])
                    return
                
                # Get the current mob's target Id.
                currentTargetId = mob.target.id
                
                # Iterate over the cycleMobs
                nextIndex = 0
                for cycleMob in cycleMobs:
                    nextIndex += 1
                    
                    # Break iterations once the cycle mob
                    # matches the current target.
                    if cycleMob.id == currentTargetId:
                        break
                
                # The current target was not found in the cycle list.
                # This should not occur, but return early just incase.
                else:
                    return

                # Set target and guarantee a safe index.
                mob.zone.setTarget(mob, cycleMobs[nextIndex % len(cycleMobs)])
                return
            
    # Get name of mob to target if it is provided.
    if 3 <= len(args):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot target %s.\n'%(mob.name,' '.join(args[2:])))


def CmdWorldMsg(mob, args):
    # If the player has been muted, return.
    if CheckMuted(mob):
        return
    
    # Get a handle to the player mob.
    player = mob.player
    
    # If the message is empty, return.
    if not len(args):
        return
    
    # Get the players character name, with and without chat pseudo formatting.
    name = player.charName
    sname = name.replace(' ','_')
    
    # Assemble the message.
    msg = ' '.join(args)
    msg = r'World: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(sname,name,msg)
    
    # Get a handle to the world the player is in.
    world = player.world
    
    # If this server uses multiple clusters, need to propagate the world
    #  message across them.
    if world.daemonPerspective:
        world.daemonPerspective.callRemote("propagateCmd","sendWorldMsg",name,msg)
    
    # Run through this servers players and send them the message.
    for p in world.activePlayers:
        #if name.upper() in p.ignored:
        #    continue
        p.sendSpeechText(RPG_MSG_SPEECH_WORLD,msg,name)


def CmdGuildMsg(mob, args):
    # If the player has been muted, return.
    if CheckMuted(mob):
        return
    
    # Get a handle to the player mob.
    player = mob.player
    
    # Get a handle to the players guild.
    guild = player.guildName
    
    # If the player is not a member of a guild, inform and return.
    if not guild:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of a guild.\\n")
        return
    
    # If the message is empty, return.
    if not len(args):
        return
    
    # Get the players character name, with and without chat pseudo formatting.
    name = player.charName
    sname = name.replace(' ','_')
    
    # Assemble the message.
    msg = ' '.join(args)
    msg = r'Guild: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(sname,name,msg)
    
    # Get a handle to the world the player is in.
    world = player.world
    
    # If this server uses multiple clusters, need to propagate the guild
    #  message across them.
    if world.daemonPerspective:
        world.daemonPerspective.callRemote("propagateCmd","sendGuildMsg",name,msg,guild)
    
    # Run through this servers players and send them the message.
    for p in world.activePlayers:
        #if name.upper() in p.ignored:
        #    continue
        # Exclude all players not members of this guild.
        if p.guildName != guild:
            continue
        p.sendSpeechText(RPG_MSG_SPEECH_GUILD,msg,name)


def CmdZoneMsg(mob,args):
    if CheckMuted(mob):
        return
    
    if not len(args):
        return
    
    msg = ' '.join(args)
    charName = mob.player.charName
    scharName = charName.replace(' ','_')
    msg = r'Zone: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(scharName,charName,msg)
    
    for p in mob.zone.players:
        #if mob.player.name.upper() in p.ignored:
        #    continue
        p.sendSpeechText(RPG_MSG_SPEECH_ZONE,msg,charName)


def CmdSayMsg(mob,args):
    if CheckMuted(mob):
        return
    player = mob.player
    
    if not len(args):
        return
    
    msg = ' '.join(args)
    charName = mob.player.charName
    scharName = charName.replace(' ','_')
    othermsg = r'<a:gamelinkcharlink%s>%s</a> says, \"%s\"\n'%(scharName,charName,msg)
    
    for p in mob.zone.players:
        #if mob.player.name.upper() in p.ignored:
        #    continue
        
        if p == player:
            p.sendSpeechText(RPG_MSG_SPEECH_SAY, r'You say, \"%s\"\n'%msg, charName)
        else:
            if GetRange(mob, p.curChar.mob) < 30:
                p.sendSpeechText(RPG_MSG_SPEECH_SAY,othermsg,charName)


def CmdLaugh(mob,args):
    #mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,"agree")
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
    mob.player.modelChar.mob.vocalize(VOX_LAUGH)
    if not args:
        if mob.target:
            args = ["laughs at %s."%mob.target.name]
        else:
            args = ["laughs."]
    CmdEmote(mob, args) 

def CmdScream(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
    mob.player.modelChar.mob.vocalize(VOX_MADSCREAM)
    if not args:
        if mob.target:
            args = ["screams at %s."%mob.target.name]
        else:
            args = ["screams."]
    CmdEmote(mob, args) 

def CmdGroan(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.cancelStatProcess("sneak","$tgt is no longer sneaking!\\n")
    mob.player.modelChar.mob.vocalize(VOX_GROAN)
    if not args:
        if mob.target:
            args = ["groans at %s."%mob.target.name]
        else:
            args = ["groans."]
    CmdEmote(mob, args) 
        

def CmdEmote(mob,args):
    if CheckMuted(mob):
        return
    
    if not len(args):
        return
    
    charName = mob.player.charName
    scharName = charName.replace(' ','_')
    msg = r'<a:gamelinkcharlink%s>%s</a> %s\n'%(scharName,charName,' '.join(args))
    
    for p in mob.zone.players:
        #if mob.player.name.upper() in p.ignored:
        #    continue
        
        if p == mob.player:
            p.sendSpeechText(RPG_MSG_SPEECH_EMOTE,msg,charName)
        else:
            if GetRange(mob,p.curChar.mob) < 30:
                p.sendSpeechText(RPG_MSG_SPEECH_EMOTE,msg,charName)


def CmdCamp(mob,args):
    player = mob.player
    player.logout()
    
    
def CmdAllianceMsg(mob,args):
    if not len(args):
        return
    
    mob.player.alliance.message(mob.player, ' '.join(args))


def CmdTime(mob,args):
    time = mob.player.world.time
    
    am = True
    
    hour = time.hour
    if 10 >= hour >= 4:
        msg = r'It is %i in the morning.\n'%hour
    elif 12 > hour > 10:
        msg = r'It is %i in the late morning.\n'%hour
    elif hour == 12:
        msg = r'It is around noon.\n'
    elif 16 >= hour > 12:
        msg = r'It is %i in the afternoon.\n'%(hour-12)
    elif 19 >= hour > 16:
        msg = r'It is %i in the early evening.\n'%(hour-12)
    elif 24 >= hour > 16:
        msg = r'It is %i at night.\n'%(hour-12)
    elif hour == 0:
        msg = r'It is around midnight.\n'
    else:
        msg = r'It is %i at night.\n'%hour
        
    mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,msg)


def CmdUpTime(mob,args):
    uptime = sysTime() - mob.player.world.launchTime
    t = timedelta(0,uptime)
    msg = "This world server has been up for %s.\\n"%str(t)
    mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,msg)


def CmdVersion(mob,args):
    msg = "Minions of Mirth World Server (v)1.01a\\n"
    msg +="Minions of Mirth Database (v)1.0a\\n"
    mob.player.sendGameText(RPG_MSG_GAME_GLOBAL,msg)


def CmdDance(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,"dance")
    if not args:
        if mob.target:
            args = ["dances for %s."%mob.target.name]
        else:
            args = ["dances."]
    CmdEmote(mob, args) 
    
    
def CmdPoint(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,"point")
    if not args:
        if mob.target:
            args = ["points at %s."%mob.target.name]
        else:
            args = ["points ahead."]
    CmdEmote(mob, args)    
    
def CmdAgree(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,"agree")
    if not args:
        if mob.target:
            args = ["agrees with %s."%mob.target.name]
        else:
            args = ["agrees."]
    CmdEmote(mob, args)  
    
def CmdDisagree(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,"disagree")
    if not args:
        if mob.target:
            args = ["disagrees with %s."%mob.target.name]
        else:
            args = ["disagrees."]
    CmdEmote(mob, args) 
    
def CmdBow(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,"bow")
    if not args:
        if mob.target:
            args = ["bows before %s."%mob.target.name]
        else:
            args = ["bows."]
    CmdEmote(mob, args)     
    
def CmdWave(mob,args):
    mob.cancelStatProcess("feignDeath","$tgt is obviously not dead!\\n")
    mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,"wave")
    if not args:
        if mob.target:
            args = ["waves at %s."%mob.target.name]
        else:
            args = ["waves."]
    CmdEmote(mob, args)   


def CmdCycleTarget(mob,args,doMouse=True,useInputMob = False,reverse = False):
    if not useInputMob:
        #curchar
        mob = mob.player.curChar.mob
    
    zone = mob.zone
    simAvatar = zone.simAvatar
    
    targets = []
    for id in mob.simObject.canSee:
        try:
            otherMob = zone.mobLookup[simAvatar.simLookup[id]]
        except KeyError:
            continue #not spawned yet, though in cansee
        
        kos = IsKOS(otherMob, mob)
        if otherMob.player or (otherMob.master and otherMob.master.player):
            kos = kos or AllowHarmful(mob, otherMob)
        if not kos or otherMob.detached:
            continue
        
        # If the othermob is not visible, skip it.
        if not IsVisible(mob, otherMob):
            continue
        
        if GetRange(otherMob,mob) < 100:
            targets.append(id)
    
    if not len(targets):
        return
    
    if not mob.target or mob.target.simObject.id not in targets or len(targets) == 1:
        tid = targets[0]
    else:
        index = targets.index(mob.target.simObject.id)
        
        if reverse:
            index -= 1
            if index < 0:
                index = len(targets) - 1
        else:
            index += 1
            if index == len(targets):
                index = 0
        
        tid = targets[index]
    
    tmob = zone.mobLookup[simAvatar.simLookup[tid]]
    zone.setTarget(mob,tmob)
    if doMouse:
        mob.player.mind.callRemote("mouseSelect",mob.charIndex,tmob.id)


def CmdCycleTargetBackwards(mob,args):        
    CmdCycleTarget(mob,args,True,False,True)


def CmdTargetNearest(mob,args,doMouse=True,useInputMob = False):
    if not useInputMob:
        #curchar
        mob = mob.player.curChar.mob
    
    zone = mob.zone
    simAvatar = zone.simAvatar
    
    target = -1
    best = 999999
    for id in mob.simObject.canSee:
        try:
            otherMob = zone.mobLookup[simAvatar.simLookup[id]]
        except KeyError:
            continue #not spawned yet, though in cansee
        kos = IsKOS(otherMob,mob)
        if otherMob.player or (otherMob.master and otherMob.master.player):
            kos = kos or AllowHarmful(mob, otherMob)
        if not kos or otherMob.detached:
            continue
        
        # If the othermob is not visible, skip it.
        if not IsVisible(mob, otherMob):
            continue
        
        r = GetRange(otherMob,mob)
        if  r < best:
            # Only target mobs that are infront of us.
            # If the other mob is within 4 units we select it even if it is behind.
            if r > 4:
                if not mob.isFacing(otherMob):
                    continue
            target = id
            best = r
    
    if target == -1:
        return
    
    tmob = zone.mobLookup[simAvatar.simLookup[target]]
    zone.setTarget(mob,tmob)
    if doMouse:
        mob.player.mind.callRemote("mouseSelect",mob.charIndex,tmob.id)


def FindMobByName(src, nameToFind):
    ''' FindMobByName: Attempts to locate and return a visible mob by name. '''
    
    nameToFind = nameToFind.upper()
    
    # Check sources party.
    for character in src.player.party.members:
        if character.name.upper() == nameToFind:
            
            # If the character is not detached, return the mob.
            if not character.mob.detached:
                return character.mob
            
            # Otherwise, the name was matched, but cannot target the mob.
            else:
                return None
    
    # Only search for mobs the source can see.
    zone = src.zone
    simLookup = zone.simAvatar.simLookup
    mobLookup = zone.mobLookup
    for id in src.simObject.canSee:
        
        # Try to find the mob by its sim id.
        try:
            otherMob = mobLookup[simLookup[id]]
            
        # The mob has not spawned yet, but it is in cansee.
        except KeyError:
            continue
        
        # If the mob is a player, check party member's for a match.
        if otherMob.player:
            for character in otherMob.player.party.members:
                
                # Check if character matches name.
                if character.name.upper() == nameToFind:
                    
                    mobToTarget = character.mob

                    # Character is targetable and visible.
                    if not mobToTarget.detached and IsVisible(src, mobToTarget):
                        return mobToTarget
                    
                    # Mob had matching name, but was either not
                    # targetable or visible.
                    else:
                        return None
                    

        # Otherwise, check mob.
        else:
            
            # Check if mob matches the name.
            if otherMob.name.upper() == nameToFind:
                
                # If the mob is not detached, target it.  An early
                # return does not occur if the mob is detached because
                # there can be mobs with the same name.
                if not otherMob.detached and IsVisible(src, otherMob):
                    return otherMob
    
    # No matches found.
    return None


def CmdAssist(mob,args):
    
    # If no arguements are provided, assist the current target.
    if not len(args):
        if mob.target:
            mob.zone.setTarget(mob,mob.target.target)
        return
    
    # Build name of mob to assist.
    mobToAssistName = ' '.join(args)
    
    # Always assist pet, without checking if the pet can be seen.
    if mobToAssistName.upper() == "PET":
        if mob.pet:
            mob.zone.setTarget(mob,mob.pet.target)
            return
        else:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot assist pet.\n'%mob.name)
            return
    
    # Find assist-mob by name.  If the assist-mob is found and
    # visible, set mob's target to be assist-mob's target.
    mobToAssist = FindMobByName(mob, mobToAssistName)
    if mobToAssist:
        mob.zone.setTarget(mob, mobToAssist.target, checkVisibility = True)
        return
    
    # Mob was not found, alert player.
    mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot assist %s.\n'%(mob.name,mobToAssistName))


def CmdTarget(mob,args):
    ''' CmdTarget: Target a mob by name. '''

    # Build name of mob to target.
    mobToTargetName = ' '.join(args)
    
    # Always target pet, without checking if the pet can be seen.
    if mobToTargetName.upper() == "PET":
        if mob.pet:
            mob.zone.setTarget(mob,mob.pet)
            return
        else:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot target pet.\n'%mob.name)
            return

    # Find visible target-mob by name.  If the target-mob
    # is found set the mob's target to the target-mob.
    mobToTarget = FindMobByName(mob, mobToTargetName)
    if mobToTarget:
        mob.zone.setTarget(mob,mobToTarget)
        return
    
    # Mob was not found, alert player.
    mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot target %s.\n'%(mob.name,mobToTargetName))


def CmdCast(mob,args):
    
    # If the mob is casting or if the mob is detached, 
    # return early.  Detached should be caught on client-side.
    if mob.casting or mob.detached:
        return
    
    # Build spell to cast name.
    spellToCastName = ' '.join(args)
    spellToCastNameUpper = spellToCastName.upper()
    
    # Iteraete through spells the character knows.    
    for knownSpell in mob.character.spells:
        
        # Check if the spell being casted is a spell the character konws.
        spellToCastProto = knownSpell.spellProto
        if spellToCastProto.name.upper() == spellToCastNameUpper:
            
            # Check if the mob is allowed to cast this spell.
            if spellToCastProto.qualify(mob):
                mob.cast(spellToCastProto, knownSpell.level)
            else:
                mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s does not know how to cast %s.\n'%(mob.name,spellToCastName))
            return
    
    # Iterated through all spells, but none matched the
    # name provided.
    else:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot cast %s.\n'%(mob.name,spellToCastName))


def CmdSkill(mob, args):
    # Build skill to use name.
    skillToUseName = ' '.join(args)
    skillToUseNameUpper = skillToUseName.upper()
    
    # Iteraete through skills the character knows.    
    for knownSkill in mob.mobSkillProfiles.iterkeys():
        
        # Check if the skill being used is a skill the character knows.
        if knownSkill.upper() == skillToUseNameUpper:
            from mud.world.skill import UseSkill
            UseSkill(mob,mob.target,knownSkill)
            return
    
    # Iterated through all skills, but none matched
    # the name provided.
    else:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot use the %s skill.\n'%(mob.name,skillToUseName))
        return


def CmdInvite(mob,args):
    mob.player.avatar.perspective_invite()


def CmdChannel(mob,args):
    player = mob.player
    if len(args)<2:
        return
    channel = args[0].lower()
    mode = args[1].lower()
            
    if channel == "world":
        if mode == "off":
            player.channelWorld =False
            player.sendGameText(RPG_MSG_GAME_GAINED,r'You are no longer listening to world chat.\n')
        else:
            player.channelWorld =True
            player.sendGameText(RPG_MSG_GAME_GAINED,r'You are now listening to world chat.\n')
        
    if channel == "zone":
        if mode == "off":
            player.channelZone =False
            player.sendGameText(RPG_MSG_GAME_GAINED,r'You are no longer listening to zone chat.\n')
        else:
            player.channelZone =True
            player.sendGameText(RPG_MSG_GAME_GAINED,r'You are now listening to zone chat.\n')
            
    if channel == "combat":
        if mode == "off":
            player.channelCombat =False
            player.sendGameText(RPG_MSG_GAME_GAINED,r"You are no longer listening to other's combat messages.\n")
        else:
            player.channelCombat =True
            player.sendGameText(RPG_MSG_GAME_GAINED,r"You are now listening to other's combat messages.\n")
        
    
def CmdStopCast(mob,args):
    if mob.casting:
        if mob.stopCastingTimer:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,r"%s cannot stop casting at this time.\n"%(mob.name))
            return
        mob.stopCastingTimer=60
        mob.casting.cancel()
        mob.player.sendGameText(RPG_MSG_GAME_YELLOW,r"%s stops casting.\n"%(mob.name))
        
    

def CmdSetPassword(mob,args):
    if CoreSettings.SINGLEPLAYER:
        return
    if CoreSettings.PGSERVER:
        return
    
    if len(args) != 1:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Please specify a password.\\n")
        return

    player = mob.player

    try:
        user = User.byName(player.publicName)
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown user %s.\\n"%player.publicName)
        return
    
    pw = args[0]
    if len(pw) < 6:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Password must be at least 6 characters.\\n")
        return
    
    user.password = player.password = pw
        
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Your password is now set to %s\\n"%(pw))


def CmdGetPassword(mob,args):
    if CoreSettings.SINGLEPLAYER:
        return
    
    if CoreSettings.PGSERVER:
        return

    

    player = mob.player

    try:
        user = User.byName(player.publicName)
    except:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Unknown user %s.\\n"%player.publicName)
        return
    
        
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"Your password is %s\\n"%(user.password))


def CmdDisenchant(mob, args):
    from mud.world.crafting import DisenchantCmd
    DisenchantCmd(mob, ' '.join(args).upper())


def CmdEnchant(mob,args):
    from mud.world.crafting import EnchantCmd
    EnchantCmd(mob, ' '.join(args).upper())


def CmdRoll(mob,args):
    r = randint(1,100)
    charName = mob.player.charName
    GameMessage(RPG_MSG_GAME_LEVELGAINED,mob.zone,mob,mob,"<a:gamelinkcharlink%s>%s</a> has rolled a %i.\\n"%(charName.replace(' ','_'),charName,r),mob.simObject.position,20)


def CmdUnlearn(mob, args):
    name = ' '.join(args)
    if not len(name):
        return
    
    name = name.lower()
    
    for spell in mob.character.spells:
        if spell.spellProto.name.lower()==name:
            sname = spell.spellProto.name
            spell.destroySelf()
            mob.character.spellsDirty=True
            mob.player.cinfoDirty=True
            mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s forgets all about the %s spell.\\n"%(mob.name,sname))        
            return
    

    mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't know the %s spell.\\n"%(mob.name,name))


def CmdWalk(mob, args):
    # Get a handle to this mobs player.
    player = mob.player
    
    # If there was an argument supplied, get it.
    if len(args):
        if 'ON' in args[0].upper():
            arg = True
        else:
            arg = False
    
    # Otherwise just toggle.
    else:
        arg = not player.walk
    
    # Give feedback to player if necessary.
    if arg != player.walk:
        if arg:
            player.sendGameText(RPG_MSG_GAME_EVENT, \
                "%s slows to a casual pace.\\n"%mob.name)
        else:
            player.sendGameText(RPG_MSG_GAME_EVENT, \
                "%s speeds up the pace.\\n"%mob.name)
    
    # Update the players walking state.
    player.walk = arg


def CmdClearLastName(mob, args):
    
    player = mob.player
    if not player.curChar.lastName:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have a last name.\\n"%(player.curChar.name))
        
    player.curChar.lastName = ""
    
    player.zone.simAvatar.setDisplayName(player)

    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s's last name has been cleared.\\n"%(player.curChar.name))
    
    
def CmdLastName(mob,args):
    player = mob.player
    
    #if player.curChar.spawn.realm == RPG_REALM_MONSTER:
    #    player.sendGameText(RPG_MSG_GAME_DENIED,"lastname: %s is a monster.\\n"%mob.player.curChar.name)
    #    return
        
    
    
    #perhaps lock this and allow gm's to flag name needing to be changed, ie. blanking name
    #if player.curChar.lastName:
    #    player.sendGameText(RPG_MSG_GAME_DENIED,"%s already has a last name.\\n"%mob.player.curChar.name)
    #    return

    if player.curChar.mob.plevel<25:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s must be level 25 before acquiring a last name.\\n"%mob.player.curChar.name)
        return
    
    if len(args)!=1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"lastname: incorrect number of arguments\\n")
        return
    
    last = args[0]
    if len(last)>12:
        player.sendGameText(RPG_MSG_GAME_DENIED,"lastname: must be less than 13 characters\\n")
        return

    if len(last)<4:
        player.sendGameText(RPG_MSG_GAME_DENIED,"lastname: must be at least 4 characters\\n")
        return
    
    if not last.isalpha():
        player.sendGameText(RPG_MSG_GAME_DENIED,"Guild names must not contain numbers, spaces, or punctuation marks.\\n")
        return
    
    player.curChar.lastName = last.capitalize()
    
    player.zone.simAvatar.setDisplayName(player)
    
    c = player.curChar
    player.sendGameText(RPG_MSG_GAME_GAINED,"%s is now known as %s %s!\\n"%(c.name,c.name,c.lastName))
    
def CmdChangeClass(mob,args):

    if len(args) != 3:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"changeclass: incorrect number of arguments")
        return
    
    which,name,klass = args
    which = which.upper()
    
    if which not in ("PRIMARY","SECONDARY","TERTIARY"):
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Please specify which class you which to change (primary, secondary, or tertiary)\\n")
        return
    
    if mob.name.upper() != name.upper():
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You must specify your active character's name (%s)\\n"%mob.name)
        return
    
    #mob.character.pchange = True
    #mob.character.schange = True
    #mob.character.tchange = True
    
    klasses = (mob.spawn.pclassInternal,mob.spawn.sclassInternal,mob.spawn.tclassInternal)
    if klass in klasses:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s is already a %s, unchanged.\\n"%(mob.name,klass))
        return
        
    
    if which == "PRIMARY" and not mob.character.pchange:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s may not change primary class at this time.\\n"%mob.name)
        return
    if which == "SECONDARY" and not mob.character.schange:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s may not change secondary class at this time.\\n"%mob.name)
        return
    if which == "TERTIARY" and not mob.character.tchange:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s may not change tertiary class at this time.\\n"%mob.name)
        return
    
    if mob.spawn.realm == RPG_REALM_MONSTER:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s is a monster and cannot change class.\\n"%mob.name)
        return

    if mob.spawn.realm == RPG_REALM_LIGHT:
        if klass not in RPG_REALM_LIGHT_CLASSES:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Invalid class specified (case sensitive and make sure realm allows it).\\n")
            return
    if mob.spawn.realm == RPG_REALM_DARKNESS:
        if klass not in RPG_REALM_DARKNESS_CLASSES:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Invalid class specified (case sensitive and make sure realm allows it).\\n")
            return
        
    if which == 'PRIMARY':
        mob.spawn.pclassInternal = klass
        mob.levelChanged()
        mob.character.pchange = False
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s's primary class has been changed to %s.\\n"%(mob.name,klass))        
        return
        
    if which == 'SECONDARY':
        if not mob.spawn.sclassInternal or not mob.spawn.slevel:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no secondary class, unchanged.\\n"%(mob.name))
            return
        
        mob.spawn.sclassInternal = klass
        mob.levelChanged()
        mob.character.schange = False
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s's secondary class has been changed to %s.\\n"%(mob.name,klass))        
        return
        
    if which == 'TERTIARY':
        if not mob.spawn.tclassInternal or not mob.spawn.tlevel:
            mob.player.sendGameText(RPG_MSG_GAME_DENIED,"%s has no tertiary class, unchanged.\\n"%(mob.name))
            return
        
        mob.spawn.tclassInternal = klass
        mob.levelChanged()
        mob.character.tchange = False
        mob.player.sendGameText(RPG_MSG_GAME_GAINED,"%s's tertiary class has been changed to %s.\\n"%(mob.name,klass))        
        return
            
def CmdServer(mob,args):
    wname = mob.player.world.multiName.replace("_"," ")
    
    mob.player.sendGameText(RPG_MSG_GAME_GAINED,"You are on the %s server\\n"%wname)        


def CmdResize(mob, args):
    ''' CmdResize: Command that will toggle between default spawn scale and
                   a the default human spawn scale.
    
        This is useful for player with a large character spawn that has 
        difficulties with zone geometry/npc interaction due to size.
        Setting the player override scale will cause sim udata to update the
        model's scale on the sim server.  The modified scale is for world 
        checks, such as combat and spell range.
    '''
    
    player = mob.player
    # Toggle player's scale override.
    if player.overrideScale:
        # Stop overriding scale and set modified scale to base scale.
        player.overrideScale = False
        mob.spawn.modifiedScale = mob.spawn.scale
    else:
        # Begin overriding scale, set modified scale to standard human size.
        player.overrideScale = True
        mob.spawn.modifiedScale = 1.0

    
# This function empties the contents of the craft window into the players
# inventory.  This function will attempt to reduce item into stacks if
# possible.
def CmdEmptyCraft(mob, args):
    
    # Collapse item stacks.
    items = dict((item.slot,item) for item in mob.character.items
                    if((RPG_SLOT_CRAFTING_BEGIN <= item.slot < RPG_SLOT_CRAFTING_END)
                        or (RPG_SLOT_CARRY_BEGIN <= item.slot < RPG_SLOT_CARRY_END)))
    stackInventory(mob, items)
    
    # Crafting items will be stored in a [slot, item] list.  This allows for preservation of order
    # when moving items to the inventory.
    (CRAFTING_SLOT, CRAFTING_ITEM) = range(2)
    craftingItems = []
    
    # Using a dictiontary for carry slots.  Although dictionary creation takes longer than a list,
    # the deletion invokations later are faster.
    carrySlots = dict((index, '') for index in xrange(RPG_SLOT_CARRY_BEGIN, RPG_SLOT_CARRY_END))
    
    # Iterate over the items, looking at the item's slot and handling it appropriately.
    for slot,item in items.iteritems():
        
        # Only items with a slot higher than crafting window begin are in the
        # crafting window.
        if RPG_SLOT_CRAFTING_BEGIN <= slot:
            craftingItems.append([slot, item])
        
        # Otherwise, the item is in a carry slot.  Delete the carry slot from the dictionary.
        else:
            del carrySlots[slot]
    
    # Sort the crafting items based on their current slots, this allows for order preservation
    # when moving items to carry slots.
    craftingItems.sort()
    
    # Determine how many items will actually be moved.  If there are more items needing moved
    # than slots available, only move the amount of items that will fit in the slots available.
    # Otherwise, move all of the items.
    itemsBeingMoved = 0
    if len(craftingItems) > len(carrySlots):
        itemsBeingMoved = len(carrySlots)
    else:
        itemsBeingMoved = len(craftingItems)

    
    # If there are items to move, then character info needs updated.
    if itemsBeingMoved:
        
        # Get a list of free slots available.  This list is already sorted, so items will be moved to slots
        # appearing at the beginning of the inventory first.
        freeSlots = carrySlots.keys()
        for index in xrange(itemsBeingMoved):
            craftingItems[index][CRAFTING_ITEM].slot = freeSlots[index]
            craftingItems[index][CRAFTING_ITEM].itemInfo.refreshDict({'SLOT':freeSlots[index]})

        # Set world to refresh client character info.
        mob.player.cinfoDirty = True


# This function calls stackInventory() method, passing in a dictionary of
# all inventory carry slots.
def CmdStackInventory(mob, args):
    
    # Create a list of items to be reduced.
    items = dict((item.slot,item) for item in mob.character.items if (RPG_SLOT_CARRY_BEGIN <= item.slot < RPG_SLOT_CARRY_END))
    
    stackInventory(mob, items)


# Enums used to define sort types.
(ALPHA_SORT, UNUSED_SORT) = range(2)


# This function sorts a subset of a player's inventory based on the 
# various arguments provided.
def CmdInventorySort(mob, args):
    
    # By default, the command is invoked as if it had the following arguements:
    # /sort all stack alpha
    start   = RPG_SLOT_CARRY_BEGIN
    end     = RPG_SLOT_CARRY_END
    items   = mob.character.items
    stack   = True
    reverse = False
    sort    = ALPHA_SORT
    
    # Set values based on the arguements provded by the caller.
    for word in args:
        if word.upper() == "PAGE1":
            start = RPG_SLOT_CARRY_BEGIN
            end   = RPG_SLOT_CARRY30
        
        elif word.upper() == "PAGE2":
            start = RPG_SLOT_CARRY30
            end   = RPG_SLOT_CARRY_END
        
        elif word.upper() == "NOSTACK":
            stack = False
        
        elif word.upper() == "REVERSE":
            reverse = True
    
    # Iterate through the entire itemset and create an item subset dictionary with key-value pairs
    # of item.slot and item if the item's slot is within the desired boundaries.
    itemSubsetDictionary = dict((item.slot,item) for item in items if (start <= item.slot < end))
    
    # Collapse item stacks if possible.
    if stack:
        stackInventory(mob, itemSubsetDictionary)
    
    # Build a dictionary whose values are sorted positions.
    positionDictionary = createSortedPositionDictionary(sort, reverse, itemSubsetDictionary)
    
    # Check if there are items ot sort.
    if len(itemSubsetDictionary):
        
        # Sort items in the subset dictionary based on the value in the position dictionary.
        # The start argument is used as the starting point for where the sorted items will be placed.
        # First verify that the dictionaries are the same size.  If they are not, then an item has been
        # removed somewhere in the process.  Sorting will not continue because a new or old item may be lost
        # if the sort assigned an item to the unknown used slot.
        if len(itemSubsetDictionary) == len(positionDictionary):
            
            # Iterate over each item and reassign its slot based on the position dictionary value.
            for key,item in itemSubsetDictionary.iteritems():
                newSlot = start + positionDictionary[key]
                item.slot = newSlot
                item.itemInfo.refreshDict({'SLOT':newSlot})
                        
        # Set world to refresh client character info.
        mob.player.cinfoDirty = True

# Create a sorted position dictionary with a key-value pair of item.slot and sorted position.
def createSortedPositionDictionary(sort, reverse, itemSubsetDictionary):
    positionDictionary = {}
    itemSortedList =     []
    
    # Use the supplied caller dictionary to create a list with tuples used for
    # sorting. item.slot always needs to be the last value in any sort tuple.
    # It is also suggested to use an enumeration to preserve the order if any
    # matches occur.
    
    # There is only one kind of sort right now, so default to alpha.
    #if ALPHA_SORT == sort:
    itemSortedList = [(item.name.lower(), item.itemProto.stackMax - item.stackCount, i, slot) for i,(slot,item) in enumerate(itemSubsetDictionary.iteritems())]
    
    # Sort the list.  The overall sort order depends on the created tuples.
    # Reverse sort if caller specified.
    itemSortedList.sort(reverse = reverse)
    
    # Item.slot should always be the last variable in a tuple.  
    # Since the length of the sort tuple may vary,  determine
    # the index for where item.slot is in the tuple.
    if 0 < len(itemSortedList):
        
        # Iterate through the sorted list, populating a dictionary.  The created
        # dictionary has a key-value pair of [item.slot] = sorted position index.
        for position,item in enumerate(itemSortedList):
            positionDictionary[item[-1]] = position
    
    return positionDictionary


# Define enums used for tuple index.
(FULL_STACKS, REMAINING_ITEMS, TOTAL_CHARGES) = range(3)
(ITEM_SLOT, ITEM_OBJECT) = range(2)

# This function attempts to stack items within a given item dictionary with item.slot as the key.
# The items argument is a dictionary key-value pair of item.slot and item.  This dictionary
# list may change in size as items are reduced into stacks.
def stackInventory(mob, items):
    
    stackableItems  = {}
    stackData       = {}
    
    # Iterate over all items provided by the caller.
    for item in items.itervalues():
        iproto = item.itemProto
        
        # Only process items that stack.
        if 1 < iproto.stackMax:
            
            # Check if the item uses charges.
            chargesMax = iproto.useMax
            
            # Append item to the stack list.
            # If there is not an item list for the item name, create one.
            try:
                stackableItems[item.name].append(item)
            except KeyError:
                stackableItems[item.name] = [item]
                stackData[item.name]      = [0, 0, 0]

            # Update the unmodified cumulative value of the stack count.  
            stackData[item.name][REMAINING_ITEMS] += item.stackCount
            
            # Calculate the total charges.
            if chargesMax:
                stackData[item.name][TOTAL_CHARGES] += chargesMax * ( item.stackCount - 1 ) + item.useCharges
        
    # Iterate over stackable items.
    for itemName,stackables in stackableItems.iteritems():
        iproto = stackables[0].itemProto
        stackMax = iproto.stackMax
        chargesMax = iproto.useMax
        
        # Attempt to collapse charges to items.
        if chargesMax:
            
            # Store uncollapsed and unmodified count.  This will be checked
            # against later to inform user if stack count changes due to
            # charges collasping into an item.
            uncollapsedCount = stackData[itemName][REMAINING_ITEMS]
            
            # Collapse the charges into items.
            stackData[itemName][REMAINING_ITEMS]  = stackData[itemName][TOTAL_CHARGES] / chargesMax
            stackData[itemName][TOTAL_CHARGES]   %= chargesMax
            
            # If the items did not collapse evenly, add an item that will
            # hold the charge count.
            if stackData[itemName][TOTAL_CHARGES]: 
                stackData[itemName][REMAINING_ITEMS] += 1
                
            # If it collapsed eventually, then the item has max charges.
            else:
                stackData[itemName][TOTAL_CHARGES] = chargesMax
            
            # Items collapsed, alert user.
            if uncollapsedCount > stackData[itemName][REMAINING_ITEMS]:
                mob.player.sendGameText(RPG_MSG_GAME_GAINED, "%s's charges collapsed into a single item.\\n"%(itemName))        
        
        # Collapse remaining items to full stacks.
        stackData[itemName][FULL_STACKS]      = stackData[itemName][REMAINING_ITEMS] / stackMax
        stackData[itemName][REMAINING_ITEMS] %= stackMax
        
        # Create a list and sort based on the item's slot position.  This allows 
        # for items appearing  earlier in the inventory to be full stacks, and
        # empty stacks later in the inventory to be expunged.
        sortedList = [(item.slot, item) for item in stackables]
        sortedList.sort()
        
        for itemTuple in sortedList:
            item = itemTuple[ITEM_OBJECT]
            
            #  If there are still full stack to make, create a stack with max items.
            if stackData[itemName][FULL_STACKS]:
                item.stackCount = stackMax
                stackData[itemName][FULL_STACKS] -= 1
                
                # If the item uses charges, charge values need to be updated.
                if chargesMax:

                    # If it is not the last stack, set charges to full charge.
                    if stackData[itemName][FULL_STACKS] or stackData[itemName][REMAINING_ITEMS]:
                        item.useCharges = chargesMax

                    # Otherwise, this is is the last stack, so set the charge value to the stored value.
                    else:
                        item.useCharges = stackData[itemName][TOTAL_CHARGES]
                    
                    item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})
                else:
                    item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
            
            # At this point, all full stacks have been created. The remaining stack will not be full,
            # so populate it with the remaining items.
            elif stackData[itemName][REMAINING_ITEMS]:
                item.stackCount = stackData[itemName][REMAINING_ITEMS]
                stackData[itemName][REMAINING_ITEMS] = 0
                
                # If the item uses charges, set the charge value to the stored value.
                if chargesMax:
                    item.useCharges = stackData[itemName][TOTAL_CHARGES]
                    item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})
                else:
                    item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
            
            # All items have been distributed.  Only empty stacks exists now.
            # These items need to be expunged.
            else:
                del items[item.slot]
                mob.player.takeItem(item)

    # If stackable items had been iterated over, have world update client.
    if len(stackableItems):
        mob.player.cinfoDirty = True


COMMANDS = {}

COMMANDS['CHANGECLASS'] = CmdChangeClass

COMMANDS['ROLL'] = CmdRoll

# Inventory/item sorts
COMMANDS['STACK'] = CmdStackInventory
COMMANDS['EMPTY'] = CmdEmptyCraft
COMMANDS['SORT']  = CmdInventorySort

#emotes
COMMANDS['DANCE']=CmdDance
COMMANDS['WAVE']=CmdWave
COMMANDS['AGREE']=CmdAgree
COMMANDS['YES']=CmdAgree
COMMANDS['DISAGREE']=CmdDisagree
COMMANDS['NO']=CmdDisagree
COMMANDS['POINT']=CmdPoint
COMMANDS['BOW']=CmdBow


COMMANDS['SETPASSWORD']=CmdSetPassword
COMMANDS['GETPASSWORD']=CmdGetPassword

COMMANDS['SERVER']=CmdServer

COMMANDS['ATTACK']=CmdAttack
COMMANDS['RANGEDATTACK']=CmdRangedAttack
COMMANDS['TARGETID']=CmdTargetId
COMMANDS['INTERACT']=CmdInteract

COMMANDS['BIND']=CmdBind
COMMANDS['PET']=CmdPet

COMMANDS['DISENCHANT']=CmdDisenchant
COMMANDS['ENCHANT']=CmdEnchant

COMMANDS['E']=CmdEmote
COMMANDS['ME']=CmdEmote

COMMANDS['EMOTE']=CmdEmote
COMMANDS['LAUGH']=CmdLaugh
COMMANDS['SCREAM']=CmdScream
COMMANDS['GROAN']=CmdGroan

COMMANDS['CHANNEL']=CmdChannel

COMMANDS['S']=CmdSayMsg
COMMANDS['SAY']=CmdSayMsg

COMMANDS['W']=CmdWorldMsg
COMMANDS['WORLD']=CmdWorldMsg

COMMANDS['Z']=CmdZoneMsg
COMMANDS['ZONE']=CmdZoneMsg

COMMANDS['A']=CmdAllianceMsg
COMMANDS['ALLIANCE']=CmdAllianceMsg

COMMANDS['UPTIME']=CmdUpTime

COMMANDS['CAST']=CmdCast
COMMANDS['SKILL']=CmdSkill

COMMANDS['CAMP']=CmdCamp

COMMANDS['TIME']=CmdTime

COMMANDS['EVAL'] = CmdEval
COMMANDS['DESC'] = CmdDesc
COMMANDS['MYDESC'] = CmdMyDesc

COMMANDS['AVATAR']=CmdAvatar

COMMANDS['SUICIDE']=CmdSuicide

COMMANDS['LADDER']=CmdLadder

COMMANDS['CYCLETARGET']=CmdCycleTarget
COMMANDS['CYCLETARGETBACKWARDS']=CmdCycleTargetBackwards
COMMANDS['TARGETNEAREST']=CmdTargetNearest

COMMANDS['TARGET']=CmdTarget
COMMANDS['ASSIST']=CmdAssist

COMMANDS['VERSION']=CmdVersion

COMMANDS['LASTNAME']=CmdLastName
COMMANDS['CLEARLASTNAME']=CmdClearLastName


COMMANDS['WHO']=CmdWho

COMMANDS['INVITE']=CmdInvite

COMMANDS['UNSTICK']=CmdUnstick
COMMANDS['RESIZE']=CmdResize

COMMANDS['STOPCAST']=CmdStopCast

COMMANDS['UNLEARN']=CmdUnlearn

COMMANDS['WALK'] = CmdWalk

#GUILDS

COMMANDS['GCREATE']=GuildCreate
COMMANDS['GLEAVE']=GuildLeave
COMMANDS['GINVITE']=GuildInvite
COMMANDS['GJOIN']=GuildJoin
COMMANDS['GDECLINE']=GuildDecline
COMMANDS['GPROMOTE']=GuildPromote
COMMANDS['GDEMOTE']=GuildDemote
COMMANDS['GREMOVE']=GuildRemove
COMMANDS['GSETMOTD']=GuildSetMOTD
COMMANDS['GCLEARMOTD']=GuildClearMOTD
COMMANDS['GROSTER']=GuildRoster
COMMANDS['GSETLEADER']=GuildSetLeader
COMMANDS['GDISBAND']=GuildDisband
COMMANDS['GCHARACTERS']=GuildCharacters
COMMANDS['G']=CmdGuildMsg
COMMANDS['GUILD']=CmdGuildMsg
COMMANDS['GPUBLICNAME']=GuildPublicName



def DoCommand(mob,cmd,args):
    if type(args) != list:
        args = [args]

    cmd = cmd.upper()
    if COMMANDS.has_key(cmd):
        COMMANDS[cmd](mob,args)
    else:
        print "Unknown Command",cmd
        mob.player.sendGameText(RPG_MSG_GAME_DENIED, r'Unknown command: %s.\n'%cmd)


