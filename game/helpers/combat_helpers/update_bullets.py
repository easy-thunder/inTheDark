import pygame
import math

from game.helpers.combat_helpers.handle_splash_damage import handle_splash_damage
from game.weapons import ContactEffect
from game.helpers.combat_helpers.apply_creature_effects import apply_creature_effects
def update_bullets(bullets, creatures, walls, dt, camera_x=0, camera_y=0):
    bullets_to_remove = []
    splash_effects = []  # Initialize splash_effects list
    
    for bullet in bullets[:]:
        # --- MINE LOGIC ---
        if getattr(bullet, 'is_mine', False) or bullet.get('is_mine', False):
            # Mines do not move and do not disappear due to range
            # Check for proximity to any creature
            triggered = False
            trigger_radius = bullet.get('trigger_radius', 32)
            for creature in creatures:
                if creature.hp > 0:
                    dist = math.hypot(bullet['x'] - creature.rect.centerx, bullet['y'] - creature.rect.centery)
                    if dist <= trigger_radius:
                        # Explode: deal splash damage to all creatures in splash radius
                        splash_radius = (bullet.get('splash', 2.0) * 32)  # Default 2 tiles
                        for c in creatures:
                            if c.hp > 0:
                                cdist = math.hypot(bullet['x'] - c.rect.centerx, bullet['y'] - c.rect.centery)
                                if cdist <= splash_radius:
                                    c.hp -= bullet['damage']
                        bullets_to_remove.append(bullet)
                        triggered = True
                        break
            if triggered:
                continue  # Skip further processing for this bullet
            # Draw mine (optional: add visual effect here)
            continue  # Skip normal bullet logic for mines
            
        if bullet.get('type') == 'beam':
            # Store previous position for robust collision detection
            prev_x, prev_y = bullet['x'], bullet['y']

            # Handle beam projectiles
            dx = math.cos(bullet['angle']) * bullet['speed']
            dy = math.sin(bullet['angle']) * bullet['speed']
            
            bullet['x'] += dx
            bullet['y'] += dy
            
            # Add current position to trail
            bullet['trail_points'].append((bullet['x'], bullet['y']))
            
            # Limit trail length to prevent memory issues
            if len(bullet['trail_points']) > 20:
                bullet['trail_points'].pop(0)
            
            # Check for wall collisions
            bullet_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], 
                                    bullet['size'] * 2, bullet['size'] * 2)
            
            wall_collision = False
            for wall in walls:
                if bullet_rect.colliderect(wall):
                    wall_collision = True
                    break
            
            if wall_collision:
                bullets_to_remove.append(bullet)
                continue
            
            # Check for creature collisions using clipline to prevent tunneling
            for creature in creatures:
                if creature.id not in bullet['hits'] and creature.rect.clipline((prev_x, prev_y), (bullet['x'], bullet['y'])):
                    bullet['hits'].add(creature.id)
                    # Apply all effects for beam weapons
                    apply_creature_effects(bullet, creature)
                    
                    # Beams don't get destroyed by creature hits due to high pierce
                    if len(bullet['hits']) >= bullet['piercing']:
                        bullets_to_remove.append(bullet)
                        break
            
            # Check if beam has traveled its maximum range
            start_x, start_y = bullet['trail_points'][0]
            distance_traveled = math.sqrt((bullet['x'] - start_x)**2 + (bullet['y'] - start_y)**2)
            if distance_traveled > bullet['range']:
                bullets_to_remove.append(bullet)
                
        elif bullet.get('is_orbital'):
            # Handle orbital missiles
            bullet['z'] -= bullet['fall_speed']
            if bullet['z'] <= 0:
                # Landed, now explode
                if bullet.get('splash'):
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                bullets_to_remove.append(bullet)
                continue
            # Skip all other physics for orbital projectiles
            continue
            
        elif bullet.get('is_orbital_beam'):
            # Handle solar death beam mechanics
            current_time = pygame.time.get_ticks()
            warm_up_elapsed = (current_time - bullet['warm_up_start']) / 1000.0
            warm_up_time = bullet.get('warm_up_time', 2.0)
            
            if not bullet.get('beam_active', False) and warm_up_elapsed >= warm_up_time:
                # Warm-up complete, activate beam
                bullet['beam_active'] = True
                bullet['beam_start_time'] = current_time
                bullet['last_damage_time'] = current_time  # Start dealing damage immediately
            
            if bullet.get('beam_active', False):
                # Update mouse position for beam following
                mouse_x, mouse_y = pygame.mouse.get_pos()
                bullet['x'] = mouse_x + camera_x
                bullet['y'] = mouse_y + camera_y
                
                # Check if beam duration has expired
                beam_elapsed = (current_time - bullet['beam_start_time']) / 1000.0
                if beam_elapsed >= bullet['beam_duration']:
                    # Beam expired, remove it
                    bullets_to_remove.append(bullet)
                    continue
                
                # Apply continuous damage to creatures in beam area
                damage_elapsed = (current_time - bullet['last_damage_time']) / 1000.0
                if damage_elapsed >= bullet['beam_damage_tick']:
                    # Deal damage to creatures in beam area
                    beam_radius = bullet.get('splash', 2.0) * 32
                    for creature in creatures:
                        distance = math.sqrt((creature.rect.centerx - bullet['x'])**2 + 
                                           (creature.rect.centery - bullet['y'])**2)
                        if distance <= beam_radius:
                            # Apply all effects for orbital beam
                            apply_creature_effects(bullet, creature)
                    bullet['last_damage_time'] = current_time
            
            # Don't remove the beam - let it continue until duration expires
            continue
            
        elif bullet.get('is_grenade'):
            now = pygame.time.get_ticks()
            # Detonate after timer
            if now - bullet['creation_time'] >= bullet['detonation_time'] * 1000:
                if bullet.get('splash'):
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                bullets_to_remove.append(bullet)
                continue
            # Handle movement (arc, then roll)
            if bullet['phase'] == 'flying':
                bullet['x'] += bullet['velocity_x']
                bullet['y'] += bullet['velocity_y']
                bullet['distance_traveled'] += math.hypot(bullet['velocity_x'], bullet['velocity_y'])
                # Wall bounce logic for flying phase
                grenade_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], bullet['size']*2, bullet['size']*2)
                for wall in walls:
                    if grenade_rect.colliderect(wall):
                        # Simple bounce: reverse velocity and dampen
                        if abs(wall.left - grenade_rect.right) < 5 or abs(wall.right - grenade_rect.left) < 5:
                            bullet['velocity_x'] *= -0.7
                        if abs(wall.top - grenade_rect.bottom) < 5 or abs(wall.bottom - grenade_rect.top) < 5:
                            bullet['velocity_y'] *= -0.7
                # Use dot product to check if passed landing point
                start_x, start_y = bullet['start_x'], bullet['start_y']
                landing_x, landing_y = bullet['landing_x'], bullet['landing_y']
                dir_x, dir_y = bullet['direction_vec']
                to_current = ((bullet['x'] - start_x), (bullet['y'] - start_y))
                to_landing = ((landing_x - start_x), (landing_y - start_y))
                dot = to_current[0]*to_landing[0] + to_current[1]*to_landing[1]
                if dot >= 0 and bullet['distance_traveled'] >= bullet['travel_distance']:
                    bullet['phase'] = 'rolling'
                    bullet['velocity_x'] = bullet['roll_dx'] * 2
                    bullet['velocity_y'] = bullet['roll_dy'] * 2
            elif bullet['phase'] == 'rolling':
                bullet['x'] += bullet['velocity_x']
                bullet['y'] += bullet['velocity_y']
                # Wall bounce logic for rolling phase
                grenade_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], bullet['size']*2, bullet['size']*2)
                for wall in walls:
                    if grenade_rect.colliderect(wall):
                        if abs(wall.left - grenade_rect.right) < 5 or abs(wall.right - grenade_rect.left) < 5:
                            bullet['velocity_x'] *= -0.7
                        if abs(wall.top - grenade_rect.bottom) < 5 or abs(wall.bottom - grenade_rect.top) < 5:
                            bullet['velocity_y'] *= -0.7
                bullet['roll_left'] -= math.hypot(bullet['velocity_x'], bullet['velocity_y'])
                bullet['velocity_x'] *= 0.92
                bullet['velocity_y'] *= 0.92
                if bullet['roll_left'] <= 0 or (abs(bullet['velocity_x']) < 0.2 and abs(bullet['velocity_y']) < 0.2):
                    bullet['velocity_x'] = 0
                    bullet['velocity_y'] = 0
                    bullet['phase'] = 'stopped'
            # No wall/creature collision for grenades (they only explode on timer)
            continue
            
        else:
            # Handle regular bullets (existing logic)
            # Homing logic
            if bullet.get('homing_angle') and bullet.get('homing_time', 0) > 0 and dt > 0:
                bullet['homing_timer'] = bullet.get('homing_timer', 0) + int(dt * 1000)
                if bullet['homing_timer'] < bullet['homing_time'] * 1000:
                    # Find nearest living creature
                    nearest = None
                    nearest_dist = float('inf')
                    for creature in creatures:
                        if creature.hp > 0:
                            dist = math.hypot(creature.rect.centerx - bullet['x'], creature.rect.centery - bullet['y'])
                            if dist < nearest_dist:
                                nearest = creature
                                nearest_dist = dist
                    if nearest:
                        # Calculate angle to target
                        dx = nearest.rect.centerx - bullet['x']
                        dy = nearest.rect.centery - bullet['y']
                        target_angle = math.atan2(dy, dx)
                        current_angle = math.atan2(bullet['dy'], bullet['dx'])
                        # Find smallest angle difference
                        diff = (target_angle - current_angle + math.pi) % (2 * math.pi) - math.pi
                        max_turn = math.radians(bullet['homing_angle'])
                        # Clamp the turn
                        if abs(diff) < max_turn:
                            new_angle = target_angle
                        else:
                            new_angle = current_angle + max_turn * (1 if diff > 0 else -1)
                        bullet['dx'] = math.cos(new_angle)
                        bullet['dy'] = math.sin(new_angle)
            
            # Store previous position for distance calculation
            old_x = bullet['x']
            old_y = bullet['y']
            
            # Update position
            bullet['x'] += bullet['dx'] * bullet['speed']
            bullet['y'] += bullet['dy'] * bullet['speed']
            
            # Calculate actual distance moved this frame
            actual_distance = math.hypot(bullet['x'] - old_x, bullet['y'] - old_y)
            bullet['distance'] += actual_distance
            
            # Check if bullet has exceeded its range
            if bullet['distance'] > bullet['range']:
                bullets_to_remove.append(bullet)
                continue
            
            # Create bullet rectangle for collision detection
            bullet_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], 
                                    bullet['size'] * 2, bullet['size'] * 2)
            
            # --- Wall Collision with continuous detection ---
            hit_wall = False
            for wall in walls:
                # Check both current position and the path to it
                if bullet_rect.colliderect(wall) or wall.clipline((old_x, old_y), (bullet['x'], bullet['y'])):
                    hit_wall = True
                    break
            
            if hit_wall:
                if bullet['contact_effect'] == ContactEffect.EXPLODE:
                    # Handle explosive bullets
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                    bullets_to_remove.append(bullet)
                elif bullet.get('bounce_limit', 0) > 0:
                    # Handle bouncing bullets
                    bullet['bounce_limit'] -= 1
                    
                    # Move bullet back to previous position before bounce
                    bullet['x'] = old_x
                    bullet['y'] = old_y
                    
                    # --- Determine bounce direction ---
                    bullet_rect = pygame.Rect(bullet['x'] - bullet['size'], bullet['y'] - bullet['size'], bullet['size']*2, bullet['size']*2)
                    hit_wall_rect = None
                    for w in walls:
                        if bullet_rect.colliderect(w) or w.clipline((old_x, old_y), (bullet['x'], bullet['y'])):
                            hit_wall_rect = w
                            break
                    
                    if hit_wall_rect:
                        # Check for horizontal vs. vertical collision
                        bullet_rect.x -= bullet['dx'] * bullet['speed']
                        if bullet_rect.colliderect(hit_wall_rect):
                            bullet['dy'] *= -1 # Vertical bounce
                        else:
                            bullet['dx'] *= -1 # Horizontal bounce
                        
                        # Apply damage on bounce if applicable
                        if bullet['contact_effect'] == ContactEffect.DAMAGE_BOUNCE:
                            bullet['damage'] = bullet['damage'] * 1.1 # Increase damage by 10% on bounce
                    else:
                        # Default bounce if wall rect not found (should not happen)
                        bullet['dx'] *= -1
                        bullet['dy'] *= -1
                else:
                    bullets_to_remove.append(bullet)
                continue
            
            # --- Creature Collision with continuous detection ---
            contact_effect = bullet['contact_effect']
            collided_creature = None
            
            for creature in creatures:
                if creature.hp > 0 and (bullet_rect.colliderect(creature.rect) or 
                                      creature.rect.clipline((old_x, old_y), (bullet['x'], bullet['y']))):
                    collided_creature = creature
                    break
            
            if collided_creature:
                # Apply all creature effects modularly
                apply_creature_effects(bullet, collided_creature)
                # --- Handle bullet effects ---
                if bullet['contact_effect'] in [ContactEffect.DAMAGE_BOUNCE, ContactEffect.NO_DAMAGE_BOUNCE]:
                    if bullet.get('bounce_limit', 0) > 0:
                        bullet['bounce_limit'] -= 1
                        if bullet['contact_effect'] == ContactEffect.DAMAGE_BOUNCE:
                            bullet['damage'] *= 1.1
                        bullet['dx'] *= -1
                        bullet['dy'] *= -1
                    else:
                        bullets_to_remove.append(bullet)
                elif bullet['contact_effect'] == ContactEffect.PIERCE:
                    if 'hit_creatures' not in bullet:
                        bullet['hit_creatures'] = set()
                    bullet['hit_creatures'].add(id(collided_creature))
                    bullet['pierces_left'] -= 1
                    if bullet['pierces_left'] < 0:
                        bullets_to_remove.append(bullet)
                elif bullet['contact_effect'] == ContactEffect.EXPLODE:
                    splash_effects = handle_splash_damage(bullet, creatures, splash_effects, 32)
                    bullets_to_remove.append(bullet)
                else:
                    bullets_to_remove.append(bullet)
                continue

    # Remove bullets marked for removal
    for bullet in bullets_to_remove:
        if bullet in bullets:
            bullets.remove(bullet)
            
    return bullets, splash_effects