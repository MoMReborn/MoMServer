# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup character character
#  @ingroup world
#  @brief The character module provides persistent data types pertaining to
#         Player owned and controlled mobs (Characters).
#  @{


from mud.common.persistent import Persistent
from mud.world.advancement import AdvancementProto
from mud.world.archetype import GetClass
from mud.world.defines import *
from mud.world.item import ItemInstance,ItemProto
from mud.world.race import GetRace
from mud.world.shared.sounddefs import *
from mud.worlddocs.utils import GetTWikiName

from collections import defaultdict
from datetime import datetime
from math import floor
from random import randint
from sqlobject import *
import traceback



## @brief Persistent data type defining a list of starting items and the
#         requirements for the items to be given to a Character upon Character
#         creation.
class StartingGear(Persistent):

    # Attributes.
    ## @brief (Persistent String) Race, if any, required to receive the
    #         StartingGear.
    racename = StringCol(default="")
    ## @brief (Persistent String) Class, if any, required to receive the
    #         StartingGear.
    classname = StringCol(default="")
    ## @brief (Persistent String) Sex, if any, required to receive the
    #         StartingGear.
    sex = StringCol(default="")
    ## @brief (Persistent Integer) Realm required to receive the StartingGear.
    realm = IntCol()
    ## @brief (Persistent String) Comma delimited list of Item names.
    items = StringCol(default="")


    ## @brief Checks if a Spawn qualifies for the StartingGear.
    #  @param self (StartingGear) The object pointer.
    #  @param spawn (Spawn) The Spawn being tested for qualification.
    #  @return (Boolean) True if the Spawn qualifies for the StartingGear.
    #          Otherwise, False.
    def qualify(self, spawn):

        # If this StartingGear requires a race, then check if Spawn's race
        # matches.
        if self.racename and self.racename != spawn.race:
            # Return False as the Spawn did not qualify due race.
            return False

        # If this StartingGear requires a class, then check if Spawn's class
        # matches.
        if self.classname:
            if spawn.pclass.name != self.classname:
                # Return False as the Spawn did not qualify due to class.
                return False

        # If this StartingGear requires a sex, then check if Spawn's sex
        # matches.
        if self.sex and self.sex != spawn.sex:
            # Return False as the Spawn did not qualify due to sex.
            return False

        # If this StartingGear requires a realm, then check if this Spawn's
        # realm matches.
        if self.realm and self.realm != spawn.realm:
            # Return False as the Spawn did not qualify due to realm.
            return False

        # Return True as the Spawn qualifies for this StartingGear.
        return True


## @brief Persistent data type defining a Spell known by a Character.
class CharacterSpell(Persistent):

    # Attributes.
    ## @brief (Persistent Integer) Unique slot the Spell is scribed to within a
    #         SpellBook.
    #  @details 150 possible spell slots.  TWS: What defines this?
    slot = IntCol(default=0)
    ## @brief (Persistent Integer) Recast time, maybe?
    #  @deprecated Is this used?  If not, what should it be used for?
    #              Maybe handling recast times between zoning?
    recast = IntCol(default=0)
    ## @brief (Persistent Integer) The power level at which the Character knows
    #         the Spell.
    level = IntCol(default=1)

    # Relationships.
    ## @brief (Persistent Character) Character that knows the spell.
    character = ForeignKey('Character')
    ## @brief (Persistent SpellProto) Spell known by the Character.
    spellProto = ForeignKey('SpellProto')


    ## @brief Initializer delegates variable initialization to parent class.
    #  @param self (CharacterSpell) The object pointer.
    def _init(self, *args, **kw):

        Persistent._init(self, *args, **kw)

        ## @brief (CharSpellInfo) Stores handle to a CharSpellInfo object,
        #          observed by Client.
        self.spellInfo = None


## @brief Persistent data type defining a Skill known by a Character.
class CharacterSkill(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of skill known by the Character.
    skillname = StringCol()
    ## @brief (Persistent Integer) The power level at which the Character knows
    #         the Skill.
    level = IntCol(default = 1)

    # Relationships.
    ## @brief (Persistent Character) Character that knows the Skill.
    character = ForeignKey('Character')


## @brief Persistent data type defining the amount of times a Character has
#         choosen a DialogChoice.
class CharacterDialogChoice(Persistent):

    # Attributes.
    ## @brief (Persistent String) The choosen DialogChoice's identifier
    #         attribute.
    identifier = StringCol()
    ## @brief (Persistent Integer) Count of times a Character has choosen the
    #         DialogChoice.
    count = IntCol(default=1)

    # Relationships.
    ## @brief (Persistent Character) Character that has choosen the
    #         DialogChoice.
    character = ForeignKey('Character')


## @brief Persistent data type defining an Advancement purchased by a Character.
class CharacterAdvancement(Persistent):

    # Attributes.
    ## @brief (Persistent Integer)  The number of times the Advancemennt has
    #         been purchased by the Character.
    rank = IntCol(default = 1)

    # Relationships.
    ## @brief (Persistent AdvancementProto) The Advancement trained by the
    #         Character.
    advancementProto = ForeignKey('AdvancementProto')
    ## @brief (Persistent Character) The Character that has trained the
    #         Advancement.
    character = ForeignKey('Character')


    ## @brief Apply does nothing.
    #  @param self (CharacterAdvancement) The object pointer.
    #  @return None.
    #  @deprecated TWS: Is this used?  It does nothing but pass.
    def apply(self):
        pass


    ## @brief Remove does nothing.
    #  @param self (CharacterAdvancement) The object pointer.
    #  @return None.
    #  @deprecated TWS: Is this used?  It does nothing but pass.
    def remove(self):
        pass


## @brief Persistent data type defining an Item stored in a Character's private
#         vault (item storage unit).
class CharacterVaultItem(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of the Item.
    name = StringCol()
    ## @brief (Persistent Integer) The count of the items in the stack.
    stackCount = IntCol()

    # Relationships.
    ## @brief (Persistent Character) The Character who owns the Items.
    character = ForeignKey('Character')
    ## @brief (Persistent Item) The Item owned by the Character.
    item = ForeignKey('Item')


## @brief Persistent data type defining a Character's faction points/standing
#         for a Faction.
class CharacterFaction(Persistent):

    # Attributes.
    ## @brief (Persistent Integer) The Character's faction points for a Faction.
    #  @details The lower the points, the more the Character is disliked by the
    #           faction.
    points = IntCol(default = 0)

    # Relationships.
    ## @brief (Persistent Character) The Character who has points with the
    #         Faction.
    character = ForeignKey('Character')
    ## @brief (Persistent Faction) The Faction for whom the Character has
    #         points.
    faction = ForeignKey('Faction')


## @brief Persistent data type defining a Player owned and controlled mobs.
class Character(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of the Character.  This must be unique.
    name = StringCol(alternateID = True,default="")
    ## @brief (Persistent String) Surname for the Character.
    lastName = StringCol(default="")
    ## @brief (Persistent DateTime) Time of creation for the Character.
    creationTime = DateTimeCol(default = datetime.now)
    ## @brief (Persistent Integer) Total amount of experience for the
    #         Character's primary class.
    xpPrimary = IntCol(default = 0)
    ## @brief (Persistent Integer) Total amount of experience for the
    #         Character's secondary class.
    xpSecondary = IntCol(default = 0)
    ## @brief (Persistent Integer) Total amount of experience for the
    #         Character's tertiary class.
    xpTertiary = IntCol(default = 0)
    ## @brief (Persistent Integer) Amount of experience the Character's primary
    #         class lost from the most recent death.
    xpDeathPrimary = IntCol(default=0)
    ## @brief (Persistent Integer) Amount of experience the Character's
    #         secondary class lost from the most recent death.
    xpDeathSecondary = IntCol(default=0)
    ## @brief (Persistent Integer) Amount of experience the Character's tertiary
    #         class lost from the most recent death.
    xpDeathTertiary = IntCol(default=0)
    ## @brief (Persistent Integer) Amount of advancement points the Character
    #         has.
    advancementPoints = IntCol(default=0)
    ## @brief (Persistent Integer) Highest primary class level for which the
    #         Character has been rewarded advancement points.
    advancementLevelPrimary = IntCol(default=1)
    ## @brief (Persistent Integer) Highest secondary class level for which the
    #         Character has been rewarded advancement points.
    advancementLevelSecondary = IntCol(default=1)
    ## @brief (Persistent Integer) Highest tertiary class level for which the
    #         Character has been rewarded advancement points.
    advancementLevelTertiary = IntCol(default=1)
    ## @brief (Persistent String) Contains the file name (no extension) for
    #         the Character portait.
    portraitPic = StringCol()
    ## @brief (Persistent Boolean) Flag indicating if the Character is dead.
    dead = BoolCol(default = False)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase strength.
    strRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase strength.
    bdyRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase body.
    dexRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase dexterity.
    mndRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase mind.
    wisRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase wisdom.
    agiRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase agility.
    refRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amount of stat points by which the
    #         Character may permanently increase reflex.
    mysRaise = IntCol(default=300)
    ## @brief (Persistent Integer) The amout of health the Character currently
    #         has.
    health = IntCol(default=-999999)
    ## @brief (Persistent Integer) The amout of mana the Character currently
    #         has.
    mana = IntCol(default=-999999)
    ## @brief (Persistent Integer) The amout of stamina the Character currently
    #         has.
    stamina = IntCol(default=-999999)
    ## @brief (Persistent Boolean) Flag indicating if the Character's primary
    #         class may be changed.
    pchange = BoolCol(default=False)
    ## @brief (Persistent Boolean) Flag indicating if the Character's secondary
    #         class may be changed.
    schange = BoolCol(default=False)
    ## @brief (Persistent Boolean) Flag indicating if the Character's tertiary
    #         class may be changed.
    tchange = BoolCol(default=False)
    ## @brief (Persistent String) Transform storing the Character's most recent
    #         death position and rotation.
    deathTransformInternal = StringCol(default="0 0 0 1 0 0 0")

    # Relationships.
    ## @brief (Persistent Player) The Player who owns the Character.
    player = ForeignKey('Player')
    ## @brief (Persistent Spawn) The Spawn for the Character.
    spawn = ForeignKey('Spawn')
    ## @brief (Persistent CharacterSpell List) CharacterSpells belonging to the
    #         Character.
    spellsInternal = MultipleJoin('CharacterSpell')
    ## @brief (Persistent Item List) Items belonging to the Character.
    itemsInternal = MultipleJoin('Item')
    ## @brief (Persistent CharacterVaultItem List) CharacterVaultItems belonging
    #         to the Character.
    vaultItemsInternal = MultipleJoin('CharacterVaultItem')
    ## @brief (Persistent CharacterAdvancement List) CharacterAdvancements
    #         belonging to the Character.
    advancements = MultipleJoin('CharacterAdvancement')
    ## @brief (Persistent CharacterSkill List) CharacterSkills belonging to the
    #         Character.
    skills = MultipleJoin('CharacterSkill')
    ## @brief (Persistent CharacterDialogChoice List) CharacterDialogChoices
    #         belonging to the Character.
    characterDialogChoices = MultipleJoin('CharacterDialogChoice')
    ## @brief (Persistent CharacterFaction List) CharacterFactions belonging to
    #         the Character.
    characterFactions = MultipleJoin('CharacterFaction')
    ## @brief (Persistent SpellStore List) List of Spells needing reapplied to
    #         the Character.
    spellStore = MultipleJoin('SpellStore')
    ## @brief (Persistent Zone) Zone in which the Character's most recent death
    #         occured.
    deathZone = ForeignKey('Zone',default=None)


    ## @brief Initializer delegates variable initialization to parent class, and
    #         sets experience mods and percents.
    #  @param self (Character) The object pointer.
    def _init(self, *args, **kw):

        # Delegate variable initialization to parent class.
        Persistent._init(self, *args, **kw)

        ## @brief (Mob) The Mob for the Character.
        self.mob = None

        ## @brief (Float) Percent of experience that will be distributed to the
        #         primary class per experience gain.
        self.xpGainPrimary = 1.0

        ## @brief (Float) Percent of experience that will be distributed to the
        #         secondary class per experience gain.
        self.xpGainSecondary = 0

        ## @brief (Float) Percent of experience that will be distributed to the
        #         tertiary class per experience gain.
        self.xpGainTertiary = 0

        ## @brief (ItemInstance List) List of ItemInstances belonging to the
        #         Character.
        self.itemList = None

        ## @brief (Boolean) Flag indicating if the list of CharacterVaultItems
        #         is out of sync with the database and needs queried again.
        self.vaultItemsDirty = True

        ## @brief (CharacterVaultItem List) CharacterVaultItems belonging to the
        #         Character.
        #  @remarks The reassignment of vaultItemsInternal to vaultItemList
        #           prevents having to query the database when iterating over
        #           the Character's CharacterVaultItems.
        self.vaultItemList = None

        ## @brief (Boolean) Flag indicating if the list of CharacterSpells is
        #         out of sync with the database and needs queried again.
        self.spellsDirty = True

        ## @brief (CharacterSpell List) CharacterSpells belonging to the
        #         Character.
        #  @remarks The reassignment of spellsInternal to spellList prevents
        #           having to query the database when iterating over the
        #           Character's CharacterSpells.
        self.spellList = None

        ## @brief (Integer) Stores the former pet's heath.
        self.petHealthBackup = 0

        ## @brief (Integer) Timer value indicating how much longer till a new
        #         pet may be summoned with full health instead of the backup
        #         pet health value.
        self.petHealthTimer = -9999


        # Variables are initialized, so perform some initialization.

        # Calculate this Character's experience modifiers.
        self.setXPMods()

        # Calculate the percent of experience this Character has in each level.
        # This information will be used for filling the experience bar on the
        # client.
        self.calcXPPercents()

        # Check for newly exluding advancements.  This is should be done on each
        # initialization incase an advancement's exclusions are changed.
        # Otherwise, this Character may have newly excluding advancements
        # applied at the same time until this Character purchases a new
        # advancement.
        self.checkAdvancements()


    ## @brief Gets the Character's death transform.
    #  @param self (Character) The object pointer.
    #  @return (Float List) List of floats representing the Character's death
    #          transformation.
    def _get_deathTransform(self):
        # Death transform is stored as a string.  Convert the string of floats
        # seperated by spaces to a list of floats.
        return map(float, self.deathTransformInternal.split(" "))


    ## @brief Sets the Character's death transform.
    #  @param self (Character) The object pointer.
    #  @param transform (Float List) The Character's death transformation as a
    #                   list of floats.
    #  @return None.
    def _set_deathTransform(self, transform):
        # Death transform is stored as a string.  Convert a list of floats to a
        # string of floats seperated by spaces.
        ## @brief (Persistent String) Transform storing the Character's most
        #         recent death position and rotation.
        self.deathTransformInternal = ' '.join(map(str,transform))


    ## @brief Gets the Character's Items.
    #  @details Upon first call, this will
    #  @param self (Character) The object pointer.
    #  @return (ItemInstance List) List of ItemInstances belonging to the
    #          Character.
    #  @remarks The reassignment prevents having to query the database each
    #           time a Character's Items are checked.
    #  @todo TWS: If list is loaded only once, consider dynamic function
    #        remapping.
    #  @bug  TWS: Check if ethereal item handling is zone cluster friendly.
    def _get_items(self):

        # If itemList has not been initialized, then load the Items from the
        # database.
        if not self.itemList:

            # Empty list will store this ItemInstances created from this
            # Character's Items.
            self.itemList = []

            # Query the database for this Character's Items.  Iterate over the
            # result, populating itemList with ItemInstances created from
            # non-ethereal Items.
            for item in self.itemsInternal:

                # If the item is ethereal, then it should have never persisted.
                # As a precaution, destroy the Item.
                if item.itemProto.flags & RPG_ITEM_ETHEREAL:
                    item.destroySelf()

                    # Continue to the next item.
                    continue

                # Create an ItemInstance and append to the item list.
                self.itemList.append(ItemInstance(item))

        # Return the list of ItemInstances belonging to the Character.
        return self.itemList


    ## @brief Gets the Character's Private Vault Items.
    #  @param self (Character) The object pointer.
    #  @return (CharacterVaultItem List) List of CharacterVaultItem belonging to
    #          the Character.
    #  @remarks The reassignment prevents having to query the database each
    #           time a Character's CharacterVaultItem are checked.
    #  @todo TWS: non-dirty flag can move to if statement.  Consider
    #        dynamically rebind function instead of using a flag (saves each
    #        time get is called when in sync.  Also, consider if pulling
    #        from persistant layer is desired, might be best to push the
    #        changes in memory to keep in sync or maybe pull from memory.
    def _get_vaultItems(self):

        # If the list of CharacterVaultItems items is out of sync with the
        # database, then querty the database.
        if self.vaultItemsDirty:

            # Query the database for this Character's CharacterVaultItems, and
            # store the results in vaultItemList.
            self.vaultItemList = self.vaultItemsInternal

        # Vault items are in sync with the database.
        self.vaultItemsDirty = False

        # Return the list of vault items.
        return self.vaultItemList


    ## @brief Gets the Character's Spells.
    #  @param self (Character) The object pointer.
    #  @return (CharacterSpell List) List of CharacterSpell known by the
    #          Character.
    #  @remarks The reassignment prevents having to query the database each
    #           time a Character's CharacterSpells are checked.
    #  @todo TWS: non-dirty flag can move to if statement.  Consider
    #        dynamically rebind function instead of using a flag (saves each
    #        time get is called when in sync.  Also, consider if pulling
    #        from persistant layer is desired, might be best to push the
    #        changes in memory to keep in sync or maybe pull from memory.
    def _get_spells(self):

        # If the list of CharacterSpells is out of sync with the database, then
        # query the database.
        if self.spellsDirty:

            # Query the database for this Character's CharacterSpells, and
            # store the results in spellList.
            self.spellList = self.spellsInternal

        # Character spells are in sync with the database.
        self.spellsDirty = False

        # Return the list of known spells.
        return self.spellList


    ## @brief Refresh all ItemInstances owned by this Character based on
    #         current values.
    #  @remarks This is generally called when a Character attribute that
    #           affects item stats, such as level, changes.
    #  @param self (Character) The object pointer.
    #  @return None.
    def refreshItems(self):
        
        # List that will hold the items in the pet slots.
        petItems = []

        # Iterate over items belonging to the Character.
        for item in self.items:

            # Items equiped by pet are handled in a seperate method.
            if not (RPG_SLOT_PET_END > item.slot >= RPG_SLOT_PET_BEGIN):

                # Refresh the item, updating the item's stats based on the
                # ItemProto and current penalty.
                item.refreshFromProto()
            
            # Otherwise add this item to the pet item list.
            else:
                petItems.append(item)

        # Refresh items equiped in pet slots.
        self.refreshPetItems(petItems)

        # Flag the Player as having a dirty Character.  This will have the
        # ZoneInstance send a full CharacterInfo refresh to the Player.
        self.player.cinfoDirty = True


    ## @brief Creates Database backend for all ItemInstances owned by a Character.
    #  @param self (Character) The object pointer.
    #  @return None.
    def backupItems(self):

        # For all ItemInstances owned by this Character, store to a persistent
        # Item.
        map(ItemInstance.storeToItem, self.items)


    ## @brief Train an RPG-cass for the Character's Spawn.
    #  @param self (Character) The object pointer.
    #  @param klass (String) Name of the RPG-class being trained.
    #  @return None.
    #  @todo TWS: Should this be a little safer?  Calling multiple times
    #        would reset tertiary.  Dynamic function rebinding could be
    #        done, but it may be too excessive and confusing.  This method
    #        should not be getting called much anyways.
    def trainClass(self, klass):

        # Get the Character's Spawn.
        spawn = self.spawn

        # If the Spawn does not have a secondary level, then the Character
        # has not trained in a secondary class.
        if not spawn.slevel:

            # Set the Spawn's secondary to the class being trained.
            spawn.slevel = 1
            spawn.sclassInternal = klass

        # Otherwise, the Spawn has a secondary and is training a tertiary
        else:
            spawn.tlevel = 1
            spawn.tclassInternal = klass

        # The new class may an associated experience modifier, so update
        # experience modifiers.
        self.setXPMods()

        # The newly trained class needs its experience display percent
        # calculated.
        self.calcXPPercents()

        # The mob needs updated since the level change.  This will update
        # stats, items, and provide updates to the Player.
        self.mob.levelChanged()


    ## @brief Sets experience distribution valules.
    #  @param self (Character) The object pointer.
    #  @param pgain (Float) Percent of experience distributed to primary class.
    #  @param sgain (Float) Percent of experience distributed to secondary
    #               class.
    #  @param tgain (Float) Percent of experience distributed to tertiary class.
    #  @return None.
    #  @todo TWS: Are there any limitations on experience distribution that
    #        could be set here instead of checked during experience
    #        distribution?
    def setXPGain(self, pgain, sgain, tgain):

        # Update this Character's experience distribution values.
        self.xpGainPrimary = pgain
        self.xpGainSecondary = sgain
        self.xpGainTertiary = tgain

        # For safety, if this Character's Spawn has not trained a secondary
        # class, set the secondary experience gain to 0.
        if not self.spawn.sclassInternal:
            self.xpGainSecondary = 0.0

        # For safety, if this Character's Spawn has not trained a tertiary
        # class, set the tertiary experience gain to 0.
        if not self.spawn.tclassInternal:
            self.xpGainTertiary = 0.0


    ## @brief Sets experience modifiers for the Character.
    #  @param self (Character) The object pointer.
    #  @return None.
    #  @todo TWS: Consider reworking some statements to if/else instead of
    #        none/if.
    def setXPMods(self):
        
        # Set default experience modifiers.

        ##  @brief (Float) Modifier for primary experience gains.
        self.pxpMod = 1.0 # Is this required?  It gets recalculated each time
                          # afterwards.
        ##  @brief (Float) Modifier for secondary experience gains.
        self.sxpMod = 1.0
        ##  @brief (Float) Modifier for tertiary experience gains.
        self.txpMod = 1.0

        # Get the Character's Spawn.
        spawn = self.spawn

        # Get the Race based on the Character's Spawn.
        race = GetRace(self.spawn.race)

        # Get Classes.
        pclass = GetClass(spawn.pclassInternal)

        if spawn.sclassInternal:
            sclass = GetClass(spawn.sclassInternal)
            if spawn.tclassInternal:
                tclass = GetClass(spawn.tclassInternal)
            else:
                tclass = None
        else:
            sclass = None
            tclass = None

        # Update experience modifier based on the race.
        xpmod = race.getXPMod() - 1.0

        # Update experience modifiers per (TWS: what word?) based on
        # the RPG-class.
        self.pxpMod = 1.0 + xpmod + (pclass.getXPMod()-1.0)
        if sclass:
            self.sxpMod = 1.0 + xpmod + (sclass.getXPMod()-1.0)
            if tclass:
                self.txpMod = 1.0 + xpmod + (tclass.getXPMod()-1.0)


    ## @brief Calculates percent of experience a Character currently has gained
    #         compared to the amount of experience required to level for each
    #         trained RPG-class.
    #  @param self (Character) The object pointer.
    #  @return None.
    #  @todo TWS: Consider sending client both current and required experience.
    #         This allows for percent calculations to be pushed to client, and
    #         alows for raw numbers to display on client, as it has been requested
    #         a few times.  Is this something we may want to do?
    #  @todo TWS: What was causing None to be set for the levels?  Should try to
    #        find where this is occuring, or even if it is still occuring.
    #  @todo TWS: This is called a bit, and it calculates the same values each
    #        time.  It seems unnecessary, and previous needed and current needed
    #        could be recalculated only level change.  Calculate on start and
    #        change, store in a class attribute so it does not go out of scope.
    def calcXPPercents(self):

        # TWS: Consider adding as a remark to method description.
        # Percents are calculated by:
        #   expNeeded = experience needed for current level.
        #   totaExpNeeded = tota experience needed for current level.
        #   totalExpPreviouslyNeeded = total experience needed for previous
        #                              level
        #   currentTotalExp = total experience a player currently has.
        #   currentExp = experience a player currently has in a level.
        #
        #   expNeeded = totalExpNeeded - totalExpPreviouslyNeeded
        #   currentExp = currentTotaExp - totalExpPreviouslyNeeded
        #   percent = currentExp / expNeeded

        # Get the Character's Spawn.
        spawn = self.spawn

        # Set default percent to 0.
        self.pxpPercent = 0
        self.sxpPercent = 0
        self.txpPercent = 0

        # For safety, set primary Spawn level to be of an integer type.
        # Previous Note: This happened on the server when I was doing an
        # update, odd
        if spawn.plevel == None:
            spawn.plevel = 1

        # Calculate percent of experience each class has in its current level.
        
        # Calculate total experience needed to level in primary class.
        pneeded = spawn.plevel * spawn.plevel * 100L * self.pxpMod
        
        # Calculate the previous level's total experience needed to level in
        #  primary class.
        pprevneeded = ((spawn.plevel - 1) * (spawn.plevel - 1) * 100L * self.pxpMod)

        ## @brief (Float) The percent of experience the primary class has in
        #         the current level.
        self.pxpPercent = (self.xpPrimary - pprevneeded) / (pneeded - pprevneeded)

        # If the Spawn has a secondary level, then calculate the secondary
        # percent.
        if spawn.slevel:
        
            # Calculate total experience needed to level in secondary class.
            sneeded = spawn.slevel * spawn.slevel * 100L * self.sxpMod
            
            # Calculate the previous level's total experience needed to level in
            #  secondary class.
            sprevneeded = ((spawn.slevel - 1) * (spawn.slevel - 1) * 100L * self.sxpMod)

            ## @brief (Float) The percent of experience the secondary class has
            #         in the current level.
            self.sxpPercent = (self.xpSecondary - sprevneeded) / (sneeded - sprevneeded)

            # If the Spawn has a tertiary level, then calculate the tertiary
            # percent.
            if spawn.tlevel:
        
                # Calculate total experience needed to level in tertiary class.
                tneeded = spawn.tlevel * spawn.tlevel * 100L * self.txpMod
                
                # Calculate the previous level's total experience needed to level in
                #  tertiary class.
                tprevneeded = ((spawn.tlevel - 1) * (spawn.tlevel - 1) * 100L * self.txpMod)

                ## @brief (Float) The percent of experience the tertiary class has
                #         in the current level.
                self.txpPercent = (self.xpTertiary - tprevneeded) / (tneeded - tprevneeded)


    ## @brief Increase a level.
    #  @param self (Character) The object pointer.
    #  @param which (Integer) Specifies if the level gained was for primary,
    #               secondary, or tertiary.
    #  @return None.
    #  @remarks This is used for the Immortal command.
    def gainLevel(self, which):

        # Get the Character's Spawn.
        spawn = self.spawn

        # If the World is a demo build and the Player is not a premium Player,
        # then limit the Player.
        if RPG_BUILD_DEMO and not self.player.premium:

            # If primary is already at demo limit, then return early.
            if which == 0 and spawn.plevel >= RPG_DEMO_PLEVEL_LIMIT:
                return

            # If secondary is already at demo limit, then return early.
            if which == 1 and spawn.slevel >= RPG_DEMO_SLEVEL_LIMIT:
                return

            # If tertiary is trying to gain a level, then return early.
            # Non-premium players cannot train or level a tertiary class.
            if which == 2:
                return

        # If primary is being leveled, then set primary experience to the amount
        # of experience needed plus one.
        if which == 0:
            self.xpPrimary = int(spawn.plevel * spawn.plevel * 100L * self.pxpMod + 1)

        # If secondary is being leveled, then set secondary experience to the
        # amount of experience needed plus one.
        elif which == 1:
            self.xpSecondary = int(spawn.slevel * spawn.slevel * 100L * self.sxpMod + 1)

        # If tertiary is being leveled, then set tertiary experience to the
        # amount of experience needed plus one.
        elif which == 2:
            self.xpTertiary = int(spawn.tlevel * spawn.tlevel * 100L * self.txpMod + 1)

        # Call gainXP to trigger the actual leveling and cleanly handle refresh
        #  of experience display, gain of advancement points, stats and calculate
        #  new penalties.
        self.gainXP(10)


    ## @brief Distributes experience based on Player's settings to the Character.
    #  @param self (Character) The object pointer.
    #  @param amount (Integer) The total experience being distributed.
    #  @param clamp (Boolean) Indicates if experience rewarded is limited.
    #  @param rez (Tuple Integer) Provides the amount of experience being
    #             recovered from a ressurection for primary, secondary, and
    #             tertiary.
    #  @param clampAdjust (Float) Amount to adjust clamp.  (TWS: needs more detail)
    #  @return None.
    #  @todo TWS: It looks like it would be easier and safer to make clampAdjust
    #        be treated as the entire clamp, and just set a default to .1 (10%
    #        of the expeirnece required for level).  This prevents a divide by
    #        zero possibility and makes the math and usage much easier.
    #  @todo TWS: Again, lots of values getting recalculated each time this is
    #        called, but the values only change if the mob leveled.  Store it as
    #        a non-persistent class attribute!
    #  @todo TWS: Check if it is easier to assign, then if/assign vs.
    #        if/assign/else/assign.
    #  @todo TWS: More redundant calculations.  The mutator for xpGainClass
    #        should enforce the 100% rule.  No need to re-enforce each
    #        time!  If needed push some of it to client, but validate and
    #        send valiation back to client.  This would make sliders easier
    #        to understand.
    #  @todo TWS: A lot of calculations occur even if it is a rez!  Rez
    #        experience distrubtion is provided, the gains do not need
    #        calculated.
    #  @todo TWS: Experience required for a level is calculated even if clamp is
    #        not going to occur.
    def gainXP(self, amount, clamp=True, rez=None, clampAdjust=0):

        # Make a local reference to this Character's Spawn.
        spawn = self.spawn

        # Make a local reference to this Character's Mob.
        mob = self.mob

        # Total experience percent is 100%.
        total = 1.0

        # Reduce the total percent by the percent primary is receiving.
        pgain = self.xpGainPrimary
        total -= pgain

        # Total should never go below 0.  If the total percent remaining is
        # below 0, then clamp it to 0.
        if total < 0.0:
            total = 0.0

        # If the secondary is set to get a higher percent distribution than
        # what remains from the total, then set it so that the secondary will
        # only gain the remaining tota.
        sgain = self.xpGainSecondary
        if sgain > total:
            sgain = total

        # Reduce the remaining total percent by the percent the secondary is
        # receiving.
        total -= sgain

        # Total should never go below 0.  If the total percent remaining is
        # below 0, then clamp it to 0.
        if total < 0.0:
            total = 0.0

        # If the tertiary is set to get a higher percent distribution than what
        # remains from the total, then set it so that the tertiary will only
        # gain the remaining tota.
        tgain = self.xpGainTertiary
        if tgain > total:
            tgain = total

        # Reduce the remaining total percent by the percent the secondary is
        # receiving.
        total -= tgain
        
        # Total should never go below 0.  If the total percent remaining is
        # below 0, then clamp it to 0.
        if total < 0.0:
            total = 0.0

        # If all the experience percent was not distributed, then attempt to
        # distribute the remaining to the slot with the highest percent already.
        if total:

            # TWS: Optimize to max maybe?  Or redo it so that 100% is accounted
            # for beforehand.
            if self.xpGainPrimary >= self.xpGainSecondary and self.xpGainPrimary >= self.xpGainTertiary:
                pgain += total
            elif self.xpGainSecondary >= self.xpGainPrimary and self.xpGainSecondary >= self.xpGainTertiary:
                sgain += total
            elif self.xpGainTertiary >= self.xpGainPrimary and self.xpGainTertiary >= self.xpGainSecondary:
                tgain += total
            else:
                pgain += total

        # If the spawn has not trained a secondary cass, then set the secondary
        # gain to 0.
        if not spawn.slevel:
            sgain = 0.0

        # If the spawn has not trained a tertiary cass, then set the tertiary
        # gain to 0.
        if not spawn.tlevel:
            tgain = 0.0

        # msg is used to prevent sending multiple demo limit messages to a
        # Player.
        # TWS: This should probaby move inside the demo build if statement.
        msg = False

        # If the World is a demo build and the Player is not a premium Player,
        # then limit the Player.
        if RPG_BUILD_DEMO and not self.player.premium:

            # If the Player is set to gain experience for primary but has
            # reached the demo primary level limit, then attempt to set the
            # secondary class to receive the experience.
            if spawn.plevel >= RPG_DEMO_PLEVEL_LIMIT and pgain:

                # If the Player has trained in a secondary but has not reached
                # the demo seconary level limit, then set the secondary class to
                # receive the experience.
                if spawn.slevel > 0 and spawn.slevel < RPG_DEMO_SLEVEL_LIMIT:

                    # Take the percent of experience primary was receiving, and
                    # add it to secondary.
                    sgain += pgain

                    # Make sure secondary does not receive more than 100% of
                    # the experience being distributed.
                    if sgain > 1.0:
                        sgain = 1.0

                # Set primary to gain no experience.
                pgain = 0

                # Inform player that the demo primary cap has been reached.
                msg = True
                self.player.sendGameText(RPG_MSG_GAME_DENIED,"\\n%s has reached primary level %i and can gain more experience by training in a secondary class or purchasing the Minions of Mirth: Premium Edition.  The Premium Edition will also allow %s to use premium gear and multiclass in a third class to level 100!  Please see www.prairiegames.com for more information.\\n\\n"%(self.spawn.name, RPG_DEMO_PLEVEL_LIMIT, self.spawn.name))


            # If the Player is set to gain experience for secondary but has
            # reached the demo secondary level limit, then attempt to set the
            # primary class to receive the experience and set secondary to gain
            # no experience.
            if spawn.slevel >= RPG_DEMO_SLEVEL_LIMIT and sgain:

                # If the Player has not reached the demo primary level limit,
                # then set the primary class to receive the experience.
                if spawn.plevel < RPG_DEMO_PLEVEL_LIMIT:

                    # Take the percent of experience secondary was receiving,
                    # and add it to primary.
                    pgain+=sgain

                    # Make sure primary does not receive more than 100% of
                    # the experience being distributed.
                    if pgain > 1.0:
                        pgain = 1.0

                # Set secondary to gain no experience.
                sgain = 0

                # If a message was not already sent about the primary level
                # being capped, then inform player that the demo secondary cap
                # has been reached.
                if not msg:
                    self.player.sendGameText(RPG_MSG_GAME_DENIED,"\\n%s has reached secondary level %i and can gain more experience by purchasing the Minions of Mirth: Premium Edition.  The Premium Edition will also allow %s to use premium gear and multiclass in a third class to level 100!  Please see www.prairiegames.com for more information.\\n\\n"%(self.spawn.name, RPG_DEMO_SLEVEL_LIMIT, self.spawn.name))

            # If primary and secondary are not gaining any experience, then the
            # Player has capped both classes at the demo level limit.  Exit
            # early.
            if not sgain and not pgain:
                return

        # If a secondary class has been trained, the secondary level is equal to
        # or greater than the primary level (secondary cannot exceed primary),
        # and the primary level is not 100 (lets players fill secondary at level
        # 100), then take the percent of experience secondary was receiving and
        # add it to primary.
        if spawn.sclass and spawn.slevel >= spawn.plevel and spawn.plevel != 100:
            pgain += sgain
            sgain = 0

        # If a tertiary class has been trained, the tertiary level is equal to
        # or greater than the secondary level (tertiary cannot exceed
        # secondary), and the tertiary level is not 100 (lets players fill
        # tertiary at level 100), then take the percent of experience tertiary
        # was receiving and add it to primary.
        # TWS: Should probably try to bump it up to secondary first, then
        #      primary?
        if spawn.tclass and spawn.tlevel >= spawn.slevel and spawn.slevel != 100:
            pgain += tgain
            tgain = 0

        # If it is a resurrection, then get amount of experience being recovered
        # by the ressurection.
        if rez:
            xpp,xps,xpt = rez

        # Otherwise, it was not a resurrection, and experience should be
        # distributed based on the calculated distribution rates.
        else:

            # Calculate unclamped experience amount for primary.
            xpp = amount * pgain

            # Calculate unclamped experience amount for secondary.  Secondary
            # experience recives a 50% penalty.
            xps = amount * sgain / 2

            # Calcualte unclamped experience amount for tertiary.  Tertiary
            # experience recives a 67% penalty.
            xpt = amount * tgain / 3

            # TWS: Is this actually useful?  It looks like this always remains
            # a constant of 1.0.
            xpp *= mob.xpScalar
            xps *= mob.xpScalar
            xpt *= mob.xpScalar


        # Calculate total experience needed to level for each class.
        pneeded = spawn.plevel*spawn.plevel*100L*self.pxpMod
        sneeded = spawn.slevel*spawn.slevel*100L*self.sxpMod
        tneeded = spawn.tlevel*spawn.tlevel*100L*self.txpMod

         # Calculate how much experience is required to level each class.
        pgap = pneeded - ((spawn.plevel-1)*(spawn.plevel-1)*100L*self.pxpMod)
        sgap = sneeded - ((spawn.slevel-1)*(spawn.slevel-1)*100L*self.sxpMod)
        tgap = tneeded - ((spawn.tlevel-1)*(spawn.tlevel-1)*100L*self.txpMod)

        # If a clamp is true, then clamp experience based on the amount of
        # experience required to level.
        if clamp:

            # Calculate clamp adjustement.
            clampAdjust = 1.0 - clampAdjust

            # Modify clamp divisors.
            # TWS: Same value for all levels, just calculate once?
            pdiv = 10 / clampAdjust
            sdiv = 10 / clampAdjust
            tdiv = 10 / clampAdjust

            # If the primary experience being earned is greater than the clamped
            # value, then set primary experience being earned to the clamped
            # value.
            if xpp > pgap/pdiv:
                xpp = pgap/pdiv

            # If secondary experience is being earned, then check if secondary
            # needs clamp.
            if xps:
                # If the secondary experience being earned is greater than the
                # clamped value, then set secondary experience being earned to
                # the clamped value.
                if xps > sgap/sdiv:
                    xps = sgap/sdiv

            # If tertiary experience is being earned, then check if tertiary
            # needs clamped.
            if xpt:
                # If the tertiary experience being earned is greater than the
                # clamped value, then set tertiary experience being earned to
                # the clamped value.
                if xpt > tgap/tdiv:
                    xpt = tgap/tdiv

        # Round each experience gain to an integer.
        xpp = int(floor(xpp))
        xps = int(floor(xps))
        xpt = int(floor(xpt))

        # Flag used to indicate experience was adjusted and display percents
        # need recalculated.
        calc = False

        # If this Character has a class at the max level, and the experience
        # the class is earning would put the class above the experience amount
        # needed to leve, then set the class's experience to be one below the
        # experience needed to level.  This is done because being at or above
        # the experience needed is the condition for increasing in a level.
        # TWS: Some of this just looks awkward.  Experience gets recalculated
        #      even if the class is capped.

        # If the primary class exceeds the cap, then clamp the primary class
        # level and experience.
        if spawn.plevel == 100 and self.xpPrimary + xpp >= pneeded:
            self.xpPrimary = int(pneeded)-1
            xpp = 0
            calc = True

        # If the secondary class exceeds the cap, then clamp the secondary
        # class level and experience.
        if spawn.slevel == 100 and self.xpSecondary + xps >= sneeded:
            self.xpSecondary = int(sneeded)-1
            xps = 0
            calc = True

        # If the tertiary class exceeds the cap, then clamp the tertiary
        # class level and experience.
        if spawn.tlevel == 100 and self.xpTertiary + xpt >= tneeded:
            self.xpTertiary = int(tneeded)-1
            xpt = 0
            calc = True

        # If all three classes are not receiving experience, then return early.
        if not xpp and not xps and not xpt:

            # If a class gained experience, but was adjusted due to a cap, then
            # update percents.
            if calc:
                self.calcXPPercents()

            # Return early.
            return

        # Reward the experience to this Character.
        self.xpPrimary += xpp
        self.xpSecondary += xps
        self.xpTertiary += xpt


        # Generate experience gain message based on the classes that gained
        # experience.
        text = []
        if xpp:
            text.append("%i primary"%xpp)
        if xps:
            text.append("%i secondary"%xps)
        if xpt:
            text.append("%i tertiary"%xpt)
        text = "%s gained %s xp!\\n"%(self.name, ', '.join(text))

        # Send experience gain message to the Player.
        self.player.sendGameText(RPG_MSG_GAME_GAINED,text)


        # Flag used to indicate if a level was gained.
        gained = False

        # If this Character's primary level is below the cap, and the updated
        # experience is greater or equal to the amount needed, then a level was
        # gained.
        if spawn.plevel < 100:
            if self.xpPrimary >= pneeded:

                # Increase the spawn and mob's primary level.
                spawn.plevel += 1
                mob.plevel += 1

                # Set the level gain flagged.
                gained = True

                # TWS: These variables should be inside the if statement.
                advance = False
                points = 0
                totalPoints = 0

                # Calculate the differnce in spawn's primary level and this
                # Character's advancement primary level.
                advDiff = spawn.plevel - self.advancementLevelPrimary

                # A positive value indicates the primary level gained is a new
                # level and not a previously gained level.  If a new level was
                # gained, then advancement points need rewarded.    
                if advDiff > 0:

                    # Set a flag indicating an advancement was gained.
                    # TWS: Why is this used, the "send a message" when gained
                    # should be in this entire if statement.
                    advance = True
                    
                    #from cserveravatar import AVATAR
                    #if cserveravatar.AVATAR:
                    #    cserveravatar.AVATAR.doContestLevelUp( \
                    #        self.player,"primary",spawn.plevel)

                    # Iterate over the amount of levels for which advancement
                    # points are to be rewarded.
                    # TWS: Why iterate?  Just having it in the formulas may be
                    # faster.
                    for i in xrange(advDiff):

                        # Increase the primary advancement level.
                        self.advancementLevelPrimary += 1

                        # Calculate how many points to reward for the level.
                        points = int(float(spawn.plevel - i) / 2.0)

                        # If the points beind rewarded is below 5, then clamp
                        # the points to be at least 5.
                        if points < 5:
                            points = 5

                        # Add the rewarded points to the Character.
                        self.advancementPoints += points
                        totalPoints += points

                # Play sound for Player.
                self.player.mind.callRemote("playSound","sfx/Pickup_Magic02.ogg")

                # Get this Character's primary class name.
                pclassName = spawn.pclassInternal

                # If advancements were rewarded to the Player, then inform the
                # Player.
                if advance:
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s is now a level %i <a:Class%s>%s</a>!!!\\n"%(self.name,spawn.plevel,GetTWikiName(pclassName),pclassName.lower()))
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s has gained %i advancement points!!!\\n"%(self.name,totalPoints))

                    # If the player has unlocked the ability to multiclass, then
                    # send a message to the Player.
                    if RPG_MULTICLASS_SECONDARY_LEVEL_REQUIREMENT == spawn.plevel and not spawn.slevel:
                        self.player.sendGameText(RPG_MSG_GAME_GAINED,"%s can now train in a secondary class.\\n"%(self.name))
                    elif RPG_MULTICLASS_TERTIARY_LEVEL_REQUIREMENT == spawn.plevel and not spawn.tlevel:
                        self.player.sendGameText(RPG_MSG_GAME_GAINED,"%s can now train in a tertiary class.\\n"%(self.name))

                # The Character regained a primary class level.
                else:
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s has regained a primary level!!! (<a:Class%s>%s</a>, %i)\\n"%(self.name,GetTWikiName(pclassName),pclassName.lower(),spawn.plevel))


        # If this Character's secondary level is below the cap, and the updated
        # experience is greater or equal to the amount needed, then a level was
        # gained.
        if spawn.sclass and spawn.slevel < spawn.plevel:
            if self.xpSecondary >= sneeded:

                # Increase the spawn and mob's secondary level.
                spawn.slevel += 1
                mob.slevel += 1

                # Set the level gain flagged.
                gained = True

                # TWS: These variables should be inside the if statement.
                advance = False
                points = 0
                totalPoints = 0

                # Calculate the differnce in spawn's secondary level and this
                # Character's advancement secondary level.
                advDiff = spawn.slevel - self.advancementLevelSecondary

                # A positive value indicates the secondary level gained is a new
                # level and not a previously gained level.
                if advDiff > 0:
                    
                    #from cserveravatar import AVATAR
                    #if cserveravatar.AVATAR:
                    #    cserveravatar.AVATAR.doContestLevelUp( \
                    #        self.player,"secondary",spawn.slevel)

                    # Set a flag indicating an advancement was gained.
                    # TWS: Why is this used, the "send a message" when gained
                    # should be in this entire if statement.
                    advance = True

                    # Iterate over the amount of levels for which advancement
                    # points are to be rewarded.
                    # TWS: Why iterate?  Just having it in the formulas may be
                    # faster.
                    for i in xrange(advDiff):

                        # Increase the secondary advancement level.
                        self.advancementLevelSecondary += 1

                        # Calculate how many points to reward for the level.
                        points = int(float(spawn.slevel - i) / 2.0)

                        # If the points beind rewarded is below 3, then clamp
                        # the points to be at least 3.
                        if points < 3:
                            points = 3

                        # Add the rewarded points to the Character.
                        self.advancementPoints += points
                        totalPoints += points

                # Play sound for Player.
                self.player.mind.callRemote("playSound","sfx/Pickup_Magic02.ogg")

                # Get this Character's secondary class name.
                sclassName = spawn.sclassInternal

                # If advancements were rewarded to the Player, then inform the
                # Player.
                if advance:
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s's secondary class of <a:Class%s>%s</a> is now level %i!!\\n"%(self.name,GetTWikiName(sclassName),sclassName.lower(),spawn.slevel))
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s has gained %i advancement points!!!\\n"%(self.name,totalPoints))

                # The Character regained a secondary class level.
                else:
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s has regained a secondary class level! (<a:Class%s>%s</a>, %i)!!\\n"%(self.name,GetTWikiName(sclassName),sclassName.lower(),spawn.slevel))


        # If this Character's tertiary level is below the cap, and the updated
        # experience is greater or equal to the amount needed, then a level was
        # gained.
        if spawn.tclass and spawn.tlevel < spawn.slevel:
            if self.xpTertiary >= tneeded:

                # Increase the spawn and mob's tertiary level.
                spawn.tlevel += 1
                mob.tlevel += 1

                # Set the level gain flagged.
                gained = True

                # TWS: These variables should be inside the if statement.
                advance = False
                points = 0
                totalPoints = 0

                # Calculate the differnce in spawn's tertiary level and this
                # Character's advancement secondary level.
                advDiff = spawn.tlevel - self.advancementLevelTertiary

                # A positive value indicates the tertiary level gained is a new
                # level and not a previously gained level.
                if advDiff > 0:
                    
                    #from cserveravatar import AVATAR
                    #if cserveravatar.AVATAR:
                    #    cserveravatar.AVATAR.doContestLevelUp( \
                    #        self.player,"tertiary",spawn.tlevel)


                    # Set a flag indicating an advancement was gained.
                    # TWS: Why is this used, the "send a message" when gained
                    # should be in this entire if statement.
                    advance = True

                    # Iterate over the amount of levels for which advancement
                    # points are to be rewarded.
                    # TWS: Why iterate?  Just having it in the formulas may be
                    # faster.
                    for i in xrange(advDiff):
                        self.advancementLevelTertiary += 1

                        # Calculate how many points to reward for the level.
                        points = int(float(spawn.tlevel - i) / 2.0)

                        # If the points beind rewarded is below 1, then clamp
                        # the points to be at least 1.
                        if points < 1:
                            points = 1

                        # Add the rewarded points to the Character.
                        self.advancementPoints += points
                        totalPoints += points

                # Play sound for Player.
                self.player.mind.callRemote("playSound","sfx/Pickup_Magic02.ogg")

                # Get this Character's tertiary class name.
                tclassName = spawn.tclassInternal

                # If advancements were rewarded to the Player, then inform the
                # Player.
                if advance:
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s's tertiary class of <a:Class%s>%s</a> is now level %i!!\\n"%(self.name,GetTWikiName(tclassName),tclassName.lower(),spawn.tlevel))
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s has gained %i advancement points!!!\\n"%(self.name,totalPoints))

                # The Character regained a tertiary class level.
                else:
                    self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,"%s has regained a tertiary level!!! (<a:Class%s>%s</a>, %i)\\n"%(self.name,GetTWikiName(tclassName),tclassName.lower(),spawn.tlevel))


        # This Character gained experience, so update display percents.
        self.calcXPPercents()

        # If a level was gained, then update the Mob.
        if gained:
            mob.levelChanged()


    ## @brief Swaps spells slots, if any, in a Character's spell book.
    #  @param self (Character) The object pointer.
    #  @param srcslot (Integer) The source slot clicked.
    #  @param dstslot (Integer) The destination slot clicked.
    #  @return None.
    #  @todo TWS: The spells list gets iterated over twice.  It may be better
    #        to iterate over once, checking for both conditions.
    def onSpellSlotSwap(self, srcslot, dstslot):
        
        # If source and destination slots are the same, return early.
        if srcslot == dstslot:
            return

        # Handle to the source spell.
        srcspell = None

        # Iterate over the Character's spells.
        for spell in self.spells:

            # If the spell's slot matches the source slot, then store a handle
            # to the source spell and exit the loop.
            if spell.slot == srcslot:
                srcspell = spell
                break


        # Handle to the destination spell.
        dstspell = None

        # Iterate over the Character's spells.
        for spell in self.spells:

            # If the spell's slot matches the destination slot, then store a
            # handle to the destination spell and exit the loop.
            if spell.slot == dstslot:
                dstspell = spell
                break

        # If there is a source spell, then set the destination slot to the
        # source spell's slot.
        if srcspell:
            srcspell.slot = dstslot

        # If there is a destination spell, then set the source slot to the
        # destination spell's slot.
        if dstspell:
            dstspell.slot = srcslot


    ## @brief Cast a spell or scribe a spell when a spell slot is clicked.
    #  @param self (Character) The object pointer.
    #  @param slot (Integer) Slot that is being activated.
    #  @param item (ItemInstance) ItemInstance being checked.  TWS: needs
    #              better description.
    #  @return None.
    #  @todo TWS: The spells list gets iterated over twice.  It may be better
    #        to iterate over once, checking for both conditions.
    def onSpellSlot(self, slot, item=None):

        # Iterate over this Character's spells.
        for spell in self.spells:

            # If a spell was found that matches slots, then check if this
            # Character can cast.
            if spell.slot == slot:

                # Get the SpellProto.
                sProto = spell.spellProto

                # If this Character qualifies for the spell, then begin casting.
                if sProto.qualify(self.mob):
                    self.mob.cast(sProto, spell.level)

                # Otherwise, this Character has the spell but cannot cast the
                # spell.
                else:
                    self.player.sendGameText(RPG_MSG_GAME_DENIED, r'%s does not know how to cast <a:Spell%s>%s</a>.\n'%(self.name,GetTWikiName(sProto.name),sProto.name))

                # Return early.
                return

        # If no item is provided, then use the item on the Player's cursor.
        if not item:
            item = self.player.cursorItem

            # If there is no item on cursor, then return early.
            if not item:
                return

        # If a tome was clicked on a spell, then return early.
        if item.spellEnhanceLevel:
            return

        # If there is no SpellProto, then the item on the cursor is not a spell
        # scroll, so return early.
        spellToLearnProto = item.itemProto.spellProto
        if not spellToLearnProto:
            return

        # Trying to learn spell.
        # TWS: All spells were iterated over early, maybe this check can occur
        # during those iterations?  It may be best to keep the cast code to
        # be as optimized as possible though.
        # Iterate over this Character's spells.
        for characterSpell in self.spells:

            # If this Character already knows the spell, then send a message to
            # the Player and return early.
            if spellToLearnProto == characterSpell.spellProto:
                self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s already knows this spell!\n'%self.name)
                return

        # If this Character does not qualify for the spell, then send a message
        # to the Player and return early.
        if not spellToLearnProto.qualify(self.mob):
            self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot learn <a:Spell%s>%s</a> at this time.\n'%(self.name,GetTWikiName(spellToLearnProto.name),spellToLearnProto.name))
            return

        # Character can learn spell, so create a CharacterSpell.
        CharacterSpell(character=self,spellProto=spellToLearnProto,slot=slot,recast=0)

        # Flag spels at dirty so they will be reloaded on next access.
        self.spellsDirty = True

        # Item was used, so update the stack count.
        item.stackCount -= 1

        # If the stack count is zero or below, then consume the item.
        if 0 >= item.stackCount:

            # Take the item.
            item.destroySelf()

        # Otherwise, the stack still has items.
        else:

            # Refresh ItemInfo so observing clients see the new stack count.
            item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})

        # Send a sound and message to the Player.
        self.player.mind.callRemote("playSound","sfx/Pencil_WriteOnPaper2.ogg")
        self.player.sendGameText(RPG_MSG_GAME_GOOD,r'%s learns <a:Spell%s>%s</a>.\n'%(self.name,GetTWikiName(spellToLearnProto.name),spellToLearnProto.name))


    ## @brief Equips all ItemInstances with a worn slot on this Character's Mob.
    #  @param self (Character) The object pointer.
    #  @param printSets (Boolean) Indicates if ItemSet messages will be sent to
    #                    the Player.
    #  @return None.
    def equipItems(self, printSets=True):

        # Iterate over this Character's items.
        for item in self.items:

            # If the ItemInstance has a worn slot, then have this Character's
            # Mob equip the ItemInstance.
            if RPG_SLOT_WORN_END > item.slot >= RPG_SLOT_WORN_BEGIN:
                self.mob.equipItem(item.slot, item, printSets)


    ## @brief Unequips all ItemInstances with a worn slot on this Character's
    #         Mob.
    #  @param self (Character) The object pointer.
    #  @return None.
    def unequipItems(self):

        # Iterate over this Character's items.
        for item in self.items:

            # If the ItemInstance has a worn slot, then have this Character's
            # Mob unequip the ItemInstance.
            if RPG_SLOT_WORN_END > item.slot >= RPG_SLOT_WORN_BEGIN:
                self.mob.unequipItem(item.slot)


    ## @brief Places, removes, or swaps an ItemInstance in a trade slot.
    #  @param self (Character) The object pointer.
    #  @param slot (Integer) The slot that has been clicked.
    #  @return None.
    #  @todo TWS: Some of this looks overly complicated and could use
    #        simplified.
    def onTradeSlot(self, slot):

        # Get this Character's Player.
        player = self.player

        # Get the Player's trade.
        trade = player.trade

        # If there is no Trade, then return early.
        if not trade:
            return

        # If either Player in a Trade has accepted the Trade, then the trade may
        # not be modified, so return early.
        if trade.p0Accepted or trade.p1Accepted:
            return

        # Get the ItemInstance list in the trade based on the Player.
        if trade.p0 == player:
            titems = trade.p0Items
        else:
            titems = trade.p1Items

        # Get the item on the Player's cursor.
        cursorItem = player.cursorItem
        
        # Get the item slot in the trade window.
        tradeSlot = slot - RPG_SLOT_TRADE_BEGIN

        # Attempt to get the item in the clicked slot.
        previtem = titems.get(tradeSlot,None)

        # If there is no item on the cursor and the slot clicked does not have
        # an item, then return early.
        if not cursorItem and not previtem:
            return

        # If there is an item on the cursor, then  the Player is trying to offer
        # the item for a trade.
        if cursorItem:

            # If the item is soulbound and the Player is not an Immortal, then
            # alert the Player that the item cannot be traded and return early.
            if cursorItem.flags & RPG_ITEM_SOULBOUND and player.role.name != "Immortal":
                self.player.sendGameText(RPG_MSG_GAME_DENIED,r'This item cannot be traded.\n')
                return

            # Iterate over trade slots.
            for tslot in xrange(RPG_SLOT_TRADE_BEGIN,RPG_SLOT_TRADE_END):

                # Iterate over this Character's items.
                for item in self.items:

                    # If the ItemInstance is a trade slot, the slot is not
                    # empty.
                    if item.slot == tslot:
                        break

                # If the slot is empty, then place the cursor item into the
                # slot.
                else:
                    cursorItem.slot = tslot
                    break

            # If a slot was not found, then return early.
            else:
                return

            # If a slot was found, then add the cursor item to the trade item
            # list.
            titems[tradeSlot] = cursorItem
        
        # Otherwise there was no item in the cursor but there is one
        #  in the clicked slot. So need to remove the item from the trade list.
        else:
            del titems[tradeSlot]

        # If there is a previous item, then place it on the cursor.
        if previtem:

            # Set the previous item's slot to be that of the cursor.
            previtem.slot = RPG_SLOT_CURSOR

            # Set the previous item's owner as this Character, updating the
            # item's stats based on this Character.
            previtem.setCharacter(self)

        # Set the previous item onto the Player's cursor.
        player.cursorItem = previtem
        
        # Refresh the cursor info.
        player.updateCursorItem(cursorItem)

        # Refresh the trade so that both Player's observing the trade have their
        # clients updated.
        trade.refresh()


    ## @brief Equips an ItemInstance in the first available slot, swapping slots
    #         with the existing item if necessary.
    #  @param self (Character) The object pointer.
    #  @param item (ItemInstance) The ItemInstance being equipped.
    #  @return None.
    def equipItem(self, item):
        
        # Make a local reference to this Character's Mob.
        mob = self.mob
        
        # Make a local reference to this item's ItemProto.
        itemProto = item.itemProto
        
        # Get all slots in which the item may be equipped.
        slots = set(itemProto.slots)
        
        # If the item can be put into weapon slots, do some additional
        #  preparation.
        if RPG_SLOT_PRIMARY in slots or RPG_SLOT_SECONDARY in slots:
            
            # Store a flag if the item to be equipped is two-handed.
            itemTwoHanded = "2H" in item.skill
            
            # Check this Character's Mob skills for Power Wield.
            powerwield = mob.skillLevels.get("Power Wield")
            
            # Check this Character's Mob skills for Dual Wield.
            # The Mob knowing how to Power Wield is sufficient as well.
            dualwield = powerwield or mob.skillLevels.get("Dual Wield")
            
            # If this Character does not have the Dual Wield skill, then attempt
            #  to remove the secondary slot from the list of slots in which the
            #  item may be equipped.
            if not dualwield:
                
                # Remove the secondary slot from the set of slots in which the
                #  item may be equipped.
                slots.discard(RPG_SLOT_SECONDARY)
            
            # If the item is a two-handed weapon, the mob knows the
            #  power wield skill and the weapon can be equipped in the
            #  primary slot, then add the secondary weapon slot to the
            #  set of possible slots as well.
            elif powerwield and itemTwoHanded and RPG_SLOT_PRIMARY in slots:
                
                # Add secondary weapon slot to the set of allowed slots.
                slots.add(RPG_SLOT_SECONDARY)
        
        # Scan items for wearability conflicts and remove according slots.
        for citem in self.items:
            # If there is already a secondary weapon equipped then deny
            # wearing a shield.
            if citem.slot == RPG_SLOT_SECONDARY:
                # If the item to be equipped is a 2H weapon then quit immediately.
                if "2H" in item.skill and not self.mob.skillLevels.get("Power Wield"):
                    return
                try:
                    slots.remove(RPG_SLOT_SHIELD)
                except KeyError:
                    pass
            # If there is already a shield equipped then deny wearing a
            # secondary weapon.
            elif citem.slot == RPG_SLOT_SHIELD:
                # If the item to be equipped is a 2H weapon then quit immediately.
                if "2H" in item.skill:
                    return
                try:
                    slots.remove(RPG_SLOT_SECONDARY)
                except KeyError:
                    pass
            # If there is already a 2H weapon equipped then deny wearing a
            # secondary weapon or a shield.
            elif citem.slot == RPG_SLOT_PRIMARY and "2H" in citem.skill:
                if "2H" in item.skill and not self.mob.skillLevels.get("Power Wield"):
                    return
                try:
                    slots.remove(RPG_SLOT_SHIELD)
                except KeyError:
                    pass

        # If there are no possible slots, then the item cannot be equipped.
        # Return early.
        if not len(slots):
            return False
        
        # Slot in which the item will be equipped.
        useslot = None
        
        # Flag indicating if an item needs unequipped.
        unequip = False
        
        # Iterate over all slots in which the item may be equipped.
        for slot in slots:
            
            # Check if an item is already equipped in that slot.
            if not self.mob.worn.get(slot):
                
                # No item equipped in the slot, so use the slot.
                useslot = slot
                break
        
        # If there is no slot available, then there is an item in all the slots.
        else:
            
            # If item that should be equipped has invalid slot or is in a loot
            #  slot, then do not attempt to swap it with an equipped item.
            if item.slot == -1 or RPG_SLOT_LOOT_BEGIN <= item.slot < RPG_SLOT_LOOT_END:
                return False
            
            # Set the unequip flag.
            unequip = True
            
            # Use the first slot in the list.
            useslot = slots.pop()
        
        # If the slot chosen is the primary weapon slot, then check if the new
        #  item can be equipped there considering a possible secondary weapon.
        if useslot == RPG_SLOT_PRIMARY:
            
            # Get the item in the secondary weapon slot.
            sitem = mob.worn.get(RPG_SLOT_SECONDARY,None)
            
            # If there is an item in the secondary weapon slot, perform
            #  the additional checks.
            if sitem:
                
                # If the Character cannot Dual Wield, the other item
                #  shouldn't even be there, so directly unequip and
                #  all might be well.
                if not dualwield:
                    if not self.unequipItem(RPG_SLOT_SECONDARY):
                        
                        # Somehow that item resisted removal, so return
                        #  before we make things worse.
                        return False
                
                # Otherwise the Character is able to Dual Wield, so check now
                #  if the weapon combination would require Power Wield.
                # If yes and the Character isn't able to Power Wield then
                #  unequip the weapon in the secondary slot.
                elif not powerwield and (itemTwoHanded or "2H" in sitem.skill):
                    if not self.unequipItem(RPG_SLOT_SECONDARY):
                        
                        # Somehow that item resisted removal, so return
                        #  before we make things worse.
                        return False
        
        # If the slot chosen is the secondary weapon slot, then check if the new
        #  item can be equipped there considering a possible primary weapon.
        elif useslot == RPG_SLOT_SECONDARY:
            
            # Get the item in the primary weapon slot.
            pitem = mob.worn.get(RPG_SLOT_PRIMARY,None)
            
            # If there is an item in the primary weapon slot, perform
            #  the additional checks.
            if pitem:
                
                # Check if the Character knows how to Dual Wield.
                if not dualwield:
                    
                    # Skill check failed, see if this weapon could also
                    #  be put in the primary slot and prefer this one over
                    #  the secondary slot.
                    if RPG_SLOT_PRIMARY in slots:
                        useslot = RPG_SLOT_PRIMARY
                        
                        # If the new item would have replaced an existing item
                        #  in the secondary weapon slot, unequip the secondary
                        #  weapon now.
                        if unequip:
                            if not self.unequipItem(RPG_SLOT_SECONDARY):
                                
                                # Somehow that item resisted removal, so return
                                #  before we make things worse.
                                return False
                        
                        # Set the unequip flag.
                        unequip = True
                    
                    # Otherwise directly try to unequip the primary weapon.
                    elif not self.unequipItem(RPG_SLOT_SECONDARY):
                        
                        # Somehow that item resisted removal, so return
                        #  before we make things worse.
                        return False
                
                # The Character knows how to Dual Wield.
                # We still need to check if the new weapon configuration would
                #  require Power Wield though and if the Character is capable
                #  of that.
                elif not powerwield and (itemTwoHanded or "2H" in pitem.skill):
                    
                    # Can't use this weapon configuration.
                    
                    # If the new weapon can be put in the primary weapon slot
                    #  as well, put it there instead.
                    if RPG_SLOT_PRIMARY in slots:
                        useslot = RPG_SLOT_PRIMARY
                        
                        # If the new item would have replaced an existing item
                        #  in the secondary weapon slot, check again for a valid
                        #  weapon configuration.
                        if unequip and (itemTwoHanded or "2H" in \
                            mob.worn.get(RPG_SLOT_SECONDARY).skill):
                            
                            # Still invalid configuration, so try to unequip
                            #  the item in the secondary weapon slot.
                            if not self.unequipItem(RPG_SLOT_SECONDARY):
                                
                                # Somehow that item resisted removal, so return
                                #  before we make things worse.
                                return False
                        
                        # Set the unequip flag.
                        unequip = True
                    
                    # Otherwise directly try to unequip the primary weapon.
                    elif not self.unequipItem(RPG_SLOT_PRIMARY):
                        
                        # Somehow that item resisted removal, so return
                        #  before we make things worse.
                        return False
        
        # If the item is unique, then check if another item of the same type
        #  is already equipped.
        if item.flags & RPG_ITEM_UNIQUE:
            
            # Iterate over the item's worn by this Character's Mob.
            for iitem in self.mob.worn.itervalues():
                
                # If an item of this type is already worn and the items are not
                #  being swapped because of different slots, then send a message
                #  to the Player and return early.
                if itemProto == iitem.itemProto and iitem.slot != useslot:
                    self.player.sendGameText(RPG_MSG_GAME_DENIED, \
                        "%s can only use one of these at a time!\\n"%self.name)
                    return False
        
        # If unequip flag is set, but unequipItem failed, then this item cannot
        #  be equiped so return early.
        if unequip and not self.unequipItem(useslot,item.slot):
            return False
        
        # Update the item's slot.
        item.slot = useslot
        
        # Equip the item on this Character's Mob.
        self.mob.equipItem(useslot,item)
        
        # If the item has an equip sound, then get it.
        if item.sndProfile and item.sndProfile.sndEquip:
            snd = item.sndProfile.sndEquip
        
        # Otherwise, use a default sound.
        else:
            snd = SND_ITEMEQUIP
        
        # Play a sound to the Player.
        self.player.mind.callRemote("playSound",snd)
        
        # Finally return success.
        return True


    ## @brief Unequips an ItemInstance from a slot for the Character.
    #  @param self (Character) The object pointer.
    #  @param slot (Integer) Slot from which an ItemInstance will be removed.
    #  @param putslot (Integer) Slot in which the ItemInstance will be placed.
    #  @return (Boolean) True if an ItemInstance was was unequiped.  Otherwise,
    #          False.
    #  @bug TWS: What happens if putslot already has an item in it?  Two items
    #       will share a slot, and true will still be returned.
    #  @todo TWS: Optimize.  getFreeCarrySlots is a bit too much, only one
    #        slot is needed.
    #  @todo TWS: This should probably return a boolean, as should mob.equip().
    def unequipItem(self, slot, putslot=None):

        # Iterate over this Character's items.
        # TWS: Should/could probably check a dictionary of worn items.
        for item in self.items:

            # If an item was found with the slot to unequip, then attempt to
            # find a new slot.
            if item.slot == slot:

                # If a new slot was provided by caller, then change the
                # unequipped item's slot.
                if putslot != None and putslot != -1:
                    item.slot = putslot

                # Otherwise, find a free slot.
                else:

                    # Get free carry slots.
                    free = self.getFreeCarrySlots()

                    # If there are no free carry slots, return False.
                    if not len(free):
                        return False

                    # Change the unequipped item's slot to the free slot.
                    item.slot = free[0]

                # Unequip the slot from this Character's Mob.
                self.mob.unequipItem(slot)

                # Return True as an item in the slot was unequipped.
                return True

        # All items have been iterated over, but no item matched the slot to
        # unequip, so return False.
        return False


    ## @brief Unequips equipped items, picks up a single item from a stack of
    #         items, or equips an item, swapping slots with the previously
    #         equipped item for the double-clicked slot.
    #  @param self (Character) The object pointer.
    #  @param slot (Integer) The slot that has been double-clicked.
    #  @return None.
    #  @todo TWS: The worn slot logic is a little odd to me (maybe redundant).
    #        Behavior is suppose to be: If there is an item on the cursor,
    #        unequip item in slot (move to free inventory) and equip cursor item.
    #        If there are no free inventory spots, then the items basically swap
    #        slots (equiped on cursor and previous cursor is equiped).  It may
    #        be better to attempt to swap under all cases, and then move cursor
    #        item to free inventory slot if any.  This may be a bit more natural
    #        and reduce times an inventory iteration occurs.
    #  @todo TWS: Control flow is hard to folow with the if and returns.  This
    #        should be simplified to prevent logic layers becoming deep in
    #        levels.
    #  @bug  TWS: Possible not doing proper item info refreshes. The if codntion
    #        looks awkward.
    def onInvSlotAlt(self, slot):

        # If the slot is a worn slot, attempt to unequip the Item.
        if RPG_SLOT_WORN_END > slot >= RPG_SLOT_WORN_BEGIN:

            # Unequip the slot.
            self.unequipItem(slot)

            # If there is an item on the cursor, then attempt to equip it in the
            # inventory slot.
            if self.player.cursorItem:

                # Attempt to equip in the inventory slot.
                self.onInvSlot(slot)

            # The worn slot was handled, so return.
            return

        # If the slot is a carry or crafting slot, then attempt to either
        # pickup a single instance from a stacked item, or equip the item.
        if (RPG_SLOT_CARRY_END > slot >= RPG_SLOT_CARRY_BEGIN) or (RPG_SLOT_CRAFTING_END > slot >= RPG_SLOT_CRAFTING_BEGIN):

            # Iterate over this Character's items.
            for item in self.items:

                # If an item matches the slot clicked on, then this ItemInstance
                # was clicked.
                if item.slot == slot:

                    # Make local variables to values referenced during stacking.

                    # Make a local handle to the item's ItemProto, this Player's
                    # cursor item, and the max amount of items a stack can hold.
                    proto = item.itemProto
                    cursorItem = self.player.cursorItem
                    stackMax = proto.stackMax

                    # The clicked location has a stackable item.
                    if stackMax > 1:

                        # Try to take one element from the stack and put it onto
                        # the cursor.
                        if not cursorItem or cursorItem.name == item.name:

                            # If the clicked item has no stack count, set a
                            # stack count to 1.
                            # TWS: Does this occur?  Seems unsafe if it does.
                            if not item.stackCount:
                                item.stackCount = 1

                            # If there is no item on the cursor, then
                            if not cursorItem:

                                # If the item only has one item left, then
                                # grab the stack.
                                if item.stackCount == 1:

                                    # Treat the click as if it was a normal
                                    # click.
                                    self.onInvSlot(slot)

                                    # Assign the item to this Player's cursor.
                                    # TWS: Is this redundant, onInvSlot does
                                    # this.
                                    self.player.cursorItem = item

                                    # Update the client's cursor item.
                                    self.player.updateCursorItem(None)
                                    return

                                # Otherwise, create a clone and update stack
                                # counts on the cursor item and inventory item.

                                # Create the ItemInstance and set this Character
                                # as the owner.
                                nitem = item.clone()
                                nitem.setCharacter(self,False)

                                # Set initial stack count and reduce the stack
                                # count from the item.
                                nitem.stackCount = 1
                                item.stackCount -= 1

                                # Refresh ItemInfo so observing clients see the
                                # new stack count.
                                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})

                                # Move the cloned item onto this Player's
                                # cursor.
                                self.player.cursorItem = nitem
                                nitem.slot = RPG_SLOT_CURSOR

                                # Update the client's cursor item.
                                self.player.updateCursorItem(None)
                                return

                            # We have a stackable item in cursor, move one item
                            # from the stack to the cursor.
                            if cursorItem.stackCount < stackMax:

                                # The max charges alowed on the item.
                                useMax = proto.useMax

                                # Flag indicating if the item's stack count
                                # changed.
                                useStack = False

                                # Flag indicating if the item's charges changed.
                                refreshUse = False

                                # If there are charges and the item being added
                                # is below the max.  If it is at the max, then
                                # only the stack count will be adjusted.
                                if useMax > 1 and item.useCharges < useMax:

                                    # Calculate how many more charges the cursor
                                    # can hold.
                                    amt = useMax - cursorItem.useCharges

                                    # Set the item's infoitem to refresh
                                    # charges.
                                    refreshUse = True

                                    # If the amount available is greater than
                                    # the amount on the item, then the cursor
                                    # item can hold all the charges.
                                    if amt >= item.useCharges:

                                        # Update the charges.
                                        cursorItem.useCharges += item.useCharges

                                        # Set flag to indicate stacking did
                                        # not occur on the stack, but occured
                                        # on charges.
                                        useStack = True

                                    # Otherwise, item is providing more charges
                                    # than the cursor can hold.  Stacking will
                                    # occur on the stack count, so calculate the
                                    # new item charges.
                                    else:
                                        cursorItem.useCharges = item.useCharges - amt

                                    # Set the item to be at useMax, as the item
                                    # removed was the one that may not have had
                                    # max changes.
                                    item.useCharges = useMax

                                # TWS: this is misleading, if you do not useStack
                                # then update it?  useStack is only set true
                                # Updating cursor item if stacking did not occur
                                # only on charges.
                                if not useStack:
                                    cursorItem.stackCount += 1

                                # TWS: This if statement seems awkward to me.
                                # If both the refresh and stack counts have
                                # changed, update client.
                                if refreshUse and useStack:
                                    # Refresh ItemInfo so observing clients see
                                    # the cursor item's new charge value.
                                    cursorItem.itemInfo.refreshDict({'USECHARGES':cursorItem.useCharges})

                                # Only the charge count has changed.
                                elif refreshUse:
                                    # Refresh ItemInfo so observing clients see
                                    # the cursor item's new charge value and
                                    # stack count.
                                    cursorItem.itemInfo.refreshDict({'STACKCOUNT':cursorItem.stackCount,'USECHARGES':cursorItem.useCharges})

                                # Only the stack count has changed.
                                else:
                                    # Refresh ItemInfo so observing clients see
                                    # the cursor item's new stack count.
                                    cursorItem.itemInfo.refreshDict({'STACKCOUNT':cursorItem.stackCount})

                                # If the item has a stack count, reduce a stack.
                                if item.stackCount > 1:
                                    item.stackCount -= 1

                                    # If charges changed, refresh charges and
                                    # stack count.
                                    if refreshUse:
                                        # Refresh ItemInfo so observing clients
                                        # see the item's new charge value and
                                        # stack count.
                                        item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})

                                    # Otherwise, only stack count changed.
                                    else:
                                        # Refresh ItemInfo so observing clients
                                        # see the item's new stack.
                                        item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})

                                    # Stacking handled, return.
                                    return

                                # TWS: For safety, this should probably be in an
                                # else statement.
                                # Item has no more stacks, so remove it.
                                self.player.takeItem(item)

                        # Stackable handled, return.
                        return

                    # Otherwise, check if the item has slots in which it may be
                    # equipped.
                    # TWS: Some of this should be caught on the client, but
                    # it is done here because the client cannot be trusted.
                    # Maybe this should be logged?
                    if len(proto.slots):

                        # If this Character's Mob cannot use the item, then
                        # inform the Player and return early.
                        if not item.isUseable(self.mob):

                            # If the world is a demo or the Player is not
                            # premium, inform the player.
                            if RPG_BUILD_DEMO and not self.player.premium:
                                if item.level>=50 or item.itemProto.flags&RPG_ITEM_PREMIUM:
                                    self.player.sendGameText(RPG_MSG_GAME_DENIED,"\\nThis item requires the Minions of Mirth: Premium Edition.  Please see www.prairiegames.com for more information.\\n\\n")

                            # Inform the Player.
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot use this item!\n'%self.name)
                            return

                        # Otherwise, equip the item.
                        self.equipItem(item)
                        return

                    break


    ## @brief Equips this Character's Pet, updating stats and simulation.
    #  @param self (Character) The object pointer.
    #  @return None.
    def setPetEquipment(self):

        # If this Character has no Mob, return early.
        if not self.mob:
            return

        # Make a local handle to this Character's Pet.
        pet = self.mob.pet

        # If this Character has no pet, the pet is detached, or the pet is
        # a charmed pet, then return early.
        if not pet or pet.detached or pet.charmEffect:
            return

        # Refresh pet items, calculating penalties and equpping items.
        self.refreshPetItems()

        # Refresh the pet's SimMobInfo, as the items may have changed simulated
        # data, such as visual items equipped and visibility.
        pet.mobInfo.refresh()


    ## @brief Refreshes ItemInstances equipped in pet slots.
    #  @param self (Character) The object pointer.
    #  @param itemList (List of ItemInstances) The list to iterate over.
    #                  If no list is provided, iterate over all items
    #                  in this Character's possession.
    #  @return None.
    def refreshPetItems(self, itemList=None):

        # Make a local handle to this Character's Pet.
        pet = self.mob.pet
        
        # If no item list was provided, deal with all items in this
        #  Character's possession.
        if not itemList:
            itemList = self.items

        # If there is no pet (died, unsummoned, etc.), reassign the item to
        # this Character.
        if not pet:

            # Iterate over the list of items.
            for item in itemList:

                # If the item is in a pet slot, reassign to this Character.
                if RPG_SLOT_PET_BEGIN <= item.slot < RPG_SLOT_PET_END:

                    # Reassigment will calculate a new penalty and update the
                    # item's stats based on this penalty.  This is required
                    # because when an item is equipped on a pet, the item gets
                    # a new penalty calculated and item stats adjusted for the
                    # pet.
                    item.setCharacter(self,True)

            # No pet exists, so items cannot be equipped.  Return early.
            return

        # Unequip any pet slot.
        map(pet.unequipItem,xrange(RPG_SLOT_WORN_BEGIN,RPG_SLOT_WORN_END))
        
        # Get a handle to the pets realm.
        myrealm = self.mob.spawn.realm

        # Iterate over the list of items.
        for item in itemList:

            # If the item is not in a pet slot, continue to the next item.
            if not (RPG_SLOT_PET_BEGIN <= item.slot < RPG_SLOT_PET_END):
                continue

            # Get the ItemProto.
            proto = item.itemProto

            # Get the relative pet slot the current item would go into.
            petSlot = item.slot - RPG_SLOT_PET_BEGIN
            
            # If the world is a demo and the player is not premium
            if RPG_BUILD_DEMO and not self.player.premium:
                if item.level >= 50 or proto.flags&RPG_ITEM_PREMIUM:

                    # Equip the item but use masters 100% penalty.
                    pet.equipItem(petSlot,item)

                    # Continue to the next item.
                    continue

            # If the item has realm requirements, then check them.
            if len(proto.realms):

                # Iterate over the item's realm requirements.
                for r in proto.realms:

                    # If the spawn's realm matches, break the loop.
                    if myrealm == r.realmname:

                        # Exit the loop.
                        break

                # If this Character's mob did not satisfy the realm requirement,
                # then equip the item on the pet but use the master's 100%
                # penalty.
                else:
                    pet.equipItem(petSlot,item)

                    # Continue to the next item.
                    continue

            # Update the item's penalty based on the penalty it provides for a
            # pet.
            item.penalty = item.getPenalty(pet,True)

            # Update the item stats based on the updated penalty.
            item.refreshFromProto(True)

            # Equip the item on the pet.
            pet.equipItem(petSlot,item)


    ## @brief Equips this Character's Pet.
    #  @param self (Character) The object pointer.
    #  @param slot (Integer) The slot that has been double-clicked.
    #  @return None.
    #  @note TWS: Some of the flow could be optimized.  setPetEquipment gets
    #        called, then refreshPetItems gets called.   This will unequip and
    #        re-equip a pet, iterating over all items.  Maybe a single refresh
    #        type behavior could be used when only a single item changes.
    #  @note TWS: Does the client's cursor slot display need updated?
    def onPetSlot(self, slot):

        # Make a local handle to the item on this Player's cursor, if any.
        cursorItem = self.player.cursorItem

        # Handle used to store item currently in the slot.
        previtem = None

        # Iterate over this Character's items.
        for item in self.items:

            # If an item is found with the slot clicked, then store a handle to
            # the item.
            if item.slot == slot:
                previtem = item
                break

        # If an item is on the cursor, then the Player is attempting to
        # equip the item in the pet slot.
        if cursorItem:

            # If the slot clicked is not in the cursor item's slots, then
            # the inform the Player the item can not be equipped and return
            # early.
            if (slot-RPG_SLOT_PET_BEGIN) not in cursorItem.itemProto.slots:

                self.player.sendGameText(RPG_MSG_GAME_DENIED,r'This item cannot be equipped here.\n')
                return

            # Set the item's owner as this Character, updating the item's stats
            # based on this Character.
            cursorItem.setCharacter(self)

            # Update the cursor item's slot to be the clicked pet slot.
            cursorItem.slot = slot

            # Clear the Player's cursor.
            self.player.cursorItem = None

            # Update player GUI to show the old cursor item in the pet slot.
            self.player.mind.callRemote("setItemSlot",self.id,cursorItem.itemInfo,slot)

        # Otherwise, the Player is removing an item from a pet slot.
        else:

            if previtem:

                # Update player GUI to show the old item being removed.
                self.player.mind.callRemote("setItemSlot",self.id,None,slot)

        # If there was previously an item in the pet slot, then it has swapped
        # and is now on the cursor.
        if previtem:

            # Update the previously equipped item to the cursor slot.
            previtem.slot = RPG_SLOT_CURSOR

            # Set the previously equipped item onto this Player's cursor.
            self.player.cursorItem = previtem

            # Reassigment will calculate a new penalty and update the item's
            # stats based on this penalty.  This is required because when an
            # item is equipped on a pet, the item can get a new penalty
            # calculated and item stats adjusted for the pet.
            previtem.setCharacter(self,True)

        # If any items swapped slots.
        if previtem or cursorItem:

            # Play a sound for the Player.
            self.player.mind.callRemote("playSound",SND_INVENTORY)

            # Attempts to update the pet, as an item was either removed or
            # added.
            self.setPetEquipment()


    ## @brief The Character will attempt to locate food within the Party and
    #         eat.
    #  @param self (Character) The object pointer.
    #  @param tick (Boolean) Indicates if the eat timer has been satisfied.
    #  @return None.
    #  @bug TWS: Bug not specific to this method, reviewing this code sparked
    #       the idea.  Different stacking code may be destroying food value.
    #       To prevent this, maybe food should adjust the tick rate.  This would
    #       free up some database room too.
    def eat(self, tick=True):

        # If this Character has no player, return early.
        if not self.player:
            return

        # Stores a list of food items.
        items = []

        # For each Character in this Player's party.
        for m in self.player.party.members:

            # Add the member's food to the list.
            items.extend(m.mob.itemFood.keys())

        # Iterate over the food items found.
        for item in items:

            # If the item has a food value, reduce it.
            if item.food:

                # Reduce the food value.
                item.food -= 1

                # The mob just ate, so it is not hungry.
                self.mob.hungry = False

                # If there is no more food on the item, then reduce the item's
                # stack count.
                if item.food <= 0:

                    # Reduce the item's stack count.
                    item.stackCount -= 1

                    # If there are no more items in the stack, then take the
                    # item.
                    if item.stackCount <= 0:

                        # Remove the item from this Character.
                        self.player.takeItem(item)

                    # Otherwise, there is still an item in the stack.
                    else:

                        # Set the item's food value to be the max food value.
                        item.food = item.itemProto.food

                        # Refresh ItemInfo so observing clients see the food's
                        # new stack count.
                        item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})

                # This Character has ate and is not starving, so return.
                return

        # If is a tick call, then the eat timer has been satisfied.  This is
        # used to control informing the Player of hunger.
        if tick:

            # No food was found and this Character is hungry.
            self.mob.hungry = True

            # Inform the Player.
            self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s is starving.\n'%self.name)


    ## @brief The Character will attempt to locate water within the Party and
    #         drink.
    #  @param self (Character) The object pointer.
    #  @param tick (Boolean) Indicates if the drink timer has been satisfied.
    #  @return None.
    #  @bug TWS: Bug not specific to this method, reviewing this code sparked
    #       the idea.  Different stacking code may be destroying drink value.
    #       To prevent this, maybe drink should adjust the tick rate.  This
    #       would free up some database room too.
    def drink(self, tick=True):

        # If this Character has no player, return early.
        if not self.player:
            return

        # Stores a list of drinks.
        items = []

        # For each Character in this Player's party.
        for m in self.player.party.members:

            # Add the member's drinks to the list.
            items.extend(m.mob.itemDrink.keys())

        # Iterate over the drink items found.
        for item in items:

            # If the item has a drink value, reduce it.
            if item.drink:

                # Reduce the drink value.
                item.drink -= 1

                # The mob just drank, so it is not thirsty.
                self.mob.thirsty = False

                # If there is no more drink on the item, then reduce the item's
                # stack count.
                if item.drink <= 0:

                    # Reduce the item's stack count.
                    item.stackCount -= 1

                    # If there are no more items in the stack, then take the
                    # item.
                    if item.stackCount <= 0:

                        # Remove the item from this Character.
                        self.player.takeItem(item)

                    # Otherwise, there is still an item in the stack.
                    else:

                        # Set the item's drink value to be the max drink value.
                        item.drink = item.itemProto.drink

                        # Refresh ItemInfo so observing clients see the drink's
                        # new stack count.
                        item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})

                # This Character has drank and is not thirsty, so return.
                return

        # If is a tick call, then the drink timer has been satisfied.  This is
        # used to control informing the Player of thirst.
        if tick:

            # No drink was found and this Character is thirsty.
            self.mob.thirsty = True

            # Inform the Player.
            self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s is thirsty.\n'%self.name)


    ## @brief Handles trade, pet, or inventory slot clicked.  Attempts to equip
    #         an item if a worn slot was clicked.  Item attempts to stack.  If
    #         possible, picks up an item, placing a cursor item (if any) in the
    #         slot clicked.
    #  @param self (Character) The object pointer.
    #  @param slot (Integer) The slot that has been clicked.
    #  @return None.
    #  @todo TWS: Equip checks and logic occur in two places, maybe this
    #        should be consolidated to one function.
    def onInvSlot(self, slot):

        # Handle if a trade slot was clicked.
        if RPG_SLOT_TRADE_END > slot >= RPG_SLOT_TRADE_BEGIN:
            self.onTradeSlot(slot)
            return

        # Handle if a pet slot was clicked.
        if RPG_SLOT_PET_END > slot >= RPG_SLOT_PET_BEGIN:
            self.onPetSlot(slot)
            return

        # Make a local handle to the item on this Player's cursor, if any.
        cursorItem = self.player.cursorItem

        # Handle used to store item currently in the slot.
        previtem = None

        # Iterate over this Character's items.
        for item in self.items:

            # If an item is found with the slot clicked, then store a handle to
            # the item.
            if item.slot == slot:
                previtem = item
                break

        # If there is a previous item, check for container or attempt stacking.
        if previtem:
            
            # Check if the item clicked on is a container. If so, try to insert
            #  the item in cursor.
            if cursorItem and previtem.container:
                
                # If adding the item returns true, then it actually worked.
                if previtem.container.insertItem(cursorItem,True):
                    # Update the container contents on client.
                    previtem.itemInfo.refreshContents()
                    return
                
                # Couldn't store to container, so swap for consistency.
                switched,cursorItem,previtem = True,previtem,cursorItem

            # Otherwise attempt to stack the items.
            else:
                switched,cursorItem,previtem = previtem.doStack(cursorItem)

                # If items did not get switched, then the items stacked.
                if not switched:
                    return

        # Flag indicating if an item should be equipped.
        shouldEquip = False

        # If there was an item on the cursor.
        if cursorItem:

            # If the slot equipped was a worn slot, then check if this
            # Character can equip the item.
            if RPG_SLOT_WORN_END > slot >= RPG_SLOT_WORN_BEGIN:

                # Check if the ItemInstance is useable by this
                #  Character's Mob.
                # If this Character's Mob cannot use the item, then
                #  inform the Player and return early.
                if not cursorItem.isUseable(self.mob):

                    # If the world is a demo or the Player is not
                    # premium, inform the player.
                    if RPG_BUILD_DEMO and not self.player.premium:
                        if cursorItem.level>=50 or cursorItem.itemProto.flags&RPG_ITEM_PREMIUM:
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,"\\nThis item requires the Minions of Mirth: Premium Edition.  Please see www.prairiegames.com for more information.\\n\\n")

                    # Inform the Player.
                    self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s cannot use this item!\n'%self.name)

                    # TWS: This should be caught on client, maybe log otherwise?
                    return

                # If the item is unique, then check if another item of the same
                # type is already equipped.
                if cursorItem.flags & RPG_ITEM_UNIQUE:

                    # Iterate over the item's worn by this Character's Mob.
                    for iitem in self.mob.worn.itervalues():

                        # If an item of this type is already worn and the items
                        # are not being swapped beacuse of different slots, then
                        # send a message to the Player and return early.
                        if cursorItem.itemProto == iitem.itemProto and slot != iitem.slot:
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s can only use one of these at a time!\n'%self.name)
                            return

                # If the slot clicked was secondary, and this Character has not
                # trained dual wield, then inform the player and return early.
                if slot == RPG_SLOT_SECONDARY and not self.mob.skillLevels.get("Dual Wield"):
                    self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s does not know how to <a:SkillDualWield>dual wield</a>.\n'%self.name)
                    return

                # If there is already a shield equipped then deny wearing a
                # secondary or two handed weapon.
                if slot == RPG_SLOT_SECONDARY:
                    for iitem in self.mob.worn.itervalues():
                        if iitem.slot == RPG_SLOT_PRIMARY and "2H" in iitem.skill and not self.mob.skillLevels.get("Power Wield"):
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,"You can't wear that together with a two handed weapon.\\n")
                            return
                    if RPG_SLOT_SHIELD in self.mob.worn:
                        self.player.sendGameText(RPG_MSG_GAME_DENIED,"You can't wear that together with a shield.\\n")
                        return

                # If there is already a secondary weapon equipped then deny
                # wearing a shield or two handed weapon.
                if slot == RPG_SLOT_SHIELD:
                    for iitem in self.mob.worn.itervalues():
                        if iitem.slot == RPG_SLOT_PRIMARY and "2H" in iitem.skill:
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,"You can't wear that together with a two handed weapon.\\n")
                            return
                    if RPG_SLOT_SECONDARY in self.mob.worn:
                        self.player.sendGameText(RPG_MSG_GAME_DENIED,"You can't wear that together with a secondary weapon.\\n")
                        return

                # Scan items for wearability conflicts when trying to equip a 2H weapon.
                if "2H" in cursorItem.skill:
                    for iitem in self.mob.worn.itervalues():
                        # If there is already a secondary weapon equipped then quit.
                        if iitem.slot == RPG_SLOT_SECONDARY  and not self.mob.skillLevels.get("Power Wield"):
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,"You can't wear that together with a secondary weapon.\\n")
                            return
                        # If there is already a shield equipped then quit.
                        elif iitem.slot == RPG_SLOT_SHIELD:
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,"You can't wear that together with a shield.\\n")
                            return

                # If the slot clicked was secondary, the cursor item is a two
                # handed weapon, and this Character has not power wield, then
                # inform the Player and return early.
                # TWS: Should probably move this if statement and the one above
                # into a if statement with the condition of RPG_SLOT_SECONDARY.
                if slot == RPG_SLOT_SECONDARY and "2H" in cursorItem.skill and not self.mob.skillLevels.get("Power Wield"):
                    self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s does not know how to <a:SkillPowerWield>power wield</a>.\n'%self.name)
                    return

                # If the slot clicked is not in the cursor item's slots, and the
                # item is not a two-hander clicked on a secondary slot, then the
                # item can not be equipped in the clicked slot, so inform the
                # Player and return early.
                if slot not in cursorItem.itemProto.slots and not ("2H" in cursorItem.skill and slot == RPG_SLOT_SECONDARY):
                    self.player.sendGameText(RPG_MSG_GAME_DENIED,r'This item cannot be equipped here.\n')
                    return

                # Set the flag indicating the item should be equipped.
                shouldEquip = True

            # The item is either equippable in the worn slot clicked, or the
            # item is being placed in an inventory carry slot.  In either case,
            # set Character ownership, updating the item, and update the client.

            # Set the cursor item's owner as this Character, updating the item's
            # stats based on this Character.
            cursorItem.setCharacter(self)

            # Update the cursor item's slot to be the clicked slot.
            cursorItem.slot = slot

            # Clear the Player's cursor.
            self.player.cursorItem = None

            # Update the clients cursor item.
            self.player.updateCursorItem(cursorItem)

            # Update player GUI to show the old cursor item in the pet slot.
            self.player.mind.callRemote("setItemSlot",self.id,cursorItem.itemInfo,slot)

        # Otherwise, the Player is removing an item from the slot.
        else:
            if previtem:

                # Update player GUI to show the old item being removed.
                self.player.mind.callRemote("setItemSlot",self.id,None,slot)

        # If there was previously an item in the slot, then it has swapped
        # and is now on the cursor.
        if previtem:

            # If the slot clicked on was a worn slot, then unequip the slot.
            if RPG_SLOT_WORN_END > slot >= RPG_SLOT_WORN_BEGIN:
                self.mob.unequipItem(slot)

            # Update the previously equipped item to the cursor slot.
            previtem.slot = RPG_SLOT_CURSOR

            # Set the previously equipped item onto this Player's cursor.
            self.player.cursorItem = previtem

            # Update the client's cursor item.
            self.player.updateCursorItem(cursorItem)

        # If the cursor item was equippable in the clicked slot, then equip it.
        if shouldEquip:

            # Equip the item.
            self.mob.equipItem(slot,cursorItem)

            # Set default sound to play.
            snd = SND_ITEMEQUIP

            # If the item has an equip sound, get it.
            if cursorItem.sndProfile and cursorItem.sndProfile.sndEquip:
                snd = cursorItem.sndProfile.sndEquip

            # Play a sound to the Player.
            self.player.mind.callRemote("playSound",snd)

        # Otherwise, the item was placed in an inventory slot.
        else:

            # Play a sound to the Player.
            self.player.mind.callRemote("playSound",SND_INVENTORY)


    ## @brief Attempts to fully stack a provided item to the Character's
    #         inventory.  The stacked item does not get disposed.
    #  @param self (Character) The object pointer.
    #  @param sitem (ItemInstance) The item attempting to be stacked.
    #  @return (Boolean) True if stacking ooccured.  Otherwise, False.
    #  @todo TWS: Consider reviewing charge stacking math for a simplier
    #        solution.
    #  @todo TWS: Consider having the stacked item being disposed instead of
    #        depending on caller to dispose.  Currently, it seems like this code
    #        could be the source of a few easily overlooked item dupes.
    def stackItem(self, sitem):

        # If there is no item t stack, return early.
        if not sitem:

            # Return False to indicate stacking did not occur.
            return False

        # Get the Item's max stack value.
        stackMax = sitem.itemProto.stackMax

        # If the item is not stackable, return early.
        if stackMax <= 1:

            # Return False to indicate stacking did not occur.
            return False

        # Get the Item's max use value.
        useMax = sitem.itemProto.useMax

        # Stacking will
        stacking = {}

        # For improved performance, items with charges will be handled in a
        # seperate loop than items without charges.

        # If the item holds more than one charge, then specifically handle
        # stacking for counts and charges.
        if useMax > 1:

            # Since the stack count on an item with charges is dependent on the
            # charge count, calculate stackability based on the total number of
            # charges an ItemInstance has.

            # Calculate the amount of charges that are on the item attempting to
            # be stacked.
            neededCharges = useMax * (sitem.stackCount - 1) + sitem.useCharges

            # Iterate over this Character's items.
            for item in self.items:

                # If the ItemInstance is the same as the ItemInstance being
                # stacked, or if the names of the items are different, continue
                # to the next item.
                if sitem == item or sitem.name != item.name:
                    continue

                # The item being iterated over may possible stack with the item
                # attempting to be stacked.  Calculate how many charges the
                # iterated item can hold.
                freeCharges = useMax * (stackMax - item.stackCount + 1) - item.useCharges

                # If the item holds no more charges, then it has the max stack
                # count and max charges.  It will not stack with the item
                # attempting to be stacked, so continue to the next item.
                # TWS: Is it better to check stackcount and usecharges for max?
                if freeCharges <= 0:
                    continue

                # If the iterated item holds more charges than the attempting
                # to stack item has, just use the charges available.  Otherwise,
                # the item to stack has more charges, and the iterated item
                # should only use the count of charges it can hold.
                if freeCharges > neededCharges:
                    freeCharges = neededCharges

                # Store the iterated item and the count of charges being added
                # to the item.
                stacking[item] = freeCharges

                # Subtract the charges that might be added to the iterated item
                # from count of charges stil needing to be stacked.
                neededCharges -= freeCharges

                # If there are no more charges needing stacked, then the item
                # attempting to be stacked can be completely stacked, so exit
                # the loop.
                if neededCharges <= 0:
                    break

            # Otherwise, all items have been iterated over and some charges
            # still remain unstacked, so the item did not successfully stack.
            else:

                # Return False to indicate stacking did not occur.
                return False

            # Iterate over items that stacked with the item attempting to be
            # stacked, adjusting and refreshing the stack count and charge
            # value for each item.
            for item,charges in stacking.iteritems():

                # Calculate the amount of stacks that will be added to the item.
                stackCount = charges / useMax

                # Calculate the amount of charges that will be added to the
                # item.
                charges = charges % useMax

                # Update the stack count.
                item.stackCount += stackCount

                # Update the charges.
                item.useCharges += charges

                # If the item use charges is greater than the use max, then
                # collapse charges to an item.
                if item.useCharges > useMax:

                    # Reduce by the max charges a single item would provide.
                    item.useCharges -= useMax

                    # Increase the stack count, since the charges collapsed.
                    item.stackCount += 1

                # Refresh ItemInfo so observing clients see the item's new
                # charge value and stack count.
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})

            # Return True as the item succesfully stacked.
            return True


        # Otherwise, the item holds one or no charges.
        else:

            # Get the amount of items needing stacked.
            neededStack = sitem.stackCount

            # Iterate over this Character's items.
            for item in self.items:

                # If the ItemInstance is the same as the ItemInstance being
                # stacked, or if the names of the items are different, continue
                # to the next item.
                if sitem == item or sitem.name != item.name:
                    continue

                # The item being iterated over may possible stack with the item
                # attempting to be stacked.  Calculate how many items the
                # iterated item can hold.
                freeStack = stackMax - item.stackCount

                # If the item holds no more items, then it has the max stack
                # count.  It will not stack with the item attempting to be
                # stacked, so continue to the next item.
                if freeStack <= 0:
                    continue

                # If the iterated item holds more items than the attempting
                # to stack item has, just use the items available.  Otherwise,
                # the item to stack has more items, and the iterated item
                # should only use the count of items it can hold.
                if freeStack > neededStack:
                    freeStack = neededStack

                # Store the iterated item and the count of items being added
                # to the item.
                stacking[item] = freeStack

                # Subtract the items that might be added to the iterated item
                # from count of items stil needing to be stacked.
                neededStack -= freeStack

                # If there are no more items needing stacked, then the item
                # attempting to be stacked can be completely stacked, so exit
                # the loop.
                if neededStack <= 0:
                    break

            # Otherwise, all items have been iterated over and some items still
            # remain unstacked, so the item did not successfully stack.
            else:

                # Return False to indicate stacking did not occur.
                return False

            # Iterate over items that stacked with the item attempting to be
            # stacked, adjusting and refreshing the stack count for each item.
            for item,count in stacking.iteritems():

                # Update the stack count.
                item.stackCount += count

                # Refresh ItemInfo so observing clients see the items new stack
                # count.
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})

            # Return True as the item succesfully stacked.
            return True


    ## @brief Loots an ItemInstance from a Mob.
    #  @param self (Character) The object pointer.
    #  @param mob (Mob) The mob who is being looted.
    #  @param slot (Integer) The loot slot clicked.
    #  @param alt (Boolean) Indicates if alt-click occured.
    #  @return None.
    #  @todo TWS: Consider making a quick hande to mob.loot.items.
    def onLoot(self, mob, slot, alt=False):

        # This Character attempted to loot a slot no longer containing an item.
        # This may occur if the player's client had not received a loot table
        # update since the last loot call.
        if not mob.loot or len(mob.loot.items) <= slot:
            return

        # Get the item attempting to be looted.
        item = mob.loot.items[slot]

        # Get the item's slot.
        mslot = item.slot

        # The player alt-clicked the loot item.  Try to quick-loot, placing the
        # item into this Character's inventory, attempting to stack if possible.
        if alt:

            # Attempt to stack the item.
            if self.stackItem(item):

                # The item completely stacked with items already in this
                # Character's inventory so destroy the item.
                item.destroySelf()

            # The item failed to completely stack, so attempt to give this
            # Character the item.
            else:

                # Attempt to give the item instance to this Player.  If it
                # fails, then there are no free inventory slots, so inform the
                # Player and return early.
                if not self.player.giveItemInstance(item):

                    # Inform the Player.
                    self.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s has no free inventory slots!\n'%self.name)

                    # Return early.
                    return

                # If the item has an invalid slot, then something has gone
                # wrong.  Print traceback information, but continue with
                # execution because the mob still needs clean up.
                if item.slot == -1:

                    # Print a traceback that may provide some useful debug
                    # information.
                    traceback.print_stack()
                    print "AssertionError: item owner whackiness!"

        # The Player single-clicked the loot item, try to put the item into
        # players cursor.
        else:

            # There is no check for lost cursor item.  They will appear once
            # the Player puts down the current item.

            # If the Player has an item currently on the cursor, then inform the
            # Player and return early.
            if self.player.cursorItem:

                # Inform the Player.
                self.player.sendGameText(RPG_MSG_GAME_DENIED,r'Put down the item in %s\'s cursor first!\n'%self.name)

                # Return early.
                return

            # There was no cursor item, so the item being looted will be placed
            # on the cursor.

            # Set the item's owner as this Character, updating the item's stats
            # based on this Character.
            item.setCharacter(self)

            # Update the looted item's slot to the cursor.
            item.slot = RPG_SLOT_CURSOR

            # Set the looted item onto the Player's cursor.
            self.player.cursorItem = item

            # Update the client's cursor item.
            self.player.updateCursorItem(None)

        # If the mob had the looted item equipped, unequip it so that the corpse
        # simulation will be display the item being looted from the mob.
        # TWS: This could probably be in the final else statement where the loot
        # table is updated.
        if mslot != -1:

            # Unequip the item from the mob being looted.
            # TWS: Can a light weight unequip be done?  Is this specifically for
            # simulation updates?  If so, this should be in the below if statement.
            mob.unequipItem(mslot)

            # Only refresh if mob has more items because the corpse is going to
            # pop.
            if len(mob.loot.items) > 1:

                # Refresh the mob's SimMobInfo, as the looted item was equipped
                # and therefore visible.  Thus, removing the item needs
                # simulation data to be resent.
                mob.mobInfo.refresh()

        # Update the dead mob's loot table, removing the item that has been
        # looted.
        mob.loot.items.remove(item)

        # Handle items unique to the world.
        if item.itemProto.flags&RPG_ITEM_WORLDUNIQUE:

            # Inform all players on the world about the world unique item that
            # has been looted.
            for p in self.player.world.activePlayers:
                p.sendGameText(RPG_MSG_GAME_BLUE,r'%s has looted the sought-after <a:Item%s>%s</a>.\n'%(item.character.name,GetTWikiName(item.itemProto.name),item.name))

        # Otherwise, just inform this Player's Alliance about the item that has
        # been looted.
        else:
            self.player.alliance.lootMessage(self.player,item)

        # If all the items have been looted from the mob, remove the Mob from
        # the ZoneInstance.
        if not len(mob.loot.items):

            # Inform this Player that the corpse is disappearing.
            self.player.sendGameText(RPG_MSG_GAME_LOOT,r'As %s takes the last item, the corpse crumbles to dust!\n'%self.name)

            # Remove the mob from the ZoneInstance.
            mob.zone.removeMob(mob)

        # Otherwise, an updated loot table needs sent to the client.
        else:

            # Create a dictionary containing an index (key) and ItemInfo (value)
            # pair.
            loot = dict((x,item.itemInfo) for x,item in enumerate(mob.loot.items))

            # Send the dictionary to the client.  This will create ItemInfoGhost
            # on the client which will observe the ItemInfo for the loot table.
            self.player.mind.callRemote("setLoot",loot)


    ## @brief Recovers death experience for the Character.
    #  @param self (Character) The object pointer.
    #  @param xpRecover (Float) Percent of death experience recovered.
    #  @return None.
    #  @todo TWS: xpRecover should probably be renamed to be more specific to
    #        what it does.
    def recoverDeathXP(self, xpRecover):

        # Calculate the experience to recover based on the experience lost and
        # the xpRecover percent modifier.
        pxp = int(self.xpDeathPrimary*xpRecover)
        sxp = int(self.xpDeathSecondary*xpRecover)
        txp = int(self.xpDeathTertiary*xpRecover)

        # If any class is receiving ressurection experience, have this
        # Character gain the experience.
        if pxp or sxp or txp:

            # Build tuple with the experience amount to recover for each class.
            # TWS: Should probably be done in the gainXp call, no need to assign
            # a name and then only use it once immediately afterwards.
            rez = (pxp,sxp,txp)

            # Set this Character to gain the ressurection experience without
            # clamping the experience.
            self.gainXP(1,False,rez)

        # Reset the death experience values.  This prevents the Character from
        # receiving experience multiple times from multiple ressurections for
        # the same death.
        # TWS: Should death experience be reset ONLY when experience was
        # recovered?  This would let no-experience rez spells be used without
        # destroying the chance for an experience rez later.

        ## @brief (Persistent Integer) Amount of experience the Character's
        #         primary class lost from the most recent death.
        self.xpDeathPrimary = 0

        ## @brief (Persistent Integer) Amount of experience the Character's
        #         secondary class lost from the most recent death.
        self.xpDeathSecondary = 0

        ## @brief (Persistent Integer) Amount of experience the Character's
        #         tertiary class lost from the most recent death.
        self.xpDeathTertiary = 0

        # If no experience was gained, just inform the Player of the
        # resurrection and return.
        # TWS: This could be the else if the above if statement.
        if not pxp and not sxp and not txp:
            self.player.sendGameText(RPG_MSG_GAME_GOOD,"%s has been resurrected!\\n"%self.name)
            return

        # Inform the Player if some experience was gained.
        # TWS: This could be put in the the area where gainXP is called.
        self.player.sendGameText(RPG_MSG_GAME_GOOD,"%s has been resurrected and regained some lost experience!\\n"%self.name)


    ## @brief Resurrects the Character to the Character's death marker, possible
    #         causing the Player to transferred between ZoneInstances.  This
    #         resurrection may recover a percent of experience, and some health,
    #         mana, and stamina.
    #  @details The Character that the resurrection has been casted on does not
    #           have to be currently dead, but must have previously died.
    #  @param self (Character) The object pointer.
    #  @param xpRecover (Float) Percent of death experience recovered.
    #  @param healthRecover (Integer) The amount of health the Character will
    #         recover from the resurrection.
    #  @param manaRecover (Integer) The amount of mana the Character will
    #         recover from the resurrection.
    #  @param staminaRecover (Integer) The amount of stamina the Character will
    #         recover from the resurrection.
    #  @return None.
    #  @todo TWS: The health, mana, and stamina recovery should probably be
    #        percents or be abe to be treated as
    #  @todo TWS: Remove the inline import!
    #  @todo TWS: Check if it is easier to assign, then if/assign vs.
    #        if/assign/else/assign.
    def playerResurrect(self, xpRecover, healthRecover, manaRecover, staminaRecover):

        # The Character ins being resurrected, so remove the death marker from
        # the World.
        self.player.world.clearDeathMarker(self.player)

        # Recover experience for this Character.
        self.recoverDeathXP(xpRecover)

        # Make a local handle to Zone in which this Character had died.
        # TWS: dz is only used once, so this should probably not use a local
        # variable.  It is saved off right now because it is cleared immediately
        # afters, but the clear could occur elsewhere.
        dz = self.deathZone

        # Clear this Character's death Zone.
        self.deathZone = None

        # Make a local reference to this Character's Mob.
        mob = self.mob

        # This Character is being resurrected, and will respawn with at least
        # one health, so flag this Character as not dead.
        ## @brief (Persistent Boolean) Flag indicating if the Character is dead.
        self.dead = False


        # If an amount of heath to recover was provided, then recover some of
        # this Character's health.
        if healthRecover:

            # Set this Character's Mob's health to the amount of health being
            # recovered.
            mob.health = healthRecover

            # If the health recovered is greater than the max health, then clamp
            # the health to be that of the max health.
            if mob.health > mob.maxHealth:
                mob.health = mob.maxHealth

        # The resurrection is not providing health, so set this Character's
        # Mob's health to 1.
        else:
            mob.health = 1

        # This Character may be transported across ZoneInstances, so store the
        # whole integer amount of health recovered to this Character for
        # persistence.  This important because the Mob data is not persistent.
        self.health = int(mob.health)


        # If an amount of mana to recover was provided, then recover some of
        # this Character's mana.
        if manaRecover:

            # Set this Character's Mob's mana to the amount of mana being
            # recovered.
            mob.mana = manaRecover

            # If the mana recovered is greater than the max mana, then clamp
            # the mana to be that of the max mana.
            if mob.mana > mob.maxMana:
                mob.mana = mob.maxMana

        # The resurrection is not providing mana, so set this Character's
        # Mob's mana to 1.
        else:
            mob.mana = 1

        # This Character may be transported across ZoneInstances, so store the
        # whole integer amount of mana recovered to this Character for
        # persistence.  This important because the Mob data is not persistent.
        self.mana = int(mob.mana)


        # If an amount of stamina to recover was provided, then recover some of
        # this Character's stamina.
        if staminaRecover:

            # Set this Character's Mob's stamina to the amount of stamina being
            # recovered.
            mob.stamina = staminaRecover

            # If the stamina recovered is greater than the max stamina, then
            # clamp the stamina to be that of the max stamina.
            if mob.stamina > mob.maxStamina:
                mob.stamina = mob.maxStamina

        # The resurrection is not providing stamina, so set this Character's
        # Mob's stamina to 1.
        else:
            mob.stamina = 1

        # This Character may be transported across ZoneInstances, so store the
        # whole integer amount of stamina recovered to this Character for
        # persistence.  This important because the Mob data is not persistent.
        self.stamina = int(mob.stamina)


        # If the Player is currenty in the Zone in which this Character had
        # died, then respawn the Player.
        if dz == self.player.zone.zone:

            # Respawn the Player in the current ZoneInstance at the location
            # of where this Character died.
            self.player.zone.respawnPlayer(self.player,self.deathTransformInternal)

        # The Player is not in the Zone in which this Character had died, so the
        # Player needs to transfered to another ZoneInstance.
        else:
            
            # TWS: This inline import neesd to be moved to be global.
            from zone import TempZoneLink

            # Create a temporary zone link (TempZoneLink) to the Zone and
            # location at which this Character had died.
            zlink = TempZoneLink(dz.name,self.deathTransformInternal)

            # Force the Player to transport between zones, triggering the
            # temporary zone link.
            self.player.world.onZoneTrigger(self.player,zlink)


    ## @brief Resurrects a dead Character, recovering a percent of experience.
    #         This will not cause a Player to be transferred to the Character's
    #         death marker or between ZoneInstances.
    #  @details The Character that the resurrection has been casted on must be
    #           dead.
    #  @param self (Character) The object pointer.
    #  @param xpRecover (Float) Percent of death experience recovered.
    #  @return None.
    #  @todo TWS: Should health, mana, and stamina recover be provided as well?
    #        Or should the caller ber responsibe.
    def resurrect(self, xpRecover):

        # If this Character is not dead, then this Character does not need
        # resurrected.
        if not self.dead:
            return

        # This Character is being resurrected, so disable auto attack.
        self.mob.autoAttack = False

        # Flag this Character as no longer being dead.
        self.dead = False

        # Set this Character's Mob's health, mana, and stamina to 1.  This
        # prevents the Character's Mob to start with zero or negative health
        # when being reattached.  Otherwise, the Mob would immediately die.
        self.mob.health = 1
        self.mob.mana = 1
        self.mob.stamina = 1

        # Reattach the Mob to the ZoneInstance.  This will set the Mob as an
        # active mob, so that mob management routines will occur.
        self.mob.zone.reattachMob(self.mob)

        # Recover experience that this Character had lost from a previous death.
        self.recoverDeathXP(xpRecover)


    ## @brief Removes experience from the Character.
    #  @param self (Character) The object pointer.
    #  @param factor (Float) Multiplier affecting the amount of experience lost.
    #  @param death (Boolean) Indicates if the source of the experience lost is
    #               from a death.
    #  @return None.
    #  @todo TWS: Experience calculations need to be calculated once.
    #  @todo TWS: The experience lost calculation could be changed to not have
    #        to account for the .8 multiplier each time.  Factor should probably
    #        be a bit more meaningful.
    def loseXP(self, factor=1.0, death=True):

        # Make a local handle to this Character's Player and Spawn.
        player = self.player
        spawn = self.spawn

        # Calculate total experience needed to level for each class.
        pneeded = spawn.plevel*spawn.plevel*100L*self.pxpMod
        sneeded = spawn.slevel*spawn.slevel*100L*self.sxpMod
        tneeded = spawn.tlevel*spawn.tlevel*100L*self.txpMod

        # Calculate the previous level's total experience needed to level for
        # each class.
        pprevneeded = ((spawn.plevel-1)*(spawn.plevel-1)*100L*self.pxpMod)
        sprevneeded = ((spawn.slevel-1)*(spawn.slevel-1)*100L*self.sxpMod)
        tprevneeded = ((spawn.tlevel-1)*(spawn.tlevel-1)*100L*self.txpMod)

        # Calculate how much experience is required to level each class.
        pgap = pneeded - pprevneeded
        sgap = sneeded - sprevneeded
        tgap = tneeded - tprevneeded

        # Calculate the amount of experience lost per class.
        pxploss = pgap/(spawn.plevel*2)
        sxploss = 0
        txploss = 0

        if spawn.slevel:
            sxploss = sgap/(spawn.slevel*2)
        if spawn.tlevel:
            txploss = tgap/(spawn.tlevel*2)

        # Modify the amount of experience lost per class.
        pxploss = int(pxploss*.8*factor)
        sxploss = int(sxploss*.8*factor)
        txploss = int(txploss*.8*factor)

        # TWS: Use spawn.plevel instead.  This should probably be at the
        # beginning of the function and return early.
        # Character's with a primary level below 5 do not lose experience, so
        # set the experience loss to be 0.
        if self.spawn.plevel < 5:
            pxploss = sxploss = txploss = 0


        # The losses list will store strings representing the amount of
        # experience lost.  This is used for creating the output message that
        # will be sent to the Player.
        losses = []

        # Populate the losses list based on the amount of experience lost per
        # class.
        # TWS: This should probably be done after xploss values are completely
        # calculated and right before the Player output.
        if pxploss and self.xpPrimary:
            losses.append(str(pxploss))
        if sxploss and self.xpSecondary:
            losses.append(str(sxploss))
        if txploss and self.xpTertiary:
            losses.append(str(txploss))

        # Calcupate this Character's reduced experience per class.
        # TWS: This should probably by an if/else for each in order to prevent
        # having to do an if on each one later to prevent negative experience.
        pxp = int(self.xpPrimary - pxploss)
        sxp = int(self.xpSecondary - sxploss)
        txp = int(self.xpTertiary - txploss)

        # TWS: This print if/else block could be moved soomewhere else, it kind
        # of obstructs the linear flow of experience calculations.
        # If the Character died.  It should probably go at the end too, as
        # xposs variables can change.
        if death:

            # If this Character lost experience, inform the Player of how much
            # experience was lost.
            if len(losses):
                player.sendGameText(RPG_MSG_GAME_CHARDEATH,"%s has died and lost %s experience!!\\n"%(self.name,'/'.join(losses)))

            # Otherwise, no experience lost occured.  Inform the Player of the
            # death.
            else:
                player.sendGameText(RPG_MSG_GAME_CHARDEATH,"%s has died!!\\n"%self.name)

        # Otherwise, the Character did not die, but is losing experience.
        else:
            # TWS: Somewhat unsafe.  Losses could be empty!
            player.sendGameText(RPG_MSG_GAME_CHARDEATH,"%s has lost %s experience!!\\n"%(self.name,'/'.join(losses)))

        # Characters cannot go negative in experience, so check if the reduce
        # experience amount is below zero.  If it is, set the amount of
        # experience to be lost equal to the amount of experience the class
        # has obtained and set the reduced experience to be zero.
        if pxp < 0:
            pxploss = self.xpPrimary
            pxp = 0
        if sxp < 0:
            sxploss = self.xpSecondary
            sxp = 0
        if txp < 0:
            txploss = self.xpTertiary
            txp = 0

        # Store the amount of experience lost this Character lost, as it may be
        # recovered from a resurrection.
        self.xpDeathPrimary = pxploss
        self.xpDeathSecondary = sxploss
        self.xpDeathTertiary = txploss

        # Set this Character's experience to the reduced experience.

        # Required to prevent doxygen warning:
        ## @var xpPrimary
        #  @brief (Persistent Integer) Total amount of experience for the
        #         Character's primary class.
        
        ## @brief (Persistent Integer) Total amount of experience for the
        #         Character's primary class.
        self.xpPrimary = int(pxp)

        ## @brief (Persistent Integer) Total amount of experience for the
        #         Character's secondary class.
        self.xpSecondary = int(sxp)

        ## @brief (Persistent Integer) Total amount of experience for the
        #         Character's tertiary class.
        self.xpTertiary = int(txp)


        # This Character may have lost enough experience to have lost one or
        # more levels.  To determine this, for each class, the experience
        # required by previous levels needs to be compared to the current
        # reduced experience, until the current reduced experience is greater
        # than or equal to the amount of experience a level requires.

        # Flag used to indicate if a level was lost.
        lost = False

        # Dictioanry used to provide a grammatical number string in messages
        # that will be sent to the Player.
        selector = {True: 's', False: ''}

        # Count of levels  lost.
        lostLevels = 0

        # Find the previous primary level.
        prevLevel = spawn.plevel - 1

        # Calculate level loss as long as the reduced experience for primary
        # is less than the experience required for the previous primary level,
        # and the previous level is greater than zero.
        while pxp < pprevneeded and prevLevel > 0:

            # Increase the count of levels lost.
            lostLevels += 1

            # Decrease the previous level.
            prevLevel -= 1

            # Calculate the new previous level's total experience required for
            # the level.
            pprevneeded = (prevLevel*prevLevel*100L*self.pxpMod)

        # If levels have been lost, then this Character's Spawn needs updated.
        if lostLevels:

            # Set flag to indicate at least one level was lost.
            lost = True

            # Decrease this Character's Spawn'slevel.
            # TWS: What is spawn.level?
            spawn.level -= lostLevels

            # Decrease this Character's Spawn's's primary level.
            spawn.plevel -= lostLevels

            # Inform the Player.
            self.player.sendGameText(RPG_MSG_GAME_LEVELLOST,"%s has lost %i primary level%s in the <a:Class%s>%s</a> class.\\n"%(self.name,lostLevels,selector[lostLevels>1],GetTWikiName(spawn.pclassInternal),spawn.pclassInternal))


        # Reset the count of levels lost.
        lostLevels = 0

        # Find the previous secondary level.
        prevLevel = spawn.slevel - 1

        # Calculate level loss as long as the reduced experience for secondary
        # is less than the experience required for the previous secondary level,
        # and the previous level is greater than zero.
        while sxp < sprevneeded and prevLevel > 0:

            # Increase the count of levels lost.
            lostLevels += 1

            # Decrease the previous level.
            prevLevel -= 1

            # Calculate the new previous level's total experience required for
            # the level.
            sprevneeded = (prevLevel*prevLevel*100L*self.sxpMod)

        # If levels have been lost, then this Character's Spawn needs updated.
        if lostLevels:

            # Set flag to indicate at least one level was lost.
            lost = True

            # Decrease this Character's Spawn's's secondary level.
            spawn.slevel -= lostLevels

            # Inform the Player.
            self.player.sendGameText(RPG_MSG_GAME_LEVELLOST,"%s has lost %i secondary level%s in the <a:Class%s>%s</a> class.\\n"%(self.name,lostLevels,selector[lostLevels>1],GetTWikiName(spawn.sclassInternal),spawn.sclassInternal))

        # Reset the count of levels lost.
        lostLevels = 0

        # Find the previous tertiary level.
        prevLevel = spawn.tlevel - 1

        # Calculate level loss as long as the reduced experience for tertiary
        # is less than the experience required for the previous tertiary level,
        # and the previous level is greater than zero.
        while txp < tprevneeded and prevLevel > 0:

            # Increase the count of levels lost.
            lostLevels += 1

            # Decrease the previous level.
            prevLevel -= 1

            # Calculate the new previous level's total experience required for
            # the level.
            tprevneeded = (prevLevel*prevLevel*100L*self.txpMod)

        # If levels have been lost, then this Character's Spawn needs updated.
        if lostLevels:

            # Set flag to indicate at least one level was lost.
            lost = True

            # Decrease this Character's Spawn's's tertiary level.
            spawn.tlevel -= lostLevels

            # Inform the Player.
            self.player.sendGameText(RPG_MSG_GAME_LEVELLOST,"%s has lost %i tertiary level%s in the <a:Class%s>%s</a> class.\\n"%(self.name,lostLevels,selector[lostLevels>1],GetTWikiName(spawn.tclassInternal),spawn.tclassInternal))

        # This Character lost experience or even eves, so update display
        # percents.
        self.calcXPPercents()

        # If the lost flag is set, then at least one level was lost.  The mob
        # needs updated since the level change.  This will update stats, items,
        # and provide updates to the Player.
        if lost:
            self.mob.levelChanged()


    ## @brief Adds StartingGear and PlayerXPCredits to a Character's inventory.
    #  @param self (Character) The object pointer.
    #  @return None.
    #  @todo TWS: Optimize.  Proper select could be used, but some looping
    #        could be handled better.  The usedslots should use a set to allow
    #        for hash checks instead of linear checks.
    def addStartingGear(self):

        # The initial slot to use is the first carry slot.
        slot = RPG_SLOT_CARRY0

        # List containg slots used when adding StartingGear to this Character.
        usedslots = []

        # Get a list of StartingGear.
        sgear = list(StartingGear.select())

        # Iterate over StartingGear.
        for sg in sgear:

            # Check if this Character's Spawn qualifies for the StartingGear.
            if sg.items != "" and sg.qualify(self.spawn):

                # Get a list of item names.
                inames = sg.items.split(',')

                # Iterate over the item names.
                for iname in inames:

                    # Get the ItemProto based on the name provided by the
                    # StartingGear.
                    iproto = ItemProto.byName(iname)

                    # Create an ItemInstance from the StartingGear.
                    item = iproto.createInstance()

                    # Set the initial item slot to be invalid.
                    item.slot = -1

                    # Iterate over slots in which the item may be equipped.
                    for islot in iproto.slots:

                        # If the slot has not been used, then use the slot.
                        if islot not in usedslots:
                            # Removed in 1.3 SP2 for now.
                            """
                            # If there is no dual wield skill then don't allow for the secondary weapon slot.
                            if islot == RPG_SLOT_SECONDARY and not "Dual Wield" in self.skills:
                                break

                            # Don't wear a secondary weapon and a shield together.
                            if islot == RPG_SLOT_SECONDARY and RPG_SLOT_SHIELD in usedslots:
                                break
                            if islot == RPG_SLOT_SHIELD and RPG_SLOT_SECONDARY in usedslots:
                                break

                            # Scan for wearability conflicts.
                            wear_item = True
                            for iitem in self.items:
                                # If there is already a secondary weapon, a shield
                                # or a 2H weapon equipped then don't wear another 2H weapon.
                                if (iitem.slot == RPG_SLOT_SECONDARY) or (iitem.slot == RPG_SLOT_SHIELD) or \
                                   (iitem.slot == RPG_SLOT_PRIMARY and "2H" in iitem.skill):
                                    if "2H" in item.skill:
                                        wear_item = False
                                        break
                                # If there is already a 2H weapon equipped then don't wear a shield.
                                if iitem.slot == RPG_SLOT_PRIMARY and "2H" in iitem.skill:
                                    if item.skill == "Shields":
                                        wear_item = False
                                        break

                            # Exit the loop if the item is not allowed to be weared.
                            if not wear_item:
                                break
                            """
                            # Set the item to use the available slot.
                            item.slot = islot

                            # Add the slot to the used slot list.
                            usedslots.append(islot)

                            # Exit the loop, as the item has been assigned a
                            # new slot.
                            break

                    # If the item was not assigned a new slot, then give it a
                    # carry slot.
                    if item.slot == -1:

                        # Set the item to use a carry slot.
                        item.slot = slot

                        # Set the next slot to be assigned to be the the next
                        # carry slot.
                        slot += 1

                    # Set the item's owner as this Character, updating the
                    # item's stats based on this Character.
                    item.setCharacter(self)


        # Check if the Player has any PlayerXPCredits.
        credits = list(self.player.xpCredits)

        # If the Player has experience credits, then the credits need to be
        # created.
        if len(credits):

            # Get the ItemProto for the experience credits.
            iproto=ItemProto.byName("Certificate of Experience")

            # Iterate over the credits.
            for cr in credits:

                # Create an ItemInstance for the experience credit.
                credit = iproto.createInstance()

                # Provide a description for the ItemInstancem, stating the
                # amount of experience points the credit provides.
                credit.descOverride = "This certificate grants it's user %i experience points."%cr.xp

                # Set the experience amount the credit provides.
                credit.xpCoupon = cr.xp

                # Set the credits's owner as this Character, updating the
                # credit's stats based on this Character.
                credit.setCharacter(self)

                # Set the item to use a carry slot.
                credit.slot = slot

                # Set the next slot to be assigned to be the the next
                # carry slot.
                slot+=1

                # The Character has received the experience credit, so destroy
                # the PlayerXPCredit.  This prevents the same PlayerXPCredit
                # credit to be awarded multiple times.
                cr.destroySelf()

                # If the next slot that will be assigned is the end carry slot,
                # then exit the loop as there is no more room to place the
                # credits.
                if slot == RPG_SLOT_CARRY_END:
                    break


    ## @brief Checks if the Character has enough free carry slots.
    #  @param self (Character) The object pointer.
    #  @param numItems (Integer) Number of free carry slots needed.
    #  @return (Boolean) True if the Character has equal to or more than the
    #          number of free carry slots needed.  Otherwise, False.
    #  @todo TWS: Optimize.  getFreeCarrySlots may be better.
    def checkGiveItems(self, numItems):

        # If there are free slots required, then check this Character's
        # inventory.
        if numItems:

            # Count of carry slots being used.
            usedslots = 0

            # Iterate over this Character's items.
            for item in self.items:

                # If the item is in a carry slot, then increment the count of
                # used carry slots.
                if RPG_SLOT_CARRY_END > item.slot >= RPG_SLOT_CARRY_BEGIN:
                    usedslots += 1

            # Get the count of free slots.
            freeslots = (RPG_SLOT_CARRY_END - RPG_SLOT_CARRY_BEGIN) - usedslots

            # If the number of free carry slots needed is more than the number
            # of free slots actually available, then inform the Player and
            # return False.
            if freeslots < numItems:

                # Inform the Player.
                self.player.sendGameText(RPG_MSG_GAME_DENIED,"%s needs %i free inventory spaces.\\n"%(self.name,numItems))

                # Return False as this Character does not have enough free
                # carry slots.
                return False

        # Return True as this Character has equal to or more than enough free
        # carry slots.
        return True


    ## @brief Gives ItemInstances to the Character.
    #  @param self (Character) The object pointer.
    #  @param itemProtos (ItemProto List) List of ItemProtos for Items being
    #         given to the Character.
    #  @param counts (Integer List) List of Integer indicating the quantity of
    #         items being given for each ItemProto.
    #  @return None.
    #  @todo TWS: Handle item stacking.
    #  @todo TWS: for/else logic, lots of wasted iterations too.
    def giveItemProtos(self, itemProtos, counts):

        # Make a local handle to this Character's Player.
        player = self.player

        # Iterate over ItemProtos and Counts.
        for proto,count in zip(itemProtos,counts):

            # For each count associated with the item, create an ItemInstance
            # and place it in a carry slot.
            for c in xrange(0,count):

                # Create an ItemInstance from the ItemProto.
                item = proto.createInstance()

                # Carry slot in which the item will be placed.
                slot = None

                # Iterate over slots, attempting to find a free carry slot.
                for x in xrange(RPG_SLOT_CARRY_BEGIN,RPG_SLOT_CARRY_END):

                    # Iterate over this Character's items.
                    for sitem in self.items:

                        # If the item was in the carry slot, then set the flag
                        # to indicate that an item was found in the slot.
                        if x == sitem.slot:

                            # Exit the loop as an item is in the slot.
                            break

                    # If no item was found in the slot, then the slot is empty.
                    else:

                        # Use the empty slot.
                        slot = x

                        # Exit the loop, as a slot was found.
                        break

                # If no slot was empty, then print debug information and exit
                # the method.
                if not slot:

                    # Print debug information.
                    traceback.print_stack()
                    print "AssertionError: no slot found!"

                    # Return early.
                    return

                # Set the item to use a carry slot.
                item.slot = slot

                # Set the item's owner as this Character, updating the item's
                # stats based on this Character.
                item.setCharacter(self)

                # Inform the Player of the item this Character has gained.
                player.sendGameText(RPG_MSG_GAME_GAINED,"%s has gained <a:Item%s>%s</a>!\\n"%(self.name,GetTWikiName(proto.name),item.name))


    ## @brief Takes ItemInstances from the Character.
    #  @param self (Character) The object pointer.
    #  @param itemDict (Dictionary) ItemProtos (key) and counts (value) to take
    #                  from the Character.
    #  @param silent (Boolean) Indicates if the Player will receive a message if
    #                items are taken.
    #  @return None.
    def takeItems(self, itemDict, silent=False):
        
        # Do some sanity check on the item requirements.
        # Don't use iteritems so we iterate over a copy.
        for proto,count in itemDict.items():
            if count <= 0:
                del itemDict[proto]
        
        # If the item dictionary is empty, return early.
        if not len(itemDict):
            return
        
        # Create a dictionary to hold the items actually taken away.
        # Normally this would be the same as itemDict, but let's create
        #  a new one just to be on the safe side.
        # The dictionary will only be needed if we give feedback to the
        #  player though.
        if not silent:
            lostItems = defaultdict(int)
        
        # Iterate over a copy of this Character's items since the item list
        #  will get modified during the iteration.
        for item in self.items[:]:
            
            # If the item is in a trade slot, continue to the next item.
            if RPG_SLOT_TRADE_END > item.slot >= RPG_SLOT_TRADE_BEGIN:
                continue
            
            # If the item is in a loot slot, continue to the next item.
            if RPG_SLOT_LOOT_END > item.slot >= RPG_SLOT_LOOT_BEGIN:
                continue
            
            # If this item is a container, check its contents.
            if item.container:
                
                # Run through all items in the container. Make a copy because
                #  contents might get modified.
                for citem in item.container.content[:]:
                    
                    # Get a handle to the current container item's item proto.
                    citemProto = citem.itemProto
                    
                    # Get the amount of items we need of this specific
                    #  item proto.
                    countNeeded = itemDict.get(citemProto,None)
                    
                    # If we don't need any, skip to the next content item.
                    if not countNeeded:
                        continue
                    
                    # Get the count of items on the stack.
                    sc = citem.stackCount
                    
                    # If there is no stack count, then set a minimum to 1.
                    if not sc:
                        sc = 1
                    
                    # If there are more items in the stack than the amount
                    #  needed, set sc to be equal to the amount of items being
                    #  taken.
                    if sc > countNeeded:
                        sc = countNeeded
                    
                    # Reduce the item's stack count.
                    citem.stackCount -= sc
                    
                    # If there are no more items on the stack, then the item
                    #  needs to be destroyed.
                    if citem.stackCount <= 0:
                        
                        # Remove the ItemInstance from the container.
                        item.container.extractItem(citem)
                        
                        # The ItemInstance is being taken from the Player, so
                        #  destroy the Item.
                        citem.destroySelf()
                    
                    # Otherwise, the stack still has items.
                    else:
                        
                        # Refresh ItemInfo so observing clients see the new
                        #  stack count.
                        citem.itemInfo.refreshDict({'STACKCOUNT':citem.stackCount})
                    
                    # Add the items taken away to the dictionary holding the
                    #  lost items if we're gonna give feedback to the player.
                    if not silent:
                        lostItems[citemProto] += sc
                    
                    # If the requirement was only partially satisfied, decrement
                    #  the needed amount and continue to the next content item.
                    if sc < countNeeded:
                        itemDict[citemProto] -= sc
                        continue
                    
                    # Otherwise the requirement was completely satisfied, so
                    #  remove it from the item dictionary.
                    del itemDict[citemProto]
                    
                    # Check if there actually are more items to be checked for
                    #  and exit the loop over the container contents otherwise.
                    if not len(itemDict):
                        break
                
                # Check again if all items were taken away by iterating over
                #  the container and exit the loop over the Character's items
                #  if so.
                if not len(itemDict):
                    break
            
            # Get a handle to the current item's item proto.
            itemProto = item.itemProto
            
            # Get the amount of items we need of this specific
            #  item proto.
            countNeeded = itemDict.get(itemProto,None)
            
            # If we don't need any, skip to the next item.
            if not countNeeded:
                continue
            
            # Get the count of items on the stack.
            sc = item.stackCount
            
            # If there is no stack count, then set a minimum to 1.
            if not sc:
                sc = 1
            
            # If there are more items in the stack than the amount
            #  needed, set sc to be equal to the amount of items being
            #  taken.
            if sc > countNeeded:
                sc = countNeeded
            
            # Reduce the item's stack count.
            item.stackCount -= sc
            
            # If there are no more items on the stack, then the item
            #  needs to be destroyed.
            if item.stackCount <= 0:
                
                # The ItemInstance is being taken from the Player, so
                #  destroy the Item.
                item.destroySelf()
            
            # Otherwise, the stack still has items.
            else:
                
                # Refresh ItemInfo so observing clients see the new
                #  stack count.
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})
            
            # Add the items taken away to the dictionary holding the
            #  lost items if we're gonna give feedback to the player.
            if not silent:
                lostItems[itemProto] += sc
            
            # If the requirement was only partially satisfied, decrement
            #  the needed amount and continue to the next item.
            if sc < countNeeded:
                itemDict[itemProto] -= sc
                continue
            
            # Otherwise the requirement was completely satisfied, so
            #  remove it from the item dictionary.
            del itemDict[itemProto]
            
            # Check if there actually are more items to be checked for
            #  and exit the loop over the Character's items otherwise.
            if not len(itemDict):
                break
        
        # All items in the item dictionary that could be taken away from this
        #  Character now have been taken away.
        
        # If output is not disabled, inform the Player of the items lost.
        if not silent:
            self.player.sendGameText(RPG_MSG_GAME_LOST,"%s lost %s.\\n"%(self.name,', '.join('<a:Item%s>%i %s</a>'%(GetTWikiName(ip.name),c,ip.name) for ip,c in lostItems.iteritems())))
        
        # Flag the Player as having a dirty Character. This will have the
        #  ZoneInstance send a full CharacterInfo refresh to the Player.
        self.player.cinfoDirty = True


    ## @brief Gives an ItemInstance to a Character.  Placing it in a carry slot,
    #         equipping it, or moving it to the Player's cursor if possible.
    #  @param self (Character) The object pointer.
    #  @param item (ItemInstance) The ItemInstance being given to the Character.
    #  @return (Boolean) True if the item was given to the Character.
    #          Otherwise, False.
    def giveItemInstance(self, item):

        # Get a list of free carry slots.
        freeSlots = self.getFreeCarrySlots()

        # If there is at least one free carry slot, then place the item into
        # the free slot.
        if len(freeSlots):

            # Set the item to use the first free carry slot.
            item.slot = freeSlots[0]

            # Set the item's owner as this Character, updating the item's
            # stats based on this Character.
            item.setCharacter(self)

            # Return True as this Character was successfully given the item,
            # placing the item in a free carry slot.
            return True

        # If this Character can equip the item, then attempt to equip the item.
        if item.isUseable(self.mob):
            
            # Back up the item slot.
            backupSlot = item.slot

            # Set the slot to be invalid, this allows for detection if the
            # item was equipped.
            item.slot = -1

            # Attempt to equip the item on this Character.
            # TWS: equipItem should probably return true or false.
            self.equipItem(item)

            # If the item was equipped, then the item's slot would have been
            # changed.
            if item.slot != -1:

                # Set the item's owner as this Character, updating the item's
                # stats based on this Character
                item.setCharacter(self)

                # Return True as this Character was successfully given the item,
                # equipping the item in a worn slot.
                return True
            
            # Item couldn't be equipped, so restore the original item slot.
            item.slot = backupSlot

        # This Character has no free carry slots and could not equip the item,
        # so attempt to place the item on the Player's cursor.


        # Iterate over this Character's items.
        # TWS: Is the looping required or can the player.cursorItem be checked?
        for ownedItems in self.items:

            # If an item is on the cursor slot, then exit the loop.
            if ownedItems.slot == RPG_SLOT_CURSOR:
                break

        # If the for loop exits normally, then no item is on the cursor.
        else:

            # Set the item's slot to be that of the cursor.
            item.slot = RPG_SLOT_CURSOR

            # Set the item's owner as this Character, updating the item's stats
            # based on this Character.
            item.setCharacter(self)

            # Set the item onto this Player's cursor.
            self.player.cursorItem = item

            # Update the clients cursor item.
            self.player.updateCursorItem(None)

            # Return True as this Character was successfully given the item,
            # placing the item on the Player's cursor.
            return True

        # Return False as this Character was not given the ItemInstance.
        return False


    ## @brief Gets a list of free carry slots.
    #  @param self (Character) The object pointer.
    #  @return (Integer List) List of carry slots that does not have an
    #          ItemInstance in the slot.
    def getFreeCarrySlots(self):

        # Get a list of all carry slots.
        freeSlots = range(RPG_SLOT_CARRY_BEGIN, RPG_SLOT_CARRY_END)

        # Iterate over this Character's items.
        for item in self.items:

            # Remove the item's slot from the free slot list.  Try/except
            # tends to be faster than checking if the value is in the list, and
            # then removing the value from the list.
            try:
                freeSlots.remove(item.slot)

            # The item was not in a carry slot.  Continue to the next item.
            except:
                continue

        # Return the list of free slots.
        return freeSlots


    ## @brief Attempts to raise a skill level for the Character.
    #  @param self (Character) The object pointer.
    #  @param skillname (String) The ClassSkill's skillname which is being
    #                   checked for a skill level being raised.
    #  @param min (Integer) The minimum chance range for a skill up. (1 out of
    #                       min + 1 chances.)
    #  @param max (Integer) The maximum chance range for a skill up.  (1 out of
    #                       max + 1 chances.)
    #  @param playSound (Boolean) Indicates if the Player will be played a
    #                   sound if the skill level is raised.  Currently disabled.
    #  @param silent (Boolean) Indicates if the Player will receive a message
    #                if the skill level is raised.
    #  @return None.
    #  @deprecated TWS: Is the playSound arguement needed?
    #  @todo TWS: Optimize: The class skill can be returned, to local scope.
    #        At miniumum, this reduces down to 8 hash lookups, with even more
    #        possible as many variables are used only once.
    #  @todo TWS: Optimize: If the quest requirements are satisfied for a mob,
    #        is it safe to delete the requirement from the SkillProfile?  This
    #        prevents querying the database each skill up after the requirement
    #        has been satisfied.  If CharacterDialogChoice is only deleted when
    #        the Character is deleted, then I think it is safe to do so.
    def checkSkillRaise(self, skillname, min=3, max=8, playSound=True, silent=False):

        # Make a local reference to this Character's Mob.
        mob = self.mob

        # Set the initial skill reuse time.
        # TWS: Is this needed?  SkillProfile will set it or return if the skill
        # is not found.
        reuseTime = 0

        # Get the Mob's skill related data.
        try:

            # Get the Mob's current skill leve.
            slevel    = mob.skillLevels[skillname]

            # Get this max skill level allowed for this Mob's skill.
            mlevel    = mob.mobSkillProfiles[skillname].maxValue

            # Get this reuse time for this Mob's skill.
            reuseTime = mob.mobSkillProfiles[skillname].reuseTime

            # Get the quest requirements for this Mob's skill.
            questReq  = mob.mobSkillProfiles[skillname].questRequirements

        # The mob's skill related data could not be found for the skill being
        # raised, so return early.
        except KeyError:
            return

        # If this Character's current skill level is greater than or equal to
        # the max value allowed for the ClassSkill, then this Character has
        # maxed the skill, so return early.
        if slevel >= mlevel:
            return

        # Iterate over the skill's quest requirements.
        for qreq in questReq:

            # If the skill level is greater than or equal to the level barrier
            # provided by the quest requirement, then check if this Character
            # has completed the quest.
            # TWS: This index stuff is confusing to read.  Should probably
            # use an enum or make a class.
            if slevel >= qreq[1]:

                # Query the database for a CharacterDialogChoice that has an
                # identifier matching the ClassSkillQuestRequirement's
                # identifier, and a characterID matching this Character's ID.
                dcs = list(CharacterDialogChoice.select(AND(CharacterDialogChoice.q.identifier==qreq[0],CharacterDialogChoice.q.characterID==self.id)))

                # If the CharacterDialogChoice query returned nothing, the list
                # was empty, or if the count of times the Character has choosen
                # the dialog is 0, then this Character does not satisfy the
                # skill's ClassSkillQuestRequirement, so return early.
                if not dcs or not len(dcs) or not dcs[0].count:
                    return


        # Calculate the base chance based on the skill level.
        i = int (slevel/10)

        # If the chance is less than the minimum, then clamp the chance to the
        # minimum.
        # TWS: This could probably come after the activated skill adjustement
        # below.
        if i < min:
            i = min

        # If the chance is greater than the maximum, then clamp the chance to
        # the maximum.
        if i > max:
            i = max

        # If there is a resuse time, then the skill is non-passive.  Modify
        # the chance so that these skills are easier to raise.
        if reuseTime:
            i/=2

            # If the modified chance is less than the minimum, then clamp the
            # chance to the minimum.
            # TWS: This could probably be removed if the clamp is done outside
            # of the if statement below.
            if i < min:
                i = min

        # Character has a 1 out of i + 1 chance of raising the skill.  Generate
        # a random number from 0 to i.  If any value other than zero is
        # returned, then this Character failed at raising the skill.
        if randint(0,i):

            # This Character failed at raising the skill so return early.
            return

        # Iterate over this Character's skills.
        for skill in self.skills:

            # If the CharacterSkill for the skill was found, then raise the
            # skill level.
            if skill.skillname == skillname:

                # Increase the skill level.
                skill.level += 1

                # Update this Mob's skill level.
                mob.skillLevels[skillname] = skill.level

                # The chance in skill level can cause derived stats to adjusted,
                # and the mob needs to recalculate skill reuse times, so update
                # the mob.
                mob.updateClassStats()

                # If output is not disabled, inform the Player of the items
                # lost.
                if not silent:
                    self.player.sendGameText(RPG_MSG_GAME_GAINED,"%s has become better at <a:Skill%s>%s</a>! (%i)\\n"%(self.name,GetTWikiName(skillname),skillname,skill.level))

                # Sound disabled until someone finds a sound short enough and
                # fitting that does not disturb gameplay.
                # if playSound:
                #     self.player.mind.callRemote("playSound","sfx/magic_spell_heal3.ogg")

                # There is no need to continue iterating through this
                # Character's skills, as the skill was found and increased, so
                # return.
                return


    ## @brief Removes stats provided by an AdvancementStat from the Character.
    #  @param self (Character) The object pointer.
    #  @return None.
    #  @todo TWS: mob.advancementStats should probably chance to a dictionary
    #             named "advancementDerivedStats" that contains only derived
    #             modifiers.  Prevents checks in the mob's updateDerivedStats.
    def removeAdvancementStats(self):
        
        mob = self.mob

        try:

            # If this Character has no Mob, then return early.
            if not mob:
                return

            # Stats may be adjusted.  Therefore, the Mob's derived stats will
            # need to be recalculated, so flag them as dirty.
            mob.derivedDirty = True

            # Clear advancement stats for the Mob's derived stats.
            mob.advancementStats = []

            # Clear advancement stats for the Mob's "advance_" stats.
            mob.advancements.clear()

            # Iterate over this Character's CharacterAdvancements.
            for adv in self.advancements:

                # Iterate over each stat provided by the AdvancementProto.
                for stat in adv.advancementProto.stats:

                    # Advance_ stats are aready cleared, so continue to the next
                    # stat.
                    if stat.statname.startswith("advance_"):
                        continue

                    # Calculate the total value the advancement modifies based
                    # on the rank.
                    v = float(adv.rank) * stat.value

                    # If the stat is a resist, modify the Mob's resist
                    # dictionary.
                    if stat.statname in RPG_RESISTSTATS:

                        # Reduce the value provided by the Advancement from the
                        # Mob's resist dictionary.
                        mob.resists[RPG_RESISTLOOKUP[stat.statname]] -= v

                    # Otherwise, it is a non-resist stat, and is a Mob
                    # attribute.
                    else:

                        # Reduce the Mob's attribute by the value provided by
                        # the Advancement.
                        mob.__dict__[stat.statname] -= v

        # If any exception is raised, print a traceback to help in debugging
        # the cause.
        except:
            traceback.print_exc()


    ## @brief Applies stats provided by an AdvancementStat to the Character.
    #  @param self (Character) The object pointer.
    #  @return None.
    #  @todo TWS: mob.advancementStats should probably chance to a dictionary
    #             named "advancementDerivedStats" that contains only derived
    #             modifiers.  Prevents checks in the mob's updateDerivedStats.
    def applyAdvancementStats(self):
        
        mob = self.mob

        try:

            # If this Character has no Mob, then return early.
            if not mob:
                return

            # Stats may be adjusted.  Therefore, the Mob's derived stats will
            # need to be recalculated, so flag them as dirty.
            mob.derivedDirty = True

            # Clear advancement stats for the Mob's "advance_" stats.
            mob.advancementStats = []

            # Clear advancement stats for the Mob's derived stats.
            advancements = mob.advancements
            advancements.clear()

            # Iterate over this Character's CharacterAdvancements.
            for adv in self.advancements:

                # Iterate over each stat provided by the AdvancementProto.
                for stat in adv.advancementProto.stats:

                    # Calculate the total value the advancement modifies based
                    # on the rank.
                    v = float(adv.rank) * stat.value

                    # Advance_ stats are special stats are are added to the
                    # Mob's advancements dictionary.
                    if stat.statname.startswith("advance_"):

                        # Use the letters after "advance_" for the stat name.
                        st = stat.statname[8:]

                        # Add the stat (key) and value (value) to the Mob's
                        # advancement dictionary.
                        advancements[st] += v

                    # If the stat is a resist, modify the Mob's resist
                    # dictionary.
                    elif stat.statname in RPG_RESISTSTATS:

                        # Add the value provided by the Advancement to the Mob's
                        # resist dictionary.
                        mob.resists[RPG_RESISTLOOKUP[stat.statname]] += v

                    # Otherwise, it is a non-resist stat, and is a Mob
                    # attribute.
                    else:

                        # Add the value provided by the Advancement to the
                        # Mob's attribute.
                        mob.__dict__[stat.statname] += v

                        # Add the stat to the Mob's dictionary.
                        mob.advancementStats.append((stat.statname,v))

        # If any exception is raised, print a traceback to help in debugging
        # the cause.
        except:
            traceback.print_exc()


    ## @brief Checks for AdvancementExclusions, destroying excluded advancements
    #         for the Character.
    #  @param self (Character) The object pointer.
    #  @return None.
    #  @todo TWS: Optimize, the xs = list(MultiJoin) for x in xs... could be
    #        changed to for x in Multi
    def checkAdvancements(self):

        # Get a list of this Character's CharacterAdvancements.
        advancements = list(self.advancements)

        # Iterate over this Character's Advancements.
        for a in advancements:

            # If the CharacterAdvancement has already been destroyed, continue
            # to the next Advancement.
            if hasattr(a,"hasBeenDestroyed"):
                continue

            # Get a list of this Character's CharacterAdvancements.
            adv = list(self.advancements)

            # Iterate over this Character's CharacterAdvancements.  These
            # advancements will be checked for exclusion and may be destroyed.
            for b in adv:

                # If the CharacterAdvancements are the same, continue to the
                # next CharacterAdvancement.
                if a == b:
                    continue

                # Iterate over the Advancement's exclusions.
                for ex in a.advancementProto.exclusions:

                    # If the Advancement is excluded, then delete the
                    # CharacterAdvancement.
                    if ex.exclude == b.advancementProto.name:

                        # Flag the CharacterAdvancement as deleted.
                        b.hasBeenDestroyed = True

                        # Delete the CharacterAdvancement.
                        b.destroySelf()

        # Cache this Character's CharacterAdvancements.
        ## @brief (CharacterAdvancement List) CharacterAdvancements
        #         belonging to the Character.
        #  @remarks The reassignment of advancements to advancementsCache
        #           prevents having to query the database when iterating over
        #           the Character's CharacterAdvancement.
        self.advancementsCache = self.advancements


        # Reward advanmcent points to monsters who have not already received
        # starting advancement points.
        # TWS: This should probably be done elsewhere.  This is out of the scope
        # for checkAdvancements and should only be performed once really.  Maybe
        # consider consolidating the rewards of old and new advancement points
        # for monsters.
        if self.spawn.template and not self.spawn.flags&RPG_SPAWN_MONSTERADVANCED:
            
            # TWS: This inline import neesd to be moved to be global.
            from spawn import Spawn

            # Get the Spawn's template.
            template = Spawn.byName(self.spawn.template)

            # Iterate over the amount of primary levels for which advancement
            # points are to be rewarded.
            for i in xrange(2,template.plevel):

                # Calculate how many points to reward for the level.
                points = int(float(i) / 2.0)

                # Set minimum advancement points rewarded.
                if points < 5:
                    points = 5

                # Add the rewarded points to the Character.
                self.advancementPoints += points

            # Iterate over the amount of secondary levels for which advancement
            # points are to be rewarded.
            for i in xrange(2,template.slevel):

                # Calculate how many points to reward for the level.
                points = int(float(i) / 2.0)

                # Set minimum advancement points rewarded.
                if points < 3:
                    points = 3

                # Add the rewarded points to the Character.
                self.advancementPoints += points

            # Iterate over the amount of tertiary levels for which advancement
            # points are to be rewarded.
            for i in xrange(2,template.tlevel):

                # Calculate how many points to reward for the level.
                points = int(float(i) / 2.0)

                # Set minimum advancement points rewarded.
                if points < 1:
                    points = 1

                # Add the rewarded points to the Character.
                self.advancementPoints += points

            # Update the Spawn's flags to indicate advancements have been
            # rewarded.
            self.spawn.flags |= RPG_SPAWN_MONSTERADVANCED


    ## @brief Purchases an AdvancementProto for the Character.
    #  @param self (Character) The object pointer.
    #  @param advance (String) The name of the AdvancementProto being purchased.
    #  @return None.
    #  @todo TWS: Some of the +rank or +advancement logic is duplicated and
    #        could be reworked to help code reuse, readability, and clean logic.
    def chooseAdvancement(self, advance):

        # Make a local reference to this Character's Spawn.
        # TWS: Move this assignment to right before it is used.
        spawn = self.spawn

        # Get the AdvancementProto by the name.
        try:
            a = AdvancementProto.byName(advance)

        # The caller provided an invalid advancement name.  Print debug
        # information and return early.
        except:
            print "WARNING: Unknown Advancement %s"%advance
            return

        # Handle to the choosen CharacterAdvancement.
        thisAdv = None

        # Dictionary that will store the names of AdvancementProtos (key) this
        # Character has trained, and the rank of the Advancement (value).
        existingAdv = {}

        # Iterate over this Character's Advancements.
        for adv in self.advancements:

            # Get the AdvancementProto for the CharacterAdvancement.
            proto = adv.advancementProto

            # Update the existing advancement dictionary with the
            # AdvancementProto's name (key) and CharacterAdvance's rank (value).
            existingAdv[proto.name] = adv.rank

            # If the iterated CharacterAdvance's AdvancementProto is the choosen
            # advancement, set a hanlde to the Advancement.
            if proto == a:
                thisAdv = adv


        # Passed is used to indicate if the choosen Advancement may be trained.
        passed = True

        # Flag failure under any of the following conditions:
        # - Spawn primary level is below the level required by the Advancement.
        # - The count of advancement points this Character has is less than the
        #   Advancement cost.
        # - The Advancement is already trained greater than or equal to the max.
        if spawn.plevel < a.level or self.advancementPoints < a.cost or (thisAdv and thisAdv.rank >= a.maxRank):
            passed = False

        # If the advancement has class and level requirements, check them.
        elif len(a.classes):

            # Set a flag to indicate this Character has not met all
            # requirements.
            passed = False

            # Iterate over the classes that may train the advancement.
            for cl in a.classes:

                # If this Character has trained class satisfying both the class
                # and level requirements, then set the passed flag to indicate
                # the requirements have been satisfied.
                if (cl.classname == spawn.pclassInternal and cl.level <= spawn.plevel) or (cl.classname == spawn.sclassInternal and cl.level <= spawn.slevel) or (cl.classname == spawn.tclassInternal and cl.level <= spawn.tlevel):

                    # Set flag indicating this requirement was satisfied.
                    passed = True

                    # The requirement was satisfied, so exit the loop.
                    break

        # If all requirements have been met and the advancement has race and
        # level requirements, check them.
        if passed and len(a.races):

            # Set a flag to indicate this Character has not met all
            # requirements.
            passed = False

            # Iterate over the races that may train the advancement.
            for rc in a.races:

                # If this Character satisfies both the race and level
                # requirements, then set the passed flag to indicate the
                # requirements have been satisfied.
                if rc.racename == spawn.race and rc.level <= spawn.plevel:

                    # Set flag indicating this requirement was satisfied.
                    passed = True

                    # The requirement was satisfied, so exit the loop.
                    break

        # If all requirements have been met, then check for required
        # advancements.
        if passed:

            # Iterate over the required advancements.
            for req in a.requirements:

                # If the advancement required has not been trained by this
                # Character or the advancement is trained but does not meet the
                # required rank, then set the passed flag to indicate the
                # requirement has not been satisfied.
                if req.require not in existingAdv or req.rank > existingAdv[req.require]:

                    # Set flag indicating this requirement was not satisfied.
                    passed = False

                    # The requirement was not satisfied, so exit the loop.
                    break

        # If all requirements were not satisfied, then the advancement did not
        # pass.  The Character should have never been given the option to
        # purchase the advancement, so print a debug message and return early.
        if not passed:
            print "WARNING: %s attempted unqualified advancement %s"%(self.name,advance)
            return

        # Either an advanceemnt is increasing in rank or a new advancement is
        # being purchased.  In either case, remove all advancement stats before
        # making modificatiosn and applying CharacterAdvancements.  Otherwise,
        # removing the advancements after modifications would cause this
        # Character's Mob to lose more stats than what the advancements had
        # actually provided when they were last applied.
        self.removeAdvancementStats()

        # This Character already has a CharacterAdvancement for the Advancement,
        # so just increase the rank.
        if thisAdv:

            # Increase the rank.
            thisAdv.rank += 1

            # Reduce this Character's advancement points by the cost of the
            # Advancement.
            self.advancementPoints -= a.cost

            # The Advancement has already been purchased, and exclusions have
            # have already been checked and applied when the advancement was
            # originally purchased.  Thus, there is no need to check for
            # exclusions as only the advancement rank is increasing.

            # Stats have changed, so reapply all advancements.
            self.applyAdvancementStats()

            # Inform the Player.
            self.player.sendGameText(RPG_MSG_GAME_GAINED,"%s has gained a rank in %s! (%i)\\n"%(self.name,advance,thisAdv.rank))

            # Return early as the advancement has been handled.
            return

        # This Character is purchasing a new Advancement, so create a
        # CharacterAdvancement.
        CharacterAdvancement(advancementProto=a,character=self)

        # Reduce this Character's advancement points by the cost of the
        # Advancement.
        self.advancementPoints -= a.cost

        # The newly purchased advancement may have exclusions, so check for
        # advancement exclusions.
        self.checkAdvancements()

        # Stats have changed, so reapply all advancements.
        self.applyAdvancementStats()

        # Inform the Player.
        self.player.sendGameText(RPG_MSG_GAME_GAINED,"%s has advanced in %s!\\n"%(self.name,advance))

        # Cache this Character's CharacterAdvancements.  This reassignment
        # prevents having to query the database each time the CharacterInfo
        # refreshes.
        self.advancementsCache = self.advancements


    ## @brief The Character will attempt to craft using a recipe or ingredients
    #         within the crafting slots.
    #  @param self (Character) The object pointer.
    #  @param recipeID (Integer) The ID of the Recipe being crafted.
    #  @param useCraftWindow (Boolean) Indicates if craft window should be used
    #                        to derive the recipe.
    #  @return None.
    #  @todo TWS: Move inline import to global.
    def onCraft(self, recipeID, useCraftWindow):

        # If this Character is dead, then this Character cannot craft.
        if self.dead:
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"%s is dead and cannot craft!\\n"%(self.name))
            return

        # TWS: This inline import neesd to be moved to be global.
        from crafting import Craft
        
        # Delegate crafting to the Craft function.
        Craft(self.mob,recipeID,useCraftWindow)


    ## @brief Splits an ItemInstance stack into two seperate ItemInstance
    #         stacks.
    #  @param self (Character) The object pointer.
    #  @param item (ItemInstance) The ItemInstance being split.
    #  @param newStackSize (Integer) The desired quantity of the original stack.
    #  @return None.
    def splitItem(self, item, newStackSize):

        # If the new stack size is greater than the amount of items available on
        # the original stack, or if the new stack size is less than one, then a
        # new stack cannot be created, so return early.
        if newStackSize >= item.stackCount or newStackSize < 1:
            return

        # If the count of free carry slots is less than 1, then this
        #  Character does not have enough room for the item to be split.
        if len(self.getFreeCarrySlots()) < 1:

            # Inform the Player.
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"%s doesn't have enough free carry slots for item split!\\n"%(self.name))

            # Return early.
            return

        # Clone the stack being split, creating a new ItemInstance.
        nitem = item.clone()

        # Set the new item's stack count.
        nitem.stackCount = item.stackCount - newStackSize

        # The new item's ItemInfo is not updated because it is not set to any
        # Character and there are no observers.  If the new ItemInstance is
        # successfully given to this Character, then the ItemInfo will be
        # updated and sent to the observers automatically.

        # Attempt to give the new item.  If a failure occurs when giving the
        # ItemInstance to this Character, then the item needs destroyed.
        if not self.giveItemInstance(nitem):

            # Destroy the ItemInstance.
            nitem.destroySelf()
            raise "Unable to give item instance on split!"
            return

        # The ItemInstance could be given to the Character. So update now
        #  the original item's stack count. Do this after checking so no
        #  items get lost.
        item.stackCount = newStackSize

        # Refresh the original item's ItemInfo so observing clients see the new
        # stack count.
        item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount})


    ## @brief Destroys the Character, deleting the Character and related
    #         objects from the persistence layer.
    #  @param self (Character) The object pointer.
    #  @return None.
    #  @todo TWS: Consider map calls for many of the destroys.
    def destroySelf(self):

        # Destroy all of this Character's CharacterSpell.
        for o in self.spellsInternal:
            o.destroySelf()

        # Iterate over all of this Character's ItemInstances, removing traces of
        # this Character for ItemInstances in bank slots or destroying the
        # ItemInstance.
        for o in self.itemsInternal:

            # Some bank items might have Character and Player simultaneously
            # assigned.  Reset the ItemInstance's Character attribute.
            if RPG_SLOT_BANK_BEGIN <= o.slot < RPG_SLOT_BANK_END:
                o.character = None

            # The Item is not in a bank slot so destroy the ItemInstance.
            else:
                o.destroySelf()

        # Destroy all of this Character's CharacterAdvancements.
        for o in self.advancements:
            o.destroySelf()

        # Destroy all of this Character's CharacterSkills.
        for o in self.skills:
            o.destroySelf()

        # Destroy all of this Character's DialogChoice.
        for o in self.characterDialogChoices:
            o.destroySelf()

        # Destroy all of this Character's SpellStore.
        for o in self.spellStore:
            o.destroySelf()

        # Destroy all of this Character's CharacterVaultItems.
        for o in self.vaultItems:
            o.destroySelf()

        # Destroy all of this Character's CharacterFactions.
        for o in self.characterFactions:
            o.destroySelf()

        # Destroy this Character's Spawn.
        self.spawn.destroySelf()

        # Destroy this Character.
        Persistent.destroySelf(self)



## @} # End character group.
