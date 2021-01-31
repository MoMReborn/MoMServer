# Copyright (C) 2004-2007 Prairie Games, Inc
# Please see LICENSE.TXT for details

## @defgroup projectile projectile
#  @ingroup world
#  @brief The projectile module contains the Projectile class which allows for
#         projectiles, such as arrows and bolts, to be launched and collide with
#         objects.
#  @{


from mud.world.core import AllowHarmful,GetRange
from mud.world.damage import Damage
from mud.world.defines import *

from math import ceil
from random import randint



## @brief Projectile contains the basic mechanism to launch projectiles, such as
#         arrows, bolts, and spells at a target and process the collision. 
class Projectile:
    
    ## @brief (Long) Count of created Projectiles.  This value is used to create
    #         identifiers for instances of Projectile.  
    id = 1L
    
    ## @brief Initialize class.
    #  @param self (Projectile) The object pointer.
    #  @param src (Mob) The source Mob that created the Projectile.
    #  @param dst (Mob) The destination Mob that the Projectile targets.
    #  @param level (Integer) The level of the Spell-based Projectile.
    def __init__(self, src, dst, level=1):
        
        ## @brief (Mob) The source Mob that created the projectile.
        self.src = src
        
        ## @brief (Mob) The destination Mob that the Projectile targets and 
        #         with which the Projectile collides.
        #  @details Although the projectile targets a Mob, it may collide with a
        #          different Mob.  The dst attribute will reflect this change.
        self.dst = dst
        
        ## @brief (ItemInstance) The item from which the projectile is launched.
        self.weapon = None
        
        ## @brief (Integer) The damage value of the ammo.
        self.ammoDamage = 0
        
        ## @brief (SpellProto List) List of SpellProtos that may attempt to proc
        #         from the ammo.
        self.ammoSpells = []
        
        ## @brief (SpellProto) The SpellProto for Spell-based projectile.
        self.spellProto = None
        
        ## @brief (Integer) The speed at which the projectile moves.
        self.speed = 1
        
        ## @brief (Integer) The level of the SpellProto for a Spell-based
        #         Projectile.
        self.level = level
        
        ## @brief (String) The name of the Torque ProjectileData being launched.
        self.projectile = None
        
        ## @brief (Long) Unique identifier for Projectile.
        #  @todo TWS: Maybe Python's id() should be used instead?  Technically
        #        a rollaround is possible, but stastical chances of collision is
        #        low.
        self.id = Projectile.id    
        
        # Increase the static projectile counter to prevent projectile
        # identifier collisions.
        Projectile.id+=1
        

    ## @brief Handes the collision of the projectile.
    #  @param self (Projectile) The object pointer.  
    #  @param hitPos (Float Tuple) The location at which the projectile
    #                 collides. 
    def onCollision(self, hitPos):
        
        # Make a local handle to this Projectile's source and destination Mob.
        src = self.src
        dst = self.dst
        
        # If the destination or source has been detached, then return early.
        if dst.detached or src.detached:
            return
        
        # If this projectile was a Spell-based projectile, then handle the
        # Spell.
        if  self.spellProto:
            
            # Return early if the projectile meets all the conditions:
            # - Spell is harmful.
            # - The source of the projectile is not a Character.
            # - The destination is not the source's target. 
            if self.spellProto.spellType&RPG_SPELL_HARMFUL and not src.character and dst != src.target:
                return

            # Mod is the spell power modifier.
            mod = 1.0
            
            # If this projectile's level is not the default level, then increase
            # the spell's modifier based on the projectile's level.
            if self.level != 1.0:
                mod+=self.level/10.0
            
            # TWS: This import should be at global scope.
            from mud.world.spell import SpawnSpell
            
            # Spawn the spell.
            SpawnSpell(self.spellProto,src,dst,hitPos,mod)
            
        # Otherwise, the projectile was an arrow.
        else:
            
            # If the source is not allowed to harm the destination, then return
            # early.
            if not AllowHarmful(src,dst):
                return
            
            # Any aggressive attack by an invulnerable character will remove the
            # character's invulnerability state.  If the source of this
            # projectile is a Character, and the Character is invulnerable, then
            # attack is invulnerable, then cancel the invulnerability effect.
            if src.character:
                src.cancelStatProcess("invulnerable", \
                    "$tgt is no longer protected from death!\\n")
            
            # If the source is not in thehate list of the mob with which the
            # projectile collided, then add the source to the destination's
            # hate list.
            if not dst.aggro.get(src,0):
                dst.addAggro(src,10)
            
            # Get the source's Archery skill.
            askill = src.skillLevels.get("Archery")
            
            # If the source does not have an Archery skill, then return early.
            if not askill:
                return
            
            # missed is used to indicate the source has missed the target.
            missed = False
            
            # If the destination is more than 30 levels above the source,
            # then the source automatically misses.  This is used to prevent a
            # lower level source from kiting a higher level destination for an
            # indefinite amount of time.
            if dst.plevel - src.plevel > 30:
                missed = True
                
            # Otherwise, the source may hit the destination.
            else:
                
                # Calculate the base hit chance for the projectile to hit based
                # on the difference in levels of the destination and source.
                base = 4 - int((float(dst.plevel) - float(src.plevel))/10.0)
                
                # If the base hit chance range is greater than 4, then clamp
                # the unmodified hit chance range to never exceed 4.  This sets
                # the base hit chance to be 4 out of 5.
                if base > 4:
                    base = 4
                    
                # Caculate a modifier that will increase the hit chance based
                # on the source's archery skill level and the destination's
                # level. 
                mod = int(float(askill)*2.0/float(dst.plevel))
                
                # Get the destination's resist.
                resistance = dst.resists.get(RPG_RESIST_PHYSICAL, 0)
                
                # Adjust the modifier based on destination's resist and the
                # source's archery skill level.
                mod -= int(float(resistance)/float(askill))
                
                # If the hit modifier is greater than 20, then clamp the hit
                # modifier to never exceed 20.  
                if mod > 20:
                    mod = 20
                    
                # Increase the base hit chance ranged based on the modifier.
                base += mod
                
                # If the modified hit chance range is less than 1, then clamp
                # the hit chance range to be at least 1.   This sets the worst
                # hit chance to be 1 out of 2.
                if base < 1:
                    base = 1
                    
                # Generate a random number to see if the projectile missed.
                # The projectile has 1 out of base + 1 chance of hitting, and 0
                # indicates a miss.
                if not randint(0,base):
                    missed = True
                    
            # If the projectile missed, then return early.
            if missed:
                
                # If this projectile's source was a Player, then inform the
                # Player.
                if src.character:
                    
                    # Send a different message to the Player depending on the 
                    # distance between the source and destination.
                    if GetRange(src,dst) > 20:
                        src.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s completely misses the target.\n'%src.name)
                    else:
                        src.player.sendGameText(RPG_MSG_GAME_DENIED,r'%s easily deflects %s\'s ranged attack.\n'%(dst.name,src.name))
                        
                # Return early, as the projectile missed.
                return
            
            # Otherwise, the projectile is hitting a target.  If the projectile
            # collided with a Mob that is not the source's target, then the
            # source missed and hit a different Mob.
            elif src.target != dst:
                
                # If this projectile's source was a Player, then inform the
                # Player.
                if src.character:
                    src.player.sendGameText(RPG_MSG_GAME_YELLOW,r'%s misses the target and hits %s instead.\n'%(src.name,dst.name))
                    
                # Otherwise, return early.
                else:
                    return
            
            
            # Caculate the projectile damage based on the source's archery
            # skill level, the weapon damage, and the ammo damage.
            dmg = askill
            wdmg=(self.weapon.wpnDamage + self.ammoDamage)*10
            wdmg*=askill/1000.0
            dmg+=wdmg
            
            # If the damage is less than 20, then clamp the damage to be at
            # least 20.
            if dmg < 20:
                dmg = 20
            
            # Set the actual base damage to be a randomly generated number
            # between 1/2 of the dmg and the dmg.
            dmg = randint(int(dmg/2),int(dmg))
            
            
            # Flag used to indicate if the projectile is doing critical damage.
            critical = False
            
            # Get the source's Precise Shot skill level.
            try:
                icrit = src.skillLevels["Precise Shot"]
            except:
                icrit = 0
            
            # If the source has a Precise Shot skill, then the projectile may
            # do critical damage. 
            if icrit:
                
                # Get the precise shot advancement value.
                ps = src.advancements.get("preciseShot",0.0)
                
                # Calculate the base critical chance range from the source's
                # critical attribute.
                chance = float(ceil(15/src.critical))
                
                # Modify the base critical chance based on the precise shot
                # advancement.
                chance *= 1.0 - ps
                chance = int(chance)
                
                # Generate a random number to see if a critical occurs.  The
                # source has a 1 out of chance + 1 chance to critica, and 0
                # indicates success.
                if not randint(0,chance):
                    
                    # If the source is a Character, then attempt to increase the
                    # source's Precise Shot skill.
                    if src.character:
                        src.character.checkSkillRaise("Precise Shot",5)
                        
                    # Calculate the base damage multiplier based on the source's
                    # Precise Shot skill level.
                    icrit /= 200.0
                    
                    # If the damage multiplier is less than 2, then clamp the 
                    # value to be at least 2.
                    if icrit < 2:
                        icrit = 2.0
                        
                    # TWS: This should be part of an if/else-if.
                    
                    # If the damage multiplier is greater than 5, then clamp the
                    # value to never exceed 5.
                    if icrit > 5:
                        icrit = 5.0
                        
                    # Calculate the new damage value based on the critical's
                    # damage multiplier, Precise Shot advancements, and the 
                    # source's critical attribute.
                    dmg *= icrit*(1.0 + ps)
                    dmg *= src.critical
                    dmg = int(dmg)
                    
                    # Set a flag to indicate a critical has occured.
                    critical = True
            
            # If there is damage to be inflicted, then inflict the damage.
            if dmg:
                
                
                # If the collision is not a critical, then inflict piercing 
                # damage with the default output text.
                if not critical:
                    Damage(dst,src,dmg,RPG_DMG_PIERCING,None,False)
                    
                # Otherwise, a critical occured.  Inflict piercing damage with 
                # with special output text.
                else:
                    Damage(dst,src,dmg,RPG_DMG_PIERCING,"precisely wounds",False)
                
                # TWS: This import should occur at global scope.
                from mud.world.combat import doAttackProcs
                
                # Perform attack procs.
                doAttackProcs(src,dst,self.weapon,self.ammoSpells)
                
                # If the source is a Character, then attempt to increase the
                # source's Archery skill.
                if src.character:
                    src.character.checkSkillRaise("Archery")
    
    
    ## @brief Launches the Projectile.
    #  @param self (Projectile) The object pointer.  
    def launch(self):
        
        # If this Projectile is a Spell-based projectile, then set the
        # projection's projectile and speed based on the SpellProto. 
        if self.spellProto:
            self.projectile = self.spellProto.projectile
            self.speed = self.spellProto.projectileSpeed

        # Delegate the projectile launch to the source's ZoneInstance.
        self.src.zone.launchProjectile(self)



## @} # End projectile group.
