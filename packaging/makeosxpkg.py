# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



import os,shutil,sys


if '-free' in sys.argv:
    FREE = True
elif '-testing' in sys.argv:
    FREE = False
else:
    raise "Please specifiy -free or -testing in command line options"

    
PKGNAME = "MoMFreeEdition"
#if not FREE:
#   PKGNAME = "MoMPremiumEdition"

os.chdir("../")
#try:
 #   shutil.rmtree(PKGNAME)
#except:
 #   pass
    
    
#if os.path.exists(PKGNAME):
 # #  raise "Unable to remove %s folder"%PKGNAME

folders =[
"Package_Root",
"Package_Root/usr","Package_Root/usr/bin","Package_Root/usr/local","Package_Root/usr/local/bin",
"Package_Root/private","Package_Root/private/etc",
"Package_Root/Applications","Package_Root/Applications/MinionsOfMirth",
"Resources","Resources/PreFlight","Resources/PostFlight",
]

#for folder in folders:
#   os.makedirs(PKGNAME+"/"+folder)
    
    
srcpath = "./demo/mac/MinionsOfMirth.app"
if not FREE:
    srcpath = "./testing/mac/MinionsOfMirth.app"

if FREE:    
    dstpath = PKGNAME+"/Package_Root/Applications/MinionsOfMirth/MinionsOfMirth.app"
else:
    dstpath = PKGNAME+"/Package_Root/Applications/MinionsOfMirthTesting/MinionsOfMirth.app"
 
    
for root,dirs,files in os.walk(srcpath):
    for name in files:
        filename = os.path.join(root,name)
        
        if ".svn" in filename.lower():
            continue
        
        if filename.lower().endswith(".pyc"):
            os.remove(filename)
            continue
        
        dst = filename.replace(srcpath,dstpath) 
        
        try:
            os.makedirs(os.path.dirname(dst))
        except:
            pass
        
        shutil.copyfile(filename,dst)
        print filename,dst 

    
#shutil.copytree("./testing_mom/dist/MinionsOfMirth.app",PKGNAME+"/"+"Package_Root/Applications/MinionsOfMirth/MinionsOfMirth.app",False)
#shutil.copytree("./packaging/common",PKGNAME+"/"+"Applications/MinionsOfMirth/common")
    



