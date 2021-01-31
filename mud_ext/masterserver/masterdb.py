# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from twisted.spread import pb
from sqlobject import *
from datetime import datetime
from mud.common.persistent import Persistent,PersistentGhost

class ProductEmail(Persistent):
    email = StringCol(alternateID = True)
    product = StringCol()

class RegKey(Persistent):
    key = StringCol(alternateID = True)

class Product(Persistent):
    account = ForeignKey('Account')
    name = StringCol()
    
class Account(Persistent):
    regkey = StringCol(alternateID = True)
    publicName = StringCol(alternateID = True)
    email = StringCol(alternateID = True)
    password = StringCol(default="")
    creationTime = DateTimeCol(default = datetime.now)
    lastActivityTime = DateTimeCol(default = datetime.now)
    worlds = MultipleJoin('World')
    products = MultipleJoin('Product')
    
    def addProduct(self,name):
        Product(account=self,name=name.upper())
        
    def hasProduct(self,name):
        name = name.upper()
        for p in self.products:
            if p.name.upper() == name.upper():
                return True
            
        try:
            pe = ProductEmail.byEmail(self.email)
            if pe.product==name:
                account.addProduct(name)       
                pe.destroySelf()
                return True
        except:
            pass

            
        return False
    
class AccountGhost(PersistentGhost):
    def __init__(self):
        PersistentGhost.__init__(self)
        self.primaryKey = 'publicName'

pb.setUnjellyableForClass(Account, AccountGhost) 

class World(Persistent):
    name = StringCol(alternateID = True)
    maxLiveZones = IntCol()
    maxLivePlayers = IntCol()
    numLiveZones = IntCol(default = 0)
    numLivePlayers = IntCol(default = 0)
    #ok, this is grungy though I can clean this up later, allowGuests is being used for test worlds
    allowGuests = BoolCol(default=False)
    playerPassword = StringCol(default="")
    zonePassword = StringCol(default="")
    
    #note that lastAnnouce isn't meaningful until verified is True
    verified = BoolCol(default=False)
    announceTime = DateTimeCol(default = datetime(2000,1,1))
    announceIP = StringCol(default="")
    announcePort = IntCol(default=0)
    
    demoWorld = BoolCol(default=False)
    
    account = ForeignKey('Account')
    
    def _init(self,*args,**kw):
        Persistent._init(self, *args, **kw)
        
class WorldGhost(PersistentGhost):
    def __init__(self):
        PersistentGhost.__init__(self)
        self.primaryKey = 'name'

pb.setUnjellyableForClass(World, WorldGhost) 


        
