from genesis.dbdict import *
from mud.world.defines import *

#Critter Pack Examples
#Available from:
#http://www.mmoworkshop.com/trac/mom/wiki/Store

#Bat

spawn = DBSpawn()
spawn.name = "Bat"
spawn.pclass = "Warrior"
spawn.plevel = 1
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = .25
spawn.model = "bat/bat.dts"
spawn.textureSingle = "bat_brown"

#Bear

spawn = DBSpawn()
spawn.name = "Kodiak"
spawn.pclass = "Warrior"
spawn.plevel = 8
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = 1.5
spawn.model = "bear/bear.dts"
spawn.textureSingle = "bear_grey"

spawn = spawn.clone(name = "Black Bear")
spawn.textureSingle = "bear_black"

spawn = spawn.clone(name = "Brown Bear")
spawn.textureSingle = "bear_brown"

spawn = spawn.clone(name = "Polar Bear")
spawn.textureSingle = "bear_polar"

#Beetles

spawn = DBSpawn()
spawn.name = "Desert Beetle"
spawn.pclass = "Warrior"
spawn.plevel = 2
spawn.race = "Insect"
spawn.isMonster = True
spawn.scale = .5
spawn.model = "beetle/beetle.dts"
spawn.textureSingle = "beetle_desert"

spawn = spawn.clone(name = "Fire Beetle")
spawn.textureSingle = "beetle_fire"

spawn = spawn.clone(name = "Scarab Beetle")
spawn.textureSingle = "beetle_scarab"

#Cats

spawn = DBSpawn()
spawn.name = "Panther"
spawn.pclass = "Warrior"
spawn.plevel = 6
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = 1.0
spawn.model = "cat/cat.dts"
spawn.textureSingle = "cat_panther"

spawn = spawn.clone(name = "Snow Leopard")
spawn.textureSingle = "cat_snow"

spawn = spawn.clone(name = "Mountain Lion")
spawn.textureSingle = "cat_mountain"

spawn = spawn.clone(name = "Tiger")
spawn.textureSingle = "cat_tiger"

#Crocodile

spawn = DBSpawn()
spawn.name = "Crocodile"
spawn.pclass = "Warrior"
spawn.plevel = 6
spawn.race = "Reptile"
spawn.isMonster = True
spawn.scale = 1.5
spawn.model = "crocodile/crocodile.dts"
spawn.textureSingle = "crocodile"

#Mammoth

spawn = DBSpawn()
spawn.name = "Mammoth"
spawn.pclass = "Warrior"
spawn.plevel = 6
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = 3.5
spawn.model = "mammoth/mammoth.dts"
spawn.textureSingle = "mammoth_special"
spawn.textureBody = "mammoth_body"

#Rats

spawn = DBSpawn()
spawn.name = "Rat"
spawn.pclass = "Warrior"
spawn.plevel = 6
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = .5
spawn.model = "rat/rat.dts"
spawn.textureSingle = "rat_brown"

spawn = spawn.clone(name = "Rabid Rat")
spawn.scale = .75
spawn.textureSingle = "rat_rabid"

#Snakes

spawn = DBSpawn()
spawn.name = "Green Snake"
spawn.pclass = "Warrior"
spawn.plevel = 6
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = .5
spawn.model = "snake/snake.dts"
spawn.textureSingle = "snake_green"

spawn = spawn.clone(name = "Striped Snake")
spawn.textureSingle = "snake_striped"

spawn = spawn.clone(name = "Solid Snake")
spawn.textureSingle = "snake_solid"

#Spiders

spawn = DBSpawn()
spawn.name = "Black Widow"
spawn.pclass = "Warrior"
spawn.plevel = 3
spawn.race = "Arachnid"
spawn.isMonster = True
spawn.scale = .5
spawn.model = "spider/spider.dts"
spawn.textureSingle = "spider_black"

spawn = spawn.clone(name = "Brown Recluse")
spawn.textureSingle = "spider_brown"

spawn = spawn.clone(name = "Jungle Spider")
spawn.textureSingle = "spider_green"

spawn = spawn.clone(name = "Demon Spider")
spawn.textureSingle = "spider_red"

#Turtle

spawn = DBSpawn()
spawn.name = "Snapper"
spawn.pclass = "Warrior"
spawn.plevel = 3
spawn.race = "Reptile"
spawn.isMonster = True
spawn.scale = .5
spawn.model = "turtle/turtle.dts"
spawn.textureBody = "turtle_body"
spawn.textureHead = "turtle_head"

#Wolves

spawn = DBSpawn()
spawn.name = "Arctic Wolf"
spawn.pclass = "Warrior"
spawn.plevel = 8
spawn.race = "Animal"
spawn.isMonster = True
spawn.scale = .8
spawn.model = "wolf/wolf.dts"
spawn.textureSingle = "wolf_arctic"

spawn = spawn.clone(name = "Dire Wolf")
spawn.textureSingle = "wolf_hell"



#Worm

spawn = DBSpawn()
spawn.name = "Worm"
spawn.pclass = "Warrior"
spawn.plevel = 3
spawn.race = "Reptile"
spawn.isMonster = True
spawn.scale = 4
spawn.model = "worm/worm.dts"
spawn.textureSingle = "worm"




