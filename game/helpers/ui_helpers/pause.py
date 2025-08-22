import pygame

def pause_loop(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock, overlay_text="PAUSED"):
    dim = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 140))
    font = pygame.font.Font(None, 48)
    label = font.render(overlay_text, True, (255, 255, 255))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_p, pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    return "resume"

        screen.blit(dim, (0, 0))
        screen.blit(label, (SCREEN_WIDTH // 2 - label.get_width() // 2,
                            SCREEN_HEIGHT // 2 - label.get_height() // 2))
        pygame.display.flip()
        clock.tick(60)

def _shift_attr(obj, name, delta):
    if hasattr(obj, name):
        val = getattr(obj, name)
        if val is not None:
            setattr(obj, name, val + delta)

def shift_time_references(players, creatures, bullets, paused_ms):
    for p in players:
        for attr in ("last_xp_time", "last_regen_time", "time_of_death"):
            _shift_attr(p, attr, paused_ms)
        if hasattr(p.character, "weapons") and p.character.weapons:
            for w in p.character.weapons:
                for attr in ("reload_start", "warm_up_start"):
                    _shift_attr(w, attr, paused_ms)

    for c in creatures:
        for attr in ("last_cleave_time", "cleave_start_time", "hurt_time"):
            _shift_attr(c, attr, paused_ms)

    for b in bullets or []:
        for attr in ("spawn_time", "created_at", "last_update", "explode_at"):
            _shift_attr(b, attr, paused_ms)
