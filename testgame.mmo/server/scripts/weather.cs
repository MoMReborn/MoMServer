

function startRain()
{
   if (!isObject(SweetRain))
      $Rain = new Precipitation() {
         datablock = "HeavyRain";
         minSpeed = 2.5;
         maxSpeed = 3.0;
         numDrops = 3000;
         boxWidth = 200;
         boxHeight = 100;
         minMass = 1.0;
         maxMass = 1.2;
         rotateWithCamVel = true;
         doCollision = true;
         useTurbulence = false;
      };
}

function stopRain()
{
   if (isObject(SweetRain))
      SweetRain.delete();
   //SweetRain = "";
}

function startLightning()
{
   if (!isObject($Lightning))
      $Lightning = new Lightning() {
         position = "350 300 180";
         scale = "250 400 500";
         dataBlock = "LightningStorm";
         strikesPerMinute = "20";
         strikeWidth = "2.5";
         chanceToHitTarget = "100";
         strikeRadius = "50";
         boltStartRadius = "20";
         color = "1.000000 1.000000 1.000000 1.000000";
         fadeColor = "0.100000 0.100000 1.000000 1.000000";
         useFog = "0";
         locked = "false";
      };
}

function stopLightning()
{
   if (isObject(SweetingLightning))
      SweetLightning.delete();
   //SweetLightning = "";
}

