
import pygame


from game.helpers.menus.skill_tree import show_skill_tree
from game.helpers.menus.controls_menu import show_controls



def _draw_dim_overlay(screen, w, h, title=None):
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 160))
    screen.blit(dim, (0, 0))
    if title:
        font = pygame.font.Font(None, 56)
        label = font.render(title, True, (255, 255, 255))
        screen.blit(label, (w // 2 - label.get_width() // 2, 60))

def _button_rects(w, start_y, gap, count, btn_w=None, btn_h=56):
    btn_w = btn_w or min(420, int(w * 0.6))
    x = (w - btn_w) // 2
    rects = []
    y = start_y
    for _ in range(count):
        rects.append(pygame.Rect(x, y, btn_w, btn_h))
        y += btn_h + gap
    return rects

def _draw_buttons(screen, rects, labels, selected_idx):
    font = pygame.font.Font(None, 44)
    for i, (r, text) in enumerate(zip(rects, labels)):
        is_sel = (i == selected_idx)
        bg = (35, 35, 35) if is_sel else (22, 22, 22)
        border = (240, 240, 240) if is_sel else (160, 160, 160)
        pygame.draw.rect(screen, bg, r, border_radius=10)
        pygame.draw.rect(screen, border, r, width=2, border_radius=10)
        label = font.render(text, True, (255, 255, 255))
        screen.blit(label, (r.centerx - label.get_width() // 2,
                            r.centery - label.get_height() // 2))


_DEFAULT_SKILL_TREE = {
    1: ["Vitality", "Ballistics", "Pyromancy"],
    2: ["Heavy Armor", "Pierce Shot", "Fire Bloom"],
    3: ["Juggernaut", "Splinter Rounds", "Inferno"],
}

def pause_loop(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock, overlay_text="Paused"):
    labels = ["Resume", "Skill Tree", "Controls", "Quit"]
    selected = 0
    rects = _button_rects(SCREEN_WIDTH, start_y=180, gap=14, count=len(labels))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    return "resume"
                elif event.key in (pygame.K_UP, pygame.K_w):
                    selected = (selected - 1) % len(labels)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    selected = (selected + 1) % len(labels)
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    choice = labels[selected]
                    if choice == "Resume":
                        return "resume"
                    elif choice == "Quit":
                        return "quit"
                    elif choice == "Skill Tree":
                        show_skill_tree(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock,
                                        skill_tree=_DEFAULT_SKILL_TREE,
                                        active_skills=[])
                    elif label == "Controls":
                        show_controls(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock)

                        
            elif event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, r in enumerate(rects):
                    if r.collidepoint(mx, my):
                        selected = i
                        break
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for i, (r, label) in enumerate(zip(rects, labels)):
                    if r.collidepoint(mx, my):
                        if label == "Resume":
                            return "resume"
                        elif label == "Quit":
                            return "quit"
                        elif label == "Skill Tree":  
                            show_skill_tree(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock,
                                            skill_tree=_DEFAULT_SKILL_TREE,
                                            active_skills=[])
                            break  
                                                
                        elif label == "Controls":
                            show_controls(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock)

        _draw_dim_overlay(screen, SCREEN_WIDTH, SCREEN_HEIGHT, overlay_text)
        _draw_buttons(screen, rects, labels, selected)
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
