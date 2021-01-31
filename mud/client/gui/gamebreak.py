# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *


BREAKTEXT = """<shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98>
<bitmap:minions.of.mirth/client/ui/mom_gamebreak>








<font:Arial:16><color:FFBBFF>
Thank you for playing the Minions of Mirth: Free Edition
<font:Arial:18><color:FFFF66>
The game is currently in a break and will resume in less than a minute.










<font:Arial:16><color:BBFFFF>
The Minions of Mirth: Premium Edition has no game breaks and requires no monthly fee for online play.  

<font:Arial:14><color:BBBBFF>
+ Access to all the game's equipment, spells, advancements, and skills!

+ Multiclass your characters with secondary and tertiary classes to increase their power!

+ Access to our Premium Servers with no monthly fee.

+ Characters transfer from the Free Edition to the Premium Edition and can then be played on our premium servers!

+ Store up to 24 characters and 10 monsters on our premium servers!

+ A simple patch that upgrades the Free Edition to the Premium Edition!

+ Play without game breaks!

+ Host your own persistent world or play on other custom servers. 

+ Please see http://www.prairiegames.com for more details.

"""


BREAKTEXTPREMIUM = """<shadowcolor:000000><shadow:1:1><just:center><lmargin%:2><rmargin%:98>
<bitmap:minions.of.mirth/client/ui/mom_gamebreak>








<font:Arial:16><color:FFBBFF>
You are playing on a Minions of Mirth: Free Server.  
<font:Arial:18><color:FFFF66>
The game is currently in a break and will resume in less than a minute.

<font:Arial:16><color:BBFFFF>
You may also play on Premium Servers which have no game breaks.

"""

GAMEBREAK = False

def DisplayBreak(value):
    global GAMEBREAK
    if value == GAMEBREAK:
        return
    GAMEBREAK = value
    if not value:
        TGEEval("canvas.popDialog(GameBreakGui);")
    else:
        TGEEval("canvas.pushDialog(GameBreakGui);")

def PyExec():
    #eventually this can be a full help system
    
    
    
    if RPG_BUILD_LIMITED:
        text = BREAKTEXT.replace('\n','\\n')
        TGEObject("MOM_BUYBUTTON").visible = True
    else:
        TGEObject("MOM_BUYBUTTON").visible = False
        text = BREAKTEXTPREMIUM.replace('\n','\\n')
        
    TGEEval(r'GAMEBREAK_TEXT.setText("%s");'%text)

    
