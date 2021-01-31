# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


#utilities for the character server's central store, this is located here primarily so it's not included in the
#world server sources (although, it could be and we could just provide pyc

import time
from mud.world.defines import *
from mud.common.dbconfig import GetDBURI
from twisted.internet import reactor
import traceback

from sqlite3 import dbapi2 as sqlite
import os,re,zlib

PLAYER_TABLES = ["player","player_monster_spawn","item","item_container_content","item_variant"]

CHARACTER_TABLES= ["character","character_spell","character_skill","character_advancement","character_dialog_choice","character_vault_item","character_faction",
"spawn","spawn_skill","spawn_resistance","spawn_spell","spawn_stat","item","item_container_content","item_variant","spell_store"]

TABLES = PLAYER_TABLES[:]
TABLES.extend(CHARACTER_TABLES)


TVALUES = {}

TATTR = {}

CREATE_PLAYER_TABLE_SQL = ""
CREATE_CHARACTER_TABLE_SQL = ""

PLAYER_BUFFERS = []

CLUSTER = -1





def SetClusterNum(cluster):
    global CLUSTER
    CLUSTER = cluster


def GenerateInsertValues(table,valuesIn,playerID=None,characterID=None,spawnID=None,itemID=None,contentID=None):
    valuesOut = []
    for valueIn in valuesIn:
        valueOut = []
        
        for col,v in zip(TATTR[table],valueIn):
            if col == 'id':
                valueOut.append(None)
            elif col == 'playerID':
                valueOut.append(playerID)
            elif col == 'characterID':
                valueOut.append(characterID)
            elif col == 'itemID':
                valueOut.append(itemID)
            elif col == 'contentID':
                valueOut.append(contentID)
            elif col == 'spawnID':
                valueOut.append(spawnID)
            else:
                valueOut.append(v)
        
        valuesOut.append(valueOut)
    
    return valuesOut



# Separate function to install items because item containers require this to be recursive.
def InstallItemList(cursor, dstCursor, itemList, playerID, characterID, spawnID, indirect=False, oldContainerItem=None, newContainerItem=None, vault=False):
    # If indirect is True, the item list only contains item ids without the complete item
    #  information. We get such input from vault and container content. In both cases
    #  we need to do some sanity check on the linked item.
    if indirect:
        for itemID in itemList:
            cursor.execute("SELECT * FROM item WHERE id=? LIMIT 1;",(itemID[0],))
            itemValues = cursor.fetchone()
            # If itemValues is empty, the item backing store is missing. Can't do much more
            #  than purge the faulty items... but let's at least give a printout.
            if not itemValues:
                try:
                    # Get the name of the character that will be losing items.
                    charName = cursor.execute("SELECT name FROM spawn WHERE id=? LIMIT 1;",(spawnID,)).fetchone()[0]
                    # Print out an error message. For vault items we can actually say what
                    #  and how much got purged.
                    if vault:
                        cursor.execute("SELECT stack_count,name FROM character_vault_item WHERE item_id=? LIMIT 1;",(itemID[0],))
                        itemValues = cursor.fetchone()
                        print "ERROR: %i %s had to be purged from character %s's vault because they miss item backing."%(itemValues[0],itemValues[1],charName)
                    else:
                        dstCursor.execute("SELECT name FROM item WHERE id=? LIMIT 1;",(containerItem,))
                        print "ERROR: an item from character %s's container %s had to be purged because it misses item backing."%(charName,dstCursor.fetchone()[0])
                # Shouldn't happen, but if an exception occurs, sqlite returned us an
                #  empty value to process ... means there's no further error about
                #  vault or container content.
                except:
                    pass
                continue
            itemID = itemValues[0]
            # For indirect item storage player and character id must always be None.
            # Otherwise those items will show up in character inventory or bank.
            values = GenerateInsertValues('item',(itemValues,),None,None,spawnID)
            dstCursor.executemany('INSERT INTO item VALUES(%s)'%(TVALUES['item']),values)
            newItemID = dstCursor.lastrowid
            # Item Variants
            cursor.execute("SELECT * FROM item_variant WHERE item_id=?;",(itemID,))
            values = GenerateInsertValues('item_variant',cursor.fetchall(),None,None,spawnID,newItemID)
            dstCursor.executemany('INSERT INTO item_variant VALUES(%s)'%(TVALUES['item_variant']),values)
            # Item Containers
            try:
                cursor.execute("SELECT content_id FROM item_container_content WHERE item_id=?;",(itemID,))
                InstallItemList(cursor,dstCursor,cursor.fetchall(),playerID,characterID,spawnID,True,itemID,newItemID)
            except:
                traceback.print_exc()
                print "Probably a database that didn't yet hear of the introduction of item containers."
            
            # Store vault or container content elements.
            if vault:
                cursor.execute("SELECT * FROM character_vault_item WHERE item_id=? LIMIT 1;",(itemID,))
                values = GenerateInsertValues('character_vault_item',cursor.fetchall(),playerID,characterID,spawnID,newItemID)
                dstCursor.executemany('INSERT INTO character_vault_item VALUES(%s)'%(TVALUES['character_vault_item']),values)
            else:
                try:
                    cursor.execute("SELECT * FROM item_container_content WHERE item_id=? LIMIT 1;",(oldContainerItem,))
                    values = GenerateInsertValues('item_container_content',cursor.fetchall(),playerID,characterID,spawnID,newContainerItem,newItemID)
                    dstCursor.executemany('INSERT INTO item_container_content VALUES(%s)'%(TVALUES['item_container_content']),values)
                except:
                    traceback.print_exc()
                    print "Probably a database that didn't yet hear of the introduction of item containers."
    
    # Otherwise we deal with standard bank or inventory items.
    else:
        for itemValues in itemList:
            itemID = itemValues[0]
            values = GenerateInsertValues('item',(itemValues,),playerID,characterID,spawnID)
            dstCursor.executemany('INSERT INTO item VALUES(%s)'%(TVALUES['item']),values)
            newItemID = dstCursor.lastrowid
            # Item Variants
            cursor.execute("SELECT * FROM item_variant WHERE item_id=?;",(itemID,))
            values = GenerateInsertValues('item_variant',cursor.fetchall(),playerID,characterID,spawnID,newItemID)
            dstCursor.executemany('INSERT INTO item_variant VALUES(%s)'%(TVALUES['item_variant']),values)
            # Item Containers
            try:
                cursor.execute("SELECT content_id FROM item_container_content WHERE item_id=?;",(itemID,))
                InstallItemList(cursor,dstCursor,cursor.fetchall(),playerID,characterID,spawnID,True,itemID,newItemID)
            except:
                traceback.print_exc()
                print "Probably a database that didn't yet hear of the introduction of item containers."


def InstallCharacterBuffer(playerID,cname,buffer):
    from mud.world.player import Player
    tm = time.time()
    
    if not os.path.exists("data/tmp"):
        os.makedirs("data/tmp")
    
    try:
        dbuffer = zlib.decompress(buffer)
        f = file("data/tmp/character%i.db"%CLUSTER,"wb")
        f.write(dbuffer)
        f.close()
        
        dbconn = sqlite.connect("data/tmp/character%i.db"%CLUSTER)
        cursor = dbconn.cursor()
        dstConn = Player._connection.getConnection()
        dstCursor = dstConn.cursor()
    except:
        traceback.print_exc()
        return True
    
    error = False
    
    dstCursor.execute("END TRANSACTION;")
    dstCursor.execute("BEGIN TRANSACTION;")
    
    try:
        #character tables
        
        #character name and spawn name in buffer can be at odds based on rename
        #in fact rename doesn't check spawn names and must
        cursor.execute("SELECT name FROM character LIMIT 1;")
        name = cursor.fetchone()[0]
        if name != cname:
            cursor.execute("UPDATE character SET name = '%s' WHERE name = '%s';"%(cname,name))
        
        cursor.execute("SELECT name FROM spawn LIMIT 1;")
        name = cursor.fetchone()[0]
        if name != cname:
            cursor.execute("UPDATE spawn SET name = '%s' WHERE name = '%s';"%(cname,name))
        
        cursor.execute("SELECT * FROM character where name = '%s' LIMIT 1;"%cname)
        cvalues = cursor.fetchone()
        cid = cvalues[0] #for look up
        values = GenerateInsertValues('character',(cvalues,),playerID)
        sql = 'INSERT INTO character VALUES(%s)'%(TVALUES['character'])
        try:
            dstCursor.executemany(sql,values)
        except:
            traceback.print_exc()
            print sql,values
            raise "Error installing character",cname
        characterID = dstCursor.lastrowid
        #generate spawn
        cursor.execute("SELECT * FROM spawn WHERE character_id = %i LIMIT 1;"%cid)
        svalues = cursor.fetchone()
        sid = svalues[0]
        values = GenerateInsertValues('spawn',(svalues,),playerID,characterID)
        dstCursor.executemany('INSERT INTO spawn VALUES(%s)'%(TVALUES['spawn']),values)
        spawnID = dstCursor.lastrowid
        #update character with spawnID now that we have it
        dstCursor.execute("UPDATE character SET spawn_id = %i WHERE id = %i;"%(spawnID,characterID))
        
        #character tables
        ctables = ["character_spell","character_skill","character_advancement","character_dialog_choice","spell_store","character_faction"]
        for t in ctables:
            cursor.execute("SELECT * FROM %s WHERE character_id = %i;"%(t,cid))
            values = GenerateInsertValues(t,cursor.fetchall(),playerID,characterID,spawnID)
            dstCursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),values)
        
        #items
        # Get all items, make sure to leave out bank and vault items
        #  that still have a character id assigned (legacy).
        cursor.execute("SELECT * FROM item WHERE character_id = %i and (slot >= %i or slot < %i) and slot != -1;"%(cid,RPG_SLOT_BANK_END,RPG_SLOT_BANK_BEGIN))
        # player_id must be None for items not in bank.
        InstallItemList(cursor,dstCursor,cursor.fetchall(),None,characterID,spawnID)
        
        #character vault items
        cursor.execute("SELECT item_id FROM character_vault_item WHERE character_id = %i;"%cid)
        InstallItemList(cursor,dstCursor,cursor.fetchall(),playerID,characterID,spawnID,True,None,None,True)
        
        #spawn tables
        stables = ["spawn_skill","spawn_resistance","spawn_spell","spawn_stat"]
        for t in stables:
            cursor.execute("SELECT * FROM %s WHERE spawn_id = %i;"%(t,sid))
            values = GenerateInsertValues(t,cursor.fetchall(),playerID,characterID,spawnID)
            dstCursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),values)
        
        #print "whee"
        dstCursor.execute('END TRANSACTION;')
    except:
        error = True
        traceback.print_exc()
        dstCursor.execute('ROLLBACK TRANSACTION;')
    
    dstCursor.execute('BEGIN TRANSACTION;')
    
    dstCursor.close()
    #dstConn.close()
    cursor.close()
    dbconn.close()
    
    print "Character installation took %f seconds"%(time.time()-tm)
    
    return error



def InstallPlayerBuffer(buffer):
    global CREATE_PLAYER_TABLE_SQL
    if not CREATE_PLAYER_TABLE_SQL:
        Initialize()
    tm = time.time()
    from mud.world.player import Player
    
    if not os.path.exists("data/tmp"):
        os.makedirs("data/tmp")
    
    try:
        dbuffer = zlib.decompress(buffer)
        f = file("data/tmp/player%i.db"%CLUSTER,"wb")
        f.write(dbuffer)
        f.close()
        
        dbconn = sqlite.connect("data/tmp/player%i.db"%CLUSTER)
        cursor = dbconn.cursor()
        dstConn = Player._connection.getConnection()
        dstCursor = dstConn.cursor()
    except:
        traceback.print_exc()
        return True
    
    error = False
    
    dstCursor.execute("END TRANSACTION;")
    dstCursor.execute("BEGIN TRANSACTION;")
    try:
        cursor.execute("SELECT * FROM player;")
        values = GenerateInsertValues('player',cursor.fetchall())
        dstCursor.executemany('INSERT INTO player VALUES(%s)'%(TVALUES['player']),values)
        playerID = dstCursor.lastrowid
        
        #player tables
        ptables = ["player_monster_spawn"]
        for t in ptables:
            cursor.execute("SELECT * FROM %s;"%(t))
            values = GenerateInsertValues(t,cursor.fetchall(),playerID)
            dstCursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),values)
        
        #bank items
        cursor.execute("SELECT * FROM item WHERE slot >= %i and slot < %i;"%(RPG_SLOT_BANK_BEGIN,RPG_SLOT_BANK_END))
        InstallItemList(cursor,dstCursor,cursor.fetchall(),playerID,None,None)
        
        #character tables
        if 0:
            cursor.execute("SELECT * FROM character;")
            for cvalues in cursor.fetchall():
                cid = cvalues[0] #for look up
                values = GenerateInsertValues('character',(cvalues,),playerID)
                dstCursor.executemany('INSERT INTO character VALUES(%s)'%(TVALUES['character']),values)
                characterID = dstCursor.lastrowid
                #generate spawn
                cursor.execute("SELECT * FROM spawn WHERE character_id = %i LIMIT 1;"%cid)
                svalues = cursor.fetchone()
                sid = svalues[0]
                values = GenerateInsertValues('spawn',(svalues,),playerID,characterID)
                dstCursor.executemany('INSERT INTO spawn VALUES(%s)'%(TVALUES['spawn']),values)
                spawnID = dstCursor.lastrowid
                #update character with spawnID now that we have it
                dstCursor.execute("UPDATE character SET spawn_id = %i WHERE id = %i;"%(spawnID,characterID))
                
                #character tables
                ctables = ["character_spell","character_skill","character_advancement","character_dialog_choice","spell_store","character_faction"]
                for t in ctables:
                    cursor.execute("SELECT * FROM %s WHERE character_id = %i;"%(t,cid))
                    values = GenerateInsertValues(t,cursor.fetchall(),playerID,characterID,spawnID)
                    dstCursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),values)
                
                #items
                # Get all items, make sure to leave out bank and vault items
                #  that still have a character id assigned (legacy).
                cursor.execute("SELECT * FROM item WHERE character_id = %i and (slot >= %i or slot < %i) and slot != -1;"%(cid,RPG_SLOT_BANK_END,RPG_SLOT_BANK_BEGIN))
                # player_id must be None for items not in bank.
                InstallItemList(cursor,dstCursor,cursor.fetchall(),None,characterID,spawnID)
                
                #character vault items
                cursor.execute("SELECT item_id FROM character_vault_item WHERE character_id = %i;"%cid)
                InstallItemList(cursor,dstCursor,cursor.fetchall(),playerID,characterID,spawnID,True,None,None,True)
                
                #spawn tables
                stables = ["spawn_skill","spawn_resistance","spawn_spell","spawn_stat"]
                for t in stables:
                    cursor.execute("SELECT * FROM %s WHERE spawn_id = %i;"%(t,sid))
                    values = GenerateInsertValues(t,cursor.fetchall(),playerID,characterID,spawnID)
                    dstCursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),values)
        
        #print "whee"
        dstCursor.execute('END TRANSACTION;')
    except:
        error = True
        traceback.print_exc()
        dstCursor.execute('ROLLBACK TRANSACTION;')
    
    dstCursor.execute('BEGIN TRANSACTION;')
    
    dstCursor.close()
    #dstConn.close()
    cursor.close()
    dbconn.close()
    
    print "Player installation took %f seconds"%(time.time()-tm)
    
    return error



def Initialize():
    global CREATE_PLAYER_TABLE_SQL,CREATE_CHARACTER_TABLE_SQL
    
    dbconn = sqlite.connect(GetDBURI()[10:])
    cursor = dbconn.cursor()
    
    CREATE_PLAYER_TABLE_SQL = ""
    for t in PLAYER_TABLES:
        try:
            cursor.execute('PRAGMA table_info(%s);'%t)
            TATTR[t] = []
            sql = []
            c = 0
            for col in cursor.fetchall():
                TATTR[t].append(UnderToMixed(col[1]))
                sql.append("%s %s"%(col[1],col[2]))
                c += 1
            TVALUES[t] = ','.join('?' * c)
            CREATE_PLAYER_TABLE_SQL += "CREATE TABLE %s (%s);"%(t,', '.join(sql))
        except:
            traceback.print_exc()
    
    CREATE_CHARACTER_TABLE_SQL = ""
    for t in CHARACTER_TABLES:
        try:
            cursor.execute('PRAGMA table_info(%s);'%t)
            TATTR[t] = []
            sql = []
            c = 0
            for col in cursor.fetchall():
                TATTR[t].append(UnderToMixed(col[1]))
                sql.append("%s %s"%(col[1],col[2]))
                c += 1
            TVALUES[t] = ','.join('?' * c)
            CREATE_CHARACTER_TABLE_SQL += "CREATE TABLE %s (%s);"%(t,', '.join(sql))
        except:
            traceback.print_exc()
    
    cursor.close()
    dbconn.close()


def ExtractItemList(cursor, excursor, itemList, indirect=False):
    # If indirect is true, need first to get item attributes, the item list doesn't
    #  already contain them. This is necessary for vault and container content.
    if indirect:
        for item in itemList:
            itemID = item[0]
            cursor.execute("SELECT * FROM item WHERE id=? LIMIT 1;",(itemID,))
            excursor.executemany('INSERT INTO item VALUES(%s)'%(TVALUES['item']),cursor.fetchall())
            cursor.execute("SELECT * FROM item_variant WHERE item_id=?;",(itemID,))
            excursor.executemany('INSERT INTO item_variant VALUES(%s)'%(TVALUES['item_variant']),cursor.fetchall())
            # Separate select so we know at which index we can find the item id.
            try:
                cursor.execute("SELECT content_id FROM item_container_content WHERE item_id=?;",(itemID,))
                ExtractItemList(cursor,excursor,cursor.fetchall(),True)
                cursor.execute("SELECT * FROM item_container_content WHERE item_id=?;",(itemID,))
                excursor.executemany('INSERT INTO item_container_content VALUES(%s)'%(TVALUES['item_container_content']),cursor.fetchall())
            except:
                traceback.print_exc()
                print "Probably a database that didn't yet hear of the introduction of item containers."
    else:
        for item in itemList:
            itemID = item[0]
            cursor.execute("SELECT * FROM item_variant WHERE item_id=?;",(itemID,))
            excursor.executemany('INSERT INTO item_variant VALUES(%s)'%(TVALUES['item_variant']),cursor.fetchall())
            # Separate select so we know at which index we can find the item id.
            try:
                cursor.execute("SELECT content_id FROM item_container_content WHERE item_id=?;",(itemID,))
                ExtractItemList(cursor,excursor,cursor.fetchall(),True)
                cursor.execute("SELECT * FROM item_container_content WHERE item_id=?;",(itemID,))
                excursor.executemany('INSERT INTO item_container_content VALUES(%s)'%(TVALUES['item_container_content']),cursor.fetchall())
            except:
                traceback.print_exc()
                print "Probably a database that didn't yet hear of the introduction of item containers."
        excursor.executemany('INSERT INTO item VALUES(%s)'%(TVALUES['item']),itemList)


def ExtractPlayer(publicName,pid,cid,append=True):
    from mud.world.player import Player
    #commit current transaction so we are current
    conn = Player._connection.getConnection()
    c = conn.cursor()
    c.execute("END TRANSACTION;")
    c.execute("BEGIN TRANSACTION;")
    c.close()
    return ExtractCharactersThread(publicName,pid,cid,append)


def ExtractCharactersThread(publicName,pid,cid,append=True):
    global CREATE_PLAYER_TABLE_SQL
    
    from mud.world.player import Player
    
    try:
        try:
            os.remove("export%i.db"%CLUSTER)
        except:
            pass
        
        #commit current transaction
        dbconn = sqlite.connect(GetDBURI()[10:])#chars[0]._connection.getConnection()
        cursor = dbconn.cursor()
        exconn = sqlite.connect("export%i.db"%CLUSTER,isolation_level = None)
        excursor = exconn.cursor()
        excursor.execute("BEGIN TRANSACTION;")
        
        if not CREATE_PLAYER_TABLE_SQL:
            Initialize()
        
        tm = time.time()
        excursor.executescript(CREATE_PLAYER_TABLE_SQL)
        
        #copy player information
        cursor.execute("SELECT * FROM player WHERE id = %i LIMIT 1;"%pid)
        excursor.executemany('INSERT INTO player VALUES(%s)'%(TVALUES['player']),cursor.fetchall())
        
        #player tables
        ptables = ["player_monster_spawn"]
        for t in ptables:
            cursor.execute("SELECT * FROM %s WHERE player_id = %i;"%(t,pid))
            excursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),cursor.fetchall())
        
        #bank items
        cursor.execute("SELECT * FROM item WHERE player_id = %i and slot >= %i and slot < %i;"%(pid,RPG_SLOT_BANK_BEGIN,RPG_SLOT_BANK_END))
        ExtractItemList(cursor,excursor,cursor.fetchall())
        
        excursor.execute("END;")
        
        excursor.close()
        exconn.close()
        
        f = file("export%i.db"%CLUSTER,"rb")
        buff = f.read()
        f.close()
        pbuffer = zlib.compress(buff)
        
        #character export
        
        try:
            os.remove("cexport%i.db"%CLUSTER)
        except:
            pass
        
        #commit current transaction
        exconn = sqlite.connect("cexport%i.db"%CLUSTER,isolation_level = None)
        excursor = exconn.cursor()
        excursor.execute("BEGIN TRANSACTION;")
        
        tm = time.time()
        excursor.executescript(CREATE_CHARACTER_TABLE_SQL)
        
        cursor.execute("SELECT * FROM character WHERE id = %i;"%cid)
        excursor.executemany('INSERT INTO character VALUES(%s)'%(TVALUES['character']),cursor.fetchall())
        
        ctables = ["character_spell","character_skill","character_advancement","character_dialog_choice","spell_store","character_faction"]
        for t in ctables:
            cursor.execute("SELECT * FROM %s WHERE character_id = %i;"%(t,cid))
            excursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),cursor.fetchall())
        
        #items
        cursor.execute("SELECT * FROM item WHERE character_id = %i and (slot >= %i or slot < %i) and slot != -1;"%(cid,RPG_SLOT_BANK_END,RPG_SLOT_BANK_BEGIN))
        ExtractItemList(cursor,excursor,cursor.fetchall())
        
        #vault items
        cursor.execute("SELECT * FROM character_vault_item WHERE character_id = %i;"%cid)
        excursor.executemany('INSERT INTO character_vault_item VALUES(%s)'%(TVALUES['character_vault_item']),cursor.fetchall())
        # Separate select to make sure item_id is at a known index.
        cursor.execute("SELECT item_id FROM character_vault_item WHERE character_id = %i;"%cid)
        ExtractItemList(cursor,excursor,cursor.fetchall(),True)
        
        #spawn info
        cursor.execute("SELECT name,race,pclass_internal,sclass_internal,tclass_internal,plevel,slevel,tlevel,realm FROM spawn WHERE character_id = '%i' LIMIT 1;"%cid)
        cvalues = cursor.fetchone()
        
        cursor.execute("SELECT * FROM spawn WHERE character_id = %i LIMIT 1;"%cid)
        v = cursor.fetchone()
        sid = v[0]
        excursor.executemany('INSERT INTO spawn VALUES(%s)'%(TVALUES['spawn']),(v,))
        
        stables = ["spawn_skill","spawn_resistance","spawn_spell","spawn_stat"]
        for t in stables:
            cursor.execute("SELECT * FROM %s WHERE spawn_id = %i;"%(t,sid))
            excursor.executemany('INSERT INTO %s VALUES(%s)'%(t,TVALUES[t]),cursor.fetchall())
        
        excursor.execute("END;")
        
        excursor.close()
        exconn.close()
        
        f = file("cexport%i.db"%CLUSTER,"rb")
        buff = f.read()
        f.close()
        cbuffer = zlib.compress(buff)
        
        cursor.close()
        
        v = (publicName,pbuffer,cbuffer,cvalues)
        if append:
            PLAYER_BUFFERS.append(v)
        
        print "Character export took %f seconds"%(time.time()-tm)
        return v
    
    except:
        traceback.print_exc()
        return None



# Function to reformat strings with underscores
#  to strings with mixed case. Every underscore
#  precedes an uppercase letter.
# Database uses underscore names, since it's case-insensitive.
_underToMixedRE = re.compile('_(.)')
def UnderToMixed(name):
    if name.endswith('_id'):
        return UnderToMixed(name[:-3] + "ID")
    return _underToMixedRE.sub(lambda m: m.group(1).upper(), name)

