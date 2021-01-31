# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


import re
import os,stat
from array import *
from mud.gamesettings import GAMEROOT

MISSION_PARSER = re.compile(r'new +[!~/\\\'\sa-zA-Z0-9().{_;="-]*};+')
TYPE_PARSER = re.compile(r'new +[a-zA-Z0-9]*')
ATTR_PARSER = re.compile(r'[a-zA-Z0-9]* = +.+')

PROCESSED_INTERIORS = []
PROCESSED_DTS = []

def SiftInteriorInstance(interior):
    from contentsifter import AddTexture,AddInterior
    
    filename = interior['interiorFile'].replace("~","./%s"%GAMEROOT)
    if filename in PROCESSED_INTERIORS:
        return
    
    #print "Processing Interior: %s"%filename
    
    AddInterior(filename)
    PROCESSED_INTERIORS.append(filename)
    
    mystat  =  os.lstat(filename)
    size = mystat[stat.ST_SIZE]
    
    f = file(filename,"rb")
    data = array('B')
    data.fromfile(f,size)
    f.close()
    
    
    index=0
    

    index+=4 #file version
    index+=1 #previewIncluded
    
    numDetails = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    
    index+=4 #numdetails
    
    #--- detail0
    
    index+=4 #fileversion
    index+=4 #detaillevel
    index+=4 #minpixels
    
    index+=6*4 #bound
    index+=4*4 #sphere
    
    index+=1 #mHasAlarmState
    index+=4 #numLight
        
    numNormals = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    
    index+=numNormals*12
    
    vecSize = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    
    index+=vecSize*6
    
    #points
    points = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    
    index+=points*4*3
    
    visSize = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    index+=visSize
    
    numTexGen = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    index+=numTexGen*16*2
    
    numBSPNodes = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    index+=6*numBSPNodes
    
    numSolidLeaves = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    index+=6*numSolidLeaves
    
    #MATERIAL LIST
    
    index+=1 #version
    
    materials = (data[index+3]<<24)+(data[index+2]<<16)+(data[index+1]<<8)+data[index]
    index+=4
    
    for i in range(0,materials):
        material = ""
        length = data[index]
        index+=1
        for x in range(0,length):
            material += chr(data[index])
            index+=1
                                
        if "NULL" in material or "TRIGGER" in material or "FORCEFIELD" in material or "ORIGIN" in material:
            continue
        
        texture = "./%s/data/interiors/%s"%(GAMEROOT,material)
        
        textureJPG = texture+".jpg"
        texturePNG = texture+".png"
        
        if not os.path.exists(textureJPG) and not os.path.exists(texturePNG):
            base,filename = os.path.split(texture)
            base = base[:base.rfind("/")]
            texture = base+"/"+filename
        
        AddTexture(texture)
            
        
        
def SiftDTS(filename):
    if filename in PROCESSED_DTS:
        return
    
    PROCESSED_DTS.append(filename)
    
    from contentsifter import AddTexture,AddDTS
    
    AddDTS(filename)
    
    #print "Processing DTS: %s"%filename
    

def SiftTSStatic(static):
    shapefile = static['shapeName']
    shapefile=shapefile.replace("~","./%s"%GAMEROOT)
    
    SiftDTS(shapefile)

def SiftTSDynamic(static):
    shapefile = static['shapeName']
    shapefile=shapefile.replace("~","./%s"%GAMEROOT)
    
    SiftDTS(shapefile)

    
def SiftShapeReplicator(repl):
    shapefile = repl['shapeFile']
    shapefile=shapefile.replace("~","./%s"%GAMEROOT)
    SiftDTS(shapefile)
    
    
    
        
def SiftMission(missionfile):
    from contentsifter import AddTexture,AddSound,AddFile
    base = "./%s/data/missions/%s"%(GAMEROOT,missionfile[:-4])
    AddFile(base+".mis")
    AddFile(base+".ter")
    AddFile(base+".ml")
    
    
    spawngroups = []
    dialogTriggers = []
    
    f = file("./%s/data/missions/%s"%(GAMEROOT,missionfile))
    mission = f.read()
    f.close()
    mission = mission.replace ("new SimGroup(","xxx xxxx")
    
    components = MISSION_PARSER.findall(mission)
    
    for comp in components:
        mtype = TYPE_PARSER.search(comp).group()[4:]
        attributes = ATTR_PARSER.findall(comp)
        
        adict={}
        for a in attributes:
            attr,value = a.split("=")
            attr=attr.replace(" ","")
            value = value[2:-2]
            adict[attr]=value
            
        if mtype == "InteriorInstance":
            SiftInteriorInstance(adict)
            
        if mtype == "TSStatic":
            SiftTSStatic(adict)
            dialogTrigger = adict.get("dialogTrigger","")
            if dialogTrigger:
                if dialogTrigger not in dialogTriggers:
                    dialogTriggers.append(dialogTrigger)

        if mtype == "TSDynamic":
            SiftTSDynamic(adict)

            
        if mtype == "fxShapeReplicator":
            SiftShapeReplicator(adict)
            
        if mtype == "fxFoliageReplicator":
            ff = adict['FoliageFile']
            ff = ff.replace("~","./%s"%GAMEROOT)
            AddTexture(ff)

        if mtype == "fxGrassReplicator":
            ff = adict['GrassFile']
            ff = ff.replace("~","./%s"%GAMEROOT)
            AddTexture(ff)
            
        if mtype == "AudioEmitter":
            ff = adict['fileName']
            ff = ff.replace("~","./%s"%GAMEROOT)
            AddSound(ff)
            
        if mtype == "TerrainBlock":
            ff = adict['detailTexture']
            ff = ff.replace("~","./%s"%GAMEROOT)
            AddTexture(ff)
            
        if mtype == "WaterBlock":
            textures = ("surfaceTexture","ShoreTexture","envMapOverTexture","envMapUnderTexture","submergeTexture","specularMaskTex")
            for t in textures:
                filename = adict.get(t,"")
                if filename:
                    filename = filename.replace("~","./%s"%GAMEROOT)
                    AddTexture(filename)
                    
        if mtype == "rpgSpawnPoint":
            sgroup = adict['SpawnGroup'].upper()
            if  sgroup not in spawngroups:
                spawngroups.append(sgroup)
                                
    return spawngroups,dialogTriggers
                    
            
     


TEXTURENAME_PARSER = re.compile(r'texturename\s*=\s*\S*')
TEXTURE_PARSER = re.compile(r'texture\s*=\s*\S*')
#textureName          = "~/data/spells/tests/zodiacs/crop2_zode";
#texture = "~/data/spells/AP/zodiacs/AP_teleportZode.png";
     
def SiftSpellScript(script):
    from contentsifter import AddTexture
    script = "./%s/datablocks/spells/%s"%(GAMEROOT,script)
    file = open(script)
        
    c = file.read().lower()
    
    tnames = TEXTURENAME_PARSER.findall(c)
    tnames.extend(TEXTURE_PARSER.findall(c))
    for tname in tnames:
        tname = tname.replace("~","./%s"%GAMEROOT)
        tnames = tname.split('"')
        filename = tnames[1]
        
        filebase,ext = os.path.splitext(filename)
        if not len(ext):
            if os.path.exists(filename+".jpg"):
                filename+=".jpg"
            elif os.path.exists(filename+".png"):
                filename+=".png"
            else:
                if "spells/ap_quickwavea" not in filename:
                    assert 0,filename
                
            
            
        AddTexture(filename)
        
        
    
        
    file.close()  
            

            
                
                
        
        
        
        
    
    
    
    
    
    