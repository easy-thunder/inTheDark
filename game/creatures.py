import pygame
from game.ai.movement import DirectApproach
from game.ai.attacks import MeleeCollisionAttack

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

# --- Creature Factory Functions ---

def create_zombie_cat(x, y, player_size):
    """Creates a pre-configured zombie cat with direct approach and melee attack."""
    return Creature(
        x=x, y=y,
        player_size=player_size,
        size_str='small',
        hp=5,
        damage=20,
        speed=2,
        movement_profile=DirectApproach(),
        attack_profile=MeleeCollisionAttack(cooldown=1000), # 1s cooldown
        color=(0, 255, 0) # Green for now
    ) 