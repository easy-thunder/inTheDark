import pygame
import math
import os


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