# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from distutils.core import setup
import py2exe
import shutil
import os,sys

#python 2.5 change
sys.path.append(os.getcwd())

if os.path.exists('./build'):
    shutil.rmtree('./build')

if os.path.exists('./dist'):
    shutil.rmtree('./dist')

from mud.world.defines import *


if RPG_BUILD_DEMO:
    OUTPUT_FOLDER = "demo"
    INPUT_SCRIPT = "MinionsOfMirth.pyw"
else:
    if not RPG_BUILD_LIVE:
        OUTPUT_FOLDER = "testing"
    else:
        OUTPUT_FOLDER = "live"
        
    INPUT_SCRIPT = "MinionsOfMirth.pyw"
        
    
    
#generate the version.py
from sqlite3 import dbapi2 as sqlite
import datetime,pickle


print "Generating ./mud/world/genesistime.py"
con = sqlite.connect("./minions.of.mirth/data/worlds/multiplayer.baseline/world.db")
cur = con.cursor()
cur.execute('select genesis_time from World where name="TheWorld"')
dt = cur.fetchone()[0]

f = file("./mud/world/genesistime.py","w")
f.write("""
#AUTOMATICALLY GENERATED FILE DO NOT EDIT!

GENESISTIME = "%s"
"""%dt)

f.close()

#setup(windows=[{"script":"mom.py","icon_resources": [(1, "packaging/eye.ico")]}],
#      options = {"py2exe": {"packages": ["encodings"],"dist_dir":"./dist/MinionsOfMirth" }},
#) 

#!!! THERE APPEARS TO BE A BUG WITH DIST_DIR and pyd files!!!
#we exclude the wx dll because pytge is linked to it and it can't be found (py2exe should probably check that it's not already in dist)
setup(windows=[{"dest_base":"MinionsOfMirth","script":INPUT_SCRIPT,"icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": { "compressed":True,"dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"],"packages": ["encodings","twisted.web"]}}
) 

#"dist_dir":"../%s/windows/bin"%OUTPUT_FOLDER,
for file in os.listdir("./dist"):
    shutil.copy("./dist/%s"%file,"../%s/windows/bin/%s"%(OUTPUT_FOLDER,file))
    

shutil.copy("./OpenAL32.dll","../%s/windows/bin/OpenAL32.dll"%OUTPUT_FOLDER)
shutil.copy("./wrap_oal.dll","../%s/windows/bin/wrap_oal.dll"%OUTPUT_FOLDER)

shutil.copy('./packaging/MinionsOfMirth.exe','../%s/windows/MinionsOfMirth.exe'%OUTPUT_FOLDER)
#shutil.copy('./packaging/WorldManager.exe','../%s/windows/WorldManager.exe'%OUTPUT_FOLDER)


from createmanifest import CreateManifest,SaveManifest
import sys
print "Creating Windows Manifest"
wm = CreateManifest("../%s/windows"%OUTPUT_FOLDER,"../%s/windows/"%OUTPUT_FOLDER)
SaveManifest(wm,"../%s/windows/manifest.zip"%OUTPUT_FOLDER,"../%s/windows/manifest.sha"%OUTPUT_FOLDER)







