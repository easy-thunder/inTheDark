from enum import Enum, auto

class FireMode(Enum):
    MANUAL = auto()
    AUTOMATIC = auto()
    BURST = auto()
    SHOTGUN = auto()

class WeaponSpecialization(Enum):
    PRECISION = auto()
    EXPLOSIVES = auto()
    PISTOLS = auto()
    ASSAULT = auto()
    SHOTGUNS = auto()
    MELEE = auto()

class Weapon:
    def __init__(self, name, accuracy, range_, fire_mode, fire_rate, damage, clip_size, reload_speed, bullet_size=0.2, splash=None, bullet_color=(200,200,0), bullet_speed=12, ammo=None, traits=None, ability=None, specialization_type=None, specialization_level=1):
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
        # State
        self.current_clip = clip_size
        self.is_reloading = False
        self.last_shot_time = 0

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
        specialization_level=1
    )

def create_rocket_launcher():
    return Weapon(
        name="Rocket Launcher",
        accuracy=40,  # 40/360 spread
        range_=15,    # 15 tiles
        fire_mode=FireMode.MANUAL,
        fire_rate=10, # 10 rounds per minute
        damage=20,
        clip_size=1,
        reload_speed=5, # seconds
        bullet_size=0.5, # 50% of TILE_SIZE
        splash=2,        # 2 tiles
        bullet_color=(80, 255, 80), # greenish
        bullet_speed=8,  # slower rocket
        ammo=3,
        traits=[],
        ability=None,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=3
    ) 