from genesis.dbdict import *
from mud.world.defines import *

item = DBItemProto()
item.name = "Strange stone"
item.desc = "A strange looking lightweighted stone."
item.bitmap = "STUFF/5000"
item.itemType = ['COMMON','STONE']
item.worthSilver = 70
item.stackMax = 20
item.stackDefault = 1

item = DBItemProto()
item.name = "Strange cold stone"
item.desc = "A strange looking lightweighted stone that is cold as ice."
item.bitmap = "STUFF/5000"
item.itemType = ['COMMON','STONE']
item.worthCopper = 70
item.stackMax = 20
item.stackDefault = 1

item = DBItemProto()
item.name = "Strange slimy stone"
item.desc = "A strange looking lightweighted stone that is covered with slime."
item.bitmap = "STUFF/5000"
item.itemType = ['COMMON','STONE']
item.worthCopper = 70
item.stackMax = 20
item.stackDefault = 1
