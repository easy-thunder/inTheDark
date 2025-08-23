# game/menus/skill_tree_menu.py
import pygame
from collections import defaultdict
from game.player import Player
# Persistence helpers (catalog + save/load)
from game.storage.skill_tree_store import (
    build_merged_nodes,        # -> (nodes_with_owned_and_levels, state_dict)
    update_progress_from_nodes,
    save_player_state,
)

# -----------------------
# Layout & style knobs
# -----------------------
NODE_RADIUS = 26
H_SPACING   = 170   # horizontal gap between nodes in a tier
V_SPACING   = 130   # vertical gap between tiers (rows)
PADDING_LR  = 120
PADDING_TB  = 120

COLOR_BG_LOCKED    = (28, 28, 28)
COLOR_BG_AVAILABLE = (55, 55, 55)
COLOR_BG_OWNED     = (240, 240, 240)
COLOR_RING_LOCKED  = (80, 80, 80)
COLOR_RING_AVAIL   = (170, 170, 100)
COLOR_RING_OWNED   = (255, 255, 255)
COLOR_EDGE_LOCKED  = (70, 70, 70)
COLOR_EDGE_AVAIL   = (160, 140, 80)
COLOR_TEXT         = (240, 240, 240)


class SkillTreeSubscreen:
    """
    Deterministic, data-driven skill tree with persistence.
      - Panning: hold LMB and drag
      - Invest: click an available node (increments level up to max)
      - Tooltip: hover a node
      - Close: Esc / Backspace / P
    """
    def __init__(self, profile_id: str, title: str = "Skill Tree", player=None):
        # Merge design-time catalog with player progress (owned/node_level)
        self.player = player  # <-- keep a reference to the Player
        self.profile_id = profile_id
        self.nodes, self._state = build_merged_nodes(profile_id)
        self.by_id = {n["id"]: n for n in self.nodes}

        self.title      = title
        self.font_title = pygame.font.Font(None, 48)
        self.font       = pygame.font.Font(None, 28)
        self.small      = pygame.font.Font(None, 22)

        # Compute availability for all nodes
        self._refresh_availability()

        # Layout positions (by node_order)
        self.pos = {}  # node_id -> (x, y)
        info = pygame.display.Info()
        width, height = info.current_w, info.current_h

        self._layout(screen_w=width, screen_h=height)

        # Panning
        self.pan         = [0, 0]
        self._dragging   = False
        self._drag_anchor = (0, 0)
        self._pan_anchor  = (0, 0)

        # Hover
        self._hover_id = None

    # -------------------
    # Graph helpers
    # -------------------
    def _refresh_availability(self):
        """
        Node is available if all its node_requirements are OWNED.
        NOTE: If you prefer 'requirements must be maxed', change the check below.
        """
        for n in self.nodes:
            if n.get("owned"):
                n["available"] = True
                continue
            reqs = n.get("node_requirements", []) or []
            ok = True
            for rid in reqs:
                r = self.by_id.get(rid)
                if not r:
                    continue
                # 'owned' threshold — swap to (r["node_level"] >= r["max_level"]) if you prefer
                if not r.get("owned", False):
                    ok = False
                    break
            n["available"] = ok


    def _tiers(self):
        """
        Group nodes by node_order (tier). We still return them in ascending
        node_order, but _layout() will place tier 0 at the BOTTOM.
        """
        tiers = defaultdict(list)
        for n in self.nodes:
            tiers[int(n.get("node_order", 0))].append(n)
        ordered_keys = sorted(tiers.keys())  # 0,1,2,...
        return [tiers[k] for k in ordered_keys]  # bottom tier is index 0

    def _layout(self, screen_w=None, screen_h=None):
        """
        Bottom-up layered layout:
        - Root tier (node_order==0) anchored at the CENTER BOTTOM of the screen.
        - Higher tiers stacked upward.
        - Nodes within a tier horizontally centered.
        - Optional barycenter ordering to reduce crossings.
        """
        tiers = self._tiers()
        num_tiers = len(tiers)
        if num_tiers == 0:
            return

        # If no screen size passed, assume 1920x1080-ish safe area
        screen_w = screen_w 
        screen_h = screen_h 

        center_x = screen_w // 2
        bottom_y = screen_h - PADDING_TB  # leave some padding at bottom

        tier_y = {}
        for idx in range(num_tiers):
            # bottom row -> bottom_y, then move upward
            y = bottom_y - idx * V_SPACING
            tier_y[idx] = y

        self.pos.clear()

        def _place_row(sorted_nodes, y):
            total_w = max(0, (len(sorted_nodes) - 1) * H_SPACING)
            x0 = center_x - total_w // 2  # center horizontally
            x = x0
            for n in sorted_nodes:
                self.pos[n["id"]] = (x, y)
                x += H_SPACING

        # Bottom row
        bottom_nodes = sorted(tiers[0], key=lambda n: (n.get("end_node", False), n["id"]))
        _place_row(bottom_nodes, tier_y[0])

        # Higher rows: order by barycenter
        for t in range(1, num_tiers):
            row = tiers[t]

            def _barycenter(n):
                reqs = n.get("node_requirements", []) or []
                xs = [self.pos[r][0] for r in reqs if r in self.pos]
                return sum(xs) / len(xs) if xs else float(hash(n["id"]) & 0xFFFFFFFF)

            row_sorted = sorted(row, key=lambda n: (_barycenter(n), n.get("end_node", False), n["id"]))
            _place_row(row_sorted, tier_y[t])


    def _draw_edges(self, screen):
        """
        Draw orthogonal (elbow) edges to improve readability and perceived crossings.
        """
        for n in self.nodes:
            dst_id = n["id"]
            x1, y1 = self.pos[dst_id]
            color = COLOR_EDGE_AVAIL if n.get("available") else COLOR_EDGE_LOCKED
            for src_id in n.get("node_requirements", []) or []:
                if src_id not in self.pos:
                    continue
                x0, y0 = self.pos[src_id]

                # elbow at the vertical midpoint between source and destination
                mid_y = (y0 + y1) // 2

                # three segments: up from parent, across, then up to child
                pygame.draw.line(screen, color,
                                (x0 + self.pan[0], y0 + self.pan[1]),
                                (x0 + self.pan[0], mid_y + self.pan[1]), 3)
                pygame.draw.line(screen, color,
                                (x0 + self.pan[0], mid_y + self.pan[1]),
                                (x1 + self.pan[0], mid_y + self.pan[1]), 3)
                pygame.draw.line(screen, color,
                                (x1 + self.pan[0], mid_y + self.pan[1]),
                                (x1 + self.pan[0], y1 + self.pan[1]), 3)
    # -------------------
    # Input handling
    # -------------------
    def _node_at(self, mx, my):
        """Return node id under mouse (accounting for pan)."""
        wx, wy = mx - self.pan[0], my - self.pan[1]
        for nid, (x, y) in self.pos.items():
            dx, dy = wx - x, wy - y
            if dx * dx + dy * dy <= NODE_RADIUS * NODE_RADIUS:
                return nid
        return None

    def _invest_in_node(self, nid: str, player=None):
        """
        Increase node_level by 1 (up to max_level) if:
          - node is available,
          - player has node_points (if a player is provided).
        """
        n = self.by_id[nid]
        if not n.get("available", False):
            return
        cur = int(n.get("node_level", 0))
        mx  = int(n.get("max_level", 1))
        if cur >= mx:
            return

        # Require an unspent point if we have a player
        if player is not None:
            if not getattr(player, "spend_node_point", None) or not player.spend_node_point():
                return  # not enough points, or no method

        n["node_level"] = cur + 1
        n["owned"] = n["node_level"] > 0

        self._refresh_availability()
        update_progress_from_nodes(self._state, self.nodes)  # if you're persisting
        save_player_state(self.profile_id, self._state)      # if you're persisting

    def handle_event(self, event):
        # Close keys
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE, pygame.K_p):
                return True  # close

        # Panning start
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._dragging = True
            self._drag_anchor = event.pos
            self._pan_anchor  = tuple(self.pan)

        # Panning end (and click-to-invest if it was a click, not a drag)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self._dragging:
                # If minimal movement, treat this as a click to invest
                dx = event.pos[0] - self._drag_anchor[0]
                dy = event.pos[1] - self._drag_anchor[1]
                if abs(dx) < 6 and abs(dy) < 6:
                    nid = self._node_at(*event.pos)
                    if nid:
                        self._invest_in_node(nid, player=self.player)  # <-- pass player
            self._dragging = False

        # Panning motion
        elif event.type == pygame.MOUSEMOTION and self._dragging:
            dx = event.pos[0] - self._drag_anchor[0]
            dy = event.pos[1] - self._drag_anchor[1]
            self.pan[0] = self._pan_anchor[0] + dx
            self.pan[1] = self._pan_anchor[1] + dy

        # Hover update
        if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
            mx, my = pygame.mouse.get_pos()
            self._hover_id = self._node_at(mx, my)

        return False  # keep open

    # -------------------
    # Drawing
    # -------------------


    def _draw_nodes(self, screen):
        for n in self.nodes:
            x, y = self.pos[n["id"]]
            owned = n.get("owned", False)
            avail = n.get("available", False)

            bg   = COLOR_BG_OWNED if owned else (COLOR_BG_AVAILABLE if avail else COLOR_BG_LOCKED)
            ring = COLOR_RING_OWNED if owned else (COLOR_RING_AVAIL if avail else COLOR_RING_LOCKED)

            # Node circle + ring
            pygame.draw.circle(screen, bg, (x + self.pan[0], y + self.pan[1]), NODE_RADIUS)
            pygame.draw.circle(screen, ring, (x + self.pan[0], y + self.pan[1]), NODE_RADIUS, 3)

            # Name
            name_color = COLOR_TEXT if (owned or avail) else (150, 150, 150)
            name_surf = self.small.render(n["name"], True, name_color)
            screen.blit(name_surf, (x + self.pan[0] - name_surf.get_width() // 2,
                                    y + self.pan[1] + NODE_RADIUS + 6))

            # Level text
            cur = int(n.get("node_level", 0))
            mxl = int(n.get("max_level", 1))
            lvl_surf = self.small.render(f"{cur}/{mxl}", True, (200, 200, 200))
            screen.blit(lvl_surf, (x + self.pan[0] - lvl_surf.get_width() // 2,
                                   y + self.pan[1] - 10))

    def _draw_tooltip(self, screen, mx, my):
        nid = self._hover_id
        if not nid:
            return
        n = self.by_id[nid]
        skills = n.get("associated_skills", []) or []
        cur = int(n.get("node_level", 0))
        mxl = int(n.get("max_level", 1))

        lines = [n["name"], f"Level: {cur}/{mxl}"]
        if skills:
            lines.append("—")
            lines.extend(skills)

        padding = 10
        texts = [self.font.render(line, True, (255, 255, 255)) for line in lines]
        w = max(t.get_width() for t in texts) + padding * 2
        h = sum(t.get_height() for t in texts) + padding * 2 + (len(texts) - 1) * 4

        box = pygame.Rect(mx + 18, my + 18, w, h)
        pygame.draw.rect(screen, (20, 20, 20), box, border_radius=8)
        pygame.draw.rect(screen, (200, 200, 200), box, 2, border_radius=8)

        y = box.y + padding
        for t in texts:
            screen.blit(t, (box.x + padding, y))
            y += t.get_height() + 4

    def draw(self, screen, w, h):
        # Title
        title = self.font_title.render(self.title, True, (255, 255, 255))
        screen.blit(title, (w // 2 - title.get_width() // 2, 60))

        # Graph
        self._draw_edges(screen)
        self._draw_nodes(screen)

        # Tooltip
        mx, my = pygame.mouse.get_pos()
        self._draw_tooltip(screen, mx, my)

        # Footer
        hint = self.small.render("Click to invest • Drag to pan • Esc/Backspace to return", True, (210, 210, 210))
        screen.blit(hint, (w // 2 - hint.get_width() // 2, h - 42))


# ------------------------------------------------------------
# Wrapper helpers: create a subscreen or run an in-place loop
# ------------------------------------------------------------
def make_skill_tree_subscreen(profile_id: str, title: str = "Skill Tree") -> SkillTreeSubscreen:
    """Return a subscreen instance (useful if your pause menu manages the loop)."""
    return SkillTreeSubscreen(profile_id, title)


def show_skill_tree(screen, w, h, clock, skill_tree=None, active_skills=None, current_player=None):
    subscreen = SkillTreeSubscreen(
        nodes_data=skill_tree or [],
        owned_ids=set(),           # or what you track
        title="Skill Tree",
        player=current_player      # <--- pass it through
    )

    running = True
    while running:
        for event in pygame.event.get():
            if subscreen.handle_event(event):  # returns True to close
                running = False
                break

        screen.fill((0, 0, 0))
        subscreen.draw(screen, w, h)
        pygame.display.flip()
        clock.tick(60)