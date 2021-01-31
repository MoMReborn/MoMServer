# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details



# spread = .01 to 100 NONLINEAR! 
# spread = 1 at (MYLEVEL = OTHERLEVEL)

#NOTE THAT THIS IS BASED ON OVERALL LEVEL and not class specific levels
#good for those multiclassers!


from mud.common.permission import User
from mud.world.defines import *

from math import floor,sqrt
from random import randint



#is mob2 kos to mob1
def IsKOS(mob1,mob2):
    # If one of both mobs does not exist, there's no hate.
    if not mob1 or not mob2:
        return False
    
    # Only the masters relation counts, not the pets.
    # For pets aggro is inherited through master.
    if mob1.master:
        mob1 = mob1.master
    if mob2.master:
        mob2 = mob2.master
    
    # If the two mobs aren't allowed to harm each other,
    #  then there's no hate.
    if not AllowHarmful(mob1,mob2):
        return False
    
    # If the mobs already hate each other, return true.
    if mob1.aggro.get(mob2,0):
        return True
    if mob2.aggro.get(mob1,0):
        return True
    
    # Mobs that are no player mobs and have the passive flag set
    #  never generate aggro based on realm or factions.
    # But if assistance flag is set, they might still assist other
    #  mobs that do!
    # Non-player mobs with the aggressive flag set always hate
    #  player mobs, regardless the realm or factions.
    if not mob1.player:
        if mob1.spawn.flags & RPG_SPAWN_PASSIVE:
            return False
        if mob1.spawn.flags & RPG_SPAWN_AGGRESSIVE and mob2.player:
            return True
    if not mob2.player:
        if mob2.spawn.flags & RPG_SPAWN_PASSIVE:
            return False
        if mob2.spawn.flags & RPG_SPAWN_AGGRESSIVE and mob1.player:
            return True
    
    # Get handles to the realms of the two mobs.
    realm1 = mob1.realm
    realm2 = mob2.realm
    
    # If the realms don't match, check for realm relations.
    # If one of both mobs is of RPG_REALM_UNDEFINED, then
    #  there's no hate based on realm.
    if realm1 != realm2 and realm1 != RPG_REALM_UNDEFINED and \
        realm2 != RPG_REALM_UNDEFINED:
        
        # Monster realm is hostile towards all other realms.
        if realm1 == RPG_REALM_MONSTER or realm2 == RPG_REALM_MONSTER:
            return True
        
        # Fellowship of Light and the Minions of Darkness hate each
        #  other and the monster realm. Monsters have already been
        #  handled.
        if realm1 == RPG_REALM_LIGHT and realm2 == RPG_REALM_DARKNESS:
            return True
        if realm1 == RPG_REALM_DARKNESS and realm2 == RPG_REALM_LIGHT:
            return True
    
    # The two mobs still like each other, so check factions.
    # Checking factions only makes sense when dealing with
    #  at least one non-player mob.
    if not mob1.player or not mob2.player:
        # The KOS dictionary is already kept symmetric,
        #  so no need to check both directions.
        from mud.world.faction import KOS
        if mob2.spawn.name in KOS[mob1.spawn.name]:
            return True
    
    # By getting here, we can be sure that the two mobs
    #  are friendly to each other.
    return False


# Returns a tuple with (RPG_FACTION_#, desc)
def GetFactionRelationDesc(playermob,mob):
    if mob.player:
        if AllowHarmful(playermob,mob):
            standing = (RPG_FACTION_DISLIKED,"%s hasn't quite decided what to make of %s, but seems ready for battle.  "%(mob.name,playermob.name))
        else:
            standing = (RPG_FACTION_UNDECIDED,"%s hasn't quite decided what to make of %s.  "%(mob.name,playermob.name))
    else:
        kos = IsKOS(mob,playermob)
        if not kos:
            worstfaction = 999999999L
            sfactions = mob.spawn.factions
            for f in playermob.character.characterFactions:
                for of in sfactions:
                    if f.faction == of:
                        # got one
                        if f.points < RPG_FACTION_DISLIKED:
                            kos = True
                            break
                        if f.points < worstfaction:
                            worstfaction = f.points
                else:
                    continue
                break
        
        if kos:
            standing = (RPG_FACTION_HATED,"%s stares at %s with utter contempt.  "%(mob.name,playermob.name))
        else:
            if worstfaction == 999999999L:
                worstfaction = 0
            if worstfaction >= RPG_FACTION_ADORED:
                standing = (RPG_FACTION_ADORED,"%s gazes at %s adoringly.  "%(mob.name,playermob.name))
            elif worstfaction >= RPG_FACTION_LIKED:
                standing = (RPG_FACTION_LIKED,"%s likes %s.  "%(mob.name,playermob.name))
            elif worstfaction >= 0:
                standing = (RPG_FACTION_UNDECIDED,"%s hasn't quite decided what to make of %s.  "%(mob.name,playermob.name))
            else:
                standing = (RPG_FACTION_DISLIKED,"%s gives %s a very sour look.  "%(mob.name,playermob.name))
    return standing


def GetLevelSpread(mob1,mob2):

  spread = mob2.level - mob1.level
  
  if mob1.level < mob2.level:
    spread = spread + ((mob2.level - mob1.level) ** 2)
    
  return ((spread + 100.0) * 10.0) / 1000.0


def GetRange(mob1,mob2):
    
    #it's possible that we don't have a simObject yet for some checks that 
    #don't depend on activeMob list, like allianceXP
    if not mob1 or not mob2:
        return 999999
    
    if mob1 == mob2:
        return 0
    
    if not mob1.simObject or not mob2.simObject:
        return 999999
    
    p1 = mob1.simObject.position
    p2 = mob2.simObject.position
    x = p1[0]-p2[0]
    y = p1[1]-p2[1]
    z = p1[2]-p2[2]
    return sqrt(x*x+y*y+z*z)

def GetRangeMin(mob1,mob2):
    
    #it's possible that we don't have a simObject yet for some checks that 
    #don't depend on activeMob list, like allianceXP
    if not mob1 or not mob2:
        return 999999
    
    if mob1 == mob2:
        return 0
    
    if not mob1.simObject or not mob2.simObject:
        return 999999
    
    p1 = mob1.simObject.position
    p2 = mob2.simObject.position
    x = p1[0] - p2[0]
    y = p1[1] - p2[1]
    z = p1[2] - p2[2]
    dist = sqrt(x * x + y * y + z * z)
    dist -= mob1.spawn.modifiedScale * mob1.spawn.radius * mob1.size
    dist -= mob2.spawn.modifiedScale * mob2.spawn.radius * mob2.size
    return dist


def SkillCheck(mob1,mob2,freq):
    #very simple mob1 vs mob2
    
    #reversed
    spread = GetLevelSpread(mob2,mob1)
    
    r = int(spread * freq)
    
    if r < 1:
        r = 1
    
    if not randint(0,int(r)):
        return True
    
    return False


def GetPlayerHealingTarget(src,tgt,spellProto=None):
    checkHealth = None
    
    # Only friendly targets can be healed.
    if tgt and not AllowHarmful(src,tgt):
        # Check if we need to check max health.
        # If the spell directly restores a set amount of health,
        #  find a target that actually needs healing.
        checkHealth = spellProto.affectsStat("health")
        # Either this spell is a regeneration spell or the target needs healing,
        #  so return original target.
        if not checkHealth or tgt.health < tgt.maxHealth:
            return tgt
    
    # Only check for stat if not already done.
    if checkHealth == None:
        checkHealth = spellProto.affectsStat("health")
    
    # If this spell is a regeneration spell, don't search for a hurt target,
    #  directly return the caster.
    if not checkHealth:
        return src
    
    # Ok, no valid target so far or we do care about finding a target that actually
    #  needs healing, so try to find one in our party.
    for c in src.player.party.members:
        if c.mob.health < c.mob.maxHealth:
            return c.mob
    
    return None


def GenMoneyText(tin):
    platinum, tin = divmod(tin,100000000L)
    gold, tin = divmod(tin,1000000L)
    silver, tin = divmod(tin,10000L)
    copper, tin = divmod(tin,100L)
    
    ext = ('pp','gp','sp','cp','tp')
    worth = (platinum,gold,silver,copper,tin)
    return ', '.join('%i%s'%(w,ext[i]) for i,w in enumerate(worth) if w != 0)

def CollapseMoney(money,multiplier=0):
    if multiplier:
        money = int(money * multiplier)
    
    platinum, tin = divmod(money,100000000L)
    gold, tin = divmod(tin,1000000L)
    silver, tin = divmod(tin,10000L)
    copper, tin = divmod(tin,100L)
    
    return (tin,copper,silver,gold,platinum)


def AllowHarmful(src,dst):
    if not src or not dst:
        return True
    
    if src.master:
        src = src.master
    if dst.master:
        dst = dst.master
    
    if src == dst:
        return False
    
    if src.player and dst.player:
        p1 = src.player
        p2 = dst.player
        if p1 == p2:
            return False
        if p1.alliance and p1.alliance == p2.alliance:
            return False
        if p1.encounterSetting == RPG_ENCOUNTER_PVE or p2.encounterSetting == RPG_ENCOUNTER_PVE:
            return False
        if p1.encounterSetting == RPG_ENCOUNTER_RVR or p2.encounterSetting == RPG_ENCOUNTER_RVR:
            if src.realm == dst.realm:
                return False
        if p1.encounterSetting == RPG_ENCOUNTER_GVG or p2.encounterSetting == RPG_ENCOUNTER_GVG:
            if p1.guildName and p1.guildName == p2.guildName:
                return False
    
    return True


def IsUserSuperior(username1, username2):
    try:
        user1 = User.byName(username1)
    except:
        return False
    
    try:
        user2 = User.byName(username2)
    except:
        return False
    
    from mud.world.newplayeravatar import NewPlayerAvatar
    
    if user1.name == NewPlayerAvatar.ownerPublicName:
        return True #root
    
    if user2.name == NewPlayerAvatar.ownerPublicName:
        return False #root
    
    g1 = g2 = False
    i1 = i2 = False
    
    for role in user1.roles:
        if role.name == "Guardian":
            g1 = True
        if role.name == "Immortal":
            i1 = True
    
    for role in user2.roles:
        if role.name == "Guardian":
            g2 = True
        if role.name == "Immortal":
            i2 = True
            
    #check immortal
    if i1 and i2:
        return False

    if i1 and not i2:
        return True

    if i2 and not i1:
        return False
    
    #check guardian
    if g1 and g2:
        return False

    if g1 and not g2:
        return True

    if g2 and not g1:
        return False
    
    return False
    
        
def IsVisible(mob, target):
    ''' IsVisible: Returns true if the target is visible to the mob
                   based on visibility, not line of sight. '''
                   
    # Target is visible if it is casting or attacking, or if the mob
    # has see invis greater or equal to 1 minus the targets visibility.
    return (target.casting or target.attacking or mob.seeInvisible >= 1.0 - target.visibility)
    

class CoreSettings:
    DIFFICULTY   = RPG_DIFFICULTY_NORMAL
    SINGLEPLAYER = False
    SPPOPULATORS = False
    MOTD         = None
    WORLDTEXT    = ""
    WORLDPIC     = None
    MAXPARTY     = 6
    RESPAWNTIME  = 50.0
    PGSERVER     = False
    LOGCHAT      = None
    LOGGAME      = None
    
    #IDE
    IDE          = False
    IDE_ZONE     = ""
    IDE_EDITZONE = False


