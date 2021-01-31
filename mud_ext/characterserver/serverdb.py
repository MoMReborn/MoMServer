# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from sqlite3 import dbapi2 as sqlite
import shutil
from twisted.internet import reactor
import traceback
import sha
import sys
import os

sys.path.append(os.getcwd())

from mud.gamesettings import *

CREATE_PLAYER_BUFFER_SQL = """
CREATE TABLE player_buffer
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    public_name TEXT,
    buffer BLOB
);

CREATE TABLE character_buffer
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    public_name TEXT,
    character_name TEXT UNIQUE,
    race TEXT,
    pclass TEXT,
    sclass TEXT,
    tclass TEXT,
    plevel INTEGER,
    slevel INTEGER,
    tlevel INTEGER,
    realm INTEGER,
    rename INTEGER,
    buffer BLOB
);


CREATE TABLE cserver_character
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

CREATE TABLE guild
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    info TEXT,
    motd TEXT,
    creator TEXT
);

CREATE TABLE guild_member
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    public_name TEXT UNIQUE,
    guild_name TEXT,
    rank INTEGER
);
"""

LASTBACKUPFILE = None
def BackupCharacterDB():
    global LASTBACKUPFILE
    import datetime
    import shutil
    
    filename = "data/character/character.db"
    n = datetime.datetime.now()
    s = n.strftime("%B_%d_%Y")
    d,f = os.path.split(filename)
    
    f,ext = os.path.splitext(f)
    
    backfolder = d+"/"+s
    if not os.path.exists(backfolder):
        os.makedirs(backfolder)
        
    x = 1
    while True:
        backupfile = backfolder+"/"+"%s_backup_%i%s"%(f,x,ext)
        if os.path.exists(backupfile):
            x+=1
            continue
        
        
        shutil.copyfile(filename,backupfile)
        LASTBACKUPFILE = backupfile
        break



class CharDB:
    def __init__(self,filename):
        self.conn = sqlite.connect(filename,isolation_level=None)
        self.conn.text_factory = lambda x: unicode(x, "utf-8", "ignore")
        
        cursor = self.conn.cursor()
        cursor.execute("SELECT genesis_time from world")
        self.genesisTime = cursor.fetchone()[0]

        cursor.execute("BEGIN TRANSACTION;")
            
        cursor.close()
        
        self.tickTransaction = reactor.callLater(120,self.transactionTick)
        
        self.backupCounter = 40 #once every 80 minutes
    
    
    def __del__(self):
        self.conn.close()
    
    
    def commit(self, commitOnly=False):
        if self.tickTransaction:
            self.tickTransaction.cancel()
        self.transactionTick(commitOnly)
    
    
    def transactionTick(self, commitOnly=False):
        print "... Commit Character Database ..."
        
        cursor = self.conn.cursor()
        cursor.execute("END TRANSACTION;")
        
        if not commitOnly:
            self.backupCounter -= 1
            if not self.backupCounter:
                print "Backing up character database"
                self.backupCounter = 40 #once every 80 minutes
                try:
                    BackupCharacterDB()
                except:
                    traceback.print_exc()
        
        cursor.execute("BEGIN TRANSACTION;")
        cursor.close()

        self.tickTransaction = reactor.callLater(120,self.transactionTick)
    
    
    def checkIntegrity(self):
        print "... Checking Database Integrity ..."
        cursor = self.conn.cursor()
        cursor.execute("PRAGMA integrity_check;")
        if cursor.fetchone()[0]!='ok':
            raise "Database Error"
        print "... ok ..."
        
        cursor.close()
        
    def deleteCharacter(self,publicName,characterName):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM character_buffer WHERE public_name = '%s' AND character_name = '%s';"%(publicName,characterName))
        except:
            traceback.print_exc()
            cursor.close()
            return False
        
        try:
            cursor.execute("DELETE from cserver_character WHERE name = '%s';"%(characterName.upper()))
        except:
            traceback.print_exc()
            pass
        cursor.close()
        return characterName
        
        
        
    def getCharacterInfos(self,publicName):
        cinfos = {}
        
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT character_name,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm,rename FROM character_buffer WHERE public_name = '%s';"%publicName)
            for v in cursor.fetchall():
                cinfos[v[0]]=v
        except:
            traceback.print_exc()
            pass
        cursor.close()
        
        return cinfos
        
    def getCharacterBuffer(self,publicName,characterName):
        cursor = self.conn.cursor()
        buffer = None
        try:
            cursor.execute("SELECT buffer FROM character_buffer WHERE public_name = '%s' AND character_name ='%s';"%(publicName,characterName))
            buffer = cursor.fetchone()[0]
        except:
            traceback.print_exc()
        cursor.close()
        return buffer


    def insertCharacterBuffer(self,publicName,cvalues,buffer):        
        cursor = self.conn.cursor()
        
        characterName,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm = cvalues
        rename = 0
        try:
            cursor.execute("SELECT rename FROM character_buffer WHERE public_name = '%s' AND character_name = '%s';"%(publicName,characterName))
            rename = cursor.fetchone()[0]
        except:
            pass

        try:
            cursor.execute("DELETE FROM character_buffer WHERE public_name = '%s' AND character_name = '%s';"%(publicName,characterName))
        except:
            traceback.print_exc()
            
        buffer = sqlite.Binary(buffer)
        values = (None,publicName,characterName,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm,rename,buffer)
        cursor.executemany("INSERT INTO character_buffer VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);",(values,))
        cursor.close()
    
    
        
    def getPlayerBuffer(self,publicName):
        cursor = self.conn.cursor()
        buffer = None
        try:
            cursor.execute("SELECT buffer FROM player_buffer WHERE public_name = '%s' ORDER BY id DESC LIMIT 1;"%publicName)
            buffer = cursor.fetchone()[0]
        except:
            pass
        cursor.close()
        return buffer
        

    def insertPlayerBuffer(self,publicName,buffer):
        cursor = self.conn.cursor()
        buffer = sqlite.Binary(buffer)
        cursor.executemany("INSERT INTO player_buffer VALUES(?,?,?);",((None,publicName,buffer),))
        cursor.execute("SELECT id FROM player_buffer WHERE public_name = '%s' ORDER BY id DESC;"%publicName)
        remove = []
        try:
            remove = cursor.fetchall()[10:]
        except:
            pass
            
        for id in remove:
            cursor.execute("DELETE FROM player_buffer WHERE id = %i;"%id)
            
        
        cursor.close()
        
        
    #guilds
    
    def getGuildInfo(self, publicName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT guild_name,rank FROM guild_member WHERE public_name='%s' LIMIT 1;"%publicName)
        
        try:
            name,rank = cursor.fetchone()
        except:
            cursor.close()
            return ("","","",0)
        
        cursor.execute("SELECT name,info,motd FROM guild WHERE name='%s' LIMIT 1;"%name)
        try:
            name,info,motd = cursor.fetchone()
            name = str(name)
            info = str(info)
            motd = str(motd)
            cursor.close()
            return (name,info,motd,rank)
        except:
            traceback.print_exc()
        
        cursor.close()
        return ("","","",0)
    
    
    def createGuild(self, name, publicName, mnames):
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT id FROM guild WHERE name LIKE '%s' LIMIT 1;"%name)
        if cursor.fetchone():
            cursor.close()
            return (-1,"The guild name '%s' is taken, please choose another."%name,None)
        
        cursor.execute("SELECT id FROM guild_member WHERE public_name='%s' LIMIT 1;"%publicName)
        if cursor.fetchone():
            cursor.close()
            return (-1,"You are already a member of a guild.",None)
        
        #validate users
        vusers = []
        iusers = []
        
        for m in mnames:
            cursor.execute("SELECT id FROM guild_member WHERE public_name='%s' LIMIT 1;"%m)
            if cursor.fetchone():
                iusers.append(m)
            else:
                vusers.append(m)
        
        if len(vusers) < 3:
            return (-1,"You must have signed charters from 3 different members to form a new guild.",iusers)
        
        values = (None,name,"","",publicName)
        try:
            cursor.execute("INSERT INTO guild VALUES(?,?,?,?,?);",values)
        except:
            traceback.print_exc()
            cursor.close()
            return (-1,"There was an error creating the guild '%s'."%name,None)
        
        values = (None,publicName,name,2)
        try:
            cursor.execute("INSERT INTO guild_member VALUES(?,?,?,?);",values)
        except:
            traceback.print_exc()
            cursor.close()
            self.deleteGuild(name)
            return (-1,"Error inserting leader into new guild '%s'.",None)
        
        cursor.close()
        return (0,"The guild '%s' has been created."%name,None)
    
    
    def deleteGuild(self, name):
        cursor = self.conn.cursor()
        try:
            cursor.execute("DELETE FROM guild WHERE name='%s';"%name)
        except:
            traceback.print_exc()
            cursor.close()
            return (-1,"Error deleting guild."%name)
        
        try:
            cursor.execute("DELETE FROM guild_member WHERE guild_name='%s';"%name)
        except:
            traceback.print_exc()
            cursor.close()
            return (-1,"Error deleting guild members."%name)
        
        cursor.close()
        return (0,"Guild '%s' deleted."%name)
    
    
    def addGuildMember(self, name, publicName, inviter):
        cursor = self.conn.cursor()
        cursor.execute("SELECT guild_name FROM guild_member WHERE public_name='%s' LIMIT 1;"%publicName)
        if cursor.fetchone():
            cursor.close()
            return (-1,"%s is already a member of a guild."%publicName)
        
        cursor.execute("SELECT name FROM guild WHERE name='%s' LIMIT 1;"%name)
        if not len(cursor.fetchall()):
            cursor.close()
            return (-1,"%s is an unknown guild."%name)
        
        cursor.execute("SELECT rank FROM guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(inviter,name))
        r = cursor.fetchone()
        if r == None:
            cursor.close()
            return (-1,"%s is not a member of the guild '%s'."%(inviter,name))
        
        if r[0] < 1:
            return (-1,"%s is not a guild officer."%inviter)
        
        values = (None,publicName,name,0)
        
        try:
            cursor.execute("INSERT INTO guild_member VALUES(?,?,?,?);",values)
        except:
            traceback.print_exc()
            cursor.close()
            return (-1,"Error adding member.")
        
        cursor.execute("SELECT name,motd,info FROM guild WHERE name='%s' LIMIT 1;"%name)
        r = cursor.fetchone()
        name,motd,info = r
        r = (str(name),0,str(motd),str(info))
        cursor.close()
        return (0,r)
    
    
    def removeGuildMember(self, name, publicName, removeName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild remove member")
        myrank = r[0]
        if myrank < 1:
            return (-1,"You are not a guild officer.")
        
        cursor.execute("SELECT public_name,rank from guild_member WHERE public_name LIKE '%s' AND guild_name='%s' LIMIT 1;"%(removeName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"%s is not a member of your guild."%removeName)
        if r[1] >= myrank:
            return (-1,"%s must be removed by a guild leader."%removeName)
        
        try:
            cursor.execute("DELETE FROM guild_member WHERE guild_name='%s' AND public_name='%s';"%(name,r[0]))
        except:
            traceback.print_exc()
            cursor.close()
            return (-1,"Error removing guild member '%s' from guild '%s'."%(removeName,name))
        
        cursor.close()
        return (0,"Removed guild member '%s' from guild '%s'."%(removeName,name))
    
    
    def demoteGuildMember(self, name, publicName, demoteName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild demote member")
        if r[0] < 2:
            return (-1,"You are not a guild leader.")
        
        cursor.execute("SELECT rank from guild_member WHERE public_name LIKE '%s' AND guild_name='%s';"%(demoteName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"%s is not a member of your guild."%demoteName)
        if r[0] != 1:
            return (-1,"%s is not a guild officer."%demoteName)
        
        cursor.execute("UPDATE guild_member SET rank=0 WHERE public_name LIKE '%s';"%demoteName)
        cursor.close()
        
        return (0,"%s is no longer a guild officer."%demoteName)
    
    
    def setGuildMOTD(self, name, publicName, motd):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild set motd")
        if r[0] < 1:
            return (-1,"You are not a guild officer.")
        
        motd = motd.replace('"',"'")
        try:
            cursor.execute('UPDATE guild SET motd="%s" WHERE name="%s";'%(motd,name))
        except:
            return (-1,"Error setting motd.")
        
        cursor.close()
        return (0,"guild motd set")
    
    
    def leaveGuild(self, name, publicName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"You aren't a member of a guild.")
        if r[0] == 2:
            return (-1,"You are a guild leader and must either set a new leader or disband to leave.")
        
        try:
            cursor.execute("DELETE FROM guild_member WHERE guild_name='%s' AND public_name LIKE '%s';"%(name,publicName))
        except:
            traceback.print_exc()
            cursor.close()
            return (-1,"There was an error leaving the guild.")
        
        cursor.close()
        return (0,"You have left the guild.")
    
    
    def getGuildRoster(self, name, publicName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild get roster")
        if r[0] < 1:
            return (-1,"You are not a guild officer.")
        
        cursor.execute("SELECT public_name,rank FROM guild_member WHERE guild_name='%s';"%name)
        r = cursor.fetchall()
        cursor.close()
        return (0,r)
    
    
    def clearGuildMOTD(self, name, publicName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild clear motd")
        if r[0] < 1:
            return (-1,"You are not a guild officer.")
        
        try:
            cursor.execute('UPDATE guild SET motd="" WHERE name="%s";'%(name))
        except:
            return (-1,"Error setting motd.")
        
        cursor.close()
        return (0,"guild motd cleared")
    
    
    def disbandGuild(self, name, publicName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild disband")
        if r[0] < 2:
            return (-1,"You are not a guild leader.")
        
        cursor.close()
        
        return self.deleteGuild(name)
    
    
    def promoteGuildMember(self, name, publicName, promoteName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild promote member")
        if r[0] < 2:
            return (-1,"You are not a guild leader.")
        
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(promoteName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"%s is not a member of your guild."%promoteName)
        if r[0] != 0:
            if r[0] == 1:
                return (-1,"%s is already a guild officer."%promoteName)
            else:
                return (-1,"%s is a guild leader."%promoteName)
        
        cursor.execute("UPDATE guild_member SET rank=1 WHERE public_name='%s';"%promoteName)
        cursor.close()
        
        return (0,"%s is now a guild officer."%promoteName)
    
    
    def getGuildCharacters(self, name, publicName, who):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild get characters")
        if r[0] < 1:
            return (-1,"You are not a guild officer.")
        
        cursor.execute("SELECT public_name,rank FROM guild_member WHERE public_name LIKE '%s' AND guild_name='%s' LIMIT 1;"%(who,name))
        
        r = cursor.fetchone()
        if r == None:
            return (-1,"%s is not in your guild."%who)
        
        cursor.execute("SELECT character_name FROM character_buffer WHERE public_name='%s';"%r[0])
        r = cursor.fetchall()
        cursor.close()
        return (0,r)
    
    
    def getGuildPublicName(self, name, publicName, characterName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild get public name")
        if r[0] < 1:
            return (-1,"You are not a guild officer.")
        
        cursor.execute("SELECT public_name FROM character_buffer WHERE character_name LIKE '%s' LIMIT 1;"%characterName)
        
        r = cursor.fetchone()
        if r == None:
            return (-1,"Character %s is not in your guild."%characterName)
        
        pname = r[0]
        
        cursor.execute("SELECT rank FROM guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(pname,name))
        
        r = cursor.fetchone()
        if r == None:
            return (-1,"Character %s is not in your guild."%characterName)
        
        return (0,pname)
    
    
    def setGuildLeader(self, name, publicName, promoteName):
        cursor = self.conn.cursor()
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(publicName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"Bad privileges on guild set leader")
        if r[0] < 2:
            return (-1,"You are not a guild leader.")
        
        cursor.execute("SELECT rank from guild_member WHERE public_name='%s' AND guild_name='%s' LIMIT 1;"%(promoteName,name))
        r = cursor.fetchone()
        
        if r == None:
            return (-1,"%s is not a member of your guild."%promoteName)
        
        cursor.execute("UPDATE guild_member SET rank=2 WHERE public_name='%s';"%promoteName)
        cursor.execute("UPDATE guild_member SET rank=1 WHERE public_name='%s';"%publicName)
        
        cursor.close()
        
        return (0,"%s is now the guild leader."%promoteName)
    
    
    #WARNING!!!! This only updates the name on the character server and not the 
    #BLOB compressed character database... when the character is installed name will be 
    #updated on server, but only character:name and spawn:name columns and no other!!!
    
    def renameCharacter(self,oldname,newname):
        cursor = self.conn.cursor()
        
        #just changing case
        if oldname.lower()==newname.lower():
            try:
                cursor.execute("UPDATE character_buffer SET rename=0 WHERE character_name LIKE '%s';"%oldname)
            except:
                pass
            try:
                cursor.execute("UPDATE character_buffer SET character_name='%s' WHERE character_name LIKE '%s';"%(newname,oldname))
            except:
                return -1
            
            return 0
            
            
        
        cursor.execute("SELECT id FROM cserver_character WHERE name LIKE '%s';"%(oldname.upper()))
        
        if not len(cursor.fetchall()):
            try:
                cursor.execute("INSERT INTO cserver_character VALUES(NULL,'%s');"%(oldname.upper()))
            except:                
                return -1 
            
        cursor.execute("SELECT id FROM cserver_character WHERE name LIKE '%s';"%(newname.upper()))
        
        if len(cursor.fetchall()):
            return -1

        cursor.execute("SELECT id FROM spawn WHERE name LIKE '%s';"%(newname))
        
        if len(cursor.fetchall()):
            return -1
        
        try:            
            cursor.execute("UPDATE cserver_character SET name='%s' WHERE name LIKE '%s';"%(newname.upper(),oldname.upper()))
        except:
            return -1
    
        try:
            cursor.execute("UPDATE character_buffer SET rename=0 WHERE character_name LIKE '%s';"%oldname)
        except:
            pass

        
        try:
            cursor.execute("UPDATE character_buffer SET character_name='%s' WHERE character_name LIKE '%s';"%(newname,oldname))
        except:
            return -1

        
        return 0
        

def SendBuffer(result,filename,wconn,buffer,pos):
    buf = buffer[pos:pos+32768]
    done = False
    if pos+32768 >= len(buffer):
        done = True
        
    digest = None
    if done:
        m = sha.new()
        m.update(buffer)
        digest = m.hexdigest()

    d = wconn.perspective.callRemote("receiveBuffer",filename,buf,digest)
    if not done:
        d.addCallback(SendBuffer,filename,wconn,buffer,pos+32768)
    
WCONNECTIONS = []
def GotLastBackupFile(masterfile,wconns):
    global WCONNECTIONS
    wc = wconns[:]
    
    for w in wconns:
        if w.worldName in WCONNECTIONS:
            wc.remove(w)
            
    wconn = None
    if not len(wc):
        WCONNECTIONS = []
        wconn = wconns[0]
    else:
        wconn = wc[0]
        
    if wconn:
        WCONNECTIONS.append(wconn.worldName)
    else:
        return

    try:
        if LASTBACKUPFILE:
            
            f = file(LASTBACKUPFILE,'rb')
            buffer = f.read()
            f.close()

            d = wconn.perspective.callRemote("beginReplication",LASTBACKUPFILE)
            d.addCallback(SendBuffer,LASTBACKUPFILE,wconn,buffer,0)
            print "Replicating File: %s to %s"%(LASTBACKUPFILE,wconn.perspective.broker.transport.getPeer().host)
    except:
        traceback.print_exc()

    try:
        if masterfile:
            
            f = file(masterfile,'rb')
            buffer = f.read()
            f.close()

            md = wconn.perspective.callRemote("beginReplication",masterfile)
            md.addCallback(SendBuffer,masterfile,wconn,buffer,0)
            
            print "Replicating File: %s to %s"%(masterfile,wconn.perspective.broker.transport.getPeer().host)
    except:
        traceback.print_exc()
    

def ReplicateDB(WCONNS,MASTERP):
    if not len(WCONNS):
        return
    d = MASTERP.callRemote("CharacterAvatar","getLastBackupFile")
    d.addCallback(GotLastBackupFile,WCONNS)


    
    
    
    
