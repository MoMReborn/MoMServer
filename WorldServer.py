# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import imp, os, sys

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
        #sys.path.insert(0,maindir)
        
    sys.path.append(maindir)    
    

from mud.worldserver.main import main
#import profile
#profile.runctx("main()",globals(),locals(),"profile.prof")

#import hotshot
#prof = hotshot.Profile("hotshot.prof",0,0)
#prof.runctx("main()",globals(),locals())
#prof.close()


main()


