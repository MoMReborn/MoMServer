# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from mud.world.defines import *

class IRCFactory(protocol.ClientFactory):
    def __init__(self, nickname,channel):
        self.nickname = nickname
        self.channel = channel
        self.protocol = MyIRCClient
    
    def buildProtocol(self,addr):
        print addr.host
        
        p = protocol.ClientFactory.buildProtocol(self,addr)
        p.player = self.player
        p.live = False
        
        return p

class MyIRCClient(irc.IRCClient):
    
    def connectionMade(self):
        self.nickname = self.factory.nickname
        irc.IRCClient.connectionMade(self)

    def connectionLost(self, reason):
        if self.player:
            self.player.irc = None
        irc.IRCClient.connectionLost(self, reason)


    # callbacks for events
    
    def irc_RPL_NAMREPLY(self,prefix, params):
        if params[2]==IRC_CHANNEL_OFF_TOPIC:
            self.player.sendGameText(RPG_MSG_GAME_EVENT,"Players in chat: %s \\n"%params[3])
        
    def userJoined(self, user, channel):
        """Called when I see another user joining a channel.
        """
        if channel == IRC_CHANNEL_OFF_TOPIC:
            self.player.sendSpeechText(RPG_MSG_SPEECH_PLAYERJOINED,r'%s has joined chat\n'%(user))

    def userLeft(self, user, channel):
        """Called when I see another user leaving a channel.
        """
        if channel == IRC_CHANNEL_OFF_TOPIC:
            self.player.sendSpeechText(RPG_MSG_SPEECH_WORLD,r'%s has left Globat Chat\n'%(user))
        


    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        #self.join(self.factory.channel)
        self.join(IRC_CHANNEL_OFF_TOPIC) #off-topic
        self.join(IRC_CHANNEL_GLOBAL) #global
        self.join(IRC_CHANNEL_HELP) #help
        
        

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        #self.logger.log("[I have joined %s]" % channel)
        self.live = True        
        if channel == IRC_CHANNEL_OFF_TOPIC:
            self.player.sendGameText(RPG_MSG_GAME_EVENT,r'You have joined chat\n')
            #self.sendLine("/names\n")
        self.player.irc = self

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        if not self.live:
            return
        
        
        disconnect = False
        
        
        if not self.player or not self.player.mind:
            disconnect = True
        if self.player and self.player.world:
            if self.player not in self.player.world.activePlayers:
                disconnect = True
                
        if disconnect:
            self.sendLine("QUIT :%s" % "Errant IRC connection closed")
            return

        if channel == IRC_CHANNEL_OFF_TOPIC and not self.player.channelOffTopic:
            return

        if channel == IRC_CHANNEL_GLOBAL and not self.player.channelGlobal:
            return

        if channel == IRC_CHANNEL_HELP and not self.player.channelHelp:
            return
            
        
        user = user.split('!', 1)[0]
        
        msg = msg.replace("\\","")
        
        if user.upper() in self.player.ignored:
            return
        
        
        if channel == self.nickname:
            self.player.sendSpeechText(RPG_MSG_SPEECH_TELL,r'%s tells you, \"%s\"\n'%(user,msg))
        else:
            if channel == IRC_CHANNEL_GLOBAL:
                self.player.sendSpeechText(RPG_MSG_SPEECH_GLOBAL,r'Global: <%s> %s\n'%(user,msg))
            elif channel == IRC_CHANNEL_HELP:
                self.player.sendSpeechText(RPG_MSG_SPEECH_HELP,r'Help: <%s> %s\n'%(user,msg))
            elif channel == IRC_CHANNEL_OFF_TOPIC:
                self.player.sendSpeechText(RPG_MSG_SPEECH_OT,r'OT: <%s> %s\n'%(user,msg))
            
            
        #
        #self.logger.log("<%s> %s" % (user, msg))
        
        # Check to see if they're sending me a private message
        #if channel == self.nickname:
        #    msg = "It isn't nice to whisper!  Play nice with the group."
        #    self.msg(user, msg)
        #    return

        # Otherwise check to see if it is a message directed at me
        #if msg.startswith(self.nickname + ":"):
        #    msg = "%s: I am a log bot" % user
        #    self.msg(channel, msg)
        #    self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        #self.logger.log("* %s %s" % (user, msg))
        
        if user.upper() in self.player.ignored:
            return
        
        msg = msg.replace("\\","")
        self.player.sendSpeechText(RPG_MSG_SPEECH_EMOTE,r'%s %s.\n'%(user,msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        #old_nick = prefix.split('!')[0]
        #new_nick = params[0]
        #self.logger.log("%s is now known as %s" % (old_nick, new_nick))


 