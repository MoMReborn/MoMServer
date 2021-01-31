
from genesis.dbdict import DBDict,DBClassProto

def CombineSkills(proto,exclude=[]):
    caster = proto.archetype == 'Magi' or proto.archetype == 'Priest'
    if DBDict.registry.has_key('ClassSkill'):
        for cs in DBDict.registry['ClassSkill']:
            if cs.skillname in exclude:
                continue
            if proto.name in cs.type: 
                proto.addClassSkill(cs,True) #force replace is class specific
            elif proto.archetype in cs.type or (caster and 'Caster' in cs.type):
                proto.addClassSkill(cs)
            elif 'General' in cs.type:
                proto.addClassSkill(cs)
    
proto = DBClassProto(name = "Warrior", archetype = "Combatant")
CombineSkills(proto)

proto = DBClassProto(name = "Doom Knight", archetype = "Combatant")
CombineSkills(proto)

exclude = ["Heavy Armor"]
proto = DBClassProto(name = "Monk", archetype = "Combatant")
CombineSkills(proto,exclude)

proto = DBClassProto(name = "Paladin", archetype = "Combatant")
CombineSkills(proto)

proto = DBClassProto(name = "Barbarian", archetype = "Combatant")
CombineSkills(proto)

proto = DBClassProto(name = "Ranger", archetype = "Combatant")
CombineSkills(proto)

proto = DBClassProto(name = "Necromancer", archetype = "Magi")
CombineSkills(proto)

proto = DBClassProto(name = "Wizard", archetype = "Magi")
CombineSkills(proto)

proto = DBClassProto(name = "Revealer", archetype = "Magi")
CombineSkills(proto)

proto = DBClassProto(name = "Cleric", archetype = "Priest")
CombineSkills(proto)

proto = DBClassProto(name = "Tempest", archetype = "Priest")
CombineSkills(proto)

proto = DBClassProto(name = "Shaman", archetype = "Priest")
CombineSkills(proto)

proto = DBClassProto(name = "Druid", archetype = "Priest")
CombineSkills(proto)

proto = DBClassProto(name = "Bard", archetype = "Rogue")
CombineSkills(proto)

proto = DBClassProto(name = "Thief", archetype = "Rogue")
CombineSkills(proto)

proto = DBClassProto(name = "Assassin", archetype = "Rogue")
CombineSkills(proto)













