import pygame
import math
import random
from game.weapons import FireMode, ContactEffect, EnemyContactEffect

def handle_firing(players, indices, bullets, current_player_index=0, tile_size=32, camera_x=0, camera_y=0, ability_active=None, is_ability=False):
    """
    Handle firing for weapons or abilities depending on is_ability flag.
    """
    player = players[current_player_index]
    if player.dead:
        return bullets
    
    if is_ability:
        ability_index = indices[current_player_index]
        ability = player.character.abilities[ability_index]
        now = pygame.time.get_ticks()
        if getattr(ability, 'is_ability', False) and ability_active is not None and ability_active[0]:
            ap_cost = getattr(ability.uncommon, 'ap_cost', 0)
            if player.ability_points >= ap_cost:
                player.ability_points -= ap_cost
                # Create mine bullet at player location
                bullet = create_bullet(player, ability, ability_index, tile_size, camera_x, camera_y)
                bullet['is_mine'] = True
                bullet['trigger_radius'] = getattr(ability.uncommon, 'trigger_radius', 32)
                bullet['splash'] = getattr(ability.uncommon, 'splash', 2.0)
                bullets.append(bullet)
            # Reset ability_active so only one mine per press
            ability_active[0] = False
            return bullets
        return bullets
    else:
        weapon_index = indices[current_player_index]
        weapon = player.character.weapons[weapon_index]
        now = pygame.time.get_ticks()

    # --- Ability weapon firing (e.g., mine) ---
    if getattr(weapon, 'is_ability', False) and ability_active is not None and ability_active[0]:
        ap_cost = getattr(weapon.uncommon, 'ap_cost', 0)
        if player.ability_points >= ap_cost:
            player.ability_points -= ap_cost
            # Create mine bullet at player location
            bullet = create_bullet(player, weapon, weapon_index, tile_size, camera_x, camera_y)
            bullet['is_mine'] = True
            bullet['trigger_radius'] = getattr(weapon.uncommon, 'trigger_radius', 32)
            bullet['splash'] = getattr(weapon.uncommon, 'splash', 2.0)
            bullets.append(bullet)
        # Reset ability_active so only one mine per press
        ability_active[0] = False
        return bullets
    
    # Handle warm-up time
    if weapon.uncommon.warm_up_time and not weapon.is_warming_up:
        weapon.is_warming_up = True
        weapon.warm_up_start = now
    
    # Check if weapon is ready to fire (warmed up or no warm-up required)
    can_fire = True
    if weapon.uncommon.warm_up_time and weapon.is_warming_up:
        warm_up_elapsed = (now - weapon.warm_up_start) / 1000.0
        if warm_up_elapsed < weapon.uncommon.warm_up_time:
            can_fire = False
    
    fire_delay = 60000 / weapon.common.fire_rate  # ms per shot
    if can_fire and now - weapon.last_shot_time >= fire_delay and weapon.current_clip > 0 and not weapon.is_reloading:
        # Create bullet(s)
        if weapon.common.fire_mode == FireMode.SHOTGUN:
            for i in range(weapon.uncommon.volley or 1):
                bullet = create_bullet(player, weapon, weapon_index, tile_size, camera_x, camera_y, pellet_index=i)
                bullets.append(bullet)
        elif weapon.common.fire_mode == FireMode.SPRAY:
            base_angle = math.atan2(player.aim_direction[1], player.aim_direction[0])
            for i in range((weapon.uncommon.volley or 1) * 2):
                spread_angle = ((weapon.uncommon.spread or 0) / ((weapon.uncommon.volley or 1) * 2 - 1)) * i - ((weapon.uncommon.spread or 0) / 2)
                spread_angle += random.uniform(-5, 5)
                spread_rad = math.radians(spread_angle)
                cos_spread = math.cos(spread_rad)
                sin_spread = math.sin(spread_rad)
                dx = player.aim_direction[0] * cos_spread - player.aim_direction[1] * sin_spread
                dy = player.aim_direction[0] * sin_spread + player.aim_direction[1] * cos_spread
                speed_variation = random.uniform(0.8, 1.2)
                bullet = create_bullet(player, weapon, weapon_index, tile_size, camera_x, camera_y, pellet_index=i)
                bullet['dx'] = dx
                bullet['dy'] = dy
                bullet['speed'] = weapon.common.bullet_speed * speed_variation
                bullet['particle_variation'] = random.uniform(0, 2 * math.pi)
                bullet['particle_size_variation'] = random.uniform(0.7, 1.3)
                bullet['particle_intensity'] = random.uniform(0.8, 1.2)
                bullets.append(bullet)
        elif weapon.common.fire_mode == FireMode.ORBITAL:
            bullet = create_bullet(player, weapon, weapon_index, tile_size, camera_x, camera_y)
            bullets.append(bullet)
        elif weapon.common.fire_mode == FireMode.ORBITAL_BEAM:
            bullet = create_bullet(player, weapon, weapon_index, tile_size, camera_x, camera_y)
            bullets.append(bullet)
        elif weapon.common.fire_mode == FireMode.BEAM:
            # Handle beam weapons (lightning-fast piercing beam)
            bullets.append(create_beam(player.rect.centerx, player.rect.centery, math.atan2(player.aim_direction[1], player.aim_direction[0]), weapon))
        else:
            bullet = create_bullet(player, weapon, weapon_index, tile_size, camera_x, camera_y)
            bullets.append(bullet)
        
        # Update weapon state
        weapon.current_clip -= 1
        weapon.last_shot_time = now
        
        # Automatic reload if clip is empty and reserve ammo (or infinite)
        if weapon.current_clip == 0 and (player.has_infinite_ammo(weapon) or (weapon.common.ammo is None or weapon.common.ammo > 0)):
            player.reload_weapon(weapon_index)
    
    # Special case for orbital beam weapons - they can fire even during warm-up
    elif weapon.common.fire_mode == FireMode.ORBITAL_BEAM and weapon.current_clip > 0 and not weapon.is_reloading:
        # Create orbital beam weapon immediately, let bullet handle its own warm-up
        bullet = create_bullet(player, weapon, weapon_index, tile_size, camera_x, camera_y)
        bullets.append(bullet)
        
        # Update weapon state
        weapon.current_clip -= 1
        weapon.last_shot_time = now
        
        # Automatic reload if clip is empty and reserve ammo (or infinite)
        if weapon.current_clip == 0 and (player.has_infinite_ammo(weapon) or (weapon.common.ammo is None or weapon.common.ammo > 0)):
            player.reload_weapon(weapon_index)
    
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
    base_dx, base_dy = player.aim_direction
    # Favor pierce over bounce if both are set
    piercing = weapon.uncommon.piercing if weapon.uncommon.piercing else 0
    bounce_limit = weapon.uncommon.bounce_limit if weapon.uncommon.bounce_limit else 0
    if piercing > 0 and bounce_limit > 0:
        bounce_limit = 0  # Ignore bounce if pierce is set
    
    # Apply spread for shotguns
    if weapon.common.fire_mode == FireMode.SHOTGUN and (weapon.uncommon.volley or 1) > 1:
        # Calculate spread angle for this pellet
        spread_angle = ((weapon.uncommon.spread or 0) / ((weapon.uncommon.volley or 1) - 1)) * pellet_index - ((weapon.uncommon.spread or 0) / 2)
        # Convert to radians and apply to base direction
        spread_rad = math.radians(spread_angle)
        cos_spread = math.cos(spread_rad)
        sin_spread = math.sin(spread_rad)
        dx = base_dx * cos_spread - base_dy * sin_spread
        dy = base_dx * sin_spread + base_dy * cos_spread
    else:
        # Regular accuracy spread for non-shotguns
        spread_angle = (random.uniform(-0.5, 0.5) * weapon.common.accuracy * 360)
        angle = math.atan2(base_dy, base_dx) + math.radians(spread_angle)
        dx = math.cos(angle)
        dy = math.sin(angle)
    
    bullet_speed = weapon.common.bullet_speed
    bullet_range = weapon.common.range * tile_size
    bullet_size = int(weapon.common.bullet_size * tile_size)
    
    bullet = {
        'x': player.rect.centerx,
        'y': player.rect.centery,
        'dx': dx,
        'dy': dy,
        'speed': bullet_speed,
        'range': bullet_range,
        'distance': 0,
        'size': bullet_size,
        'damage': weapon.common.damage,
        'color': weapon.common.bullet_color,
        'splash': weapon.uncommon.splash,
        'weapon_index': weapon_index,
        'contact_effect': weapon.common.contact_effect,
        'bounces': 0,
        'bounce_limit': bounce_limit,
        'enemy_effects': weapon.common.enemy_effects,
        'pierces_left': piercing,
        'knockback_force': weapon.uncommon.knockback_force if hasattr(weapon.uncommon, 'knockback_force') else 0
    }
    
    # Add effect-specific properties
    if EnemyContactEffect.FIRE in weapon.common.enemy_effects:
        bullet['burn_damage'] = weapon.common.damage * 0.3  # 30% of base damage
    
    if weapon.common.fire_mode == FireMode.SPRAY:
        bullet['is_spray_particle'] = True

    if weapon.common.fire_mode == FireMode.ORBITAL:
        bullet['is_orbital'] = True
        bullet['z'] = weapon.uncommon.drop_height
        bullet['initial_z'] = weapon.uncommon.drop_height
        bullet['fall_speed'] = weapon.common.bullet_speed

        # Target point based on mouse, adjusted for camera and accuracy
        mouse_x, mouse_y = pygame.mouse.get_pos()
        target_x = mouse_x + camera_x
        target_y = mouse_y + camera_y
        
        # Apply accuracy as a random offset from the cursor
        offset_angle = random.uniform(0, 2 * math.pi)
        # Use a more reasonable accuracy radius (tile_size * accuracy * 10 for better scaling)
        offset_radius = tile_size * weapon.common.accuracy * 10 * random.random()
        target_x += math.cos(offset_angle) * offset_radius
        target_y += math.sin(offset_angle) * offset_radius

        # The bullet's (x,y) is the ground target
        bullet['x'] = target_x
        bullet['y'] = target_y
    elif weapon.common.fire_mode == FireMode.ORBITAL_BEAM:
        # Special properties for solar death beam
        bullet['is_orbital_beam'] = True
        bullet['beam_duration'] = weapon.unique.beam_duration or 5.0  # Use weapon's duration
        bullet['beam_start_time'] = pygame.time.get_ticks()
        bullet['beam_damage_tick'] = weapon.unique.beam_damage_tick or 0.2  # Use weapon's tick rate
        bullet['last_damage_time'] = pygame.time.get_ticks()
        bullet['beam_active'] = False  # Will activate after warm-up
        bullet['warm_up_start'] = pygame.time.get_ticks()
        bullet['warm_up_time'] = weapon.uncommon.warm_up_time  # Charge-up time
        bullet['mouse_follow'] = True  # Follow mouse cursor
        
        # Initial position based on mouse
        mouse_x, mouse_y = pygame.mouse.get_pos()
        bullet['x'] = mouse_x + camera_x
        bullet['y'] = mouse_y + camera_y
    elif weapon.common.fire_mode == FireMode.THROWN:
        # This logic is for thrown weapons with special physics (arcing, rolling)
        bullet['is_grenade'] = True # Keep this flag for movement logic
        bullet['detonation_time'] = weapon.uncommon.detonation_time
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
        max_throw_range = weapon.common.range * tile_size
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
    
    # Add homing-specific properties if present
    if hasattr(weapon.uncommon, 'homing_angle') and weapon.uncommon.homing_angle:
        bullet['homing_angle'] = weapon.uncommon.homing_angle
        bullet['homing_time'] = weapon.uncommon.homing_time or 0
        bullet['homing_timer'] = 0  # ms

    return bullet

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

def reset_warm_up(players):
    """
    Reset warm-up state for all weapons of all players.
    
    Args:
        players: List of Player objects
    """
    for player in players:
        for weapon in player.character.weapons:
            if weapon.uncommon.warm_up_time:
                weapon.is_warming_up = False
                weapon.warm_up_start = None

def update_bullets(bullets, creatures, walls, dt, camera_x=0, camera_y=0):
    bullets_to_remove = []
    splash_effects = []  # Initialize splash_effects list
    
    for bullet in bullets[:]:
        # --- MINE LOGIC ---
        if getattr(bullet, 'is_mine', False) or bullet.get('is_mine', False):
            # Mines do not move and do not disappear due to range
            # Check for proximity to any creature
            triggered = False
            trigger_radius = bullet.get('trigger_radius', 32)
            for creature in creatures:
                if creature.hp > 0:
                    dist = math.hypot(bullet['x'] - creature.rect.centerx, bullet['y'] - creature.rect.centery)
                    if dist <= trigger_radius:
                        # Explode: deal splash damage to all creatures in splash radius
                        splash_radius = (bullet.get('splash', 2.0) * 32)  # Default 2 tiles
                        for c in creatures:
                            if c.hp > 0:
                                cdist = math.hypot(bullet['x'] - c.rect.centerx, bullet['y'] - c.rect.centery)
                                if cdist <= splash_radius:
                                    c.hp -= bullet['damage']
                        bullets_to_remove.append(bullet)
                        triggered = True
                        break
            if triggered:
                continue  # Skip further processing for this bullet
            # Draw mine (optional: add visual effect here)
            continue  # Skip normal bullet logic for mines
            
        if bullet.get('type') == 'beam':
            # Store previous position for robust collision detection
            prev_x, prev_y = bullet['x'], bullet['y']

            # Handle beam projectiles
            dx = math.cos(bullet['angle']) * bullet['speed']
            dy = math.sin(bullet['angle']) * bullet['speed']
            
            bullet['x'] += dx
            bullet['y'] += dy
            
            # Add current position to trail
            bullet['trail_points'].append((bullet['x'], bullet['y']))
            
            # Limit trail length to prevent memory issues
            if len(bullet['trail_points']) > 20:
                bullet['trail_points'].pop(0)
            
            # Check for wall collisions
            bullet_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], 
                                    bullet['size'] * 2, bullet['size'] * 2)
            
            wall_collision = False
            for wall in walls:
                if bullet_rect.colliderect(wall):
                    wall_collision = True
                    break
            
            if wall_collision:
                bullets_to_remove.append(bullet)
                continue
            
            # Check for creature collisions using clipline to prevent tunneling
            for creature in creatures:
                if creature.id not in bullet['hits'] and creature.rect.clipline((prev_x, prev_y), (bullet['x'], bullet['y'])):
                    bullet['hits'].add(creature.id)
                    # Apply all effects for beam weapons
                    apply_creature_effects(bullet, creature)
                    
                    # Beams don't get destroyed by creature hits due to high pierce
                    if len(bullet['hits']) >= bullet['piercing']:
                        bullets_to_remove.append(bullet)
                        break
            
            # Check if beam has traveled its maximum range
            start_x, start_y = bullet['trail_points'][0]
            distance_traveled = math.sqrt((bullet['x'] - start_x)**2 + (bullet['y'] - start_y)**2)
            if distance_traveled > bullet['range']:
                bullets_to_remove.append(bullet)
                
        elif bullet.get('is_orbital'):
            # Handle orbital missiles
            bullet['z'] -= bullet['fall_speed']
            if bullet['z'] <= 0:
                # Landed, now explode
                if bullet.get('splash'):
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                bullets_to_remove.append(bullet)
                continue
            # Skip all other physics for orbital projectiles
            continue
            
        elif bullet.get('is_orbital_beam'):
            # Handle solar death beam mechanics
            current_time = pygame.time.get_ticks()
            warm_up_elapsed = (current_time - bullet['warm_up_start']) / 1000.0
            warm_up_time = bullet.get('warm_up_time', 2.0)
            
            if not bullet.get('beam_active', False) and warm_up_elapsed >= warm_up_time:
                # Warm-up complete, activate beam
                bullet['beam_active'] = True
                bullet['beam_start_time'] = current_time
                bullet['last_damage_time'] = current_time  # Start dealing damage immediately
            
            if bullet.get('beam_active', False):
                # Update mouse position for beam following
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bullet['x'] = mouse_x + camera_x
                bullet['y'] = mouse_y + camera_y
                
                # Check if beam duration has expired
                beam_elapsed = (current_time - bullet['beam_start_time']) / 1000.0
                if beam_elapsed >= bullet['beam_duration']:
                    # Beam expired, remove it
                    bullets_to_remove.append(bullet)
                    continue
                
                # Apply continuous damage to creatures in beam area
                damage_elapsed = (current_time - bullet['last_damage_time']) / 1000.0
                if damage_elapsed >= bullet['beam_damage_tick']:
                    # Deal damage to creatures in beam area
                    beam_radius = bullet.get('splash', 2.0) * 32
                    for creature in creatures:
                        distance = math.sqrt((creature.rect.centerx - bullet['x'])**2 + 
                                           (creature.rect.centery - bullet['y'])**2)
                        if distance <= beam_radius:
                            # Apply all effects for orbital beam
                            apply_creature_effects(bullet, creature)
                    bullet['last_damage_time'] = current_time
            
            # Don't remove the beam - let it continue until duration expires
            continue
            
        elif bullet.get('is_grenade'):
            now = pygame.time.get_ticks()
            # Detonate after timer
            if now - bullet['creation_time'] >= bullet['detonation_time'] * 1000:
                if bullet.get('splash'):
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                bullets_to_remove.append(bullet)
                continue
            # Handle movement (arc, then roll)
            if bullet['phase'] == 'flying':
                bullet['x'] += bullet['velocity_x']
                bullet['y'] += bullet['velocity_y']
                bullet['distance_traveled'] += math.hypot(bullet['velocity_x'], bullet['velocity_y'])
                # Wall bounce logic for flying phase
                grenade_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], bullet['size']*2, bullet['size']*2)
                for wall in walls:
                    if grenade_rect.colliderect(wall):
                        # Simple bounce: reverse velocity and dampen
                        if abs(wall.left - grenade_rect.right) < 5 or abs(wall.right - grenade_rect.left) < 5:
                            bullet['velocity_x'] *= -0.7
                        if abs(wall.top - grenade_rect.bottom) < 5 or abs(wall.bottom - grenade_rect.top) < 5:
                            bullet['velocity_y'] *= -0.7
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
                # Wall bounce logic for rolling phase
                grenade_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], bullet['size']*2, bullet['size']*2)
                for wall in walls:
                    if grenade_rect.colliderect(wall):
                        if abs(wall.left - grenade_rect.right) < 5 or abs(wall.right - grenade_rect.left) < 5:
                            bullet['velocity_x'] *= -0.7
                        if abs(wall.top - grenade_rect.bottom) < 5 or abs(wall.bottom - grenade_rect.top) < 5:
                            bullet['velocity_y'] *= -0.7
                bullet['roll_left'] -= math.hypot(bullet['velocity_x'], bullet['velocity_y'])
                bullet['velocity_x'] *= 0.92
                bullet['velocity_y'] *= 0.92
                if bullet['roll_left'] <= 0 or (abs(bullet['velocity_x']) < 0.2 and abs(bullet['velocity_y']) < 0.2):
                    bullet['velocity_x'] = 0
                    bullet['velocity_y'] = 0
                    bullet['phase'] = 'stopped'
            # No wall/creature collision for grenades (they only explode on timer)
            continue
            
        else:
            # Handle regular bullets (existing logic)
            # Homing logic
            if bullet.get('homing_angle') and bullet.get('homing_time', 0) > 0 and dt > 0:
                bullet['homing_timer'] = bullet.get('homing_timer', 0) + int(dt * 1000)
                if bullet['homing_timer'] < bullet['homing_time'] * 1000:
                    # Find nearest living creature
                    nearest = None
                    nearest_dist = float('inf')
                    for creature in creatures:
                        if creature.hp > 0:
                            dist = math.hypot(creature.rect.centerx - bullet['x'], creature.rect.centery - bullet['y'])
                            if dist < nearest_dist:
                                nearest = creature
                                nearest_dist = dist
                    if nearest:
                        # Calculate angle to target
                        dx = nearest.rect.centerx - bullet['x']
                        dy = nearest.rect.centery - bullet['y']
                        target_angle = math.atan2(dy, dx)
                        current_angle = math.atan2(bullet['dy'], bullet['dx'])
                        # Find smallest angle difference
                        diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                        max_turn = math.radians(bullet['homing_angle'])
                        # Clamp the turn
                        if abs(diff) < max_turn:
                            new_angle = target_angle
                        else:
                            new_angle = current_angle + max_turn * (1 if diff > 0 else -1)
                        bullet['dx'] = math.cos(new_angle)
                        bullet['dy'] = math.sin(new_angle)
            
            # Store previous position for distance calculation
            old_x = bullet['x']
            old_y = bullet['y']
            
            # Update position
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']
            
            # Calculate actual distance moved this frame
            actual_distance = math.hypot(bullet['x'] - old_x, bullet['y'] - old_y)
            bullet['distance'] += actual_distance
            
            # Check if bullet has exceeded its range
            if bullet['distance'] > bullet['range']:
                bullets_to_remove.append(bullet)
                continue
            
            # Create bullet rectangle for collision detection
            bullet_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], 
                                    bullet['size'] * 2, bullet['size'] * 2)
            
            # --- Wall Collision with continuous detection ---
            hit_wall = False
            for wall in walls:
                # Check both current position and the path to it
                if bullet_rect.colliderect(wall) or wall.clipline((old_x, old_y), (bullet['x'], bullet['y'])):
                    hit_wall = True
                    break
            
            if hit_wall:
                if bullet['contact_effect'] == ContactEffect.EXPLODE:
                    # Handle explosive bullets
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                    bullets_to_remove.append(bullet)
                elif bullet.get('bounce_limit', 0) > 0:
                    # Handle bouncing bullets
                    bullet['bounce_limit'] -= 1
                    
                    # Move bullet back to previous position before bounce
                    bullet['x'] = old_x
                    bullet['y'] = old_y
                    
                    # --- Determine bounce direction ---
                    bullet_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], bullet['size']*2, bullet['size']*2)
                    hit_wall_rect = None
                    for w in walls:
                        if bullet_rect.colliderect(w) or w.clipline((old_x, old_y), (bullet['x'], bullet['y'])):
                            hit_wall_rect = w
                            break
                    
                    if hit_wall_rect:
                        # Check for horizontal vs. vertical collision
                        bullet_rect.x -= bullet['dx'] * bullet['speed']
                        if bullet_rect.colliderect(hit_wall_rect):
                            bullet['dy'] *= -1 # Vertical bounce
                        else:
                            bullet['dx'] *= -1 # Horizontal bounce
                        
                        # Apply damage on bounce if applicable
                        if bullet['contact_effect'] == ContactEffect.DAMAGE_BOUNCE:
                            bullet['damage'] = bullet['damage'] * 1.1 # Increase damage by 10% on bounce
                    else:
                        # Default bounce if wall rect not found (should not happen)
                        bullet['dx'] *= -1
                        bullet['dy'] *= -1
                else:
                    bullets_to_remove.append(bullet)
                continue
            
            # --- Creature Collision with continuous detection ---
            contact_effect = bullet['contact_effect']
            collided_creature = None
            
            for creature in creatures:
                if creature.hp > 0 and (bullet_rect.colliderect(creature.rect) or 
                                      creature.rect.clipline((old_x, old_y), (bullet['x'], bullet['y']))):
                    collided_creature = creature
                    break
            
            if collided_creature:
                # Apply all creature effects modularly
                apply_creature_effects(bullet, collided_creature)
                # --- Handle bullet effects ---
                if bullet['contact_effect'] in [ContactEffect.DAMAGE_BOUNCE, ContactEffect.NO_DAMAGE_BOUNCE]:
                    if bullet.get('bounce_limit', 0) > 0:
                        bullet['bounce_limit'] -= 1
                        if bullet['contact_effect'] == ContactEffect.DAMAGE_BOUNCE:
                            bullet['damage'] *= 1.1
                        bullet['dx'] *= -1
                        bullet['dy'] *= -1
                    else:
                        bullets_to_remove.append(bullet)
                elif bullet['contact_effect'] == ContactEffect.PIERCE:
                    if 'hit_creatures' not in bullet:
                        bullet['hit_creatures'] = set()
                    bullet['hit_creatures'].add(id(collided_creature))
                    bullet['pierces_left'] -= 1
                    if bullet['pierces_left'] < 0:
                        bullets_to_remove.append(bullet)
                elif bullet['contact_effect'] == ContactEffect.EXPLODE:
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                    bullets_to_remove.append(bullet)
                else:
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

def apply_creature_effects(bullet, creature):
    """Apply all enemy effects from a bullet to a creature."""
    # Always apply direct damage first
    creature.hp -= bullet['damage']
    
    # Apply each enemy effect
    for effect in bullet['enemy_effects']:
        if effect == EnemyContactEffect.PHYSICAL:
            continue  # Physical damage already applied
            
        elif effect == EnemyContactEffect.FIRE:
            # Initialize burning_effects as a dict
            if not hasattr(creature, 'burning_effects') or creature.burning_effects is None:
                creature.burning_effects = {}
            # Add or refresh burning effect
            creature.burning_effects[id(creature)] = {
                'damage': bullet.get('burn_damage', bullet['damage'] * 0.3),  # 30% of base damage as burn
                'duration': 3.0,
                'tick_rate': 0.5,
                'start_time': pygame.time.get_ticks(),
                'last_tick': pygame.time.get_ticks()
            }
            
        elif effect == EnemyContactEffect.ICE:
            if hasattr(creature, 'apply_slow'):
                creature.apply_slow(duration=3000, factor=0.5)
                
        elif effect == EnemyContactEffect.POISON:
            apply_poison(creature, bullet['damage'])
            
        elif effect == EnemyContactEffect.KNOCKBACK:
            # Skip knockback for beam weapons
            if bullet.get('type') == 'beam':
                continue

            # Initialize knockback attributes if they don't exist
            if not hasattr(creature, 'knockback_dx'):
                creature.knockback_dx = 0
                creature.knockback_dy = 0
                creature.knockback_resistance = getattr(creature, 'knockback_resistance', 1.0)

            knockback_force = bullet.get('knockback_force', 10)  # Default force if not specified
            
            if bullet.get('is_orbital_beam') or bullet.get('contact_effect') == ContactEffect.EXPLODE:
                # Knockback from center point for explosions and orbital beams
                dx = creature.rect.centerx - bullet['x']
                dy = creature.rect.centery - bullet['y']
            else:
                # Knockback in bullet's direction for regular bullets
                dx = bullet['dx']
                dy = bullet['dy']
            
            # Normalize direction vector
            length = math.sqrt(dx * dx + dy * dy)
            if length > 0:
                dx = dx / length
                dy = dy / length
                
                # Apply knockback force (reduced by creature's knockback resistance)
                creature.knockback_dx = dx * knockback_force * (1 - creature.knockback_resistance)
                creature.knockback_dy = dy * knockback_force * (1 - creature.knockback_resistance) 