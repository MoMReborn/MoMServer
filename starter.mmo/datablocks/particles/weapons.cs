//
// Weapon particle effects
//

//cluster

datablock ParticleData(WPN_PARTICLE_CLUSTER) 
{
   dragCoefficient = "0";
   windCoefficient = "0";
   gravityCoefficient = "0";
   inheritedVelFactor = "0";
   constantAcceleration = "0";
   lifetimeMS = "2912";
   lifetimeVarianceMS = "928";
   spinSpeed = "1";
   spinRandomMin = "-100";
   spinRandomMax = "100";
   useInvAlpha = "1";
   animateTexture = "0";
   framesPerSec = "1";
   textureName = "minions.of.mirth/data/spells/MLF/particles/MLF_leafA";
   animTexName[0] = "minions.of.mirth/data/spells/MLF/particles/MLF_leafA";
   colors[0] = "1.000000 1.000000 1.000000 0.000000";
   colors[1] = "1.000000 1.000000 1.000000 0.299213";
   colors[2] = "1.000000 1.000000 1.000000 0.000000";
   colors[3] = "1.000000 1.000000 1.000000 1.000000";
   sizes[0] = "0";
   sizes[1] = "0.03";
   sizes[2] = "0";
   sizes[3] = "1";
   times[0] = "0";
   times[1] = "0.5";
   times[2] = "1";
   times[3] = "1";
   dragCoeffiecient = "0.5";
};


datablock ParticleEmitterData(WPN_PARTICLE_CLUSTER_EMITTER)
{    
   ejectionPeriodMS = "40";
   periodVarianceMS = "0";
   ejectionVelocity = "0";
   velocityVariance = "0";
   ejectionOffset = "0.1";
   thetaMin = "0";
   thetaMax = "180";
   phiReferenceVel = "0";
   phiVariance = "360";
   overrideAdvance = "0";
   orientParticles = "0";
   orientOnVelocity = "0";
   particles = "WPN_PARTICLE_CLUSTER";
   lifetimeMS = "0";
   lifetimeVarianceMS = "0";
   useEmitterSizes = "0";
   useEmitterColors = "0";
   emitterType = "sprinkler";
   ejectionInvert = "0";
   fadeColor = "0";
   fadeSize = "0";
   fadeVelocity = "0";
   fadeOffset = "0";
   vector = "0 0 1";
   spreadMin = "0";
   spreadMax = "90";
   pathOrigin = "origin";
   radiusMin = "0";
   radiusMax = "1";
};





datablock ParticleData(WPN_PARTICLE_FACE1)
{
   dragCoefficient = "0";
   windCoefficient = "0";
   gravityCoefficient = "-0.021978";
   inheritedVelFactor = "0";
   constantAcceleration = "0";
   lifetimeMS = "3712";
   lifetimeVarianceMS = "1248";
   spinSpeed = "0.5";
   spinRandomMin = "-200";
   spinRandomMax = "200";
   useInvAlpha = "1";
   animateTexture = "0";
   framesPerSec = "1";
   textureName = "minions.of.mirth/data/shapes/particles/face1";
   animTexName[0] = "minions.of.mirth/data/shapes/particles/face1";
   colors[0] = "1.000000 1.000000 1.000000 0.000000";
   colors[1] = "1.000000 1.000000 1.000000 0.150000";
   colors[2] = "1.000000 1.000000 1.000000 0.000000";
   colors[3] = "1.000000 1.000000 1.000000 1.000000";
   sizes[0] = "0";
   sizes[1] = "0.18";
   sizes[2] = "0";
   sizes[3] = "1";
   times[0] = "0";
   times[1] = "0.51";
   times[2] = "1";
   times[3] = "1";
   dragCoeffiecient = "0.5";
};

datablock ParticleData(WPN_PARTICLE_FACE2)
{
   dragCoefficient = "0";
   windCoefficient = "0";
   gravityCoefficient = "-0.021978";
   inheritedVelFactor = "0";
   constantAcceleration = "0";
   lifetimeMS = "2922";
   lifetimeVarianceMS = "928";
   spinSpeed = "0.25";
   spinRandomMin = "-200";
   spinRandomMax = "200";
   useInvAlpha = "1";
   animateTexture = "0";
   framesPerSec = "1";
   textureName = "minions.of.mirth/data/shapes/particles/face2";
   animTexName[0] = "minions.of.mirth/data/shapes/particles/face2";
   colors[0] = "1.000000 1.000000 1.000000 0.000000";
   colors[1] = "1.000000 1.000000 1.000000 0.150000";
   colors[2] = "1.000000 1.000000 1.000000 0.000000";
   colors[3] = "1.000000 1.000000 1.000000 1.000000";
   sizes[0] = "0";
   sizes[1] = "0.1";
   sizes[2] = "0.2";
   sizes[3] = "1";
   times[0] = "0";
   times[1] = "0.5";
   times[2] = "1";
   times[3] = "1";
      dragCoeffiecient = "0.5";
};

datablock ParticleData(WPN_PARTICLE_FACE3)
{
   dragCoefficient = "0";
   windCoefficient = "0";
   gravityCoefficient = "0";
   inheritedVelFactor = "0";
   constantAcceleration = "0";
   lifetimeMS = "2723";
   lifetimeVarianceMS = "1580";
   spinSpeed = "0";
   spinRandomMin = "-10";
   spinRandomMax = "10";
   useInvAlpha = "1";
   animateTexture = "0";
   framesPerSec = "1";
   textureName = "minions.of.mirth/data/shapes/particles/face3";
   animTexName[0] = "minions.of.mirth/data/shapes/particles/face3";
   colors[0] = "1.000000 1.000000 1.000000 0.000000";
   colors[1] = "1.000000 1.000000 1.000000 0.250000";
   colors[2] = "1.000000 1.000000 1.000000 0.000000";
   colors[3] = "1.000000 1.000000 1.000000 1.000000";
   sizes[0] = "0.06";
   sizes[1] = "0.25";
   sizes[2] = "0.4";
   sizes[3] = "1";
   times[0] = "0";
   times[1] = "0.46";
   times[2] = "1";
   times[3] = "1";
      dragCoeffiecient = "0.5";
};

datablock ParticleEmitterData(WPN_PARTICLE_FACE_EMITTER)
{    
   ejectionPeriodMS = "2000";
   periodVarianceMS = "1000";
   ejectionVelocity = "0.2";
   velocityVariance = "0";
   ejectionOffset = "0";
   thetaMin = "90";
   thetaMax = "180";
   phiReferenceVel = "0";
   phiVariance = "0";
   overrideAdvance = "0";
   orientParticles = "0";
   orientOnVelocity = "0";
   particles = "WPN_PARTICLE_FACE1\tWPN_PARTICLE_FACE2\tWPN_PARTICLE_FACE3";
   lifetimeMS = "0";
   lifetimeVarianceMS = "0";
   useEmitterSizes = "0";
   useEmitterColors = "0";
   emitterType = "sprinkler";
   ejectionInvert = "0";
   fadeColor = "0";
   fadeSize = "0";
   fadeVelocity = "0";
   fadeOffset = "0";
   vector = "0 0 0";
   spreadMin = "0";
   spreadMax = "90";
   pathOrigin = "origin";
   radiusMin = "0";
   radiusMax = "1";
};


datablock ParticleData(WPN_PARTICLE_LEAF)
{
   dragCoefficient = "0";
   windCoefficient = "0";
   gravityCoefficient = ".01";
   inheritedVelFactor = "0";
   constantAcceleration = "-0.1";
   lifetimeMS = "2922";
   lifetimeVarianceMS = "928";
   spinSpeed = "1";
   spinRandomMin = "-200";
   spinRandomMax = "200";
   useInvAlpha = "1";
   animateTexture = "0";
   framesPerSec = "1";
   textureName = "minions.of.mirth/data/spells/MLF/particles/MLF_leafA";
   colors[0] = "1.000000 1.000000 1.000000 0.000000";
   colors[1] = "1.000000 1.000000 1.000000 0.30000";
   colors[2] = "1.000000 1.000000 1.000000 0.000000";
   colors[3] = "1.000000 1.000000 1.000000 1.000000";
   sizes[0] = "0";
   sizes[1] = "0.05";
   sizes[2] = "0.075";
   sizes[3] = "1";
   times[0] = "0";
   times[1] = "0.5";
   times[2] = "1";
   times[3] = "1";
   dragCoeffiecient = "0.5";
};


datablock ParticleEmitterData(WPN_PARTICLE_LEAF_EMITTER)
{    
   ejectionPeriodMS = "250";
   periodVarianceMS = "125";
   ejectionVelocity = "0.25";
   velocityVariance = "0";
   ejectionOffset = "0";
   thetaMin = "0";
   thetaMax = "180";
   phiReferenceVel = "0";
   phiVariance = "360";
   overrideAdvance = "0";
   orientParticles = "0";
   orientOnVelocity = "0";
   particles = "WPN_PARTICLE_LEAF";
   lifetimeMS = "0";
   lifetimeVarianceMS = "0";
   useEmitterSizes = "0";
   useEmitterColors = "0";
   emitterType = "sprinkler";
   ejectionInvert = "0";
   fadeColor = "0";
   fadeSize = "0";
   fadeVelocity = "0";
   fadeOffset = "0";
   vector = "0 0 1";
   spreadMin = "0";
   spreadMax = "90";
   pathOrigin = "origin";
   radiusMin = "0";
   radiusMax = "1";
};


datablock ParticleData(WPN_PSYCHO_P1)
{
   textureName          = "~/data/spells/tests/zodiacs/crop1_zode";
   dragCoeffiecient     = 0.0;
   gravityCoefficient   = 0.0;
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 100;
   useInvAlpha          = false;
   spinRandomMin        = 800.0;
   spinRandomMax        = 800.0;
   colors[0]            = "0.0 0.5 1.0 0.3";
   colors[1]            = "1.0 0.2 0.0 0.0";
   sizes[0]             = 0.1;
   sizes[1]             = 0.2;
   times[0]             = 0.0;
   times[1]             = 1.0;
};

datablock ParticleData(WPN_PSYCHO_P2)
{
   textureName          = "~/data/spells/tests/zodiacs/crop2_zode";
   dragCoeffiecient     = 0.0;
   gravityCoefficient   = 0.0;
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 100;
   useInvAlpha          = false;
   spinRandomMin        = 800.0;
   spinRandomMax        = 800.0;
   colors[0]            = "0.0 0.5 1.0 0.3";
   colors[1]            = "1.0 0.2 0.0 0.0";
   sizes[0]             = 0.1;
   sizes[1]             = 0.2;
   times[0]             = 0.0;
   times[1]             = 1.0;
};

datablock ParticleData(WPN_PSYCHO_P3)
{
   textureName          = "~/data/spells/tests/zodiacs/crop3_zode";
   dragCoeffiecient     = 0.0;
   gravityCoefficient   = 0.0;
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 100;
   useInvAlpha          = false;
   spinRandomMin        = 800.0;
   spinRandomMax        = 800.0;
   colors[0]            = "0.0 0.5 1.0 0.3";
   colors[1]            = "1.0 0.2 0.0 0.0";
   sizes[0]             = 0.1;
   sizes[1]             = 0.2;
   times[0]             = 0.0;
   times[1]             = 1.0;
};

datablock ParticleEmitterData(WPN_PARTICLE_PSYCHO_EMITTER)
{
  ejectionPeriodMS      = 100;
  periodVarianceMS      = 0;
  ejectionVelocity      = 0.2;
  velocityVariance      = 0.1;
  thetaMin              = 0;
  thetaMax              = 180;
  phiReferenceVel       = 90;
  phiVariance           = 180;
  particles             = "WPN_PSYCHO_P1\tWPN_PSYCHO_P2\tWPN_PSYCHO_P3";
};

// 
// Sparkles!
// 
//

datablock ParticleData(WPN_PARTICLE_SPARKLE_P1)
{
   textureName          = "~/data/shapes/particles/skull";
   dragCoeffiecient     = 0.5;
   windCoefficient = "0";
   gravityCoefficient   = 0.05;
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 800;
   lifetimeVarianceMS   = 200;
   useInvAlpha          = false;
   spinRandomMin        = -360.0;
   spinRandomMax        = 360.0;
   colors[0]            = "1.0 1.0 1.0 0.0";
   colors[1]            = "1.0 1.0 1.0 0.35";
   colors[2]            = "1.0 1.0 1.0 0.35";
   colors[3]            = "1.0 1.0 1.0 0.0";
   sizes[0]             = 0.025;
   sizes[1]             = 0.025;
   sizes[2]             = 0.025;
   sizes[3]             = 0.025;
   times[0]             = 0.0;
   times[1]             = 0.3;
   times[2]             = 0.7;
   times[3]             = 1.0;
};
datablock ParticleData(WPN_PARTICLE_SPARKLE_P2)
{
   textureName          = "~/data/spells/shared/particles/sparkle";
   dragCoeffiecient     = 0.5;
   gravityCoefficient   = 0.0;
   windCoefficient = "0";
   inheritedVelFactor   = 0.00;
   lifetimeMS           = 600;
   lifetimeVarianceMS   = 200;
   useInvAlpha          = false;
   spinRandomMin        = 0.0;
   spinRandomMax        = 0.0;
   colors[0]            = "1.0 1.0 1.0 1.0";
   colors[1]            = "0.5 1.0 0.5 1.0";
   colors[2]            = "0.0 1.0 0.0 1.0";
   sizes[0]             = 0.025;
   sizes[1]             = 0.02;
   sizes[2]             = 0.01;
   times[0]             = 0.0;
   times[1]             = 0.3;
   times[2]             = 1.0;
};

datablock ParticleEmitterData(WPN_PARTICLE_SPARKLE_EMITTER)
{
  ejectionOffset        = 0.01;
  ejectionPeriodMS      = 10;
  periodVarianceMS      = 0;
  ejectionVelocity      = 0.2;
  velocityVariance      = 0.1;
  thetaMin              = 0.0;
  thetaMax              = 180.0;
  particles             = "WPN_PARTICLE_SPARKLE_P1\tWPN_PARTICLE_SPARKLE_P2";
};

