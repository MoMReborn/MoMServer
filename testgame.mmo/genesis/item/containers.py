from genesis.dbdict import *
from mud.world.defines import *



#---  Green Key
item = DBItemProto(name="Green Key")
item.desc = "The Green Key."
item.bitmap = "STUFF/2"
item.flags = RPG_ITEM_SOULBOUND
item.itemClassifiers = ['Key']

#---  Red Key
item = DBItemProto(name="Red Key")
item.desc = "The Red Key."
item.bitmap = "STUFF/2"
item.flags = RPG_ITEM_SOULBOUND
item.itemClassifiers = ['Key']

#--- Key Ring
item = DBItemProto(name="Key Ring")
item.flags = RPG_ITEM_SOULBOUND|RPG_ITEM_UNIQUE|RPG_ITEM_INDESTRUCTIBLE
item.desc = "A key ring to hold multiple keys."
item.bitmap = "STUFF/5000"
# Should be large enough for all keys to fit in, including future ones.
item.containerSize = 25
item.containerContentClassifiers = ['Key']

#--- Bottomless Pit
item = DBItemProto(name="Bottomless Pit")
item.flags = RPG_ITEM_SOULBOUND|RPG_ITEM_UNIQUE|RPG_ITEM_INDESTRUCTIBLE
item.desc = "A container. Trust it."
item.bitmap = "STUFF/5000"
item.containerSize = 50
