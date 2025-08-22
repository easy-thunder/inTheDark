import pygame
import sys
import copy
import random
import math
from game.world import World, get_day_phase
from game.stats.stats import GameStats
from game.characters import TESTY
from game.creatures import create_zombie_cat, create_tough_zombie_cat, create_thorny_venom_thistle, CREATURE_DIFFICULTY_POOLS
from game.combat import handle_firing, reset_warm_up, update_bullets, update_burning_creatures, update_poison_effects
from game.player import Player
from game.ui import draw_world, draw_creatures, draw_bullets, draw_splash_effects, draw_stats_ui, draw_xp_bar, draw_game_over, draw_darkness_overlay
from game.input_handler import handle_events, get_player_movement, is_fire_pressed
from game.game_logic import update_players, handle_revival, apply_tether_mechanic, update_camera, cleanup_dead_creatures
from game.helpers.ui_helpers.pause import pause_loop, shift_time_references
pygame.init()


info = pygame.display.Info()
DISPLAY_WIDTH = info.current_w
DISPLAY_HEIGHT = info.current_h


SCREEN_WIDTH = int(DISPLAY_WIDTH * 0.9)
SCREEN_HEIGHT = int(DISPLAY_HEIGHT * 0.9)


BORDER_SIZE = int(min(SCREEN_WIDTH, SCREEN_HEIGHT) * 0.02)  
TOP_MENU_HEIGHT = int(SCREEN_HEIGHT * 0.12)  


GAME_X = BORDER_SIZE
GAME_Y = BORDER_SIZE + TOP_MENU_HEIGHT
GAME_WIDTH = SCREEN_WIDTH - 2 * BORDER_SIZE
GAME_HEIGHT = SCREEN_HEIGHT - 2 * BORDER_SIZE - TOP_MENU_HEIGHT


TILE_SIZE = int(min(GAME_WIDTH, GAME_HEIGHT) / 18)  
PLAYER_SIZE = TILE_SIZE


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BORDER_COLOR = (40, 40, 40)
MENU_COLOR = (20, 20, 20)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("In The Dark - Simple Pygame Starter")
clock = pygame.time.Clock()

def main():
    world = World(seed=123)
    stats = GameStats()
    player_start_pos = (TILE_SIZE, TILE_SIZE)
    players = [
        Player(player_start_pos[0], player_start_pos[1], copy.deepcopy(TESTY), TILE_SIZE),
    ]
    player_weapon_indices = [0, 0]
    player_ability_indices = [0, 0]
    caps_lock_on = [False]
    creatures = []
    
    spawn_timer = 0
    spawn_interval = 5000 
    min_spawn_distance = TILE_SIZE * 6 
    start_ticks = pygame.time.get_ticks()
    running = True
    camera_x, camera_y = 0, 0
    bullets = []
    show_creature_hp = False
    splash_effects = []
    current_max_distance = 0
   
    ability_active = [False]

    
    while running:
       
        running, show_creature_hp, player_weapon_indices, player_ability_indices, caps_lock_on, pause_requested = handle_events(
            players, player_weapon_indices, show_creature_hp, ability_active, player_ability_indices, caps_lock_on
        )
        if not running:
            break
        dx1, dy1, dx2, dy2 = get_player_movement(players)
       
        if ability_active[0]:
            bullets = handle_firing(players, player_ability_indices, bullets, 0, TILE_SIZE, camera_x, camera_y, ability_active, is_ability=True)
        elif is_fire_pressed():
            player = players[0]
            weapon = player.character.weapons[player_weapon_indices[0]]
            now = pygame.time.get_ticks()
            bullets = handle_firing(players, player_weapon_indices, bullets, 0, TILE_SIZE, camera_x, camera_y)
        else:
            reset_warm_up(players)
        
        camera_x, camera_y = update_camera(players, GAME_WIDTH, GAME_HEIGHT)
        
        dx1, dy1 = apply_tether_mechanic(players, camera_x, camera_y, dx1, dy1, GAME_WIDTH, PLAYER_SIZE)
        
        now = pygame.time.get_ticks()
        elapsed = now - start_ticks
        minutes = elapsed // 60000
        spawn_interval = max(300, 5000 // (2 ** minutes))  
        if now - spawn_timer > spawn_interval:
            
            px, py = players[0].rect.center
            for _ in range(100):  
                x = random.randint(TILE_SIZE * 2, TILE_SIZE * 15)
                y = random.randint(TILE_SIZE * 2, TILE_SIZE * 15)
                if math.hypot(x - px, y - py) >= min_spawn_distance:
                    
                    pool_index = 0 if minutes < 1 else 1
                    pool = CREATURE_DIFFICULTY_POOLS[3] # JAKE CHANGE THIS TO POOL_INDEX AFTER TESTING
                    creature_class, kwargs = random.choice(pool)
                    creatures.append(creature_class(x=x, y=y, **kwargs))
                    break
            spawn_timer = now

        clock.tick(60)
        current_game_time_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        day_phase, darkness_alpha = get_day_phase(current_game_time_seconds)
        visible_walls = draw_world(screen, world, camera_x, camera_y, GAME_X, GAME_Y, TILE_SIZE, BORDER_COLOR, MENU_COLOR, BLACK,  darkness_alpha)
        all_dead = update_players(players, dx1, dy1, dx2, dy2, visible_walls, camera_x, camera_y, player_weapon_indices, GAME_X, GAME_Y)
        handle_revival(players, clock)

        for creature in creatures:
            creature.update(1/60, visible_walls, players)
        draw_creatures(screen, creatures, camera_x, camera_y, GAME_X, GAME_Y, show_creature_hp)
        cleanup_dead_creatures(creatures, players)
        bullets, splash_effects = update_bullets(bullets, creatures, visible_walls, 1/60, camera_x, camera_y)
        update_burning_creatures(creatures)
        update_poison_effects(creatures)
        draw_splash_effects(screen, splash_effects, camera_x, camera_y, GAME_X, GAME_Y)
        draw_bullets(screen, bullets, camera_x, camera_y, GAME_X, GAME_Y)
        player_screen_x = players[0].rect.centerx - camera_x + GAME_X
        player_screen_y = players[0].rect.centery - camera_y + GAME_Y
        aim_dx, aim_dy = players[0].aim_direction # JAKE THIS WILL NEED TO BE CHANGED FOR MULTIPLAYER
        player_angle = math.degrees(math.atan2(aim_dy, aim_dx))

        lights = [
                # { 'type': 'radial', 'x': player_screen_x, 'y': player_screen_y, 'radius': 300, 'alpha': darkness_alpha }, # Example of a radial light
                { 'type': 'cone', 'x': player_screen_x, 'y': player_screen_y, 'radius': 300, 'angle': player_angle, 'spread': 45 } # Example of a cone light

        ]
        draw_darkness_overlay(screen, darkness_alpha, lights)
        for i, player in enumerate(players):
            player.draw(screen, camera_x, camera_y, player_index=i, current_weapon_index=player_weapon_indices[i], game_x=GAME_X, game_y=GAME_Y)
        if all_dead:
            draw_game_over(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
            break
        current_max_distance = draw_stats_ui(screen, players, player_start_pos, current_max_distance, start_ticks, stats, TILE_SIZE, BORDER_SIZE, TOP_MENU_HEIGHT, WHITE)
        draw_xp_bar(screen, players[0], SCREEN_WIDTH, SCREEN_HEIGHT, BORDER_SIZE)
        pygame.display.flip()
        if pause_requested:
            pause_started = pygame.time.get_ticks()
            result = pause_loop(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock, overlay_text="PAUSED")
            if result == "quit":
                running = False
                break
            paused_ms = pygame.time.get_ticks() - pause_started

            
            shift_time_references(players, creatures, bullets, paused_ms)

            
            start_ticks += paused_ms         
            spawn_timer += paused_ms         




    stats.save_records(current_game_time_seconds, current_max_distance)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()












