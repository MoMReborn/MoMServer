# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

#  The defines module provides enumeration and constants used throughout
#  mud.

# Add back in the stuff that is missing from the MoM_Install version of this file. It is from the TMMOKit version
from mud.world.defines import *

RPG_BUILD_DEMO = False
RPG_BUILD_LIVE = False
RPG_BUILD_TESTING = False

def SetVersion(demo):
    global RPG_BUILD_DEMO
    RPG_BUILD_DEMO = demo


if RPG_BUILD_DEMO:
    RPG_BUILD_LIVE = True
    RPG_CLIENT_VERSION = "Free 1.26"
else:
    RPG_CLIENT_VERSION = "Premium 1.26"
    if not RPG_BUILD_LIVE:
        RPG_CLIENT_VERSION = "Test Version"

RPG_BUILD_LIMITED = RPG_BUILD_DEMO
