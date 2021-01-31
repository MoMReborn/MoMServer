# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport
from mud.world.defines import *
import math


def SetWeatherDry(wc):
    if wc.precip < .7:
        try:
            rain = TGEObject("SweetRain")
            rain.delete()
            dust = TGEObject("SweetDust")
            dust.delete()

        except:
            pass
    else:
        try:
            rain = TGEObject("SweetRain")
            dust = TGEObject("SweetDust")
        except:
            TGEEval("""
              %rain = new Precipitation(SweetRain) {
              dataBlock = "Sandstorm";
              minSpeed = "1";
              maxSpeed = "1";
              minMass = "0.5";
              maxMass = "1";
              maxTurbulence = "10";
              turbulenceSpeed = "0.1";
              rotateWithCamVel = "0";
              useTurbulence = "1";
              numDrops = "1700";
              boxWidth = "150";
              boxHeight = "100";
              doCollision = "0";

          };
           %dust = new Precipitation(SweetDust) {
              position = "25.7111 -201.737 100.477";
              rotation = "1 0 0 0";
              scale = "1 1 1";
              nameTag = "Dust";
              dataBlock = "dustspecks";
              minSpeed = "0.1";
              maxSpeed = "0.7";
              minMass = "1";
              maxMass = "2";
              maxTurbulence = "5";
              turbulenceSpeed = "1";
              rotateWithCamVel = "0";
              useTurbulence = "1";
              numDrops = "2600";
              boxWidth = "200";
              boxHeight = "100";
              doCollision = "0";
           };
           MissionCleanup.add(%rain);
           MissionCleanup.add(%dust);""")
        

def SetWeatherCold(wc):
    if not wc.precip:
        try:
            rain = TGEObject("SweetRain")
            rain.delete()
        except:
            pass
    else:
        try:
            rain = TGEObject("SweetRain")
        except:
            TGEEval("""
             %rain = new Precipitation(SweetRain) {
             datablock = "HeavySnow";
             minSpeed = 0.01;
             maxSpeed = 0.3;
             numDrops = 5000;
             boxWidth = 200;
             boxHeight = 100;
             minMass = 0.5;
             maxMass = 1.5;
             rotateWithCamVel = false;
             doCollision = true;
             useTurbulence = true;
             maxTurbulence = 15.0;
             turbulenceSpeed = 0.01;

          };
          MissionCleanup.add(%rain);""")
            rain = TGEObject("SweetRain")
        
        rain.minSpeed = .05 + (wc.windspeed*.3)
        rain.maxSpeed = .3 + (wc.windspeed*.5)
        
        rain.setPercentage(wc.precip)
        
    if wc.precip < .8:
        try:
            light = TGEObject("SweetLightning")
            light.delete()
        except:
            pass
        
    else:
        try:
            lightning = TGEObject("SweetLightning")
        except:
            TGEEval("""
            %lightning = new Lightning(SweetLightning) {
            position = "350 300 180";
            scale = "250 400 500";
            dataBlock = "LightningStorm";
            strikesPerMinute = "10";
            strikeWidth = "2.5";
            chanceToHitTarget = "100";
            strikeRadius = "50";
            boltStartRadius = "20";
            color = "1.000000 1.000000 1.000000 1.000000";
            fadeColor = "0.100000 0.100000 1.000000 1.000000";
            useFog = "0";
            locked = "false";
            };
            MissionCleanup.add(%lightning);""")

        


def SetWeatherTemperate(wc):
    if not wc.precip:
        try:
            rain = TGEObject("SweetRain")
            rain.delete()
        except:
            pass
    else:
        try:
            rain = TGEObject("SweetRain")
        except:
            TGEEval("""
             %rain = new Precipitation(SweetRain) {
             datablock = "HeavyRain";
             minSpeed = 2.5;
             maxSpeed = 3.0;
             numDrops = 5000;
             boxWidth = 200;
             boxHeight = 100;
             minMass = 1.0;
             maxMass = 1.2;
             rotateWithCamVel = true;
             doCollision = true;
             useTurbulence = false;
          };
          MissionCleanup.add(%rain);""")
            rain = TGEObject("SweetRain")
            
        rain.setPercentage(wc.precip)
        
    if wc.precip < .4:
        try:
            rain2 = TGEObject("SweetRainStorm")
            rain2.delete()

        except:
            pass
        
    else:
        try:
            rain2 = TGEObject("SweetRainStorm")
            
        except:
            TGEEval("""
             %rain = new Precipitation(SweetRainStorm) {
             datablock = "HeavyRain2";
             minSpeed = 2.5;
             maxSpeed = 3.0;
             numDrops = 1000;
             boxWidth = 200;
             boxHeight = 100;
             minMass = 1.0;
             maxMass = 1.2;
             rotateWithCamVel = true;
             doCollision = false;
             useTurbulence = false;
          };
          MissionCleanup.add(%rain);""")
                
            rain2 = TGEObject("SweetRainStorm")
                
        rain2.setPercentage(wc.precip)

        
    if wc.precip < .8:
        try:
            light = TGEObject("SweetLightning")
            light.delete()
        except:
            pass
        
    else:
        try:
            lightning = TGEObject("SweetLightning")
        except:
            TGEEval("""
            %rain =new Lightning(SweetLightning) {
            position = "350 300 180";
            scale = "250 400 500";
            dataBlock = "LightningStorm";
            strikesPerMinute = "10";
            strikeWidth = "2.5";
            chanceToHitTarget = "100";
            strikeRadius = "50";
            boltStartRadius = "20";
            color = "1.000000 1.000000 1.000000 1.000000";
            fadeColor = "0.100000 0.100000 1.000000 1.000000";
            useFog = "0";
            locked = "false";
            };
            MissionCleanup.add(%rain);""")




def SetWeather(wc):
    sky = TGEObject("sky")
    sky.setCloudCover(wc.cloudCover)
    d  = math.radians(wc.winddir)
    x = math.sin(d)
    y = math.cos(d)
    sky.setWindVelocity(x*wc.windspeed,y*wc.windspeed,0)
    
    try:
        if int(TGEGetGlobal("$pref::DisableWeatherEffects")):
            return
    except:
        pass
        
#RPG_CLIMATE_TROPICAL = 0
#RPG_CLIMATE_DRY = 1
#RPG_CLIMATE_TEMPERATE = 2
#RPG_CLIMATE_COLD = 3
#RPG_CLIMATE_POLAR = 4

    if wc.climate == RPG_CLIMATE_TROPICAL or wc.climate == RPG_CLIMATE_TEMPERATE:
        SetWeatherTemperate(wc)
    if wc.climate == RPG_CLIMATE_COLD or wc.climate == RPG_CLIMATE_POLAR:
        SetWeatherCold(wc)
    if wc.climate == RPG_CLIMATE_DRY:
        SetWeatherDry(wc)
        

