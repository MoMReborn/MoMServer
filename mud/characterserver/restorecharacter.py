# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


"""
TABLE character_buffer
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
"""

CHARACTERNAME = "test"
PUBLICNAME = "test"

from sqlite3 import dbapi2 as sqlite

#FROMCONN = sqlite.connect("from.db",isolation_level=None)
#TOCONN = sqlite.connect("to.db",isolation_level=None)

FROMCONN = sqlite.connect("../../data/character/June_11_2008/character_backup_1.db",isolation_level=None)
TOCONN = sqlite.connect("../../data/character/character.db",isolation_level=None)

fcursor = FROMCONN.cursor()
tcursor = TOCONN.cursor()



tcursor.execute("SELECT public_name FROM character_buffer WHERE character_name ='%s';"%CHARACTERNAME)
results = tcursor.fetchall()
print results
if len(results):
    raise "There is already a character buffer in destination",results

fcursor.execute("SELECT public_name,character_name,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm,rename,buffer FROM character_buffer WHERE public_name='%s' AND character_name ='%s';"%(PUBLICNAME,CHARACTERNAME))

results = fcursor.fetchall()
assert len(results)==1
r = results[0]
print r


buffer = sqlite.Binary(r[11])
values = (None,r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[8],r[9],r[10],buffer)

tcursor.execute("INSERT INTO character_buffer VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?);",values)









