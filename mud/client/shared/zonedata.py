# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

class ZoneConnectionInfo(Ghost):
    def __init__(self):
        self.ip = ""
        self.port = -1
        self.login = ""
        self.password = ""
        
#hooks        
pb.setUnjellyableForClass(ZoneConnectionInfo, ZoneConnectionInfo)  

