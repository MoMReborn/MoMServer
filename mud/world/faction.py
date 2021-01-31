# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup faction faction
#  @ingroup world
#  @brief The faction module provides persistent data object class
#  definitions used for creating Character enchancements through an advancement
#  purchasing system.
#  @{


from sqlobject import *
from defines import *
from mud.common.persistent import Persistent


## @brief Persistent data type defining a one-way, non-mutual relationship  one
#         Faction has towards another Faction.
class FactionRelation(Persistent):

    # Attributes.
    ## @brief (Persistent RPG_FACTION_LEVEL)  The relationship level that the
    #         Faction has towards the other Faction.
    #  @details The lower the points, the more the Faction dislikes the other
    #           Faction.
    relation = IntCol(default=RPG_FACTION_UNDECIDED)

    # Relationships.
    ## @brief (Persistent Faction) The Faction that has the relationship towards
    #         the other Faction.
    faction = ForeignKey('Faction')
    ## @brief (Persistent Faction) The Faction towards which the relationship is
    #         had.
    otherFaction = ForeignKey('Faction')


## @brief Persistent data type defining a faction.  Factions can be used to
#         create groups that have a common set of lore-based characeristics.
class Faction(Persistent):

    # Attributes.
    ## @brief (Persistent String) Name of the Faction.  This must be unique.
    name = StringCol(alternateID = True)
    ## @brief (Persistent Integer) Level scalar for the Faction's relative
    #         political power.
    #  @deprecated TWS: Is this even used?
    level = IntCol(default=1)
    ## @brief (Persistent RPG_REALM_TYPE) The realm associated with the Faction.
    #  @details If a specific realm is defined, then only Characters of the
    #           specified realm may adjust the Character's relationship with
    #           the Faction.
    realm  = IntCol(default=RPG_REALM_UNDEFINED)

    # Relationships.
    ## @brief (Persistent FactionRelation) Relationships the Faction has
    #         torwards other Factions.
    relations = MultipleJoin('FactionRelation')
    ## @brief (Persistent String) Aggro message Spawns aligned to the Faction
    #         scream when aggroing another Mob.
    #  @details The attackMsg is used only if the Mob being aggroed is not
    #           aligned with or in good standings with an opposing Faction that
    #           has an enemyMsg.
    attackMsg = StringCol(default = "")
    ## @brief (Persistent String) Aggro message Mobs scream when aggroing a
    #         Spawn aligned with or in good standings with an opposing Faction.
    enemyMsg = StringCol(default = "")
    ## @brief (Persistent Spawn) Spawns aligned to the Faction.
    spawns = RelatedJoin('Spawn')


## @brief (Dictionary) Dictionary containing spawn names (key) and a list of
#         kill on sight spawn (value).
KOS = {}


## @brief Initialize kill on sight dictionary for all spawns based on faction
#         relations.
#  @todo TWS: Move the import to global scope.
#  @todo TWS: Unless some caching and indexing occurs on the persistence layer,
#        then it looks like there are some optimizations that could occur, as
#        it looks like many of the sub queries will be identifical in some
#        iterations.  This method really only gets called once though, so the
#        overal gain is minimal.
def InitKOS():
    from spawn import Spawn

    # Get the database connection used by the Spawn class.
    con = Spawn._connection.getConnection()

    # Iterate over all spawns.
    for sname,sid in con.execute("SELECT name,id FROM spawn;"):

        # Insert a list into the KOS dictionary based on the spawn name.
        kos = KOS[str(sname)] = []

        # Iterate over all spawns that are kill on sight based on associated
        # faction relations between spawns.
        for otherName in con.execute("SELECT name FROM spawn WHERE id IN (SELECT DISTINCT spawn_id FROM faction_spawn WHERE faction_id IN (SELECT DISTINCT other_faction_id FROM faction_relation WHERE relation<%i AND (faction_id IN (SELECT faction_id FROM faction_spawn WHERE spawn_id=%i))));"%(RPG_FACTION_DISLIKED,sid)):

            # Add the spawn name to the kill on sight list.
            kos.append(str(otherName[0]))


## @} # End faction group.
