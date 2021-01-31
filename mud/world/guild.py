# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#guild commands
from defines import *
from messages import GameMessage
from core import *
import random
import time
import traceback,sys

def SendCharacterInfo(player):
    c = player.party.members[0]
    s = c.spawn
    prefix = ""
    if player.avatar and player.avatar.masterPerspective:
        if player.avatar.masterPerspective.avatars.has_key("GuardianAvatar"):
            prefix = "(Guardian) "
        if player.avatar.masterPerspective.avatars.has_key("ImmortalAvatar"):
            prefix = "(Immortal) "

    cinfo = (prefix,c.name,s.realm,s.pclassInternal,s.sclassInternal,s.tclassInternal,s.plevel,s.slevel,s.tlevel,player.zone.zone.niceName,player.guildName)
    
    player.world.daemonPerspective.callRemote("setCharacterInfo",player.publicName,cinfo)


def GotGuildCreate(result,player,guildName):
    code,text,users = result
    if not code:
        player.guildName = guildName
        player.guildRank = 2
        player.guildMOTD = ""
        player.guildInfo = ""
        player.guildInvite = None
        player.sendGameText(RPG_MSG_GAME_GAINED,"Congratulations, the guild has been created.\\n")
        player.zone.simAvatar.setDisplayName(player)
        SendCharacterInfo(player)
        charters = []
        for item in player.party.members[0].items:
            if item.name == "Guild Charter":
                if (RPG_SLOT_CARRY_END > item.slot >= RPG_SLOT_CARRY_BEGIN) or (RPG_SLOT_CRAFTING_END > item.slot >= RPG_SLOT_CRAFTING_BEGIN):
                    charters.append(item)
        for item in charters:
            player.takeItem(item)
        return
    
    if users and len(users):
        text = "\\nYou must have signed guild charters from 3 different members.  The following charters are from members who are already in a guild and can't be used: %s\\n"%', '.join(users)
        
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)
    
#/gcreate on client should open up a window for creating guild?

def GuildCreate(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:
        return 
    
    if not mob.player.premium:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to create guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return


    if len(args)<1:
        return
    

    player = mob.player
        
    charters = []
    for item in mob.character.items:
        if item.name == "Guild Charter":
            if (RPG_SLOT_CARRY_END > item.slot >= RPG_SLOT_CARRY_BEGIN) or (RPG_SLOT_CRAFTING_END > item.slot >= RPG_SLOT_CRAFTING_BEGIN):
                charters.append(item)
                
    if len(charters)<3:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You must have signed charters from 3 members before forming the guild.\\n")
        return
    
    cnames = []
    for c in charters:
        desc = c.descOverride
        desc = desc.split("This charter has been signed by ")
        try:
            if desc[1] not in cnames:
                cnames.append(desc[1])
        except:
            pass

    if len(cnames)<3:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"You must have signed charters from 3 different members before forming the guild.\\n")
        return
        
    name = ' '.join(args)
    
    if not name.replace(' ','').replace('\'','').isalpha():
        player.sendGameText(RPG_MSG_GAME_DENIED,"Guild names must not contain numbers or punctuation marks other than apostrophe.\\n")
        return

    
    if len(name)>24:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Guild names must be 24 characters or less.\\n")
        return
    if len(name)<6:
        mob.player.sendGameText(RPG_MSG_GAME_DENIED,"Guild names must be at least 6 characters in length.\\n")
        return
    
    
    d = AVATAR.mind.callRemote("createGuild",name,player.publicName,cnames)
    d.addCallback(GotGuildCreate,player,name)


def GotGuildDisband(result,player):
    code,text = result
    if not code:
        #do this here?
        player.guildName = ""
        player.guildInfo = ""
        player.guildMOTD = ""
        player.guildRank = 0
        player.guildInvite = None
        player.sendGameText(RPG_MSG_GAME_GAINED,"The guild has been disbanded.\\n")
        player.zone.simAvatar.setDisplayName(player)
        SendCharacterInfo(player)
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)    
        
def GuildDisband(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<2:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild leader.\\n")
        return
        
    d = AVATAR.mind.callRemote("disbandGuild",player.guildName,player.publicName)
    d.addCallback(GotGuildDisband,player)



def GotGuildSetLeader(result,player,promote):
    code,text = result
    if not code:
        promote.guildRank = 2
        player.guildRank = 1
        player.sendGameText(RPG_MSG_GAME_GAINED,"%s is now the guild leader.  You are now an officer.\\n"%promote.publicName)
        promote.sendGameText(RPG_MSG_GAME_GAINED,"You are now the guild leader.\\n")
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)
        

def GuildSetLeader(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if len(args)<1:
        return
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<2:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild leader.\\n")
        return
    
    name = args[0].upper()
    promote = None
    for p in mob.zone.players:
        if p.publicName.upper()==name:
            promote = p
            break
    if not promote:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is not in this zone.\\n"%args[0])
        return
    
    if promote == player:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You cannot set the leader to yourself.\\n")
        return
    
    if promote.guildName != player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is not a member of the guild.\\n"%(args[0]))
        return
    
    d = AVATAR.mind.callRemote("setGuildLeader",player.guildName,player.publicName,promote.publicName)
    d.addCallback(GotGuildSetLeader,player,promote)


def GotGuildRoster(result,player):
    code,text = result
    if not code:
        r = text
        leader = ""
        officers = ""
        members = ""
        for name,rank in r:
            if rank == 2:
                leader = name
            elif rank == 1:
                officers+="%s, "%name
            else:
                members+="%s, "%name
                
        text = "Leader: %s\\n"%leader
        
        if officers:
            text += "Officers: %s\\n"%officers[:-2]
        if members:
            text += "Members: %s\\n"%members[:-2]
                
        player.sendGameText(RPG_MSG_GAME_WHITE,"<%s> Roster:\\n%s"%(player.guildName,text))
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)    

def GuildRoster(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild officer.\\n")
        return
        
    d = AVATAR.mind.callRemote("getGuildRoster",player.guildName,player.publicName)
    d.addCallback(GotGuildRoster,player)


def GotGuildCharacters(result,player,who):
    code,characters = result
    if not code:
        
        chars = [c[0] for c in characters]
        text = "Characters for guild member: %s\\n%s\\n"%(who,', '.join(chars))
                
        player.sendGameText(RPG_MSG_GAME_WHITE,text)
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%characters)    


def GuildCharacters(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild officer.\\n")
        return
    
    if not len(args):
        player.sendGameText(RPG_MSG_GAME_DENIED,"Please specify the public name of the member to display characters.\\n")
        return
        
        
    d = AVATAR.mind.callRemote("getGuildCharacters",player.guildName,player.publicName,args[0])
    d.addCallback(GotGuildCharacters,player,args[0])

def GotGuildPublicName(result,player,cname):
    code,pname = result
    if not code:
        player.sendGameText(RPG_MSG_GAME_WHITE,"Character %s belongs to guild member %s.\\n"%(cname,pname))
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%pname)    


def GuildPublicName(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild officer.\\n")
        return
    
    if not len(args):
        player.sendGameText(RPG_MSG_GAME_DENIED,"Please specify the character name of the member to display their public name.\\n")
        return
        
    cname = ' '.join(args)
        
    d = AVATAR.mind.callRemote("getGuildPublicName",player.guildName,player.publicName,cname)
    d.addCallback(GotGuildPublicName,player,cname)
    

def GotGuildClearMOTD(result,player):
    code,text = result
    if not code:
        player.sendGameText(RPG_MSG_GAME_GAINED,"Guild MOTD cleared.\\n")
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)    
        
def GuildClearMOTD(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild officer.\\n")
        return
        
    d = AVATAR.mind.callRemote("clearGuildMOTD",player.guildName,player.publicName)
    d.addCallback(GotGuildClearMOTD,player)


def GotGuildSetMOTD(result,player,text):
    code,t = result
    if not code:
        player.sendGameText(RPG_MSG_GAME_GAINED,"Guild MOTD set to: %s\\n"%text)
        return
    

    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%t)    
        
    

def GuildSetMOTD(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if len(args)<1:
        return
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild officer.\\n")
        return
    
    text = ""
    for w in args:
        text+=w+" "
    if len(text) < 10:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The MOTD must be at least 10 characters in length.\\n")
        return

    if len(text) > 192:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The MOTD must be less than 192 characters in length.\\n")
        return
        
    d = AVATAR.mind.callRemote("setGuildMOTD",player.guildName,player.publicName,text)
    d.addCallback(GotGuildSetMOTD,player,text)
    
def GotGuildRemove(result,player,removed):
    code,text = result
    if not code:
        player.sendGameText(RPG_MSG_GAME_GAINED,"%s\\n"%text)
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)


def GuildRemove(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if len(args)<1:
        return
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild officer.\\n")
        return
    
    name = args[0].upper()
        
    d = AVATAR.mind.callRemote("removeGuildMember",player.guildName,player.publicName,name)
    d.addCallback(GotGuildRemove,player,name)

    

def GotGuildDemote(result,player):
    code,text = result
    if not code:
        player.sendGameText(RPG_MSG_GAME_GAINED,"%s\\n"%text)
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)


def GuildDemote(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if len(args)<1:
        return
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<2:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild leader.\\n")
        return
    
    name = args[0].upper()
        
    d = AVATAR.mind.callRemote("demoteGuildMember",player.guildName,player.publicName,name)
    d.addCallback(GotGuildDemote,player)


def GotGuildPromote(result,player,promote):
    code,text = result
    if not code:
        promote.guildRank = 1
        player.sendGameText(RPG_MSG_GAME_GAINED,"%s is now a guild officer.\\n"%promote.publicName)
        promote.sendGameText(RPG_MSG_GAME_GAINED,"You are now a guild officer.\\n")
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)
        

def GuildPromote(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if len(args)<1:
        return
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<2:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild leader.\\n")
        return
    
    name = args[0].upper()
    promote = None
    for p in mob.zone.players:
        if p.publicName.upper()==name:
            promote = p
            break
    if not promote:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is not in this zone.\\n"%args[0])
        return
    
    if promote == player:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You cannot promote yourself.\\n")
        return
    
    if promote.guildName != player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is not a member of the guild.\\n"%(args[0]))
        return
    
        
    
    d = AVATAR.mind.callRemote("promoteGuildMember",player.guildName,player.publicName,promote.publicName)
    d.addCallback(GotGuildPromote,player,promote)

    
def GotGuildLeave(result,player):
    code,text = result
    if not code:
        #do this here?
        player.guildName = ""
        player.guildInfo = ""
        player.guildMOTD = ""
        player.guildRank = 0
        player.guildInvite = None
        player.sendGameText(RPG_MSG_GAME_GAINED,"You have left the guild.\\n")
        player.zone.simAvatar.setDisplayName(player)
        SendCharacterInfo(player)
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)
        
def GuildLeave(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
        
    d = AVATAR.mind.callRemote("leaveGuild",player.guildName,player.publicName)
    d.addCallback(GotGuildLeave,player)
        
def GotGuildJoin(result,player):
    code,text = result
    if not code:
        ginfo = text
        player.guildName = ginfo[0]
        player.guildRank = ginfo[1]
        player.guildMOTD = ginfo[2]
        player.guildInfo = ginfo[3]        
        player.sendGameText(RPG_MSG_GAME_GAINED,"Congratulations, you have joined the <%s> guild!\\n"%ginfo[0])
        player.zone.simAvatar.setDisplayName(player)
        SendCharacterInfo(player)
        return
    
    player.sendGameText(RPG_MSG_GAME_DENIED,"%s\\n"%text)

def GuildJoin(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are already a guild member of <%s>.\\n"%player.guildName)#this should never happen
        return
        
    if not player.guildInvite:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You haven't been invited to a guild.\\n")
        return
    
    s,inviter = player.guildInvite 
    player.guildInvite= None
    d = AVATAR.mind.callRemote("addGuildMember",s,player.publicName,inviter)
    d.addCallback(GotGuildJoin,player)

def GuildDecline(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildInvite:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You haven't been invited to a guild.\\n")
        return

    s,inviter = player.guildInvite
    player.guildInvite=None
    player.sendGameText(RPG_MSG_GAME_DENIED,"You have declined to join the <%s> guild.\\n"%s)
    


def GuildInvite(mob,args):
    from cserveravatar import AVATAR
    if not AVATAR:    
        return 
    
    player = mob.player
    
    if len(args)<1:
        return
    
    if not player.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"The Premium Edition is required to enjoy guilds.  Please see www.prairiegames.com for ordering information.\\n")
        return
    
    if not player.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a member of any guild.\\n")
        return
            
    if player.guildRank<1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"You are not a guild officer or leader.\\n")
        return
    
    name = args[0].upper()
    invite = None
    for p in mob.zone.players:
        if p.charName.upper()==name:
            invite = p
            break
    if not invite:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is not in this zone.\\n"%args[0])
        return

    if not invite.premium:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s must have the Premium Edition to join the guild.\\n"%args[0])
        return

    if invite.guildName:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is already a guild member of <%s>.\\n"%(args[0],invite.guildName))
        return


    if invite.guildInvite:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is already considering a guild.\\n"%args[0])
        return
    
    invite.guildInvite = (player.guildName,player.publicName)
    player.sendGameText(RPG_MSG_GAME_GAINED,"You have invited %s to join the guild.\\n"%args[0])
    invite.sendGameText(RPG_MSG_GAME_GAINED,"You have been invited to join the <%s> guild.\\n"%(player.guildName))
        
        
    
