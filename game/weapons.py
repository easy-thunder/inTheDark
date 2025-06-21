from enum import Enum, auto

class FireMode(Enum):
    MANUAL = auto()
    AUTOMATIC = auto()
    BURST = auto()
    SHOTGUN = auto()
    SINGLE = auto()

class WeaponSpecialization(Enum):
    PRECISION = auto()
    EXPLOSIVES = auto()
    PISTOLS = auto()
    ASSAULT = auto()
    SHOTGUNS = auto()
    MELEE = auto()

class Weapon:
    def __init__(self, name, accuracy, range_, fire_mode, fire_rate, damage, clip_size, reload_speed, bullet_size=0.2, splash=None, bullet_color=(200,200,0), bullet_speed=12, ammo=None, traits=None, ability=None, specialization_type=None, specialization_level=1, piercing=0, warm_up_time=None):
        self.name = name
        # Accuracy: 0 (perfect) to 360 (random); internally, 0-1 is easier, so we use 0-1
        self.accuracy = accuracy / 360 if accuracy > 1 else accuracy
        self.range = range_  # in tiles or pixels, to be interpreted by the game
        self.fire_mode = fire_mode
        self.fire_rate = fire_rate  # rounds per minute
        self.damage = damage
        self.clip_size = clip_size
        self.reload_speed = reload_speed  # seconds
        self.bullet_size = bullet_size  # as a fraction of TILE_SIZE
        self.splash = splash  # None or a radius
        self.bullet_color = bullet_color
        self.bullet_speed = bullet_speed
        self.ammo = ammo  # None means infinite
        self.traits = traits or []
        self.ability = ability  # Can be None or a callable/ability object
        self.specialization_type = specialization_type
        self.specialization_level = specialization_level
        self.piercing = piercing
        self.warm_up_time = warm_up_time  # seconds, None means no warm-up
        # State
        self.current_clip = clip_size
        self.is_reloading = False
        self.last_shot_time = 0
        self.warm_up_start = None  # When warm-up started
        self.is_warming_up = False  # Whether currently warming up

# Factory function for the Rusty Pistol

def create_rusty_pistol():
    return Weapon(
        name="Rusty Pistol",
        accuracy=30,  # 30/360 spread
        range_=10,    # 10 tiles
        fire_mode=FireMode.MANUAL,
        fire_rate=40, # 40 rounds per minute
        damage=2,
        clip_size=10,
        reload_speed=3, # seconds
        bullet_size=0.2, # 20% of TILE_SIZE
        splash=None,     # no splash
        bullet_color=(200, 200, 0),
        bullet_speed=12,
        ammo=None,      # infinite
        traits=[],
        ability=None,
        specialization_type=WeaponSpecialization.PISTOLS,
        specialization_level=1,
        piercing=1
    )

def create_rocket_launcher():
    return Weapon(
        name="Rocket Launcher",
        accuracy=5,  # Very accurate
        range_=12,  # Long range
        fire_mode=FireMode.SINGLE,
        fire_rate=30,  # Slow fire rate
        damage=50,  # High damage
        clip_size=1,  # Single shot
        reload_speed=3.0,  # Slow reload
        bullet_size=0.4,  # Large projectile
        splash=2.0,  # Explosive radius
        bullet_color=(255, 100, 0),  # Orange
        bullet_speed=8,  # Slower projectile
        ammo=10,  # Limited ammo
        traits=[],
        ability=None,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=3,
        piercing=0
    )

def create_mini_gun():
    return Weapon(
        name="Mini Gun",
        accuracy=15,  # Less accurate due to high fire rate
        range_=8,  # Medium range
        fire_mode=FireMode.AUTOMATIC,
        fire_rate=480,  # Very high fire rate
        damage=1,  # Low damage per bullet
        clip_size=100,  # Large clip
        reload_speed=4.0,  # Slow reload
        bullet_size=0.15,  # Smaller bullets than pistol
        splash=None,  # No splash damage
        bullet_color=(255, 255, 100),  # Bright yellow
        bullet_speed=10,  # Medium speed
        ammo=480,  # Large ammo reserve
        traits=[],
        ability=None,
        specialization_type=WeaponSpecialization.ASSAULT,
        specialization_level=4,
        piercing=1,  # Can pierce through one enemy
        warm_up_time=2.0  # 2 second warm-up time
    ) 