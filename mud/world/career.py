# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup career career
#  @ingroup world
#  @brief The career module provides a persistent data types defining
#         ClassSkills obtainable for a RPG-class and Archetype.
#  @{


from mud.common.persistent import Persistent
from sqlobject import *


## @brief Persistent data type defining ClassSkills obtainable for a RPG-classes
#         and Archetype.
class ClassProto(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of the RPG-class for the Career.  This
    #         must be unique.
    name = StringCol(alternateID = True)
    ## @brief (Persistent String) Name of the RPG-class's archetype for the
    #         Career.
    archetype = StringCol(default = "")
    ## @brief (Persistent Float) Experience modifier provided by the Career.
    #  @deprecated TWS: Is this even used?
    xpMod = FloatCol(default=1.0)

    # Relationships.
    ## @brief (Persistent ClassSkill List) Skills obtainable by the Career.
    skills = RelatedJoin('ClassSkill')


## @} # End career group.