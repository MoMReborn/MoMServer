//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Crossbow weapon. This file contains all the items related to this weapon
// including explosions, ammo, the item and the weapon item image.
// These objects rely on the item & inventory support system defined
// in item.cs and inventory.cs
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Sounds profiles


datablock AudioProfile(CrossbowExplosionSound)
{
filename = "~/data/sound/crossbow_explosion.ogg";
description = AudioDefault3d;
preload = true;
};

//-----------------------------------------------------------------------------
// Crossbow bolt projectile splash

datablock ParticleData(CrossbowSplashMist)
{
   dragCoefficient      = 2.0;
   gravityCoefficient   = -0.05;
   inheritedVelFactor   = 0.0;
   constantAcceleration = 0.0;
   lifetimeMS           = 400;
   lifetimeVarianceMS   = 100;
   useInvAlpha          = false;
   spinRandomMin        = -90.0;
   spinRandomMax        = 500.0;
   textureName          = "~/data/shapes/player/splash";
   
   colors[0]     = "0.7 0.8 1.0 1.0";
   colors[1]     = "0.7 0.8 1.0 0.5";
   colors[2]     = "0.7 0.8 1.0 0.0";
   
   sizes[0]      = 0.5;
   sizes[1]      = 0.5;
   sizes[2]      = 0.8;
   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(CrossbowSplashMistEmitter)
{
   ejectionPeriodMS = 5;
   periodVarianceMS = 0;
   ejectionVelocity = 3.0;
   velocityVariance = 2.0;
   ejectionOffset   = 0.0;
   thetaMin         = 85;
   thetaMax         = 85;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   overrideAdvance = false;
   lifetimeMS       = 250;
   particles = "CrossbowSplashMist";
};

datablock ParticleData( CrossbowSplashParticle )
{
   dragCoefficient      = 1;
   gravityCoefficient   = 0.2;
   inheritedVelFactor   = 0.2;
   constantAcceleration = -0.0;
   lifetimeMS           = 600;
   lifetimeVarianceMS   = 0;
   colors[0]     = "0.7 0.8 1.0 1.0";
   colors[1]     = "0.7 0.8 1.0 0.5";
   colors[2]     = "0.7 0.8 1.0 0.0";
   sizes[0]      = 0.5;
   sizes[1]      = 0.5;
   sizes[2]      = 0.5;
   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData( CrossbowSplashEmitter )
{
   ejectionPeriodMS = 1;
   periodVarianceMS = 0;
   ejectionVelocity = 3;
   velocityVariance = 1.0;
   ejectionOffset   = 0.0;
   thetaMin         = 60;
   thetaMax         = 80;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   overrideAdvance = false;
   orientParticles  = true;
   lifetimeMS       = 100;
   particles = "CrossbowSplashParticle";
};

datablock SplashData(CrossbowSplash)
{
   numSegments = 15;
   ejectionFreq = 15;
   ejectionAngle = 40;
   ringLifetime = 0.5;
   lifetimeMS = 300;
   velocity = 4.0;
   startRadius = 0.0;
   acceleration = -3.0;
   texWrap = 5.0;

   texture = "~/data/shapes/player/splash";

   emitter[0] = CrossbowSplashEmitter;
   emitter[1] = CrossbowSplashMistEmitter;

   colors[0] = "0.7 0.8 1.0 0.0";
   colors[1] = "0.7 0.8 1.0 0.3";
   colors[2] = "0.7 0.8 1.0 0.7";
   colors[3] = "0.7 0.8 1.0 0.0";
   times[0] = 0.0;
   times[1] = 0.4;
   times[2] = 0.8;
   times[3] = 1.0;
};

//-----------------------------------------------------------------------------
// Crossbow bolt projectile particles

datablock ParticleData(CrossbowBoltParticle)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoefficient     = 0.0;
   gravityCoefficient   = -0.1;   // rises slowly
   inheritedVelFactor   = 0.0;
   lifetimeMS           = 150;
   lifetimeVarianceMS   = 10;   // ...more or less
   useInvAlpha = false;
   spinRandomMin = -30.0;
   spinRandomMax = 30.0;

   colors[0]     = "0.1 0.1 0.1 1.0";
   colors[1]     = "0.1 0.1 0.1 1.0";
   colors[2]     = "0.1 0.1 0.1 0";

   sizes[0]      = 0.15;
   sizes[1]      = 0.20;
   sizes[2]      = 0.25;

   times[0]      = 0.0;
   times[1]      = 0.3;
   times[2]      = 1.0;
};

datablock ParticleData(CrossbowBubbleParticle)
{
   textureName          = "~/data/shapes/particles/bubble";
   dragCoefficient      = 0.0;
   gravityCoefficient   = -0.25;   // rises slowly
   inheritedVelFactor   = 0.0;
   constantAcceleration = 0.0;
   lifetimeMS           = 1500;
   lifetimeVarianceMS   = 600;    // ...more or less
   useInvAlpha          = false;
   spinRandomMin        = -100.0;
   spinRandomMax        = 100.0;

   colors[0]     = "0.7 0.8 1.0 0.4";
   colors[1]     = "0.7 0.8 1.0 1.0";
   colors[2]     = "0.7 0.8 1.0 0.0";

   sizes[0]      = 0.2;
   sizes[1]      = 0.2;
   sizes[2]      = 0.2;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(CrossbowBoltEmitter)
{
   ejectionPeriodMS = 2;
   periodVarianceMS = 0;

   ejectionVelocity = 0.0;
   velocityVariance = 0.10;

   thetaMin         = 0.0;
   thetaMax         = 90.0;  

   particles = CrossbowBoltParticle;
};

datablock ParticleEmitterData(CrossbowBoltBubbleEmitter)
{
   ejectionPeriodMS = 9;
   periodVarianceMS = 0;

   ejectionVelocity = 1.0;
   ejectionOffset   = 0.1;
   velocityVariance = 0.5;

   thetaMin         = 0.0;
   thetaMax         = 80.0;

   phiReferenceVel  = 0;
   phiVariance      = 360;
   overrideAdvances = false;  

   particles = CrossbowBubbleParticle;
};


//-----------------------------------------------------------------------------
// Explosion Debris

// Debris "spark" explosion
datablock ParticleData(CrossbowDebrisSpark)
{
   textureName          = "~/data/shapes/particles/fire";
   dragCoefficient      = 0;
   gravityCoefficient   = 0.0;
   windCoefficient      = 0;
   inheritedVelFactor   = 0.5;
   constantAcceleration = 0.0;
   lifetimeMS           = 500;
   lifetimeVarianceMS   = 50;
   spinRandomMin = -90.0;
   spinRandomMax =  90.0;
   useInvAlpha   = false;

   colors[0]     = "0.8 0.2 0 1.0";
   colors[1]     = "0.8 0.2 0 1.0";
   colors[2]     = "0 0 0 0.0";

   sizes[0]      = 0.2;
   sizes[1]      = 0.3;
   sizes[2]      = 0.1;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(CrossbowDebrisSparkEmitter)
{
   ejectionPeriodMS = 20;
   periodVarianceMS = 0;
   ejectionVelocity = 0.5;
   velocityVariance = 0.25;
   ejectionOffset   = 0.0;
   thetaMin         = 0;
   thetaMax         = 90;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   overrideAdvances = false;
   orientParticles  = false;
   lifetimeMS       = 300;
   particles = "CrossbowDebrisSpark";
};

datablock ExplosionData(CrossbowDebrisExplosion)
{
   emitter[0] = CrossbowDebrisSparkEmitter;

   // Turned off..
   shakeCamera = false;
   impulseRadius = 0;
   lightStartRadius = 0;
   lightEndRadius = 0;
};

// Debris smoke trail
datablock ParticleData(CrossbowDebrisTrail)
{
   textureName          = "~/data/shapes/particles/fire";
   dragCoefficient      = 1;
   gravityCoefficient   = 0;
   inheritedVelFactor   = 0;
   windCoefficient      = 0;
   constantAcceleration = 0;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 100;
   spinSpeed     = 0;
   spinRandomMin = -90.0;
   spinRandomMax =  90.0;
   useInvAlpha   = true;

   colors[0]     = "0.8 0.3 0.0 1.0";
   colors[1]     = "0.1 0.1 0.1 0.7";
   colors[2]     = "0.1 0.1 0.1 0.0";

   sizes[0]      = 0.2;
   sizes[1]      = 0.3;
   sizes[2]      = 0.4;

   times[0]      = 0.1;
   times[1]      = 0.2;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(CrossbowDebrisTrailEmitter)
{
   ejectionPeriodMS = 30;
   periodVarianceMS = 0;
   ejectionVelocity = 0.0;
   velocityVariance = 0.0;
   ejectionOffset   = 0.0;
   thetaMin         = 170;
   thetaMax         = 180;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   //overrideAdvances = false;
   //orientParticles  = true;
   lifetimeMS       = 5000;
   particles = "CrossbowDebrisTrail";
};

// Debris object
datablock DebrisData(CrossbowExplosionDebris)
{
   shapeFile = "~/data/shapes/crossbow/debris.dts";
   emitters = "CrossbowDebrisTrailEmitter";
   explosion = CrossbowDebrisExplosion;
   
   elasticity = 0.6;
   friction = 0.5;
   numBounces = 1;
   bounceVariance = 1;
   explodeOnMaxBounce = true;
   staticOnMaxBounce = false;
   snapOnMaxBounce = false;
   minSpinSpeed = 0;
   maxSpinSpeed = 700;
   render2D = false;
   lifetime = 4;
   lifetimeVariance = 0.4;
   velocity = 5;
   velocityVariance = 0.5;
   fade = false;
   useRadiusMass = true;
   baseRadius = 0.3;
   gravModifier = 0.5;
   terminalVelocity = 6;
   ignoreWater = true;
};


//-----------------------------------------------------------------------------
// Bolt Explosion

datablock ParticleData(CrossbowExplosionSmoke)
{
   textureName          = "~/data/shapes/particles/smoke";
   dragCoeffiecient     = 100.0;
   gravityCoefficient   = 0;
   inheritedVelFactor   = 0.25;
   constantAcceleration = -0.30;
   lifetimeMS           = 1200;
   lifetimeVarianceMS   = 300;
   useInvAlpha =  true;
   spinRandomMin = -80.0;
   spinRandomMax =  80.0;

   colors[0]     = "0.56 0.36 0.26 1.0";
   colors[1]     = "0.2 0.2 0.2 1.0";
   colors[2]     = "0.0 0.0 0.0 0.0";

   sizes[0]      = 4.0;
   sizes[1]      = 2.5;
   sizes[2]      = 1.0;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleData(CrossbowExplosionBubble)
{
   textureName          = "~/data/shapes/particles/bubble";
   dragCoeffiecient     = 0.0;
   gravityCoefficient   = -0.25;
   inheritedVelFactor   = 0.0;
   constantAcceleration = 0.0;
   lifetimeMS           = 1500;
   lifetimeVarianceMS   = 600;
   useInvAlpha          = false;
   spinRandomMin        = -100.0;
   spinRandomMax        =  100.0;

   colors[0]     = "0.7 0.8 1.0 0.4";
   colors[1]     = "0.7 0.8 1.0 0.4";
   colors[2]     = "0.7 0.8 1.0 0.0";

   sizes[0]      = 0.3;
   sizes[1]      = 0.3;
   sizes[2]      = 0.3;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(CrossbowExplosionSmokeEmitter)
{
   ejectionPeriodMS = 10;
   periodVarianceMS = 0;
   ejectionVelocity = 4;
   velocityVariance = 0.5;
   thetaMin         = 0.0;
   thetaMax         = 180.0;
   lifetimeMS       = 250;
   particles = "CrossbowExplosionSmoke";
};

datablock ParticleEmitterData(CrossbowExplosionBubbleEmitter)
{
   ejectionPeriodMS = 9;
   periodVarianceMS = 0;
   ejectionVelocity = 1;
   ejectionOffset   = 0.1;
   velocityVariance = 0.5;
   thetaMin         = 0.0;
   thetaMax         = 80.0;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   overrideAdvances = false;
   particles = "CrossbowExplosionBubble";
};

datablock ParticleData(CrossbowExplosionFire)
{
   textureName          = "~/data/shapes/particles/fire";
   dragCoeffiecient     = 100.0;
   gravityCoefficient   = 0;
   inheritedVelFactor   = 0.25;
   constantAcceleration = 0.1;
   lifetimeMS           = 1200;
   lifetimeVarianceMS   = 300;
   useInvAlpha =  false;
   spinRandomMin = -80.0;
   spinRandomMax =  80.0;

   colors[0]     = "0.8 0.4 0 0.8";
   colors[1]     = "0.2 0.0 0 0.8";
   colors[2]     = "0.0 0.0 0.0 0.0";

   sizes[0]      = 1.5;
   sizes[1]      = 0.9;
   sizes[2]      = 0.5;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(CrossbowExplosionFireEmitter)
{
   ejectionPeriodMS = 10;
   periodVarianceMS = 0;
   ejectionVelocity = 0.8;
   velocityVariance = 0.5;
   thetaMin         = 0.0;
   thetaMax         = 180.0;
   lifetimeMS       = 250;
   particles = "CrossbowExplosionFire";
};

datablock ParticleData(CrossbowExplosionSparks)
{
   textureName          = "~/data/shapes/particles/spark";
   dragCoefficient      = 1;
   gravityCoefficient   = 0.0;
   inheritedVelFactor   = 0.2;
   constantAcceleration = 0.0;
   lifetimeMS           = 500;
   lifetimeVarianceMS   = 350;

   colors[0]     = "0.60 0.40 0.30 1.0";
   colors[1]     = "0.60 0.40 0.30 1.0";
   colors[2]     = "1.0 0.40 0.30 0.0";

   sizes[0]      = 0.25;
   sizes[1]      = 0.15;
   sizes[2]      = 0.15;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleData(CrossbowExplosionWaterSparks)
{
   textureName          = "~/data/shapes/particles/bubble";
   dragCoefficient      = 0;
   gravityCoefficient   = 0.0;
   inheritedVelFactor   = 0.2;
   constantAcceleration = 0.0;
   lifetimeMS           = 500;
   lifetimeVarianceMS   = 350;

   colors[0]     = "0.4 0.4 1.0 1.0";
   colors[1]     = "0.4 0.4 1.0 1.0";
   colors[2]     = "0.4 0.4 1.0 0.0";

   sizes[0]      = 0.5;
   sizes[1]      = 0.5;
   sizes[2]      = 0.5;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(CrossbowExplosionSparkEmitter)
{
   ejectionPeriodMS = 3;
   periodVarianceMS = 0;
   ejectionVelocity = 5;
   velocityVariance = 1;
   ejectionOffset   = 0.0;
   thetaMin         = 0;
   thetaMax         = 180;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   overrideAdvances = false;
   orientParticles  = true;
   lifetimeMS       = 100;
   particles = "CrossbowExplosionSparks";
};

datablock ParticleEmitterData(CrossbowExplosionWaterSparkEmitter)
{
   ejectionPeriodMS = 3;
   periodVarianceMS = 0;
   ejectionVelocity = 4;
   velocityVariance = 4;
   ejectionOffset   = 0.0;
   thetaMin         = 0;
   thetaMax         = 60;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   overrideAdvances = false;
   orientParticles  = true;
   lifetimeMS       = 200;
   particles = "CrossbowExplosionWaterSparks";
};

datablock ExplosionData(CrossbowSubExplosion1)
{
   offset = 0;
   emitter[0] = CrossbowExplosionSmokeEmitter;
   emitter[1] = CrossbowExplosionSparkEmitter;
};

datablock ExplosionData(CrossbowSubExplosion2)
{
   offset = 1.0;
   emitter[0] = CrossbowExplosionSmokeEmitter;
   emitter[1] = CrossbowExplosionSparkEmitter;
};

datablock ExplosionData(CrossbowSubWaterExplosion1)
{
   delayMS   = 100;
   offset    = 1.2;
   playSpeed = 1.5;

   emitter[0] = CrossbowExplosionBubbleEmitter;
   emitter[1] = CrossbowExplosionWaterSparkEmitter;
   
   sizes[0] = "0.75 0.75 0.75";
   sizes[1] = "1.0 1.0 1.0";
   sizes[2] = "0.5 0.5 0.5";
   times[0] = 0.0;
   times[1] = 0.5;
   times[2] = 1.0;
};

datablock ExplosionData(CrossbowSubWaterExplosion2)
{
   delayMS   = 50;
   offset    = 1.2;
   playSpeed = 0.75;

   emitter[0] = CrossbowExplosionBubbleEmitter;
   emitter[1] = CrossbowExplosionWaterSparkEmitter;

   sizes[0] = "1.5 1.5 1.5";
   sizes[1] = "1.5 1.5 1.5";
   sizes[2] = "1.0 1.0 1.0";
   times[0] = 0.0;
   times[1] = 0.5;
   times[2] = 1.0;
};

datablock ExplosionData(CrossbowExplosion)
{
   soundProfile = CrossbowExplosionSound;
   lifeTimeMS = 1200;

   // Volume particles
   particleEmitter = CrossbowExplosionFireEmitter;
   particleDensity = 75;
   particleRadius = 2;

   // Point emission
   emitter[0] = CrossbowExplosionSmokeEmitter;
   emitter[1] = CrossbowExplosionSparkEmitter;

   // Sub explosion objects
   subExplosion[0] = CrossbowSubExplosion1;
   subExplosion[1] = CrossbowSubExplosion2;
   
   // Camera Shaking
   shakeCamera = true;
   camShakeFreq = "10.0 11.0 10.0";
   camShakeAmp = "1.0 1.0 1.0";
   camShakeDuration = 0.5;
   camShakeRadius = 10.0;

   // Exploding debris
   debris = CrossbowExplosionDebris;
   debrisThetaMin = 0;
   debrisThetaMax = 60;
   debrisPhiMin = 0;
   debrisPhiMax = 360;
   debrisNum = 6;
   debrisNumVariance = 2;
   debrisVelocity = 1;
   debrisVelocityVariance = 0.5;
   
   // Impulse
   impulseRadius = 10;
   impulseForce = 15;

   // Dynamic light
   lightStartRadius = 6;
   lightEndRadius = 3;
   lightStartColor = "0.5 0.5 0";
   lightEndColor = "0 0 0";
};

datablock ExplosionData(CrossbowWaterExplosion)
{
   soundProfile = CrossbowExplosionSound;

   // Volume particles
   particleEmitter = CrossbowExplosionBubbleEmitter;
   particleDensity = 375;
   particleRadius = 2;


   // Point emission
   emitter[0] = CrossbowExplosionBubbleEmitter;
   emitter[1] = CrossbowExplosionWaterSparkEmitter;

   // Sub explosion objects
   subExplosion[0] = CrossbowSubWaterExplosion1;
   subExplosion[1] = CrossbowSubWaterExplosion2;
   
   // Camera Shaking
   shakeCamera = true;
   camShakeFreq = "8.0 9.0 7.0";
   camShakeAmp = "3.0 3.0 3.0";
   camShakeDuration = 1.3;
   camShakeRadius = 20.0;

   // Exploding debris
   debris = CrossbowExplosionDebris;
   debrisThetaMin = 0;
   debrisThetaMax = 60;
   debrisPhiMin = 0;
   debrisPhiMax = 360;
   debrisNum = 6;
   debrisNumVariance = 2;
   debrisVelocity = 0.5;
   debrisVelocityVariance = 0.2;
   
   // Impulse
   impulseRadius = 10;
   impulseForce = 15;

   // Dynamic light
   lightStartRadius = 6;
   lightEndRadius = 3;
   lightStartColor = "0 0.5 0.5";
   lightEndColor = "0 0 0";
};

//-----------------------------------------------------------------------------
// Projectile Object

datablock ProjectileData(CrossbowProjectile)
{
   projectileShapeName = "~/data/shapes/crossbow/projectile.dts";
   directDamage        = 20;
   radiusDamage        = 20;
   damageRadius        = 1.5;
   explosion           = CrossbowExplosion;
   waterExplosion      = CrossbowWaterExplosion;

   particleEmitter     = CrossbowBoltEmitter;
   particleWaterEmitter= CrossbowBoltBubbleEmitter;

   splash              = CrossbowSplash;

   muzzleVelocity      = 100;
   velInheritFactor    = 0.3;

   armingDelay         = 0;
   lifetime            = 5000;
   fadeDelay           = 5000;
   bounceElasticity    = 0;
   bounceFriction      = 0;
   isBallistic         = false;
   gravityMod = 0.80;

   hasLight    = true;
   lightRadius = 4;
   lightColor  = "0.5 0.5 0.25";

   hasWaterLight     = true;
   waterLightColor   = "0 0.5 0.5";
   
   isGuided = true;
   precision = 100;
   trackDelay = 0;
};


datablock ProjectileData(ArrowProjectile)
{
   projectileShapeName = "~/data/shapes/crossbow/projectile.dts";
   particleWaterEmitter= CrossbowBoltBubbleEmitter;
   splash              = CrossbowSplash;

   muzzleVelocity      = 100;
   velInheritFactor    = 0.3;

   armingDelay         = 0;
   lifetime            = 5000;
   fadeDelay           = 5000;
   bounceElasticity    = 0;
   bounceFriction      = 0;
   isBallistic         = false;
   gravityMod = 0.80;

   hasLight    = false;
   lightRadius = 4;
   lightColor  = "0.5 0.5 0.25";

   hasWaterLight     = false;
   waterLightColor   = "0 0.5 0.5";

   isGuided = true;
   precision = 100;
   trackDelay = 0;
};



