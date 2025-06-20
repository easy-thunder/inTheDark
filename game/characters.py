class Character:
    def __init__(self, name, max_hp, speed, ability_points):
        self.name = name
        self.max_hp = max_hp
        self.speed = speed
        self.ability_points = ability_points

# Default character: testy
TESTY = Character(name="testy", max_hp=50, speed=4, ability_points=30) 