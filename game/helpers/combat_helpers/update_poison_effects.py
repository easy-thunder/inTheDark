import pygame


def update_poison_effects(creatures):
    """
    Update all poisoned creatures and apply damage over time.
    """
    current_time = pygame.time.get_ticks()

    for creature in creatures:
        if hasattr(creature, 'poison_effects') and creature.poison_effects:
            effects_to_remove = []
            
            for i, effect in enumerate(creature.poison_effects):
                elapsed_time = (current_time - effect['start_time'])
                
                # Check if poison duration has expired
                if elapsed_time >= effect['duration']:
                    effects_to_remove.append(i)
                    continue
                
                # Apply damage at tick rate intervals
                time_since_last_tick = (current_time - effect['last_tick'])
                if time_since_last_tick >= effect['tick_rate']:
                    creature.hp -= effect['damage_per_tick']
                    effect['last_tick'] = current_time
            
            # Remove expired effects by index, in reverse order to not mess up indices
            for i in sorted(effects_to_remove, reverse=True):
                del creature.poison_effects[i]