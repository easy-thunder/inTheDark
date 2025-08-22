
import pygame

def show_controls(screen, width, height, clock, title="Keyboard Controls"):
    """
    Displays a simple static list of keyboard controls.
    Esc / Backspace / P / Right-click closes it.
    """
    font_title = pygame.font.Font(None, 56)
    font = pygame.font.Font(None, 36)

    controls = [
        ("WASD", "Move Player 1"),
        ("Arrow Keys", "Move Player 2"),
        ("Space / Left Mouse", "Fire"),
        ("F", "Activate Ability"),
        ("R", "Reload Weapon"),
        ("1–6", "Switch Weapon / Ability"),
        ("Caps Lock", "Toggle Weapon/Ability Mode"),
        ("H", "Toggle Creature HP Bars"),
        ("P / Esc", "Pause Menu"),
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_p):
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  
                    return

        
        dim = pygame.Surface((width, height), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        screen.blit(dim, (0, 0))

        
        title_surf = font_title.render(title, True, (255, 255, 255))
        screen.blit(title_surf, (width // 2 - title_surf.get_width() // 2, 60))

        
        y = 150
        for key, desc in controls:
            text = f"{key} – {desc}"
            label = font.render(text, True, (230, 230, 230))
            screen.blit(label, (100, y))
            y += 45

        
        hint = font.render("Esc / Backspace / Right-click to return", True, (200, 200, 200))
        screen.blit(hint, (width // 2 - hint.get_width() // 2, height - 60))

        pygame.display.flip()
        clock.tick(60)
