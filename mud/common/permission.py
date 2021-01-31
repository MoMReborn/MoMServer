# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#Todo, add granting permissions for giving other users permissions
from sqlobject import *
import sqlobject.classregistry as classregistry
from twisted.spread import pb
from mud.common.persistent import Persistent,PersistentGhost
import traceback


class ColumnPermission(Persistent):
    name = StringCol(notNone=True)
    type = StringCol(notNone=True)
    read = BoolCol(default=False)
    write = BoolCol(default=False)    
    alternateID = BoolCol(default=False)    
    table_permission = ForeignKey('TablePermission')
    
class ColumnPermissionGhost(PersistentGhost):
    def __init__(self):
        PersistentGhost.__init__(self)
        self.primaryKey = 'name'

pb.setUnjellyableForClass(ColumnPermission, ColumnPermissionGhost) 


    
        
class TablePermission(Persistent):
    name = StringCol(notNone=True)
    read = BoolCol(default=False)
    write = BoolCol(default=False)
    insert = BoolCol(default=False,dbName="iinsert")
    delete = BoolCol(default=False,dbName="ddelete")
    update = BoolCol(default=False,dbName="uupdate")    
    columnPermissions=MultipleJoin('ColumnPermission')
    
    role = ForeignKey('Role')
    
    def _init(self,*args,**kw):
        Persistent._init(self,*args,**kw)
        self.tableClass=classregistry.registry(None).getClass(self.name)
    
    def grantColumn(self,columnName,read=False,write=False):
        for c in self.columnPermissions:
            if c.name == columnName:
                c.read=read
                c.write=write
                return
        #new column permission
        #XXX check that column exists

        #get type
        t = None
        for c in self.tableClass._columns:
            if columnName == c.name:
                t = c.__class__.__name__
                try:
                    alternateID = c.kw['alternateID']
                except:
                    alternateID = False
                break
                
        if not t: #join
            for j in self.tableClass._joins:
                if columnName == j.joinMethodName:
                    t = 'Join'
                    alternateID=False
                    break
                    
        if not t:
            traceback.print_stack()
            print "AssertionError: type is still None!"
            return None
        
        return ColumnPermission(name=columnName,read=read,write=write,alternateID=alternateID,type=t,table_permission=self)
        
    def getColumnPermission(self,columnName):
        for c in self.columnPermissions:
            if c.name == columnName:
                return c
        return None
        
class TablePermissionGhost(PersistentGhost):
    def __init__(self):
        PersistentGhost.__init__(self)
        self.primaryKey = 'name'

pb.setUnjellyableForClass(TablePermission, TablePermissionGhost) 
                
        
class UserColumnPermissions(pb.Copyable,pb.RemoteCopy):
    def __init__(self,cpermission=None):
        if cpermission:
            #server side
            self.name = cpermission.name
            self.type = cpermission.type
            self.read = cpermission.read
            self.write = cpermission.write
            self.alternateID = cpermission.alternateID
            

class UserTablePermissions(pb.Copyable,pb.RemoteCopy):
    def __init__(self,tpermission=None):
        if tpermission:
            #server side
            attrs = ['read','write','update','delete','insert','name']
            for a in attrs:
                setattr(self,a,getattr(tpermission,a))
            
            self.columnPermissions = {}
            for cp in tpermission.columnPermissions:
                self.columnPermissions[cp.name]=UserColumnPermissions(cp)
        
class UserSchema(pb.Copyable,pb.RemoteCopy):
    def __init__(self,user=None):
        if user:
            #server side
            attrs = ['read','write','update','delete','insert']
            self.tablePermissions = {}
            for role in user.roles:
                for tp in role.tablePermissions:
                    if not self.tablePermissions.has_key(tp.name):
                        self.tablePermissions[tp.name]=UserTablePermissions(tp)
                    else:
                        utp = self.tablePermissions[tp.name]
                        #table permissions
                        for a in attrs:
                            if getattr(tp,a):
                                setattr(utp,a,True)
                        #column permissions
                        for cp in tp.columnPermissions:
                            ucp = utp.columnPermissions[cp.name]
                            if cp.read:
                                ucp.read = True
                            if cp.write:
                                ucp.write = True
                                
                        
pb.setUnjellyableForClass(UserColumnPermissions, UserColumnPermissions) 
pb.setUnjellyableForClass(UserTablePermissions, UserTablePermissions) 
pb.setUnjellyableForClass(UserSchema, UserSchema) 
                    

class Role(Persistent):
    name = StringCol(alternateID=True,notNone=True)
    restrictToLocalHost = BoolCol(default=True)
    tablePermissions=MultipleJoin('TablePermission')
    avatars=MultipleJoin('RoleAvatar')
    users=RelatedJoin('User')

    def grantTable(self,tclass,full=False):
        tp=TablePermission(name=tclass.__name__,role=self)
        if full:
            #full access
            tp.read=True
            tp.write=True
            tp.insert=True
            tp.delete=True
            tp.update=True
            
            for col in tclass._columns:
                tp.grantColumn(col.name,True,True)
            for join in tclass._joins:#and joins
                tp.grantColumn(join.joinMethodName,True,True)
                
        return tp
        
    def getTablePermission(self,tablename):
        for t in self.tablePermissions:
            if t.name==tablename:
                return t
        return None
        
    def getAvatar(self,avatarName):
        for a in self.avatars:
            if avatarName==a.name:
                return a
        return None
        
from random import choice
import string
def GenPasswd(length=32, chars=string.letters + string.digits):
    return ''.join([choice(chars) for i in xrange(length)])
    
class RoleGhost(PersistentGhost):
    def __init__(self):
        PersistentGhost.__init__(self)
        self.primaryKey = 'name'

pb.setUnjellyableForClass(Role, RoleGhost) 

BANNED_PRAIRIEWORLDS = 1
BANNED_ALLWORLDS = 2
BANNED_NUKED = 3

class User(Persistent):
    doPasswordHack = True
    name=StringCol(alternateID=True,notNone=True)
    password=StringCol(notNone=True)
    tempPassword = StringCol(default="")
    banLevel = IntCol(default=0)
    lastConnectSubnet = StringCol(default="") #should probably use all ips used to connect from
    roles=RelatedJoin('Role')
    
    def _init(self,*args,**kw):
        Persistent._init(self,*args,**kw)
        if User.doPasswordHack:
            self.tempPassword = GenPasswd()
        
    def getRole(self,rolename):
        for r in self.roles:
            if r.name == rolename:
                return r
        return None
    

class UserGhost(PersistentGhost):
    def __init__(self):
        PersistentGhost.__init__(self)
        self.primaryKey = 'name'

#banning
class BannedUser(Persistent):
    name = StringCol(alternateID=True)

class BannedIP(Persistent):
    address = StringCol(alternateID=True)


pb.setUnjellyableForClass(User, UserGhost) 

    
