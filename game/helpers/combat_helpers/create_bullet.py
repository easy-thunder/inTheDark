import pygame
import math
import random


from game.weapons import FireMode, EnemyContactEffect

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
