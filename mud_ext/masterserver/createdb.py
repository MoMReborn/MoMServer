# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#!/usr/bin/env python

import sys,os
sys.path.append(os.getcwd())
sys.argv.append('database=data/master')

from mud_ext.server.config import ConfigureServer,LoadConfiguration
from mud.common.permission import Role,TablePermission,ColumnPermission,User
from mud.common.avatar import RoleAvatar,Avatar
from mud_ext.masterserver.masterdb import *

CONFIG = {}

def ConfigureRoles():
    registration = Role(name="Registration")
    RoleAvatar(name="RegistrationAvatar",role=registration)

    enumWorlds = Role(name="EnumWorlds")
    RoleAvatar(name="EnumWorldsAvatar",role=enumWorlds)


    player = Role(name="Player")
    RoleAvatar(name="EnumWorldsAvatar",role=player)
    RoleAvatar(name="PlayerAvatar",role=player)
    
    world = Role(name="World")
    RoleAvatar(name="NewWorldAvatar",role=world)
    RoleAvatar(name="WorldAvatar",role=world)
    RoleAvatar(name="EnumWorldsAvatar",role=world)
    
    character = Role(name="CharacterServer")
    RoleAvatar(name="CharacterAvatar",role=character)

    
def ConfigureUsers():
    reg = User(name="Registration",password="Registration")
    reg.addRole(Role.byName("Registration"))
    
    enumWorlds = User(name="EnumWorlds",password="EnumWorlds")
    enumWorlds.addRole(Role.byName("EnumWorlds"))
        
    cserver = User(name="CharacterServer",password=CONFIG["Character Server Password"])
    cserver.addRole(Role.byName("CharacterServer"))


def InitTables():
    TABLES = [World,RegKey,Account,Product,Role,User,TablePermission,ColumnPermission,RoleAvatar]

    #for now we'll drop and recreate the tables every time
    for t in TABLES:
        t.dropTable(ifExists=True)
        t.createTable()


def main():
    LoadConfiguration(CONFIG)
    ConfigureServer("master.db")
    InitTables()
    ConfigureRoles()
    ConfigureUsers()


if __name__ == '__main__':
    print "Creating Master Database..."
    main()
    print "Done!"

