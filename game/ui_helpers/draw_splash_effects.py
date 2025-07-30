import pygame


def draw_splash_effects(screen, splash_effects, camera_x, camera_y, game_x, game_y):
    """Draw splash effects from explosions."""
    now = pygame.time.get_ticks()
    for effect in splash_effects[:]:
        elapsed = now - effect['start']
        if elapsed > 200:
            splash_effects.remove(effect)
            continue
        alpha = max(0, 120 - int(120 * (elapsed / 200)))
        s = pygame.Surface((effect['radius']*2, effect['radius']*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (80, 255, 80, alpha), (int(effect['radius']), int(effect['radius'])), int(effect['radius']))
        bx = int(effect['x'] - camera_x + game_x - effect['radius'])
        by = int(effect['y'] - camera_y + game_y - effect['radius'])
        screen.blit(s, (bx, by))