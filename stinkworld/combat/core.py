"""Core combat mechanics."""
import random
from stinkworld.core.settings import (
    DAMAGE_MULTIPLIER, DEFENSE_MULTIPLIER,
    CRITICAL_HIT_CHANCE, CRITICAL_HIT_MULTIPLIER
)
from stinkworld.utils.debug import debug_log

def calculate_damage(attacker, defender, base_damage):
    """Calculate damage dealt in combat."""
    # Apply attacker's strength and defender's defense
    damage = base_damage * (1 + attacker.strength * DAMAGE_MULTIPLIER)
    damage *= (1 - defender.defense * DEFENSE_MULTIPLIER)
    
    # Critical hit check
    if random.random() < CRITICAL_HIT_CHANCE:
        damage *= CRITICAL_HIT_MULTIPLIER
        return int(damage), True
    
    return int(damage), False

def apply_damage(target, damage):
    """Apply damage to target and check for knockout/death."""
    target.hp -= damage
    
    if target.hp <= 0:
        target.is_dead = True
        return "death"
    elif target.hp < target.max_hp * 0.3:
        if random.random() < 0.3:  # 30% chance to be knocked out when low health
            target.is_knocked_out = True
            return "knockout"
    
    return "damage"

def can_fight(entity):
    """Check if an entity can fight."""
    return (not entity.is_dead and 
            not entity.is_knocked_out and 
            entity.hp > 0)

def get_combat_stats(entity):
    """Get entity's combat-relevant stats."""
    return {
        'hp': entity.hp,
        'max_hp': entity.max_hp,
        'strength': entity.strength,
        'defense': entity.defense,
        'is_knocked_out': entity.is_knocked_out,
        'is_dead': entity.is_dead
    }

def heal_entity(entity, amount):
    """Heal an entity and potentially revive from knockout."""
    if entity.is_dead:
        return False
    
    entity.hp = min(entity.hp + amount, entity.max_hp)
    
    if entity.is_knocked_out and entity.hp > entity.max_hp * 0.3:
        entity.is_knocked_out = False
        return True
    
    return False