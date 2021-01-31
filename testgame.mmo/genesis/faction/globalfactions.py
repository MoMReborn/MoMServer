
from genesis.dbdict import DBFaction, DBFactionRelation
from mud.world.defines import *


DBFaction(name="The Blue", attackMsg = "The Blue will survive!",enemyMsg = "Die if you are against the Blue!")
DBFaction(name="The Green", attackMsg = "The Green will survive!",enemyMsg = "Die if you are against the Green!")
DBFaction(name="The Red", attackMsg = "The Red will survive!",enemyMsg = "Die if you are against the Red!")

DBFactionRelation(faction="The Blue", otherFaction = "The Green", relation = RPG_FACTION_UNDECIDED)
DBFactionRelation(faction="The Blue", otherFaction = "The Red", relation = RPG_FACTION_UNDECIDED)
DBFactionRelation(faction="The Green", otherFaction = "The Blue", relation = RPG_FACTION_UNDECIDED)
DBFactionRelation(faction="The Green", otherFaction = "The Red", relation = RPG_FACTION_UNDECIDED)
DBFactionRelation(faction="The Red", otherFaction = "The Blue", relation = RPG_FACTION_UNDECIDED)
DBFactionRelation(faction="The Red", otherFaction = "The Green", relation = RPG_FACTION_UNDECIDED)
