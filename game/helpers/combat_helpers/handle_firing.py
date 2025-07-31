import pygame
import math
import random

from game.weapons import FireMode
from game.helpers.combat_helpers.create_bullet import create_bullet
from game.helpers.combat_helpers.create_beam import create_beam


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