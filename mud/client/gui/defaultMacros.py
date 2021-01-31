# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from defaultCommandsWnd import GetDefaultCommandAsMacro



def Warrior(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Kick',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Ranger(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Ranged Attack',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Kick',charIndex,0,2)
    if defaultCommandMacro:
        macros[(0,2)] = defaultCommandMacro
    
    return macros


def Bard(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Kick',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,2)
    if defaultCommandMacro:
        macros[(0,2)] = defaultCommandMacro
    
    return macros


def Barbarian(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Kick',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Paladin(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Kick',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Tempest(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Wizard(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Revealer(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Thief(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    return macros


def Doom_Knight(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Kick',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,2)
    if defaultCommandMacro:
        macros[(0,2)] = defaultCommandMacro
    
    return macros


def Assassin(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    return macros


def Shaman(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Druid(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Cleric(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Monk(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Kick',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    return macros


def Necromancer(charIndex):
    macros = dict()
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Attack',charIndex,0,0)
    if defaultCommandMacro:
        macros[(0,0)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('Stop Cast',charIndex,0,1)
    if defaultCommandMacro:
        macros[(0,1)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('PetAtk',charIndex,0,2)
    if defaultCommandMacro:
        macros[(0,2)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('PetSd',charIndex,0,3)
    if defaultCommandMacro:
        macros[(0,3)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('PetFlw',charIndex,0,4)
    if defaultCommandMacro:
        macros[(0,4)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('PetStay',charIndex,0,5)
    if defaultCommandMacro:
        macros[(0,5)] = defaultCommandMacro
    
    defaultCommandMacro = GetDefaultCommandAsMacro('PetDis',charIndex,0,6)
    if defaultCommandMacro:
        macros[(0,6)] = defaultCommandMacro
    
    return macros



CLASSES = {}
CLASSES['Warrior'] = Warrior
CLASSES['Monk'] = Monk
CLASSES['Ranger'] = Ranger
CLASSES['Paladin'] = Paladin
CLASSES['Barbarian'] = Barbarian

CLASSES['Necromancer'] = Necromancer
CLASSES['Revealer'] = Revealer
CLASSES['Wizard'] = Wizard

CLASSES['Cleric'] = Cleric
CLASSES['Tempest'] = Tempest
CLASSES['Shaman'] = Shaman
CLASSES['Druid'] = Druid

CLASSES['Bard'] = Bard
CLASSES['Thief'] = Thief
CLASSES['Assassin'] = Assassin
CLASSES['Doom Knight'] = Doom_Knight



def CreateDefaultMacros(charIndex,charClass):
    try:
        return CLASSES[charClass](charIndex)
    except KeyError:
        return None
