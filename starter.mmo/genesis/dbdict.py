# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.world.career import ClassProto
from mud.world.character import Character,CharacterSpell,StartingGear
from mud.world.crafting import Recipe,RecipeIngredient
from mud.world.defines import *
from mud.world.dialog import Dialog,DialogAction,DialogCheckItem, \
    DialogCheckMaxFaction,DialogCheckMinFaction,DialogCheckSkill, \
    DialogChoice,DialogFaction,DialogGiveItem,DialogLine, \
    DialogRequireClass,DialogRequireItem,DialogRequirement, \
    DialogRequireRace,DialogRequireRealm,DialogRequireSkill, \
    DialogTakeItem,DialogTrainSkill,JournalEntry
from mud.world.effect import EffectDamage,EffectDrain,EffectIllusion, \
    EffectLeech,EffectRegen,EffectPermanentStat,EffectProto,EffectStat
from mud.world.faction import Faction,FactionRelation
from mud.world.item import Item,ItemClass,ItemClassifier,ItemContainerProto, \
    ItemProto,ItemRace,ItemRealm,ItemSet,ItemSetPower,ItemSetProto, \
    ItemSetRequirement,ItemSetSpell,ItemSetStat,ItemSlot,ItemSpell,ItemStat
from mud.world.loot import LootItem,LootProto
from mud.world.player import Player
from mud.world.race import GetRace
from mud.world.skill import ClassSkill,ClassSkillQuestRequirement, \
    ClassSkillRaceRequirement
from mud.world.spawn import Spawn,SpawnGroup,SpawnGroupController, \
    SpawnGroupControllerInfo,SpawnInfo,SpawnKillFaction,SpawnResistance, \
    SpawnSkill,SpawnSpell,SpawnStat
from mud.world.spell import SpellClass,SpellComponent,SpellExclusion, \
    SpellParticleNode,SpellProto
from mud.world.vendor import VendorItem,VendorProto
from mud.world.theworld import World
from mud.world.zone import Zone,ZoneLink

from copy import copy
import traceback



class DBDict(dict):
    registry = {}
    cache = {}
    
    #static methods
    
    def clearRegistry():
        DBDict.registry = {}
        
    clearRegistry = staticmethod(clearRegistry)

    
    def getInstanceList(classname):
        return DBDict.registry[classname]
        
    getInstanceList = staticmethod(getInstanceList)
    
    def getDBDict(classname,key,value):
        try:
            t = (classname,key,value)
            try:
                return DBDict.cache[t]
            except KeyError:
                pass
                
            for db in DBDict.registry[classname]:
                if db[key]==value:
                    DBDict.cache[t]=db
                    return db
            assert 0, "Unable to find: %s.%s == %s"%(classname,key,str(value))
            return None
        except:
            traceback.print_exc()
            return None
            
    getDBDict = staticmethod(getDBDict)
    
    
    def createRows(classname,enforce=True):
        if not DBDict.registry.has_key(classname):
            return
        try:
            for r in DBDict.registry[classname]:
                r.create()
        except:    # no such object instance defined in any file
            if enforce:
                traceback.print_exc()
                raise ValueError,"No such object instance defined in any file."
            # Return and continue instead of aborting.
            else:
                return
    
    createRows = staticmethod(createRows)
    
    
    #end static methods
    
    def __init__(self,**args):
        for k,v in args.iteritems():
            if k == 'src':
                if v:
                    for key,value in v.iteritems():
                        if isinstance(value,DBDict):
                            self[key]=value
                        else:
                            self[key]=copy(value)
            else:
                self[k]=v
        if not self.classname:
            assert 0
 
        classname = self.classname
        
        if not DBDict.registry.has_key(classname):
            DBDict.registry[classname]=[]
        
        DBDict.registry[classname].append(self)
        
        self.sqlObject = None
            
        
    def __setattr__(self,item,val):
        dict.__setitem__(self,item,val)
        
    def __getattr__(self,item):
        return dict.__getitem__(self,item)
        
    def clone(self,**args):
        c = self.__class__(src=self,classname = self.classname)
        for k,v in args.iteritems():
            c[k]=v
        c.sqlObject = None
        return c
        
    def create(self):
        assert 0


class DBItemSetPower(DBDict):
    def __init__(self,**args):
        self.classname = 'ItemSetPower'
        
        self.requirements = []
        self.stats = []
        self.spells = []
        
        DBDict.__init__(self,**args)
    
    def addRequirement(self,name,itemCount,countTest = RPG_ITEMSET_TEST_GREATEREQUAL):
        if not name:
            traceback.print_exc()
            raise ValueError,"%s requirement has no assigned name!"%self.name
        for req in self.requirements:
            if name == req[0]:
                traceback.print_exc()
                raise ValueError,"%s requirement name is not unique for this ItemSetPower!"%self.name
        if itemCount < 1:    # also check for negatives
            traceback.print_exc()
            raise ValueError,"%s requirement %s has an itemCount < 1, use spell procs instead."%(self.name,name)
        if countTest not in [RPG_ITEMSET_TEST_LESSEQUAL,RPG_ITEMSET_TEST_EQUAL,RPG_ITEMSET_TEST_GREATEREQUAL]:
            traceback.print_exc()
            raise ValueError,"%s requirement %s has an invalid count test!\nCount test needs to be either RPG_ITEMSET_TEST_LESSEQUAL, RPG_ITEMSET_TEST_EQUAL or RPG_ITEMSET_TEST_GREATEREQUAL."%(self.name,name)
        self.requirements.append((name,itemCount,countTest))
    
    def addStat(self,statname,value):
        if not statname:
            traceback.print_exc()
            raise ValueError,"%s stat has no assigned stat name!"%self.name
        if not value:
            traceback.print_exc()
            raise ValueError,"%s stat attribute is zero and therefore useless."%self.name
        self.stats.append((statname,value))
    
    # only RPG_ITEM_TRIGGER_WORN, RPG_ITEM_TRIGGER_MELEE or RPG_ITEM_TRIGGER_DAMAGED
    def addSpell(self,spellProto,trigger,frequency,duration=0):
        if not spellProto:
            traceback.print_exc()
            raise ValueError,"Spell proto missing for %s.addSpell()!"%self.name
        if trigger not in [RPG_ITEM_TRIGGER_WORN,RPG_ITEM_TRIGGER_MELEE,RPG_ITEM_TRIGGER_DAMAGED]:
            traceback.print_exc()
            raise ValueError,"Only RPG_ITEM_TRIGGER_WORN, RPG_ITEM_TRIGGER_MELEE or RPG_ITEM_TRIGGER_DAMAGED are allowed for triggers on item set spells!"
        self.spells.append((spellProto,trigger,frequency,duration))
    
    def clearSpells(self):
        self.spells = []
    
    def clearStats(self):
        self.stats = []
    
    def clearRequirements(self):
        self.requirements = []
    
    
    #the get functions return from the db
    def getSQLObject(name):
        ip = DBDict.getDBDict('ItemSetPower','name',name)
        assert ip,name
        
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
    
#ItemSet
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        try:
            item = ItemSetPower.byName(self.name)
            for req in item.requirements:
                req.destroySelf()
            for st in item.stats:
                st.destroySelf()
            for sp in item.spells:
                sp.destroySelf()
        except:
            item = ItemSetPower(name=self.name)
            
        set = dict(self)
        del set['name']
        del set['classname']
        del set['sqlObject']
        
        del set['requirements']
        del set['stats']
        del set['spells']
        
        item.set(**set)
        
        for req in self.requirements:
            ItemSetRequirement(itemSetPower=item,name=req[0],itemCount=req[1],countTest=req[2])
        for stat in self.stats:
            ItemSetStat(itemSetPower=item,statname=stat[0],value=stat[1])
        for spell in self.spells:
            spellProto = DBSpellProto.getSQLObject(spell[0])
            ItemSetSpell(itemSetPower=item,spellProto=spellProto,trigger=spell[1],frequency=spell[2],duration=spell[3])

        
        self.sqlObject = item
        
        return item


class DBItemSetProto(DBDict):
    def __init__(self,**args):
        self.classname = 'ItemSetProto'
        
        self.powers = []
        
        DBDict.__init__(self,**args)
    
    def addPower(self,setPower):
        if setPower not in self.powers:
            self.powers.append(setPower)
    
    def clearPowers(self):
        self.powers = []
    
    
    #the get functions return from the db
    def getSQLObject(name):
        ip = DBDict.getDBDict('ItemSetProto','name',name)
        assert ip,name
        
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
    
#ItemSetProto
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        if not len(self.powers):
            raise ValueError,"DBItemSetProto %s has no assigned ItemSetPowers"%self.name
        
        try:
            item = ItemSetProto.byName(self.name)
            for setpower in item.powers:
                item.removeItemSetPower(setpower)
        except:
            item = ItemSetProto(name=self.name)
            
        set = dict(self)
        del set['name']
        del set['classname']
        del set['sqlObject']
        
        del set['powers']
        
        item.set(**set)
        
        for power in self.powers:
            item.addItemSetPower(DBItemSetPower.getSQLObject(power))

        
        self.sqlObject = item
        
        return item



class DBItemProto(DBDict):
    def __init__(self,**args):
        self.classname = 'ItemProto'
        self.slots = []
        self.spellProto = None
        
        self.itemSets = []
        self.stats = []        
        self.races = []
        self.realms = []
        self.classes = []
        self.itemSpells = []
        
        self.itemType = []
        self.itemClassifiers = []
        
        self.worthTin = 0
        self.worthCopper = 0
        self.worthSilver = 0
        self.worthGold = 0
        self.worthPlatinum = 0
        
        # Container specific variables.
        self.containerSize = 0
        self.containerContentFlags = 0
        self.containerContentClassifiers = []
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def addStat(self,stat,value):
        self.stats.append((stat,value))
    
    def addRace(self,race):
        if race not in self.races:
            self.races.append(race)

    def addRealm(self,realm,level=0):
        for r in self.realms:
            if realm == r[0]:
                return
        self.realms.append((realm,level))
            
    def addClass(self,classname,level):
        self.classes.append((classname,level))
        
    def addSpell(self,spellProto,trigger,frequency,duration=0):
        self.itemSpells.append((spellProto,trigger,frequency,duration))
    
    def addItemSet(self,itemSet,contribution):
        if not contribution:
            traceback.print_exc()
            raise ValueError,"Contribution string of %s.addItemSet() is empty."%self.name
        for set in self.itemSets:
            if set[0] == itemSet and set[1] == contribution:
                traceback.print_exc()
                raise ValueError,"A given item can only contribute once to a specific set in the same manner! (Clones inherit item sets by the way)"
        self.itemSets.append((itemSet,contribution))
    
    def clearItemSets(self):
        self.itemSets = []
    
    def clearSpells(self):
        self.itemSpells = []
        
    def clearStats(self):
        self.stats = []
        
    def clearClasses(self):
        self.classes = []
        
    def clearRaces(self):
        self.races = []

    def clearRealms(self):
        self.realms = []
        
    
    #the get functions return from the db
    def getSQLObject(name):

        ip = DBDict.getDBDict('ItemProto','name',name)
        assert ip,name
        
        if ip.sqlObject:
            return ip.sqlObject
        
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
    
#ItemProto        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        try:
            item = ItemProto.byName(self.name)
            #print "updating",self.name
            for r in item.racesInternal:
                r.destroySelf()
            for r in item.realms:
                r.destroySelf()
            for cl in item.classes:
                cl.destroySelf()
            for s in item.slotsInternal:
                s.destroySelf()
            for s in item.stats:
                s.destroySelf()
            for s in item.itemSets:
                s.destroySelf()
        except:
            #print "creating",self.name
            item = ItemProto(name=self.name)
            
        set = dict(self)
        del set['name']
        del set['classname']
        del set['sqlObject']
        del set['slots']
        del set['spellProto']
        
        del set['itemSets']
        del set['stats']
        del set['races']
        del set['realms']
        del set['classes']
        del set['itemType']
        del set['itemClassifiers']
        del set['itemSpells']
        
        del set['worthTin']
        del set['worthCopper']
        del set['worthSilver']
        del set['worthGold']
        del set['worthPlatinum']
        
        del set['containerSize']
        del set['containerContentFlags']
        del set['containerContentClassifiers']
        
        item.set(**set)
        
        MINLEVEL = LEVEL = item.level
        
        for slot in self.slots:
            ItemSlot(itemProto=item,slot=slot)
        for race in self.races:
            ItemRace(racename=race,itemProto=item)
        for realm in self.realms:
            if realm[1] > LEVEL:
                LEVEL = realm[1]
            if (realm[1] < MINLEVEL and realm[1] > 0) or (MINLEVEL == 1 and realm[1] > 1):
                MINLEVEL = realm [1]
            ItemRealm(realmname=realm[0],level=realm[1],itemProto=item)
        for klass in self.classes:
            if klass[1] > LEVEL:
                LEVEL = klass[1]
            if klass[1] < MINLEVEL or MINLEVEL == 1:
                MINLEVEL = klass[1]
            ItemClass(classname=klass[0],level=klass[1],itemProto=item)
        for stat in self.stats:
            if stat[0]=='pre' and MINLEVEL<90:
                assert 0, "PRESENCE ON AN ITEM WITH LEVEL < 90! -> %s"%self.name
            ItemStat(statname=stat[0],value=stat[1],itemProto=item)
            
        for spell in self.itemSpells:
            spellProto = DBSpellProto.getSQLObject(spell[0])
            ItemSpell(itemProto = item, spellProto=spellProto,trigger=spell[1],frequency=spell[2],duration=spell[3])
        
        for set,contribution in self.itemSets:
            setProto = DBItemSetProto.getSQLObject(set)
            ItemSet(itemProto = item, itemSetProto = setProto, contribution = contribution)
            
        if self.spellProto:
            item.spellProto = DBSpellProto.getSQLObject(self.spellProto)
            
        
        item.level = MINLEVEL
        #repair baseline
        if not item.repairMax:
            if not item.flags & RPG_ITEM_INDESTRUCTIBLE and len(item.slots) and item.skill:
                item.repairMax = LEVEL*5
        
        tin = long(self.worthTin)
        tin += self.worthCopper*100L
        tin += self.worthSilver*10000L
        tin += self.worthGold*1000000L
        tin += self.worthPlatinum*100000000L
        item.worthTin = tin
        
        for classifier in self.itemClassifiers:
            try:
                cl = ItemClassifier.byName(classifier)
            except:
                cl = ItemClassifier(name=classifier)
            item.addItemClassifier(cl)
        
        # Create container object if needed.
        if self.containerSize > 0:
            container = ItemContainerProto(containerSize=self.containerSize, contentFlagsRequired=self.containerContentFlags)
            item.itemContainerProto = container
            for classifier in self.containerContentClassifiers:
                try:
                    cl = ItemClassifier.byName(classifier)
                except:
                    cl = ItemClassifier(name=classifier)
                container.addItemClassifier(cl)
        
        self.sqlObject = item
        
        return item



class DBSpawn(DBDict):
    def __init__(self,**args):
        self.classname = 'Spawn'
        self.realm = None
        self.choices = []
        self.model=""
        self.dialog = None
        self.loot = None
        self.respawn = None
        self.vendor = ""
        self.sclass = ""
        self.tclass = ""
        self.factions = []
        self.killFactions = []
        self.resistances = []
        self.spawnSkills = []
        self.spawnSpells = []
        self.spawnStats = []
        self.isMonster = True
        self.assists = True
        self.isUnique = False
        self.banker = False
        self.inn = False
        self.noCorpse = False
        self.fixedSex = False
        self.resource = False
        self.aggressive = False
        self.passive = False
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def getDBSpawn(name):
        return DBDict.getDBDict('Spawn','name',name)
    
    getDBSpawn = staticmethod(getDBSpawn)

    def addSkill(self,skillname,level):
        self.spawnSkills.append((skillname,level))

    def addSpell(self,spellname):
        self.spawnSpells.append(spellname)
        
    def addFaction(self,faction):
        self.factions.append(faction)

    def addResistance(self,rtype,ramount):
        self.resistances.append((rtype,ramount))

    def addKillFaction(self,faction,percent = 1.0):
        self.killFactions.append((faction,percent))
        
    def addStat(self,statname,value):
        self.spawnStats.append((statname,value))
        
    def clearFactions(self):
        self.factions = []
    def clearKillFactions(self):
        self.killFactions = []
    def clearResistances(self):
        self.resistances = []
    def clearSkills(self):
        self.spawnSkills = []
    def clearSpells(self):
        self.spawnSpells = []
        
    def clearStats(self):
        self.spawnStats = []
        
    
    #the get functions return from the db
    def getSQLObject(name):
        #try to create this item proto
        ip = DBDict.getDBDict('Spawn','name',name)
        assert ip,name
        
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject

        try:
            spawn = Spawn.byName(self.name)
            spawn.pclassInternal = self.pclass
            spawn.sclassInternal = self.sclass
            spawn.tclassInternal = self.tclass
            spawn.model = self.model
        except:
            try:
                spawn = Spawn(name=self.name,pclassInternal = self.pclass,model = self.model)
                spawn.sclassInternal = self.sclass
                spawn.tclassInternal = self.tclass
                

            except:
                traceback.print_exc()
                print "Error in Spawn %s"%self.name
        
        if self.loot:
            spawn.lootProto = self.loot.getSQLObject()
            
            #moneh!
        
        lp = spawn.lootProto
        if not lp:
            lp = spawn.lootProto = LootProto()
          
        if not lp.tin:
            #baseline
            level = self.plevel
            tp = level**5+10
            lp.tin = tp
            
        if self.dialog:
            spawn.dialog=DBDialog.getSQLObject(self.dialog)
            
        
        if self.vendor:
            spawn.vendorProto=DBVendorProto.getSQLObject(self.vendor)


        if self.respawn:
            spawn.respawn=DBSpawn.getSQLObject(self.respawn)
            
        for sskill in self.spawnSkills:
            SpawnSkill(spawn=spawn,skillname=sskill[0],level=sskill[1])

        for sspell in self.spawnSpells:
            SpawnSpell(spawn=spawn,spellname=sspell)
            
        for sstat in self.spawnStats:
            SpawnStat(spawn=spawn,statname=sstat[0],value=sstat[1])
        
        if not hasattr(self,"move"):
            self.move = 1
        if not hasattr(self,"plevel"):
            self.plevel = 1
            
        self.move += float(self.plevel)/150.0
        
        #factions
        for f in self.factions:
            faction = DBFaction.getSQLObject(f)
            spawn.addFaction(faction)
            
        for f in self.killFactions:
            faction = DBFaction.getSQLObject(f[0])
            SpawnKillFaction(spawn=spawn,faction=faction,percent=f[1])
            
        done = []
        for rtype,ramount in self.resistances:
            if rtype in done:
                print "WARNING: Spawn %s duplicate resistance: %s"%(spawn.name,RPG_RESIST_TEXT[rtype])
                continue
            done.append(rtype)
            SpawnResistance(spawn=spawn,resistType=rtype,resistAmount=ramount)
            
        
        set = dict(self)
        
        if self.realm == None:
            del set['realm']
            
        del set['name']
        del set['classname']
        del set['sqlObject']
        del set['pclass']
        del set['sclass']
        del set['tclass']
        del set['model']
        del set['choices']
        del set['loot']
        del set['dialog']
        del set['vendor']
        del set['respawn']
        del set['factions']
        del set['killFactions']
        del set['resistances']
        del set['spawnSkills']
        del set['spawnSpells']
        del set['spawnStats']
        del set['isMonster']
        del set['assists']
        del set['isUnique']
        del set['banker']
        del set['inn']
        del set['noCorpse']
        del set['fixedSex']
        del set['resource']
        del set['aggressive']
        del set['passive']
        
        try:
            
            spawn.set(**set)
        except:
            traceback.print_exc()
            raise RuntimeWarning,"Error creating spawn %s"%self.name
        
        self.sqlObject = spawn
        
        if spawn.plevel == None:
            spawn.plevel = 1
        if spawn.slevel == None:
            spawn.slevel = 0
        if spawn.tlevel == None:
            spawn.tlevel = 0
            
        if self.isMonster:
            spawn.realm = RPG_REALM_MONSTER
        elif self.realm == None:
            r = GetRace(spawn.race)
            if r.realm != RPG_REALM_MONSTER:
                spawn.realm = r.realm
            else:
                spawn.realm = RPG_REALM_NEUTRAL
        
        # only change if different from default to not overwrite direct flags assignments
        if not self.assists:
            spawn.flags |= RPG_SPAWN_NOASSIST
        if self.isUnique:
            spawn.flags |= RPG_SPAWN_UNIQUE
        if self.banker:
            spawn.flags |= RPG_SPAWN_BANKER
        if self.inn:
            spawn.flags |= RPG_SPAWN_INN
        if self.noCorpse:
            spawn.flags |= RPG_SPAWN_NOCORPSE
        if self.fixedSex:
            spawn.flags |= RPG_SPAWN_FIXEDSEX
        if self.resource: 
            spawn.flags |= RPG_SPAWN_RESOURCE
        if self.aggressive:
            spawn.flags |= RPG_SPAWN_AGGRESSIVE
        if self.passive:
            spawn.flags |= RPG_SPAWN_PASSIVE
            # Remove the aggressive flag that would cancel passivity.
            spawn.flags &= ~RPG_SPAWN_AGGRESSIVE
        
        return spawn
        
    #dialog

class DBSpawnInfo(DBDict):
    def __init__(self,**args):
        self.classname = 'SpawnInfo'
        self.spawn = ""
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    
    #the get functions return from the db
    def getSQLObject(self):
        return self.create()
            
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        spawn = DBSpawn.getSQLObject(self.spawn)
        si = SpawnInfo(spawn=spawn)
        
        set = dict(self)

        del set['classname']
        del set['sqlObject']
        del set['spawn']
        
        si.set(**set)
        
            
        self.sqlObject = si
        
        return si
"""
    groupName = StringCol() 
    zone = ForeignKey('Zone')
    spawninfos = RelatedJoin('SpawnInfo')
    targetName = StringCol(default='')
"""

class DBSpawnGroup(DBDict):
    def __init__(self,**args):
        self.classname = 'SpawnGroup'
        self.groupName = ""
        self.zone = ""
        self.spawnInfos = []
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def addSpawnInfo(self,si):
        self.spawnInfos.append(si)
    
    
    # The get functions return from the db.
    def getSQLObject(spawnGroup):
        assert spawnGroup,"No Spawn Group to get!"
        
        if spawnGroup.sqlObject:
            return spawnGroup.sqlObject
        
        return spawnGroup.create()
    
    getSQLObject = staticmethod(getSQLObject)
    
    
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        zone = DBZone.getSQLObject(self.zone)
        sg = SpawnGroup(groupName = self.groupName,zone = zone)
        
        for si in self.spawnInfos:
            sg.addSpawnInfo(si.getSQLObject())
        
        set = dict(self)

        del set['classname']
        del set['sqlObject']
        del set['zone']
        del set['groupName']
        del set['spawnInfos']
        
        sg.set(**set)
        
            
        self.sqlObject = sg
        
        return sg



# Simple class to ease development of spawngroup controllers.
# (Better readable code)
class SpawnGroupSet(list):
    def __init__(self, *args, **kw):
        super(SpawnGroupSet,self).__init__(*args,**kw)
    
    
    def addSpawnGroup(self, sGroup, groupIndex):
        if not super(SpawnGroupSet,self).__contains__((sGroup,groupIndex)):
            super(SpawnGroupSet,self).append((sGroup,groupIndex))



class DBSpawnGroupController(DBDict):
    def __init__(self, **args):
        self.classname = 'SpawnGroupController'
        
        self.spawnGroups = []
        self.spawnGroupSets = []
        
        # This comes after defaults, so that the src can override.
        DBDict.__init__(self,**args)
    
    
    def addSpawnGroup(self, sGroup, cycleMessage='', cycleSound=''):
        # Meh, DBDict objects aren't hashable, can't use sets or dicts.
        for sg,cmessage,csound in self.spawnGroups:
            if sg == sGroup:
                traceback.print_exc()
                raise ValueError,"can't assign the same Spawn Group twice to the same Spawn Group Controller!"
        
        self.spawnGroups.append((sGroup,cycleMessage,cycleSound))
    
    
    def addSpawnGroupSet(self, sGroupSet, cycleMessage='', cycleSound=''):
        for sgs,cmessage,csound in self.spawnGroupSets:
            if sgs == sGroupSet:
                traceback.print_exc()
                raise ValueError,"can't assign the same Spawn Group Set twice to the same Spawn Group Controller!"
        
        self.spawnGroupSets.append((sGroupSet,cycleMessage,cycleSound))
    
    
    def clearSpawnGroups(self):
        self.spawnGroups = []
    
    
    def clearSpawnGroupSets(self):
        self.spawnGroupSets = []
    
    
    # The get functions return from the db.
    def getSQLObject(name):
        sgc = DBDict.getDBDict('SpawnGroupController','name',name)
        assert sgc,name
        
        if sgc.sqlObject:
            return sgc.sqlObject
        
        return sgc.create()
    
    getSQLObject = staticmethod(getSQLObject)
    
    
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        try:
            controller = SpawnGroupController.byName(self.name)
            # Found existing, update.
            for sgInfo in controller.spawnGroupInfosInternal:
                sgInfo.destroySelf()
        except:
            # Not found, so create a new one.
            controller = SpawnGroupController(name=self.name)
        
        set = dict(self)
        del set['name']
        del set['classname']
        del set['sqlObject']
        del set['spawnGroups']
        del set['spawnGroupSets']
        controller.set(**set)
        
        setIndex = 1
        
        # Process single spawngroups.
        for sg,cmessage,csound in self.spawnGroups:
            dbSG = DBSpawnGroup.getSQLObject(sg)
            # Check if all spawns in this spawngroup are of the same realm.
            realm = RPG_REALM_UNDEFINED
            for sinfo in dbSG.spawninfosInternal:
                srealm = sinfo.spawn.realm
                if srealm != realm:
                    if realm != RPG_REALM_UNDEFINED:
                        realm = RPG_REALM_UNDEFINED
                        break
                    realm = srealm
            # Create a spawngroup controller info object.
            controllerInfo = SpawnGroupControllerInfo(spawnGroup=dbSG,spawnGroupController=controller,realm=realm,cycleMessage=cmessage,cycleSound=csound,spawnGroupSet=setIndex)
            # Assign this controller info to the spawngroup.
            dbSG.controllerInfo = controllerInfo
            # Increment spawngroup set index.
            setIndex += 1
        
        # Process spawngroup sets.
        for sgSet,cmessage,csound in self.spawnGroupSets:
            controllerInfos = []
            realm = RPG_REALM_UNDEFINED
            realmCheck = True
            for sg,index in sgSet:
                dbSG = DBSpawnGroup.getSQLObject(sg)
                if realmCheck:
                    # Check if all spawns in this spawngroup are of the same realm.
                    for sinfo in dbSG.spawninfosInternal:
                        srealm = sinfo.spawn.realm
                        if srealm != realm:
                            if realm != RPG_REALM_UNDEFINED:
                                realm = RPG_REALM_UNDEFINED
                                realmCheck = False
                                break
                            realm = srealm
                # Create a spawngroup controller info object.
                controllerInfo = SpawnGroupControllerInfo(spawnGroup=dbSG,spawnGroupController=controller,cycleMessage=cmessage,cycleSound=csound,spawnGroupSet=setIndex,groupIndex=index)
                # Assign this controller info to the spawngroup.
                dbSG.controllerInfo = controllerInfo
                controllerInfos.append(controllerInfo)
            # All spawngroups have been processed, we should know now the realm of the
            #  whole set (if any). So run through all controller infos and set it.
            for controllerInfo in controllerInfos:
                controllerInfo.realm = realm
            # Increment spawngroup set index.
            setIndex += 1
        
        self.sqlObject = controller
        
        return controller



class DBDialog(DBDict):
    
    def clone(self,**args):
        assert 0, "Do not clone dialogs, use addDialog to insert instead"
        
    
    def __init__(self,**args):
        self.classname = 'Dialog'
        self.greeting = None
        self.rebuke = None
        self.subDialogs = []
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def getDBDialog(name):
        return DBDict.getDBDict('Dialog','name',name)
        
    getDBDialog = staticmethod(getDBDialog)
        
    
    #the get functions return from the db
    def getSQLObject(name):
        #try to create this item proto
        ip = DBDict.getDBDict('Dialog','name',name)
        assert ip,name
        
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
    
    def addDialog(self,dlg):
        self.subDialogs.append(dlg)
        #self.greeting.choices.extend(dlg.greeting.choices)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
            
        try:
            dlg = Dialog.byName(self.name)
        except:
            dlg = Dialog(name=self.name)
        
        set = dict(self)
        del set['name']
        del set['classname']
        del set['sqlObject']
        del set['subDialogs']
        
        greeting = None
        if self.greeting:
            greeting = self.greeting.getSQLObject(dlg)
        set['greeting']=greeting
        
        rebuke = None
        if self.rebuke:
            rebuke = self.rebuke.getSQLObject(dlg)
        set['rebuke']=rebuke
        
        for d in self.subDialogs:
            sqld = d.getSQLObject(d.name)
            for c in sqld.greeting.choices:
                dlg.addDialogChoice(c)
                greeting.addDialogChoice(c)
                
                

        
        dlg.set(**set)
        
        self.sqlObject = dlg
        
        return dlg

    
class DBDialogLine(DBDict):
    def __init__(self,**args):
        self.classname = 'DialogLine'
        self.choices = []
        self.actions = []
        self.text = ""
        
        self.journalTopic = ""
        self.journalEntry = ""
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
      
    def addAction(self,action):
        self.actions.append(action)
        
    def addChoice(self,choice):
        self.choices.append(choice)
        
    def insertChoice(self,index,choice):
        self.choices.insert(index,choice)
    
    #the get functions return from the db
    def getSQLObject(self,dialog):
        return self.create(dialog)
        
    def create(self,dialog):
        if self.sqlObject:
            return self.sqlObject
       
            
        line = DialogLine(dialog=dialog)
        set = dict(self)
        
        text = self.text.replace('\n',"")
        line.text = text
        
        for c in self.choices:
            line.addDialogChoice(c.getSQLObject(dialog))
            
        for a in self.actions:
            line.addDialogAction(a.getSQLObject(dialog))
        
        if self.journalTopic and self.journalEntry:
            journalEntry = JournalEntry(topic = self.journalTopic,entry = self.journalEntry,text = self.text)
            line.journalEntryID = journalEntry.id
        elif self.journalTopic:
            traceback.print_exc()
            raise ValueError,"incomplete journal definition for DBDialogLine, journalEntry has not been defined!"
        elif self.journalEntry:
            traceback.print_exc()
            raise ValueError,"incomplete journal definition for DBDialogLine, journalTopic has not been defined!"
        
        
        del set['classname']
        del set['sqlObject']
        del set['choices']
        del set['actions']
        del set['text']
        
        del set['journalTopic']
        del set['journalEntry']
        
        line.set(**set)
        
        
        self.sqlObject = line
        
        return line


class DBDialogRequirement(DBDict):
    def __init__(self,**args):
        self.classname = 'DialogRequirement'
        self.requireClasses = []
        self.requireRaces = []
        self.requireRealms = []
        self.requireSkills = []
        self.requireItems = []
        self.classesInclusive = True
        self.racesInclusive = True
        self.realmsInclusive = True
        self.skillsInclusive = True
        self.itemsInclusive = True
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
    
    def addClassRequirement(self,positiveCheck,className,classLevel = 0):
        if not className:
            raise ValueError,"addClassRequirement used without a className specified (2nd argument)!"
            return
        if (positiveCheck,className,classLevel) not in self.requireClasses:
            self.requireClasses.append((positiveCheck,className,classLevel))
    def clearClassRequirements(self):
        self.requireClasses = []
    
    def addRaceRequirement(self,positiveCheck,raceName):
        if not raceName:
            raise ValueError,"addRaceRequirement used without a raceName specified (2nd argument)!"
            return
        if (positiveCheck,raceName) not in self.requireRaces:
            self.requireRaces.append((positiveCheck,raceName))
    def clearRaceRequirements(self):
        self.requireRaces = []
    
    def addRealmRequirement(self,positiveCheck,realm,realmLevel = 0):
        if realm not in [RPG_REALM_LIGHT,RPG_REALM_DARKNESS,RPG_REALM_MONSTER]:
            raise ValueError,"realm argument in addRealmRequirement is not one of RPG_REALM_LIGHT, RPG_REALM_DARKNESS or RPG_REALM_MONSTER (2nd argument)!"
            return
        if (positiveCheck,realm,realmLevel) not in self.requireRealms:
            self.requireRealms.append((positiveCheck,realm,realmLevel))
    def clearRealmRequirements(self):
        self.requireRealms = []
    
    def addSkillRequirement(self,positiveCheck,skillName,skillLevel = 0):
        if not skillName:
            raise ValueError,"addSkillRequirement used without a skillName specified (2nd argument)!"
            return
        if (positiveCheck,skillName,skillLevel) not in self.requireSkills:
            self.requireSkills.append((positiveCheck,skillName,skillLevel))
    def clearSkillRequirements(self):
        self.requireSkills = []
    
    def addItemRequirement(self,positiveCheck,itemName,itemCount = 1):
        if not itemName:
            raise ValueError,"addItemRequirement used without a itemName specified (2nd argument)!"
            return
        if (positiveCheck,itemName,itemCount) not in self.requireItems:
            self.requireItems.append((positiveCheck,itemName,itemCount))
    def clearItemRequirements(self):
        self.requireItems = []
    
    #the get functions return from the db
    def getSQLObject(self):
        return self.create()
    
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        req = DialogRequirement()
        set = dict(self)
        del set['classname']
        del set['sqlObject']
        
        del set['requireClasses']
        del set['requireRaces']
        del set['requireRealms']
        del set['requireSkills']
        del set['requireItems']
        del set['classesInclusive']
        del set['racesInclusive']
        del set['realmsInclusive']
        del set['skillsInclusive']
        del set['itemsInclusive']
        req.set(**set)
        
        for positiveCheck,className,classLevel in self.requireClasses:
            DialogRequireClass(dialogRequirement = req,positiveCheck = positiveCheck,className = className,classLevel = classLevel)
        for positiveCheck,raceName in self.requireRaces:
            DialogRequireRace(dialogRequirement = req,positiveCheck = positiveCheck,raceName = raceName)
        for positiveCheck,realm,realmLevel in self.requireRealms:
            DialogRequireRealm(dialogRequirement = req,positiveCheck = positiveCheck,realm = realm, realmLevel = realmLevel)
        for positiveCheck,skillName,skillLevel in self.requireSkills:
            DialogRequireSkill(dialogRequirement = req,positiveCheck = positiveCheck,skillName = skillName,skillLevel = skillLevel)
        for positiveCheck,itemName,itemCount in self.requireItems:
            itemProto = DBItemProto.getSQLObject(itemName)
            DialogRequireItem(dialogRequirement = req,positiveCheck = positiveCheck,itemProto = itemProto,count = itemCount)
        req.exclusiveFlags = 0
        if not self.classesInclusive:
            req.exclusiveFlags |= RPG_DIALOG_REQUIREMENT_EXCLUSIVE_CLASSES
        if not self.racesInclusive:
            req.exclusiveFlags |= RPG_DIALOG_REQUIREMENT_EXCLUSIVE_RACES
        if not self.realmsInclusive:
            req.exclusiveFlags |= RPG_DIALOG_REQUIREMENT_EXCLUSIVE_REALMS
        if not self.skillsInclusive:
            req.exclusiveFlags |= RPG_DIALOG_REQUIREMENT_EXCLUSIVE_SKILLS
        if not self.itemsInclusive:
            req.exclusiveFlags |= RPG_DIALOG_REQUIREMENT_EXCLUSIVE_ITEMS
        
        self.sqlObject = req
        
        return req



class DBDialogChoice(DBDict):
    def __init__(self,**args):
        self.classname = 'DialogChoice'
        self.failLine = None
        self.successLine = None
        self.reqs = []
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def addRequirement(self,req):
        self.reqs.append(req)
    def clearRequirements(self):
        self.reqs = []
        
        
    
    #the get functions return from the db
    def getSQLObject(self,dialog):
        return self.create(dialog)
        
    def create(self,dialog):
        if self.sqlObject:
            return self.sqlObject
            
        
            
        choice = DialogChoice()
        dialog.addDialogChoice(choice)
        set = dict(self)
        
        failLine = self.failLine
        if failLine:
            set['failLine']=failLine.getSQLObject(dialog)
        successLine = self.successLine
        if successLine:
            set['successLine']=successLine.getSQLObject(dialog)
            
        
        del set['classname']
        del set['sqlObject']
        del set['reqs']
        
        choice.set(**set)
        
        for r in self.reqs:
            choice.addDialogRequirement(r.getSQLObject())
        
            
        self.sqlObject = choice
        
        return choice
        
class DBZone(DBDict):
    def __init__(self,**args):
        self.classname = 'Zone'
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    
    #the get functions return from the db
    def getSQLObject(name):
        ip = DBDict.getDBDict('Zone','name',name)
        assert ip
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
       
        world = World.byName("TheWorld")
        
        try:
            zone = Zone.byName(self.name)
            zone.missionFile=self.missionFile
            zone.niceName = self.niceName
        except:

            zone = Zone(name=self.name,world=world,missionFile=self.missionFile,niceName = self.niceName)
        
        set = dict(self)

        del set['classname']
        del set['sqlObject']
        
        zone.set(**set)
        
            
        self.sqlObject = zone
        
        return zone

class DBDialogAction(DBDict):
    def __init__(self,**args):
        self.classname = 'DialogAction'
        self.respawn = None
        self.takeItems = []
        self.giveItems = []
        self.checkItems = []
        self.factions = []
        self.checkMinFactions = []
        self.checkMaxFactions = []
        self.trainSkills = []
        self.checkSkills = []
        
        self.giveTin = 0
        self.giveCopper = 0
        self.giveSilver = 0
        self.giveGold = 0
        self.givePlatinum = 0
        self.takeTin = 0
        self.takeCopper = 0
        self.takeSilver = 0
        self.takeGold = 0
        self.takePlatinum = 0
        
        self.journalTopic = ""
        self.journalEntry = ""
        self.journalText = ""
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def addCheckMinFaction(self,faction,amount):
        self.checkMinFactions.append((faction,amount))

    def addCheckMaxFaction(self,faction,amount):
        self.checkMaxFactions.append((faction,amount))
        
    def addTakeItem(self,item,count=1):
        self.takeItems.append((item,count))
        
    def clearTakeItems(self):
        self.takeItems = []

    def clearFactions(self):
        self.factions = []

    def addGiveItem(self,item,count=1):
        self.giveItems.append((item,count))
        
    def clearGiveItems(self):
        self.giveItems = []
    
    def addCheckItem(self,item,count=1):
        self.checkItems.append((item,count))
        
    def clearCheckItems(self):
        self.checkItems = []
        
    def addFaction(self,fname,amount):
        self.factions.append((fname,amount))
    
    def trainSkill(self,skillname):
        if skillname not in self.trainSkills:
            self.trainSkills.append(skillname)
    
    def clearTrainSkills(self):
        self.trainSkills = []
    
    def addCheckSkill(self,skill,minLevel=0):
        if (skill,minLevel) not in self.checkSkills:
            self.checkSkills.append((skill,minLevel))
    
    def clearCheckSkills(self):
        self.checkSkills = []
        
        
    #the get functions return from the db
    def getSQLObject(self,dialog):
        return self.create(dialog)
        
    def create(self,dialog):
        if self.sqlObject:
            return self.sqlObject

        
        action = DialogAction(dialog=dialog)
        
        for titem in self.takeItems:
            itemProto = DBItemProto.getSQLObject(titem[0])
            DialogTakeItem(itemProto=itemProto,dialogAction=action,count = titem[1])
        for citem in self.checkItems:
            itemProto = DBItemProto.getSQLObject(citem[0])
            DialogCheckItem(itemProto=itemProto,dialogAction=action,count = citem[1])
        for gitem in self.giveItems:
            itemProto = DBItemProto.getSQLObject(gitem[0])
            DialogGiveItem(itemProto=itemProto,dialogAction=action,count = gitem[1])
            
        if self.respawn:
            action.respawn = DBSpawn.getSQLObject(self.respawn)
            
        for f in self.factions:
            fname,amount = f
            faction = DBFaction.getSQLObject(fname)
            DialogFaction(dialogAction=action,faction=faction,amount=amount)
            
        for f in self.checkMinFactions:
            fname,amount = f
            faction = DBFaction.getSQLObject(fname)
            DialogCheckMinFaction(dialogAction=action,faction=faction,amount=amount)


        for f in self.checkMaxFactions:
            fname,amount = f
            faction = DBFaction.getSQLObject(fname)
            DialogCheckMaxFaction(dialogAction=action,faction=faction,amount=amount)
        
        for sk in self.trainSkills:
            DialogTrainSkill(dialogAction = action, skill = sk)
        
        for skill,level in self.checkSkills:
            DialogCheckSkill(dialogAction = action,skillName = skill,skillLevel = level)
        
        tin = long(self.giveTin)
        tin += self.giveCopper * 100L
        tin += self.giveSilver * 10000L
        tin += self.giveGold * 1000000L
        tin += self.givePlatinum * 100000000L
        action.giveTin = tin
        tin = long(self.takeTin)
        tin += self.takeCopper * 100L
        tin += self.takeSilver * 10000L
        tin += self.takeGold * 1000000L
        tin += self.takePlatinum * 100000000L
        action.takeTin = tin
        
        if self.journalTopic and self.journalEntry and self.journalText:
            journalEntry = JournalEntry(topic = self.journalTopic,entry = self.journalEntry,text = self.journalText)
            action.journalEntryID = journalEntry.id
        elif self.journalTopic or self.journalEntry or self.journalText:
            traceback.print_exc()
            raise ValueError,"incomplete journal definition for DBDialogAction, not all components of journalTopic, journalEntry and journalText have been defined!"
        
        set = dict(self)
        
        del set['classname']
        del set['sqlObject']
        
        del set['respawn']
        del set['takeItems']
        del set['checkItems']
        del set['giveItems']
        del set['factions']
        del set['checkMinFactions']
        del set['checkMaxFactions']
        del set['trainSkills']
        del set['checkSkills']
        
        del set['giveTin']
        del set['giveCopper']
        del set['giveSilver']
        del set['giveGold']
        del set['givePlatinum']
        del set['takeTin']
        del set['takeCopper']
        del set['takeSilver']
        del set['takeGold']
        del set['takePlatinum']
        
        del set['journalTopic']
        del set['journalEntry']
        del set['journalText']
        
        action.set(**set)
        
            
        self.sqlObject = action
        
        return action
        
        
class DBEffectProto(DBDict):
    def __init__(self,**args):
        self.classname = 'EffectProto'
        self.summonPet = ""
        self.summonItem = ""
        #(stage,var,value)
        self.stats = []
        self.permStats = []
        self.damage = []
        
        self.leechType = ""
        self.leechBegin = 0
        self.leechEnd = 0
        self.leechTick = 0
        self.leechTickRate = 0
        
        self.drainType = ""
        self.drainBegin = 0
        self.drainEnd = 0
        self.drainTick = 0
        self.drainTickRate = 0
        
        self.regenType = ""
        self.regenBegin = 0
        self.regenEnd = 0
        self.regenTick = 0
        self.regenTickRate = 0
        
        self.illusionModel = ""
        self.illusionAnimation = ""
        self.illusionTextureSingle = ""
        self.illusionTextureBody = ""
        self.illusionTextureHead = ""
        self.illusionTextureLegs = ""
        self.illusionTextureHands = ""
        self.illusionTextureFeet = ""
        self.illusionTextureArms = ""
        self.illusionSex = ""
        self.illusionRace = ""
        self.illusionSndProfile = None
        self.illusionSize = 0.0
        
        self.root = False
        self.paralysis = False
        self.levitate = False
        self.waterbreathing = False
        self.resurrection = False
        self.stun = False
        self.sleep = False
        self.charm = False
        self.interrupt = False
        self.banish = False
        self.summonMonster = False
        self.summonAlly = False
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
        
    def addDamage(self,type,amount,stage=RPG_EFFECT_STAGE_GLOBAL):
        if amount < 0:
            amount = -amount
        self.damage.append((stage,type,amount))
        
    def addStat(self,stage,stat,value):
        if stat == 'slow' and value < 0:
            value = -value
        if stat == 'haste' and value < 0:
            value = -value
            
        self.stats.append((stage,stat,value))
        
    def addPermanentStat(self,stat,value):
        self.permStats.append((stat,value))

        
        
    #the get functions return from the db
    def getSQLObject(name):
        #try to create this item proto
        ip = DBDict.getDBDict('EffectProto','name',name)
        assert ip,name
        
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
            
        try:
            proto = EffectProto.byName(self.name)
            for st in proto.stats:
                st.destroySelf()
        except:
            proto = EffectProto(name=self.name)
        
        if self.summonItem:
            proto.summonItem = DBItemProto.getSQLObject(self.summonItem)
        if self.summonPet:
            proto.summonPet = DBSpawn.getSQLObject(self.summonPet)
            
        for st in self.stats:
            EffectStat(stage = st[0],statname=st[1],value=st[2],effectProto=proto)

        for st in self.permStats:
            EffectPermanentStat(statname=st[0],value=st[1],effectProto=proto)

            
        for dmg in self.damage:
            EffectDamage(stage=dmg[0],type=dmg[1],amount=dmg[2],effectProto=proto)
        
        set = dict(self)
        
        del set['classname']
        del set['sqlObject']
        del set['name']
        del set['summonPet']
        del set['summonItem']
        del set['stats']
        del set['permStats']
        del set['damage']
        
        del set['leechType']
        del set['leechBegin']
        del set['leechEnd']
        del set['leechTick']
        del set['leechTickRate']
        
        del set['drainType']
        del set['drainBegin']
        del set['drainEnd']
        del set['drainTick']
        del set['drainTickRate']
        
        del set['regenType']
        del set['regenBegin']
        del set['regenEnd']
        del set['regenTick']
        del set['regenTickRate']
        
        del set['illusionModel']
        del set['illusionAnimation']
        del set['illusionTextureSingle']
        del set['illusionTextureBody']
        del set['illusionTextureHead']
        del set['illusionTextureLegs']
        del set['illusionTextureHands']
        del set['illusionTextureFeet']
        del set['illusionTextureArms']
        del set['illusionSex']
        del set['illusionRace']
        del set['illusionSndProfile']
        del set['illusionSize']
        
        del set['root']
        del set['paralysis']
        del set['levitate']
        del set['waterbreathing']
        del set['resurrection']
        del set['stun']
        del set['sleep']
        del set['charm']
        del set['interrupt']
        del set['banish']
        del set['summonMonster']
        del set['summonAlly']
        
        try: 
            proto.set(**set)
        except:
            traceback.print_exc()
            
            raise RuntimeWarning,self.name
        
        
        if self.leechType:
            proto.leechEffect = EffectLeech(leechType = self.leechType,leechBegin = self.leechBegin,leechEnd = self.leechEnd,leechTick = self.leechTick,leechTickRate = self.leechTickRate,effectProto = proto)
        if self.drainType:
            proto.drainEffect = EffectDrain(drainType = self.drainType,drainBegin = self.drainBegin,drainEnd = self.drainEnd,drainTick = self.drainTick,drainTickRate = self.drainTickRate,effectProto = proto)
        if self.regenType:
            proto.regenEffect = EffectRegen(regenType = self.regenType,regenBegin = self.regenBegin,regenEnd = self.regenEnd,regenTick = self.regenTick,regenTickRate = self.regenTickRate,effectProto = proto)
        
        if self.illusionModel or self.illusionRace:
            proto.illusion = EffectIllusion(illusionModel = self.illusionModel,illusionAnimation = self.illusionAnimation,illusionTextureSingle = self.illusionTextureSingle,illusionTextureBody = self.illusionTextureBody,illusionTextureHead = self.illusionTextureHead,illusionTextureLegs = self.illusionTextureLegs,illusionTextureHands = self.illusionTextureHands,illusionTextureFeet = self.illusionTextureFeet,illusionTextureArms = self.illusionTextureArms,illusionSex = self.illusionSex,illusionRace = self.illusionRace,illusionSndProfile = self.illusionSndProfile,illusionSize = self.illusionSize)
        
        proto.flags = 0    # no inheritance when cloning
        if self.root:
            proto.flags |= RPG_EFFECT_ROOT
        if self.paralysis:
            proto.flags |= RPG_EFFECT_PARALYSIS
        if self.levitate:
            proto.flags |= RPG_EFFECT_LEVITATE
        if self.waterbreathing:
            proto.flags |= RPG_EFFECT_WATERBREATHING
        if self.resurrection:
            proto.flags |= RPG_EFFECT_RESURRECTION
        if self.stun:
            proto.flags |= RPG_EFFECT_STUN
        if self.sleep:
            proto.flags |= RPG_EFFECT_SLEEP
        if self.charm:
            proto.flags |= RPG_EFFECT_CHARM
        if self.interrupt:
            proto.flags |= RPG_EFFECT_INTERRUPT
        if self.banish:
            proto.flags |= RPG_EFFECT_BANISH
        if self.summonMonster:
            proto.flags |= RPG_EFFECT_SUMMONMONSTER
        if self.summonAlly:
            proto.flags |= RPG_EFFECT_SUMMONALLY
        
        
        self.sqlObject = proto
        
        return proto
        
class DBSpellProto(DBDict):
    def __init__(self,**args):
        self.classname = 'SpellProto'
        #(classname,level)
        self.classes = []
        self.effects = []
        self.pnodes = []
        self.particleTextureCasting = ""
        self.particleTextureBegin = ""
        self.spellbookPic = ""
        self.components = []
        self.exclusions = []
        
        self.healing    = False
        self.harmful    = True
        self.aiCast     = True
        self.persistent = True
        self.noAggro    = False
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def addClass(self,klass,level):        
        self.classes.append((klass,level))
    
    def clearClasses(self):        
        self.classes = []
        
    def addEffect(self,effect):
        self.effects.append(effect)
    
    def clearEffects(self):
        self.effects = []
        
    def addExclusion(self,otherName,overwrites=False):
        
        #quietly ignore
        if otherName == self.name:
            return
        
        for e in self.exclusions:
            if e[0]==otherName:
                assert False, "Redundant spell exclusion %s -> %s"%(self.name,otherName)
        
        self.exclusions.append((otherName,overwrites))
        
        
    def clearExclusions(self):
        self.exclusions = []
        
    def addComponent(self,component,count=1):
        self.components.append((component,count))
        
    def clearComponents(self):
        self.components=[]
        
    def addParticleNode(self,node,particle,texture,duration):
        self.pnodes.append((node,particle,texture,duration))
        
    def getDBSpellProto(name):
        return DBDict.getDBDict('SpellProto','name',name)
        
    getDBSpellProto = staticmethod(getDBSpellProto)

        
    #the get functions return from the db
    def getSQLObject(name):
        #try to create this item proto
        ip = DBDict.getDBDict('SpellProto','name',name)
        assert ip
        
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        if not len(self.effects):
            raise ValueError,"DBSpellProto %s has no effects"%self.name
            
        try:
            proto = SpellProto.byName(self.name)
            for cl in proto.classes:
                cl.destroySelf()
            #print dir(proto)
            for eff in proto.effectProtos:
                proto.removeEffectProto(eff)
                
                
        except:
            proto = SpellProto(name=self.name)
            
        #calculate mana
        if not proto.manaCost:
            # else this is a skill or proc which shouldn't use mana at all
            # in special cases, add mana cost in skill definition
            if len(self.classes):
                best = 1
                for cl in self.classes:
                    if cl[1] > best:
                        best = cl[1]
                    
                proto.manaCost = int(best*best*proto.manaScalar)/6
                proto.manaCost+=int(proto.manaCost*float(best)/50.0)
            
            
                if proto.target == RPG_TARGET_PARTY or proto.target==RPG_TARGET_ALLIANCE:
                    proto.manaCost*=2.5
                
                #scale for cast time (this needs to be in the actual spell as a mana scalar, setup by hand)
                #s = 30 - proto.castTime/6
                #if s < 0:
                #    s = 0
                #proto.manaCost+=int(proto.manaCost*(float(s)/15.0))
                
                if proto.manaCost < 6:
                    proto.manaCost = 6
        else:
            proto.manaCost = int(proto.manaCost*proto.manaScalar)
            


        #make a scroll, not sure if this is how we are going to handle this
        if len(self.classes):
            ip = DBItemProto(name="Scroll of %s"%self.name,spellProto = self.name,bitmap = "STUFF/2")
            ip.useMax = 1
            ip.stackMax = 20
            ip.stackDefault = 1
            ip.flags = RPG_ITEM_LITERATURE
        
        level = 1000
        for cl in self.classes:
            if cl[1] < level:
                level = cl[1]
        if level!=1000:
            #assign worth
            tin = level**6+500
            if level > 20:
                tin*=int(level/10)
            ip.worthTin = tin
            
        for cl in self.classes:
            SpellClass(classname=cl[0],level=cl[1],spellProto = proto)
            
        for effect in self.effects:
            proto.addEffectProto(DBEffectProto.getSQLObject(effect))
            
        
        for p in self.pnodes:
            SpellParticleNode(spellProto=proto,node=p[0],particle=p[1],texture=p[2],duration=p[3])

        for c in self.components:
            SpellComponent(spellProto=proto,itemProto=DBItemProto.getSQLObject(c[0]),count=c[1])
            
        for e in self.exclusions:
            SpellExclusion(spellProto = proto,otherProtoName=e[0],overwrites=e[1])
            
        try:
            if not self.duration and self.persistent:
                raise ValueError,"Error: Spell %s is persistent and has 0 duration"%self.name
        except:
            pass
        
        
        set = dict(self)
        
        del set['classname']
        del set['sqlObject']
        del set['name']
        del set['effects']
        del set['classes']
        del set['pnodes']
        del set['components']
        del set['exclusions']
        
        del set['healing']
        del set['harmful']
        del set['aiCast']
        del set['persistent']
        del set['noAggro']
        
        proto.set(**set)
        
        if not self.particleTextureCasting:
            proto.particleTextureCasting = self.spellbookPic
        if not self.particleTextureBegin:
            proto.particleTextureBegin = self.spellbookPic
        
        proto.spellType = RPG_SPELL_NOSPECIAL
        if self.healing:
            proto.spellType |= RPG_SPELL_HEALING
        if self.harmful:
            proto.spellType |= RPG_SPELL_HARMFUL
        if self.aiCast:
            proto.spellType |= RPG_SPELL_AICAST
        if self.persistent:
            proto.spellType |= RPG_SPELL_PERSISTENT
        if self.noAggro:
            proto.spellType |= RPG_SPELL_NOAGGRO
        
        self.sqlObject = proto
        return proto


class DBLootProto(DBDict):
    def __init__(self,**args):
        self.classname = 'LootProto'
        #(name,frequency)
        self.lootItems = []
        
        self.tin = 0
        self.copper = 0
        self.silver = 0
        self.gold = 0
        self.platinum = 0
        
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
    
    
    def addItem(self,itemname,frequency=RPG_FREQ_ALWAYS,flags=0):
        if RPG_BUILD_TESTING:
            frequency = RPG_FREQ_ALWAYS
        self.lootItems.append((itemname,frequency,flags))
    
    
    #the get functions return from the db
    def getSQLObject(self):
        return self.create()
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
       
        loot = LootProto()
        for item in self.lootItems:
            frequency = item[1]
            if RPG_BUILD_TESTING and len(self.lootItems) < 15:
                frequency = RPG_FREQ_ALWAYS
            LootItem(itemProto=DBItemProto.getSQLObject(item[0]),freq = frequency,lootProto = loot,flags = item[2])
        
        tin = long(self.tin)
        tin += self.copper * 100L
        tin += self.silver * 10000L
        tin += self.gold * 1000000L
        tin += self.platinum * 100000000L
        loot.tin = tin
        
        set = dict(self)
        
        del set['classname']
        del set['sqlObject']
        del set['lootItems']
        
        del set['tin']
        del set['copper']
        del set['silver']
        del set['gold']
        del set['platinum']
        
        loot.set(**set)
        
        self.sqlObject = loot
        
        return loot
        
        
"""
class VendorItem(Persistent):
    itemProto = ForeignKey('ItemProto')
    frequency = IntCol(default=RPG_FREQ_ALWAYS)
    count = IntCol(default=1) 
    vendorProtos = RelatedJoin('VendorProto')
    
class VendorProto(Persistent):
    
    markup = FloatCol(default=1.0)
    restockRate = IntCol(default=15) #in realtime minutes, might be nice if this was per item but hey
    vendorItems = RelatedJoin('VendorItem')    
    
    spawns = MultipleJoin('Spawn')
    
    def createVendorInstance(self,mob):
        vi = VendorInstance(self,mob)
        vi.regenerateStock()
        mob.vendor = vi
"""

class DBVendorProto(DBDict):
    def __init__(self,**args):
        self.classname = 'VendorProto'
        #(name,freq,count)
        self.vendorItems = []
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def addItem(self,itemname,frequency = RPG_FREQ_ALWAYS,count = -1):
        self.vendorItems.append((itemname,frequency,count))
    
    
    #the get functions return from the db
    def getSQLObject(name):
        try:
            return VendorProto.byName(name)
        except:
            #try to create this item proto
            ip = DBDict.getDBDict('VendorProto','name',name)
            assert ip, name
            
            return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
       
        set = dict(self)
        
        vendor = VendorProto(name=self.name)
        
        for item in self.vendorItems:
            iproto = DBItemProto.getSQLObject(item[0])
            vi = VendorItem(itemProto = iproto,frequency=item[1],count = item[2])
            vendor.addVendorItem(vi)
        
        del set['classname']
        del set['sqlObject']
        del set['vendorItems']
        
        
        vendor.set(**set)
        
            
        self.sqlObject = vendor
        
        return vendor


class DBClassSkill(DBDict):
    def __init__(self,**args):
        self.classname = 'ClassSkill'
        self.spellProto = ""
        self.type = []
        self.races = []
        self.quests = []
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    def addRaceRequirement(self,race):
        self.races.append(race)
    
    def addQuestRequirement(self,identifier,levelBarrier):
        self.quests.append((identifier,levelBarrier))
        
    #the get functions return from the db
    def getSQLObject(self):
        return self.create()
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
       
        cskill = ClassSkill()
        
        if self.spellProto:
            cskill.spellProto = DBSpellProto.getSQLObject(self.spellProto)
            
        for r in self.races:
            ClassSkillRaceRequirement(classSkill=cskill,race=r)
        
        for qi,ql in self.quests:
            ClassSkillQuestRequirement(classSkill=cskill,choiceIdentifier=qi,levelBarrier=ql)
            
        set = dict(self)
        
        del set['classname']
        del set['sqlObject']
        del set['spellProto']
        del set['type']
        del set['races']
        del set['quests']
        
        cskill.set(**set)
        
        self.sqlObject = cskill
        
        return cskill


class DBClassProto(DBDict):
    def __init__(self,**args):
        self.classname = 'ClassProto'
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        self.skills = []
        
    def addClassSkill(self,skill,forceReplace = False):
        for s in self.skills[:]:
            if s.skillname == skill.skillname:
                if forceReplace:
                    self.skills.remove(s)
                    self.skills.append(skill)
                    return
                else:
                    return
                    
        self.skills.append(skill)
        
    
    #the get functions return from the db
    def getSQLObject(name):
        ip = DBDict.getDBDict('ClassProto','name',name)
        assert ip
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
            
        try:
            proto = ClassProto.byName(self.name)
        except:
            proto = ClassProto(name=self.name)

        assert len(proto.skills) == 0

        for skill in self.skills:
            proto.addClassSkill(skill.getSQLObject())
        
        set = dict(self)

        del set['classname']
        del set['sqlObject']
        del set['skills']
        
        proto.set(**set)
        
                    
        self.sqlObject = proto
        
        return proto
    
    
class DBFactionRelation(DBDict):
    def __init__(self,**args):
        self.classname = 'FactionRelation'
        self.faction = None
        self.otherFaction = None
        self.relation = 0

        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
        
    #the get functions return from the db
    def getSQLObject(self):
        return self.create()
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        f1 = DBFaction.getSQLObject(self.faction)
        f2 = DBFaction.getSQLObject(self.otherFaction)
        
        self.sqlObject = FactionRelation(faction=f1,otherFaction=f2,relation = self.relation)

        return self.sqlObject


class DBFaction(DBDict):
    def __init__(self,**args):
        self.classname = 'Faction'
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override
    
    #the get functions return from the db
    def getSQLObject(name):
        ip = DBDict.getDBDict('Faction','name',name)
        assert ip,"Faction %s"%name
        return ip.create()
            
    getSQLObject = staticmethod(getSQLObject)
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
            
        try:
            faction = Faction.byName(self.name)
        except:
            faction = Faction(name=self.name)

        
        set = dict(self)

        del set['classname']
        del set['name']
        del set['sqlObject']
        
        faction.set(**set)
   
        self.sqlObject = faction
        
        return faction

"""    
class RecipeIngredient(Persistent):
    recipe = ForeignKey('Recipe')
    itemProto = ForeignKey('ItemProto')
    count = IntCol(default=1)
    
class Recipe(Persistent):
    ingredients = MultipleJoin('RecipeIngredient')
    skillname = StringCol()
    skillLevel = IntCol()
    
    filterClass = StringCol(default="")
    filterRealm = IntCol(default=-1)
    filterRace = StringCol(default="")
    filterLevelMin = IntCol(default=0)
    filterLevelMax = IntCol(default=1000)
"""

class DBRecipe(DBDict):
    def __init__(self,**args):
        self.classname = 'Recipe'
        
        self.name = ""
        self.skillname = ""
        self.skillLevel = 1
        self.filterClass = ""
        self.filterRealm = -1
        self.filterRace = ""
        self.filterLevelMin = 0
        self.filterLevelMax = 1000        
        
        self.craftItem = ""
        self.craftSound = ""
        
        self.costPP = 0
        self.costGP = 0
        self.costSP = 0
        self.costCP = 0
        self.costTP = 0
        
        self.ingredients = []
        DBDict.__init__(self,**args) #<--- comes after defaults, so that the src can override        
        
    def clearIngredients(self):
        self.ingredients = []

    def addIngredient(self,name,count=1):
        self.ingredients.append((name,count))

        
    #the get functions return from the db
    def getSQLObject(self):
        return self.create()
        
    def create(self):
        if self.sqlObject:
            return self.sqlObject
        
        tin = long(self.costTP)
        tin += self.costCP*100L
        tin += self.costSP*10000L
        tin += self.costGP*1000000L
        tin += self.costPP*100000000L
        
        craftedItemProto = DBItemProto.getSQLObject(self.craftItem)
        try:
            self.sqlObject = r = Recipe(name = self.name,skillname=self.skillname,skillLevel=self.skillLevel,filterClass=self.filterClass,
            filterRealm=self.filterRealm,filterRace=self.filterRace,filterLevelMin = self.filterLevelMin,filterLevelMax = self.filterLevelMax,
            craftedItemProto = craftedItemProto,craftSound = self.craftSound,
            costTP = tin)
        except:
            traceback.print_exc()
            raise self.name
            
        
        #ingredient
        for i in self.ingredients:
            ip = itemProto = DBItemProto.getSQLObject(i[0])
            if ip.useMax > 1 and i[1] > 1:
                raise ValueError,"Ingredient %s of recipe %s has several charges and more than one item is required for recipe. Charges on ingredients represent their crafting durability, if it can contain more than one charge."%(i[0],self.name)
                traceback.print_exc()
            
            RecipeIngredient(recipe=r,itemProto=ip,count=i[1])
            
        

        return self.sqlObject


