# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from distutils.core import setup
import py2exe
import shutil,string
import sys
import zipfile
import os
import os.path
import getopt
import glob


#patch to py2exe so all deps get included in zip
"""
            if not dry_run:
                z = zipfile.ZipFile(zip_filename, "w",
                                    compression=compression)
                def visit (z, dirname, names):
                    dname = dirname[dirname.find(base_dir)+len(base_dir)+1:]
                    #print dname
                    
                    for name in names:
                        path = os.path.normpath(os.path.join(dirname, name))
                        if os.path.isfile(path):
                            z.write( path,os.path.join(dname, name))#z.write(path, path)
                            #print "adding '%s'" % path
        
                z = zipfile.ZipFile(zip_filename, "w",
                                    compression=zipfile.ZIP_DEFLATED)
    
                os.path.walk(base_dir, visit, z)
                z.close()

                #for f in files:
                #    z.write(os.path.join(base_dir, f), f)
                #z.close()

            return zip_filename

"""

#python 2.5 change
sys.path.append(os.getcwd())

from mud.world.defines import *

DEMO = False
if RPG_BUILD_DEMO:
    DEMO = True

if os.path.exists('./build'):
    shutil.rmtree('./build')
    
if os.path.exists('./dist'):
    shutil.rmtree('./dist')

if DEMO:
    OUTPUT_FOLDER = "demo_dws"
else:
    if not RPG_BUILD_LIVE:
        OUTPUT_FOLDER = "testing_dws"
    else:
        OUTPUT_FOLDER = "live_dws"
    
#!!! THERE APPEARS TO BE A BUG WITH DIST_DIR and pyd files!!!
    
if not DEMO:
    setup(console=[{"script":"Genesis.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True ,"dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"], "packages": ["encodings"]}}
) 

setup(windows=[{"script":"WorldManager.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True , "dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll","gdiplus.dll"],"excludes":["genesis"],"packages": ["encodings"]}}
) 

setup(console=[{"script":"WorldServer.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True ,"dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"],"packages": ["encodings"]}}
) 

setup(console=[{"script":"WorldDaemon.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True ,"dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"],"packages": ["encodings"]}}
)

setup(console=[{"script":"WorldImp.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True ,"dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"],"packages": ["encodings"]}}
)
#we exclude the wx dll because pytge is linked to it and it can't be found (py2exe should probably check that it's not already in dist)
setup(console=[{"script":"ZoneServer.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True , "dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"],"packages": ["encodings"]}}
) 

setup(console=[{"script":"WorldUpdate.py","icon_resources": [(1, "packaging/eye.ico")]}],
      options = {"py2exe": {"compressed":True ,"dll_excludes": ["wxmsw26uh_vc.dll","netapi32.dll"],"excludes":["genesis"],"packages": ["encodings"]}}
) 

#"dist_dir":"./bin/%s/windows/bin"%OUTPUT_FOLDER,
try:
    os.makedirs("./bin/%s/bin"%OUTPUT_FOLDER)
except:
    pass

for file in os.listdir("./dist"):
    shutil.copy("./dist/%s"%file,"./bin/%s/bin/%s"%(OUTPUT_FOLDER,file))


shutil.copy('./packaging/WorldManager.exe.manifest','./bin/%s/bin/WorldManager.exe.manifest'%OUTPUT_FOLDER)
shutil.copy('./packaging/WorldServer.exe.manifest','./bin/%s/bin/WorldServer.exe.manifest'%OUTPUT_FOLDER)


shutil.copy('./packaging/WorldManager.exe','./bin/%s/WorldManager.exe'%OUTPUT_FOLDER)

#ok, now we need to pick apart the zip

FILES = []
class unzip:
    def __init__(self, verbose = False, percent = 10):
        self.verbose = verbose
        self.percent = percent
        
    def extract(self, file, dir):
        if not dir.endswith(':') and not os.path.exists(dir):
            os.makedirs(dir)

        zf = zipfile.ZipFile(file)

        num_files = len(zf.namelist())
        percent = self.percent
        divisions = 100 / percent
        perc = int(num_files / divisions)

        # extract files to directory structure
        for i, name in enumerate(zf.namelist()):

            if not name.endswith('/') and not name.endswith('\\'):
                path,f = os.path.split(os.path.join(dir, name))
                if not os.path.exists(path):
                    os.makedirs(path)
                
                FILES.append(os.path.join(dir, name))
                outfile = open(os.path.join(dir, name), 'wb')

                outfile.write(zf.read(name))
                outfile.flush()
                outfile.close()

if not DEMO:
    unzipper = unzip()
            
    unzipper.extract("./bin/%s/bin/library.zip"%OUTPUT_FOLDER, "./distrib_dws/library")
    
    #now put everything back in the zip, minus the mud module
    
    file = zipfile.ZipFile("./distrib_dws/library.zip", "w")
    
    for name in FILES:
        if name[22:].startswith("mud"):
            continue
        file.write(name, name[22:], zipfile.ZIP_DEFLATED)
    file.close()
    
    IGNORE = []
    IGNOREEXT = []
    KEEP = []
    SKIP = []
    
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
                            
    
    STUFF = list(dirwalk("./distrib_dws/library/mud"))
    
    NEWSTUFF = []
    SRCFILES = []
    dstuff = STUFF[:]
    STUFF = []
    for s in dstuff:
        if s.startswith('./distrib_dws/library/mud/world/') and not s.startswith('./distrib_dws/library/mud/world/shared'):
            SRCFILES.append(s)
            continue
        d = s.replace("./distrib_dws/library/mud","./bin/%s/common/mud"%OUTPUT_FOLDER)
        STUFF.append(s)
        NEWSTUFF.append(d)
        
    for src,dst in zip(STUFF,NEWSTUFF):
            path,f = os.path.split(dst)
            if not os.path.exists(path):
                os.makedirs(path)
            try:
                shutil.copy(src,dst)
            except:
                print "WARNING: Couldn't copy %s"%elem
    
        
    for src in SRCFILES:
        s = src.replace("./distrib_dws/library/","./")
        s = s.replace(".pyc",".py")
        d = src.replace("./distrib_dws/library/","./bin/%s/common/"%OUTPUT_FOLDER)
        d = d.replace(".pyc",".py")        
        shutil.copy(s,d)
        
        
        
        
    shutil.copy("./distrib_dws/library.zip","./bin/%s/bin/library.zip"%OUTPUT_FOLDER)
        
    
    #shutil.rmtree("./distrib_dws/library")
    #os.remove("./distrib_dws/library.zip")








