# Feral Gods — A Turn-Based RPG

A turn-based RPG set in the world of Feral Gods, where each person receives a spirit companion from one of eight divine gods during a sacred Ceremony.

## The Eight Gods

| God | Title | Domain |
|-----|-------|--------|
| **Ophidia** | Scales and Fire | Reptiles, cold-blooded power |
| **Galanth** | Sky and Wind | Flight and perspective |
| **Pelagon** | The Deep | Ocean pressure and fluidity |
| **Myriad** | The Swarm | Insects, arachnids, hive minds |
| **Karn** | The Hunt | Predators and pack tactics |
| **Pachymos** | The Tank | Heavy defense and stamina |
| **Skulk** | Shadows | Stealth, nocturnal creatures, trickery |
| **Sagax** | The Mind | Intelligence and mystery |

## How to Play

### 2D Visual Mode (Recommended)

```bash
pip install pygame
python run_gui.py
```

Launches a full 2D visual game inspired by classic JRPGs (Final Fantasy, Dragon Quest) with:
- **Tile-based overworld** — Walk around with arrow keys / WASD, explore multiple maps
- **Visual turn-based combat** — Side-view battles with animated sprites, HP/energy bars, and command menus
- **Character creation** — Name entry, Diviner's Mark check, and animated Ceremony
- **Procedural pixel art** — All sprites generated at runtime, no external assets needed

#### Controls
| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move (overworld) / Navigate menus |
| Enter / Z / Space | Confirm / Select |
| Escape / X | Back / Pause menu |

### Text Mode

```bash
python main.py
```

### Game Modes

1. **New Game** — Create a character, undergo the Ceremony to receive your spirit companion, then explore the world, battle enemies, and level up.
2. **Quick Battle** — Watch two auto-generated characters fight in a visual battle.
3. **Lore** — Browse the eight gods, their spirits, and abilities.

### The Ceremony

Twice yearly (Spring/Autumn), 16-year-olds journey to god shrines and face challenges. Visit shrines in any order until a god grants you a spirit companion. Those with the rare **Diviner's Mark** (1/1000 births) have greater potential for powerful spirits.

### Combat

Turn-based combat with:
- **Basic Attack** — A standard physical strike
- **Abilities** — Active abilities from your god (cost energy, may have cooldowns)
- **Rest** — Recover energy
- **Passive abilities** — Always-active bonuses from your spirit
- **Status effects** — Poison, burn, stun, berserker rage, shields, and more

### Spirit Companions

Each spirit has a **rarity** that affects power:
- Common (1.0x), Uncommon (1.25x), Rare (1.5x), Legendary (2.0x)

Spirits grant physical traits (e.g., slitted eyes, scales, feathers) and magical abilities tied to their god.

## Project Structure

```
feral_gods/
├── __init__.py        # Package init
├── enums.py           # Enumerations and constants
├── abilities.py       # All ability definitions (6 per god)
├── gods.py            # God and Spirit definitions
├── characters.py      # Character model and factory functions
├── combat.py          # Turn-based combat engine
├── ceremony.py        # The Ceremony system
├── game.py            # CLI game loop
└── gui/               # 2D Pygame visual interface
    ├── __init__.py
    ├── constants.py   # Colors, sizes, tuning values
    ├── sprites.py     # Procedural pixel-art sprite generation
    ├── maps.py        # Tile-based overworld maps
    ├── ui.py          # Reusable UI drawing helpers
    ├── battle_scene.py  # Visual turn-based combat scene
    ├── overworld.py   # Top-down exploration scene
    ├── menu_scenes.py # Main menu, character creation, lore
    └── main_gui.py    # GUI entry point
tests/
├── test_feral_gods.py # 58 core game mechanic tests
└── test_gui.py        # 40 GUI module tests
main.py                # CLI entry point
run_gui.py             # 2D visual game entry point
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```
