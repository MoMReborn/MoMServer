# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

SERVER= "http://minions.prairiegames.com:8000"

#INDEX
INDEX_HTML = """
            <p align="center">PrairieWorld<br>Overall Player Statistics</p>
            <a href="SERVER/highestprimary">Characters - Highest Primary Level</a><br>
            <a href="SERVER/highestcombined">Characters - Highest Combined Level</a><br>
            <a href="SERVER/highestpresence">Characters - Highest Presence</a><br>
            
            <p align="center">Fellowship of Light Statistics</p>
            <a href="SERVER/highestprimaryfol">Characters - Highest Primary Level - FoL</a><br>
            <a href="SERVER/highestcombinedfol">Characters - Highest Combined Level - FoL</a><br>
            <a href="SERVER/richestfol">Players - Richest - FoL</a><br>
            
            <p align="center">Minions of Darkness Statistics</p>
            <a href="SERVER/highestprimarymod">Characters - Highest Primary Level - MoD</a><br>
            <a href="SERVER/highestcombinedmod">Characters - Highest Combined Level - MoD</a><br>
            <a href="SERVER/richestmod">Players - Richest - MoD</a><br>

       
            <p class="smallheader" align="center">Class Statistics</p>
            
            <a href="SERVER/highestassassin">Characters - Highest Primary - Assassin</a><br>
            <a href="SERVER/highestbarbarian">Characters - Highest Primary - Barbarian</a><br>
            <a href="SERVER/highestbard">Characters - Highest Primary - Bard</a><br>
            <a href="SERVER/highestcleric">Characters - Highest Primary - Cleric</a><br>
            <a href="SERVER/highestdoomknight">Characters - Highest Primary - Doom Knight</a><br>
            <a href="SERVER/highestdruid">Characters - Highest Primary - Druid</a><br>
            <a href="SERVER/highestmonk">Characters - Highest Primary - Monk</a><br>
            <a href="SERVER/highestnecromancer">Characters - Highest Primary - Necromancer</a><br>
            <a href="SERVER/highestpaladin">Characters - Highest Primary - Paladin</a><br>
            <a href="SERVER/highestranger">Characters - Highest Primary - Ranger</a><br>
            <a href="SERVER/highestrevealer">Characters - Highest Primary - Revealer</a><br>
            <a href="SERVER/highestshaman">Characters - Highest Primary - Shaman</a><br>
            <a href="SERVER/highesttempest">Characters - Highest Primary - Tempest</a><br>
            <a href="SERVER/highestthief">Characters - Highest Primary - Thief</a><br>
            <a href="SERVER/highestwarrior">Characters - Highest Primary - Warrior</a><br>
            <a href="SERVER/highestwizard">Characters - Highest Primary - Wizard</a><br>
            </p>
"""

INDEX_HTML = INDEX_HTML.replace("SERVER/",SERVER+"/")


TEMPLATE = """
            %s
"""

