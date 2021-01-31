# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

"""
Creating the world... 

We really need to have selective control over the creation process

If we drop and recreate things every time, characters, etc will be nuked which is 
definitely a bugger for testing... also, we need to be able to upgrade player's worlds
and our own worlds 
"""


from mud.gamesettings import *


print "----------------------------------"
print "%s - Genesis - v1.0a"%GAMENAME
print "----------------------------------"
print "Creating world, please wait..."


import imp, os,shutil, sys

WORKSPACE = ""
for arg in sys.argv:
    if arg.startswith("-ideworkspace="):
        WORKSPACE = arg[14:]

if WORKSPACE:
    sys.path.insert(0,"%s/%s"%(os.getcwd(),WORKSPACE))
else:
    sys.path.insert(0,"%s/%s"%(os.getcwd(),GAMEROOT))


def main_is_frozen():
   return (hasattr(sys, "frozen") or # new py2exe
           hasattr(sys, "importers") # old py2exe
           or imp.is_frozen("__main__")) # tools/freeze

def get_main_dir():
   if main_is_frozen():
       return os.path.dirname(sys.executable)
   return os.path.dirname(sys.argv[0])

if main_is_frozen():
    #maindir = get_main_dir()
    
    if sys.platform[:6] == 'darwin':
        #need to go up three folders
        os.chdir("../../../mom")
        maindir = os.getcwd()
    else:
        os.chdir("../common")
        maindir = os.getcwd()
    
    sys.path.append(maindir)


from mud.common.dbconfig import SetDBConnection


#setup the db connection
DATABASEPATH = "%s/data/worlds/multiplayer.baseline"%GAMEROOT
DATABASE = DATABASEPATH+"/world.db"

try:
    shutil.rmtree(DATABASEPATH)
except:
    pass

if not os.path.exists(DATABASEPATH):
    os.makedirs(DATABASEPATH)

SetDBConnection('sqlite:/%s'%DATABASE,True)

from sqlobject import *
from mud.common.persistent import Persistent
conn = Persistent._connection

#conn.getConnection().autoCommit = False
conn.autoCommit = False   
Persistent._connection = transaction = conn.transaction()

from genesis.dbdict import DBDict#must be imported after db connection set

#table import
from mud.world.theworld import World
from mud.world.player import Player,PlayerXPCredit,PlayerMonsterSpawn
from mud.world.character import Character,CharacterSpell,StartingGear,CharacterSkill,CharacterAdvancement,CharacterDialogChoice,CharacterVaultItem,CharacterFaction
from mud.world.zone import Zone,ZoneLink
from mud.world.loot import LootItem,LootProto
from mud.world.dialog import JournalEntry,Dialog,DialogLine,DialogChoice,DialogRequirement,DialogRequireClass,DialogRequireRace,DialogRequireRealm,DialogRequireSkill,DialogRequireItem,DialogAction,DialogTakeItem,DialogGiveItem,DialogCheckItem,DialogFaction,DialogCheckMinFaction,DialogCheckMaxFaction,DialogTrainSkill,DialogCheckSkill
from mud.world.vendor import VendorItem,VendorProto
from mud.world.spawn import Spawn,SpawnSkill,SpawnInfo,SpawnGroup,SpawnGroupController,SpawnGroupControllerInfo,SpawnSoundProfile,SpawnKillFaction,SpawnResistance,SpawnSpell,SpawnStat
from mud.world.item import ItemStat,ItemSlot,ItemRace,ItemRealm,ItemClass,Item,ItemSpell,ItemSet,ItemProto,ItemSoundProfile,ItemSetStat,ItemSetSpell,ItemSetRequirement,ItemSetPower,ItemSetProto,ItemClassifier,ItemContainerContent,ItemContainerProto
from mud.world.itemvariants import ItemVariant
from mud.world.faction import Faction,FactionRelation
from mud.world.effect import EffectProto,EffectStat,EffectPermanentStat,EffectDamage,EffectLeech,EffectDrain,EffectRegen,EffectIllusion
from mud.world.spell import SpellProto,SpellClass,SpellComponent,SpellParticleNode,SpellExclusion,SpellStore
from mud.world.career import ClassProto
from mud.world.crafting import RecipeIngredient,Recipe
from mud.world.skill import ClassSkill,ClassSkillRaceRequirement,ClassSkillQuestRequirement
from mud.world.advancement import AdvancementClass,AdvancementRace,AdvancementStat,AdvancementSkill,AdvancementProto,AdvancementRequirement,AdvancementExclusion
from mud.world.race import RaceGraphic,Race
#battles
from mud.world.battle import BattleGroup,BattleSequence,BattleResult,BattleProto,BattleMustSurvive

def ConfigureRoles():
    #--- User and Role Table creation

    from mud.common.permission import Role,TablePermission,ColumnPermission,User,BannedUser,BannedIP
    from mud.common.avatar import RoleAvatar

    #configure connections
    TABLES = [Role,User,BannedUser,BannedIP,TablePermission,ColumnPermission,RoleAvatar]

    #for now we'll drop and recreate the tables every time
    for t in TABLES:
        t.dropTable(ifExists=True)
        t.createTable()
    
    #immortal
    immortal = Role(name="Immortal")
    RoleAvatar(name="RoleEnumAvatar",role=immortal)
    RoleAvatar(name="DatabaseAvatar",role=immortal)
    RoleAvatar(name="ImmortalAvatar",role=immortal)
    RoleAvatar(name="GuardianAvatar",role=immortal)
    RoleAvatar(name="PlayerAvatar",role=immortal)
    RoleAvatar(name="SimAvatar",role=immortal)
    
    
    #guardian
    guardian = Role(name="Guardian")
    RoleAvatar(name="PlayerAvatar",role=guardian)
    RoleAvatar(name="GuardianAvatar",role=guardian)
    RoleAvatar(name="SimAvatar",role=guardian)
    
    
    newplayer = Role(name="NewPlayer")
    RoleAvatar(name="NewPlayerAvatar",role=newplayer)

    player = Role(name="Player")
    RoleAvatar(name="PlayerAvatar",role=player)
    RoleAvatar(name="SimAvatar",role=player)
    
    #dedicated zone server
    zserver = Role(name="ZoneServer")
    RoleAvatar(name="SimAvatar",role=zserver)
    zuser = User(name="ZoneServer",password="ZoneServer")
    zuser.addRole(zserver)

    query = Role(name="Query")
    RoleAvatar(name="QueryAvatar",role=query)
    
    stats = Role(name="Stats")
    RoleAvatar(name="StatsAvatar",role=stats)
    
def CreateTables():
    tables = [Player,PlayerMonsterSpawn,PlayerXPCredit,Character,CharacterSpell,CharacterAdvancement,CharacterDialogChoice,CharacterVaultItem,CharacterFaction,StartingGear,Zone,ZoneLink,LootItem,LootProto,
    JournalEntry,Dialog,DialogLine,DialogChoice,DialogRequirement,DialogRequireClass,DialogRequireRace,DialogRequireRealm,DialogRequireSkill,DialogRequireItem,DialogAction,DialogTakeItem,DialogGiveItem,DialogCheckItem,DialogFaction,
    DialogCheckMinFaction,DialogCheckMaxFaction,DialogTrainSkill,DialogCheckSkill,
    VendorItem,VendorProto,Spawn,SpawnSkill,SpawnKillFaction,SpawnResistance,SpawnSpell,SpawnStat,SpawnInfo,SpawnGroup,SpawnGroupController,SpawnGroupControllerInfo,SpawnSoundProfile,
    ItemStat,ItemSlot,ItemSpell,ItemRace,ItemRealm,ItemClass,Item,ItemSet,ItemVariant,ItemSetStat,ItemSetSpell,ItemSetRequirement,ItemSetPower,ItemSetProto,ItemClassifier,ItemContainerContent,ItemContainerProto,
    Faction,FactionRelation,EffectProto,EffectStat,EffectPermanentStat,EffectDamage,EffectLeech,EffectDrain,EffectRegen,EffectIllusion,SpellProto,SpellClass,SpellComponent,SpellParticleNode,SpellExclusion,SpellStore,ItemProto,ItemSoundProfile,
    ClassProto,ClassSkill,ClassSkillRaceRequirement,ClassSkillQuestRequirement,CharacterSkill,BattleGroup,BattleSequence,BattleResult,BattleProto,BattleMustSurvive,
    AdvancementClass,AdvancementRace,AdvancementStat,AdvancementSkill,AdvancementProto,AdvancementRequirement,AdvancementExclusion,
    RecipeIngredient,Recipe,Race,RaceGraphic]

    for t in tables:
        t.dropTable(ifExists=True)
        t.createTable()

    

def main():
    import time
    beginTime = time.time()
    ConfigureRoles()
    World.dropTable(ifExists=True)
    World.createTable()
    #create world
    World(name="TheWorld")
    import genesis.world.world
        
    CreateTables()
    
    import genesis.main
    
    DBDict.createRows('SpellProto') #all effects used should be drug in (this is before itemproto, so scrolls are made)
    DBDict.createRows('ItemSetPower')
    DBDict.createRows('ItemSetProto')
    DBDict.createRows('ItemProto')
    DBDict.createRows('ClassSkill') 
    DBDict.createRows('ClassProto') 
    DBDict.createRows('Dialog')
    DBDict.createRows('Spawn')
    DBDict.createRows('SpawnInfo')
    DBDict.createRows('SpawnGroup')
    DBDict.createRows('SpawnGroupController',False)
    DBDict.createRows('Zone')
    DBDict.createRows('FactionRelation')
    DBDict.createRows('Recipe')
    
    #DBDict.createRows('DialogLine') #all used dialog lines should be created automatically
    
    # Get a cursor for the database connection.
    cur = conn.getConnection().cursor()
    
    # Maybe stuff some things into DB to speed up certain
    #  gathering processes on world start here.
    
    # Commit the transaction.
    transaction.commit()
    
    # Clean up the database, make it as small as possible,
    #  optimize for faster access.
    cur.execute("VACUUM")
    
    # Close the cursor.
    cur.close()
    
    print "Completed in %i seconds..."%int(time.time()-beginTime)
    print '\a'


#import profile
#profile.runctx("main()",globals(),locals(),"profile.prof")

#import hotshot
#prof = hotshot.Profile("hotshot.prof",0,0)
#prof.runctx("main()",globals(),locals())


main()

#prof.close()
