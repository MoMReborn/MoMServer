# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from tgenative import *
from mud.tgepython.console import TGEExport

from sqlite3 import dbapi2 as sqlite
from md5 import new as newMD5
import os
import traceback

from mud.gamesettings import *
from mud.world.defines import *
from pointsOfInterest import POI
from mud.client.playermind import TOGGLEABLECHANNELS
from defaultCommandsWnd import GetDefaultCommand
from skillinfo import GetSkillInfo
from defaultMacros import CreateDefaultMacros
from tomeGui import TomeGui
TomeGui = TomeGui.instance



# Window version.
WINDOW_DAT_VERSION = 2
# Initial window settings.
# Values are (name, x_coord, y_coord, x_extent, y_extent, active).
WINDOW_INITIAL = {
    'PARTYWND_WINDOW': (523, 73, -1, -1, 0),
    'CHARMINIWND_WINDOW': (0, 0, -1, -1, 1),
    'MACROWND_WINDOW': (302, 580, -1, -1, 1),
    'TOMEGUI_WINDOW': (340, 0, -1, -1, 1),
    'CHATGUI_WINDOW': (732, 580, 292, 188, 1),
    'GAMETEXTGUI_WINDOW': (0, 580, 292, 188, 1),
    'ITEMINFOWND_WINDOW': (352, 158, -1, -1, -1),
    'DEFAULTCOMMANDSWND_WINDOW': (464, 196, -1, -1, 0),
    'NPCWND_WINDOW': (119, 79, -1, -1, -1),
    'GAMEOPTIONSWND_WINDOW': (434, 302, -1, -1, -1),
    'ALLIANCEWND_WINDOW': (456, 0, -1, -1, 0),
    'LEADERWND_WINDOW': (192, 232, -1, -1, 0),
    'TRACKINGWND_WINDOW': (370, 282, 364, 316, -1),
    'MAPWND_WINDOW': (0, 0, 300, 325, 0),
    'HELPWND_WINDOW': (337, 180, -1, -1, 0),
    'JOURNALWND_WINDOW': (337, 180, -1, -1, 0),
    'PETWND_WINDOW': (337, 180, -1, -1, -1),
    'BUFFWND_WINDOW': (903, 0, -1, -1, 0),
    'VAULTWND_WINDOW': (541, 170, -1, -1, -1),
    'FRIENDSWND_WINDOW': (309, 77, -1, -1, 0),
    'CRAFTINGWND_WINDOW': (150, 100, -1, -1, -1),
    'LOOTWND_WINDOW': (150, 100, -1, -1, -1)
}
def fillWindow(cursor):
    for name,data in WINDOW_INITIAL.iteritems():
        values = [None,name]
        values.extend(data)
        cursor.execute("INSERT INTO window VALUES(?,?,?,?,?,?,?);",values)



# Script to fill the settings database with necessary tables.
PLAYERSETTINGS_CREATETABLES = """
CREATE TABLE world
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    singleplayer INTEGER
);

CREATE TABLE character
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    realm INTEGER,
    world_id INTEGER,
    last_party INTEGER DEFAULT 0,
    p_xp_gain FLOAT DEFAULT 1.0,
    s_xp_gain FLOAT DEFAULT 0.0,
    t_xp_gain FLOAT DEFAULT 0.0,
    encounter_pve_zone INTEGER DEFAULT 1,
    encounter_pve_death INTEGER DEFAULT 1,
    link_mouse_target INTEGER DEFAULT 1,
    link_character_target TEXT DEFAULT "",
    default_target TEXT DEFAULT ""
);

CREATE TABLE journal_entry
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT,
    entry TEXT,
    text TEXT,
    character_id INTEGER,
    hidden INTEGER DEFAULT 0
);

CREATE TABLE poi
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    zone TEXT,
    x_coord FLOAT,
    y_coord FLOAT,
    z_coord FLOAT,
    description TEXT,
    character_id INTEGER
);

CREATE TABLE friend
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

CREATE TABLE ignore
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

CREATE TABLE macro
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT DEFAULT "",
    page INTEGER,
    slot INTEGER,
    hotkey TEXT DEFAULT "",
    icon TEXT DEFAULT "",
    description TEXT DEFAULT "",
    wait_all INTEGER DEFAULT 1,
    manual_delay INTEGER DEFAULT 0,
    character_id INTEGER
);

CREATE TABLE macro_line
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    line_index INTEGER,
    command TEXT DEFAULT "",
    mandatory INTEGER DEFAULT 1,
    delay_after INTEGER DEFAULT 0,
    macro_id INTEGER
);

CREATE TABLE window
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    x_coord INTEGER,
    y_coord INTEGER,
    x_extent INTEGER,
    y_extent INTEGER,
    active INTEGER
);

CREATE TABLE misc
(
    channel_filters INTEGER DEFAULT %i,
    window_version INTEGER DEFAULT %i,
    last_realm INTEGER DEFAULT %i,
    extended_macros INTEGER DEFAULT 1
);
"""%(TOGGLEABLECHANNELS['COMBAT'],WINDOW_DAT_VERSION,RPG_REALM_DEFAULT)


# Dictionary with scripts or functions to fill database tables with initial values.
# Every entry that needs a default value should either be defined with a default in the
#  create tables script or with a script or function in this dictionary.
# Functions take the cursor as argument.
PlayerSettingsFillScripts = {
    'window': fillWindow,
    'misc': "INSERT INTO misc VALUES(%i,%i,%i,%i);"%(TOGGLEABLECHANNELS['COMBAT'],WINDOW_DAT_VERSION,RPG_REALM_DEFAULT,1)
}



PLAYERSETTINGS = None



class PlayerSettings:
    def __init__(self):
        dbpath = "%s/data/settings.db"%(GAMEROOT)
        # If the database holding player settings doesn't exist yet,
        #  create a new one and initialize.
        newDB = False
        if not os.path.exists(dbpath):
            newDB = True
        
        # Get database connection and cursor.
        # Connecting will create database if non-existant.
        self.connection = sqlite.connect(dbpath)
        self.connection.text_factory = str
        self.connection.isolation_level = None
        cursor = self.cursor = self.connection.cursor()
        
        # Create tables if necessary and fill with initial content.
        if newDB:
            cursor.executescript(PLAYERSETTINGS_CREATETABLES)
            # Fill database with initial values.
            for table,filler in PlayerSettingsFillScripts.iteritems():
                try:
                    filler(cursor)
                except:
                    cursor.execute(filler)
        # If database is already present, check if layout needs an update.
        else:
            self.updateDatabase()
        
        # Load everything that doesn't need other stuff to be set up.
        # Windows have to be loaded separately.
        
        # Load misc settings.
        self.channelFilters,self.windowVersion,self.lastRealm,self.useExtendedMacros = cursor.execute("SELECT channel_filters,window_version,last_realm,extended_macros FROM misc LIMIT 1;").fetchone()
        
        # Configure macro master.
        from macro import MACROMASTER
        MACROMASTER.extendedMacros = self.useExtendedMacros
        
        # Load friend and ignore lists.
        self.loadFriends()
        self.loadIgnored()
        
        # Dictionary for window settings. Keys are window names,
        #  values are tuples of (window object,boolean True if active,flag if resizable).
        self.windows = dict()
        # Name of current world.
        self.worldname = ""
        # ID of current world in settings database.
        self.worldID = 0
        # Flag that gets set if world changes, used when zone changes to
        #  determine if it's an initial zone-in, needs some additional setup.
        self.newWorld = False
        # Current zone name.
        self.zone = ""
        # Currently active character infos, the same as PARTYWND.charInfos.
        self.charInfos = None
        # Currently active character index, not to be confused with characterID.
        # charIndex holds the index in character or charInfo dicts, while characterID
        #  holds the character index in player settings database.
        self.charIndex = 0
        # Dictionary of currently active character. Key is index,
        #  value is character ID in settings database.
        self.characters = dict()
        # Character ID in settings database of main character.
        self.characterID = 0
        # Dictionary of points of interest for main character and current zone.
        # Key is description, value a tuple of three coordinates.
        self.poi = dict()
        # Journal for currently active character. A journal is a dictionary of topics with
        #  the values (again dictionaries) holding the different topic entries along with the text.
        self.journal = None
        # Collection of macros for currently active party members. A macro collection is a dictionary
        #  with character indexes (not IDs) as keys and character macro dictionaries as values.
        # Those character macro dictionaries have as keys a tuple of (macroPage,macroSlot) and
        #  directly store the related Macro class instances as values.
        self.macroCollection = None
    
    
    # Update database to current layout.
    def updateDatabase(self):
        cursor = self.cursor
        
        # Setup database in memory.
        memconn = sqlite.connect(":memory:")
        memconn.text_factory = str
        memconn.isolation_level = None
        memcursor = memconn.cursor()
        memcursor.executescript(PLAYERSETTINGS_CREATETABLES)
        
        # Compare database layout.
        memlist = dict(memcursor.execute("SELECT name,sql FROM sqlite_master WHERE type='table';").fetchall())
        curlist = dict(cursor.execute("SELECT name,sql FROM sqlite_master WHERE type='table';").fetchall())
        # If layout is equal, clean up and return.
        if memlist == curlist:
            print 'Player settings database layout is up to date.'
            memcursor.close()
            memconn.close()
            return
        
        # Otherwise, update database layout.
        print 'Updating player settings database layout ...'
        
        # Gather information about tables that need updating.
        tableAdd = []
        tableAlter = {}
        for name,sql in memlist.iteritems():
            try:
                prevsql = curlist[name]
                if prevsql != sql:
                    tableAlter[name] = sql
                del curlist[name]
            except KeyError:
                tableAdd.append(name)
        tableDrop = curlist.iterkeys()
        
        # First add missing tables.
        for newTable in tableAdd:
            cursor.execute(memlist[newTable])
            # Try executing fill script or function if available.
            try:
                filler = PlayerSettingsFillScripts[newTable]
                try:
                    filler(cursor)
                except:
                    cursor.execute(filler)
            except KeyError:
                pass
        
        # Then drop tables no longer used.
        for dropTable in tableDrop:
            cursor.execute('DROP TABLE %s;'%dropTable)
        
        # Finally alter tables that differ in layout.
        for alterTable,newsql in tableAlter.iteritems():
            # Get table schema.
            curSchema = cursor.execute('PRAGMA TABLE_INFO(%s);'%alterTable).fetchall()
            memSchema = memcursor.execute('PRAGMA TABLE_INFO(%s);'%alterTable).fetchall()
            # Gather new column names.
            newColumns = dict((column[1],column[4]) for column in memSchema)
            # Gather current table information, except what will be dropped.
            curColumns = tuple(column[1] for column in curSchema if column[1] in newColumns)
            curColnum = len(curColumns)
            curColumns = ','.join(curColumns)
            curTableData = cursor.execute('SELECT %s FROM %s;'%(curColumns,alterTable)).fetchall()
            # Now drop old table, the alter table command can't be used because this one
            #  would not be able to clear old columns.
            cursor.execute('DROP TABLE %s;'%alterTable)
            # Recreate table and insert backupped data.
            cursor.execute(newsql)
            for data in curTableData:
                cursor.execute('INSERT INTO %s (%s) VALUES(%s)'%(alterTable,curColumns,','.join('?'*curColnum)),data)
    
    
    # Update world the player is on. Doesn't need to be called from outside of class.
    # Also gets current realm if available.
    def updateWorld(self):
        cursor = self.cursor
        
        # Get current world and single player flag.
        worldname = TGEGetGlobal("$Py::WORLDNAME")
        singleplayer = int(TGEGetGlobal("$Py::ISSINGLEPLAYER"))
        
        # Only need to process further if current world differs from set world.
        if self.worldname != worldname:
            self.newWorld = True
            self.worldname = worldname
            data = cursor.execute("SELECT id,singleplayer FROM world WHERE name=? AND (singleplayer=? OR singleplayer isnull) LIMIT 1;",(worldname,singleplayer)).fetchone()
            # If world doesn't yet exist in database, insert it.
            if data == None:
                cursor.execute("INSERT INTO world (name,singleplayer) VALUES(?,?);",(worldname,singleplayer))
                self.worldID = cursor.execute("SELECT id FROM world WHERE name=? AND singleplayer=? LIMIT 1;",(worldname,singleplayer)).fetchone()[0]
            else:
                self.worldID,dbsingleplayer = data
                # Insert singleplayer value if missing.
                if dbsingleplayer == None:
                    cursor.execute("UPDATE world SET singleplayer=? WHERE id=?;",(singleplayer,self.worldID))
        try:
            realm = int(TGEGetGlobal("$Py::REALM"))
            if self.lastRealm != realm:
                self.lastRealm = realm
                cursor.execute("UPDATE misc SET last_realm=?;",(realm,))
        except:
            # Use default.
            pass
    
    
    # Update the zone the player is in and related settings.
    def updateZone(self,zoneName):
        self.updateWorld()
        self.zone = zoneName
        # Update settings that need the player zoned in but only get set once per world.
        if self.newWorld:
            self.newWorld = False
            # Set channel filters (some may need to be passed to server, that's why here).
            channelFilters = self.channelFilters
            from mud.client.playermind import PLAYERMIND
            if channelFilters & TOGGLEABLECHANNELS['H']:
                TomeGui.onHelpChannelToggle(False,True)
            if channelFilters & TOGGLEABLECHANNELS['O']:
                TomeGui.onOffTopicChannelToggle(False,True)
            if channelFilters & TOGGLEABLECHANNELS['M']:
                TomeGui.onGlobalChannelToggle(False,True)
            if channelFilters & TOGGLEABLECHANNELS['W']:
                PLAYERMIND.doCommand("CHANNEL",[0,"world","off"])
            if channelFilters & TOGGLEABLECHANNELS['Z']:
                PLAYERMIND.doCommand("CHANNEL",[0,"zone","off"])
            # Need to do inverse check for combat channel since it defaults to off.
            if not channelFilters & TOGGLEABLECHANNELS['COMBAT']:
                PLAYERMIND.doCommand("CHANNEL",[0,"combat","on"])
        self.loadPOI()
    
    
    # After a character has been renamed, call this function so journal entries,
    #  macros and other character related stuff doesn't get lost.
    def renameCharacter(self,oldName,newName):
        cursor = self.cursor
        
        # Need to update world information first so we pick the right character.
        self.updateWorld()
        
        # Rename the character. If the database update fails, the character hasn't
        #  yet been entered and we don't need to worry anyway.
        try:
            cursor.execute("UPDATE character SET name=? WHERE world_id=? AND name=?;",(newName,self.worldID,oldName))
        except:
            traceback.print_exc()
    
    
    # Set character infos, which characters are active.
    def setCharacterInfos(self,cinfos):
        # Only need to do anything if character informations actually change.
        if cinfos == self.charInfos:
            return
        
        cursor = self.cursor
        
        # Need to update world information first.
        self.updateWorld()
        
        # Reset last party in database for current realm.
        realm = self.lastRealm
        cursor.execute("UPDATE character SET last_party=? WHERE world_id=? AND last_party=?;",(0,self.worldID,realm))
        
        # Update character information.
        self.charInfos = cinfos
        self.charIndex = 0
        characters = {}
        for index,cinfo in cinfos.iteritems():
            characterID = cursor.execute("SELECT id FROM character WHERE world_id=? AND (realm=? OR realm isnull) AND name=? LIMIT 1;",(self.worldID,realm,cinfo.NAME)).fetchone()
            # If characterID is None, the entry isn't present in the database, so insert.
            if characterID == None:
                cursor.execute("INSERT INTO character (name,realm,world_id,last_party) VALUES(?,?,?,?);",(cinfo.NAME,realm,self.worldID,realm))
                characters[index] = cursor.execute("SELECT id FROM character WHERE world_id=? AND realm=? AND name=? LIMIT 1;",(self.worldID,realm,cinfo.NAME)).fetchone()[0]
            else:
                characterID = characterID[0]
                # Update last party.
                cursor.execute("UPDATE character SET realm=?, last_party=? WHERE id=?;",(realm,realm,characterID))
                characters[index] = characterID
        self.characterID = characters[self.charIndex]
        
        # Load character settings for all party members.
        for charIndex,characterID in characters.iteritems():
            charSettings = cinfos[charIndex].clientSettings = dict()
            pXPGain,sXPGain,tXPGain,encounterPVEZone,encounterPVEDeath,linkMouseTarget,linkCharacterTarget,defaultTarget = cursor.execute("SELECT p_xp_gain,s_xp_gain,t_xp_gain,encounter_pve_zone,encounter_pve_death,link_mouse_target,link_character_target,default_target FROM character WHERE id=? LIMIT 1;",(characterID,)).fetchone()
            charSettings['PXPGAIN'] = pXPGain
            charSettings['SXPGAIN'] = sXPGain
            charSettings['TXPGAIN'] = tXPGain
            charSettings['ENCOUNTERPVEZONE'] = encounterPVEZone
            charSettings['ENCOUNTERPVEDIE'] = encounterPVEDeath
            charSettings['LINKMOUSETARGET'] = linkMouseTarget
            charSettings['LINKTARGET'] = linkCharacterTarget
            charSettings['DEFAULTTARGET'] = defaultTarget
        
        # Check if this is a new constellation of characters.
        # Macros and journals only need reloading if this constellation changes.
        if self.characters != characters:
            
            # Assign the new character constellation.
            self.characters = characters
            
            # Load macros for our characters.
            self.loadMacros()
            
            # Update journal for main character, each character has his/her/its own.
            self.updateJournal()
        
        # Otherwise we're zoning and need to make sure the special attack macros
        #  update their special visibility.
        else:
            from macro import MACROMASTER
            for charIndex in characters.iterkeys():
                MACROMASTER.updateAttackMacros(charIndex,cinfos[charIndex].RAPIDMOBINFO.AUTOATTACK)
        
        # If the zone name isn't set yet, we're still zoning and points of interest
        #  will be updated after anyway.
        if self.zone:
            self.loadPOI()
    
    
    # Call this function if character settings have changed to store them in the database.
    def storeCharacterSettings(self):
        cursor = self.cursor
        
        # Run through all characters in current party and store their related settings.
        for charIndex,characterID in self.characters.iteritems():
            charSettings = self.charInfos[charIndex].clientSettings
            cursor.execute("UPDATE character SET p_xp_gain=?, s_xp_gain=?, t_xp_gain=?, encounter_pve_zone=?, encounter_pve_death=?, link_mouse_target=?, link_character_target=?, default_target=? WHERE id=?;",(charSettings['PXPGAIN'],charSettings['SXPGAIN'],charSettings['TXPGAIN'],charSettings['ENCOUNTERPVEZONE'],charSettings['ENCOUNTERPVEDIE'],charSettings['LINKMOUSETARGET'],charSettings['LINKTARGET'],charSettings['DEFAULTTARGET'],characterID))
    
    
    # If the main character in party changes, need to update
    #  character based settings like journal and poi.
    def updateMainCharIndex(self,index):
        # Only update if index actually changes and to a valid one.
        if index >= 0 and index != self.charIndex:
            self.charIndex = index
            self.characterID = self.characters[index]
            # Update journal for main character, each character has his/her/its own.
            self.updateJournal()
            # Update points of interest.
            self.loadPOI()
    
    
    # If a character gets deleted, call this function to clean up journal entries,
    #  points of interest and stuff.
    def characterDeleted(self,charname):
        cursor = self.cursor
        # Try to get the id of the character to be deleted.
        charID = cursor.execute("SELECT id FROM character WHERE world_id=? AND realm=? AND name=?;",(self.worldID,self.lastRealm,charname)).fetchone()
        if charID == None:
            # Nothing to delete, character probably didn't get used yet.
            return
        charID = charID[0]
        # Remove all associated data from database.
        cursor.execute("DELETE FROM poi WHERE character_id=?;",(charID,))
        cursor.execute("DELETE FROM journal_entry WHERE character_id=?;",(charID,))
        macroIDs = cursor.execute("SELECT id FROM macro WHERE character_id=?;",(charID,))
        for macroID in macroIDs:
            cursor.execute("DELETE FROM macro_line WHERE macro_id=?;",(macroID[0],))
        cursor.execute("DELETE FROM macro WHERE character_id=?;",(charID,))
        cursor.execute("DELETE FROM character WHERE id=?;",(charID,))
    
    
    # This function gets called from init, no need to call anywhere else.
    # Just a separate function for better readability.
    def loadWindowSettings(self):
        cursor = self.cursor
        if self.windowVersion < WINDOW_DAT_VERSION:
            # Maybe would need to drop and recreate table as well...
            #  we'll see once it's necessary.
            print "Stored window data is of old version, deleting and recreating window data."
            cursor.execute("DELETE FROM window;")
            # Insert initial window data into db.
            fillWindow(cursor)
            # Update window version.
            cursor.execute("UPDATE misc SET window_version=?;",(WINDOW_DAT_VERSION,))
        # Check for old storage method.
        filename = "%s/data/settings/windows.dat"%(GAMEROOT)
        if os.path.exists(filename):
            from cPickle import load as pickleLoad
            try:
                f = file(filename,'rb')
                ws = pickleLoad(f)
                f.close()
                if ws['VERSION'] < WINDOW_DAT_VERSION:
                    print "Stored window data is of old version, deleting and recreating window data."
                    # Already created, just pass.
                else:
                    pos = ws['POS']
                    active = ws['ACTIVE']
                    extents = ws.get('EXTENTS')
                    for window,position in pos.iteritems():
                        position = position.split(' ')
                        cursor.execute("UPDATE window SET x_coord=?, y_coord=? WHERE name=?;",(position[0],position[1],window))
                    for window,extent in extents.iteritems():
                        extent = extent.split(' ')
                        cursor.execute("UPDATE window SET x_extent=?, y_extent=? WHERE name=?;",(extent[0],extent[1],window))
                    for window,a in active.iteritems():
                        if a:
                            a = 1
                        else:
                            a = 0
                        cursor.execute("UPDATE window SET active=? WHERE name=?;",(a,window))
            except:
                # An error occurred, just pass and use default.
                traceback.print_exc()
            # Don't forget to remove old windows.dat.
            os.remove(filename)
        windowSettings = cursor.execute("SELECT * FROM window;")
        
        # Check window data.
        self.windows = {}
        resolution = TGECall("getRes").split(" ")
        screenWidth,screenHeight = int(resolution[0]),int(resolution[1])
        for id,name,x_coord,y_coord,x_extent,y_extent,active in windowSettings:
            # Get the window object if available.
            try:
                window = TGEObject(name)
            except:
                continue
            
            # Window found, so enter into window dict.
            resizable = x_extent != -1 and y_extent != -1
            self.windows[name] = (window,active,resizable)
            
            # Adjust position and size to current resolution.
            if not resizable:
                width,height = window.extent.split(' ')
                x_extent = int(width)
                y_extent = int(height)
            if x_extent > screenWidth:
                x_extent = screenWidth
            if y_extent > screenHeight:
                y_extent = screenHeight
            if x_coord + x_extent > screenWidth + 5 or y_coord + y_extent > screenHeight + 5:
                initial = WINDOW_INITIAL[name]
                x_coord = initial[0]
                y_coord = initial[1]
            
            # Set size and position.
            window.resize(x_coord,y_coord,x_extent,y_extent)
            
            # Set active if necessary.
            if active == 1:
                TGEEval("canvas.pushDialog(%s);"%name[:-7])
    
    
    # Call this function on logout to store window settings.
    def storeWindowSettings(self):
        for name,windowInfo in self.windows.iteritems():
            window,active,resizable = windowInfo
            posX,posY = window.position.split(' ')
            x_coord = int(posX)
            y_coord = int(posY)
            if resizable:
                width,height = window.extent.split(' ')
                x_extent = int(width)
                y_extent = int(height)
            else:
                x_extent = y_extent = -1
            if active > -1:
                if int(window.isAwake()):
                    active = 1
                else:
                    active = 0
        
            self.cursor.execute("UPDATE window SET x_coord=?, y_coord=?, x_extent=?, y_extent=?, active=? WHERE name=?;",(x_coord,y_coord,x_extent,y_extent,active,name))
    
    
    # Called from tge when setting new screen mode.
    def checkWindowPositions(self):
        resolution = TGECall("getRes").split(" ")
        screenWidth,screenHeight = int(resolution[0]),int(resolution[1])
        for name,windowInfo in self.windows.iteritems():
            window,active,resizable = windowInfo
            posX,posY = window.position.split(' ')
            x_coord = int(posX)
            y_coord = int(posY)
            width,height = window.extent.split(' ')
            x_extent = int(width)
            y_extent = int(height)
            # Adjust position to current screen resolution.
            if x_coord + x_extent > screenWidth + 5 or y_coord + y_extent > screenHeight + 5:
                initial = WINDOW_INITIAL[name]
                window.position = ' '.join((initial[0],initial[1]))
    
    
    # Call this function to load the last party for the set realm.
    # If realm supplied is none, will query last realm.
    # Returns a tuple of the realm and a tuple with the respective
    #  character names.
    def loadLastParty(self,getRealm=None):
        cursor = self.cursor
        
        # Update world information.
        self.updateWorld()
        
        # Check for old storage method.
        wdirname = newMD5(self.worldname).hexdigest()
        single = int(TGEGetGlobal("$Py::ISSINGLEPLAYER"))
        if single:
            gdirname = "single"
        else:
            gdirname = "multiplayer"
        filename = "%s/data/settings/%s/%s/lastparty.dat"%(GAMEROOT,gdirname,wdirname)
        if os.path.exists(filename):
            try:
                from cPickle import load as pickleLoad
                f = file(filename,'rb')
                data = pickleLoad(f)
                f.close()
                lastParty = data["PARTY"]
                realm = RPG_REALM_LIGHT
                if data["DARKNESS"]:
                    realm = RPG_REALM_DARKNESS
                elif data["MONSTER"]:
                    realm = RPG_REALM_MONSTER
                # Insert recovered last realm information into database.
                cursor.execute("UPDATE misc SET last_realm=?;",(realm,))
                self.lastRealm = realm
                # Insert recovered character information into database or update.
                for name in lastParty:
                    charID = cursor.execute("SELECT id FROM character WHERE world_id=? AND (realm=? OR realm isnull) AND name=? LIMIT 1;",(self.worldID,realm,name)).fetchone()
                    if charID == None:
                        cursor.execute("INSERT INTO character (name,world_id,realm,last_party) VALUES(?,?,?,?);",(name,self.worldID,realm,realm))
                    else:
                        cursor.execute("UPDATE character SET realm=?, last_party=? WHERE id=?;",(realm,realm,charID[0]))
            except:
                # An error occurred, continue without recovery.
                traceback.print_exc()
            # Don't forget to remove old lastparty.dat.
            os.remove(filename)
        # Get last realm if required.
        if getRealm == None:
            getRealm = self.lastRealm
        # Load last party from database. Last realm has already been loaded.
        lastParty = cursor.execute("SELECT name FROM character WHERE world_id=? AND (realm=? OR realm isnull) AND last_party=?;",(self.worldID,getRealm,getRealm))
        lastParty = (member[0] for member in lastParty)
        return (getRealm,lastParty)
    
    
    # This function gets called from init, no need to call anywhere else.
    # Just a separate function for better readability.
    def loadFriends(self):
        cursor = self.cursor
        # Check for old storage method.
        filename = "%s/data/settings/friends.dat"%(GAMEROOT)
        if os.path.exists(filename):
            from cPickle import load as pickleLoad
            try:
                f = file(filename,'rb')
                friends = pickleLoad(f)
                f.close()
                for friend in friends:
                    cursor.execute("INSERT INTO friend (name) VALUES(?);",(friend,))
            except:
                # An error occurred, continue without recovery.
                traceback.print_exc()
            # Don't forget to remove old friends.dat.
            os.remove(filename)
        # Load friends list from database.
        friends = cursor.execute("SELECT name FROM friend;")
        self.friends = list(friend[0] for friend in friends)
    
    
    def addFriend(self,friend):
        friend = friend.upper()
        if friend not in self.friends:
            self.cursor.execute("INSERT INTO friend (name) VALUES(?);",(friend,))
            self.friends.append(friend)
            self.friends.sort()
            return True
        else:
            return False
    
    
    def removeFriend(self,friend):
        friend = friend.upper()
        if friend in self.friends:
            self.cursor.execute("DELETE FROM friend WHERE name=?;",(friend,))
            self.friends.remove(friend)
            return True
        else:
            return False
    
    
    # This function gets called from init, no need to call anywhere else.
    # Just a separate function for better readability.
    def loadIgnored(self):
        cursor = self.cursor
        # Check for old storage method.
        filename = "%s/data/settings/ignore.dat"%(GAMEROOT)
        if os.path.exists(filename):
            from cPickle import load as pickleLoad
            try:
                f = file(filename,'rb')
                ignored = pickleLoad(f)
                f.close()
                for ignore in ignored:
                    cursor.execute("INSERT INTO ignore (name) VALUES(?);",(ignore,))
            except:
                # An error occurred, continue without recovery.
                traceback.print_exc()
            # Don't forget to remove old ignore.dat.
            os.remove(filename)
        # Load ignore list from database.
        ignored = cursor.execute("SELECT name FROM ignore;")
        self.ignored = list(ignore[0] for ignore in ignored)
    
    
    def ignore(self,nick):
        nick = nick.replace("_"," ").upper()
        if nick not in self.ignored:
            self.cursor.execute("INSERT INTO ignore (name) VALUES(?);",(nick,))
            self.ignored.append(nick)
            self.ignored.sort()
            return True
        else:
            return False
    
    
    def unignore(self,nick):
        nick = nick.replace("_"," ").upper()
        if nick in self.ignored:
            self.cursor.execute("DELETE FROM ignore WHERE name=?;",(nick,))
            self.ignored.remove(nick)
            return True
        else:
            return False
    
    
    # This function gets called every time the main character
    #  or the local zone changes.
    def loadPOI(self):
        poi = self.cursor.execute("SELECT description,x_coord,y_coord,z_coord FROM poi WHERE zone=? AND character_id=?;",(self.zone,self.characterID))
        if poi:
            self.poi = dict((description,(x_coord,y_coord,z_coord)) for description,x_coord,y_coord,z_coord in poi)
        else:
            self.poi = dict()
        if POI.has_key(self.zone):
            self.poi.update(POI[self.zone])
    
    
    def addPOI(self,desc,loc,zoneName=None):
        if zoneName == None:
            zoneName = self.zone
        if len(desc) > 35:
            TomeGui.receiveGameText(RPG_MSG_GAME_DENIED,"For your own good, don't describe points of interest with more than 35 characters.\\n")
        else:
            self.poi[desc] = loc
            self.cursor.execute("INSERT INTO poi (zone,description,x_coord,y_coord,z_coord,character_id) VALUES(?,?,?,?,?,?);",(zoneName,desc,loc[0],loc[1],loc[2],self.characterID))
    
    
    def removePOI(self,desc,zoneName=None):
        if zoneName == None:
            zoneName = self.zone
        if not self.poi.has_key(desc):
            TomeGui.receiveGameText(RPG_MSG_GAME_DENIED,"Point of interest of name %s could not be found.\\n"%desc)
        else:
            del self.poi[desc]
            self.cursor.execute("DELETE FROM poi WHERE zone=? AND description=? AND character_id=?;",(zoneName,desc,self.characterID))
    
    
    # Call this function if a channel gets toggled. Provide channel index
    #  as per the dictionary in playermind.py.
    def setChannel(self,channel,on):
        if on:
            newFilters = self.channelFilters & ~channel
        else:
            newFilters = self.channelFilters | channel
        # If this is a new channel setting, write back to database.
        if newFilters != self.channelFilters:
            self.channelFilters = newFilters
            self.cursor.execute("UPDATE misc SET channel_filters=?;",(newFilters,))
    
    
    # This function gets called automatically from within this class if currently
    #  active character changes in any way.
    def updateJournal(self):
        cursor = self.cursor
        
        # Need to update world information first, because this function may
        #  be called if only the character index changes.
        self.updateWorld()
        
        # Check for old storage method.
        loadOld = False
        wdirname = newMD5(self.worldname).hexdigest()
        single = int(TGEGetGlobal("$Py::ISSINGLEPLAYER"))
        if single:
            gdirname = "single"
        else:
            gdirname = "multiplayer"
        
        # Old storage method number one: journals by character.
        dirname = "%s/data/settings/%s/%s"%(GAMEROOT,gdirname,wdirname)
        filename = "%s/%s_journal.dat"%(dirname,self.charInfos[self.charIndex].NAME)
        if os.path.exists(filename):
            loadOld = True
        # Even older storage method number two: journals by realm.
        else:
            if self.lastRealm == RPG_REALM_LIGHT:
                filename = "%s/journal.dat"%dirname
            elif self.lastRealm == RPG_REALM_DARKNESS:
                filename = "%s/journal_dark.dat"%dirname
            else:
                filename = "%s/journal_monster.dat"%dirname
            if os.path.exists(filename):
                print "Could not find character specific journal, copying from old file ..."
                loadOld = True
        
        # If we got some legacy to load, finally do so.
        if loadOld == True:
            from cPickle import load as pickleLoad
            try:
                f = file(filename,'rb')
                journal = pickleLoad(f)
                f.close()
                for topic,entryDict in journal.iteritems():
                    for entry,text in entryDict.iteritems():
                        cursor.execute("INSERT INTO journal_entry (topic,entry,text,character_id) VALUES(?,?,?,?);",(topic,entry,text,self.characterID))
                del journal
            except:
                # An error occurred, continue without recovery.
                traceback.print_exc()
            # Don't forget to remove old ..._journal.dat.
            os.remove(filename)
        
        # Load journal from database.
        journal = dict()
        journalData = cursor.execute("SELECT topic,entry,text,hidden FROM journal_entry WHERE character_id=?;",(self.characterID,))
        # Process journal data, build the journal dictionary and
        #  collect information on hidden entries. If at least one
        #  entry isn't hidden, the topic is visible.
        for topic,entry,text,hidden in journalData:
            journal.setdefault(topic,[{},True])[0][entry] = [text,hidden]
            if not hidden:
                journal[topic][1] = False
        
        # If we don't have a valid journal by this point,
        #  create a new one with default entries.
        if len(journal) == 0:
            from journalWnd import CreateDefaultJournal
            journal = CreateDefaultJournal(self.lastRealm)
            # Directly store new journal to database.
            for topic,topicData in journal.iteritems():
                for entry,entryData in topicData[0].iteritems():
                    cursor.execute("INSERT INTO journal_entry (topic,entry,text,character_id,hidden) VALUES(?,?,?,?,?);",(topic,entry,entryData[0],self.characterID,entryData[1]))
        
        self.journal = journal
        
        # Hook journal up to gui.
        from journalWnd import JOURNALWND
        JOURNALWND.setJournal(journal)
    
    
    # Returns a tuple with a boolean if journal actually needed updating
    #  and the journal itself.
    def addJournalEntry(self,topic,entry,text):
        cursor = self.cursor
        
        # Check if the topic is already present in current journal.
        existingTopic = self.journal.get(topic)
        if existingTopic:
            # If the topic is present, check if the same entry already exists.
            existingEntry = existingTopic[0].get(entry)
            if existingEntry:
                # Entry already exists, now check for text content.
                if existingEntry[0] == text:
                    # Exact same entry already exists. Just make it visible if needed.
                    if not existingEntry[1]:
                        # If it is already visible, return with no change.
                        return (False,self.journal)
                else:
                    existingEntry[0] = text
                # Make topic and entry visible if needed.
                existingEntry[1] = False
                existingTopic[1] = False
                # Update database content. Doesn't really matter that text gets written
                #  even if it's already correct. New journal entries don't come often.
                cursor.execute("UPDATE journal_entry SET text=?, hidden=? WHERE topic=? AND entry=? AND character_id=?;",(text,False,topic,entry,self.characterID))
            else:
                # Entry doesn't exist, create one.
                existingTopic[0][entry] = [text,False]
                # Make topic visible if needed.
                existingTopic[1] = False
                cursor.execute("INSERT INTO journal_entry (topic,entry,text,character_id) VALUES(?,?,?,?);",(topic,entry,text,self.characterID))
        else:
            # Topic doesn't exist yet, create and insert into database.
            self.journal[topic] = [{entry:[text,False]},False]
            cursor.execute("INSERT INTO journal_entry (topic,entry,text,character_id) VALUES(?,?,?,?);",(topic,entry,text,self.characterID))
        
        # Journal changed, so return True.
        return (True,self.journal)
    
    
    # Returns a tuple with a boolean if journal actually needed updating
    #  and the journal itself.
    def hideJournalTopic(self,topic,hide=True):
        cursor = self.cursor
        
        # Check if the topic is even present in current journal.
        existingTopic = self.journal.get(topic)
        if not existingTopic or existingTopic[1] == hide:
            return (False,self.journal)
        
        # Update hide flag, in journal and database.
        existingTopic[1] = hide
        cursor.execute("UPDATE journal_entry SET hidden=? WHERE topic=? AND character_id=?;",(hide,topic,self.characterID))
        for entry,entryData in existingTopic[0].iteritems():
            entryData[1] = hide
        
        # Return that there was a change and current journal.
        return (True,self.journal)
    
    
    # Returns a tuple with a boolean if journal actually needed updating
    #  and the journal itself.
    def hideJournalEntry(self,topic,entry,hide=True):
        cursor = self.cursor
        
        # Check if the topic is even present in current journal.
        existingTopic = self.journal.get(topic)
        if not existingTopic or (hide == True and existingTopic[1] == True):
            return (False,self.journal)
        
        # Now check for the specific entry.
        existingEntry = existingTopic[0].get(entry)
        if not existingEntry or existingEntry[1] == hide:
            return (False,self.journal)
        
        # Update hide flag, in journal and database.
        existingEntry[1] = hide
        cursor.execute("UPDATE journal_entry SET hidden=? WHERE topic=? AND entry=? AND character_id=?;",(hide,topic,entry,self.characterID))
        
        # Hide topic if all topic entries are hidden.
        existingTopic[1] = True
        for entry,entryData in existingTopic[0].iteritems():
            if entryData[1] == False:
                existingTopic[1] = False
                break
        
        # Return that there was a change and current journal.
        return (True,self.journal)
    
    
    # Returns a tuple with a boolean if journal actually needed updating
    #  and the journal itself.
    def clearJournalTopic(self,topic):
        cursor = self.cursor
        
        # Check if the topic is even present in current journal.
        existingTopic = self.journal.get(topic)
        if not existingTopic:
            return (False,self.journal)
        
        # Clear all related entries from database.
        cursor.execute("DELETE FROM journal_entry WHERE topic=? AND character_id=?;",(topic,self.characterID))
        
        # Update current journal.
        del self.journal[topic]
        
        # Return that there was a change and current journal.
        return (True,self.journal)
    
    
    # Returns a tuple with a boolean if journal actually needed updating
    #  and the journal itself.
    def clearJournalEntry(self,topic,entry):
        cursor = self.cursor
        
        # Check if the topic is even present in current journal.
        existingTopic = self.journal.get(topic)
        if not existingTopic:
            return (False,self.journal)
        
        # Now check for the specific entry.
        existingEntry = existingTopic[0].get(entry)
        if not existingEntry:
            return (False,self.journal)
        
        # Clear specific journal entry from database.
        cursor.execute("DELETE FROM journal_entry WHERE topic=? AND entry=? AND character_id=?;",(topic,entry,self.characterID))
        
        # Update current journal.
        del existingTopic[0][entry]
        # Clear topic as well if there's no more entry left.
        if len(existingTopic[0]) == 0:
            del self.journal[topic]
        
        # Return that there was a change and current journal.
        return (True,self.journal)
    
    
    # Loads the macros of all active characters. Automatically called if
    #  character constellation changes from within this class.
    def loadMacros(self):
        from macro import Macro,MacroLine,MACROMASTER
        cursor = self.cursor
        
        self.macroCollection = dict()
        
        # Set up paths to check for old storage method.
        wdirname = newMD5(self.worldname).hexdigest()
        single = int(TGEGetGlobal("$Py::ISSINGLEPLAYER"))
        if single:
            gdirname = "single"
        else:
            gdirname = "multiplayer"
        dirname = "%s/data/settings/%s/%s"%(GAMEROOT,gdirname,wdirname)
        # If this flag gets set during recovery of old settings,
        #  character settings got updated and need saving.
        storeCharacterSettings = False
        
        # Iterate over all characters in the party.
        for charIndex,characterID in self.characters.iteritems():
            charInfo = self.charInfos[charIndex]
            # Check for old storage method.
            filename = "%s/%s_macros.dat"%(dirname,charInfo.NAME)
            if os.path.exists(filename):
                from cPickle import load as pickleLoad
                try:
                    f = file(filename,'rb')
                    macroStore = pickleLoad(f)
                    f.close()
                    
                    # Old macro savefile also contained character settings.
                    # Update current settings and set flag to update them in database.
                    self.charInfos[charIndex].clientSettings.update(macroStore['CLIENTSETTINGS'])
                    storeCharacterSettings = True
                    del macroStore['CLIENTSETTINGS']
                    
                    # Now extract the old macros.
                    for macroIndex,macroData in macroStore.iteritems():
                        # Translate macro index to page and slot number.
                        page = macroIndex / 10
                        slot = macroIndex % 10
                        name = ""
                        hotkey = str((slot + 1) % 10)
                        icon = ""
                        description = ""
                        # This list of macro lines holds tuples of the actual lines plus the delay.
                        macroLines = list()
                        # Gather rest of macro data.
                        for attr,value in macroData.iteritems():
                            if attr == 'hotKey':
                                hotkey = value
                            # Default command, we'll turn that one into a standard macro line.
                            elif attr == 'defaultCommand':
                                if value:
                                    defaultCommand = GetDefaultCommand(value.name)
                                    name = defaultCommand.name
                                    icon = defaultCommand.icon
                                    if icon and not icon.startswith('SPELLICON_'):
                                        icon = 'icons/%s'%icon
                                    description = defaultCommand.tooltip
                                    macroLines.append((defaultCommand.command,0))
                            elif attr == 'skill':
                                if value:
                                    skillInfo = GetSkillInfo(value)
                                    name = skillInfo.name
                                    icon = skillInfo.icon
                                    if icon and not icon.startswith('SPELLICON_'):
                                        icon = 'icons/%s'%icon
                                    description = name
                                    macroLines.append(('/skill %s'%skillInfo.name,0))
                            elif attr == 'spellSlot':
                                if value != None:
                                    spell = charInfo.SPELLS.get(value)
                                    if spell:
                                        spellInfo = spell.SPELLINFO
                                        name = spellInfo.NAME
                                        icon = spellInfo.SPELLBOOKPIC
                                        if icon and not icon.startswith('SPELLICON_'):
                                            icon = 'spellicons/%s'%icon
                                        description = name
                                        macroLines.append(('/cast %s'%spellInfo.BASENAME,0))
                            elif attr == 'customMacro':
                                if value:
                                    name = value['name']
                                    icon = value['icon']
                                    if icon and not icon.startswith('SPELLICON_'):
                                        icon = 'icons/%s'%icon
                                    description = name
                                    for command,delay in zip(value['lines'].itervalues(),value['delays'].itervalues()):
                                        macroLines.append((command,delay))
                            # Other possible attributes are either unused, not important
                            #  or simply outdated beyond usability.
                        
                        # Ok, data gathered, insert into database.
                        cursor.execute("INSERT INTO macro (name,page,slot,hotkey,icon,description,character_id) VALUES(?,?,?,?,?,?,?);",(name,page,slot,hotkey,icon,description,characterID))
                        macroID = cursor.execute("SELECT id FROM macro WHERE character_id=? AND page=? AND slot=? LIMIT 1;",(characterID,page,slot)).fetchone()[0]
                        for lineIndex,macroLine in enumerate(macroLines):
                            cursor.execute("INSERT INTO macro_line (line_index,command,delay_after,macro_id) VALUES(?,?,?,?);",(lineIndex,macroLine[0].lstrip().rstrip(),macroLine[1],macroID))
                    
                    # Dispose of this chunk.
                    del macroStore
                except:
                    # An error occurred, continue without recovery.
                    traceback.print_exc()
                # Don't forget to remove old ..._macros.dat.
                os.remove(filename)
            
            # Load character macros from database.
            characterMacros = dict()
            characterMacroData = cursor.execute("SELECT * FROM macro WHERE character_id=?;",(characterID,)).fetchall()
            for macroData in characterMacroData:
                newMacro = Macro(charIndex,macroData[2],macroData[3])
                newMacro.name = macroData[1]
                newMacro.hotkey = macroData[4]
                newMacro.icon = macroData[5]
                newMacro.description = macroData[6]
                newMacro.waitAll = macroData[7]
                newMacro.manualDelay = macroData[8]
                
                macroLines = cursor.execute("SELECT line_index,command,mandatory,delay_after FROM macro_line WHERE macro_id=?;",(macroData[0],)).fetchall()
                for lineIndex,command,mandatory,delayAfter in macroLines:
                    newLine = MacroLine(command,mandatory,delayAfter)
                    newMacro.insertMacroLine(lineIndex,newLine)
                
                # If there was an error at some point and we got this macro
                #  slot doubly occupied, remove the already existing entry.
                if characterMacros.has_key((macroData[2],macroData[3])):
                    oldMacroID = cursor.execute("SELECT id FROM macro WHERE character_id=? AND page=? AND slot=? LIMIT 1;",(characterID,macroData[2],macroData[3])).fetchone()[0]
                    cursor.execute("DELETE FROM macro_line WHERE macro_id=?;",(oldMacroID,))
                    cursor.execute("DELETE FROM macro WHERE id=?;",(oldMacroID,))
                    # If we just deleted the currently processed entry, continue.
                    if oldMacroID == macroData[0]:
                        continue
                
                # Insert new macro into character macro dictionary.
                characterMacros[(macroData[2],macroData[3])] = newMacro
            
            # If there were no macros to be found in the database,
            #  create a set of new default ones.
            if len(characterMacros) == 0:
                characterMacros = CreateDefaultMacros(charIndex,charInfo.PCLASS)
                # Of course these new macros need to be saved to database.
                for macro in characterMacros.itervalues():
                    cursor.execute("INSERT INTO macro (name,page,slot,hotkey,icon,description,character_id) VALUES(?,?,?,?,?,?,?);",(macro.name,macro.page,macro.slot,macro.hotkey,macro.icon,macro.description,characterID))
                    macroID = cursor.execute("SELECT id FROM macro WHERE character_id=? AND page=? AND slot=? LIMIT 1;",(characterID,macro.page,macro.slot)).fetchone()[0]
                    for lineIndex,macroLine in macro.macroLines.iteritems():
                        cursor.execute("INSERT INTO macro_line (line_index,command,delay_after,macro_id) VALUES(?,?,?,?);",(lineIndex,macroLine.command,macroLine.delayAfter,macroID))
            
            # Finally all the macros for one character are loaded.
            self.macroCollection[charIndex] = characterMacros
        
        # If character settings got updated, update them now in database.
        if storeCharacterSettings:
            self.storeCharacterSettings()
        
        # Finished loading macros, hook them up to the macro master.
        MACROMASTER.installMacroCollection(self.macroCollection)
    
    
    # Call this function to save a specific macro to database.
    # Set prevMacro to True if there already exists a macro at the same location.
    # Internal macro collection won't be updated by calling this function.
    # This function should only be called by the macro master.
    def saveMacro(self,macro,prevMacro=False):
        cursor = self.cursor
        characterID = self.characters[macro.charIndex]
        
        # If there already exists a macro at the desired location,
        #  it's easiest to just delete it instead of updating.
        if prevMacro:
            oldMacroID = cursor.execute("SELECT id FROM macro WHERE character_id=? AND page=? AND slot=? LIMIT 1;",(characterID,macro.page,macro.slot)).fetchone()[0]
            cursor.execute("DELETE FROM macro_line WHERE macro_id=?;",(oldMacroID,))
            cursor.execute("DELETE FROM macro WHERE id=?;",(oldMacroID,))
        
        # Now insert the new macro into database.
        cursor.execute("INSERT INTO macro VALUES(?,?,?,?,?,?,?,?,?,?);",(None,macro.name,macro.page,macro.slot,macro.hotkey,macro.icon,macro.description,macro.waitAll,macro.manualDelay,characterID))
        macroID = cursor.execute("SELECT id FROM macro WHERE character_id=? AND page=? AND slot=? LIMIT 1;",(characterID,macro.page,macro.slot)).fetchone()[0]
        for lineIndex,macroLine in macro.macroLines.iteritems():
            cursor.execute("INSERT INTO macro_line VALUES(?,?,?,?,?,?);",(None,lineIndex,macroLine.command,macroLine.mandatory,macroLine.delayAfter,macroID))
    
    
    # Call this function to delete a specific macro entry in the database.
    # As for the function above, this one should only be called by the macro master
    #  as it doesn't update the macro collection.
    def deleteMacro(self,charIndex,page,slot):
        cursor = self.cursor
        characterID = self.characters[charIndex]
        oldMacroID = cursor.execute("SELECT id FROM macro WHERE character_id=? AND page=? AND slot=? LIMIT 1;",(characterID,page,slot)).fetchone()
        if oldMacroID:
            oldMacroID = oldMacroID[0]
            cursor.execute("DELETE FROM macro_line WHERE macro_id=?;",(oldMacroID,))
            cursor.execute("DELETE FROM macro WHERE id=?;",(oldMacroID,))
    
    
    def toggleExtendedMacros(self, args):
        enabled = int(args[1])
        
        if self.useExtendedMacros != enabled:
            self.useExtendedMacros = enabled
            from macro import MACROMASTER
            MACROMASTER.extendedMacros = enabled
            self.cursor.execute("UPDATE misc SET extended_macros=?;",(enabled,))



PLAYERSETTINGS = PlayerSettings()

TGEExport(PLAYERSETTINGS.checkWindowPositions,"Py","CheckWindowPositions","desc",1,1)
TGEExport(PLAYERSETTINGS.toggleExtendedMacros,"Py","ToggleExtendedMacros","desc",2,2)

