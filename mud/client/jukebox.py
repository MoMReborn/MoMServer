# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

     
from tgenative import *
from mud.world.defines import *
from mud.gamesettings import *
from mud.tgepython.console import TGEExport
from twisted.internet import reactor
import random
     
"""'
    
   
TGEEval(eval)"""

if GAMEROOT != "minions.of.mirth":
    FULL_MUSIC = [
    "28 - Dwarves_Krig.ogg",
    "38 - Minions_of_Mirth_Title_Track.ogg"
    ]
else:


    FULL_MUSIC = [
    "01 - Welcome_Sign.ogg",
    "02 - Villagers_of_Mirth_I.ogg",
    "03 - Peaceful.ogg",
    "04 - Landpromise.ogg",
    #"05 - Villagers_of_Mirth_II.ogg",
    "06 - Inexhaustible_Ardor.ogg",
    "07 - The_System.ogg",
    "08 - East_to_West.ogg",
    "09 - Battlefields_Pride.ogg",
    "10 - Ages_Long_Past.ogg",
    "11 - Ancient_Sleepers.ogg",
    "12 - Harpsichord_Movement.ogg",
    "13 - Mediromatic.ogg",
    "14 - Black_Air_Magic.ogg",
    "15 - Horn_Movement.ogg",
    "16 - Alveus.ogg",
    "17 - Settled_In_Sand.ogg",
    "18 - Safar_Khatir.ogg",
    "19 - Sea_Fighters_1.ogg",
    "20 - The_Sails_Of_Salvage.ogg",
    "21 - Sea_Fighters_2.ogg",
    "22 - Wandering_Day.ogg",
    "23 - Cold_Mountain_Clouds.ogg",
    "24 - The_Light_Of_Betrayal.ogg",
    "25 - Dramatic_Harp.ogg",
    "26 - Mystery_Forest_Of_Vikings.ogg",
    "27 - Beyond_Darkness.ogg",
    "28 - Dwarves_Krig.ogg",
    "29 - View_Over_The_Water.ogg",
    "30 - Simple_Mirth.ogg",
    "31 - View_Upon_The_Clouds.ogg",
    "32 - Negative_Tensed_Drama.ogg",
    "33 - Presenting_Battle.ogg",
    "34 - About_To_Attack.ogg",
    "35 - Horn_Queue.ogg",
    "36 - Harpsichord_Queue.ogg",
    "37 - Peaceful_2.ogg",
    "38 - Minions_of_Mirth_Title_Track.ogg"
    ]

    


allmuzak = FULL_MUSIC

currentmuzak = []
def Initialize():
    global currentmuzak
    currentmuzak = allmuzak[:]
    random.shuffle(currentmuzak)

FIRST = False
def PlayMusic():
    #return
    global FIRST
    global MUSICDEFFERED
    MUSICDEFFERED = None

    
    if not len(currentmuzak):
        Initialize()
    index = random.randint(0,len(currentmuzak)-1)
    song = currentmuzak[index]
    if not FIRST:
        song = "38 - Minions_of_Mirth_Title_Track.ogg"        
    currentmuzak.remove(song)
    filename = "%s/data/sound/music/%s"%(GAMEROOT,song)
    
    eval = r'alxPlay(alxCreateSource(AudioMusic, "%s"));'%filename
    
    TGEEval(eval)
    
    FIRST = True
    

MUSICDEFFERED = None    
def PySongStopped():
    #return
    global MUSICDEFFERED
    if MUSICDEFFERED:
        return
    MUSICDEFFERED = reactor.callLater(random.randint(30,180),PlayMusic)
    
    
def PlayTrack(song):
    fullsong = ' '.join(song)
    filename = "%s/data/sound/music/%s"%(GAMEROOT,fullsong)
    eval = r'alxPlay(alxCreateSource(AudioMusic, "%s"));'%filename
    
    TGEEval(eval)
    
    
TGEExport(PySongStopped,"Py","SongStopped","desc",1,1)
    
    
reactor.callLater(0,PlayMusic)
    
    
    



