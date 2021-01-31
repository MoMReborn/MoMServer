# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import imp, os, sys

def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze
           
if main_is_frozen():
    os.chdir("../common")
    maindir = os.getcwd()
    sys.path.append(maindir)    

from mud.worlddaemon.worldimp import main
main()


