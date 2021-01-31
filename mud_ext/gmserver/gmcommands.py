# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#GM commands
CHARSERVER_MIND = None

def SetCharServerMind(mind):
    global CHARSERVER_MIND
    CHARSERVER_MIND = mind
    
    
#--- Who

def GotWho(result,avatar):
    who = result
    
    num = 0
    text = ""
    for wname,info in who.iteritems():
        text += "----------------\n"
        text += "Players on world: %s\n"%wname
        for pname,cname in info.iteritems():
            if not cname:
                text += "Character: Logging In Account: %s\n"%(pname)
            else:
                text += "Character: %s Account: %s\n"%(cname,pname)
                
            num+=1
        text += "----------------\n"
        
            
    text += "%i characters displayed.\n"%num
    
    avatar.mind.callRemote("logText",text)
    

def CmdWho(avatar,args):
    world = ' '.join(args)
    
    if not CHARSERVER_MIND:
        avatar.mind.callRemote("logText","The character server is not current up.\n")
        return
    
    d = CHARSERVER_MIND.callRemote("gmWho",world)
    d.addCallback(GotWho,avatar)
    return d



#--- Character Change Name

def GotRenameCharacter(result,avatar):
    
    if result == 1:
        avatar.mind.callRemote("logText","\nCharacter flagged for rename.\n")
        return

    if result == -2:
        avatar.mind.callRemote("logText","\nUnknown Character, rename failed\n")
        return

    #if result == -3:
    #    avatar.mind.callRemote("logText","\nPlayer has been active within the last 2 minutes, rename failed.\n")
    #    return

    avatar.mind.callRemote("logText","\nUnknown error, rename character.\n")


def CmdRenameCharacter(avatar,args):
    #
    name = ' '.join(args)
    
    if not name:
        avatar.mind.callRemote("logText","\nUnknown Character, rename failed\n")
        return
        
    
    if not CHARSERVER_MIND:
        avatar.mind.callRemote("logText","The character server is not current up.\n")
        return
    
    d = CHARSERVER_MIND.callRemote("gmRenameCharacter",name)
    d.addCallback(GotRenameCharacter,avatar)
    return d


#--- Character Kick

def GotCharacterKick(result,avatar):
    if result == None:
        avatar.mind.callRemote("logText","\nUnknown Character\n")
        return
    
    cname,pname,minutes, active = result
    
    text = "\nCharacter %s owned by account %s has been kicked for %i minutes!\n"%(cname,pname,minutes)
    if active:
        text+="The character was active on the %s world server.  An attempt has been made to kick the player from the world server.\n"%active
            
    avatar.mind.callRemote("logText",text)
    

def CmdCharacterKick(avatar,args):
    if len(args) < 2:
        avatar.mind.callRemote("logText","You must specify a character and amount of time in minutes.\n")
        return
    
    minutes = args.pop()
    
    try:
        minutes = int(minutes)
    except:
        avatar.mind.callRemote("logText","You must specify a character and amount of time in minutes.\n")
        return
        
        
    if not CHARSERVER_MIND:
        avatar.mind.callRemote("logText","The character server is not current up.\n")
        return
    
    d = CHARSERVER_MIND.callRemote("gmKickCharacter",' '.join(args),minutes)
    d.addCallback(GotCharacterKick,avatar)
    return d


def GotCharacterMute(result,avatar):
    if result == None:
        avatar.mind.callRemote("logText","\nUnknown Character\n")
        return
    
    cname,pname,minutes, active = result
    
    text = "\nCharacter %s owned by account %s has been muted for %i minutes! (This may take up to 2 minutes to take effect)\n"%(cname,pname,minutes)
            
    avatar.mind.callRemote("logText",text)
    

def CmdCharacterMute(avatar,args):
    if len(args) < 2:
        avatar.mind.callRemote("logText","You must specify a character and amount of time in minutes.\n")
        return
    
    minutes = args.pop()
    
    try:
        minutes = int(minutes)
    except:
        avatar.mind.callRemote("logText","You must specify a character and amount of time in minutes.\n")
        return
        
        
    if not CHARSERVER_MIND:
        avatar.mind.callRemote("logText","The character server is not current up.\n")
        return
    
    d = CHARSERVER_MIND.callRemote("gmMuteCharacter",' '.join(args),minutes)
    d.addCallback(GotCharacterMute,avatar)
    return d

def GotCharacterUnmute(result,avatar):
    if result == None:
        avatar.mind.callRemote("logText","\nUnknown Character\n")
        return
    
    cname,pname = result
    
    text = "\nCharacter %s owned by account %s has been unmuted. (This may take up to 2 minutes to take effect)\n"%(cname,pname)
            
    avatar.mind.callRemote("logText",text)
    

def CmdCharacterUnmute(avatar,args):
    if len(args) < 1:
        avatar.mind.callRemote("logText","You must specify a character to unmute.\n")
        return
        
    if not CHARSERVER_MIND:
        avatar.mind.callRemote("logText","The character server is not current up.\n")
        return
    
    d = CHARSERVER_MIND.callRemote("gmUnmuteCharacter",' '.join(args))
    d.addCallback(GotCharacterUnmute,avatar)
    return d



#--- Character Info

def GotCharacterInfo(result,avatar):
    if result == None:
        avatar.mind.callRemote("logText","\nUnknown Character\n")
        return
        
    cname,pname,characters,active,subnet = result
    
    #from sqlite on server
    chars = []
    for c in characters:
        chars.append(c[0])        
    characters = chars
        
    
    text = "\nCharacter Information for %s:\n"%cname
    text +="-------------------------------\n"
    
    text +="Account: %s\n"%pname
    
    text +="Characters: %s\n"%(', '.join(characters))
    
    if not active:
        text +="Activity: No Current Data\n"
    else:
        tm = active[1]/60
        if tm < 1:
            tm = 1
        text +="Activity: %s as of %i minutes ago.\n"%(active[0],tm)
        
    text +="Last recorded subnet: %s\n"%subnet
        
    
    avatar.mind.callRemote("logText",text)

def CmdCharacterInfo(avatar,args):
    if not len(args):
        avatar.mind.callRemote("logText","You must specify a character to get information on.\n")
        return
        
    if not CHARSERVER_MIND:
        avatar.mind.callRemote("logText","The character server is currently not available.\n")
        return
    
    d = CHARSERVER_MIND.callRemote("gmGetCharacterInfo",' '.join(args))
    d.addCallback(GotCharacterInfo,avatar)
    return d
    
def GotRaffleTicket(result,avatar):
    if result == "":
        avatar.mind.callRemote("logText","\nNo Raffle Ticket Awarded\n")
        return
        
    avatar.mind.callRemote("logText","\nRaffle Ticket awarded to %s\n"%result)


def CmdRaffleTicket(avatar,args):
        
    if not CHARSERVER_MIND:
        avatar.mind.callRemote("logText","The character server is currently not available.\n")
        return
    
    d = CHARSERVER_MIND.callRemote("gmAwardTicket")
    
    d.addCallback(GotRaffleTicket,avatar)
    
    return d



COMMANDS = {}
COMMANDS['CINFO'] = CmdCharacterInfo
COMMANDS['CKICK'] = CmdCharacterKick
COMMANDS['CMUTE'] = CmdCharacterMute
COMMANDS['CUNMUTE'] = CmdCharacterUnmute
COMMANDS['CRENAME'] = CmdRenameCharacter
COMMANDS['WHO'] = CmdWho
COMMANDS['RAFFLETICKET'] = CmdRaffleTicket



def DoGMCommand(gmavatar, command):
    command = str(command)
    args = command.split(" ")[1:]
    command = args[0].upper()
    
    if command == "RAFFLETICKET" and gmavatar.username.lower() != "pgsupport":
        return
    
    if not COMMANDS.has_key(command):
        gmavatar.mind.callRemote("logText","Unknown command %s\n"%command)
        return
    
    COMMANDS[command](gmavatar,args[1:])

