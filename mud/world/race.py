# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from defines import *
from mud.common.persistent import Persistent
from sqlobject import *

class RaceGraphic(Persistent):
    name = StringCol(default = "", alternateID = True)
    
    model_fit_male = StringCol(default = "")
    model_heavy_male = StringCol(default = "")
    model_thin_male = StringCol(default = "")
    
    model_fit_female = StringCol(default = "")
    model_heavy_female = StringCol(default = "")
    model_thin_female = StringCol(default = "")
    
    animation_male = StringCol(default = "")
    animation_female = StringCol(default = "")
    
    texture_head_male = StringCol(default = "")
    texture_body_male = StringCol(default = "")
    texture_arms_male = StringCol(default = "")
    texture_legs_male = StringCol(default = "")
    texture_hands_male = StringCol(default = "")
    texture_feet_male = StringCol(default = "")
    texture_special_male = StringCol(default = "")

    texture_head_female = StringCol(default = "")
    texture_body_female = StringCol(default = "")
    texture_arms_female = StringCol(default = "")
    texture_legs_female = StringCol(default = "")
    texture_hands_female = StringCol(default = "")
    texture_feet_female = StringCol(default = "")
    texture_special_female = StringCol(default = "")
    
    size_male = FloatCol(default = 1.0)
    size_female = FloatCol(default = 1.0)
    
    hmount_fit_male = FloatCol(default = 1.0)
    hmount_heavy_male = FloatCol(default = 1.0)
    hmount_thin_male = FloatCol(default = 1.0)

    hmount_fit_female = FloatCol(default = 1.0)
    hmount_heavy_female = FloatCol(default = 1.0)
    hmount_thin_female = FloatCol(default = 1.0)

class Race(Persistent):
    
    name = StringCol(default = "", alternateID = True)
    playable = BoolCol(default=False)
    xpMod = FloatCol(default = 1.0)
    regenHealth = FloatCol(default = 1.0)
    regenMana = FloatCol(default = 2.0)
    regenStamina = FloatCol(default = 1.0)
    consumeWater = FloatCol(default = 1.0)
    consumeFood = FloatCol(default = 1.0)
    move = FloatCol(default = 1.0)
    swim = FloatCol(default = 1.0)
    realm = IntCol(default = RPG_REALM_MONSTER)
    seeInvisible = FloatCol(default = 0.0)
    
    def getXPMod(self):
        return self.xpMod
    
class DummyRace:
    def __init__(self, name):
        self.name = name
        self.xpMod = 1.0
        self.regenHealth = 1.0
        self.regenMana = 2.0
        self.regenStamina = 1.0
        self.consumeWater = 1.0
        self.consumeFood = 1.0
        self.move = 1.0
        self.swim = 1.0
        self.realm = 0
        self.seeInvisible = 0.0
        
    def getXPMod(self):
        return 1.0
       
        
def CreatePlayableRace(name):
    
    r = Race(name = name)
    r.playable = True
    
    g = RaceGraphic(name = name)
    
    lower = name.lower()
        
    g.model_fit_male = "%s_male/%s_male_fit"%(lower,lower)
    g.model_heavy_male = "%s_male/%s_male_heavy"%(lower,lower)
    g.model_thin_male = "%s_male/%s_male_thin"%(lower,lower)
    
    g.model_fit_female = "%s_female/%s_female_fit"%(lower,lower)
    g.model_heavy_female = "%s_female/%s_female_heavy"%(lower,lower)
    g.model_thin_female = "%s_female/%s_female_thin"%(lower,lower)
    
    g.animation_male = ""
    g.animation_female = ""
    
    g.texture_head_male = "%s_male_head"%lower
    g.texture_body_male = "%s_male_body"%lower
    g.texture_arms_male = "%s_male_arms"%lower
    g.texture_legs_male = "%s_male_legs"%lower
    g.texture_hands_male = "%s_male_hands"%lower
    g.texture_feet_male = "%s_male_feet"%lower
    g.texture_special_male = ""
    
    g.texture_head_female = "%s_female_head"%lower
    g.texture_body_female = "%s_female_body"%lower
    g.texture_arms_female = "%s_female_arms"%lower
    g.texture_legs_female = "%s_female_legs"%lower
    g.texture_hands_female = "%s_female_hands"%lower
    g.texture_feet_female = "%s_female_feet"%lower
    g.texture_special_female = ""
    
    g.size_male = 1.0
    g.size_female = 1.0
    
    return r, g
    

    


# ---------------------------------------

INITIALIZED = False
RACES = {}
RACE_GRAPHICS = []
RACE_GRAPHICS_INITIALIZED = False
# ---------------------------------------

def GetRace(racename):
    global INITIALIZED
    
    if not INITIALIZED:
        INITIALIZED = True
        for race in Race.select():
            RACES[race.name] = race
            
    if not RACES.has_key(racename):
        race = DummyRace(racename)
        RACES[racename] = race
    
    return RACES[racename]

def GetRaceGraphics():
    from mud.world.shared.worlddata import RaceGraphicInfo
    global RACE_GRAPHICS_INITIALIZED
    if not RACE_GRAPHICS_INITIALIZED:
        RACE_GRAPHICS_INITIALIZED = True
        for rg in RaceGraphic.select():
            RACE_GRAPHICS.append(RaceGraphicInfo(rg))
            
    return RACE_GRAPHICS
            
        
