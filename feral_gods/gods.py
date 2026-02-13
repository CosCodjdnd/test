"""God and Spirit definitions for the Feral Gods RPG."""

from __future__ import annotations

from dataclasses import dataclass, field

from .enums import GodName, Rarity, RARITY_MULTIPLIERS
from .abilities import Ability, GOD_ABILITIES


@dataclass
class Spirit:
    """A spirit companion granted by a god."""
    name: str
    god: GodName
    rarity: Rarity
    description: str
    physical_traits: list[str] = field(default_factory=list)
    base_power: int = 10

    @property
    def power_multiplier(self) -> float:
        return RARITY_MULTIPLIERS[self.rarity]

    @property
    def effective_power(self) -> int:
        return int(self.base_power * self.power_multiplier)


@dataclass
class God:
    """One of the eight gods of the Feral Gods world."""
    name: GodName
    title: str
    domain: str
    description: str
    personality_traits: list[str]
    spirits: list[Spirit] = field(default_factory=list)

    @property
    def abilities(self) -> list[Ability]:
        return GOD_ABILITIES.get(self.name.value, [])


# ---------------------------------------------------------------------------
# Spirit definitions
# ---------------------------------------------------------------------------

# OPHIDIA spirits
SNAKE = Spirit("Snake", GodName.OPHIDIA, Rarity.COMMON, "A cunning serpent companion.",
               ["slitted eyes", "scaled patches"], 10)
TURTLE = Spirit("Turtle", GodName.OPHIDIA, Rarity.COMMON, "A patient, armored spirit.",
                ["tough skin", "slow gait"], 10)
LIZARD = Spirit("Lizard", GodName.OPHIDIA, Rarity.COMMON, "A quick, adaptive reptile.",
                ["color-shifting skin", "slitted eyes"], 10)
CROCODILE = Spirit("Crocodile", GodName.OPHIDIA, Rarity.UNCOMMON, "A powerful ambush predator.",
                   ["armored ridges", "powerful jaw"], 14)
KOMODO = Spirit("Komodo Dragon", GodName.OPHIDIA, Rarity.RARE, "A massive venomous hunter.",
                ["heavy scales", "forked tongue", "thermal pits"], 18)
BASILISK = Spirit("Basilisk", GodName.OPHIDIA, Rarity.RARE, "A legendary serpent of petrifying gaze.",
                  ["glowing slitted eyes", "crown-like scales"], 20)
WYVERN = Spirit("Wyvern", GodName.OPHIDIA, Rarity.LEGENDARY, "A winged reptilian terror.",
                ["wing membranes", "heavy scales", "tail barb"], 25)
DRAGON = Spirit("Dragon", GodName.OPHIDIA, Rarity.LEGENDARY, "The ultimate apex predator of scales and fire.",
                ["full scale plating", "slitted golden eyes", "ember breath"], 30)

# GALANTH spirits
SPARROW = Spirit("Sparrow", GodName.GALANTH, Rarity.COMMON, "A quick, cheerful songbird.",
                 ["light feathered arms", "amber eyes"], 10)
HAWK = Spirit("Hawk", GodName.GALANTH, Rarity.COMMON, "A keen-eyed hunter of the sky.",
              ["sharp amber eyes", "feathered forearms"], 10)
EAGLE = Spirit("Eagle", GodName.GALANTH, Rarity.UNCOMMON, "A majestic raptor of great vision.",
               ["golden amber eyes", "broad feathered limbs"], 14)
OWL = Spirit("Owl", GodName.GALANTH, Rarity.UNCOMMON, "A wise nocturnal hunter.",
             ["wide amber eyes", "soft feathered skin"], 14)
GRIFFIN = Spirit("Griffin", GodName.GALANTH, Rarity.RARE, "A noble beast of sky and earth.",
                 ["lion-like mane", "eagle talons", "amber eyes"], 20)
PTERANODON = Spirit("Pteranodon", GodName.GALANTH, Rarity.RARE, "An ancient flying reptile.",
                    ["membrane skin", "elongated fingers", "crested brow"], 18)
PHOENIX = Spirit("Phoenix", GodName.GALANTH, Rarity.LEGENDARY, "An immortal bird of healing fire.",
                 ["radiant feathers", "ember-glow eyes", "warm aura"], 30)

# PELAGON spirits
FISH = Spirit("Fish", GodName.PELAGON, Rarity.COMMON, "A swift swimmer of the currents.",
              ["gills", "scaled skin patches"], 10)
JELLYFISH = Spirit("Jellyfish", GodName.PELAGON, Rarity.COMMON, "A translucent drifter with stinging tendrils.",
                   ["translucent skin patches", "faint bioluminescence"], 10)
SHARK = Spirit("Shark", GodName.PELAGON, Rarity.UNCOMMON, "A fearsome predator of the deep.",
               ["rows of sharp teeth", "dark eyes", "sleek skin"], 14)
OCTOPUS = Spirit("Octopus", GodName.PELAGON, Rarity.RARE, "A clever shapeshifter of the sea.",
                 ["sucker-marked skin", "color-shifting patches"], 18)
DOLPHIN = Spirit("Dolphin", GodName.PELAGON, Rarity.RARE, "A playful, intelligent ocean dweller.",
                 ["sleek skin", "bright eyes", "echolocation sense"], 18)
KRAKEN = Spirit("Kraken", GodName.PELAGON, Rarity.LEGENDARY, "A colossal terror of the abyss.",
                ["tentacle-like limbs", "massive build", "deep-sea eyes"], 28)
LEVIATHAN = Spirit("Leviathan", GodName.PELAGON, Rarity.LEGENDARY, "An ancient sea god incarnate.",
                   ["armored scales", "bioluminescent markings", "crushing presence"], 30)

# MYRIAD spirits
ANT = Spirit("Ant", GodName.MYRIAD, Rarity.COMMON, "A tireless worker of the colony.",
             ["coarse body hair", "strong mandible-like jaw"], 10)
BEE = Spirit("Bee", GodName.MYRIAD, Rarity.COMMON, "A dutiful pollinator with a potent sting.",
             ["fuzzy skin", "compound-like eyes", "barbed nails"], 10)
BEETLE = Spirit("Beetle", GodName.MYRIAD, Rarity.COMMON, "A sturdy insect with heavy armor.",
                ["thick exoskeletal patches", "horn-like protrusion"], 10)
SPIDER = Spirit("Spider", GodName.MYRIAD, Rarity.UNCOMMON, "A patient web-weaver and ambush hunter.",
                ["multiple eye markings", "fine body hair"], 14)
SCORPION = Spirit("Giant Scorpion", GodName.MYRIAD, Rarity.RARE, "An ancient arachnid of lethal venom.",
                  ["tail-like appendage", "pincer-like hands", "chitin patches"], 20)
DRAGONFLY = Spirit("Ancient Dragonfly", GodName.MYRIAD, Rarity.RARE, "A primordial insect of incredible speed.",
                   ["iridescent skin patches", "large multifaceted eyes", "wing nubs"], 18)

# KARN spirits
WOLF = Spirit("Wolf", GodName.KARN, Rarity.COMMON, "A loyal pack hunter.",
              ["yellow eyes", "thick body hair", "sharp canines"], 10)
WILD_DOG = Spirit("Wild Dog", GodName.KARN, Rarity.COMMON, "A tenacious, social predator.",
                  ["keen eyes", "lean build", "sharp teeth"], 10)
LION = Spirit("Lion", GodName.KARN, Rarity.UNCOMMON, "A proud king of beasts.",
              ["mane-like hair", "yellow eyes", "retractable nails"], 14)
PANTHER = Spirit("Panther", GodName.KARN, Rarity.UNCOMMON, "A stealthy, powerful hunter.",
                 ["dark sleek hair", "yellow-green eyes", "claws"], 14)
SABERTOOTH = Spirit("Sabertooth", GodName.KARN, Rarity.RARE, "An ancient apex predator with massive fangs.",
                    ["elongated canines", "thick fur-like hair", "powerful build"], 20)
CERBERUS = Spirit("Cerberus", GodName.KARN, Rarity.LEGENDARY, "A three-headed guardian beast.",
                  ["triple shadow", "burning eyes", "massive frame"], 28)

# PACHYMOS spirits
HORSE = Spirit("Horse", GodName.PACHYMOS, Rarity.COMMON, "A steadfast, powerful companion.",
               ["thick skin", "strong build", "calm eyes"], 10)
RHINO = Spirit("Rhino", GodName.PACHYMOS, Rarity.UNCOMMON, "A thick-skinned charger.",
               ["horn protrusion", "grey tough skin", "massive build"], 14)
ELEPHANT = Spirit("Elephant", GodName.PACHYMOS, Rarity.UNCOMMON, "A wise and powerful giant.",
                  ["grey tough skin", "large ears", "calm demeanor"], 14)
MAMMOTH = Spirit("Mammoth", GodName.PACHYMOS, Rarity.RARE, "An ancient woolly giant of immense strength.",
                 ["thick fur", "tusks", "massive frame"], 20)
TRICERATOPS = Spirit("Triceratops", GodName.PACHYMOS, Rarity.RARE, "A triple-horned defender from ancient times.",
                     ["bony crest", "triple horn ridges", "armored skin"], 20)
BEHEMOTH = Spirit("Behemoth", GodName.PACHYMOS, Rarity.LEGENDARY, "An unstoppable primordial titan.",
                  ["stone-like skin", "towering frame", "earthquake steps"], 30)

# SKULK spirits
RAT = Spirit("Rat", GodName.SKULK, Rarity.COMMON, "A cunning, resourceful survivor.",
             ["twitchy nose", "sharp teeth", "small frame"], 10)
BAT = Spirit("Bat", GodName.SKULK, Rarity.COMMON, "A nocturnal flyer with supersonic hearing.",
             ["large ears", "thin wing-like membranes", "dark eyes"], 10)
RACCOON = Spirit("Raccoon", GodName.SKULK, Rarity.UNCOMMON, "A clever masked trickster.",
                 ["mask-like markings", "dexterous fingers"], 14)
MONKEY = Spirit("Monkey", GodName.SKULK, Rarity.UNCOMMON, "A nimble, crafty primate.",
                ["agile limbs", "prehensile dexterity"], 14)
JACKALOPE = Spirit("Jackalope", GodName.SKULK, Rarity.RARE, "A mythical horned hare of impossible luck.",
                   ["antler stubs", "rabbit-like ears", "alert eyes"], 20)

# SAGAX spirits
FOX = Spirit("Fox", GodName.SAGAX, Rarity.COMMON, "A clever, analytical predator.",
             ["sharp eyes", "reddish tint to hair"], 10)
OTTER = Spirit("Otter", GodName.SAGAX, Rarity.COMMON, "A playful but sharp-minded companion.",
               ["sleek build", "bright curious eyes"], 10)
CHIMPANZEE = Spirit("Chimpanzee", GodName.SAGAX, Rarity.UNCOMMON, "An intelligent, tool-using primate.",
                    ["dexterous hands", "keen eyes"], 14)
GORILLA = Spirit("Gorilla", GodName.SAGAX, Rarity.UNCOMMON, "A powerful, thoughtful great ape.",
                 ["broad build", "intelligent gaze"], 14)
SPHINX = Spirit("Sphinx", GodName.SAGAX, Rarity.LEGENDARY, "A mythical being of supreme intellect and mystery.",
                ["enigmatic gaze", "leonine grace", "riddle aura"], 30)


# ---------------------------------------------------------------------------
# God definitions
# ---------------------------------------------------------------------------

ALL_SPIRITS: dict[str, list[Spirit]] = {
    "Ophidia": [SNAKE, TURTLE, LIZARD, CROCODILE, KOMODO, BASILISK, WYVERN, DRAGON],
    "Galanth": [SPARROW, HAWK, EAGLE, OWL, GRIFFIN, PTERANODON, PHOENIX],
    "Pelagon": [FISH, JELLYFISH, SHARK, OCTOPUS, DOLPHIN, KRAKEN, LEVIATHAN],
    "Myriad": [ANT, BEE, BEETLE, SPIDER, SCORPION, DRAGONFLY],
    "Karn": [WOLF, WILD_DOG, LION, PANTHER, SABERTOOTH, CERBERUS],
    "Pachymos": [HORSE, RHINO, ELEPHANT, MAMMOTH, TRICERATOPS, BEHEMOTH],
    "Skulk": [RAT, BAT, RACCOON, MONKEY, JACKALOPE],
    "Sagax": [FOX, OTTER, CHIMPANZEE, GORILLA, SPHINX],
}

OPHIDIA = God(
    name=GodName.OPHIDIA,
    title="Scales and Fire",
    domain="Reptiles and cold-blooded power",
    description="Ophidia grants dominion over reptilian forms—from cunning serpents to mighty dragons. "
                "Her followers are adaptive, fierce, and ever-changing.",
    personality_traits=["cunning", "adaptive", "affectionate", "ever-changing", "growth-oriented", "steadfast", "fierce"],
    spirits=ALL_SPIRITS["Ophidia"],
)

GALANTH = God(
    name=GodName.GALANTH,
    title="Sky and Wind",
    domain="Flight and perspective",
    description="Galanth rules the skies, granting the gift of flight and vision beyond mortal ken. "
                "The most common blessing, given to those of broad and varied temperament.",
    personality_traits=["intelligent", "strategic", "decisive", "empathetic", "creative", "ambitious"],
    spirits=ALL_SPIRITS["Galanth"],
)

PELAGON = God(
    name=GodName.PELAGON,
    title="The Deep",
    domain="Ocean pressure and fluidity",
    description="Pelagon commands the depths, bestowing the power of water and the resilience of the abyss. "
                "His followers are fierce yet misunderstood, fluid in personality.",
    personality_traits=["fierce", "loyal", "playful", "curious", "fluid", "social"],
    spirits=ALL_SPIRITS["Pelagon"],
)

MYRIAD = God(
    name=GodName.MYRIAD,
    title="The Swarm",
    domain="Insects, arachnids, and hive minds",
    description="Myriad embodies the collective—the strength of the swarm, the unity of the hive. "
                "The most common blessing for average folk.",
    personality_traits=["community-oriented", "harmonious", "hardworking", "optimistic", "naïve"],
    spirits=ALL_SPIRITS["Myriad"],
)

KARN = God(
    name=GodName.KARN,
    title="The Hunt",
    domain="Predators and pack tactics",
    description="Karn is the patron of hunters and soldiers. His followers thrive in groups, "
                "communicating through instinct and hierarchy.",
    personality_traits=["cooperative", "communicative", "hierarchical", "social", "territorial"],
    spirits=ALL_SPIRITS["Karn"],
)

PACHYMOS = God(
    name=GodName.PACHYMOS,
    title="The Tank",
    domain="Heavy defense and stamina",
    description="Pachymos blesses the gentle giants—those who lead through presence, not aggression. "
                "Silent leaders with unbreakable resolve.",
    personality_traits=["gentle", "empathetic", "generous", "wise", "stubborn", "altruistic"],
    spirits=ALL_SPIRITS["Pachymos"],
)

SKULK = God(
    name=GodName.SKULK,
    title="Shadows",
    domain="Stealth, nocturnal creatures, and trickery",
    description="Skulk lurks in the darkness, gifting cunning and shadow to those who walk between worlds. "
                "Rule-breakers and survivors.",
    personality_traits=["deceitful", "witty", "clever", "solitary", "charismatic", "adaptable"],
    spirits=ALL_SPIRITS["Skulk"],
)

SAGAX = God(
    name=GodName.SAGAX,
    title="The Mind",
    domain="Intelligence and mystery",
    description="Sagax is the god of thought itself—granting powers of the mind that transcend the physical. "
                "The most enigmatic of all blessings.",
    personality_traits=["intelligent", "cunning", "mysterious", "analytical", "pragmatic", "enigmatic"],
    spirits=ALL_SPIRITS["Sagax"],
)

ALL_GODS = [OPHIDIA, GALANTH, PELAGON, MYRIAD, KARN, PACHYMOS, SKULK, SAGAX]

GODS_BY_NAME: dict[str, God] = {god.name.value: god for god in ALL_GODS}
