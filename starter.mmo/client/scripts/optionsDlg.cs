// Variables needed by detail options!
$max_screenerror = 25;
$min_TSScreenError = 2;
$max_TSScreenError = 20;
$min_TSDetailAdjust = 0.6;
$max_TSDetailAdjust = 1.0;

//------------------------------------------

function optionsDlg::setPane(%this, %pane)
{
   OptAudioPane.setVisible(false);
   OptGraphicsPane.setVisible(false);
   OptGuiPane.setVisible(false);
   OptControlsPane.setVisible(false);
   OptGameplayPane.setVisible(false);
   ("Opt" @ %pane @ "Pane").setVisible(true);
   OptRemapList.fillList();
   
   OPTION_TURNSPEED.setValue($pref::Input::MouseTurnSpeed);
   OPTION_GUISPEED.setValue($pref::Input::MouseGUISpeed);

}


function OptionsDlg::doTextureFlush(%this)
{
    MessagePopup("Changing Graphics Settings...","Please wait...");
	Canvas.repaint();
	flushTextureCache();
    CloseMessagePopup();
 
}

function OptionsDlg::onWake(%this)
{
   %this.setPane(Graphics);
   %buffer = getDisplayDeviceList();
   %count = getFieldCount( %buffer );
   OptGraphicsDriverMenu.clear();
   for(%i = 0; %i < %count; %i++)
      OptGraphicsDriverMenu.add(getField(%buffer, %i), %i);
   %selId = OptGraphicsDriverMenu.findText( $pref::Video::displayDevice );
	if ( %selId == -1 )
		%selId = 0; // How did THAT happen?
	OptGraphicsDriverMenu.setSelected( %selId );
	OptGraphicsDriverMenu.onSelect( %selId, "" );
   OP_GammaSlider.setValue( $pref::OpenGL::gammaCorrection ); // Gamma Correction
   OP_ChatFontSlider.setValue($pref::Game::ChatFontSize);
   OP_GameFontSlider.setValue($pref::Game::GameFontSize);
   
   OP_GuiOpacitySlider.setValue($pref::Gui::Opacity);
   


   // Audio
   OptAudioUpdate();
   OptAudioVolumeMaster.setValue( $pref::Audio::masterVolume);
   OptAudioVolumeShell.setValue(  $pref::Audio::channelVolume[$GuiAudioType]);
   OptAudioVolumeSim.setValue(    $pref::Audio::channelVolume[$MusicAudioType]);
   OptAudioDriverList.clear();
   OptAudioDriverList.add("OpenAL", 1);
   OptAudioDriverList.add("none", 2);
   %selId = OptAudioDriverList.findText($pref::Audio::driver);
	if ( %selId == -1 )
		%selId = 0; // How did THAT happen?
	OptAudioDriverList.setSelected( %selId );
	OptAudioDriverList.onSelect( %selId, "" );
   OP_VisibleDistanceSlider.setValue( $pref::MyVisibleDistanceMod );
   // Vsync
   if ( $SwapIntervalSupported )
   {
      OP_VSyncTgl.setValue( $pref::Video::disableVerticalSync );
      OP_VSyncTgl.setActive( true );
   }
   else
   {
      OP_VSyncTgl.setValue( false );
      OP_VSyncTgl.setActive( false );
   }

    GDETAIL_VERYLOW.setValue(false);
    GDETAIL_LOW.setValue(false);
    GDETAIL_HIGH.setValue(false);
    GDETAIL_VERYHIGH.setValue(false);
    

   if ($pref::Video::GraphicDetail == 0)
   {
    GDETAIL_VERYLOW.setValue(true);
   }
   if ($pref::Video::GraphicDetail == 1)
   {
    GDETAIL_LOW.setValue(true);
   }
   if ($pref::Video::GraphicDetail == 2)
   {
    GDETAIL_HIGH.setValue(true);
   }
   if ($pref::Video::GraphicDetail == 3)
   {
    GDETAIL_VERYHIGH.setValue(true);
   }
   
   ShowPlayerLights($pref::Video::showPlayerLights);
   OptGraphicsShowPlayerLights.setValue($pref::Video::showPlayerLights);
   
   
   //gameplay
   if ($pref::gameplay::difficulty == 1)
   {
      GameplayDifficultyEasy.setValue(1);
      GameplayDifficultyNormal.setValue(0);
      GameplayDifficultyHardcore.setValue(0);
   }
   else if ($pref::gameplay::difficulty == 2)
   {
      GameplayDifficultyEasy.setValue(0);
      GameplayDifficultyNormal.setValue(0);
      GameplayDifficultyHardcore.setValue(1);
   }
   else
   {
      GameplayDifficultyEasy.setValue(0);
      GameplayDifficultyNormal.setValue(1);
      GameplayDifficultyHardcore.setValue(0);
   }
   
   GameplayMonsterRespawn.setValue($pref::gameplay::monsterrespawn);
   GameplaySPPopulators.setValue($pref::gameplay::SPpopulators);

}


function OptionsDlg::onSleep(%this)
{
   // write out the control config into the fps/config.cs file
   moveMap.save( "~/client/config.cs" );

   if (GameplayDifficultyEasy.getValue())
      $pref::gameplay::difficulty = 1;
   else if (GameplayDifficultyHardcore.getValue())
      $pref::gameplay::difficulty = 2;
   else
      $pref::gameplay::difficulty = 0;

   Py::SetGameDifficulty();

}


function OptGraphicsDriverMenu::onSelect( %this, %id, %text )
{
	// Attempt to keep the same res and bpp settings:
	if ( OptGraphicsResolutionMenu.size() > 0 )
		%prevRes = OptGraphicsResolutionMenu.getText();
	else
		%prevRes = getWords( $pref::Video::resolution, 0, 1 );

	// Check if this device is full-screen only:
	if ( isDeviceFullScreenOnly( %this.getText() ) )
	{
		OptGraphicsFullscreenToggle.setValue( true );
		OptGraphicsFullscreenToggle.setActive( false );
		OptGraphicsFullscreenToggle.onAction();
	}
	else
		OptGraphicsFullscreenToggle.setActive( true );

	if ( OptGraphicsFullscreenToggle.getValue() )
	{
		if ( OptGraphicsBPPMenu.size() > 0 )
			%prevBPP = OptGraphicsBPPMenu.getText();
		else
			%prevBPP = getWord( $pref::Video::resolution, 2 );
	}

	// Fill the resolution and bit depth lists:
	OptGraphicsResolutionMenu.init( %this.getText(), OptGraphicsFullscreenToggle.getValue() );
	OptGraphicsBPPMenu.init( %this.getText() );

	// Try to select the previous settings:
	%selId = OptGraphicsResolutionMenu.findText( %prevRes );
	if ( %selId == -1 )
		%selId = 0;
	OptGraphicsResolutionMenu.setSelected( %selId );

	if ( OptGraphicsFullscreenToggle.getValue() )
	{
		%selId = OptGraphicsBPPMenu.findText( %prevBPP );
		if ( %selId == -1 )
			%selId = 0;
		OptGraphicsBPPMenu.setSelected( %selId );
		OptGraphicsBPPMenu.setText( OptGraphicsBPPMenu.getTextById( %selId ) );
	}
	else
		OptGraphicsBPPMenu.setText( "Default" );

}

function OptGraphicsResolutionMenu::init( %this, %device, %fullScreen )
{
	%this.clear();
	%resList = getResolutionList( %device );
	%resCount = getFieldCount( %resList );
	%deskRes = getDesktopResolution();

   %count = 0;
	for ( %i = 0; %i < %resCount; %i++ )
	{
		%res = getWords( getField( %resList, %i ), 0, 1 );

		if ( !%fullScreen )
		{
			if ( firstWord( %res ) >= firstWord( %deskRes ) )
				continue;
			if ( getWord( %res, 1 ) >= getWord( %deskRes, 1 ) )
				continue;
		}

		// Only add to list if it isn't there already:
		if ( %this.findText( %res ) == -1 )
      {
			%this.add( %res, %count );
         %count++;
      }
	}
}

function OptGraphicsFullscreenToggle::onAction(%this)
{
   Parent::onAction();
   %prevRes = OptGraphicsResolutionMenu.getText();

   // Update the resolution menu with the new options
   OptGraphicsResolutionMenu.init( OptGraphicsDriverMenu.getText(), %this.getValue() );

   // Set it back to the previous resolution if the new mode supports it.
   %selId = OptGraphicsResolutionMenu.findText( %prevRes );
   if ( %selId == -1 )
   	%selId = 0;
 	OptGraphicsResolutionMenu.setSelected( %selId );
}


function OptGraphicsBPPMenu::init( %this, %device )
{
	%this.clear();

	if ( %device $= "Voodoo2" )
		%this.add( "16", 0 );
	else
	{
		%resList = getResolutionList( %device );
		%resCount = getFieldCount( %resList );
      %count = 0;
		for ( %i = 0; %i < %resCount; %i++ )
		{
			%bpp = getWord( getField( %resList, %i ), 2 );

			// Only add to list if it isn't there already:
			if ( %this.findText( %bpp ) == -1 )
         {
				%this.add( %bpp, %count );
            %count++;
         }
		}
	}
}


function OptionsDlg::onVeryLow()
{
 $pref::MyVisibleDistanceMod = 0.3;
 OP_VisibleDistanceSlider.setValue( $pref::MyVisibleDistanceMod );
}

function OptionsDlg::onLow()
{
 $pref::MyVisibleDistanceMod = 0.5;
 OP_VisibleDistanceSlider.setValue( $pref::MyVisibleDistanceMod );
}
function OptionsDlg::onHigh()
{
 $pref::MyVisibleDistanceMod = 0.7;
 OP_VisibleDistanceSlider.setValue( $pref::MyVisibleDistanceMod );
}
function OptionsDlg::onVeryHigh()
{
 $pref::MyVisibleDistanceMod = 1.0;
 OP_VisibleDistanceSlider.setValue( $pref::MyVisibleDistanceMod );
}



function SetGraphicsOptions()
{

   %flushTextures = false;

   if ($pref::Video::GraphicDetail==0)
   {
      $pref::Terrain::screenError = 30;
      $pref::PrecipitationDensity = 0.1;
      $pref::Shadows = 0;
      $pref::TS::screenError = 8;
      $pref::TS::detailAdjust = 0.2;
      $pref::Terrain::texDetail = 1;
      %tempOpenGLMipReduction = 3;
      %tempInteriorMipReduction = 3;
      $pref::Interior::detailAdjust = 0.1;
      $pref::Terrain::enableDetails = 0;
   }
   if ($pref::Video::GraphicDetail ==1)
   {
      $pref::Shadows = 0;
      $pref::Terrain::screenError = 20;
      $pref::PrecipitationDensity = 0.2;
      $pref::TS::screenError = 6;
      $pref::TS::detailAdjust = 0.3;
      $pref::Terrain::texDetail = 1;
      %tempOpenGLMipReduction = 2;
      %tempInteriorMipReduction = 2;
      //$pref::MyVisibleDistanceMod = 0.5;
      $pref::Interior::detailAdjust = 0.3;
      $pref::Terrain::enableDetails = 1;
   }
   if ($pref::Video::GraphicDetail==2)
   {
      $pref::Terrain::screenError = 15;
      $pref::PrecipitationDensity = 0.5;
      $pref::Shadows = 0.5;
      $pref::TS::screenError = 4;
      $pref::TS::detailAdjust = 0.5;
      $pref::Terrain::texDetail = 0;
      %tempOpenGLMipReduction = 1;
      %tempInteriorMipReduction = 1;
      //$pref::MyVisibleDistanceMod = 0.7;
      $pref::Interior::detailAdjust = 0.8;
      $pref::Terrain::enableDetails = 1;
   }
   if ($pref::Video::GraphicDetail==3)
   {
      $pref::Terrain::screenError = 5;
      $pref::PrecipitationDensity = 1;
      $pref::Shadows = 1;
      $pref::TS::screenError = 2;
      $pref::TS::detailAdjust = 0.8;
      $pref::Terrain::texDetail = 0;
      %tempOpenGLMipReduction = 0;
      %tempInteriorMipReduction = 0;
      //$pref::MyVisibleDistanceMod = 1.0;
      $pref::Interior::detailAdjust = 1;
      $pref::Terrain::enableDetails = 1;
   }

    setShadowDetailLevel( $pref::Shadows );
    
    if ( $SwapIntervalSupported)
        setVerticalSync( !$pref::Video::disableVerticalSync );
        

   if ( $pref::OpenGL::mipReduction != %tempOpenGLMipReduction )
   {
      $pref::OpenGL::mipReduction = %tempOpenGLMipReduction;
      setOpenGLMipReduction( $pref::OpenGL::mipReduction );
      %flushTextures = true;
   }

   if ( $pref::OpenGL::interiorMipReduction != %tempInteriorMipReduction )
   {
      $pref::OpenGL::interiorMipReduction = %tempInteriorMipReduction;
      setOpenGLInteriorMipReduction( $pref::OpenGL::interiorMipReduction );
      %flushTextures = true;
   }
   

   
   if (%flushTextures)
    OptionsDlg.schedule( 0, doTextureFlush );


}

function optionsDlg::applyGraphics( %this )
{

    %newRes = OptGraphicsResolutionMenu.getText();
    %newBpp = OptGraphicsBPPMenu.getText();
    %newFullScreen = OptGraphicsFullscreenToggle.getValue();

    %x = firstWord( %newRes );
    %y = getWord( %newRes, 1 );

    if (%x >= 1024 && %y >= 768)
        setScreenMode( firstWord( %newRes ), getWord( %newRes, 1 ), %newBpp, %newFullScreen );
  
   %flushTextures = false;
   
   if (GDETAIL_VERYLOW.getValue())
   {
      $pref::Video::GraphicDetail = 0;
   }
   if (GDETAIL_LOW.getValue())
   {
      $pref::Video::GraphicDetail = 1;
   }
   if (GDETAIL_HIGH.getValue())
   {
      $pref::Video::GraphicDetail = 2;
   }
   if (GDETAIL_VERYHIGH.getValue())
   {
      $pref::Video::GraphicDetail = 3;
   }

   // Vsync
   if ( $SwapIntervalSupported && OP_VSyncTgl.getValue() != $pref::Video::disableVerticalSync )
   {
      $pref::Video::disableVerticalSync = OP_VSyncTgl.getValue();
   }
   
   SetGraphicsOptions();
}



$RemapCount = 0;
$RemapName[$RemapCount] = "Toggle Mouse Look";
$RemapCmd[$RemapCount] = "ToggleMouseLook";
$RemapCount++;
$RemapName[$RemapCount] = "Forward";
$RemapCmd[$RemapCount] = "moveforward";
$RemapCount++;
$RemapName[$RemapCount] = "Backward";
$RemapCmd[$RemapCount] = "movebackward";
$RemapCount++;
$RemapName[$RemapCount] = "Strafe Left";
$RemapCmd[$RemapCount] = "moveleft";
$RemapCount++;
$RemapName[$RemapCount] = "Strafe Right";
$RemapCmd[$RemapCount] = "moveright";
$RemapCount++;
$RemapName[$RemapCount] = "Turn Left";
$RemapCmd[$RemapCount] = "turnLeft";
$RemapCount++;
$RemapName[$RemapCount] = "Turn Right";
$RemapCmd[$RemapCount] = "turnRight";
$RemapCount++;
$RemapName[$RemapCount] = "Look Up";
$RemapCmd[$RemapCount] = "panUp";
$RemapCount++;
$RemapName[$RemapCount] = "Look Down";
$RemapCmd[$RemapCount] = "panDown";
$RemapCount++;
$RemapName[$RemapCount] = "Jump";
$RemapCmd[$RemapCount] = "jump";
$RemapCount++;
$RemapName[$RemapCount] = "Clear Target";
$RemapCmd[$RemapCount] = "InputClearTarget";
$RemapCount++;
$RemapName[$RemapCount] = "Cycle Enemies";
$RemapCmd[$RemapCount] = "InputCycleTarget";
$RemapCount++;
$RemapName[$RemapCount] = "Cycle Enemies Reverse";
$RemapCmd[$RemapCount] = "InputCycleTargetBackwards";
$RemapCount++;
$RemapName[$RemapCount] = "Nearest Enemy";
$RemapCmd[$RemapCount] = "InputTargetNearest";
$RemapCount++;

$RemapName[$RemapCount] = "Evaluate";
$RemapCmd[$RemapCount] = "InputEvaluate";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Autowalk";
$RemapCmd[$RemapCount] = "InputToggleAutowalk";
$RemapCount++;
$RemapName[$RemapCount] = "Squint";
$RemapCmd[$RemapCount] = "toggleZoom";
$RemapCount++;
$RemapName[$RemapCount] = "Free Look";
$RemapCmd[$RemapCount] = "toggleFreeLook";
$RemapCount++;
$RemapName[$RemapCount] = "Switch 1st/3rd";
$RemapCmd[$RemapCount] = "toggleFirstPerson";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Camera";
$RemapCmd[$RemapCount] = "toggleCamera";
$RemapCount++;
$RemapName[$RemapCount] = "Drop Player at Camera";
$RemapCmd[$RemapCount] = "dropPlayerAtCamera";
$RemapCount++;

//windows
$RemapName[$RemapCount] = "Toggle Inventory";
$RemapCmd[$RemapCount] = "InputTogglePartyWndInventory";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Skills";
$RemapCmd[$RemapCount] = "InputTogglePartyWndSkills";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Stats";
$RemapCmd[$RemapCount] = "InputTogglePartyWndStats";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Spells";
$RemapCmd[$RemapCount] = "InputTogglePartyWndSpells";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Tracking";
$RemapCmd[$RemapCount] = "InputToggleTrackingWnd";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Party";
$RemapCmd[$RemapCount] = "InputToggleCharMiniWnd";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Buffs";
$RemapCmd[$RemapCount] = "InputToggleBuffWnd";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Alliance";
$RemapCmd[$RemapCount] = "InputToggleAllianceWnd";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Leader";
$RemapCmd[$RemapCount] = "InputToggleLeaderWnd";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Macros";
$RemapCmd[$RemapCount] = "InputToggleMacroWnd";
$RemapCount++;
$RemapName[$RemapCount] = "Toggle Map";
$RemapCmd[$RemapCount] = "InputToggleMapWnd";
$RemapCount++;
$RemapName[$RemapCount] = "Reply";
$RemapCmd[$RemapCount] = "InputTomeToggleReply";
$RemapCount++;
$RemapName[$RemapCount] = "Reply Cycle";
$RemapCmd[$RemapCount] = "InputTomeToggleCycleReply";
$RemapCount++;
$RemapName[$RemapCount] = "Reply Cycle Reverse";
$RemapCmd[$RemapCount] = "InputTomeToggleCycleReplyBackwards";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 1";
$RemapCmd[$RemapCount] = "InputSetMacroPage1";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 2";
$RemapCmd[$RemapCount] = "InputSetMacroPage2";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 3";
$RemapCmd[$RemapCount] = "InputSetMacroPage3";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 4";
$RemapCmd[$RemapCount] = "InputSetMacroPage4";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 5";
$RemapCmd[$RemapCount] = "InputSetMacroPage5";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 6";
$RemapCmd[$RemapCount] = "InputSetMacroPage6";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 7";
$RemapCmd[$RemapCount] = "InputSetMacroPage7";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 8";
$RemapCmd[$RemapCount] = "InputSetMacroPage8";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 9";
$RemapCmd[$RemapCount] = "InputSetMacroPage9";
$RemapCount++;
$RemapName[$RemapCount] = "Set Macro Page 10";
$RemapCmd[$RemapCount] = "InputSetMacroPage10";
$RemapCount++;

function restoreDefaultMappings()
{
   moveMap.delete();
   exec( "~/client/scripts/default.bind.cs" );
   OptRemapList.fillList();
}

function getMapDisplayName( %device, %action )
{
	if ( %device $= "keyboard" )
		return( %action );		
	else if ( strstr( %device, "mouse" ) != -1 )
	{
		// Substitute "mouse" for "button" in the action string:
		%pos = strstr( %action, "button" );
		if ( %pos != -1 )
		{
			%mods = getSubStr( %action, 0, %pos );
			%object = getSubStr( %action, %pos, 1000 );
			%instance = getSubStr( %object, strlen( "button" ), 1000 );
			return( %mods @ "mouse" @ ( %instance + 1 ) );
		}
		else
			error( "Mouse input object other than button passed to getDisplayMapName!" );
	}
	else if ( strstr( %device, "joystick" ) != -1 )
	{
		// Substitute "joystick" for "button" in the action string:
		%pos = strstr( %action, "button" );
		if ( %pos != -1 )
		{
			%mods = getSubStr( %action, 0, %pos );
			%object = getSubStr( %action, %pos, 1000 );
			%instance = getSubStr( %object, strlen( "button" ), 1000 );
			return( %mods @ "joystick" @ ( %instance + 1 ) );
		}
		else
	   { 
	      %pos = strstr( %action, "pov" );
         if ( %pos != -1 )
         {
            %wordCount = getWordCount( %action );
            %mods = %wordCount > 1 ? getWords( %action, 0, %wordCount - 2 ) @ " " : "";
            %object = getWord( %action, %wordCount - 1 );
            switch$ ( %object )
            {
               case "upov":   %object = "POV1 up";
               case "dpov":   %object = "POV1 down";
               case "lpov":   %object = "POV1 left";
               case "rpov":   %object = "POV1 right";
               case "upov2":  %object = "POV2 up";
               case "dpov2":  %object = "POV2 down";
               case "lpov2":  %object = "POV2 left";
               case "rpov2":  %object = "POV2 right";
               default:       %object = "??";
            }
            return( %mods @ %object );
         }
         else
            error( "Unsupported Joystick input object passed to getDisplayMapName!" );
      }
	}
		
	return( "??" );		
}

function buildFullMapString( %index )
{
   %name       = $RemapName[%index];
   %cmd        = $RemapCmd[%index];

	%temp = moveMap.getBinding( %cmd );
   %device = getField( %temp, 0 );
   %object = getField( %temp, 1 );
   if ( %device !$= "" && %object !$= "" )
	   %mapString = getMapDisplayName( %device, %object );
   else
      %mapString = "";

	return( %name TAB %mapString );
}

function OptRemapList::fillList( %this )
{
	%this.clear();
   for ( %i = 0; %i < $RemapCount; %i++ )
      %this.addRow( %i, buildFullMapString( %i ) );
}

//------------------------------------------------------------------------------
function OptRemapList::doRemap( %this )
{
	%selId = %this.getSelectedId();
   %name = $RemapName[%selId];

	OptRemapText.setValue( "REMAP \"" @ %name @ "\"" );
	OptRemapInputCtrl.index = %selId;

	Canvas.pushDialog( RemapDlg );
    OptRemapInputCtrl.makeFirstResponder(true);

}

//------------------------------------------------------------------------------
function redoMapping( %device, %action, %cmd, %oldIndex, %newIndex )
{
	//%actionMap.bind( %device, %action, $RemapCmd[%newIndex] );
	moveMap.bind( %device, %action, %cmd );
	OptRemapList.setRowById( %oldIndex, buildFullMapString( %oldIndex ) );
	OptRemapList.setRowById( %newIndex, buildFullMapString( %newIndex ) );
}

//------------------------------------------------------------------------------
function findRemapCmdIndex( %command )
{
	for ( %i = 0; %i < $RemapCount; %i++ )
	{
		if ( %command $= $RemapCmd[%i] )
			return( %i );			
	}
	return( -1 );	
}

function OptRemapInputCtrl::onInputEvent( %this, %device, %action )
{
	//error( "** onInputEvent called - device = " @ %device @ ", action = " @ %action @ " **" );
	Canvas.popDialog( RemapDlg );

	// Test for the reserved keystrokes:
	if ( %device $= "keyboard" )
	{
      // Cancel...
      if ( %action $= "escape" )
      {
         // Do nothing...
		   return;
      }
      
	}

	if ( %device $= "mouse" )
	{
      // Cancel...
      if ( %action $= "button0" )
      {
         // Do nothing...
		   return;
      }
      if ( %action $= "button1" )
      {
         // Do nothing...
		   return;
      }

      
	}

	if ( %device $= "mouse0" )
	{
      // Cancel...
      if ( %action $= "button0" )
      {
         // Do nothing...
		   return;
      }
      if ( %action $= "button1" )
      {
         // Do nothing...
		   return;
      }

      
	}

	
   %cmd  = $RemapCmd[%this.index];
   %name = $RemapName[%this.index];

	// First check to see if the given action is already mapped:
	%prevMap = moveMap.getCommand( %device, %action );
   if ( %prevMap !$= %cmd )
   {
       %mname = getMapDisplayName( %device, %action );
       if (!Py::KeyCanBeRemapped(%mname))
       {
          MessageBoxOK( "REMAP FAILED", "\"" @ %mname @ "\" is already bound to a non-remappable command!" );
          return;
       }
	   if ( %prevMap $= "" )
	   {
         moveMap.bind( %device, %action, %cmd );
		   OptRemapList.setRowById( %this.index, buildFullMapString( %this.index ) );
	   }
	   else
	   {
           %mapName = getMapDisplayName( %device, %action );
		   %prevMapIndex = findRemapCmdIndex( %prevMap );
		   if ( %prevMapIndex == -1 )
			   MessageBoxOK( "REMAP FAILED", "\"" @ %mapName @ "\" is already bound to a non-remappable command!" );
		   else
         {
            %prevCmdName = $RemapName[%prevMapIndex];
			   MessageBoxYesNo( "WARNING", 
				   "\"" @ %mapName @ "\" is already bound to \"" 
					   @ %prevCmdName @ "\"!\nDo you want to undo this mapping?", 
				   "redoMapping(" @ %device @ ", \"" @ %action @ "\", \"" @ %cmd @ "\", " @ %prevMapIndex @ ", " @ %this.index @ ");", "" );
         }
		   return;
	   }
   }
}

// Audio 
function OptAudioUpdate()
{
   // set the driver text
   %text =   "Vendor: " @ alGetString("AL_VENDOR") @
           "\nVersion: " @ alGetString("AL_VERSION") @
           "\nRenderer: " @ alGetString("AL_RENDERER") @
           "\nExtensions: " @ alGetString("AL_EXTENSIONS");
   OptAudioInfo.setText(%text);

}


// Channel 0 is unused in-game, but is used here to test master volume.

new AudioDescription(AudioChannel0)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 0;
};

new AudioDescription(AudioChannel1)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 1;
};

new AudioDescription(AudioChannel2)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 2;
};

new AudioDescription(AudioChannel3)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 3;
};

new AudioDescription(AudioChannel4)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 4;
};

new AudioDescription(AudioChannel5)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 5;
};

new AudioDescription(AudioChannel6)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 6;
};

new AudioDescription(AudioChannel7)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 7;
};

new AudioDescription(AudioChannel8)
{
   volume   = 1.0;
   isLooping= false;
   is3D     = false;
   type     = 8;
};

$AudioTestHandle = 0;

function OptAudioUpdateMasterVolume(%volume)
{
   if (%volume == $pref::Audio::masterVolume)
      return;
   alxListenerf(AL_GAIN_LINEAR, %volume);
   $pref::Audio::masterVolume = %volume;
   if (!alxIsPlaying($AudioTestHandle))
   {
      $AudioTestHandle = alxCreateSource("AudioChannel0", expandFilename("~/data/sound/testing.wav"));
      alxPlay($AudioTestHandle);
   }
}

function OptAudioUpdateChannelVolume(%channel, %volume)
{
   if (%channel < 1 || %channel > 8)
      return;

   if (%volume == $pref::Audio::channelVolume[%channel])
      return;

   alxSetChannelVolume(%channel, %volume);
   $pref::Audio::channelVolume[%channel] = %volume;
   if (!alxIsPlaying($AudioTestHandle))
   {
      $AudioTestHandle = alxCreateSource("AudioChannel"@%channel, expandFilename("~/data/sound/testing.wav"));
      alxPlay($AudioTestHandle);
   }
}


function OptAudioDriverList::onSelect( %this, %id, %text )
{
   if (%text $= "")
      return;

   if ($pref::Audio::driver $= %text)
      return;

   $pref::Audio::driver = %text;
   OpenALInit();
}

//------------------------------------------

// Graphic Stuff

function updateGammaCorrection()
{
   $pref::OpenGL::gammaCorrection = OP_GammaSlider.getValue();
   videoSetGammaCorrection( $pref::OpenGL::gammaCorrection ); 
}



function updateChatFont()
{
   $pref::Game::ChatFontSize = OP_ChatFontSlider.getValue();
      Py::OnChatFontSizeChanged();
}


function updateGameFont()
{
   $pref::Game::GameFontSize = OP_GameFontSlider.getValue();
   Py::OnGameFontSizeChanged();
}

function updateGuiOpacity()
{
   $pref::Gui::Opacity = OP_GuiOpacitySlider.getValue();
}


function updateVisibleDistance()
{
   $pref::MyVisibleDistanceMod = OP_VisibleDistanceSlider.getValue();

}

function updateMouseTurn()
{
   $pref::Input::MouseTurnSpeed=OPTION_TURNSPEED.getValue();

}

function updateMouseGui()
{
   $pref::Input::MouseGuiSpeed=OPTION_GUISPEED.getValue();

}

function updateMonsterRespawn()
{
   $pref::gameplay::monsterrespawn=GameplayMonsterRespawn.getValue();
   Py::OnRespawnTimeChanged();

}





//------------------------------------------

