import pygame

def handle_events(players, player_weapon_indices, show_creature_hp):
    """
    Handle all pygame events.
    
    Returns:
        Tuple of (running, show_creature_hp, player_weapon_indices)
    """
    running = True
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # --- Weapon switching ---
            elif event.key == pygame.K_1:
                if len(players[0].character.weapons) > 0:
                    # Cancel reload on current weapon
                    current_index = player_weapon_indices[0]
                    current_weapon = players[0].character.weapons[current_index]
                    current_weapon.is_reloading = False
                    if hasattr(current_weapon, 'reload_start'):
                        current_weapon.reload_start = None
                    player_weapon_indices[0] = 0
            elif event.key == pygame.K_2:
                if len(players[0].character.weapons) > 1:
                    current_index = player_weapon_indices[0]
                    current_weapon = players[0].character.weapons[current_index]
                    current_weapon.is_reloading = False
                    if hasattr(current_weapon, 'reload_start'):
                        current_weapon.reload_start = None
                    player_weapon_indices[0] = 1
            elif event.key == pygame.K_3:
                if len(players[0].character.weapons) > 2:
                    current_index = player_weapon_indices[0]
                    current_weapon = players[0].character.weapons[current_index]
                    current_weapon.is_reloading = False
                    if hasattr(current_weapon, 'reload_start'):
                        current_weapon.reload_start = None
                    player_weapon_indices[0] = 2
            elif event.key == pygame.K_4:
                if len(players[0].character.weapons) > 3:
                    current_index = player_weapon_indices[0]
                    current_weapon = players[0].character.weapons[current_index]
                    current_weapon.is_reloading = False
                    if hasattr(current_weapon, 'reload_start'):
                        current_weapon.reload_start = None
                    player_weapon_indices[0] = 3
            elif event.key == pygame.K_5:
                if len(players[0].character.weapons) > 4:
                    current_index = player_weapon_indices[0]
                    current_weapon = players[0].character.weapons[current_index]
                    current_weapon.is_reloading = False
                    if hasattr(current_weapon, 'reload_start'):
                        current_weapon.reload_start = None
                    player_weapon_indices[0] = 4
            elif event.key == pygame.K_6:
                if len(players[0].character.weapons) > 5:
                    current_index = player_weapon_indices[0]
                    current_weapon = players[0].character.weapons[current_index]
                    current_weapon.is_reloading = False
                    if hasattr(current_weapon, 'reload_start'):
                        current_weapon.reload_start = None
                    player_weapon_indices[0] = 5
            # --- Toggle creature HP bars ---
            elif event.key == pygame.K_h:
                show_creature_hp = not show_creature_hp
            # --- Reloading ---
            elif event.key == pygame.K_r:
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
                        if weapon.uncommon.warm_up_time:
                            weapon.is_warming_up = False
                            weapon.warm_up_start = None
    
    return running, show_creature_hp, player_weapon_indices

def get_player_movement(players):
    """
    Get movement input for all players.
    
    Returns:
        Tuple of (dx1, dy1, dx2, dy2) for player movement
    """
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
    
    return dx1, dy1, dx2, dy2

def is_fire_pressed():
    """Check if any fire button is pressed."""
    keys = pygame.key.get_pressed()
    return keys[pygame.K_SPACE] or pygame.mouse.get_pressed()[0] 