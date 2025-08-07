import pygame
from game.ai.movement import DirectApproach
from game.ai.attacks import MeleeCollisionAttack
import math
import itertools
import os
from enum import Enum

creature_id_counter = itertools.count()

class Orientation(Enum):
    LEFT = 'left'
    RIGHT = 'right'

class MELEE_ACTION_FX(Enum):
    CLEAVE = 'cleave'
    SLASH = 'slash'
    PUNCH = 'punch'
    BITE = 'bite'
    STAB = 'stab'

class RANGED_ACTION_FX(Enum):
    FIREBALL = 'fireball'
    LASER = 'laser'
    ARROW = 'arrow'
    THROW = 'throw'
    BLAST = 'blast'

class Creature:
    """A flexible class for any non-player character in the game."""
    # Fixed pixel sizes for each creature category
    SIZE_MAP = {
        'tiny': 12,      # Very small creatures (rats, insects)
        'small': 24,     # Small creatures (cats, dogs)
        'medium': 36,    # Medium creatures (humans, zombies)
        'large': 48,     # Large creatures (bears, ogres)
        'xlarge': 64,    # Extra large creatures (elephants, giants)
        'gigantic': 96   # Boss-sized creatures
    }

    # Size to knockback resistance mapping (higher = more resistant)
    SIZE_RESISTANCE = {
        'tiny': 0.1,      # Takes 90% of knockback
        'small': 0.3,     # Takes 70% of knockback
        'medium': 0.5,    # Takes 50% of knockback
        'large': 0.7,     # Takes 30% of knockback
        'xlarge': 0.85,   # Takes 15% of knockback
        'gigantic': 0.95  # Takes 5% of knockback
    }

    def __init__(
        self, x, y, size_str, hp, damage, speed, movement_profile, attack_profile, color=(0,255,0),
        image_files=None,  # {'walk': (filepath, orientation), 'hurt': (filepath, orientation)}
        action_type=None,  # 'melee' or 'ranged' (optional)
        action_fx=None,    # MELEE_ACTION_FX or RANGED_ACTION_FX enum value
        ability1=None,     # Optional ability 1
        ability2=None,     # Optional ability 2
        ability3=None,     # Optional ability 3
        ability_fx1=None,  # Optional ability 1 effect
        ability_fx2=None,  # Optional ability 2 effect
        ability_fx3=None,  # Optional ability 3 effect
        # weapon=None,  # (future use)
        facing='right'
    ):
        self.x = float(x)
        self.y = float(y)
        self.size_str = size_str
        self.hp = hp
        self.max_hp = hp
        self.damage = damage
        self.speed = speed
        self.color = color
        self.movement_profile = movement_profile
        self.attack_profile = attack_profile
        self.width = self.SIZE_MAP[self.size_str]
        self.height = self.SIZE_MAP[self.size_str]
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.id = next(creature_id_counter)
        self.knockback_dx = 0
        self.knockback_dy = 0
        self.knockback_friction = 0.85
        self.knockback_resistance = self.SIZE_RESISTANCE[self.size_str]
        self.burning_effects = {}
        self.poison_stacks = []
        self.slow_duration = 0
        self.slow_factor = 1.0
        self.base_speed = speed
        self.facing = facing
        self.animation_state = 'walk'
        self.images = {}
        self.meshes = {}
        self.hurt_time = None
        self.hurt_duration = 500
        self.attack_type = 'contact'  # All creatures have contact damage
        self.action_type = action_type
        self.action_fx = action_fx
        self.ability1 = ability1
        self.ability2 = ability2
        self.ability3 = ability3
        self.ability_fx1 = ability_fx1
        self.ability_fx2 = ability_fx2
        self.ability_fx3 = ability_fx3
        self.cleave_cooldown = 2000  # milliseconds
        self.last_cleave_time = 0
        self.cleave_range = max(24, int(self.width * 0.75))  # scale cleave with creature size
        self.cleave_duration = 300  # milliseconds
        self.cleave_start_time = None
        self.is_cleaving = False
        # self.weapon = weapon  # (future use)
        if image_files:
            self.load_and_prepare_images(image_files)

    def load_and_prepare_images(self, image_files):
        asset_dir = os.path.join(os.path.dirname(__file__), 'assets')
        for state in ['walk', 'hurt']:
            if state not in image_files:
                raise FileNotFoundError(f"Required image for state '{state}' not found in image_files!")
            filename, orientation = image_files[state]
            path = os.path.join(asset_dir, filename)
            img = pygame.image.load(path).convert_alpha()
            img = pygame.transform.smoothscale(img, (self.width, self.height))
            # Store the base direction
            self.images[f'{state}_{orientation.value}'] = img
            self.meshes[f'{state}_{orientation.value}'] = pygame.mask.from_surface(img)
            # Flip for the opposite direction
            opposite = 'left' if orientation == Orientation.RIGHT else 'right'
            flipped_img = pygame.transform.flip(img, True, False)
            self.images[f'{state}_{opposite}'] = flipped_img
            self.meshes[f'{state}_{opposite}'] = pygame.mask.from_surface(flipped_img)
        
        # Load action effect image if action_type is specified
        if self.action_type and self.action_fx:
            action_path = os.path.join(asset_dir, 'action_fx', f'{self.action_fx.value}.png')
            if os.path.exists(action_path):
                action_img = pygame.image.load(action_path).convert_alpha()
                action_img = pygame.transform.smoothscale(action_img, (self.cleave_range * 2, self.cleave_range * 2))
                self.action_image = action_img
            else:
                # Create a simple effect if image doesn't exist
                self.action_image = pygame.Surface((self.cleave_range * 2, self.cleave_range * 2), pygame.SRCALPHA)
                color = (255, 0, 0, 128) if self.action_type == 'melee' else (0, 0, 255, 128)
                pygame.draw.circle(self.action_image, color, (self.cleave_range, self.cleave_range), self.cleave_range)

    def set_animation_state(self, state):
        if f'{state}_left' in self.images or f'{state}_right' in self.images:
            self.animation_state = state

    def get_current_image(self):
        key = f'{self.animation_state}_{self.facing}'
        return self.images.get(key)

    def get_current_mesh(self):
        key = f'{self.animation_state}_{self.facing}'
        return self.meshes.get(key)

    def apply_slow(self, duration, factor):
        """Apply a slow effect to the creature (default: change color and slow factor)"""
        self.slow_duration = duration
        self.slow_factor = factor
        self.color = (100, 150, 255)  # Icy blue

    def take_damage(self, amount):
        self.hp -= amount
        self.set_animation_state('hurt')
        self.hurt_time = pygame.time.get_ticks()

    def perform_action_attack(self, players):
        if not self.action_type or not self.action_fx:
            return
            
        now = pygame.time.get_ticks()
        if now - self.last_cleave_time < self.cleave_cooldown:
            return
            
        # Find nearest player
        nearest_player = None
        min_dist = float('inf')
        for player in players:
            if not player.dead:
                dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
                if dist < min_dist:
                    min_dist = dist
                    nearest_player = player
        
        if nearest_player and min_dist <= self.cleave_range * 2:
            # Start action attack
            self.is_cleaving = True
            self.cleave_start_time = now
            self.last_cleave_time = now
            # Calculate angle to player for cleave effect
            dx = nearest_player.rect.centerx - self.rect.centerx
            dy = nearest_player.rect.centery - self.rect.centery
            self.cleave_angle = math.degrees(math.atan2(dy, dx))
            # Simple attack area check (semi-circle in facing direction)
            if self.facing == 'right' and dx > 0 and abs(dy) < self.cleave_range:
                if hasattr(nearest_player, 'take_damage'):
                    nearest_player.take_damage(self.damage)
            elif self.facing == 'left' and dx < 0 and abs(dy) < self.cleave_range:
                if hasattr(nearest_player, 'take_damage'):
                    nearest_player.take_damage(self.damage)

    def update(self, dt, walls, players):
        # Handle knockback movement first
        if abs(self.knockback_dx) > 0.1 or abs(self.knockback_dy) > 0.1:
            original_x = self.rect.x
            original_y = self.rect.y
            resistance = self.knockback_resistance
            actual_dx = self.knockback_dx * (1 - resistance)
            actual_dy = self.knockback_dy * (1 - resistance)
            self.rect.x += actual_dx
            for wall in walls:
                if self.rect.colliderect(wall):
                    if actual_dx > 0:
                        self.rect.right = wall.left
                    else:
                        self.rect.left = wall.right
                    self.knockback_dx *= -0.5
            self.rect.y += actual_dy
            for wall in walls:
                if self.rect.colliderect(wall):
                    if actual_dy > 0:
                        self.rect.bottom = wall.top
                    else:
                        self.rect.top = wall.bottom
                    self.knockback_dy *= -0.5
            self.knockback_dx *= self.knockback_friction
            self.knockback_dy *= self.knockback_friction
        
        # Update slow effect
        if self.slow_duration > 0:
            self.slow_duration -= dt * 1000
            if self.slow_duration <= 0:
                self.slow_factor = 1.0
                self.color = self.original_color if hasattr(self, 'original_color') else self.color
        
        # Continue with normal movement using modified speed
        current_speed = self.speed * self.slow_factor
        if self.movement_profile:
            self.movement_profile.move(self, players)
        
        # Handle action attacks (melee/ranged)
        if self.action_type:
            self.perform_action_attack(players)
        elif self.attack_profile:
            self.attack_profile.execute(self, players)
        
        self.rect.topleft = (self.x, self.y)
        
        # Handle cleave animation
        if self.is_cleaving and self.cleave_start_time:
            if pygame.time.get_ticks() - self.cleave_start_time > self.cleave_duration:
                self.is_cleaving = False
                self.cleave_start_time = None
        
        # Handle hurt animation state
        if self.animation_state == 'hurt' and self.hurt_time is not None:
            if pygame.time.get_ticks() - self.hurt_time > self.hurt_duration:
                self.set_animation_state('walk')
                self.hurt_time = None
        
        # --- New: Update facing based on nearest player (for subclasses that want it) ---
        if hasattr(self, 'update_facing_nearest_player') and callable(self.update_facing_nearest_player):
            self.update_facing_nearest_player(players)
        elif getattr(self, 'auto_face_nearest_player', False):
            nearest_player = None
            min_dist = float('inf')
            for player in players:
                if not player.dead:
                    dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
                    if dist < min_dist:
                        min_dist = dist
                        nearest_player = player
            if nearest_player:
                dx = nearest_player.rect.centerx - self.rect.centerx
                self.facing = 'right' if dx > 0 else 'left'

    def draw(self, surface, camera_x, camera_y, game_x, game_y):
        screen_x = self.rect.x - camera_x + game_x
        screen_y = self.rect.y - camera_y + game_y
        # Draw cleave effect if active
        if self.is_cleaving and hasattr(self, 'action_image'):
            angle = getattr(self, 'cleave_angle', 0)
            rotated_img = pygame.transform.rotate(self.action_image, -angle - 110)
            rect = rotated_img.get_rect(center=(screen_x + self.rect.width // 2, screen_y + self.rect.height // 2))
            surface.blit(rotated_img, rect.topleft)
        img = self.get_current_image()
        if img:
            surface.blit(img, (screen_x, screen_y))
        # Draw HP bar
        hp_bar_width = self.width
        hp_bar_height = 4
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (60, 60, 60), (screen_x, screen_y - 6, hp_bar_width, hp_bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (screen_x, screen_y - 6, hp_bar_width * hp_ratio, hp_bar_height))

class ZombieCat(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/zombie_cat/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/zombie_cat/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='small',
            hp=30,
            damage=5,
            speed=3,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            # weapon=None,  # (future use)
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 1

class ToughZombieCat(Creature):
    def __init__(self, x, y):
        super().__init__(
            x=x,
            y=y,
            size_str='medium',
            hp=80,
            damage=12,
            speed=2,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=800),
            color=(120, 80, 80)
        )
        self.original_color = self.color

class ThornyVenomThistle(Creature):
    def __init__(self, x, y):
        super().__init__(
            x=x,
            y=y,
            size_str='large',  # Thistles are large
            hp=120,
            damage=18,
            speed=0,  # Stationary
            movement_profile=None,
            attack_profile=None,
            color=(80, 200, 80)
        )
        self.original_color = self.color
        self.last_attack_time = 0
        self.attack_cooldown = 1500  # milliseconds
        self.attack_range = 40  # pixels

    def apply_slow(self, duration, factor):
        pass  # Thistles are stationary, so slow has no effect

    def update(self, dt, walls, players):
        # Stationary, but can attack players in range
        if self.hp <= 0:
            return
        now = pygame.time.get_ticks()
        for player in players:
            if hasattr(player, 'dead') and not player.dead:
                # Use center points for distance
                dist = math.hypot(player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery)
                if dist <= self.attack_range:
                    if now - self.last_attack_time >= self.attack_cooldown:
                        if hasattr(player, 'take_damage'):
                            player.take_damage(self.damage)
                        self.last_attack_time = now

    def draw(self, surface, camera_x, camera_y, game_x, game_y):
        screen_x = self.rect.x - camera_x + game_x
        screen_y = self.rect.y - camera_y + game_y
        pygame.draw.rect(surface, self.color, (screen_x, screen_y, self.rect.width, self.rect.height))
        # Draw HP bar
        hp_bar_width = self.rect.width
        hp_bar_height = 4
        hp_ratio = max(0, self.hp / self.max_hp)
        pygame.draw.rect(surface, (255, 0, 0), (screen_x, screen_y - 6, hp_bar_width, hp_bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (screen_x, screen_y - 6, hp_bar_width * hp_ratio, hp_bar_height))

class ZombieDog(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/zombie_dog/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/zombie_dog/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='medium',  # one size bigger than cat
            hp=60,  # double HP
            damage=10,  # more damage
            speed=3,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            # weapon=None,  # (future use)
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 1

class ZombieFemale(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/zombie_female/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/zombie_female/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='medium',
            hp=40,
            damage=8,
            speed=2.5,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 2

class ZombieMale(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/zombie_male/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/zombie_male/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='medium',
            hp=40,
            damage=8,
            speed=2.5,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 2

class NecroBat(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/necro_bat/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/necro_bat/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='small',
            hp=20,
            damage=6,
            speed=4,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 2

class NecroMountainLion(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/necro_mountain_lion/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/necro_mountain_lion/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='large',
            hp=100,
            damage=20,
            speed=3.5,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 3

class NecroApe(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/necro_ape/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/necro_ape/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='large',
            hp=100,
            damage=20,
            speed=3.5,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 3

class CyberEnhancedZombie(Creature):
    def __init__(self, x, y, facing='right'):
        image_files = {
            'walk': ('creatures/cyber_enhanced_zombie/walk.png', Orientation.RIGHT),
            'hurt': ('creatures/cyber_enhanced_zombie/hurt.png', Orientation.RIGHT)
        }
        super().__init__(
            x=x,
            y=y,
            size_str='xlarge',
            hp=200,
            damage=35,
            speed=4,
            movement_profile=DirectApproach(),
            attack_profile=MeleeCollisionAttack(cooldown=1000),
            image_files=image_files,
            action_type='melee',
            action_fx=MELEE_ACTION_FX.CLEAVE,
            ability1=None,
            ability2=None,
            ability3=None,
            ability_fx1=None,
            ability_fx2=None,
            ability_fx3=None,
            facing=facing
        )
        self.original_color = self.color
        self.auto_face_nearest_player = True
        self.difficulty = 4

# --- Creature Factory Functions ---

def create_zombie_cat(x, y):
    return ZombieCat(x, y)

def create_tough_zombie_cat(x, y):
    return ToughZombieCat(x, y)

def create_thorny_venom_thistle(x, y):
    return ThornyVenomThistle(x, y)

# --- Creature Difficulty Pools ---
# Each pool is a list of (factory_function, kwargs) tuples
CREATURE_DIFFICULTY_POOLS = [
    [
        (ZombieCat, {}),
        (ZombieDog, {}),
    ],
    [
        (ZombieFemale, {}),
        (ZombieMale, {}),
        (NecroBat, {}),
    ],
    [
        (NecroMountainLion, {}),
        (NecroApe, {}),
    ],
    [
        (CyberEnhancedZombie, {}),
    ],
    # Add higher difficulty pools as new lists
] 