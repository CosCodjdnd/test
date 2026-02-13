"""The Ceremony system for the Feral Gods RPG.

The Ceremony occurs twice yearly (Spring and Autumn) for 16-year-olds.
Participants visit god shrines and face challenges until gifted a spirit.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .enums import GodName, Rarity, DIVINERS_MARK_CHANCE
from .gods import God, Spirit, ALL_GODS, ALL_SPIRITS, GODS_BY_NAME
from .characters import Character


@dataclass
class ShrineChallenge:
    """A challenge at a god's shrine during the Ceremony."""
    god: God
    name: str
    description: str
    difficulty: int  # 1-10
    stat_tested: str  # "strength", "intelligence", "speed", "willpower", "stealth", "empathy"

    def attempt(self, character: Character) -> tuple[bool, str]:
        """Attempt the shrine challenge. Returns (success, message)."""
        stat_map = {
            "strength": character.base_attack,
            "intelligence": character.base_accuracy,
            "speed": character.base_speed,
            "willpower": character.base_defense,
            "stealth": character.base_speed,
            "empathy": character.base_defense,
        }
        stat_value = stat_map.get(self.stat_tested, 10)
        # Roll against difficulty, stat helps
        roll = random.randint(1, 20) + stat_value // 3
        threshold = self.difficulty + 5

        if roll >= threshold:
            return True, f"  {character.name} overcomes the challenge of {self.name}!"
        else:
            return False, f"  {character.name} struggles with the challenge of {self.name}."


# ---------------------------------------------------------------------------
# Shrine definitions (each god has a thematic shrine)
# ---------------------------------------------------------------------------

SHRINE_CHALLENGES: dict[str, ShrineChallenge] = {
    "Ophidia": ShrineChallenge(
        god=GODS_BY_NAME["Ophidia"],
        name="The Serpent's Pit",
        description="Navigate a dark cavern filled with hissing serpents and volcanic heat. "
                    "Only the cunning and adaptive survive.",
        difficulty=6,
        stat_tested="willpower",
    ),
    "Galanth": ShrineChallenge(
        god=GODS_BY_NAME["Galanth"],
        name="The Tower Peak",
        description="Ascend a towering spire above the clouds. The wind howls and the "
                    "path narrows—only those with vision and courage reach the top.",
        difficulty=5,
        stat_tested="speed",
    ),
    "Pelagon": ShrineChallenge(
        god=GODS_BY_NAME["Pelagon"],
        name="The Abyssal Pool",
        description="Dive into a deep underground pool. In the crushing dark, "
                    "find the pearl of Pelagon before your breath runs out.",
        difficulty=7,
        stat_tested="strength",
    ),
    "Myriad": ShrineChallenge(
        god=GODS_BY_NAME["Myriad"],
        name="The Hive Labyrinth",
        description="Enter a maze of honeycombed tunnels. Work with the swarm, "
                    "not against it, to find the path through.",
        difficulty=5,
        stat_tested="empathy",
    ),
    "Karn": ShrineChallenge(
        god=GODS_BY_NAME["Karn"],
        name="The Hunting Grounds",
        description="Track and tag a spirit beast through dense forest. "
                    "Only true predators with pack instinct succeed.",
        difficulty=6,
        stat_tested="speed",
    ),
    "Pachymos": ShrineChallenge(
        god=GODS_BY_NAME["Pachymos"],
        name="The Stone Circle",
        description="Endure a trial of strength and patience in a sacred stone circle. "
                    "Hold the weight of the world on your shoulders.",
        difficulty=7,
        stat_tested="strength",
    ),
    "Skulk": ShrineChallenge(
        god=GODS_BY_NAME["Skulk"],
        name="The Shadow Maze",
        description="Sneak through a labyrinth of shifting shadows and traps. "
                    "Only the cleverest and stealthiest escape.",
        difficulty=6,
        stat_tested="stealth",
    ),
    "Sagax": ShrineChallenge(
        god=GODS_BY_NAME["Sagax"],
        name="The Riddler's Sanctum",
        description="Answer three riddles posed by a spectral sphinx. "
                    "Fail, and you are ejected from the shrine.",
        difficulty=8,
        stat_tested="intelligence",
    ),
}


def _select_spirit(god: God, has_mark: bool) -> Spirit:
    """Select a spirit from the god's roster, weighted by rarity."""
    spirits = ALL_SPIRITS[god.name.value]
    if has_mark:
        # Diviner's Mark greatly increases chance of rare spirit
        weights = []
        for s in spirits:
            if s.rarity == Rarity.LEGENDARY:
                weights.append(20)
            elif s.rarity == Rarity.RARE:
                weights.append(40)
            elif s.rarity == Rarity.UNCOMMON:
                weights.append(25)
            else:
                weights.append(15)
    else:
        weights = []
        for s in spirits:
            if s.rarity == Rarity.LEGENDARY:
                weights.append(2)
            elif s.rarity == Rarity.RARE:
                weights.append(8)
            elif s.rarity == Rarity.UNCOMMON:
                weights.append(25)
            else:
                weights.append(65)

    return random.choices(spirits, weights=weights, k=1)[0]


class Ceremony:
    """The Ceremony where 16-year-olds receive their spirit companions."""

    def __init__(self, season: str = "Spring") -> None:
        self.season = season
        self.shrines_visited: list[str] = []
        self.log: list[str] = []

    def run_ceremony(self, character: Character, shrine_order: list[str] | None = None) -> Spirit | None:
        """Run the ceremony for a character.

        Args:
            character: The 16-year-old participating.
            shrine_order: Order to visit shrines, or None for random.

        Returns:
            The spirit received, or None if ungifted.
        """
        self.log = [
            f"\n{'='*50}",
            f"THE CEREMONY OF {self.season.upper()}",
            f"{'='*50}",
            f"\n{character.name} begins the sacred journey...\n",
        ]

        if shrine_order is None:
            gods = list(SHRINE_CHALLENGES.keys())
            random.shuffle(gods)
            shrine_order = gods

        for god_name in shrine_order:
            if god_name in self.shrines_visited:
                continue

            challenge = SHRINE_CHALLENGES[god_name]
            self.shrines_visited.append(god_name)

            self.log.append(f"\n--- Shrine of {god_name}: {challenge.name} ---")
            self.log.append(f"  {challenge.description}")

            success, message = challenge.attempt(character)
            self.log.append(message)

            if success:
                god = GODS_BY_NAME[god_name]
                spirit = _select_spirit(god, character.has_diviners_mark)
                character.receive_spirit(spirit)

                self.log.append(f"\n  The light of {god_name} fills {character.name}!")
                self.log.append(f"  A {spirit.name} spirit materializes—visible only to {character.name}.")
                self.log.append(f"  Rarity: {spirit.rarity.value}")
                if spirit.physical_traits:
                    self.log.append(f"  Physical changes: {', '.join(spirit.physical_traits)}")
                self.log.append(f"\n  {character.name} has been blessed by {god_name}!")

                return spirit

        # If no shrine grants a spirit
        self.log.append(f"\n  {character.name} completes the journey without receiving a spirit.")
        self.log.append("  They are... ungifted. Perhaps their time will come.")
        character.is_ungifted = True
        return None

    def run_auto_ceremony(self, character: Character) -> Spirit | None:
        """Run a fully automated ceremony with random shrine order."""
        return self.run_ceremony(character)
