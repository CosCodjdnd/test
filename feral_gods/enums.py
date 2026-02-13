"""Enumerations and constants for the Feral Gods RPG."""

from enum import Enum


class GodName(Enum):
    """The eight gods of the Feral Gods world."""
    OPHIDIA = "Ophidia"
    GALANTH = "Galanth"
    PELAGON = "Pelagon"
    MYRIAD = "Myriad"
    KARN = "Karn"
    PACHYMOS = "Pachymos"
    SKULK = "Skulk"
    SAGAX = "Sagax"


class AbilityType(Enum):
    """Whether an ability is passive (always active) or active (willed)."""
    PASSIVE = "passive"
    ACTIVE = "active"


class DamageType(Enum):
    """Types of damage in combat."""
    PHYSICAL = "physical"
    FIRE = "fire"
    WIND = "wind"
    WATER = "water"
    POISON = "poison"
    PSYCHIC = "psychic"
    SHADOW = "shadow"
    SWARM = "swarm"


class Rarity(Enum):
    """Rarity of a spirit companion."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"


class StatusEffect(Enum):
    """Status effects that can be applied in combat."""
    POISONED = "poisoned"
    BURNING = "burning"
    FROZEN = "frozen"
    STUNNED = "stunned"
    BLINDED = "blinded"
    BERSERKER = "berserker"
    SHIELDED = "shielded"
    REGENERATING = "regenerating"
    INTIMIDATED = "intimidated"
    HIDDEN = "hidden"


# Rarity multipliers for spirit power scaling
RARITY_MULTIPLIERS = {
    Rarity.COMMON: 1.0,
    Rarity.UNCOMMON: 1.25,
    Rarity.RARE: 1.5,
    Rarity.LEGENDARY: 2.0,
}

# Diviner's Mark probability
DIVINERS_MARK_CHANCE = 1 / 1000

# Ceremony seasons
CEREMONY_SEASONS = ["Spring", "Autumn"]
CEREMONY_AGE = 16
