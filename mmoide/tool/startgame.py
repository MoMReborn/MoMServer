import sys,os,string,shutil
import os.path
import re
import wx
import wx.lib.docview
import MessageService

IGNORE = []

IGNOREEXT = ['.db','.ms3d','.pyc','.max','.txt','.dso','.tmp','.log',
'.ilk','.pyd','.prof','.pyw','.bat','.sh','.html','.lnk','.rec','.3ds',
'.qkm','.qrk',".ds_store",".dll",".so",".xls",".xcf",".map",".bak",".pdb",".idb"]

FILES = []

KEEP = []

PROGRESS = None

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
            
            for x in dirwalk(fullpath):  # recurse into subdir
                yield x
        else:
            root,ext = os.path.splitext(fullpath)
            path,file = os.path.split(fullpath)
            if ext.lower() in IGNOREEXT and file not in KEEP:
                continue
            #if fullpath in SKIP:
            #    continue
            yield fullpath
    
CONFIGTEXT = """[Game Settings]
Game Name = %s
Game Root = %s
Master IP = 127.0.0.1
Master Port = 2007
GMServer IP = 127.0.0.1
GMServer PORT = 1998
"""
    
    
def SaveConfig(project):
    model = project.GetModel()
    text = CONFIGTEXT%(model.gameName,model.gameRoot)
    base,ext = os.path.splitext(project.GetFilename())
    base+=".cfg"
    f = file(base,"w")
    f.write(text)
    f.close()


def AddCoreModules(project):
    
    PROGRESS_COUNTER = 0
    
    valid = (".py",".cs")
    
    STUFF = list(dirwalk('./mud'))
    
    pdict = {}
    
    for dst in STUFF:
        dst = dst[2:]
        fname,ext=os.path.splitext(dst)
        if ext.lower() not in valid:
            continue
        
        base = os.path.dirname(dst)
        
        if not pdict.has_key(base):
            pdict[base]=[]
            
        pdict[base].append(dst)
        
    pview = project.GetFirstView()
    
    if pview:
        pview._treeCtrl.Freeze()

    
    bases = pdict.keys()
    bases.sort()
    for base in bases:
        files = pdict[base]
        files.sort()
        project.AddFiles(files,base)
        PROGRESS.Update(PROGRESS_COUNTER, base)
        PROGRESS_COUNTER+=1
        PROGRESS_COUNTER%=100


        
    if pview:
        try:
            pview._treeCtrl.CollapseAll()
        except:
            pass
        
        pview._treeCtrl.Thaw()


    
def StartGame(gameroot,project,progress):
    
    global PROGRESS
    
    PROGRESS = progress
    PROGRESS_COUNTER = 0
 
    valid = (".py",".cs")
 
    pdict = {}
    
    messageService = wx.GetApp().GetService(MessageService.MessageService)
    messageService.ShowWindow()

    view = messageService.GetView()
    if view:
        wx.GetApp().GetTopWindow().SetCursor(wx.StockCursor(wx.CURSOR_WAIT))
        view.ClearLines()
        view.AddLines("Starting new game\n\n")


    STUFF = list(dirwalk('./starter.mmo'))

    
    assert 'starter.mmo' not in gameroot
    assert 'minions.of.mirth' not in gameroot
    #assert not os.path.exists(gameroot)
    
    pfiles = []
    for src in STUFF:
        dst = src.replace("starter.mmo",gameroot)

        try:
            os.makedirs(os.path.dirname(dst))
        except OSError:
            pass  # dir exists, ignore error
        if view:
            view.AddLines("copying %s\n"%src)
        shutil.copyfile(src,dst)
        
        PROGRESS.Update(PROGRESS_COUNTER, dst)
        PROGRESS_COUNTER+=.25
        PROGRESS_COUNTER%=100
        
        pfiles.append(dst)
        
    f = file("%s/packaging/content.py"%gameroot,"r")
    s = f.read()
    f.close()
    s = s.replace("starter.mmo",gameroot)
        
    f = file("%s/packaging/content.py"%gameroot,"w")
    f.write(s)
    f.close()
    
    project.AddFiles(["serverconfig/server.cfg"],"config")
    
    AddCoreModules(project)

    for dst in pfiles:
        dst = dst[2:]
        fname,ext=os.path.splitext(dst)
        if ext.lower() not in valid:
            continue
        
        base = os.path.dirname(dst)
        
        if not pdict.has_key(base):
            pdict[base]=[]
            
        pdict[base].append(dst)
        
    pview = project.GetFirstView()
    
    if pview:
        pview._treeCtrl.Freeze()
    
    bases = pdict.keys()
    bases.sort()
    
    for base in bases:
        files = pdict[base]
        files.sort()
        project.AddFiles(files,base)
        PROGRESS.Update(PROGRESS_COUNTER, base)
        PROGRESS_COUNTER+=1
        PROGRESS_COUNTER%=100
        
    if pview:
        try:
            pview._treeCtrl.CollapseAll()
        except:
            pass
        
        pview._treeCtrl.Thaw()
        
    
        
    SaveConfig(project)
    
    project.OnSaveDocument(project.GetFilename())
    
    if view:
        view.AddLines("\n\nNew game started.\n")
        wx.GetApp().GetTopWindow().SetCursor(wx.StockCursor(wx.CURSOR_DEFAULT))


