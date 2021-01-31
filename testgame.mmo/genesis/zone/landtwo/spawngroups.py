from mud.world.defines import *
from genesis.dbdict import DBSpawnInfo,DBSpawnGroup

mob = DBSpawnInfo(spawn="Mountain Crawler",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="landtwo",groupName="MOUNTAINCRAWLER")
sg.addSpawnInfo(mob)
