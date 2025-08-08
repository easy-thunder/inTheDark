import pygame

def update_players(players, dx1, dy1, dx2, dy2, visible_walls, camera_x, camera_y, player_weapon_indices, game_x, game_y):
    """Update all players including movement, XP, regen, aiming, and reloading."""
    all_dead = True
    
    for i, player in enumerate(players):
        if not player.dead:
            all_dead = False
        
        # Movement
        if i == 0:
            player.move(dx1, dy1, visible_walls)
        elif i == 1:
            player.move(dx2, dy2, visible_walls)
        
        # Updates
        player.update_xp()
        player.regen()
        player.update_aim(camera_x, camera_y, player_index=i, game_x=game_x, game_y=game_y)
        player.update_reload(player_weapon_indices[i])
    
    return all_dead

def handle_revival(players, clock):
    """Handle player revival mechanics."""
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

def apply_tether_mechanic(players, camera_x, camera_y, dx1, dy1, game_width, player_size):
    """Apply tether mechanic to restrict player movement."""
    if len(players) > 1:
        p2_screen_x = players[1].x - camera_x
        p2_screen_y = players[1].y - camera_y
        
        # If Player 2 is at the left edge and Player 1 tries to move right, block
        if p2_screen_x <= 0 and dx1 > 0:
            dx1 = 0
        # If Player 2 is at the right edge and Player 1 tries to move left, block
        if p2_screen_x >= game_width - player_size and dx1 < 0:
            dx1 = 0
        # If Player 2 is at the top edge and Player 1 tries to move down, block
        if p2_screen_y <= 0 and dy1 > 0:
            dy1 = 0
        # If Player 2 is at the bottom edge and Player 1 tries to move up, block
        if p2_screen_y >= game_width - player_size and dy1 < 0:
            dy1 = 0
    
    return dx1, dy1

def update_camera(players, game_width, game_height):
    """Update camera to follow player 1."""
    camera_x = players[0].x - game_width // 2
    camera_y = players[0].y - game_height // 2
    return camera_x, camera_y

def award_xp_shared(players, total_xp, alive_only=False):
    """Split total_xp evenly among players. If alive_only=True, only alive players share."""
    if alive_only:
        targets = [p for p in players if not p.dead]
    else:
        targets = players

    if not targets or total_xp <= 0:
        return

    # Integer-safe split with remainder distribution
    share = total_xp // len(targets)
    remainder = total_xp % len(targets)

    for i, p in enumerate(targets):
        p.gain_xp(share + (1 if i < remainder else 0))


def cleanup_dead_creatures(creatures, players):
    """
    Award XP for dead creatures and remove them from the list.
    Returns number of creatures removed (optional).
    """
    removed = 0
    i = 0
    while i < len(creatures):
        c = creatures[i]
        if c.hp <= 0:
            # Award XP once
            if not getattr(c, "xp_awarded", False):
                xp = getattr(c, "xp_value", 0)
                award_xp_shared(players, xp, alive_only=False)  # flip to False if you want everyone to share
                c.xp_awarded = True

            # Remove creature
            creatures.pop(i)
            removed += 1
            continue
        i += 1
    return removed
