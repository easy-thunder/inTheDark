import math
import pygame

from game.weapons import EnemyContactEffect
from game.weapons import ContactEffect
from game.helpers.combat_helpers.apply_poison import apply_poison

def apply_creature_effects(bullet, creature):
    """Apply all enemy effects from a bullet to a creature."""
    # Always apply direct damage first
    creature.hp -= bullet['damage']
    
    # Apply each enemy effect
    for effect in bullet['enemy_effects']:
        if effect == EnemyContactEffect.PHYSICAL:
            continue  # Physical damage already applied
            
        elif effect == EnemyContactEffect.FIRE:
            # Initialize burning_effects as a dict
            if not hasattr(creature, 'burning_effects') or creature.burning_effects is None:
                creature.burning_effects = {}
            # Add or refresh burning effect
            creature.burning_effects[id(creature)] = {
                'damage': bullet.get('burn_damage', bullet['damage'] * 0.3),  # 30% of base damage as burn
                'duration': 3.0,
                'tick_rate': 0.5,
                'start_time': pygame.time.get_ticks(),
                'last_tick': pygame.time.get_ticks()
            }
            
        elif effect == EnemyContactEffect.ICE:
            if hasattr(creature, 'apply_slow'):
                creature.apply_slow(duration=3000, factor=0.5)
                
        elif effect == EnemyContactEffect.POISON:
            apply_poison(creature, bullet['damage'])
            
        elif effect == EnemyContactEffect.KNOCKBACK:
            # Skip knockback for beam weapons
            if bullet.get('type') == 'beam':
                continue

            # Initialize knockback attributes if they don't exist
            if not hasattr(creature, 'knockback_dx'):
                creature.knockback_dx = 0
                creature.knockback_dy = 0
                creature.knockback_resistance = getattr(creature, 'knockback_resistance', 1.0)

            knockback_force = bullet.get('knockback_force', 10)  # Default force if not specified
            
            if bullet.get('is_orbital_beam') or bullet.get('contact_effect') == ContactEffect.EXPLODE:
                # Knockback from center point for explosions and orbital beams
                dx = creature.rect.centerx - bullet['x']
                dy = creature.rect.centery - bullet['y']
            else:
                # Knockback in bullet's direction for regular bullets
                dx = bullet['dx']
                dy = bullet['dy']
            
            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
                
                # Apply knockback force (reduced by creature's knockback resistance)
                creature.knockback_dx = dx * knockback_force * (1 - creature.knockback_resistance)
                creature.knockback_dy = dy * knockback_force * (1 - creature.knockback_resistance) 