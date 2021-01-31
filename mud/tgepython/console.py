# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

import traceback
from tgenative import *
import inspect


class TGEManager:
    def __init__(self):
        self.simDataBlocks={}
        self.simObjects={}
        
        self.objectLookup={} #id -> SimObject and SimDataBlocks
        self.functionBindings={} #[namespace][functionname]=function
                
    def registerObject(self,id,object):
        self.objectLookup[id]=object
        
        #order is important here as SimDataBlock is a SimObject
        if isinstance(object,SimDataBlock):            
            self.simDataBlocks[id]=object
        else:            
            self.simObjects[id]=object
        
    def unregisterObject(self, objectid):
        
        o=self.objectLookup[objectid]
        
        #order is important here as SimDataBlock is a SimObject
        if isinstance(o,SimDataBlock):            
            del self.simDataBlocks[objectid]
        else:            
            del self.simObjects[objectid]
        
        #register that this object has been deleted to containers
        o._tgedeleted=True
        
        del self.objectLookup[objectid]
        
    def cleanup(self):
        for x in self.simObjects.itervalues():
            x._tge.delete()
        for x in self.simDataBlocks.itervalues():
            x._tge.delete()
    
        self.objectLookup.clear()
        self.simObjects.clear()
        self.simDataBlocks.clear()
            
    def export(self,function,namespace,fname,usage,minarg,maxarg):
        if namespace==None:
            namespace='Global'
            TGENativeExport(fname,usage,minarg,maxarg)
        else:        
            TGENativeExport(namespace,fname,usage,minarg,maxarg)
            
        if not self.functionBindings.has_key(namespace):
            self.functionBindings[namespace]={}
                
        self.functionBindings[namespace][fname]=function
        
    def callback(self,selfid,namespace,functionname,args):
        simo=None
        if selfid != None:       
            try:
                simo=self.objectLookup[selfid]
            except:
                simo=None#TGEObject(selfid)
        
                
        if not self.functionBindings[namespace].has_key(functionname):
            raise TypeError,("TGECall: Function doesn't exist",namespace,functionname)
            return None
        try:
            if simo != None:
                r=self.functionBindings[namespace][functionname](simo,args)
            elif args[0]!=None:
                r=self.functionBindings[namespace][functionname](args)
            else:
                r=self.functionBindings[namespace][functionname]()
                
        except:
            traceback.print_exc()

            return None
        
        return r        
        
        
    
def TGECleanup():
    gTGEManager.cleanup()

def TGEExport(function,namespace,fname,usage,minarg,maxarg):
    gTGEManager.export(function,namespace,fname,usage,minarg,maxarg)
        
#notification from TGE when it deletes a Python created instance
def TGEDelete(selfid):    
    gTGEManager.unregisterObject(selfid)
    
def TGEPyExec(filename,function=None):
    m=__import__(filename)
    if not function:
        m.PyExec()
        
#TGEObject() raises expecption if object not found... this is desireable to catch spelling mistakes and stuff
#here we allow it to not be found
def TGEGetObject(objname):
    try:
        x=TGEObject("objname")
    except:
        return None
    
    return x
    
#WE ARE USING THE INSPECT MODULE... IF YOU MOVE YOUR FILES YOU MUST DELETE .pyc file as 
#path info is embedded in them!  I could probably fix this by going backwards
#and ignorning the fullpath beginning
def TGEExec(filename):
    if filename[0:2]=='./':
        srcfile=inspect.stack()[1][1]
        filename = filename.replace('\\','/')
        srcfile = srcfile.replace('\\','/').rsplit('/',1)[0]
        #we need to strip the .py out.. should really learn re
        #  - is this still necessary?
        
        wd=TGECall("PyGetWorkingDirectory")
        
        filename = '%s/%s'%(srcfile,filename[2:])
        
        #we now have a fully qualified filename c:/torque/example/arpg/gui... etc... we need to 
        #make it fit into the TGE file constraint of only seeing files with in certain tree (security)
        
        modpaths = TGECall("getModPaths").split(";")
        
        for path in modpaths:
            #we need to find the last instance of /path/ in then truncate up to that point
            
            spath = wd+'/'+path+'/'

            index = filename.find(spath)
            if index != -1:
                filename=path+'/'+filename[index+len(spath):]
                break
           
    TGECall("exec",filename)
    
    
    
#sole entry point for TGE->Python
def TGECallback(selfid,namespace,functionname,args):
    return gTGEManager.callback(selfid,namespace,functionname,args)

#shortcut
def TGEGameRunning():
    b=TGEGetGlobal("$Game::Running")
    if b==None:
        return False
    
    b=int(b)
    if b==0:
        return False
    return True
    
        
gTGEManager=TGEManager()      
        
    
    
