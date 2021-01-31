

function CreateLocalMission(%missionFile,%password)
{
   disconnect();
   %mission = $defaultGame @ "/data/missions/"@%missionFile;
   createServer("Multiplayer", %mission);
}

function ConnectLocalMission()
{
   %conn = new GameConnection(ServerConnection);
   RootGroup.add(ServerConnection);
   %conn.setConnectArgs($pref::PublicName);
   %conn.setJoinPassword($Client::Password);
   %conn.connectLocal();
}

function ConnectRemoteMission(%address,%password)
{
    disconnect();
    %conn = new GameConnection(ServerConnection);
    %conn.setConnectArgs($pref::FantasyName);
    %conn.setJoinPassword(%password);
    %conn.connect(%address);
}

