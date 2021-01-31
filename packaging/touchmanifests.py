# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from createmanifest import CreateManifest,SaveManifest
import sys,os

sys.path.append(os.getcwd())

from mud.gamesettings import GAMEROOT

if sys.platform[:6] == 'darwin':
    raise "no longer used by OSX, use minions2app exclusively"
    print "Creating OSX Manifest"
    ignore = ["../ALPHA/MAC/COMMON","../ALPHA/MAC/CACHE","../ALPHA/MAC/.DS_STORE","../ALPHA/MAC/MANIFEST.ZIP","../ALPHA/MAC/MANIFEST.SHA"]
    wm = CreateManifest("../alpha/mac","../alpha/mac/",ignore)
    SaveManifest(wm,"../alpha/mac/manifest.zip","../alpha/mac/manifest.sha")
else:
    from mud.world.defines import *
    from mud.gamesettings import SERVER_SVN_WORKING_REPO
    
    if GAMEROOT == "minions.of.mirth":
        OUTPUT_FOLDER = "testing"
        if RPG_BUILD_LIVE:
            OUTPUT_FOLDER = "live"
            
        if RPG_BUILD_DEMO:
            OUTPUT_FOLDER = "demo"

        print "Creating Windows Manifest"
        wm = CreateManifest("../%s/windows"%OUTPUT_FOLDER,"../%s/windows/"%OUTPUT_FOLDER)
        SaveManifest(wm,"../%s/windows/manifest.zip"%OUTPUT_FOLDER,"../%s/windows/manifest.sha"%OUTPUT_FOLDER)
            
        cm = CreateManifest("../%s/common"%OUTPUT_FOLDER,"common")
        SaveManifest(cm,"../%s/common/manifest.zip"%OUTPUT_FOLDER,"../%s/common/manifest.sha"%OUTPUT_FOLDER)

    else:
        from ConfigParser import SafeConfigParser

        parser = SafeConfigParser()
        parser.read("./serverconfig/server.cfg")

        # Local Repo
        OUTPUT_FOLDER = SERVER_SVN_WORKING_REPO
        
        print "Creating Common Manifest"
            
        cm = CreateManifest("%s/common"%OUTPUT_FOLDER,"common")
        SaveManifest(cm,"%s/common/manifest.zip"%OUTPUT_FOLDER,"%s/common/manifest.sha"%OUTPUT_FOLDER)
    
