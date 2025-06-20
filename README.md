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

- **Python:** 3.13 (or compatible 3.x version)
- **Pygame:** 2.6.1
- **perlin-noise:** 1.13

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

---

## Project Structure

- `game/characters.py` — Character definitions
- `game/creatures.py` — Creature/enemy definitions and factory functions
- `game/ai/movement.py` — AI movement profiles
- `game/ai/attacks.py` — AI attack profiles
- `game/world.py` — World generation logic
- `game/stats/` — Persistent stats and tracking
- `assets/fonts/` — Fonts for UI

---

## Notes

- This is a continuous project—expect frequent changes and new features!
- For best results, use the latest version of Python 3.13 and Pygame.
- If you encounter import errors, always run the game as a module:  
  `python -m game.main` from the project root.

---

## Contributing

Pull requests and suggestions are welcome!  
Feel free to fork and experiment.

---

## License

MIT License