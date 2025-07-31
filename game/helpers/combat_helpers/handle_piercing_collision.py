def handle_piercing_collision(bullet, creature, players):
    """
    Handle piercing collision logic for bullets.

    Args:
        bullet: Bullet dictionary
        creature: Creature object that was hit
        players: List of Player objects

    Returns:
        True if bullet should be removed, False if it should continue
    """
    # Initialize piercing data if not present
    if 'pierces_left' not in bullet:
        weapon_index = bullet.get('weapon_index', 0)
        weapon = None
        for player in players:
            if hasattr(player.character, 'weapons') and len(player.character.weapons) > weapon_index:
                weapon = player.character.weapons[weapon_index]
                break
        piercing = getattr(weapon, 'piercing', 0) if weapon else 0
        bullet['pierces_left'] = piercing
        bullet['original_damage'] = bullet['damage']
        bullet['hit_creatures'] = set()

    # Check if we've already hit this creature
    if id(creature) in bullet['hit_creatures']:
        return False

    # Apply damage
    creature.hp -= bullet['damage']
    bullet['hit_creatures'].add(id(creature))

    # If piercing is 0, remove bullet immediately
    if bullet['pierces_left'] == 0:
        return True

    # If piercing > 0, decrement piercing and reduce damage
    bullet['pierces_left'] -= 1
    min_damage = bullet['original_damage'] * 0.3
    new_damage = bullet['damage'] * 0.9
    bullet['damage'] = max(min_damage, new_damage)

    # If out of pierces, remove bullet
    if bullet['pierces_left'] < 0:
        return True

    return False