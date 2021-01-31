# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from setuptools import setup
import py2app
import os
import string
import shutil
import findertools


PROCESS_PYTGE = True
PROCESS_FRAMEWORKS = False

RPG_BUILD_DEMO = True
RPG_BUILD_LIVE = True

OUTPUT_FOLDER = "testing"
if RPG_BUILD_DEMO:
    OUTPUT_FOLDER = "demo"
elif RPG_BUILD_LIVE:
    OUTPUT_FOLDER = "live"

if os.path.exists('./dist'):
    shutil.rmtree('./dist')

if os.path.exists('./build'):
    shutil.rmtree('./build')

setup(
    app=['MinionsOfMirth.pyw'],setup_requires=["py2app"],options = dict (py2app = {"iconfile":"./packaging/MinionsOfMirth.icns","excludes":["genesis"],"packages":["encodings"]})
)

#setup(
#    app=['Patcher.py'],options = dict (py2app = {"iconfile":"./packaging/MinionsOfMirth.icns","excludes":["genesis"],"packages":["encodings"]})
#)


frameworkskip = ["Ogg.framework","Python.framework","Vorbis.framework"]

SKIPPED = []
        

for root,dirs,files in os.walk("./dist"):
    for name in files:
        filename = os.path.join(root,name)
        
        if filename.lower().endswith(".pyc"):
            os.remove(filename)
            continue
        
        skip = False
        if not PROCESS_FRAMEWORKS:
            for f in frameworkskip:
                if f.lower() in filename.lower():
                    skip = True
                    break
        if not PROCESS_PYTGE and "pytge.so" in filename:
            skip=True

        if skip:
            SKIPPED.append(filename)
            continue
                 
        
        dst = filename.replace("./dist","../%s/mac"%OUTPUT_FOLDER) 
        
        print dst
        
        try:
            os.makedirs(os.path.dirname(dst))
        except:
            pass
        
        shutil.copyfile(filename,dst)
        
        #dst = "../alpha/mac/%s/"%dirs,name)
        #print dst
    

from createmanifest import CreateManifest,SaveManifest
import sys

print "Creating OSX Manifest"
opf = OUTPUT_FOLDER.upper()
ignore = ["../%s/MAC/COMMON"%opf,"../%s/MAC/CACHE"%opf,"../%s/MAC/.DS_STORE"%opf,"../%s/MAC/MANIFEST.ZIP"%opf,"../%s/MAC/MANIFEST.SHA"%opf,
"../%s/MAC/PATCH_FILES"%opf,"../%s/MAC/RESTORE"%opf, "../%s/MAC/MINIONSOFMIRTH.APP/CONTENTS/RESOURCES/LOG_MINIONSOFMIRTH.TXT"%opf]
wm = CreateManifest("../%s/mac"%OUTPUT_FOLDER,"../%s/mac"%OUTPUT_FOLDER,ignore)
SaveManifest(wm,"../%s/mac/manifest.zip"%OUTPUT_FOLDER,"../%s/mac/manifest.sha"%OUTPUT_FOLDER)
print "\n"
if len(SKIPPED):
    print "Skipped",SKIPPED
    print "WARNING some items skipped: If you have changed and of these items you MUST tweak this script!"
