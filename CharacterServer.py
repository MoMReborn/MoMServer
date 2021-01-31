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
    #maindir = get_main_dir()
    
    if sys.platform[:6] == 'darwin':
        #need to go up three folders
        os.chdir("../../../mom")
        maindir = os.getcwd()
    else:
        os.chdir("../common")
        maindir = os.getcwd()
    
    sys.path.append(maindir)


from mud_ext.characterserver.server import main
main()
