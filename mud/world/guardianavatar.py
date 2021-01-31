# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.avatar import Avatar
from mud.common.permission import User,Role
from mud.world.defines import RPG_MSG_SPEECH_SYSTEM
from mud.world.guardiancommand import DoGuardianCommand
from mud.world.player import Player



class GuardianAvatar(Avatar):
    def __init__(self, username, role, mind):
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.mind = mind
        self.player = Player.byPublicName(username)
        from mud.world.theworld import World
        self.world = World.byName("TheWorld")
    
    
    def perspective_command(self, cmd, args):
        DoGuardianCommand(self.player,cmd,args)
    
    
    def perspective_chat(self, args):
        # If the message is empty, return.
        if not len(args):
            return
        
        # Get the GM's character name, with and without chat pseudo formatting.
        name = self.player.charName
        sname = name.replace(' ','_')
        
        # Assemble the message.
        msg = ' '.join(args)
        msg = r'GM: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(sname,name,msg)
        
        # Get a handle to the world the GM is in.
        world = self.player.world
        
        # If this server uses multiple clusters, need to propagate the GM
        #  message across them.
        if world.daemonPerspective:
            world.daemonPerspective.callRemote("propagateCmd","receiveGMChat",name,msg)
        
        # Run through this servers players and send the GM's the message.
        for p in world.activePlayers:
            # Exclude all players without GM status.
            if p.role.name == "Immortal" or p.role.name == "Guardian":
                p.sendSpeechText(RPG_MSG_SPEECH_SYSTEM,msg,name)


