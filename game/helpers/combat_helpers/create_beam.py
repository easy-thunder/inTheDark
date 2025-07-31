def create_beam(x, y, angle, weapon):
    """Create a lightning-fast beam projectile"""
    return {
        'x': x,
        'y': y,
        'angle': angle,
        'speed': weapon.common.bullet_speed,
        'damage': weapon.common.damage,
        'size': weapon.common.bullet_size,
        'color': weapon.common.bullet_color,
        'range': weapon.common.range * 32,  # Use weapon's actual range
        'piercing': weapon.uncommon.piercing or 0,
        'enemy_effects': weapon.common.enemy_effects,
        'hits': set(),  # Track creatures hit to prevent multiple hits
        'trail_points': [(x, y)],  # Store trail points for visual effect
        'type': 'beam'
    }