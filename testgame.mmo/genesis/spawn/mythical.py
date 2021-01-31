from genesis.dbdict import *
from mud.world.defines import *

#Mythical Creatures Pack Examples
#Available from:
#http://www.mmoworkshop.com/trac/mom/wiki/Store

#Dragons

spawn = DBSpawn()
spawn.name = "Gold Dragon"
spawn.pclass = "Warrior"
spawn.plevel = 50
spawn.race = "Dragon"
spawn.isMonster = True
spawn.scale = 6
spawn.model = "dragon_gold/dragon_gold.dts"
spawn.textureHead = "dragon_gold_head"
spawn.textureBody = "dragon_gold_body"
spawn.textureSingle = "dragon_gold_special"

spawn = spawn.clone(name = "Red Dragon")
spawn.model = "dragon_red/dragon_red.dts"
spawn.textureHead = "dragon_red_head"
spawn.textureBody = "dragon_red_body"
spawn.textureSingle = "dragon_red_special"

spawn = spawn.clone(name = "Green Dragon")
spawn.model = "dragon_green/dragon_green.dts"
spawn.textureHead = "dragon_green_head"
spawn.textureBody = "dragon_green_body"
spawn.textureSingle = "dragon_green_special"

spawn = spawn.clone(name = "Blue Dragon")
spawn.model = "dragon_blue/dragon_blue.dts"
spawn.textureHead = "dragon_blue_head"
spawn.textureBody = "dragon_blue_body"
spawn.textureSingle = "dragon_blue_special"

#Treant

spawn = DBSpawn()
spawn.name = "Treant"
spawn.pclass = "Warrior"
spawn.plevel = 60
spawn.race = "Treant"
spawn.isMonster = True
spawn.scale = 4
spawn.model = "treant/treant.dts"
spawn.textureHead = "treant_head"
spawn.textureBody = "treant_body"
spawn.textureSingle = "treant_special"

#Giants

spawn = DBSpawn()
spawn.name = "Hill Giant"
spawn.pclass = "Warrior"
spawn.plevel = 20
spawn.race = "Giant"
spawn.isMonster = True
spawn.scale = 4
spawn.model = "giant/giant.dts"
spawn.textureHead = "giant_hill_head"
spawn.textureBody = "giant_hill_body"
spawn.textureSingle = "giant_hill_special"

spawn = spawn.clone(name = "Sand Giant")
spawn.textureHead = "giant_sand_head"
spawn.textureBody = "giant_sand_body"
spawn.textureSingle = "giant_sand_special"

spawn = spawn.clone(name = "Storm Giant")
spawn.textureHead = "giant_storm_head"
spawn.textureBody = "giant_storm_body"
spawn.textureSingle = "giant_storm_special"

#Basilisk

spawn = DBSpawn()
spawn.name = "Basilisk"
spawn.pclass = "Warrior"
spawn.plevel = 24
spawn.race = "Basilisk"
spawn.isMonster = True
spawn.scale = 3
spawn.model = "basilisk/basilisk.dts"
spawn.textureHead = "basilisk_head"
spawn.textureBody = "basilisk_body"

#Demon

spawn = DBSpawn()
spawn.name = "Demon"
spawn.pclass = "Warrior"
spawn.plevel = 45
spawn.race = "Demon"
spawn.isMonster = True
spawn.scale = 3
spawn.model = "demon/demon.dts"
spawn.textureHead = "demon_head"
spawn.textureBody = "demon_body"
spawn.textureSingle = "demon_special"

#Bisotaur

spawn = DBSpawn()
spawn.name = "Bisotaur"
spawn.pclass = "Warrior"
spawn.plevel = 15
spawn.race = "Bisotaur"
spawn.isMonster = True
spawn.scale = 3
spawn.model = "bisotaur/bisotaur.dts"
spawn.textureHead = "bisotaur_head"
spawn.textureBody = "bisotaur_body"
spawn.textureSingle = "bisotaur_special"

spawn = spawn.clone(name = "Bisotaur Lord")
spawn.textureHead = "bisotaur_lord_head"
spawn.textureBody = "bisotaur_lord_body"
spawn.textureSingle = "bisotaur_lord_special"