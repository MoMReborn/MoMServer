# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details


from mud.common.avatar import Avatar
from mud.world.item import ItemInstance,Item
from mud.world.player import Player
from mud.world.character import Character,CharacterSpell,CharacterVaultItem
from mud.world.theworld import World
from mud.world.spawn import Spawn,SpawnResistance,SpawnStat
from mud.world.party import Party
from mud.world.spell import SpellClass,Spell
from mud.world.command import DoCommand
from mud.world.repair import RepairItem,RepairAll,RepairParty
from mud.world.zone import Zone
from mud.world.messages import GameMessage
from defines import *
from core import *
from sqlobject import *
from twisted.internet import reactor
from alliance import Alliance
from traceback import print_stack,print_exc
from time import time
from cPickle import dumps,loads
from base64 import encodestring,decodestring
from mud.worldserver.charutil import ExtractPlayer,InstallCharacterBuffer
from mud.gamesettings import GAMENAME
from race import GetRaceGraphics


#for jelly
from mud.world.shared.worlddata import CharacterInfo,ZoneConnectionInfo
from mud.world.shared.playdata import RootInfo


#also query
class PlayerAvatar(Avatar):
    
    def __init__(self,username,role,mind):
        Avatar.__init__(self,username,role,mind)
        self.mind = mind
        self.username = username
        self.player = Player.byPublicName(username)
        self.player.role = role
        self.player.reset()
        self.player.mind = mind
        self.world = World.byName("TheWorld")
        self.player.world = self.world
        self.syncTime()
        self.player.avatar = self

        self.world.playerJoinWorld(self.player)
        
        self.charInfos = []


    def perspective_logout(self):
        self.logout()


    def logout(self):
        player = self.player

        if not player:
            return

        player.avatar = None

        if player.loggingOut:
            return

        if self.tickSyncTime:
            try:
                self.tickSyncTime.cancel()
            except:
                pass
            self.tickSyncTime = None

        player.loggingOut = True
        player.logout()
        player.loggingOut = False

        self.player = None


    def syncTime(self):
        self.mind.callRemote("syncTime",self.world.time.hour,self.world.time.minute)
        self.tickSyncTime = reactor.callLater(60,self.syncTime)
        

    def gotCheckCharacterName(self,result,newchar):
        if not result:
            return self.newCharacter(newchar)
        return (-1,"That name is taken, please choose another")
        
    
    def gotCheckCharacterNameError(self,result):
        return (-1,"There was an error creating this character")
        
    def perspective_newCharacter(self,newchar):
        from cserveravatar import AVATAR
        
        if RPG_BUILD_DEMO and not self.player.premium:
            nc = 0
            names = []
            if self.player.cserverInfos:
                for cinfo in self.player.cserverInfos:
                    if cinfo.realm != RPG_REALM_MONSTER:
                        nc+=1
                        names.append(cinfo.name)
                
                
            for c in self.player.characters:
                if c.spawn.realm != RPG_REALM_MONSTER and c.spawn.name not in names:
                    nc+=1
            if nc>=3:
                return (-1,"You may have 3 characters in the Minions of Mirth Free Version.  The Premium Version allows up to 24 characters.  Please see www.prairiegames.com for ordering information.",None)

        if AVATAR:
            d = AVATAR.mind.callRemote("checkCharacterName",newchar.name)
            d.addCallback(self.gotCheckCharacterName,newchar)
            d.addErrback(self.gotCheckCharacterNameError)
            return d
        return self.newCharacter(newchar)
    
    
    def newCharacter(self,newchar):
        if not self.player.world.singlePlayer:
            nc = 0
            if self.player.cserverInfos:
                nc = len(self.player.cserverInfos)

            for c in self.player.characters:
                if c.spawn.realm != RPG_REALM_MONSTER:
                    nc+=1
            if nc >=24:
                return (-1,"The maximum characters on this server is 24.",None)
                
            
        #does character already exist?
        try:
            char = Character.byName(newchar.name)
        except:
            pass
        else:
            return (-1,"That character name is taken.",None)
            
        try:
            s = Spawn.byName(newchar.name)
        except:
            pass
        else:
            return (-1,"That character name is invalid.",None)
        
        
        rg = GetRaceGraphics()
        size = 1.0
        for ri in rg:
            if ri.name == newchar.race:
                if newchar.sex == "Male":
                    size = ri.size_male
                    animation = ri.animation_male
                    if newchar.look == 0:
                        model = ri.model_thin_male
                    elif newchar.look == 1:
                        model = ri.model_fit_male
                    else:
                        model = ri.model_heavy_male
                else:
                    size = ri.size_female
                    animation = ri.animation_female
                    if newchar.look == 0:
                        model = ri.model_thin_female
                    elif newchar.look == 1:
                        model = ri.model_fit_female
                    else:
                        model = ri.model_heavy_female
                break
        
        spawn = Spawn(name=newchar.name,race=newchar.race,pclassInternal = newchar.klass,plevel = 1,model=model,scale=size,radius=2,vocalSet="C")
        spawn.realm = newchar.realm
        
        spawn.sex = newchar.sex

        #fix this BS, score should be coming from world server and only adj being sent
        spawn.strBase = newchar.scores['STR'] + newchar.adjs['STR']
        spawn.dexBase = newchar.scores['DEX'] + newchar.adjs['DEX'] 
        spawn.refBase = newchar.scores['REF'] + newchar.adjs['REF'] 
        spawn.agiBase = newchar.scores['AGI'] + newchar.adjs['AGI'] 
        spawn.wisBase = newchar.scores['WIS'] + newchar.adjs['WIS'] 
        spawn.bdyBase = newchar.scores['BDY'] + newchar.adjs['BDY'] 
        spawn.mndBase = newchar.scores['MND'] + newchar.adjs['MND'] 
        spawn.mysBase = newchar.scores['MYS'] + newchar.adjs['MYS'] 

        
        
        char = Character(player=self.player,name=newchar.name,spawn=spawn,portraitPic = newchar.portraitPic)
        spawn.character = char
        spawn.playerName = self.player.publicName
                    
        if newchar.sex == 'Male':
            ret = (0,"%s has been created.  He awaits your command!"%newchar.name)
        else:
            ret = (0,"%s has been created.  She awaits your command!"%newchar.name)
            
        char.addStartingGear()
        char.backupItems()
        
        #send off the character
        from cserveravatar import AVATAR
        if AVATAR:
            publicName,pbuffer,cbuffer,cvalues = ExtractPlayer(self.player.publicName,self.player.id,char.id,False)                
            pbuffer = encodestring(dumps(pbuffer, 2))
            if cbuffer:
                cbuffer = encodestring(dumps(cbuffer, 2))

            AVATAR.mind.callRemote("savePlayerBuffer",publicName,pbuffer,cbuffer,cvalues)
            
            # Clean up the character in the running database.
            # Everything has been saved off and character will
            #  be queried from player buffer again if needed.
            char.destroySelf()

        return ret


    def gotCheckMonsterName(self,result,mname,mspawn):
        if not result:
            return self.newMonster(mname,mspawn)
        return (-1,"That name is taken, please chose another")
        
    
    def gotCheckMonsterNameError(self,result):
        return (-1,"There was an error creating this monster")
    
    
    def perspective_newMonster(self,mname,mspawn):
        from cserveravatar import AVATAR
        
        if RPG_BUILD_DEMO and not self.player.premium:
            nc = 0
            names = []
            if self.player.cserverInfos:
                for cinfo in self.player.cserverInfos:
                    if cinfo.realm == RPG_REALM_MONSTER:
                        nc+=1
                        names.append(cinfo.name)

            for c in self.player.characters:
                if c.spawn.realm == RPG_REALM_MONSTER and c.spawn.name not in names:
                    nc+=1
            if nc >=1:
                return (-1,"You may have 1 monster in the Minions of Mirth Free Version.  The Premium Version allows up to 10 monsters.  Please see www.prairiegames.com for ordering information.",None)
            
        if RPG_BUILD_DEMO and not self.player.premium:
            try:
                src = Spawn.byName(mspawn)
            except:
                return (-1,"That's odd no spawn.",None)
            
            if src.plevel > 20:
                return (-1,"You may create monsters greater than level 20 with the Minions of Mirth Premium Edition.  Please see www.prairiegames.com for ordering information.",None)
                    

        

        if AVATAR:
            
            level = 0
            if self.player.cserverInfos:
                for cinfo in self.player.cserverInfos:
                    if cinfo.levels[0] > level:
                        level = cinfo.levels[0]
                        
            for c in self.player.characters:
                if c.spawn.plevel > level:
                    level = c.spawn.level

            try:
                src = Spawn.byName(mspawn)
            except:
                return (-1,"That's odd no spawn.",None)
            
            if src.plevel > level:
                return (-1,"You must have a MoD or FoL character of level %i or higher to create this monster."%src.plevel,None)
            
            
            d = AVATAR.mind.callRemote("checkCharacterName",mname)
            d.addCallback(self.gotCheckMonsterName,mname,mspawn)
            d.addErrback(self.gotCheckMonsterNameError)
            return d
        return self.newMonster(mname,mspawn)

    def newMonster(self,mname,mspawn):
        #does character already exist?
        
        if not self.player.world.singlePlayer:
            nc = 0
            for c in self.player.characters:
                if c.spawn.realm == RPG_REALM_MONSTER:
                    nc+=1
                
            if nc >=10:
                return (-1,"The maximum monsters on this server is 10.",None)

        try:
            p = Player.byPublicName(mname)
        except:
            pass
        else:
            return (-1,"That character name is taken.",None)

        try:
            p = Player.byFantasyName(mname)
        except:
            pass
        else:
            return (-1,"That character name is taken.",None)


        try:
            char = Character.byName(mname)
        except:
            pass
        else:
            return (-1,"That character name is taken.",None)
            
        try:
            s = Spawn.byName(mname)
        except:
            pass
        else:
            return (-1,"That character name is invalid.",None)

        try:
            src = Spawn.byName(mspawn)
        except:
            return (-1,"That's odd no spawn.",None)

        spawn = Spawn(name=mname,pclassInternal = src.pclassInternal,plevel = 1,model="")
        for ncol in Spawn.sqlmeta._columns:
            if ncol.name != "id" and ncol.name!="name":
                setattr(spawn,ncol.name,getattr(src,ncol.name))
        
        spawn.difficultyMod = 1.0
        spawn.healthMod = 1.0
        spawn.damageMod = 1.0
        spawn.offenseMod = 1.0
        spawn.defenseMod = 1.0
        
        char = Character(player=self.player,name=mname,spawn=spawn,portraitPic = "p033")
        spawn.character = char
        spawn.playerName = self.player.publicName
        
        if spawn.sex == 'Male':
            ret = (0,"%s has been created.  He awaits your command!"%mname)
        elif spawn.sex == 'Female':
            ret = (0,"%s has been created.  She awaits your command!"%mname)
        else:
            ret = (0,"%s has been created.  It awaits your command!"%mname)
            
        #char.addMonsterGear()
        
        # spells
        qspells = list(SpellClass.select(OR(AND(SpellClass.q.classname == spawn.pclassInternal,SpellClass.q.level <= spawn.plevel),AND(SpellClass.q.classname == spawn.sclassInternal,SpellClass.q.level <= spawn.slevel),AND(SpellClass.q.classname == spawn.tclassInternal,SpellClass.q.level <= spawn.tlevel))))
        sprotos = frozenset([sc.spellProto for sc in sorted(qspells, key=lambda obj:obj.level)])
        
        for slot,sproto in enumerate(sprotos):
            CharacterSpell(character=char,spellProto=sproto,slot=slot,recast=0)
        
        #just make sure    
        spawn.realm = RPG_REALM_MONSTER 
        spawn.template = mspawn
        
        pneeded = 0
        sneeded = 0
        tneeded = 0
        if spawn.plevel > 1:
            pneeded = (spawn.plevel-1)*(spawn.plevel-1)*100L*char.pxpMod
        if spawn.slevel > 1:
            sneeded = (spawn.slevel-1)*(spawn.slevel-1)*100L*char.sxpMod
        if spawn.tlevel > 1:
            tneeded = (spawn.tlevel-1)*(spawn.tlevel-1)*100L*char.txpMod
        
        char.xpPrimary = int(pneeded+1)
        char.xpSecondary = int(sneeded+1)
        char.xpTertiary = int(tneeded+1)
        
        base = spawn.plevel*10+100
        spawn.strBase = base
        spawn.dexBase = base
        spawn.refBase = base
        spawn.agiBase = base
        spawn.wisBase = base
        spawn.bdyBase = base
        spawn.mndBase = base
        spawn.mysBase = base
        
        char.advancementLevelPrimary = spawn.plevel
        for i in xrange(2,char.advancementLevelPrimary):
            points = int(float(i) / 2.0)
            if points < 5:
                points = 5
            char.advancementPoints += points
        char.advancementLevelSecondary = spawn.slevel
        for i in xrange(2,char.advancementLevelSecondary):
            points = int(float(i) / 2.0)
            if points < 3:
                points = 3
            char.advancementPoints += points
        char.advancementLevelTertiary = spawn.tlevel
        for i in xrange(2,char.advancementLevelTertiary):
            points = int(float(i) / 2.0)
            if points < 1:
                points = 1
            char.advancementPoints += points
        spawn.flags |= RPG_SPAWN_MONSTERADVANCED
        
        #spawn stats and resists
        for resist in src.resists:
            SpawnResistance(spawn=spawn,resistType=resist.resistType,resistAmount=resist.resistAmount)
        for stat in src.spawnStats:
            s=SpawnStat(spawn=spawn,statname=stat.statname,value=stat.value)
            spawn.spawnStats.append(s)

        #send off the character
        from cserveravatar import AVATAR
        if AVATAR:
            publicName,pbuffer,cbuffer,cvalues = ExtractPlayer(self.player.publicName,self.player.id,char.id,False)                
            pbuffer = encodestring(dumps(pbuffer, 2))
            if cbuffer:
                cbuffer = encodestring(dumps(cbuffer, 2))
            AVATAR.mind.callRemote("savePlayerBuffer",publicName,pbuffer,cbuffer,cvalues)
            
            # Clean up the character in the running database.
            # Everything has been saved off and character will
            #  be queried from player buffer again if needed.
            char.destroySelf()

        return ret
    
    
    def gotDeleteCharacter(self,result):
        if result == False:
            return (-1,"There was an error deleting this character")
        
        return (0,"%s has been deleted."%result)
    
    
    def gotDeleteCharacterError(self,result):
        return (-1,"There was an error deleting this character")
    
    
    def perspective_deleteCharacter(self,cname):
        from cserveravatar import AVATAR
        if not AVATAR:
            # Does character to be deleted exist?
            try:
                char = Character.byName(cname)
            except:
                return (-1,"No character named %s."%cname)
            
            if char.player != self.player:
                return (-1,"Hack attempt!")
            
            char.destroySelf()
            
            return (0,"%s has been deleted."%cname)
        else:
            try:
                char = Character.byName(cname)
                if char.player != self.player:
                    return (-1,"There was an error deleting %s"%cname)
                char.destroySelf()
            except:
                pass
            
            self.player.cserverInfos = [n for n in self.player.cserverInfos if n.name != cname]
            
            try:
                d = AVATAR.mind.callRemote("deleteCharacter",self.player.publicName,cname)
                d.addCallback(self.gotDeleteCharacter)
                d.addErrback(self.gotDeleteCharacterError)
                return d
            except:
                return (-1,"There was an error deleting %s"%cname)
    
    
    def gotCharacterInfos(self,result):
        cinfos = []
        mspawns = []
        for ms in self.player.monsterSpawns:
            mspawns.append(ms.spawn)

        names = []
        for cname,cvalues in result.iteritems():
            names.append(cname)
            name,race,pclass,sclass,tclass,plevel,slevel,tlevel,realm,rename = cvalues
            cinfo = CharacterInfo()
            cinfo.status = "Alive"
            cinfo.name = str(cname)
            cinfo.race = str(race)
            cinfo.realm = realm
            cinfo.klasses.append(str(pclass))
            cinfo.levels.append(plevel)
            cinfo.newCharacter = False
            cinfo.rename = rename
            cinfos.append(cinfo)
            
        self.player.cserverInfos  = cinfos[:]
  
        #any that we have made on the server (new character)
        for c in self.player.characters:
            if c.name not in names:
                cinfo = CharacterInfo(c)
                cinfo.newCharacter = True
                cinfos.append(cinfo)

        self.charInfos = cinfos
        return cinfos,mspawns,1
    
    def gotRenameCheckCharacterName(self,result,c,newname):
        if result==0:
            c.rename = 0
            c.name = newname
            return (0,"Character renamed")
        return (-1,"There was a problem renaming this character.  It's possible that the name is taken.  Please try another name or try again later.")
        
    
    def gotRenameCheckCharacterNameError(self,result):
        return (-1,"There was an error renaming this character.")

       
    def perspective_renameCharacter(self,oldname,newname):
        for c in self.charInfos:
            if not c.rename:
                continue
            if c.name == oldname:
                from cserveravatar import AVATAR
                d = AVATAR.mind.callRemote("renameCharacter",oldname,newname)
                d.addCallback(self.gotRenameCheckCharacterName,c,newname)
                d.addErrback(self.gotRenameCheckCharacterNameError)
                return d

        return (-1,"There was an error renaming this character.")        
        
    
    def gotCharacterInfosError(self,result):
        #error!
        return [],[],1
    
    def perspective_queryCharacters(self):
        from cserveravatar import AVATAR
        if not AVATAR:
            cinfos = []
            mspawns = []
            for ms in self.player.monsterSpawns:
                mspawns.append(ms.spawn)
            for c in self.player.characters:
                cinfo = CharacterInfo(c)
                cinfos.append(cinfo)
            return cinfos,mspawns,CoreSettings.MAXPARTY
        else:
            try:
                d = AVATAR.mind.callRemote("getCharacterInfos",self.player.publicName)
                d.addCallback(self.gotCharacterInfos)
                d.addErrback(self.gotCharacterInfosError)
                return d
            except:
                #error!
                print "ERROR!"
                return [],[],1
            
            
    def gotCharacterBuffer(self,cbuffer,party,simPort,simPassword):
        if cbuffer:
            cbuffer = loads(decodestring(cbuffer))
            InstallCharacterBuffer(self.player.id,party[0],cbuffer)
        self.enterWorld(party,simPort,simPassword)
        
    def playerJumped(self,result):        
        try:
            self.mind.broker.transport.loseConnection()
        except:
            pass
        self.logout()
        
        
        
    def playerTransfered(self,result,party):
        wip,wport,wpassword,zport,zpassword = result
        d = self.mind.callRemote("jumpServer",wip,wport,wpassword,zport,zpassword,party)
        d.addCallback(self.playerJumped)
        d.addErrback(self.playerJumped)

    def gotTransferCharacterBuffer(self,cbuffer,party,zoneName):
        from cserveravatar import AVATAR
        self.player.transfering = True
        p = self.player
        guildInfo = (p.guildName,p.guildInfo,p.guildMOTD,p.guildRank)
        d = AVATAR.mind.callRemote("transferPlayer",self.player.publicName,None,party[0],cbuffer,zoneName,None,self.player.publicName,guildInfo)
        d.addCallback(self.playerTransfered,party)
        return d
    
    
    def perspective_jumpIntoWorld(self, cname):
        self.enterWorld([cname],None,None)
        #fill charInfos
        self.perspective_queryCharacters()
    
    
    def perspective_enterWorld(self,party,simPort, simPassword):
        from cserveravatar import AVATAR
        if not AVATAR:
            self.enterWorld(party,simPort,simPassword)
            return
        
        #alright, we need to figure out what zone we are going to so we can pick a zone cluster
        cname = party[0]
        newc = False
        player = self.player
        
        for c in self.charInfos:
            if cname == c.name:
                newc = c.newCharacter
                if c.realm == RPG_REALM_DARKNESS:
                    zone = self.player.darknessLogZone.name
                elif c.realm == RPG_REALM_MONSTER:
                    zone = self.player.monsterLogZone.name
                elif c.realm == RPG_REALM_LIGHT:
                    zone = self.player.logZone.name
                else:
                    raise "Unknown Realm!"
                
        if zone in self.world.staticZoneNames:
            #we're on the right world server already            
            d = AVATAR.mind.callRemote("getCharacterBuffer",self.player.publicName,party[0])
            d.addCallback(self.gotCharacterBuffer,party,simPort,simPassword)
            return d
        
        #we need to transfer to another server
        if newc:
            #this is a new character and so we need to extract the player/character and transfer it
            char = Character.byName(cname)
            publicName,pbuffer,cbuffer,cvalues = ExtractPlayer(player.publicName,player.id,char.id,False)
            self.player.transfering = True
            pbuffer = encodestring(dumps(pbuffer, 2))
            cbuffer = encodestring(dumps(cbuffer, 2))
            p = self.player
            guildInfo = (p.guildName,p.guildInfo,p.guildMOTD,p.guildRank)
            d = AVATAR.mind.callRemote("transferPlayer",player.publicName,pbuffer,cname,cbuffer,zoneName,cvalues,self.player.publicName,guildInfo)
            d.addCallback(self.playerTransfered,party)
        else:
            #we just need to transfer servers
            d = AVATAR.mind.callRemote("getCharacterBuffer",self.player.publicName,party[0])
            d.addCallback(self.gotTransferCharacterBuffer,party,zone)
            return d

        return 
            
    def enterWorld(self,party,simPort,simPassword):
        from cserveravatar import AVATAR
    
        #zone is an instance
        
        #if we are logging in with all dead characters, it's back to our bind point for us
        alldead = True
        
        chars = []
        for p in party:
            c = Character.byName(p)
            chars.append(c)
            if not c.dead:
                alldead = False
                break
        
        c = chars[0]
        
        #lame, should have gone with realm
        # (working on removing darkness and monster flags in favor of realm - Llarlen)
        self.player.darkness = False
        self.player.monster = False
        if c.spawn.realm == RPG_REALM_DARKNESS:
            self.player.darkness = True
        elif c.spawn.realm == RPG_REALM_MONSTER:
            self.player.monster = True
        
        self.player.charName = c.name
        self.player.realm = c.spawn.realm
        
        if alldead:
            for c in chars:
                c.dead = False
                c.health = -999999
                c.stamina = -999999
                c.mana = -999999
            if self.player.darkness:
                self.player.darknessLogTransformInternal = self.player.darknessBindTransformInternal
                self.player.darknessLogZone = self.player.darknessBindZone
            elif self.player.monster:
                self.player.monsterLogTransformInternal = self.player.monsterBindTransformInternal
                self.player.monsterLogZone = self.player.monsterBindZone
            else:
                self.player.logTransformInternal = self.player.bindTransformInternal
                self.player.logZone = self.player.bindZone
        
        zone = self.world.playerSelectZone(self,simPort,simPassword)
        if not zone:
            return
        
        print "EnterWorld",zone.ip,self.mind.broker.transport.getPeer().host
        ip = zone.ip
        if zone.owningPlayer == self.player:
            #we are being told to host, what about people sharing an IP?
            ip = '127.0.0.1'
        
        self.player.loggingOut = False
        self.player.cursorItem = None
        self.player.simPort = simPort
        self.player.simPassword = simPassword
            
        zconnect = ZoneConnectionInfo()
        zconnect.ip = ip
        zconnect.password = zone.password
        zconnect.port = zone.port
        zconnect.niceName = zone.zone.niceName
        zconnect.missionFile = zone.zone.missionFile
        zconnect.instanceName = zone.name
        
        zone.submitPlayer(self.player,zconnect)
        
        
        
        #assemble the party in preparation
        self.player.party = Party()
        self.player.party.assemble(self.player,party)
            
        self.player.updateKOS()
        
        if AVATAR:
            if self.masterPerspective.avatars.has_key("ImmortalAvatar"):
                for c in self.player.party.members:
                    c.mob.aggroOff = True
        
        #if we are logging in with all dead character
        
        self.player.rootInfo = RootInfo(self.player,self.player.party.charInfos)
        self.mind.callRemote("setRootInfo",self.player.rootInfo,time()-self.player.world.pauseTime)
        
        if self.player.cursorItem:
            self.mind.callRemote("setCursorItem",self.player.cursorItem.itemInfo)
            
        
        if not Player.remoteLeaderNames.has_key(self.player.publicName):
            self.player.alliance = Alliance(self.player)
        else:
            rln = Player.remoteLeaderNames[self.player.publicName]
            del Player.remoteLeaderNames[self.player.publicName]
        
            #make sure we are still in this alliance 
            found = False
            try:
                a = Alliance.masterAllianceInfo[rln]
                for pname,cname in a:
                    if pname == self.player.publicName:
                        found = True
                        break
            except KeyError:
                pass
            if not found:
                self.player.alliance = Alliance(self.player)
            else:
                found = False
                for p in self.world.activePlayers:
                    if p == self.player:
                        continue
                    if not p.alliance:
                        continue
                    
                    if p.alliance.remoteLeaderName == rln:
                        found = True
                        self.player.alliance = p.alliance
                        if p.alliance.remoteLeaderName == self.player.publicName:
                            p.alliance.leader = self.player
                            p.alliance.members.insert(0,self.player)
                        else:
                            p.alliance.members.append(self.player)
                        self.player.alliance.setupForPlayer(self.player)
                        break
                if not found:
                    self.player.alliance = Alliance(self.player,rln)
        
        #at this time, the player mind takes over
        
        self.player.sendGameText(RPG_MSG_GAME_GLOBAL,r'Welcome to %s!\n'%GAMENAME)
        
        if CoreSettings.MOTD:
            self.player.sendGameText(RPG_MSG_GAME_GLOBAL,r'Server MOTD: '+CoreSettings.MOTD+r'\n')
        
        if self.player.guildMOTD:
            self.player.sendGameText(RPG_MSG_GAME_LEVELGAINED,r'Guild MOTD: '+self.player.guildMOTD+r'\n')
    
    
    
    def perspective_doCommand(self,cmd,args):
        index = 0
        if len(args):
            index = int(args[0])
        try:
            char = self.player.party.members[index]
            if not char or char.dead or not char.mob:
                return
            DoCommand(char.mob,cmd,args[1:])
        except:
            print_exc()
    
    
    #cast or memorize spell, empty spell slot should be caught on client
    def perspective_onSpellSlot(self,cid,slot):
        party = self.player.party
        char = Character.get(cid)
        if char not in party.members:
            print "onSpellSlot: PLAYER ATTEMPTING TO MANIPULATE NONPARTY CHARACTER"
            return
        if char.dead or not char.mob:
            return
        
        cursorItem = self.player.cursorItem
        char.onSpellSlot(slot)
        self.player.updateCursorItem(cursorItem)
    
    
    def perspective_onSpellSlotSwap(self,cid,src,dest):
        party = self.player.party
        char = Character.get(cid)
        if char not in party.members:
            print "onSpellSlot: PLAYER ATTEMPTING TO MANIPULATE NONPARTY CHARACTER"
            return
        if char.dead or not char.mob:
            return
        
        char.onSpellSlotSwap(src,dest)
    
    
    def perspective_onInvSlot(self,cid,slot):
        party = self.player.party
        char = Character.get(cid)
        if char not in party.members:
            print "onInvSlot: PLAYER ATTEMPTING TO MANIPULATE NONPARTY CHARACTER"
            return
        if char.dead or not char.mob:
            return
        
        cursorItem = self.player.cursorItem
        char.onInvSlot(slot)
        self.player.updateCursorItem(cursorItem)
    
    def perspective_onInvSlotAlt(self,cid,slot):
        party = self.player.party
        char = Character.get(cid)
        if char not in party.members:
            print "onInvSlot: PLAYER ATTEMPTING TO MANIPULATE NONPARTY CHARACTER"
            return
        if char.dead or not char.mob:
            return
            
        char.onInvSlotAlt(slot)
    
    
    ## @brief Uses an ItemInstance for the ctrl-clicked slot.
    #  @param self (PlayerAvatar) The object pointer.
    #  @param charID (Integer) The ID of the character owning the clicked inventory.
    #  @param invSlot (Integer) The inventory slot that has been ctrl-clicked.
    #  @return None.
    def perspective_onInvSlotCtrl(self,charID,invSlot):
        
        # Try to get a handle to the Character of the provided ID.
        char = Character.get(charID)
        
        # Check if our Player truly is the owner of this Character.
        if char not in self.player.party.members:
            print "onInvSlotCtrl: PLAYER ATTEMPTING TO MANIPULATE NONPARTY CHARACTER"
            return
        
        # If this Character is dead or has no Mob, then return early.
        if char.dead or not char.mob:
            return
        
        # Check for an inventory slot (worn, carry, or crafting).
        if (RPG_SLOT_WORN_END > invSlot >= RPG_SLOT_WORN_BEGIN) or (RPG_SLOT_CARRY_END > invSlot >= RPG_SLOT_CARRY_BEGIN) or (RPG_SLOT_CRAFTING_END > invSlot >= RPG_SLOT_CRAFTING_BEGIN):
            
            # Iterate over the Character's items.
            for item in char.items:
                
                # If an item was found with a matching slot, then attempt to
                # process the item.
                if item.slot == invSlot:
                    
                    # Use the ItemInstance and return.
                    item.use(char.mob)
                    return
        
        # If the ctrl-clicked slot was not worn, nor carry nor crafting...
        else:
            
            # Player attempted to use invalid slot, give debug print.
            print "onInvSlotCtrl: PLAYER ATTEMPTING TO USE INVALID SLOT"
            return
    
    
    def perspective_onApplyPoison(self,charID,poisonSlot,applicationSlot):
        
        # Get a handle to the current Player.
        player = self.player
        
        # Try to get a handle to the Character of the provided ID.
        char = Character.get(charID)
        
        # Check if our Player truly is the owner of this Character.
        if char not in player.party.members:
            print "onApplyPoison: PLAYER ATTEMPTING TO MANIPULATE NONPARTY CHARACTER"
            return
        
        # Get a handle to this Characters Mob.
        mob = char.mob
        
        # If this Character is dead or has no Mob, then return early.
        if char.dead or not mob:
            return
        
        # Check if the mob is in a condition to use an item.
        if mob.sleep > 0 or mob.stun > 0  or mob.isFeared:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot use items while asleep, stunned, or feared.\\n"%(char.name))
            return
        
        # Get the item to be poisoned.
        # Check validity of poison target in the run.
        poisonTarget = None
        if applicationSlot in (RPG_SLOT_PRIMARY,RPG_SLOT_SECONDARY,RPG_SLOT_RANGED):
            poisonTarget = mob.worn.get(applicationSlot)
            if not poisonTarget:
                player.sendGameText(RPG_MSG_GAME_DENIED,"Can't apply poison, %s has nothing equipped in this slot.\\n"%(char.name))
                return
        elif applicationSlot in (RPG_SLOT_PET_PRIMARY,RPG_SLOT_PET_SECONDARY,RPG_SLOT_PET_RANGED):
            if mob.pet:
                poisonTarget = mob.pet.worn.get(applicationSlot - RPG_SLOT_PET_PRIMARY + RPG_SLOT_PRIMARY)
                if not poisonTarget:
                    player.sendGameText(RPG_MSG_GAME_DENIED,"Can't apply poison, %s's pet has nothing equipped in this slot.\\n"%(char.name))
                    return
            else:
                player.sendGameText(RPG_MSG_GAME_DENIED,"Can't apply poison, %s has no pet.\\n"%(char.name))
                return
        if not poisonTarget:
            print "onApplyPoison: PLAYER ATTEMPTING TO APPLY POISON TO WRONG SLOT"
            return
        
        # Iterate over the Character's items to find the specified poison.
        for item in char.items:
            
            # If an item was found with a matching slot, then attempt to
            # process the item.
            if item.slot == poisonSlot:
                
                poison = item
                break
        
        # Player attempted to use invalid slot, give debug print.
        else:
            print "onApplyPoison: PLAYER ATTEMPTING TO USE INVALID SLOT"
            return
        
        # Check if the mob is allowed to use this item.
        if not poison.isUseable(mob) or poison.penalty:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot currently use this %s.\\n"%(char.name,poison.name))
            return
        
        # Check if this item can already be used again.
        if poison.reuseTimer:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot use this %s for another %i seconds.\\n"%(char.name,poison.name,poison.reuseTimer))
            return
        
        skipRefresh = True
        
        # If this item is associated with a skill, check if
        #  the mob has the skill and reset reuse timer.
        #todo proper timing
        if poison.skill:
            if not mob.skillLevels.get(poison.skill):
                player.sendGameText(RPG_MSG_GAME_DENIED,"%s cannot use this %s as it requires the %s skill.\\n"%(char.name,poison.name,poison.skill))
                return
            try:
                mskill = mob.mobSkillProfiles[poison.skill]
                poison.reuseTimer = mskill.reuseTime
            except:
                poison.reuseTimer = 60
            mob.itemRequireTick[poison] = poison.reuseTimer
            skipRefresh = False
        
        if len(poison.spells):
            for ispell in poison.spells:
                if ispell.trigger == RPG_ITEM_TRIGGER_POISON:
                    # It really is a poison, so apply it.
                    targetProcs = poisonTarget.procs
                    # If the weapon already has this poison active, refresh it.
                    if targetProcs.has_key(ispell):
                        targetProcs[ispell] = [ispell.duration,RPG_ITEMPROC_POISON]
                        player.sendGameText(RPG_MSG_GAME_GAINED,"%s refreshes %s.\\n"%(char.name,poison.name))
                    # Else check if there's still room for one additional poison.
                    elif len(targetProcs) < RPG_ITEMPROC_MAX:
                        targetProcs[ispell] = [ispell.duration,RPG_ITEMPROC_POISON]
                        player.sendGameText(RPG_MSG_GAME_GAINED,"%s applies %s.\\n"%(char.name,poison.name))
                    # No more free room, so overwrite one.
                    else:
                        # Get the poison with the lowest duration.
                        overwriting = []
                        for proc,procData in targetProcs.iteritems():
                            if procData[1] != RPG_ITEMPROC_ENCHANTMENT:
                                if not overwriting or overwriting[1] < procData[0]:
                                    overwriting = (proc,procData[0])
                        # Overwrite poison with lowest duration.
                        if overwriting:
                            del targetProcs[overwriting[0]]
                            targetProcs[ispell] = [ispell.duration,RPG_ITEMPROC_POISON]
                            player.sendGameText(RPG_MSG_GAME_DENIED,"The applied %s nullifies %s.\\n"%(poison.name,overwriting[0].spellProto.name))
                        else:
                            player.sendGameText(RPG_MSG_GAME_DENIED,"%s radiates so much power that %s evaporates.\\n"%(poisonTarget.name,poison.name))
                    
                    # Play a sound for application.
                    player.mind.callRemote("playSound","sfx/Underwater_Bubbles2.ogg")
                    # Refresh the iteminfo so the proc shows.
                    poisonTarget.itemInfo.refreshProcs()
                    
                    # Update poison charges if needed.
                    if poison.useCharges:
                        poison.useCharges -= 1
                        if not poison.useCharges and poison.itemProto.useDestroy:
                            poison.stackCount -= 1
                            if poison.stackCount <= 0:
                                player.takeItem(poison)
                            else:
                                poison.useCharges = poison.itemProto.useMax
                                skipRefresh = False
                        else:
                            if poison.useCharges < 0:
                                poison.useCharges = 0
                            else:
                                skipRefresh = False
        
        # Refresh the poison if needed.
        if not skipRefresh:
            poison.itemInfo.refresh()
    
    
    def perspective_endLooting(self):
        if not self.player.looting:
            return
        
        self.player.looting.looter = None
        self.player.looting = None
        
        return True
    
    
    def perspective_loot(self, cindex, slot, alt=False):
        if not self.player.looting:
            return
        char = self.player.party.members[cindex]
        if char.dead or not char.mob:
            return
        char.onLoot(self.player.looting,slot,alt)
    
    
    def perspective_destroyCorpse(self):
        if not self.player.looting:
            return
        
        self.player.looting.zone.removeMob(self.player.looting)
    
    
    # Only use to expunge cursor item, else use takeItem in player class.
    def perspective_expungeItem(self):
        item = self.player.cursorItem
        self.player.cursorItem = None
        if item.character.player != self.player:
            raise ValueError,"Attempting to expunge an item not belonging to player!"
            return
        item.slot = -1
        self.player.updateCursorItem(item)
        item.destroySelf()
        self.player.cinfoDirty = True
    
    
    def perspective_splitItem(self,newStackSize):
        item = self.player.cursorItem
        if item.character not in self.player.party.members:
            raise "Attempting to split an item not belonging to player's present party!"
            self.player.cursorItem = None
            return
        item.character.splitItem(item,newStackSize)
    
    
    #choice will either be a zoneinstance name or "new" if player wants to launch own zone
    def perspective_chooseZone(self,choice):
        found = False
        zoneInstanceName = ""
        player = self.player
        if player.darkness:
            player.darknessLogTransformInternal = player.triggeredZoneLink.dstZoneTransform
            player.darknessLogZone = Zone.byName(player.triggeredZoneLink.dstZoneName)
        elif player.monster:
            player.monsterLogTransformInternal = player.triggeredZoneLink.dstZoneTransform
            player.monsterLogZone = Zone.byName(player.triggeredZoneLink.dstZoneName)            
        else:
            player.logTransformInternal = player.triggeredZoneLink.dstZoneTransform
            player.logZone = Zone.byName(player.triggeredZoneLink.dstZoneName)
            
        
        self.world.closePlayerZone(player)
        
        if choice == 'new' and player.world.singlePlayer:
            zi = self.world.playerSelectZone(self,self.player.simPort,self.player.simPassword)
            if zi:
                zoneInstanceName = zi.name
                found = True
            else:
                found = False
        else:
            
            for zo in player.triggeredZoneOptions:
                if zo.zoneInstanceName == choice:
                    zoneInstanceName = zo.zoneInstanceName
                    found = True
                    break
                    
        if found:
            zi = self.world.getZoneByInstanceName(zoneInstanceName)
            if not zi:
                print_stack()
                print "AssertionError: zone not found!"
                return
            
            player.zone = zi
            player.party.reassemble()
            
            ip = zi.ip
            if zi.owningPlayer == player:
                #we are being told to host, what about people sharing an IP?
                ip = '127.0.0.1'
                
            zconnect = ZoneConnectionInfo()
            zconnect.ip = ip
            zconnect.password = zi.password
            zconnect.port = zi.port
            zconnect.niceName = zi.zone.niceName
            zconnect.missionFile = zi.zone.missionFile
            zconnect.instanceName = zi.name
            
            zi.submitPlayer(self.player,zconnect)

            
            self.player.rootInfo = RootInfo(self.player,self.player.party.charInfos)            
            self.mind.callRemote("setRootInfo",self.player.rootInfo)
            
            if self.player.cursorItem:
                self.mind.callRemote("setCursorItem",self.player.cursorItem.itemInfo)
                   
    #interaction
    
    #dialog
    def perspective_onInteractionChoice(self,index,pane):
        if not self.player.interacting or not self.player.curDialogLine:
            pane.callRemote("close")
            return
        
        self.player.dialog.handleChoice(self.player,index,pane)
        
    #global
    def perspective_endInteraction(self):
        self.player.endInteraction()
    
    
    def perspective_sellItem(self,charIndex,slot):  # use slot in inventory
        if not self.player.interacting or not self.player.interacting.vendor:
            return
        
        char = self.player.party.members[charIndex]
        if char.dead or not char.mob:
            return
        item = None
        found = False
        for item in char.items:
            if item.slot == slot:
                found = True
                break
        
        if item and found:
            self.player.interacting.vendor.buyItem(self.player,item)
        else:
            print "Warning: Player item selling wackiness!!! Item to be sold not found!"
    
    def perspective_buyItem(self,charIndex,itemIndex):  # use index from vendor list
        if not self.player.interacting or not self.player.interacting.vendor:
            return
        
        char = self.player.party.members[charIndex]
        if char.dead or not char.mob:
            return
        
        self.player.interacting.vendor.sellItem(self.player,char,itemIndex)
    
    
    def perspective_setCurrentCharacter(self,cindex):
        if cindex > len(self.player.party.members) - 1:
            return
        
        cchar = self.player.party.members[cindex]
        
        if self.player.curChar == cchar:
            return
        
        
        self.player.curChar = cchar
        
        if hasattr(self.player,"dialog"):#bah
            if self.player.dialog and self.player.interacting:
                if hasattr(self.player.interacting,"spawn"):
                    name = self.player.interacting.spawn.name
                else:
                    name = self.player.dialog.title
                    
                self.player.dialog.setLine(self.player,self.player.dialog.greeting,name)
        
    def perspective_setXPGain(self,charindex,pvalue,svalue,tvalue):
        
        char = self.player.party.members[charindex]
        
        char.setXPGain(pvalue,svalue,tvalue)
        
    #Alliances

    def perspective_invite(self):
        player = self.player
        alliance = player.alliance
        
        if player.invite:
            player.sendGameText(RPG_MSG_GAME_DENIED,"You must accept or decline an outstanding invitation first.\\n")
            return
        
        #get currently selected player
        target = player.curChar.mob.target
        
        if not target:
            player.sendGameText(RPG_MSG_GAME_DENIED,"You must have a valid target to invite.\\n")
            return
            
        if not target.player:
            player.sendGameText(RPG_MSG_GAME_DENIED,"You cannot invite %s to the alliance.\\n"%target.name)
            return #not a player
            
        if alliance.leader != player or alliance.remoteLeaderName != player.publicName:
            player.sendGameText(RPG_MSG_GAME_DENIED,"You are not the leader of the alliance.\\n")
            return
            
        if alliance.countMembers()>=6:
            player.sendGameText(RPG_MSG_GAME_DENIED,"The alliance is full.\\n")
            return
            
        otherplayer = target.player
        
        if otherplayer == player:
            return
        
        if otherplayer.invite:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s is already considering an alliance.\\n"%otherplayer.charName)
            return
    
        if otherplayer.alliance.countMembers()>1:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s is already in an alliance.\\n"%otherplayer.charName)
            return
        
        d = otherplayer.mind.callRemote("checkIgnore",player.charName)
        d.addCallback(self.gotCheckIgnoreAlliance,player,otherplayer)
        d.addErrback(self.gotCheckIgnoreAllianceError)
    
    def gotCheckIgnoreAlliance(self,ignored,player,otherplayer):
        if ignored:
            player.sendGameText(RPG_MSG_GAME_DENIED,"%s is ignoring you.\\n"%otherplayer.charName)
            return
        player.sendGameText(RPG_MSG_GAME_GOOD,"You have invited %s to the alliance.\\n"%otherplayer.charName)
        otherplayer.sendGameText(RPG_MSG_GAME_GOOD,"%s has invited you to form an alliance.\\n"%player.charName)
        player.alliance.invite(otherplayer)
    
    def gotCheckIgnoreAllianceError(self,error):
        print "Error in checkIgnore: %s"%str(error)
    
    def perspective_joinAlliance(self):
        player = self.player
        if not player.invite:
            return False
        
        leader = player.invite.leader
        if player.invite.alliance != leader.alliance: #incase alliance disbanded or something
            player.invite = None
            player.sendGameText(RPG_MSG_GAME_DENIED,"This alliance has disbanded.\\n")
            return False
        
        alliance = leader.alliance
        
        if not alliance.join(player):
            player.sendGameText(RPG_MSG_GAME_DENIED,"You cannot join the alliance at this time.\\n")
            return False
            
        player.sendGameText(RPG_MSG_GAME_GOOD,"You have joined %s's alliance.\\n"%leader.charName)
        
        for p in alliance.members:
            for c in p.party.members:
                mob = c.mob
                target = mob.target
                if target:
                    if target.master:
                        target = target.master
                    if target.player and target.player in alliance.members:
                        mob.attackOff()
                mob = mob.pet
                if mob:
                    target = mob.target
                    if target:
                        if target.master:
                            target = target.master
                        if target.player and target.player in alliance.members:
                            mob.attackOff()
                            try:
                                del mob.aggro[mob.target]
                            except KeyError:
                                pass
            if p == player:
                continue
            p.sendGameText(RPG_MSG_GAME_GOOD,"%s has joined your alliance.\\n"%player.charName)
        
        return True
    
    def perspective_leaveDecline(self):
        player = self.player
        
        if player.invite:
            try:
                player.invite.decline()
            except:
                print_exc()
            player.invite = None
            return
            
        if player.alliance.countMembers()>1:
            player.alliance.leave(player)
        
        
    def perspective_disband(self):
        
        player = self.player
        if player.publicName != player.alliance.remoteLeaderName:
            return

        if player.alliance.countMembers()>1:
            player.alliance.disband()
        
        
    def perspective_kick(self,name):
        player = self.player
        if player.publicName != player.alliance.remoteLeaderName:
            return

        if player.alliance.leader == player and player.alliance.countMembers()>1:
            player.alliance.kick(name)
    
    
    # Player trades
    def perspective_onPlayerTradeMoney(self,money):
        player = self.player
        if not player.trade:
            return 0L
        return player.trade.submitMoney(player,money)
    
    def perspective_onPlayerTradeSlot(self,slot):
        player = self.player
        
        if not player.trade:
            return
            
        party = player.party
        char = player.curChar
            
        cursorItem = player.cursorItem

        char.onInvSlot(slot+RPG_SLOT_TRADE0)
        
        player.updateCursorItem(cursorItem)

    def perspective_onPlayerTradeCancel(self):
        player = self.player
        
        if not player.trade:
            return
            
        player.trade.cancel()
            

    def perspective_onPlayerTradeAccept(self):
        player = self.player
        
        if not player.trade:
            return
            
        player.trade.accept(player)
    
    
    # Target description
    def sendTgtDesc(self,src,tgt):
        if not tgt:
            return
        char = tgt.character
        player = tgt.player
        infoDict = {}
        
        infoDict['NAME'] = tgt.name
        infoDict['TGTID'] = tgt.id
        
        infoDict['PCLASS'] = tgt.pclass.name
        infoDict['PLEVEL'] = tgt.plevel
        if tgt.sclass and tgt.slevel:
            infoDict['SCLASS'] = tgt.sclass.name
            infoDict['SLEVEL'] = tgt.slevel
            if tgt.tclass and tgt.tlevel:
                infoDict['TCLASS'] = tgt.tclass.name
                infoDict['TLEVEL'] = tgt.tlevel
        infoDict['RACE'] = tgt.race.name
        infoDict['REALM'] = tgt.realm
        
        infoDict['DESC'] = tgt.spawn.desc
        
        if self.player == player:
            infoDict['MYSELF'] = True
        else:
            if player:
                player.sendGameText(RPG_MSG_GAME_EVENT,"%s is getting inspected by <a:gamelinkcharlink%s>%s</a>.\\n"%(char.name,src.name.replace(' ','_'),src.name))
            infoDict['MYSELF'] = False
            infoDict['STANDING'] = GetFactionRelationDesc(src,tgt)
        
        infoDict['CHARTGT'] = char != None
        if char:
            infoDict['VARIANTNAME'] = char.lastName
            infoDict['DEADTGT'] = char.dead == True
            infoDict['GUILDNAME'] = player.guildName
            infoDict['BIRTHDATE'] = char.creationTime.strftime('%a, %b %d %Y')
            infoDict['PORTRAIT'] = char.portraitPic
            infoDict['ENCOUNTERSETTING'] = player.encounterSetting
        else:
            infoDict['DEADTGT'] = tgt.detached == True
            infoDict['PET'] = tgt.master != None
            infoDict['VARIANTNAME'] = tgt.variantName
        
        # Send target description to client
        self.mind.callRemote("setTgtDesc",infoDict)
    
    
    def perspective_setSpawnDesc(self,myDesc,mobID):
        mob = None
        for c in self.player.party.members:
            if c.mob.id == mobID:
                mob = c.mob
                break
        if mob:
            mob.spawn.desc = myDesc
        else:
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"Spawn description couldn't be set, spawn not found.\\n")
    
    
    def perspective_setPortraitPic(self,pic):
        self.player.curChar.portraitPic = pic
    
    #processes
    
    def perspective_cancelProcess(self,cid,pid):
        for c in self.player.party.members:
            if c.id == cid:
                for p in c.mob.processesIn:
                    if isinstance(p,Spell):
                        if pid == p.pid and not p.spellProto.spellType&RPG_SPELL_HARMFUL:
                            p.cancel()
                            return
                
        
    def perspective_chooseAdvancement(self,cname,advancement):
        for c in self.player.party.members:
            if c.name == cname:
                c.chooseAdvancement(advancement)
                return
            
        raise RuntimeWarning,"Player %s attempting to choose advancement %s for %s"%(self.player.name,advancement,cname)
    
    
    def perspective_onCraft(self,cindex,recipeID,useCraftWindow=False):
        # cindex = character index in players party
        # recipeID = id of requested crafting recipe
        # useCraftWindow: True if only items in crafting window should be checked
        if cindex > len(self.player.party.members) - 1:
            return
        self.player.party.members[cindex].onCraft(recipeID,useCraftWindow)
    
    
#REPAIR
    def perspective_repairItem(self,cindex):
        if cindex > len(self.player.party.members) - 1:
            return
        RepairItem(self.player,self.player.party.members[cindex])
    
    def perspective_repairAll(self,cindex):
        if cindex > len(self.player.party.members) - 1:
            return
        RepairAll(self.player,self.player.party.members[cindex])
    
    def perspective_repairParty(self,cindex):
        if cindex > len(self.player.party.members) - 1:
            return
        RepairParty(self.player,self.player.party.members[cindex])
    
    
    def perspective_onBankSlot(self,slot):
        player = self.player
        
        cursorItem = player.cursorItem
        bankItem = player.bankItems.get(slot,None)
        
        # If there is an item on the clicked slot...
        if bankItem:
            switched,newBankItem,newCursorItem = bankItem.doStack(cursorItem)
            # Stacking wasn't possible or cursor was empty.
            if switched:
                # Set new cursor item to previous bank item.
                # This will also remove previous bank item from bank.
                newCursorItem.setCharacter(player.curChar,False)
                newCursorItem.slot = RPG_SLOT_CURSOR
                newCursorItem.refreshFromProto()
                # If there was an item in cursor, place this in bank.
                if newBankItem:
                    newBankItem.setCharacter(None,False)
                    newBankItem.slot = slot
                    newBankItem.setPlayerAsOwner(player)
                    player.bankItems[slot] = newBankItem
                    newBankItem.refreshFromProto()
            # Succeeded in stacking cursor item onto bank item.
            elif not newCursorItem:
                cursorItem = None
            # Update cursor and force a bank update.
            player.cursorItem = newCursorItem
            player.updateCursorItem(cursorItem)
            player.rootInfo.forceBankUpdate = True
            return
        
        # No item in clicked bank slot, but one on cursor.
        # Place cursor item in bank.
        if cursorItem:
            cursorItem.setCharacter(None,False)
            cursorItem.slot = slot
            cursorItem.setPlayerAsOwner(player)
            player.bankItems[slot] = cursorItem
            cursorItem.refreshFromProto()
            player.cursorItem = None
            player.rootInfo.forceBankUpdate = True
        
        player.updateCursorItem(cursorItem)
    
    
    def perspective_onAcceptResurrect(self):
        if not self.player.resurrectionRequest:
            return
        
        t,xpRecover,healthRecover,manaRecover,staminaRecover,cname = self.player.resurrectionRequest
        
        if time() - t > 30:
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"This resurrection has expired.\\n")
            return
        
        self.player.resurrectionRequest = None
        
        c = self.player.party.members[0]
        
        if c.name != cname:
            return
        if not c.deathZone:
            return
        
        c.playerResurrect(xpRecover,healthRecover,manaRecover,staminaRecover)
    
    
    def perspective_onResurrect(self,cname):
        if not self.player.resurrection:
            return
        
        t,xpRecover,healthRecover,manaRecover,staminaRecover,cnames = self.player.resurrection
        self.player.resurrection = None
        if self.player.curChar:
            pCharName = self.player.curChar.name
        else:
            pCharName = self.player.fantasyName
        
        if cname not in cnames:
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"Resurrection error, resurrect target %s not in list of possible resurrection targets.\\n"%cname)
            return
        
        if time() - t > 30:
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"Resurrection expired.\\n")
            return
        
        for p in self.player.world.activePlayers:
            if p.zone and p in p.zone.players:
                c = p.party.members[0]
                if c.deathZone and c.name == cname:
                    #got it and we are on this cluster
                    if p.resurrectionRequest:
                        timer = p.resurrectionRequest[0]
                        if time() - timer < 30:
                            self.player.sendGameText(RPG_MSG_GAME_DENIED,"%s is already being resurrected.\\n"%cname)
                            return
                    
                    p.resurrectionRequest = (time(),xpRecover,healthRecover,manaRecover,staminaRecover,cname)
                    p.mind.callRemote("resurrectionRequest",pCharName,xpRecover)
                    return
        
        self.player.world.daemonPerspective.callRemote("resurrectionRequest",pCharName,xpRecover,healthRecover,manaRecover,staminaRecover,time(),cname)


#item vault
    
    def perspective_onRemoveVault(self,id):
        player = self.player
        if player.cursorItem:
            return
        
        char = player.curChar
        
        try:
            vitem = CharacterVaultItem.get(id)
        except:
            print "WARNING: Invalid vault item id %i"%id
            return
        
        if char != vitem.character:
            print "WARNING: Player %s attempting to remove vault item to incorrect character %s"%(player.name,char.name)
            return
        
        item = ItemInstance(vitem.item)
        vitem.destroySelf()
        char.vaultItemsDirty = True
        item.setCharacter(char)
        item.slot = RPG_SLOT_CURSOR
        player.cursorItem = item
        player.updateCursorItem(None)
    
    
    def perspective_onPlaceVault(self):
        player = self.player
        
        if not player.cursorItem:
            return
        
        item = player.cursorItem
        
        # Check if this item is allowed for vault storage.
        # The client actually already checks this, but make sure, otherwise
        #  items could get lost. Just don't return a message.
        if item.flags & (RPG_ITEM_ETHEREAL | RPG_ITEM_WORLDUNIQUE):
            return
        
        stackMax = item.itemProto.stackMax
        
        char = player.curChar
        
        # Check if this item can be stacked onto an existing vault entry.
        stacked = False
        if stackMax > 1:
            # Get the items max charges.
            useMax = item.itemProto.useMax
            
            # For better performance run a separate loop for items that use charges.
            if useMax > 1:
                
                # Get amount of needed charges.
                neededCharges = useMax * (item.stackCount - 1) + item.useCharges
                
                # Iterate through all vault items.
                for vitem in char.vaultItems:
                    # If the names don't match, continue to the next item.
                    if vitem.name != item.name:
                        continue
                    
                    # Get the item we'll be trying to stack onto.
                    candidate = vitem.item
                    # Calculate the free charges on the candidate.
                    freeCharges = useMax * (stackMax - candidate.stackCount + 1) - candidate.useCharges
                    # If the charge count and stack count have both been maxed on
                    #  the candidate, continue to the next item.
                    if freeCharges <= 0:
                        continue
                    
                    # Beginning here, we'll definitely stack.
                    stacked = True
                    
                    # Clamp free charges to needed charges.
                    if freeCharges > neededCharges:
                        freeCharges = neededCharges
                    
                    # Get the stack and charge counts that can be stacked.
                    stackCount = freeCharges / useMax
                    useCharges = freeCharges % useMax
                    
                    # Update charges on both items.
                    candidate.useCharges += useCharges
                    item.useCharges -= useCharges
                    
                    # If the stacked item has now 0 or less charges, need to decrement its
                    #  stack count and adjust the charges.
                    if item.useCharges <= 0:
                        item.useCharges += useMax
                        item.stackCount -= 1
                    # If the candidate has now more than the maximum number of charges,
                    #  need to increment its stack count and adjust its charges.
                    if candidate.useCharges > useMax:
                        candidate.useCharges -= useMax
                        candidate.stackCount += 1
                    
                    # Thanks to autostacking on every entry, we won't need to check
                    #  further items for stacking capability and can break here.
                    break
            
            # Otherwise we have only to deal with stack counts which simplifies things.
            else:
                
                # Iterate through all vault items.
                for vitem in char.vaultItems:
                    # If the names don't match or if the stack count is already
                    #  maxed on the iterated item, continue to the next item.
                    if vitem.name != item.name or vitem.stackCount >= stackMax:
                        continue
                    
                    # Beginning here, we'll definitely stack.
                    stacked = True
                    # Get the item we'll be trying to stack onto.
                    candidate = vitem.item
                    
                    # Get amount of free space to stack.
                    stackCount = stackMax - candidate.stackCount
                    
                    # Clamp stack count to needed count.
                    if stackCount > item.stackCount:
                        stackCount = item.stackCount
                    
                    # Thanks to autostacking on every entry, we won't need to check
                    #  further items for stacking capability and can break here.
                    break
            
            if stacked:
                # Didn't forget about those stack count updates, we just can do
                #  them here for both variants, with and without charges.
                candidate.stackCount += stackCount
                vitem.stackCount += stackCount
                item.stackCount -= stackCount
                
                # If the item to be inserted was fully stacked, destroy it.
                if item.stackCount <= 0:
                    player.takeItem(item)
                    # Mark vault for update and send update to player.
                    char.vaultItemsDirty = True
                    char.charInfo.refreshVault()
                    return
        
        # If we get here, the item couldn't be stacked or at least not fully.
        # In this case we need to check if there's still enough space in the vault
        #  for an additional item.
        if RPG_PRIVATE_VAULT_LIMIT <= len(char.vaultItems):
            self.player.sendGameText(RPG_MSG_GAME_DENIED,"%s's private vault is full.\\n"%char.name)
            # If partial stacking was possible, need to refresh the item info.
            if stacked:
                item.itemInfo.refreshDict({'STACKCOUNT':item.stackCount,'USECHARGES':item.useCharges})
                char.vaultItemsDirty = True
                char.charInfo.refreshVault()
            return
        
        # Add the item as a new entry to the vault. Before doing so, make sure that
        #  character and player information is reset or the item might turn up in the
        #  wrong place again.
        item.setCharacter(None)
        item.player = None
        # Reset the item slot.
        item.slot = -1
        # Reset the players cursor item.
        player.cursorItem = None
        player.updateCursorItem(item)
        
        # First store the item to database, set override to true to ignore the missing
        #  player and character fields. We'll add a link via a CharacterVaultItem object.
        item.storeToItem(True)
        # Now add the link to the stored item.
        CharacterVaultItem(character=char,item=item.item,name=item.name,stackCount=item.stackCount)
        
        # Flag the vault items as dirty and send an update to the player.
        char.vaultItemsDirty = True
        
        #go with something more lightweight?  The whole refresh logic needs to be rewritten in C 
        char.charInfo.refresh()
    
    
    # Receive friends list from client.
    def perspective_submitFriends(self,friends):
        self.player.friends = set(f.upper() for f in friends)
    
    
    def perspective_setEncounterSetting(self,index,now=False):
        if now:
            self.player.encounterSetting = index
        elif self.player.encounterSetting != index:
            char = self.player.curChar
            mob = char.mob
            if index == RPG_ENCOUNTER_PVE:
                msg = r'%s will cease fighting other players.\n'%char.name
            elif index == RPG_ENCOUNTER_RVR:
                msg = r'Attention: %s may now engage in realm versus realm battles!\n'%char.name
            elif index == RPG_ENCOUNTER_GVG:
                msg = r'Attention: %s may now engage in guild versus guild battles!\n'%char.name
            else:
                msg = r'WARNING: %s may now engage in player versus player battles!\n'%char.name
            GameMessage(RPG_MSG_GAME_COMBAT,mob.zone,mob,None,msg,mob.simObject.position,range=30)
            reactor.callLater(10,self.player.applyEncounterSetting,index)  # call 10 seconds later
    
    
    # Function to insert an item on cursor into a container specified by its slot.
    # Works on containers in bank and on character. If on character, provide the
    #  id of the owning character as well.
    def perspective_insertItem(self, containerSlot, charID):
        player = self.player
        
        # Get the item on the cursor.
        cursorItem = player.cursorItem
        
        # If there's nothing on the cursor, skip.
        if not cursorItem:
            return
        
        # Check if the character id is valid and get the character if so.
        srcChar = None
        if charID:
            srcChar = Character.get(charID)
            if srcChar not in player.party.members:
                print "insertItem: PLAYER %s IS ATTEMPTING TO MANIPULATE NONPARTY CHARACTER %s!"%(player.name,srcChar.name)
                return
        
        # Get the container item.
        container = None
        if RPG_SLOT_BANK_BEGIN <= containerSlot < RPG_SLOT_BANK_END:
            container = player.bankItems.get(containerSlot)
        elif not srcChar:
            print "insertItem: ERROR, container owner unspecified!"
            return
        elif srcChar.mob and RPG_SLOT_WORN_BEGIN <= containerSlot < RPG_SLOT_WORN_END:
            container = srcChar.mob.worn.get(containerSlot)
        else:
            for citem in srcChar.items:
                if citem.slot == containerSlot:
                    container = citem
                    break
        
        # If the container could not be found, log a warning.
        if not container or not container.container:
            print "insertItem: WARNING, could not find desired container for player %s!"%player.name
            return
        
        # Insert the item on cursor into the container.
        if container.container.insertItem(cursorItem, True):
            # Update the container contents on client.
            container.itemInfo.refreshContents()
    
    
    # Function to extract an item specified by its index from a container specified
    #  by its slot. Works on containers in bank and on character. If on character,
    #  provide the id of the owning character as well.
    def perspective_extractItem(self, containerSlot, charID, itemIndex):
        player = self.player
        
        # If there's already something on the cursor, skip.
        if player.cursorItem:
            return
        
        # Check if the character id is valid and get the character if so.
        srcChar = None
        if charID:
            srcChar = Character.get(charID)
            if srcChar not in player.party.members:
                print "extractItem: PLAYER %s IS ATTEMPTING TO MANIPULATE NONPARTY CHARACTER %s!"%(player.name,srcChar.name)
                return
        
        # Get the character that will be owning the extracted item.
        tgtChar = player.curChar
        
        # Get the container item.
        container = None
        if RPG_SLOT_BANK_BEGIN <= containerSlot < RPG_SLOT_BANK_END:
            container = player.bankItems.get(containerSlot)
        elif not srcChar:
            print "extractItem: ERROR, container owner unspecified!"
            return
        elif srcChar.mob and RPG_SLOT_WORN_BEGIN <= containerSlot < RPG_SLOT_WORN_END:
            container = srcChar.mob.worn.get(containerSlot)
        else:
            for citem in srcChar.items:
                if citem.slot == containerSlot:
                    container = citem
                    break
        
        # If the container could not be found, log a warning.
        if not container or not container.container:
            print "extractItem: WARNING, could not find desired container for player %s!"%player.name
            return
        
        # Extract the item from the container.
        extraction = container.container.extractItemByIndex(itemIndex)
        
        # If the item to be extracted could not be found, return.
        # Logging an error here won't make much sense as this might happen
        #  often if a player lags.
        if not extraction:
            return
        
        # Assign the extracted item to the current character.
        extraction.setCharacter(tgtChar)
        # Put the extracted item into the players cursor.
        extraction.slot = RPG_SLOT_CURSOR
        player.cursorItem = extraction
        player.updateCursorItem(None)
        
        # Update the container contents on client.
        container.itemInfo.refreshContents()


    def perspective_queryRaceGraphics(self):
        from race import GetRaceGraphics
        return GetRaceGraphics()

