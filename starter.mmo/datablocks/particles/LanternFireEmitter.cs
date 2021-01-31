//--- OBJECT WRITE BEGIN ---
datablock ParticleEmitterData(LanternFireEmitter) {
   className = "ParticleEmitterData";
   ejectionPeriodMS = "30";
   periodVarianceMS = "29";
   ejectionVelocity = "0.8";
   velocityVariance = "0";
   ejectionOffset = "0";
   thetaMin = "0";
   thetaMax = "14";
   phiReferenceVel = "0";
   phiVariance = "360";
   overrideAdvance = "0";
   orientParticles = "0";
   orientOnVelocity = "1";
   particles = "LanternFire";
   lifetimeMS = "0";
   lifetimeVarianceMS = "0";
   useEmitterSizes = "0";
   useEmitterColors = "0";
};
//--- OBJECT WRITE END ---

datablock ParticleEmitterNodeData(LanternFireEmitterNode)
{
   timeMultiple = 1;
};
