from genesis.dbdict import DBVendorProto,DBItemProto,DBDict
from mud.world.defines import *

spells = ["Arcane Blast","Arcane Storm","Summon Wolf Consort","Sapre's Airy Melody"]

vendor = DBVendorProto(name="Spell Dealer")
for s in spells:
    vendor.addItem("Scroll of %s"%s)
