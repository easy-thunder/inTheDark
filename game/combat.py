import pygame
import math
import random

def handle_firing(players, player_weapon_indices, bullets, current_player_index=0, tile_size=32):
    """
    Handle automatic firing for the specified player.
    
    Args:
        players: List of Player objects
        player_weapon_indices: List of weapon indices for each player
        bullets: List of active bullets
        current_player_index: Index of the player to handle firing for (default 0)
        tile_size: Size of tiles in pixels
    
    Returns:
        Updated bullets list
    """
    player = players[current_player_index]
    if player.dead:
        return bullets
    
    weapon = player.character.weapons[player_weapon_indices[current_player_index]]
    now = pygame.time.get_ticks()
    
    # Handle warm-up time
    if weapon.warm_up_time and not weapon.is_warming_up:
        weapon.is_warming_up = True
        weapon.warm_up_start = now
    
    # Check if weapon is ready to fire (warmed up or no warm-up required)
    can_fire = True
    if weapon.warm_up_time and weapon.is_warming_up:
        warm_up_elapsed = (now - weapon.warm_up_start) / 1000.0
        if warm_up_elapsed < weapon.warm_up_time:
            can_fire = False
    
    fire_delay = 60000 / weapon.fire_rate  # ms per shot
    if can_fire and now - weapon.last_shot_time >= fire_delay and weapon.current_clip > 0 and not weapon.is_reloading:
        # Create bullet
        bullet = create_bullet(player, weapon, player_weapon_indices[current_player_index], tile_size)
        bullets.append(bullet)
        
        # Update weapon state
        weapon.current_clip -= 1
        weapon.last_shot_time = now
        
        # Automatic reload if clip is empty and reserve ammo (or infinite)
        if weapon.current_clip == 0 and (player.has_infinite_ammo(weapon) or (weapon.ammo is None or weapon.ammo > 0)):
            player.reload_weapon(player_weapon_indices[current_player_index])
    
    return bullets

def create_bullet(player, weapon, weapon_index, tile_size=32):
    """
    Create a bullet for the given player and weapon.
    
    Args:
        player: Player object
        weapon: Weapon object
        weapon_index: Index of the weapon in the player's weapon list
        tile_size: Size of tiles in pixels
    
    Returns:
        Bullet dictionary
    """
    spread_angle = (random.uniform(-0.5, 0.5) * weapon.accuracy * 360)
    base_dx, base_dy = player.aim_direction
    angle = math.atan2(base_dy, base_dx) + math.radians(spread_angle)
    dx = math.cos(angle)
    dy = math.sin(angle)
    
    # Calculate bullet properties
    bullet_speed = weapon.bullet_speed
    bullet_range = weapon.range * tile_size
    bullet_size = int(weapon.bullet_size * tile_size)
    
    return {
        'x': player.rect.centerx,
        'y': player.rect.centery,
        'dx': dx,
        'dy': dy,
        'speed': bullet_speed,
        'range': bullet_range,
        'distance': 0,
        'size': bullet_size,
        'damage': weapon.damage,
        'color': weapon.bullet_color,
        'splash': weapon.splash,
        'weapon_index': weapon_index
    }

def reset_warm_up(players):
    """
    Reset warm-up state for all weapons of all players.
    
    Args:
        players: List of Player objects
    """
    for player in players:
        for weapon in player.character.weapons:
            if weapon.warm_up_time:
                weapon.is_warming_up = False
                weapon.warm_up_start = None

def update_bullets(bullets, visible_walls, creatures, splash_effects, players, tile_size=32):
    """
    Update bullet positions and handle collisions.
    
    Args:
        bullets: List of active bullets
        visible_walls: List of wall rectangles
        creatures: List of creature objects
        splash_effects: List of splash effects
        players: List of Player objects
        tile_size: Size of tiles in pixels
    
    Returns:
        Tuple of (updated_bullets, updated_splash_effects)
    """
    # Update bullet positions
    for bullet in bullets[:]:
        bullet['x'] += bullet['dx'] * bullet['speed']
        bullet['y'] += bullet['dy'] * bullet['speed']
        bullet['distance'] += bullet['speed']
        if bullet['distance'] > bullet['range']:
            bullets.remove(bullet)
    
    # Handle bullet collisions
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(
            bullet['x'] - bullet['size'],
            bullet['y'] - bullet['size'],
            bullet['size'] * 2,
            bullet['size'] * 2
        )
        
        # Wall collision
        hit_wall = False
        for wall in visible_walls:
            if bullet_rect.colliderect(wall):
                hit_wall = True
                break
        
        if hit_wall:
            # Handle splash damage
            if bullet.get('splash'):
                splash_effects = handle_splash_damage(bullet, creatures, splash_effects, tile_size)
            bullets.remove(bullet)
            continue
        
        # Creature collision with piercing
        hit_creature = handle_creature_collision(bullet, bullet_rect, creatures, players)
        if hit_creature:
            bullets.remove(bullet)
            continue
    
    return bullets, splash_effects

def handle_splash_damage(bullet, creatures, splash_effects, tile_size=32):
    """
    Handle splash damage from explosive bullets.
    
    Args:
        bullet: Bullet dictionary
        creatures: List of creature objects
        splash_effects: List of splash effects
        tile_size: Size of tiles in pixels
    
    Returns:
        Updated splash_effects list
    """
    splash_radius = bullet['splash'] * tile_size
    center = (bullet['x'], bullet['y'])
    splash_damages = [20, 16, 12, 8, 2]
    
    for creature in creatures:
        if creature.hp > 0:
            dist = math.hypot(creature.rect.centerx - center[0], creature.rect.centery - center[1])
            for i in range(5):
                if dist <= splash_radius * (i+1)/5:
                    creature.hp -= splash_damages[i]
                    break
    
    # Add splash effect for visual
    splash_effects.append({'x': center[0], 'y': center[1], 'radius': splash_radius, 'start': pygame.time.get_ticks()})
    return splash_effects

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