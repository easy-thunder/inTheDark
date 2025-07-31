import pygame
import math


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
