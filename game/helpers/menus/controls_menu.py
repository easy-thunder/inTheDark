# game/menus/controls_menu.py
import pygame

class ControlsSubscreen:
    def __init__(self, title="Keyboard Controls"):
        self.title = title
        self.font_title = pygame.font.Font(None, 56)
        self.font = pygame.font.Font(None, 36)
        self.controls = [
            ("WASD", "Move Player 1"),
            ("Arrow Keys", "Move Player 2"),
            ("Space / Left Mouse", "Fire"),
            ("F", "Activate Ability"),
            ("R", "Reload Weapon"),
            ("1–6", "Switch Weapon / Ability"),
            ("Caps Lock", "Toggle Weapon/Ability Mode"),
            ("H", "Toggle Creature HP Bars"),
            ("P", "Pause Menu"),
        ]

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_p):
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            return True
        return False

    def draw(self, screen: pygame.Surface, w: int, h: int) -> None:
        title_surf = self.font_title.render(self.title, True, (255, 255, 255))
        screen.blit(title_surf, (w // 2 - title_surf.get_width() // 2, 70))

        y = 150
        for key, desc in self.controls:
            text = f"{key} – {desc}"
            label = self.font.render(text, True, (230, 230, 230))
            screen.blit(label, (100, y))
            y += 45

        hint = self.font.render("Esc / Backspace / Right-click to return", True, (200, 200, 200))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 60))

def make_controls_subscreen():
    return ControlsSubscreen()
