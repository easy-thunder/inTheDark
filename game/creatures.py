import pygame
from game.ai.movement import DirectApproach
from game.ai.attacks import MeleeCollisionAttack
import math
import random
import itertools

creature_id_counter = itertools.count()

class Creature:
    """A flexible class for any non-player character in the game."""
    SIZE_MAP = {
        'small': 0.25,
        'medium': 0.5,
        'large': 1.0,
        'xlarge': 1.5,
        'gigantic': 2.0
    }

    def __init__(self, x, y, size_str, hp, damage, speed, player_size, movement_profile, attack_profile, color=(0,255,0)):
        # Core attributes
        self.x = float(x)
        self.y = float(y)
        self.size_str = size_str
        self.hp = hp
        self.damage = damage
        self.speed = speed
        self.color = color
        
        # AI Behavior Profiles
        self.movement_profile = movement_profile
        self.attack_profile = attack_profile
        
        # Calculate size based on player_size, which is derived from screen size
        self.width = int(player_size * self.SIZE_MAP[self.size_str])
        self.height = int(player_size * self.SIZE_MAP[self.size_str])
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self, players):
        """Update creature's state by executing its AI profiles."""
        # Only consider living players
        living_players = [p for p in players if not p.dead]
        if self.movement_profile:
            self.movement_profile.move(self, living_players)
        if self.attack_profile:
            self.attack_profile.execute(self, living_players)

    def draw(self, surface, camera_x, camera_y, game_x, game_y):
        """Draws the creature relative to the camera."""
        draw_rect = self.rect.move(-camera_x + game_x, -camera_y + game_y)
        pygame.draw.rect(surface, self.color, draw_rect)

class ZombieCat:
    def __init__(self, x, y, size):
        self.id = next(creature_id_counter)
        self.x = x
        self.y = y
        self.width = int(size * 0.8)
        self.height = int(size * 0.8)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.hp = 15
        self.max_hp = 15
        self.original_speed = 2.0
        self.speed = 2.0
        self.damage = 5
        self.movement_profile = DirectApproach()
        self.attack_profile = MeleeCollisionAttack(cooldown=1000)
        
        # Status Effect Attributes
        self.is_slowed = False
        self.slow_duration = 0
        self.slow_timer = 0
        self.slow_color = (173, 216, 230) # Icy blue
        self.poison_effects = []

    def apply_slow(self, duration, factor):
        if not self.is_slowed:
            self.speed *= factor
        self.is_slowed = True
        self.slow_duration = duration
        self.slow_timer = pygame.time.get_ticks()

    def update(self, players):
        if self.hp <= 0: return

        if self.is_slowed:
            if pygame.time.get_ticks() - self.slow_timer > self.slow_duration:
                self.is_slowed = False
                self.speed = self.original_speed

        living_players = [p for p in players if not p.dead]
        if self.movement_profile: self.movement_profile.move(self, living_players)
        if self.attack_profile: self.attack_profile.execute(self, living_players)
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface, camera_x, camera_y, game_x, game_y):
        if self.hp <= 0: return
        draw_rect = self.rect.move(-camera_x + game_x, -camera_y + game_y)
        
        color = (139, 69, 19)
        if self.is_slowed:
            color = self.slow_color
        
        if hasattr(self, 'poison_effects') and self.poison_effects:
            # Blend poison green with current color
            r, g, b = color
            num_stacks = len(self.poison_effects)
            # Intensity of green increases with stacks
            alpha = min(0.7, 0.2 + (num_stacks * 0.1))
            pr, pg, pb = (0, 180, 0)
            color = (
                int(r * (1-alpha) + pr * alpha),
                int(g * (1-alpha) + pg * alpha),
                int(b * (1-alpha) + pb * alpha)
            )

        pygame.draw.rect(surface, color, draw_rect)

class ToughZombieCat:
    def __init__(self, x, y, size):
        self.id = next(creature_id_counter)
        self.x = x
        self.y = y
        self.width = int(size * 0.8)
        self.height = int(size * 0.8)
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.hp = 100
        self.max_hp = 100
        self.original_speed = 2.0
        self.speed = 2.0
        self.damage = 5
        self.movement_profile = DirectApproach()
        self.attack_profile = MeleeCollisionAttack(cooldown=1000)
        
        # Status Effect Attributes
        self.is_slowed = False
        self.slow_duration = 0
        self.slow_timer = 0
        self.slow_color = (173, 216, 230) # Icy blue
        self.poison_effects = []

    def apply_slow(self, duration, factor):
        if not self.is_slowed:
            self.speed *= factor
        self.is_slowed = True
        self.slow_duration = duration
        self.slow_timer = pygame.time.get_ticks()

    def update(self, players):
        if self.hp <= 0: return

        if self.is_slowed:
            if pygame.time.get_ticks() - self.slow_timer > self.slow_duration:
                self.is_slowed = False
                self.speed = self.original_speed

        living_players = [p for p in players if not p.dead]
        if self.movement_profile: self.movement_profile.move(self, living_players)
        if self.attack_profile: self.attack_profile.execute(self, living_players)
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface, camera_x, camera_y, game_x, game_y):
        if self.hp <= 0: return
        draw_rect = self.rect.move(-camera_x + game_x, -camera_y + game_y)
        
        color = (139, 0, 0) # Dark Red
        if self.is_slowed:
            color = self.slow_color
        
        if hasattr(self, 'poison_effects') and self.poison_effects:
            # Blend poison green with current color
            r, g, b = color
            num_stacks = len(self.poison_effects)
            # Intensity of green increases with stacks
            alpha = min(0.7, 0.2 + (num_stacks * 0.1))
            pr, pg, pb = (0, 180, 0)
            color = (
                int(r * (1-alpha) + pr * alpha),
                int(g * (1-alpha) + pg * alpha),
                int(b * (1-alpha) + pb * alpha)
            )

        pygame.draw.rect(surface, color, draw_rect)

class ThornyVenomThistle:
    def __init__(self, x, y, size):
        self.id = next(creature_id_counter)
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.rect = pygame.Rect(x, y, size, size)
        self.hp = 20
        self.max_hp = 20
        self.speed = 0  # Stationary
        self.damage = 10
        self.last_attack_time = 0
        self.attack_cooldown = 1500  # 1.5 seconds
        self.attack_range = 40  # Slightly larger attack range since it's stationary
        self.is_slowed = False
        self.poison_effects = []

    def apply_slow(self, duration, factor):
        """A dummy method to allow for consistent API calls."""
        self.is_slowed = True # You could add a visual effect here if desired

    def update(self, players):
        if self.hp <= 0:
            return
        
        # Find closest living player
        closest_player = None
        closest_distance = float('inf')
        
        for player in players:
            if not player.dead:
                distance = math.hypot(player.x - self.x, player.y - self.y)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_player = player
        
        if closest_player is None:
            return
        
        # Check if in attack range
        if closest_distance <= self.attack_range:
            now = pygame.time.get_ticks()
            if now - self.last_attack_time >= self.attack_cooldown:
                closest_player.take_damage(self.damage)
                self.last_attack_time = now
    
    def draw(self, surface, camera_x, camera_y, game_x, game_y):
        if self.hp <= 0:
            return
        
        draw_rect = self.rect.move(-camera_x + game_x, -camera_y + game_y)
        
        color = self.color
        if hasattr(self, 'poison_effects') and self.poison_effects:
            # Blend poison green with current color
            r, g, b = color
            num_stacks = len(self.poison_effects)
            # Intensity of green increases with stacks
            alpha = min(0.7, 0.2 + (num_stacks * 0.1))
            pr, pg, pb = (0, 180, 0)
            color = (
                int(r * (1-alpha) + pr * alpha),
                int(g * (1-alpha) + pg * alpha),
                int(b * (1-alpha) + pb * alpha)
            )

        pygame.draw.rect(surface, color, draw_rect)

# --- Creature Factory Functions ---

def create_zombie_cat(x, y, size):
    return ZombieCat(x, y, size)

def create_tough_zombie_cat(x, y, size):
    return ToughZombieCat(x, y, size)

def create_thorny_venom_thistle(x, y, size):
    return ThornyVenomThistle(x, y, size) 