
from mud.world.race import CreatePlayableRace

# --- HUMAN ---

r, g = CreatePlayableRace("Human")

#head mount scales
g.hmount_fit_male = 1.1
g.hmount_heavy_male = 1.1
g.hmount_thin_male = 1.1

g.hmount_fit_female = 1.1
g.hmount_heavy_female = 1.1
g.hmount_thin_female = 1.1

# START: DSQ based animation
#g.model_fit_male = "human_male/human_male_fit_dsqanim"
#g.model_heavy_male = "human_male/human_male_heavy_dsqanim"
#g.model_thin_male = "human_male/human_male_thin_dsqanim"
    
#g.model_fit_female = "human_female/human_female_fit_dsqanim"
#g.model_heavy_female = "human_female/human_female_heavy_dsqanim"
#g.model_thin_female = "human_female/human_female_thin_dsqanim"

#g.animation_male = "humanoid"
#g.animation_female = "humanoidfemale"
# END: DSQ based animation

#Avatar Pack Examples
#Available from:
#http://www.mmoworkshop.com/trac/mom/wiki/Store

"""

# --- ELF ---

r, g = CreatePlayableRace("Elf")

#head mount scales
g.hmount_fit_male = 1.0
g.hmount_heavy_male = 1.0
g.hmount_thin_male = 1.0

g.hmount_fit_female = 1.0
g.hmount_heavy_female = 1.0
g.hmount_thin_female = .95

# --- HALFLING ---

r, g = CreatePlayableRace("Halfling")

#head mount scales
g.hmount_fit_male = 1.25
g.hmount_heavy_male = 1.3
g.hmount_thin_male = 1.25

g.hmount_fit_female = 1.15
g.hmount_heavy_female = 1.2
g.hmount_thin_female = 1.15

# --- DWARF ---

r, g = CreatePlayableRace("Dwarf")

#head mount scales
g.hmount_fit_male = 1.3
g.hmount_heavy_male = 1.3
g.hmount_thin_male = 1.2

g.hmount_fit_female = 1.3
g.hmount_heavy_female = 1.3
g.hmount_thin_female = 1.2

# --- GNOME ---

r, g = CreatePlayableRace("Gnome")

#head mount scales
g.hmount_fit_male = 1.4
g.hmount_heavy_male = 1.4
g.hmount_thin_male = 1.35

g.hmount_fit_female = 1.2
g.hmount_heavy_female = 1.2
g.hmount_thin_female = 1.15

# --- DRAKKEN ---

r, g = CreatePlayableRace("Drakken")

#head mount scales
g.hmount_fit_male = 1.4
g.hmount_heavy_male = 1.45
g.hmount_thin_male = 1.4

g.hmount_fit_female = 1.4
g.hmount_heavy_female = 1.45
g.hmount_thin_female = 1.4

# --- TITAN ---

r, g = CreatePlayableRace("Titan")

g.texture_special_female = "titan_female_special"
g.texture_special_male = "titan_male_special"

#head mount scales
g.hmount_fit_male = 1.1
g.hmount_heavy_male = 1.1
g.hmount_thin_male = 1.1

g.hmount_fit_female = 1.0
g.hmount_heavy_female = 1.0
g.hmount_thin_female = 1.0

# --- ORC ---

r, g = CreatePlayableRace("Orc")

# --- GOBLIN ---

r, g = CreatePlayableRace("Goblin")

# --- TROLL ---

r, g = CreatePlayableRace("Troll")

#head mount scales
g.hmount_fit_male = 1.25
g.hmount_heavy_male = 1.35
g.hmount_thin_male = 1.1

g.hmount_fit_female = 1.25
g.hmount_heavy_female = 1.3
g.hmount_thin_female = 1.1

# --- OGRE ---

r, g = CreatePlayableRace("Ogre")

#head mount scales
g.hmount_fit_male = 1.15
g.hmount_heavy_male = 1.25
g.hmount_thin_male = 1.1

g.hmount_fit_female = 1.15
g.hmount_heavy_female = 1.25
g.hmount_thin_female = 1.1

"""
