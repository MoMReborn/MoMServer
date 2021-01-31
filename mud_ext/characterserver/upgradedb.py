# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#update all the player database blobs with new data from world db
from sqlobject import *
#from mud.common.dbconfig import SetDBConnection


import os
import sys

sys.path.append(os.getcwd())

from mud.gamesettings import *
from mud.world.advancement import AdvancementProto
from mud.world.character import Character,CharacterAdvancement, \
    CharacterDialogChoice,CharacterFaction,CharacterSkill,CharacterSpell, \
    CharacterVaultItem
from mud.world.faction import Faction
from mud.world.item import Item,ItemContainerContent,ItemProto,ItemSpell
from mud.world.itemvariants import ItemVariant
from mud.world.player import Player,PlayerMonsterSpawn,PlayerXPCredit
from mud.world.spawn import Spawn,SpawnResistance,SpawnSkill,SpawnSpell,SpawnStat
from mud.world.spell import SpellProto,SpellStore
from mud.world.zone import Zone

from datetime import datetime
import re
import shutil
from sqlite3 import dbapi2 as sqlite
import traceback
import zlib



"""
The character database also includes the world.db that it relates to (all tables)
"""

#column name -> index
CINDEXES = {}
NINDEXES = {}

CHARACTER_NAMES = {}
SPAWN_NAMES = {}

DEFAULTS = {}

CURCONN = None
NEWCONN = None
PCONN = None
NEWPCONN = None

BAD_CHARACTERS = []

CREATE_PLAYER_TABLE_SQL = ""
CREATE_CHARACTER_TABLE_SQL = ""

PLAYER_TABLES = ["player","player_monster_spawn","item","item_container_content","item_variant"]

CHARACTER_TABLES = ["character","character_spell","character_skill","character_advancement","character_dialog_choice","character_vault_item","character_faction",
"spawn","spawn_skill","spawn_resistance","spawn_spell","spawn_stat","item","item_container_content","item_variant","spell_store"]

TABLES = PLAYER_TABLES[:]
TABLES.extend(CHARACTER_TABLES)

TVALUES = {}

TLOOKUP = {
    "character": Character,
    "character_advancement": CharacterAdvancement,
    "character_dialog_choice": CharacterDialogChoice,
    "character_faction": CharacterFaction,
    "character_skill": CharacterSkill,
    "character_spell": CharacterSpell,
    "character_vault_item": CharacterVaultItem,
    "item": Item,
    "item_container_content": ItemContainerContent,
    "item_variant": ItemVariant,
    "player": Player,
    "player_monster_spawn": PlayerMonsterSpawn,
    "spawn": Spawn,
    "spawn_resistance": SpawnResistance,
    "spawn_skill": SpawnSkill,
    "spawn_spell": SpawnSpell,
    "spawn_stat": SpawnStat,
    "spell_store": SpellStore
}

#old id->new id
TRANS_ZONE = {}
TRANS_ITEMPROTO = {}
TRANS_SPELLPROTO = {}
TRANS_FACTION = {}
TRANS_ADVANCEMENTPROTO = {}


TTRANS = {}
TTRANS['monster_log_zone'] = TRANS_ZONE
TTRANS['darkness_log_zone'] = TRANS_ZONE
TTRANS['monster_bind_zone'] = TRANS_ZONE
TTRANS['darkness_bind_zone'] = TRANS_ZONE

TTRANS['log_zone'] = TRANS_ZONE
TTRANS['bind_zone'] = TRANS_ZONE
TTRANS['death_zone'] = TRANS_ZONE

TTRANS['zone'] = TRANS_ZONE
TTRANS['item_proto'] = TRANS_ITEMPROTO
TTRANS['spell_proto'] = TRANS_SPELLPROTO
TTRANS['faction'] = TRANS_FACTION
TTRANS['advancement_proto'] = TRANS_ADVANCEMENTPROTO

#actually, we probably need snd_profile for monstor spawns?
TTRANS_IGNORE = ('loot_proto','vendor_proto','respawn','dialog','snd_profile')

PREMIUM_PLAYERS = []

WARN = True

#todo change this to last activity when available
TIME_NOW = datetime.now()
FREE_DATE_CUTOFF = datetime(2006,12,12,0,0,0)
FREE_LEVEL_CUTOFF = 100
ACCOUNT_TIMES = {}
LASTCHARACTER = ""
PRUNEDACCOUNTS = 0
MUSTRENAMECOUNTER = 0



def DoTranslation(table):
    nindexes = NINDEXES[str(table)]
    remap = []
    for name,nindex in nindexes.iteritems():
        if name.endswith("_id"):
            n = name[:-3]
            if n not in TTRANS_IGNORE:
                if not TTRANS.has_key(n):
                    if table == 'item' and n == 'character':
                        #this happens in player buffer for bank items
                        continue
                if table == 'item' and n == 'player':
                    #don't need this, will be set on install on world server
                    continue
                
                if not TTRANS.has_key(n):
                    traceback.print_stack()
                    print "AssertionError: %s not in TTRANS!"%n
                    continue
                remap.append((name))
    
    if not len(remap):
        return
    
    pcursor = PCONN.cursor()
    ncursor = NEWPCONN.cursor()
    if nindexes.has_key("name"):
        sql = "SELECT id, name, "
    else:
        sql = "SELECT id, "
    sql += '%s FROM %s;'%(', '.join(remap),table)
    
    try:
        pcursor.execute(sql)
    except sqlite.OperationalError, message:
        if message[0].startswith("no such table"):
            print "Table %s does not yet exist."%table
        else:
            traceback.print_exc()
        return
    except:
        traceback.print_exc()
        return
    
    for values in pcursor.fetchall():
        try:
            sql = "UPDATE %s SET "%table
            
            c = 1
            if nindexes.has_key("name"):
                c = 2
            for name in remap:
                if name.endswith("_id") and not values[c]: #bank items can do this, player_id and character_id
                    sql += "%s = NULL, "%(name)
                elif name == "player_id":
                    sql += "%s = 1, "%(name)
                else:
                    sql += "%s = %i, "%(name,TTRANS[name[:-3]][values[c]])
                c += 1
            
            sql = sql[:-2]
            sql += " WHERE id = %i;"%TTRANS[table][values[0]]
            
            ncursor.execute(sql)
        
        except KeyError:
            #traceback.print_exc()
            
            ncursor.execute("DELETE FROM %s WHERE id = %i"%(table,TTRANS[table][values[0]]))
            if nindexes.has_key("name"):
                print "Removing named row %s from %s"%(values[1],table),values
            else:
                print "Removing anonymous row from %s"%table,values
    
    pcursor.close()
    ncursor.close()


def DoTable(table):
    pcursor = PCONN.cursor()
    ncursor = NEWPCONN.cursor()
    try:
        pcursor.execute("SELECT * from %s"%table)
    except sqlite.OperationalError, message:
        if message[0].startswith("no such table"):
            print "Table %s does not yet exist."%table
        else:
            traceback.print_exc()
        return
    except:
        traceback.print_exc()
        return
    
    TTRANS[table] = {}
    for r in pcursor.fetchall():
        ovalues = r
        nindexes = NINDEXES[str(table)]
        cindexes = CINDEXES[str(table)]
        
        values = nindexes.keys() #just makes a list of the proper size
        
        for name,nindex in nindexes.iteritems():
            if name == "player_id":
                values[nindex] = 1
            else:
                if cindexes.has_key(name):
                    values[nindex] = ovalues[cindexes[name]]
                else:
                    values[nindex] = DEFAULTS[table][name]
        
        try:
            oid = values[0]
            values[0] = None
            ncursor.executemany("INSERT INTO %s VALUES (%s);"%(table,TVALUES[str(table)]),(values,))
            TTRANS[table][oid] = ncursor.lastrowid
        except:
            traceback.print_exc()
            print table,values
    
    ncursor.close()
    pcursor.close()



def UpgradeCharacterBuffer(values):
    global PCONN,NEWPCONN,BAD_CHARACTERS,WARN,MUSTRENAMECOUNTER
    
    id,publicName,characterName,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm,rename,buffer = values
    
    try:
        dbuffer = zlib.decompress(buffer)
    except:
        traceback.print_stack()
        print "Error in character buffer",publicName,characterName
        BAD_CHARACTERS.append((publicName,characterName))
        return
    
    f = file("./data/tmp/cbuffer","wb")
    f.write(dbuffer)
    f.close()
    
    PCONN = sqlite.connect("./data/tmp/cbuffer")
    if os.path.exists("./data/tmp/nbuffer"):
        os.remove("./data/tmp/nbuffer")
    
    #get character names
    
    #cursor = PCONN.cursor()
    #cursor.execute("SELECT name from character")
    #for name in cursor.fetchall():
    #    n = (name[0],)
    #    assert n not in CHARACTER_NAMES, "Character name collision: %s -> %s"%(publicName,n[0])
    #    CHARACTER_NAMES.append(n)
    
    NEWPCONN = sqlite.connect("./data/tmp/nbuffer",isolation_level=None)
    nc = NEWPCONN.cursor()
    nc.execute("BEGIN TRANSACTION;")
    nc.executescript(CREATE_CHARACTER_TABLE_SQL)
    
    if WARN:
        WARN = False
        #for x in range(0,50):
        #    print "WARNING: ignoring character item vault, add once it exists"
    
    map(DoTable, CHARACTER_TABLES)
    
    # Create an alias 'content' for the 'item' translation entry.
    # Needed for the ItemContainerContent class in item.py.
    try:
        TTRANS['content'] = TTRANS['item']
    except KeyError:
        pass
    
    # Do translation.
    map(DoTranslation, CHARACTER_TABLES)
    
    #handle the freaking classchange for the conversion
    #nc.execute("SELECT name from character;")
    #name = nc.fetchone()[0]
    #print "Setting up change class for %s"%name
    
    #nc.execute("SELECT plevel,slevel,tlevel FROM spawn WHERE name = '%s';"%name)
    #plevel,slevel,tlevel = nc.fetchone()
    #print plevel,slevel,tlevel
    
    #if slevel and tlevel:
    #    nc.execute("UPDATE character SET pchange=1, schange=1, tchange=1 WHERE name = '%s';"%name)
    #elif slevel:
    #    nc.execute("UPDATE character SET pchange=1, schange=1, tchange=0 WHERE name = '%s';"%name)
    #else:
    #    nc.execute("UPDATE character SET pchange=1, schange=0, tchange=0 WHERE name = '%s';"%name)
    
    nc.execute("END TRANSACTION;")
    nc.close()
    PCONN.close()
    NEWPCONN.close()
    PCONN = None
    NEWPCONN = None
    
    f = file("./data/tmp/nbuffer","rb")
    buffer = f.read()
    f.close()
    
    buffer = zlib.compress(buffer)
    buffer = sqlite.Binary(buffer)
    
    #perhaps remove me post pname->cname update
    name = str(characterName.title())
    name = name.replace("The ","the ")
    name = name.replace("To ","to ")
    name = name.replace("And ","and ")
    name = name.replace("Of ","of ")
    
    spawnc = SPAWN_NAMES.has_key(name.upper())
    
    if spawnc or CHARACTER_NAMES.has_key(name):
        MUSTRENAMECOUNTER += 1
        mname = "Please Rename %i"%MUSTRENAMECOUNTER
        if not spawnc:
            print "Character Name collision %s, renaming to %s and setting rename=2"%(name,mname)
        else:
            print "Spawn Name collision %s, renaming to %s and setting rename=2"%(name,mname)
        name = mname
    else:
        CHARACTER_NAMES[name] = name
    
    #v = (None,publicName,characterName,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm,rename,buffer)
    v = (None,publicName,name,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm,rename,buffer)
    
    cursor = NEWCONN.cursor()
    cursor.executemany("INSERT INTO character_buffer VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);",(v,))
    cursor.close()



def UpgradePlayerBuffer(publicName,buffer):
    global PCONN,NEWPCONN,LASTCHARACTER
    if LASTCHARACTER != publicName[0]:
        LASTCHARACTER = publicName[0]
        print "Upgrading Players: %s"%LASTCHARACTER
    
    dbuffer = zlib.decompress(buffer)
    f = file("./data/tmp/pbuffer","wb")
    f.write(dbuffer)
    f.close()
    
    PCONN = sqlite.connect("./data/tmp/pbuffer")
    if os.path.exists("./data/tmp/nbuffer"):
        os.remove("./data/tmp/nbuffer")
    
    #get character names
    
    #cursor = PCONN.cursor()
    #cursor.execute("SELECT name from character")
    #for name in cursor.fetchall():
    #    n = (name[0],)
    #    assert n not in CHARACTER_NAMES, "Character name collision: %s -> %s"%(publicName,n[0])
    #    CHARACTER_NAMES.append(n)
    
    NEWPCONN = sqlite.connect("./data/tmp/nbuffer",isolation_level=None)
    nc = NEWPCONN.cursor()
    nc.execute("BEGIN TRANSACTION;")
    nc.executescript(CREATE_PLAYER_TABLE_SQL)
    
    map(DoTable, PLAYER_TABLES)
    
    # Create an alias 'content' for the 'item' translation entry.
    # Needed for the ItemContainerContent class in item.py.
    try:
        TTRANS['content'] = TTRANS['item']
    except KeyError:
        pass
    
    # Do translation.
    map(DoTranslation, PLAYER_TABLES)
    
    nc.execute("END TRANSACTION;")
    nc.close()
    PCONN.close()
    NEWPCONN.close()
    PCONN = None
    NEWPCONN = None
    
    f = file("./data/tmp/nbuffer","rb")
    buffer = f.read()
    f.close()
    
    buffer = zlib.compress(buffer)
    buffer = sqlite.Binary(buffer)
    
    cursor = NEWCONN.cursor()
    cursor.executemany("INSERT INTO player_buffer VALUES(?,?,?);",((None,publicName,buffer),))
    cursor.close()





def UpdateCharacters():
    global CURCONN,NEWCONN,PRUNEDACCOUNTS,MUSTRENAMECOUNTER
    try:
        os.remove("./data/updated.db")
    except:
        pass
    shutil.copyfile("%s/data/worlds/multiplayer.baseline/world.db"%GAMEROOT,"./data/updated.db")
    
    #get the premium accounts
    MCONN = sqlite.connect("./data/master/master.db",isolation_level = None)
    MCURSOR = MCONN.cursor()
    print "Checking Master database integrity"
    MCURSOR.execute("PRAGMA integrity_check;")
    if MCURSOR.fetchone()[0] != 'ok':
        raise "Master Database Error"
    print "... ok ..."
    
    MCURSOR.execute("SELECT account_id FROM product WHERE name='MOM';")
    ids = MCURSOR.fetchall()
    
    for id in ids:
        MCURSOR.execute("SELECT public_name FROM account WHERE id='%i' LIMIT 1;"%id)
        pname = str(MCURSOR.fetchone()[0])
        PREMIUM_PLAYERS.append(pname)
    
    #change to activity time when available
    MCURSOR.execute("SELECT public_name,last_activity_time FROM account;")
    tms = MCURSOR.fetchall()
    for pname,t in tms:
        # I guess the variant below should be used, please revise if necessary.
        #if not t:
        #    ACCOUNT_TIMES[str(pname)]=datetime.now()
        #    continue
        
        if not t:
            t = str(datetime.now())
        
        date,time = t.split(" ")
        year,month,day = date.split("-")
        hour,minute,second = time.split(":")
        d = datetime(int(year),int(month),int(day),int(hour),int(minute),0)
        ACCOUNT_TIMES[str(pname)] = d
    
    CURCONN = sqlite.connect("./data/character/character.db",isolation_level = None)
    NEWCONN = sqlite.connect("./data/updated.db",isolation_level = None)
    CURCONN.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    NEWCONN.text_factory = lambda x: unicode(x, "utf-8", "ignore")
    
    print "... Checking Database Integrity ..."
    cursor = CURCONN.cursor()
    cursor.execute("PRAGMA integrity_check;")
    if cursor.fetchone()[0] != 'ok':
        raise "Database Error"
    print "... ok ..."
    
    cursor.execute("SELECT character_name FROM character_buffer;")
    for n in cursor.fetchall():
        n = n[0].upper()
        if "PLEASE RENAME" in n:
            p,r,num = n.split(" ")
            num = int(num)
            if num >= MUSTRENAMECOUNTER:
                MUSTRENAMECOUNTER = num + 1
    
    cursor.close()
    
    print "Rename Counter starting at",MUSTRENAMECOUNTER
    
    Initialize()
    
    cursor = CURCONN.cursor()
    ncursor = NEWCONN.cursor()
    
    ncursor.execute("BEGIN TRANSACTION;")
    
    from serverdb import CREATE_PLAYER_BUFFER_SQL
    ncursor.executescript(CREATE_PLAYER_BUFFER_SQL)
    
    #here we go (I am sure there is some good SQL to do this, but hey)
    bid = {}
    cursor.execute("SELECT public_name,id FROM player_buffer;")
    for pname,id in cursor.fetchall():
        pname = str(pname)
        if not ACCOUNT_TIMES.has_key(pname):
            print "WARNING: %s account has no account time!!!!"%pname
            continue
        if not bid.has_key(pname):
            bid[pname] = id
        elif bid[pname] < id:
            bid[pname] = id
    
    for pname in sorted(bid.iterkeys()):
        #if pname != 'Azdruin':
        #    continue
        
        if pname not in PREMIUM_PLAYERS:
            if ACCOUNT_TIMES[pname] <= FREE_DATE_CUTOFF:
                PRUNEDACCOUNTS += 1
                continue
        id = bid[pname]
        cursor.execute("SELECT buffer from player_buffer where id = %i LIMIT 1;"%id)
        UpgradePlayerBuffer(pname,cursor.fetchone()[0])
        
        cursor.execute("SELECT * from character_buffer where public_name = '%s';"%pname)
        for char in cursor.fetchall():
            UpgradeCharacterBuffer(char)
    
    print "Setting up cserver_character table"
    #convert to uppercase here, and not above because some old character have the same name other than case
    #these are grandfathered in, though new ones are case insenstive
    CNAMES = [(v.upper(),) for v in CHARACTER_NAMES.iterkeys()]
    ncursor.executemany("INSERT INTO cserver_character VALUES (NULL,?)",CNAMES)
    
    print "Copying guild information..."
    try:
        cursor.execute("SELECT id,name,info,motd,creator FROM guild;")
        guilds = cursor.fetchall()
        nguilds = [(None,name,info,motd,creator) for id,name,info,motd,creator in guilds]
        
        cursor.execute("SELECT id,public_name,guild_name,rank FROM guild_member;")
        members = cursor.fetchall()
        nmembers = [(None,pname,gname,rank) for id,pname,gname,rank in members]
        
        ncursor.executemany("INSERT INTO guild VALUES (?,?,?,?,?)",nguilds)
        ncursor.executemany("INSERT INTO guild_member VALUES (?,?,?,?)",nmembers)
    except:
        traceback.print_exc()
    
    ncursor.execute("END TRANSACTION;")
    
    cursor.close()
    ncursor.close()
    CURCONN.close()
    NEWCONN.close()
    
    if len(BAD_CHARACTERS):
        print "WARNING: Bad Character Buffers -> ",BAD_CHARACTERS
    
    print "Pruned Accounts: %i"%PRUNEDACCOUNTS
    
    print "Done"


def Initialize():
    #get table information from existing
    global CREATE_PLAYER_TABLE_SQL,CREATE_CHARACTER_TABLE_SQL
    
    cursor = CURCONN.cursor()
    ncursor = NEWCONN.cursor()
    
    for t in PLAYER_TABLES:
        cursor.execute('PRAGMA table_info(%s);'%t)
        CINDEXES[t] = dict((col[1],col[0]) for col in cursor.fetchall())
        
        ncursor.execute('PRAGMA table_info(%s);'%t)
        sql = []
        ct = NINDEXES[t] = {}
        td = 0
        for col in ncursor.fetchall():
            ct[col[1]] = col[0]
            td += 1
            if col[1] == 'id':
                sql.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                sql.append("%s %s"%(col[1],col[2]))
        TVALUES[t] = ','.join('?' * td)
        CREATE_PLAYER_TABLE_SQL += "CREATE TABLE %s (%s);"%(t,', '.join(sql))
        
        #sure would be nice if SQLObject just encoded these properly in the db
        so = TLOOKUP[t]
        defs = DEFAULTS[t] = {}
        for ncol in so.sqlmeta._columns:
            d = ncol.default
            if d == sqlbuilder.NoDefault:
                d = None
            defs[mixedToUnder(ncol.name)] = d
    
    for t in CHARACTER_TABLES:
        cursor.execute('PRAGMA table_info(%s);'%t)
        CINDEXES[t] = dict((col[1],col[0]) for col in cursor.fetchall())
        
        ncursor.execute('PRAGMA table_info(%s);'%t)
        sql = []
        ct = NINDEXES[t] = {}
        td = 0
        for col in ncursor.fetchall():
            ct[col[1]] = col[0]
            td += 1
            if col[1] == 'id':
                sql.append("id INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                sql.append("%s %s"%(col[1],col[2]))
        TVALUES[t] = ','.join('?' * td)
        CREATE_CHARACTER_TABLE_SQL += "CREATE TABLE %s (%s);"%(t,', '.join(sql))
        
        #sure would be nice if SQLObject just encoded these properly in the db
        so = TLOOKUP[t]
        defs = DEFAULTS[t] = {}
        for ncol in so.sqlmeta._columns:
            d = ncol.default
            if d == sqlbuilder.NoDefault:
                d = None
            defs[mixedToUnder(ncol.name)] = d
    
    #setup translations
    cursor.execute("SELECT name,id from item_proto;")
    for name,oid in cursor.fetchall():
        try:
            ncursor.execute('SELECT id from item_proto WHERE name = "%s" LIMIT 1;'%name)
            nid = ncursor.fetchone()[0]
            TRANS_ITEMPROTO[oid] = nid
        except:
            print "ItemProto %s no longer exists"%name
    
    cursor.execute("SELECT name,id from spell_proto;")
    for name,oid in cursor.fetchall():
        try:
            ncursor.execute('SELECT id from spell_proto WHERE name = "%s" LIMIT 1;'%name)
            nid = ncursor.fetchone()[0]
            TRANS_SPELLPROTO[oid] = nid
        except:
            print "SpellProto %s no longer exists"%name
    
    cursor.execute("SELECT name,id from zone;")
    for name,oid in cursor.fetchall():
        try:
            ncursor.execute('SELECT id from zone WHERE name = "%s" LIMIT 1;'%name)
            nid = ncursor.fetchone()[0]
            TRANS_ZONE[oid] = nid
        except:
            print "Zone %s no longer exists"%name
    
    cursor.execute("SELECT name,id from faction;")
    for name,oid in cursor.fetchall():
        try:
            ncursor.execute('SELECT id from faction WHERE name = "%s" LIMIT 1;'%name)
            nid = ncursor.fetchone()[0]
            TRANS_FACTION[oid] = nid
        except:
            print "Faction %s no longer exists"%name
    
    cursor.execute("SELECT name,id from advancement_proto;")
    for name,oid in cursor.fetchall():
        try:
            ncursor.execute('SELECT id from advancement_proto WHERE name = "%s" LIMIT 1;'%name)
            nid = ncursor.fetchone()[0]
            TRANS_ADVANCEMENTPROTO[oid] = nid
        except:
            print "Advancement %s no longer exists"%name
    
    cursor.execute("SELECT name from spawn;")
    for name in cursor.fetchall():
        n = str(name[0]).upper()
        SPAWN_NAMES[n] = n
    cursor.close()
    ncursor.close()


# Function to reformat mixed case strings to strings
#  with underscores. Every upper case letter gets
#  turned into a lowercase letter and prefixed with
#  an underscore.
# Database uses underscore names, since it's case-insensitive.
_mixedToUnderRE = re.compile(r'[A-Z]+')
def mixedToUnder(s):
    if s.endswith('ID'):
        return mixedToUnder(s[:-2] + "_id")
    trans = _mixedToUnderRE.sub(mixedToUnderSub, s)
    if trans.startswith('_'):
        trans = trans[1:]
    return trans

def mixedToUnderSub(match):
    m = match.group(0).lower()
    if len(m) > 1:
        return '_%s_%s'%(m[:-1],m[-1])
    else:
        return '_%s'%m



if __name__=='__main__':
    UpdateCharacters()

