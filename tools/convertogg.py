
import os
import string
import shutil

if os.path.exists('c:/sfxogg'):
    shutil.rmtree('c:/sfxogg')
    
os.makedirs('c:/sfxogg')

IGNORE = []
IGNOREEXT = []
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


for elem in dirwalk('./'):
    if ".wav" in elem.lower():
        base,ext = os.path.splitext(elem)
        
        ogg = base+".ogg"
        
        dir = os.path.split(ogg)[0]
        dir = "c:/sfxogg/"+dir[2:]
        print dir
        
        try:
            os.makedirs(dir)
        except:
            pass
            
        print ogg
        
        cmd = r'oggenc'
        args = '-o="%s" -q 7 "%s"'%(ogg,elem)
        
        os.spawnl(os.P_WAIT,cmd,args)            
        
        
for elem in dirwalk('./'):
    if ".ogg" in elem.lower():
        base,file = os.path.split(elem)
        
        base = "c:/sfxogg/"+base[2:]+"/"+file
        
        shutil.copy(elem,base)
        
        print base
        
        
        
        
        
        

        
    

