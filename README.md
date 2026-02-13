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

```bash
python main.py
```

### Game Modes

1. **New Game** — Create a character, undergo the Ceremony to receive your spirit companion, then battle enemies to gain experience and level up.
2. **Quick Battle** — Watch two auto-generated characters fight.
3. **Lore** — Learn about the eight gods and their domains.

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
└── game.py            # Main game loop and UI
tests/
└── test_feral_gods.py # 58 tests covering all game mechanics
main.py                # Entry point
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/ -v
```
