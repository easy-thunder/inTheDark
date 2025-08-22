from perlin_noise import PerlinNoise

TILE_SIZE = 40

class World:
    def __init__(self, seed):
        self.noise = PerlinNoise(seed=seed)
        self.tile_cache = {}
        # You can adjust these values to change the map's appearance
        # Lower threshold = more paths; Higher threshold = more walls
        self.threshold = 0.05 
        # Lower scale = larger, smoother features; Higher scale = smaller, rougher features
        self.scale = 0.05 

    def get_tile(self, x, y):
        # Check cache first to avoid re-calculating
        if (x, y) in self.tile_cache:
            return self.tile_cache[(x, y)]

        # Use Perlin noise to determine tile type
        noise_val = self.noise([x * self.scale, y * self.scale])
        
        # Ensure the starting area is always open for the player
        if -5 < x < 5 and -5 < y < 5:
            tile_type = ' '
        elif noise_val > self.threshold:
            tile_type = 'W' # Wall
        else:
            tile_type = ' ' # Path

        # Cache the result and return it
        self.tile_cache[(x, y)] = tile_type
        return tile_type 
    

# WORLD FUNCTIONS
def get_day_phase(elapsed_time):
    """
    Returns the current phase and an optional alpha value for lighting.
    """
    cycle_duration = 1200  # 20 minutes in seconds
    time_in_cycle = elapsed_time % cycle_duration

    if time_in_cycle < 120:
        phase = "dawn"
        # Alpha fades from 100 (dark) to 0 (bright)
        alpha = int(100 * (1 - time_in_cycle / 120))
    elif time_in_cycle < 600:
        phase = "day"
        alpha = 0
    elif time_in_cycle < 720:
        phase = "dusk"
        # Alpha fades from 0 to 100
        alpha = int(100 * ((time_in_cycle - 600) / 120))
    else:
        phase = "night"
        alpha = 240  # or up to 200 for maximum darkness

    return phase, alpha

