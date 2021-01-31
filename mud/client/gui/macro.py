# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


# todo, eventually change item macro recovery from polling to calling for better performance?
from tgenative import *
from mud.tgepython.console import TGEExport
from twisted.internet import reactor
from mud.world.defines import *
from mud.gamesettings import *
from defaultCommandsWnd import GetDefaultCommand
from skillinfo import GetSkillInfo
from mud.client.playermind import PyDoCommand
from macroWnd import MacroWnd
MacroWnd = MacroWnd.instance
from time import time
from copy import deepcopy
from operator import itemgetter



MACROMASTER = None
CURSORMACRO = None
(MACRO_IDLE,MACRO_RUNNING,MACRO_RECOVERING) = range(3)



class CursorMacro:
    def __init__(self):
        self.macroType = None
        self.macroInfo = None
        self.charIndex = -1
        self.clearingTimer = None
        self.cursor = TGEObject("DefaultCursor")
    
    
    def clear(self):
        if not self.clearingTimer:
            return
        try:
            self.clearingTimer.cancel()
        except:
            pass
        self.clearingTimer = None
        self.setMacro(None,None)
        MACROMASTER.showEmptySlots(False)
    
    
    def setMacro(self,macroType,macroInfo,button=None,charIndex=-1):
        cursor = self.cursor
        cursor.bitmapName = ""
        cursor.u0 = cursor.v0 = 0
        cursor.u1 = cursor.v1 = 1
        cursor.sizeX = -1
        cursor.sizeY = -1
        
        if self.clearingTimer:
            try:
                self.clearingTimer.cancel()
            except:
                pass
            self.clearingTimer = None
        
        if macroType:
            self.clearingTimer = reactor.callLater(14,self.clear)
            MACROMASTER.showEmptySlots(True)
        
        self.macroType,self.macroInfo,self.charIndex = macroType,macroInfo,charIndex
        
        if button:
            cursor.cursorControl = button
        else:
            cursor.cursorControl = ""



class MacroLine:
    def __init__(self,command="",mandatory=True,delayAfter=0):
        self.command = command
        self.mandatory = mandatory
        self.delayAfter = delayAfter
        
        self.skill = ""
        self.spell = ""
        self.item = ""
        self.retarget = ""
        self.realCommand = ""
    
    
    # Use this function to check for this macro lines availability.
    # Returns True if the command can currently be executed.
    def checkAvailability(self,charIndex):
        from partyWnd import PARTYWND
        commandCharIndex = charIndex
        commandCharInfo = None
        
        # Check for a retarget command.
        if self.retarget:
            command = self.realCommand
            for charIndex,charInfo in PARTYWND.charInfos.iteritems():
                if charInfo.NAME.upper() == self.retarget:
                    commandCharIndex = charIndex
                    commandCharInfo = charInfo
                    break
            else:
                return True
        else:
            command = self.command
            commandCharInfo = PARTYWND.charInfos[commandCharIndex]
        
        if not command:
            return True
        
        # Now check for the availability of the command and return the result.
        return checkCommandAvailability(commandCharInfo,command)
    
    
    # Execute this macro line. Returns a tuple (executed,skipped).
    # If executed is True, the line has been executed normally.
    # If the command had to be skipped, skipped will be set to True.
    def execute(self,charIndex):
        from partyWnd import PARTYWND
        commandCharIndex = charIndex
        commandCharInfo = None
        
        # Check for a retarget command.
        if self.retarget:
            command = self.realCommand
            for charIndex,charInfo in PARTYWND.charInfos.iteritems():
                if charInfo.NAME.upper() == self.retarget:
                    commandCharIndex = charIndex
                    commandCharInfo = charInfo
                    break
            else:
                return (True,self.delayAfter==0)
        else:
            command = self.command
            commandCharInfo = PARTYWND.charInfos[commandCharIndex]
        
        # If there is nothing to process, return executed = True.
        # If this line does have a delay however, it can't be skipped.
        if not command:
            return (True,self.delayAfter==0)
        
        # Check for the availability of the command.
        available = checkCommandAvailability(commandCharInfo,command)
        
        # If the command was not available, check if this line is mandatory.
        if not available:
            if self.mandatory:
                return (False,False)
            else:
                return (False,True)
        
        # If the command is valid and available, execute it.
        if len(command) and command[0] == '/':
            PyDoCommand(['PyDoCommand',command],False,commandCharIndex)
        
        # Line got executed, return True,False.
        return (True,False)



class Macro:
    def __init__(self,charIndex,page,slot,name="",hotkey="",icon="",description="",waitAll=True,manualDelay=0):
        # Character index of character owning this macro.
        self.charIndex = charIndex
        # Page on which this macro can be found.
        self.page = page
        # Slot the macro occupies on current macro page.
        self.slot = slot
        # Name of the macro, displays on macro button.
        self.name = name
        # Macro hotkey, automatically assign according to slot
        #  if none provided.
        self.hotkey = hotkey
        if not self.hotkey:
            self.hotkey = str((slot + 1) % 10)
        # Macro icon to display in macro button.
        self.icon = icon
        # Macro tooltip to display on mouseover.
        self.description = description
        # If the macro should wait for all commands to recover, not just mandatory.
        self.waitAll = waitAll
        # To set manually a minimal delay until reuse is possible.
        self.manualDelay = manualDelay
        
        # Never manually modify the following variables.
        # These variables get used to keep track of Macro content.
        self.macroLines = dict()
        self.macroLineNextIndex = 0
        self.macroLineNum = 0
        self.skills = list()
        self.spells = list()
        self.items = list()
        self.hasAttack = 0
        self.hasRangedAttack = 0
        
        self.status = MACRO_IDLE
        self.activeLine = -1
        self.startTime = 0
        self.recoveryDelay = 0
        self.visible = False
        
        self.macroButton = TGEObject("MACROWND_MACRO%i_%i"%(charIndex,slot))
        self.appearanceAggressive = False  # Used for the attack macros.
        self.resetPulseTimer = None
    
    
    # Warning: appending macro lines should only be done during initialization.
    # After that, supply a new macro to the macro master instead.
    def appendMacroLine(self,macroLine):
        command = macroLine.command
        self.macroLines[self.macroLineNextIndex] = macroLine
        self.macroLineNextIndex += 1
        self.macroLineNum += 1
        
        try:
            # Check for a retarget command.
            if command[0] == '*':
                charName,command = command[1:].split('* ',1)
                command = command.lstrip()
                charName = charName.upper()
                macroLine.retarget = charName
                macroLine.realCommand = command
            
            # Extract skill, spell, item and attack commands.
            if command[0] == '/':
                args = command[1:].upper().split(' ',1)
                if len(args) > 1:
                    command,arg = args
                    arg = arg.lstrip()
                else:
                    command,arg = args[0],''
                
                if command == 'SKILL':
                    macroLine.skill = arg
                    self.skills.append(arg)
                elif command == 'CAST':
                    macroLine.spell = arg
                    self.spells.append(arg)
                elif command == 'USEITEM':
                    macroLine.item = arg
                    self.items.append(arg)
                elif command == 'ATTACK':
                    self.hasAttack += 1
                elif command == 'RANGEDATTACK':
                    self.hasRangedAttack += 1
        except IndexError:
            pass
    
    
    # Warning: appending macro lines should only be done during initialization.
    # After that, supply a new macro to the macro master instead.
    def appendMacroLines(self,lineIterable):
        for macroLine in lineIterable:
            command = macroLine.command
            self.macroLines[self.macroLineNextIndex] = macroLine
            self.macroLineNextIndex += 1
            self.macroLineNum += 1
            
            try:
                # Check for retarget command.
                if command[0] == '*':
                    charName,command = command[1:].split('* ',1)
                    command = command.lstrip()
                    charName = charName.upper()
                    macroLine.retarget = charName
                    macroLine.realCommand = command
                
                # Extract skill, spell, item and attack commands.
                if command[0] == '/':
                    args = command[1:].upper().split(' ',1)
                    if len(args) > 1:
                        command,arg = args
                        arg = arg.lstrip()
                    else:
                        command,arg = args[0],''
                    
                    if command == 'SKILL':
                        macroLine.skill = arg
                        self.skills.append(arg)
                    elif command == 'CAST':
                        macroLine.spell = arg
                        self.spells.append(arg)
                    elif command == 'USEITEM':
                        macroLine.item = arg
                        self.items.append(arg)
                    elif command == 'ATTACK':
                        self.hasAttack += 1
                    elif command == 'RANGEDATTACK':
                        self.hasRangedAttack += 1
            except IndexError:
                continue
    
    
    # Warning: inserting macro lines should only be done during initialization.
    # After that, supply a new macro to the macro master instead.
    def insertMacroLine(self,lineIndex,macroLine):
        # Update next line index if necessary.
        if lineIndex >= self.macroLineNextIndex:
            self.macroLineNextIndex = lineIndex + 1
        # Check if that index already holds a macro line.
        oldLine = self.macroLines.get(lineIndex)
        if oldLine:
            # If this old line uses any skill, spell or item, need to remove now.
            # Note that skills, spells and items are lists, therefore an item can
            #  be present multiple times. Removing is safe.
            if oldLine.skill:
                self.skills.remove(oldLine.skill)
            if oldLine.spell:
                self.spells.remove(oldLine.spell)
            if oldLine.item:
                self.items.remove(oldLine.item)
            # If the old macro line contained the attack command, need to decrement
            #  attack counter. Now it gets obvious why a counter was used.
            # (Yeah, I bet there are players which fill in the /attack macro line
            #  more than once in a single macro. Just to try if it breaks.)
            if oldLine.command.upper().find('/ATTACK') != -1:
                self.hasAttack -= 1
            # Same goes for ranged attack. Here it actually makes sense to use it
            #  more than once (fire next arrow as soon as ready).
            if oldLine.command.upper().find('/RANGEDATTACK') != -1:
                self.hasRangedAttack -= 1
            # Dispose of old line.
            del oldLine
        else:
            # If there's no previous line here, need to increment line count.
            self.macroLineNum += 1
        
        # Finally insert the new line at the desired place.
        self.macroLines[lineIndex] = macroLine
        
        command = macroLine.command
        try:
            # Check for retarget command.
            if command[0] == '*':
                charName,command = command[1:].split('* ',1)
                command = command.lstrip()
                charName = charName.upper()
                macroLine.retarget = charName
                macroLine.realCommand = command
            
            # Extract skill, spell, item and attack commands.
            if command[0] == '/':
                args = command[1:].upper().split(' ',1)
                if len(args) > 1:
                    command,arg = args
                    arg = arg.lstrip()
                else:
                    command,arg = args[0],''
                
                if command == 'SKILL':
                    macroLine.skill = arg
                    self.skills.append(arg)
                elif command == 'CAST':
                    macroLine.spell = arg
                    self.spells.append(arg)
                elif command == 'USEITEM':
                    macroLine.item = arg
                    self.items.append(arg)
                elif command == 'ATTACK':
                    self.hasAttack += 1
                elif command == 'RANGEDATTACK':
                    self.hasRangedAttack += 1
        except IndexError:
            pass
    
    
    def setVisibility(self,visible):
        if visible != self.visible:
            self.visible = visible
            
            # If this macro is now visible, update the TGEObject.
            if visible:
                macroButton = self.macroButton
                icon = self.icon
                if icon:
                    if icon.startswith("SPELLICON_"):
                        split = icon.split("_")
                        index = int(split[2])
                        u0 = (float(index % 6) * 40.0) / 256.0
                        v0 = (float(index / 6) * 40.0) / 256.0
                        u1 = 40.0 / 256.0
                        v1 = 40.0 / 256.0
                        
                        macroButton.setBitmapUV("~/data/ui/icons/spells0%s"%split[1],u0,v0,u1,v1)
                    else:
                        macroButton.setBitmap("~/data/ui/%s"%icon)
                else:
                    macroButton.setBitmap("")
                macroButton.setText(self.name)
                macroButton.hotKey = self.hotkey
                macroButton.tooltip = self.description
                
                # If appearanceAggressive is set to True, this macro contains an activated
                #  attack command and needs to override status appearance.
                if self.appearanceAggressive:
                    macroButton.pulseGreen = False
                    macroButton.pulseRed = True
                    macroButton.setValue(1)
                    macroButton.toggleLocked = False
                # If status is running, start pulsing red.
                elif self.status == MACRO_RUNNING:
                    macroButton.pulseGreen = False
                    macroButton.pulseRed = True
                    macroButton.setValue(1)
                    macroButton.toggleLocked = False
                # If this macro is recovering, deactivate the button.
                elif self.status == MACRO_RECOVERING:
                    macroButton.pulseGreen = False
                    macroButton.pulseRed = False
                    macroButton.setValue(1)
                    macroButton.toggleLocked = True
                # Otherwise, the macro awaits its next use, don't pulse red and activate.
                else:
                    macroButton.pulseGreen = False
                    macroButton.pulseRed = False
                    macroButton.setValue(0)
                    macroButton.toggleLocked = False
    
    
    # Resets the buttons pulsing if needed.
    def resetPulsing(self):
        if self.resetPulseTimer:
            try:
                self.resetPulseTimer.cancel()
            except:
                pass
            self.resetPulseTimer = None
        if self.visible:
            self.macroButton.pulseGreen = False
    
    
    # Macro.tick() handles one macro line and then
    #  returns a tuple with (finished,nextFireTime).
    def tick(self):
        finished = False
        
        # If the active line index is set to -1,
        #  we just started this macro. So increment
        #  the line index and get the starting time.
        if self.activeLine == -1:
            self.activeLine = 0
            self.startTime = time()
            self.status = MACRO_RUNNING
        
        # Try to execute exactly one line.
        done = False
        executed = False
        while not done:
            try:
                executed,skipped = self.macroLines[self.activeLine].execute(self.charIndex)
                if skipped:
                    self.activeLine += 1
                else:
                    done = True
            except KeyError:
                self.activeLine += 1
            if self.activeLine >= self.macroLineNextIndex:
                done = True
                finished = True
        
        # Get delay until next fire time.
        delay = 0
        if not finished and executed:
            delay = self.macroLines[self.activeLine].delayAfter
        
        # Update active line and check if there are remaining lines to be executed.
        if executed:
            self.activeLine += 1
            lineIndex = self.activeLine
            done = False
            while not done:
                try:
                    nextLine = self.macroLines[lineIndex]
                    if not nextLine.command and not nextLine.delayAfter:
                        lineIndex += 1
                    else:
                        done = True
                except KeyError:
                    lineIndex += 1
                if lineIndex >= self.macroLineNextIndex:
                    done = True
                    finished = True
        
        curTime = time()
        
        # If the macro is basically finished, update final delay if needed.
        # A delay that goes beyond macro execution will set a minimum
        #  recovery time.
        if finished:
            manualDelay = self.manualDelay + self.startTime - curTime
            if manualDelay > 0:
                if manualDelay > delay:
                    self.recoveryDelay = manualDelay
                else:
                    self.recoveryDelay = delay
            else:
                self.recoveryDelay = delay
            # Reset start time to current time for recovery.
            self.startTime = curTime
        
        # Macro is definitely not finished yet.
        else:
            # If the macro is visible, start pulsing red.
            if self.visible:
                self.macroButton.pulseGreen = False
                self.macroButton.pulseRed = True
                self.macroButton.setValue(1)
                self.macroButton.toggleLocked = False
            # Make sure that wait time until next line is
            #  at least one second. This to wait a bit for
            #  a response from the previous action.
            if delay < 1:
                delay = 1
        
        return (finished,delay + curTime)
    
    
    # Macro.recover() checks if the macro already is usable again.
    # Returns True if recovery is completed according to set rules.
    def recover(self):
        # Check each mandatory line if it can be executed again.
        recovered = True
        # If there is only one macro line, we need this one to be available,
        #  no matter the mandatory setting.
        if self.macroLineNum == 1:
            for macroLine in self.macroLines.itervalues():
                recovered = macroLine.checkAvailability(self.charIndex)
        else:
            for macroLine in self.macroLines.itervalues():
                # If this line is mandatory or we're required to wait
                #  for all commands to recover, check if this command
                #  has already recovered.
                if macroLine.mandatory or self.waitAll:
                    if not macroLine.checkAvailability(self.charIndex):
                        recovered = False
                        break
        
        # Even if the macro would have recovered command-wise,
        #  we need now to check any minimum delays set.
        if recovered:
            if self.startTime + self.recoveryDelay > time():
                recovered = False
        
        # If the macro still counts as recovered if we get here, it is
        #  or never needed recovery in the first place.
        if recovered:
            # Update visible status of the macro.
            # Skip if this macro contains an /attack command and
            #  the character currently is in an aggressive stance.
            if not self.appearanceAggressive and self.visible:
                self.macroButton.pulseRed = False
                self.macroButton.setValue(0)
                self.macroButton.toggleLocked = False
                # If we needed recovery signal the recovered status
                #  by pulsing green.
                if self.status == MACRO_RECOVERING:
                    self.macroButton.pulseGreen = True
                    self.resetPulseTimer = reactor.callLater(0.5,self.resetPulsing)
            # Need to reset recovery delay here in case the macro
            #  gets checked for recovery without having run.
            self.recoveryDelay = 0
            # Reset active line.
            self.activeLine = -1
            self.status = MACRO_IDLE
            return True
        
        # Ok, we just entered recovery mode (or already were in it).
        self.status = MACRO_RECOVERING
        
        # If the macro hasn't already recovered, update view of the button.
        # Skip if the macro contains an /attack command and the character
        #  currently is in an aggressive stance.
        if self.visible and not self.appearanceAggressive:
            self.macroButton.pulseGreen = False
            self.macroButton.pulseRed = False
            self.macroButton.setValue(1)
            self.macroButton.toggleLocked = True
        
        return False
    
    
    # This function gets called when a skill also used in this macro gets triggered.
    # Returns a boolean if the macro needs a recovery test.
    # Going into recovery here doesn't mean that the macro will actually get disabled.
    # It will just be entered the list to be checked if it can be activated or not.
    def skillUsed(self,skill):
        # If this macro is already recovering or running,
        #  we don't need to go into recovery mode.
        if self.status != MACRO_IDLE:
            return False
        else:
            # If there is only one line in this macro, we definitely need
            #  the skill available. Go into recovery mode.
            if self.macroLineNum == 1:
                return True
            # Otherwise run through all lines and check which ones need
            #  the skill. If the lines needing the skill are mandatory,
            #  go into recovery mode.
            for line in self.macroLines.itervalues():
                if line.mandatory:
                    if line.skill == skill:
                        return True
        # Line using this skill is not that important, no need for recovery.
        return False
    
    
    # This function gets called when a spell also used in this macro gets triggered.
    # Returns a boolean if the macro needs a recovery test.
    # Going into recovery here doesn't mean that the macro will actually get disabled.
    # It will just be entered the list to be checked if it can be activated or not.
    def spellUsed(self,spell):
        # If this macro is already recovering or running,
        #  we don't need to go into recovery mode.
        if self.status != MACRO_IDLE:
            return False
        else:
            # If there is only one line in this macro, we definitely need
            #  the spell available. Go into recovery mode.
            if self.macroLineNum == 1:
                return True
            # Otherwise run through all lines and check which ones need
            #  the spell. If the lines needing the spell are mandatory,
            #  go into recovery mode.
            for line in self.macroLines.itervalues():
                if line.mandatory:
                    if line.spell == spell:
                        return True
        # Line using this spell is not that important, no need for recovery.
        return False
    
    
    # This function gets called when an item also used in this macro gets triggered.
    # Returns a boolean if the macro needs a recovery test.
    # Going into recovery here doesn't mean that the macro will actually get disabled.
    # It will just be entered the list to be checked if it can be activated or not.
    def itemUsed(self,item):
        # If this macro is already recovering or running,
        #  we don't need to go into recovery mode.
        if self.status != MACRO_IDLE:
            return False
        else:
            # If there is only one line in this macro, we definitely need
            #  the item available. Go into recovery mode.
            if self.macroLineNum == 1:
                return True
            # Otherwise run through all lines and check which ones need
            #  the item. If the lines needing the item are mandatory,
            #  go into recovery mode.
            for line in self.macroLines.itervalues():
                if line.mandatory:
                    if line.item == item:
                        return True
        # Line using this item is not that important, no need for recovery.
        return False
    
    
    # This function gets called when the characters aggressive stance changes or
    #  when the ranged weapon got used.
    # Adjust visibility for /attack macros.
    # Return if the macro needs recovery or not (for ranged attacks).
    # This function unifies ranged and melee in preparation for a possible future
    #  revise of the ranged attack.
    def updateAttacking(self,attacking=True,ranged=False):
        if not ranged:
            # Only update appearance if necessary.
            if attacking != self.appearanceAggressive:
                self.appearanceAggressive = attacking
                # Ah yes, need to check for visibility.
                if self.visible:
                    macroButton = self.macroButton
                    # If attacking is set to True, this macro contains an activated
                    #  attack command and needs to override status appearance.
                    if attacking:
                        macroButton.pulseGreen = False
                        macroButton.pulseRed = True
                        macroButton.setValue(1)
                        macroButton.toggleLocked = False
                    # If status is running, start pulsing red.
                    elif self.status == MACRO_RUNNING:
                        macroButton.pulseGreen = False
                        macroButton.pulseRed = True
                        macroButton.setValue(1)
                        macroButton.toggleLocked = False
                    # If this macro is recovering, deactivate the button.
                    elif self.status == MACRO_RECOVERING:
                        macroButton.pulseGreen = False
                        macroButton.pulseRed = False
                        macroButton.setValue(1)
                        macroButton.toggleLocked = True
                    # Otherwise, the macro awaits its next use, don't pulse red and activate.
                    else:
                        macroButton.pulseGreen = False
                        macroButton.pulseRed = False
                        macroButton.setValue(0)
                        macroButton.toggleLocked = False
            return False
        else:
            # If this macro is already recovering or running,
            #  we don't need to go into recovery mode.
            if self.status != MACRO_IDLE:
                return False
            else:
                # If there is only one line in this macro, we definitely need
                #  the ranged weapon available. Go into recovery mode.
                if self.macroLineNum == 1:
                    return True
                # Otherwise run through all lines and check which ones need
                #  the ranged attack. If those lines are mandatory,
                #  go into recovery mode.
                for line in self.macroLines.itervalues():
                    if line.mandatory:
                        if line.command.upper().find('/RANGEDATTACK') != -1:
                            return True
            # Line using the ranged attack is not that important, no need for recovery.
            return False



class MacroMaster:
    def __init__(self):
        self.extendedMacros = True
        self.macros = dict()
        self.hotkeyDict = dict()
        self.activePage = 0
        self.runningMacros = dict()
        self.recoveringMacros = dict()
        self.skillDict = dict()
        self.spellDict = dict()
        self.itemDict = dict()
        self.attackMacros = dict()
        self.rangedAttackMacros = dict()
        self.emptyVisibleSlots = dict()
    
    
    # Set a full collection of macros, done so after loading from player settings.
    def installMacroCollection(self,macroCollection):
        # Reset macro dictionaries and active page index.
        self.macros = macroCollection
        self.hotkeyDict.clear()
        self.activePage = 0
        MacroWnd.updateActivePage(0)
        self.runningMacros.clear()
        self.recoveringMacros.clear()
        self.skillDict.clear()
        self.spellDict.clear()
        self.itemDict.clear()
        self.attackMacros.clear()
        self.rangedAttackMacros.clear()
        self.emptyVisibleSlots.clear()
        
        for charIndex,macroDict in macroCollection.iteritems():
            # Reset the set of empty visible slots for this character index.
            emptyVisibleSlots = self.emptyVisibleSlots[charIndex] = set(range(10))
            # Refill the hotkey, skill, spell and item dictionaries.
            charHotkeys = self.hotkeyDict[charIndex] = dict()
            for position,macro in macroDict.iteritems():
                hotkey = macro.hotkey
                if hotkey:
                    if hotkey[0] != 'F':
                        hotkey = '%i - %s'%(position[0],hotkey)
                    charHotkeys.setdefault(hotkey,set()).add(macro)
                for skill in macro.skills:
                    self.skillDict.setdefault(skill,set()).add(macro)
                for spell in macro.spells:
                    self.spellDict.setdefault(spell,set()).add(macro)
                for item in macro.items:
                    self.itemDict.setdefault(item,set()).add(macro)
                # Update attack sets.
                if macro.hasAttack:
                    self.attackMacros.setdefault(charIndex,set()).add(macro)
                if macro.hasRangedAttack:
                    self.rangedAttackMacros.setdefault(charIndex,set()).add(macro)
                # Update list of empty visible slots.
                if self.activePage == position[0]:
                    emptyVisibleSlots.discard(position[1])
                    # Also update macro visibility.
                    macro.setVisibility(True)
                # To begin, send macro into recovery mode. Just to check.
                self.recoveringMacros.setdefault(charIndex,set()).add(macro)
            
            # Reset the appearance of all visible empty macro slots.
            for slot in emptyVisibleSlots:
                control = TGEObject("MACROWND_MACRO%i_%i"%(charIndex,slot))
                control.setText("")
                control.setBitmap("")
                control.hotKey = -1
                control.pulseGreen = False
                control.pulseRed = False
                control.toggleLocked = True
                control.setValue(0)
                control.tooltip = "Macro Button (Press Ctrl + number to access more macro pages.  Double or Right Click to edit the macro.  Drag & Drop spells, items or skills to automatically create a macro.)"
    
    
    # Insert a macro into the macro master.
    # This is the only option to add or change a macro after them being
    #  loaded in player settings.
    # If the macro is None, will instead remove previous macro.
    def insertMacro(self,charIndex,page,slot,macro=None):
        from playerSettings import PLAYERSETTINGS
        visible = self.activePage == page
        
        # Check if there already is a macro present at the desired location.
        charMacros = self.macros.setdefault(charIndex,dict())
        oldMacro = charMacros.get((page,slot),None)
        
        # If an old macro exists we need first to clean up some stuff.
        if oldMacro:
            # Remove the old macro from the dictionary of running macros.
            try:
                del self.runningMacros[charIndex][oldMacro]
            except KeyError:
                pass
            # Remove the old macro from the set of recovering macros.
            try:
                self.recoveringMacros[charIndex].discard(oldMacro)
            except KeyError:
                pass
            # Remove the old macro from the hotkey dictionary.
            try:
                hotkey = oldMacro.hotkey
                if hotkey:
                    if hotkey[0] != 'F':
                        hotkey = '%i - %s'%(page,hotkey)
                    self.hotkeyDict[charIndex][hotkey].discard(oldMacro)
            except KeyError:
                pass
            # Remove any connections the old macro has in the skill dictionary.
            for skill in oldMacro.skills:
                try:
                    self.skillDict[skill].discard(oldMacro)
                    if len(self.skillDict[skill]) == 0:
                        del self.skillDict[skill]
                # KeyError occurs if the same macro uses the same skill more
                #  than once and if it's the last macro using this skill.
                except KeyError:
                    continue
            # Remove any connections the old macro has in the spell dictionary.
            for spell in oldMacro.spells:
                try:
                    self.spellDict[spell].discard(oldMacro)
                    if len(self.spellDict[spell]) == 0:
                        del self.spellDict[spell]
                # KeyError occurs if the same macro uses the same spell more
                #  than once and if it's the last macro using this spell.
                except KeyError:
                    continue
            # Remove any connections the old macro has in the item dictionary.
            for item in oldMacro.items:
                try:
                    self.itemDict[item].discard(oldMacro)
                    if len(self.itemDict[item]) == 0:
                        del self.itemDict[item]
                # KeyError occurs if the same macro uses the same item more
                #  than once and if it's the last macro using this item.
                except KeyError:
                    continue
            # Remove macro from attack sets.
            if oldMacro.hasAttack:
                self.attackMacros[charIndex].discard(oldMacro)
            if oldMacro.hasRangedAttack:
                self.rangedAttackMacros[charIndex].discard(oldMacro)
            # Add the macro slot back in to empty visible macro slots if needed.
            if visible:
                self.emptyVisibleSlots.setdefault(charIndex,set(range(10))).add(slot)
            # And remove the old macro from the general collection of macros.
            del charMacros[(page,slot)]
            
            # If there was no new macro supplied, just delete the old one
            #  in the database.
            if not macro:
                PLAYERSETTINGS.deleteMacro(charIndex,page,slot)
                # If the button was visible, need to reset its appearance.
                if visible:
                    control = TGEObject("MACROWND_MACRO%i_%i"%(charIndex,slot))
                    control.setText("")
                    control.setBitmap("")
                    control.hotKey = -1
                    control.pulseGreen = False
                    control.pulseRed = False
                    control.toggleLocked = True
                    control.setValue(0)
                    control.tooltip = "Macro Button (Press Ctrl + number to access more macro pages.  Double or Right Click to edit the macro.  Drag & Drop spells, items or skills to automatically create a macro.)"
                return
        
        # Check again if there was no macro supplied. No macro and no old macro = return.
        if not macro:
            return
        
        # Insert the new macro into the hotkey dictionary.
        hotkey = macro.hotkey
        if hotkey:
            if hotkey[0] != 'F':
                hotkey = '%i - %s'%(page,hotkey)
            self.hotkeyDict.setdefault(charIndex,dict()).setdefault(hotkey,set()).add(macro)
        
        # Insert the new macro into the macro dictionary.
        self.macros.setdefault(charIndex,dict())[(page,slot)] = macro
        
        # Update the skill, spell and item dictionaries.
        for skill in macro.skills:
            self.skillDict.setdefault(skill,set()).add(macro)
        for spell in macro.spells:
            self.spellDict.setdefault(spell,set()).add(macro)
        for item in macro.items:
            self.itemDict.setdefault(item,set()).add(macro)
        # Update attack sets.
        if macro.hasAttack:
            self.attackMacros.setdefault(charIndex,set()).add(macro)
        if macro.hasRangedAttack:
            self.rangedAttackMacros.setdefault(charIndex,set()).add(macro)
        
        # Update list of empty visible slots.
        if visible:
            self.emptyVisibleSlots.setdefault(charIndex,set(range(10))).discard(slot)
            # Also update macro visibility.
            macro.setVisibility(True)
        
        # Now save the new macro to database.
        PLAYERSETTINGS.saveMacro(macro,oldMacro!=None)
        
        # To begin, send macro into recovery mode. Just to check.
        self.recoveringMacros.setdefault(charIndex,set()).add(macro)
    
    
    # If the macro page changes, call this function to set new page.
    def setMacroPage(self,page):
        # If the new page equals the old page, nothing to be done.
        if page != self.activePage:
            from partyWnd import PARTYWND
            self.emptyVisibleSlots.clear()
            
            # If there is a macro in the cursor, all empty slots should pulse green.
            pulseGreen = CURSORMACRO.macroType or PARTYWND.mind.cursorItem
            
            # Tell all macros that were visible that they no longer
            #  are and set the macros on the new page visible.
            # Collect data on which slots actually contain a macro.
            for charIndex,macroDict in self.macros.iteritems():
                emptyVisibleSlots = self.emptyVisibleSlots.setdefault(charIndex,set(range(10)))
                for position,macro in macroDict.iteritems():
                    if position[0] == self.activePage:
                        macro.setVisibility(False)
                    elif position[0] == page:
                        macro.setVisibility(True)
                        emptyVisibleSlots.discard(position[1])
                
                # Reset view for empty macro slots.
                for emptySlot in emptyVisibleSlots:
                    control = TGEObject("MACROWND_MACRO%i_%i"%(charIndex,emptySlot))
                    control.setText("")
                    control.setBitmap("")
                    control.hotKey = -1
                    control.pulseGreen = pulseGreen
                    control.pulseRed = False
                    control.toggleLocked = pulseGreen
                    control.setValue(0)
                    control.tooltip = "Macro Button (Press Ctrl + number to access more macro pages.  Double or Right Click to edit the macro.  Drag & Drop spells, items or skills to automatically create a macro.)"
            
            # Update current macro page.
            self.activePage = page
            MacroWnd.updateActivePage(page)
    
    
    # Call this function to show all empty macro slots (pulse green).
    def showEmptySlots(self,show=True):
        for charIndex,emptyVisibleSlots in self.emptyVisibleSlots.iteritems():
            for emptySlot in emptyVisibleSlots:
                control = TGEObject("MACROWND_MACRO%i_%i"%(charIndex,emptySlot))
                control.pulseGreen = show
                control.toggleLocked = show
    
    
    # Process one of the currently running macros for each character,
    #   update recovering macros and wait for the next tick.
    def tick(self):
        # If we don't use extended macros, switch page if necessary.
        if not self.extendedMacros:
            page = 0
            try:
                if int(TGEGetGlobal("$Py::Input::ShiftDown")):
                    page = 1
            except:
                pass
            try:
                if int(TGEGetGlobal("$Py::Input::ControlDown")):
                    page = 2
            except:
                pass
            self.setMacroPage(page)
        
        # Process one macro line per macro active per character.
        curTime = time()
        for charIndex,runningMacros in self.runningMacros.iteritems():
            if not runningMacros:
                continue
            try:
                oneGetter = itemgetter(1)
                handleMacro,fireTime = min(runningMacros.iteritems(),key=oneGetter)
                # If the earliest fire time still is in the future, skip to next character.
                if fireTime > curTime:
                    continue
                finished,nextFireTime = handleMacro.tick()
                # Since it is possible to issue a stopmacro(s) command from a
                #  macro which might affect itself, we need to check again
                #  if the macro just handled still is in the active macro set.
                if handleMacro not in runningMacros:
                    continue
                # If the macro isn't finished, update its fire time.
                if not finished:
                    runningMacros[handleMacro] = nextFireTime
                # If the macro finished, insert it into the set of recovering macros
                #  and remove it from the running dictionary.
                else:
                    del runningMacros[handleMacro]
                    self.recoveringMacros.setdefault(charIndex,set()).add(handleMacro)
            # If the dictionary is empty, just continue.
            except IndexError:
                continue
        
        # Update all recovering macros.
        for charIndex,recoveringMacros in self.recoveringMacros.iteritems():
            recoveredMacros = set()
            for macro in recoveringMacros:
                if macro.recover():
                    recoveredMacros.add(macro)
            # Remove all recovered macros from the set of recovering.
            recoveringMacros.difference_update(recoveredMacros)
    
    
    # Stop all running macros for supplied character.
    def stopMacrosForChar(self,charIndex):
        runningMacros = self.runningMacros.get(charIndex)
        if runningMacros:
            # Push macros to be stopped over to recovering macros.
            self.recoveringMacros.setdefault(charIndex,set()).update(runningMacros.iterkeys())
            # Effectively stop macros from running by emptying the dictionary.
            runningMacros.clear()
    
    
    # Stop all running macros for supplied character that
    #  bear the supplied name.
    def stopNamedMacroForChar(self,charIndex,macroName):
        runningMacros = self.runningMacros.get(charIndex)
        
        if runningMacros:
            macroName = macroName.upper()
            recoveringMacros = self.recoveringMacros.setdefault(charIndex,set())
            needRemoval = set()
            
            # Iterate over all running macros.
            for macro in runningMacros:
                # Check if the macro name matches.
                if macroName == macro.name.upper():
                    # Push macro to be stopped over to recovering macros.
                    recoveringMacros.add(macro)
                    # Add now recovering macro to those that need removal
                    #  from the set of running macros.
                    needRemoval.add(macro)
            
            # Iterate over all macros that need to be stopped and
            #  remove them from the set of running macros.
            for macro in needRemoval:
                del runningMacros[macro]
    
    
    # Call this function if a skill got used to update all macros containing that skill.
    # Instead of a single skill a list or dictionary can be given with the iterableSkills
    #  argument.
    def updateSkillUsingMacros(self,skill="",iterableSkills=None):
        if not iterableSkills:
            iterableSkills = [skill]
        for skill in iterableSkills:
            skill = skill.upper()
            skillMacros = self.skillDict.get(skill)
            if skillMacros:
                for macro in skillMacros:
                    needsRecovery = macro.skillUsed(skill)
                    if needsRecovery:
                        self.recoveringMacros.setdefault(macro.charIndex,set()).add(macro)
    
    
    # Call this function if a spell got used to update all macros containing that spell.
    def updateSpellUsingMacros(self,spell):
        spell = spell.upper()
        spellMacros = self.spellDict.get(spell)
        if spellMacros:
            for macro in spellMacros:
                needsRecovery = macro.spellUsed(spell)
                if needsRecovery:
                    self.recoveringMacros.setdefault(macro.charIndex,set()).add(macro)
    
    
    # Call this function if an item got used to update all macros containing that item.
    def updateItemUsingMacros(self,itemName):
        itemName = itemName.upper()
        itemMacros = self.itemDict.get(itemName)
        if itemMacros:
            for macro in itemMacros:
                needsRecovery = macro.itemUsed(itemName)
                if needsRecovery:
                    self.recoveringMacros.setdefault(macro.charIndex,set()).add(macro)
    
    
    # Macros containing the /attack command need to keep pulsing red as long as the
    #  character is in an aggressive stance.
    def updateAttackMacros(self,charIndex,attacking):
        attackMacros = self.attackMacros.get(charIndex)
        if attackMacros:
            for macro in attackMacros:
                macro.updateAttacking(attacking)
    
    
    # Call this function if a ranged weapon was used to update all linked macros.
    def updateRangedAttackMacros(self,charIndex):
        rangedAttackMacros = self.rangedAttackMacros.get(charIndex)
        if rangedAttackMacros:
            for macro in rangedAttackMacros:
                needsRecovery = macro.updateAttacking(ranged=True)
                if needsRecovery:
                    self.recoveringMacros.setdefault(charIndex,set()).add(macro)
    
    
    def onMacroButtonClick(self,args):
        from partyWnd import PARTYWND
        charIndex = int(args[1])
        macroSlot = int(args[2])
        page = self.activePage
        
        # If the character index is higher than maximum index,
        #  the player is using multiple macro bars for the single
        #  character, so adjust page and charIndex.
        if charIndex >= len(PARTYWND.charInfos):
            page += charIndex
            charIndex = 0
        
        charInfo = PARTYWND.charInfos[charIndex]
        
        # Check if there's some macro in the cursor.
        macroType = CURSORMACRO.macroType
        macroInfo = CURSORMACRO.macroInfo
        if macroType:
            # Create a new macro with the cursor content.
            newMacro = Macro(charIndex,page,macroSlot)
            newMacroLines = list()
            
            # Adjust the character info if the cursor macro is linked to one.
            if CURSORMACRO.charIndex != -1:
                charInfo = PARTYWND.charInfos[CURSORMACRO.charIndex]
            
            # Fill new macro with data from cursor macro according to type.
            if macroType == 'INV':
                pass #todo, actually needed?
            elif macroType == 'SKILL':
                skillInfo = GetSkillInfo(macroInfo)
                newMacro.name = skillInfo.name
                newMacro.icon = skillInfo.icon
                if newMacro.icon and not newMacro.icon.startswith('SPELLICON_'):
                    newMacro.icon = 'icons/%s'%newMacro.icon
                newMacro.description = skillInfo.name
                newMacroLines.append(MacroLine('/skill %s'%skillInfo.name))
            elif macroType == 'SPELL':
                spell = charInfo.SPELLS.get(macroInfo)
                if spell:
                    spellInfo = spell.SPELLINFO
                    newMacro.name = spellInfo.NAME
                    newMacro.icon = spellInfo.SPELLBOOKPIC
                    if newMacro.icon and not newMacro.icon.startswith('SPELLICON_'):
                        newMacro.icon = 'spellicons/%s'%newMacro.icon
                    newMacro.description = spellInfo.NAME
                    newMacroLines.append(MacroLine('/cast %s'%spellInfo.BASENAME))
            elif macroType == 'CMD':
                newMacro.name = macroInfo.name
                newMacro.icon = macroInfo.icon
                if newMacro.icon and not newMacro.icon.startswith('SPELLICON_'):
                    newMacro.icon = 'icons/%s'%newMacro.icon
                newMacro.description = macroInfo.tooltip
                newMacroLines.append(MacroLine(macroInfo.command))
            elif macroType == 'CUSTOMMACRO':
                newMacro.name = macroInfo.name
                newMacro.icon = macroInfo.icon
                newMacro.description = macroInfo.description
                newMacro.waitAll = macroInfo.waitAll
                newMacro.manualDelay = macroInfo.manualDelay
                newMacroLines = deepcopy(macroInfo.macroLines.values())
            
            # Check for valid charIndex in cursor macro.
            if CURSORMACRO.charIndex != -1:
                # If the character indexes don't fit, need to edit in
                #  a retarget command.
                if charIndex != CURSORMACRO.charIndex:
                    charName = charInfo.NAME
                    for macroLine in newMacroLines:
                        macroLine.command = '*%s* %s'%(charName,macroLine.command)
            
            # As the macro lines are now all prepared, insert them into the macro.
            newMacro.appendMacroLines(newMacroLines)
            
            # The new macro is now ready, so insert into macro master.
            self.insertMacro(charIndex,page,macroSlot,newMacro)
            
            # Clear the macro in the cursor.
            CURSORMACRO.clear()
        
        # Ok, no cursor macro, but can still have an item in cursor.
        elif PARTYWND.mind.cursorItem:
            cursorItem = PARTYWND.mind.cursorItem
            # Create a new macro with the cursor content.
            newMacro = Macro(charIndex,page,macroSlot)
            # If the item is a ranged weapon, automatically create a ranged attack macro.
            if RPG_SLOT_RANGED in cursorItem.SLOTS:
                defaultCommand = GetDefaultCommand('Ranged Attack')
                newMacro.name = defaultCommand.name
                newMacro.icon = defaultCommand.icon
                if newMacro.icon and not newMacro.icon.startswith('SPELLICON_'):
                    newMacro.icon = 'icons/%s'%newMacro.icon
                newMacro.description = defaultCommand.tooltip
                newMacro.appendMacroLine(MacroLine(defaultCommand.command))
            else:
                newMacro.name = cursorItem.NAME
                newMacro.icon = 'items/%s/0_0_0'%cursorItem.BITMAP
                newMacro.description = 'Use %s'%cursorItem.NAME
                newMacro.appendMacroLine(MacroLine('/useitem %s'%cursorItem.NAME))
            
            # The new macro is now ready, so insert into macro master.
            self.insertMacro(charIndex,page,macroSlot,newMacro)
        
        # Nothing in cursor, just simply activate or stop the macro.
        else:
            # Check if we need to activate or stop the macro.
            # Having shift pressed while clicking the button will interrupt the macro
            #  if extended macros are used. Otherwise, ignore the modifier.
            activate = True
            if self.extendedMacros:
                try:
                    if int(TGEGetGlobal("$Py::Input::ShiftDown")):
                        activate = False
                except:
                    pass
            
            # Get the macro in the clicked slot.
            charMacros = self.macros.get(charIndex)
            # If this character has no macros, return.
            if not charMacros:
                return
            clickedMacro = charMacros.get((page,macroSlot))
            # If the clicked macro slot is empty, return.
            if not clickedMacro:
                return
            
            if activate:
                # Activate the macro in the clicked slot.
                try:
                    # If the macro is recovering, can't activate it.
                    if clickedMacro in self.recoveringMacros[charIndex]:
                        return
                except KeyError:
                    pass
                self.runningMacros.setdefault(charIndex,dict())[clickedMacro] = time()
            else:
                # Stop the clicked macro and insert it into the recovering set.
                try:
                    del self.runningMacros[charIndex][clickedMacro]
                    # The try-except makes sure we'll skip this if the macro wasn't running.
                    self.recoveringMacros.setdefault(charIndex,set()).add(clickedMacro)
                except KeyError:
                    pass
    
    
    def onMacroButtonClickAlt(self,args):
        from partyWnd import PARTYWND
        charIndex = int(args[1])
        macroSlot = int(args[2])
        page = self.activePage
        
        # If the character index is higher than maximum index,
        #  the player is using multiple macro bars for the single
        #  character, so adjust page and charIndex.
        if charIndex >= len(PARTYWND.charInfos):
            page += charIndex
            charIndex = 0
        
        # Get existing macro if available.
        macro = None
        charMacros = self.macros.get(charIndex)
        if charMacros:
            macro = charMacros.get((page,macroSlot))
        
        from macroEditorWnd import MACROEDITOR
        MACROEDITOR.openMacroEditor(charIndex,page,macroSlot,macro)
    
    
    # The user chose a new macro bar, so switch to new one.
    def onSetMacroPage(self, args):
        index = args[1]
        
        # If the user chose to disable extended macros,
        #  just return. It would only mess with the shift
        #  and control toggle.
        if not self.extendedMacros:
            return
        
        # Otherwise switch to the desired page.
        self.setMacroPage(int(index) % 10)
    
    
    # A hotkey got pressed, either activate or stop bound macros.
    def onHotKey(self, args):
        hotkey = args[1]
        
        # First check if control was pressed. If so, switch macro page.
        # If the hotkey was an F-key or if we don't use extended macros,
        #  ignore the control key though.
        if hotkey[0] != 'F':
            if self.extendedMacros:
                try:
                    if int(TGEGetGlobal("$Py::Input::ControlDown")):
                        self.setMacroPage((int(hotkey) - 1) % 10)
                        return
                except:
                    pass
            
            # If we get here, no control was pressed and we need to either
            #  trigger or stop macros.
            # F-keys work across all macro pages, number keys are by page.
            hotkey = '%i - %s'%(self.activePage,hotkey)
        
        # Check if we need to activate or stop the bound macros.
        # Having shift pressed while activating the hotkey will interrupt the macro
        #  if extended macros are used. Otherwise, ignore the modifier.
        activate = True
        if self.extendedMacros:
            try:
                if int(TGEGetGlobal("$Py::Input::ShiftDown")):
                    activate = False
            except:
                pass
        
        if activate:
            # Activate all macros bound to this hotkey if they aren't recovering.
            curTime = time()
            for charIndex,hotkeyDict in self.hotkeyDict.iteritems():
                try:
                    macroSet = hotkeyDict[hotkey]
                    runningMacros = self.runningMacros.setdefault(charIndex,dict())
                    recoveringMacros = self.recoveringMacros.setdefault(charIndex,set())
                    for macro in macroSet:
                        # If the macro is recovering, can't activate it.
                        if macro in recoveringMacros:
                            continue
                        runningMacros[macro] = curTime
                except KeyError:
                    continue
        else:
            # Stop all macros bound to this hotkey and insert them into the recovering set.
            for charIndex,hotkeyDict in self.hotkeyDict.iteritems():
                runningMacros = self.runningMacros.setdefault(charIndex,dict())
                recoveringMacros = self.recoveringMacros.setdefault(charIndex,set())
                try:
                    for macro in hotkeyDict[hotkey]:
                        try:
                            del runningMacros[macro]
                            # The try-except makes sure we'll skip this if the macro wasn't running.
                            recoveringMacros.add(macro)
                        except KeyError:
                            continue
                except KeyError:
                    continue



# Returns True if the command is available, False otherwise.
def checkCommandAvailability(charInfo,command):
    if not command:
        return True
    
    if charInfo.DEAD:
        return False
    
    if command[0] == '/':
        args = command[1:].upper().split(' ',1)
        if len(args) > 1:
            command,arg = args
            arg = arg.lstrip()
        else:
            command,arg = args[0],''
        
        if command == 'SKILL':
            if charInfo.SKILLREUSE.has_key(arg):
                return False
            return True
        elif command == 'CAST':
            if charInfo.RAPIDMOBINFO.CASTING:
                return False
            for spellSlot,charSpell in charInfo.SPELLS.iteritems():
                if charSpell.SPELLINFO.BASENAME.upper() == arg:
                    if charSpell.RECASTTIMER:
                        return False
                    break
            return True
        elif command == 'USEITEM':
            for itemSlot,itemInfo in charInfo.ITEMS.iteritems():
                if itemSlot == RPG_SLOT_CURSOR:
                    continue
                if itemInfo.NAME.upper() == arg:
                    if not itemInfo.REUSETIMER:
                        return True
            return False
        elif command == 'RANGEDATTACK':
            if charInfo.RAPIDMOBINFO.RANGEDREUSE > 0:
                return False
            return True
    
    return True



MACROMASTER = MacroMaster()

def PyExec():
    global CURSORMACRO
    CURSORMACRO = CursorMacro()
    
    TGEExport(MACROMASTER.onHotKey,"Py","OnHotKey","desc",2,2)
    TGEExport(MACROMASTER.onSetMacroPage,"Py","OnSetMacroPage","desc",2,2)
    
    TGEExport(MACROMASTER.onMacroButtonClick,"Py","OnMacroButtonClick","desc",3,3)
    TGEExport(MACROMASTER.onMacroButtonClickAlt,"Py","OnMacroButtonClickAlt","desc",3,3)

