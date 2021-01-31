# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *

#Py::OnPlaceVault();Py::OnPlaceVault();
#Py::OnRemoveVault();
#Py::OnPrivateVault();

def VItemSort(a,b):
    if a[1] > b[1]:
        return 1
    if a[1] < b[1]:
        return -1
    return 0

VAULTWND = None
class VaultWnd:
    def __init__(self):
        self.vaultWnd       = TGEObject("VaultWnd_Window")
        self.itemScroll     = TGEObject("VaultWnd_ItemScroll")
        self.itemList       = TGEObject("VaultWnd_ItemTextList")
        self.availableSlots = TGEObject("VaultWnd_AvailableSlots")
        self.availableSlots.SetValue("Available Slots: %u" %(RPG_PRIVATE_VAULT_LIMIT))
        self.cinfo = None
        self.lastVaultItems = []
        self.sortedItems = []
    
    def onRemoveVault(self):
        from mud.client.playermind import PLAYERMIND
        if len(self.sortedItems)<=0:
            return
        index = int(self.itemList.getSelectedId())
        if index > len(self.sortedItems):
            return
        
        id = self.sortedItems[index][0]
        
        #self.cinfo.VAULTITEMS.remove(self.sortedItems[index])
        #self.setFromCharacterInfo(self,self.cinfo)
        
        PLAYERMIND.perspective.callRemote("PlayerAvatar","onRemoveVault",id)
        
    def setFromCharacterInfo(self,cinfo):

        self.cinfo = cinfo
        self.vaultWnd.setText(cinfo.NAME+"'s Private Vault")
        
        #previndex = int(self.itemList.getSelectedId())
        pos = self.itemScroll.childRelPos.split(" ")
        
        
        if self.lastVaultItems != cinfo.VAULTITEMS:
            
            self.lastVaultItems = cinfo.VAULTITEMS
            self.sortedItems = self.lastVaultItems[:]
            self.sortedItems.sort(VItemSort)
            
            tc = self.itemList
            tc.setVisible(False)
            tc.clear()
            i=0

            for id,name,count in self.sortedItems:
                if count:
                    self.itemList.addRow(i,"%s\t%i"%(name,count))
                else:
                    self.itemList.addRow(i,"%s\t"%(name))
                    
                i+=1
    
            #if previndex!=0 and len(self.sortedItems)>=1:
            #    if previndex >= len(self.sortedItems):
            #        previndex = len(self.sortedItems)-1
            #    tc.setSelectedRow(previndex)
            #    tc.scrollVisible(previndex)
            tc.setActive(True)
            tc.setVisible(True)
            
            self.availableSlots.SetValue("Available Slots: %u" %(RPG_PRIVATE_VAULT_LIMIT - i ))
        
        self.itemScroll.scrollRectVisible(pos[0],pos[1],1,444)
        
    
def OnPrivateVault():
    vw = TGEObject("VaultWnd_Window")
    
    if not int(vw.isAwake()):
        TGEEval('Canvas.pushDialog("VaultWnd");')
    else:
        TGEEval('Canvas.popDialog("VaultWnd");')

def OnPlaceVault():
    #yuck
    from mud.client.playermind import PLAYERMIND
    item = PLAYERMIND.cursorItem
    if not item:
        return
    if item.FLAGS & RPG_ITEM_ETHEREAL:
        TGEEval("""MessageBoxOK("Invalid item for vault", "Ethereal classified items cannot be placed in the vault.");""")
        return
    if item.FLAGS & RPG_ITEM_WORLDUNIQUE:
        TGEEval("""MessageBoxOK("Invalid item for vault", "Items unique to the world cannot be placed in the vault.");""")
        return
    PLAYERMIND.perspective.callRemote("PlayerAvatar","onPlaceVault")

def OnRemoveVault():
    #yuck
    from mud.client.playermind import PLAYERMIND
    if PLAYERMIND.cursorItem:
        from tomeGui import TomeGui
        TomeGui.instance.receiveGameText(RPG_MSG_GAME_DENIED,"Please remove the item in your cursor first!\\n")
        return
    VAULTWND.onRemoveVault()
    


def PyExec():
    global VAULTWND
    VAULTWND = VaultWnd()
    TGEExport(OnPrivateVault,"Py","OnPrivateVault","desc",1,1)
    TGEExport(OnPlaceVault,"Py","OnPlaceVault","desc",1,1)
    TGEExport(OnRemoveVault,"Py","OnRemoveVault","desc",1,1)