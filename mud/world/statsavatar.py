# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

from mud.common.permission import User,Role
from mud.common.avatar import Avatar
import traceback
import time



class StatsAvatar(Avatar):
    def __init__(self,username,role,mind):
        Avatar.__init__(self,username,role,mind)
        self.username = username
        self.mind = mind
        from mud.world.theworld import World
        self.world = World.byName("TheWorld")

        
    def perspective_getStats(self):
        t = time.time()
        from mud.common.persistent import Persistent        
        connection = Persistent._connection
        cursor = connection.getConnection().cursor()
        results = {}
        
        #TODO, filter out immortals
        
        #HIGHEST LEVEL OVERALL
        try:
            cursor.execute("select player_name,name,plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal,realm from spawn where character_id <> 0 order by plevel desc limit 100;")
            results["levels"]=levels = []
            for r in cursor.fetchall():
                playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm = r                
                levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm))
        except:
            traceback.print_exc()
        
        #TOTAL LEVELS OVERALL
        try:
            cursor.execute("select player_name,name,sum((plevel+slevel+tlevel)), plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal,realm from spawn where character_id <> 0 GROUP BY name ORDER BY sum((plevel+slevel+tlevel)) desc limit 100;")
            results["totallevels"]=levels = []
            for r in cursor.fetchall():
                playerName,name,total,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm = r
                levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm))
        except:
            traceback.print_exc()

        #HIGHEST LEVEL FOL
        try:
            cursor.execute("select player_name,name,plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal from spawn where character_id <> 0 and realm = 1 order by plevel desc limit 100;")
            results["follevels"]=levels = []
            for r in cursor.fetchall():
                playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal = r                
                levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal))
        except:
            traceback.print_exc()

            
        #TOTAL LEVELS FOL
        try:
            cursor.execute("select player_name,name,sum((plevel+slevel+tlevel)), plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal from spawn where character_id <> 0 and realm = 1 GROUP BY name ORDER BY sum((plevel+slevel+tlevel)) desc limit 100;")
            results["foltotallevels"]=levels = []
            for r in cursor.fetchall():
                playerName,name,total,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal = r
                levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal))
        except:
            traceback.print_exc()
        
        #HIGHEST LEVEL MOD
        try:
            cursor.execute("select player_name,name,plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal from spawn where character_id <> 0 and realm = 2 order by plevel desc limit 100;")
            results["modlevels"]=levels = []
            for r in cursor.fetchall():
                playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal = r                
                levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal))
        except:
            traceback.print_exc()

            
        #TOTAL LEVELS MOD
        try:
            cursor.execute("select player_name,name,sum((plevel+slevel+tlevel)), plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal from spawn where character_id <> 0 and realm = 2 GROUP BY name ORDER BY sum((plevel+slevel+tlevel)) desc limit 100;")
            results["modtotallevels"]=levels = []
            for r in cursor.fetchall():
                playerName,name,total,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal = r
                levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal))
        except:
            traceback.print_exc()
            
            
        #HIGHEST CLASSES
        classes = ["Paladin","Cleric","Necromancer","Tempest","Wizard","Shaman","Monk","Barbarian","Warrior","Assassin","Revealer","Druid","Ranger","Bard","Thief","Doom Knight"]
        for cl in classes:
            try:
                cursor.execute("select player_name,name,plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal,realm from spawn where character_id <> 0 and pclass_internal = '%s' order by plevel desc limit 100;"%cl)
                results["%slevels"%cl.lower()]=levels = []
                for r in cursor.fetchall():
                    playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm = r                
                    levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm))
            except:
                traceback.print_exc()

        #Richest Players FOL
        try:
            cursor.execute("select public_name,light_tin,light_copper,light_silver,light_gold,light_platinum,sum((light_tin+light_copper*100+light_silver*10000+light_gold*1000000+light_platinum*100000000)) from player GROUP BY public_name order by sum((light_tin+light_copper*100+light_silver*10000+light_gold*1000000+light_platinum*100000000)) desc limit 100;")
            results["folrichest"]=levels = []
            for r in cursor.fetchall():
                playerName,tin,copper,silver,gold,platinum,total = r                
                levels.append((playerName,tin,copper,silver,gold,platinum))
        except:
            traceback.print_exc()
        
        #Richest Players MOD
        try:
            cursor.execute("select public_name,darkness_tin,darkness_copper,darkness_silver,darkness_gold,darkness_platinum,sum((darkness_tin+darkness_copper*100+darkness_silver*10000+darkness_gold*1000000+darkness_platinum*100000000)) from player GROUP BY public_name order by sum((darkness_tin+darkness_copper*100+darkness_silver*10000+darkness_gold*1000000+darkness_platinum*100000000)) desc limit 100;")
            results["modrichest"]=levels = []
            for r in cursor.fetchall():
                playerName,tin,copper,silver,gold,platinum,total = r                
                levels.append((playerName,tin,copper,silver,gold,platinum))
        except:
            traceback.print_exc()
            
        #highest presence
        try:
            cursor.execute("select player_name,name,plevel,slevel,tlevel,pclass_internal,sclass_internal,tclass_internal,realm,pre_base from spawn where character_id <> 0 order by pre_base desc limit 100;")
            results["presence"]=levels = []
            for r in cursor.fetchall():
                playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm,preBase = r                
                levels.append((playerName,name,plevel,slevel,tlevel,pclassInternal,sclassInternal,tclassInternal,realm,preBase))
        except:
            traceback.print_exc()
        cursor.close()
        
        
        
        return results
            
        
        
        
        
        
        
        
 