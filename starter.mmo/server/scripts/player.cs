//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

// Load dts shapes and merge animations
//exec("~/data/shapes/player/player.cs");

// Timeouts for corpse deletion.
$CorpseTimeoutValue = 22 * 1000;

// Damage Rate for entering Liquid
$DamageLava       = 0.01;
$DamageHotLava    = 0.01;
$DamageCrustyLava = 0.01;

//
$PlayerDeathAnim::TorsoFrontFallForward = 1;
$PlayerDeathAnim::TorsoFrontFallBack = 2;
$PlayerDeathAnim::TorsoBackFallForward = 3;
$PlayerDeathAnim::TorsoLeftSpinDeath = 4;
$PlayerDeathAnim::TorsoRightSpinDeath = 5;
$PlayerDeathAnim::LegsLeftGimp = 6;
$PlayerDeathAnim::LegsRightGimp = 7;
$PlayerDeathAnim::TorsoBackFallForward = 8;
$PlayerDeathAnim::HeadFrontDirect = 9;
$PlayerDeathAnim::HeadBackFallForward = 10;
$PlayerDeathAnim::ExplosionBlowBack = 11;


//----------------------------------------------------------------------------
// Player Audio Profiles
//----------------------------------------------------------------------------







//----------------------------------------------------------------------------
// Armor Datablock methods
//----------------------------------------------------------------------------

//----------------------------------------------------------------------------

function Armor::onAdd(%this,%obj)
{
   // Vehicle timeout
   %obj.mountVehicle = true;

   // Default dynamic armor stats
   %obj.setRechargeRate(%this.rechargeRate);
   %obj.setRepairRate(0);
}

function Armor::onRemove(%this, %obj)
{
   if (%obj.client.player == %obj)
      %obj.client.player = 0;
}

function Armor::onNewDataBlock(%this,%obj)
{
}


//----------------------------------------------------------------------------

function Armor::onMount(%this,%obj,%vehicle,%node)
{
   if (%node == 0)  {
      %obj.setTransform("0 0 0 0 0 1 0");
      %obj.setActionThread(%vehicle.getDatablock().mountPose[%node],true,true);
      %obj.lastWeapon = %obj.getMountedImage($WeaponSlot);

      %obj.unmountImage($WeaponSlot);
      %obj.setControlObject(%vehicle);
      %obj.client.setObjectActiveImage(%vehicle, 2);
   }
}

function Armor::onUnmount( %this, %obj, %vehicle, %node )
{
   if (%node == 0)
      %obj.mountImage(%obj.lastWeapon, $WeaponSlot);
}

function Armor::doDismount(%this, %obj, %forced)
{
   // This function is called by player.cc when the jump trigger
   // is true while mounted
   if (!%obj.isMounted())
      return;

   // Position above dismount point
   %pos    = getWords(%obj.getTransform(), 0, 2);
   %oldPos = %pos;
   %vec[0] = " 0  0  1";
   %vec[1] = " 0  0  1";
   %vec[2] = " 0  0 -1";
   %vec[3] = " 1  0  0";
   %vec[4] = "-1  0  0";
   %impulseVec  = "0 0 0";
   %vec[0] = MatrixMulVector( %obj.getTransform(), %vec[0]);

   // Make sure the point is valid
   %pos = "0 0 0";
   %numAttempts = 5;
   %success     = -1;
   for (%i = 0; %i < %numAttempts; %i++) {
      %pos = VectorAdd(%oldPos, VectorScale(%vec[%i], 3));
      if (%obj.checkDismountPoint(%oldPos, %pos)) {
         %success = %i;
         %impulseVec = %vec[%i];
         break;
      }
   }
   if (%forced && %success == -1)
      %pos = %oldPos;

   %obj.mountVehicle = false;
   %obj.schedule(4000, "mountVehicles", true);

   // Position above dismount point
   %obj.setTransform(%pos);
   %obj.applyImpulse(%pos, VectorScale(%impulseVec, %obj.getDataBlock().mass));
   %obj.setPilot(false);
   %obj.vehicleTurret = "";
}


//----------------------------------------------------------------------------

function Armor::onCollision(%this,%obj,%col)
{
   if (%obj.getState() $= "Dead")
      return;

   // Try and pickup all items
   if (%col.getClassName() $= "Item")
      %obj.pickup(%col);

   // Mount vehicles
   %this = %col.getDataBlock();
   if ((%this.className $= WheeledVehicleData) && %obj.mountVehicle &&
         %obj.getState() $= "Move" && %col.mountable) {

      // Only mount drivers for now.
      %node = 0;
      %col.mountObject(%obj,%node);
      %obj.mVehicle = %col;
   }
}

function Armor::onImpact(%this, %obj, %collidedObject, %vec, %vecLen)
{
   %obj.damage(0, VectorAdd(%obj.getPosition(),%vec),
      %vecLen * %this.speedDamageScale, "Impact");
}


//----------------------------------------------------------------------------

function Armor::damage(%this, %obj, %sourceObject, %position, %damage, %damageType)
{
   if (%obj.getState() $= "Dead")
      return;
   %obj.applyDamage(%damage);
   %location = "Body";

   // Deal with client callbacks here because we don't have this
   // information in the onDamage or onDisable methods
   %client = %obj.client;
   %sourceClient = %sourceObject ? %sourceObject.client : 0;

   if (%obj.getState() $= "Dead")
      %client.onDeath(%sourceObject, %sourceClient, %damageType, %location);
}

function Armor::onDamage(%this, %obj, %delta)
{
   // This method is invoked by the ShapeBase code whenever the 
   // object's damage level changes.
   if (%delta > 0 && %obj.getState() !$= "Dead") {

      // Increment the flash based on the amount.
      %flash = %obj.getDamageFlash() + ((%delta / %this.maxDamage) * 2);
      if (%flash > 0.75)
         %flash = 0.75;
      %obj.setDamageFlash(%flash);

      // If the pain is excessive, let's hear about it.
      if (%delta > 10)
         %obj.playPain();
   }
}

function Armor::onDisabled(%this,%obj,%state)
{
   // The player object sets the "disabled" state when damage exceeds
   // it's maxDamage value.  This is method is invoked by ShapeBase
   // state mangement code.

   // If we want to deal with the damage information that actually
   // caused this death, then we would have to move this code into
   // the script "damage" method.
   //%obj.playDeathCry();
   //%obj.playDeathAnimation();
   //%obj.setDamageFlash(0.75);

   // Release the main weapon trigger
   //%obj.setImageTrigger(0,false);

   // Schedule corpse removal.  Just keeping the place clean.
   //%obj.schedule($CorpseTimeoutValue - 1000, "startFade", 1000, 0, true);
   //%obj.schedule($CorpseTimeoutValue, "delete");
}


//-----------------------------------------------------------------------------

function Armor::onLeaveMissionArea(%this, %obj)
{
   // Inform the client
   %obj.client.onLeaveMissionArea();
}

function Armor::onEnterMissionArea(%this, %obj)
{
   // Inform the client
   %obj.client.onEnterMissionArea();
}

//-----------------------------------------------------------------------------

function Armor::onEnterLiquid(%this, %obj, %coverage, %type)
{
   switch(%type)
   {
      case 0: //Water
      case 1: //Ocean Water
      case 2: //River Water
      case 3: //Stagnant Water
      case 4: //Lava
         %obj.setDamageDt(%this, $DamageLava, "Lava");
      case 5: //Hot Lava
         %obj.setDamageDt(%this, $DamageHotLava, "Lava");
      case 6: //Crusty Lava
         %obj.setDamageDt(%this, $DamageCrustyLava, "Lava");
      case 7: //Quick Sand
   }
}

function Armor::onLeaveLiquid(%this, %obj, %type)
{
   %obj.clearDamageDt();
}


//-----------------------------------------------------------------------------

function Armor::onTrigger(%this, %obj, %triggerNum, %val)
{
   // This method is invoked when the player receives a trigger
   // move event.  The player automatically triggers slot 0 and
   // slot one off of triggers # 0 & 1.  Trigger # 2 is also used
   // as the jump key.
}


//-----------------------------------------------------------------------------
// Player methods
//-----------------------------------------------------------------------------

//----------------------------------------------------------------------------

function Player::kill(%this, %damageType)
{
   %this.damage(0, %this.getPosition(), 10000, %damageType);
}


//----------------------------------------------------------------------------

function Player::mountVehicles(%this,%bool)
{
   // If set to false, this variable disables vehicle mounting.
   %this.mountVehicle = %bool;
}

function Player::isPilot(%this)
{
   %vehicle = %this.getObjectMount();
   // There are two "if" statements to avoid a script warning.
   if (%vehicle)
      if (%vehicle.getMountNodeObject(0) == %this)
         return true;
   return false;
}


//----------------------------------------------------------------------------

function Player::playDeathAnimation(%this)
{
   if (%this.deathIdx++ > 11)
      %this.deathIdx = 1;
   %this.setActionThread("Death" @ %this.deathIdx);
}

function Player::playCelAnimation(%this,%anim)
{
   if (%this.getState() !$= "Dead")
      %this.setActionThread("cel"@%anim);
}


//----------------------------------------------------------------------------

function Player::playDeathCry( %this )
{
   %this.playAudio(0,DeathCrySound);
}

function Player::playPain( %this )
{
   %this.playAudio(0,PainCrySound);
}



