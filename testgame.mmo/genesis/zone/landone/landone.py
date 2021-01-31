from mud.world.defines import *
from genesis.dbdict import DBZone
from mud.world.zone import ZoneLink

zone = DBZone()
zone.name = "landone"
zone.niceName = "The swamp"
zone.missionFile = "landone.mis"
zone.climate = RPG_CLIMATE_TROPICAL
zone.immTransform = "31.1697 -274.647 126.7 1 0 0 0"

import spawns
import spawngroups
import items
import quests

ZoneLink(name = "landone_to_base",dstZoneName="base",dstZoneTransform="54.9763 -375.349 133.2 1 0 0 0")
