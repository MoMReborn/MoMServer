from mud.world.defines import *
from genesis.dbdict import DBSpawnInfo,DBSpawnGroup

mob = DBSpawnInfo(spawn="Wolf Aggrorange 0",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLF0")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Wolf Aggrorange 1",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLF1")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Wolf Aggrorange 5",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLF5")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Wolf Aggrorange 10",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLF10")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Wolf Aggrorange 15",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLF15")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Wolf Aggrorange 20",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLF20")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Wolf",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLF")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Dog",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="DOG")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Wolf of Rolf",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="WOLFOFROLF")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Rolf",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="ROLF")
sg.addSpawnInfo(mob)

#--- Vendors
vendor = DBSpawnInfo(spawn="Stone Vendor")
sg = DBSpawnGroup(zone="base",groupName="Stone Vendor")
sg.addSpawnInfo(vendor)

vendor = DBSpawnInfo(spawn="Scroll Vendor")
sg = DBSpawnGroup(zone="base",groupName="Scroll Vendor")
sg.addSpawnInfo(vendor)

vendor = DBSpawnInfo(spawn="Weapon Vendor")
sg = DBSpawnGroup(zone="base",groupName="Weapon Vendor")
sg.addSpawnInfo(vendor)

vendor = DBSpawnInfo(spawn="Tool Vendor")
sg = DBSpawnGroup(zone="base",groupName="Tool Vendor")
sg.addSpawnInfo(vendor)

#--- Trainers
trainer = DBSpawnInfo(spawn="Skill Trainer")
sg = DBSpawnGroup(zone="base",groupName="Skill Trainer")
sg.addSpawnInfo(trainer)

#--- faction test
mob = DBSpawnInfo(spawn="Wolf of the Green")
sg = DBSpawnGroup(zone="base",groupName="Wolf of the Green")
sg.addSpawnInfo(mob)
mob = DBSpawnInfo(spawn="Follower of the Green")
sg = DBSpawnGroup(zone="base",groupName="Follower of the Green")
sg.addSpawnInfo(mob)
mob = DBSpawnInfo(spawn="Wolf of the Red")
sg = DBSpawnGroup(zone="base",groupName="Wolf of the Red")
sg.addSpawnInfo(mob)
mob = DBSpawnInfo(spawn="Follower of the Red")
sg = DBSpawnGroup(zone="base",groupName="Follower of the Red")
sg.addSpawnInfo(mob)
mob = DBSpawnInfo(spawn="Wolf of the Blue")
sg = DBSpawnGroup(zone="base",groupName="Wolf of the Blue")
sg.addSpawnInfo(mob)
mob = DBSpawnInfo(spawn="Follower of the Blue")
sg = DBSpawnGroup(zone="base",groupName="Follower of the Blue")
sg.addSpawnInfo(mob)

mob = DBSpawnInfo(spawn="Rolf")
sg = DBSpawnGroup(zone="base",groupName="TRIGGEREDROLF",targetName="TRROLFSP")
sg.addSpawnInfo(mob)
mob = DBSpawnInfo(spawn="Wolf")
sg = DBSpawnGroup(zone="base",groupName="TRIGGEREDWOLF",targetName="TRWOLFANDDOGSP")
sg.addSpawnInfo(mob)
mob = DBSpawnInfo(spawn="Dog")
sg = DBSpawnGroup(zone="base",groupName="TRIGGEREDDOG",targetName="TRWOLFANDDOGSP")
sg.addSpawnInfo(mob)

vendor = DBSpawnInfo(spawn="Food Vendor")
sg = DBSpawnGroup(zone="base",groupName="Food Vendor")
sg.addSpawnInfo(vendor)

fighter = DBSpawnInfo(spawn="Fighter")
sg = DBSpawnGroup(zone="base",groupName="Fighter")
sg.addSpawnInfo(fighter)

fighter = DBSpawnInfo(spawn="Wolfman")
sg = DBSpawnGroup(zone="base",groupName="Wolfman")
sg.addSpawnInfo(fighter)

#--- Human vs. Wolf
#---  Human Spawngroups
o1 = DBSpawnInfo(spawn="Human Destroyer")
sg = DBSpawnGroup(zone="base",groupName="DESTROYER")
sg.addSpawnInfo(o1)

o1 = DBSpawnInfo(spawn="Human Punisher")
sg = DBSpawnGroup(zone="base",groupName="PUNISHER")
sg.addSpawnInfo(o1)

o1 = DBSpawnInfo(spawn="Human Deathbinder")
sg = DBSpawnGroup(zone="base",groupName="DEATHBINDER")
sg.addSpawnInfo(o1)

o1 = DBSpawnInfo(spawn="Ororcali")
sg = DBSpawnGroup(zone="base",groupName="ORORCALI")
sg.addSpawnInfo(o1)

o1 = DBSpawnInfo(spawn="Taskmaster Duro")
sg = DBSpawnGroup(zone="base",groupName="TASKMASTER")
sg.addSpawnInfo(o1)

#---  Wolf Spawngroups
e1 = DBSpawnInfo(spawn="Wolf Crusader")
sg = DBSpawnGroup(zone="base",groupName="CRUSADER")
sg.addSpawnInfo(e1)

e1 = DBSpawnInfo(spawn="Wolf Protector")
sg = DBSpawnGroup(zone="base",groupName="PROTECTOR")
sg.addSpawnInfo(e1)

e1 = DBSpawnInfo(spawn="Captain Flamehorn")
sg = DBSpawnGroup(zone="base",groupName="CAPTAIN")
sg.addSpawnInfo(e1)

fighter = DBSpawnInfo(spawn="Fighter")
sg = DBSpawnGroup(zone="base",groupName="WALK1")
sg.addSpawnInfo(fighter)

fighter = DBSpawnInfo(spawn="Fighter")
sg = DBSpawnGroup(zone="base",groupName="WALK2")
sg.addSpawnInfo(fighter)

dragon = DBSpawnInfo(spawn="Grisu")
sg = DBSpawnGroup(zone="base",groupName="grisu")
sg.addSpawnInfo(dragon)

dragon = DBSpawnInfo(spawn="Red Baby Fire Dragon")
sg = DBSpawnGroup(zone="base",groupName="redbabydragon")
sg.addSpawnInfo(dragon)

dragon = DBSpawnInfo(spawn="Red Fire Dragon")
sg = DBSpawnGroup(zone="base",groupName="reddragon")
sg.addSpawnInfo(dragon)

dragon = DBSpawnInfo(spawn="Red King Fire Dragon")
sg = DBSpawnGroup(zone="base",groupName="redkingdragon")
sg.addSpawnInfo(dragon)

dragon = DBSpawnInfo(spawn="Green Baby Fire Dragon")
sg = DBSpawnGroup(zone="base",groupName="greenbabydragon")
sg.addSpawnInfo(dragon)

dragon = DBSpawnInfo(spawn="Green Fire Dragon")
sg = DBSpawnGroup(zone="base",groupName="greendragon")
sg.addSpawnInfo(dragon)

dragon = DBSpawnInfo(spawn="Green King Fire Dragon")
sg = DBSpawnGroup(zone="base",groupName="greenkingdragon")
sg.addSpawnInfo(dragon)

#--- Resource
oak = DBSpawnInfo(spawn="Oak Tree",frequency=RPG_FREQ_ALWAYS)
sg = DBSpawnGroup(zone="base",groupName="OAKTREE")
sg.addSpawnInfo(oak)
