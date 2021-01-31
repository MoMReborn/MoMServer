from genesis.dbdict import *
from mud.world.defines import *

#--- Defines
durSecond = 6
durMinute = durSecond * 60
durHour = durMinute * 60

r = DBRecipe(name = "Zharim Spring Water")
r.skillname = "Brewing"
r.craftSound = "sfx/Underwater_Bubbles2.ogg"
r.addIngredient("Drinking Water",3)
r.addIngredient("Strange slimy stone",1)
r.skillLevel = 1
r.craftItem = "Zharim Spring Water"
r.costCP = 3

r = DBRecipe(name = "Tasty Meal")
r.skillname = "Cooking"
r.craftSound = "sfx/Underwater_Bubbles2.ogg"
r.addIngredient("Meager Meal",3)
r.addIngredient("Strange slimy stone",1)
r.skillLevel = 1
r.craftItem = "Tasty Meal"
r.costCP = 3

r = DBRecipe(name = "Flaming Arrow")
r.skillname = "Archery"
r.craftSound = "sfx/Underwater_Bubbles2.ogg"
r.addIngredient("Feather Arrow",4)
r.skillLevel = 1
r.craftItem = "Flaming Arrow"
r.costCP = 3
