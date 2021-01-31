#Content definitions for Starter MMO

COMMON_SPELLSCRIPTS=[]

COMMON_TEXTURES = ["./starter.mmo/data/shapes/player/splash.png","./starter.mmo/data/shapes/graves/FoLGrave01.jpg","./starter.mmo/data/shapes/graves/MoDGrave01.png"]

COMMON_DTS = ["./starter.mmo/data/shapes/markers/octahedron.dts","./starter.mmo/data/shapes/crossbow/projectile.dts",
"./starter.mmo/data/shapes/graves/modgrave01_32.dts","./starter.mmo/data/shapes/graves/folgrave01a_32.dts"]

COMMON_SFX = ["character/Boxing_FemalePunchBreath06.ogg","character/Boxing_FemalePunchBreath07.ogg","character/Boxing_FemalePunchBreath09.ogg",
"character/Boxing_MalePunchGrunt01.ogg","character/Boxing_MalePunchGrunt02.ogg","character/Boxing_MalePunchGrunt05.ogg","character/Boxing_MalePunchGrunt03.ogg",
"character/Boxing_MalePunchBreath02.ogg","character/Punch_Boxing_BodyHit01.ogg","character/Punch_Boxing_BodyHit02.ogg","character/Punch_Boxing_BodyHit03.ogg",
"character/Punch_Boxing_BodyHit04.ogg","character/Punch_Boxing_FaceHit1.ogg","character/Punch_Boxing_FaceHit2.ogg","character/Punch_Boxing_FaceHit3.ogg",
"character/Punch_Boxing_FaceHit4.ogg",
"sfx/Pickup_Armour_FlakVest2.ogg","sfx/Pickup_ArmourShield05.ogg","sfx/Pencil_WriteOnPaper2.ogg",
"sfx/Pickup_Magic02.ogg","sfx/Pickup_Coins01.ogg","sfx/Magic_Appear01.ogg",
"sfx/Menu_Accept.ogg","sfx/Menu_Magic01.ogg","sfx/Menu_Cancel01.ogg",
"environment/rain.ogg","environment/thunder1.ogg","environment/thunder2.ogg","environment/thunder3.ogg","environment/thunder4.ogg",
"sfx/Hit_MetalPoleImpact2.ogg","sfx/Underwater_Bubbles2.ogg",
"sfx/EvilMonster_TauntGrowl.ogg","sfx/Shatter_IceBlock1.ogg","sfx/Menu_Horror24.ogg",
"sfx/Pickup_ArmourShield04.ogg"
]

FULL_ZONES = ["base"]

FULL_TEXTURES =[]

FULL_RACES = ["Human"]

FULL_MUSIC = [
"28 - Dwarves_Krig.ogg","38 - Minions_of_Mirth_Title_Track.ogg"
]

FULL_SFX = []


FULL_SFX.extend(COMMON_SFX)
FULL_TEXTURES.extend(COMMON_TEXTURES)
    
FOLDERS = ["./starter.mmo/data/environment","./starter.mmo/data/skies","./starter.mmo/data/water","./starter.mmo/data/ui/icons",
"./starter.mmo/data/ui/tracking","./starter.mmo/data/ui/charportraits","./starter.mmo/data/ui/spellicons","./starter.mmo/data/ui/elements","./starter.mmo/data/ui/demo","./starter.mmo/data/terrains",
"./starter.mmo/data/shapes/particles","./starter.mmo/data/shapes/crossbow","./starter.mmo/data/ui/encyclopedia",
"./starter.mmo/data/sound/vocalsets/Female_LongSet_A","./starter.mmo/data/sound/vocalsets/Male_LongSet_A",
"./starter.mmo/data/ui/loading"]


