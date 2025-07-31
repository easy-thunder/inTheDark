def reset_warm_up(players):
    """
    Reset warm-up state for all weapons of all players.
    
    Args:
        players: List of Player objects
    """
    for player in players:
        for weapon in player.character.weapons:
            if weapon.uncommon.warm_up_time:
                weapon.is_warming_up = False
                weapon.warm_up_start = None