from genesis.dbdict import DBVendorProto,DBItemProto,DBDict
from mud.world.defines import *

vendor = DBVendorProto(name="Weapon Vendor")
for ip in DBDict.registry['ItemProto']:
    if 'BOW' in ip.itemType and 'COMMON' in ip.itemType:
        vendor.addItem(ip.name)
        
vendor = DBVendorProto(name="Tool Vendor")
for ip in DBDict.registry['ItemProto']:
    if 'TOOL' in ip.itemType and 'COMMON' in ip.itemType:
        vendor.addItem(ip.name)
