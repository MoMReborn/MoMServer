//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------

datablock ParticleData(ChimneySmoke)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.2;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 3000;
   lifetimeVarianceMS   = 250;
   useInvAlpha = false;
   spinRandomMin = -30.0;
   spinRandomMax = 30.0;

   colors[0]     = "0.6 0.6 0.6 0.1";
   colors[1]     = "0.6 0.6 0.6 0.1";
   colors[2]     = "0.6 0.6 0.6 0.0";

   sizes[0]      = 0.5;
   sizes[1]      = 0.75;
   sizes[2]      = 1.5;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(ChimneySmokeEmitter)
{
   ejectionPeriodMS = 20;
   periodVarianceMS = 5;

   ejectionVelocity = 0.25;
   velocityVariance = 0.10;

   thetaMin         = 0.0;
   thetaMax         = 90.0;  

   particles = ChimneySmoke;
};

datablock ParticleEmitterNodeData(ChimneySmokeEmitterNode)
{
   timeMultiple = 1;
};


//-----------------------------------------------------------------------------

datablock ParticleData(ChimneyFire1)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.1;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 1000;
   lifetimeVarianceMS   = 600;
   useInvAlpha = false;
   spinRandomMin = -90.0;
   spinRandomMax = 90.0;

   colors[0]     = "0.8 0.4 0.0 1.0";
   colors[1]     = "0.6 0.2 0.0 1.0";
   colors[2]     = "0.2 0.0 0.0 0.0";

   sizes[0]      = 1.0;
   sizes[1]      = 0.60;
   sizes[2]      = 0.20;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleData(ChimneyFire2)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.5;   // rises slowly
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 150;
   useInvAlpha = false;
   spinRandomMin = -30.0;
   spinRandomMax = 30.0;

   colors[0]     = "0.6 0.6 0.0 0.1";
   colors[1]     = "0.6 0.6 0.0 0.1";
   colors[2]     = "0.0 0.0 0.0 0.0";

   sizes[0]      = 0.5;
   sizes[1]      = 0.5;
   sizes[2]      = 0.5;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(ChimneyFireEmitter)
{
   ejectionPeriodMS = 200;
   periodVarianceMS = 10;

   ejectionVelocity = 0.15;
   velocityVariance = 0.05;

   thetaMin         = 3.0;
   thetaMax         = 90.0;  

   particles = "ChimneyFire1";
};

datablock ParticleEmitterNodeData(ChimneyFireEmitterNode)
{
   timeMultiple = 1;
};

