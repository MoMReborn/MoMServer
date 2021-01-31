# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
from skillinfo import GetSkillInfo
from macro import Macro,MacroLine



MACROEDITOR = None



class MacroEditor:
    def __init__(self):
        self.charIndex = -1
        self.page = -1
        self.slot = -1
        self.icon = ""
        
        self.macroClipboard = None
        
        hotkeyList = ("None","1","2","3","4","5","6","7","8","9","0","F7","F8","F9","F10","F11","F12")
        
        self.guiName = TGEObject('CM_NAME')
        self.guiToolTip = TGEObject('CM_TOOLTIP')
        self.guiWaitAll = TGEObject('CM_WAITALL')
        self.guiHotkey = TGEObject('CM_HOTKEY')
        self.guiHotkey.clear()
        for index,hotkey in enumerate(hotkeyList):
            self.guiHotkey.add(hotkey,index)
        self.guiIconButton = TGEObject('CM_ICON')
        self.guiLines = dict()
        self.guiDelays = dict()
        self.guiMandatory = dict()
        for indexA,indexB in zip(xrange(10),xrange(1,11)):
            self.guiLines[indexA] = TGEObject('CM_LINE%i'%indexB)
            self.guiDelays[indexA] = TGEObject('CM_DELAY%i'%indexB)
            self.guiMandatory[indexA] = TGEObject('CM_MANDATORY%i'%indexB)
        self.guiManualDelay = TGEObject('CM_MANUALDELAY')
    
    
    def openMacroEditor(self,charIndex,page,slot,macro=None):
        self.charIndex = charIndex
        self.page = page
        self.slot = slot
        if macro:
            self.pasteMacro(macro)
        else:
            self.clearMacro()
        TGEEval("Canvas.pushDialog(MacroEditorWnd);")
    
    
    def createMacro(self):
        newMacro = Macro(self.charIndex,self.page,self.slot)
        newMacro.name = self.guiName.getValue()
        newMacro.description = self.guiToolTip.getValue()
        hotkey = self.guiHotkey.getValue()
        if hotkey == 'None':
            newMacro.hotkey = ''
        else:
            newMacro.hotkey = hotkey
        newMacro.icon = self.icon
        newMacro.waitAll = int(self.guiWaitAll.getValue()) == 1
        try:
            manualDelay = int(self.guiManualDelay.getValue)
            if manualDelay < 0:
                manualDelay = 0
        except:
            manualDelay = 0
        newMacro.manualDelay = manualDelay
        
        for lineIndex in xrange(10):
            lineCommand = self.guiLines[lineIndex].getValue().lstrip().rstrip()
            mandatory = int(self.guiMandatory[lineIndex].getValue()) == 1
            try:
                lineDelay = int(self.guiDelays[lineIndex].getValue())
                if lineDelay < 0:
                    lineDelay = 0
            except:
                lineDelay = 0
            if not lineCommand and not lineDelay:
                continue
            newMacroLine = MacroLine(lineCommand,mandatory,lineDelay)
            newMacro.insertMacroLine(lineIndex,newMacroLine)
        
        if newMacro.macroLineNum == 0:
            del newMacro
            return None
        
        return newMacro
    
    
    def clearMacro(self):
        self.icon = ""
        
        self.guiName.setText("")
        self.guiToolTip.setText("")
        self.guiHotkey.setSelected(0)
        self.guiIconButton.setBitmap("")
        self.guiWaitAll.setValue(0)
        self.guiManualDelay.setText("0")
        
        for index in xrange(10):
            self.guiLines[index].setText("")
            self.guiMandatory[index].setValue(0)
            self.guiDelays[index].setText("0")
    
    
    def saveMacro(self):
        from macro import MACROMASTER
        newMacro = self.createMacro()
        MACROMASTER.insertMacro(self.charIndex,self.page,self.slot,newMacro)
        TGEEval("canvas.popDialog(MacroEditorWnd);")
    
    
    def copyMacro(self):
        newMacro = self.createMacro()
        self.macroClipboard = newMacro
        from macro import CURSORMACRO
        if newMacro:
            CURSORMACRO.setMacro('CUSTOMMACRO',newMacro)
        else:
            CURSORMACRO.clear()
    
    
    def pasteMacro(self,macro=None):
        if not macro:
            macro = self.macroClipboard
        if macro:
            self.clearMacro()
            self.guiName.setText(macro.name)
            self.guiToolTip.setText(macro.description)
            if macro.hotkey:
                self.guiHotkey.setText(macro.hotkey)
            self.chooseIcon(macro.icon,True)
            self.guiWaitAll.setValue(macro.waitAll)
            self.guiManualDelay.setText(str(macro.manualDelay))
            for lineIndex,macroLine in macro.macroLines.iteritems():
                self.guiLines[lineIndex].setText(macroLine.command)
                self.guiMandatory[lineIndex].setValue(macroLine.mandatory)
                self.guiDelays[lineIndex].setText(str(macroLine.delayAfter))
    
    
    def chooseIcon(self,chosen,fromMacro=False):
        if chosen:
            icon = self.icon = chosen
            if icon.startswith("SPELLICON_"):
                split = icon.split("_")
                index = int(split[2])
                u0 = (float(index % 6) * 40.0) / 256.0
                v0 = (float(index / 6) * 40.0) / 256.0
                u1 = 40.0 / 256.0
                v1 = 40.0 / 256.0
                
                self.guiIconButton.setBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
            else:
                if not fromMacro:
                    self.icon = 'icons/%s'%self.icon
                self.guiIconButton.setBitmap("~/data/ui/%s"%self.icon)
        else:
            self.guiIconButton.setBitmap("")
    
    
    def OnMacroChooseIcon(self):
        from chooseIconWnd import SetChooseIconCallback
        SetChooseIconCallback(self.chooseIcon)
        TGEEval("canvas.pushDialog(ChooseIconWnd);")
    
    
    def OnCustomMacroLine(self,args):
        try:
            from macro import CURSORMACRO
            from partyWnd import PARTYWND
            
            lineIndex = int(args[1])
            macroLine = self.guiLines[lineIndex]
            
            # Check if there's some macro in the cursor.
            macroType = CURSORMACRO.macroType
            macroInfo = CURSORMACRO.macroInfo
            if macroType:
                # Get the linked character info if available.
                if CURSORMACRO.charIndex != -1:
                    charInfo = PARTYWND.charInfos[CURSORMACRO.charIndex]
                # Otherwise get character info for macro owner.
                else:
                    charInfo = PARTYWND.charInfos[self.charIndex]
                
                newCommand = ""
                
                # Fill current command line with cursor macro content according to type.
                if macroType == 'INV':
                    pass #todo, actually needed?
                elif macroType == 'SKILL':
                    skillInfo = GetSkillInfo(macroInfo)
                    newCommand = '/skill %s'%skillInfo.name
                elif macroType == 'SPELL':
                    spell = charInfo.SPELLS.get(macroInfo)
                    if spell:
                        spellInfo = spell.SPELLINFO
                        newCommand = '/cast %s'%spellInfo.BASENAME
                elif macroType == 'CMD':
                    newCommand = macroInfo.command
                
                # If we actually have to insert a command...
                if newCommand:
                    # Check for valid charIndex in cursor macro.
                    if CURSORMACRO.charIndex != -1:
                        # If the character indexes don't fit, need to edit in
                        #  a retarget command.
                        if self.charIndex != CURSORMACRO.charIndex:
                            charName = charInfo.NAME
                            newCommand = '*%s* %s'%(charName,newCommand)
                    # Set text of the command entry to cursor macro content.
                    macroLine.setText(newCommand)
                
                # Clear the macro in the cursor.
                CURSORMACRO.clear()
            
            # Ok, no cursor macro, but can still have an item in cursor.
            elif PARTYWND.mind.cursorItem:
                cursorItem = PARTYWND.mind.cursorItem
                # If the item is a ranged weapon, automatically create a ranged attack macro.
                if RPG_SLOT_RANGED in cursorItem.SLOTS:
                    defaultCommand = GetDefaultCommand('Ranged Attack')
                    macroLine.setText(defaultCommand.command)
                else:
                    macroLine.setText('/useitem %s'%cursorItem.NAME)
        # Exception if we got wrong arguments supplied.
        except:
            import traceback
            traceback.print_exc()
            pass



def PyExec():
    global MACROEDITOR
    MACROEDITOR = MacroEditor()
    
    TGEExport(MACROEDITOR.OnMacroChooseIcon,"Py","OnMacroChooseIcon","desc",1,1)
    TGEExport(MACROEDITOR.saveMacro,"Py","OnCustomMacroSave","desc",1,1)
    TGEExport(MACROEDITOR.clearMacro,"Py","OnCustomMacroClear","desc",1,1)
    TGEExport(MACROEDITOR.copyMacro,"Py","OnCustomMacroCopy","desc",1,1)
    TGEExport(MACROEDITOR.pasteMacro,"Py","OnCustomMacroPaste","desc",1,1)
    TGEExport(MACROEDITOR.OnCustomMacroLine,"Py","OnCustomMacroLine","desc",2,2)

