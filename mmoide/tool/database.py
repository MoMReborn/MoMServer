from sqlite3 import dbapi2 as sqlite

def QueryWorldZones(gameroot,worldname):
    conn = sqlite.connect("./%s/data/worlds/multiplayer.baseline/world.db"%(gameroot))
    conn.text_factory = sqlite.OptimizedUnicode
    
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM zone;")
    
    zones = [row[0] for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    return zones
