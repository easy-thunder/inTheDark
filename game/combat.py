import pygame
import math
import random
from game.weapons import FireMode, ContactEffect, DamageType

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
        # Create bullet(s)
        if weapon.fire_mode == FireMode.SHOTGUN:
            # Create multiple pellets for shotgun
            for i in range(weapon.volley):
                bullet = create_bullet(player, weapon, player_weapon_indices[current_player_index], tile_size, camera_x, camera_y, pellet_index=i)
                bullets.append(bullet)
        elif weapon.fire_mode == FireMode.SPRAY:
            # Create multiple flame particles for flamethrower
            for i in range(weapon.volley):
                bullet = create_bullet(player, weapon, player_weapon_indices[current_player_index], tile_size, camera_x, camera_y, pellet_index=i)
                bullets.append(bullet)
        else:
            # Create single bullet for other weapons
            bullet = create_bullet(player, weapon, player_weapon_indices[current_player_index], tile_size, camera_x, camera_y)
            bullets.append(bullet)
        
        # Update weapon state
        weapon.current_clip -= 1
        weapon.last_shot_time = now
        
        # Automatic reload if clip is empty and reserve ammo (or infinite)
        if weapon.current_clip == 0 and (player.has_infinite_ammo(weapon) or (weapon.ammo is None or weapon.ammo > 0)):
            player.reload_weapon(player_weapon_indices[current_player_index])
    
    return bullets

def create_bullet(player, weapon, weapon_index, tile_size=32, camera_x=0, camera_y=0, pellet_index=0):
    """
    Create a bullet for the given player and weapon.
    
    Args:
        player: Player object
        weapon: Weapon object
        weapon_index: Index of the weapon in the player's weapon list
        tile_size: Size of tiles in pixels
        camera_x: X coordinate of the camera
        camera_y: Y coordinate of the camera
        pellet_index: Index of pellet for shotguns (0 for single bullets)
    
    Returns:
        Bullet dictionary
    """
    # Calculate base direction
    base_dx, base_dy = player.aim_direction
    
    # Apply spread for shotguns
    if weapon.fire_mode == FireMode.SHOTGUN and weapon.volley > 1:
        # Calculate spread angle for this pellet
        spread_angle = (weapon.spread / (weapon.volley - 1)) * pellet_index - (weapon.spread / 2)
        # Convert to radians and apply to base direction
        spread_rad = math.radians(spread_angle)
        cos_spread = math.cos(spread_rad)
        sin_spread = math.sin(spread_rad)
        dx = base_dx * cos_spread - base_dy * sin_spread
        dy = base_dx * sin_spread + base_dy * cos_spread
    else:
        # Regular accuracy spread for non-shotguns
        spread_angle = (random.uniform(-0.5, 0.5) * weapon.accuracy * 360)
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
        'weapon_index': weapon_index,
        'contact_effect': weapon.contact_effect,
        'bounces': 0,
        'bounce_limit': weapon.bounce_limit,
        'damage_type': weapon.damage_type
    }
    
    # Add flame-specific properties for fire damage
    if weapon.damage_type == DamageType.FIRE:
        bullet['is_flame'] = True
        bullet['burn_duration'] = 3.0  # 3 seconds of burn damage
        bullet['burn_damage'] = weapon.damage
        bullet['burn_tick_rate'] = 0.5  # Damage every 0.5 seconds
        bullet['burned_creatures'] = set()  # Track which creatures are burning
    
    if weapon.fire_mode == FireMode.ORBITAL:
        bullet['is_orbital'] = True
        bullet['z'] = weapon.drop_height
        bullet['initial_z'] = weapon.drop_height
        bullet['fall_speed'] = weapon.bullet_speed

        # Target point based on mouse, adjusted for camera and accuracy
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target_x = mouse_x + camera_x
        target_y = mouse_y + camera_y
        
        # Apply accuracy as a random offset from the cursor
        offset_angle = random.uniform(0, 2 * math.pi)
        offset_radius = weapon.accuracy * (random.random() * 3) # Randomize radius for less of a donut effect
        target_x += math.cos(offset_angle) * offset_radius
        target_y += math.sin(offset_angle) * offset_radius

        # The bullet's (x,y) is the ground target
        bullet['x'] = target_x
        bullet['y'] = target_y
    elif weapon.fire_mode == FireMode.THROWN:
        # This logic is for thrown weapons with special physics (arcing, rolling)
        bullet['is_grenade'] = True # Keep this flag for movement logic
        bullet['detonation_time'] = weapon.detonation_time
        bullet['creation_time'] = pygame.time.get_ticks()
        
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_mouse_x = mouse_x + camera_x
        world_mouse_y = mouse_y + camera_y
        start_x, start_y = player.rect.centerx, player.rect.centery

        # Vector from player to mouse
        dir_dx = world_mouse_x - start_x
        dir_dy = world_mouse_y - start_y
        distance_to_mouse = math.hypot(dir_dx, dir_dy)

        # Normalize direction vector
        if distance_to_mouse == 0:
            norm_dx, norm_dy = player.aim_direction
        else:
            norm_dx = dir_dx / distance_to_mouse
            norm_dy = dir_dy / distance_to_mouse

        # Determine the actual travel distance, clamped by range
        max_throw_range = weapon.range * tile_size
        travel_distance = min(distance_to_mouse, max_throw_range)

        # Calculate the landing spot based on the clamped distance
        target_x = start_x + norm_dx * travel_distance
        target_y = start_y + norm_dy * travel_distance

        # Set velocity so grenade lands at the target spot in N frames
        arc_frames = max(10, min(40, int(travel_distance / 10)))
        velocity = travel_distance / arc_frames if arc_frames > 0 else 0
        velocity_x = norm_dx * velocity
        velocity_y = norm_dy * velocity
        
        bullet['velocity_x'] = velocity_x
        bullet['velocity_y'] = velocity_y
        bullet['start_x'] = start_x
        bullet['start_y'] = start_y
        bullet['landing_x'] = target_x
        bullet['landing_y'] = target_y
        bullet['phase'] = 'flying'
        bullet['roll_distance'] = max(30, min(80, travel_distance * 0.15))
        bullet['roll_dx'] = norm_dx
        bullet['roll_dy'] = norm_dy
        bullet['roll_left'] = bullet['roll_distance']
        bullet['direction_vec'] = (norm_dx, norm_dy)
        bullet['travel_distance'] = travel_distance
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
        if bullet.get('is_orbital'):
            bullet['z'] -= bullet['fall_speed']
            if bullet['z'] <= 0:
                # Landed, now explode
                if bullet.get('splash'):
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, tile_size)
                bullets_to_remove.append(bullet)
                continue
            # Skip all other physics for orbital projectiles
            continue

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
        
        contact_effect = bullet.get('contact_effect')

        # --- Wall Collision ---
        hit_wall = False
        for wall in visible_walls:
            if bullet_rect.colliderect(wall):
                hit_wall = True
                can_bounce = contact_effect in (ContactEffect.DAMAGE_BOUNCE, ContactEffect.NO_DAMAGE_BOUNCE) and bullet.get('bounce_limit') is not None and bullet.get('bounces', 0) < bullet.get('bounce_limit')
                
                if can_bounce:
                    bullet['bounces'] += 1
                    # --- Perform bounce physics ---
                    # Calculate overlap to determine collision side
                    dx_overlap = min(bullet_rect.right - wall.left, wall.right - bullet_rect.left)
                    dy_overlap = min(bullet_rect.bottom - wall.top, wall.bottom - bullet_rect.top)

                    if dx_overlap < dy_overlap:
                        # Horizontal collision
                        if bullet.get('is_grenade'): bullet['velocity_x'] *= -1
                        else: bullet['dx'] *= -1
                    else:
                        # Vertical collision
                        if bullet.get('is_grenade'): bullet['velocity_y'] *= -1
                        else: bullet['dy'] *= -1
                else:
                    # --- Cannot bounce, handle other effects or remove ---
                    if contact_effect == ContactEffect.EXPLODE:
                        if bullet.get('splash'): splash_effects = handle_splash_damage(bullet, creatures, splash_effects, tile_size)
                    bullets_to_remove.append(bullet)
                break 
        if hit_wall: continue

        # --- Creature Collision ---
        collided_creature = None
        for creature in creatures:
            if creature.hp > 0 and bullet_rect.colliderect(creature.rect):
                collided_creature = creature
                break

        if collided_creature:
            can_bounce = contact_effect in (ContactEffect.DAMAGE_BOUNCE, ContactEffect.NO_DAMAGE_BOUNCE) and bullet.get('bounce_limit') is not None and bullet.get('bounces', 0) < bullet.get('bounce_limit')

            if can_bounce:
                # Deal damage only if it's a damage-dealing bounce
                if contact_effect == ContactEffect.DAMAGE_BOUNCE:
                    if 'hit_creatures' not in bullet:
                        bullet['hit_creatures'] = set()
                    
                    if id(collided_creature) not in bullet['hit_creatures']:
                        collided_creature.hp -= bullet['damage']
                        bullet['hit_creatures'].add(id(collided_creature))

                bullet['bounces'] += 1
                
                # --- Perform bounce physics ---
                creature_rect = collided_creature.rect
                # Calculate overlap to determine collision side
                dx_overlap = min(bullet_rect.right - creature_rect.left, creature_rect.right - bullet_rect.left)
                dy_overlap = min(bullet_rect.bottom - creature_rect.top, creature_rect.bottom - bullet_rect.top)

                if dx_overlap < dy_overlap:
                    # Horizontal collision
                    if bullet.get('is_grenade'): bullet['velocity_x'] *= -1
                    else: bullet['dx'] *= -1
                else:
                    # Vertical collision
                    if bullet.get('is_grenade'): bullet['velocity_y'] *= -1
                    else: bullet['dy'] *= -1
            elif contact_effect == ContactEffect.EXPLODE:
                if bullet.get('splash'): splash_effects = handle_splash_damage(bullet, creatures, splash_effects, tile_size)
                bullets_to_remove.append(bullet)
            elif contact_effect == ContactEffect.PIERCE:
                # Handle flame weapons with burning effects
                if bullet.get('damage_type') == DamageType.FIRE:
                    should_remove = handle_burning_effects(bullet, collided_creature, players)
                    if should_remove:
                        bullets_to_remove.append(bullet)
                else:
                    # Regular piercing logic
                    if handle_creature_collision(bullet, bullet_rect, creatures, players):
                        bullets_to_remove.append(bullet)
            else: # Bouncing bullet that has run out of bounces
                bullets_to_remove.append(bullet)
            continue

    # Remove bullets marked for removal
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

def handle_burning_effects(bullet, creature, players):
    """
    Handle burning damage over time effects for flame weapons.
    
    Args:
        bullet: Bullet dictionary with flame properties
        creature: Creature object that was hit
        players: List of Player objects
    
    Returns:
        True if bullet should be removed, False if it should continue
    """
    if not bullet.get('is_flame') or bullet.get('damage_type') != DamageType.FIRE:
        return False
    
    creature_id = id(creature)
    
    # Initialize burning data for this creature if not already burning
    if creature_id not in bullet['burned_creatures']:
        bullet['burned_creatures'].add(creature_id)
        
        # Apply initial damage
        creature.hp -= bullet['burn_damage']
        
        # Initialize burning state on creature
        if not hasattr(creature, 'burning_effects'):
            creature.burning_effects = {}
        
        # Add or update burning effect
        creature.burning_effects[creature_id] = {
            'damage': bullet['burn_damage'],
            'duration': bullet['burn_duration'],
            'tick_rate': bullet['burn_tick_rate'],
            'start_time': pygame.time.get_ticks(),
            'last_tick': pygame.time.get_ticks()
        }
    
    # Don't remove the bullet - let it continue to spread fire
    return False

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