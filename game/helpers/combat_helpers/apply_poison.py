import pygame


def apply_poison(creature, base_damage):
    if not hasattr(creature, 'poison_effects'):
        creature.poison_effects = []

    # Limit stacks to 4
    if len(creature.poison_effects) >= 4:
        # Refresh duration of existing stacks instead of adding a new one
        for effect in creature.poison_effects:
            effect['start_time'] = pygame.time.get_ticks()
        return

    # Calculate damage for the new stack with diminishing returns
    if not creature.poison_effects:
        new_damage = base_damage  # First stack does full damage
    else:
        last_damage = creature.poison_effects[-1]['damage_per_tick']
        new_damage = last_damage * 0.7  # Subsequent stacks do 70% of the previous

    new_effect = {
        'damage_per_tick': new_damage,
        'duration': 20000,  # 20 seconds
        'tick_rate': 1000,   # 1 second
        'start_time': pygame.time.get_ticks(),
        'last_tick': pygame.time.get_ticks()
    }
    creature.poison_effects.append(new_effect)


