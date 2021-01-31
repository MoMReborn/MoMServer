# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from skillinfo import GetSkillInfo



class DefaultCommand:
    def __init__(self,name,tooltip,command,icon=""):
        self.name = name
        self.tooltip = tooltip
        self.command = command
        self.icon = icon



# Dictionary of default commands.
DEFAULTCOMMANDS = {}
DEFAULTCOMMANDS['Attack'] = DefaultCommand('Attack','Toggles Auto-Attack on and off','/attack toggle','standardmeleeupgrade')
DEFAULTCOMMANDS['PetAtk'] = DefaultCommand('PetAtk','Order your pet to attack','/pet attack')
DEFAULTCOMMANDS['PetSd'] = DefaultCommand('PetSd','Order your pet to stand down','/pet standdown')
DEFAULTCOMMANDS['PetFlw'] = DefaultCommand('PetFlw','Order your pet to follow you','/pet followme')
DEFAULTCOMMANDS['PetStay'] = DefaultCommand('PetStay','Order your pet to stay','/pet stay')
DEFAULTCOMMANDS['PetDis'] = DefaultCommand('PetDis','Dismiss your pet','/pet dismiss')
DEFAULTCOMMANDS['Stop Cast'] = DefaultCommand('Stop Cast','Stop casting your current spell','/stopcast','SPELLICON_3_17')
DEFAULTCOMMANDS['Ranged Attack'] = DefaultCommand('Ranged Attack','Perform a ranged attack','/rangedattack','SPELLICON_4_19')


def GetDefaultCommand(cmd):
    defaultCommand = DEFAULTCOMMANDS.get(cmd)
    # If it's not one of the default commands here,
    #  check if it's a skill in the skillInfo dictionary.
    # If present there, create a DefaultCommand instance from it and return that.
    if not defaultCommand:
        skillInfo = GetSkillInfo(cmd,False)
        if skillInfo:
            defaultCommand = DefaultCommand(cmd,skillInfo.name,'/skill %s'%cmd,skillInfo.icon)
    return defaultCommand


def GetDefaultCommandAsMacro(cmd,charIndex,page,slot):
    from macro import Macro,MacroLine
    
    # Initialize the default macro to None,
    #  in case we don't find the desired command.
    defaultMacro = None
    
    # Try to get the default command from the local dictionary.
    defaultCommand = DEFAULTCOMMANDS.get(cmd)
    # If it's not one of the default commands here,
    #  check if it's a skill in the skillInfo dictionary
    #  and create a macro from that.
    if not defaultCommand:
        skillInfo = GetSkillInfo(cmd,False)
        if skillInfo:
            defaultMacro = Macro(charIndex,page,slot)
            defaultMacro.name = cmd
            defaultMacro.icon = skillInfo.icon
            if not defaultMacro.icon.startswith('SPELLICON_'):
                defaultMacro.icon = 'icons/%s'%defaultMacro.icon
            defaultMacro.description = skillInfo.name
            defaultMacro.appendMacroLine(MacroLine(command='/skill %s'%cmd))
    else:
        defaultMacro = Macro(charIndex,page,slot)
        defaultMacro.name = defaultCommand.name
        defaultMacro.icon = defaultCommand.icon
        if not defaultMacro.icon.startswith('SPELLICON_'):
            defaultMacro.icon = 'icons/%s'%defaultMacro.icon
        defaultMacro.description = defaultCommand.tooltip
        defaultMacro.appendMacroLine(MacroLine(command=defaultCommand.command))
    
    # Return the default macro.
    return defaultMacro



DEFAULTCOMMANDWND = None



class DefaultCommandWnd:
    def __init__(self):
        self.currentPage = 0
        self.prevButton = TGEObject('DefaultCommands_Prev')
        self.nextButton = TGEObject('DefaultCommands_Next')
        self.commandButtons = dict()
        for x in xrange(0,10):
            button = TGEObject("DefaultCommand%i"%x)
            self.commandButtons[x] = button
            button.visible = False
        
        # Create a lookup dictionary for the default commands by index.
        self.defaultCommands = dict((i,name) for i,name in enumerate(sorted(DEFAULTCOMMANDS.iterkeys())))
        
        self.setPage(self.currentPage)
    
    
    def setPage(self,page):
        self.currentPage = page
        
        # Enable page turn buttons if needed.
        if page > 0:
            self.prevButton.setActive(True)
        else:
            self.prevButton.setActive(False)
        if self.defaultCommands.get((page + 1) * 10):
            self.nextButton.setActive(True)
        else:
            self.nextButton.setActive(False)
        
        # Fill the 10 buttons for default commands with content.
        for x in xrange(0,10):
            commandIndex = x + page * 10
            try:
                defaultCommand = DEFAULTCOMMANDS[self.defaultCommands[commandIndex]]
                if defaultCommand.icon:
                    if defaultCommand.icon.startswith("SPELLICON_"):
                        split = defaultCommand.icon.split("_")
                        index = int(split[2])
                        u0 = (float(index % 6) * 40.0) / 256.0
                        v0 = (float(index / 6) * 40.0) / 256.0
                        u1 = 40.0 / 256.0
                        v1 = 40.0 / 256.0
                        
                        self.commandButtons[x].setBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
                    else:
                        self.commandButtons[x].setBitmap("~/data/ui/icons/%s"%defaultCommand.icon)
                    self.commandButtons[x].setText("")
                else:
                    self.commandButtons[x].setText(defaultCommand.name)
                self.commandButtons[x].tooltip = defaultCommand.tooltip
                self.commandButtons[x].visible = True
            except KeyError:
                self.commandButtons[x].visible = False
    
    
    def OnDefaultCommandPrev(self):
        if self.currentPage > 0:
            self.setPage(self.currentPage - 1)
    
    
    def OnDefaultCommandNext(self):
        newPage = self.currentPage + 1
        if self.defaultCommands.get(newPage * 10):
            self.setPage(newPage)
    
    def OnDefaultCommand(self,args):
        hitIndex = int(args[1])
        commandIndex = self.currentPage * 10 + hitIndex
        defaultCommand = self.defaultCommands.get(commandIndex)
        if defaultCommand:
            button = self.commandButtons[hitIndex]
            from macro import CURSORMACRO
            CURSORMACRO.setMacro("CMD",DEFAULTCOMMANDS[defaultCommand],button)



def PyExec():
    global DEFAULTCOMMANDWND
    DEFAULTCOMMANDWND = DefaultCommandWnd()
    
    TGEExport(DEFAULTCOMMANDWND.OnDefaultCommand,"Py","OnDefaultCommand","desc",2,2)
    TGEExport(DEFAULTCOMMANDWND.OnDefaultCommandNext,"Py","OnDefaultCommandNext","desc",1,1)
    TGEExport(DEFAULTCOMMANDWND.OnDefaultCommandPrev,"Py","OnDefaultCommandPrev","desc",1,1)
