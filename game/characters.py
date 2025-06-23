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
    WeaponSpecialization
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
        create_ricochet_pistol(),        # --- Ridiculous Weapons ---
        # create_apocalypse_engine(),
        create_ricocheting_venom(),
        create_poison_dart_gun(),
        create_solar_death_beam(),
        # create_the_kraken(),
        # create_comets_fury(),

    ],
    specializations={
        WeaponSpecialization.EXPLOSIVES: 5,
        WeaponSpecialization.ASSAULT: 4,
        WeaponSpecialization.SHOTGUNS: 1,
    }
) 