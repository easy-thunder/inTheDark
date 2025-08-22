# game/menus/skill_tree_menu.py
import pygame
from typing import Dict, List, Iterable, Optional

"""
Skill Tree Menu (view-only)
---------------------------
Call show_skill_tree(screen, w, h, clock, skill_tree, active_skills)

- skill_tree: dict[int, list[str]]
  Example:
    {
      1: ["Vitality", "Ballistics", "Pyromancy"],
      2: ["Heavy Armor", "Pierce Shot", "Fire Bloom"],
      3: ["Juggernaut", "Splinter Rounds", "Inferno"],
    }

- active_skills: iterable of str (skills the player has already picked)
  These will be rendered as "active" (highlight outline).
"""

# ---------- Drawing helpers ----------

def _draw_dim_overlay(screen, w, h, title=None):
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 170))
    screen.blit(dim, (0, 0))
    if title:
        font = pygame.font.Font(None, 56)
        label = font.render(title, True, (255, 255, 255))
        screen.blit(label, (w // 2 - label.get_width() // 2, 60))

def _draw_skill_box(screen, rect: pygame.Rect, text: str, *, active: bool):
    bg = (28, 28, 30)
    border = (210, 210, 210)
    active_border = (255, 215, 0)  # gold

    pygame.draw.rect(screen, bg, rect, border_radius=10)
    pygame.draw.rect(screen, active_border if active else border, rect, width=2, border_radius=10)

    font = pygame.font.Font(None, 32)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, (rect.x + 10, rect.y + (rect.height - label.get_height()) // 2))

# ---------- Public API ----------

def show_skill_tree(
    screen: pygame.Surface,
    width: int,
    height: int,
    clock: pygame.time.Clock,
    skill_tree: Dict[int, List[str]],
    active_skills: Optional[Iterable[str]] = None,
    title: str = "Skill Tree"
) -> None:
    """
    Blocks until the user exits (Esc / Backspace / P / Right-click).
    Renders tiers vertically; each tier lists its nodes in rows.
    """
    active_set = set(active_skills or [])

    # Layout
    lane_x = 100
    lane_w = width - 200
    box_h = 34
    box_gap = 8
    tier_gap = 18
    top_margin = 130
    bottom_hint_margin = 50

    # Scroll
    scroll_y = 0
    scroll_step = 40
    max_scroll = 0  # computed each frame

    font_hint = pygame.font.Font(None, 28)

    # Precompute positions each frame (cheap) based on scroll.
    def draw_content() -> None:
        nonlocal max_scroll
        y = top_margin - scroll_y
        # Compute content height to clamp scroll
        content_height = 0
        for tier in sorted(skill_tree.keys()):
            # Tier header height
            # (We render it each frame; measurement is approximated)
            tier_title = pygame.font.Font(None, 44).render(f"Tier {tier}", True, (255, 255, 255))
            content_height += tier_title.get_height() + 8
            # Boxes in this tier
            if skill_tree[tier]:
                content_height += len(skill_tree[tier]) * (box_h + box_gap) - box_gap
            content_height += tier_gap  # space between tiers

        # Max scroll so the bottom is reachable but not overscrolled
        max_scroll = max(0, content_height - (height - top_margin - bottom_hint_margin))

        # Actual drawing
        y = top_margin - scroll_y
        for tier in sorted(skill_tree.keys()):
            # Title
            title_surf = pygame.font.Font(None, 44).render(f"Tier {tier}", True, (255, 255, 255))
            screen.blit(title_surf, (lane_x, y))
            y += title_surf.get_height() + 8

            # Nodes
            for node in skill_tree[tier]:
                rect = pygame.Rect(lane_x, y, lane_w, box_h)
                _draw_skill_box(screen, rect, node, active=(node in active_set))
                y += box_h + box_gap

            y += tier_gap

    # Main loop for the menu
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Bubble back to caller; they decide whether to quit game
                return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_p):
                    return
                elif event.key in (pygame.K_UP, pygame.K_w):
                    scroll_y = max(0, scroll_y - scroll_step)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    scroll_y = min(max_scroll, scroll_y + scroll_step)
                elif event.key in (pygame.K_PAGEUP,):
                    scroll_y = max(0, scroll_y - scroll_step * 4)
                elif event.key in (pygame.K_PAGEDOWN,):
                    scroll_y = min(max_scroll, scroll_y + scroll_step * 4)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:  # right-click to exit
                    return
                elif event.button == 4:  # wheel up
                    scroll_y = max(0, scroll_y - scroll_step)
                elif event.button == 5:  # wheel down
                    scroll_y = min(max_scroll, scroll_y + scroll_step)

        _draw_dim_overlay(screen, width, height, title)
        draw_content()

        # Footer hint
        hint = font_hint.render("Esc / Backspace / Right-click to return • ↑/↓ scroll", True, (220, 220, 220))
        screen.blit(hint, (width // 2 - hint.get_width() // 2, height - bottom_hint_margin))

        pygame.display.flip()
        clock.tick(60)
