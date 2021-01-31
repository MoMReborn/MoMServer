# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.persistent import Persistent
from mud.world.core import *
from mud.world.defines import *
from mud.world.item import getTomeAtLevelForScroll,ItemProto
from mud.world.itemvariants import GenVariantItem
from mud.world.shared.sounddefs import *

from datetime import date
from random import randint
from sqlobject import *
from time import strftime,strptime,time as sysTime
import traceback



#--- Updated 9/19/07 by BellyFish
#---    Added 'ZONE_SEASONALITEMS' array.
#---    Extensive modifications and additions to def generateCorpseLoot()
#---    Added imports from 'time' and 'datetime' modules
#---    PURPOSE:
#---    Additions to enable spawning items based on
#---    the Day of the Real Life Year and in a specific zone.

ZONE_POTIONS = {
"anidaenforest":"Potion of Anidaen Gate",
"arctic":"Potion of Frostbite Gate",
"jakrethjungle":"Potion of Jakreth Gate",
"talrimhills":"Potion of Talrim Gate",
"desertmohrum":"Potion of Mohrum Gate",
"trinst":"Potion of Trinst Gate",
"kauldur":"Potion of Kauldur Gate",
"swamp":"Potion of Swamp Gate"
}

# modification begin
# list of which enchanting foci will drop in which zone
ZONE_ENCHANTINGITEMS = {
"desertmohrum":["Sandstone of Clarity","Sandstone of Strength","Sandstone of Health","Sandstone of Ether","Sandstone of Endurance","Sandstone of the Sphinx"],
"mountain":["Coal of Insight","Coal of Fiery Protection","Coal of Health","Coal of Ether","Coal of Endurance","Coal of the Dwarven King"],
"arctic":["Icy Shard of Instinct","Icy Shard of the Arcane","Icy Shard of Cold Protection","Icy Shard of Health","Icy Shard of Ether","Icy Shard of Endurance","Icy Shard of Volsh"],
"anidaenforest":["Bark of Magic Protection","Bark of Health","Bark of Ether","Bark of Endurance","Bark of Speed"],
"talrimhills":["Limestone of Constitution","Limestone of Electrical Resistance","Limestone of Health","Limestone of Ether","Limestone of Endurance","Limestone of Lightning"],
"hazerothkeep":["Quartz of Nimbleness","Quartz of Physical Protection","Quartz of Health","Quartz of Ether","Quartz of Endurance","Quartz of the Warling Cleric"],
"wasteland":["Blighted Shard of Quickness","Blighted Shard of Defense","Blighted Shard of Health","Blighted Shard of Ether","Blighted Shard of Endurance","Blighted Shard of Aelieas"],
"jakrethjungle":["Vine of Poison Resist","Vine of Disease Resist","Vine of Health","Vine of Ether","Vine of Endurance","Vine of the Cavebear"],
"swamp":["Muck-Covered Stone of Acidity","Muck-Covered Stone of Health","Muck-Covered Stone of Ether","Muck-Covered Stone of Endurance","Muck-Covered Stone of the Ghoul Slayer"]
}
# list of quality prefixes, 'raw' is not yet enchanted item (Coal, Sandstone, ...), raw can't be dropped, only gained from disenchanting and the prefix won't be used anyway.
ENCHANT_QualityPrefix = ["Raw ","Fractured ","Rough ","Jagged ","Smooth ","Clear ","Pristine ","Exquisite "]
# raw can't be dropped, so 0; chances are [0%,50%,25%,13%,6%,3%,2%,1%]
ENCHANT_QualityDropDistribution = [0,50,75,88,94,97,99,100]
# modification end

#Potion of and Elixir of
STAT_POTIONS = ("Strength","Mind","Reflex","Agility","Body","Wisdom","Mysticism","Dexterity")

WILDTOMES = ("Paladin","Cleric","Necromancer","Tempest","Wizard","Shaman","Revealer","Druid","Ranger","Bard","Doom Knight")

ZONE_SEASONALITEMS = {
"arctic":[],
"anidaenforest":["Spring Leaf"],
"desertmohrum":["Parched Bone"],
"hazerothkeep":[],
"jakrethjungle":[],
"mountain":["Wheat Panicle"],
"swamp":[],
"talrimhills":[],
"trinst":["Wheat Panicle"],
"wasteland":["Parched Bone"],
"kauldur":["Parched Bone"]
}



class LootItem(Persistent):
    lootProto = ForeignKey('LootProto')
    itemProto = ForeignKey('ItemProto')
    freq = IntCol(default=RPG_FREQ_ALWAYS)
    flags = IntCol(default=0)



class LootProto(Persistent):
    spawns = MultipleJoin('Spawn')
    lootItems = MultipleJoin('LootItem')
    
    tin = IntCol(default = 0L)
    
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        self.itemDetails = dict((item.itemProto.name,item.flags) for item in self.lootItems)



class Loot:
    def initRandomLoot():
        #to do, better
        randomProtos = Loot.randomItemProtos = []
        spellScrolls = Loot.spellScrolls = {}
        protos = {}
        
        con = ItemProto._connection.getConnection()
        
        for id,spell_proto_id in con.execute("SELECT id,spell_proto_id FROM item_proto WHERE spell_proto_id OR (rating = 1 AND NOT flags & ?);",(RPG_ITEM_SOULBOUND,)):
            ip = protos.setdefault(id,ItemProto.get(id))
            
            if spell_proto_id:
                for classname,level in con.execute("SELECT classname,level FROM spell_class WHERE spell_proto_id = ?;",(spell_proto_id,)):
                    spellScrolls.setdefault(classname,{}).setdefault(level,[]).append(ip)
            else:
                randomProtos.append(ip)
        
        # 'unique' variant loot
        uloot = {}
        for itemid,freq in con.execute("SELECT DISTINCT item_proto_id,freq FROM loot_item WHERE freq >= ? AND loot_proto_id IN (SELECT DISTINCT loot_proto_id FROM spawn WHERE NOT flags & ?);",(RPG_FREQ_COMMON,RPG_SPAWN_UNIQUE)):
            if con.execute("SELECT id FROM item_slot WHERE item_proto_id = ? LIMIT 1;",(itemid,)).fetchone():
                # equippable
                if freq > uloot.get(itemid,0):
                    uloot[itemid] = freq
        
        # level -> list of item protos
        uniqueProtos = Loot.uniqueItemProtos = {}
        for itemid,freq in uloot.iteritems():
            ip = protos.setdefault(itemid,ItemProto.get(itemid))
            
            level = ip.level
            for cl in ip.classes:
                if cl.level > level:
                    level = cl.level
            if level == 1:
                continue
            
            uniqueProtos.setdefault(level,[]).append((freq,ip))
    
    initRandomLoot = staticmethod(initRandomLoot)
    
    
    def __init__(self,mob,lootProto):
        self.mob = mob
        self.lootProto = lootProto
        
        self.items = []
        
        self.tin = 0L
        
        self.fleshDone = False
        self.corpseLootGenerated = False
        self.pickPocketTimer = 0  # timer won't allow immediate repickpocketing
    
    
    def giveMoney(self,player):
        gotsome = False
        spawn = self.mob.spawn
        if spawn.flags & RPG_SPAWN_RESOURCE:
            gotsome = False
            
        elif self.tin:
            gotsome=True
            player.alliance.giveMoney(player,self.tin)
        
        self.tin = 0L
        
        return gotsome
    
    
    def generateCorpseLoot(self):
        
        loot = self.items
        
        if self.corpseLootGenerated:
            return (self.tin or len(loot))
        
        spawn = self.mob.spawn
        proto = self.lootProto
        self.corpseLootGenerated = True
        
        if proto:
            #$$$, to do, curve these
            if proto.tin:
                self.tin = randint(0,proto.tin)
     #Start code modified and expanded by BellyFish           
            for lootitem in proto.lootItems:
                if not len(lootitem.itemProto.slots):
                    freq = lootitem.freq
                    r = 0
                    if freq > 1:
                        r = randint(0,freq-1)
                    if not r:
                        iproto = lootitem.itemProto
                        # check if the item has a start and end day
                        if (iproto.startDayRL != "" or iproto.endDayRL != ""):
                            startDayRL = date(*strptime(iproto.startDayRL + "-" + strftime('%Y'), "%m-%d-%Y")[0:3])
                            endDayRL = date(*strptime(iproto.endDayRL + "-" + strftime('%Y'), "%m-%d-%Y")[0:3])
                            todayRL = date.today()
                            #check if spawn period crosses a yearly boundary
                            if endDayRL < startDayRL:
                                #crosses yearly boundary, so check if the day is outside the allowed date range
                                if endDayRL < todayRL < startDayRL:
                                    continue #day is outside the allowed date range, so skip it
                            #no boundaries are crossed, so check if the day is ouside the allowed date range
                            elif not (startDayRL <= todayRL <= endDayRL):
                                continue #day is outside the allowed date range, so skip it
                      
                        #If we get here, the item can be added to the loot table.
      #End code modified and expanded by BellyFish  
                        #Create an instance of the item
                        item = iproto.createInstance()
                        
                        #possibly generate a variant
                        GenVariantItem(item,self.mob.plevel)
                        
                        item.slot = -1
                        loot.append(item)
                    
                    if len(loot) == 16:
                        break
        
        # Check if this particular spawn drops random loot or if the loot
        #  table already is maxed out.
        if len(loot) >= 16 or spawn.flags & RPG_SPAWN_NORANDOMLOOT:
            # No random loot or loot table full,
            #  so finish the corpse loot generation.
            return self.finishCorpseLootGeneration()
 
    #Start code added by BellyFish
         # Zone dependent Seasonal drops
        if ZONE_SEASONALITEMS.has_key(self.mob.zone.zone.name):
            # check if mob can have a Seasonal drop, a 1 in 4 chance
            # as the ZONE_SEASONALITEMS list increases for the same time period the chance for a
            # specific drop decreases.
            if not randint(0,3): 
                tempSeasonalItemlist = []
                zoneSeasonalItemList = ZONE_SEASONALITEMS[self.mob.zone.zone.name]
                if len(zoneSeasonalItemList) > 0:
                    #sort through the zoneSeasonalItemList list
                    for eachSeasonalItem in zoneSeasonalItemList:
                        #get the items prototype so we can reference the items info
                        try:
                        # If an item is not found, an SQLObjectNotFound exception is raised.
                             testItem = ItemProto.byName(eachSeasonalItem)
                        # So continue to the next item.
                        except SQLObjectNotFound:
                           continue                            
                        # check if the item has a start and end day
                        if (testItem.startDayRL != "" or testItem.endDayRL != ""):
                            startDayRL = date(*strptime(testItem.startDayRL + "-" + strftime('%Y'), "%m-%d-%Y")[0:3])
                            endDayRL = date(*strptime(testItem.endDayRL + "-" + strftime('%Y'), "%m-%d-%Y")[0:3])
                            todayRL = date.today()
                            #check if spawn period crosses a yearly boundary
                            if endDayRL < startDayRL:
                                #crosses yearly boundary, so check if the day is outside the allowed date range
                                if endDay < todayRL < startDayRL:
                                    continue #day is outside the allowed date range, so skip it
                            #no boundaries are crossed, so check if the day is ouside the allowed date range        
                            elif not (startDayRL <= todayRL <= endDayRL):
                                continue #day is outside the allowed date range, so skip it
                        #add the item to a tempSeasonalItemlist and repeat the for loop
                        tempSeasonalItemlist.append(testItem)

                    #Does the tempSeasonalItemlist contain data?
                    if len(tempSeasonalItemlist) > 0:
                        #pick a random item from the list
                        seasonalItem = tempSeasonalItemlist[randint(0,len(tempSeasonalItemlist) - 1)]
                        #create an instance of the item
                        itemInstance = seasonalItem.createInstance()
                        #make sure the item does not fit in a slot, only in inventory
                        itemInstance.slot = -1
                        #add the item to the loot list
                        loot.append(itemInstance)                    
    #End code added by BellyFish
        
        # If there is still room in the loot table, check
        #  if this mob carries additional random goodies.
        if len(loot) < 16:
            # Higher level mob possibly carries more random stuff.
            num = randint(0,int(spawn.plevel / 10) + 1)
            for x in xrange(0,num):
                # For each single item 25% chance to have or not to have.
                if randint(0,3):
                    continue
                
                # Get one of the random item protos.
                iproto = Loot.randomItemProtos[randint(0,len(Loot.randomItemProtos) - 1)]
                item = iproto.createInstance()
                # Eventually create a variant of this item.
                GenVariantItem(item,self.mob.plevel)
                
                # Finally add random item to loot table.
                item.slot = -1
                loot.append(item)
                if len(loot) == 16:
                    break
        
        # If there's still room in the loot table, check
        #  if this mob carries a zone potion.
        if len(loot) < 16:
            # The higher level the mob, the higher the chance
            #  to carry a zone potion.
            chance = 35 - spawn.plevel / 3
            if not randint(0,chance):
                # Success, try to get an appropriate zone potion.
                try:
                    zpotion = ZONE_POTIONS[self.mob.zone.zone.name]
                    zpotion = ItemProto.byName(zpotion)
                    item = zpotion.createInstance()
                    item.slot = -1
                    loot.append(item)
                except:
                    pass
        
        # If there's still room in the loot table, check
        #  if this mob carries some Moon Powder.
        if len(loot) < 16:
            # The higher level the mob, the higher the chance
            #  to carry Moon Powder.
            chance = 35 - spawn.plevel / 4
            if not randint(0,chance):
                # Success, try to add one Moon Powder to
                #  this mobs loot table.
                try:
                    p = ItemProto.byName("Moon Powder")
                    item = p.createInstance()
                    item.slot = -1
                    loot.append(item)
                except:
                    traceback.print_exc()
        
        # If there's still room in the loot table, check
        #  whether this mob carries a stat potion.
        num = 1
        # Unique mobs may carry more than one potion.
        if self.mob.uniqueVariant:
            num = 2
        for x in xrange(0,num):
            if len(loot) < 16:
                # The higher level the mob, the higher the chance
                #  to carry a stat potion.
                chance = (110 - spawn.plevel) / 2
                if not randint(0,chance):
                    try:
                        index = randint(0,len(STAT_POTIONS) - 1)
                        stat = STAT_POTIONS[index]
                        potion = "Potion of %s"%stat
                        # Mobs above level 25 may even carry an Elixir
                        #  instead of a normal stat potion.
                        if spawn.plevel >= 25:
                            chance = (110 - spawn.plevel) / 3
                            if not randint(0,chance):
                                potion = "Elixir of %s"%stat
                        
                        potion = ItemProto.byName(potion)
                        item = potion.createInstance()
                        item.slot = -1
                        loot.append(item)
                    except:
                        traceback.print_exc()
        
        num = 2 if self.mob.uniqueVariant else 1
        for x in xrange(0,num):                    
            if len(loot) < 16:
                if not randint(0,4): #got one
                    scrolls = set()
                    if not randint(0,2):
                        wclass = WILDTOMES[randint(0,len(WILDTOMES)-1)]
                        wlevel = spawn.plevel
                        classes = ((spawn.pclassInternal,spawn.plevel),(spawn.sclassInternal,spawn.slevel),(spawn.tclassInternal,spawn.tlevel),(wclass,wlevel))
                    else:
                        classes = ((spawn.pclassInternal,spawn.plevel),(spawn.sclassInternal,spawn.slevel),(spawn.tclassInternal,spawn.tlevel))
                        
                    for cl,level in classes:
                        spellScrolls = Loot.spellScrolls.get(cl)
                        if spellScrolls:
                            for x in xrange(max(1,level - 5),level + 11):
                                try:
                                    scrolls.update(spellScrolls[x])
                                except KeyError:
                                    continue
                    
                    scroll = None
                    if len(scrolls) == 1:
                        scroll = scrolls.pop()
                    elif len(scrolls) > 1:
                        scroll = list(scrolls)[randint(0,len(scrolls)-1)]
                    
                    if scroll:
                        v = (0,30,55,75,85,90,94,97,101)
                        x = randint(0,100)
                        for z in xrange(0,9):
                            if x < v[z]:
                                break
                        x = z + 1
                        
                        if self.mob.uniqueVariant:
                            x += 5
                            if x > 10:
                                x = 10
                        
                        item = getTomeAtLevelForScroll(scroll,x)
                        item.slot = -1
                        item.itemInfo.reset()
                        
                        loot.append(item)
        
        #books of learning
        num = 2 if self.mob.uniqueVariant else 1
        for x in xrange(0,num):
            if len(loot) < 16:
                chance = (110 - spawn.plevel) / 2
                if not randint(0,chance):
                    try:
                        iname = "Scroll of Learning"
                        if spawn.plevel >= 60:
                            chance = (110 - spawn.plevel) / 3
                            if not randint(0,chance):
                                iname = "Book of Learning"
                        
                        book = ItemProto.byName(iname)
                        item = book.createInstance()
                        item.slot = -1
                        loot.append(item)
                    
                    except:
                        traceback.print_exc()
        
        # Unique variant mobs may carry even more additional
        #  random items.
        if len(loot) < 16 and self.mob.uniqueVariant:
            x = max(1,spawn.plevel - 20)
            
            # Build a list of possible random items
            #  to add to the loot table.
            items = {}
            uniqueProtos = Loot.uniqueItemProtos
            for level in xrange(x,spawn.plevel + 1):
                try:
                    for freq,ip in uniqueProtos[level]:
                        items.setdefault(freq,[]).append(ip)
                except KeyError:
                    continue
            
            # If there are random items available...
            if len(items):
                # Try to add maximally 3.
                for x in xrange(3):
                    ip = None
                    # 33% Chance to get an additional item per iteration.
                    if not randint(0,2):
                        # Start iteration over possible items at lowest
                        #  drop frequency.
                        for freq in sorted(items.iterkeys(),reverse=True):
                            if not randint(0,freq):
                                if len(items[freq]) == 1:
                                    ip = items[freq][0]
                                    break
                                else:
                                    ip = items[freq][randint(0,len(items[freq])-1)]
                                    break
                        # If we got an item, add it to the loot table.
                        if ip:
                            item = ip.createInstance()
                            item.slot = -1
                            loot.append(item)
        
        # zone dependend enchanting-item drop, last item per list is more rare than the rest
        if len(loot) < 16:
            # check if we got one; ok, this is actually 1 in RPG_FREQ_RARE+1 but that's good enough
            if not randint(0,RPG_FREQ_RARE):
                try:
                    zoneEnchItemList = ZONE_ENCHANTINGITEMS[self.mob.zone.zone.name]
                    enchQuality = 0
                    
                    # check if this is even an uber enchantment type (chance total: 1 in 561)
                    # this seems like an extremely low drop chance, but considering it gets applied to every single loot collection...
                    # because the special enchantments are this rare and because of their power, they're always exquisite
                    if not randint(0,RPG_FREQ_IMPOSSIBLE):
                        # Get last item of list (uber enchantment).
                        enchName = zoneEnchItemList[-1]
                        enchQuality = len(ENCHANT_QualityPrefix) - 1
                    else:
                        # Otherwise, get a random normal type.
                        enchName = zoneEnchItemList[randint(0,len(zoneEnchItemList)-2)]
                        # Random quality for item (lower quality items can be combined
                        #  for higher quality), but don't allow index 0 (raw drop).
                        qualityCursor = randint(1,100)
                        for qualityTester in xrange(len(ENCHANT_QualityPrefix)):
                            if qualityCursor <= ENCHANT_QualityDropDistribution[qualityTester]:
                                break
                            enchQuality += 1
                    
                    enchItem = ItemProto.byName(enchName)
                    item = enchItem.createInstance()
                    # Hack, spellEnhanceLevel is used for quality of this item type
                    #  (less attribs), values < 10 are used to identify tomes,
                    #  so use values 10 - 17
                    item.spellEnhanceLevel = enchQuality + 10
                    item.name = ENCHANT_QualityPrefix[enchQuality] + item.name
                    item.slot = -1
                    loot.append(item)
                    
                except:
                    pass
                
        #Essence of the Void
        if len(loot) < 16:
            if not randint(0,RPG_FREQ_IMPOSSIBLE * 3):
                try:
                    p = ItemProto.byName("Essence of the Void")
                    item = p.createInstance()
                    item.slot = -1
                    loot.append(item)
                    
                except:
                    traceback.print_exc()
        
        # Finish corpse loot generation.
        return self.finishCorpseLootGeneration()
    
    
    def finishCorpseLootGeneration(self):
        # Now assign to every item in the loot table a random
        #  repair value if the item makes use of one.
        for item in self.items:
            if not (item.flags & RPG_ITEM_INDESTRUCTIBLE) and item.repairMax > 0:
                if item.repairMax == 1:
                    item.repair = 1
                else:
                    item.repair = randint(1,item.repairMax)
        
        # Return True if this mob got something to loot,
        #  otherwise False.
        return (self.tin or len(self.items))
    
    
    def generateLoot(self):
        #ONLY SPAWN LOOT FROM LOOT TABLE THAT CAN BE EQUIPPED HERE!!!!!
        spawn = self.mob.spawn
        
        proto = self.lootProto
        self.items = loot = []
        if proto:
            for lootitem in proto.lootItems:
                if len(lootitem.itemProto.slots):
                    freq = lootitem.freq
                    r = 0
                    if freq > 1:
                        r = randint(0,freq-1)
                    if not r:
                        #got it
                        iproto = lootitem.itemProto
                        
                        item = iproto.createInstance()
                        
                        #possibly generate a variant
                        GenVariantItem(item,self.mob.plevel)
                        
                        item.slot = -1
                        loot.append(item)
                    
                        if len(loot) == 16:
                            break





def GenerateLoot(mob):
    
    if mob.player or (mob.master and not mob.spawn.lootProto):
        return
    
    mob.loot = Loot(mob,mob.spawn.lootProto)
    mob.loot.generateLoot()
    #mob.loot.mob = None
    #mob.loot = None


