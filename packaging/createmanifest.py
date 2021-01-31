# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#this will be shared on OSX, Windows, and eventually linux... the repo has platform and common folders

import os
import pickle,time
import sha,stat,sys
import string
from zipfile import ZipFile,ZIP_DEFLATED
from shutil import copyfile,rmtree,copytree

#a list of sha checksums every 64k of a file

def getsha(filename):
    f = open(filename, "rb")
    data = f.read()
    size=len(data)
    shalist = []
    start = 0
    while (size>0):
        
        m = sha.new()
        d = data[start:start+65535]
        m.update(d)
        shalist.append(m.hexdigest())
        size -= 65535
        start+= 65535
        
    f.close()
        
    return shalist


"""
def getfoldersha(dir):
    foldersha = []
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        if not os.path.isdir(fullpath) and not os.path.islink(fullpath):
            f = open(fullpath,'rb')
            foldersha.append(getsha(f))
            f.close()
            
    return foldersha
"""        

def dirwalk(dir,ignore):
    "walk a directory tree, using a generator"
    
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        fullpath = fullpath.replace("\\","/")
        if fullpath.upper().find(".SVN")!=-1:
            continue
       
        #these are causing a problem on osx 
        if fullpath.lower().endswith(".pyc"):
            continue

        if "thumbs.db" in fullpath.lower():
            continue

        if ".ds_store" in fullpath.lower():
            assert 0, ".DS_Store in %s"%fullpath
            continue
        
        ignored = False
        for i in ignore:
            if fullpath.upper().find(i) != -1:
                ignored = True 
                break
            
        if ignored:
            continue
        
        
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath,ignore):  # recurse into subdir
                yield x
        else:
            yield fullpath
                        
COUNT = 0L
def GenerateManifest(path,BASE,ignore = [],callback=None):
    global COUNT
    filedesc={}
    for elem in dirwalk(path,ignore):
        if not os.path.isfile(elem):
            continue
        elem=string.replace(elem,'\\','/')
        if os.path.islink(elem):
            continue

        
        size=os.stat(elem)[stat.ST_SIZE]
        
        if BASE == "common":
            fd = elem[elem.find(BASE):]
        else:
            fd = elem[len(BASE):]
            
        if sys.platform[:6] == 'darwin':
            fd = fd[1:] #lame getting rid of /
        filedesc[fd]=(size,getsha(elem))
        
        if callback:
            callback()
        
        COUNT+=1
        if not COUNT%250:
            print ".",
    return filedesc

def CreateManifest(FOLDER,BASE,ignore=[]):    
        
    m=GenerateManifest(FOLDER,BASE,ignore)
    mstr = pickle.dumps(m)
    zfile = ZipFile('%s/manifest.zip'%(FOLDER),'w',ZIP_DEFLATED)
    zfile.writestr('./manifest',mstr)
    zfile.close()
    
    #sha the manifest for a quick check
    s = getsha("%s/manifest.zip"%FOLDER)
    f = open("%s/manifest.sha"%FOLDER,"wb")
    pickle.dump(s,f)
    
    return m
    
def SaveManifest(m,filename,filenamesha):
    mstr = pickle.dumps(m)
    zfile = ZipFile(filename,'w',ZIP_DEFLATED)
    zfile.writestr('./manifest',mstr)
    zfile.close()
    
    #sha the manifest for a quick check
    s = getsha(filename)
    f = open(filenamesha,"wb")
    pickle.dump(s,f)





