import pygame
import math
import random

def handle_firing(players, player_weapon_indices, bullets, current_player_index=0, tile_size=32, camera_x=0, camera_y=0):
    """
    Handle automatic firing for the specified player.
    
    Args:
        players: List of Player objects
        player_weapon_indices: List of weapon indices for each player
        bullets: List of active bullets
        current_player_index: Index of the player to handle firing for (default 0)
        tile_size: Size of tiles in pixels
        camera_x: X coordinate of the camera
        camera_y: Y coordinate of the camera
    
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
        bullet = create_bullet(player, weapon, player_weapon_indices[current_player_index], tile_size, camera_x, camera_y)
        bullets.append(bullet)
        
        # Update weapon state
        weapon.current_clip -= 1
        weapon.last_shot_time = now
        
        # Automatic reload if clip is empty and reserve ammo (or infinite)
        if weapon.current_clip == 0 and (player.has_infinite_ammo(weapon) or (weapon.ammo is None or weapon.ammo > 0)):
            player.reload_weapon(player_weapon_indices[current_player_index])
    
    return bullets

def create_bullet(player, weapon, weapon_index, tile_size=32, camera_x=0, camera_y=0):
    """
    Create a bullet for the given player and weapon.
    
    Args:
        player: Player object
        weapon: Weapon object
        weapon_index: Index of the weapon in the player's weapon list
        tile_size: Size of tiles in pixels
        camera_x: X coordinate of the camera
        camera_y: Y coordinate of the camera
    
    Returns:
        Bullet dictionary
    """
    spread_angle = (random.uniform(-0.5, 0.5) * weapon.accuracy * 360)
    base_dx, base_dy = player.aim_direction
    angle = math.atan2(base_dy, base_dx) + math.radians(spread_angle)
    dx = math.cos(angle)
    dy = math.sin(angle)
    
    bullet_speed = weapon.bullet_speed
    bullet_range = weapon.range * tile_size
    bullet_size = int(weapon.bullet_size * tile_size)
    
    bullet = {
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
    
    if weapon.detonation_time:
        bullet['detonation_time'] = weapon.detonation_time
        bullet['creation_time'] = pygame.time.get_ticks()
        bullet['is_grenade'] = True
        bullet['bounces'] = 0
        bullet['max_bounces'] = 3
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y
        start_x, start_y = player.rect.centerx, player.rect.centery
        target_x = world_mouse_x
        target_y = world_mouse_y
        dx = target_x - start_x
        dy = target_y - start_y
        distance_to_target = math.hypot(dx, dy)
        if distance_to_target == 0:
            dx, dy = 1, 0
            distance_to_target = 1
        norm_dx = dx / distance_to_target
        norm_dy = dy / distance_to_target
        
        # Set velocity so grenade lands at mouse position in N frames
        arc_frames = max(10, min(40, int(distance_to_target / 10)))
        velocity = distance_to_target / arc_frames
        velocity_x = norm_dx * velocity
        velocity_y = norm_dy * velocity
        
        bullet['velocity_x'] = velocity_x
        bullet['velocity_y'] = velocity_y
        bullet['start_x'] = start_x
        bullet['start_y'] = start_y
        bullet['landing_x'] = target_x
        bullet['landing_y'] = target_y
        bullet['phase'] = 'flying'
        bullet['roll_distance'] = max(30, min(80, distance_to_target * 0.15))
        bullet['roll_dx'] = norm_dx
        bullet['roll_dy'] = norm_dy
        bullet['roll_left'] = bullet['roll_distance']
        bullet['direction_vec'] = (norm_dx, norm_dy)
        bullet['travel_distance'] = distance_to_target
        bullet['distance_traveled'] = 0
    
    return bullet

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
    bullets_to_remove = []
    for bullet in bullets[:]:
        if bullet.get('is_grenade'):
            now = pygame.time.get_ticks()
            if now - bullet['creation_time'] >= bullet['detonation_time'] * 1000:
                if bullet.get('splash'):
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, tile_size)
                bullets_to_remove.append(bullet)
                continue
            
            if bullet['phase'] == 'flying':
                # Move toward landing point
                bullet['x'] += bullet['velocity_x']
                bullet['y'] += bullet['velocity_y']
                bullet['distance_traveled'] += math.hypot(bullet['velocity_x'], bullet['velocity_y'])
                # Use dot product to check if passed landing point
                start_x, start_y = bullet['start_x'], bullet['start_y']
                landing_x, landing_y = bullet['landing_x'], bullet['landing_y']
                dir_x, dir_y = bullet['direction_vec']
                to_current = ((bullet['x'] - start_x), (bullet['y'] - start_y))
                to_landing = ((landing_x - start_x), (landing_y - start_y))
                dot = to_current[0]*to_landing[0] + to_current[1]*to_landing[1]
                if dot >= 0 and bullet['distance_traveled'] >= bullet['travel_distance']:
                    bullet['phase'] = 'rolling'
                    bullet['velocity_x'] = bullet['roll_dx'] * 2
                    bullet['velocity_y'] = bullet['roll_dy'] * 2
            elif bullet['phase'] == 'rolling':
                bullet['x'] += bullet['velocity_x']
                bullet['y'] += bullet['velocity_y']
                bullet['roll_left'] -= math.hypot(bullet['velocity_x'], bullet['velocity_y'])
                bullet['velocity_x'] *= 0.92
                bullet['velocity_y'] *= 0.92
                if bullet['roll_left'] <= 0 or (abs(bullet['velocity_x']) < 0.2 and abs(bullet['velocity_y']) < 0.2):
                    bullet['velocity_x'] = 0
                    bullet['velocity_y'] = 0
                    bullet['phase'] = 'stopped'
        else:
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']
            bullet['distance'] += bullet['speed']
            if bullet['distance'] > bullet['range']:
                bullets_to_remove.append(bullet)
                continue
        
        bullet_rect = pygame.Rect(
            bullet['x'] - bullet['size'],
            bullet['y'] - bullet['size'],
            bullet['size'] * 2,
            bullet['size'] * 2
        )
        
        hit_wall = False
        for wall in visible_walls:
            if bullet_rect.colliderect(wall):
                hit_wall = True
                if bullet.get('is_grenade'):
                    if bullet['phase'] in ('flying', 'rolling'):
                        center_x = bullet_rect.centerx
                        center_y = bullet_rect.centery
                        if abs(center_x - wall.left) < 5:
                            normal = (1, 0)
                        elif abs(center_x - wall.right) < 5:
                            normal = (-1, 0)
                        elif abs(center_y - wall.top) < 5:
                            normal = (0, 1)
                        elif abs(center_y - wall.bottom) < 5:
                            normal = (0, -1)
                        else:
                            normal = (0, 0)
                        v = [bullet['velocity_x'], bullet['velocity_y']]
                        dot = v[0]*normal[0] + v[1]*normal[1]
                        v_reflect = [v[0] - 2*dot*normal[0], v[1] - 2*dot*normal[1]]
                        # Set new landing point in reflected direction
                        distance = bullet['travel_distance']
                        bullet['velocity_x'] = v_reflect[0]
                        bullet['velocity_y'] = v_reflect[1]
                        bullet['start_x'] = bullet['x']
                        bullet['start_y'] = bullet['y']
                        bullet['landing_x'] = bullet['x'] + v_reflect[0] * (distance / max(abs(v_reflect[0]), abs(v_reflect[1]), 1))
                        bullet['landing_y'] = bullet['y'] + v_reflect[1] * (distance / max(abs(v_reflect[0]), abs(v_reflect[1]), 1))
                        norm = math.hypot(v_reflect[0], v_reflect[1])
                        if norm == 0:
                            norm = 1
                        bullet['direction_vec'] = (v_reflect[0]/norm, v_reflect[1]/norm)
                        bullet['distance_traveled'] = 0
                        bullet['phase'] = 'flying'
                        bullet['roll_left'] = bullet['roll_distance']
                    bullet['bounces'] += 1
                    if bullet['bounces'] >= bullet['max_bounces']:
                        if bullet.get('splash'):
                            splash_effects = handle_splash_damage(bullet, creatures, splash_effects, tile_size)
                        bullets_to_remove.append(bullet)
                        continue
                else:
                    if bullet.get('splash'):
                        splash_effects = handle_splash_damage(bullet, creatures, splash_effects, tile_size)
                    bullets_to_remove.append(bullet)
                break
        if hit_wall:
            continue
        if not bullet.get('is_grenade'):
            hit_creature = handle_creature_collision(bullet, bullet_rect, creatures, players)
            if hit_creature:
                bullets_to_remove.append(bullet)
                continue
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
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