from mud import gamesettings

def override_ip_addresses():
    gamesettings.MASTERIP = '127.0.0.1'  # master.minionsofmirth.net'
    gamesettings.GMSERVERIP = gamesettings.MASTERIP
    gamesettings.IRC_IP = '127.0.0.1'  # 'irc.prairiegames.com'