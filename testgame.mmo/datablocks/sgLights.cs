//-----------------------------------------------
// Copyright (c) Synapse Gaming 2004
// Written by John Kabus
//-----------------------------------------------

$sgLightEditor::lightDBPath = $defaultGame @ "/datablocks/sgLights/";

function sgLoadLightDataBlocks()
{
   //load precompiled...
   %path = $sgLightEditor::lightDBPath @ "*.dso";
   echo("//-----------------------------------------------");
   echo("Loading Synapse Gaming light datablocks from: " @ %path);
   %file = findFirstFile(%path);
  
  while(%file !$= "")
  {
     %file = filePath(%file) @ "/" @ fileBase(%file);
     exec(%file);
      %file = findNextFile(%path);
  }

   //load uncompiled...
   %path = $sgLightEditor::lightDBPath @ "*.cs";
   echo("//-----------------------------------------------");
   echo("Loading Synapse Gaming light datablocks from: " @ %path);
   %file = findFirstFile(%path);
  
  while(%file !$= "")
  {
     exec(%file);
      %file = findNextFile(%path);
  }
   
   echo("Loading complete.");
   echo("//-----------------------------------------------");
}

sgLoadLightDataBlocks();

function serverCmdsgGetLightDBId(%client, %db)
{
   %id = nameToId(%db);
   commandToClient(%client, 'sgGetLightDBIdCallback', %id);
}

//----------------------------------------

datablock ParticleData(RealFireParticle)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.075;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 2000;
   lifetimeVarianceMS   = 0;
   useInvAlpha = false;
   spinRandomMin = -90.0;
   spinRandomMax = 90.0;

   colors[0]     = "0.6 0.2 0.0 1.0";
   colors[1]     = "0.6 0.2 0.0 1.0";
   colors[2]     = "0.2 0.0 0.0 0.0";

   sizes[0]      = 0.9;
   sizes[1]      = 0.75;
   sizes[2]      = 0.3;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(RealFireEmitter)
{
   ejectionPeriodMS = 200;
   periodVarianceMS = 0;

   ejectionVelocity = 0.07;
   velocityVariance = 0.00;

   thetaMin         = 1.0;
   thetaMax         = 100.0;  

   particles = "RealFireParticle";
};

datablock ParticleData(RealFireSmallParticle)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.05;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 2000;
   lifetimeVarianceMS   = 0;
   useInvAlpha = false;
   spinRandomMin = -90.0;
   spinRandomMax = 90.0;

   colors[0]     = "0.6 0.2 0.0 1.0";
   colors[1]     = "0.6 0.2 0.0 1.0";
   colors[2]     = "0.2 0.0 0.0 0.0";

   sizes[0]      = 0.6;
   sizes[1]      = 0.5;
   sizes[2]      = 0.1;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(RealFireSmallEmitter)
{
   ejectionPeriodMS = 200;
   periodVarianceMS = 0;

   ejectionVelocity = 0.07;
   velocityVariance = 0.00;

   thetaMin         = 1.0;
   thetaMax         = 100.0;  

   particles = "RealFireSmallParticle";
};

datablock ParticleData(RealFireBigParticle)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.15;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 2000;
   lifetimeVarianceMS   = 0;
   useInvAlpha = false;
   spinRandomMin = -90.0;
   spinRandomMax = 90.0;

   colors[0]     = "0.6 0.2 0.0 1.0";
   colors[1]     = "0.6 0.2 0.0 1.0";
   colors[2]     = "0.2 0.0 0.0 0.0";

   sizes[0]      = 2.0;
   sizes[1]      = 1.6;
   sizes[2]      = 0.75;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(RealFireBigEmitter)
{
   ejectionPeriodMS = 200;
   periodVarianceMS = 0;

   ejectionVelocity = 0.07;
   velocityVariance = 0.00;

   thetaMin         = 2.0;
   thetaMax         = 180.0;  

   particles = "RealFireBigParticle";
};

datablock ParticleEmitterNodeData(RealFireNode)
{
   timeMultiple = 1;
};

datablock ParticleData(SparkParticle)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 4.0;
   gravityCoefficient   = 0.2;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 1000;
   lifetimeVarianceMS   = 750;
   useInvAlpha = false;
   spinRandomMin = 0.0;
   spinRandomMax = 0.0;

   colors[0]     = "0.6 0.6 0.6 1.0";
   colors[1]     = "0.6 0.6 0.6 1.0";
   colors[2]     = "0.0 0.0 0.0 0.0";

   sizes[0]      = 0.2;
   sizes[1]      = 0.15;
   sizes[2]      = 0.1;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(SparkEmitter)
{
   ejectionPeriodMS = 200;
   periodVarianceMS = 100;

   ejectionVelocity = 1.50;
   velocityVariance = 0.50;

   thetaMin         = 0.0;
   thetaMax         = 0.0;  

   particles = "SparkParticle";
};

datablock ParticleEmitterNodeData(SparkNode)
{
   timeMultiple = 1;
};

datablock ParticleData(TriggeredFireParticle)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.075;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 2000;
   lifetimeVarianceMS   = 0;
   useInvAlpha = false;
   spinRandomMin = -90.0;
   spinRandomMax = 90.0;

   colors[0]     = "0.0 0.0 0.0 1.0";
   colors[1]     = "0.0 0.0 0.0 1.0";
   colors[2]     = "0.0 0.0 0.0 0.0";

   sizes[0]      = 0.9;
   sizes[1]      = 0.75;
   sizes[2]      = 0.3;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(TriggeredFireEmitter)
{
   ejectionPeriodMS = 500;
   periodVarianceMS = 0;

   ejectionVelocity = 0.07;
   velocityVariance = 0.00;

   thetaMin         = 1.0;
   thetaMax         = 100.0;  

   particles = "TriggeredFireParticle";
};

datablock TriggerData(sgParticleEmitterTriggerDataBlock)
{
   // The period is value is used to control how often the console
   // onTriggerTick callback is called while there are any objects
   // in the trigger.  The default value is 100 MS.
   tickPeriodMS = 100;
};

function sgParticleEmitterTriggerDataBlock::sgResetTriggeredFireEmitter()
{
   TriggeredFireParticle.colors[0] = "0.0 0.0 0.0 1.0";
   TriggeredFireParticle.colors[1] = "0.0 0.0 0.0 1.0";
   TriggeredFireEmitter.ejectionPeriodMS = 750;
}

function sgParticleEmitterTriggerDataBlock::onEnterTrigger(%this,%trigger,%obj)
{

   TriggeredFireParticle.colors[0] = "0.6 0.2 0.0 1.0";
   TriggeredFireParticle.colors[1] = "0.6 0.2 0.0 1.0";
   TriggeredFireEmitter.ejectionPeriodMS = 200;
   Parent::onEnterTrigger(%this,%trigger,%obj);
}

function sgParticleEmitterTriggerDataBlock::onLeaveTrigger(%this,%trigger,%obj)
{
   TriggeredFireEmitter.ejectionPeriodMS = 3500;
   Parent::onLeaveTrigger(%this,%trigger,%obj);
   %this.schedule(3000, "sgResetTriggeredFireEmitter");
}



