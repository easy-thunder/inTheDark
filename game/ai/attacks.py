import pygame

class MeleeCollisionAttack:
    """An attack profile that deals damage on collision with a cooldown."""
    def __init__(self, cooldown=1000): # Cooldown in milliseconds
        self.cooldown = cooldown
        # Dictionary to track cooldown per creature-target pair
        # This ensures one creature can attack multiple targets, each on their own timer
        self.last_attack_times = {} 

    def execute(self, creature, targets):
        now = pygame.time.get_ticks()
        for target in targets:
            if creature.rect.colliderect(target.rect):
                # Unique key for each creature-target pair
                attack_key = (id(creature), id(target))
                last_attack_time = self.last_attack_times.get(attack_key, 0)
                
                if now - last_attack_time > self.cooldown:
                    # The target (player) needs a 'take_damage' method
                    target.take_damage(creature.damage)
                    self.last_attack_times[attack_key] = now 