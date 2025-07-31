import pygame
import math


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
