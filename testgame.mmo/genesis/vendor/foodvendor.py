from genesis.dbdict import DBVendorProto,DBItemProto,DBDict
from mud.world.defines import *


vendor = DBVendorProto(name="Snacks")
for ip in DBDict.registry['ItemProto']:
    if 'FOOD' in ip.itemType and 'COMMON' in ip.itemType:
        vendor.addItem(ip.name)

for ip in DBDict.registry['ItemProto']:
    if 'DRINK' in ip.itemType and 'COMMON' in ip.itemType:
        vendor.addItem(ip.name)

