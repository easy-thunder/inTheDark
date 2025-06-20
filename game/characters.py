from game.weapons import create_rusty_pistol, create_rocket_launcher

class Character:
    def __init__(self, name, max_hp, speed, ability_points, armor=0, hp_regen=0, ap_regen=0, revival_time=5, weapons=None):
        self.name = name
        self.max_hp = max_hp
        self.speed = speed
        self.ability_points = ability_points
        self.armor = armor
        self.hp_regen = hp_regen
        self.ap_regen = ap_regen
        self.revival_time = revival_time
        self.weapons = weapons or []

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
    weapons=[create_rocket_launcher()]
) 