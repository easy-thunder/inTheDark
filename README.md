# In The Dark

A procedurally generated, horror-themed, top-down multiplayer game built with Python and Pygame.  
This is a continuous, evolving project—new features and creatures are added regularly!

---


## Features

- Procedurally generated, infinite world
- Modular character and creature system
- Local multiplayer support (WASD and Arrow keys)
- Modular AI for movement and attacks
- Regeneration, armor, and ability points
- Clean, scalable UI
- Designed for easy future expansion

---

## Requirements

- Python 3.8 or newer (Python 3.13+ recommended)
- [pygame](https://www.pygame.org/) (version 2.6.1 or newer)
- [perlin-noise](https://pypi.org/project/perlin-noise/) (version 1.13 or newer)

Install dependencies with:
```bash
pip install -r requirements.txt
```

---

## How to Run

From the root of the project, start the game with:
```bash
python -m game.main
```
This ensures all imports work correctly.

---

## Controls

- **Player 1:** WASD
- **Player 2:** Arrow keys
- "space" key or left click to fire weapons
- "R" to reload
- 1-6 to swap weapons

---

## Project Structure

- `game/characters.py` — Character definitions
- `game/creatures.py` — Creature/enemy definitions and factory functions
- `game/ai/movement.py` — AI movement profiles
- `game/ai/attacks.py` — AI attack profiles
- `game/world.py` — World generation logic
- `game/stats/` — Persistent stats and tracking

---

## Notes

- This game is currently single-player. You can enable multiplayer by going to the players array in main.py and uncommenting out the second player. There is no targeting system for him yet though.

## Future Improvements
This project is under active development, and there are several exciting features planned for future releases:

- **Enhanced Visuals:** Import custom images and use mesh-based outlines for creatures and characters to create a more visually appealing and dynamic UI.
- **Dynamic Enemy Scaling:** Implement progressive enemy spawning, with increasing difficulty as time passes and as players venture further from the starting area.
- **Barriers and Cover:** Add destructible and indestructible barriers that both players and AI can use for cover and tactical gameplay.
- **Cave and Room System:** Introduce a cave system with hand-crafted rooms interspersed within the procedurally generated world, providing unique and memorable exploration experiences.
- **Day/Night Cycle:** Add a day and night system, including limited player vision at night and the use of flashlights and lanterns to navigate the darkness.
- **Abilities and Crowd Control:** Develop an abilities system, allowing players to deploy walls, traps, and other crowd control effects, with each character having unique abilities and playstyles.

These improvements aim to create a richer, more immersive, and replayable experience for players.

---

## Contributing

Pull requests and suggestions are welcome!  
Feel free to fork and experiment.

---

## License

MIT License