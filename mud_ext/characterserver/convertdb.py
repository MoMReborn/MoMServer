# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#this is a temporary script to convert from the player buffer to player buffer -> character buffers layout

import os
from sqlite3 import dbapi2 as sqlite
from serverdb import CREATE_PLAYER_BUFFER_SQL
import zlib
import shutil
import traceback

PLAYER_TABLES = ["player","player_monster_spawn"]

CHARACTER_TABLES=["character","character_spell","character_skill","character_advancement","character_dialog_choice","character_faction",
"spawn","spawn_skill","spawn_resistance","spawn_spell","spawn_stat","item","item_container_content","item_variant","spell_store"]

CHARACTER_NAMES = []

def RemoveCharacterTables(cursor):
    for t in CHARACTER_TABLES:
        if t == "item" or t == 'item_variant' or t == 'item_container_content':
            #these are also used for bank items in pbuffer
            cursor.execute("DELETE FROM %s;"%t)
        else:    
            cursor.execute("DROP TABLE %s;"%t)
        
def RemovePlayerTables(cursor):
    for t in PLAYER_TABLES:
        cursor.execute("DROP TABLE %s;"%t)


def DeleteItem(cursor, itemID):
    cursor.execute("DELETE FROM item_variant WHERE item_id=?;",(itemID,))
    cursor.execute("SELECT content_id FROM item_container_content WHERE item_id=?;",(itemID,))
    for contentID in list(cursor.fetchall()):
        DeleteItem(cursor,contentID[0])
        cursor.execute("DELETE FROM item WHERE id=?;",(contentID[0],))
    cursor.execute("DELETE FROM item_container_content WHERE item_id=?;",(itemID,))


def DeleteAllCharactersExcept(cursor,keepId):
    
    RemovePlayerTables(cursor)

    cursor.execute("SELECT id from character;")
    CIDS = []
    for cid in cursor.fetchall():
        if cid[0]==keepId:
            continue
        CIDS.append(cid[0])
    
    for cid in CIDS:
        cursor.execute("SELECT id from spawn where character_id=?;",(cid,))
        spawnid = cursor.fetchone()[0]
        
        cursor.execute("DELETE from character where id=?;",(cid,))
        cursor.execute("DELETE from character_spell where character_id=?;",(cid,))
        cursor.execute("DELETE from character_skill where character_id=?;",(cid,))
        cursor.execute("DELETE from character_advancement where character_id=?;",(cid,))
        cursor.execute("DELETE from character_dialog_choice where character_id=?;",(cid,))
        cursor.execute("DELETE from spell_store where character_id=?;",(cid,))
        
        cursor.execute("DELETE from spawn where id=?;",(spawnid,))
        cursor.execute("DELETE from spawn_skill where spawn_id=?;",(spawnid,))
        cursor.execute("DELETE from spawn_resistance where spawn_id=?;",(spawnid,))
        cursor.execute("DELETE from spawn_spell where spawn_id=?;",(spawnid,))
        cursor.execute("DELETE from spawn_stat where spawn_id=?;",(spawnid,))
        
        cursor.execute("SELECT id FROM item WHERE character_id=?;",(cid,))
        for itemID in list(cursor.fetchall()):
            DeleteItem(cursor,itemID[0])
        cursor.execute("DELETE from item where character_id=?;",(cid,))


def ConvertBuffer(publicName,buffer):
    print "Converting Player: %s"%publicName
    dbuffer = zlib.decompress(buffer)
    f = file("./data/tmp/pbuffer","wb")
    f.write(dbuffer)
    f.close()

    #first let's make the new player buffer which is just the player info
    shutil.copyfile("./data/tmp/pbuffer","./data/tmp/nbuffer")
    PLAYER_CONN = sqlite.connect("./data/tmp/nbuffer")
    c = PLAYER_CONN.cursor()
    RemoveCharacterTables(c)
    c.close()
    PLAYER_CONN.close()
    
    PCONN = sqlite.connect("./data/tmp/pbuffer")
    PCURSOR = PCONN.cursor()
    PCURSOR.execute("SELECT id from character;")
    
    for cid in PCURSOR.fetchall():
        shutil.copyfile("./data/tmp/pbuffer","./data/tmp/cbuffer")
        CHAR_CONN = sqlite.connect("./data/tmp/cbuffer",isolation_level = None)
        ccursor = CHAR_CONN.cursor()
        ccursor.execute("BEGIN TRANSACTION;")
        DeleteAllCharactersExcept(ccursor,cid[0])
        ccursor.execute("SELECT name,spawn_id from character where id = %i;"%cid[0])
        name,spawnid = ccursor.fetchone()

        CHARACTER_NAMES.append(name)
        
        ccursor.execute("SELECT race,pclass_internal,sclass_internal,tclass_internal,plevel,slevel,tlevel,realm from spawn where id = %i;"%spawnid)
        values = [None,publicName,name]
        values.extend(list(ccursor.fetchone()))
        
        
        ccursor.execute("END TRANSACTION;")
        ccursor.close()
        CHAR_CONN.close()
        
        #insert new PBUFFER
        f = file("./data/tmp/cbuffer","rb")
        cbuffer = f.read()
        f.close()
        
        cbuffer = zlib.compress(cbuffer)
        
        cbuffer = sqlite.Binary(cbuffer)
        
        values.append(cbuffer)
        
        DST_CURSOR.executemany("INSERT INTO character_buffer VALUES(?,?,?,?,?,?,?,?,?,?,?,?);",(values,))    

    PCURSOR.close()
    PCONN.close()
    
    #insert new PBUFFER
    f = file("./data/tmp/nbuffer","rb")
    pbuffer = f.read()
    f.close()
    
    pbuffer = zlib.compress(pbuffer)
    
    pbuffer = sqlite.Binary(pbuffer)
    
    
    DST_CURSOR.executemany("INSERT INTO player_buffer VALUES(?,?,?);",((None,publicName,pbuffer),))    

try:
    os.remove("./data/character_dst.db")
except:
    pass
if os.path.exists("./data/character_dst.db"):
    raise "unable to remove ./data/character_dst.db"

shutil.copyfile("./data/character_src.db","./data/character_dst.db")
    

SRC_CONN = sqlite.connect("./data/character_src.db")
DST_CONN = sqlite.connect("./data/character_dst.db",isolation_level = None)

SRC_CURSOR = SRC_CONN.cursor()
DST_CURSOR = DST_CONN.cursor()

DST_CURSOR.executescript("""
DROP TABLE player_buffer;
DROP TABLE cserver_character;
""")

#create schema
DST_CURSOR.executescript(CREATE_PLAYER_BUFFER_SQL)


DST_CURSOR.execute("BEGIN TRANSACTION;")


#every character buffer
SRC_CURSOR.execute("SELECT DISTINCT public_name from player_buffer")
pnames = SRC_CURSOR.fetchall()
for publicName in pnames:
    publicName = publicName[0]
    #if publicName != "JRitter":
    #    continue
    try:
        SRC_CURSOR.execute("SELECT buffer FROM player_buffer WHERE public_name = '%s' ORDER BY id DESC LIMIT 1;"%publicName)
        buffer = SRC_CURSOR.fetchone()[0]
        
        ConvertBuffer(publicName,buffer)
        
    except:
        traceback.print_exc()
        
        
CNAMES = []
for v in CHARACTER_NAMES:
    CNAMES.append((v[0].upper(),))
    
DST_CURSOR.executemany("INSERT INTO cserver_character VALUES (NULL,?)",CNAMES)


DST_CURSOR.execute("END TRANSACTION;")

SRC_CURSOR.close()
DST_CURSOR.close()
