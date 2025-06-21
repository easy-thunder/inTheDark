import pygame
from game.ai.movement import DirectApproach
from game.ai.attacks import MeleeCollisionAttack
import math
import random

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
        self.x = x
        self.y = y
        self.width = size
        self.height = size
        self.rect = pygame.Rect(x, y, size, size)
        self.hp = 15
        self.max_hp = 15
        self.speed = 1
        self.damage = 5
        self.last_attack_time = 0
        self.attack_cooldown = 1000  # 1 second
        self.aggro_range = 200
        self.attack_range = 30
    
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
            return
        
        # Move towards player if in aggro range
        if closest_distance <= self.aggro_range:
            dx = closest_player.x - self.x
            dy = closest_player.y - self.y
            distance = math.hypot(dx, dy)
            
            if distance > 0:
                dx = (dx / distance) * self.speed
                dy = (dy / distance) * self.speed
                
                self.x += dx
                self.y += dy
                self.rect.x = self.x
                self.rect.y = self.y
    
    def draw(self, screen, camera_x, camera_y, game_x, game_y):
        if self.hp <= 0:
            return
        
        draw_rect = self.rect.move(-camera_x + game_x, -camera_y + game_y)
        pygame.draw.rect(screen, (139, 69, 19), draw_rect)  # Brown color

class ThornyVenomThistle:
    def __init__(self, x, y, size):
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
    
    def draw(self, screen, camera_x, camera_y, game_x, game_y):
        if self.hp <= 0:
            return
        
        draw_rect = self.rect.move(-camera_x + game_x, -camera_y + game_y)
        # Draw a dark green thistle-like shape
        pygame.draw.rect(screen, (34, 139, 34), draw_rect)  # Forest green
        # Add some darker spots to make it look thorny
        pygame.draw.circle(screen, (0, 100, 0), (draw_rect.centerx - 3, draw_rect.centery - 3), 2)
        pygame.draw.circle(screen, (0, 100, 0), (draw_rect.centerx + 3, draw_rect.centery + 3), 2)

# --- Creature Factory Functions ---

def create_zombie_cat(x, y, size):
    return ZombieCat(x, y, size)

def create_thorny_venom_thistle(x, y, size):
    return ThornyVenomThistle(x, y, size) 