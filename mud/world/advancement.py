# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup advancement advancement
#  @ingroup world
#  @brief The advancement module provides persistent data types used for
#         creating Character enchancements through an advancement purchasing
#         system.
#  @{


from mud.common.persistent import Persistent
from sqlobject import *


## @brief Persistent data type defining a Class and level requirement for an
#         Advancement.
class AdvancementClass(Persistent):

    # Attributes.
    ## @brief (Persistent String) Class required by the Advancement.
    classname = StringCol()
    ## @brief (Persistent Integer) Level required by the Advancement.
    level = IntCol()

    # Relationships.
    ## @brief (Persistent AdvancementProto) Advancement that requires the class
    #         and level.
    advancementProto = ForeignKey('AdvancementProto')


## @brief Persistent data type defining a Race and level requirement for an
#         Advancement.
class AdvancementRace(Persistent):

    # Attributes.
    ## @brief (Persistent String) Race required by the Advancement.
    racename = StringCol()
    ## @brief (Persistent Integer) Level required by the Advancement.
    level = IntCol()

    # Relationships.
    ## @brief (Persistent AdvancementProto) Advancement that requires the race
    #         and level.
    advancementProto = ForeignKey('AdvancementProto')


## @brief Persistent data type defining a requirement that an Advancement
#         must be trained before the associated Advancement is available.
class AdvancementRequirement(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of an Advancement required by the
    #         Advancement.
    require = StringCol()
    ## @brief (Persistent Integer) Rank of an Advancement required by the
    #         Advancement.
    rank = IntCol(default=1)

    # Relationships.
    ## @brief (Persistent AdvancementProto) Advancement that requires another
    #         Advancement.
    advancementProto = ForeignKey('AdvancementProto')


## @brief Persistent data type defining an Advancement that is removed from a
#         Character when the associated Advancement is trained.
class AdvancementExclusion(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of Advancement that is destroyed/removed.
    exclude = StringCol()

    # Relationships.
    ## @brief (Persistent AdvancementProto) Advancement that destroys the other
    #         Advancement when trained.
    advancementProto = ForeignKey('AdvancementProto')


## @brief Persistent data type defining a stat and value modified by an
##        Advancement.
class AdvancementStat(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of a stat an Advancement modifies.
    statname = StringCol()
    ## @brief (Persistent Float)The amount a stat is modified by an
    #         Advancement.
    value = FloatCol()

    # Relationships.
    ## @brief (Persistent AdvancementProto) Advancement that modifies the
    #         stats.
    advancementProto = ForeignKey('AdvancementProto')


## @brief Persistent data type defining a skill gained by an Advancement.
#  @deprecated TWS: Is this class used or supported?
class AdvancementSkill(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of Skill provides by an Advancement.
    skillname = StringCol()

    # Relationships.
    ## @brief (Persistent AdvancementProto) Advancement that provides a skill.
    advancementProto = ForeignKey('AdvancementProto')


## @brief Persistent data type defining an Advancement.  Advancements are
#         Character enhancements that may be purchased at the expense of
#         advancement points by Characters meeting all the Advancement's
#         requirements.
class AdvancementProto(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of the Advancement.  This must be unique.
    name = StringCol(alternateID=True)
    ## @brief (Persistent Integer) Level required by an Advancement.
    level = IntCol(default=1)
    ## @brief (Persistent String) Description of the enhancements provided by
    #         the Advancement.
    desc = StringCol(default="")
    ## @brief (Persistent Integer) Advancement point cost to purchase the
    #         Advancement.
    cost = IntCol(default=1)
    ## @brief (Persistent Integer) Max number of times the Advancement may be
    #         purchased.
    maxRank = IntCol(default=1)

    # Relationships.
    ## @brief (Persistent AdvancementStat List) Stat modifiers provided by the
    #         Advancement.
    stats = MultipleJoin('AdvancementStat')
    ## @brief (Persistent AdvancementStat List) Skills provided by the
    #         Advancement.
    skills = MultipleJoin('AdvancementSkill')
    ## @brief (Persistent AdvancementStat List) Class requirements for the
    #          Advancement.
    classes = MultipleJoin('AdvancementClass')
    ## @brief (Persistent AdvancementStat List) Race requirements for the
    #         Advancement.
    races = MultipleJoin('AdvancementRace')
    ## @brief (Persistent AdvancementStat List) Trained Advancement requirements
    #         for the Advancement.
    requirements = MultipleJoin('AdvancementRequirement')
    ## @brief (Persistent AdvancementStat List) Advancements removed once the
    #         Advancement is trained.
    exclusionsInternal = MultipleJoin('AdvancementExclusion')


    ## @brief Initializer delegates variable initialization to parent class.
    #  @param self (AdvancementProto) The object pointer.
    #  @todo TWS: Given advancement relationships are known at world compile
    #        time, and constant at runtime, maybe all multijoins should be
    #        copying at initialization to prevent polling database everytime.
    def _init(self, *args, **kwargs):

        Persistent._init(self, *args, **kwargs)

        ## @brief (AdvancementExclusion List) List containing
        #         AdvancementExclusions.
        #  @remarks The reassignment prevents having to query the database each
        #           time related ExclusionInternals are checked.
        self.exclusions = self.exclusionsInternal


## @} # End advancement group.
