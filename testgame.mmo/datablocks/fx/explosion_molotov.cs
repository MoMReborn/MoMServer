//-----------------------------------------------------------------------------
//	Particles
//-----------------------------------------------------------------------------

datablock ParticleData(MolotovDebrisTrail)
{
   textureName          = "~/data/shapes/particles/fxpack1/flame02";
   lifetimeMS           = 500;
   lifetimeVarianceMS   = 200;
   gravityCoefficient   = -0.1;
   spinRandomMin = -280.0;
   spinRandomMax =  280.0;
   useInvAlpha   = false;
   
   colors[0]     = "1.0 0.9 0.8 0.9";
   colors[1]     = "0.8 0.4 0 0.2";
   colors[2]     = "0.2 0.2 0.2 0.0";

   sizes[0]      = 0.5;
   sizes[1]      = 2.0;
   sizes[2]      = 0.5;

   times[0]      = 0.0;
   times[1]      = 0.2;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(MolotovDebrisTrailEmitter)
{
   ejectionPeriodMS = 20;
   periodVarianceMS = 10;
   ejectionVelocity = 1.0;
   velocityVariance = 0.5;
   ejectionOffset   = 0.2;
   thetaMin         = 0;
   thetaMax         = 180;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   particles = "MolotovDebrisTrail";
};

datablock ParticleData(MolotovDebrisBurst)
{
   textureName          = "~/data/shapes/particles/fxpack1/flame02";
   gravityCoefficient   = -0.3;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 400;
   spinRandomMin = -280.0;
   spinRandomMax =  280.0;
   useInvAlpha   = false;

   colors[0]     = "0.9 0.8 0.7 0.9";
   colors[1]     = "0.8 0.4 0 0.2";
   colors[2]     = "0.0 0.0 0.0 0.0";
   
   sizes[0]      = 0.6;
   sizes[1]      = 3.0;
   sizes[2]      = 0.2;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(MolotovDebrisBurstEmitter)
{
   ejectionPeriodMS = 50;
   periodVarianceMS = 20;
   ejectionVelocity = 2.0;
   velocityVariance = 1.0;
   ejectionOffset   = 0.5;
   thetaMin         = 0;
   thetaMax         = 100;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   particles = "MolotovDebrisBurst";
};


datablock ParticleData(MolotovSparks)
{
   textureName          = "~/data/shapes/particles/fxpack1/fxpack1/spark";
   gravityCoefficient   = 7.0;
   lifetimeMS           = 400;
   lifetimeVarianceMS   = 10;
   useInvAlpha =  false;
   spinRandomMin = -0.0;
   spinRandomMax =  0.0;

   colors[0]     = "1.0 0.9 0.8 0.2";
   colors[1]     = "1.0 0.9 0.8 0.8";
   colors[2]     = "0.8 0.4 0.0 0.0";

   sizes[0]      = 0.5;
   sizes[1]      = 1.5;
   sizes[2]      = 0.5;

   times[0]      = 0.0;
   times[1]      = 0.35;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(MolotovSparksEmitter)
{
   ejectionPeriodMS = 20;
   periodVarianceMS = 2;
   ejectionVelocity = 20;
   velocityVariance = 4;
   thetaMin         = 0;
   thetaMax         = 80;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   orientParticles  = true;
   orientOnVelocity = true;
   particles = "MolotovSparks";
};

datablock ParticleData(MolotovSmoke)
{
   textureName          = "~/data/shapes/particles/fxpack1/fxpack1/smoke01";
   dragCoeffiecient     = 0.0;
   gravityCoefficient   = -0.3;
   inheritedVelFactor   = 0.0;
   constantAcceleration = 0.0;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 300;
   useInvAlpha =  false;
   spinRandomMin = -80.0;
   spinRandomMax =  80.0;

   colors[0]     = "0.5 0.5 1.0 0.0";
   colors[1]     = "0.6 0.5 0.4 0.4";
   colors[2]     = "0.4 0.4 0.4 0.0";

   sizes[0]      = 2.0;
   sizes[1]      = 6.0;
   sizes[2]      = 10.0;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(MolotovSmokeEmitter)
{
   ejectionPeriodMS = 15;
   periodVarianceMS = 5;
   ejectionVelocity = 2.8;
   velocityVariance = 2.0;
   thetaMin         = 0.0;
   thetaMax         = 180.0;
   ejectionOffset   = 1;
   particles = "MolotovSmoke";
};

datablock ParticleData(MolotovFireball)
{
   textureName          = "~/data/shapes/particles/fxpack1/fxpack1/flame01";
   gravityCoefficient   = -0.5;
   lifetimeMS           = 300;
   lifetimeVarianceMS   = 100;
   useInvAlpha =  false;
   spinRandomMin = -180.0;
   spinRandomMax =  180.0;

   colors[0]     = "0.0 0.0 0.9 0.9";
   colors[1]     = "0.8 0.4 0.2 0.3";
   colors[2]     = "0.8 0.4 0.0 0.0";

   sizes[0]      = 2.0;
   sizes[1]      = 14.0;
   sizes[2]      = 9.0;

   times[0]      = 0.0;
   times[1]      = 0.2;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(MolotovFireballEmitter)
{
   ejectionPeriodMS = 10;
   periodVarianceMS = 5;
   ejectionVelocity = 6;
   velocityVariance = 2;
   thetaMin         = 0;
   thetaMax         = 180;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   particles = "MolotovFireball";
};

datablock ParticleData(MolotovVolume)
{
   textureName          = "~/data/shapes/particles/fxpack1/flame01";
   gravityCoefficient   = -0.3;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 400;
   spinRandomMin = -180.0;
   spinRandomMax =  180.0;
   useInvAlpha   = false;

   colors[0]     = "0.0 0.0 1.0 0.0";
   colors[1]     = "0.4 0.2 0.0 0.2";
   colors[2]     = "0.0 0.0 0.0 0.0";

   sizes[0]      = 2.0;
   sizes[1]      = 4.0;
   sizes[2]      = 8.0;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(MolotovVolumeEmitter)
{
   ejectionPeriodMS = 15;
   periodVarianceMS = 5;
   ejectionVelocity = 2.0;
   velocityVariance = 0.5;
   thetaMin         = 0.0;
   thetaMax         = 180.0;
   particles = "MolotovVolume";
};

datablock ParticleData(MolotovPoint)
{
   textureName          = "~/data/shapes/particles/fxpack1/flame02";
   gravityCoefficient   = -3.0;
   lifetimeMS           = 600;
   lifetimeVarianceMS   = 200;
   useInvAlpha =  false;
   spinRandomMin = -180.0;
   spinRandomMax =  180.0;

   colors[0]     = "1.0 0.9 0.8 0.9";
   colors[1]     = "0.8 0.4 0 0.2";
   colors[2]     = "0.0 0.0 0.0 0.0";

   sizes[0]      = 4.0;
   sizes[1]      = 1.0;
   sizes[2]      = 0.5;

   times[0]      = 0.0;
   times[1]      = 0.5;
   times[2]      = 1.0;
};

datablock ParticleEmitterData(MolotovPointEmitter)
{
   ejectionPeriodMS = 80;
   periodVarianceMS = 30;
   ejectionVelocity = 6;
   velocityVariance = 0.5;
   thetaMin         = 0;
   thetaMax         = 80;
   phiReferenceVel  = 0;
   phiVariance      = 360;
   ejectionOffset   = 1;
   particles = "MolotovPoint";
};


//-----------------------------------------------------------------------------
//	Explosion
//-----------------------------------------------------------------------------


datablock ExplosionData(MolotovDebrisExplosion)
{
   emitter[0] = MolotovDebrisBurstEmitter;
};

datablock DebrisData(MolotovDebris)
{
   shapeFile = "~/data/shapes/explosiondebris/invisible.dts";
   emitters = "MolotovDebrisTrailEmitter";   
   explosion = MolotovDebrisExplosion;
   
   elasticity = 0.6;
   friction = 0.5;
   numBounces = 1;
   bounceVariance = 1;
   explodeOnMaxBounce = true;
   staticOnMaxBounce = false;
   snapOnMaxBounce = false;
   minSpinSpeed = 300;
   maxSpinSpeed = 700;
   render2D = false;
   lifetime = 1;
   lifetimeVariance = 0.2;
   velocity = 10;
   velocityVariance = 0;
   fade = false;
   useRadiusMass = true;
   baseRadius = 0.2;
   gravModifier = 5;
   terminalVelocity = 0;
   ignoreWater = false;
};


datablock ExplosionData(MolotovSubExplosion)
{
   lifeTimeMS = 80;
   offset = 0.2;
   emitter[0] = MolotovSparksEmitter;
};


datablock ExplosionData(MolotovExplosion)
{
   //soundProfile = CrossbowExplosionSound;
   lifeTimeMS = 100;

   // Volume particles
   particleEmitter = MolotovVolumeEmitter;
   particleDensity = 30;
   particleRadius = 2;

   // Point emission
   emitter[0] = MolotovPointEmitter;
   emitter[1] = MolotovSmokeEmitter;
   emitter[2] = MolotovSparksEmitter;
   emitter[3] = MolotovFireballEmitter;

   // Sub explosion objects
   subExplosion[0] = MolotovSubExplosion;
   
   // debris
   debris = MolotovDebris;
   debrisThetaMin = 0;
   debrisThetaMax = 60;
   debrisPhiMin = 0;
   debrisPhiMax = 360;
   debrisNum = 10;
   debrisNumVariance = 2;
   debrisVelocity = 1;
   debrisVelocityVariance = 0.5;
 
};


datablock ExplosionData(MolotovExplosionBig)
{
   //soundProfile = CrossbowExplosionSound;
   lifeTimeMS = 100;

   // Volume particles
   particleEmitter = MolotovVolumeEmitter;
   particleDensity = 30;
   particleRadius = 2;

   // Point emission
   emitter[0] = MolotovPointEmitter;
   emitter[1] = MolotovSmokeEmitter;
   emitter[2] = MolotovSparksEmitter;
   emitter[3] = MolotovFireballEmitter;

   // Sub explosion objects
   subExplosion[0] = MolotovExplosion;
   subExplosion[1] = MolotovExplosion;
   
   // debris
   debris = MolotovDebris;
   debrisThetaMin = 0;
   debrisThetaMax = 60;
   debrisPhiMin = 0;
   debrisPhiMax = 360;
   debrisNum = 10;
   debrisNumVariance = 2;
   debrisVelocity = 1;
   debrisVelocityVariance = 0.5;
 
};