from mud.world.battle import BattleGroup,BattleSequence,BattleResult,BattleMustSurvive,BattleProto
from genesis.dbdict import *

#--- DEFINES
durSecond = 6
durMinute = durSecond * 60
durHour = durMinute * 60

battle = BattleProto(name="HumanWolfSkirmish",zoneName = "base")

battle.zoneMessage = "Great armies of humans and wolves are amassed!  The battle will soon be fought!"
battle.zoneSound = "sfx/College_DrumCadence07.ogg"

BattleMustSurvive(name="Taskmaster Duro",battleProto=battle)
BattleMustSurvive(name="Captain Flamehorn",battleProto=battle)

#--- SIDE 1 SEQUENCE 1
bs = BattleSequence()
bs.zoneSound = "sfx/College_DrumCadence03.ogg"
battle.side1StartSequence = bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S1_1"
bg.spawnGroup = "DESTROYER"
bg.attackDelay = 60*durSecond
bg.battleSequence=bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S1_2"
bg.spawnGroup = "PUNISHER"
bg.attackDelay = 65*durSecond
bg.battleSequence=bs

#--- SIDE 1 SEQUENCE 2
bs.nextSequence = bs = BattleSequence()
bs.zoneSound = "sfx/College_DrumCadence25.ogg"
bs.zoneMessage = "Taskmaster Duro and his troopers have joined the battle!"

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S1_3"
bg.spawnGroup = "DEATHBINDER"
bg.battleSequence=bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S1_4"
bg.spawnGroup = "ORORCALI"
bg.battleSequence=bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S1_0"
bg.spawnGroup = "TASKMASTER"
bg.battleSequence=bs

#--- SIDE 2 SEQUENCE 1
bs = BattleSequence()
bs.zoneSound = "sfx/College_DrumCadence11.ogg"
battle.side2StartSequence = bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S2_1"
bg.spawnGroup = "CRUSADER"
bg.attackDelay = 65*durSecond
bg.battleSequence=bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S2_2"
bg.spawnGroup = "PROTECTOR"
bg.attackDelay = 70*durSecond
bg.battleSequence=bs

#--- SIDE 2 SEQUENCE 2
bs.nextSequence = bs = BattleSequence()
bs.zoneSound = "sfx/College_DrumCadence25.ogg"
bs.zoneMessage = "Captain Flamehorn has joined the battle!"

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S2_3"
bg.spawnGroup = "CRUSADER"
bg.battleSequence=bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S2_4"
bg.spawnGroup = "PROTECTOR"
bg.attackDelay = 5*durSecond
bg.battleSequence=bs

bg = BattleGroup()
bg.triggerSpawnGroup = "B1_S2_0"
bg.spawnGroup = "CAPTAIN"
bg.attackDelay = 15*durSecond
bg.passive = True
bg.battleSequence=bs

#--- end results
s1victory = BattleResult()
s1victory.zoneMessage = "Taskmaster Duro's legions are victorious!"
s1victory.triggerSpawnGroup = "B1_S1_0"
s1victory.spawnGroup = "TASKMASTER"
s1victory.zoneSound = "sfx/College_DrumCadence07.ogg"

s2victory = BattleResult()
s2victory.zoneMessage = "Captain Flamehorn has prevailed!"
s2victory.triggerSpawnGroup = "B1_S2_0"
s2victory.spawnGroup = "CAPTAIN"
s2victory.zoneSound = "sfx/College_DrumCadence07.ogg"

battle.side1VictoryResult = s1victory
battle.side2VictoryResult = s2victory
