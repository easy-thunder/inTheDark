import json
import os
import math

class GameStats:
    """A class to manage game statistics."""
    def __init__(self, stats_file='game/stats/game_stats.json'):
        """Initialize the stats."""
        self.stats_file = stats_file
        self.record_distance = 0
        self.record_time = 0
        self.load_records()

    def load_records(self):
        """Load record distance and time from a file if it exists."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    stats = json.load(f)
                    self.record_distance = stats.get('record_distance', 0)
                    self.record_time = stats.get('record_time', 0)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or can't be read, start with default stats
                self.record_distance = 0
                self.record_time = 0

    def save_records(self, current_game_time, current_max_distance):
        """Save the updated records to the file."""
        os.makedirs(os.path.dirname(self.stats_file), exist_ok=True)
        # Update records if the current game's stats are better
        if current_max_distance > self.record_distance:
            self.record_distance = current_max_distance
        if current_game_time > self.record_time:
            self.record_time = current_game_time
        
        stats = {
            'record_distance': self.record_distance,
            'record_time': self.record_time
        }
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f)

    def update_max_distance(self, player_pos, start_pos):
        """Calculate and update the maximum distance from the start."""
        distance = math.sqrt((player_pos[0] - start_pos[0])**2 + (player_pos[1] - start_pos[1])**2)
        if distance > self.record_distance:
            self.record_distance = distance 