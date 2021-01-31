//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------


//------------------------------------------------------------------------------
// - serveral marker types may share MissionMarker datablock type
function MissionMarkerData::create(%block)
{
   switch$(%block)
   {
      case "WayPointMarker":
         %obj = new WayPoint() {
            dataBlock = %block;
         };
         return(%obj);
      case "SpawnSphereMarker":
         %obj = new SpawnSphere() {
            datablock = %block;
         };
         return(%obj);
      case "rpgSpawnPointMarker":
         %obj = new rpgSpawnPoint() {
            datablock = %block;
         };
         return(%obj);
      case "rpgWayPointMarker":
         %obj = new rpgWayPoint() {
            datablock = %block;
         };
         return(%obj);

      case "rpgBindPointMarker":
         %obj = new rpgBindPoint() {
            datablock = %block;
         };
         return(%obj);

   }
   return(-1);
}
