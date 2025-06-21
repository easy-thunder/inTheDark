from enum import Enum, auto

class FireMode(Enum):
    MANUAL = auto()
    AUTOMATIC = auto()
    BURST = auto()
    SHOTGUN = auto()
    SINGLE = auto()
    THROWN = auto()
    ORBITAL = auto()
    SPRAY = auto()

class WeaponSpecialization(Enum):
    PRECISION = auto()
    EXPLOSIVES = auto()
    PISTOLS = auto()
    ASSAULT = auto()
    SHOTGUNS = auto()
    MELEE = auto()

class ContactEffect(Enum):
    PIERCE = auto()
    EXPLODE = auto()
    DAMAGE_BOUNCE = auto()
    NO_DAMAGE_BOUNCE = auto()

class DamageType(Enum):
    PHYSICAL = auto()
    FIRE = auto()
    ICE = auto()

class Weapon:
    def __init__(self, name, accuracy, range_, fire_mode, fire_rate, damage, clip_size, reload_speed, bullet_size=0.2, splash=None, bullet_color=(200,200,0), bullet_speed=12, ammo=None, traits=None, ability=None, specialization_type=None, specialization_level=1, piercing=0, warm_up_time=None, detonation_time=None, contact_effect=ContactEffect.PIERCE, bounce_limit=None, drop_height=None, volley=1, spread=0, damage_type=DamageType.PHYSICAL):
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
        self.detonation_time = detonation_time  # seconds, None means no detonation
        self.contact_effect = contact_effect
        self.bounce_limit = bounce_limit
        self.drop_height = drop_height
        self.volley = volley  # Number of pellets for shotguns
        self.spread = spread  # Spread angle in degrees for shotguns
        self.damage_type = damage_type  # Type of damage (physical, fire, ice, etc.)
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
        piercing=1,
        contact_effect=ContactEffect.PIERCE,
        bounce_limit=None,
        drop_height=None,
        volley=1,
        spread=0,
        damage_type=DamageType.PHYSICAL
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
        piercing=0,
        contact_effect=ContactEffect.EXPLODE,
        bounce_limit=None,
        drop_height=None,
        volley=1,
        spread=0,
        damage_type=DamageType.PHYSICAL
    )

def create_mini_gun():
    return Weapon(
        name="Mini Gun",
        accuracy=15,  # Less accurate due to high fire rate
        range_=8,  # Medium range
        fire_mode=FireMode.AUTOMATIC,
        fire_rate=480,  # Very high fire rate
        damage=1,  # Low damage per bullet
        clip_size=120,  # Large clip
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
        piercing=0,
        contact_effect=ContactEffect.PIERCE,
        warm_up_time=2.0,  # 2 second warm-up time
        bounce_limit=None,
        drop_height=None,
        volley=1,
        spread=0,
        damage_type=DamageType.PHYSICAL
    )

def create_grenade():
    return Weapon(
        name="Grenade",
        accuracy=5,
        range_=12,
        fire_mode=FireMode.THROWN,
        fire_rate=30,
        damage=25,
        clip_size=1,
        reload_speed=2.0,
        bullet_size=0.3,
        splash=3.0,
        bullet_color=(0, 255, 0),
        bullet_speed=8,
        ammo=5,
        traits=[],
        ability=None,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=2,
        piercing=0,
        warm_up_time=None,
        detonation_time=3.0,
        contact_effect=ContactEffect.NO_DAMAGE_BOUNCE,
        bounce_limit=100,
        drop_height=None,
        volley=1,
        spread=0,
        damage_type=DamageType.PHYSICAL
    )

def create_ricochet_pistol():
    return Weapon(
        name="Ricochet Pistol",
        accuracy=10,
        range_=15,
        fire_mode=FireMode.MANUAL,
        fire_rate=120,
        damage=1.5,
        clip_size=15,
        reload_speed=2.5,
        bullet_size=0.2,
        bullet_color=(100, 100, 255),
        bullet_speed=10,
        ammo=None,
        specialization_type=WeaponSpecialization.PISTOLS,
        specialization_level=2,
        piercing=0,
        bounce_limit=2,
        contact_effect=ContactEffect.DAMAGE_BOUNCE,
        drop_height=None,
        volley=1,
        spread=0,
        damage_type=DamageType.PHYSICAL
    )

def create_missile_striker():
    return Weapon(
        name="Missile Striker",
        accuracy=15,
        range_=1000, # Allows targeting anywhere
        fire_mode=FireMode.ORBITAL,
        fire_rate=30, # Effectively controls time between shots
        damage=50,
        clip_size=1,
        reload_speed=4,
        bullet_size=0.8, # The missile itself is large
        splash=7.0,
        bullet_color=(255, 150, 50),
        bullet_speed=4, # This will be its fall speed
        ammo=3,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=5,
        warm_up_time=2.0,
        contact_effect=ContactEffect.EXPLODE,
        drop_height=600, # Missile falls from this "altitude"
        volley=1,
        spread=0,
        damage_type=DamageType.PHYSICAL
    )

def create_shotgun():
    return Weapon(
        name="Pump Shotgun",
        accuracy=5,  # Very accurate center
        range_=6,  # Short range
        fire_mode=FireMode.SHOTGUN,
        fire_rate=60,  # Slow fire rate (pump action)
        damage=8,  # High damage per pellet
        clip_size=6,  # Classic shotgun capacity
        reload_speed=3.0,  # Slow reload
        bullet_size=0.1,  # Small pellets
        splash=None,  # No splash
        bullet_color=(255, 200, 100),  # Golden pellets
        bullet_speed=8,  # Medium speed
        ammo=24,  # Limited ammo
        traits=[],
        ability=None,
        specialization_type=WeaponSpecialization.SHOTGUNS,
        specialization_level=1,
        piercing=0,  # No piercing
        contact_effect=ContactEffect.PIERCE,
        volley=8,  # 8 pellets
        spread=30,  # 30 degree spread
        damage_type=DamageType.PHYSICAL
    )

def create_flamethrower():
    return Weapon(
        name="Inferno Flamethrower",
        accuracy=20,  # Wide spray pattern
        range_=4,  # Short range but devastating
        fire_mode=FireMode.SPRAY,  # Continuous spray
        fire_rate=120,  # High fire rate for continuous flames
        damage=3,  # Damage per flame particle
        clip_size=50,  # Fuel tank capacity
        reload_speed=4.0,  # Slow fuel refill
        bullet_size=0.15,  # Small flame particles
        splash=None,  # No splash, but damage over time
        bullet_color=(255, 100, 0),  # Orange flames
        bullet_speed=6,  # Slower moving flames
        ammo=100,  # Limited fuel
        traits=["Burning"],  # Special trait for fire damage
        ability=None,
        specialization_type=WeaponSpecialization.EXPLOSIVES,  # Fire is explosive-like
        specialization_level=3,
        piercing=0,  # No piercing
        contact_effect=ContactEffect.PIERCE,  # Flames pass through but deal damage
        volley=3,  # Multiple flame particles per spray
        spread=45,  # Wide flame cone
        damage_type=DamageType.FIRE  # Fire damage type for DoT
    ) 