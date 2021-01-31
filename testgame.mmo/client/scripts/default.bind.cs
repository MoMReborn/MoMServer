//-----------------------------------------------------------------------------
// Torque Game Engine 
// Copyright (C) GarageGames.com, Inc.
//-----------------------------------------------------------------------------

if ( isObject( moveMap ) )
   moveMap.delete();
new ActionMap(moveMap);


//------------------------------------------------------------------------------
// Non-remapable binds
//------------------------------------------------------------------------------

function escapeFromGame()
{
   if ( $Server::ServerType $= "SinglePlayer" )
      MessageBoxYesNo( "Quit Mission", "Exit from this Mission?", "disconnect();", "");
   else
      MessageBoxYesNo( "Disconnect", "Disconnect from the server?", "disconnect();", "");
}

moveMap.bindCmd(keyboard, "escape", "", "ToggleGameOptionsWnd();");

function showPlayerList(%val)
{
   if (%val)
      PlayerListGui.toggle();
}

//moveMap.bind( keyboard, F2, showPlayerList );
moveMap.bind( keyboard, "ctrl F5", toggleParticleEditor);


//------------------------------------------------------------------------------
// Movement Keys
//------------------------------------------------------------------------------

$movementSpeed = 1; // m/s

function setSpeed(%speed)
{
   if(%speed)
      $movementSpeed = %speed;
}

function moveleft(%val)
{
   $mvLeftAction = %val * $movementSpeed;
}

function moveright(%val)
{
   $mvRightAction = %val * $movementSpeed;
}

function moveforward(%val)
{
   $mvForwardAction = %val * $movementSpeed;
}

function movebackward(%val)
{
   $mvBackwardAction = %val * $movementSpeed;
}

function moveup(%val)
{
   $mvUpAction = %val * $movementSpeed;
}

function movedown(%val)
{
   $mvDownAction = %val * $movementSpeed;
}

function turnLeft( %val )
{
   $mvYawRightSpeed = %val ? $Pref::Input::KeyboardTurnSpeed : 0;
}

function turnRight( %val )
{
   $mvYawLeftSpeed = %val ? $Pref::Input::KeyboardTurnSpeed : 0;
}

function panUp( %val )
{
   $mvPitchDownSpeed = %val ? $Pref::Input::KeyboardTurnSpeed : 0;
}

function panDown( %val )
{
   $mvPitchUpSpeed = %val ? $Pref::Input::KeyboardTurnSpeed : 0;
}

function getMouseAdjustAmount(%val)
{
   //0-1
   %val = %val * (($Pref::Input::MouseTurnSpeed*1.5)+0.25);
   return(%val * ($cameraFov / 90) * 0.01);
}

function yaw(%val)
{
   $mvYaw += getMouseAdjustAmount(%val);
}

function pitch(%val)
{
   if ($pref::InvertMouse)
      $mvPitch -= getMouseAdjustAmount(%val);
   else
      $mvPitch += getMouseAdjustAmount(%val);
}

function jump(%val)
{
   $mvTriggerCount2++;
}

moveMap.bind( keyboard, q, moveleft );
moveMap.bind( keyboard, e, moveright );
moveMap.bind( keyboard, w, moveforward );
moveMap.bind( keyboard, s, movebackward );
moveMap.bind( keyboard, a, turnleft );
moveMap.bind( keyboard, d, turnright );
moveMap.bind( keyboard, space, jump );
moveMap.bind( mouse, xaxis, yaw );
moveMap.bind( mouse, yaxis, pitch );


//------------------------------------------------------------------------------
// Mouse Trigger
//------------------------------------------------------------------------------

function mouseFire(%val)
{
   $mvTriggerCount0++;
}

function altTrigger(%val)
{
   $mvTriggerCount1++;
}

//moveMap.bind( mouse, button0, mouseFire );
//moveMap.bind( mouse, button1, altTrigger );


//------------------------------------------------------------------------------
// Zoom and FOV functions
//------------------------------------------------------------------------------

if($Pref::player::CurrentFOV $= "")
   $Pref::player::CurrentFOV = 45;

function setZoomFOV(%val)
{
   if(%val)
      toggleZoom();
}
      
function toggleZoom( %val )
{
   if ( %val )
      {
      $ZoomOn = true;
      setFov( $Pref::player::CurrentFOV );
   }
   else
   {
      $ZoomOn = false;
      setFov( $Pref::player::DefaultFov );
   }
}

//moveMap.bind(keyboard, "r", setZoomFOV);



//------------------------------------------------------------------------------
// Camera & View functions
//------------------------------------------------------------------------------

function toggleFreeLook( %val )
{
   if ( %val )
   {
      ToggleMouseLookBlah(true);
      $mvFreeLook = true;
   }
   else
   {

      ToggleMouseLookBlah(false);
      $mvFreeLook = false;
   }
}

function toggleFirstPerson(%val)
{
   if (%val)
   {
      $pref::firstPerson = !$pref::firstPerson;
   }
}

function toggleCamera(%val)
{
   if (%val)
      commandToServer('ToggleCamera');
}

//moveMap.bind( keyboard, "period", toggleFreeLook );
moveMap.bind( "mouse0", "button2", toggleFreeLook );
moveMap.bind(keyboard, "comma", toggleFirstPerson );
moveMap.bind(keyboard, "alt c", toggleCamera);

//Window Toggles
function InputTogglePartyWndInventory(%val)
{
    if (%val)
       return;

    TogglePartyWndInventory();
}
function InputTogglePartyWndSkills(%val)
{
    if (%val)
       return;

    TogglePartyWndSkills();
}
function InputTogglePartyWndStats(%val)
{
    if (%val)
       return;

    TogglePartyWndStats();
}
function InputTogglePartyWndSpells(%val)
{
    if (%val)
       return;

    TogglePartyWndSpells();
}
function InputToggleTrackingWnd(%val)
{
    if (%val)
       return;

    ToggleTrackingWnd();
}

function InputToggleCharMiniWnd(%val)
{
    if (%val)
       return;

    ToggleCharMiniWnd();
}

function InputToggleAllianceWnd(%val)
{
    if (%val)
       return;

    ToggleAllianceWnd();
}

function InputToggleLeaderWnd(%val)
{
    if (%val)
       return;

    ToggleLeaderWnd();
}


function InputToggleMacroWnd(%val)
{
    if (%val)
       return;

    ToggleMacroWnd();
}

function InputTomeToggleReply(%val)
{
    if (%val)
       return;

    TomeToggleReply();
}

function InputTomeToggleCycleReply(%val)
{
    if (%val)
       return;

    TomeToggleCycleReply();
}

function InputTomeToggleCycleReplyBackwards(%val)
{
    if (%val)
       return;

    TomeToggleCycleReplyBackwards();
}

function InputToggleMapWnd(%val)
{
    if (%val)
       return;

    ToggleMapWnd();
}

function InputToggleJournalWnd(%val)
{
    if (%val)
       return;

    ToggleJournalWnd();
}

function InputToggleHelpWnd(%val)
{
    if (%val)
       return;

    ToggleHelpWnd();
}

function InputToggleBuffWnd(%val)
{
    if (%val)
       return;

    ToggleBuffWnd();
}


function InputClearTarget(%val)
{
  if (%val)
      return;

  Py::ClearCharTarget();
}

moveMap.bind(keyboard, "f", InputToggleBuffWnd);
moveMap.bind(keyboard, "j", InputToggleJournalWnd);
moveMap.bind(keyboard, "h", InputToggleHelpWnd);
moveMap.bind(keyboard, "i", InputTogglePartyWndInventory);
moveMap.bind(keyboard, "k", InputTogglePartyWndSkills);
moveMap.bind(keyboard, "c", InputTogglePartyWndStats);
moveMap.bind(keyboard, "b", InputTogglePartyWndSpells);
moveMap.bind(keyboard, "t", InputToggleTrackingWnd);
moveMap.bind(keyboard, "p", InputToggleCharMiniWnd);
moveMap.bind(keyboard, "y", InputToggleAllianceWnd);
moveMap.bind(keyboard, "l", InputToggleLeaderWnd);
moveMap.bind(keyboard, "m", InputToggleMapWnd);
moveMap.bind(keyboard, "n", InputToggleMacroWnd);
moveMap.bind(keyboard, "r", InputTomeToggleReply);
moveMap.bind(keyboard, "ctrl tab", InputTomeToggleCycleReply);
moveMap.bind(keyboard, "ctrl-alt tab", InputTomeToggleCycleReplyBackwards);



//------------------------------------------------------------------------------
// Macro calls
//------------------------------------------------------------------------------
function InputSetMacroPage1(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(0);
}
function InputSetMacroPage2(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(1);
}
function InputSetMacroPage3(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(2);
}
function InputSetMacroPage4(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(3);
}
function InputSetMacroPage5(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(4);
}
function InputSetMacroPage6(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(5);
}
function InputSetMacroPage7(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(6);
}
function InputSetMacroPage8(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(7);
}
function InputSetMacroPage9(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(8);
}
function InputSetMacroPage10(%val)
{
  if (%val)
      return;

  Py::OnSetMacroPage(9);
}

moveMap.bind(keyboard, "ctrl-1", InputSetMacroPage1);
moveMap.bind(keyboard, "ctrl-2", InputSetMacroPage2);
moveMap.bind(keyboard, "ctrl-3", InputSetMacroPage3);
moveMap.bind(keyboard, "ctrl-4", InputSetMacroPage4);
moveMap.bind(keyboard, "ctrl-5", InputSetMacroPage5);
moveMap.bind(keyboard, "ctrl-6", InputSetMacroPage6);
moveMap.bind(keyboard, "ctrl-7", InputSetMacroPage7);
moveMap.bind(keyboard, "ctrl-8", InputSetMacroPage8);
moveMap.bind(keyboard, "ctrl-9", InputSetMacroPage9);
moveMap.bind(keyboard, "ctrl-0", InputSetMacroPage10);
moveMap.bindCmd(keyboard, "f7", "Py::OnHotKey(F7);", "");
moveMap.bindCmd(keyboard, "f8", "Py::OnHotKey(F8);", "");
moveMap.bindCmd(keyboard, "f9", "Py::OnHotKey(F9);", "");
moveMap.bindCmd(keyboard, "f10", "Py::OnHotKey(F10);", "");
moveMap.bindCmd(keyboard, "f11", "Py::OnHotKey(F11);", "");
moveMap.bindCmd(keyboard, "f12", "Py::OnHotKey(F12);", "");
moveMap.bindCmd(keyboard, "1", "Py::OnHotKey(1);", "");
moveMap.bindCmd(keyboard, "2", "Py::OnHotKey(2);", "");
moveMap.bindCmd(keyboard, "3", "Py::OnHotKey(3);", "");
moveMap.bindCmd(keyboard, "4", "Py::OnHotKey(4);", "");
moveMap.bindCmd(keyboard, "5", "Py::OnHotKey(5);", "");
moveMap.bindCmd(keyboard, "6", "Py::OnHotKey(6);", "");
moveMap.bindCmd(keyboard, "7", "Py::OnHotKey(7);", "");
moveMap.bindCmd(keyboard, "8", "Py::OnHotKey(8);", "");
moveMap.bindCmd(keyboard, "9", "Py::OnHotKey(9);", "");
moveMap.bindCmd(keyboard, "0", "Py::OnHotKey(0);", "");
moveMap.bindCmd(keyboard, "numpad1", "Py::OnHotKey(1);", "");
moveMap.bindCmd(keyboard, "numpad2", "Py::OnHotKey(2);", "");
moveMap.bindCmd(keyboard, "numpad3", "Py::OnHotKey(3);", "");
moveMap.bindCmd(keyboard, "numpad4", "Py::OnHotKey(4);", "");
moveMap.bindCmd(keyboard, "numpad5", "Py::OnHotKey(5);", "");
moveMap.bindCmd(keyboard, "numpad6", "Py::OnHotKey(6);", "");
moveMap.bindCmd(keyboard, "numpad7", "Py::OnHotKey(7);", "");
moveMap.bindCmd(keyboard, "numpad8", "Py::OnHotKey(8);", "");
moveMap.bindCmd(keyboard, "numpad9", "Py::OnHotKey(9);", "");
moveMap.bindCmd(keyboard, "numpad0", "Py::OnHotKey(0);", "");



//------------------------------------------------------------------------------
// Item manipulation
//------------------------------------------------------------------------------
moveMap.bindCmd(keyboard, "f1", "MACROWND_CHAR0.performClick();", "");
moveMap.bindCmd(keyboard, "f2", "MACROWND_CHAR1.performClick();", "");
moveMap.bindCmd(keyboard, "f3", "MACROWND_CHAR2.performClick();", "");
moveMap.bindCmd(keyboard, "f4", "MACROWND_CHAR3.performClick();", "");
moveMap.bindCmd(keyboard, "f5", "MACROWND_CHAR4.performClick();", "");
moveMap.bindCmd(keyboard, "f6", "MACROWND_CHAR5.performClick();", "");
moveMap.bindCmd(keyboard, "shift f1", "Py::CharSetTarget(0);", "");
moveMap.bindCmd(keyboard, "shift f2", "Py::CharSetTarget(1);", "");
moveMap.bindCmd(keyboard, "shift f3", "Py::CharSetTarget(2);", "");
moveMap.bindCmd(keyboard, "shift f4", "Py::CharSetTarget(3);", "");
moveMap.bindCmd(keyboard, "shift f5", "Py::CharSetTarget(4);", "");
moveMap.bindCmd(keyboard, "shift f6", "Py::CharSetTarget(5);", "");


moveMap.bind(keyboard, "backspace", "InputClearTarget");

function InputEvaluate(%val)
{
   if (%val)
      return;

   Py::DoCommand("/EVAL");
}

function InputToggleAutowalk(%val)
{
   if (%val)
      return;

   Py::DoClientCommand("/AUTOWALK");
}

function InputCycleTarget(%val)
{
   if (%val)
      return;

   Py::DoCommand("/CYCLETARGET");
}

function InputCycleTargetBackwards(%val)
{
   if (%val)
      return;

   Py::DoCommand("/CYCLETARGETBACKWARDS");
}

function InputTargetNearest(%val)
{
   if (%val)
      return;

   Py::DoCommand("/TARGETNEAREST");
}


moveMap.bind(keyboard, "g", InputEvaluate);
moveMap.bind(keyboard, "v", InputToggleAutowalk);
moveMap.bind(keyboard, "tilde", InputCycleTarget);
moveMap.bind(keyboard, "shift tab", InputCycleTargetBackwards);
moveMap.bind(keyboard, "tab", InputTargetNearest);




//------------------------------------------------------------------------------
// Demo recording functions
//------------------------------------------------------------------------------

function startRecordingDemo( %val )
{
   if ( %val )
      startDemoRecord();
}

function stopRecordingDemo( %val )
{
   if ( %val )
      stopDemoRecord();
}

//moveMap.bind( keyboard, F3, startRecordingDemo );
//moveMap.bind( keyboard, F4, stopRecordingDemo );


//------------------------------------------------------------------------------
// Helper Functions
//------------------------------------------------------------------------------

function dropCameraAtPlayer(%val)
{
   if (%val)
      commandToServer('dropCameraAtPlayer');
}

function dropPlayerAtCamera(%val)
{
   if (%val)
      commandToServer('DropPlayerAtCamera');
}

//moveMap.bind(keyboard, "ctrl c", dropCameraAtPlayer);
moveMap.bind(keyboard, "ctrl c", dropPlayerAtCamera);

function bringUpOptions(%val)
{
   if (%val)
      Canvas.pushDialog(OptionsDlg);
}

moveMap.bind(keyboard, "ctrl o", bringUpOptions);


//------------------------------------------------------------------------------
// Dubuging Functions
//------------------------------------------------------------------------------

$MFDebugRenderMode = 0;
function cycleDebugRenderMode(%val)
{
   if (!%val)
      return;
      
   if (!$pref::developer)
      return;


   if (getBuildString() $= "Debug")
   {
      if($MFDebugRenderMode == 0)
      {
         // Outline mode, including fonts so no stats
         $MFDebugRenderMode = 1;
         GLEnableOutline(true);
      }
      else if ($MFDebugRenderMode == 1)
      {
         // Interior debug mode
         $MFDebugRenderMode = 2;
         GLEnableOutline(false);
         setInteriorRenderMode(7);
         showInterior();
      }
      else if ($MFDebugRenderMode == 2)
      {
         // Back to normal
         $MFDebugRenderMode = 0;
         setInteriorRenderMode(0);
         GLEnableOutline(false);
         show();
      }
   }
   else
   {
      echo("Debug render modes only available when running a Debug build.");
   }
}

GlobalActionMap.bind(keyboard, "ctrl F9", cycleDebugRenderMode);

moveMap.bindCmd(keyboard, "slash", "TomeToggleSlash();", "");
moveMap.bindCmd(keyboard, "return", "TomeToggleEnter();", "");

moveMap.bind(keyboard, "x", ToggleMouseLook );
moveMap.bind(keyboard, "z", toggleZoom);

//------------------------------------------------------------------------------
// Misc.
//------------------------------------------------------------------------------

GlobalActionMap.bind(keyboard, "ctrl tilde", toggleConsole);
GlobalActionMap.bindCmd(keyboard, "alt enter", "", "toggleFullScreen();");
GlobalActionMap.bindCmd(keyboard, "ctrl F1", "", "InputToggleHelpWnd();");

if (PlayGui.isAwake())
{
   moveMap.push();
}
//moveMap.bindCmd(keyboard, "n", "NetGraph::toggleNetGraph();", "");
