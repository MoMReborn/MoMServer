from genesis.dbdict import *
from mud.world.defines import *

durSecond = 6
durMinute = durSecond * 60
durHour = durMinute * 60

effect = DBEffectProto(name="Arcane Blast")
effect.addDamage(RPG_DMG_MAGICAL,100)
effect.resist = RPG_RESIST_MAGICAL

spell = DBSpellProto()
spell.name = "Arcane Blast"
spell.spellbookPic = "SPELLICON_1_25"
spell.particleTextureCasting = "staticring"
spell.particleCasting = "ChimneySmokeEmitter"
spell.sndCasting = "sfx/MagicSpell_CastingLoop1.ogg"
spell.particleTextureBegin = "staticring"
spell.particleBegin = "ChimneyFireEmitter"
spell.sndBegin = "sfx/DarkMagic_SpellImpact01.ogg"
spell.beginMsg = "$tgt is struck by an arcane blast."
spell.target = RPG_TARGET_OTHER
spell.duration = 0
spell.castRange = 20
spell.castTime = durSecond * 4
spell.recastTime = durSecond * 6
spell.harmful = True
spell.desc = "Damages a single target with a magical blast."
spell.skillname = "Evocation"
spell.addEffect("Arcane Blast")
spell.addClass("Wizard", 1)

effect = DBEffectProto(name="Arcane Storm")
effect.drainType = "health"
effect.drainTick = 20
effect.drainTickRate = durSecond * 6
effect.resist = RPG_RESIST_MAGICAL

spell = DBSpellProto()
spell.name = "Arcane Storm"
spell.spellbookPic = "SPELLICON_1_25"
spell.iconDst = "SPELLICON_1_25"
spell.particleTextureCasting = "staticring"
spell.particleCasting = "ChimneySmokeEmitter"
spell.sndCasting = "sfx/MagicSpell_CastingLoop1.ogg"
spell.particleTextureBegin = "staticring"
spell.particleBegin = "ChimneyFireEmitter"
spell.sndBegin = "sfx/DarkMagic_SpellImpact01.ogg"
spell.beginMsg = "$tgt is struck by an arcane storm."
spell.target = RPG_TARGET_OTHER
spell.duration = durMinute * 1
spell.castRange = 20
spell.castTime = durSecond * 4
spell.recastTime = durSecond * 6
spell.harmful = True
spell.aoeRange = 10
spell.desc = "Damages surrounding enemies by a magical storm."
spell.endMsg = "$tgt is no longer affected by the arcane storm."
spell.skillname = "Evocation"
spell.addEffect("Arcane Storm")
spell.addClass("Wizard", 1)

effect = DBEffectProto(name = "Summon Wolf Consort")
effect.summonPet = "Wolf Consort"

spell = DBSpellProto()
spell.name = "Summon Wolf Consort"
spell.spellbookPic = "SPELLICON_4_15"
spell.particleTextureCasting = "wingedc"
spell.particleCasting = "ChimneySmokeEmitter"
spell.sndCasting = "sfx/MagicSpell_CastingLoop1.ogg"
spell.particleTextureBegin = "wingedc"
spell.particleBegin = "ChimneyFireEmitter"
spell.sndBegin = "sfx/Skeleton_EmergeFromGround10.ogg"
spell.beginMsg = "$src has called upon a companion!"
spell.target = RPG_TARGET_SELF
spell.duration = 0
spell.castTime = durSecond * 10
spell.recastTime = durSecond * 5 * 60 # 5 minutes
spell.harmful = False
spell.desc = "Summons a wolf to help you."
spell.skillname = "Conjuration"
spell.addEffect("Summon Wolf Consort")
spell.addClass("Druid",1)

effect = DBEffectProto(name = "Bard Levitation")
effect.addStat(RPG_EFFECT_STAGE_GLOBAL,"flying",1.0)

spell = DBSpellProto()
spell.name = "Sapre's Airy Melody"
spell.spellbookPic = "SPELLICON_4_3"
spell.iconDst = "SPELLICON_4_3"
spell.particleTextureCasting = "wingedc"
spell.particleCasting = "ChimneySmokeEmitter"
spell.sndCasting = "sfx/MagicSpell_CastingLoop1.ogg"
spell.particleTextureBegin = "wingedc"
spell.particleBegin = "ChimneyFireEmitter"
spell.sndBegin = "sfx/Pickup_Speed03.ogg"
spell.target = RPG_TARGET_PARTY
spell.duration = durMinute * 15 #15 minutes
spell.castTime = durSecond * 2
spell.harmful = False
spell.beginMsg = "$tgt dances on the air!"
spell.endMsg = "$tgt becomes heavier."
spell.desc = "Allows your party to levitate."
spell.skillname = "Singing"
spell.addEffect("Bard Levitation")
spell.addClass("Bard",1)
