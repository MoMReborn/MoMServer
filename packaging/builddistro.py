# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import sys,os
sys.path.append(os.getcwd())

import string
import shutil
from mud.world.defines import *
from mud.gamesettings import GAMEROOT,USE_PNG_SVN

sys.path.insert(0,os.getcwd()+"/%s"%GAMEROOT)

BUILD_MODPACK = True

if os.path.exists('./distrib/common'):
    shutil.rmtree('./distrib/common')
    
os.makedirs('./distrib/common')

#IGNORE = ['./build','./data','./dist','./mud','./packaging','./sandbox', './editor',
#'./%s/data'%GAMEROOT,'./%s/cache'%GAMEROOT,'./distrib','./distrib_dws','./processedPNG','./serverconfig']

INCLUDE = ['./common/','./%s/'%GAMEROOT]

IGNORE = ['./%s/data'%GAMEROOT,'./%s/cache'%GAMEROOT]


IGNOREEXT = ['.db','.ms3d','.py','.pyc','.cs','.max','.txt','.exe','.gui','.tmp','.log',
'.ilk','.pyd','.prof','.pyw','.bat','.sh','.html','.lnk','.rec','.3ds',
'.qkm','.qrk',".ds_store",".dll",".so",".xls",".xcf",".map",".bak",".pdb",".idb"]

FILES = []

KEEP = ['patchlist.txt']

SKIP = ['./%s/client/prefs.cs.dso'%GAMEROOT,'./%s/client/config.cs.dso'%GAMEROOT,
'./common/ui/cache/clipboard.gui.dso',"./htpasswd"]

if BUILD_MODPACK:
    IGNOREEXT.remove(".gui")
    IGNOREEXT.remove(".cs")
    IGNOREEXT.append(".dso")
    


def ProcessTextures(stuff):
    import Image

    leave = ["./common","./%s/data/environment"%GAMEROOT,"./%s/data/skies"%GAMEROOT,"./%s/client"%GAMEROOT,
    "./%s/data/terrains/details"%GAMEROOT,"./%s/data/shapes/plants"%GAMEROOT,"./%s/data/shapes/player"%GAMEROOT,
    "./%s/data/shapes/particles/fxpack1"%GAMEROOT,"./%s/data/shapes/explosiondebris"%GAMEROOT]
    
    
        
    if not os.path.exists('./processedPNG'):
        os.mkdir('./processedPNG')
    
    
    for file in stuff[:]:    
        if not USE_PNG_SVN:
            if ".png" not in file:
                continue
        
            process = True
            for p in leave:
                if p in file:
                    process = False
                    break
            
            if not process:
                continue
                
        
            filename = "./processedPNG/"+file[2:]
            filename = filename[:-4]
            filename+='.jpg'
            
            if os.path.exists(filename):
                stuff.remove(file)
                stuff.append(filename)
            
                alpha = filename[:-4]
                alpha+=".alpha.jpg"    
            
                if os.path.exists(alpha):
                    stuff.append(alpha)
                continue
        
            path,f = os.path.split(filename)
        
            if not os.path.exists(path):
                os.makedirs(path)

            
        
            try:
                png = Image.open(file)
            except:
                print "WARNING: Unable to process: %s"%file
                continue
        
        
            if png.mode != 'RGBA' and png.mode != 'RGB':
                continue
        
            assert png.size[0]<=512 and png.size[1]<=512,file
        
            print "Processing: %s"%file
            stuff.remove(file)
        
            png.save(filename)
            stuff.append(filename)
            alpha = png.split()

            if len(alpha) > 3 and ("data/shapes/character" not in filename or ("/lich_" in filename or "treant_special" in filename)): #some of the character textures have alpha for some reason
                filename = filename[:-4]
                filename+=".alpha.jpg"        
                alpha[3].save(filename)
                stuff.append(filename)
        else:
            print "Processing: %s"%file
            continue


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
            found = False
            for i in INCLUDE:
                if ("%s/"%fullpath).startswith(i):
                    found = True
                    break
            if not found:
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
                        

def Go(stuff):
    for elem in stuff:
        if "thumbs.db" in elem.lower():
            continue
        if elem.startswith("./processedPNG/"):
            filename = "./distrib/common/"+elem[15:]
        else:
            filename = "./distrib/common/"+elem[2:]
        path,f = os.path.split(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        try:
            shutil.copy(elem,filename)
        except:
            print "WARNING: Couldn't copy %s"%elem


from contentsifter import GatherContent

STUFF = list(dirwalk('./'))
CONTENT = GatherContent()

FILTER = []
for c in CONTENT:
    root,ext = os.path.splitext(c)
    if ext.lower() in IGNOREEXT:
        continue
    FILTER.append(c)
     
CONTENT = FILTER
    
    

STUFF.extend(CONTENT)


ProcessTextures(STUFF)

Go(STUFF)
shutil.copy("./main.cs","./distrib/common/main.cs")

"""    
for elem in dirwalk('./processedPNG'):
    filename = "./distrib/common/"+elem[14:]
    path,f = os.path.split(filename)
    if not os.path.exists(path):
        os.makedirs(path)
    print "copying ",elem
    shutil.copy(elem,filename)
"""

os.makedirs('./distrib/common/%s/data/worlds/multiplayer.baseline'%GAMEROOT)
shutil.copy('./%s/data/worlds/multiplayer.baseline/world.db'%GAMEROOT,
'./distrib/common/%s/data/worlds/multiplayer.baseline/world.db'%GAMEROOT)
    
#shutil.copy('./packaging/Patcher.exe','./distrib/Patcher.exe')
if GAMEROOT == "minions.of.mirth":
    shutil.copy('./packaging/prefs/starter_prefs.cs','./distrib/common/%s/client/prefs.cs'%GAMEROOT)
    shutil.copy('./packaging/prefs/config.cs','./distrib/common/%s/client/config.cs'%GAMEROOT)
else:
    shutil.copy('./packaging/prefs/prefs.cs','./distrib/common/%s/client/prefs.cs'%GAMEROOT)
    shutil.copy('./packaging/prefs/config.cs','./distrib/common/%s/client/config.cs'%GAMEROOT)
    

os.makedirs('./distrib/common/serverconfig')
shutil.copy('./serverconfig/__init__.py','./distrib/common/serverconfig/__init__.py')






 
