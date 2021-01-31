# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup archetype archetype
#  @ingroup world
#  @brief The archetype module provides mob RPG-class.  These RPG-classes define
#         how standard stats, such as strength and body, affect derived stats,
#         such as maxHealth and offense.
#  @{


from career import ClassProto


## @brief (Dictionary) Stores handles to a RPG-classes (value) by RPG-class
#         name (key).
CLASSES = {}


## @brief Archetype is the base for all RPG-classes.  It provides the basic
#         methods required, and may be overriden by derived classes.
#  @details This class should not directly instantiated.  Derived classes that will
#            be directly instantiated should set a "name" member attribute to
#            correspond to the ClassProto.name value in the database.
class Archetype:

    ## @brief Initialize class.
    #  @param self (Archetype) The object pointer.
    def __init__(self):

        ## @brief (Float) Experience modifier for a RPG-class.
        #  @remark TWS: Is this used or needed?
        self.xpMod = 1.0

        ## @var classProto
        #  @brief (ClassProto) ClassProto for the RPG-class.

        ## @var classSkills
        #  @brief (ClassSkill List) List containing skills available for the
        #         RPG-class.

        # Attempt to set the classProto and classSkills attributes.
        try:

            # Get the classProto based on the derived class' name attribute.
            self.classProto = ClassProto.byName(self.name)

            # Copy the skill list to avoid querying the database on sequential
            # reads.
            self.classSkills = list(self.classProto.skills)

        # Failure occured.  This probably occured because the derived class'
        # name attribute does not have a ClassProto.name in the word database.
        except:

            # No class proto was found.
            self.classProto = None

            # No skills.  Use an empty list because class skills may be
            # iterated over even if empty.
            ## Skills available for the RPG-class.
            self.classSkills = []


    ## @brief Gets the max health for a mob at a given level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Integer) The max health for a mob at a given level.
    def getMaxHealth(self, mob, level):
        return level*level+10


    ## @brief Gets the max mana for a mob at a given level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Integer) The max mana for a mob at a given level.
    def getMaxMana(self, mob, level):
       return 100


    ## @brief Gets the max stamina for a mob at a given level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Integer) The max stamina for a mob at a given level.
    def getMaxStamina(self, mob, level):
        return level*level


    ## @brief Gets the offense for a mob at a given level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Integer) The offense for a mob at a given level.
    def getOffense(self, mob, level):
        return level*level


    ## @brief Gets the defense for a mob at a given level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Integer) The defense for a mob at a given level.
    def getDefense(self, mob, level):
        return level*level


    ## Gets the experience modifier.
    #  @param self (Archetype) The object pointer.
    #  @return (Integer) The experience modifier.
    def getXPMod(self):
        return 1


    ## @brief Gets the primary/main hand attack speed for a mob at a given
    #         level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Integer) The tick counter for primary/main hand attack.
    def getPrimaryAttackRate(self, mob, level):
        # Combat ticks timers two times a second, reducing 3 from a counter.
        # Thus, with 16, the primary attacks once every 3 seconds.
        return 16


    ## @brief Gets the secondary/offhand attack speed for a mob at a given
    #         level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Integer) The tick counter for secondary/offhand attack.
    def getSecondaryAttackRate(self, mob, level):
        # Combat ticks timers two times a second, reducing 3 from a counter.
        # Thus, with 24, the primary attacks once every 4 seconds.
        return 24


    ## @brief Gets the critical chance modifier for a mob at a given level.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Float) Critical chance modifier.  Baseline is 1.0.
    #          Higher values increase the chance of a critical.
    def getCritical(self, mob, level):
        return 1.0


    ## @brief Gets the derived stats and values for an RPG-class.  This is
    #         called when a mob is created or changes levels.
    #  @param self (Archetype) The object pointer.
    #  @param mob (Mob) The mob whose stats are used in the calculation.
    #  @param level (Integer) The level for which the calculation occurs.
    #  @return (Dictionary) Dictionary containing derived stats and values.
    def getClassStats(self, mob, level):

        # Dictionary that will store all of the derived stats.
        stats = {}

        # Get the max health.
        health = self.getMaxHealth(mob, level)

        # Boost max health for non-Player mobs above level 20.
        if not mob.player and level > 20:
            health *= level/20
            # Uncomment the following to really raise the bar on tough mobs
            # over level 20
            #if mob.spawn.difficultyMod > 1.0:
            #    health += int(health * (mob.spawn.difficultyMod / 2.0))

        # Populate the dictionary with the derived stats.  Due to virtual
        # behavior, classes derived from Archtype will have their get methods
        # called instead.  This allows for more specific derived values to be
        # returned for each RPG-class.
        stats['maxHealth'] = health
        stats['maxMana'] = self.getMaxMana(mob, level)+6
        stats['maxStamina'] = self.getMaxStamina(mob, level)
        stats['offense'] = self.getOffense(mob, level)
        stats['defense'] = self.getDefense(mob, level)
        stats['primaryAttackRate'] = self.getPrimaryAttackRate(mob, level)
        stats['secondaryAttackRate'] = self.getSecondaryAttackRate(mob, level)
        stats['critical'] = self.getCritical(mob, level)

        # Return the dictionary containing the derived stats and values.
        return stats


## @brief Combatant serves as the base class for melee fighter RPG-classes.
class Combatant(Archetype):

    ## @brief Delegate initialization to parent class (Archetype).
    #  @param self (Combatant) The object pointer.
    def __init__(self):
        Archetype.__init__(self)


    def getMaxMana(self, mob, level):
        return 0


    def getCritical(self, mob, level):
        return 1.0


    def getMaxHealth(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))+mob.pre*5

    def getMaxStamina(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))+mob.pre*5


    def getOffense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        return int(level*level+10+(mob.str*s1)+(mob.dex*s2)+(mob.ref*s3))+mob.pre*10


    def getDefense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        s4 = level/100.0
        base = int(level*level+10+(mob.bdy*s1)+(mob.dex*s2)+(mob.ref*s3)+(mob.agi*s4))
        base+=mob.armor*4++mob.pre*4
        return base


## @brief Magi serves as the base class for spellcaster RPG-classes.
class Magi(Archetype):

    ## @brief Delegate initialization to parent class (Archetype).
    #  @param self (Magi) The object pointer.
    def __init__(self):
        Archetype.__init__(self)


    def getMaxStamina(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))/2+16+mob.pre*5


    def getMaxMana(self, mob, level):
        x = int((mob.mnd/10)*level)+int(mob.pre*level*.5)
        x += int(mob.mnd*5*float(level)/100.0)
        return x


    def getMaxHealth(self, mob, level):
        # NPCs get more health, to make them more of a challenge to fight.
        if not mob.player:
            return int(CLASSES['Warrior'].getMaxHealth(mob, level)*.75)
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))/4+16+mob.pre*2


    def getOffense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        offence = int(level*level+10+(mob.str*s1)+(mob.dex*s2)+(mob.ref*s3))
        return offence / 4 + mob.pre


    def getDefense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        s4 = level/100.0
        base = int(level*level+10+(mob.bdy*s1)+(mob.dex*s2)+(mob.ref*s3)+(mob.agi*s4))
        base+=mob.armor*4+mob.pre
        return base/5


    def getCritical(self, mob, level):
        return .5


## @brief Priest serves as the base class for healer and buffer RPG-classes.
class Priest(Archetype):

    ## @brief Delegate initialization to parent class (Archetype).
    #  @param self (Priest) The object pointer.
    def __init__(self):
        Archetype.__init__(self)


    def getMaxStamina(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))+16+mob.pre*5


    def getMaxMana(self, mob, level):
        x = int((mob.mys/10)*level)+int(mob.pre*level*.5)
        x += int(mob.mys*5*float(level)/100.0)
        return x


    def getMaxHealth(self, mob, level):
        # NPCs get more health, to make them more of a challenge to fight.
        if not mob.player:
            return int(CLASSES['Warrior'].getMaxHealth(mob, level)*.75)
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))/2


    def getOffense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        return int(level*level+10+(mob.str*s1)+(mob.dex*s2)+(mob.ref*s3))/2


    def getDefense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        s4 = level/100.0
        base = int(level*level+10+(mob.bdy*s1)+(mob.dex*s2)+(mob.ref*s3)+(mob.agi*s4))
        base+=mob.armor*4
        return base/2


    def getCritical(self, mob, level):
        return .8


## @brief Rogue serves as the base class for sneaky RPG-classes.
#  @todo TWS: Better description.
class Rogue(Archetype):

    ## @brief Delegate initialization to parent class (Archetype).
    #  @param self (Rogue) The object pointer.
    def __init__(self):
        Archetype.__init__(self)


    def getMaxStamina(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))+mob.pre*5


    def getMaxMana(self, mob, level):
        return 0


    def getMaxHealth(self, mob, level):
        # NPCs get more health, to make them more of a challenge to fight.
        if not mob.player:
            return int(CLASSES['Warrior'].getMaxHealth(mob, level)*.85)
        s1 = level/10.0
        s2 = level/25.0
        return int(((level*level+50+(mob.bdy*s1)+(mob.str*s2)))*.75)+mob.pre*5


    def getOffense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        base = int((level*level+10+(mob.str*s2)+(mob.dex*s1)+(mob.ref*s2))*1.3)
        return base + mob.pre * 6


    def getDefense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        s4 = level/100.0
        base = int((level*level+10+(mob.bdy*s2)+(mob.dex*s1)+(mob.ref*s2)+(mob.agi*s2))*.75)
        base+=mob.armor*3+mob.pre*3
        return base


    def getCritical(self, mob, level):
        return 1.2


## @brief The standard high health tank.
#  @details The Warrior is a master of heavy armor and equipment. They hit
#           their enemies hard and protect their allies in times of battle.
class Warrior(Combatant):

    ## @brief Initialize class.
    #  @param self (Warrior) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Warrior" ClassProto.
        self.name = "Warrior"
        Combatant.__init__(self)

    def getXPMod(self):
        return .9


    def getCritical(self, mob, level):
        return 1.1


    def getDefense(self, mob, level):
        return int(Combatant.getDefense(self, mob, level)*1.20)


    def getMaxHealth(self, mob, level):
        return int(Combatant.getMaxHealth(self, mob, level)*1.3)


## @brief Melee-hybrid who is a master of the natural realm.
#  @details Rangers are masters of the natural realm. They use speed and
#           camouflage to blend into  their surroundings while attacking
#           their foes with great might.
class Ranger(Combatant):

    ## @brief Initialize class.
    #  @param self (Ranger) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Ranger" ClassProto.
        self.name = "Ranger"
        Combatant.__init__(self)


    def getXPMod(self):
        return 1


    def getMaxMana(self, mob, level):
        x = int((mob.mnd/10)*level)+int(mob.pre*level*.5)
        x += int(mob.mnd*5*float(level)/100.0)
        return x


    def getMaxHealth(self, mob, level):
        return int(Combatant.getMaxHealth(self, mob, level)*1)


## @brief Melee-hybrid holy warrior, uses heals and stuns.
#  @details The paladin is a holy warrior who excels in outlasting the opponent
#           with an array of stuns, heals, and divine favors.
class Paladin(Combatant):

    ## @brief Initialize class.
    #  @param self (Paladin) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Paladin" ClassProto.
        self.name = "Paladin"
        Combatant.__init__(self)


    def getXPMod(self):
        return 1.05

    def getMaxMana(self, mob, level):
        x = int((mob.wis/10)*level)+int(mob.pre*level*.5)
        x += int(mob.wis*5*float(level)/100.0)
        return x


    def getDefense(self, mob, level):
        return int(Combatant.getDefense(self, mob, level)*1.10)


    def getMaxHealth(self, mob, level):
        return int(Combatant.getMaxHealth(self, mob, level)*1.2)


## @brief Melee-hybrid corrupt warrior, uses undead pet and chaos.
## @details Doom Knights are among the most evil of all classes. They are
#           corrupt warriors who thrive on chaos and mastering the undead.
class DoomKnight(Combatant):

    ## @brief Initialize class.
    #  @param self (DoomKnight) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Doom Knight"  ClassProto.
        self.name = "Doom Knight"
        Combatant.__init__(self)


    def getMaxMana(self, mob, level):
        x = int((mob.mnd/10)*level)+int(mob.pre*level*.5)
        x += int(mob.mnd*5.0*float(level)/100.0)
        return x


    def getXPMod(self):
        return .9


## @brief Similar to the Warrior, but has higher offense at the cost of health
#         and defense.
#  @details Barbarians are masters of physical combat. They use their brute
#           strength to overcome their foes. Their rage is nearly palpable
#           and they never back down from a fight.
class Barbarian(Combatant):

    ## @brief Initialize class.
    #  @param self (Barbarian) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Barbarian" ClassProto.
        self.name = "Barbarian"
        Combatant.__init__(self)


    def getXPMod(self):
        return 1.05


    def getOffense(self, mob, level):
        return int(Combatant.getOffense(self, mob, level)*1.2)


    def getDefense(self, mob, level):
        return int(Combatant.getDefense(self, mob, level)*.9)


    def getMaxHealth(self, mob, level):
        return int(Combatant.getMaxHealth(self, mob, level)*1.1)


## @brief Strong offense and defense fist-fighter.
## @details Monks are graceful and deadly. Their inner calm forms the basis of
#           their character and allows them great focus in battle.
class Monk(Combatant):

    ## @brief Initialize class.
    #  @param self (Monk) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Monk" ClassProto.
        self.name = "Monk"
        Combatant.__init__(self)


    def getXPMod(self):
        return 1.1


    def getMaxHealth(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))+mob.pre*7


    def getOffense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        base = int((level*level+10+(mob.str*s1)+(mob.dex*s2)+(mob.ref*s3))*1.25)
        return base + mob.pre * 6


    def getDefense(self, mob, level):
        s0 = level/5.0
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        s4 = level/100.0
        base = int(level*level+10+(mob.bdy*s1)+(mob.dex*s2)+(mob.ref*s1)+(mob.agi*s0))
        base+=mob.armor*2+mob.pre*4
        return base


## @brief Backstab, poison, melee-offense class.
#  @details Assassins are very sneaky. They lurk in the shadows and poison
#           their enemies with the tip of their blade. They enjoy inflicting
#           death upon others and watching them breathe their final breath.
class Assassin(Rogue):

    ## @brief Initialize class.
    #  @param self (Assassin) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Assassin" ClassProto.
        self.name = "Assassin"
        Rogue.__init__(self)


    def getXPMod(self):
        return 1.1


    def getCritical(self, mob, level):
        return 1.4

## @brief Sneaky and cunning melee-offense class.
#  @details Thieves are clever and sneaky. They are quick to poison their
#           enemies, steal their valuables, and disappear without a trace.
class Thief(Rogue):

    ## @brief Initialize class.
    #  @param self (Thief) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Thief" ClassProto.
        self.name = "Thief"
        Rogue.__init__(self)


    def getXPMod(self):
        return 1


## @brief Song-caster providing buffs, crowd control, and minor magical damage.
#  @details Bards are musicians. They use their musical strengths to confuse
#           and distract their enemies or even lull them to sleep.
class Bard(Rogue):

    ## @brief Initialize class.
    #  @param self (Bard) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Bard" ClassProto.
        self.name = "Bard"
        Rogue.__init__(self)


    def getXPMod(self):
        return 1


    def getMaxStamina(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))+mob.pre*5


    def getCritical(self, mob, level):
        return 1.0


    def getMaxMana(self, mob, level):
        x = int((mob.mnd/10)*level)+int(mob.pre*level*.5)
        x += int(mob.mnd*5*float(level)/100.0)
        return x


    def getMaxHealth(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        return int((level*level+50+(mob.bdy*s1)+(mob.str*s2)))+mob.pre*6


    def getOffense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        base = int(level*level+10+(mob.str*s1)+(mob.dex*s2)+(mob.ref*s3))
        return base + mob.pre * 4


    def getDefense(self, mob, level):
        s1 = level/10.0
        s2 = level/25.0
        s3 = level/50.0
        s4 = level/100.0
        base = int(level*level+10+(mob.bdy*s1)+(mob.dex*s2)+(mob.ref*s3)+(mob.agi*s4))
        base+=mob.armor*4+mob.pre*4
        return base


## @brief Best direct damage caster.
#  @details The wizard is a master of spellcasting who is dedicated to studying
#           their craft.
class Wizard(Magi):

    ## @brief Initialize class.
    #  @param self (Wizard) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Wizard" ClassProto.
        self.name = "Wizard"
        Magi.__init__(self)


    def getXPMod(self):
        return 1.05


## @brief Crowd control, haste, charm, ports.
#  @details Revealers are powerful spellcasters who manipulate the very Threads
#           of Creation and Chaos which they use to transport themselves around
#           the World of Mirth. Those who are not driven mad by their glimpses
#           into the Blight, learn to summon the atrocities that dwell there.
class Revealer(Magi):

    ## @brief Initialize class.
    #  @param self (Revealer) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Revealer" ClassProto.
        self.name = "Revealer"
        Magi.__init__(self)


    def getXPMod(self):
        return 1.05


## @brief Master of the undead, leach spells, damage over time, and pets.
#  @details Necromancers can summon vast legions of undead to respond to their
#           call and bow before them.
class Necromancer(Magi):

    ## @brief Initialize class.
    #  @param self (Necromancer) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Necromancer" ClassProto.
        self.name = "Necromancer"
        Magi.__init__(self)


    def getXPMod(self):
        return 1.1


## @brief Mostly healing powers, but has some stuns and undead nukes.
#  @details Clerics are masters of the art of healing from mending simple
#           wounds to bringing back fallen comrades from death. They summon the
#           spiritual realm to bring strength and courage to their friends and
#           cast down wrath and fury upon their enemies.
class Cleric(Priest):

    ## @brief Initialize class.
    #  @param self (Cleric) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Cleric" ClassProto.
        self.name = "Cleric"
        Priest.__init__(self)


    def getXPMod(self):
        return 1


    def getMaxMana(self, mob, level):
        x = int((mob.wis/10)*level)+int(mob.pre*level*.5)
        x += int(mob.wis*5*float(level)/100.0)
        return x


## @brief Wizard-like class, with lower nukes, but debuffs, and pets.
#  @details Tempests summon the forces present within the elements.
class Tempest(Priest):

    ## @brief Initialize class.
    #  @param self (Tempest) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Tempest" ClassProto.
        self.name = "Tempest"
        Priest.__init__(self)


    def getXPMod(self):
        return 1.05


## @brief Buffs, debuffs, and pets.
#  @details The Shaman calls upon the spirits of the natural world to aid them
#           and uses the very forces of nature to strike down enemies.
class Shaman(Priest):

    ## @brief Initialize class.
    #  @param self (Shaman) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Shaman" ClassProto.
        self.name = "Shaman"
        Priest.__init__(self)


    def getXPMod(self):
        return 1.05


## @brief Buffs, ports, debuffs, with a nature theme.
#  @details Druids are most aware of the beauty and forces present within the
#           natural world. They respect this knowledge and guard it closely.
#           They tread lightly upon the land, barely leaving a mark where their
#           footsteps touched.
class Druid(Priest):

    ## @brief Initialize class.
    #  @param self (Druid) The object pointer.
    def __init__(self):
        ## @brief (String) Set an association to the "Druid" ClassProto.
        self.name = "Druid"
        Priest.__init__(self)


    def getMaxMana(self, mob, level):
        x = int((mob.wis/10)*level)+int(mob.pre*level*.5)
        x += int(mob.wis*5*float(level)/100.0)
        return x


    def getXPMod(self):
        return 1
        
class Harvest(Combatant): 

    ## @brief Initialize class. 
    #  @param self (Warrior) The object pointer. 
    def __init__(self): 
        ## @brief (String) Set an association to the "Warrior" ClassProto. 
        self.name = "Harvest" 
        Combatant.__init__(self) 
        
    def getDefense(self, mob, level): 
        return 0 
        
    def getMaxHealth(self, mob, level): 
        x = level * 5.0 
        return x


## @brief Initialize dictionary with all RPG-classes.
#  @details This method sets up a dictionary used for a GetClass invocations.
#           This method may be invoked during World Startup, from an Immortal's
#           Recompile command, or by the first time the GetCass method is
#           invoked.
def InitClassSkills():
    
    global CLASSES

    # Clear the previous dictionary.
    CLASSES = {}

    # Create and add  RPG classes to dictionary.
    CLASSES['Warrior'] = Warrior()
    CLASSES['Ranger'] = Ranger()
    CLASSES['Paladin'] = Paladin()
    CLASSES['Doom Knight'] = DoomKnight()
    CLASSES['Barbarian'] = Barbarian()
    CLASSES['Monk'] = Monk()
    CLASSES['Thief'] = Thief()
    CLASSES['Assassin'] = Assassin()
    CLASSES['Bard'] = Bard()
    CLASSES['Wizard'] = Wizard()
    CLASSES['Revealer'] = Revealer()
    CLASSES['Necromancer'] = Necromancer()
    CLASSES['Cleric'] = Cleric()
    CLASSES['Tempest'] = Tempest()
    CLASSES['Shaman'] = Shaman()
    CLASSES['Druid'] = Druid()
    CLASSES['Harvest'] = Harvest()

    # For each RPG-class, copy the ClassProto's skill into RPG-class.
    for cl in CLASSES.itervalues():
        
        # If the RPG-class has an associated ClassProto, then copy the
        # ClassProto's skill into the RPG-class.  This reassignment prevents
        # having to query the database each time the skill list is checked.
        if cl.classProto:
            cl.classSkills = cl.classProto.skills


## @brief Returns an RPG-class.
#  @param classname (String) Name of the RPG-class.
#  @return (Class derived from Archetype) RPG-class if named class is found.
#          Otherwise, Warrior is returned.
#  @todo TWS: Why check for class initialization each time? When does it become
#             un-initialized?  Should it be "protected"?  Function remapping
#             could be used to optimize this.
def GetClass(classname):

    # If the classes have not been initialized, then initialize them.
    if not len(CLASSES):
        InitClassSkills()

    # Get and return the RPG-class by name.
    try:
        return CLASSES[classname]
    
    # An RPG-class coud not be found for the supplied classname, return the
    # Warrior RPG-class instead.
    except KeyError:
        print "WARNING: Unknown class:", classname
        return CLASSES["Warrior"]


## @} # End archetype group.
