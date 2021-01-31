# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

"""
$srcname
$tgtname
$srcher
$tgther
$srcherself
$tgtherself
"""

import math
from defines import *

#range of zero is global to zone
def ZoneMessage(zone,msg):
    for p in zone.players:
        p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,"\\n<Scribe of Mirth> %s\\n"%msg)
        

def ZoneSound(zone,sound):
    for p in zone.players:
        p.mind.callRemote("playSound",sound)
        

"""
srche
srchim
srchis
srcself
src
srcfull
tgthe
tgthim
tgthis
tgtself
tgt
tgtfull
"""
def MessagePersonalize(msg,mob,tgt=None):
    if not msg:
        return msg
    
    if mob:
        char = mob.character
        if mob.sex == 'Female':
            srche = "she"
            srchim = "her"
            srchis = "her"
            srcself = "herself"
        elif mob.sex == 'Male':
            srche = "he"
            srchim = "him"
            srchis = "his"
            srcself = "himself"
        else:
            srche = "it"
            srchim = "it"
            srchis = "its"
            srcself = "itself"
        if mob.player:
            srcfull = "%s %s"%(char.name,char.lastName)
        else:
            srcfull = mob.name
        msg = msg.replace("$srche", srche)
        msg = msg.replace("$srchim", srchim)
        msg = msg.replace("$srchis", srchis)
        msg = msg.replace("$srcself", srcself)
        msg = msg.replace("$srcfull", srcfull)
        if char:
            msg = msg.replace("$src", char.name)
        else:
            msg = msg.replace("$src", mob.name)
            
        
        if not tgt:
            tgt = mob.target
    
    if tgt:
        if tgt.sex == 'Female':
            tgthe = "she"
            tgthim = "her"
            tgthis = "her"
            tgtself = "herself"
        elif tgt.sex == 'Male':
            tgthe = "he"
            tgthim = "him"
            tgthis = "his"
            tgtself = "himself"
        else:
            tgthe = "it"
            tgthim = "it"
            tgthis = "its"
            tgtself = "itself"
        if tgt.player:
            char = tgt.character
            tgtname = char.name
            tgtfull = "%s %s"%(char.name,char.lastName)
        else:
            tgtname = tgtfull = tgt.name
        msg = msg.replace("$tgthe", tgthe)
        msg = msg.replace("$tgthim", tgthim)
        msg = msg.replace("$tgthis", tgthis)
        msg = msg.replace("$tgtself", tgtself)
        msg = msg.replace("$tgtfull", tgtfull)
        msg = msg.replace("$tgt", tgtname)
    
    return msg


def GameMessage(msgType,zone,src,tgt,msg,position,range=0):
        
    if src:
        if src.sex == 'Female':
            srcher = "her"
            srcherself = "herself"
        elif src.sex == 'Male':
            srcher = "his"
            srcherself = "himself"
        else:
            srcher = "its"
            srcherself = "itself"
            
        #must be in order longest to shortest for replace to work!
        msg = msg.replace("$srcherself",srcherself)
        msg = msg.replace("$srcher",srcher)
        msg = msg.replace("$src",src.name)
    
    if tgt:
        if tgt.sex == 'Female':
            tgther = "her"
            tgtherself = "herself"
        elif tgt.sex == 'Male':
            tgther = "his"
            tgtherself = "himself"
        else:
            tgther = "its"
            tgtherself = "itself"
        
    
        #must be in order longest to shortest for replace to work!
        msg = msg.replace("$tgtherself",tgtherself)
        msg = msg.replace("$tgther",tgther)
        msg = msg.replace("$tgt",tgt.name)
    
    if msgType == RPG_MSG_GAME_COMBAT:
        tp = None
        sp = None
        if tgt:
            if tgt.master:
                tp = tgt.master.player
            else:
                tp = tgt.player
        if src:
            if src.master:
                sp = src.master.player
            else:
                sp = src.player
    
    
    for p in zone.players:
        if not p.party:
            continue
        
        if msgType == RPG_MSG_GAME_COMBAT:
            if tp != p and sp != p:
                if not p.channelCombat:
                    continue
        
        # leave this, src could still be listening to tgt's messages and vice-versa
        skipcheck = False
        if src and src.player == p:
            skipcheck = True
        if tgt and tgt.player == p:
            skipcheck = True
            
        if not range and not skipcheck:
            continue

        if range and not skipcheck:
            mob = p.party.members[0].mob
            if not mob or not mob.simObject:
                continue
            p1 = mob.simObject.position
            x = p1[0]-position[0]
            y = p1[1]-position[1]
            z = p1[2]-position[2]
            
            dist = math.sqrt(x*x+y*y+z*z)
            dist = math.floor(dist)
            if dist < 1:
                dist = 1
            if dist > range:
                continue
        
        if msgType == RPG_MSG_GAME_COMBAT and src and src.player == p:
            src.player.sendGameText(RPG_MSG_GAME_COMBAT_HIT,msg)
        elif msgType == RPG_MSG_GAME_COMBAT and tgt and tgt.player == p:
            tgt.player.sendGameText(RPG_MSG_GAME_COMBAT_GOTHIT,msg)
        #we need better string handling
        elif msgType == RPG_MSG_SPEECH_SAY:
            p.sendSpeechText(msgType,msg)
        else:
            p.sendGameText(msgType,msg)
            
        
    

#void rpg_zone_msg(rpgzone_t* zone, int msgtype, rpgmob_t* src, rpgmob_t* tgt, char* msg, char* src_action, char* others_action, float range)
