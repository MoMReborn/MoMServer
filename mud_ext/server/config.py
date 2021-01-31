# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud.gamesettings import *
from mud_ext.server.serversettings import *


def ConfigureServer(DBNAME):
    import sys,os
    
    options={"database":""}
    
    database = ""
    
    # String options
    for option in ['database']:
        for x in xrange(len(sys.argv)):
            if sys.argv[x].find(option) == 0:
                pos = sys.argv[x].find('=') + 1
                if pos > 0 and options.has_key(option):
                    options[option]=sys.argv[x][pos:]
                    sys.argv[x] = ''
    
    DATABASE=options['database']
    
    from mud.common.dbconfig import SetDBConnection
    
    if not os.path.exists(DATABASE):
        os.makedirs(DATABASE)
        
    from mud.utils import getSQLiteURL
    SetDBConnection(getSQLiteURL('/%s/%s'%(DATABASE,DBNAME)),True)


def LoadConfiguration(config):
    #Patch Server
    s = SERVER_PATCH_PREMIUM
    up,address = s.split("@")
    user,password = up.split(":")

    config["Patch Server Premium"]=(address,user,password)

    s = SERVER_PATCH_DEMO
    up,address = s.split("@")
    user,password = up.split(":")

    config["Patch Server Demo"]=(address,user,password)

    #Master Port
    config["Master IP"] = MASTERIP
    config["Master Port"] = MASTERPORT

    #World
    config["World Username"] = SERVER_WORLD_USERNAME
    config["World Password"] = SERVER_WORLD_PASSWORD
    config["Default World Port"] = SERVER_DEFAULT_PORT

    #Manhole
    config["Manhole Username"] = SERVER_MANHOLE_USERNAME
    config["Manhole Password"] = SERVER_MANHOLE_PASSWORD
    config["Manhole Port"] = SERVER_MANHOLE_PORT

    #Character Server
    config["Character Server Password"] = SERVER_CSERVER_PASSWORD

    #Support Email
    config["Support Email Address"] = SERVER_EMAIL_ADDRESS
    config["Support Email Account"] = SERVER_EMAIL_ACCOUNT
    config["Support Email Password"] = SERVER_EMAIL_PASSWORD
    try:
        config["Support Email Server"] = SERVER_EMAIL_SERVER
    except:
        config["Support Email Server"] = ""
    try:
        config["Support Email Port"] = SERVER_EMAIL_PORT
    except:
        config["Support Email Port"] = 25


    #mysql
    try:
        config["MySQL User"] = SERVER_MYSQL_USER
        config["MySQL Password"] = SERVER_MYSQL_PASSWORD
    except:
        pass
