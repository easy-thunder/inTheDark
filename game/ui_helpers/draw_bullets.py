import pygame
import math


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
