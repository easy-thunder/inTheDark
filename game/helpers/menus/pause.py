
import pygame
from typing import Protocol, Optional


from game.helpers.menus.skill_tree import make_skill_tree_subscreen
from game.helpers.menus.controls_menu import make_controls_subscreen
# from game.data.skill_nodes import NODES

class PauseSubscreen(Protocol):
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Return True when this subscreen wants to close."""
        ...
    def draw(self, screen: pygame.Surface, w: int, h: int) -> None:
        ...

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




def pause_loop(screen, SCREEN_WIDTH, SCREEN_HEIGHT, clock, overlay_text="",current_player=None):
    labels = ["Resume", "Skill Tree", "Controls", "Quit"]
    selected = 0
    rects = _button_rects(SCREEN_WIDTH, start_y=180, gap=14, count=len(labels))
    smoke = SmokeLayer(SCREEN_WIDTH, SCREEN_HEIGHT)

    # No loops inside subscreens. We'll hold one here when opened.
    active_subscreen: Optional[PauseSubscreen] = None

    while True:
        dt = clock.get_time() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if active_subscreen:
                # Let subscreen process input; if it returns True, close it
                if active_subscreen.handle_event(event):
                    active_subscreen = None
                continue

            # Root pause menu input
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
                        active_subscreen = make_skill_tree_subscreen(profile_id="default", player=current_player)

                    elif choice == "Controls":
                        active_subscreen = make_controls_subscreen()    

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
                            active_subscreen = make_skill_tree_subscreen(profile_id="default", player=current_player)
                            break
                        elif label == "Controls":
                            active_subscreen = make_controls_subscreen()
                            break

        # --- Draw order: frozen game frame is already on screen ---
        smoke.update_and_draw(screen, dt)
        _draw_dim_overlay(screen, SCREEN_WIDTH, SCREEN_HEIGHT, overlay_text)

        if active_subscreen:
            active_subscreen.draw(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
        else:
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
# --- Smoke layer (shared across all pause submenus) --------------------------
import random, math, pygame

class SmokeLayer:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.textures = self._make_smoke_textures()
        self.particles = []
        self.spawn_timer = 0.0
        self.spawn_interval = 0.35
        self.max_particles = 120

    def _radial_smoke_tex(self, radius: int, falloff=1.8) -> pygame.Surface:
        s = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        cx, cy = radius, radius
        for y in range(2*radius):
            dy = y - cy
            for x in range(2*radius):
                dx = x - cx
                d = math.hypot(dx, dy) / radius
                if d <= 1.0:
                    a = int(255 * max(0.0, (1.0 - d) ** falloff))
                    s.set_at((x, y), (255, 255, 255, a))
        return s.convert_alpha()

    def _make_smoke_textures(self):
        return [
            self._radial_smoke_tex(32),
            self._radial_smoke_tex(40),
            self._radial_smoke_tex(52),
        ]

    def _spawn_smoke(self, amount=3):
        for _ in range(amount):
            tex = random.choice(self.textures)
            edge = random.random()
            if edge < 0.65:
                x = random.uniform(0, self.w); y = self.h + random.uniform(10, 80)
                vx = random.uniform(-8, 8) * 0.02; vy = -random.uniform(10, 30) * 0.02
            elif edge < 0.825:
                x = -random.uniform(20, 80); y = random.uniform(self.h*0.2, self.h*0.9)
                vx = random.uniform(10, 30) * 0.02; vy = -random.uniform(5, 20) * 0.02
            else:
                x = self.w + random.uniform(20, 80); y = random.uniform(self.h*0.2, self.h*0.9)
                vx = -random.uniform(10, 30) * 0.02; vy = -random.uniform(5, 20) * 0.02
            scale = random.uniform(1.1, 1.8)
            alpha = random.randint(110, 170)
            life = random.uniform(7.0, 11.0)
            self.particles.append([x, y, vx, vy, scale, alpha, 0.0, life, tex])

    def update_and_draw(self, screen, dt):
        # spawn
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0.0
            if len(self.particles) < self.max_particles:
                self._spawn_smoke(amount=3)

        # update/draw
        alive = []
        for p in self.particles:
            # p: [x, y, vx, vy, scale, alpha, life, max_life, tex]
            p[6] += dt
            if p[6] >= p[7]:
                continue
            p[0] += p[2] * (dt * 60.0)
            p[1] += p[3] * (dt * 60.0)
            p[4] *= (1.0 + 0.02 * dt)

            t = p[6] / p[7]
            if t < 0.2: fade = t / 0.2
            elif t > 0.75: fade = max(0.0, 1.0 - (t - 0.75) / 0.25)
            else: fade = 1.0
            alpha = int(p[5] * fade)
            if alpha <= 0:
                continue

            tex = p[8]
            tw, th = tex.get_size()
            dw, dh = int(tw * p[4]), int(th * p[4])
            if dw > 2 and dh > 2:
                puff = pygame.transform.smoothscale(tex, (dw, dh))
                puff.set_alpha(alpha)
                screen.blit(puff, (p[0] - dw//2, p[1] - dh//2))

            if -120 <= p[0] <= self.w + 120 and -120 <= p[1] <= self.h + 120:
                alive.append(p)
        self.particles = alive
