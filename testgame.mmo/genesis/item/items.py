from genesis.dbdict import *
from mud.world.defines import *

#---  Grey Wolf Hide
item = DBItemProto()
item.name = "Grey Wolf Hide"
item.desc = "This repugnant gray mass was once the skin of a fierce wolf."
item.bitmap = "EQUIPMENT/BACK/3"
item.flags = RPG_ITEM_SOULBOUND
item.stackMax = 20
item.stackDefault = 1

#--- Wolf Meat
item = DBItemProto(name="Wolf Meat")
item.desc = "The meaty parts of a wolf. Mmmm ... tastes like chicken."
item.stackMax = 100
item.stackDefault = 1
item.worthCopper = 10
item.bitmap = "STUFF/66"

#--- Foresting
item = DBItemProto() 
item.itemType = ['COMMON','TOOL'] 
item.name = "Small Wood Axe" 
item.skill="Foresting" 
item.wpnDamage = 4 
item.wpnRate = 11 
item.wpnRange = 2 
item.repairMax = 10 
item.bitmap = "EQUIPMENT/SWORDS/24" 
item.model = "weapons/sword01.dts" 
item.worthCopper = 45 
item.slots = (RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY)

#--- Mining
item = DBItemProto() 
item.itemType = ['COMMON','TOOL'] 
item.name = "Small Pick" 
item.skill="Mining" 
item.wpnDamage = 4 
item.wpnRate = 11 
item.wpnRange = 2 
item.repairMax = 10 
item.bitmap = "EQUIPMENT/SWORDS/24" 
item.model = "weapons/sword01.dts" 
item.worthCopper = 45 
item.slots = (RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY)
