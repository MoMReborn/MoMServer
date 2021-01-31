# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from distutils.core import setup
import py2exe
import shutil
import os,sys
#python 2.5 change
sys.path.append(os.getcwd())

if os.path.exists('./distrib/bin'):
    shutil.rmtree('./distrib/bin')
    
os.makedirs('./distrib/bin')


from mud.gamesettings import GAMEROOT,SERVER_SVN_WORKING_REPO

for arg in sys.argv:
    if arg.startswith("gameconfig="):
        sys.argv.remove(arg)
        break


# Local Repo
REPO_FOLDER = SERVER_SVN_WORKING_REPO

if os.path.exists('./build'):
    shutil.rmtree('./build')

if os.path.exists('./dist'):
    shutil.rmtree('./dist')

from mud.world.defines import *

if RPG_BUILD_DEMO:
    OUTPUT_FOLDER = "demo"
    INPUT_SCRIPT = "Client.pyw"
else:
    if not RPG_BUILD_LIVE:
        OUTPUT_FOLDER = "testing"
    else:
        OUTPUT_FOLDER = "live"
        
    INPUT_SCRIPT = "Client.pyw"

OUTPUT_FOLDER = "" #for now don't confuse the matter with demo/live/testing builds
        
#generate the version.py
from sqlite3 import dbapi2 as sqlite
import datetime,pickle

print "Generating ./mud/world/genesistime.py"
con = sqlite.connect("./%s/data/worlds/multiplayer.baseline/world.db"%GAMEROOT)
cur = con.cursor()
cur.execute('select genesis_time from World where name="TheWorld"')
dt = cur.fetchone()[0]

f = file("./mud/world/genesistime.py","w")
f.write("""
#AUTOMATICALLY GENERATED FILE DO NOT EDIT!

GENESISTIME = "%s"
"""%dt)

f.close()

f = file("./mud/binarygameconfig.py","w")
f.write("""
#AUTOMATICALLY GENERATED FILE DO NOT EDIT!

GAMECONFIG = "%s"
"""%arg)

f.close()


#!!! THERE APPEARS TO BE A BUG WITH DIST_DIR and pyd files!!!
setup(windows=[{"dest_base":"Client","script":INPUT_SCRIPT,"icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": { "compressed":True,"dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"],"packages": ["encodings","twisted.web"]}}
) 

try:
    os.makedirs("%s/%s/windows/bin"%(REPO_FOLDER,OUTPUT_FOLDER))
except:
    pass

for file in os.listdir("./dist"):
    shutil.copy("./dist/%s"%file,"%s/%s/windows/bin/%s"%(REPO_FOLDER,OUTPUT_FOLDER,file))
    
shutil.copy("./OpenAL32.dll","%s/%s/windows/bin/OpenAL32.dll"%(REPO_FOLDER,OUTPUT_FOLDER))
shutil.copy("./wrap_oal.dll","%s/%s/windows/bin/wrap_oal.dll"%(REPO_FOLDER,OUTPUT_FOLDER))

for file in os.listdir("./dist"):
    shutil.copy("./dist/%s"%file,"./distrib/bin/%s"%(file))
    
shutil.copy("./OpenAL32.dll","./distrib/bin/OpenAL32.dll")
shutil.copy("./wrap_oal.dll","./distrib/bin/wrap_oal.dll")

from createmanifest import CreateManifest,SaveManifest
import sys
print "Creating Windows Manifest"
wm = CreateManifest("%s/%s/windows"%(REPO_FOLDER,OUTPUT_FOLDER),"%s/%s/windows/"%(REPO_FOLDER,OUTPUT_FOLDER))
SaveManifest(wm,"%s/%s/windows/manifest.zip"%(REPO_FOLDER,OUTPUT_FOLDER),"%s/%s/windows/manifest.sha"%(REPO_FOLDER,OUTPUT_FOLDER))







