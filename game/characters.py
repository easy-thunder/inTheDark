from game.weapons import (
    create_rusty_pistol,
    create_rocket_launcher,
    create_mini_gun,
    create_grenade,
    create_ricochet_pistol,
    create_missile_striker,
    create_shotgun,
    create_flamethrower,
    create_solar_death_beam,
    create_freeze_gun,
    create_ice_sprayer,
    create_laser_beam,
    create_poison_dart_gun,
    # Ridiculous Weapons
    create_apocalypse_engine,
    create_glacial_torrent,
    create_serpents_breath,
    create_singularity_beam,
    create_ricocheting_venom,
    create_inferno_shotgun,
    create_the_kraken,
    create_comets_fury,
    create_gatling_freezer,
    create_world_ender,
    # New Batch
    create_wall_of_lead,
    create_absolute_sniper,
    create_assault_shotgun,
    create_classic_assault_rifle,
    create_toxic_assault_rifle,
    create_cryo_assault_rifle,
    create_incendiary_assault_rifle,
    create_ricochet_minigun,
    create_piercing_laser_smg,
    create_poison_spray_blaster,
    WeaponSpecialization,

    create_knockback_gun,
    create_combo_gun
)

DEFAULT_SPECIALIZATIONS = {
    WeaponSpecialization.PRECISION: 1,
    WeaponSpecialization.EXPLOSIVES: 1,
    WeaponSpecialization.PISTOLS: 1,
    WeaponSpecialization.ASSAULT: 1,
    WeaponSpecialization.SHOTGUNS: 1,
    WeaponSpecialization.MELEE: 1
}

class Character:
    def __init__(self, name, max_hp, speed, ability_points, armor=0, hp_regen=0, ap_regen=0, revival_time=5, weapons=None, specializations=None):
        self.name = name
        self.max_hp = max_hp
        self.speed = speed
        self.ability_points = ability_points
        self.armor = armor
        self.hp_regen = hp_regen
        self.ap_regen = ap_regen
        self.revival_time = revival_time
        self.weapons = weapons or []
        # Always set specializations
        self.specializations = dict(DEFAULT_SPECIALIZATIONS)
        if specializations:
            self.specializations.update(specializations)

# Default character: testy
TESTY = Character(
    name="testy",
    max_hp=50,
    speed=4,
    ability_points=30,
    armor=1,
    hp_regen=0.1,
    ap_regen=0.1,
    revival_time=5,
    weapons=[
        # --- Standard Weapons ---

        # --- New Batch: Toggle below ---

        create_solar_death_beam(),
        create_grenade(),
        create_ricochet_pistol(),
        create_gatling_freezer(),
        create_wall_of_lead(),
        create_serpents_breath()
    ],
    specializations={
        WeaponSpecialization.EXPLOSIVES: 5,
        WeaponSpecialization.ASSAULT: 4,
        WeaponSpecialization.SHOTGUNS: 1,
    }
)

def create_testy():
    """Create the TESTY character for testing weapons."""
    weapons = [
        create_knockback_gun(),  # Test knockback alone
        create_combo_gun(),      # Test combined effects
        create_shotgun(),
        # ... rest of weapons commented out for testing ...
    ]
    return Character("TESTY", "The Weapon Tester", weapons=weapons) 