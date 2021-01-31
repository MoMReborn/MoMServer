
from genesis.dbdict import *
from mud.world.defines import *

item = DBItemProto(name="Composite Longbow")
item.itemType = ['COMMON','BOW']
item.skill = "Archery"
item.wpnRate = 11
item.wpnDamage = 20
item.wpnRange = 44
item.wpnAmmunitionType = "Arrow"
item.bitmap = "EQUIPMENT/BOWS/3"
#item.model = "weapons/bow04.dts"
item.worthSilver = 1
item.worthCopper = 5
item.worthTin = 50
item.rating = 1
item.slots = (RPG_SLOT_RANGED,)
item.addStat("dex", 150)
item.addStat("agi", 150)
item.addStat("ref", 150)

item = DBItemProto(name="Feather Arrow")
item.itemType = ['COMMON','BOW','AMMO']
item.slots = (RPG_SLOT_AMMO,)
item.bitmap = "EQUIPMENT/AMMO/1"
item.isAmmunitionType="Arrow"
item.projectile = "ArrowProjectile"
item.stackMax = 750
item.stackDefault = 50
item.wpnDamage = 10
item.wpnRange = 22
item.speed = 30
item.worthCopper = 1

item = DBItemProto(name="Flaming Arrow")
item.itemType = ['COMMON','BOW','AMMO']
item.slots = (RPG_SLOT_AMMO,)
item.bitmap = "EQUIPMENT/AMMO/1"
item.isAmmunitionType="Arrow"
item.projectile = "CrossbowProjectile"
item.stackMax = 750
item.stackDefault = 25
item.wpnDamage = 20
item.wpnRange = 44
item.speed = 30
item.worthCopper = 3
