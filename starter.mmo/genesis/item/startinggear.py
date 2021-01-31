from mud.world.defines import *
from genesis.dbdict import DBItemProto
from mud.world.character import StartingGear


item = DBItemProto(name="Plain Helm")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/HEAD/44"
item.model = "head/helmet.dts"
item.material="head/helmet"
item.slots = (RPG_SLOT_HEAD,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 2

item = DBItemProto()
item.itemType = ['UNIQUE']
item.name = "Magic Shield"
item.skill="Shields"
item.armor = 8
item.bitmap = "EQUIPMENT/SHIELDS/4"
item.model = "weapons/shield02.dts"
item.slots = (RPG_SLOT_SHIELD,)
item.flags = RPG_ITEM_ARTIFACT
item.addStat("agi",4)
item.addStat("dex",3)
item.addStat("maxHealth",25)
item.addStat("resistPoison",5)
item.addStat("defense",16)

item = DBItemProto()
item.itemType = ['COMMON','WEAPON']
item.name = "Longsword"
item.skill="1H Slash"
item.wpnDamage = 4
item.wpnRate = 11
item.wpnRange = 2
item.repairMax = 10
item.bitmap = "EQUIPMENT/SWORDS/24"
item.model = "weapons/sword01.dts"
item.worthCopper = 45
item.slots = (RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY)


item = DBItemProto(name="Plain Shirt")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/CHEST/9"
item.material = "tset_0_body"
item.slots = (RPG_SLOT_CHEST,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1

item = DBItemProto(name="Plain Boots")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/FEET/13"
item.material = "tset_0_feet"
item.slots = (RPG_SLOT_FEET,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1


item = DBItemProto(name="Plain Arms")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/ARMS/16"
item.material = "tset_0_arms"
item.slots = (RPG_SLOT_ARMS,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1

item = DBItemProto(name="Plain Pants")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/LEGS/16"
item.material = "tset_0_legs"
item.slots = (RPG_SLOT_LEGS,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1

item = DBItemProto(name="Plain Gloves")
item.skill = "Light Armor"
item.bitmap = "EQUIPMENT/HANDS/2"
item.material = "tset_0_hands"
item.slots = (RPG_SLOT_HANDS,)
item.flags=RPG_ITEM_SOULBOUND
item.armor = 1

RPG_REALM_DARKNESS_CLASSES =["Necromancer","Wizard","Cleric","Warrior","Barbarian","Tempest","Shaman","Assassin","Revealer","Thief","Doom Knight","Druid"]
RPG_REALM_LIGHT_CLASSES =["Shaman","Warrior","Paladin","Cleric","Tempest","Wizard","Monk","Barbarian","Thief","Druid","Bard","Ranger","Revealer"]

for cl in RPG_REALM_LIGHT_CLASSES:
    StartingGear(realm=RPG_REALM_LIGHT,classname=cl,items="Drinking Water,Tasty Meal,Plain Gloves,Plain Helm,Plain Boots,Plain Shirt,Plain Arms,Plain Pants,Longsword,Magic Shield")

for cl in RPG_REALM_DARKNESS_CLASSES:
    StartingGear(realm=RPG_REALM_DARKNESS,classname=cl,items="Drinking Water,Tasty Meal,Plain Gloves,Plain Boots,Plain Helm,Plain Shirt,Plain Arms,Plain Pants,Longsword,Magic Shield")
