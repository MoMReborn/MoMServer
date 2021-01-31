from mud.world.defines import *
from genesis.dbdict import DBSpawnInfo,DBSpawnGroup

mob = DBSpawnInfo(spawn="Swamp Walker",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="landone",groupName="SWAMPWALKER")
sg.addSpawnInfo(mob)
