# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

 
#Generate TWiki docs

import os,sys,shutil,time
sys.path.append(os.getcwd())
beginTime = time.time()

try:
    shutil.rmtree("./distrib/twiki")
except:
    pass

if not os.path.exists("./distrib/twiki/data/MoMWorld"):
    os.makedirs("./distrib/twiki/data/MoMWorld")
if not os.path.exists("./distrib/twiki/pub/MoMWorld"):
    os.makedirs("./distrib/twiki/pub/MoMWorld")
    

for sfile in os.listdir("./mud/worlddocs/static"):
    if ".svn" in sfile:
        continue
    shutil.copyfile("./mud/worlddocs/static/%s"%sfile,"./distrib/twiki/data/MoMWorld/%s"%sfile)

#images to pub
for sfile in os.listdir("./mud/worlddocs/images"):
    if ".svn" in sfile:
        continue
    shutil.copyfile("./mud/worlddocs/images/%s"%sfile,"./distrib/twiki/pub/MoMWorld/%s"%sfile)

 
from mud.common.dbconfig import SetDBConnection
from mud.gamesettings import *

#setup the db connection
DATABASEPATH = "%s/data/worlds/multiplayer.baseline"%GAMEROOT
DATABASE = DATABASEPATH+"/world.db"

SetDBConnection('sqlite:/%s'%DATABASE,True)

from sqlobject import *


from spawnpages import CreateSpawnPages
from zonepages import CreateZonePages
from itempages import CreateItemPages
from questpages import CreateQuestPages
from classpages import CreateClassPages
from spellpages import CreateSpellPages
from skillpages import CreateSkillPages
from recipepages import CreateRecipePages
from itemsetpages import CreateItemSetPages
from factionpages import CreateFactionPages


print "Creating Spawn Pages..."
spawnQuests,spawnSpells,spawnFactions = CreateSpawnPages()
print "Creating Zone Pages..."
CreateZonePages()
print "Creating Quest Pages..."
questItems, questFactions = CreateQuestPages(spawnQuests)
del spawnQuests
print "Creating Faction Pages..."
CreateFactionPages(spawnFactions,questFactions)
del spawnFactions
del questFactions
print "Creating Spell Pages..."
spellSummonItems,spellClasses = CreateSpellPages(spawnSpells)
del spawnSpells
print "Creating Class Pages..."
classSkills = CreateClassPages(spellClasses)
del spellClasses
print "Creating Skill Pages..."
CreateSkillPages(classSkills)
del classSkills
print "Creating Item Pages..."
itemSetDict = CreateItemPages(spellSummonItems,questItems)
del spellSummonItems
del questItems
print "Creating Item Set Pages..."
CreateItemSetPages(itemSetDict)
del itemSetDict
print "Creating Recipe Pages..."
CreateRecipePages()
#tar it

def dirwalk(dir,ignore=[]):
    "walk a directory tree, using a generator"
    
    for f in os.listdir(dir):
        fullpath = os.path.join(dir,f)
        fullpath = fullpath.replace("\\","/")
        if fullpath.upper().find(".SVN")!=-1:
            continue
        
        ignored = False
        for i in ignore:
            if fullpath.upper().find(i) != -1:
                ignored = True 
                break
            
        if ignored:
            continue
        
        
        if os.path.isdir(fullpath) and not os.path.islink(fullpath):
            for x in dirwalk(fullpath,ignore):  # recurse into subdir
                yield x
        else:
            yield fullpath


print "Creating ./distrib/momworld.tar.gz"
import tarfile

files = dirwalk("./distrib/twiki/")

tar = tarfile.open("./distrib/momworld.tar.gz",'w:gz')
for name in files:
    pname = "./%s"%name[10:]
    tarinfo = tar.gettarinfo(name, pname)
    tar.addfile(tarinfo, file(name,"rb"))
tar.close()
print "Encyclopedia compiled and packed up nicely in %i Seconds."%int(time.time()-beginTime)
print '\a'
 
