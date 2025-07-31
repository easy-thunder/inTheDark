
import pygame
import math
"""Has two helper functions below for the drawing of the darkness overlay"""

_light_cache = {}
def draw_darkness_overlay(screen, darkness_alpha, lights=[]):
    """
    Draws a darkness overlay and subtracts radial or simple cone lights.
    """
    if darkness_alpha <= 0:
        return

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, darkness_alpha))

    for light in lights:
        if light['type'] == 'radial':
            x, y, radius = light['x'], light['y'], light['radius']
            key = (radius, darkness_alpha)
            if key not in _light_cache:
                _light_cache[key] = create_radial_light_surface(radius, darkness_alpha)
            light_surf = _light_cache[key]
            overlay.blit(light_surf, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_SUB)

        elif light['type'] == 'cone':
            draw_flashlight_cone(
                overlay,
                x=light['x'],
                y=light['y'],
                angle_deg=light['angle'],
                length=light['radius'],
                spread_deg=light.get('spread', 45),
                darkness_alpha=darkness_alpha
            )

    screen.blit(overlay, (0, 0))

    
def create_radial_light_surface(radius, darkness_alpha):
    """
    Creates a radial gradient light surface once and reuses it.
    Alpha fades from 0 (transparent) at center to darkness_alpha at edge (opaque).
    """
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    center = radius

    for r in range(radius, 0, -1):
        alpha = int(darkness_alpha * (1 - (r / radius)))
        pygame.draw.circle(surface, (0, 0, 0, alpha), (center, center), r)

    return surface

def draw_flashlight_cone(screen, x, y, angle_deg, length, spread_deg, darkness_alpha):
    """
    Draws a simple cone-shaped flashlight overlay.
    - (x, y): Origin of flashlight in screen coordinates
    - angle_deg: Flashlight direction
    - length: Distance of beam
    - spread_deg: Beam width
    """
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 0))

    angle_rad = math.radians(angle_deg)
    half_spread = math.radians(spread_deg / 2)

    dx1 = math.cos(angle_rad - half_spread) * length
    dy1 = math.sin(angle_rad - half_spread) * length
    dx2 = math.cos(angle_rad + half_spread) * length
    dy2 = math.sin(angle_rad + half_spread) * length

    points = [
        (x, y),
        (x + dx1, y + dy1),
        (x + dx2, y + dy2),
    ]

    pygame.draw.polygon(overlay, (0, 0, 0, darkness_alpha), points)
    screen.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)


