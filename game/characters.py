class Character:
    def __init__(self, name, max_hp, speed, ability_points, armor=0, hp_regen=0, ap_regen=0):
        self.name = name
        self.max_hp = max_hp
        self.speed = speed
        self.ability_points = ability_points
        self.armor = armor
        self.hp_regen = hp_regen
        self.ap_regen = ap_regen

# Default character: testy
TESTY = Character(
    name="testy",
    max_hp=50,
    speed=4,
    ability_points=30,
    armor=1,
    hp_regen=0.1,
    ap_regen=0.1
) 