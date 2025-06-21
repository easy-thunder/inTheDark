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

class Player:
    def __init__(self, x, y, character):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, PLAYER_SIZE, PLAYER_SIZE)
        self.character = character
        self.hp = character.max_hp
        self.speed = character.speed
        # XP/Level system
        self.xp = 0
        self.level = 1
        self.xp_to_next = 100
        self.last_xp_time = pygame.time.get_ticks()
        # Ability points
        self.ability_points = character.ability_points
        # Armor and regen
        self.armor = character.armor
        self.hp_regen = character.hp_regen
        self.ap_regen = character.ap_regen
        self.last_regen_time = pygame.time.get_ticks()
        # Death and revival
        self.dead = False
        self.time_of_death = None
        self.revive_progress = 0  # seconds standing over
        # Aiming
        self.aim_direction = (1, 0)  # Default aim right
        # In the future, add input_profile/controller here
    
    def take_damage(self, amount):
        if self.dead:
            return
        dealt_damage = max(0, amount - self.armor)
        self.hp -= dealt_damage
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.time_of_death = pygame.time.get_ticks()
            self.revive_progress = 0
    
    def move(self, dx, dy, walls):
        if self.dead:
            return
        self.x = self.rect.x
        self.y = self.rect.y
        if dx != 0:
            self.rect.x += dx
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dx > 0:
                        self.rect.right = wall.left
                    if dx < 0:
                        self.rect.left = wall.right
        if dy != 0:
            self.rect.y += dy
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dy > 0:
                        self.rect.bottom = wall.top
                    if dy < 0:
                        self.rect.top = wall.bottom
        self.x = self.rect.x
        self.y = self.rect.y
    
    def gain_xp(self, amount):
        if self.dead:
            return
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.xp_to_next += 100
    
    def update_xp(self):
        if self.dead:
            return
        now = pygame.time.get_ticks()
        if now - self.last_xp_time >= 10000:  # 10 seconds
            self.gain_xp(1)
            self.last_xp_time = now
    
    def regen(self):
        if self.dead:
            return
        now = pygame.time.get_ticks()
        if now - self.last_regen_time >= 1000:  # 1 second
            # HP regen
            if self.hp < self.character.max_hp:
                self.hp = min(self.character.max_hp, self.hp + self.hp_regen)
            # AP regen
            if self.ability_points < self.character.ability_points:
                self.ability_points = min(self.character.ability_points, self.ability_points + self.ap_regen)
            self.last_regen_time = now
    
    def try_revive(self):
        self.dead = False
        self.hp = max(1, int(math.ceil(self.character.max_hp / 2)))
        self.ability_points = self.character.ability_points
        self.time_of_death = None
        self.revive_progress = 0
    
    def update_aim(self, camera_x, camera_y, player_index=0):
        if self.dead:
            return
        # For now, only Player 1 uses mouse aiming
        if player_index == 0:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Player center in screen coordinates
            center_x = self.rect.x - camera_x + GAME_X + self.rect.width // 2
            center_y = self.rect.y - camera_y + GAME_Y + self.rect.height // 2
            dx = mouse_x - center_x
            dy = mouse_y - center_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.aim_direction = (dx / dist, dy / dist)
            else:
                self.aim_direction = (1, 0)
        # For future: add controller stick aiming for other players
    
    def has_infinite_ammo(self, weapon):
        if not weapon or not hasattr(self.character, 'specializations') or not weapon.specialization_type:
            return False
        return self.character.specializations.get(weapon.specialization_type, 0) >= weapon.specialization_level

    def reload_weapon(self, weapon_index=0):
        weapon = self.character.weapons[weapon_index] if hasattr(self.character, 'weapons') and self.character.weapons else None
        if weapon and not weapon.is_reloading and weapon.current_clip < weapon.clip_size:
            weapon.is_reloading = True
            weapon.reload_start = pygame.time.get_ticks()

    def update_reload(self, weapon_index=0):
        weapon = self.character.weapons[weapon_index] if hasattr(self.character, 'weapons') and self.character.weapons else None
        if weapon and weapon.is_reloading:
            now = pygame.time.get_ticks()
            if now - weapon.reload_start >= weapon.reload_speed * 1000:
                # Calculate how many bullets to reload
                if self.has_infinite_ammo(weapon):
                    reload_amount = weapon.clip_size
                elif weapon.ammo is None:
                    reload_amount = weapon.clip_size
                else:
                    reload_amount = min(weapon.clip_size, weapon.ammo)
                weapon.current_clip = reload_amount
                # Only decrement reserve if not infinite
                if not self.has_infinite_ammo(weapon) and weapon.ammo is not None:
                    weapon.ammo -= reload_amount
                weapon.is_reloading = False

    def draw(self, surface, camera_x, camera_y, player_index=0, current_weapon_index=0):
        draw_rect = self.rect.move(-camera_x + GAME_X, -camera_y + GAME_Y)
        if self.dead:
            pygame.draw.rect(surface, (80, 80, 80), draw_rect)
        else:
            pygame.draw.rect(surface, RED, draw_rect)
        # --- Health Bar ---
        bar_width = draw_rect.width
        bar_height = 1  # Extremely thin
        bar_x = draw_rect.x
        bar_y = draw_rect.y - 10  # Slightly higher to make room for ability bar
        s = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        s.fill((100, 0, 0, 120))  # dark red, semi-transparent
        surface.blit(s, (bar_x, bar_y))
        if self.hp > 0:
            fill_width = int(bar_width * (self.hp / self.character.max_hp))
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(surface, RED, fill_rect)
        ab_bar_y = bar_y + bar_height + 2  # 2px below health bar
        s2 = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        s2.fill((0, 0, 100, 120))  # dark blue, semi-transparent
        surface.blit(s2, (bar_x, ab_bar_y))
        if self.ability_points > 0:
            ab_fill_width = int(bar_width * (self.ability_points / self.character.ability_points))
            ab_fill_rect = pygame.Rect(bar_x, ab_bar_y, ab_fill_width, bar_height)
            pygame.draw.rect(surface, (0, 120, 255), ab_fill_rect)
        if self.dead and self.revive_progress > 0:
            revive_bar_y = ab_bar_y + bar_height + 2
            revive_bar_height = 2
            revive_bar_width = int(bar_width * (self.revive_progress / self.character.revival_time))
            pygame.draw.rect(surface, (255, 255, 0), (bar_x, revive_bar_y, revive_bar_width, revive_bar_height))
        # --- Draw aim direction for Player 1 ---
        if player_index == 0 and not self.dead:
            center_x = draw_rect.x + draw_rect.width // 2
            center_y = draw_rect.y + draw_rect.height // 2
            aim_len = 40
            end_x = int(center_x + self.aim_direction[0] * aim_len)
            end_y = int(center_y + self.aim_direction[1] * aim_len)
            pygame.draw.line(surface, (255, 255, 0), (center_x, center_y), (end_x, end_y), 2)
        # --- Ammo UI to the right of HP bar for all players ---
        weapon = self.character.weapons[current_weapon_index] if hasattr(self.character, 'weapons') and len(self.character.weapons) > current_weapon_index else None
        if weapon:
            ammo_font = pygame.font.Font(None, 18)
            if weapon.ammo is None:
                reserve_text = "∞"
            else:
                reserve_text = str(weapon.ammo)
            if weapon.is_reloading:
                clip_text = "..."
            else:
                clip_text = str(weapon.current_clip)
            ammo_text = f"{reserve_text} | {clip_text}"
            ammo_surface = ammo_font.render(ammo_text, True, (255, 255, 0))
            ammo_x = bar_x + bar_width + 8
            ammo_y = bar_y - 6
            surface.blit(ammo_surface, (ammo_x, ammo_y))
            # --- Reload progress semi-circle ---
            if weapon.is_reloading:
                now = pygame.time.get_ticks()
                progress = min(1.0, (now - weapon.reload_start) / (weapon.reload_speed * 1000))
                arc_radius = 6  # Much smaller
                arc_center = (ammo_x + ammo_surface.get_width() // 2, ammo_y - arc_radius + 2)
                arc_rect = pygame.Rect(arc_center[0] - arc_radius, arc_center[1] - arc_radius, arc_radius * 2, arc_radius * 2)
                start_angle = math.pi  # 180 deg (left)
                end_angle = math.pi + math.pi * progress  # fill clockwise
                pygame.draw.arc(surface, (255, 255, 0), arc_rect, start_angle, end_angle, 2)
            # --- Warm-up progress bar ---
            elif weapon.warm_up_time and weapon.is_warming_up:
                now = pygame.time.get_ticks()
                warm_up_progress = min(1.0, (now - weapon.warm_up_start) / (weapon.warm_up_time * 1000))
                warm_up_bar_width = ammo_surface.get_width()
                warm_up_bar_height = 3
                warm_up_bar_x = ammo_x
                warm_up_bar_y = ammo_y + ammo_surface.get_height() + 2
                # Background
                pygame.draw.rect(surface, (60, 60, 60), (warm_up_bar_x, warm_up_bar_y, warm_up_bar_width, warm_up_bar_height))
                # Progress
                if warm_up_progress > 0:
                    fill_width = int(warm_up_bar_width * warm_up_progress)
                    pygame.draw.rect(surface, (255, 100, 0), (warm_up_bar_x, warm_up_bar_y, fill_width, warm_up_bar_height))

def main():
    world = World(seed=123)
    stats = GameStats()
    player_start_pos = (TILE_SIZE, TILE_SIZE)
    # Use default character 'testy'
    players = [
        Player(player_start_pos[0], player_start_pos[1], copy.deepcopy(TESTY)),
        Player(player_start_pos[0] + TILE_SIZE * 2, player_start_pos[1], copy.deepcopy(TESTY))
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
            player = players[0]
            if not player.dead:
                weapon = player.character.weapons[player_weapon_indices[0]]
                now = pygame.time.get_ticks()
                
                # Handle warm-up time
                if weapon.warm_up_time and not weapon.is_warming_up:
                    weapon.is_warming_up = True
                    weapon.warm_up_start = now
                
                # Check if weapon is ready to fire (warmed up or no warm-up required)
                can_fire = True
                if weapon.warm_up_time and weapon.is_warming_up:
                    warm_up_elapsed = (now - weapon.warm_up_start) / 1000.0
                    if warm_up_elapsed < weapon.warm_up_time:
                        can_fire = False
                
                fire_delay = 60000 / weapon.fire_rate  # ms per shot
                if can_fire and now - weapon.last_shot_time >= fire_delay and weapon.current_clip > 0 and not weapon.is_reloading:
                    spread_angle = (random.uniform(-0.5, 0.5) * weapon.accuracy * 360)
                    base_dx, base_dy = player.aim_direction
                    angle = math.atan2(base_dy, base_dx) + math.radians(spread_angle)
                    dx = math.cos(angle)
                    dy = math.sin(angle)
                    bullet_speed = weapon.bullet_speed
                    bullet_range = weapon.range * TILE_SIZE
                    bullet_size = int(weapon.bullet_size * TILE_SIZE)
                    bullet = {
                        'x': player.rect.centerx,
                        'y': player.rect.centery,
                        'dx': dx,
                        'dy': dy,
                        'speed': bullet_speed,
                        'range': bullet_range,
                        'distance': 0,
                        'size': bullet_size,
                        'damage': weapon.damage,
                        'color': weapon.bullet_color,
                        'splash': weapon.splash,
                        'weapon_index': player_weapon_indices[0]
                    }
                    bullets.append(bullet)
                    weapon.current_clip -= 1
                    weapon.last_shot_time = now
                    # Automatic reload if clip is empty and reserve ammo (or infinite)
                    if weapon.current_clip == 0 and (player.has_infinite_ammo(weapon) or (weapon.ammo is None or weapon.ammo > 0)):
                        player.reload_weapon(player_weapon_indices[0])
        else:
            # Reset warm-up when no fire button is pressed
            for player in players:
                for weapon in player.character.weapons:
                    if weapon.warm_up_time:
                        weapon.is_warming_up = False
                        weapon.warm_up_start = None
        
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
            player.update_aim(camera_x, camera_y, player_index=i)
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
            player.draw(screen, camera_x, camera_y, player_index=i, current_weapon_index=player_weapon_indices[i])

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

        # --- Update bullets ---
        for bullet in bullets[:]:
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']
            bullet['distance'] += bullet['speed']
            if bullet['distance'] > bullet['range']:
                bullets.remove(bullet)

        # --- Bullet collision with creatures and walls ---
        for bullet in bullets[:]:
            bullet_rect = pygame.Rect(
                bullet['x'] - bullet['size'],
                bullet['y'] - bullet['size'],
                bullet['size'] * 2,
                bullet['size'] * 2
            )
            # Wall collision
            hit_wall = False
            for wall in visible_walls:
                if bullet_rect.colliderect(wall):
                    hit_wall = True
                    break
            if hit_wall:
                # Splash damage if rocket
                if bullet.get('splash'):
                    splash_radius = bullet['splash'] * TILE_SIZE
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
                bullets.remove(bullet)
                continue
            # Creature collision (PIERCING SUPPORT)
            hit_creature = False
            for creature in creatures:
                if creature.hp > 0 and bullet_rect.colliderect(creature.rect):
                    # Splash damage if rocket
                    if bullet.get('splash'):
                        splash_radius = bullet['splash'] * TILE_SIZE
                        center = (bullet['x'], bullet['y'])
                        splash_damages = [20, 16, 12, 8, 2]
                        for c in creatures:
                            if c.hp > 0:
                                dist = math.hypot(c.rect.centerx - center[0], c.rect.centery - center[1])
                                for i in range(5):
                                    if dist <= splash_radius * (i+1)/5:
                                        c.hp -= splash_damages[i]
                                        break
                        splash_effects.append({'x': center[0], 'y': center[1], 'radius': splash_radius, 'start': pygame.time.get_ticks()})
                        bullets.remove(bullet)
                        break
                    else:
                        # --- PIERCING LOGIC ---
                        # On bullet creation, set 'pierces_left' and 'original_damage' if not present
                        if 'pierces_left' not in bullet:
                            # Get weapon for this bullet
                            weapon_index = bullet.get('weapon_index', 0)
                            weapon = None
                            for player in players:
                                if hasattr(player.character, 'weapons') and len(player.character.weapons) > weapon_index:
                                    weapon = player.character.weapons[weapon_index]
                                    break
                            piercing = getattr(weapon, 'piercing', 0) if weapon else 0
                            bullet['pierces_left'] = piercing
                            bullet['original_damage'] = bullet['damage']
                            bullet['hit_creatures'] = set()  # Track which creatures this bullet has hit
                        
                        # Check if we've already hit this creature
                        if id(creature) in bullet['hit_creatures']:
                            continue
                        
                        # Apply damage
                        creature.hp -= bullet['damage']
                        bullet['hit_creatures'].add(id(creature))  # Mark this creature as hit
                        
                        # If no piercing, remove bullet
                        if bullet['pierces_left'] == 0:
                            bullets.remove(bullet)
                            break
                        # If piercing, decrement and reduce damage
                        bullet['pierces_left'] -= 1
                        # Reduce damage by 10%, but not below 70% of original
                        min_damage = bullet['original_damage'] * 0.3
                        new_damage = bullet['damage'] * 0.9
                        bullet['damage'] = max(min_damage, new_damage)
                        # If out of pierces, remove bullet
                        if bullet['pierces_left'] < 0:
                            bullets.remove(bullet)
                            break
                    hit_creature = True
            # Only allow one creature hit per frame per bullet
            if hit_creature:
                continue

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












