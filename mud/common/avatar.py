# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from sqlobject import *
from mud.common.persistent import Persistent,PersistentGhost
from mud.common.permission import User,UserSchema
from twisted.spread import pb

class MetaAvatar(type):
    avatarClasses = {}
    def __init__(cls, className, bases, d):
        type.__init__(cls,className,bases,d)
        MetaAvatar.avatarClasses[className]=cls
        
class Avatar(pb.Avatar,object):

    __metaclass__=MetaAvatar
    
    def createAvatar(classname):
        cls=MetaAvatar.avatarClasses[classname]
        return object.__new__(cls)
        
    createAvatar = staticmethod(createAvatar)


class RoleAvatar(Persistent):
    name = StringCol(notNone=True)
    role = ForeignKey('Role')
    
class RoleAvatarGhost(PersistentGhost):
    def __init__(self):
        PersistentGhost.__init__(self)
        self.primaryKey = 'name'

pb.setUnjellyableForClass(RoleAvatar, RoleAvatarGhost) 


class RoleEnumAvatar(Avatar):
    
    def __init__(self,username,role,mind):
        self.username=username
        self.role=role
        self.mind = mind
    
    def logout(self):
        pass
        
    def perspective_getRoles(self):
        #get roles
        user=User.byName(self.username)
        d = []
        for r in user.roles:
            d.append(r.name)
        return d
    
from datetime import datetime
class DatabaseAvatar(Avatar):    
    
    def __init__(self,username,role,mind):
        self.username=username
        self.user = User.byName(username)
        self.role = role
        self.mind = mind
        
    def logout(self):
        pass
        
    def perspective_getUserSchema(self):
        return UserSchema(self.user)
        
    def perspective_delete(self,table,id):
        role=self.role
        tp = role.getTablePermission(table)        
        if not tp or not tp.delete:
            return False #error
            
        tableClass = tp.tableClass
        
        persist = tableClass.get(id)
        persist.destroySelf()

            
        return True
            
        
    def perspective_update(self,table,id,data):
        
        from datetime import datetime

        role=self.role
        tp = role.getTablePermission(table)        
        if not tp or not tp.read:
            return False #error
            
        tableClass = tp.tableClass
        
        changed = {}
        persist = tableClass.get(id)
       
        update = False
        for k,v in data.iteritems():
            attr = getattr(persist,k)
            if isinstance(attr,datetime):
                continue
            if v != attr:
                
                if type(v) != type(attr):
                    print "Warning: attempting to typecast",k
                    v = type(attr)(v)
                changed[k]=v
                update=True
                
        if update:
            persist.updateChanged(changed)
        
        return True
        
    def perspective_insert(self,ghost):
        role=self.role
        table=ghost._dbClass._table
        tp = role.getTablePermission(table)        
        if not tp:
            return None
        if not tp.insert or not tp.write:
            return None#we don't have update on table
                    
        return ghost.insertDB().getGhost()
         
    
    def perspective_get(self,table,ids):
        role=self.role
        tp = role.getTablePermission(table)        
        if not tp or not tp.read:
            return [] #error
            
        selection = []
        tableClass = tp.tableClass
        for id in ids:
            selection.append(tableClass.get(id))
            
        return (table,selection)
        
    def perspective_query(self,table,qdata):
        
        role=self.role
        tp = role.getTablePermission(table)        
        if not tp or not tp.read:
            return [] #error
        results = list(tp.tableClass.select())
            
        return results
