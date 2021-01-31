# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport



def DisplayPatchInfo():
    try:
        f = file('./readme.txt','r')
        text = f.read()
        
        text = text.replace('\r',"\\r")
        text = text.replace('\n',"\\n") #valid quote
        text = text.replace('\a',"\\a") #valid quote
        text = text.replace('"','\\"') #invalid quote
        f.close()
    
        text = text[:4000]+ "  *** SNIP *** see readme.txt if you'd like to read more"
    
    
        TGEEval('patchinfownd_text.setText("%s");'%text)
    
        TGECall("CloseMessagePopup")
        TGEEval("canvas.setContent(MultiplayerGui);")
        TGEEval("canvas.pushDialog(PatchInfoWnd);")
        
    except:
        pass
    
def PyExec():
    pass
    