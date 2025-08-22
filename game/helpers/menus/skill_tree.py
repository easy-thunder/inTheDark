# game/menus/skill_tree_menu.py
import pygame

_DEFAULT_SKILL_TREE = {
    1: ["Vitality", "Ballistics", "Pyromancy"],
    2: ["Heavy Armor", "Pierce Shot", "Fire Bloom"],
    3: ["Juggernaut", "Splinter Rounds", "Inferno"],
}

class SkillTreeSubscreen:
    def __init__(self, skill_tree=None, active_skills=None, title="Skill Tree"):
        self.skill_tree = skill_tree or _DEFAULT_SKILL_TREE
        self.active = set(active_skills or [])
        self.title = title
        self.scroll = 0
        self.line_h = 40

        self.font_title = pygame.font.Font(None, 48)
        self.font = pygame.font.Font(None, 32)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_p):
                return True  # close subscreen
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.scroll = max(0, self.scroll - self.line_h)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.scroll = min(10000, self.scroll + self.line_h)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:   # wheel up
                self.scroll = max(0, self.scroll - self.line_h)
            elif event.button == 5: # wheel down
                self.scroll = min(10000, self.scroll + self.line_h)
        return False

    def draw(self, screen: pygame.Surface, w: int, h: int) -> None:
        # We’re already dimmed/smoked by pause_loop; just draw content
        y = 120 - self.scroll
        lane_x = 100
        lane_w = w - 200

        title = self.font_title.render(self.title, True, (255, 255, 255))
        screen.blit(title, (w//2 - title.get_width()//2, 70))

        for tier in sorted(self.skill_tree.keys()):
            tlabel = self.font_title.render(f"Tier {tier}", True, (255, 255, 255))
            screen.blit(tlabel, (lane_x, y)); y += tlabel.get_height() + 8
            for node in self.skill_tree[tier]:
                box = pygame.Rect(lane_x, y, lane_w, 32)
                pygame.draw.rect(screen, (30, 30, 30), box, border_radius=8)
                pygame.draw.rect(screen, (200, 200, 200), box, width=2, border_radius=8)
                label = self.font.render(node, True, (255, 255, 255))
                screen.blit(label, (box.x + 10, box.y + 6))
                y += 40
            y += 12

        hint = self.font.render("Esc / Backspace to return", True, (220, 220, 220))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 48))

def make_skill_tree_subscreen(skill_tree=None, active_skills=None):
    return SkillTreeSubscreen(skill_tree, active_skills)
