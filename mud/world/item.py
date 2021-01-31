# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.persistent import Persistent
from mud.world.defines import *
from mud.world.projectile import Projectile
from mud.world.spell import SpawnSpell,SpellProto
from mud.world.shared.playdata import ItemInfo
from mud.worlddocs.utils import GetTWikiName

from copy import copy
from math import ceil,floor
from random import randint
from sqlobject import *
import traceback



#--- Updated 9/19/07 by BellyFish
#---    Added startDayRL and endDayRL initializations in 'class ItemProto'
#---    PURPOSE:
#---    Additions to enable spawning items based on
#---    the Day of the Year.



# ------------------------------------------------------------------------------


class ItemClassifier(Persistent):
    # Identifier of this container content type.
    name = StringCol(alternateID=True)
    # Items belonging to this type.
    itemProtosInternal = RelatedJoin('ItemProto')
    # Containers storing this type.
    itemContainerProtosInternal = RelatedJoin('ItemContainerProto')



class ItemContainerContent(Persistent):
    # Link to the container item.
    item = ForeignKey('Item')
    # Link to the content item.
    content = ForeignKey('Item')



class ItemContainerProto(Persistent):
    # Number of items that fit into this container.
    containerSize = IntCol(default=1)
    # Item types allowed to go into this container.
    itemClassifiersInternal = RelatedJoin('ItemClassifier')
    # Item flags required for an item to go into this container.
    contentFlagsRequired = IntCol(default=0)
    
    
    def _init(self, *args, **kw):
        Persistent._init(self, *args, **kw)



class ItemContainer:
    def __init__(self, item):
        # Store this containers associated item.
        self.item = item
        
        containerProto = item.itemProto.itemContainerProto
        
        # Cache container info.
        if containerProto:
            self.containerSize = containerProto.containerSize
            self.contentTypes = [it.name for it in containerProto.itemClassifiersInternal]
            self.contentFlagsRequired = containerProto.contentFlagsRequired
        else:
            self.containerSize = 1
            self.contentTypes = []
            self.contentFlagsRequired = 0
        
        # Build the list of contained items.
        if item.item:
            self.content = [ItemInstance(cc.content) for cc in item.item.containerContent]
        else:
            self.content = []
        
        # Flag to check if contents have changed. Won't check on initialization,
        #  so set to false.
        self.dirty = False
    
    
    # Check if a specific item can be stacked on items present in this container.
    # Thanks to our autostacking there will be at maximum a single item with incomplete
    #  charges or stack count for any given item kind.
    # Return a tuple with (can fully stack,stacking target).
    def checkStack(self, item):
        # If there's no item, return false.
        if not item:
            return (False,None)
        
        # Get the maximum items on a stack of this item kind.
        stackMax = item.itemProto.stackMax
        
        # If stackMax is smaller or equal to 1, stacking will be impossible.
        if stackMax <= 1:
            return (False,None)
        
        # Get the item's max use value.
        useMax = item.itemProto.useMax
        
        # For improved performance, items with charges will be handled in a
        #  separate loop than items without charges.
        # If the item holds more than one charge, then specifically handle
        #  stacking for counts and charges.
        if useMax > 1:
            
            # Before looping through all items, check the item to be inserted
            #  if it doesn't completely fill a stack already.
            if item.stackCount >= stackMax and item.useCharges >= useMax:
                return (False,None)
            
            # Calculate the amount of charges that are on the item attempting to
            #  be stacked.
            neededCharges = useMax * (item.stackCount - 1) + item.useCharges
            
            # Iterate over all items contained in this container.
            for citem in self.content:
                
                # If the item names don't match, continue to the next item.
                if citem.name != item.name:
                    continue
                
                # The names match, so it may be possible to stack the item.
                # Get the total number of free charges on the target item.
                freeCharges = useMax * (stackMax - item.stackCount + 1) - item.useCharges
                
                # If there are no more free charges, can't stack.
                # Continue to the next item.
                if freeCharges <= 0:
                    continue
                
                # If we get here, stacking is possible.
                
                # Thanks to our autostacking, there will never be more than a single
                #  incomplete item stack.
                # If the free charges are less than the needed charges, the item won't
                #  stack fully.
                if freeCharges < neededCharges:
                    return (False,citem)
                # Otherwise the item will fully stack.
                else:
                    return (True,citem)
            
            # If we get here, all items have been iterated over without finding a candidate
            #  for stacking. Return false.
            else:
                return (False,None)
        
        # Otherwise we can safely ignore charges on the item, which simplifies things.
        else:
            
            # Before looping through all items, check the item to be inserted
            #  if it doesn't completely fill a stack already.
            if item.stackCount >= stackMax:
                return (False,None)
            
            # Iterate over all items contained in this container.
            for citem in self.content:
                
                # If the item names don't match, continue to the next item.
                if citem.name != item.name:
                    continue
                
                # The names match, so it may be possible to stack the item.
                # Get the number of items that could be stacked on the iterated item.
                freeStack = stackMax - item.stackCount
                
                # If the stack count is maxed, continue to the next item.
                if freeStack <= 0:
                    continue
                
                # If we get here, stacking is possible.
                
                # Thanks to our autostacking, there will never be more than a single
                #  incomplete item stack.
                # If the free stack count is less than the needed stack count,
                #  the item won't stack fully.
                if freeStack < item.stackCount:
                    return (False,citem)
                # Otherwise the item will fully stack.
                else:
                    return (True,citem)
            
            # If we get here, all items have been iterated over without finding a candidate
            #  for stacking. Return false.
            else:
                return (False,None)
    
    
    # Attempt to stack an item onto items already in the container.
    # If a stacking candidate gets provided, only try to stack with this one.
    # Return true if the provided item could be fully stacked, false otherwise.
    def stackItem(self, item, candidate=None):
        # If there's no item, return false.
        if not item:
            return False
        
        # If a candidate was provided, do a quick sanity check.
        if candidate and candidate.name != item.name:
            candidate = None
        
        # No valid candidate, so need to search one.
        if not candidate:
            fullyStack,candidate = self.checkStack(item)
            # If no candidate was found, return.
            if not candidate:
                return False
        
        # Stack the item.
        switched,item1,item2 = candidate.doStack(item)
        success = not switched and not item2
        
        # Flag container as dirty if needed
        if success:
            self.dirty = True
        
        return success
    
    
    # Check if a specific item can go into this container.
    # Return true if possible, otherwise false.
    # Provide an empty list with candidate if the stacking candidate should be returned.
    # The candidate will then be appended to this list.
    def checkItem(self, item, candidate=None, verbose=False):
        # If there's no item, return false.
        if not item:
            return False
        
        # If we need to put out a message to the player, get the player now.
        if verbose:
            if self.item.character:
                player = self.item.character.player
            elif self.item.player:
                player = self.item.player
            else:
                # No player object found, set verbose to false.
                verbose = False
        
        # First check if the item meets all of the required flags.
        if self.contentFlagsRequired != 0:
            if (item.flags ^ self.contentFlagsRequired) & self.contentFlagsRequired:
                if verbose:
                    player.sendGameText(RPG_MSG_GAME_DENIED, "<a:Item%s>%s</a> can't be stored in a <a:Item%s>%s</a>!\\n"%(GetTWikiName(item.name),item.name,GetTWikiName(self.item.name),self.item.name))
                return False
        
        # Then check if the item is one of the supported content types.
        if len(self.contentTypes):
            for ctName in item.itemProto.itemTypes:
                if ctName in self.contentTypes:
                    break
            else:
                if verbose:
                    player.sendGameText(RPG_MSG_GAME_DENIED, "<a:Item%s>%s</a> can't be stored in a <a:Item%s>%s</a>!\\n"%(GetTWikiName(item.name),item.name,GetTWikiName(self.item.name),self.item.name))
                return False
        
        # Check if the item can be stacked on items already in the container.
        fullyStack,citem = self.checkStack(item)
        
        # If we want the candidate returned, append it to the provided list.
        if isinstance(candidate,list):
            candidate.append(citem)
        
        # If the item can't be fully stacked onto items already in the container,
        #  check if the container is already full.
        if not fullyStack and len(self.content) >= self.containerSize:
            if verbose:
                player.sendGameText(RPG_MSG_GAME_DENIED, "There's not enough space for the <a:Item%s>%s</a> in the <a:Item%s>%s</a>.\\n"%(GetTWikiName(item.name),item.name,GetTWikiName(self.item.name),self.item.name))
            return False
        
        # If we get here, the item can be inserted into this container without problems.
        if verbose:
            player.sendGameText(RPG_MSG_GAME_GAINED, "The <a:Item%s>%s</a> has been stowed away in the <a:Item%s>%s</a>.\\n"%(GetTWikiName(item.name),item.name,GetTWikiName(self.item.name),self.item.name))
        return True
    
    
    # Insert an item into this container.
    # Return true if successful, otherwise false.
    def insertItem(self, item, verbose=False):
        candidate = []
        
        # Forbid insertion of a container into another container.
        if item.container:
            return False
        
        # Check if this item can go into the container.
        if not self.checkItem(item,candidate,verbose):
            return False
        
        # Mark item insertion completion as false.
        complete = False
        
        # If the item can be stacked, do so.
        if len(candidate):
            complete = self.stackItem(item,candidate[0])
        
        # If the item didn't fully stack, add a new entry.
        if not complete:
            # Get the item's associated player if any.
            player = None
            if item.character:
                player = item.character.player
            elif item.player:
                player = item.player
            
            # Make sure this item doesn't belong neither to player nor character
            #  or it will turn up at the wrong place on loading.
            item.setCharacter(None)
            item.player = None
            
            # Reset item slot.
            item.slot = -1
            
            # If this item is the players cursor item, update cursor.
            if player and player.cursorItem == item:
                player.cursorItem = None
                player.updateCursorItem(item)
            
            # Add the new entry.
            self.content.append(item)
        
        # Flag container as dirty, something changed.
        self.dirty = True
        
        # Succeeded in adding item, return true.
        return True
    
    
    # Extract and return an item from this container.
    def extractItem(self, item):
        # Remove the item from the cached list of contents.
        try:
            self.content.remove(item)
        except ValueError:
            return None
        
        # If the item instance links to a database item and our own container
        #  item as well, need to remove the container link if present.
        if item.item and self.item.item:
            con = ItemContainerContent._connection.getConnection()
            try:
                con.execute("DELETE FROM item_container_content WHERE item_id=? AND content_id=?;",(self.item.item.id,item.item.id))
            except:
                pass
        
        # Flag container as dirty, something changed.
        self.dirty = True
        
        return item
    
    
    # Extract an item from this container, the item is specified by its index
    #  in the container content list.
    def extractItemByIndex(self, itemIndex):
        # Try to extract the designated item and return the result.
        try:
            return self.extractItem(self.content[itemIndex])
        # If an invalid index was supplied, return none.
        except IndexError:
            return None
    
    
    # Save current container contents to database.
    def storeContents(self):
        backingStore = self.item.item
        # Need to have a database backing for the container item.
        if not backingStore:
            return
        
        # Get the list of currently stored content.
        currList = [cc.content for cc in backingStore.containerContent]
        
        # Run through the complete container content to check which items need storing.
        # It shouldn't be possible to have more stored in database than in memory,
        #  since we make sure to delete a present link when an item gets removed.
        for item in self.content:
            # Skip ethereal items, those should never get stored to database.
            if item.flags&RPG_ITEM_ETHEREAL:
                continue
            # If there is not yet database backing for this item, need to add it.
            if not item.item:
                item.storeToItem(True)
                ItemContainerContent(item=backingStore,content=item.item)
            # Otherwise check if the item already has a container link.
            # If not, add it.
            elif item.item not in currList:
                ItemContainerContent(item=backingStore,content=item.item)


# ------------------------------------------------------------------------------



class ItemSoundProfile(Persistent):
    
    #sounds (could split to seperate table)
    sndAttack1 = StringCol(default="")
    sndAttack2 = StringCol(default="")
    sndAttack3 = StringCol(default="")
    sndAttack4 = StringCol(default="")
    sndAttack5 = StringCol(default="")
    sndAttack6 = StringCol(default="")
    sndAttack7 = StringCol(default="")
    sndAttack8 = StringCol(default="")

    sndHit1 = StringCol(default="")
    sndHit2 = StringCol(default="")
    sndHit3 = StringCol(default="")
    sndHit4 = StringCol(default="")
    sndHit5 = StringCol(default="")
    sndHit6 = StringCol(default="")
    sndHit7 = StringCol(default="")
    sndHit8 = StringCol(default="")
    
    sndUse = StringCol(default="")
    
    #override
    sndEquip = StringCol(default="")
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        
        
        #setup numSndIdleLoop, etc
        sndattribs = ['sndAttack','sndHit']
        for snd in sndattribs:
            num = 0
            for x in xrange(1,5):
                if not getattr(self,snd+str(x)):
                    break
                num+=1
                
            setattr(self,"numS"+snd[1:],num)
            
        sounds = self.sounds = {}
        sounds["sndAttack"]=self.numSndAttack
        sounds["sndHit"]=self.numSndHit
        
        
            
    def getSound(self,snd):
        w = self.sounds[snd]
        w = randint(1,w)
        return getattr(self,snd+str(w))

class ItemStat(Persistent):
    itemProto = ForeignKey('ItemProto')
    statname = StringCol()
    value = FloatCol()
    
class ItemSlot(Persistent):
    itemProto = ForeignKey('ItemProto')
    slot = IntCol()

class ItemRace(Persistent):
    itemProto = ForeignKey('ItemProto')
    racename = StringCol()

class ItemRealm(Persistent):
    itemProto = ForeignKey('ItemProto')
    realmname = IntCol()
    level = IntCol(default=0)

#item class level recommendation
class ItemClass(Persistent):
    itemProto = ForeignKey('ItemProto')
    classname = StringCol()
    level = IntCol()
    
class ItemSpell(Persistent):
    itemProto = ForeignKey('ItemProto')
    spellProto = ForeignKey('SpellProto')
    trigger = IntCol(default = RPG_ITEM_TRIGGER_WORN)
    frequency = IntCol(default = RPG_FREQ_ALWAYS) #freq always applies the effect when worn and never rechecks
    duration = IntCol(default=0) # for poisons and things (proc duration is in successful hits)

class ItemSpellTemp: # no duration here, this is handled differently
    def __init__(self,spellProto,trigger,frequency):
        self.spellProto = spellProto
        self.trigger = trigger
        self.frequency = frequency

class ItemSet(Persistent):
    itemProto = ForeignKey('ItemProto')
    itemSetProto = ForeignKey('ItemSetProto')
    contribution = StringCol()



# Item Proto class to store item base information.
class ItemProto(Persistent):
    # Name of the base item, must be unique.
    name = StringCol(alternateID=True)
    
    # Special item flags.
    flags = IntCol(default = 0)
    # Item type classifiers.
    itemClassifiersInternal = RelatedJoin('ItemClassifier')
    
    # Slots the item can be equipped in.
    slotsInternal = MultipleJoin('ItemSlot')
    
    # Item requirements.
    # Require one of these races.
    racesInternal = MultipleJoin('ItemRace')
    # Require one of these realms.
    realmsInternal = MultipleJoin('ItemRealm')
    # Require one or more of these classes.
    classesInternal = MultipleJoin('ItemClass')
    # If the item has class restrictions, require
    #  this many classes.
    requiredClassNum = IntCol(default=1)
    # Control how the requirement checks are done.
    requirementFlags = IntCol(default=RPG_ITEMREQUIREMENT_NORMAL)
    
    # Level recommendation (blanket).
    level = IntCol(default=1)
    
    # Base stats this item has.
    statsInternal = MultipleJoin('ItemStat')
    # Base procs this item has.
    spellsInternal = MultipleJoin('ItemSpell')
    
    # Set to non-zero if consumable by eating, higher number lasts longer.
    food = IntCol(default=0)
    # Set to non-zero if consumable by drinking, higher number lasts longer.
    drink = IntCol(default=0)
    
    # Skill required to use this item.
    skill = StringCol(default="")
    
    # Basic item description.
    desc = StringCol(default="")
    # Message to be sent to player when equipping this item.
    equipMessage = StringCol(default="")
    
    # Base worth of this item in tin.
    worthTin = IntCol(default=0L)
    
    # Date parameters for Seasonal items
    startDayRL = StringCol(default="")
    endDayRL = StringCol(default="")
    
    # Flag if the item will be destroyed when used up.
    useDestroy = BoolCol(default=True)
    # Base amount of how many times this item can be used.
    useMax = IntCol(default=0)
    
    # ---
    # Weapon fields.
    
    # If weapon has a race bane, name of race.
    wpnRaceBane = StringCol(default="")
    # If weapon has a race bane, bane mod, default at 5%.
    wpnRaceBaneMod = FloatCol(default=0)
    
    # Weapon resist debuff type.
    wpnResistDebuff = IntCol(default=RPG_RESIST_PHYSICAL)
    # Weapon resist debuff mod.
    wpnResistDebuffMod = IntCol(default=0)
    
    # Weapon damage.
    wpnDamage = FloatCol(default = 0)
    # Weapon attack rate, higher number means slower.
    wpnRate = FloatCol(default = 0)
    # Weapon range.
    wpnRange = FloatCol(default = 0)
    
    # Weapon projectile model.
    projectile = StringCol(default="")
    # Weapon projectile speed.
    speed = FloatCol(default=0)
    # ---
    
    # Armor value.
    armor = IntCol(default=0)
    
    #stackable items are always normal quality!!!
    stackMax = IntCol(default = 1)
    stackDefault = IntCol(default=1)
    
    #repair
    repairMax = FloatCol(default = 0)
    
    # Restricted life time for items
    lifeTime = IntCol(default = 0)  # 0 = infinite, else in 1/durSecond seconds
    expireMessage = StringCol(default="")
    
    items = MultipleJoin('Item')
    itemSetsInternal = MultipleJoin('ItemSet')
    
    #graphics
    bitmap = StringCol(default="") #for gui
    model = StringCol(default="")

    sndProfile = ForeignKey('ItemSoundProfile',default=None)
    
    #texture override
    material = StringCol(default="")
    
    spellProto = ForeignKey('SpellProto',default=None) #scrolls
    
    light = FloatCol(default=0.0)
    
    craftConsumed = BoolCol(default=True)
    
    ingredientsInternal = MultipleJoin("RecipeIngredient")
    
    
    
    equippedParticle = StringCol(default="")
    equippedParticleTexture = StringCol(default="")
    
    # If this item is a container store related data here.
    itemContainerProto = ForeignKey('ItemContainerProto',default=None)
    
    # Unused, thus far.
    effectDesc = StringCol(default="")
    #-6 -> 6
    rating = IntCol(default=0)
    noise = IntCol(default = 0)
    wpnAmmunitionType = StringCol(default="")
    isAmmunitionType = StringCol(default="")
    weight = FloatCol(default = 0)
    
    
    def _init(self, *args, **kw):
        Persistent._init(self, *args, **kw)
        
        self.raceList = None
        self.realmList = None
        self.slotList = None
        self.classList = None
        self.statList = None
        self.spellList = None
        self.itemSets = self.itemSetsInternal[:]
        self.ingredientList = None
        self.typeClassList = None


    def _get_ingredients(self):
        if self.ingredientList != None:
            return self.ingredientList
        
        self.ingredientList = list(self.ingredientsInternal)
        return self.ingredientList
    
    def _get_races(self):
        if self.raceList != None:
            return self.raceList
        
        self.raceList = tuple(race.racename for race in self.racesInternal)
        return self.raceList

    def _get_realms(self):
        if self.realmList != None:
            return self.realmList
        
        self.realmList = list(self.realmsInternal)
        return self.realmList

    def _get_slots(self):
        if self.slotList != None:
            return self.slotList
        
        self.slotList = tuple(slot.slot for slot in self.slotsInternal)
        return self.slotList
    
    def _get_classes(self):
        if self.classList != None:
            return self.classList
        
        self.classList = list(self.classesInternal)
        return self.classList


    def _get_stats(self):
        if self.statList != None:
            return self.statList
        
        self.statList = list(self.statsInternal)
        return self.statList
    
    def _get_spells(self):
        if self.spellList != None:
            return self.spellList
        
        self.spellList = list(self.spellsInternal)
        return self.spellList
    
    def _get_itemTypes(self):
        if self.typeClassList != None:
            return self.typeClassList
        
        self.typeClassList = [it.name for it in self.itemClassifiersInternal]
        return self.typeClassList
    
    
    def createInstance(self,bitmapOverride = None,normalQuality=True):
        quality = RPG_QUALITY_EXCEPTIONAL
        repairMax = self.repairMax
        
        if not self.flags and not self.spellProto and len(self.slots):
            if normalQuality:
                quality = RPG_QUALITY_NORMAL
                repairMax = floor(repairMax*.8)
            elif self.stackMax <= 1:
                #generate quality
                r = randint(0,99)
                if r < 50:
                    quality = RPG_QUALITY_NORMAL
                    repairMax = floor(repairMax*.8)
                elif r < 65:
                    quality = RPG_QUALITY_CRUDDY
                    repairMax = floor(repairMax*.6)
                elif r < 85:
                    quality = RPG_QUALITY_SHODDY
                    repairMax = floor(repairMax*.7)
                elif r < 95:
                    quality = RPG_QUALITY_SUPERIOR
                    repairMax = floor(repairMax*.9)
                #otherwise exceptional, which is already set
        
        if self.flags & RPG_ITEM_INDESTRUCTIBLE:
            repairMax = 0
        elif self.repairMax > 0 and not repairMax:
            repairMax = 1
        else:
            repairMax = int(repairMax)
        
        repair = repairMax
        #create the instance
        
        if self.stackMax > 1 and self.stackDefault > 1:
            stackCount = self.stackDefault
        else:
            stackCount = 1
        
        if bitmapOverride:
            bitmap = bitmapOverride
        else:
            bitmap = self.bitmap
        
        item = ItemInstance()
        item.name       = self.name
        item.itemProto  = self
        item.quality    = quality
        item.repair     = repair
        item.repairMax  = repairMax
        item.lifeTime   = self.lifeTime
        item.character  = None
        item.stackCount = stackCount
        item.food       = self.food
        item.drink      = self.drink
        item.useCharges = self.useMax
        item.bitmap     = bitmap
        if self.itemContainerProto:
            item.container = ItemContainer(item)
        item.refreshFromProto()
        
        return item


DAMAGELOOKUP = {
    "Fists": RPG_DMG_PUMMEL,
    "1H Pierce": RPG_DMG_PIERCING,
    "2H Pierce": RPG_DMG_PIERCING,
    "1H Impact": RPG_DMG_IMPACT,
    "2H Impact": RPG_DMG_IMPACT,
    "1H Cleave": RPG_DMG_CLEAVE,
    "2H Cleave": RPG_DMG_CLEAVE,
    "1H Slash": RPG_DMG_SLASHING,
    "2H Slash": RPG_DMG_SLASHING,
    "Foresting":RPG_DMG_FOREST,
    "Mining":RPG_DMG_MINE,
}


class Item(Persistent):
    name = StringCol()
    itemProto = ForeignKey('ItemProto')
    
    #instance specifics
    
    stackCount = IntCol(default = 1)
    
    useCharges = IntCol(default = 0)
    
    quality = IntCol(default=RPG_QUALITY_NORMAL)
    
    food = IntCol(default=0)
    drink = IntCol(default=0)
    
    repairMax = FloatCol(default = 0)
    repair = FloatCol(default = 0)
    lifeTime = IntCol(default = 0)  # 0 = infinite, else in ticks
    
    slot = IntCol(default=0) #where the item is on the character
    
    #persistent items only owned by characters
    character = ForeignKey('Character',default = None)
    player = ForeignKey('Player',default=None)
    
    xpCoupon = IntCol(default = 0)
    
    descOverride = StringCol(default="")
    levelOverride = IntCol(default=0)
    
    spellEnhanceLevel = IntCol(default=0)
    
    bitmap = StringCol(default = "")
    
    #todo, store reuse
    #persistentReuseTimer = IntCol(default=0)
    
    #variants
    hasVariants = BoolCol(default=False)
    variants = MultipleJoin("ItemVariant")
    
    crafted = BoolCol(default=False)
    
    containerContent = MultipleJoin('ItemContainerContent')
    
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
    
    
    def expire(self):
        for v in self.variants:
            v.expire()
        for cc in self.containerContent:
            cc.content.expire()
            cc.expire()
        Persistent.expire(self)
    
    
    def destroySelf(self):
        for v in self.variants:
            v.destroySelf()
        for cc in self.containerContent:
            cc.content.destroySelf()
            cc.destroySelf()
        Persistent.destroySelf(self)




class ItemInstance:
    def __init__(self, item=None):
        self.worthIncreaseTin  = 0
        # timer for poisons and spell enchantments
        self.procs    = {}
        self.itemInfo = ItemInfo(self)
        if not item:
            self.item              = None  # associated db item
            # fields that better be initialized
            self.stackCount        = 1
            self.useCharges        = 0
            self.quality           = RPG_QUALITY_NORMAL
            self.food              = 0
            self.drink             = 0
            self.repairMax         = 0
            self.repair            = 0
            self.lifeTime          = 0
            self.slot              = -1 #where the item is on the character
            self.character         = None
            self.player            = None
            self.xpCoupon          = 0
            self.descOverride      = ""
            self.levelOverride     = 0
            self.spellEnhanceLevel = 0
            self.bitmap            = ""
            self.hasVariants       = False
            self.variants          = {}
            self.crafted           = False
            self.container         = None
        else:
            self.loadFromItem(item)
    
    
    def loadFromItem(self, item):
        self.item              = item  # associated db item
        self.name              = item.name
        self.itemProto         = item.itemProto
        self.stackCount        = item.stackCount
        self.useCharges        = item.useCharges
        self.quality           = item.quality
        self.food              = item.food
        self.drink             = item.drink
        self.repairMax         = item.repairMax
        self.repair            = item.repair
        self.lifeTime          = item.lifeTime
        self.slot              = item.slot #where the item is on the character
        self.character         = item.character
        self.player            = item.player
        self.xpCoupon          = item.xpCoupon
        self.descOverride      = item.descOverride
        self.levelOverride     = item.levelOverride
        self.spellEnhanceLevel = item.spellEnhanceLevel
        self.bitmap            = item.bitmap
        #variants
        self.hasVariants       = item.hasVariants
        from itemvariants import ItemVariantsLoad
        ItemVariantsLoad(self)
        self.crafted           = item.crafted
        if self.itemProto.itemContainerProto:
            self.container     = ItemContainer(self)
        else:
            self.container     = None
        self.refreshFromProto()
        return self
    
    
    def storeToItem(self, override=False):
        # Only store items in the posession of a player!
        if not self.character and not self.player and not override:
            return
        if not self.item:
            self.item = Item(name=self.name,itemProto=self.itemProto)
        # Fill a dict with the values that need saving to db to prevent multiple calls.
        data = {
            'name': self.name,
            'stackCount': self.stackCount,
            'useCharges': self.useCharges,
            'quality': self.quality,
            'food': self.food,
            'drink': self.drink,
            'repairMax': self.repairMax,
            'repair': self.repair,
            'lifeTime': self.lifeTime,
            'slot': self.slot,
            'character': self.character,
            'player': self.player,
            'xpCoupon': self.xpCoupon,
            'descOverride': self.descOverride,
            'levelOverride': self.levelOverride,
            'spellEnhanceLevel': self.spellEnhanceLevel,
            'bitmap': self.bitmap,
            'hasVariants': self.hasVariants,
            'crafted': self.crafted
        }
        self.item.set(**data)
        # Save variants.
        from itemvariants import ItemVariantsSave
        ItemVariantsSave(self)
        # Save container contents.
        if self.container:
            self.container.storeContents()
    
    
    def clone(self):
        proto = self.itemProto
        nitem = proto.createInstance()
        #instance specifics
        nitem.name              = self.name
        nitem.quality           = self.quality
        nitem.repair            = self.repair
        nitem.repairMax         = self.repairMax
        nitem.lifeTime          = self.lifeTime
        nitem.stackCount        = self.stackCount
        nitem.food              = proto.food
        nitem.drink             = proto.drink
        nitem.useCharges        = proto.useMax
        nitem.bitmap            = self.bitmap
        nitem.xpCoupon          = self.xpCoupon
        nitem.descOverride      = self.descOverride
        nitem.levelOverride     = self.levelOverride
        nitem.spellEnhanceLevel = self.spellEnhanceLevel
        nitem.variants          = copy(self.variants)
        return nitem
    
    
    def destroySelf(self):
        player = None
        
        # Clean up character item.
        if self.character:
            player = self.character.player
            mob = self.character.mob
            # Clean up caches in the characters mob.
            if mob:
                try:
                    del mob.itemRequireTick[self]
                except KeyError:
                    pass
                try:
                    del mob.itemFood[self]
                except KeyError:
                    pass
                try:
                    del mob.itemDrink[self]
                except KeyError:
                    pass
            
            try:
                # If the item was worn by the character, unequip it now.
                if RPG_SLOT_WORN_END > self.slot >= RPG_SLOT_WORN_BEGIN:
                    mob.unequipItem(self.slot)
                
                # If the item was equipped by the pet, unequip it now.
                elif mob.pet and RPG_SLOT_PET_END > self.slot >= RPG_SLOT_PET_BEGIN:
                    mob.pet.unequipItem(self.slot - RPG_SLOT_PET_BEGIN)
                
                # Actually remove the item from characters inventory.
                self.character.items.remove(self)
            
            # Item in bank probably assigned to a character currently not active,
            #  removal from non-existing list will naturally fail.
            except ValueError:
                pass
        
        # Clean up player (bank) item.
        if self.player:
            player = self.player
            try:
                del self.player.bankItems[self.slot]
            except KeyError:  # borked item, may happen on cleanup
                pass
        
        # Delete database backing of this item.
        if self.item:
            self.item.destroySelf()
            self.item = None
        
        # If this item was owned by a character or player, need to make sure
        #  it isn't the cursor item. If so, remove it.
        if player:
            if self == player.cursorItem:
                player.cursorItem = None
                player.updateCursorItem(self)
            player.cinfoDirty = True
    
    
    # Just a little function for easier dynamic changes to an object
    #  (enchanting, socketing, ...)
    def clearVariants(self):
        self.variants = {}
        self.hasVariants = False
    
    
    def numVariants(self):
        num = 0
        for varList in self.variants.itervalues():
            if isinstance(varList,tuple):
                num += 1
            else:
                num += len(varList)
        return num
    
    
    # Function attempts to stack argument on self.
    # If stacking is not possible, switch items.
    # Returns a tuple with (switched,item1,item2),
    #  item2 being the updated argument if not switched.
    def doStack(self, item):
        # Get the items max stack count.
        stackMax = self.itemProto.stackMax
        
        # Just switch the items if stacking is impossible.
        if not item or stackMax <= 1 or self.name != item.name:
            return (True,item,self)
        
        # Fix borked stackCounts (from legacy).
        if not item.stackCount:
            item.stackCount = 1
        if not self.stackCount:
            self.stackCount = 1
        
        # Get the items max charge count.
        useMax = self.itemProto.useMax
        
        # Handle items with more than one charge separately
        #  from those without to cleanly stack charges.
        if useMax > 1:
            
            # Get free charges.
            freeCharges = useMax * (stackMax - self.stackCount + 1) - self.useCharges
            
            # If stacking is not possible due to full stack or charges,
            #  just switch.
            if freeCharges <= 0:
                return (True,item,self)
            
            # For easier stacking calculation, calculate in charges only.
            # Get charges that need stacking.
            neededCharges = useMax * (item.stackCount - 1) + item.useCharges
            # Clamp amount of stackable charges to needed charges.
            if freeCharges > neededCharges:
                freeCharges = neededCharges
            # Recalculate charge and stack count.
            useCharges = freeCharges % useMax
            stackCount = freeCharges / useMax
            # First update charges on both items.
            self.useCharges += useCharges
            item.useCharges -= useCharges
            # If the stacked item has now 0 or less charges, need to decrement its
            #  stack count and adjust the charges.
            if item.useCharges <= 0:
                item.useCharges += useMax
                item.stackCount -= 1
            # If we have now more than the maximum number of charges, need to
            #  increment our stack count and adjust our charges.
            if self.useCharges > useMax:
                self.useCharges -= useMax
                self.stackCount += 1
        
        # Otherwise we only have to deal with stack count.
        else:
            # Get free stack count.
            stackCount = stackMax - self.stackCount
            # If there's no room to stack, just switch.
            if stackCount <= 0:
                return (True,item,self)
            # Clamp free stack count to needed stack count.
            if stackCount > item.stackCount:
                stackCount = item.stackCount
        
        # Update stack count on item and ourselves.
        self.stackCount += stackCount
        item.stackCount -= stackCount
        
        # If the item has been fully stacked, destroy it before returning.
        if item.stackCount <= 0:
            item.destroySelf()
            # Refresh item info.
            if useMax > 1:
                self.itemInfo.refreshDict({'STACKCOUNT':self.stackCount,'USECHARGES':self.useCharges})
            else:
                self.itemInfo.refreshDict({'STACKCOUNT':self.stackCount})
            # Return.
            return (False,self,None)
        else:
            # Refresh item info of both items.
            if useMax > 1:
                self.itemInfo.refreshDict({'STACKCOUNT':self.stackCount,'USECHARGES':self.useCharges})
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})
            else:
                self.itemInfo.refreshDict({'STACKCOUNT':self.stackCount})
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
            # Return.
            return (False,self,item)
    
    
    def doItemSpellUse(self,mob,proto):
        tgt = mob.target
        if proto.target == RPG_TARGET_SELF:
            tgt = mob
        if proto.target == RPG_TARGET_PARTY:
            tgt = mob
        if proto.target == RPG_TARGET_ALLIANCE:
            tgt = mob
        if proto.target == RPG_TARGET_PET:
            tgt = mob.pet
        
        if not tgt:
            return
        
        if proto.animOverride:
            mob.zone.simAvatar.mind.callRemote("playAnimation",mob.simObject.id,proto.animOverride)
        if len(proto.particleNodes):
            mob.zone.simAvatar.mind.callRemote("triggerParticleNodes",mob.simObject.id,proto.particleNodes)
        
        mod = 1.0 #to do recommended level
        
        if proto.projectile:
            p = Projectile(mob,mob.target)
            p.spellProto = proto
            p.launch()
        else:
            SpawnSpell(proto,mob,tgt,tgt.simObject.position,mod,proc=True)
    
    
    def use(self,mob):
        # Is this a ranged weapon?
        # Everything below will be handled in shootRanged() anyway so test here.
        if self.wpnDamage and self.wpnRange and self.slot == RPG_SLOT_RANGED and mob.rangedReuse <= 0:
            mob.shootRanged()
            return
        
        player = mob.player
        
        # Check if the mob is allowed to use this item.
        if not self.isUseable(mob) or self.penalty:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot currently use this %s.\\n"%(mob.name,self.name))
            return
        
        # Check if the mob is in a condition to use this item.
        if mob.sleep > 0 or mob.stun > 0  or mob.isFeared:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot use items while asleep, stunned, or feared.\\n"%(mob.name))
            return
        
        # Check if this item can already be used again.
        if self.reuseTimer:
            if player:
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot use this %s for another %i seconds.\\n"%(mob.name,self.name,self.reuseTimer))
            return
        
        # If this item is associated with a skill, check if
        #  the mob has the skill and reset reuse timer.
        #todo proper timing
        if self.skill:
            if not mob.skillLevels.get(self.skill):
                if player:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot use this %s as it requires the %s skill.\\n"%(mob.name,self.name,self.skill))
                return
            try:
                mskill = mob.mobSkillProfiles[self.skill]
                self.reuseTimer = mskill.reuseTime
            except:
                self.reuseTimer = 60
            mob.itemRequireTick[self] = self.reuseTimer
        else:
            self.reuseTimer = 0
        
        self.itemInfo.refresh()  # needed? maybe selective refresh?
        
        # Only players use tomes and scrolls, or should.
        if player:
            
            # Get the character now.
            char = mob.character
            
            # Get the item's SpellProto.
            spellProto = self.itemProto.spellProto
            
            # If the item has a SpellProto, then it is either a tome or
            #  a spell scroll.
            if spellProto:
                
                # If the item has a spellEnhanceLevel, then it is a tome.
                if self.spellEnhanceLevel:
                    
                    # Iterate over the Character's spells.
                    for s in char.spells:
                        
                        # If a spell is found within a SpellProto
                        #  matching the tome's SpellProto, then the
                        #  Character's spell level may increase.
                        if s.spellProto == spellProto:
                            
                            # If the spell's tome level is above the
                            #  item's spellEnhanceLevel, then the tome is
                            #  too low level.
                            if s.level >= self.spellEnhanceLevel:
                                
                                # Inform the Player.
                                player.sendGameText(RPG_MSG_GAME_DENIED,r'%s already understands the knowledge contained in this tome.\n'%char.name)
                            
                            # Otherwise, the spell is being upgraded.
                            else:
                                
                                # Inform the Player.
                                player.sendGameText(RPG_MSG_GAME_GAINED,r'$src has increased $srchis knowledge of the <a:Spell%s>%s</a> spell!\n'%(GetTWikiName(spellProto.name),spellProto.name),mob)
                                
                                # Item was used, so update the stack
                                #  count.
                                self.stackCount -= 1
                                
                                # If the stack count is zero or below,
                                #  then consume the item.
                                if self.stackCount <= 0:
                                    
                                    # Take the item.
                                    player.takeItem(self)
                                
                                # Otherwise, the stack still has items.
                                else:
                                    
                                    # Refresh ItemInfo so observing
                                    #  clients see the new stack count.
                                    self.itemInfo.refreshDict({'STACKCOUNT':self.stackCount})
                                
                                # Update the spell level.
                                s.level += 1
                                
                                # Refresh SpellInfo so observing clients
                                #  see the new level.
                                s.spellInfo.fullRefresh()
                            
                            # The tome was either used or not used, so
                            #  return.
                            return
                    
                    # Otherwise, the Character does not know the spell
                    #  so inform the Player and return.
                    player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't know the <a:Spell%s>%s</a> spell.\\n"%(char.name,GetTWikiName(spellProto.name),spellProto.name))
                    return
                
                # A spell scroll was clicked.
                else:
                    
                    # Get a list of all slots for spells known by the
                    #  Character.
                    sslots = [s.slot for s in char.spells]
                    
                    # Iterate over all possible slot values.
                    for sslot in xrange(0,256):
                        
                        # If the number is not in the used slots, then
                        #  use it.
                        if not sslot in sslots:
                            
                            # Use the spell slot with the scroll.
                            char.onSpellSlot(sslot,self)
                            return
                    
                    # All slots have been iterated over, return.
                    return
        
        # The Item has no SpellProto, continue with further tests.
        
        if len(self.spells) and mob.character:
            gotone = False
            for ispell in self.spells:
                if ispell.trigger == RPG_ITEM_TRIGGER_POISON:
                    pw = mob.worn.get(RPG_SLOT_PRIMARY,None)
                    if not pw:
                        if player:
                            player.sendGameText(RPG_MSG_GAME_DENIED,"%s must have a primary weapon equipped to apply a poison.\\n"%mob.name)
                        return
                    # apply poison, funnier than ever before
                    if pw.procs.has_key(ispell):    # just refresh old poison
                        pw.procs[ispell] = [ispell.duration,RPG_ITEMPROC_POISON]
                        player.sendGameText(RPG_MSG_GAME_GAINED,"%s refreshes %s.\\n"%(mob.name,self.name))
                    elif len(pw.procs) < RPG_ITEMPROC_MAX:    # check for max temporary procs on weapon
                        pw.procs[ispell] = [ispell.duration,RPG_ITEMPROC_POISON]
                        player.sendGameText(RPG_MSG_GAME_GAINED,"%s applies %s.\\n"%(mob.name,self.name))
                    else:
                        overwriting = []
                        for proc in pw.procs.iterkeys():    # overwrite poison with lowest duration
                            if pw.procs[proc][1] != RPG_ITEMPROC_ENCHANTMENT:
                                if not overwriting or overwriting[1] < pw.procs[proc][0]:
                                    overwriting = (proc,pw.procs[proc][0])
                        if not overwriting:
                            player.sendGameText(RPG_MSG_GAME_DENIED,"%s radiates so much power that %s evaporates.\\n"%(pw.name,self.name))
                        else:    # found something to overwrite
                            del pw.procs[overwriting[0]]
                            pw.procs[ispell] = [ispell.duration,RPG_ITEMPROC_POISON]
                            player.sendGameText(RPG_MSG_GAME_DENIED,"The applied %s nullifies %s.\\n"%(self.name,overwriting[0].spellProto.name))
                    # only need to update for description,
                    # so only do if attacker is a player or a player pet
                    if player or (mob.master and mob.master.player):
                        pw.itemInfo.refreshProcs()
                    mob.playSound("sfx/Underwater_Bubbles2.ogg")
                    gotone=True
                
                elif ispell.trigger == RPG_ITEM_TRIGGER_USE:
                    for e in ispell.spellProto.effectProtos:
                        if e.hasPermanentStats:
                            for stat in e.permanentStats:
                                if "Base" in stat.statname:
                                    stname = stat.statname.replace("Base","Raise")
                                    if not getattr(mob.character,stname):
                                        if player:
                                            player.sendGameText(RPG_MSG_GAME_DENIED,"You cannot raise your stat higher in this manner.\\n")
                                        return
                        if e.giveSkill:
                            if mob.skillLevels.get(e.giveSkill,0):
                                if player:
                                    player.sendGameText(RPG_MSG_GAME_DENIED,"%s already knows the %s skill.\\n"%(mob.name,e.giveSkill))
                                return
                                    
                    gotone = True
                    self.doItemSpellUse(mob,ispell.spellProto)
            if gotone and self.useCharges:
                self.useCharges-=1
                if not self.useCharges and self.itemProto.useDestroy:
                    
                    # no need to check for positive stackCount
                    self.stackCount-=1
                    if self.stackCount <= 0:
                        player.takeItem(self)
                    else:
                        self.useCharges = self.itemProto.useMax
                        self.itemInfo.refreshDict({'STACKCOUNT':self.stackCount,'USECHARGES':self.useCharges})
                    return
                else:
                    if self.useCharges < 0:
                        self.useCharges = 0
                    else:
                        self.itemInfo.refreshDict({'USECHARGES':self.useCharges})
        
        #an xpCoupin?
        if self.xpCoupon:
            #always destroys self
            mob.character.gainXP(self.xpCoupon,False)
            player.takeItem(self)
    
    
    def tick(self):
        needsTick = True
        if self.reuseTimer:
            self.reuseTimer -= 1
            if self.reuseTimer <= 0:
                self.reuseTimer = 0
                self.itemInfo.refreshDict({'REUSETIMER':self.reuseTimer})
                needsTick = False
        if (self.character or self.player) and self.itemProto.lifeTime > 0:
            needsTick = True
            self.lifeTime -= 3
            if self.lifeTime <= 0:
                if self.character:
                    player = self.character.player
                    char = self.character
                else:
                    player = self.player
                    char = player.curChar
                if self.itemProto.expireMessage:
                    player.sendGameText(RPG_MSG_GAME_LOST,"%s\\n"%(self.itemProto.expireMessage),char.mob)
                else:
                    player.sendGameText(RPG_MSG_GAME_LOST,r'The %s has magically been whisked away from %s!\n'%(self.name,char.name))
                self.destroySelf()
                needsTick = False
        
        # Return if this item needs further ticking or not.
        return needsTick
    
    
    def isUseable(self,mob):
        spawn = mob.spawn
        proto = self.itemProto
        
        # Don't allow premium flagged items and items over level 50 to
        #  demo players.
        if RPG_BUILD_DEMO and mob.player and not mob.player.premium:
            if self.level >= 50 or self.itemProto.flags&RPG_ITEM_PREMIUM:
                return False
        
        # Check if the mob has the skill to use this item.
        if proto.skill:
            if not mob.skillLevels.get(proto.skill):
                # Can't use based on skill.
                return False
        
        # Check if the mob meets the race requirements.
        if len(proto.races):
            # If the RPG_ITEMREQUIREMENT_RACEREVERSED flag is set,
            #  the mob isn't allowed to have one of the listed races.
            if proto.requirementFlags&RPG_ITEMREQUIREMENT_RACEREVERSED:
                if spawn.race in proto.races:
                    # Can't use based on race.
                    return False
            # Otherwise check the positive way (need race).
            elif spawn.race not in proto.races:
                # Can't use based on race.
                return False
        
        # Check if the mob meets the realm requirements.
        if len(proto.realms):
            for r in proto.realms:
                if spawn.realm == r.realmname:
                    break
            else:
                # Can't use based on realm.
                return False
        
        # Check if the mob meets the class requirements.
        # If the RPG_ITEMREQUIREMENT_EXACTCLASSNUM flag is set,
        #  need to have exactly this many classes.
        if proto.requirementFlags&RPG_ITEMREQUIREMENT_EXACTCLASSNUM:
            classNum = (3 if spawn.tclass else 2) if spawn.sclass else 1
            if classNum != proto.requiredClassNum:
                # Can't use based on class number.
                return False
        if len(proto.classes):
            # If the RPG_ITEMREQUIREMENT_CLASSREVERSED flag is set,
            #  the mob isn't allowed to have one of the listed classes.
            if proto.requirementFlags&RPG_ITEMREQUIREMENT_CLASSREVERSED:
                for cl in proto.classes:
                    if cl.classname == spawn.pclass.name or (spawn.sclass and spawn.sclass.name == cl.classname) or (spawn.tclass and spawn.tclass.name == cl.classname):
                        # Can't use based on class.
                        return False
            # Otherwise check the positive way (need class).
            # Need to match at least requiredClassNum classes.
            else:
                match = 0
                for cl in proto.classes:
                    if cl.classname == spawn.pclass.name or (spawn.sclass and spawn.sclass.name == cl.classname) or (spawn.tclass and spawn.tclass.name == cl.classname):
                        match += 1
                        if match >= proto.requiredClassNum:
                            break
                else:
                    # Can't use based on class.
                    return False
        
        # If we end here, the mob can use this item.
        return True
    
    
    def setCharacter(self, char, refresh=True):
        if hasattr(char,"mob") and char.mob:
            self.canUse = self.isUseable(char.mob)
            self.penalty = self.getPenalty(char.mob)
        
        if self.character == char:
            if refresh:
                self.refreshFromProto()
            return
        
        if self.character:
            if hasattr(self.character,"mob") and self.character.mob:
                if self in self.character.mob.worn.itervalues():
                    self.character.mob.unequipItem(self.slot)
            try:
                mob = self.character.mob
                if mob:
                    try:
                        del mob.itemRequireTick[self]
                    except KeyError:
                        pass
                    try:
                        del mob.itemFood[self]
                    except KeyError:
                        pass
                    try:
                        del mob.itemDrink[self]
                    except KeyError:
                        pass
                self.character.items.remove(self)
            # It's possible that the item is sitting in the bank, but still
            #  assigned to the character that put it there.
            # In such a case, the original owner might not be in the world
            #  and the removal will fail. Luckily without producing a duping bug
            #  as the item list will be generated from assigned items once the
            #  relevant character goes live. After the items character value has
            #  been set to a new value.
            except ValueError:
                pass
        if self.player:
            del self.player.bankItems[self.slot]
        
        self.character = char
        self.player = None
        
        if char:
            char.items.append(self)
            mob = char.mob
            if mob:
                if self.lifeTime:
                    mob.itemRequireTick[self] = self.lifeTime
                if self.food:
                    mob.itemFood[self] = self.food
                if self.drink:
                    mob.itemDrink[self] = self.drink
        
        # changes to character attribute have to be written to db immediately,
        # else a player giving away an item and logging in before said item gets
        # backupped will receive the item again.
        item = self.item
        if item:
            item.character = char
            item.player = None
        
        if refresh:
            self.refreshFromProto()
    
    
    ## @brief Sets the items owner to the Player.
    #  @param (self) The object pointer.
    #  @param (player) The player who will take ownership of the item.
    #  @return None.
    def setPlayerAsOwner(self, player):
        
        # Only one entity may own the item.  Clear the Character and set the
        # Player.
        self.character = None
        self.player = player
        
        # Ownership must persist immediately, otherwise a player could relog
        # and receive the item again.
        item = self.item
        if item:
            item.character = None
            item.player = player
    
    
    #this function exists so that we can display different stats 
    #to different characters based on their level and stuff
    #like in a trade screen, etc
    def getPenalty(self,mob,forPet = False):
        if not forPet and not self.isUseable(mob):
            return 1.0
        proto = self.itemProto
        
        penalty = 1.0
        repairRatio = 1.0
        
        itemLevel = self.level
        levelCheck = mob.plevel
        delta = 9999
        
        # class recommendation
        for cl in list(proto.classes):
            if not cl.level:
                traceback.print_stack()
                print "AssertionError: no level to class %s recommendation assigned, on item %s!"%(cl.classname,self.name)
                continue
            if forPet:
                if cl.level > itemLevel:
                    itemLevel = cl.level
                continue
            if cl.classname == mob.pclass.name:
                diff = cl.level - mob.plevel
                if diff < delta:
                    delta = diff
                    itemLevel = cl.level
                    levelCheck = mob.plevel
            elif mob.sclass and cl.classname == mob.sclass.name:
                diff = cl.level - mob.slevel
                if diff < delta:
                    delta = diff
                    itemLevel = cl.level
                    levelCheck = mob.slevel
            elif mob.tclass and cl.classname == mob.tclass.name:
                diff = cl.level - mob.tlevel
                if diff < delta:
                    delta = diff
                    itemLevel = cl.level
                    levelCheck = mob.tlevel
        
        # realm recommendation (only for level, usability already checked)
        for r in list(proto.realms):
            if r.level:
                if forPet:
                    if r.level > itemLevel:
                        itemLevel = r.level
                else:
                    diff = r.level - mob.plevel
                    if diff < delta:
                        itemLevel = r.level
                        levelCheck = mob.plevel
        
        # enhanced item penalty code, if user lacks more than 20 levels -> 100% penalty
        if itemLevel > 1:
            if itemLevel < 20:
                penalty = 1.0 - float(levelCheck)/float(itemLevel)
                if penalty < 0.0:
                    penalty = 0.0
            else:
                diff = float(itemLevel - levelCheck) / 20.0
                if diff <= 0.0:
                    penalty = 0.0
                elif diff >= 1.0:
                    penalty = 1.0
                # diminishing penalty the closer the user gets to required level
                else:
                    point = diff*diff
                    penalty = 1.0 - floor(100.0 * (1.0 + point*(point - 2.0))) / 100.0
        else:
            penalty = 0.0
        
        # repair
        if self.repairMax:
            repairRatio = float(self.repair)/float(self.repairMax)
            if repairRatio < .2: #at 20% of repair penalty starts
                penalty+=(.2-repairRatio)*4.0 #up to 80% penalty for repair
            if self.repair == 0:
                penalty = 1.0
        
        if penalty < .01:
            penalty = 0.0
        if penalty > 1.0:
            penalty = 1.0
        
        return penalty
    
    
    def getWorth(self,valueMod = 1.0,playerSelling = False):
        proto = self.itemProto
        
        tin = proto.worthTin
        tin += self.worthIncreaseTin
        
        tin = floor(tin * RPG_QUALITY_MODS[self.quality])
        tin = ceil(tin * valueMod)
        
        mod = 1.0
        if self.stackCount:
            if not proto.stackDefault:
                mod = float(self.stackCount)
            else:
                mod = float(self.stackCount)/float(proto.stackDefault)
        
        # literature items sell for far less than they're bought at
        if playerSelling and self.flags&RPG_ITEM_LITERATURE:
            mod /= 2.0
        
        # modify worth by relative repair value
        if self.repairMax:
            diminish = 0.1 - 0.1 * float(self.repair) / float(self.repairMax)
            mod -= mod * diminish
        
        tin = ceil(tin * mod)
        
        return long(tin)
    
    
    #this is called when database is recompiled, and when item is first brought into memory
    def refreshFromProto(self,forPet = False):
        self.reuseTimer = 0
        
        #create all the poop from the proto
        proto = self.itemProto
        
        self.spellProto = proto.spellProto
        self.classes = [(cl.classname,cl.level) for cl in proto.classes]
        if self.spellProto:
            for cl in self.spellProto.classes:
                self.classes.append((cl.classname,cl.level))
                
        self.level = proto.level
        if self.levelOverride:
            self.level = self.levelOverride
        
        if not forPet:
            self.penalty = 0
            self.canUse = False
            if self.character:
                self.setCharacter(self.character,False) #sets up some stuff
        
        penalty = 1.0 - self.penalty
        
        self.light = floor(proto.light*penalty)
        self.flags = proto.flags
        
        self.material = proto.material
        # fix borked counts, since we still have the item it doesn't need expunging
        if not self.stackCount:
            self.stackCount = 1
        
        #todo split off wpnDamage/wpnRate into actual columns for quality
        self.wpnDamage = ceil(proto.wpnDamage*penalty)
        self.wpnRate = ceil(proto.wpnRate+self.penalty*proto.wpnRate)
        self.wpnRange = ceil(proto.wpnRange*penalty)
        
        self.model = proto.model
        self.sndProfile = proto.sndProfile
        
        self.dmgType = RPG_DMG_PUMMEL
        if DAMAGELOOKUP.has_key(proto.skill):
            self.dmgType = DAMAGELOOKUP[proto.skill]
        
        self.wpnAmmunitionType = proto.wpnAmmunitionType
        
        self.projectile = proto.projectile
        self.speed = proto.speed
        
        self.weight = proto.weight
        self.desc = proto.desc
        self.effectDesc = proto.effectDesc
        self.armor = floor(proto.armor*penalty)
        
        self.skill = proto.skill
        
        if not self.penalty:
            self.spells = list(proto.spells)
        else:
            self.spells = []
        
        self.stats = []
        for st in proto.stats:
            self.stats.append((st.statname,st.value))
        
        if self.hasVariants:
            self.flags |= RPG_ITEM_ARTIFACT
            numVariants = self.numVariants()
            if numVariants:
                self.quality = RPG_QUALITY_EXCEPTIONAL
                if self.spellEnhanceLevel == 9999:  # hack
                    self.flags |= RPG_ITEM_ENCHANTED
                level = self.level+10
                self.worthIncreaseTin = level**5+500
                self.worthIncreaseTin*=(numVariants*2)+5
            elif self.spellEnhanceLevel == 9999:  # hack
                self.quality = RPG_QUALITY_CRUDDY
        
        mod = RPG_QUALITY_MODS[self.quality]
        #adjust for quality
        self.armor = floor(self.armor*mod)
        self.wpnDamage = floor(self.wpnDamage*mod)
        self.wpnRate = ceil(self.wpnRate+self.wpnRate*(1.0-mod))
        self.wpnRange = floor(self.wpnRange*mod)
        self.light = ceil(self.light*mod)
        
        self.wpnRaceBane = proto.wpnRaceBane
        self.wpnRaceBaneMod = proto.wpnRaceBaneMod
        
        self.wpnResistDebuff = proto.wpnResistDebuff
        self.wpnResistDebuffMod = proto.wpnResistDebuffMod
        
        self.repairMax = proto.repairMax
        
        if self.hasVariants:
            # Always apply enchantments if 'flag' is set.
            # Either to strip normal stats or to give special ones.
            if self.spellEnhanceLevel == 9999:
                from itemvariants import ApplyEnchantment
                ApplyEnchantment(self)
            elif numVariants:
                from itemvariants import ApplyVariants
                ApplyVariants(self)
        
        if self.quality == RPG_QUALITY_NORMAL:
            self.repairMax = floor(self.repairMax*.8)
        elif self.quality == RPG_QUALITY_CRUDDY:
            self.repairMax = floor(self.repairMax*.6)
        elif self.quality == RPG_QUALITY_SHODDY:
            self.repairMax = floor(self.repairMax*.7)
        elif self.quality == RPG_QUALITY_SUPERIOR:
            self.repairMax = floor(self.repairMax*.9)
        # otherwise exceptional, which is already set
        if self.flags & RPG_ITEM_INDESTRUCTIBLE:
            self.repairMax = 0
        elif proto.repairMax > 0 and not self.repairMax:
            self.repairMax = 1
        else:
            self.repairMax = int(self.repairMax)
        
        if self.repair > self.repairMax:
            self.repair = self.repairMax
        
        if penalty < 1.0:
            stats = []
            for st in self.stats:
                if st[1] < 0:
                    stats.append(st)
                else:
                    value = st[1]
                    if st[0] in RPG_STAT_PERCENTLOOKUP:
                        value = value * penalty
                    else:
                        value = floor(value * penalty)
                    
                    if value:
                        stats.append((st[0],value))
            
            self.stats = stats
        
        self.itemInfo.reset()




class ItemSetStat(Persistent):
    itemSetPower = ForeignKey('ItemSetPower')
    statname = StringCol()
    value = FloatCol()

class ItemSetSpell(Persistent):
    itemSetPower = ForeignKey('ItemSetPower')
    spellProto = ForeignKey('SpellProto')
    # only RPG_ITEM_TRIGGER_WORN, RPG_ITEM_TRIGGER_MELEE or RPG_ITEM_TRIGGER_DAMAGED allowed
    trigger = IntCol(default = RPG_ITEM_TRIGGER_WORN)
    frequency = IntCol(default = RPG_FREQ_ALWAYS) #freq always applies the effect when worn and never rechecks
    duration = IntCol(default=0)

class ItemSetRequirement(Persistent):
    itemSetPower = ForeignKey('ItemSetPower')
    name = StringCol(default = "")
    itemCount = IntCol(default = 1)
    countTest = IntCol(default = RPG_ITEMSET_TEST_GREATEREQUAL)
    
    def makeTest(self,count):
        if self.countTest == RPG_ITEMSET_TEST_GREATEREQUAL:
            if count >= self.itemCount:
                return True
        elif self.countTest == RPG_ITEMSET_TEST_EQUAL:
            if count == self.itemCount:
                return True
        else:
            if count <= self.itemCount:
                return True
        return False

class ItemSetPower(Persistent):
    name = StringCol(alternateID = True)
    
    harmful = BoolCol(default = False)
    
    requirementsInternal = MultipleJoin('ItemSetRequirement')
    statsInternal = MultipleJoin('ItemSetStat')
    # only RPG_ITEM_TRIGGER_WORN, RPG_ITEM_TRIGGER_MELEE or RPG_ITEM_TRIGGER_DAMAGED allowed
    spellsInternal = MultipleJoin('ItemSetSpell')
    
    #message when set power is activated
    message = StringCol(default = "")
    #sound when set power is activated
    sound = StringCol(default="")
    
    itemSetProtos = RelatedJoin("ItemSetProto")
    
    
    def _init(self,*args,**kw):
        Persistent._init(self,*args,**kw)
        self.requirements = self.requirementsInternal[:]
        self.stats = self.statsInternal[:]
        self.spells = self.spellsInternal[:]
    
    def removeMods(self,mob):
        for stat in self.stats:
            if stat.statname == "haste":
                mob.itemSetHastes.remove(stat.value)
                mob.calcItemHaste()
            elif stat.statname in RPG_RESISTSTATS:
                mob.resists[RPG_RESISTLOOKUP[stat.statname]] -= stat.value
            else:
                setattr(mob,stat.statname,getattr(mob,stat.statname)-stat.value)
        for spell in self.spells:
            if mob.itemSetSpells.has_key(spell.trigger):
                mob.itemSetSpells[spell.trigger].remove(spell)
    
    def updateDerived(self,mob):
        for stat in self.stats:
            if stat.statname in RPG_DERIVEDSTATS:
                setattr(mob,stat.statname,getattr(mob,stat.statname)+stat.value)
    
    def checkAndApply(self,mob,contributions,exists,printMessage=True):
        for req in self.requirements:
            if not contributions.has_key(req.name):
                return False
            if self.harmful:
                if not req.makeTest(contributions[req.name][0]):
                    return False
            # if not harmful check only item count without penalties
            elif not req.makeTest(contributions[req.name][1]):
                return False
        
        if exists:
            return True
        
        # passed all tests, start applying effects
        if mob.simObject and mob.player and printMessage:
            if self.message:
                mob.player.sendGameText(RPG_MSG_GAME_YELLOW,"%s\\n"%(self.message),mob)
            if self.sound:
                mob.playSound(self.sound)
        for stat in self.stats:
            if stat.statname == "haste":
                mob.itemSetHastes.append(stat.value)
                mob.calcItemHaste()
            elif stat.statname in RPG_RESISTSTATS:
                mob.resists[RPG_RESISTLOOKUP[stat.statname]] += stat.value
            else:
                setattr(mob,stat.statname,getattr(mob,stat.statname)+stat.value)
        for spell in self.spells:
            if mob.itemSetSpells.has_key(spell.trigger):
                mob.itemSetSpells[spell.trigger].append(spell)
            else:
                mob.itemSetSpells[spell.trigger] = [spell]
        return True

class ItemSetProto(Persistent):
    name = StringCol(alternateID = True)
    
    powersInternal = RelatedJoin('ItemSetPower')
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        self.powers = self.powersInternal[:]
    
    def updateDerived(self,mob):
        for power in self.powers:
            if power in mob.equipMods["%s"%self.name]:
                power.updateDerived(mob)
    
    def checkAndApply(self,mob,printMessage=True):
        thisSet = mob.itemSets[self]
        if thisSet[1]:    # something changed
            thisSet[1] = False
            
            if not len(thisSet[0]):
                for power in mob.equipMods["%s"%self.name].iterkeys():
                    power.removeMods(mob)
                del mob.equipMods["%s"%self.name]
                return
            
            if not mob.equipMods.has_key("%s"%self.name):
                mob.equipMods["%s"%self.name] = []
            for power in self.powers:
                exists = power in mob.equipMods["%s"%self.name]
                if power.checkAndApply(mob,thisSet[0],exists,printMessage):
                    if not exists:
                        mob.equipMods["%s"%self.name].append(power)
                elif exists:
                    power.removeMods(mob)
                    mob.equipMods["%s"%self.name].remove(power)
            return



def getTomeAtLevelForScroll(scroll,tomelevel):
    if not scroll or tomelevel < 2 or tomelevel > 10:
        traceback.print_stack()
        print "AssertionError: invalid attributes!"
        return
    item = scroll.createInstance("STUFF/38")
    item.spellEnhanceLevel = tomelevel
    spellname = scroll.spellProto.name
    item.name = "Tome of %s %s"%(spellname,RPG_ROMAN[tomelevel - 1])
    item.descOverride = "This tome contains secrets of the %s spell.  It can increase the reader's potency up to level %s in casting."%(spellname,RPG_ROMAN[tomelevel - 1])
    return item


