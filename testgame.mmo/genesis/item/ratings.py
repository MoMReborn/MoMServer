

from genesis.dbdict import DBDict
from mud.world.defines import *

ITEMS = []

for item in DBDict.getInstanceList('ItemProto'):
    if "COMMON" in item.itemType and "WEAPON" in item.itemType:
        ITEMS.append(item)
    if "COMMON" in item.itemType and "ARMOR" in item.itemType:
        ITEMS.append(item)
    if "COMMON" in item.itemType and "JEWELRY" in item.itemType:
        ITEMS.append(item)

for item in ITEMS:
    item.rating = 1 