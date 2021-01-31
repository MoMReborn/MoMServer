# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



#getting imported by missionsifter, argh

if __name__ == '__main__':
    raise "Cannot import this module as __main__!"

import os,shutil
import os.path
from mud.world.defines import *
from mud.gamesettings import GAMEROOT

PROCESSED_DIALOG = []   

from mud.common.dbconfig import SetDBConnection

#setup the db connection
DATABASEPATH = "%s/data/worlds/multiplayer.baseline"%GAMEROOT
DATABASE = DATABASEPATH+"/world.db"

SetDBConnection('sqlite:/%s'%DATABASE)

from sqlobject import *
from mud.common.persistent import Persistent
Persistent._cacheValue = False
conn = Persistent._connection

#conn.getConnection().autoCommit = False
conn.autoCommit = False   
Persistent._connection = transaction = conn.transaction()


from packaging.content import *


CONTENT = []

def AddFolder(folder):
    dir = os.listdir(folder)
    for fn in dir:
        if ".svn" in fn:
            continue
        #up to one deep
        fn = folder+"/"+fn
        if os.path.isdir(fn):
            AddFolder(fn)
        else:
            CONTENT.append(fn)


map(AddFolder,FOLDERS)


#stock
CONTENT.extend(FULL_TEXTURES)
CONTENT.extend(COMMON_DTS)

for music in FULL_MUSIC:
    CONTENT.append("./%s/data/sound/music/%s"%(GAMEROOT,music))
    
for sfx in FULL_SFX:
    CONTENT.append("./%s/data/sound/%s"%(GAMEROOT,sfx))
    
    
    
def AddFile(filename):
    filename = filename.lower()
    filename = filename.replace("$",GAMEROOT)
    if filename in CONTENT:
        return
    CONTENT.append(filename)


def AddDTS(dts):
    dts=dts.lower()
    dts = dts.replace("$",GAMEROOT)
    if dts in CONTENT:
        return
    
    CONTENT.append(dts)
    
    if "character/models" in dts:
        return
    
    
    from DTSPython.Dts_Stream import DtsStream
    from DTSPython.Dts_Shape import DtsShape
    stream=DtsStream(dts,True)
    shape = DtsShape()
    shape.read(stream)
    
    for material in shape.materials.materials:
        dir,file = os.path.split(dts)
        dir+="/%s"%material.name
        AddTexture(dir)
    


def AddInterior(interior):
    interior=interior.lower()
    interior = interior.replace("$",GAMEROOT)
    if interior in CONTENT:
        return
    CONTENT.append(interior)

def AddMission(mission):
    pass

def AddTexture(texture):
    texture = texture.lower()
    texture = texture.replace("$",GAMEROOT)
    if ".jpg" not in texture and ".png" not in texture:
        if os.path.exists(texture+".jpg"):
            texture+=".jpg"
        else:
            texture+=".png"
    
    if texture not in CONTENT:
        CONTENT.append(texture)

def AddSound(sound):
    sound = sound.lower()
    sound = sound.replace("$",GAMEROOT)
    if sound not in CONTENT:
        CONTENT.append(sound)

ANIMATIONS = []        
def AddAnimation(animation):
    
    animation = animation.lower()
    animation = animation.replace("$",GAMEROOT)
    if animation in ANIMATIONS:
        return
    ANIMATIONS.append(animation)
    
    dir = os.listdir(animation)
    for fn in dir:
        if ".svn" in fn.lower():
            continue
        
        filename = "%s/%s"%(animation,fn)
        filename = filename.lower()
        filename = filename.replace("//","/")
        
        
        if filename not in CONTENT:
            CONTENT.append(filename)
            
        
def SiftRace(race):
    if race not in RPG_PC_RACES:
        return
    from mud.world.shared.models import GetModelInfo
    sexes = ("Male","Female")
    for sex in sexes:
        for look in range(0,3):
            size,model,tex,animation = GetModelInfo(race,sex,look)
            for t in tex:
                if t!="":
                    AddTexture("./$/data/shapes/character/textures/%s"%t)
                    
            if animation:
                animationPath = "./$/data/shapes/character/animations/%s"%animation
                animationPath = animationPath.lower()
                pathToFind = animationPath.replace("$",GAMEROOT)
                if os.path.exists(pathToFind):
                    AddAnimation(animationPath)
                    AddDTS("./$/data/shapes/character/models/%s_dsqanim.dts"%model)
            else:
                AddDTS("./$/data/shapes/character/models/%s.dts"%model)

def SiftSpellProtos():
    from mud.world.spell import SpellProto
    
    sounds = ("sndCasting","sndBegin","sndTick","sndEnd")
    
    for spell in SpellProto.select():
        for s in sounds:
            snd = getattr(spell,s)
            if snd:
                AddSound("./$/data/sound/%s"%snd)
        
        for e in spell.effectProtos:
            if e.summonPet:
                SiftSpawn(e.summonPet)


def SiftItemProtos():
    from mud.world.item import ItemProto
    
    sounds = ("sndAttack1","sndAttack2","sndAttack3","sndAttack4","sndAttack5",
              "sndAttack6","sndAttack7","sndAttack8",
              
              "sndHit1","sndHit2","sndHit3","sndHit4","sndHit5","sndHit6",
              "sndHit7","sndHit8","sndUse","sndEquip")
    
    for item in ItemProto.select():
        if not item.bitmap:
            print "WARNING: %s has no bitmap"%item.name
        else:
            texture = "./$/data/ui/items/%s/0_0_0"%item.bitmap
            AddTexture(texture)
        
        if item.model:
            AddDTS("./$/data/shapes/equipment/%s"%item.model)
        
        if item.material and "head/" not in item.material.lower() and \
            "weapons/" not in item.material.lower():
            AddTexture("./$/data/shapes/character/textures/%s"%item.material)
        elif item.material:
            AddTexture("./$/data/shapes/equipment/%s"%item.material)
        
        if item.sndProfile:
            for s in sounds:
                snd = getattr(item.sndProfile,s)
                if snd:
                    AddSound("./$/data/sound/%s"%snd)


def SiftBattleResult(zone, result):
    if not result:
        return
    
    snd = result.zoneSound
    if snd:
        AddSound("./$/data/sound/%s"%snd)

    sgroups = []
    if result.triggerSpawnGroup:
        for sg in zone.spawnGroups:
            if sg.groupName == result.triggerSpawnGroup:
                sgroups.append(sg)
                
    if result.spawnGroup:
        for sg in zone.spawnGroups:
            if sg.groupName == result.spawnGroup:
                sgroups.append(sg)
                
    for sg in sgroups:
        for sinfo in sg.spawninfos:
            SiftSpawn(sinfo.spawn)

  
def SiftBattle(name):
    from mud.world.battle import BattleGroup,BattleSequence,BattleResult,BattleMustSurvive,BattleProto
    from mud.world.zone import Zone
    bp = BattleProto.byName(name)
    
    zone = Zone.byName(bp.zoneName)
    
    sequences = []
    seq = bp.side1StartSequence
    while seq:
        sequences.append(seq)
        seq = seq.nextSequence
    seq = bp.side2StartSequence
    while seq:
        sequences.append(seq)
        seq = seq.nextSequence
        
    sgroups = []
    for s in sequences:
        snd = s.zoneSound
        if snd:
            AddSound("./$/data/sound/%s"%snd)
        for g in s.battleGroups:
            if g.triggerSpawnGroup:
                for sg in zone.spawnGroups:
                    if sg.groupName == g.triggerSpawnGroup:
                        sgroups.append(sg)
                        
            if g.spawnGroup:
                for sg in zone.spawnGroups:
                    if sg.groupName == g.spawnGroup:
                        sgroups.append(sg)
        
    
    SiftBattleResult(zone,bp.side1VictoryResult)
    SiftBattleResult(zone,bp.side2VictoryResult)
    SiftBattleResult(zone,bp.side1DefeatResult)
    SiftBattleResult(zone,bp.side2DefeatResult)
    
    for sg in sgroups:
        for sinfo in sg.spawninfos:
            SiftSpawn(sinfo.spawn)
        
            
        
                
                

def GetChoices(choice, lines, choices):
    if choice in choices:
        return
    
    choices.append(choice)
    
    if choice.successLine and choice.successLine not in lines:
        lines.append(choice.successLine)
    if choice.failLine and choice.failLine not in lines:
        lines.append(choice.failLine)
    
    for line in choice.lines:
        if line not in lines:
            lines.append(line)
    
    for line in lines:
        for c in line.choices:
            GetChoices(c,lines,choices)


def SiftDialog(dialog):
    if dialog.name in PROCESSED_DIALOG:
        return
    
    PROCESSED_DIALOG.append(dialog.name)
    
    choices = []
    lines = []
    
    for c in dialog.choices:
        GetChoices(c,lines,choices)
    
    actions = set(dialog.actions)
    
    for line in lines:
        if not line:
            continue
        actions.update(line.actions)
    
    for a in actions:
        if a.triggerBattle:
            SiftBattle(a.triggerBattle)
        
        if a.playSound:
            AddSound("./$/data/sound/%s"%a.playSound)
        
        if a.respawn:
            SiftSpawn(a.respawn)


PROCESSED_SPAWNS = []

def SiftSpawn(spawn):
    
    if spawn.name in PROCESSED_SPAWNS:
        return
    
    PROCESSED_SPAWNS.append(spawn.name)
    
    textures = ("textureSingle","textureBody","textureHead","textureLegs","textureHands","textureFeet","textureArms")
    
    if spawn.race in RPG_PC_RACES:
        SiftRace(spawn.race)
        
    for tex in textures:
        stex = getattr(spawn,tex)
        if stex:
            AddTexture("./$/data/shapes/character/textures/%s"%stex)
               
    if "quarantine" in spawn.model or not spawn.model:
        pass #will use skeleton
    elif spawn.race not in RPG_PC_RACES:
        assert spawn.name
        AddDTS("./$/data/shapes/character/models/%s"%spawn.model)
        
    if spawn.animation:
        animationPath = "./$/data/shapes/character/animations/%s"%spawn.animation
        animationPath = animationPath.lower()
        pathToFind = animationPath.replace("$",GAMEROOT)
        if os.path.exists(pathToFind):
            AddAnimation(animationPath)
         
    if spawn.sndProfile:
        sounds = ("sndIdleLoop1","sndIdleLoop2","sndIdleLoop3","sndIdleLoop4","sndIdleRandom1","sndIdleRandom2","sndIdleRandom3",
        "sndIdleRandom4","sndAlert1","sndAlert2","sndAlert3","sndAlert4","sndAttack1","sndAttack2","sndAttack3","sndAttack4",
        "sndPain1","sndPain2","sndPain3","sndPain4","sndDeath1","sndDeath2","sndDeath3","sndDeath4")
        
        for sound in sounds:
            snd = getattr(spawn.sndProfile,sound)
            if snd:
                AddSound("./$/data/sound/%s"%snd)
    
    if spawn.dialog:
        SiftDialog(spawn.dialog)
    
    if spawn.respawn:
        SiftSpawn(spawn.respawn)

def SiftZone(zonename):
    from mud.world.zone import Zone
    from mud.world.dialog import Dialog
    from missionsifter import SiftMission

    zone = Zone.byName(zonename)
    
    print "Sifting zone file: ",zone.missionFile
    spawngroups,dtriggers = SiftMission(zone.missionFile)
    
    #SPAWNS
    spawns = []
    for sg in zone.spawnGroups:
        #if sg.groupName.upper() in spawngroups: #only do the ones we are actually using
        for si in sg.spawninfos:
            if si.spawn not in spawns:
                spawns.append(si.spawn)
    
    map(SiftSpawn,spawns)
    
    #ZONE DIALOG
    for d in dtriggers:
        d = d.replace(r"\'","'")
        dlg = Dialog.byName(d)
        SiftDialog(dlg)


def GatherContent():
    from missionsifter import SiftSpellScript
    from mud.world.crafting import Recipe
    from mud.world.item import ItemSetPower
    
    for power in ItemSetPower.select():
        if power.sound:
            AddSound("./$/data/sound/%s"%power.sound)
    
    map(SiftRace,FULL_RACES)
    
    map(SiftZone,FULL_ZONES)
    
    SiftSpellProtos()
    
    SiftItemProtos()
    
    for recipe in Recipe.select():
        if recipe.craftSound:
            AddSound("./$/data/sound/%s"%recipe.craftSound)
    
    map(SiftSpellScript,COMMON_SPELLSCRIPTS)
    
    return CONTENT



if __name__ == '__main__':
    GO()
