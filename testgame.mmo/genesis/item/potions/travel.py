from genesis.dbdict import DBItemProto
from mud.world.defines import *

from genesis.dbdict import DBSpellProto,DBEffectProto
from mud.world.defines import *


def CreatePotion(name,effect,desc):
    
    spell = DBSpellProto(name = name)
    spell.target = RPG_TARGET_SELF
    spell.duration = 0
    spell.castTime = 0
    spell.recastTime = 0
    spell.harmful = False
    spell.addEffect(effect)
    
    item = DBItemProto(name = name)
    item.addSpell(name,RPG_ITEM_TRIGGER_USE,1)
    item.bitmap = "STUFF/3"
        
    item.useMax = 1
    item.desc = desc
    item.stackMax = 20
    item.stackDefault = 1
 