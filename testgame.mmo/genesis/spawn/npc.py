from genesis.dbdict import *
from mud.world.defines import *
from mud.world.spawn import SpawnSoundProfile


spawn = DBSpawn()
spawn.name = "Azala Dogooder"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Human"
spawn.sex = "Female"
spawn.pclass = "Warrior"
spawn.plevel = 10
spawn.isMonster = False
spawn.realm = RPG_REALM_NEUTRAL

#Avatar Pack Examples
#Available from:
#http://www.mmoworkshop.com/trac/mom/wiki/Store

"""

spawn = DBSpawn()
spawn.name = "Lithian Treil"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Elf"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 25
spawn.isMonster = False
spawn.realm = RPG_REALM_NEUTRAL

spawn = DBSpawn()
spawn.name = "Thurgin Oakenshielf"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Dwarf"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 35
spawn.isMonster = False
spawn.realm = RPG_REALM_NEUTRAL

spawn = DBSpawn()
spawn.name = "Blingo Longbottom"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Halfling"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 60
spawn.isMonster = False
spawn.realm = RPG_REALM_NEUTRAL


spawn = DBSpawn()
spawn.name = "Azarek Relik"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Gnome"
spawn.sex = "Female"
spawn.pclass = "Warrior"
spawn.plevel = 33
spawn.isMonster = False
spawn.realm = RPG_REALM_NEUTRAL

spawn = DBSpawn()
spawn.name = "Hemok Stonebreaker"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Titan"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 10
spawn.isMonster = False
spawn.realm = RPG_REALM_NEUTRAL

spawn = DBSpawn()
spawn.name = "Glarg Wickedblade"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Orc"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 50
spawn.isMonster = True

spawn = DBSpawn()
spawn.name = "Oshkosh Betosh"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Ogre"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 15
spawn.isMonster = True

spawn = DBSpawn()
spawn.name = "Cillik Neidle"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Goblin"
spawn.sex = "Female"
spawn.pclass = "Warrior"
spawn.plevel = 54
spawn.isMonster = True

spawn = DBSpawn()
spawn.name = "Tor the Brute"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Troll"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 40
spawn.isMonster = True

spawn = DBSpawn()
spawn.name = "Isis Krarn"
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Drakken"
spawn.sex = "Female"
spawn.pclass = "Warrior"
spawn.plevel = 20
spawn.isMonster = True

"""
# VendorNPC for tools
spawn = DBSpawn()
spawn.name = "Tool Vendor"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Paladin"
spawn.sex = "Male"
spawn.race = "Human"
spawn.plevel = 30
spawn.isMonster = False

spawn.flags = RPG_SPAWN_UNIQUE
spawn.aggroRange = 10

spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"

spawn.desc = ""

spawn.vendor = "Tool Vendor"

spawn.addSkill("Dual Wield",1)
loot = DBLootProto()
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Broadsword", RPG_FREQ_COMMON)
loot.addItem("Magic Shield", RPG_FREQ_COMMON)
spawn.loot = loot

# VendorNPC for stones
spawn = DBSpawn()
spawn.name = "Stone Vendor"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Paladin"
spawn.sex = "Male"
spawn.race = "Human"
spawn.plevel = 30
spawn.isMonster = False

spawn.flags = RPG_SPAWN_UNIQUE
spawn.aggroRange = 10

spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"

spawn.dialog = "Stone Vendor Dialog"
spawn.desc = "He really sells and buys stones. So maybe he is a little stoned himself."

spawn.vendor = "Vendorman"

spawn.addSkill("Dual Wield",1)
loot = DBLootProto()
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Broadsword", RPG_FREQ_COMMON)
loot.addItem("Magic Shield", RPG_FREQ_COMMON)
spawn.loot = loot

# VendorNPC for scrolls
spawn = DBSpawn()
spawn.name = "Scroll Vendor"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Paladin"
spawn.sex = "Male"
spawn.race = "Human"
spawn.plevel = 30
spawn.isMonster = False

spawn.flags = RPG_SPAWN_UNIQUE
spawn.aggroRange = 10

spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"

spawn.dialog = "Scroll Vendor Dialog"
spawn.desc = "He sells and buys scrolls."

spawn.vendor = "Spell Dealer"

loot = DBLootProto()
loot.addItem("Magic Shield", RPG_FREQ_ALWAYS)
loot.addItem("Longsword", RPG_FREQ_ALWAYS)
spawn.loot = loot

# VendorNPC for weapons
spawn = DBSpawn()
spawn.name = "Weapon Vendor"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Paladin"
spawn.sex = "Male"
spawn.race = "Human"
spawn.plevel = 30
spawn.isMonster = False

spawn.flags = RPG_SPAWN_UNIQUE
spawn.aggroRange = 10

spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"

spawn.dialog = "Weapon Vendor Dialog"
spawn.desc = "He sells and buys Weapons."

spawn.vendor = "Weapon Vendor"

spawn.addSkill("Dual Wield",1)
loot = DBLootProto()
loot.addItem("Longsword", RPG_FREQ_ALWAYS)
loot.addItem("Longsword", RPG_FREQ_ALWAYS)
spawn.loot = loot

# TrainerNPC for skills
spawn = DBSpawn()
spawn.name = "Skill Trainer"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Paladin"
spawn.sex = "Male"
spawn.race = "Human"
spawn.plevel = 30
spawn.isMonster = False

spawn.flags = RPG_SPAWN_UNIQUE
spawn.aggroRange = 10

spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"

spawn.dialog = "Skill Trainer Dialog"
spawn.desc = "He trains skills."

loot = DBLootProto()
loot.addItem("Broadsword", RPG_FREQ_ALWAYS)
spawn.loot = loot

# NPCs for factions
spawn = DBSpawn()
spawn.name = "Follower of the Green"
spawn.realm = RPG_REALM_NEUTRAL
spawn.sex = "Male"
spawn.race = "Human"
spawn.pclass = "Warrior"
spawn.plevel = 1
spawn.isMonster = False
spawn.flags = RPG_SPAWN_NOASSIST
spawn.aggroRange = 20
spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"
spawn.desc = "He is for the Green."
spawn.addFaction("The Green")
spawn.addKillFaction("The Blue")
spawn.addKillFaction("The Red")

spawn = DBSpawn()
spawn.name = "Follower of the Red"
spawn.realm = RPG_REALM_NEUTRAL
spawn.sex = "Male"
spawn.race = "Human"
spawn.pclass = "Warrior"
spawn.plevel = 1
spawn.isMonster = False
spawn.flags = RPG_SPAWN_NOASSIST
spawn.aggroRange = 20
spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"
spawn.desc = "He is for the Red."
spawn.addFaction("The Red")
spawn.addKillFaction("The Blue")
spawn.addKillFaction("The Green")

spawn = DBSpawn()
spawn.name = "Follower of the Blue"
spawn.realm = RPG_REALM_NEUTRAL
spawn.sex = "Male"
spawn.race = "Human"
spawn.pclass = "Warrior"
spawn.plevel = 1
spawn.isMonster = False
spawn.flags = RPG_SPAWN_NOASSIST
spawn.aggroRange = 20
spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"
spawn.desc = "He is for the Blue."
spawn.addFaction("The Blue")
spawn.addKillFaction("The Green")
spawn.addKillFaction("The Red")

# VendorNPC for Food and Drinks
spawn = DBSpawn()
spawn.name = "Food Vendor"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Paladin"
spawn.sex = "Female"
spawn.race = "Human"
spawn.plevel = 30
spawn.isMonster = False
spawn.flags = RPG_SPAWN_UNIQUE
spawn.aggroRange = 10
spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "B"
spawn.dialog = "Food Vendor Dialog"
spawn.desc = "Here you can get nice snacks."
spawn.vendor = "Snacks"
spawn.addSkill("Dual Wield",1)
loot = DBLootProto()
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Broadsword", RPG_FREQ_COMMON)
loot.addItem("Magic Shield", RPG_FREQ_COMMON)
spawn.loot = loot

# NPC for fighting
spawn = DBSpawn()
spawn.name = "Fighter"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Warrior"
spawn.sex = "Male"
spawn.race = "Human"
spawn.plevel = 10
spawn.isMonster = False
spawn.flags = 0
spawn.aggroRange = 20
spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"
spawn.desc = "A fighter."

# NPC for Quest
spawn = DBSpawn()
spawn.name = "Wolfman"
spawn.realm = RPG_REALM_LIGHT
spawn.pclass = "Paladin"
spawn.sex = "Male"
spawn.race = "Human"
spawn.plevel = 30
spawn.isMonster = False
spawn.flags = RPG_SPAWN_UNIQUE
spawn.aggroRange = 10
spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"
spawn.dialog = "The Wolf Quest"
spawn.desc = "He will give you a quest."
spawn.addSkill("Dual Wield",1)
loot = DBLootProto()
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Longsword", RPG_FREQ_COMMON)
loot.addItem("Broadsword", RPG_FREQ_COMMON)
loot.addItem("Magic Shield", RPG_FREQ_COMMON)
spawn.loot = loot

# NPC and mobs for epic battle
#--- Taskmaster Duro
spawn = DBSpawn()
spawn.name = "Taskmaster Duro"
spawn.race = "Human"
spawn.sex = "Female"
spawn.pclass = "Doom Knight"
spawn.plevel = 40
spawn.difficultyMod = 2
spawn.isMonster = False
spawn.flags = RPG_SPAWN_UNIQUE
spawn.textureArms = "tset_0_arms"
spawn.textureLegs = "tset_0_legs"
spawn.textureBody = "tset_0_body"
spawn.textureHands = "tset_0_hands"
spawn.textureFeet = "tset_0_feet"
spawn.vocalSet = "A"
spawn.dialog = "HumanWolfSkirmishReward"
spawn.desc = ""

#--- Ororcali
spawn = spawn.clone()
spawn.name = "Ororcali"
spawn.sex = "Male"
spawn.pclass = "Warrior"
spawn.plevel = 38
spawn.difficultyMod = 1
spawn.dialog = ""

#--- Human Deathbinder
spawn = spawn.clone()
spawn.name = "Human Deathbinder"
spawn.pclass = "Assassin"
spawn.flags = 0

#--- Human Punisher
spawn = spawn.clone()
spawn.name = "Human Punisher"
spawn.pclass = "Wizard"
spawn.plevel = 36

#--- Human Destroyer
spawn = spawn.clone()
spawn.name = "Human Destroyer"
spawn.pclass = "Barbarian"
spawn.plevel = 34

#--- Captain Flamehorn
spawn = DBSpawn()
spawn.name = "Captain Flamehorn"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Paladin"
spawn.plevel = 33
spawn.difficultyMod = 2
spawn.isMonster = False
spawn.flags = RPG_SPAWN_UNIQUE
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
sound = SpawnSoundProfile()
sound.sndAlert1 = "character/ZombieDog_Growl2.ogg"
sound.sndAlert2 = "character/ZombieDog_Growl3.ogg"
sound.sndAttack1 = "character/ZombieDog_Attack1.ogg"
sound.sndAttack2 = "character/ZombieDog_Attack2.ogg"
sound.sndAttack3 = "character/ZombieDog_Attack3.ogg"
sound.sndPain1 = "character/ZombieDog_Hurt1.ogg"
sound.sndPain2 = "character/ZombieDog_Hurt2.ogg"
sound.sndPain3 = "character/ZombieDog_Hurt3.ogg"
sound.sndDeath1 = "character/ZombieDog_Death1.ogg"
sound.sndDeath2 = "character/ZombieDog_Death2.ogg"
spawn.sndProfile = sound
spawn.vocalSet = ""

#--- Wolf Protector
spawn = spawn.clone()
spawn.name = "Wolf Protector"
spawn.pclass = "Warrior"
spawn.plevel = 28
spawn.difficultyMod = 1
spawn.flags = 0

#--- Wolf Crusader
spawn = spawn.clone()
spawn.name = "Wolf Crusader"
spawn.pclass = "Cleric"
spawn.plevel = 25

#--- Oak Tree
spawn = DBSpawn() 
spawn.name = "Oak Tree" 
spawn.pclass = "Harvest" 
spawn.plevel = 1 
spawn.race = "Tree" 
spawn.requiresWeapon = "Foresting" 
spawn.isMonster = True 
spawn.scale = 2 
spawn.aggroRange = 0 
spawn.move = 0 
spawn.model = "wolf/wolf.dts" 
spawn.flags = RPG_SPAWN_RESOURCE|RPG_SPAWN_NOXP|RPG_SPAWN_PASSIVE|RPG_SPAWN_NORANDOMLOOT
spawn.textureSingle = "wolf_grey" 
#loot = DBLootProto() 
#loot.addItem("Oak wood",RPG_FREQ_COMMON) 
#spawn.loot = loot 
spawn.addResistance(RPG_RESIST_PHYSICAL,100) 
spawn.addResistance(RPG_RESIST_MAGICAL,100) 
spawn.addResistance(RPG_RESIST_FIRE,100) 
spawn.addResistance(RPG_RESIST_COLD,100) 
spawn.addResistance(RPG_RESIST_POISON,100) 
spawn.addResistance(RPG_RESIST_DISEASE,100) 
spawn.addResistance(RPG_RESIST_ACID,100) 
spawn.addResistance(RPG_RESIST_ELECTRICAL,100) 
spawn.addResistance(RPG_RESIST_MINE,100)