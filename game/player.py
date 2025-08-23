import pygame
import math

class Player:
    def __init__(self, x, y, character, tile_size):
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, tile_size, tile_size)
        self.character = character
        self.hp = character.max_hp
        self.speed = character.speed
        # XP/Level system
        self.xp = 0
        self.level = 1
        self.xp_to_next = 100
        self.last_xp_time = pygame.time.get_ticks()

        self.node_points = 0          # unspent node points
        self.spent_node_points = 0    # optional: useful for UI/stats
        # Ability points
        self.ability_points = character.ability_points
        # Armor and regen
        self.armor = character.armor
        self.hp_regen = character.hp_regen
        self.ap_regen = character.ap_regen
        self.last_regen_time = pygame.time.get_ticks()
        # Death and revival
        self.dead = False
        self.time_of_death = None
        self.revive_progress = 0  # seconds standing over
        # Aiming
        self.aim_direction = (1, 0)  # Default aim right
        # In the future, add input_profile/controller here
    
    def take_damage(self, amount):
        if self.dead:
            return
        dealt_damage = max(0, amount - self.armor)
        self.hp -= dealt_damage
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.time_of_death = pygame.time.get_ticks()
            self.revive_progress = 0


    def move(self, dx, dy, walls):
        if self.dead:
            return
        self.x = self.rect.x
        self.y = self.rect.y
        if dx != 0:
            self.rect.x += dx
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dx > 0:
                        self.rect.right = wall.left
                    if dx < 0:
                        self.rect.left = wall.right
        if dy != 0:
            self.rect.y += dy
            for wall in walls:
                if self.rect.colliderect(wall):
                    if dy > 0:
                        self.rect.bottom = wall.top
                    if dy < 0:
                        self.rect.top = wall.bottom
        self.x = self.rect.x
        self.y = self.rect.y
    
    def gain_xp(self, amount):
        if self.dead:
            return
        self.xp += amount
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self.level += 1
            self.node_points += 1      # <<< NEW: award a node point
            self.xp_to_next += 100
    
    def update_xp(self):
        if self.dead:
            return
        now = pygame.time.get_ticks()
        if now - self.last_xp_time >= 10000:  # 10 seconds
            self.gain_xp(1)
            self.last_xp_time = now


    def can_spend_node_point(self) -> bool:
        return self.node_points > 0

    def spend_node_point(self) -> bool:
        """Spend one point if available; returns True on success."""
        if self.node_points > 0:
            self.node_points -= 1
            self.spent_node_points += 1
            return True
        return False

    def refund_node_point(self, n: int = 1):
        """Optional: if you add respecs later."""
        self.node_points += n
        self.spent_node_points = max(0, self.spent_node_points - n)
    
    def regen(self):
        if self.dead:
            return
        now = pygame.time.get_ticks()
        if now - self.last_regen_time >= 1000:  # 1 second
            # HP regen
            if self.hp < self.character.max_hp:
                self.hp = min(self.character.max_hp, self.hp + self.hp_regen)
            # AP regen
            if self.ability_points < self.character.ability_points:
                self.ability_points = min(self.character.ability_points, self.ability_points + self.ap_regen)
            self.last_regen_time = now
    
    def try_revive(self):
        self.dead = False
        self.hp = max(1, int(math.ceil(self.character.max_hp / 2)))
        self.ability_points = self.character.ability_points
        self.time_of_death = None
        self.revive_progress = 0
    
    def update_aim(self, camera_x, camera_y, player_index=0, game_x=0, game_y=0):
        if self.dead:
            return
        # For now, only Player 1 uses mouse aiming
        if player_index == 0:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # Player center in screen coordinates
            center_x = self.rect.x - camera_x + game_x + self.rect.width // 2
            center_y = self.rect.y - camera_y + game_y + self.rect.height // 2
            dx = mouse_x - center_x
            dy = mouse_y - center_y
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.aim_direction = (dx / dist, dy / dist)
            else:
                self.aim_direction = (1, 0)
        # For future: add controller stick aiming for other players
    
    def has_infinite_ammo(self, weapon):
        if not weapon or not hasattr(self.character, 'specializations') or not weapon.common.specialization_type:
            return False
        return self.character.specializations.get(weapon.common.specialization_type, 0) >= weapon.common.specialization_level

    def reload_weapon(self, weapon_index=0):
        weapon = self.character.weapons[weapon_index] if hasattr(self.character, 'weapons') and self.character.weapons else None
        if weapon and not weapon.is_reloading and weapon.current_clip < weapon.common.clip_size:
            weapon.is_reloading = True
            weapon.reload_start = pygame.time.get_ticks()

    def update_reload(self, weapon_index=0):
        weapon = self.character.weapons[weapon_index] if hasattr(self.character, 'weapons') and self.character.weapons else None
        if weapon and weapon.is_reloading:
            now = pygame.time.get_ticks()
            if now - weapon.reload_start >= weapon.common.reload_speed * 1000:
                # Calculate how many bullets to reload
                if self.has_infinite_ammo(weapon):
                    reload_amount = weapon.common.clip_size
                elif weapon.common.ammo is None:
                    reload_amount = weapon.common.clip_size
                else:
                    reload_amount = min(weapon.common.clip_size, weapon.common.ammo)
                weapon.current_clip = reload_amount
                # Only decrement reserve if not infinite
                if not self.has_infinite_ammo(weapon) and weapon.common.ammo is not None:
                    weapon.common.ammo -= reload_amount
                weapon.is_reloading = False

    def draw(self, surface, camera_x, camera_y, player_index=0, current_weapon_index=0, game_x=0, game_y=0):
        draw_rect = self.rect.move(-camera_x + game_x, -camera_y + game_y)
        if self.dead:
            pygame.draw.rect(surface, (80, 80, 80), draw_rect)
        else:
            pygame.draw.rect(surface, (255, 0, 0), draw_rect)  # RED
        
        # --- Health Bar ---
        bar_width = draw_rect.width
        bar_height = 1  # Extremely thin
        bar_x = draw_rect.x
        bar_y = draw_rect.y - 10  # Slightly higher to make room for ability bar
        s = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        s.fill((100, 0, 0, 120))  # dark red, semi-transparent
        surface.blit(s, (bar_x, bar_y))
        if self.hp > 0:
            fill_width = int(bar_width * (self.hp / self.character.max_hp))
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            pygame.draw.rect(surface, (255, 0, 0), fill_rect)
        
        # --- Ability Points Bar ---
        ab_bar_y = bar_y + bar_height + 2  # 2px below health bar
        s2 = pygame.Surface((bar_width, bar_height), pygame.SRCALPHA)
        s2.fill((0, 0, 100, 120))  # dark blue, semi-transparent
        surface.blit(s2, (bar_x, ab_bar_y))
        if self.ability_points > 0:
            ab_fill_width = int(bar_width * (self.ability_points / self.character.ability_points))
            ab_fill_rect = pygame.Rect(bar_x, ab_bar_y, ab_fill_width, bar_height)
            pygame.draw.rect(surface, (0, 120, 255), ab_fill_rect)
        
        # --- Revival Progress Bar ---
        if self.dead and self.revive_progress > 0:
            revive_bar_y = ab_bar_y + bar_height + 2
            revive_bar_height = 2
            revive_bar_width = int(bar_width * (self.revive_progress / self.character.revival_time))
            pygame.draw.rect(surface, (255, 255, 0), (bar_x, revive_bar_y, revive_bar_width, revive_bar_height))
        
        # --- Draw aim direction for Player 1 ---
        if player_index == 0 and not self.dead:
            center_x = draw_rect.x + draw_rect.width // 2
            center_y = draw_rect.y + draw_rect.height // 2
            aim_len = 40
            end_x = int(center_x + self.aim_direction[0] * aim_len)
            end_y = int(center_y + self.aim_direction[1] * aim_len)
            pygame.draw.line(surface, (255, 255, 0), (center_x, center_y), (end_x, end_y), 2)
        
        # --- Ammo UI to the right of HP bar for all players ---
        weapon = self.character.weapons[current_weapon_index] if hasattr(self.character, 'weapons') and len(self.character.weapons) > current_weapon_index else None
        if weapon:
            ammo_font = pygame.font.Font(None, 18)
            if weapon.common.ammo is None:
                reserve_text = "∞"
            else:
                reserve_text = str(weapon.common.ammo)
            if weapon.is_reloading:
                clip_text = "..."
            else:
                clip_text = str(weapon.current_clip)
            ammo_text = f"{reserve_text} | {clip_text}"
            ammo_surface = ammo_font.render(ammo_text, True, (255, 255, 0))
            ammo_x = bar_x + bar_width + 8
            ammo_y = bar_y - 6
            surface.blit(ammo_surface, (ammo_x, ammo_y))
            
            # --- Reload progress semi-circle ---
            if weapon.is_reloading:
                now = pygame.time.get_ticks()
                progress = min(1.0, (now - weapon.reload_start) / (weapon.common.reload_speed * 1000))
                arc_radius = 6  # Much smaller
                arc_center = (ammo_x + ammo_surface.get_width() // 2, ammo_y - arc_radius + 2)
                arc_rect = pygame.Rect(arc_center[0] - arc_radius, arc_center[1] - arc_radius, arc_radius * 2, arc_radius * 2)
                start_angle = math.pi  # 180 deg (left)
                end_angle = math.pi + math.pi * progress  # fill clockwise
                pygame.draw.arc(surface, (255, 255, 0), arc_rect, start_angle, end_angle, 2)
            
            # --- Warm-up progress bar ---
            elif weapon.uncommon.warm_up_time and weapon.is_warming_up:
                now = pygame.time.get_ticks()
                warm_up_progress = min(1.0, (now - weapon.warm_up_start) / (weapon.uncommon.warm_up_time * 1000))
                warm_up_bar_width = ammo_surface.get_width()
                warm_up_bar_height = 3
                warm_up_bar_x = ammo_x
                warm_up_bar_y = ammo_y + ammo_surface.get_height() + 2
                # Background
                pygame.draw.rect(surface, (60, 60, 60), (warm_up_bar_x, warm_up_bar_y, warm_up_bar_width, warm_up_bar_height))
                # Progress
                if warm_up_progress > 0:
                    fill_width = int(warm_up_bar_width * warm_up_progress)
                    pygame.draw.rect(surface, (255, 100, 0), (warm_up_bar_x, warm_up_bar_y, fill_width, warm_up_bar_height)) 