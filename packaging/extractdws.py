# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import os,sys
sys.path.append(os.getcwd())
import string
import shutil
from mud.world.defines import *
from mud.gamesettings import GAMEROOT

DEMO = False
if RPG_BUILD_DEMO:
    DEMO = True

#Extract Dedicated World Server

if GAMEROOT == "minions.of.mirth":
    if DEMO:
        INPUT_DIR = "demo"
    else:
        if not RPG_BUILD_LIVE:
            INPUT_DIR = "testing"
        else:
            INPUT_DIR = "demo" #always demo, it has the stuff
else:
    #fix me
    INPUT_DIR = "starter" 

if os.path.exists('./distrib_dws'):
    shutil.rmtree('./distrib_dws')

IGNORE = ["../%s/common/%s/data/environment"%(INPUT_DIR,GAMEROOT),"../%s/common/%s/data/skies"%(INPUT_DIR,GAMEROOT),
"../%s/common/%s/data/sound"%(INPUT_DIR,GAMEROOT),"../%s/common/%s/data/terrains"%(INPUT_DIR,GAMEROOT),"../%s/common/%s/data/ui"%(INPUT_DIR,GAMEROOT),
"../%s/common/%s/data/water"%(INPUT_DIR,GAMEROOT),"../%s/windows"%INPUT_DIR,"../%s/dws"%INPUT_DIR]
IGNOREEXT = ['.jpg','.png','.ml']

FILES = []
KEEP = []
SKIP = ["../%s/common/manifest.zip"%INPUT_DIR,"../%s/common/manifest.sha"%INPUT_DIR]


def dirwalk(dir):
    "walk a directory tree, using a generator"
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        fullpath = string.replace(fullpath,'\\','/')
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            if fullpath.find(".svn")!=-1:
                continue
            if fullpath in IGNORE:
                continue
            for x in dirwalk(fullpath):  # recurse into subdir
                yield x
        else:
            root,ext = os.path.splitext(fullpath)
            path,file = os.path.split(fullpath)
            if ext.lower() in IGNOREEXT and file not in KEEP:
                continue
            if fullpath in SKIP:
                continue
            yield fullpath
                        

STUFF = list(dirwalk('../%s'%INPUT_DIR))

NEWSTUFF = []
for s in STUFF:
    s = s.replace("../%s/common"%INPUT_DIR,"./distrib_dws/common")
    NEWSTUFF.append(s)
    
for src,dst in zip(STUFF,NEWSTUFF):
        path,f = os.path.split(dst)
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            shutil.copy(src,dst)
        except:
            print "WARNING: Couldn't copy %s"%src
    
    
    
    

    

