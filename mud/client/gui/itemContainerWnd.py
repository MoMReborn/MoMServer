# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *

from tomeGui import TomeGui
receiveGameText = TomeGui.instance.receiveGameText



TEXT_HEADER = """<font:Arial Bold:14><just:center><shadow:1:1><shadowcolor:000000>"""



class ItemContainerWnd(object):
    instance = None
    
    
    def __new__(cl, *p, **k):
        if not ItemContainerWnd.instance:
            ItemContainerWnd.instance = object.__new__(cl, *p, **k)
        return ItemContainerWnd.instance
    
    
    def __init__(self):
        self.container = None
        self.content = {}
        self.lastSelectedID = -1
    
    
    @staticmethod
    def getInstance(self):
        return ItemContainerWnd.instance
    
    
    def initTGEObjects(self):
        self.window = TGEObject("ItemContainerWnd")
        self.pane = TGEObject("ItemContainerWnd_Window")
        self.tgeContentCount = TGEObject("ItemContainerWnd_ContentCount")
        self.tgeContentInfoPic = TGEObject("ItemContainerWnd_ContentInfoPic")
        self.tgeContentInfoText = TGEObject("ItemContainerWnd_ContentInfoText")
        self.tgeContentInfoFlags = TGEObject("ItemContainerWnd_ContentInfoFlags")
        self.tgeContentInfoName = TGEObject("ItemContainerWnd_ContentInfoName")
        self.tgeContentList = TGEObject("ItemContainerWnd_ContentList")
    
    
    # Return a tuple (found,itemGhost), found being true
    #  if the mouse was indeed over an item entry and itemGhost
    #  being the item ghost of the item the mouse is hovering
    #  over or None.
    def getMouseOver(self):
        pass
        """
        if int(self.window.isAwake()):
            for slot,button in self.lootButtons.iteritems():
                if int(button.mouseOver):
                    return (True,self.loot.get(slot,None))
        return(False,None)
        """
    
    
    def openContainer(self, container):
        if not container.CONTAINERSIZE:
            return
        
        # Store the container we're gonna display.
        self.container = container
        
        # Set the window name to the container name.
        self.pane.setText(str(container.NAME))
        
        # Get the amount of items in the container.
        contentCount = len(container.CONTENT)
        
        # Update the content count.
        self.tgeContentCount.setText("%sStorage used: %i / %i"%(TEXT_HEADER,contentCount,container.CONTAINERSIZE))
        
        # Clear the previous content list.
        self.tgeContentList.clear()
        
        # Reset last selection.
        self.lastSelectedID = -1
        
        # Build the new content list.
        self.content.clear()
        if contentCount:
            
            # Run through all contained items and add them to the list.
            for i,citem in enumerate(container.CONTENT):
                self.content[i] = citem
                self.tgeContentList.addRow(i,"%i\t%s"%(citem.STACKCOUNT,citem.NAME))
            
            # Sort the list entries by name.
            self.tgeContentList.sort(1)
            
            # Select the first item in the list.
            self.tgeContentList.setSelectedRow(0)
            self.tgeContentList.scrollVisible(0)
        
        # If there's no content, make sure to reset the content information.
        else:
            self.tgeContentInfoName.setText("")
            self.tgeContentInfoFlags.setText("")
            self.tgeContentInfoText.setText("")
            self.tgeContentInfoPic.setBitmap("")
        
        # Make the item container window visible if it isn't already.
        if not int(self.window.isAwake()):
            TGEEval("canvas.pushDialog(ItemContainerWnd);")
    
    
    def closeContainer(self):
        # Reset the window bound container so the window doesn't reopen
        #  when contents get updated with a closed container window.
        self.container = None
        
        # Close the window.
        TGEEval("canvas.popDialog(ItemContainerWnd);")
    
    
    def onSelect(self):
        # Get the selected entry id.
        selectedID = int(self.tgeContentList.getSelectedId())
        
        # If the selection didn't change, return.
        if selectedID == self.lastSelectedID:
            return
        
        # Update the last selected id.
        self.lastSelectedID = selectedID
        
        # Get the selected item ghost.
        try:
            ghost = self.content[selectedID]
        except KeyError:
            self.tgeContentInfoName.setText("")
            self.tgeContentInfoFlags.setText("")
            self.tgeContentInfoText.setText("")
            self.tgeContentInfoPic.setBitmap("")
            return
        
        # Update content information.
        # Need to use TGEEval because of color coding.
        # Update the item name.
        TGEEval('ItemContainerWnd_ContentInfoName.setText("%s%s");'%(TEXT_HEADER,ghost.NAME))
        # Update the item flags.
        text = ' '.join(r'\cp\c2%s\co '%ftext for f,ftext in RPG_ITEM_FLAG_TEXT.iteritems() if (f&ghost.FLAGS))
        TGEEval('ItemContainerWnd_ContentInfoFlags.setText("%s%s");'%(TEXT_HEADER,text))
        # Update the item description.
        text = ""
        if ghost.SPELLINFO:
            text = r'\n\n%s'%ghost.SPELLINFO.text
        TGEEval('ItemContainerWnd_ContentInfoText.setText("%s%s%s");'%(TEXT_HEADER,ghost.text,text))
        # Update the item icon.
        self.tgeContentInfoPic.setBitmap("~/data/ui/items/%s/0_0_0"%ghost.BITMAP)
    
    
    def onInsert(self):
        container = self.container
        
        # If we have no valid container assigned, skip.
        if not container:
            return
        
        from mud.client.playermind import PLAYERMIND
        
        # Check if there's something on the cursor and skip if not.
        if not PLAYERMIND.cursorItem:
            return
        
        # Forbid insertion of a container into another container.
        if PLAYERMIND.cursorItem.CONTAINERSIZE:
            return
        
        # Call for item insertion on the server.
        PLAYERMIND.perspective.callRemote("PlayerAvatar","insertItem",container.SLOT,container.OWNERCHARID)
    
    
    def onExtract(self):
        # Get the selected entry id.
        selectedID = int(self.tgeContentList.getSelectedId())
        
        # Get the selected item ghost.
        try:
            ghost = self.content[selectedID]
        except KeyError:
            return
        
        from mud.client.playermind import PLAYERMIND
        
        # Check if there's something on the cursor and skip if so.
        if PLAYERMIND.cursorItem:
            receiveGameText(RPG_MSG_GAME_DENIED,"Please put down the item in your cursor first.\\n")
            return
        
        # Call for item extraction on the server.
        container = self.container
        PLAYERMIND.perspective.callRemote("PlayerAvatar","extractItem",container.SLOT,container.OWNERCHARID,selectedID)



ItemContainerWnd()



def PyExec():
    ITEMCONTAINERWND = ItemContainerWnd.instance
    ITEMCONTAINERWND.initTGEObjects()
    
    TGEExport(ITEMCONTAINERWND.closeContainer,"Py","OnItemContainerClose","desc",1,1)
    
    TGEExport(ITEMCONTAINERWND.onSelect,"Py","OnItemContainerSelect","desc",1,1)
    
    TGEExport(ITEMCONTAINERWND.onInsert,"Py","OnItemContainerInsert","desc",1,1)
    TGEExport(ITEMCONTAINERWND.onExtract,"Py","OnItemContainerExtract","desc",1,1)

