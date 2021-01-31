from genesis.dbdict import DBItemProto
from mud.world.defines import *

item = DBItemProto()
item.itemType = ['COMMON','DRINK']
item.stackMax = 100
item.drink = 1
item.stackDefault = 20

item.name = "Drinking Water"
item.bitmap = "STUFF/1"
item.worthTin = 3

item = item.clone(name = "Zharim Spring Water",drink = 5,worthCopper = 3,worthTin = 5)


item = DBItemProto()
item.itemType = ['COMMON','FOOD']
item.name = "Tasty Meal"
item.food = 3
item.stackMax = 100
item.stackDefault = 20
item.bitmap = "STUFF/32"
item.worthCopper = 5

item = item.clone(name = "Meager Meal",food = 1,worthCopper = 0,worthTin = 5)

#drops for some monster kills
item = item.clone(name ="Flesh and Blood",food=3,drink=3,itemType=[])
item.desc = "This is a mass of flesh and blood.  Delicious and nutritious!"
item.stackDefault = 1
item.bitmap = "STUFF/66"


