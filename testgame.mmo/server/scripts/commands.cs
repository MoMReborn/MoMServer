//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------
// Misc. server commands avialable to clients
//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------

function serverCmdToggleCamera(%client)
{
   if (%client.player.role !$= "Guardian" && %client.player.role !$= "Immortal")
       return;

   %control = %client.getControlObject();
   if (%control == %client.player)
   {
      %control = %client.camera;
      %control.mode = toggleCameraFly;
   }
   else
   {
      %control = %client.player;
      %control.mode = observerFly;
   }
   %client.setControlObject(%control);
}

function serverCmdDropPlayerAtCamera(%client)
{
   if ($Server::TestCheats || isObject(EditorGui))
   {
      %client.player.setTransform(%client.camera.getTransform());
      %client.player.setVelocity("0 0 0");
      %client.setControlObject(%client.player);
   }
}

function serverCmdDropCameraAtPlayer(%client)
{
   %client.camera.setTransform(%client.player.getEyeTransform());
   %client.camera.setVelocity("0 0 0");
   %client.setControlObject(%client.camera);
}


//-----------------------------------------------------------------------------

function serverCmdSuicide(%client)
{
   if (isObject(%client.player))
      %client.player.kill("Suicide");
}   

function serverCmdPlayCel(%client,%anim)
{
   if (isObject(%client.player))
      %client.player.playCelAnimation(%anim);
}

function serverCmdPlayDeath(%client)
{
   if (isObject(%client.player))
      %client.player.playDeathAnimation();
}

function ServerSpawnExplosion(%profile,%transform,%onground)
{
	for(%idx = 0; %idx < ClientGroup.getCount(); %idx++)
		ClientGroup.getObject(%idx).spawnExplosion(%profile,%transform,%onground);
}
