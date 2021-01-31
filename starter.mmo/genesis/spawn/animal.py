#---WOLVES
from genesis.dbdict import *
from mud.world.defines import *
from mud.world.spawn import SpawnSoundProfile

durSecond = 6
durMinute = durSecond * 60
durHour = durMinute * 60


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

#--- Grey Wolf

sounds = SpawnSoundProfile()

sounds.sndAttack1 = "character/ZombieDog_Attack1.ogg"
sounds.sndAttack2 = "character/ZombieDog_Attack2.ogg"
sounds.sndAttack3 = "character/ZombieDog_Attack3.ogg"

sounds.sndAlert1 = "character/ZombieDog_Growl2.ogg"
sounds.sndAlert2 = "character/ZombieDog_Growl3.ogg"

sounds.sndPain1 = "character/ZombieDog_Hurt1.ogg"
sounds.sndPain2 = "character/ZombieDog_Hurt2.ogg"
sounds.sndPain3 = "character/ZombieDog_Hurt2.ogg"

sounds.sndDeath1 = "character/ZombieDog_Death1.ogg"
sounds.sndDeath2 = "character/ZombieDog_Death2.ogg"

spawn = DBSpawn()
spawn.name = "Grey Wolf"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = 1
spawn.flags = 0
# START: baked in animation
spawn.model = "wolf/wolf.dts"
# END: baked in animation
# START: DSQ based animation
#spawn.model = "wolf/wolf_dsqanim.dts"
#spawn.animation = "wolf"
# END: DSQ based animation

spawn.textureSingle = "wolf_grey"
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot
spawn.sndProfile = sounds
