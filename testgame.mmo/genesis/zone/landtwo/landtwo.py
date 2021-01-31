from mud.world.defines import *
from genesis.dbdict import DBZone
from mud.world.zone import ZoneLink

zone = DBZone()
zone.name = "landtwo"
zone.niceName = "The mountains"
zone.missionFile = "landtwo.mis"
zone.climate = RPG_CLIMATE_POLAR
zone.immTransform = "62.0553 -376.161 135.3 1 0 0 0"

import spawns
import spawngroups
import items
import quests

ZoneLink(name = "landtwo_to_base",dstZoneName="base",dstZoneTransform="54.9763 -375.349 133.2 1 0 0 0")
