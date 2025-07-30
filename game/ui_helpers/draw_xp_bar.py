
import pygame
import math
import os

def draw_xp_bar(screen, player, screen_width, screen_height, border_size):
    """Draw the XP bar at the bottom of the screen."""
    xp_bar_width = screen_width - 2 * border_size
    xp_bar_height = max(2, int(screen_height * 0.008))
    xp_bar_x = border_size
    xp_bar_y = screen_height - border_size - xp_bar_height
    
    pygame.draw.rect(screen, (40, 40, 40), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), border_radius=2)
    xp_fill_width = int(xp_bar_width * (player.xp / player.xp_to_next))
    pygame.draw.rect(screen, (0, 255, 180), (xp_bar_x, xp_bar_y, xp_fill_width, xp_bar_height), border_radius=2)
    
    xp_font = pygame.font.Font(os.path.join('assets', 'fonts', 'Creepster-Regular.ttf'), max(10, xp_bar_height*2)) if os.path.exists(os.path.join('assets', 'fonts', 'Creepster-Regular.ttf')) else pygame.font.Font(None, max(10, xp_bar_height*2))
    xp_text = f"LVL {player.level}  XP: {player.xp}/{player.xp_to_next}"
    xp_text_surface = xp_font.render(xp_text, True, (0, 255, 180))
    screen.blit(xp_text_surface, (xp_bar_x + 4, xp_bar_y - xp_text_surface.get_height() - 2))