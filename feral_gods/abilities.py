"""Ability definitions for all gods in the Feral Gods RPG."""

from __future__ import annotations

from dataclasses import dataclass, field

from .enums import AbilityType, DamageType, StatusEffect


@dataclass
class Ability:
    """A magical ability granted by a spirit companion."""
    name: str
    description: str
    ability_type: AbilityType
    damage: int = 0
    healing: int = 0
    energy_cost: int = 0
    cooldown: int = 0
    damage_type: DamageType = DamageType.PHYSICAL
    status_effect: StatusEffect | None = None
    status_duration: int = 0
    accuracy: int = 100  # percentage
    defense_bonus: int = 0
    speed_bonus: int = 0

    def is_offensive(self) -> bool:
        return self.damage > 0

    def is_supportive(self) -> bool:
        return self.healing > 0 or self.defense_bonus > 0

    def can_use(self, current_energy: int) -> bool:
        return current_energy >= self.energy_cost


# ---------------------------------------------------------------------------
# OPHIDIA abilities (Scales and Fire)
# ---------------------------------------------------------------------------

REPTILIAN_SKIN = Ability(
    name="Reptilian Skin",
    description="Scales harden, reducing incoming physical damage.",
    ability_type=AbilityType.PASSIVE,
    defense_bonus=5,
    accuracy=0,
)

THERMAL_VISION = Ability(
    name="Thermal Vision",
    description="See heat signatures, boosting accuracy against hidden foes.",
    ability_type=AbilityType.PASSIVE,
    accuracy=15,  # bonus
)

VENOMOUS_BITE = Ability(
    name="Venomous Bite",
    description="Strike with sharpened teeth, injecting venom.",
    ability_type=AbilityType.ACTIVE,
    damage=25,
    energy_cost=15,
    damage_type=DamageType.POISON,
    status_effect=StatusEffect.POISONED,
    status_duration=3,
    accuracy=90,
)

FIRE_BREATH = Ability(
    name="Fire Breath",
    description="Unleash a torrent of flame from deep within.",
    ability_type=AbilityType.ACTIVE,
    damage=40,
    energy_cost=30,
    damage_type=DamageType.FIRE,
    status_effect=StatusEffect.BURNING,
    status_duration=2,
    accuracy=85,
    cooldown=2,
)

SCALE_ARMOR = Ability(
    name="Scale Armor",
    description="Reinforce natural armor with thick overlapping scales.",
    ability_type=AbilityType.ACTIVE,
    defense_bonus=15,
    energy_cost=20,
    cooldown=3,
)

TAIL_SWEEP = Ability(
    name="Tail Sweep",
    description="A powerful sweep that can stun opponents.",
    ability_type=AbilityType.ACTIVE,
    damage=20,
    energy_cost=10,
    status_effect=StatusEffect.STUNNED,
    status_duration=1,
    accuracy=80,
)

# ---------------------------------------------------------------------------
# GALANTH abilities (Sky and Wind)
# ---------------------------------------------------------------------------

TELESCOPIC_SIGHT = Ability(
    name="Telescopic Sight",
    description="Enhanced vision grants superior accuracy.",
    ability_type=AbilityType.PASSIVE,
    accuracy=20,  # bonus
)

HOLLOW_BONES = Ability(
    name="Hollow Bones",
    description="Lighter frame grants increased speed.",
    ability_type=AbilityType.PASSIVE,
    speed_bonus=10,
    accuracy=0,
)

GUST_SLASH = Ability(
    name="Gust Slash",
    description="Razor-sharp wind cuts through the air.",
    ability_type=AbilityType.ACTIVE,
    damage=30,
    energy_cost=15,
    damage_type=DamageType.WIND,
    accuracy=95,
)

UPDRAFT = Ability(
    name="Updraft",
    description="Create a powerful updraft to levitate and evade attacks.",
    ability_type=AbilityType.ACTIVE,
    defense_bonus=20,
    speed_bonus=15,
    energy_cost=20,
    cooldown=2,
)

PHOENIX_FLAME = Ability(
    name="Phoenix Flame",
    description="Healing fire that restores vitality.",
    ability_type=AbilityType.ACTIVE,
    healing=35,
    energy_cost=25,
    damage_type=DamageType.FIRE,
    status_effect=StatusEffect.REGENERATING,
    status_duration=2,
    cooldown=3,
)

DIVE_STRIKE = Ability(
    name="Dive Strike",
    description="Plunge from the sky with devastating force.",
    ability_type=AbilityType.ACTIVE,
    damage=45,
    energy_cost=30,
    damage_type=DamageType.WIND,
    accuracy=80,
    cooldown=2,
)

# ---------------------------------------------------------------------------
# PELAGON abilities (The Deep)
# ---------------------------------------------------------------------------

GILLS = Ability(
    name="Gills",
    description="Breathe underwater and resist water-based attacks.",
    ability_type=AbilityType.PASSIVE,
    defense_bonus=3,
    accuracy=0,
)

CRUSH_RESISTANCE = Ability(
    name="Crush Resistance",
    description="Body adapted to deep pressure, reducing physical damage.",
    ability_type=AbilityType.PASSIVE,
    defense_bonus=8,
    accuracy=0,
)

TIDAL_SURGE = Ability(
    name="Tidal Surge",
    description="Crash a wave of water into the enemy.",
    ability_type=AbilityType.ACTIVE,
    damage=30,
    energy_cost=15,
    damage_type=DamageType.WATER,
    accuracy=90,
)

WHIRLPOOL = Ability(
    name="Whirlpool",
    description="Trap the enemy in a spinning vortex.",
    ability_type=AbilityType.ACTIVE,
    damage=20,
    energy_cost=20,
    damage_type=DamageType.WATER,
    status_effect=StatusEffect.STUNNED,
    status_duration=2,
    accuracy=85,
    cooldown=3,
)

INK_CLOUD = Ability(
    name="Ink Cloud",
    description="Spray blinding ink to reduce enemy accuracy.",
    ability_type=AbilityType.ACTIVE,
    energy_cost=10,
    status_effect=StatusEffect.BLINDED,
    status_duration=2,
    accuracy=90,
)

CRUSHING_TENTACLE = Ability(
    name="Crushing Tentacle",
    description="A massive tentacle slam with immense pressure.",
    ability_type=AbilityType.ACTIVE,
    damage=50,
    energy_cost=35,
    damage_type=DamageType.WATER,
    accuracy=75,
    cooldown=3,
)

# ---------------------------------------------------------------------------
# MYRIAD abilities (The Swarm)
# ---------------------------------------------------------------------------

CHITIN_PLATING = Ability(
    name="Chitin Plating",
    description="Exoskeletal armor reduces incoming damage.",
    ability_type=AbilityType.PASSIVE,
    defense_bonus=7,
    accuracy=0,
)

VIBRATION_SENSE = Ability(
    name="Vibration Sense",
    description="Detect movement through ground vibrations.",
    ability_type=AbilityType.PASSIVE,
    accuracy=10,  # bonus
)

SWARM_STRIKE = Ability(
    name="Swarm Strike",
    description="Call a swarm of insects to assault the enemy.",
    ability_type=AbilityType.ACTIVE,
    damage=25,
    energy_cost=15,
    damage_type=DamageType.SWARM,
    accuracy=95,
)

STINGER_JAB = Ability(
    name="Stinger Jab",
    description="Poison jab with a barbed stinger.",
    ability_type=AbilityType.ACTIVE,
    damage=20,
    energy_cost=10,
    damage_type=DamageType.POISON,
    status_effect=StatusEffect.POISONED,
    status_duration=3,
    accuracy=90,
)

HIVE_SHIELD = Ability(
    name="Hive Shield",
    description="Summon a living shield of swarming insects.",
    ability_type=AbilityType.ACTIVE,
    defense_bonus=20,
    energy_cost=20,
    cooldown=3,
)

COLONY_TELEPATHY = Ability(
    name="Colony Telepathy",
    description="Link minds with allies, boosting coordination.",
    ability_type=AbilityType.ACTIVE,
    accuracy=25,  # team bonus
    speed_bonus=10,
    energy_cost=15,
    cooldown=2,
)

# ---------------------------------------------------------------------------
# KARN abilities (The Hunt)
# ---------------------------------------------------------------------------

RETRACTABLE_CLAWS = Ability(
    name="Retractable Claws",
    description="Sharp claws ready for combat at all times.",
    ability_type=AbilityType.PASSIVE,
    damage=5,  # passive bonus to attacks
    accuracy=0,
)

TRACKING_SCENT = Ability(
    name="Tracking Scent",
    description="Enhanced smell reveals hidden enemies.",
    ability_type=AbilityType.PASSIVE,
    accuracy=10,
)

FERAL_SLASH = Ability(
    name="Feral Slash",
    description="A savage claw attack fueled by predatory instinct.",
    ability_type=AbilityType.ACTIVE,
    damage=30,
    energy_cost=12,
    accuracy=90,
)

PACK_HOWL = Ability(
    name="Pack Howl",
    description="A terrifying howl that intimidates enemies.",
    ability_type=AbilityType.ACTIVE,
    energy_cost=15,
    status_effect=StatusEffect.INTIMIDATED,
    status_duration=2,
    accuracy=85,
)

BERSERKER_RAGE = Ability(
    name="Berserker Rage",
    description="Enter a frenzied state, boosting damage but lowering defense.",
    ability_type=AbilityType.ACTIVE,
    damage=15,  # bonus to next attacks
    energy_cost=20,
    status_effect=StatusEffect.BERSERKER,
    status_duration=3,
    cooldown=4,
)

PREDATOR_POUNCE = Ability(
    name="Predator Pounce",
    description="Leap onto prey with crushing force.",
    ability_type=AbilityType.ACTIVE,
    damage=40,
    energy_cost=25,
    accuracy=80,
    cooldown=2,
)

# ---------------------------------------------------------------------------
# PACHYMOS abilities (The Tank)
# ---------------------------------------------------------------------------

STONESKIN = Ability(
    name="Stoneskin",
    description="Skin hardens to stone, greatly reducing damage.",
    ability_type=AbilityType.PASSIVE,
    defense_bonus=12,
    accuracy=0,
)

TIRELESS = Ability(
    name="Tireless",
    description="Endless stamina allows sustained effort.",
    ability_type=AbilityType.PASSIVE,
    speed_bonus=3,
    accuracy=0,
)

GROUND_SLAM = Ability(
    name="Ground Slam",
    description="Slam the ground with immense force, shaking all enemies.",
    ability_type=AbilityType.ACTIVE,
    damage=35,
    energy_cost=20,
    accuracy=85,
    status_effect=StatusEffect.STUNNED,
    status_duration=1,
)

BARRIER = Ability(
    name="Barrier",
    description="Erect a magical barrier that absorbs damage.",
    ability_type=AbilityType.ACTIVE,
    defense_bonus=25,
    energy_cost=25,
    status_effect=StatusEffect.SHIELDED,
    status_duration=3,
    cooldown=4,
)

STAMPEDE = Ability(
    name="Stampede",
    description="Charge with the force of a herd.",
    ability_type=AbilityType.ACTIVE,
    damage=45,
    energy_cost=30,
    accuracy=80,
    cooldown=3,
)

TRUTH_SEEING = Ability(
    name="Truth Seeing",
    description="See through deception, revealing hidden enemies and dispelling illusions.",
    ability_type=AbilityType.ACTIVE,
    accuracy=30,
    energy_cost=15,
    cooldown=2,
)

# ---------------------------------------------------------------------------
# SKULK abilities (Shadows)
# ---------------------------------------------------------------------------

NIGHT_VISION = Ability(
    name="Night Vision",
    description="See perfectly in darkness.",
    ability_type=AbilityType.PASSIVE,
    accuracy=10,
)

SOUND_SUPPRESSION = Ability(
    name="Sound Suppression",
    description="Move silently, harder to detect.",
    ability_type=AbilityType.PASSIVE,
    speed_bonus=5,
    accuracy=0,
)

SHADOW_STRIKE = Ability(
    name="Shadow Strike",
    description="Attack from the shadows with devastating precision.",
    ability_type=AbilityType.ACTIVE,
    damage=35,
    energy_cost=15,
    damage_type=DamageType.SHADOW,
    accuracy=95,
)

VANISH = Ability(
    name="Vanish",
    description="Disappear into shadows, becoming nearly invisible.",
    ability_type=AbilityType.ACTIVE,
    energy_cost=20,
    status_effect=StatusEffect.HIDDEN,
    status_duration=2,
    cooldown=3,
)

LUCK_MANIPULATION = Ability(
    name="Luck Manipulation",
    description="Bend fortune to your favor, boosting all stats briefly.",
    ability_type=AbilityType.ACTIVE,
    accuracy=15,
    defense_bonus=10,
    speed_bonus=10,
    energy_cost=25,
    cooldown=4,
)

ILLUSION = Ability(
    name="Illusion",
    description="Create a deceptive image to confuse the enemy.",
    ability_type=AbilityType.ACTIVE,
    energy_cost=15,
    status_effect=StatusEffect.BLINDED,
    status_duration=2,
    accuracy=85,
    cooldown=2,
)

# ---------------------------------------------------------------------------
# SAGAX abilities (The Mind)
# ---------------------------------------------------------------------------

TELEPATHY = Ability(
    name="Telepathy",
    description="Read surface thoughts, anticipating enemy moves.",
    ability_type=AbilityType.PASSIVE,
    accuracy=15,
    defense_bonus=5,
)

HYPER_INTELLIGENCE = Ability(
    name="Hyper Intelligence",
    description="Superior intellect improves all decision-making.",
    ability_type=AbilityType.PASSIVE,
    speed_bonus=5,
    accuracy=0,
)

PSYCHIC_BLAST = Ability(
    name="Psychic Blast",
    description="A concentrated burst of mental energy.",
    ability_type=AbilityType.ACTIVE,
    damage=35,
    energy_cost=20,
    damage_type=DamageType.PSYCHIC,
    accuracy=90,
)

MIND_CRUSH = Ability(
    name="Mind Crush",
    description="Overwhelm the enemy's mind, causing confusion and pain.",
    ability_type=AbilityType.ACTIVE,
    damage=25,
    energy_cost=25,
    damage_type=DamageType.PSYCHIC,
    status_effect=StatusEffect.STUNNED,
    status_duration=2,
    accuracy=80,
    cooldown=3,
)

TELEKINETIC_SHIELD = Ability(
    name="Telekinetic Shield",
    description="Create a barrier of pure mental force.",
    ability_type=AbilityType.ACTIVE,
    defense_bonus=20,
    energy_cost=20,
    status_effect=StatusEffect.SHIELDED,
    status_duration=2,
    cooldown=3,
)

MIMICRY = Ability(
    name="Mimicry",
    description="Copy the last ability used by the enemy.",
    ability_type=AbilityType.ACTIVE,
    energy_cost=30,
    accuracy=75,
    cooldown=4,
)


# ---------------------------------------------------------------------------
# Ability sets per god (for easy lookup)
# ---------------------------------------------------------------------------

GOD_ABILITIES: dict[str, list[Ability]] = {
    "Ophidia": [REPTILIAN_SKIN, THERMAL_VISION, VENOMOUS_BITE, FIRE_BREATH, SCALE_ARMOR, TAIL_SWEEP],
    "Galanth": [TELESCOPIC_SIGHT, HOLLOW_BONES, GUST_SLASH, UPDRAFT, PHOENIX_FLAME, DIVE_STRIKE],
    "Pelagon": [GILLS, CRUSH_RESISTANCE, TIDAL_SURGE, WHIRLPOOL, INK_CLOUD, CRUSHING_TENTACLE],
    "Myriad": [CHITIN_PLATING, VIBRATION_SENSE, SWARM_STRIKE, STINGER_JAB, HIVE_SHIELD, COLONY_TELEPATHY],
    "Karn": [RETRACTABLE_CLAWS, TRACKING_SCENT, FERAL_SLASH, PACK_HOWL, BERSERKER_RAGE, PREDATOR_POUNCE],
    "Pachymos": [STONESKIN, TIRELESS, GROUND_SLAM, BARRIER, STAMPEDE, TRUTH_SEEING],
    "Skulk": [NIGHT_VISION, SOUND_SUPPRESSION, SHADOW_STRIKE, VANISH, LUCK_MANIPULATION, ILLUSION],
    "Sagax": [TELEPATHY, HYPER_INTELLIGENCE, PSYCHIC_BLAST, MIND_CRUSH, TELEKINETIC_SHIELD, MIMICRY],
}
