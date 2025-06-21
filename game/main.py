import pygame
import sys
import os
import math
import random
import copy
from game.world import World
from game.stats.stats import GameStats
from game.characters import TESTY
from game.creatures import create_zombie_cat
from game.weapons import create_rusty_pistol, create_rocket_launcher, create_mini_gun
from game.combat import handle_firing, reset_warm_up, update_bullets
from game.player import Player

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
    # Individual weapon indices for each player
    player_weapon_indices = [0, 0]  # [player1_weapon_index, player2_weapon_index]

    # --- Creature Management ---
    creatures = []
    # Spawn our first zombie cat
    zombie = create_zombie_cat(player_start_pos[0] + TILE_SIZE * 6, player_start_pos[1] + TILE_SIZE * 6, PLAYER_SIZE)
    creatures.append(zombie)
    
    current_max_distance = 0
    start_ticks = pygame.time.get_ticks()
    running = True
    camera_x, camera_y = 0, 0
    game_over = False
    bullets = []  # List of active bullets
    show_creature_hp = False
    splash_effects = []  # List of (x, y, radius, start_time)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                # --- Weapon switching ---
                if event.key == pygame.K_1:
                    if len(players[0].character.weapons) > 0:
                        player_weapon_indices[0] = 0
                if event.key == pygame.K_2:
                    if len(players[0].character.weapons) > 1:
                        player_weapon_indices[0] = 1
                if event.key == pygame.K_3:
                    if len(players[0].character.weapons) > 2:
                        player_weapon_indices[0] = 2
                # --- Toggle creature HP bars ---
                if event.key == pygame.K_h:
                    show_creature_hp = not show_creature_hp
                # --- Reloading ---
                if event.key == pygame.K_r:
                    for player in players:
                        player.reload_weapon(player_weapon_indices[players.index(player)])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    # No firing logic here - handled in main loop
                    pass
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click released
                    # Reset warm-up when fire button is released
                    for player in players:
                        for weapon in player.character.weapons:
                            if weapon.warm_up_time:
                                weapon.is_warming_up = False
                                weapon.warm_up_start = None
        keys = pygame.key.get_pressed()
        # --- Input for Player 1 (WASD) ---
        move_x1 = (keys[pygame.K_d]) - (keys[pygame.K_a])
        move_y1 = (keys[pygame.K_s]) - (keys[pygame.K_w])
        dx1 = move_x1 * players[0].speed
        dy1 = move_y1 * players[0].speed
        # --- Input for Player 2 (Arrow keys) ---
        dx2 = dy2 = 0
        if len(players) > 1:
            move_x2 = (keys[pygame.K_RIGHT]) - (keys[pygame.K_LEFT])
            move_y2 = (keys[pygame.K_DOWN]) - (keys[pygame.K_UP])
            dx2 = move_x2 * players[1].speed
            dy2 = move_y2 * players[1].speed
        
        # --- Unified automatic firing system (Player 1) ---
        # Check if any fire button is pressed
        fire_pressed = keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]
        
        if fire_pressed:
            bullets = handle_firing(players, player_weapon_indices, bullets, 0, TILE_SIZE)
        else:
            # Reset warm-up when no fire button is pressed
            reset_warm_up(players)
        
        # --- Camera follows player 1 ---
        camera_x = players[0].x - GAME_WIDTH // 2
        camera_y = players[0].y - GAME_HEIGHT // 2

        # --- Tether mechanic: restrict Player 1 if Player 2 is at the opposite edge ---
        if len(players) > 1:
            p2_screen_x = players[1].x - camera_x
            p2_screen_y = players[1].y - camera_y
            # If Player 2 is at the left edge and Player 1 tries to move right, block
            if p2_screen_x <= 0 and dx1 > 0:
                dx1 = 0
            # If Player 2 is at the right edge and Player 1 tries to move left, block
            if p2_screen_x >= GAME_WIDTH - PLAYER_SIZE and dx1 < 0:
                dx1 = 0
            # If Player 2 is at the top edge and Player 1 tries to move down, block
            if p2_screen_y <= 0 and dy1 > 0:
                dy1 = 0
            # If Player 2 is at the bottom edge and Player 1 tries to move up, block
            if p2_screen_y >= GAME_HEIGHT - PLAYER_SIZE and dy1 < 0:
                dy1 = 0
        # --- Drawing ---
        screen.fill(BORDER_COLOR)
        pygame.draw.rect(screen, MENU_COLOR, (BORDER_SIZE, BORDER_SIZE, SCREEN_WIDTH - 2 * BORDER_SIZE, TOP_MENU_HEIGHT))
        pygame.draw.rect(screen, BLACK, (GAME_X, GAME_Y, GAME_WIDTH, GAME_HEIGHT))
        buffer = 6
        start_col = (camera_x // TILE_SIZE) - buffer
        end_col = ((camera_x + GAME_WIDTH) // TILE_SIZE) + buffer
        start_row = (camera_y // TILE_SIZE) - buffer
        end_row = ((camera_y + GAME_HEIGHT) // TILE_SIZE) + buffer
        visible_walls = []
        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                tile_type = world.get_tile(col, row)
                rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if tile_type == 'W':
                    visible_walls.append(rect)
                else:
                    draw_rect = rect.move(-camera_x + GAME_X, -camera_y + GAME_Y)
                    pygame.draw.rect(screen, GRAY, draw_rect)
        # --- Update and draw all players ---
        all_dead = True
        for i, player in enumerate(players):
            if not player.dead:
                all_dead = False
            if i == 0:
                player.move(dx1, dy1, visible_walls)
            elif i == 1:
                player.move(dx2, dy2, visible_walls)
            player.update_xp()
            player.regen()
            player.update_aim(camera_x, camera_y, player_index=i, game_x=GAME_X, game_y=GAME_Y)
            player.update_reload(player_weapon_indices[i])
        # --- Revival mechanic ---
        for i, player in enumerate(players):
            if player.dead:
                # Check if any living player is standing over this dead player
                for j, other in enumerate(players):
                    if not other.dead and other.rect.colliderect(player.rect):
                        player.revive_progress += clock.get_time() / 1000.0
                        if player.revive_progress >= player.character.revival_time:
                            player.try_revive()
                        break
                else:
                    player.revive_progress = 0
            player.draw(screen, camera_x, camera_y, player_index=i, current_weapon_index=player_weapon_indices[i], game_x=GAME_X, game_y=GAME_Y)

        # --- Update and draw all creatures ---
        for creature in creatures:
            creature.update(players)
            creature.draw(screen, camera_x, camera_y, GAME_X, GAME_Y)
            # Draw HP bar if enabled
            if show_creature_hp:
                bar_width = creature.width
                bar_height = 3
                bar_x = int(creature.rect.x - camera_x + GAME_X)
                bar_y = int(creature.rect.y - camera_y + GAME_Y) - 8
                # Background
                pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
                # Filled
                if creature.hp > 0:
                    fill_width = int(bar_width * (creature.hp / max(1, getattr(creature, 'max_hp', creature.hp))))
                    pygame.draw.rect(screen, (0, 255, 0), (bar_x, bar_y, fill_width, bar_height))
        # Remove dead creatures
        creatures[:] = [c for c in creatures if c.hp > 0]

        # --- Update bullets and handle collisions ---
        bullets, splash_effects = update_bullets(bullets, visible_walls, creatures, splash_effects, players, TILE_SIZE)

        # --- Draw splash effects ---
        now = pygame.time.get_ticks()
        for effect in splash_effects[:]:
            elapsed = now - effect['start']
            if elapsed > 200:
                splash_effects.remove(effect)
                continue
            alpha = max(0, 120 - int(120 * (elapsed / 200)))
            s = pygame.Surface((effect['radius']*2, effect['radius']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (80, 255, 80, alpha), (int(effect['radius']), int(effect['radius'])), int(effect['radius']))
            bx = int(effect['x'] - camera_x + GAME_X - effect['radius'])
            by = int(effect['y'] - camera_y + GAME_Y - effect['radius'])
            screen.blit(s, (bx, by))

        # --- Game Over ---
        if all_dead:
            game_over = True
            font = pygame.font.Font(None, 72)
            text = font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            pygame.display.flip()
            pygame.time.wait(3000)
            break
        
        # --- Stats/UI for player 1 ---
        current_distance = math.sqrt((players[0].x - player_start_pos[0])**2 + (players[0].y - player_start_pos[1])**2)
        if current_distance > current_max_distance:
            current_max_distance = current_distance
        current_game_time_seconds = (pygame.time.get_ticks() - start_ticks) / 1000
        try:
            font_size = int(TOP_MENU_HEIGHT * 0.25)
            font = pygame.font.Font(os.path.join('assets', 'fonts', 'Creepster-Regular.ttf'), font_size)
        except FileNotFoundError:
            font = pygame.font.Font(None, int(TOP_MENU_HEIGHT * 0.25))
        def format_time(seconds):
            mins = int(seconds // 60)
            secs = int(seconds % 60)
            return f"{mins}:{secs:02d}"
        cd_text = f"CD: {int(current_max_distance / TILE_SIZE)}"
        ct_text = f"CT: {format_time(current_game_time_seconds)}"
        rd_text = f"RD: {int(stats.record_distance / TILE_SIZE)}"
        rt_text = f"RT: {format_time(stats.record_time)}"
        screen.blit(font.render(f"{cd_text}   {ct_text}", True, WHITE), (BORDER_SIZE + 10, BORDER_SIZE + 2))
        screen.blit(font.render(f"{rd_text}   {rt_text}", True, WHITE), (BORDER_SIZE + 10, BORDER_SIZE + 2 + font_size + 2))
        # --- XP Bar for player 1 ---
        p1 = players[0]
        xp_bar_width = SCREEN_WIDTH - 2 * BORDER_SIZE
        xp_bar_height = max(2, int(SCREEN_HEIGHT * 0.008))
        xp_bar_x = BORDER_SIZE
        xp_bar_y = SCREEN_HEIGHT - BORDER_SIZE - xp_bar_height
        pygame.draw.rect(screen, (40, 40, 40), (xp_bar_x, xp_bar_y, xp_bar_width, xp_bar_height), border_radius=2)
        xp_fill_width = int(xp_bar_width * (p1.xp / p1.xp_to_next))
        pygame.draw.rect(screen, (0, 255, 180), (xp_bar_x, xp_bar_y, xp_fill_width, xp_bar_height), border_radius=2)
        xp_font = pygame.font.Font(os.path.join('assets', 'fonts', 'Creepster-Regular.ttf'), max(10, xp_bar_height*2)) if os.path.exists(os.path.join('assets', 'fonts', 'Creepster-Regular.ttf')) else pygame.font.Font(None, max(10, xp_bar_height*2))
        xp_text = f"LVL {p1.level}  XP: {p1.xp}/{p1.xp_to_next}"
        xp_text_surface = xp_font.render(xp_text, True, (0, 255, 180))
        screen.blit(xp_text_surface, (xp_bar_x + 4, xp_bar_y - xp_text_surface.get_height() - 2))
        # --- Draw bullets ---
        for bullet in bullets:
            bx = int(bullet['x'] - camera_x + GAME_X)
            by = int(bullet['y'] - camera_y + GAME_Y)
            pygame.draw.circle(screen, bullet['color'], (bx, by), bullet['size'])
        pygame.display.flip()
        clock.tick(60)
    stats.save_records(current_game_time_seconds, current_max_distance)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()












