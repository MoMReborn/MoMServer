# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud_ext.gamesettings import override_ip_addresses
override_ip_addresses()

#world update script

import imp, os, sys
from mud.gamesettings import *

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze
           
if main_is_frozen():
    #maindir = get_main_dir()
    
    if sys.platform[:6] == 'darwin':
        #need to go up three folders
        os.chdir("../../../mom")
        maindir = os.getcwd()
    else:
        os.chdir("../common")
        maindir = os.getcwd()
        sys.path.append(maindir)
        


  
print "\n\n-------------------------------------"
print "Minions Of Mirth World Updater v .01a"
print "-------------------------------------"


mode = False
world = ""
try:
    index = 1
    if ".py" in sys.argv[1].lower():
        index = 2
        
    if sys.argv[index].lower()=="single":
        mode = "singleplayer"
    elif sys.argv[index].lower()=="multi":
        mode = "multiplayer"
    else:
        raise "error"
    
    #case?
    worldname = sys.argv[index+1]
    
    
        
except:
    #traceback.print_exception(sys.exc_info()[0],sys.exc_info()[1],sys.exc_info()[2])
    print "Usage: WorldUpdate single|multi worldname"
    sys.exit()

print "Updating World: %s"%worldname    

#backup in case something goes wrong
wpath = "%s/%s/data/worlds/%s/%s/world.db"%(os.getcwd(),GAMEROOT,mode,worldname)
basepath = "%s/%s/data/worlds/multiplayer.baseline/world.db"%(os.getcwd(),GAMEROOT)

from mud.world.worldupdate import WorldUpdate
if WorldUpdate(wpath,basepath,False,True):
    print "Error Updating World"
else:
    print "World Updated"
    
    
    
    
    
    


