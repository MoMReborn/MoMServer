# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#upto 36 grouped characters, yikes!
import time
from mud.world.shared.playdata import AllianceInfo
from twisted.internet import reactor
from mud.world.defines import *
import math
from core import *

from mud.worlddocs.utils import GetTWikiName
from mud.world.shared.sounddefs import *
import traceback
from copy import copy

XPBONUS = (1,2.5,4.0,5.5,8.0,9.5)

#your alliance timestamp changes when:

#new alliance, leave alliance

class Alliance:
    #leaders->[(pname,cname)]
    masterAllianceInfo = {}
    def __init__(self,leader,remoteLeaderName=None):
        self.leader = leader
        self.members = [leader]
        self.invites = []

        self.world = leader.world
        if not remoteLeaderName:
            self.remoteLeaderName = self.leader.publicName
            if self.world.daemonPerspective:
                info = Alliance.masterAllianceInfo[self.remoteLeaderName] = [(leader.publicName,leader.party.members[0].name)]
                self.world.daemonPerspective.callRemote("setAllianceInfo",leader.publicName,info)
        else:
            self.remoteLeaderName = remoteLeaderName
            
        self.allianceInfo = AllianceInfo(self)

        self.setupForPlayer(leader)
        
        self.tick()
    
    
    def setupForPlayer(self,player):
        player.alliance = self
        player.mind.callRemote("setAllianceInfo",self.allianceInfo)
        player.mind.callRemote("setAllianceInvite",None)
    
    
    def giveMoney(self,source,worth):
        if not len(self.members):
            print "WARNING: Alliance with no members in giveMoney"
            return

        rewards = []
        for m in self.members:
            if m == source:
                rewards.append(m)
                continue
            if m.zone != source.zone:
                continue
                
            if GetRange(m.party.members[0].mob,source.party.members[0].mob) > 50:
                continue
                
            rewards.append(m)
        
        num = len(rewards)
        
        if worth < num:
            worth = num
        if num <1:
            return
        worth /= num
        
        wtext = GenMoneyText(worth)
        
        for m in rewards:
            m.giveMoney(worth)
            m.mind.callRemote("playSound",SND_COINS)
            if num > 1:
                m.sendGameText(RPG_MSG_GAME_GAINED,"Your share of the wealth is: %s\\n"%wtext)
            else:
                m.sendGameText(RPG_MSG_GAME_GAINED,"You plunder %s from the corpse.\\n"%wtext)
    
    
    def rewardXP(self,source,totalXP,isKill=False,best=1):
        count = 0
        
        if not len(self.members):
            print "WARNING: Alliance with no members in rewardXP"
            return
        
        rewards = []
        for m in self.members:
            if m == source:
                rewards.append(m)
                continue
            if m.zone != source.zone:
                continue
                
            if GetRange(m.party.members[0].mob,source.party.members[0].mob) > 50:
                continue
            
            rewards.append(m)
        
        num = len(rewards)
        
        if isKill and num == 1 and len(rewards[0].party.members) == 1:
            totalXP*=1.33
        if num < 1:
            return
        memberXP = int(math.ceil(float(totalXP) / float(num)))
        memberXP *= XPBONUS[num-1]
        if not isKill:
            best = 1
        for m in rewards:
            m.rewardXP(memberXP,best)
    
    
    def rewardFaction(self,source,faction,amount):
        count = 0
        
        if not len(self.members):
            print "WARNING: Alliance with no members in rewardFaction"
            return

        rewards = []
        for m in self.members:
            if m == source:
                rewards.append(m)
                continue
            if m.zone != source.zone:
                continue
                
            if GetRange(m.party.members[0].mob,source.party.members[0].mob) > 50:
                continue
                
            rewards.append(m)
        
        num = len(rewards)
        
        if num < 1:
            return
        memberFaction = int(math.ceil(float(amount)/float(num)))
        #memberFaction*=XPBONUS[num]
        for m in rewards:
            m.rewardFaction(faction,memberFaction)
        
    
    def rewardKillFaction(self,killer,mob):
        factions = list(mob.spawn.factions)
        if not len(factions):
            return
        
        if not len(self.members):
            print "WARNING: Alliance with no members in rewardKillFaction"
            return

        totalFaction = float(mob.plevel*3)
        
        #decrease factions
        for f in factions:
            self.rewardFaction(killer,f,-totalFaction)
            
        for kf in mob.spawn.killFactions:
            
            if kf.percent < 0:
                kfaction = math.ceil((totalFaction/2.0)*kf.percent) #easier to lose faction
            else:
                kfaction = math.ceil((totalFaction/4.0)*kf.percent) #harder to gain
                
            self.rewardFaction(killer,kf.faction,kfaction)
                
            #this shouldn't be automatic
            #increase/decease related factions
            #for r in list(f.relations):
            #    if r.relation < 0:
            #        
            #    if r.relation > 0:
            #        self.rewardFaction(killer,r.otherFaction,-math.ceil(float(totalFaction)/2.0))
    
    
    # Penalize the killing of other players with
    #  too low relative level.
    def killPenalty(self,killer,mob):
        if not len(self.members):
            print "WARNING: Alliance with no members in killPenalty"
            return
        
        # Set up kill penalty message according to realm.
        if mob.realm == RPG_REALM_LIGHT:
            msg = "transgressed against the gods of light!"
        elif mob.realm == RPG_REALM_DARKNESS:
            msg = "transgressed against the gods of darkness!"
        else:
            msg = "displeased the earthbound!"
        
        # Get the name of the killer. Replace spaces with
        #  underscores to get internal name.
        killerName = killer.charName
        skillerName = killerName.replace(' ','_')
        
        # All alliance members must know.
        for player in self.members:
            # If this is the killer, every character in the killers party
            #  loses a good amount of experience, depending on his level
            #  to accomodate for any exponential increases in strength and
            #  experience.
            if killer == player:
                player.sendGameText(RPG_MSG_GAME_YELLOW,r'You have %s\n'%(msg))
                for character in player.party.members:
                    character.loseXP(1.5*float(character.spawn.plevel),False)
            # Else notify the other members of the killers transgression.
            else:
                player.sendGameText(RPG_MSG_GAME_YELLOW,r'<a:gamelinkcharlink%s>%s</a> has %s\n'%(skillerName,killerName,msg))
    
    
    def rewardKillXP(self,killer,mob):
        #todo alliances
        
        if not len(self.members):
            print "WARNING: Alliance with no members in rewardKillXp"
            return
        
        best = 1
        try:
            for m in self.members:
                if len(self.members) > 1 and m.role.name == "Immortal":
                    continue
                for char in m.party.members:
                    if char.mob.plevel > best and not char.dead:
                        best = char.mob.plevel
        except:
            traceback.print_exc()
            print "Warning: Exception in getting best alliance member for rewardKillXP"
            best = mob.plevel
        
        if mob.player:
            if not mob.playerInitiate[killer][0] and best - mob.plevel > 10:
                #penalty!
                self.killPenalty(killer,mob)
                return False
        
        #no XP for player vs player kills right now
        if mob.player:
            return True
        
        adjust = float(mob.plevel - best)
        
        if adjust < -10:
            return False#no XP for mobs < 10 levels
        
        if adjust < 0:
            adjust /= 5.0
        
        if adjust > 10.0:
            adjust = 10.0
        
        totalXP = mob.plevel*12.5
        if mob.slevel:
            totalXP += mob.slevel*6.5
        if mob.tlevel:
            totalXP += mob.tlevel*2.5
        
        totalXP *= mob.xpMod
        totalXP += totalXP
        totalXP *= killer.zone.xpMod
        totalXP += totalXP*(mob.plevel/10)
        
        if mob.spawn.difficultyMod > 1.0 or mob.spawn.damageMod > 1.0 or mob.spawn.healthMod > 1.0:
            # determine which modifier is the greatest value
            xpModifier = 1.0
            if mob.spawn.difficultyMod > xpModifier:
                xpModifier = mob.spawn.difficultyMod
            if mob.spawn.damageMod > xpModifier:
                xpModifier = mob.spawn.damageMod
            if mob.spawn.healthMod > xpModifier:
                xpModifier = mob.spawn.healthMod
            # modify the totalXP by the greatest modifier
            totalXP += totalXP * (xpModifier * 3)
        elif mob.spawn.flags&RPG_SPAWN_UNIQUE:
            totalXP += totalXP * (.5)
        
        totalXP /= 100.0
        if mob.slevel and mob.tlevel:
            totalXP = int(math.ceil(totalXP+mob.plevel*4.0+mob.slevel*2+mob.tlevel)*1.2)+35
        elif mob.slevel:
            totalXP = int(math.ceil(totalXP+mob.plevel*4.0+mob.slevel*2)*1.2)+35
        else:
            totalXP = int(math.ceil(totalXP+mob.plevel*4.0)*1.2)+35
        
        totalXP += totalXP*(adjust*.25)
        
        self.rewardXP(killer,totalXP,True,best)
        
        return True
    
    
    def lootMessage(self,sender, lootitem):
        senderName = sender.charName
        ssenderName = senderName.replace(' ','_')
        for m in self.members:
            if sender == m:
                m.sendGameText(RPG_MSG_GAME_YELLOW,r'You have looted: <a:Item%s>%s</a>\n'%(GetTWikiName(lootitem.itemProto.name),lootitem.name))
            else:
                m.sendGameText(RPG_MSG_GAME_YELLOW,r'<a:gamelinkcharlink%s>%s</a> has looted: <a:Item%s>%s</a>\n'%(ssenderName,senderName,GetTWikiName(lootitem.itemProto.name),lootitem.name))
    
    
    def message(self, sender, msg):
        # Get the senders character name, with and without chat pseudo formatting.
        name = sender.charName
        sname = name.replace(' ','_')
        
        # Assemble the message.
        msg = r'Alliance: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(sname,name,msg)
        
        # If this server uses multiple clusters, check if there are alliance
        #  members in a different cluster.
        if self.world.daemonPerspective:
            # More members in alliance than current instance means members
            #  in other clusters.
            if self.countMembers() > len(self.members):
                # Inform the members in other clusters.
                self.world.daemonPerspective.callRemote("propagateCmd","sendAllianceMsg",name,msg,self.remoteLeaderName)
        
        # Run through all members in the current cluster and send them the message.
        for m in self.members:
            m.sendSpeechText(RPG_MSG_SPEECH_ALLIANCE,msg,name)
    
    
    def kick(self,name):
        if self.remoteLeaderName != self.leader.publicName:
            return
        
        who = None
        for m in self.members:
            if m.party.members[0].name.lower() == name.lower():
                who = m
                break
        
        if self.world.daemonPerspective:
            a = Alliance.masterAllianceInfo[self.remoteLeaderName]
            info = [(pname,cname) for pname,cname in a if pname != name]
            if info != a:
                self.world.daemonPerspective.callRemote("setAllianceInfo",self.remoteLeaderName,info)
        
        if who:
            if who == self.leader:
                return
            leaderName = self.leader.charName
            sleaderName = leaderName.replace(' ','_')
            who.sendGameText(RPG_MSG_GAME_GOOD,"You have been removed from <a:gamelinkcharlink%s>%s</a>'s alliance.\\n"%(sleaderName,leaderName))
            
            self.leave(who)
    
    
    def invite(self,who):
        if self.remoteLeaderName != self.leader.publicName:
            return
        who.invite = Invite(who,self.leader)
        self.invites.append(who.invite)
        who.mind.callRemote("setAllianceInvite",self.remoteLeaderName)
    
    
    def disband(self):
        if not self.leader:
            print "WARNING: Alliance disbanded with no leader!"
            return
        output = self.leader.publicName == self.remoteLeaderName
        self.cancelInvites()
        leader = self.leader
        self.leader = None
        leaderName = leader.charName
        sleaderName = leaderName.replace(' ','_')
        for m in self.members:
            if not m.loggingOut and not m.transfering:
                m.alliance = Alliance(m)
                if m == leader and output:
                    m.sendGameText(RPG_MSG_GAME_GOOD,"Your alliance has been disbanded.\\n")
                elif output:
                    m.sendGameText(RPG_MSG_GAME_GOOD,"<a:gamelinkcharlink%s>%s</a>'s alliance has been disbanded.\\n"%(sleaderName,leaderName))
            else:
                m.alliance = None
        self.members = []
    
    
    #make sure this is never called for the leader, they must disband
    def leave(self,who):
        if not who.transfering and who.publicName == self.remoteLeaderName:
            self.disband()
            return
        
        if len(self.members) == 1:
            #we are a remote alliance
            self.disband()
            if not who.transfering:
                try:
                    who.sendGameText(RPG_MSG_GAME_GOOD,"You have left the alliance.\\n")
                except:
                    pass
            return
        
        if self.leader == who:
            members = self.members[:]
            members.remove(self.leader)
            self.members = [self.leader]
            
            alliance = Alliance(members[0],self.remoteLeaderName)
            members.pop(0)
            for k in members:
                alliance.setupForPlayer(k)
            alliance.allianceInfo.refresh()
            self.disband()
            if not who.transfering:
                try:
                    who.sendGameText(RPG_MSG_GAME_GOOD,"You have left the alliance.\\n")
                except:
                    pass
            return
        
        nmembers = []
        for m in self.members:
            if m == who:
                if not m.loggingOut and not m.transfering:
                    try:
                        m.sendGameText(RPG_MSG_GAME_GOOD,"You have left the alliance.\\n")
                    except:
                        pass
                    continue
                else:
                    m.alliance = None
            else:
                nmembers.append(m)
        try:
            if not who.transfering:
                if self.world.daemonPerspective:
                    #make sure local info is accurate
                    a = Alliance.masterAllianceInfo[self.remoteLeaderName]
                    na = [(pname,cname) for pname,cname in a if pname != who.publicName]
                    Alliance.masterAllianceInfo[self.remoteLeaderName] = na
                    self.world.daemonPerspective.callRemote("clearAllianceInfo",who.publicName)
        except:
            traceback.print_exc()
        
        self.members = nmembers
        
        #the person who left is still in the observer list
        self.allianceInfo.refresh()
        #we do this here so we overwrite the refreshed data for the individual who left
        if not who.loggingOut and not who.transfering:
            who.alliance = Alliance(who)
        
        leaveName = who.charName
        sleaveName = leaveName.replace(' ','_')
        if not who.transfering:
            for m in self.members:
                try:
                    m.sendGameText(RPG_MSG_GAME_GOOD,"<a:gamelinkcharlink%s>%s</a> has left the alliance.\\n"%(sleaveName,leaveName))
                except:
                    pass
    
    
    def tick(self):
        if not self.leader: #make sure to none out leader!!!
            return
        
        if not len(self.members):
            print "WARNING: 0 member alliance"
            return
        
        if self.world.daemonPerspective:
            #filter members
            try:
                a = Alliance.masterAllianceInfo[self.remoteLeaderName]
            except KeyError:
                self.disband()
                return
            
            remove = []
            keep = []
            for m in self.members[:]:
                found = False
                for pname,cname in a:
                    if pname == m.publicName:
                        found = True
                        break
                if not found:
                    remove.append(m)
                else:
                    keep.append(m)
                
                if self.leader in remove:
                    if len(keep):
                        alliance = Alliance(keep[0],self.remoteLeaderName)
                        self.members.remove(keep[0])
                        keep.pop(0)
                        for k in keep:
                            self.members.remove(k)
                            alliance.setupForPlayer(k)
                        alliance.allianceInfo.refresh()
                
                for m in remove:
                    self.members.remove(m)
                    a = Alliance(m)
                    a.setupForPlayer(m)
                
                if not len(self.members):
                    return
        
        try:
            if True:#len(self.members) > 1:
                self.allianceInfo.refresh()
        except:
            traceback.print_exc()
        
        reactor.callLater(2,self.tick)
    
    
    def cancelInvite(self,who):
        if not who.invite:
            return
        
        ninvites = []
        for inv in self.invites:
            if inv.invited == who:
                who.invite = None
                continue
            ninvites.append(inv)
        self.invites = ninvites
    
    
    def cancelInvites(self):
        invites = copy(self.invites)
        for inv in invites:
            self.cancelInvite(inv.invited)
    
    
    def countMembers(self):
        num = len(self.members)
        if self.world.daemonPerspective:
            a = Alliance.masterAllianceInfo[self.remoteLeaderName]
            for pname,cname in a:
                found = False
                for m in self.members:
                    if m.publicName == pname:
                        found = True
                        break
                if not found:
                    num += 1
        return num
    
    
    def join(self,who):
        found = False
        if self.countMembers() >= 6:
            self.cancelInvite(who)
            return False
        if len(who.alliance.members) > 1:
            self.cancelInvite(who)
            return False
        for inv in self.invites:
            if inv.invited == who:
                found = True
                break
        if not found:
            who.invite = None
            return False
        
        if self.world.daemonPerspective:
            self.world.daemonPerspective.callRemote("joinAlliance",self.remoteLeaderName,who.publicName,who.party.members[0].name)
            a = Alliance.masterAllianceInfo[self.remoteLeaderName]
            a.append((who.publicName,who.party.members[0]))
        
        self.members.append(who)
        
        if who.alliance.leader == who:
            who.alliance.leader = None
        
        who.alliance = self
        who.mind.callRemote("setAllianceInfo",self.allianceInfo)
        #self.allianceInfo.refresh()
        
        self.cancelInvite(who)
        
        return True



class Invite:
    def __init__(self,invited,leader):
        self.invited = invited
        self.leader = leader
        self.alliance = leader.alliance #incase alliance disbands, we check on join
        self.time = time.time()
    
    
    def cancel(self):
        self.alliance.cancelInvite(self.invited)
        self.leader = self.alliance = self.time = None
    
    
    def decline(self):
        try:
            invitedName = self.invited.charName
            sinvitedName = invitedName.replace(' ','_')
            leaderName = self.leader.charName
            sleaderName = leaderName.replace(' ','_')
            self.leader.sendGameText(RPG_MSG_GAME_GOOD,"<a:gamelinkcharlink%s>%s</a> has declined your invitation.\\n"%(sinvitedName,invitedName))
            self.invited.sendGameText(RPG_MSG_GAME_GOOD,"You have declined <a:gamelinkcharlink%s>%s</a>'s invitation.\\n"%(sleaderName,leaderName))
            self.invited.mind.callRemote("setAllianceInvite",None)
        except:
            traceback.print_exc()
        self.cancel()
    
    
    def tick(self):
        pass
        
        Alliance.masterAllianceInfo[self.remoteLeaderName]

