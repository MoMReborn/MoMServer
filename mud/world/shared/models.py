# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details




def GetModelInfo(race,sex,look):
    sizes = {}
    sizes['Drakken']=1.15
    sizes['Halfling']=.6
    sizes['Human']=1.0
    sizes['Titan']=1.35
    sizes['Dwarf']=.85
    sizes['Elf']=1.0
    sizes['Dark Elf']=.7
    sizes['Gnome']=.7
    sizes['Orc']=1.05
    sizes['Goblin']=.7
    sizes['Ogre']=1.1
    sizes['Troll']=1.4
    
    models = {}
    models['Dark Elf']=("elf_female/elf_female_%s","elf_male/elf_male_%s")
    models['Elf']=("elf_female/elf_female_%s","elf_male/elf_male_%s")
    models['Human']=("human_female/human_female_%s","human_male/human_male_%s")
    models['Titan']=("titan_female/titan_female_%s","titan_male/titan_male_%s")
    models['Gnome']=("gnome_female/gnome_female_%s","gnome_male/gnome_male_%s")
    models['Dwarf']=("dwarf_female/dwarf_female_%s","dwarf_male/dwarf_male_%s")
    models['Halfling']=("halfling_female/halfling_female_%s","halfling_male/halfling_male_%s")
    models['Orc']=("orc_female/orc_female_%s","orc_male/orc_male_%s")
    models['Goblin']=("goblin_female/goblin_female_%s","goblin_male/goblin_male_%s")
    models['Ogre']=("ogre_female/ogre_female_%s","ogre_male/ogre_male_%s")
    models['Troll']=("troll_female/troll_female_%s","troll_male/troll_male_%s")
    models['Drakken']=("drakken_female/drakken_female_%s","drakken_male/drakken_male_%s")

    if sex == "Female":
        if look==0:
            model = models[race][0]%"thin"
        elif look==1:
            model = models[race][0]%"fit"
        elif look==2:
            model = models[race][0]%"heavy"
    else:
        if look==0:
            model = models[race][1]%"thin"
        elif look==1:
            model = models[race][1]%"fit"
        elif look==2:
            model = models[race][1]%"heavy"
        
        
    size = sizes[race]
    
    ftextures = {}
    ftextures['Dark Elf']=("elf_female_head","elf_female_arms","elf_female_legs","elf_female_body","elf_female_feet","elf_female_hands","")
    ftextures['Elf']=("elf_female_head","elf_female_arms","elf_female_legs","elf_female_body","elf_female_feet","elf_female_hands","")
    ftextures['Human']=("human_female_head","human_female_arms","human_female_legs","human_female_body","human_female_feet","human_female_hands","")
    ftextures['Titan']=("titan_female_head","titan_female_arms","titan_female_legs","titan_female_body","","titan_female_hands","titan_female_special")
    ftextures['Gnome']=("gnome_female_head","gnome_female_arms","gnome_female_legs","gnome_female_body","gnome_female_feet","gnome_female_hands","")
    ftextures['Dwarf']=("dwarf_female_head","dwarf_female_arms","dwarf_female_legs","dwarf_female_body","dwarf_female_feet","dwarf_female_hands","")
    ftextures['Halfling']=("halfling_female_head","halfling_female_arms","halfling_female_legs","halfling_female_body","halfling_female_feet","halfling_female_hands","")
    ftextures['Orc']=("orc_female_head","orc_female_arms","orc_female_legs","orc_female_body","orc_female_feet","orc_female_hands","")
    ftextures['Goblin']=("goblin_female_head","goblin_female_arms","goblin_female_legs","goblin_female_body","goblin_female_feet","goblin_female_hands","")
    ftextures['Ogre']=("ogre_female_head","ogre_female_arms","ogre_female_legs","ogre_female_body","ogre_female_feet","ogre_female_hands","")
    ftextures['Troll']=("troll_female_head","troll_female_arms","troll_female_legs","troll_female_body","troll_female_feet","troll_female_hands","")
    ftextures['Drakken']=("drakken_female_head","drakken_female_arms","drakken_female_legs","drakken_female_body","drakken_female_feet","drakken_female_hands","")
    
    mtextures = {}
    mtextures['Dark Elf']=("elf_male_head","elf_male_arms","elf_male_legs","elf_male_body","elf_male_feet","elf_male_hands","")
    mtextures['Elf']=("elf_male_head","elf_male_arms","elf_male_legs","elf_male_body","elf_male_feet","elf_male_hands","")
    mtextures['Human']=("human_male_head","human_male_arms","human_male_legs","human_male_body","human_male_feet","human_male_hands","")
    mtextures['Titan']=("titan_male_head","titan_male_arms","titan_male_legs","titan_male_body","","titan_male_hands","titan_male_special")
    mtextures['Gnome']=("gnome_male_head","gnome_male_arms","gnome_male_legs","gnome_male_body","gnome_male_feet","gnome_male_hands","")
    mtextures['Dwarf']=("dwarf_male_head","dwarf_male_arms","dwarf_male_legs","dwarf_male_body","dwarf_male_feet","dwarf_male_hands","")
    mtextures['Halfling']=("halfling_male_head","halfling_male_arms","halfling_male_legs","halfling_male_body","halfling_male_feet","halfling_male_hands","")
    mtextures['Orc']=("orc_male_head","orc_male_arms","orc_male_legs","orc_male_body","orc_male_feet","orc_male_hands","")
    mtextures['Goblin']=("goblin_male_head","goblin_male_arms","goblin_male_legs","goblin_male_body","goblin_male_feet","goblin_male_hands","")
    mtextures['Ogre']=("ogre_male_head","ogre_male_arms","ogre_male_legs","ogre_male_body","ogre_male_feet","ogre_male_hands","")
    mtextures['Troll']=("troll_male_head","troll_male_arms","troll_male_legs","troll_male_body","troll_male_feet","troll_male_hands","")
    mtextures['Drakken']=("drakken_male_head","drakken_male_arms","drakken_male_legs","drakken_male_body","drakken_male_feet","drakken_male_hands","")
    
    textures = ftextures
    if sex == "Male":
        textures = mtextures
        
    tex = textures[race]
    
    animations = {}
    #animations['Elf']=("humanoidFemale","elfmale")
    #animations['Dark Elf']=("humanoidFemale","elfmale")
    #animations['Human']=("humanoidFemale","humanoid")
    #animations['Titan']=("titanmale","titanmale")
    #animations['Gnome']=("halflingFemale","humanoidshort")
    #animations['Dwarf']=("humanoidshort","humanoidshort")
    #animations['Halfling']=("halflingFemale","humanoidshort")
    #animations['Orc']=("halflingFemale","humanoidshort")
    #animations['Goblin']=("halflingFemale","humanoidshort")
    #animations['Ogre']=("humanoid","humanoid")
    #animations['Troll']=("trollmale","trollmale")
    #animations['Drakken']=("drakkenfemale","drakken")
    animations['Elf']=("","")
    animations['Dark Elf']=("","")
    animations['Human']=("","")
    animations['Titan']=("","")
    animations['Gnome']=("","")
    animations['Dwarf']=("","")
    animations['Halfling']=("","")
    animations['Orc']=("","")
    animations['Goblin']=("","")
    animations['Ogre']=("","")
    animations['Troll']=("","")
    animations['Drakken']=("","")
    
    animation = animations[race][1]
    if sex == "Female":
        animation = animations[race][0]
    
    
    return size,model,tex,animation

# female mount point back to account for bun

HMOUNT = {}
#good
HMOUNT[('Drakken','Male',0)]=1.4
HMOUNT[('Drakken','Male',1)]=1.4
HMOUNT[('Drakken','Male',2)]=1.45
HMOUNT[('Drakken','Female',0)]=1.4
HMOUNT[('Drakken','Female',1)]=1.4
HMOUNT[('Drakken','Female',2)]=1.45

#good
HMOUNT[('Halfling','Male',0)]=1.25
HMOUNT[('Halfling','Male',1)]=1.25
HMOUNT[('Halfling','Male',2)]=1.3
HMOUNT[('Halfling','Female',0)]=1.15
HMOUNT[('Halfling','Female',1)]=1.15
HMOUNT[('Halfling','Female',2)]=1.2

HMOUNT[('Human','Male',0)]=1.0
HMOUNT[('Human','Male',1)]=1.1
HMOUNT[('Human','Male',2)]=1.1
HMOUNT[('Human','Female',0)]=1.1 #darn bun
HMOUNT[('Human','Female',1)]=1.1
HMOUNT[('Human','Female',2)]=1.1

#good
HMOUNT[('Titan','Male',0)]=1.1
HMOUNT[('Titan','Male',1)]=1.1
HMOUNT[('Titan','Male',2)]=1.1
HMOUNT[('Titan','Female',0)]=1.0
HMOUNT[('Titan','Female',1)]=1.0
HMOUNT[('Titan','Female',2)]=1.0

#good
HMOUNT[('Dwarf','Male',0)]=1.2
HMOUNT[('Dwarf','Male',1)]=1.3
HMOUNT[('Dwarf','Male',2)]=1.3
HMOUNT[('Dwarf','Female',0)]=1.2
HMOUNT[('Dwarf','Female',1)]=1.3
HMOUNT[('Dwarf','Female',2)]=1.3

#good
HMOUNT[('Elf','Male',0)]=1.0
HMOUNT[('Elf','Male',1)]=1.0
HMOUNT[('Elf','Male',2)]=1.0
HMOUNT[('Elf','Female',0)]=.95
HMOUNT[('Elf','Female',1)]=1.0
HMOUNT[('Elf','Female',2)]=1.0

#good
HMOUNT[('Gnome','Male',0)]=1.35
HMOUNT[('Gnome','Male',1)]=1.4
HMOUNT[('Gnome','Male',2)]=1.4
HMOUNT[('Gnome','Female',0)]=1.15
HMOUNT[('Gnome','Female',1)]=1.2
HMOUNT[('Gnome','Female',2)]=1.2

#good
HMOUNT[('Dark Elf','Male',0)]=1.0
HMOUNT[('Dark Elf','Male',1)]=1.0
HMOUNT[('Dark Elf','Male',2)]=1.0
HMOUNT[('Dark Elf','Female',0)]=.95
HMOUNT[('Dark Elf','Female',1)]=1.0
HMOUNT[('Dark Elf','Female',2)]=1.0

HMOUNT[('Orc','Male',0)]=1.0
HMOUNT[('Orc','Male',1)]=1.0
HMOUNT[('Orc','Male',2)]=1.0
HMOUNT[('Orc','Female',0)]=1.0
HMOUNT[('Orc','Female',1)]=1.0
HMOUNT[('Orc','Female',2)]=1.0

#good
HMOUNT[('Goblin','Male',0)]=1.0
HMOUNT[('Goblin','Male',1)]=1.0
HMOUNT[('Goblin','Male',2)]=1.0
HMOUNT[('Goblin','Female',0)]=.95
HMOUNT[('Goblin','Female',1)]=1.0
HMOUNT[('Goblin','Female',2)]=1.0

#good
HMOUNT[('Ogre','Male',0)]=1.1
HMOUNT[('Ogre','Male',1)]=1.15
HMOUNT[('Ogre','Male',2)]=1.25
HMOUNT[('Ogre','Female',0)]=1.1
HMOUNT[('Ogre','Female',1)]=1.15
HMOUNT[('Ogre','Female',2)]=1.25

#good
HMOUNT[('Troll','Male',0)]=1.1
HMOUNT[('Troll','Male',1)]=1.25
HMOUNT[('Troll','Male',2)]=1.35
HMOUNT[('Troll','Female',0)]=1.1
HMOUNT[('Troll','Female',1)]=1.25
HMOUNT[('Troll','Female',2)]=1.3

