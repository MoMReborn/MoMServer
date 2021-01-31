# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud_ext.gamesettings import override_ip_addresses
override_ip_addresses()

import imp, os, sys

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze
           
if main_is_frozen():
    os.chdir("../common")
    maindir = os.getcwd()
    sys.path.append(maindir)    
    
elif sys.platform == "win32":
    os.chdir(os.path.dirname(sys.argv[0]))


from mud_ext.worlddaemon.main import main
main()


