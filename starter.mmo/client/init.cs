//-----------------------------------------------------------------------------

// Variables used by client scripts & code.  The ones marked with (c)
// are accessed from code.  Variables preceeded by Pref:: are client
// preferences and stored automatically in the ~/client/prefs.cs file
// in between sessions.
//
//    (c) Client::MissionFile             Mission file name
//    ( ) Client::Password                Password for server join

//    (?) Pref::Player::CurrentFOV
//    (?) Pref::Player::DefaultFov
//    ( ) Pref::Input::KeyboardTurnSpeed

//    (c) pref::Master[n]                 List of master servers
//    (c) pref::Net::RegionMask     
//    (c) pref::Client::ServerFavoriteCount
//    (c) pref::Client::ServerFavorite[FavoriteCount]
//    .. Many more prefs... need to finish this off

// Moves, not finished with this either...
//    (c) firstPerson
//    $mv*Action...

//-----------------------------------------------------------------------------

//-----------------------------------------------------------------------------

function initClient()
{
   echo("\n--------- Initializing MOD: FPS Starter Kit: Client ---------");

   // Make sure this variable reflects the correct state.
   $Server::Dedicated = false;

   // Game information used to query the master server
   $Client::GameTypeQuery = "FPS Starter Kit";
   $Client::MissionTypeQuery = "Any";

   //
   exec("./ui/customProfiles.cs"); // override the base profiles if necessary

   // The common module provides basic client functionality
   initBaseClient();

   // InitCanvas starts up the graphics system.
   // The canvas needs to be constructed before the gui scripts are
   // run because many of the controls assume the canvas exists at
   // load time.
   initCanvas("Starter MMO");

   /// Load client-side Audio Profiles/Descriptions
   exec("./scripts/audioProfiles.cs");

   // Load up the Game GUIs
   exec("./ui/defaultGameProfiles.cs");
   exec("./ui/momGameProfiles.cs");
   exec("./ui/PlayGui.gui");
//   exec("./ui/ChatHud.gui");
   exec("./ui/playerList.gui");

   // Load up the shell GUIs
   exec("./ui/mainMenuGui.gui");
   exec("./ui/QuitGui.gui");
   exec("./ui/aboutDlg.gui");
   exec("./ui/startMissionGui.gui");
   exec("./ui/joinServerGui.gui");
   exec("./ui/loadingGui.gui");
   exec("./ui/endGameGui.gui");
   exec("./ui/optionsDlg.gui");
   exec("./ui/remapDlg.gui");
//   exec("./ui/StartupGui.gui");
   
   // My Guis
   exec("./ui/EULAWnd.gui");
   exec("./ui/GameBreakGui.gui");
   exec("./ui/FadeWnd.gui");
   exec("./ui/CreditsWnd.gui");
   exec("./ui/NewSinglePlayerWorldDlg.gui");
   exec("./ui/multiplayerGui.gui");
   exec("./ui/singleplayerGui.gui");
   exec("./ui/RegisterDlg.gui");
   exec("./ui/MasterLoginDlg.gui");
   exec("./ui/PatchLoginDlg.gui");
   exec("./ui/MasterGui.gui");
   exec("./ui/WorldLoginDlg.gui");
   exec("./ui/WorldRegisterDlg.gui");
   exec("./ui/NewCharacterGui.gui");
   exec("./ui/WorldGui.gui");
   exec("./ui/CraftingWnd.gui");
   exec("./ui/SplitStackGui.gui");
   exec("./ui/ChatGui.gui");
   exec("./ui/GameTextGui.gui");
   exec("./ui/TomeGui.gui");
   
   exec("./ui/PartyWnd.gui");
   exec("./ui/PetWnd.gui");
   exec("./ui/TacticalGui.gui");
   exec("./ui/MacroWnd.gui");
   exec("./ui/DefaultCommandsWnd.gui");
   exec("./ui/CharMiniWnd.gui");
   exec("./ui/BuffWnd.gui");
   exec("./ui/LootWnd.gui");
   exec("./ui/NPCWnd.gui");
   exec("./ui/LeaderWnd.gui");
   exec("./ui/AllianceWnd.gui");
   exec("./ui/TradeWnd.gui");
   exec("./ui/InnWnd.gui");
   exec("./ui/ItemInfoWnd.gui");
   exec("./ui/TrackingWnd.gui");
   exec("./ui/GameOptionsWnd.gui");
   exec("./ui/CharPortraitWnd.gui");
   exec("./ui/PatchInfoWnd.gui");
   exec("./ui/MapWnd.gui");
   exec("./ui/HelpWnd.gui");
   exec("./ui/JournalNewEntryWnd.gui");
   exec("./ui/JournalWnd.gui");
   exec("./ui/SPGlobalChatGui.gui");
   exec("./ui/MacroEditorWnd.gui");
   exec("./ui/ChooseIconWnd.gui");
   exec("./ui/EncyclopediaWnd.gui");
   exec("./ui/EncyclopediaSearchDlg.gui");
   exec("./ui/PatcherGui.gui");
   exec("./ui/NewMonsterSelection.gui");
   exec("./ui/DirectConnectWnd.gui");
   exec("./ui/ResurrectionGui.gui");
   exec("./ui/VaultWnd.gui");
   exec("./ui/lostPasswordDlg.gui");
   exec("./ui/FriendsWnd.gui");
   exec("./ui/CharRenameWnd.gui");
   exec("./ui/CharDeleteWnd.gui");
   exec("./ui/TgtDescWnd.gui");
   exec("./ui/ItemContainerWnd.gui");

   //exec("./ui/DemoNagGui.gui");
   exec("./ui/DemoInfoWnd.gui");
   

   //-----------------------------------------------
   // Lighting Pack code block
   //-----------------------------------------------
   exec("./ui/sgLightEditor.gui");
   exec("./ui/sgLightEditorNewDB.gui");
   //-----------------------------------------------
   // Lighting Pack code block
   //-----------------------------------------------
   

   // Client scripts
   exec("./scripts/client.cs");
   exec("./scripts/game.cs");
   exec("./scripts/missionDownload.cs");
   exec("./scripts/serverConnection.cs");
   exec("./scripts/playerList.cs");
   exec("./scripts/loadingGui.cs");
   exec("./scripts/optionsDlg.cs");
//   exec("./scripts/chatHud.cs");
//   exec("./scripts/messageHud.cs");
   exec("./scripts/playGui.cs");
   exec("./scripts/centerPrint.cs");

   // Default player key bindings
   exec("./scripts/default.bind.cs");
   exec("./config.cs");

   exec("./scripts/rpg/mission.cs");

   


   // Really shouldn't be starting the networking unless we are
   // going to connect to a remote server, or host a multi-player
   // game.
   setNetPort(0);

   // Copy saved script prefs into C++ code.
   setShadowDetailLevel( $pref::shadows );
   setDefaultFov( $pref::Player::defaultFov );
   setZoomSpeed( $pref::Player::zoomSpeed );

   // Start up the main menu... this is separated out into a 
   // method for easier mod override.

   if ($JoinGameAddress !$= "") {
      // If we are instantly connecting to an address, load the
      // main menu then attempt the connect.
      loadMainMenu();
      connect($JoinGameAddress, "", $Pref::Player::Name);
   }
   else {
      // Otherwise go to the splash screen.
      Canvas.setCursor("DefaultCursor");
      //loadStartup();
	  loadMainMenu();
	  }
}


//-----------------------------------------------------------------------------


function loadMainMenu()
{
   // Startup the client with the Main menu...
   Canvas.setContent( MainMenuGui );
   Canvas.pushDialog( EULAWnd );
   FadeWnd.fadeinTime = 400;
   Canvas.pushDialog( FadeWnd );
   if ($displayPatch)
      Py::DisplayPatchInfo();


   // Make sure the audio initialized.
   if($Audio::initFailed) {
      MessageBoxOK("Audio Initialization Failed", 
         "The OpenAL audio system failed to initialize.  " @
         "You can get the most recent OpenAL drivers at http://openal.org/downloads.html");
   }

   Canvas.setCursor("DefaultCursor");
}


