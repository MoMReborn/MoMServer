from genesis.dbdict import *
from mud.world.defines import *

#Monster Pack Examples
#Available from:
#http://www.mmoworkshop.com/trac/mom/wiki/Store

#Lycanthropes

spawn = DBSpawn()
spawn.name = "Werewolf"
spawn.pclass = "Warrior"
spawn.plevel = 10
spawn.race = "Lycanthrope"
spawn.isMonster = True
spawn.scale = 1.5
spawn.model = "werebeing/werebeing.dts"
spawn.textureHead = "werewolf_head"
spawn.textureBody = "werewolf_body"

spawn = spawn.clone(name = "Wererat")
spawn.textureHead = "wererat_head"
spawn.textureBody = "wererat_body"

spawn = spawn.clone(name = "Werecat")
spawn.textureHead = "werecat_head"
spawn.textureBody = "werecat_body"

#Amphibian

spawn = DBSpawn()
spawn.name = "Amphibian"
spawn.pclass = "Warrior"
spawn.plevel = 10
spawn.race = "Amphibian"
spawn.isMonster = True
spawn.scale = .75
spawn.model = "amphibian/amphibian.dts"
spawn.textureHead = "amphibian_head"
spawn.textureBody = "amphibian_body"
spawn.textureSingle = "amphibian_special"

#Efreet

spawn = DBSpawn()
spawn.name = "Efreet"
spawn.pclass = "Warrior"
spawn.plevel = 15
spawn.race = "Efreet"
spawn.isMonster = True
spawn.scale = 1.3
spawn.model = "efreet/efreet.dts"
spawn.textureHead = "efreet_head"
spawn.textureBody = "efreet_body"

#Elementals

spawn = DBSpawn()
spawn.name = "Earth Elemental"
spawn.pclass = "Warrior"
spawn.plevel = 15
spawn.race = "Elemental"
spawn.isMonster = True
spawn.scale = 1.2
spawn.model = "elemental/elemental.dts"
spawn.textureSingle = "elemental_earth"

spawn = spawn.clone(name = "Fire Elemental")
spawn.textureSingle = "elemental_fire"

spawn = spawn.clone(name = "Water Elemental")
spawn.textureSingle = "elemental_water"

spawn = spawn.clone(name = "Air Elemental")
spawn.textureSingle = "elemental_air"

#Gargoyle

spawn = DBSpawn()
spawn.name = "Gargoyle"
spawn.pclass = "Warrior"
spawn.plevel = 30
spawn.race = "Gargoyle"
spawn.isMonster = True
spawn.scale = 1.0
spawn.model = "gargoyle/gargoyle.dts"
spawn.textureSingle = "gargoyle"


#Imps

spawn = DBSpawn()
spawn.name = "Fire Imp"
spawn.pclass = "Warrior"
spawn.plevel = 30
spawn.race = "Imp"
spawn.isMonster = True
spawn.scale = 1.0
spawn.model = "imp/imp.dts"
spawn.textureSingle = "imp_fire"

spawn = spawn.clone(name = "Ice Imp")
spawn.textureSingle = "imp_ice"

#Lich

spawn = DBSpawn()
spawn.name = "Lich"
spawn.pclass = "Warrior"
spawn.plevel = 44
spawn.race = "Undead"
spawn.isMonster = True
spawn.scale = 1.8
spawn.model = "lich/lich.dts"
spawn.textureHead = "lich_head"
spawn.textureBody = "lich_body"

spawn = spawn.clone(name = "Lich Lord")
spawn.scale = 2.5
spawn.textureBody = "lich_lord_body"

#Mummy

spawn = DBSpawn()
spawn.name = "Mummy"
spawn.pclass = "Warrior"
spawn.plevel = 25
spawn.race = "Undead"
spawn.isMonster = True
spawn.scale = 1.1
spawn.model = "mummy/mummy.dts"
spawn.textureSingle = "undead_mummy"

#Zombies

spawn = DBSpawn()
spawn.name = "Zombie"
spawn.pclass = "Warrior"
spawn.plevel = 3
spawn.race = "Undead"
spawn.isMonster = True
spawn.scale = 1.1
spawn.model = "zombie/zombie.dts"
spawn.textureSingle = "undead_zombie"

spawn = spawn.clone(name = "Putrid Zombie")
spawn.plevel = 5
spawn.scale = 1.5
spawn.textureSingle = "undead_putrid"

#Skeleton

spawn = DBSpawn()
spawn.name = "Skeleton"
spawn.pclass = "Warrior"
spawn.plevel = 2
spawn.race = "Undead"
spawn.isMonster = True
spawn.scale = 1.0
spawn.model = "skeleton/skeleton.dts"
spawn.textureSingle = "skeleton"

#Shroom

spawn = DBSpawn()
spawn.name = "Shroom"
spawn.pclass = "Warrior"
spawn.plevel = 11
spawn.race = "Shroom"
spawn.isMonster = True
spawn.scale = 1.0
spawn.model = "shroom/shroom.dts"
spawn.textureSingle = "shroom_red"

#Scorpius

spawn = DBSpawn()
spawn.name = "Scorpius Drone"
spawn.pclass = "Warrior"
spawn.plevel = 11
spawn.race = "Scorpius"
spawn.isMonster = True
spawn.scale = 1.5
spawn.model = "scorpius_male/scorpius_male.dts"
spawn.textureSingle = "scorpius_male"

spawn = spawn.clone(name = "Scorpius Queen")
spawn.scale = 2.5
spawn.textureSingle = "scorpius_female"

