# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from core import *

from random import randint
from math import floor
from defines import *

from mud.worlddocs.utils import GetTWikiName

import traceback


#0 = can't repair, 1 = don't need repair, 2= not enough $$$, tuple (tp,cp...)
def DoItemRepair(char,ritem):
    rskill = char.mob.skillLevels.get('Repair',0)
    if not rskill:
        traceback.print_stack()
        print "AssertionError: character %s doesn't have the repair skill?!"%char.name
        return
    
    cost = GetItemRepairCost(rskill,ritem.repair,ritem.repairMax,ritem.level,ritem.classes)
    
    if cost and cost != 1:
        if not char.player.checkMoney(cost):
            return 2,cost,0
        
        amount = rskill / 10
        if amount < 5:
            amount = 5
        
        base = 1
        if rskill >= 500:
            base = int(29.0 * float(rskill - 500) / 500.0) + 1
        
        amount = randint(base,amount)
        
        if amount > ritem.repairMax - ritem.repair:
            amount = ritem.repairMax - ritem.repair
        
        # If this item has a penalty, check if the item to be
        #  repaired currently is equipped and get the slot.
        equipSlot = None
        mob = None
        if ritem.penalty > 0.0 and ritem.character:
            mob = ritem.character.mob
            for slot,item in mob.worn.iteritems():
                if item == ritem:
                    equipSlot = slot
                    # If this item has a penalty and is equipped,
                    #  unequip it for the repairs.
                    mob.unequipItem(slot,True)
                    break
        
        # Now repair the item by the calculated amount.
        ritem.repair += amount
        ritem.setCharacter(ritem.character,True)
        
        # If this item was equipped, reequip it.
        if equipSlot != None:
            mob.equipItem(equipSlot,ritem,True,True)
        
        char.player.takeMoney(cost)
        
        char.checkSkillRaise("Repair",3,5,False)
        return cost,cost,amount
    
    return cost,cost,0


def GetItemRepairCost(rskill,repair,repairMax,level,classes):
    if not repairMax or repairMax == repair:
        return 1
    if not rskill:
        return 0
    
    for cl in classes:
        if cl[1] > level:
            level = cl[1]
    
    if level*5 > rskill+20:
        return 0
    
    #generate cost
    
    tp = long(level**5+500)
    
    s = float(level)/10.0
    if s >= 1:
        tp += int(tp*s)
    
    return tp



def CheckRepairItem(charname,rskill,rinfo,citem):
    from mud.client.gui.tomeGui import TomeGui
    receiveGameText = TomeGui.instance.receiveGameText
    
    if not citem:
        receiveGameText(RPG_MSG_GAME_DENIED,r'Please place an item in your cursor.\n')
        return
    
    ret = GetItemRepairCost(rskill,citem.REPAIR,citem.REPAIRMAX,citem.LEVEL,citem.CLASSES)
    
    if not ret:
        receiveGameText(RPG_MSG_GAME_DENIED,r'%s has insufficient skill to repair <a:Item%s>%s</a>.\n'%(charname,GetTWikiName(citem.PROTONAME),citem.NAME))
        return
    if ret == 1:
        receiveGameText(RPG_MSG_GAME_DENIED,r'<a:Item%s>%s</a> doesn\'t need repair.\n'%(GetTWikiName(citem.PROTONAME),citem.NAME))
        return
    
    ctext = GenMoneyText(ret)
    
    if rinfo.checkMoney(ret):
        receiveGameText(RPG_MSG_GAME_GAINED,"The repair of <a:Item%s>%s</a> requires %s.\\n"%(GetTWikiName(citem.PROTONAME),citem.NAME,ctext))
        return
    
    receiveGameText(RPG_MSG_GAME_DENIED,"The repair of <a:Item%s>%s</a> requires %s. %s doesn't have enough money.\\n"%(GetTWikiName(citem.PROTONAME),citem.NAME,ctext,charname))


def CheckRepairAll(charname,rskill,rinfo,charItems,output = True):
    from mud.client.gui.tomeGui import TomeGui
    receiveGameText = TomeGui.instance.receiveGameText
    cost = 0L
    
    ritems = []
    for rslot,ritem in charItems.iteritems():
        if RPG_SLOT_WORN_END > rslot >= RPG_SLOT_WORN_BEGIN:
            if not ritem.REPAIRMAX or ritem.REPAIRMAX == ritem.REPAIR:
                continue
            ritems.append(ritem)
    
    if not len(ritems):
        if output:
            receiveGameText(RPG_MSG_GAME_DENIED,"%s isn't using any items that need repair.\\n"%charname)
        return 0,0,cost
    
    iskill = 0
    if not rskill:
        iskill = len(ritems)
    else:
        for ritem in ritems:
            ret = GetItemRepairCost(rskill,ritem.REPAIR,ritem.REPAIRMAX,ritem.LEVEL,ritem.CLASSES)
            if not ret:
                iskill += 1
                continue
            cost += ret
    
    if iskill:
        if output:
            receiveGameText(RPG_MSG_GAME_DENIED,r'%s has insufficient skill to repair %i equipped items.\n'%(charname,iskill))
    if iskill == len(ritems):
        return len(ritems),iskill,cost
    
    ctext = ""
    if output:
        ctext = GenMoneyText(cost)
    
    if rinfo.checkMoney(cost):
        if output:
            receiveGameText(RPG_MSG_GAME_GAINED,"%s's repair of %i items will require %s.\\n"%(charname,len(ritems)-iskill,ctext))
        return len(ritems),iskill,cost
    
    if output:
        receiveGameText(RPG_MSG_GAME_DENIED,"%s's repair of %i items will require %s. %s doesn't have enough money for this repair.\\n"%(charname,len(ritems)-iskill,ctext,charname))
    
    return len(ritems),iskill,cost


def CheckRepairParty(charname,rskill,rinfo,charinfos):
    from mud.client.gui.tomeGui import TomeGui
    receiveGameText = TomeGui.instance.receiveGameText
    cost = 0L
    
    iskill = 0
    numrepairs = 0
    for c in charinfos.itervalues():
        numrep,ciskill,rcost = CheckRepairAll(charname,rskill,rinfo,c.ITEMS,False)
        cost += rcost
        iskill += ciskill
        numrepairs += numrep
    
    if not numrepairs:
        receiveGameText(RPG_MSG_GAME_DENIED,"%s's party isn't using any items that need repair.\\n"%charname)
        return
    if iskill:
        receiveGameText(RPG_MSG_GAME_DENIED,r'%s has insufficient skill to repair %i party items.\n'%(charname,iskill))
    if iskill == numrepairs:
        return
    
    ctext = GenMoneyText(cost)
    
    if rinfo.checkMoney(cost):
        receiveGameText(RPG_MSG_GAME_GAINED,"%s's repair of %i party items will require %s.\\n"%(charname,numrepairs-iskill,ctext))
        return
    
    receiveGameText(RPG_MSG_GAME_DENIED,"%s's repair of %i party items will require %s. %s doesn't have enough money.\\n"%(charname,numrepairs-iskill,ctext,charname))



def RepairItem(player,char):
    if char.dead:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is dead and cannot repair.\\n"%(char.name))
        return
    
    citem = player.cursorItem
    if not citem:
        player.sendGameText(RPG_MSG_GAME_DENIED,r'Please place an item in your cursor.\n')
        return
    
    code,cost,points = DoItemRepair(char,citem)
    
    if code == 2:
        #not enough money
        ctext = GenMoneyText(cost)
        player.sendGameText(RPG_MSG_GAME_DENIED,"The repair of <a:Item%s>%s</a> requires %s. %s doesn't have enough money\\n"%(GetTWikiName(citem.itemProto.name),citem.name,ctext,char.name))
        return
    if code == 0:
        #not enough skill
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s lacks the skill to repair <a:Item%s>%s</a>.\\n"%(char.name,GetTWikiName(citem.itemProto.name),citem.name))
        return
    if code == 1:
        player.sendGameText(RPG_MSG_GAME_DENIED,"<a:Item%s>%s</a> requires no repair.\\n"%(GetTWikiName(citem.itemProto.name),citem.name))
        return
    
    ctext = GenMoneyText(cost)
    if citem.repair == citem.repairMax:
        player.sendGameText(RPG_MSG_GAME_BLUE,r'%s completely repairs <a:Item%s>%s</a> for %i points! (%i/%i)\n%s in materials consumed.\n'%(char.name,GetTWikiName(citem.itemProto.name),citem.name,points,citem.repair,citem.repairMax,ctext))
    else:
        player.sendGameText(RPG_MSG_GAME_GAINED,r'%s repairs <a:Item%s>%s</a> for %i points! (%i/%i)\n%s in materials consumed.\n'%(char.name,GetTWikiName(citem.itemProto.name),citem.name,points,citem.repair,citem.repairMax,ctext))        
    
    player.mind.callRemote("playSound","sfx/Hit_MetalPoleImpact2.ogg")


def RepairAll(player,char):
    if char.dead:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is dead and cannot repair.\\n"%(char.name))
        return
    
    ritems = []
    for ritem in char.items:
        if RPG_SLOT_WORN_END > ritem.slot >= RPG_SLOT_WORN_BEGIN:
            if not ritem.repairMax or ritem.repairMax == ritem.repair:
                continue
            ritems.append(ritem)
    
    if not len(ritems):
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s isn't using any items that require repair.\\n"%(char.name))
        return
    
    #start repairs
    points = 0
    cost = 0L
    iskill = 0
    numrepaired = 0
    
    nomoney = False
    allgood = True
    for ritem in ritems:
        rcode,rcost,rpoints = DoItemRepair(char,ritem)
        if rcode == 2:
            #out of money
            nomoney=True
            break
        if rcode == 0:
            #not enough skill
            allgood = False
            iskill+=1
            continue
        if ritem.repairMax != ritem.repair:
            allgood = False
        numrepaired+=1
        points+=rpoints
        cost += rcost
    
    if nomoney and not numrepaired:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src doesn't have enough money to repair any of $srchis equipped items.\\n",char.mob)
        return
    if not numrepaired:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s lacks the skill to repair any equipped items.\\n"%char.name)
        return
    
    ctext = GenMoneyText(cost)
    player.sendGameText(RPG_MSG_GAME_GAINED,"%s repaired %i items for %i points.  The repair consumed %s in materials.\\n"%(char.name,numrepaired,points,ctext))
    player.mind.callRemote("playSound","sfx/Hit_MetalPoleImpact2.ogg")
    
    if not iskill and not nomoney and allgood:
        player.sendGameText(RPG_MSG_GAME_BLUE,"%s's items are fully repaired.\\n"%(char.name))
        return
    
    if nomoney:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough money to complete this repair.\\n"%char.name)
    if iskill:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s lacked the skill to repair %i items.\\n"%(char.name,iskill))


def RepairParty(player,char):
    if char.dead:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s is dead and cannot repair.\\n"%(char.name))
        return
    
    ritems = []
    for c in player.party.members:
        for ritem in c.items:
            if RPG_SLOT_WORN_END > ritem.slot >= RPG_SLOT_WORN_BEGIN:
                if not ritem.repairMax or ritem.repairMax == ritem.repair:
                    continue
                ritems.append(ritem)
    
    if not len(ritems):
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s's party has no items that require repair.\\n"%char.name)
        return
    
    #start repairs
    points = 0
    cost = 0L
    iskill = 0
    numrepaired = 0
    
    nomoney = False
    allgood = True
    for ritem in ritems:
        rcode,rcost,rpoints = DoItemRepair(char,ritem)
        if rcode == 2:
            #out of money
            nomoney=True
            break
        if rcode == 0:
            #not enough skill
            iskill+=1
            continue
        if ritem.repairMax != ritem.repair:
            allgood = False
        numrepaired+=1
        points+=rpoints
        cost += rcost
    
    if nomoney and not numrepaired:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src doesn't have enough money to repair any of $srchis party's equipment.\\n",char.mob)
        return
    if not numrepaired:
        player.sendGameText(RPG_MSG_GAME_DENIED,"$src lacks the skill to repair any of $srchis party's equipped items.\\n",char.mob)
        return
    
    ctext = GenMoneyText(cost)
    player.sendGameText(RPG_MSG_GAME_GAINED,"%s repaired %i items for %i points.  The repair consumed %s in materials.\\n"%(char.name,numrepaired,points,ctext))
    player.mind.callRemote("playSound","sfx/Hit_MetalPoleImpact2.ogg")
    
    if not iskill and not nomoney and allgood:
        player.sendGameText(RPG_MSG_GAME_BLUE,"%s's party's items are fully repaired.\\n"%char.name)
        return
    
    if nomoney:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough money to complete this repair.\\n"%char.name)
    if iskill:
        player.sendGameText(RPG_MSG_GAME_DENIED,"%s lacked the skill to repair %i items.\\n"%(char.name,iskill))



