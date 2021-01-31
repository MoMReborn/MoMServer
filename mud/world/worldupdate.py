# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from genesistime import GENESISTIME
import sys, os, traceback, imp
from datetime import datetime
import re
import shutil

from sqlobject import *
from sqlite3 import dbapi2 as sqlite

from mud.common.dbconfig import SetDBConnection
from mud.common.permission import User, Role
from mud.common.persistent import Persistent

from mud.world.defines import *

from mud.world.player import Player, PlayerXPCredit, PlayerMonsterSpawn
from mud.world.zone import Zone
from mud.world.character import Character, CharacterSpell, CharacterSkill, CharacterAdvancement, CharacterDialogChoice, CharacterVaultItem, CharacterFaction
from mud.world.spawn import Spawn, SpawnResistance, SpawnStat
from mud.world.spell import SpellProto, SpellStore
from mud.world.advancement import AdvancementProto
from mud.world.faction import Faction
from mud.world.item import Item, ItemProto, ItemSpell, ItemContainerContent
from mud.world.itemvariants import ItemVariant

try:
    from tgenative import *
    from mud.tgepython.console import TGEExport
except:
    pass



WSCHEMA = {}
TABLES = ["Player", "PlayerXPCredit", "PlayerMonsterSpawn", "PlayerIgnore",
    "Character", "CharacterSpell", "CharacterSkill", "CharacterAdvancement", "CharacterDialogChoice", "CharacterVaultItem", "CharacterFaction",
    "Item", "ItemVariant", "ItemContainerContent",
    "Spawn", "SpawnResistance", "SpawnStat",
    "User","Role",
    "SpellStore"
]

FROMGAME = False
FORCE = False



def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze


def CheckWorld(worldPath,baselinePath):
    global WCONN
    global BCONN
    
    # Genesis Time
    gdate,gtime = GENESISTIME.split(" ")
    gyear,gmonth,gday = gdate.split("-")
    ghour,gminute,gsecond = gtime.split(":")
    gyear = int(gyear)
    gmonth = int(gmonth)
    gday = int(gday)
    ghour = int(ghour)
    gminute = int(gminute)
    gsecond = int(gsecond)
    
    WCONN = sqlite.connect(worldPath)
    wcur = WCONN.cursor()
    try:
        wcur.execute('select genesis_time from World where name = "TheWorld" LIMIT 1;')
        
        # World Time
        wdate,wtime = wcur.fetchone()[0].split(" ")
        wyear,wmonth,wday = wdate.split("-")
        whour,wminute,wsecond = wtime.split(":")
        wyear = int(wyear)
        wmonth = int(wmonth)
        wday = int(wday)
        whour = int(whour)
        wminute = int(wminute)
        wsecond = int(wsecond)
    except:
        wyear = wmonth = wday = whour = wminute = wsecond = 1
    
    # Baseline World Time
    BCONN = sqlite.connect(baselinePath)
    bcur = BCONN.cursor()
    
    bcur.execute('select genesis_time from World where name = "TheWorld" LIMIT 1;')
    
    # World Time
    bdate,btime = bcur.fetchone()[0].split(" ")
    byear,bmonth,bday = bdate.split("-")
    bhour,bminute,bsecond = btime.split(":")
    byear = int(byear)
    bmonth = int(bmonth)
    bday = int(bday)
    bhour = int(bhour)
    bminute = int(bminute)
    bsecond = int(bsecond)
    
    bcur.close()
    wcur.close()
    BCONN.close()
    BCONN = None
    WCONN.close()
    WCONN = None
    
    wdatetime = datetime(wyear,wmonth,wday,whour,wminute,wsecond)
    gdatetime = datetime(gyear,gmonth,gday,ghour,gminute,gsecond)
    bdatetime = datetime(byear,bmonth,bday,bhour,bminute,bsecond)
    
    #We can add this if we want
    #if main_is_frozen():
    #    if gdatetime != bdatetime:
    #        if FROMGAME:
    #            TGEEval('canvas.setContent("MainMenuGui");')
    #            TGECall("MessageBoxOK","Error updating world!","Genesis Time does not match Baseline Time!")        
    #            return -1
    
    if wdatetime < bdatetime or FORCE:
        # We need to updade
        return 1
    
    return 0


# Function to filter columns that no longer exist
#  or shouldn't be copied over into the new database.
def FilterColumns(klass,dbAttr):
    del dbAttr["id"]
    for col,value in dbAttr.items():
        found = False
        for ncol in klass.sqlmeta._columns:
            if col == ncol.name:
                if ncol._sqliteType() == "TIMESTAMP":
                    # Convert to datetime
                    date,time = value.split(" ")
                    year,month,day = date.split("-")
                    hour,minute,second = time.split(":")
                    year = int(year)
                    month = int(month)
                    day = int(day)
                    hour = int(hour)
                    minute = int(minute)
                    second = int(second)
                    dbAttr[col] = datetime(year,month,day,hour,minute,second)
                found = True
                break
        if not found:
            del dbAttr[col]



# Class to copy container content information.
class ItemContainerContentCopier:
    # Save data on this container content.
    def __init__(self, cur, id):
        self.dbAttr = {}
        cur.execute("SELECT * from item_container_content WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["ItemContainerContent"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        contentID = self.dbAttr.get('contentID',-1)
        if contentID == -1:
            self.content = None
        else:
            self.content = ItemCopier(cur,contentID)
    
    
    # Restore data on this container content.
    def install(self, item):
        if not self.content:
            return
        FilterColumns(ItemContainerContent,self.dbAttr)
        container = self.content.install(None)
        if container:
            self.dbAttr['contentID'] = container.id
            self.dbAttr['itemID'] = item.id
            ItemContainerContent(**self.dbAttr)



# Class to copy item variant information.
class ItemVariantCopier:
    # Save data on this item variant.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from item_variant WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["ItemVariant"],cur.fetchone()):
            self.dbAttr[str(name)] = value
    
    
    # Restore data on this item variant.
    def install(self,item):
        FilterColumns(ItemVariant,self.dbAttr)
        self.dbAttr["itemID"] = item.id
        ItemVariant(**self.dbAttr)



# Class to copy item information.
class ItemCopier:
    # Save data on this item.
    def __init__(self,cur,itemID,bank=False):
        self.dbAttr = {}
        cur.execute("SELECT * from item WHERE id=? LIMIT 1;",(itemID,))
        for name,value in zip(WSCHEMA["Item"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        protoID = self.dbAttr.get('itemProtoID',-1)
        cur.execute("select name from item_proto where id=? LIMIT 1;",(protoID,))
        self.protoName = cur.fetchone()[0]
        
        variants = self.variants = []
        cur.execute("select id from item_variant where item_id=?;",(itemID,))
        for r in cur.fetchall():
            f = ItemVariantCopier(cur,r[0])
            variants.append(f)
        
        content = self.content = []
        try:
            cur.execute("SELECT id FROM item_container_content WHERE item_id=?;",(itemID,))
            for cc in cur.fetchall():
                c = ItemContainerContentCopier(cur,cc[0])
                content.append(c)
        # Exception occurs if database to be updated doesn't know yet of the
        #  introduction of item containers.
        except:
            pass
    
    
    # Restore data on this item.
    def install(self,owner,bank=False):
        try:
            ip = ItemProto.byName(self.protoName)
        except:
            print "Item: %s no longer exists"%self.protoName
            return None
        
        FilterColumns(Item,self.dbAttr)
        self.dbAttr["itemProtoID"] = ip.id
        if owner:
            # Bank items need a player assigned and no
            #  character. Otherwise, item would show up
            #  in character inventory list which could
            #  screw up things.
            if bank:
                self.dbAttr["characterID"] = None
                self.dbAttr["playerID"] = owner.id
            # Inventory items will require the player set
            #  to None or they will show up in bank list
            #  which could screw up things. They might
            #  get deleted!
            else:
                self.dbAttr["characterID"] = owner.id
                self.dbAttr["playerID"] = None
        # No owner means this is a vault item.
        # Owner is set on CharacterVaultItem, not here.
        # Otherwise, this item would appear in characters
        #  item list, which could screw up things.
        else:
            self.dbAttr["characterID"] = None
            self.dbAttr["playerID"] = None
        if not self.dbAttr["stackCount"]:
            if ip.stackMax > 1:
                self.dbAttr["stackCount"] = ip.stackDefault
            else:
                self.dbAttr["stackCount"] = 1
        item = Item(**self.dbAttr)
        
        for iv in self.variants:
            iv.install(item)
        
        for cc in self.content:
            cc.install(item)
        
        return item



# Class to copy character faction standings.
class CharacterFactionCopier:
    # Save data on this character faction.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from character_faction WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["CharacterFaction"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        cur.execute("select name from faction where id = %i LIMIT 1;"%self.dbAttr["factionID"])
        self.factionName = cur.fetchone()[0]
    
    
    # Restore data on this character faction.
    def install(self,char):
        try:
            f = Faction.byName(self.factionName)
        except:
            print "Faction: %s no longer exists"%self.factionName
            return
        FilterColumns(CharacterFaction,self.dbAttr)
        self.dbAttr["characterID"] = char.id
        self.dbAttr["factionID"] = f.id
        CharacterFaction(**self.dbAttr)



# Class to copy monster spawn information.
class PlayerMonsterSpawnCopier:
    # Save data on this monster spawn.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from player_monster_spawn WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["PlayerMonsterSpawn"],cur.fetchone()):
            self.dbAttr[str(name)] = value
    
    
    # Restore data on this monster spawn.
    def install(self,player):
        FilterColumns(PlayerMonsterSpawn,self.dbAttr)
        self.dbAttr["playerID"] = player.id
        PlayerMonsterSpawn(**self.dbAttr)



# Class to copy character advancement information.
class CharacterAdvancementCopier:
    # Save data on this character advancement.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from character_advancement WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["CharacterAdvancement"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        protoID = self.dbAttr.get('advancementProtoID',-1)
        cur.execute("select name from advancement_proto where id = %i LIMIT 1;"%protoID)
        self.protoName = cur.fetchone()[0]
    
    
    # Restore data on this character advancement.
    def install(self,char):
        try:
            adv = AdvancementProto.byName(self.protoName)
        except:
            print "Advancement: %s no longer exists"%self.protoName
            return
        
        FilterColumns(CharacterAdvancement,self.dbAttr)
        self.dbAttr["advancementProtoID"] = adv.id
        self.dbAttr["characterID"] = char.id
        CharacterAdvancement(**self.dbAttr)



# Class to copy vault item information.
class CharacterVaultItemCopier:
    # Save data on this vault item.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from character_vault_item WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["CharacterVaultItem"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        self.item = ItemCopier(cur,self.dbAttr["itemID"])
    
    
    # Restore data on this vault item.
    def install(self,char):
        FilterColumns(CharacterVaultItem,self.dbAttr)
        self.dbAttr["characterID"] = char.id
        item = self.item.install(None)
        # Item proto no longer exists, need to delete this.
        if not item:
            return
        self.dbAttr["itemID"] = item.id
        CharacterVaultItem(**self.dbAttr)



# Class to copy character skill information.
class CharacterSkillCopier:
    # Save data on this character skill.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from character_skill WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["CharacterSkill"],cur.fetchone()):
            self.dbAttr[str(name)] = value
    
    
    # Restore data on this character skill.
    def install(self,char):
        FilterColumns(CharacterSkill,self.dbAttr)
        self.dbAttr["characterID"] = char.id
        CharacterSkill(**self.dbAttr)



# Class to copy information on character dialog choices, aka quests.
class CharacterDialogChoiceCopier:
    # Save data on this character dialog choice.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from character_dialog_choice WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["CharacterDialogChoice"],cur.fetchone()):
            self.dbAttr[str(name)] = value
    
    
    # Restore data on this character dialog choice.
    def install(self,char):
        FilterColumns(CharacterDialogChoice,self.dbAttr)
        self.dbAttr["characterID"] = char.id
        CharacterDialogChoice(**self.dbAttr)



# Class to copy character spell information.
class CharacterSpellCopier:
    # Save data on this character spell.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from character_spell WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["CharacterSpell"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        protoID = self.dbAttr.get('spellProtoID',-1)
        cur.execute("select name from spell_proto where id = %i LIMIT 1;"%protoID)
        self.protoName = cur.fetchone()[0]
    
    
    # Restore data on this character spell.
    def install(self,char):
        try:
            sp = SpellProto.byName(self.protoName)
        except:
            print "Spell: %s no longer exists"%self.protoName
            return
        
        FilterColumns(CharacterSpell,self.dbAttr)
        self.dbAttr["spellProtoID"] = sp.id
        self.dbAttr["characterID"] = char.id
        CharacterSpell(**self.dbAttr)



# Class to copy active spells on character.
class SpellStoreCopier:
    # Save data on this stored spell.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from spell_store WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["SpellStore"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        protoID = self.dbAttr.get('spellProtoID',-1)
        cur.execute("select name from spell_proto where id = %i LIMIT 1;"%protoID)
        self.protoName = cur.fetchone()[0]
    
    
    # Restore data on this stored spell.
    def install(self,char):
        try:
            sp = SpellProto.byName(self.protoName)
        except:
            print "Spell: %s no longer exists"%self.protoName
            return
        
        FilterColumns(SpellStore,self.dbAttr)
        self.dbAttr["spellProtoID"] = sp.id
        self.dbAttr["characterID"] = char.id
        SpellStore(**self.dbAttr)



# Class to copy spawn stat information.
class SpawnStatCopier:
    # Save data on this spawn stat.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from spawn_stat WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["SpawnStat"],cur.fetchone()):
            self.dbAttr[str(name)] = value
    
    
    # Restore data on this spawn stat.
    def install(self,spawn):
        FilterColumns(SpawnStat,self.dbAttr)
        self.dbAttr["spawnID"] = spawn.id
        s = SpawnStat(**self.dbAttr)
        return s



# Class to copy spawn resistance information.
class SpawnResistanceCopier:
    # Save data on this spawn resistance.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from spawn_resistance WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["SpawnResistance"],cur.fetchone()):
            self.dbAttr[str(name)] = value
    
    
    # Restore data on this spawn resistance.
    def install(self,spawn):
        FilterColumns(SpawnResistance,self.dbAttr)
        self.dbAttr["spawnID"] = spawn.id
        s = SpawnResistance(**self.dbAttr)
        return s



# Class to copy spawn information.
class SpawnCopier:
    # Save data on this spawn.
    def __init__(self,cur,id):
        self.dbAttr = {}
        cur.execute("SELECT * from spawn WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["Spawn"],cur.fetchone()):
            self.dbAttr[str(name)] = value
    
    
    # Restore data on this spawn.
    def install(self):
        FilterColumns(Spawn,self.dbAttr)
        try:
            s = Spawn(**self.dbAttr)
        except:
            print "Problem installing %s trying with an appended X to name"%(self.dbAttr["name"])
            self.dbAttr["name"] = self.dbAttr["name"]+"X"
            try:
                s = Spawn(**self.dbAttr)
            except:
                raise "Error"
        return s



# Class to copy character information.
class CharacterCopier:
    # Save data on this character.
    def __init__(self,cur,id):
        self.dbAttr = {}
        
        # Query all direct information on this character.
        cur.execute("SELECT * from character WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["Character"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        # Save this characters spawn.
        spawnID = self.dbAttr.get('spawnID',-1)
        self.spawn = SpawnCopier(cur,spawnID)
        
        # Save this characters spawn resists.
        sresists = self.sresists = []
        cur.execute("select id from spawn_resistance where spawn_id = %i;"%spawnID)
        for r in cur.fetchall():
            f = SpawnResistanceCopier(cur,r[0])
            sresists.append(f)
        
        # Save this characters spawn stats.
        sstats = self.sstats = []
        cur.execute("select id from spawn_stat where spawn_id = %i;"%spawnID)
        for r in cur.fetchall():
            f = SpawnStatCopier(cur,r[0])
            sstats.append(f)
        
        # Save this characters advancements.
        advancements = self.advancements = []
        cur.execute("select id from character_advancement where character_id = %i;"%id)
        for r in cur.fetchall():
            f = CharacterAdvancementCopier(cur,r[0])
            advancements.append(f)
        
        # Save this characters skills.
        skills = self.skills = []
        cur.execute("select id from character_skill where character_id = %i;"%id)
        for r in cur.fetchall():
            f = CharacterSkillCopier(cur,r[0])
            skills.append(f)
        
        # Save this characters spells.
        spells = self.spells = []
        cur.execute("select id from character_spell where character_id = %i;"%id)
        for r in cur.fetchall():
            f = CharacterSpellCopier(cur,r[0])
            spells.append(f)
        
        # Save this characters vault items.
        vaultItems = self.vaultItems = []
        try:
            cur.execute("select id from character_vault_item where character_id = %i;"%id)
            for r in cur.fetchall():
                f = CharacterVaultItemCopier(cur,r[0])
                vaultItems.append(f)
        # Table character_vault_item doesn't exist.
        # Probably an old db from a time before
        #  character vaults got introduced.
        # Give out warning anyway.
        except:
            traceback.print_exc()
        
        # Save this characters faction standings.
        factions = self.factions = []
        try:
            cur.execute("select id from character_faction where character_id = %i;"%id)
            for r in cur.fetchall():
                f = CharacterFactionCopier(cur,r[0])
                factions.append(f)
        # Table character_faction doesn't exist.
        # Give out warning.
        except:
            traceback.print_exc()
        
        # Save this characters items, but only those
        #  that aren't in a bank slot.
        # Bank items get assigned the player, old dbs
        #  may still have character simultaneously assigned.
        # Also omit items that got a slot of -1. Those items
        #  are in fact vault items, which due to a former bug
        #  got the character_id assigned.
        items = self.items = []
        cur.execute("select id from item where character_id = %i and (slot >= %i or slot < %i) and slot != -1;"%(id,RPG_SLOT_BANK_END,RPG_SLOT_BANK_BEGIN))
        for r in cur.fetchall():
            f = ItemCopier(cur,r[0])
            items.append(f)
        
        # Save this characters dialog choices, aka quests.
        dc = self.dc = []
        try:
            cur.execute("select id from character_dialog_choice where character_id = %i;"%id)
            for r in cur.fetchall():
                f = CharacterDialogChoiceCopier(cur,r[0])
                dc.append(f)
        # Warn about missing table character_dialog_choice.
        except:
            traceback.print_exc()
        
        # Save stored spells active on this character.
        spellStore = self.spellStore = []
        try:
            cur.execute("select id from spell_store where character_id = %i;"%id)
            for r in cur.fetchall():
                sps = SpellStoreCopier(cur,r[0])
                spellStore.append(sps)
        # Warn about missing table spell_store.
        except:
            traceback.print_exc()
    
    
    # Restore data on this character.
    def install(self,player):
        spawn = self.spawn.install()
        
        FilterColumns(Character,self.dbAttr)
        self.dbAttr["name"] = spawn.name #may be renamed
        self.dbAttr["spawnID"] = spawn.id
        self.dbAttr["playerID"] = player.id
        char = Character(**self.dbAttr)
        spawn.character = char #version 1.0 didn't have a foreign key to character from spawn
        spawn.playerName = player.publicName
        
        # Restore spawn resists of this character.
        for a in self.sresists:
            a.install(spawn)
        
        # Restore spawn stats of this character.
        for a in self.sstats:
            a.install(spawn)
        
        # Restore advancements of this character.
        for a in self.advancements:
            a.install(char)
        
        # Restore spells of this character.
        for s in self.spells:
            s.install(char)
        
        # Restore skills of this character.
        for s in self.skills:
            s.install(char)
        
        # Restore this characters items.
        for i in self.items:
            i.install(char)
        
        # Restore this characters vault items.
        for i in self.vaultItems:
            i.install(char)
        
        # Restore this characters factions.
        for f in self.factions:
            f.install(char)
        
        # Restore this characters dialog choices.
        for dc in self.dc:
            dc.install(char)
        
        # Restore stored spells active on this character.
        for sps in self.spellStore:
            sps.install(char)



# Class to copy player information.
class PlayerCopier:
    # Save data on this player.
    def __init__(self,conn,id):
        self.dbAttr = {}
        cur = conn.cursor()
        
        # Initialize zone ids to something non-existant.
        # (So can later be checked)
        bindZoneID = -1
        logZoneID = -1
        darknessBindZoneID = -1
        darknessLogZoneID = -1
        monsterBindZoneID = -1
        monsterLogZoneID = -1
        
        # Query all direct information on player.
        cur.execute("SELECT * from player WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["Player"],cur.fetchone()):
            if name == "bindZoneID":
                bindZoneID = value
            elif name == "logZoneID":
                logZoneID = value
            elif name == "darknessBindZoneID":
                darknessBindZoneID = value
            elif name == "darknessLogZoneID":
                darknessLogZoneID = value
            elif name == "monsterBindZoneID":
                monsterBindZoneID = value
            elif name == "monsterLogZoneID":
                monsterLogZoneID = value
            
            self.dbAttr[str(name)] = value
        
        # Find the zone names by their respective ids.
        cur.execute("select name from Zone where id = %i LIMIT 1;"%bindZoneID)
        self.bindZone = cur.fetchone()[0]
        cur.execute("select name from Zone where id = %i LIMIT 1;"%logZoneID)
        self.logZone = cur.fetchone()[0]
        cur.execute("select name from Zone where id = %i LIMIT 1;"%darknessBindZoneID)
        self.darknessBindZone = cur.fetchone()[0]
        cur.execute("select name from Zone where id = %i LIMIT 1;"%darknessLogZoneID)
        self.darknessLogZone = cur.fetchone()[0]
        cur.execute("select name from Zone where id = %i LIMIT 1;"%monsterBindZoneID)
        self.monsterBindZone = cur.fetchone()[0]
        cur.execute("select name from Zone where id = %i LIMIT 1;"%monsterLogZoneID)
        self.monsterLogZone = cur.fetchone()[0]
        
        # Save character data on current player.
        chars = self.characters = []
        cur.execute("select id from Character where player_id = %i;"%id)
        for r in cur.fetchall():
            c = CharacterCopier(cur,r[0])
            chars.append(c)
        
        # Save monster spawn data on current player.
        mspawns = self.mspawns = []
        try:
            cur.execute("select id from player_monster_spawn where player_id = %i;"%id)
            for r in cur.fetchall():
                f = PlayerMonsterSpawnCopier(cur,r[0])
                mspawns.append(f)
        # Monster spawn table doesn't exist, give out warning.
        except:
            traceback.print_exc()
        
        # Save item data on current player.
        # These should be only bank items, so omit anything that has an invalid slot.
        # It is possible that there still exist items in some world databases that
        #  contain items where a player as well as a character are simultaneously assigned.
        items = self.items = []
        cur.execute("select id from item where player_id = %i and slot >= %i and slot < %i;"%(id,RPG_SLOT_BANK_BEGIN,RPG_SLOT_BANK_END))
        for r in cur.fetchall():
            f = ItemCopier(cur,r[0])
            items.append(f)
        
        cur.close()
    
    
    # Restore data on this player.
    def install(self):
        if not FROMGAME:
            print "Installing Player: %s"%self.dbAttr["publicName"]
        
        # Restore log and bind zone data for the three realms.
        try:
            bindZone = Zone.byName(self.bindZone)
            logZone = Zone.byName(self.logZone)
        except:
            bindZone = Zone.byName(self.world.startZone)
            logZone = Zone.byName(self.world.startZone)
            self.dbAttr["bindTransformInternal"] = bindZone.immTransform
            self.dbAttr["logTransformInternal"] = logZone.immTransform
        try:
            darknessBindZone = Zone.byName(self.darknessBindZone)
            darknessLogZone = Zone.byName(self.darknessLogZone)
        except:
            darknessBindZone = Zone.byName(self.world.dstartZone)
            darknessLogZone = Zone.byName(self.world.dstartZone)
            self.dbAttr["darknessBindTransformInternal"] = darknessBindZone.immTransform
            self.dbAttr["darknessLogTransformInternal"] = darknessLogZone.immTransform
        try:
            monsterBindZone = Zone.byName(self.monsterBindZone)
            monsterLogZone = Zone.byName(self.monsterLogZone)
        except:
            monsterBindZone = Zone.byName(self.world.mstartZone)
            monsterLogZone = Zone.byName(self.world.mstartZone)
            self.dbAttr["monsterBindTransformInternal"] = monsterBindZone.immTransform
            self.dbAttr["monsterLogTransformInternal"] = monsterLogZone.immTransform
        #todo, initial monster before live

        self.dbAttr["bindZoneID"]=bindZone.id
        self.dbAttr["logZoneID"]=logZone.id
        self.dbAttr["darknessBindZoneID"]=darknessBindZone.id
        self.dbAttr["darknessLogZoneID"]=darknessLogZone.id
        self.dbAttr["monsterBindZoneID"]=monsterBindZone.id
        self.dbAttr["monsterLogZoneID"]=monsterLogZone.id
        
        FilterColumns(Player,self.dbAttr)
        player = Player(**self.dbAttr)
        
        # Restore character data on this player.
        for c in self.characters:
            c.install(player)
        
        # Restore monster spawn data on this player.
        for f in self.mspawns:
            f.install(player)
        
        # Restore bank items of this player.
        for i in self.items:
            i.install(player,bank=True)



# Class to copy user information.
class UserCopier:
    # Save data on this user.
    def __init__(self,conn,id):
        self.dbAttr = {}
        cur = conn.cursor()
        
        cur.execute("SELECT * from user WHERE id = %i LIMIT 1;"%id)
        for name,value in zip(WSCHEMA["User"],cur.fetchone()):
            self.dbAttr[str(name)] = value
        
        self.roles = []
        cur.execute("select distinct name from role where id in (select role_id from role_user where user_id = %i);"%id)
        for name in cur.fetchall():
            self.roles.append(name[0])
        
        cur.close()
    
    
    # Restore data on this user.
    def install(self):
        if self.dbAttr["name"] == "ZoneServer":
            return
        
        FilterColumns(User,self.dbAttr)
        user = User(**self.dbAttr)
        
        for r in self.roles:
            try:
                role = Role.byName(r)
            except:
                print "Role: %s no longer exists!"%r
                continue
            
            user.addRole(role)



# Function to query the database structure on a given
#  database connection. Returns a dictionary with
#  mixed case elements.
# Database uses underscore names, since it's case-insensitive.
def QuerySchema(wconn):
    for t in TABLES:
        cols = WSCHEMA[t] = []
        for col in wconn.execute('PRAGMA table_info(%s);'%mixedToUnder(t)).fetchall():
            cols.append(str(underToMixed(col[1])))


# Function to update a world database.
# worldPath is the system path to the world to be updated.
# baselinePath is the system path to a world database containing
#  only static data, aka the main database, what you get when you
#  run Genesis.
# fromgame is True if a single player world gets checked for
#  updating, else False.
# force = True can be used to force a world update even though database
#  content would be up-to-date (or seems to be).
def WorldUpdate(worldPath,baselinePath,fromgame=False,force=False):
    global FROMGAME
    global FORCE
    # Save arguments in global variables to be used
    #  on various data copiers.
    FROMGAME = fromgame
    FORCE = force
    
    # Check if the world needs updating.
    # 0 = no update needed, 1 = updated needed, -1 = error.
    try:
        result = CheckWorld(worldPath,baselinePath)
    except:
        traceback.print_exc()
        return -1
    if result != 1:
        return result
    
    # If we get here, we need to update the world.
    try:
        # If the world update has been called from in-game,
        #  which means single-player, tell the user what we're doing.
        if FROMGAME:
            TGECall("MessagePopup","Updating World...","Please wait...")
            TGEEval("Canvas.repaint();")
        
        # Get the database connection of the world to be updated.
        WCONN = sqlite.connect(worldPath)
        
        # Get information on database structure of world-specific data.
        # We need information about users, players, characters and
        #  related content. Not needed is invariable stuff such as
        #  item protos, spell protos, mob spawns and the like.
        QuerySchema(WCONN)
        
        # Save player data.
        players = []
        for r in WCONN.execute("select id from Player;").fetchall():
            pc = PlayerCopier(WCONN,r[0])
            players.append(pc)
        
        # Save user data.
        users = []
        for r in WCONN.execute("select id from user;").fetchall():
            u = UserCopier(WCONN,r[0])
            users.append(u)
        
        # Close the database connection.
        WCONN.close()
        
        # Backup the world database.
        shutil.copyfile(worldPath,"%s.bak"%worldPath)
        
        # Create a new copy of the static world database
        #  which doesn't contain any variable data.
        shutil.copyfile(baselinePath,"%s.new"%worldPath)
        
        # Get a database connection to the new copy
        #  of the static world database.
        DATABASE = "sqlite:///%s.new"%worldPath
        SetDBConnection(DATABASE)
        
        # Start inserting saved user and player data
        #  into new world database.
        conn = Player._connection.getConnection()
        cursor = conn.cursor()
        cursor.execute("BEGIN;")
        
        for u in users:
            u.install()
        
        for p in players:
            p.install()
        
        # Finish transaction and close database connection.
        cursor.execute("END;")
        cursor.close()
        SetDBConnection(None)
        
        # Finally copy the updated database to the
        #  standard path, overwriting previous database.
        shutil.copyfile(worldPath+".new",worldPath)
    # An error occured, luckily we didn't directly write
    #  to the database to be updated.
    except:
        traceback.print_exc()
        return -1
    
    # If the database updated was done from in-game
    #  (single-player), tell the user that we're finished
    #  with updating and will now load the world.
    if FROMGAME:
        TGECall("MessagePopup","Loading World...","Please wait...")
        TGEEval("Canvas.repaint();")
    
    # Return successful.
    return 0


# Function to reformat strings with underscores
#  to strings with mixed case. Every underscore
#  precedes an uppercase letter.
# Database uses underscore names, since it's case-insensitive.
_underToMixedRE = re.compile('_(.)')
def underToMixed(name):
    if name.endswith('_id'):
        return underToMixed(name[:-3] + "ID")
    return _underToMixedRE.sub(lambda m: m.group(1).upper(), name)


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


