# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
import os, sys


INVALID = [
"mouse2"
]

def KeyCanBeRemapped(args):
    key = args[1]
    if key in INVALID:
        return 0
    return 1


def SetGameDifficulty():
    from mud.world.core import CoreSettings
    v = int(TGEGetGlobal("$pref::gameplay::difficulty"))
    
    if v==1:
        CoreSettings.DIFFICULTY = 0
    elif v ==2:
        CoreSettings.DIFFICULTY = 2
    else:
        CoreSettings.DIFFICULTY = 1
    
    
def OnRespawnTime():
    value = float(TGEGetGlobal("$pref::gameplay::monsterrespawn"))
    
    from mud.world.core import CoreSettings
    CoreSettings.RESPAWNTIME = value


def getSystemFonts():
    ''' getSystemFonts: Returns a lis of system fonts based on the OS. '''
    if sys.platform == 'win32':
        return getFonts_win32()
    # No idea how to get a list of fonts on OSX, so return a 
    # list of some common/default fonts and hope they are on OSX.
    #elif sys.platform == 'darwin':
    #    return = getFonts_darwin()
    else:
        return ["Arial", "Courier", "Courier New", "Georgia",
                "Impact", "Script", "Tahoma", "Times New Roman",
                "Verdana"]


def getFonts_win32():
    ''' getFonts_win32: Gets and returns a list of installed fonts. '''
    import _winreg
    
    fonts = []
    fontdir = os.path.join(os.environ['WINDIR'], "Fonts")

    # This is a list of registry keys containing information
    # about fonts installed on the system.
    keys = []

    # Find valid registry keys containing font information.
    possible_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Fonts",
        r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts"
        ]

    for key_name in possible_keys:
        try:
            key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, key_name)
            keys.append(key)
        except WindowsError:
            pass

    for key in keys:
        fontdict = {}
        for i in range(_winreg.QueryInfoKey(key)[1]):
            try:
                name, font, t = _winreg.EnumValue(key,i)
            except EnvironmentError:
                break

            # Try and handle windows unicode strings for some file names.
            # Here are two documents with some information about it:
            #   http://www.python.org/peps/pep-0277.html
            #   https://www.microsoft.com/technet/archive/interopmigration/linux/mvc/lintowin.mspx#ECAA
            try:
                font = str(font)
            except UnicodeEncodeError:

                # MBCS is the windows encoding for unicode file names.
                try:
                    font = font.encode('MBCS')
                except:
                    # String conversion and MBCS encoding failed, skip the font.
                    continue
   
            # Check font extension.
            if font[-4:].lower() not in [".ttf", ".ttc"]:
                continue
            
            # Strip TrueType from font name.
            if name[-10:] == '(TrueType)':
                name = name[:-11]

            # Capitalize each word in a font name and add to font list.
            fonts.append(' '.join([word.capitalize() for word in name.split()]))
     
    fonts.sort()
    return fonts


def OnLoadFontOptions():
    ''' OnLoadFontOptions: Load font options for Options menu. '''

    # Get handle to GUI objects.
    gameFontOptions = TGEObject("OptChatGameFont")
    chatFontOptions = TGEObject("OptChatSpeechFont")
    
    # Add sytem fonts to the drop down menu.
    for index, font in enumerate(getSystemFonts()):
        gameFontOptions.add(font, 1 + index)
        chatFontOptions.add(font, 1 + index)
        
    # Set default to Arial for the time being.  Get and set in
    # player options later.
    gameFontOptions.setText("Arial")
    chatFontOptions.setText("Arial")
    

def PyExec():
    OnLoadFontOptions()
    
    from playerSettings import PLAYERSETTINGS
    TGEEval("GameplayExtendedMacros.setValue(%i);"%PLAYERSETTINGS.useExtendedMacros)
    
    TGEExport(KeyCanBeRemapped,"Py","KeyCanBeRemapped","desc",2,2)
    TGEExport(OnRespawnTime,"Py","OnRespawnTimeChanged","desc",1,1)
    TGEExport(SetGameDifficulty,"Py","SetGameDifficulty","desc",1,1)
