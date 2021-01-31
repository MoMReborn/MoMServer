# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from tgenative import *
from mud.tgepython.console import TGEExport
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from mud.world.defines import *
from mud.client.playermind import formatMLString
from mud.gamesettings import *
from gui.tomeGui import TomeGui
receiveGameText = TomeGui.instance.receiveGameText
receiveSpeechText = TomeGui.instance.receiveSpeechText
from cPickle import load,dump
import re



#RPG_MSG_SPEECH_WORLD:"FFFFFF",
#RPG_MSG_SPEECH_ZONE:"B8C323",
#RPG_MSG_SPEECH_PARTY:"2896EA",
#RPG_MSG_SPEECH_SAY:"28EA44",
#RPG_MSG_SPEECH_AUCTION:"EA4828",
#RPG_MSG_SPEECH_GLOBAL:"06FFFC",
#RPG_MSG_SPEECH_NPC:"BAEA38",
#RPG_MSG_SPEECH_ALLIANCE:"2896EA",
#RPG_MSG_SPEECH_PET:"E0EA38",
#RPG_MSG_SPEECH_SYSTEM:"FFFF00",
#RPG_MSG_SPEECH_TELL:"BBBBFF",
#RPG_MSG_SPEECH_TOLD:"BBFFBB",
#RPG_MSG_SPEECH_EMOTE:"ECB3EB",
#RPG_MSG_SPEECH_OT:"E7E2EF",
#RPG_MSG_SPEECH_HELP:"79FF21",
#RPG_MSG_SPEECH_PLAYERJOINED:"E8EA38",


DISCONNECT = False
IRC = None
USERNAME = ""
MUTETIME = 0

GLOBAL_ON  = True
HELP_ON = True
OT_ON = True

#
# Respond list variables used when responding to a tell.
# 
MAX_RESPONDERS          = 10 # Max number of responders to remember.
CURRENT_RESPONDER_INDEX = 0 # Current responder index used during cycling.
RESPONDER_LIST          = [] # List of responders.
TOME_CMD_CTRL           = None # Handle to gui object.

#
# Away message variables.
#
CUSTOM_AWAY_PREFIX  = "Away Message:" # Prefix used for custom away messages.
DEFAULT_AWAY_MSG    = "Sorry, I am away right now." # Default away message.
AWAY_MSG            = DEFAULT_AWAY_MSG #
PLAYER_IS_AWAY      = False

STRIPMULTISPACES = re.compile(' +')



def SetAwayMessage(msg):
    """Called when /away or /afk command is entered.  This sets
       the users away status and away message.
    """
    global AWAY_MSG
    global PLAYER_IS_AWAY

    #
    # If any away message is provided, turn away on.
    # 
    if msg:
        PLAYER_IS_AWAY = True
        
        #
        # Strip multiple spaces.
        #
        msg = STRIPMULTISPACES.sub(' ',msg)
        
        #
        # Set custom away message.
        #
        AWAY_MSG = "%s %s" % (CUSTOM_AWAY_PREFIX, msg)
        
        #
        # Inform player.
        #
        receiveSpeechText(RPG_MSG_SPEECH_SYSTEM,r'You are away.\n')
        
    #
    # Caller did not provide a message.  Toggle away state, and set
    # custom message to the default away message.
    #
    else:
        PLAYER_IS_AWAY = not PLAYER_IS_AWAY
        
        #
        # Set custom afk to print the default afk message.
        #
        if PLAYER_IS_AWAY:
            AWAY_MSG = DEFAULT_AWAY_MSG
            receiveSpeechText(RPG_MSG_SPEECH_SYSTEM,r'You are away.\n')
        else:
            receiveSpeechText(RPG_MSG_SPEECH_SYSTEM,r'You are no longer away.\n')


def AddTeller(lastTeller):
    """Called when the irc client receives a tell.  This adds the sender
       to a responder list so that the name can be used during replies.
       Newer responders are inserted at the start of the list.
    """
    global RESPONDER_LIST
    global CURRENT_RESPONDER_INDEX
    
    #
    # The responder index needs reset each time a tell is received.
    #
    CURRENT_RESPONDER_INDEX = 0

    #
    # Iterate through the reponder queue.
    # 
    for index,responder in enumerate(RESPONDER_LIST):

        #
        # If the last tell is in the responser list.  Remove from
        # the current index and insert at the start of the list.
        # 
        if responder == lastTeller:
            
            #
            # If they are the last responder, do not change list.  
            if index:
                del RESPONDER_LIST[index]
                RESPONDER_LIST.insert(0, lastTeller)
            break
         
    #
    # New responser.  This is the first time the teller has sent a 
    # tell to the client.
    #       
    else:
        #
        # Insert at the start.
        #
        RESPONDER_LIST.insert(0, lastTeller)
        
        #
        # If the list is full, remove the oldest responder.
        #
        if MAX_RESPONDERS == len(RESPONDER_LIST):
            RESPONDER_LIST.pop()


def CycleReply(args):
    """CycleReply is called from TorqueScript.  This function
       opens the chat window and sets the text to /tell player.
       This function expects a single value in a tuple.  
         -1 = Cycle reply to a newer teller.
          0 = No cycle.           
          1 = Cycle reply to an older teller.
    """
    #
    # Open chat.
    #
    TGECall("PushChatGui")    
    TOME_CMD_CTRL.visible = True
    TOME_CMD_CTRL.makeFirstResponder(True)
    
    #
    # If no one has sent a tell, set chat to "/tell ".
    #
    if not RESPONDER_LIST:
        TOME_CMD_CTRL.setValue("/tell ")
        return

    cycleDirection = int(args[1])
    global CURRENT_RESPONDER_INDEX
    
    #
    # Cycle to a newer teller.
    #
    if -1 == cycleDirection:
        #
        # If current index is not 0, decrease index by one.  Otherwise
        # wrap the index to the oldest teller.
        #
        if CURRENT_RESPONDER_INDEX:
            CURRENT_RESPONDER_INDEX -= 1 
        else:
            CURRENT_RESPONDER_INDEX = len(RESPONDER_LIST) - 1
    #
    # Cycle to an older teller.
    #
    elif 1 == cycleDirection:
        #
        # If the current index is not at the end of the list, increase
        # the index by one.  Otherwise, wrap to the newest teller.
        # 
        if ( len(RESPONDER_LIST) - 1 ) != CURRENT_RESPONDER_INDEX: 
            CURRENT_RESPONDER_INDEX += 1
        else:
            CURRENT_RESPONDER_INDEX = 0

    TOME_CMD_CTRL.setValue("/tell %s " % RESPONDER_LIST[CURRENT_RESPONDER_INDEX])


def SetMuteTime(t):
    global MUTETIME
    if MUTETIME and not t:
        receiveSpeechText(RPG_MSG_SPEECH_SYSTEM,r'You are no longer muted.\n')
    
    if not MUTETIME and t:
        m = t / 60 + 1
        if m > 59:
            receiveSpeechText(RPG_MSG_SPEECH_ERROR,r'You have been muted.\n')
        else:
            receiveSpeechText(RPG_MSG_SPEECH_ERROR,r'You have been muted and will be able to speak in %i minutes.\n'%m)
    
    MUTETIME = t


def CheckMuted():
    if MUTETIME:
        m = MUTETIME / 60 + 1
        if m > 59:
            receiveSpeechText(RPG_MSG_SPEECH_ERROR,r'You have been muted.\n')
        else:
            receiveSpeechText(RPG_MSG_SPEECH_ERROR,r'You have been muted and will be able to speak in %i minutes.\n'%m)
        return True
    return False


def FilterChannel(channel,value):
    global GLOBAL_ON,HELP_ON,OT_ON
    if channel in ('O','OFFTOPIC'):
        OT_ON = value
    elif channel in ('H','HELP'):
        HELP_ON = value
    elif channel in ('M','MOM'):
        GLOBAL_ON = value



class MyIRCClient(irc.IRCClient):
    def connectionMade(self):
        global IRC
        IRC = self
        self.nickname = self.factory.nickname
        irc.IRCClient.connectionMade(self)
    
    
    def connectionLost(self, reason):
        global IRC
        IRC = None
        irc.IRCClient.connectionLost(self, reason)
    
    
    def irc_ERR_NOSUCHNICK(self,prefix,params):
        mynick, their_nick, error = params
        
        receiveSpeechText(RPG_MSG_SPEECH_ERROR,r'%s is not currently logged in.  If you are messaging a monster, please replace any spaces in their name with underscores.\n'%their_nick)
    
    
    # Callbacks for events
    
    def irc_RPL_NAMREPLY(self,prefix, params):
        pass #should remove this
        #if params[2]==IRC_CHANNEL_OFF_TOPIC:
        #    receiveSpeechText(RPG_MSG_SPEECH_PLAYERJOINED,"Players in chat: %s \\n"%params[3])
    
    
    def userJoined(self, user, channel):
        """Called when I see another user joining a channel.
        """
        pass
        #if user.upper() in IGNORED:
        #    return

        #if channel == IRC_CHANNEL_OFF_TOPIC:
        #    receiveSpeechText(RPG_MSG_SPEECH_PLAYERJOINED,r'%s has joined chat\n'%(user))
    
    
    def userLeft(self, user, channel):
        """Called when I see another user leaving a channel.
        """
        pass
        #if user.upper() in IGNORED:
        #    return

        #if channel == IRC_CHANNEL_OFF_TOPIC:
        #    receiveSpeechText(RPG_MSG_SPEECH_PET,r'%s has left chat.\n'%(user))
    
    
    def userQuit(self, user, quitMessage):
        """Called when I see another user disconnect from the network.
        """
        #if user.upper() in IGNORED:
        #    return

        #receiveSpeechText(RPG_MSG_SPEECH_PET,r'%s has left chat.\n'%(user))
        pass
    
    
    def userKicked(self, kickee, channel, kicker, message):
        """Called when I observe someone else being kicked from a channel.
        """
        pass
        
        #if user.upper() in IGNORED:
        #    return

        #if channel == IRC_CHANNEL_OFF_TOPIC:
        #    receiveSpeechText(RPG_MSG_SPEECH_PET,r'%s was kicked from chat by %s (%s)\n'%(kickee,kicker,message))
    
    
    def topicUpdated(self, user, channel, newTopic):
        pass
        #if channel == IRC_CHANNEL_OFF_TOPIC:
        #receiveSpeechText(RPG_MSG_SPEECH_PET,r'%s has changed the  (%s)\n'%(kickee,kicker,message))
    
    
    def userRenamed(self, oldname, newname):
        pass      
        #receiveSpeechText(RPG_MSG_SPEECH_PET,r'%s is now known as %s\n'%(oldname,newname))
    
    
    ### Information from the server.
    
    def receivedMOTD(self, motd):
        """I received a message-of-the-day banner from the server.

        motd is a list of strings, where each string was sent as a seperate
        message from the server. To display, you might want to use::

            '\\n'.join(motd)

        to get a nicely formatted string.
        """
        pass
    
    
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
            receiveSpeechText(RPG_MSG_SPEECH_HELP,"You have joined chat.\\n")
        
        #self.player.irc = self
    
    
    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        if not self.live:
            return
        
        if DISCONNECT:
            self.sendLine("QUIT :%s" % "Errant IRC connection closed")
            return
        
        #filters!
        if channel == IRC_CHANNEL_OFF_TOPIC and not OT_ON:
            return
        if channel == IRC_CHANNEL_GLOBAL and not GLOBAL_ON:
            return
        if channel == IRC_CHANNEL_HELP and not HELP_ON:
            return
        
        #
        # Clean user name and message.
        #
        user = user.split('!', 1)[0]
        userPretty = user.replace("_"," ")
        msg = msg.replace("\\","")
        msg = formatMLString(msg)
        
        #ignores
        from gui.playerSettings import PLAYERSETTINGS
        if userPretty.upper() in PLAYERSETTINGS.ignored:
            return
        
        if channel.upper() == self.nickname.upper():
            #
            # Check if chat window needs opened.
            #
            try:
                if int(TGEGetGlobal("$pref::gameplay::OpenChatOnTells")):
                    TGECall("PushChatGui")
            except:
                TGESetGlobal("$pref::gameplay::OpenChatOnTells", 0)

            #
            # Prin tht received message to the player.
            # 
            receiveSpeechText(RPG_MSG_SPEECH_TELL,r'<a:gamelinkcharlink%s>%s</a> tells you, \"%s\"\n'%(user,userPretty,msg))

            #
            # If it was a /tell and the player is afk, send an auto response.
            #
            if PLAYER_IS_AWAY:
     
                #
                # Do not respond with afk message when:
                #   - MoM sent the tell.
                #   - The player sent a tell to his/herself.
                #   - Received message was an afk response. 
                #
                userUpper = user.upper()
                if "MOM" != userUpper and channel.upper() != userUpper and not msg.startswith(DEFAULT_AWAY_MSG) and not msg.startswith(CUSTOM_AWAY_PREFIX):
                    receiveSpeechText(RPG_MSG_SPEECH_TOLD, r'You tell <a:gamelinkcharlink%s>%s</a>, \"%s\"\n' % (user,userPretty,formatMLString(AWAY_MSG)))
                    self.msg(user, AWAY_MSG)
            
            #
            # Add the user to the response list.
            #  
            AddTeller(user)
            
        else:
            if channel == IRC_CHANNEL_GLOBAL:
                receiveSpeechText(RPG_MSG_SPEECH_GLOBAL,r'MoM: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(user,userPretty,msg))
            elif channel == IRC_CHANNEL_HELP:
                receiveSpeechText(RPG_MSG_SPEECH_HELP,r'Help: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(user,userPretty,msg))
            elif channel == IRC_CHANNEL_OFF_TOPIC:
                receiveSpeechText(RPG_MSG_SPEECH_OT,r'OT: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(user,userPretty,msg))
            
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
        suser = user.split('!', 1)[0]
        user = suser.replace("_"," ")
        #print user
        #self.logger.log("* %s %s" % (user, msg))
        
        #IGNORE!
        from gui.playerSettings import PLAYERSETTINGS
        if user.upper() in PLAYERSETTINGS.ignored:
            return
        
        #filters!
        if channel == IRC_CHANNEL_OFF_TOPIC and not OT_ON:
            return
        if channel == IRC_CHANNEL_GLOBAL and not GLOBAL_ON:
            return
        if channel == IRC_CHANNEL_HELP and not HELP_ON:
            return
        
        msg = msg.replace("\\","")
        receiveSpeechText(RPG_MSG_SPEECH_EMOTE,r'<a:gamelinkcharlink%s>%s</a> %s\n'%(suser,user,formatMLString(msg)))



class IRCFactory(protocol.ClientFactory):
    def __init__(self, nickname,channel):
        self.nickname = nickname
        self.channel = channel
        self.protocol = MyIRCClient
    
    def buildProtocol(self,addr):
        print addr.host
        
        p = protocol.ClientFactory.buildProtocol(self,addr)
        p.live = False
        p.nickname = self.nickname
        
        return p


#COMMANDS['ME']=CmdGlobalEmote
#COMMANDS['GE']=CmdGlobalEmote
#COMMANDS['GEMOTE']=CmdGlobalEmote
#COMMANDS['GWHO']=CmdGlobalWho


def ChangeNick(name):
    name = name.replace(" ","_")
    try:
        IRC.setNick(name)
    except:
        pass

def IRCConnect(name):
    global IRC
    if IRC:
        try:
            IRCDisconnect()
        except:
            pass
    IRC = None
    
    #
    # Set player to not be afk each time they log into chat.
    #
    global PLAYER_IS_AWAY
    PLAYER_IS_AWAY = False
    
    #
    # Get handle to tome command control.
    #
    global TOME_CMD_CTRL
    TOME_CMD_CTRL = TomeGui.instance.tomeCommandCtrl
    
    name = name.replace(" ","_")
    cf = IRCFactory(name,IRC_CHANNEL_GLOBAL)
    reactor.connectTCP(IRC_SERVER, IRC_PORT, cf)
    ReceiveSpeechText(RPG_MSG_SPEECH_HELP,"Connecting to chat services.\\n")


def IRCDisconnect():
    global IRC
    if IRC:
        i = IRC
        IRC = None
        i.transport.loseConnection()


def GlobalMsg(msg):
    if not IRC or not len(msg) or CheckMuted():
        return
    
    name = IRC.nickname
    sname = name.replace("_"," ")
    receiveSpeechText(RPG_MSG_SPEECH_GLOBAL,r'MoM: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(name,sname,formatMLString(msg)))
    IRC.msg(IRC_CHANNEL_GLOBAL, msg)


def OTMsg(msg):
    if not IRC or not len(msg) or CheckMuted():
        return
    
    name = IRC.nickname
    sname = name.replace("_"," ")
    receiveSpeechText(RPG_MSG_SPEECH_OT,r'OT: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(name,sname,formatMLString(msg)))
    IRC.msg(IRC_CHANNEL_OFF_TOPIC, msg)


def HelpMsg(msg):
    if not IRC or not len(msg) or CheckMuted():
        return
    
    name = IRC.nickname
    sname = name.replace("_"," ")
    receiveSpeechText(RPG_MSG_SPEECH_HELP,r'Help: <<a:gamelinkcharlink%s>%s</a>> %s\n'%(name,sname,formatMLString(msg)))
    IRC.msg(IRC_CHANNEL_HELP, msg)


def SendIRCMsg(channel,msg):
    if CheckMuted():
        return
    
    msg = msg.replace("\\","")
    
    if channel in ('O','OFFTOPIC'):
        OTMsg(msg)
    if channel in ('H','HELP'):
        HelpMsg(msg)
    if channel in ('M','MOM'):
        GlobalMsg(msg)


def IRCTell(nick,msg):
    if CheckMuted():
        return
    
    receiveSpeechText(RPG_MSG_SPEECH_TOLD,r'You tell <a:gamelinkcharlink%s>%s</a>, \"%s\"\n'%(nick.replace(' ','_'),nick,formatMLString(msg).replace("\\","\\\\")))
                      
    IRC.msg(nick, msg)
    
    #
    # Reset responder cycle index to last resonder.
    #
    global CURRENT_RESPONDER_INDEX
    CURRENT_RESPONDER_INDEX = 0


def IRCEmote(lastchannel,emote):
    if CheckMuted():
        return
    
    channel = IRC_CHANNEL_OFF_TOPIC
    if lastchannel in ('M','MOM'):
        channel = IRC_CHANNEL_GLOBAL
    elif lastchannel in ('H','HELP'):
        channel = IRC_CHANNEL_HELP
    
    name = IRC.nickname
    sname = name.replace("_"," ")
    receiveSpeechText(RPG_MSG_SPEECH_EMOTE,r'<a:gamelinkcharlink%s>%s</a> %s.\n'%(name,sname,formatMLString(emote)))
    IRC.ctcpMakeQuery(channel, [('ACTION', emote)])

