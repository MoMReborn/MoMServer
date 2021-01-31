from genesis.dbdict import *
from mud.world.defines import *
from mud.world.spawn import SpawnSoundProfile

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

spawn = DBSpawn()
spawn.name = "Wolf Aggrorange 0"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 0
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addSkill("Kick",1)
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf Aggrorange 1"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 1
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addSkill("Kick",1)
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf Aggrorange 5"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 5
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addSkill("Kick",1)
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf Aggrorange 10"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 10
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addSkill("Kick",1)
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf Aggrorange 15"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 15
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addSkill("Kick",1)
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf Aggrorange 20"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addSkill("Kick",1)
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Dog"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = RPG_SPAWN_NOASSIST
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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

spawn = DBSpawn()
spawn.name = "Wolf of Rolf"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
# START: baked in animation
spawn.model = "wolf/wolf.dts"
# END: baked in animation
# START: DSQ based animation
#spawn.model = "wolf/wolf_dsqanim.dts"
#spawn.animation = "wolf"
# END: DSQ based animation
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Rolf"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 3
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = RPG_SPAWN_NOASSIST
# START: baked in animation
spawn.model = "wolf/wolf.dts"
# END: baked in animation
# START: DSQ based animation
#spawn.model = "wolf/wolf_dsqanim.dts"
#spawn.animation = "wolf"
# END: DSQ based animation
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
loot = DBLootProto()
loot.addItem("Strange stone", RPG_FREQ_ALWAYS)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Mountain Crawler"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
loot = DBLootProto()
loot.addItem("Strange cold stone", RPG_FREQ_ALWAYS)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Swamp Walker"
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = True
spawn.flags = 0
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
loot = DBLootProto()
loot.addItem("Strange slimy stone", RPG_FREQ_ALWAYS)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf of the Blue"
spawn.realm = RPG_REALM_NEUTRAL
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = False
spawn.flags = RPG_SPAWN_NOASSIST
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addFaction("The Blue")
spawn.addKillFaction("The Red")
spawn.addKillFaction("The Green")
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf of the Red"
spawn.realm = RPG_REALM_NEUTRAL
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = False
spawn.flags = RPG_SPAWN_NOASSIST
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addFaction("The Red")
spawn.addKillFaction("The Blue")
spawn.addKillFaction("The Green")
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf of the Green"
spawn.realm = RPG_REALM_NEUTRAL
spawn.race = "Animal"
spawn.sex = "Male"
spawn.pclass = "Assassin"
spawn.plevel = 1
spawn.sclass = ""
spawn.slevel = 1
spawn.tclass = ""
spawn.tlevel = 1
spawn.isMonster = False
spawn.flags = RPG_SPAWN_NOASSIST
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.aggroRange = 20
spawn.xpMod = 0
spawn.difficultyMod = 0
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
spawn.addFaction("The Green")
spawn.addKillFaction("The Blue")
spawn.addKillFaction("The Red")
loot = DBLootProto()
loot.addItem("Grey Wolf Hide", RPG_FREQ_ALWAYS)
loot.addItem("Wolf Meat", RPG_FREQ_COMMON)
spawn.loot = loot

spawn = DBSpawn()
spawn.name = "Wolf Consort"
spawn.pclass = "Warrior"
spawn.plevel = 3
spawn.sex = "Male"
spawn.race = "Animal"
spawn.isMonster = False
spawn.model = "wolf/wolf.dts"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "wolf_grey"
spawn.radius = 2
spawn.scale = .75
spawn.aggroRange = 20
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
spawn.sndProfile = sounds

effect = DBEffectProto(name="Fire Dragon AoE I")
effect.addDamage(RPG_DMG_FIRE,60)
effect.resist = RPG_RESIST_FIRE

spell = DBSpellProto(name="Fire Dragon AoE I")
spell.target = RPG_TARGET_SELF
spell.duration = 0
spell.castRange = 100
spell.recastTime = 0
spell.harmful = True
spell.sndCasting = "environment/thunder1.ogg"
spell.sndBegin = "environment/thunder4.ogg"
spell.sndBeginDuration = 6 * durSecond
spell.manaCost = 2
spell.aoeRange = 25
spell.castTime = 10 * durSecond
spell.castingMsg = "A deep rumbling begins within $src..."
spell.beginMsg = "$tgt is blasted by dragon's breath!!!"
spell.addParticleNode("special0","DragonFireEmitter","",6)
spell.addParticleNode("special0","DragonSmokeEmitter","",6)
spell.effects.append("Fire Dragon AoE I")
spell.addClass("Wizard",1)

effect = DBEffectProto(name="Fire Dragon AoE II")
effect.addDamage(RPG_DMG_FIRE,120)
effect.resist = RPG_RESIST_FIRE

spell = DBSpellProto(name="Fire Dragon AoE II")
spell.target = RPG_TARGET_SELF
spell.duration = 0
spell.castRange = 100
spell.recastTime = 0
spell.harmful = True
spell.sndCasting = "environment/thunder1.ogg"
spell.sndBegin = "environment/thunder4.ogg"
spell.sndBeginDuration = 6 * durSecond
spell.manaCost = 4
spell.aoeRange = 25
spell.castTime = 10 * durSecond
spell.castingMsg = "A deep rumbling begins within $src..."
spell.beginMsg = "$tgt is blasted by dragon's breath!!!"
spell.addParticleNode("special0","DragonFireEmitter","",6)
spell.addParticleNode("special0","DragonSmokeEmitter","",6)
spell.effects.append("Fire Dragon AoE II")
spell.addClass("Wizard",1)

effect = DBEffectProto(name="Fire Dragon AoE III")
effect.addDamage(RPG_DMG_FIRE,180)
effect.resist = RPG_RESIST_FIRE

spell = DBSpellProto(name="Fire Dragon AoE III")
spell.target = RPG_TARGET_SELF
spell.duration = 0
spell.castRange = 100
spell.recastTime = 0
spell.harmful = True
spell.sndCasting = "environment/thunder1.ogg"
spell.sndBegin = "environment/thunder4.ogg"
spell.sndBeginDuration = 6 * durSecond
spell.manaCost = 6
spell.aoeRange = 25
spell.castTime = 10 * durSecond
spell.castingMsg = "A deep rumbling begins within $src..."
spell.beginMsg = "$tgt is blasted by dragon's breath!!!"
spell.addParticleNode("special0","DragonFireEmitter","",6)
spell.addParticleNode("special0","DragonSmokeEmitter","",6)
spell.effects.append("Fire Dragon AoE III")
spell.addClass("Wizard",1)

sounds = SpawnSoundProfile()
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
spawn = DBSpawn()
spawn.name = "Red Baby Fire Dragon"
spawn.pclass = "Wizard"
spawn.plevel = 6
spawn.realm = RPG_REALM_MONSTER
spawn.isMonster = True
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Dragon"
spawn.sex = "Male"
spawn.radius=5
spawn.scale=10
spawn.move = 10
spawn.aggroRange = 20
spawn.followRange = 150
spawn.difficultyMod = 2
spawn.model = "rex/rex.dts"
spawn.animation = "rex"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "rex"
spawn.sndProfile = sounds
spawn.vocalSet = ''
spawn.desc = "Hot and spicy."
spawn.addResistance(RPG_RESIST_FIRE,100)
spawn.addSpell("Fire Dragon AoE I")

spawn = DBSpawn()
spawn.name = "Red Fire Dragon"
spawn.pclass = "Wizard"
spawn.plevel = 12
spawn.realm = RPG_REALM_MONSTER
spawn.isMonster = True
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Dragon"
spawn.sex = "Male"
spawn.radius=5
spawn.scale=10
spawn.move = 10
spawn.aggroRange = 20
spawn.followRange = 150
spawn.difficultyMod = 2
spawn.model = "rex/rex.dts"
spawn.animation = "rex"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "rex"
spawn.sndProfile = sounds
spawn.vocalSet = ''
spawn.desc = "Hot and spicy."
spawn.addResistance(RPG_RESIST_FIRE,100)
spawn.addSpell("Fire Dragon AoE I")
spawn.addSpell("Fire Dragon AoE II")

spawn = DBSpawn()
spawn.name = "Red King Fire Dragon"
spawn.pclass = "Wizard"
spawn.plevel = 18
spawn.realm = RPG_REALM_MONSTER
spawn.isMonster = True
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Dragon"
spawn.sex = "Male"
spawn.radius=5
spawn.scale=10
spawn.move = 10
spawn.aggroRange = 20
spawn.followRange = 150
spawn.difficultyMod = 2
spawn.model = "rex/rex.dts"
spawn.animation = "rex"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "rex"
spawn.sndProfile = sounds
spawn.vocalSet = ''
spawn.desc = "Hot and spicy."
spawn.addResistance(RPG_RESIST_FIRE,100)
spawn.addSpell("Fire Dragon AoE I")
spawn.addSpell("Fire Dragon AoE II")
spawn.addSpell("Fire Dragon AoE III")

sounds = SpawnSoundProfile()
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
spawn = DBSpawn()
spawn.name = "Green Baby Fire Dragon"
spawn.pclass = "Wizard"
spawn.plevel = 6
spawn.realm = RPG_REALM_MONSTER
spawn.isMonster = True
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Dragon"
spawn.sex = "Male"
spawn.radius=5
spawn.scale=10
spawn.move = 10
spawn.aggroRange = 20
spawn.followRange = 150
spawn.difficultyMod = 2
spawn.model = "rex/rex.dts"
spawn.animation = "rex"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "rex"
spawn.sndProfile = sounds
spawn.vocalSet = ''
spawn.desc = "Hot and spicy."
spawn.addResistance(RPG_RESIST_FIRE,100)
spawn.addSpell("Fire Dragon AoE I")

spawn = DBSpawn()
spawn.name = "Green Fire Dragon"
spawn.pclass = "Wizard"
spawn.plevel = 12
spawn.realm = RPG_REALM_MONSTER
spawn.isMonster = True
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Dragon"
spawn.sex = "Male"
spawn.radius=5
spawn.scale=10
spawn.move = 10
spawn.aggroRange = 20
spawn.followRange = 150
spawn.difficultyMod = 2
spawn.model = "rex/rex.dts"
spawn.animation = "rex"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "rex"
spawn.sndProfile = sounds
spawn.vocalSet = ''
spawn.desc = "Hot and spicy."
spawn.addResistance(RPG_RESIST_FIRE,100)
spawn.addSpell("Fire Dragon AoE I")
spawn.addSpell("Fire Dragon AoE II")

spawn = DBSpawn()
spawn.name = "Green King Fire Dragon"
spawn.pclass = "Wizard"
spawn.plevel = 18
spawn.realm = RPG_REALM_MONSTER
spawn.isMonster = True
spawn.flags = RPG_SPAWN_UNIQUE
spawn.race = "Dragon"
spawn.sex = "Male"
spawn.radius=5
spawn.scale=10
spawn.move = 10
spawn.aggroRange = 20
spawn.followRange = 150
spawn.difficultyMod = 2
spawn.model = "rex/rex.dts"
spawn.animation = "rex"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "rex"
spawn.sndProfile = sounds
spawn.vocalSet = ''
spawn.desc = "Hot and spicy."
spawn.addResistance(RPG_RESIST_FIRE,100)
spawn.addSpell("Fire Dragon AoE I")
spawn.addSpell("Fire Dragon AoE II")
spawn.addSpell("Fire Dragon AoE III")

sounds = SpawnSoundProfile()
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
spawn = DBSpawn()
spawn.name = "Grisu"
spawn.pclass = "Warrior"
spawn.plevel = 4
spawn.race = "Dragon"
spawn.realm = RPG_REALM_MONSTER
spawn.isMonster = True
spawn.aggroRange = 20
spawn.scale = 1.5
spawn.move = 1.5
spawn.flags = RPG_SPAWN_NOASSIST
spawn.model = "rex/rex.dts"
spawn.animation = "rex"
spawn.textureArms = ""
spawn.textureLegs = ""
spawn.textureBody = ""
spawn.textureHands = ""
spawn.textureFeet = ""
spawn.textureHead = ""
spawn.textureSingle = "rex"
spawn.sndProfile = sounds
