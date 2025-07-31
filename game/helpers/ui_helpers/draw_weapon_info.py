import pygame


def draw_weapon_info(screen, weapon, x, y):
    """Draw weapon information on the screen."""
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
