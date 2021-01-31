from genesis.dbdict import DBClassSkill
from genesis.dbdict import DBSpellProto,DBEffectProto
from mud.world.defines import *

#--- DEFINES
durSecond = 6
durMinute = durSecond * 60
durHour = durMinute * 60

effect = DBEffectProto(name = "Paladin Healing Hands - Skill")
effect.addStat(RPG_EFFECT_STAGE_BEGIN,"health",2500)

spell = DBSpellProto()
spell.name = "Paladin Healing Hands - Skill"
spell.spellType = RPG_SPELL_HEALING
spell.target = RPG_TARGET_OTHER
spell.duration = 0
spell.castTime = 0
spell.castRange = 10
spell.recastTime = 0
spell.harmful = False
spell.addEffect("Paladin Healing Hands - Skill")
spell.beginMsg = "$src lays hands on $tgt!"
spell.sndBegin = "sfx/Magic_Appear01.ogg"

skill = DBClassSkill(skillname = "Healing Hands")
skill.type = ['Paladin']
skill.minReuseTime = durMinute * 3
skill.maxReuseTime = durMinute * 6
skill.levelGained = 1
skill.levelCapped = 50
skill.maxValue = 500
skill.trained = True
skill.spellProto = "Paladin Healing Hands - Skill"
