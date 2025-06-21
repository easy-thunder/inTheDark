import pygame
import os
import math

def draw_world(screen, world, camera_x, camera_y, game_x, game_y, tile_size, border_color, menu_color, black):
    """Draw the world tiles and walls."""
    screen.fill(border_color)
    pygame.draw.rect(screen, menu_color, (0, 0, screen.get_width(), 100))  # Top menu area
    pygame.draw.rect(screen, black, (game_x, game_y, screen.get_width() - 2 * game_x, screen.get_height() - game_y - 50))
    
    buffer = 6
    start_col = (camera_x // tile_size) - buffer
    end_col = ((camera_x + screen.get_width()) // tile_size) + buffer
    start_row = (camera_y // tile_size) - buffer
    end_row = ((camera_y + screen.get_height()) // tile_size) + buffer
    
    visible_walls = []
    for row in range(start_row, end_row):
        for col in range(start_col, end_col):
            tile_type = world.get_tile(col, row)
            rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
            if tile_type == 'W':
                visible_walls.append(rect)
            else:
                draw_rect = rect.move(-camera_x + game_x, -camera_y + game_y)
                pygame.draw.rect(screen, (128, 128, 128), draw_rect)
    
    return visible_walls

def draw_creatures(screen, creatures, camera_x, camera_y, game_x, game_y, show_creature_hp):
    """Draw all creatures and their HP bars."""
    for creature in creatures:
        creature.draw(screen, camera_x, camera_y, game_x, game_y)
        # Draw HP bar if enabled
        if show_creature_hp:
            bar_width = creature.width
            bar_height = 3
            bar_x = int(creature.rect.x - camera_x + game_x)
            bar_y = int(creature.rect.y - camera_y + game_y) - 8
            # Background
            pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
            # Filled
            if creature.hp > 0:
                fill_width = int(bar_width * (creature.hp / max(1, getattr(creature, 'max_hp', creature.hp))))
                pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))

def draw_bullets(screen, bullets, camera_x, camera_y, game_x, game_y):
    """Draw all active bullets."""
    for bullet in bullets:
        bx = int(bullet['x'] - camera_x + game_x)
        by = int(bullet['y'] - camera_y + game_y)
        pygame.draw.circle(screen, bullet['color'], (bx, by), bullet['size'])

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

def draw_stats_ui(screen, players, player_start_pos, current_max_distance, start_ticks, stats, tile_size, border_size, top_menu_height, white):
    """Draw the stats UI in the top menu."""
    current_distance = math.sqrt((players[0].x - player_start_pos[0])**2 + (players[0].y - player_start_pos[1])**2)
    if current_distance > current_max_distance:
        current_max_distance = current_distance
    
    current_game_time_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
    
    try:
        font_size = int(top_menu_height * 0.25)
        font = pygame.font.Font(os.path.join('assets', 'fonts', 'Creepster-Regular.ttf'), font_size)
    except FileNotFoundError:
        font = pygame.font.Font(None, int(top_menu_height * 0.25))
    
    def format_time(seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
    
    cd_text = f"CD: {int(current_distance / tile_size)}"
    ct_text = f"CT: {format_time(current_game_time_seconds)}"
    rd_text = f"RD: {int(stats.record_distance / tile_size)}"
    rt_text = f"RT: {format_time(stats.record_time)}"
    
    screen.blit(font.render(f"{cd_text}   {ct_text}", True, white), (border_size + 10, border_size + 2))
    screen.blit(font.render(f"{rd_text}   {rt_text}", True, white), (border_size + 10, border_size + 2 + font_size + 2))
    
    return current_distance

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

def draw_game_over(screen, screen_width, screen_height):
    """Draw the game over screen."""
    font = pygame.font.Font(None, 72)
    text = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000) 