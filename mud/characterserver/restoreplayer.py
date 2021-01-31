# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from sqlite3 import dbapi2 as sqlite
import zlib,traceback


PUBLICNAME = 'Fafhred'
conn = sqlite.connect("data/character/character.db",isolation_level=None)
        
cursor = conn.cursor()
cursor.execute("SELECT id,buffer FROM player_buffer WHERE public_name = '%s' ORDER BY id DESC;"%PUBLICNAME)

keep = []
remove = []
good = 0
bad = 0
for id,buffer in cursor.fetchall():
    print id
    try:
        zlib.decompress(buffer)
        keep.append(id)
        good+=1
    except:
        bad+=1
        remove.append(id)
        traceback.print_exc()
        
if not good:
    raise "NO GOOD BUFFERS!"

print "Good Buffer IDs",keep
print "Removing Bad Buffer IDs",remove

for b in remove:
    cursor.execute("DELETE from player_buffer WHERE id = '%i';"%b)

    
cursor.close()




