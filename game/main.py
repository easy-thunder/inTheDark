import pygame
import sys
import copy
from game.world import World
from game.stats.stats import GameStats
from game.characters import TESTY
from game.creatures import create_thorny_venom_thistle
from game.weapons import create_rusty_pistol, create_rocket_launcher, create_mini_gun, create_grenade
from game.combat import handle_firing, reset_warm_up, update_bullets, update_burning_creatures
from game.player import Player
from game.ui import draw_world, draw_creatures, draw_bullets, draw_splash_effects, draw_stats_ui, draw_xp_bar, draw_game_over
from game.input_handler import handle_events, get_player_movement, is_fire_pressed
from game.game_logic import update_players, handle_revival, apply_tether_mechanic, update_camera, cleanup_dead_creatures

# Initialize pygame
pygame.init()

# Get display info for dynamic sizing
info = pygame.display.Info()
DISPLAY_WIDTH = info.current_w
DISPLAY_HEIGHT = info.current_h

# Set screen size as a fraction of the display (for windowed mode)
SCREEN_WIDTH = int(DISPLAY_WIDTH * 0.9)
SCREEN_HEIGHT = int(DISPLAY_HEIGHT * 0.9)

# Borders
BORDER_SIZE = int(min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.02)  # 2% of min dimension
TOP_MENU_HEIGHT = int(SCREEN_HEIGHT * 0.12)  # 12% of screen height

# Game area (inside borders and menu)
GAME_X = BORDER_SIZE
GAME_Y = BORDER_SIZE + TOP_MENU_HEIGHT
GAME_WIDTH = SCREEN_WIDTH - 2 * BORDER_SIZE
GAME_HEIGHT = SCREEN_HEIGHT - 2 * BORDER_SIZE - TOP_MENU_HEIGHT

# Tile and player sizes relative to game area
TILE_SIZE = int(min(GAME_WIDTH, GAME_HEIGHT) / 18)  # 18 tiles fit in smaller dimension
PLAYER_SIZE = TILE_SIZE

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BORDER_COLOR = (40, 40, 40)
MENU_COLOR = (20, 20, 20)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("In The Dark - Simple Pygame Starter")
clock = pygame.time.Clock()

def main():
    world = World(seed=123)
    stats = GameStats()
    player_start_pos = (TILE_SIZE, TILE_SIZE)
    
    # Use default character 'testy'
    players = [
        Player(player_start_pos[0], player_start_pos[1], copy.deepcopy(TESTY), TILE_SIZE),
        Player(player_start_pos[0] + TILE_SIZE * 2, player_start_pos[1], copy.deepcopy(TESTY), TILE_SIZE)
    ]
    player_weapon_indices = [0, 0]  # [player1_weapon_index, player2_weapon_index]

    # --- Creature Management ---
    creatures = []
    # Spawn three thorny venom thistles in a line for testing piercing and explosive weapons
    thistle1 = create_thorny_venom_thistle(player_start_pos[0] + TILE_SIZE * 6, player_start_pos[1] + TILE_SIZE * 6, PLAYER_SIZE)
    thistle2 = create_thorny_venom_thistle(player_start_pos[0] + TILE_SIZE * 8, player_start_pos[1] + TILE_SIZE * 6, PLAYER_SIZE)
    thistle3 = create_thorny_venom_thistle(player_start_pos[0] + TILE_SIZE * 10, player_start_pos[1] + TILE_SIZE * 6, PLAYER_SIZE)
    creatures.extend([thistle1, thistle2, thistle3])
    
    current_max_distance = 0
    start_ticks = pygame.time.get_ticks()
    running = True
    camera_x, camera_y = 0, 0
    bullets = []
    show_creature_hp = False
    splash_effects = []
    
    while running:
        # --- Handle Events ---
        running, show_creature_hp, player_weapon_indices = handle_events(players, player_weapon_indices, show_creature_hp)
        if not running:
            break
        
        # --- Get Input ---
        dx1, dy1, dx2, dy2 = get_player_movement(players)
        
        # --- Handle Firing ---
        if is_fire_pressed():
            bullets = handle_firing(players, player_weapon_indices, bullets, 0, TILE_SIZE, camera_x, camera_y)
        else:
            reset_warm_up(players)
        
        # --- Update Camera ---
        camera_x, camera_y = update_camera(players, GAME_WIDTH, GAME_HEIGHT)
        
        # --- Apply Tether Mechanic ---
        dx1, dy1 = apply_tether_mechanic(players, camera_x, camera_y, dx1, dy1, GAME_WIDTH, PLAYER_SIZE)
        
        # --- Draw World ---
        visible_walls = draw_world(screen, world, camera_x, camera_y, GAME_X, GAME_Y, TILE_SIZE, BORDER_COLOR, MENU_COLOR, BLACK)
        
        # --- Update Players ---
        all_dead = update_players(players, dx1, dy1, dx2, dy2, visible_walls, camera_x, camera_y, player_weapon_indices, GAME_X, GAME_Y)
        
        # --- Handle Revival ---
        handle_revival(players, clock)
        
        # --- Draw Players ---
        for i, player in enumerate(players):
            player.draw(screen, camera_x, camera_y, player_index=i, current_weapon_index=player_weapon_indices[i], game_x=GAME_X, game_y=GAME_Y)

        # --- Update and Draw Creatures ---
        for creature in creatures:
            creature.update(players)
        draw_creatures(screen, creatures, camera_x, camera_y, GAME_X, GAME_Y, show_creature_hp)
        cleanup_dead_creatures(creatures)

        # --- Update Bullets and Handle Collisions ---
        bullets, splash_effects = update_bullets(bullets, visible_walls, creatures, splash_effects, players, TILE_SIZE, camera_x, camera_y)
        
        # --- Update Burning Effects ---
        update_burning_creatures(creatures)

        # --- Draw Effects ---
        draw_splash_effects(screen, splash_effects, camera_x, camera_y, GAME_X, GAME_Y)
        draw_bullets(screen, bullets, camera_x, camera_y, GAME_X, GAME_Y)

        # --- Game Over ---
        if all_dead:
            draw_game_over(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            break
        
        # --- Draw UI ---
        current_max_distance = draw_stats_ui(screen, players, player_start_pos, current_max_distance, start_ticks, stats, TILE_SIZE, BORDER_SIZE, TOP_MENU_HEIGHT, WHITE)
        draw_xp_bar(screen, players[0], SCREEN_WIDTH, SCREEN_HEIGHT, BORDER_SIZE)
        
        pygame.display.flip()
        clock.tick(60)
    
    # --- Save Records ---
    current_game_time_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
    stats.save_records(current_game_time_seconds, current_max_distance)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()












