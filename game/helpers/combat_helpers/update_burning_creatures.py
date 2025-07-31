import pygame

def update_burning_creatures(creatures):
    """
    Update all burning creatures and apply damage over time.
    
    Args:
        creatures: List of creature objects
    """
    current_time = pygame.time.get_ticks()
    
    for creature in creatures:
        if hasattr(creature, 'burning_effects') and creature.burning_effects:
            effects_to_remove = []
            
            for effect_id, effect in creature.burning_effects.items():
                elapsed_time = (current_time - effect['start_time']) / 1000.0
                
                # Check if burning duration has expired
                if elapsed_time >= effect['duration']:
                    effects_to_remove.append(effect_id)
                    continue
                
                # Apply damage at tick rate intervals
                time_since_last_tick = (current_time - effect['last_tick']) / 1000.0
                if time_since_last_tick >= effect['tick_rate']:
                    creature.hp -= effect['damage']
                    effect['last_tick'] = current_time
            
            # Remove expired effects
            for effect_id in effects_to_remove:
                del creature.burning_effects[effect_id]