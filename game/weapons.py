from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

class FireMode(Enum):
    MANUAL = auto()
    AUTOMATIC = auto()
    BURST = auto()
    SHOTGUN = auto()
    SINGLE = auto()
    THROWN = auto()
    ORBITAL = auto()
    SPRAY = auto()
    ORBITAL_BEAM = auto()
    MELEE = auto()
    BEAM = auto()

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
    POISON = auto()

@dataclass
class CommonStats:
    name: str
    accuracy: float
    range: float
    damage: float
    fire_rate: float
    fire_mode: FireMode
    clip_size: int
    reload_speed: float
    bullet_size: float
    bullet_color: tuple
    bullet_speed: float
    ammo: Optional[int]
    specialization_type: Optional[WeaponSpecialization]
    specialization_level: int
    contact_effect: ContactEffect
    damage_type: DamageType

@dataclass
class UncommonStats:
    warm_up_time: Optional[float] = None
    volley: Optional[int] = None
    spread: Optional[float] = None
    bounce_limit: Optional[int] = None
    drop_height: Optional[float] = None
    detonation_time: Optional[float] = None
    splash: Optional[float] = None
    piercing: Optional[int] = None
    pellets: Optional[int] = None
    spray_angle: Optional[float] = None

@dataclass
class UniqueStats:
    beam_duration: Optional[float] = None
    beam_damage_tick: Optional[float] = None
    # Add more unique traits as needed

class Weapon:
    def __init__(self, common: CommonStats, uncommon: Optional[UncommonStats] = None, unique: Optional[UniqueStats] = None):
        self.common = common
        self.uncommon = uncommon or UncommonStats()
        self.unique = unique or UniqueStats()
        # State
        self.current_clip = common.clip_size
        self.is_reloading = False
        self.last_shot_time = 0
        self.warm_up_start = None
        self.is_warming_up = False

# Factory function for the Rusty Pistol

def create_rusty_pistol():
    common = CommonStats(
        name="Rusty Pistol",
        accuracy=30/360,
        range=10,
        damage=2,
        fire_rate=40,
        fire_mode=FireMode.MANUAL,
        clip_size=10,
        reload_speed=3,
        bullet_size=0.2,
        bullet_color=(200, 200, 0),
        bullet_speed=12,
        ammo=None,
        specialization_type=WeaponSpecialization.PISTOLS,
        specialization_level=1,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(piercing=1)
    return Weapon(common, uncommon)

def create_rocket_launcher():
    common = CommonStats(
        name="Rocket Launcher",
        accuracy=5/360,
        range=12,
        damage=50,
        fire_rate=30,
        fire_mode=FireMode.SINGLE,
        clip_size=1,
        reload_speed=3.0,
        bullet_size=0.4,
        bullet_color=(255, 100, 0),
        bullet_speed=8,
        ammo=10,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=3,
        contact_effect=ContactEffect.EXPLODE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(splash=2.0)
    return Weapon(common, uncommon)

def create_mini_gun():
    common = CommonStats(
        name="Minigun",
        accuracy=15/360,
        range=8,
        damage=1,
        fire_rate=480,
        fire_mode=FireMode.AUTOMATIC,
        clip_size=120,
        reload_speed=4.0,
        bullet_size=0.15,
        bullet_color=(255, 255, 100),
        bullet_speed=10,
        ammo=480,
        specialization_type=WeaponSpecialization.ASSAULT,
        specialization_level=4,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(warm_up_time=2.0)
    return Weapon(common, uncommon)

def create_grenade():
    common = CommonStats(
        name="Grenade",
        accuracy=5/360,
        range=12,
        damage=25,
        fire_rate=30,
        fire_mode=FireMode.THROWN,
        clip_size=1,
        reload_speed=2.0,
        bullet_size=0.3,
        bullet_color=(0, 255, 0),
        bullet_speed=8,
        ammo=5,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=2,
        contact_effect=ContactEffect.NO_DAMAGE_BOUNCE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(splash=3.0, detonation_time=3.0, bounce_limit=100)
    return Weapon(common, uncommon)

def create_ricochet_pistol():
    common = CommonStats(
        name="Ricochet Pistol",
        accuracy=10/360,
        range=15,
        damage=1.5,
        fire_rate=120,
        fire_mode=FireMode.MANUAL,
        clip_size=15,
        reload_speed=2.5,
        bullet_size=0.2,
        bullet_color=(100, 100, 255),
        bullet_speed=10,
        ammo=None,
        specialization_type=WeaponSpecialization.PISTOLS,
        specialization_level=2,
        contact_effect=ContactEffect.DAMAGE_BOUNCE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(bounce_limit=2)
    return Weapon(common, uncommon)

def create_missile_striker():
    common = CommonStats(
        name="Missile Striker",
        accuracy=15/360,
        range=1000,
        damage=50,
        fire_rate=30,
        fire_mode=FireMode.ORBITAL,
        clip_size=1,
        reload_speed=4,
        bullet_size=0.8,
        bullet_color=(255, 150, 50),
        bullet_speed=4,
        ammo=3,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=5,
        contact_effect=ContactEffect.EXPLODE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(warm_up_time=2.0, splash=7.0, drop_height=600)
    return Weapon(common, uncommon)

def create_shotgun():
    common = CommonStats(
        name="Shotgun",
        accuracy=5/360,
        range=6,
        damage=8,
        fire_rate=60,
        fire_mode=FireMode.SHOTGUN,
        clip_size=6,
        reload_speed=3.0,
        bullet_size=0.1,
        bullet_color=(255, 200, 100),
        bullet_speed=8,
        ammo=24,
        specialization_type=WeaponSpecialization.SHOTGUNS,
        specialization_level=1,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(volley=8, spread=30)
    return Weapon(common, uncommon)

def create_flamethrower():
    common = CommonStats(
        name="Flamethrower",
        accuracy=25/360,
        range=4,
        damage=2,
        fire_rate=180,
        fire_mode=FireMode.SPRAY,
        clip_size=50,
        reload_speed=4.0,
        bullet_size=0.12,
        bullet_color=(255, 100, 0),
        bullet_speed=5,
        ammo=100,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=3,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.FIRE
    )
    uncommon = UncommonStats(volley=4, spread=50)
    return Weapon(common, uncommon)

def create_solar_death_beam():
    common = CommonStats(
        name="Solar Death Beam",
        accuracy=5/360,
        range=1000,
        damage=8,
        fire_rate=1,
        fire_mode=FireMode.ORBITAL_BEAM,
        clip_size=1,
        reload_speed=8.0,
        bullet_size=0.3,
        bullet_color=(74, 100, 200),
        bullet_speed=3,
        ammo=3,
        specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=4,
        contact_effect=ContactEffect.EXPLODE,
        damage_type=DamageType.FIRE
    )
    uncommon = UncommonStats(warm_up_time=2.0, splash=2.0, drop_height=800)
    unique = UniqueStats(beam_duration=5.0, beam_damage_tick=0.2)
    return Weapon(common, uncommon, unique)

def create_freeze_gun():
    common = CommonStats(
        name="Freeze Gun",
        accuracy=10/360,
        range=8,
        damage=1,
        fire_rate=120,
        fire_mode=FireMode.AUTOMATIC,
        clip_size=50,
        reload_speed=3.0,
        bullet_size=0.2,
        bullet_color=(173, 216, 230),
        bullet_speed=10,
        ammo=200,
        specialization_type=None,
        specialization_level=1,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.ICE
    )
    uncommon = UncommonStats(piercing=0)
    return Weapon(common, uncommon)

def create_ice_sprayer():
    common = CommonStats(
        name="Ice Sprayer",
        accuracy=20/360,
        range=5,
        damage=0.5,
        fire_rate=150,
        fire_mode=FireMode.SPRAY,
        clip_size=100,
        reload_speed=4.0,
        bullet_size=0.15,
        bullet_color=(135, 206, 250), # Light Sky Blue
        bullet_speed=12,
        ammo=300,
        specialization_type=None,
        specialization_level=1,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.ICE
    )
    uncommon = UncommonStats(pellets=5, spray_angle=15, piercing=0)
    return Weapon(common, uncommon)

def create_laser_beam():
    common = CommonStats(
        name="Laser Beam",
        accuracy=0,
        range=1000, # Very long range
        damage=2,
        fire_rate=60,
        fire_mode=FireMode.BEAM,
        clip_size=20,
        reload_speed=3.0,
        bullet_size=0.2, # Represents beam thickness
        bullet_color=(255, 0, 0), # Red
        bullet_speed=80, # Speed of the beam
        ammo=100,
        specialization_type=None,
        specialization_level=1,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.PHYSICAL
    )
    uncommon = UncommonStats(piercing=10000)
    return Weapon(common, uncommon)

def create_poison_dart_gun():
    common = CommonStats(
        name="Poison Dart Gun",
        accuracy=5/360,
        range=12,
        damage=10,  # Base damage for the poison DoT
        fire_rate=60,
        fire_mode=FireMode.SINGLE,
        clip_size=10,
        reload_speed=2.5,
        bullet_size=0.15,
        bullet_color=(0, 255, 0),  # Green
        bullet_speed=15,
        ammo=50,
        specialization_type=None,
        specialization_level=1,
        contact_effect=ContactEffect.PIERCE,
        damage_type=DamageType.POISON
    )
    uncommon = UncommonStats(piercing=0)
    return Weapon(common, uncommon)

# --- LEVEL 10 "RIDICULOUS" WEAPONS ---

def create_apocalypse_engine():
    """Calls down a cluster of poison bombs from the sky."""
    common = CommonStats(
        name="Apocalypse Engine",
        accuracy=15/360, range=1000, damage=40, fire_rate=20, fire_mode=FireMode.ORBITAL,
        clip_size=5, reload_speed=8.0, bullet_size=0.8, bullet_color=(107, 142, 35),
        bullet_speed=10, ammo=20, specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=10, contact_effect=ContactEffect.EXPLODE, damage_type=DamageType.POISON
    )
    uncommon = UncommonStats(splash=4.0)
    unique = UniqueStats(drop_height=1200)
    return Weapon(common, uncommon, unique)

def create_glacial_torrent():
    """Fires a wide cone of piercing ice shards."""
    common = CommonStats(
        name="Glacial Torrent",
        accuracy=20/360, range=10, damage=5, fire_rate=90, fire_mode=FireMode.SHOTGUN,
        clip_size=30, reload_speed=4.0, bullet_size=0.1, bullet_color=(175, 238, 238),
        bullet_speed=25, ammo=150, specialization_type=WeaponSpecialization.SHOTGUNS,
        specialization_level=10, contact_effect=ContactEffect.PIERCE, damage_type=DamageType.ICE
    )
    uncommon = UncommonStats(volley=15, spread=45, piercing=3)
    return Weapon(common, uncommon)

def create_serpents_breath():
    """Spews a cone of toxic gas that poisons enemies."""
    common = CommonStats(
        name="Serpent's Breath",
        accuracy=30/360, range=7, damage=8, fire_rate=200, fire_mode=FireMode.SPRAY,
        clip_size=150, reload_speed=5.0, bullet_size=0.2, bullet_color=(153, 204, 153),
        bullet_speed=8, ammo=400, specialization_type=WeaponSpecialization.ASSAULT,
        specialization_level=10, contact_effect=ContactEffect.PIERCE, damage_type=DamageType.POISON
    )
    uncommon = UncommonStats(volley=5, spread=25, piercing=0)
    return Weapon(common, uncommon)

def create_singularity_beam():
    """A continuous orbital beam that dramatically slows anything it touches."""
    common = CommonStats(
        name="Singularity Beam",
        accuracy=0, range=1000, damage=15, fire_rate=30, fire_mode=FireMode.ORBITAL_BEAM,
        clip_size=1, reload_speed=10.0, bullet_size=0, bullet_color=(240, 248, 255),
        bullet_speed=0, ammo=5, specialization_type=WeaponSpecialization.PRECISION,
        specialization_level=10, contact_effect=ContactEffect.PIERCE, damage_type=DamageType.ICE
    )
    uncommon = UncommonStats(warm_up_time=3.0, splash=3.0)
    unique = UniqueStats(beam_duration=10.0, beam_damage_tick=0.1)
    return Weapon(common, uncommon, unique)

def create_ricocheting_venom():
    """Fires poison darts that bounce relentlessly off walls."""
    common = CommonStats(
        name="Ricocheting Venom",
        accuracy=2/360, range=30, damage=12, fire_rate=180, fire_mode=FireMode.AUTOMATIC,
        clip_size=40, reload_speed=3.0, bullet_size=0.1, bullet_color=(85, 107, 47),
        bullet_speed=20, ammo=200, specialization_type=WeaponSpecialization.PISTOLS,
        specialization_level=10, contact_effect=ContactEffect.DAMAGE_BOUNCE, damage_type=DamageType.POISON
    )
    uncommon = UncommonStats(bounce_limit=8, piercing=0)
    return Weapon(common, uncommon)

def create_inferno_shotgun():
    """A shotgun that fires pellets that explode on impact."""
    common = CommonStats(
        name="Inferno Shotgun",
        accuracy=25/360, range=8, damage=25, fire_rate=60, fire_mode=FireMode.SHOTGUN,
        clip_size=12, reload_speed=4.5, bullet_size=0.1, bullet_color=(255, 69, 0),
        bullet_speed=15, ammo=60, specialization_type=WeaponSpecialization.SHOTGUNS,
        specialization_level=10, contact_effect=ContactEffect.EXPLODE, damage_type=DamageType.FIRE
    )
    uncommon = UncommonStats(volley=8, spread=30, splash=1.5)
    return Weapon(common, uncommon)

def create_the_kraken():
    """Unleashes a volley of homing poison missiles."""
    common = CommonStats(
        name="The Kraken",
        accuracy=45/360, range=25, damage=15, fire_rate=30, fire_mode=FireMode.SHOTGUN,
        clip_size=8, reload_speed=6.0, bullet_size=0.25, bullet_color=(0, 100, 0),
        bullet_speed=10, ammo=48, specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=10, contact_effect=ContactEffect.PIERCE, damage_type=DamageType.POISON
    )
    uncommon = UncommonStats(volley=8, spread=90, homing_angle=180, homing_time=3.0, piercing=1)
    return Weapon(common, uncommon)

def create_comets_fury():
    """Calls down a massive, high-damage projectile that freezes enemies in a large radius."""
    common = CommonStats(
        name="Comet's Fury",
        accuracy=10/360, range=1000, damage=150, fire_rate=10, fire_mode=FireMode.ORBITAL,
        clip_size=1, reload_speed=12.0, bullet_size=1.2, bullet_color=(224, 255, 255),
        bullet_speed=8, ammo=10, specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=10, contact_effect=ContactEffect.EXPLODE, damage_type=DamageType.ICE
    )
    uncommon = UncommonStats(splash=6.0)
    unique = UniqueStats(drop_height=1500)
    return Weapon(common, uncommon, unique)

def create_gatling_freezer():
    """A minigun that fires a rapid stream of slowing ice bullets."""
    common = CommonStats(
        name="Gatling Freezer",
        accuracy=20/360, range=15, damage=2, fire_rate=900, fire_mode=FireMode.AUTOMATIC,
        clip_size=300, reload_speed=7.0, bullet_size=0.08, bullet_color=(135, 206, 250),
        bullet_speed=22, ammo=900, specialization_type=WeaponSpecialization.ASSAULT,
        specialization_level=10, contact_effect=ContactEffect.PIERCE, damage_type=DamageType.ICE
    )
    uncommon = UncommonStats(piercing=1, warm_up_time=1.5)
    return Weapon(common, uncommon)

def create_world_ender():
    """A devastating orbital beam that blankets a large area with poison."""
    common = CommonStats(
        name="World Ender",
        accuracy=0, range=1000, damage=20, fire_rate=30, fire_mode=FireMode.ORBITAL_BEAM,
        clip_size=1, reload_speed=15.0, bullet_size=0, bullet_color=(0, 255, 0),
        bullet_speed=0, ammo=3, specialization_type=WeaponSpecialization.EXPLOSIVES,
        specialization_level=10, contact_effect=ContactEffect.PIERCE, damage_type=DamageType.POISON
    )
    uncommon = UncommonStats(warm_up_time=5.0, splash=5.0)
    unique = UniqueStats(beam_duration=15.0, beam_damage_tick=0.25)
    return Weapon(common, uncommon, unique) 