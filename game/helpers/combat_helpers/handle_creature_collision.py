from game.helpers.combat_helpers.handle_piercing_collision import handle_piercing_collision



def handle_creature_collision(bullet, bullet_rect, creatures, players):
    """
    Handle bullet collision with creatures, including piercing logic.
    
    Args:
        bullet: Bullet dictionary
        bullet_rect: Bullet rectangle for collision detection
        creatures: List of creature objects
        players: List of Player objects
    
    Returns:
        True if bullet should be removed, False if it should continue
    """
    # Find all creatures that this bullet collides with
    hit_creatures = []
    for creature in creatures:
        if creature.hp > 0 and bullet_rect.colliderect(creature.rect):
            hit_creatures.append(creature)
    
    if not hit_creatures:
        return False
    
    # Handle splash damage
    if bullet.get('splash'):
        return True  # Bullet will be removed by caller
    
    # Handle piercing logic for all hit creatures
    for creature in hit_creatures:
        should_remove = handle_piercing_collision(bullet, creature, players)
        if should_remove:
            return True  # Remove bullet if piercing logic says so
    
    return False
