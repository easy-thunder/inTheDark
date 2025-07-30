import pygame
import os
import math

def draw_world(screen, world, camera_x, camera_y, game_x, game_y, tile_size, border_color, menu_color, black, darkness_alpha=0):
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
        if bullet.get('type') == 'beam':
            # Draw beam trail
            trail_points = bullet.get('trail_points', [])
            if len(trail_points) >= 2:
                # Convert trail points to screen coordinates
                screen_points = []
                for x, y in trail_points:
                    screen_x = x - camera_x + game_x
                    screen_y = y - camera_y + game_y
                    screen_points.append((screen_x, screen_y))
                
                # Draw trail with fading effect
                for i in range(len(screen_points) - 1):
                    # Fade from bright at the end to dim at the start
                    alpha = int(255 * (i / len(screen_points)))
                    trail_color = (*bullet['color'], alpha)
                    
                    # Draw the line segment with thickness
                    pygame.draw.line(screen, bullet['color'], screen_points[i], screen_points[i + 1], 
                                   max(1, int(bullet['size'] * 2)))
            
            # Draw current beam position (bright center)
            screen_x = bullet['x'] - camera_x + game_x
            screen_y = bullet['y'] - camera_y + game_y
            pygame.draw.circle(screen, bullet['color'], (int(screen_x), int(screen_y)), 
                             max(1, int(bullet['size'] * 3)))
            continue
        elif bullet.get('is_orbital'):
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
        elif bullet.get('is_orbital_beam'):
            # --- Draw Solar Death Beam (now generalized for any color) ---
            gx = int(bullet['x'] - camera_x + game_x)
            gy = int(bullet['y'] - camera_y + game_y)
            current_time = pygame.time.get_ticks()
            warm_up_elapsed = (current_time - bullet['warm_up_start']) / 1000.0
            warm_up_time = bullet.get('warm_up_time', 2.0)
            base_color = bullet.get('color', (255, 255, 0))
            r, g, b = base_color
            # Generate lighter and darker variants
            light_color = (min(255, int(r + 0.5 * (255 - r))), min(255, int(g + 0.5 * (255 - g))), min(255, int(b + 0.5 * (255 - b))))
            dark_color = (max(0, int(r * 0.5)), max(0, int(g * 0.5)), max(0, int(b * 0.5)))
            if not bullet.get('beam_active', False):
                if warm_up_elapsed < warm_up_time:
                    charge_progress = warm_up_elapsed / warm_up_time
                    charge_radius = int(20 + charge_progress * 30)
                    charge_alpha = int(100 + charge_progress * 155)
                    charge_surface = pygame.Surface((charge_radius * 2, charge_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(charge_surface, (*light_color, charge_alpha), (charge_radius, charge_radius), charge_radius)
                    screen.blit(charge_surface, (gx - charge_radius, gy - charge_radius))
                    font = pygame.font.Font(None, 24)
                    charge_text = font.render("CHARGING", True, light_color)
                    screen.blit(charge_text, (gx - charge_text.get_width() // 2, gy - 40))
                continue
            else:
                beam_radius = int(bullet.get('splash', 2.0) * 32)
                beam_elapsed = (current_time - bullet['beam_start_time']) / 1000.0
                beam_duration = bullet.get('beam_duration', 5.0)
                beam_intensity = 1.0 - (beam_elapsed / beam_duration)
                for i in range(3):
                    flare_radius = beam_radius - i * 3
                    if flare_radius <= 0:
                        break
                    if i == 0:
                        color = light_color  # Bright center
                    elif i == 1:
                        color = base_color   # Middle
                    else:
                        color = dark_color   # Edge
                    flicker = 0.8 + 0.2 * math.sin(current_time * 0.01)
                    flare_alpha = int(255 * beam_intensity * flicker)
                    beam_surface = pygame.Surface((flare_radius * 2, flare_radius * 2), pygame.SRCALPHA)
                    pygame.draw.circle(beam_surface, (*color, flare_alpha), (flare_radius, flare_radius), flare_radius)
                    screen.blit(beam_surface, (gx - flare_radius, gy - flare_radius))
                for flare in range(8):
                    flare_angle = (current_time * 0.02 + flare * 45) % 360
                    flare_radius = beam_radius + 10 + (current_time * 0.01) % 20
                    flare_x = gx + int(math.cos(math.radians(flare_angle)) * flare_radius)
                    flare_y = gy + int(math.sin(math.radians(flare_angle)) * flare_radius)
                    flare_size = int(3 * beam_intensity)
                    if flare_size > 0:
                        pygame.draw.circle(screen, light_color, (flare_x, flare_y), flare_size)
                remaining_time = beam_duration - beam_elapsed
                if remaining_time > 0:
                    font = pygame.font.Font(None, 20)
                    time_text = font.render(f"{remaining_time:.1f}s", True, light_color)
                    screen.blit(time_text, (gx - time_text.get_width() // 2, gy + beam_radius + 5))
                continue
        elif bullet.get('is_spray_particle'):
            bx = int(bullet['x'] - camera_x + game_x)
            by = int(bullet['y'] - camera_y + game_y)
            
            # Get particle properties
            particle_variation = bullet.get('particle_variation', 0)
            size_variation = bullet.get('particle_size_variation', 1.0)
            intensity = bullet.get('particle_intensity', 1.0)
            base_color = bullet.get('color', (255, 255, 255))
            current_time = pygame.time.get_ticks()

            # --- Generate Color Variants ---
            r, g, b = base_color
            bright_color = (min(255, r + 60), min(255, g + 60), min(255, b + 60))
            dark_color = (max(0, r - 40), max(0, g - 40), max(0, b - 40))
            
            # Calculate dynamic particle properties
            time_offset = current_time * 0.01 + particle_variation
            flicker = 0.8 + 0.4 * math.sin(time_offset * 3) * math.cos(time_offset * 2)
            size_modifier = size_variation * flicker * intensity
            
            base_size = int(bullet['size'] * size_modifier)
            
            # Draw main particle body with gradient effect
            for i in range(3):
                layer_size = base_size - i * 2
                if layer_size <= 0: break
                    
                if i == 0: color = bright_color
                elif i == 1: color = base_color
                else: color = dark_color
                
                offset_x = int(math.sin(time_offset + i) * 2)
                offset_y = int(math.cos(time_offset + i * 0.7) * 2)
                pygame.draw.circle(screen, color, (bx + offset_x, by + offset_y), layer_size)
            
            # Draw particle tongues
            for tongue in range(2):
                tongue_angle = time_offset * 0.5 + tongue * math.pi + particle_variation
                tongue_length = base_size * (0.8 + 0.4 * math.sin(time_offset * 2))
                tongue_x = bx + int(math.cos(tongue_angle) * tongue_length)
                tongue_y = by + int(math.sin(tongue_angle) * tongue_length)
                tongue_size = max(1, int(base_size * 0.4 * flicker))
                
                for j in range(2):
                    if j == 0: tongue_color = bright_color
                    else: tongue_color = base_color
                    pygame.draw.circle(screen, tongue_color, (tongue_x, tongue_y), tongue_size - j)
            
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

def draw_weapon_info(screen, weapon, x, y):
    # Example function for weapon info display
    font = pygame.font.Font(None, 20)
    # Common stats
    text = f"DMG: {weapon.common.damage} | ACC: {weapon.common.accuracy} | CLIP: {weapon.common.clip_size} | RATE: {weapon.common.fire_rate}"
    info_surface = font.render(text, True, (255,255,255))
    screen.blit(info_surface, (x, y))
    # Uncommon stats
    if weapon.uncommon.volley:
        volley_text = font.render(f"Volley: {weapon.uncommon.volley}", True, (200,200,0))
        screen.blit(volley_text, (x, y+20))
    if weapon.uncommon.spread:
        spread_text = font.render(f"Spread: {weapon.uncommon.spread}", True, (200,200,0))
        screen.blit(spread_text, (x, y+40))
    if weapon.uncommon.warm_up_time:
        warmup_text = font.render(f"Warmup: {weapon.uncommon.warm_up_time}s", True, (255,100,0))
        screen.blit(warmup_text, (x, y+60))
    # Unique stats
    if weapon.unique.beam_duration:
        beam_text = font.render(f"Beam Duration: {weapon.unique.beam_duration}s", True, (255,255,0))
        screen.blit(beam_text, (x, y+80))
    if weapon.unique.beam_damage_tick:
        tick_text = font.render(f"Beam Tick: {weapon.unique.beam_damage_tick}s", True, (255,255,0))
        screen.blit(tick_text, (x, y+100)) 



def create_radial_light_surface(radius, darkness_alpha):
    """
    Creates a radial gradient light surface once and reuses it.
    Alpha fades from 0 (transparent) at center to darkness_alpha at edge (opaque).
    """
    surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    center = radius

    for r in range(radius, 0, -1):
        alpha = int(darkness_alpha * (1 - (r / radius)))  # Brighter in center, darker at edge
        pygame.draw.circle(surface, (0, 0, 0, alpha), (center, center), r)

    return surface



_light_cache = {}  # Add this at the top of your file (for caching)

def draw_darkness_overlay(screen, darkness_alpha, lights=[]):
    """
    Draws a darkness overlay and subtracts cached radial light gradients from the given positions.
    """
    if darkness_alpha <= 0:
        return

    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, darkness_alpha))

    for light in lights:
        x, y, radius = light['x'], light['y'], light['radius']

        key = (radius, darkness_alpha)
        if key not in _light_cache:
            _light_cache[key] = create_radial_light_surface(radius, darkness_alpha)

        light_surf = _light_cache[key]
        overlay.blit(light_surf, (x - radius, y - radius), special_flags=pygame.BLEND_RGBA_SUB)

    screen.blit(overlay, (0, 0))

    
