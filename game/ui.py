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
        
        # Draw burning effects for creatures on fire
        if hasattr(creature, 'burning_effects') and creature.burning_effects:
            # Draw organic flame effects around the creature
            cx = int(creature.rect.centerx - camera_x + game_x)
            cy = int(creature.rect.centery - camera_y + game_y)
            current_time = pygame.time.get_ticks()
            
            # Create multiple flame clusters around the creature
            for cluster in range(3):
                cluster_angle = (current_time / 200 + cluster * 120) % 360
                cluster_radius = 12 + (current_time / 300) % 8
                cluster_x = cx + int(math.cos(math.radians(cluster_angle)) * cluster_radius)
                cluster_y = cy + int(math.sin(math.radians(cluster_angle)) * cluster_radius)
                
                # Draw organic flame shape for each cluster
                flame_time = current_time * 0.02 + cluster
                flicker = 0.7 + 0.3 * math.sin(flame_time * 4)
                flame_size = int(4 * flicker)
                
                # Draw flame body with gradient
                for i in range(3):
                    layer_size = flame_size - i
                    if layer_size <= 0:
                        break
                    
                    if i == 0:
                        color = (255, 150, 0)  # Bright orange
                    elif i == 1:
                        color = (255, 100, 0)  # Medium orange
                    else:
                        color = (200, 80, 0)   # Dark orange
                    
                    # Add organic movement
                    offset_x = int(math.sin(flame_time + i) * 2)
                    offset_y = int(math.cos(flame_time + i * 0.8) * 2)
                    pygame.draw.circle(screen, color, (cluster_x + offset_x, cluster_y + offset_y), layer_size)
                
                # Draw flame tongues
                for tongue in range(2):
                    tongue_angle = flame_time + tongue * math.pi
                    tongue_length = flame_size * (0.6 + 0.4 * math.sin(flame_time * 2))
                    tongue_x = cluster_x + int(math.cos(tongue_angle) * tongue_length)
                    tongue_y = cluster_y + int(math.sin(tongue_angle) * tongue_length)
                    pygame.draw.circle(screen, (255, 120, 0), (tongue_x, tongue_y), max(1, int(flame_size * 0.3)))
            
            # Draw smoke particles rising from the creature
            for smoke in range(4):
                smoke_angle = (current_time / 150 + smoke * 90) % 360
                smoke_radius = 8 + (current_time / 400) % 6
                smoke_x = cx + int(math.cos(math.radians(smoke_angle)) * smoke_radius)
                smoke_y = cy - 10 - int(math.sin(math.radians(smoke_angle)) * smoke_radius)  # Rising smoke
                
                # Smoke particle with fade effect
                smoke_time = current_time * 0.01 + smoke
                smoke_fade = 0.3 + 0.2 * math.sin(smoke_time)
                smoke_size = int(3 * smoke_fade)
                
                if smoke_size > 0:
                    pygame.draw.circle(screen, (100, 100, 100), (smoke_x, smoke_y), smoke_size)
            
            # Draw ember particles floating around
            for ember in range(2):
                ember_angle = (current_time / 100 + ember * 180) % 360
                ember_radius = 15 + (current_time / 250) % 10
                ember_x = cx + int(math.cos(math.radians(ember_angle)) * ember_radius)
                ember_y = cy + int(math.sin(math.radians(ember_angle)) * ember_radius)
                
                ember_time = current_time * 0.03 + ember
                ember_flicker = 0.5 + 0.5 * math.sin(ember_time * 5)
                ember_size = int(2 * ember_flicker)
                
                if ember_size > 0:
                    # Bright yellow ember for burning creatures
                    ember_color = (255, 255, 0)
                    pygame.draw.circle(screen, ember_color, (ember_x, ember_y), ember_size)
        
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
        if bullet.get('is_orbital'):
            # --- Draw Orbital Strike ---
            # Ground position
            gx = int(bullet['x'] - camera_x + game_x)
            gy = int(bullet['y'] - camera_y + game_y)
            
            # Shadow grows as missile falls
            shadow_size = int(bullet['size'] * (1 - bullet['z'] / bullet['initial_z']))
            if shadow_size > 1:
                pygame.draw.circle(screen, (0,0,0,100), (gx, gy), shadow_size)
            
            # Missile grows and appears to fall
            missile_draw_y = int(gy - bullet['z'] * 0.5) # Y-offset for perspective
            missile_size = int(shadow_size * 0.8) # Slightly smaller than shadow
            if missile_size > 1:
                 pygame.draw.circle(screen, bullet['color'], (gx, missile_draw_y), missile_size)
            continue

        # Special flame bullet effects
        if bullet.get('is_flame'):
            bx = int(bullet['x'] - camera_x + game_x)
            by = int(bullet['y'] - camera_y + game_y)
            
            # Get flame properties
            flame_variation = bullet.get('flame_variation', 0)
            size_variation = bullet.get('flame_size_variation', 1.0)
            intensity = bullet.get('flame_intensity', 1.0)
            # Ensure intensity is a valid number
            if intensity is None or not isinstance(intensity, (int, float)):
                intensity = 1.0
            current_time = pygame.time.get_ticks()
            
            # Calculate dynamic flame properties
            time_offset = current_time * 0.01 + flame_variation
            flicker = 0.8 + 0.4 * math.sin(time_offset * 3) * math.cos(time_offset * 2)
            size_modifier = size_variation * flicker * intensity
            
            # Create organic flame shape with multiple overlapping circles
            base_size = int(bullet['size'] * size_modifier)
            
            # Draw main flame body with gradient effect
            for i in range(3):
                layer_size = base_size - i * 2
                if layer_size <= 0:
                    break
                    
                # Color gradient from bright center to darker edges
                if i == 0:
                    color = (255, int(200 * intensity), 0)  # Bright orange center
                elif i == 1:
                    color = (255, int(150 * intensity), 0)  # Medium orange
                else:
                    color = (200, int(100 * intensity), 0)  # Darker orange edge
                
                # Add some organic movement to the flame shape
                offset_x = int(math.sin(time_offset + i) * 2)
                offset_y = int(math.cos(time_offset + i * 0.7) * 2)
                
                pygame.draw.circle(screen, color, (bx + offset_x, by + offset_y), layer_size)
            
            # Draw flame tongues (irregular flame extensions)
            for tongue in range(2):
                tongue_angle = time_offset * 0.5 + tongue * math.pi + flame_variation
                tongue_length = base_size * (0.8 + 0.4 * math.sin(time_offset * 2))
                tongue_x = bx + int(math.cos(tongue_angle) * tongue_length)
                tongue_y = by + int(math.sin(tongue_angle) * tongue_length)
                tongue_size = max(1, int(base_size * 0.4 * flicker))
                
                # Gradient for flame tongues
                for j in range(2):
                    if j == 0:
                        tongue_color = (255, int(180 * intensity), 0)
                    else:
                        tongue_color = (200, int(120 * intensity), 0)
                    pygame.draw.circle(screen, tongue_color, (tongue_x, tongue_y), tongue_size - j)
            
            # Draw trailing flame particles with organic movement
            for i in range(4):
                trail_progress = (i + 1) * 0.25
                trail_x = int(bx - bullet['dx'] * bullet['speed'] * trail_progress * 0.4)
                trail_y = int(by - bullet['dy'] * bullet['speed'] * trail_progress * 0.4)
                
                # Add organic movement to trail
                trail_offset_x = int(math.sin(time_offset * 2 + i) * 3)
                trail_offset_y = int(math.cos(time_offset * 1.5 + i) * 3)
                trail_x += trail_offset_x
                trail_y += trail_offset_y
                
                trail_size = max(1, int(base_size * (1 - trail_progress) * 0.6))
                trail_alpha = int(255 * (1 - trail_progress) * 0.8)
                
                # Trail color gradient
                if trail_progress < 0.5:
                    trail_color = (255, int(150 * intensity), 0)
                else:
                    trail_color = (200, int(100 * intensity), 0)
                
                pygame.draw.circle(screen, trail_color, (trail_x, trail_y), trail_size)
            
            # Draw flickering ember particles
            for ember in range(3):
                ember_angle = time_offset * 0.3 + ember * 2.1 + flame_variation
                ember_radius = base_size * (0.3 + 0.2 * math.sin(time_offset + ember))
                ember_x = bx + int(math.cos(ember_angle) * ember_radius)
                ember_y = by + int(math.sin(ember_angle) * ember_radius)
                ember_size = max(1, int(base_size * 0.2 * flicker))
                
                # Bright yellow ember - ensure integer color values
                ember_green = int(255 * intensity)
                ember_green = max(0, min(255, ember_green))  # Clamp to valid range
                ember_color = (255, ember_green, 0)
                pygame.draw.circle(screen, ember_color, (ember_x, ember_y), ember_size)
            
            continue

        # Regular bullet drawing
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