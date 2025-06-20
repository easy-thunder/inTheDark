import math

class DirectApproach:
    """A movement profile where the creature moves directly towards the closest target."""
    def move(self, creature, targets):
        if not targets:
            return

        # Find closest target (player)
        closest_target = min(targets, key=lambda t: math.hypot(t.rect.centerx - creature.rect.centerx, t.rect.centery - creature.rect.centery))
        
        dx = closest_target.rect.centerx - creature.rect.centerx
        dy = closest_target.rect.centery - creature.rect.centery
        dist = math.hypot(dx, dy)
        
        # Move if not already overlapping with the target
        if dist > (creature.width / 2):
            # Normalize the vector
            dx = dx / dist
            dy = dy / dist
            
            # Update creature's float position
            creature.x += dx * creature.speed
            creature.y += dy * creature.speed
            
            # Update the rect for collision and drawing
            creature.rect.x = int(creature.x)
            creature.rect.y = int(creature.y) 