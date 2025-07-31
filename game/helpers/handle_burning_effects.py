import pygame
from game.weapons import EnemyContactEffect

def handle_burning_effects(bullet, creature, players):
    """
    Handle burning damage over time effects for flame weapons.
    """
    if not bullet.get('is_flame') or EnemyContactEffect.FIRE not in bullet['enemy_effects']:
        return False
    
    creature_id = id(creature)
    
    # Initialize burning data for this creature if not already burning
    if creature_id not in bullet.get('burned_creatures', set()):
        if not hasattr(bullet, 'burned_creatures'):
            bullet['burned_creatures'] = set()
        bullet['burned_creatures'].add(creature_id)
        
        # Apply initial damage
        creature.hp -= bullet['burn_damage']
        
        # Initialize burning state on creature
        if not hasattr(creature, 'burning_effects'):
            creature.burning_effects = {}
        
        # Add or update burning effect
        creature.burning_effects[creature_id] = {
            'damage': bullet['burn_damage'],
            'duration': 3.0,  # 3 seconds burn duration
            'tick_rate': 0.5,  # Damage every 0.5 seconds
            'start_time': pygame.time.get_ticks(),
            'last_tick': pygame.time.get_ticks()
        }
    
    # Don't remove the bullet - let it continue to spread fire
    return False
