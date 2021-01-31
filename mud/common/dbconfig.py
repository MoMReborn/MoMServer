# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from sqlobject import *

DBCONNECTION = None

HUB = dbconnection.ConnectionHub()
HUB.processConnection = None

def GetDBURI():
    return DBCONNECTION

def GetDBConnection():
    global HUB
    
    return HUB
    #return DBCONNECTION

def SetDBConnection(uri,finalize = False):
    from persistent import Persistent
    global DBCONNECTION,HUB
    DBCONNECTION = uri
    
    if finalize:
        Persistent._connection = dbconnection.connectionForURI(uri)
        return
    
    Persistent._connection = HUB
    
    #DBCONNECTION.debug=True
    #DBCONNECTION.debugOutput=True
    if not uri:
        dbconnection.TheURIOpener.cachedURIs = {} #DEBUG!!!
        if HUB.processConnection:
            
            try:
                HUB.processConnection.close()
                HUB.processConnection._conn.close()
                HUB.processConnection._conn=None
            except:
                pass
            
        HUB.processConnection = None
        
        return
    
    
    HUB.processConnection = dbconnection.connectionForURI(uri)
    
    
    
    
