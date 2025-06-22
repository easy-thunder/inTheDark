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

@dataclass
class CommonStats:
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
        accuracy=5/360,
        range=1000,
        damage=8,
        fire_rate=1,
        fire_mode=FireMode.ORBITAL_BEAM,
        clip_size=1,
        reload_speed=8.0,
        bullet_size=0.3,
        bullet_color=(255, 255, 100),
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