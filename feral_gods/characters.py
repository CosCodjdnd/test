"""Character models for the Feral Gods RPG."""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from .enums import (
    AbilityType, GodName, Rarity, StatusEffect,
    RARITY_MULTIPLIERS, DIVINERS_MARK_CHANCE,
)
from .abilities import Ability, GOD_ABILITIES
from .gods import Spirit, God, ALL_GODS, ALL_SPIRITS


@dataclass
class StatusInstance:
    """An active status effect on a character."""
    effect: StatusEffect
    remaining_turns: int


@dataclass
class Character:
    """A character in the Feral Gods world."""
    name: str
    level: int = 1
    max_hp: int = 100
    current_hp: int = 100
    max_energy: int = 80
    current_energy: int = 80
    base_attack: int = 15
    base_defense: int = 10
    base_speed: int = 10
    base_accuracy: int = 80
    spirit: Spirit | None = None
    god: God | None = None
    has_diviners_mark: bool = False
    is_ungifted: bool = False
    abilities: list[Ability] = field(default_factory=list)
    status_effects: list[StatusInstance] = field(default_factory=list)
    cooldowns: dict[str, int] = field(default_factory=dict)
    experience: int = 0

    # Physical traits granted by spirit
    physical_traits: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.spirit:
            self._apply_spirit()

    def _apply_spirit(self) -> None:
        """Apply spirit bonuses and abilities to this character."""
        if not self.spirit:
            return
        god_name = self.spirit.god.value
        self.god = next((g for g in ALL_GODS if g.name.value == god_name), None)
        self.physical_traits = list(self.spirit.physical_traits)

        # Scale stats by spirit power
        power = self.spirit.effective_power
        self.max_hp += power * 2
        self.current_hp = self.max_hp
        self.max_energy += power
        self.current_energy = self.max_energy
        self.base_attack += power // 2
        self.base_defense += power // 3
        self.base_speed += power // 4

        # Assign abilities from god
        self.abilities = list(GOD_ABILITIES.get(god_name, []))

    def receive_spirit(self, spirit: Spirit) -> None:
        """Receive a spirit companion (e.g., during the Ceremony)."""
        self.spirit = spirit
        self.is_ungifted = False
        self._apply_spirit()

    @property
    def is_alive(self) -> bool:
        return self.current_hp > 0

    @property
    def attack(self) -> int:
        """Total attack including passive ability bonuses and status effects."""
        total = self.base_attack
        for ability in self.abilities:
            if ability.ability_type == AbilityType.PASSIVE:
                total += ability.damage
        if self.has_status(StatusEffect.BERSERKER):
            total += 15
        if self.has_status(StatusEffect.INTIMIDATED):
            total -= 5
        return max(1, total)

    @property
    def defense(self) -> int:
        """Total defense including passive ability bonuses and status effects."""
        total = self.base_defense
        for ability in self.abilities:
            if ability.ability_type == AbilityType.PASSIVE:
                total += ability.defense_bonus
        if self.has_status(StatusEffect.SHIELDED):
            total += 15
        if self.has_status(StatusEffect.BERSERKER):
            total -= 5
        return max(0, total)

    @property
    def speed(self) -> int:
        """Total speed including passive ability bonuses."""
        total = self.base_speed
        for ability in self.abilities:
            if ability.ability_type == AbilityType.PASSIVE:
                total += ability.speed_bonus
        return total

    @property
    def accuracy(self) -> int:
        """Total accuracy including passive ability bonuses."""
        total = self.base_accuracy
        for ability in self.abilities:
            if ability.ability_type == AbilityType.PASSIVE:
                total += ability.accuracy
        if self.has_status(StatusEffect.BLINDED):
            total -= 25
        return max(10, min(100, total))

    def has_status(self, effect: StatusEffect) -> bool:
        return any(s.effect == effect for s in self.status_effects)

    def apply_status(self, effect: StatusEffect, duration: int) -> None:
        """Apply a status effect, refreshing if already present."""
        for s in self.status_effects:
            if s.effect == effect:
                s.remaining_turns = max(s.remaining_turns, duration)
                return
        self.status_effects.append(StatusInstance(effect, duration))

    def tick_status_effects(self) -> list[str]:
        """Process status effects at the start of a turn. Returns log messages."""
        messages = []
        remaining = []
        for s in self.status_effects:
            if s.effect == StatusEffect.POISONED:
                dmg = 8
                self.current_hp = max(0, self.current_hp - dmg)
                messages.append(f"  {self.name} takes {dmg} poison damage!")
            elif s.effect == StatusEffect.BURNING:
                dmg = 10
                self.current_hp = max(0, self.current_hp - dmg)
                messages.append(f"  {self.name} takes {dmg} burn damage!")
            elif s.effect == StatusEffect.REGENERATING:
                heal = 12
                self.current_hp = min(self.max_hp, self.current_hp + heal)
                messages.append(f"  {self.name} regenerates {heal} HP!")
            elif s.effect == StatusEffect.STUNNED:
                messages.append(f"  {self.name} is stunned and cannot act!")

            s.remaining_turns -= 1
            if s.remaining_turns > 0:
                remaining.append(s)
            else:
                messages.append(f"  {self.name}'s {s.effect.value} wore off.")
        self.status_effects = remaining
        return messages

    def tick_cooldowns(self) -> None:
        """Reduce all cooldowns by 1."""
        expired = []
        for name in self.cooldowns:
            self.cooldowns[name] -= 1
            if self.cooldowns[name] <= 0:
                expired.append(name)
        for name in expired:
            del self.cooldowns[name]

    def get_active_abilities(self) -> list[Ability]:
        """Return active abilities that can be used right now."""
        return [
            a for a in self.abilities
            if a.ability_type == AbilityType.ACTIVE
            and a.can_use(self.current_energy)
            and a.name not in self.cooldowns
        ]

    def use_ability(self, ability: Ability, target: Character) -> list[str]:
        """Use an active ability against a target. Returns log messages."""
        messages = []
        if ability.name in self.cooldowns:
            messages.append(f"  {ability.name} is on cooldown for {self.cooldowns[ability.name]} more turns.")
            return messages
        if not ability.can_use(self.current_energy):
            messages.append(f"  Not enough energy to use {ability.name}!")
            return messages

        self.current_energy -= ability.energy_cost
        if ability.cooldown > 0:
            self.cooldowns[ability.name] = ability.cooldown

        # Accuracy check
        hit_chance = min(100, self.accuracy + ability.accuracy - 80)
        if self.has_status(StatusEffect.HIDDEN):
            hit_chance += 20  # attacking from stealth
        roll = random.randint(1, 100)

        if roll > hit_chance:
            messages.append(f"  {self.name} uses {ability.name} but misses!")
            return messages

        messages.append(f"  {self.name} uses {ability.name}!")

        # Damage
        if ability.is_offensive():
            raw_damage = self.attack + ability.damage
            reduction = target.defense
            final_damage = max(1, raw_damage - reduction)
            target.current_hp = max(0, target.current_hp - final_damage)
            messages.append(f"  {target.name} takes {final_damage} {ability.damage_type.value} damage! "
                            f"(HP: {target.current_hp}/{target.max_hp})")

        # Healing
        if ability.is_supportive() and ability.healing > 0:
            healed = ability.healing
            self.current_hp = min(self.max_hp, self.current_hp + healed)
            messages.append(f"  {self.name} heals for {healed}! (HP: {self.current_hp}/{self.max_hp})")

        # Defense bonus (self-buff)
        if ability.defense_bonus > 0 and not ability.is_offensive():
            messages.append(f"  {self.name} gains +{ability.defense_bonus} defense!")

        # Status effect on target
        if ability.status_effect and ability.is_offensive():
            target.apply_status(ability.status_effect, ability.status_duration)
            messages.append(f"  {target.name} is now {ability.status_effect.value}!")
        elif ability.status_effect and not ability.is_offensive():
            # Self-buff status
            if ability.status_effect in (StatusEffect.BERSERKER, StatusEffect.SHIELDED,
                                         StatusEffect.HIDDEN, StatusEffect.REGENERATING):
                self.apply_status(ability.status_effect, ability.status_duration)
                messages.append(f"  {self.name} is now {ability.status_effect.value}!")
            else:
                # Debuff on target
                target.apply_status(ability.status_effect, ability.status_duration)
                messages.append(f"  {target.name} is now {ability.status_effect.value}!")

        return messages

    def basic_attack(self, target: Character) -> list[str]:
        """Perform a basic physical attack."""
        messages = []
        roll = random.randint(1, 100)
        if roll > self.accuracy:
            messages.append(f"  {self.name} attacks but misses!")
            return messages

        raw_damage = self.attack
        reduction = target.defense
        final_damage = max(1, raw_damage - reduction)
        target.current_hp = max(0, target.current_hp - final_damage)
        messages.append(f"  {self.name} attacks {target.name} for {final_damage} damage! "
                        f"(HP: {target.current_hp}/{target.max_hp})")
        return messages

    def rest(self) -> list[str]:
        """Rest to recover energy."""
        recovered = min(20, self.max_energy - self.current_energy)
        self.current_energy += recovered
        return [f"  {self.name} rests and recovers {recovered} energy. "
                f"(Energy: {self.current_energy}/{self.max_energy})"]

    def gain_experience(self, amount: int) -> list[str]:
        """Gain experience and potentially level up."""
        messages = []
        self.experience += amount
        messages.append(f"  {self.name} gains {amount} XP!")
        xp_needed = self.level * 100
        while self.experience >= xp_needed:
            self.experience -= xp_needed
            self.level += 1
            self.max_hp += 10
            self.current_hp = self.max_hp
            self.max_energy += 5
            self.current_energy = self.max_energy
            self.base_attack += 2
            self.base_defense += 1
            self.base_speed += 1
            messages.append(f"  {self.name} leveled up to level {self.level}!")
            xp_needed = self.level * 100
        return messages

    def __str__(self) -> str:
        spirit_str = f" [{self.spirit.name}]" if self.spirit else " [Ungifted]"
        god_str = f" ({self.god.name.value})" if self.god else ""
        return (f"{self.name}{spirit_str}{god_str} "
                f"Lv.{self.level} HP:{self.current_hp}/{self.max_hp} "
                f"EN:{self.current_energy}/{self.max_energy}")


def create_character(name: str, spirit: Spirit | None = None,
                     has_diviners_mark: bool = False) -> Character:
    """Factory function to create a new character."""
    is_ungifted = spirit is None
    char = Character(
        name=name,
        spirit=spirit,
        has_diviners_mark=has_diviners_mark,
        is_ungifted=is_ungifted,
    )
    return char


def create_enemy(name: str, spirit: Spirit, level: int = 1) -> Character:
    """Create an enemy NPC with a spirit and scaled to a level."""
    enemy = Character(name=name, spirit=spirit, level=level)
    # Scale enemy stats by level
    for _ in range(level - 1):
        enemy.max_hp += 10
        enemy.max_energy += 5
        enemy.base_attack += 2
        enemy.base_defense += 1
        enemy.base_speed += 1
    enemy.current_hp = enemy.max_hp
    enemy.current_energy = enemy.max_energy
    return enemy
