from genesis.dbdict import DBVendorProto,DBItemProto,DBDict
from mud.world.defines import *


vendor = DBVendorProto(name="Vendorman")
for ip in DBDict.registry['ItemProto']:
    if 'STONE' in ip.itemType and 'COMMON' in ip.itemType:
        vendor.addItem(ip.name)