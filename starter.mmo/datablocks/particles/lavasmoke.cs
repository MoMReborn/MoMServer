//-----------------------------------------------------------------------------
// Torque Game Engine
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

////////////////////////////////////////////////////////////////////////////////
//------------ HighLavaShooters --- Added By T.Pickens 01/01/06 ------------- //
////////////////////////////////////////////////////////////////////////////////

//////////////////////////////// HighLavaShooter01 /////////////////////////////
datablock ParticleData(HighLavaShooter01)
{
   textureName          = "~/data/shapes/particles/lavashooter01";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 2.0; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 4000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 3500; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -100.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 100.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.5; // Scale for each Particle at each time value//
   sizes[1]      = 1.0; // Scale for each Particle at each time value//
   sizes[2]      = 1.5; // Scale for each Particle at each time value//
   sizes[3]      = 2.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////  HighLavaShooter02 ////////////////////////////////////////////
datablock ParticleData(HighLavaShooter02)
{
   textureName          = "~/data/shapes/particles/lavashooter02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 2.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 4000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 3500; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -100.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 100.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.5; // Scale for each Particle at each time value//
   sizes[1]      = 1.0; // Scale for each Particle at each time value//
   sizes[2]      = 1.5; // Scale for each Particle at each time value//
   sizes[3]      = 2.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////  HighLavaShooter03 ////////////////////////////////////////////
datablock ParticleData(HighLavaShooter03)
{
   textureName          = "~/data/shapes/particles/lavashooter03";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 6.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 2000; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -100.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 100.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 1.0; // Scale for each Particle at each time value//
   sizes[1]      = 2.0; // Scale for each Particle at each time value//
   sizes[2]      = 2.5; // Scale for each Particle at each time value//
   sizes[3]      = 3.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};
////////////////////////// HighLavaShooter04 ///////////////////////////////////
datablock ParticleData(HighLavaShooter04)
{
   textureName          = "~/data/shapes/particles/lavashooter04";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 6.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 0.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 2000; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -80.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 80.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 1.0; // Scale for each Particle at each time value//
   sizes[1]      = 2.0; // Scale for each Particle at each time value//
   sizes[2]      = 2.5; // Scale for each Particle at each time value//
   sizes[3]      = 3.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

datablock ParticleEmitterData(HighLavaShooterEmitter)
{
   ejectionPeriodMS = 50; // The frequency with which to emit particles //
   periodVarianceMS = 49;  // The variance of ejectionPeriodMs //

   ejectionVelocity = 60.0; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 40.0; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 0.0; // distance of offset from emitter 0-655 //

   thetaMin         = 10.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 180.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 0; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //

   particles = "HighLavaShooter01" TAB "HighLavaShooter02" TAB "HighLavaShooter03" TAB "HighLavaShooter04"; //Links Particles//
};

datablock ParticleEmitterNodeData(HighLavaShooterEmitterNode)
{
   timeMultiple = 1;
};

////////////////////////////////////////////////////////////////////////////////
//------------- LowLavaShooters --- Added By T.Pickens 01/01/06 ------------- //
////////////////////////////////////////////////////////////////////////////////

//////////////////////////////// LowLavaShooter01 //////////////////////////////
datablock ParticleData(LavaShooter01)
{
   textureName          = "~/data/shapes/particles/lavashooter01";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 2.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3500; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -100.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 100.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 2.0; // Scale for each Particle at each time value//
   sizes[1]      = 3.0; // Scale for each Particle at each time value//
   sizes[2]      = 4.5; // Scale for each Particle at each time value//
   sizes[3]      = 6.75; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////  LowLavaShooter02 /////////////////////////////////////////////
datablock ParticleData(LavaShooter02)
{
   textureName          = "~/data/shapes/particles/lavashooter02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 2.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3500; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -100.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 100.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 1.0; // Scale for each Particle at each time value//
   sizes[1]      = 1.5; // Scale for each Particle at each time value//
   sizes[2]      = 2.25; // Scale for each Particle at each time value//
   sizes[3]      = 3.40; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////  LowLavaShooter03 /////////////////////////////////////////////
datablock ParticleData(LavaShooter03)
{
   textureName          = "~/data/shapes/particles/lavashooter03";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 4.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3500; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -100.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 100.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 0.3 0 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 0.6 0.3 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 2.0; // Scale for each Particle at each time value//
   sizes[1]      = 3.0; // Scale for each Particle at each time value//
   sizes[2]      = 4.5; // Scale for each Particle at each time value//
   sizes[3]      = 6.75; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};
////////////////////////// LowLavaShooter04 ////////////////////////////////////
datablock ParticleData(LavaShooter04)
{
   textureName          = "~/data/shapes/particles/lavashooter04";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 6.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 0.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 200; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -80.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 80.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 3.0; // Scale for each Particle at each time value//
   sizes[1]      = 4.5; // Scale for each Particle at each time value//
   sizes[2]      = 5.5; // Scale for each Particle at each time value//
   sizes[3]      = 3.5; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

datablock ParticleEmitterData(LavaShooterEmitter)
{
   ejectionPeriodMS = 50; // The frequency with which to emit particles //
   periodVarianceMS = 49;  // The variance of ejectionPeriodMs //

   ejectionVelocity = 135.0; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 25.0; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 0.0; // distance of offset from emitter 0-655 //

   thetaMin         = 10.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 180.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 0; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //

   particles = "LavaShooter01" TAB "LavaShooter02" TAB "LavaShooter03" TAB "LavaShooter04"; //Links Particles//
};

datablock ParticleEmitterNodeData(LavaShooterEmitterNode)
{
   timeMultiple = 1;
};

////////////////////////////////////////////////////////////////////////////////
//-------------- Lava Explosions --- Added By T.Pickens 01/01/06 -------------//
////////////////////////////////////////////////////////////////////////////////

////////////////////////// LavaExplosion01 /////////////////////////////////////
datablock ParticleData(LavaExplosion01)
{
   textureName          = "~/data/shapes/particles/lavaexplosion01";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 4.0; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 0.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 200; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -40.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.1; // Scale for each Particle at each time value//
   sizes[1]      = 22.5; // Scale for each Particle at each time value//
   sizes[2]      = 45.0; // Scale for each Particle at each time value//
   sizes[3]      = 49.5; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////////////// LavaExplosion02 /////////////////////////////////////
datablock ParticleData(LavaExplosion02)
{
   textureName          = "~/data/shapes/particles/lavaexplosion02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 4.0; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 0.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 200; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -40.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.1; // Scale for each Particle at each time value//
   sizes[1]      = 22.5; // Scale for each Particle at each time value//
   sizes[2]      = 45.0; // Scale for each Particle at each time value//
   sizes[3]      = 49.5; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////////////// LavaExplosion03 /////////////////////////////////////
datablock ParticleData(LavaExplosion03)
{
   textureName          = "~/data/shapes/particles/lavaexplosion03";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 4.0; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 0.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 200; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -40.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // Particle's Max spin speed -10,000 to 10,000 //


   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.1; // Scale for each Particle at each time value//
   sizes[1]      = 22.5; // Scale for each Particle at each time value//
   sizes[2]      = 45.0; // Scale for each Particle at each time value//
   sizes[3]      = 49.5; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////////////// LavaExplosion04 /////////////////////////////////////
datablock ParticleData(LavaExplosion04)
{
   textureName          = "~/data/shapes/particles/lavaexplosion04";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 4.0; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 0.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 200; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -40.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.1; // Scale for each Particle at each time value//
   sizes[1]      = 22.5; // Scale for each Particle at each time value//
   sizes[2]      = 45.0; // Scale for each Particle at each time value//
   sizes[3]      = 49.5; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////////////// LavaExplosion05 /////////////////////////////////////
datablock ParticleData(LavaExplosion05)
{
   textureName          = "~/data/shapes/particles/lavaexplosion05";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 4.0; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 0.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 200; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -40.0; // Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // Particle's Max spin speed -10,000 to 10,000 //


   colors[0]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.1; // Scale for each Particle at each time value//
   sizes[1]      = 22.5; // Scale for each Particle at each time value//
   sizes[2]      = 45.0; // Scale for each Particle at each time value//
   sizes[3]      = 49.5; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};


datablock ParticleEmitterData(LavaExplosionEmitter)
{
   ejectionPeriodMS = 1000; // The frequency with which to emit particles //
   periodVarianceMS = 300;  // The variance of ejectionPeriodMs //

   ejectionVelocity = 15.0; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 10.0; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 0.0; // distance of offset from emitter 0-655 //

   thetaMin         = 0.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 10.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 0; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //

   particles = "LavaExplosion01" TAB "LavaExplosion02" TAB "LavaExplosion03" TAB "LavaExplosion04" TAB "LavaExplosion05";
};

datablock ParticleEmitterNodeData(LavaExplosionEmitterNode)
{
   timeMultiple = 1;
};
////////////////////////////////////////////////////////////////////////////////
//------------- Spattering Lava --- Added By T.Pickens 01/01/06 --------------//
////////////////////////////////////////////////////////////////////////////////

////////////////  SpatteringLava01 /////////////////////////////////////////////
datablock ParticleData(SpatteringLava01)
{
   textureName          = "~/data/shapes/particles/lavaspatter01";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 2.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 2000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -70.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 70.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 0.3 0 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 0.6 0.3 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 0.5; // Scale for each Particle at each time value//
   sizes[1]      = 1.5; // Scale for each Particle at each time value//
   sizes[2]      = 3.0; // Scale for each Particle at each time value//
   sizes[3]      = 4.5; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.33; // Must be given in ascending order //
   times[2]      = 0.66; // Must be given in ascending order //
   times[3]      = 1.0;

};

////////////////  SpatteringLava02 /////////////////////////////////////////////
datablock ParticleData(SpatteringLava02)
{
   textureName          = "~/data/shapes/particles/lavaspatter02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = 2.5; // 1.0 = 100% gravity //
   windCoefficient = 0.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 2000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = false; // False = Additive I think //
   spinRandomMin = -70.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 70.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 0.3 0 1.0"; //Color used for the Particle each value//
   colors[1]     = "1 0.6 0.3 1.0"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 1.0; // Scale for each Particle at each time value//
   sizes[1]      = 3.0; // Scale for each Particle at each time value//
   sizes[2]      = 6.0; // Scale for each Particle at each time value//
   sizes[3]      = 9.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.33; // Must be given in ascending order //
   times[2]      = 0.66; // Must be given in ascending order //
   times[3]      = 1.0;

};

datablock ParticleEmitterData(SpatteringLavaEmitter)
{
   ejectionPeriodMS = 500; // The frequency with which to emit particles //
   periodVarianceMS = 400;  // The variance of ejectionPeriodMs //

   ejectionVelocity = 20.0; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 5.0; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 0.0; // distance of offset from emitter 0-655 //

   thetaMin         = 25.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 180.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 1; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //
   orientOnVelocity = true; //oriented on the velocity ?//

   particles = "SpatteringLava01" TAB "SpatteringLava02"; //Links Particles//
};

datablock ParticleEmitterNodeData(SpatteringLavaEmitterNode)
{
   timeMultiple = 1;
};


////////////////////////////////////////////////////////////////////////////////
//----------- VolcanoSmoke, Large --- Added By T.Pickens 01/01/06 ------------//
////////////////////////////////////////////////////////////////////////////////

//////////////// VolcanoSmokeLarge01 ///////////////////////////////////////////
datablock ParticleData(VolcanoSmokeLarge)
{
   textureName          = "~/data/shapes/particles/lavasmoke";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -1.5; // rises slowly
   windCoefficient = 1.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 5000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 0.3 0 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 0.6 0.3 0.7"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 44.5; // Scale for each Particle at each time value//
   sizes[1]      = 45.5; // Note:49.5 appears to be the max size allowed//
   sizes[2]      = 47.5; // Note:49.5 appears to be the max size allowed//
   sizes[3]      = 49.5; // Note:49.5 appears to be the max size allowed//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

datablock ParticleData(VolcanoSmokeLarge02)
{
   textureName          = "~/data/shapes/particles/lavasmoke02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -1.5; // rises slowly
   windCoefficient = 1.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 5000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 0.3 0 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 0.6 0.3 0.7"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 44.5; // Scale for each Particle at each time value//
   sizes[1]      = 45.5; // Note:49.5 appears to be the max size allowed//
   sizes[2]      = 47.5; // Note:49.5 appears to be the max size allowed//
   sizes[3]      = 49.5; // Note:49.5 appears to be the max size allowed//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

datablock ParticleEmitterData(VolcanoSmokeLargeEmitter)
{
   ejectionPeriodMS = 500; // The frequency with which to emit particles //
   periodVarianceMS = 200;  // The variance of ejectionPeriodMs //

   ejectionVelocity = 2.5; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 0.5; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 10.0; // distance of offset from emitter 0-655 //

   thetaMin         = 25.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 90.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 0; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //

   particles = "VolcanoSmokeLarge" TAB "VolcanoSmokeLarge02";
};

datablock ParticleEmitterNodeData(VolcanoSmokeLargeEmitterNode)
{
   timeMultiple = 1;
};

////////////////////////////////////////////////////////////////////////////////
//------------- VolcanoSmoke, Small --- Added By T.Pickens 01/01/06 ----------//
////////////////////////////////////////////////////////////////////////////////

//////////////// VolcanoSmokeSmall01 ///////////////////////////////////////////
datablock ParticleData(VolcanoSmokeSmall)
{
   textureName          = "~/data/shapes/particles/lavasmoke";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -1.5; // rises slowly
   windCoefficient = 1.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 5000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 0.3 0 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 0.6 0.3 0.7"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 34.5; // Scale for each Particle at each time value//
   sizes[1]      = 35.5; // Note:49.5 appears to be the max size allowed//
   sizes[2]      = 37.5; // Note:49.5 appears to be the max size allowed//
   sizes[3]      = 39.5; // Note:49.5 appears to be the max size allowed//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

//////////////// VolcanoSmokeSmall02 ///////////////////////////////////////////
datablock ParticleData(VolcanoSmokeSmall02)
{
   textureName          = "~/data/shapes/particles/lavasmoke02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -1.5; // rises slowly
   windCoefficient = 1.0;
   inheritedVelFactor   = 1.0; // Multiple applied to the velocity //
   constantAcceleration = 0.0; //The amount of the initial velocity to be added to the velocity per second.
   lifetimeMS           = 5000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 0.3 0 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 0.6 0.3 0.7"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 1.0"; //Color used for the Particle each value//
   colors[3]     = "0 0 0 0.0"; //Color used for the Particle each value//

   sizes[0]      = 34.5; // Scale for each Particle at each time value//
   sizes[1]      = 35.5; // Note:49.5 appears to be the max size allowed//
   sizes[2]      = 37.5; // Note:49.5 appears to be the max size allowed//
   sizes[3]      = 39.5; // Note:49.5 appears to be the max size allowed//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;

};

datablock ParticleEmitterData(VolcanoSmokeSmallEmitter)
{
   ejectionPeriodMS = 500; // The frequency with which to emit particles //
   periodVarianceMS = 200;  // The variance of ejectionPeriodMs //

   ejectionVelocity = 2.5; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 0.5; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 10.0; // distance of offset from emitter 0-655 //

   thetaMin         = 25.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 90.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 0; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //

   particles = "VolcanoSmokeSmall" TAB "VolcanoSmokeSmall02";
};

datablock ParticleEmitterNodeData(VolcanoSmokeSmallEmitterNode)
{
   timeMultiple = 1;
};

////////////////////////////////////////////////////////////////////////////////
//--------- Lava Smoke, Medium --- Added By T.Pickens 01/01/06 ---------------//
////////////////////////////////////////////////////////////////////////////////

//////////////// LavaSmokeMedium01 /////////////////////////////////////////////
datablock ParticleData(LavaSmokeMedium)
{
   textureName          = "~/data/shapes/particles/lavasmoke";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -0.1; // rises slowly
   inheritedVelFactor   = 0.00; // Multiple applied to the velocity //
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 0.3"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 0.4"; //Color used for the Particle each value//
   colors[3]     = "1 1 1 0.0"; //Color used for the Particle each value//

   sizes[0]      = 17.5; // Scale for each Particle at each time value//
   sizes[1]      = 15.5; // Scale for each Particle at each time value//
   sizes[2]      = 11.5; // Scale for each Particle at each time value//
   sizes[3]      = 10.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;
};

//////////////// LavaSmokeMedium02 /////////////////////////////////////////////
datablock ParticleData(LavaSmokeMedium02)
{
   textureName          = "~/data/shapes/particles/lavasmoke02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -0.1; // rises slowly
   inheritedVelFactor   = 0.00; // Multiple applied to the velocity //
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 0.3"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 0.4"; //Color used for the Particle each value//
   colors[3]     = "1 1 1 0.0"; //Color used for the Particle each value//

   sizes[0]      = 17.5; // Scale for each Particle at each time value//
   sizes[1]      = 15.5; // Scale for each Particle at each time value//
   sizes[2]      = 11.5; // Scale for each Particle at each time value//
   sizes[3]      = 10.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;
};

datablock ParticleEmitterData(LavaSmokeMediumEmitter)
{
   ejectionPeriodMS = 500; // The frequency with which to emit particles //
   periodVarianceMS = 100;  // Must be less than ejectionPeriodMS //

   ejectionVelocity = 2.0; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 1.0; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 0.0; // distance of offset from emitter 0-655 //

   thetaMin         = 0.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 1.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 0; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //

   particles = "LavaSmokeMedium" TAB "LavaSmokeMedium02";
};

datablock ParticleEmitterNodeData(LavaSmokeMediumEmitterNode)
{
   timeMultiple = 1;
};

////////////////////////////////////////////////////////////////////////////////
//--------- Lava Smoke, Small --- Added By T.Pickens 01/01/06 ----------------//
////////////////////////////////////////////////////////////////////////////////

//////////////// LavaSmokeSmall01 //////////////////////////////////////////////
datablock ParticleData(LavaSmokeSmall)
{
   textureName          = "~/data/shapes/particles/lavasmoke";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -0.1; // rises slowly
   inheritedVelFactor   = 0.00; // Multiple applied to the velocity //
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 0.3"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 0.4"; //Color used for the Particle each value//
   colors[3]     = "1 1 1 0.0"; //Color used for the Particle each value//

   sizes[0]      = 12.5; // Scale for each Particle at each time value//
   sizes[1]      = 10.5; // Scale for each Particle at each time value//
   sizes[2]      = 6.5; // Scale for each Particle at each time value//
   sizes[3]      = 5.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;
};

//////////////// LavaSmokeSmall02 //////////////////////////////////////////////
datablock ParticleData(LavaSmokeSmall02)
{
   textureName          = "~/data/shapes/particles/lavasmoke02";
   dragCoefficient     = 0.0; // Drag of a particle, must be non-negative//
   gravityCoefficient   = -0.1; // rises slowly
   inheritedVelFactor   = 0.00; // Multiple applied to the velocity //
   lifetimeMS           = 3000; // life-time of each emitted particle in milsec //
   lifetimeVarianceMS   = 500; // Must not be greater than lifetimeMS //
   useInvAlpha = true; // False = Additive I think //
   spinRandomMin = -40.0; // (left) Particle's Min spin speed -10,000 to 10,000 //
   spinRandomMax = 40.0; // (right) Particle's Max spin speed -10,000 to 10,000 //

   colors[0]     = "1 1 1 0.0"; //Color used for the Particle each value//
   colors[1]     = "1 1 1 0.3"; //Color used for the Particle each value//
   colors[2]     = "1 1 1 0.4"; //Color used for the Particle each value//
   colors[3]     = "1 1 1 0.0"; //Color used for the Particle each value//

   sizes[0]      = 12.5; // Scale for each Particle at each time value//
   sizes[1]      = 10.5; // Scale for each Particle at each time value//
   sizes[2]      = 6.5; // Scale for each Particle at each time value//
   sizes[3]      = 5.0; // Scale for each Particle at each time value//

   times[0]      = 0.0; // Must be given in ascending order //
   times[1]      = 0.20; // Must be given in ascending order //
   times[2]      = 0.40; // Must be given in ascending order //
   times[3]      = 1.0;
};

datablock ParticleEmitterData(LavaSmokeSmallEmitter)
{
   ejectionPeriodMS = 350; // The frequency with which to emit particles //
   periodVarianceMS = 100;  // Must be less than ejectionPeriodMS //

   ejectionVelocity = 1.0; // Initial velocity a particle is emitted 0-655 //
   velocityVariance = 0.5; //  Must not be neg. or > ejectionVelocity 0-163//

   ejectionOffset   = 0.0; // distance of offset from emitter 0-655 //

   thetaMin         = 0.0; // Ejection angle relative to the x-axis 0-180//
   thetaMax         = 1.0; // Ejection angle relative to the x-axis 0-180//

   phiReferenceVel  = 0; // Ejection angle about the z-axis over time 0-360 //
   phiVariance      = 360; // Ejection angle about the z-axis over time 0-360 //

   overrideAdvance = false; // True = particle's time/advanc is init. deferred //
   orientParticles  = false; // True = oriented toward the emission direction //
   orientToXY  = false;    //Greg M. made it so particles always face camera //

   particles = "LavaSmokeSmall" TAB "LavaSmokeSmall02";
};

datablock ParticleEmitterNodeData(LavaSmokeSmallEmitterNode)
{
   timeMultiple = 1;
};

////////////////////////////////////////////////////////////////////////////////
//-------------- Lava Light Medium -- for creating glow from the lava --------//
//---------------- based on fxlight created by Melv May ----------------------//
////////////////////////////////////////////////////////////////////////////////

///////////////////////////// LavaLightHuge ////////////////////////////////////
datablock fxLightData(LavaLightHuge)
{
   LightOn = true;
   Radius = 45.0;
   Brightness = 1.0;
   Colour = "1.0 0.432 0.063";
};

//////////////////////////// LavaLightLarge ////////////////////////////////////
datablock fxLightData(LavaLightlarge)
{
   LightOn = true;
   Radius = 30.0;
   Brightness = 1.0;
   Colour = "1.0 0.432 0.063";
};

//////////////////////////// LavaLightMedium ///////////////////////////////////
datablock fxLightData(LavaLightMedium)
{
   LightOn = true;
   Radius = 20.0;
   Brightness = 1.0;
   Colour = "1.0 0.432 0.063";
};

//////////////////////////// LavaLightSmall ////////////////////////////////////
datablock fxLightData(LavaLightSmall)
{
   LightOn = true;
   Radius = 10.0;
   Brightness = 1.0;
   Colour = "1.0 0.432 0.063";
};

//////////////////////////// LavaLightTiny /////////////////////////////////////
datablock fxLightData(LavaLightTiny)
{
   LightOn = true;
   Radius = 5.0;
   Brightness = 1.0;
   Colour = "0.8 0.3 0";
};

////////////////////////////////////////////////////////////////////////////////
//----------------------------- fxDefaultLight -------------------------------//
//--------------------------- created by Melv May ----------------------------//
////////////////////////////////////////////////////////////////////////////////

//////////////////////////// fxDefaultLight ////////////////////////////////////
datablock fxLightData(fxDefaultLight)
{
   LightOn = true;
   Radius = 30.0;
   Brightness = 1.0;
   Colour = "0.8 0.3 0";

   FlareOn = true;
   FlareTP = true;
   FlareBitmap = "common/lighting/corona";
   FlareColour = "1 1 1";
   ConstantSizeOn = false;
   ConstantSize = 1.0;
   NearSize = 3.0;
   FarSize = 0.5;
   NearDistance = 10.0;
   FarDistance = 30.0;
   FadeTime = 0.1;
   BlendMode = 0;

   AnimColour = false;
   AnimBrightness = false;
   AnimRadius = false;
   AnimOffset = false;
   AnimRotation = false;
   LinkFlare = true;
   LinkFlareSize = false;
   MinColour = "0 0 0";
   MaxColour = "1 1 1";
   MinBrightness = 0.0;
   MaxBrightness = 1.0;
   MinRadius = 0.1;
   MaxRadius = 20.0;
   StartOffset = "-5 0 0";
   EndOffset = "5 0 0";
   MinRotation = 0;
   MaxRotation = 350;
   SingleColourKeys = true;
   RedKeys = "AZA";
   GreenKeys = "AZA";
   BlueKeys = "AZA";
   BrightnessKeys = "AZA";
   RadiusKeys = "AZA";
   OffsetKeys = "AZA";
   RotationKeys = "AZA";
   ColourTime = 1.0;
   BrightnessTime = 1.0;
   RadiusTime = 5.0;
   OffsetTime = 5.0;
   RotationTime = 5.0;
   LerpColour = true;
   LerpBrightness = true;
   LerpRadius = true;
   LerpOffset = true;
   LerpRotation = true;
};


